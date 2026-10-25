"""Etapa de preparación de observaciones y trayectorias."""

from models.experimento import Experimento
from models.observacion import Observacion
from models.trayectoria import Trayectoria
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


class PreparacionTrayectorias(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Agrupa validación, organización y reconstrucción de trayectorias."""

    def ejecutar(
        self,
        experimentos: list[Experimento],
        contexto: ContextoPipeline,
    ) -> list[Experimento]:

        for exp in experimentos:
            exp.trayectorias = self._reconstruir_trayectorias(
                self._organizar_observaciones(
                self._validar_observaciones(exp.observaciones)))

        return experimentos

    def _validar_observaciones(
        self,
        observaciones: list[Observacion],
    ) -> list[Observacion]:
        # TODO: pregutar q se hace aqui
        return observaciones


    def _organizar_observaciones(
        self,
        observaciones: list[Observacion],
    ) -> dict[int, list[Observacion]]:

        ordenadas: dict[int, list[Observacion]] = {}

        for observacion in observaciones:
            if observacion.id_peaton not in ordenadas:
                ordenadas[observacion.id_peaton] = []
            ordenadas[observacion.id_peaton].append(observacion)

        return ordenadas

    def _reconstruir_trayectorias(
        self,
        observaciones_organizadas: dict[int, list[Observacion]],
    ) -> list[Trayectoria]:

        trayectorias: list[Trayectoria] = []
        for id_peaton, observaciones in observaciones_organizadas.items():
            trayectorias.append(Trayectoria(id_peaton, observaciones))

        return trayectorias
