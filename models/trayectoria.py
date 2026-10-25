"""Modelo básico de una trayectoria peatonal."""

from dataclasses import dataclass, field
from math import sqrt

from .observacion import Observacion


@dataclass
class Trayectoria:
    """Representa las observaciones y cálculos propios de un peatón."""

    id_peaton: int
    observaciones: list[Observacion] = field(default_factory=list)

    def distancia_entre(self, a: Observacion, b: Observacion) -> float:
        """Distancia euclidiana entre dos observaciones."""
        return sqrt((b.x - a.x)**2 + (b.y - a.y)**2)

    def calcular_distancia_total(self) -> float:
        """Calcula la distancia total recorrida por el peatón."""
        total = 0
        for i in range(len(self.observaciones) - 1):
            total += self.distancia_entre(self.observaciones[i], self.observaciones[i + 1])
        return total

    def calcular_desplazamiento(self) -> float:
        """Calcula el desplazamiento entre el inicio y el final."""
        if len(self.observaciones) < 2:
            return 0
        return self.distancia_entre(self.observaciones[0], self.observaciones[-1])

    def calcular_velocidad_media(self, fps: float) -> float:
        """Calcula la velocidad media usando la frecuencia del experimento."""
        if len(self.observaciones) < 2:
            return 0
        frames = self.observaciones[-1].frame - self.observaciones[0].frame
        tiempo = frames/fps
        if tiempo == 0:
            return 0
        return self.calcular_distancia_total()/tiempo
    
    def calcular_velocidad_maxima(self, fps: float) -> float:
        """Calcula la mayor velocidad registrada entre dos observaciones consecutivas."""
        maxima = 0
        for i in range(len(self.observaciones) - 1):
            primera = self.observaciones[i]
            segunda = self.observaciones[i + 1]
            tiempo = (segunda.frame - primera.frame)/fps
            if tiempo > 0:
                velocidad = self.distancia_entre(primera, segunda)/tiempo
                if velocidad > maxima:
                    maxima = velocidad
        return maxima

    def calcular_eficiencia(self) -> float:
        """Calcula la eficiencia: desplazamiento / distancia total recorrida."""
        distancia = self.calcular_distancia_total()
        if distancia == 0:
            return 0
        eficiencia = self.calcular_desplazamiento()/distancia
        return eficiencia