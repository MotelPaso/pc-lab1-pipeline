# pc-lab1-pipeline

Pipeline para el laboratorio 1 de Programación Científica.

## Requisitos

- **Python** `>= 3.10`. Para revisar la versión instalada: `python3 --version`.
- El pipeline no necesita librerías externas: solo usa la biblioteca estándar de Python.
- Los gráficos (`graficos.py`) necesitan matplotlib, indicado en `requirements.txt`.

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

## Gráficos

Los gráficos del informe se generan aparte, a partir de los CSV que deja el pipeline. Primero hay que ejecutar `main.py` y después, en un entorno virtual con matplotlib:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python graficos.py --input ./results --output ./results/graficos
```

Como input, se toma la carpeta con los CSV del pipeline; como output, la carpeta donde se guarda un PNG por gráfico. Para dibujar las trayectorias, el script también lee los datos originales de `./data` (se cambia con `--datos`); si esa carpeta no existe, omite ese gráfico.

| Archivo | Contenido |
| --- | --- |
| `trayectorias.png` | Trayectorias de los experimentos de menor y mayor densidad, con el área de densidad, la línea de flujo y las zonas |
| `distribuciones_individuales.png` | Velocidad, tiempo, distancia y eficiencia de cada peatón, por experimento |
| `detenciones.png` | Porcentaje de peatones que se detienen y tiempo detenido promedio |
| `velocidad_por_zona.png` | Velocidad de cada tramo respecto de la media del experimento, de la entrada a la salida |
| `serie_densidad.png` | Densidad en el tiempo, un panel por experimento |
| `serie_flujo.png` | Flujo en el tiempo, un panel por experimento |
| `diagrama_fundamental.png` | Velocidad y flujo según la densidad |
| `comparacion_experimentos.png` | Indicadores agregados de cada experimento |
