"""Modelo básico de una trayectoria peatonal."""

from dataclasses import dataclass, field
from math import fsum, sqrt

from .observacion import Observacion


@dataclass
class Trayectoria:
    """Representa las observaciones y cálculos propios de un peatón."""

    id_peaton: int
    observaciones: list[Observacion] = field(default_factory=list)

    def distancia_entre(self, a: Observacion, b: Observacion) -> float:
        """Distancia euclidiana entre dos observaciones."""
        return sqrt((b.x - a.x)**2 + (b.y - a.y)**2)

    def posicion_inicial(self) -> tuple[float, float]:
        """Devuelve la posición (x, y) de la primera observación."""
        primera = self.observaciones[0]
        return (primera.x, primera.y)

    def posicion_final(self) -> tuple[float, float]:
        """Devuelve la posición (x, y) de la última observación."""
        ultima = self.observaciones[-1]
        return (ultima.x, ultima.y)

    def calcular_tiempo_total(self, fps: float) -> float:
        """Calcula el tiempo observado entre el primer y el último frame."""
        if len(self.observaciones) < 2:
            return 0
        frames = self.observaciones[-1].frame - self.observaciones[0].frame
        return frames/fps

    def calcular_distancia_total(self) -> float:
        """Calcula la distancia total recorrida por el peatón."""
        pares = zip(self.observaciones, self.observaciones[1:])
        return fsum(self.distancia_entre(a, b) for a, b in pares)

    def calcular_desplazamiento(self) -> float:
        """Calcula el desplazamiento entre el inicio y el final."""
        if len(self.observaciones) < 2:
            return 0
        return self.distancia_entre(self.observaciones[0], self.observaciones[-1])

    def calcular_velocidad_media(self, fps: float) -> float:
        """Calcula la velocidad media usando la frecuencia del experimento."""
        tiempo = self.calcular_tiempo_total(fps)
        if tiempo == 0:
            return 0
        return self.calcular_distancia_total()/tiempo
    
    def calcular_velocidad_maxima(self, fps: float) -> float:
        """Calcula la mayor velocidad registrada entre dos observaciones consecutivas."""
        pares = zip(self.observaciones, self.observaciones[1:])
        velocidades = (
            self.distancia_entre(a, b)/((b.frame - a.frame)/fps)
            for a, b in pares
            if b.frame > a.frame
        )
        return max(velocidades, default=0)

    def calcular_eficiencia(self) -> float:
        """Calcula la eficiencia: desplazamiento / distancia total recorrida."""
        distancia = self.calcular_distancia_total()
        if distancia == 0:
            return 0
        eficiencia = self.calcular_desplazamiento()/distancia
        return eficiencia