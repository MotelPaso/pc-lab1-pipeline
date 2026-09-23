
from .clases import Observacion

class Sistema:

    def calcular_distancia(pos1:tuple, pos2:tuple) -> float:
        '''
        Calcula la distancia entre dos puntos de la forma (x,y).
        '''
        cuadrado = lambda x : x**2
        return (cuadrado(pos1[0] - pos2[0]) + cuadrado(pos1[1] - pos2[1]))**0.5

    def calcular_intervalo(frame1:int, frame2:int, FPS=25) -> float:
        '''
        Calcula el intervalo entre datos registrados mediante frames,
        con un valor default de 25 FPS.
        '''
        return (frame2 - frame1) / FPS

    def calcular_velocidad_aprox(obs1: Observacion, obs2: Observacion) -> float:

        distancia = Sistema.calcular_distancia(obs1.posicion, obs2.posicion)
        intervalo = Sistema.calcular_intervalo(obs1.frame, obs2.frame)

        return distancia / intervalo
