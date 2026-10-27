"""Etapa de análisis espacial, densidad y flujo."""

from models.experimento import Experimento
from models.trayectoria import Trayectoria
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


class AnalisisEspacial(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Agrupa el análisis por zonas y los cálculos de densidad y flujo."""

    def __init__(self, linea_x: float = 0.0) -> None:
        """Define la posición x (en metros) de la línea transversal para el flujo."""
        self.linea_x = linea_x

    def ejecutar(
        self,
        experimentos: list[Experimento],
        contexto: ContextoPipeline,
    ) -> list[Experimento]:
        """Analiza las zonas, la densidad y el flujo de cada experimento."""
        for experimento in experimentos:
            fps = contexto.fps if contexto.fps is not None else experimento.fps
            # TODO: agregar el análisis por zonas y la densidad
            flujo = self._calcular_flujo(experimento, fps)
            experimento.resultados_colectivos.update(flujo)
        return experimentos

    def _analizar_zonas(self, experimento: Experimento) -> dict[str, float]:
        pass

    def _calcular_densidad(self, experimento: Experimento) -> dict[str, float]:
        pass

    def _calcular_flujo(
        self,
        experimento: Experimento,
        fps: float,
    ) -> dict[str, float]:
        """Calcula el flujo J = N / Δt a través de la línea transversal.

        N es la cantidad de peatones que cruzan la línea y Δt, el tiempo entre
        el primer y el último cruce. El flujo queda en personas por segundo.
        """
        cruces = [self._frame_de_cruce(t) for t in experimento.trayectorias]
        frames = sorted(frame for frame in cruces if frame is not None)
        duracion = (frames[-1] - frames[0]) / fps if frames else 0
        flujo = len(frames) / duracion if duracion > 0 else 0
        return {"cruces": len(frames), "flujo": flujo}

    def _frame_de_cruce(self, trayectoria: Trayectoria) -> int | None:
        """Devuelve el primer frame en que el peatón ya cruzó la línea, o None."""
        pares = zip(trayectoria.observaciones, trayectoria.observaciones[1:])
        for a, b in pares:
            if (a.x < self.linea_x) != (b.x < self.linea_x):
                return b.frame
        return None
