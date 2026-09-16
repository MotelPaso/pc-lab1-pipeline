import pc_lab1_pipeline
import sys
import os

def main() -> None:
    file_name = ""
    output_name = ""

    if len(sys.argv) > 1: # commandline exec
        try:
            if "--input" in sys.argv:
                file_name:str = sys.argv[sys.argv.index("--input") + 1]
            if "--output" in sys.argv:
                output_name:str = sys.argv[sys.argv.index("--output") + 1]
        except:
            print("Ha habido un problema con el ingreso de los datos...\nIntente por modo interactivo")

    file_name = input("Ingrese nombre del input: ") if file_name == "" else file_name

    if os.path.isfile(file_name):
        with open(file_name, 'r', encoding="utf-8") as arch:
            pc_lab1_pipeline.cargar_datos(arch)
    else:
        print("No es un input valido...")
        sys.exit()

    print("Datos cargados!")

    output_name = input("Ingrese nombre del output: ") if output_name == "" else output_name


if __name__ == "__main__":
    main()
