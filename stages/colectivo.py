"""Etapa de comparación de experimentos."""

from statistics import fmean

from models.experimento import Experimento
from models.resultado_analisis import ResultadoAnalisis
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


def promedio(valores: list[float]) -> float:
    """Calcula el promedio de una lista, o 0 si está vacía."""
    return fmean(valores) if valores else 0


class ComparacionExperimentos(
    EtapaPipeline[list[Experimento], ResultadoAnalisis]
):
    """Compara resultados de varios experimentos."""

    def ejecutar(
        self,
        experimentos: list[Experimento],
        contexto: ContextoPipeline,
    ) -> ResultadoAnalisis:
        """Retorna los experimentos junto con sus resultados comparativos."""
        for experimento in experimentos:
            resumen = self._resumir(experimento)
            experimento.resultados_colectivos.update(resumen)
            print(
                f"{experimento.nombre}: {resumen['peatones']} peatones, "
                f"velocidad media {resumen['velocidad_media']:.2f} m/s"
            )
        return ResultadoAnalisis(experimentos, self._comparar(experimentos))

    def _resumir(self, experimento: Experimento) -> dict[str, float]:
        """Promedia los indicadores individuales de los peatones de un experimento."""
        resultados = list(experimento.resultados_individuales.values())
        return {
            "peatones": len(resultados),
            "velocidad_media": promedio([r["velocidad_media"] for r in resultados]),
            "distancia_media": promedio([r["distancia_total"] for r in resultados]),
            "tiempo_medio": promedio([r["tiempo_total"] for r in resultados]),
            "porcentaje_con_detencion": 100 * promedio(
                [float(r["cantidad_detenciones"] > 0) for r in resultados]
            ),
        }

    def _comparar(self, experimentos: list[Experimento]) -> dict[str, float]:
        """Calcula métricas que comparan los experimentos entre sí."""
        # TODO: relación entre densidad y velocidad, cuando exista AnalisisEspacial
        return {}