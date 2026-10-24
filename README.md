# pc-lab1-pipeline

Pipeline para el laboratorio 1 de Programación Cientifica.

## Requisitos

- **Python** `>= 3.14`

## Cómo correrlo

Primero, clonar el repositorio:

```bash
git clone git@github.com:MotelPaso/pc-lab1-pipeline.git
cd pc-lab1-pipeline

```

Luego, para ejecutar el pipeline:

```bash
python3 main.py --input ./data --output ./results
```

Como input, se toma la ruta de la carpeta de los datos.
Como output, se toma la ruta de la carpeta de salida.

Tambien se puede especificar la frecuencia de muestreo:

```bash
python3 main.py --input ./data --output ./results --fps 25
```
