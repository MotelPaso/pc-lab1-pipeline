"""Etapa de carga de varios experimentos."""

from pathlib import Path

from models.experimento import Experimento
from models.trayectoria import Trayectoria
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline

from models.observacion import Observacion


class CargaExperimentos(EtapaPipeline[None, list[Experimento]]):
    """Carga una colección de experimentos desde la ruta configurada."""


    def crear_observacion(self, p: list[str]) -> Observacion:

        return Observacion(int(p[0]), int(p[1]), float(p[2]), float(p[3]), float(p[4]))

    def crear_experimento(self, nombre: str, fps: float, observaciones: list[Observacion], trayectorias: list[Trayectoria]) -> Experimento:
        return Experimento(nombre, fps, observaciones, trayectorias)

    def ejecutar(
        self,
        entrada: None,
        contexto: ContextoPipeline,
    ) -> list[Experimento]:
        """Carga los experimentos indicados por la configuración."""

        experimentos = self._cargar_experimentos(contexto.ruta_entrada)
        return experimentos


    def _cargar_experimentos(self, ruta_entrada: Path) -> list[Experimento]:
        """Carga los experimentos disponibles en la ruta recibida."""

        experimentos: list[Experimento] = []

        for archivo in sorted(ruta_entrada.iterdir()):
            if not archivo.is_file() or archivo.name.startswith("."):
                continue

            with archivo.open() as arch:
                print("Archivo: ", nombre_experimento := arch.readline().split()[2])
                print("FPS:     ", fps := float(arch.readline().split()[2]))
                arch.readline()
                arch.readline()

                observaciones: list[Observacion] = []
                descartadas = 0

                for linea in arch:
                    partes = linea.split()
                    if not partes:
                        continue
                    try:
                        observaciones.append(self.crear_observacion(partes))
                    except (ValueError, IndexError):
                        descartadas += 1

                if descartadas:
                    print("Filas descartadas:", descartadas)

            # Las trayectorias se arman después, en PreparacionTrayectorias
            experimentos.append(self.crear_experimento(nombre_experimento, fps, observaciones, []))

        return experimentos