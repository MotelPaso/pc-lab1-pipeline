"""Etapa de análisis espacial, densidad y flujo."""

from collections import Counter
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
    ) -> None:
        """Define la línea del flujo y el área donde se mide la densidad.

        linea_x: posición x (m) de la línea transversal para el flujo.
        area_x, area_y: límites (m) del rectángulo donde se mide la densidad.
        """
        self.linea_x = linea_x
        self.area_x = area_x
        self.area_y = area_y

    def ejecutar(
        self,
        experimentos: list[Experimento],
        contexto: ContextoPipeline,
    ) -> list[Experimento]:
        """Analiza las zonas, la densidad y el flujo de cada experimento."""
        for experimento in experimentos:
            fps = contexto.fps if contexto.fps is not None else experimento.fps
            # TODO: agregar el análisis por zonas
            flujo = self._calcular_flujo(experimento, fps)
            densidad = self._calcular_densidad(experimento)
            experimento.resultados_colectivos.update(flujo)
            experimento.resultados_colectivos.update(densidad)
        return experimentos

    def _analizar_zonas(self, experimento: Experimento) -> dict[str, float]:
        pass

    def _calcular_densidad(self, experimento: Experimento) -> dict[str, float]:
        """Calcula la densidad ρ = N / A en el área de medición, frame a frame.

        N es la cantidad de peatones dentro del área en cada frame. Se promedia en el
        mismo período que el flujo: entre el primer y el último cruce de la línea.
        La densidad queda en personas por metro cuadrado.
        """
        (x_min, x_max), (y_min, y_max) = self.area_x, self.area_y
        area = (x_max - x_min) * (y_max - y_min)
        frames = self._cruces(experimento)
        if not frames:
            return {"densidad_media": 0, "densidad_maxima": 0}
        inicio, fin = frames[0], frames[-1]
        personas = Counter(
            o.frame
            for o in experimento.observaciones
            if inicio <= o.frame <= fin
            and x_min <= o.x < x_max
            and y_min <= o.y < y_max
        )
        densidades = [personas[frame] / area for frame in range(inicio, fin + 1)]
        return {
            "densidad_media": fmean(densidades),
            "densidad_maxima": max(densidades),
        }

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
