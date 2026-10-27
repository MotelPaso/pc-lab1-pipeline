"""Etapa de análisis espacial, densidad y flujo."""

from collections import Counter
from math import floor
from statistics import fmean

from models.experimento import Experimento
from models.trayectoria import Trayectoria
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


class AnalisisEspacial(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Agrupa el análisis por zonas y los cálculos de densidad y flujo."""

    def __init__(
        self,
        linea_x: float = 0.0,
        area_x: tuple[float, float] = (-1.0, 1.0),
        area_y: tuple[float, float] = (0.0, 5.0),
        ventana_serie: float = 5.0,
        ancho_zona: float = 1.0,
    ) -> None:
        """Define la línea del flujo, el área de densidad, las ventanas y las zonas.

        linea_x: posición x (m) de la línea transversal para el flujo.
        area_x, area_y: límites (m) del rectángulo donde se mide la densidad.
        ventana_serie: duración (s) de cada ventana de las series de tiempo.
        ancho_zona: largo (m) de cada zona en que se divide el corredor a lo largo de x.
        """
        self.linea_x = linea_x
        self.area_x = area_x
        self.area_y = area_y
        self.ventana_serie = ventana_serie
        self.ancho_zona = ancho_zona

    def ejecutar(
        self,
        experimentos: list[Experimento],
        contexto: ContextoPipeline,
    ) -> list[Experimento]:
        """Analiza las zonas, la densidad y el flujo de cada experimento."""
        for experimento in experimentos:
            fps = contexto.fps if contexto.fps is not None else experimento.fps
            flujo = self._calcular_flujo(experimento, fps)
            densidad = self._calcular_densidad(experimento)
            experimento.resultados_colectivos.update(flujo)
            experimento.resultados_colectivos.update(densidad)
            experimento.serie_temporal = self._calcular_serie(experimento, fps)
            experimento.resultados_zonas = self._analizar_zonas(experimento, fps)
        return experimentos

    def _analizar_zonas(
        self,
        experimento: Experimento,
        fps: float,
    ) -> list[dict[str, float]]:
        """Calcula los peatones, la velocidad media y el tiempo medio de cada zona.

        Las zonas son franjas de ancho_zona metros a lo largo de x. Un peatón
        atraviesa una zona si tiene observaciones a ambos lados de ella. Su tiempo
        en la zona es la cantidad de frames que pasa dentro dividida por fps, y su
        velocidad, el ancho de la zona dividido por ese tiempo.
        """
        tiempos: dict[int, list[float]] = {}
        for trayectoria in experimento.trayectorias:
            zonas = [floor(o.x / self.ancho_zona) for o in trayectoria.observaciones]
            if not zonas:
                continue
            primera, ultima = min(zonas), max(zonas)
            for zona, frames in Counter(zonas).items():
                if primera < zona < ultima:
                    tiempos.setdefault(zona, []).append(frames / fps)
        return [
            {
                "x_desde": zona * self.ancho_zona,
                "x_hasta": (zona + 1) * self.ancho_zona,
                "peatones": len(tiempos_zona),
                "velocidad_media": fmean(self.ancho_zona / t for t in tiempos_zona),
                "tiempo_medio": fmean(tiempos_zona),
            }
            for zona, tiempos_zona in sorted(tiempos.items())
        ]

    def _calcular_densidad(self, experimento: Experimento) -> dict[str, float]:
        """Calcula la densidad ρ = N / A en el área de medición, frame a frame.

        N es la cantidad de peatones dentro del área en cada frame. Se promedia en el
        mismo período que el flujo: entre el primer y el último cruce de la línea.
        La densidad queda en personas por metro cuadrado.
        """
        frames = self._cruces(experimento)
        if not frames:
            return {"densidad_media": 0, "densidad_maxima": 0}
        personas = self._personas_en_area(experimento)
        area = self._area()
        densidades = [personas[f] / area for f in range(frames[0], frames[-1] + 1)]
        return {
            "densidad_media": fmean(densidades),
            "densidad_maxima": max(densidades),
        }

    def _calcular_serie(
        self,
        experimento: Experimento,
        fps: float,
    ) -> list[dict[str, float]]:
        """Calcula la densidad y el flujo en ventanas de tiempo consecutivas.

        Cubre el experimento completo, desde su primer hasta su último frame. Cada
        fila tiene el inicio de la ventana (s), la densidad media (personas/m²) y
        el flujo (personas/s) de esa ventana.
        """
        if not experimento.observaciones:
            return []
        frames = [o.frame for o in experimento.observaciones]
        inicio, fin = min(frames), max(frames)
        largo = max(1, round(self.ventana_serie * fps))
        personas = self._personas_en_area(experimento)
        cruces = Counter((f - inicio) // largo for f in self._cruces(experimento))
        area = self._area()
        serie: list[dict[str, float]] = []
        for numero, desde in enumerate(range(inicio, fin + 1, largo)):
            ventana = range(desde, min(desde + largo, fin + 1))
            serie.append({
                "tiempo_inicio": desde / fps,
                "densidad": fmean(personas[f] / area for f in ventana),
                "flujo": cruces[numero] / (len(ventana) / fps),
            })
        return serie

    def _personas_en_area(self, experimento: Experimento) -> Counter[int]:
        """Cuenta, para cada frame, cuántos peatones hay dentro del área de medición."""
        (x_min, x_max), (y_min, y_max) = self.area_x, self.area_y
        return Counter(
            o.frame
            for o in experimento.observaciones
            if x_min <= o.x < x_max and y_min <= o.y < y_max
        )

    def _area(self) -> float:
        """Calcula la superficie del área de medición, en metros cuadrados."""
        (x_min, x_max), (y_min, y_max) = self.area_x, self.area_y
        return (x_max - x_min) * (y_max - y_min)

    def _calcular_flujo(
        self,
        experimento: Experimento,
        fps: float,
    ) -> dict[str, float]:
        """Calcula el flujo J = N / Δt a través de la línea transversal.

        N es la cantidad de peatones que cruzan la línea y Δt, el tiempo entre
        el primer y el último cruce. El flujo queda en personas por segundo.
        """
        frames = self._cruces(experimento)
        duracion = (frames[-1] - frames[0]) / fps if frames else 0
        flujo = len(frames) / duracion if duracion > 0 else 0
        return {"cruces": len(frames), "flujo": flujo}

    def _cruces(self, experimento: Experimento) -> list[int]:
        """Devuelve, ordenados, los frames en que cada peatón cruza la línea."""
        cruces = [self._frame_de_cruce(t) for t in experimento.trayectorias]
        return sorted(frame for frame in cruces if frame is not None)

    def _frame_de_cruce(self, trayectoria: Trayectoria) -> int | None:
        """Devuelve el primer frame en que el peatón ya cruzó la línea, o None."""
        pares = zip(trayectoria.observaciones, trayectoria.observaciones[1:])
        for a, b in pares:
            if (a.x < self.linea_x) != (b.x < self.linea_x):
                return b.frame
        return None
