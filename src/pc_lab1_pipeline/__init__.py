'''
Interfaz general para el pipeline
'''
from .clases import Observacion

lista_observaciones: list[Observacion] = []


def main() -> None:
    '''
    main
    '''
    print("Hello from pc-lab1-pipeline!")

def cargar_datos(arch) -> None:
    '''
    cargar_datos
    '''
    fps = 0
    i = 0

    for linea in arch:
        linea = linea.strip()

        if linea == "": #saltar vacios
            continue

        if linea.startswith("#"): # Obtener el framerate del archivo
            if "framerate" in linea.lower():
                    obtenerFps = linea.split(":")
                    fps = float(obtenerFps[1].strip())
            continue # Saltar si la linea no tiene "framerate"

        partes = linea.split("\t") # Split de cualquier cantidad de espacios

        if len(partes) < 4: # Saltar la primera linea que no corresponde a los datos
            continue

        try:
            id = int(partes[0])
            frame = int(partes[1])
            pos_x = float(partes[2])
            pos_y = float(partes[3])
        except ValueError:
            continue


        lista_observaciones.append(Observacion(id, pos_x, pos_y, frame))
        i += 1
        print(i, id, frame , pos_x, pos_y)

    print(lista_observaciones)
