"""Etapa de preparación de observaciones y trayectorias."""

from math import isfinite

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
            validas = self._validar_observaciones(exp.observaciones)
            descartadas = len(exp.observaciones) - len(validas)
            if descartadas:
                print(f"{exp.nombre}: {descartadas} observaciones descartadas")
            exp.observaciones = validas
            exp.trayectorias = self._reconstruir_trayectorias(
                self._organizar_observaciones(validas))

        return experimentos

    def _validar_observaciones(
        self,
        observaciones: list[Observacion],
    ) -> list[Observacion]:
        """Descarta observaciones con coordenadas nan o infinitas, y frames repetidos.

        Si un peatón tiene dos observaciones en el mismo frame, se queda la primera.
        """
        finitas = [o for o in observaciones if all(map(isfinite, (o.x, o.y, o.z)))]
        unicas: dict[tuple[int, int], Observacion] = {}
        for observacion in finitas:
            unicas.setdefault((observacion.id_peaton, observacion.frame), observacion)
        return list(unicas.values())


    def _organizar_observaciones(
        self,
        observaciones: list[Observacion],
    ) -> dict[int, list[Observacion]]:

        ordenadas: dict[int, list[Observacion]] = {}

        for observacion in observaciones:
            if observacion.id_peaton not in ordenadas:
                ordenadas[observacion.id_peaton] = []
            ordenadas[observacion.id_peaton].append(observacion)

        return {
            id_peaton: sorted(observaciones_peaton, key=lambda o: o.frame)
            for id_peaton, observaciones_peaton in ordenadas.items()
        }

    def _reconstruir_trayectorias(
        self,
        observaciones_organizadas: dict[int, list[Observacion]],
    ) -> list[Trayectoria]:

        trayectorias: list[Trayectoria] = []
        for id_peaton, observaciones in observaciones_organizadas.items():
            trayectorias.append(Trayectoria(id_peaton, observaciones))

        return trayectorias
