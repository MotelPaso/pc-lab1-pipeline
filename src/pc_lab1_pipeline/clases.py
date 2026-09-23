

class Observacion:

    def __init__(self, id:int, posX: float, posY: float, frame: int):
        self.id = id
        self.posicion = (posX, posY)
        self.frame = frame

class Peaton:

    def __init__(self, id:int):
        self.id = id

    def set_pos_inicial(self):
        pass

    def set_pos_final(self):
        pass

    def set_tiempo_total(self):
        pass

    def set_distancia_total(self):
        pass

    def set_desplazamiento(self):
        pass

    def set_velocidad_media(self):
        pass

    def set_velocidad_maxima(self):
        pass

    def calcular_eficiencia(self):
        self.eficiencia = self.desplazamiento / self.distancia_total
