"""Etapa de exportación de resultados."""

import csv
from pathlib import Path

from models.resultado_analisis import ResultadoAnalisis
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


class ExportacionResultados(EtapaPipeline[ResultadoAnalisis, None]):
    """Exporta los resultados de los experimentos y su comparación."""

    def ejecutar(
        self,
        resultados: ResultadoAnalisis,
        contexto: ContextoPipeline,
    ) -> None:
        """Guarda los resultados en la ruta de salida configurada."""
        self._exportar(resultados, contexto.ruta_salida)

    def _exportar(self, resultados: ResultadoAnalisis, ruta_salida: Path) -> None:
        """Exporta los resultados a la ruta indicada."""
        ruta_salida.mkdir(parents=True, exist_ok=True)
        individuales = [
            {"experimento": experimento.nombre, "id_peaton": id_peaton, **indicadores}
            for experimento in resultados.experimentos
            for id_peaton, indicadores in experimento.resultados_individuales.items()
        ]
        por_experimento = [
            {"experimento": experimento.nombre, **experimento.resultados_colectivos}
            for experimento in resultados.experimentos
        ]
        self._escribir_csv(ruta_salida / "resultados_individuales.csv", individuales)
        self._escribir_csv(ruta_salida / "resultados_experimentos.csv", por_experimento)

    def _escribir_csv(self, ruta: Path, filas: list[dict[str, object]]) -> None:
        """Escribe una fila por diccionario, con una columna por cada clave."""
        columnas = list(dict.fromkeys(clave for fila in filas for clave in fila))
        with ruta.open("w", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=columnas, lineterminator="\n")
            escritor.writeheader()
            escritor.writerows(filas)
        print(f"Archivo guardado: {ruta} ({len(filas)} filas)")