"""Etapa de análisis individual de los experimentos."""

from itertools import groupby

from models.experimento import Experimento
from models.trayectoria import Trayectoria
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


class AnalisisIndividual(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Coordina el análisis de múltiples trayectorias y reúne sus indicadores."""

    def __init__(
            self,
            umbral_velocidad: float = 0.1,
            duracion_minima: float = 1.0,
            ventana: float = 1.0,
    ) -> None:
        """Define el criterio de detención.

        umbral_velocidad: velocidad (m/s) bajo la cual el peatón se considera detenido.
        duracion_minima: tiempo (s) que debe durar una detención para contarla.
        ventana: tiempo (s) en que se mide la velocidad de cada observación.
        """
        self.umbral_velocidad = umbral_velocidad
        self.duracion_minima = duracion_minima
        self.ventana = ventana

    def ejecutar(
        self,
        experimentos: list[Experimento],
        contexto: ContextoPipeline,
    ) -> list[Experimento]:
        """Analiza las trayectorias de cada experimento."""
        for experimento in experimentos:
            # Si se entrega --fps, reemplaza al fps leído del archivo
            fps = contexto.fps if contexto.fps is not None else experimento.fps
            experimento.resultados_individuales = {
                trayectoria.id_peaton: self._calcular_indicadores(trayectoria, fps)
                for trayectoria in experimento.trayectorias
            }
        return experimentos

    def _calcular_indicadores(
        self,
        trayectoria: Trayectoria,
        fps: float,
    ) -> dict[str, float]:
        """Calcula los indicadores individuales de una trayectoria."""
        x_inicial, y_inicial = trayectoria.posicion_inicial()
        x_final, y_final = trayectoria.posicion_final()
        tiempo_total = trayectoria.calcular_tiempo_total(fps)
        detenciones = self._detectar_detenciones(trayectoria, fps)
        tiempo_detenido = sum((fin-inicio) / fps for inicio, fin in detenciones)
        porcentaje = 100 * tiempo_detenido / tiempo_total if tiempo_total > 0 else 0
        return {
            "x_inicial": x_inicial,
            "y_inicial": y_inicial,
            "x_final": x_final,
            "y_final": y_final,
            "tiempo_total": tiempo_total,
            "distancia_total": trayectoria.calcular_distancia_total(),
            "desplazamiento": trayectoria.calcular_desplazamiento(),
            "velocidad_media": trayectoria.calcular_velocidad_media(fps),
            "velocidad_maxima": trayectoria.calcular_velocidad_maxima(fps),
            "eficiencia": trayectoria.calcular_eficiencia(),
            "cantidad_detenciones": len(detenciones),
            "tiempo_detenido": tiempo_detenido,
            "porcentaje_detenido": porcentaje,
        }

    def _detectar_detenciones(
        self,
        trayectoria: Trayectoria,
        fps: float,
    ) -> list[tuple[int, int]]:
        """Identifica intervalos de detención de una trayectoria.

        Devuelve (frame inicial, frame final) de cada tramo en que la velocidad
        se mantiene bajo el umbral durante al menos la duración mínima.
        """
        velocidades = self._calcular_velocidades(trayectoria, fps)
        tramos = groupby(
            zip(trayectoria.observaciones, velocidades),
            key=lambda par: par[1] < self.umbral_velocidad,
        )
        intervalos: list[tuple[int, int]] = []
        for detenido, grupo in tramos:
            if detenido:
                frames = [observacion.frame for observacion, _ in grupo]
                intervalos.append((frames[0], frames[-1]))
        return [
            (inicio, fin)
            for inicio, fin in intervalos
            if (fin - inicio) / fps >= self.duracion_minima
        ]

    def _calcular_velocidades(
        self,
        trayectoria: Trayectoria,
        fps: float,
    ) -> list[float]:
        """Calcula la velocidad de cada observación en una ventana centrada.

        Usa la posición media ventana antes y media ventana después, porque la
        velocidad entre cuadros consecutivos tiene demasiado ruido.
        """
        observaciones = trayectoria.observaciones
        mitad = max(1, round(fps * self.ventana / 2))
        velocidades: list[float] = []
        for i in range(len(observaciones)):
            antes = observaciones[max(i - mitad, 0)]
            despues = observaciones[min(i + mitad, len(observaciones) - 1)]
            tiempo = (despues.frame - antes.frame) / fps
            distancia = trayectoria.distancia_entre(antes, despues)
            velocidades.append(distancia / tiempo if tiempo > 0 else 0)
        return velocidades
