# pc-lab1-pipeline

Pipeline para el laboratorio 1 de Programación Cientifica.

## Requisitos

- **Python** `>= 3.14`
- **uv** (gestor de entornos y dependencias)

## Cómo correrlo

Primero, clonar el repositorio y preparar el entorno:

```bash
git clone git@github.com:MotelPaso/pc-lab1-pipeline.git
cd pc-lab1-pipeline

uv init            # crear el proyecto con uv
source .venv/bin/activate   # activar el entorno virtual
```

Luego, para ejecutar el pipeline:

```bash
python3 main.py --input ./input.txt --output ./output.txt
```

### Modo interactivo

Si se omiten los parámetros `--input` o `--output`, el programa los pedirá por consola.
