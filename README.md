# pc-lab1-pipeline

Pipeline para el laboratorio 1 de Programación Científica.

## Requisitos

- **Python** `>= 3.10`. Para revisar la versión instalada: `python3 --version`.
- No se necesitan librerías externas: el proyecto solo usa la biblioteca estándar de Python.

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

Cada archivo de la carpeta de datos es un experimento. Empieza con un encabezado que indica su nombre y su frecuencia de muestreo (`# framerate: 25.00`), y luego tiene una fila por observación con las columnas `PersID Frame X Y Z`.

Por defecto, se usa la frecuencia de muestreo indicada en cada archivo. Si se entrega `--fps`, ese valor reemplaza al de los archivos:

```bash
python3 main.py --input ./data --output ./results --fps 25
```