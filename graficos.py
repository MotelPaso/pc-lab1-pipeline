"""Genera los gráficos del informe a partir de los resultados del pipeline.

Lee los CSV que main.py deja en la carpeta de resultados y guarda un PNG por
gráfico. A diferencia del pipeline, este script necesita matplotlib.
"""

import argparse
import csv
from collections import defaultdict
from collections.abc import Callable, Sequence
from math import ceil, isnan, nan
from pathlib import Path
from statistics import fmean, median, pstdev

from matplotlib import patheffects, style
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap, to_rgb
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.typing import ColorType

from pipeline.contexto import ContextoPipeline
from stages import AnalisisEspacial, CargaExperimentos, PreparacionTrayectorias

Fila = dict[str, str]

# Paleta validada para gráficos: contraste y separación para daltonismo sobre blanco
AZUL = "#2a78d6"
AZUL_CLARO = "#cde2fb"
AZUL_MEDIO = "#86b6ef"
AZUL_OSCURO = "#104281"
ROJO = "#e34948"
NEUTRO = "#f0efec"
GRIS = "#c3c2b7"
TINTA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
TINTA_TENUE = "#898781"
GRILLA = "#e1e0d9"

# Ancho de texto de una hoja carta con márgenes de 1 pulgada. Insertadas a ese
# ancho, las figuras conservan el tamaño de letra definido en ESTILO.
ANCHO = 6.5

ESTILO = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
    "font.size": 8,
    "text.color": TINTA,
    "axes.titlesize": 8.5,
    "axes.titlelocation": "left",
    "axes.titlecolor": TINTA,
    "axes.labelsize": 8,
    "axes.labelcolor": TINTA_SECUNDARIA,
    "axes.edgecolor": GRIS,
    "axes.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "axes.axisbelow": True,
    "grid.color": GRILLA,
    "grid.linewidth": 0.6,
    "xtick.color": GRIS,
    "ytick.color": GRIS,
    "xtick.labelcolor": TINTA_SECUNDARIA,
    "ytick.labelcolor": TINTA_SECUNDARIA,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "xtick.major.size": 2.5,
    "ytick.major.size": 0,
    "figure.labelsize": 8,
    "legend.frameon": False,
    "legend.fontsize": 7.5,
    "figure.facecolor": "white",
    "savefig.dpi": 300,
    "lines.solid_capstyle": "round",
    "lines.solid_joinstyle": "round",
}

ESTILO_CAJAS = {
    "patch_artist": True,
    "widths": 0.55,
    "boxprops": {"facecolor": AZUL_CLARO, "edgecolor": AZUL, "linewidth": 0.8},
    "medianprops": {"color": AZUL_OSCURO, "linewidth": 1.4},
    "whiskerprops": {"color": AZUL, "linewidth": 0.8},
    "capprops": {"color": AZUL, "linewidth": 0.8},
    "flierprops": {
        "marker": "o",
        "markersize": 1.5,
        "markerfacecolor": TINTA_TENUE,
        "markeredgewidth": 0,
        "alpha": 0.5,
    },
}


def crear_parser() -> argparse.ArgumentParser:
    """Crea el analizador de argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Gráficos del informe: Análisis de Trayectorias Peatonales."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("./results"),
        help="Directorio con los CSV generados por main.py (por defecto: ./results).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("./results/graficos"),
        help="Directorio donde se guardan los gráficos "
        "(por defecto: ./results/graficos).",
    )
    parser.add_argument(
        "--datos",
        type=Path,
        default=Path("./data"),
        help="Directorio con los datos originales, para dibujar las trayectorias "
        "(por defecto: ./data).",
    )
    return parser


def leer_csv(ruta: Path) -> list[Fila]:
    """Lee un CSV de resultados como una lista de filas."""
    with ruta.open(newline="", encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def agrupar_por_experimento(filas: list[Fila]) -> dict[str, list[Fila]]:
    """Agrupa las filas según su experimento, conservando el orden del archivo."""
    grupos: dict[str, list[Fila]] = defaultdict(list)
    for fila in filas:
        grupos[fila["experimento"]].append(fila)
    return dict(grupos)


def columna(filas: list[Fila], nombre: str) -> list[float]:
    """Extrae los valores numéricos de una columna."""
    return [float(fila[nombre]) for fila in filas]


def numero(experimento: str) -> str:
    """Abrevia el nombre de un experimento a su número: UNI_CORR_500_01 -> 01."""
    return experimento.rsplit("_", 1)[-1]


def sentido_de_marcha(individuales: list[Fila]) -> int:
    """Devuelve 1 si los peatones avanzan hacia x creciente y -1 si no.

    Usa la mediana del avance en x, para que no pesen los peatones que solo
    se observaron en una parte del corredor.
    """
    avances = [
        float(fila["x_final"]) - float(fila["x_inicial"]) for fila in individuales
    ]
    return 1 if median(avances) > 0 else -1


def color_de_texto(fondo: ColorType) -> str:
    """Elige tinta oscura o blanca, la que más contraste con el fondo."""
    r, g, b = (
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        for c in to_rgb(fondo)
    )
    # Sobre esta luminancia, el negro contrasta más que el blanco
    return TINTA if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.179 else "white"


def rotular_puntos(
    eje: Axes,
    nombres: list[str],
    xs: list[float],
    ys: list[float],
) -> None:
    """Rotula cada punto con el número de su experimento.

    Alterna la etiqueta entre arriba a la derecha y abajo a la izquierda según
    el orden en x, para que los experimentos de densidad parecida no se tapen.
    """
    orden = sorted(range(len(xs)), key=lambda i: xs[i])
    for posicion, i in enumerate(orden):
        derecha = posicion % 2 == 0
        eje.annotate(
            numero(nombres[i]),
            (xs[i], ys[i]),
            xytext=(4, 3) if derecha else (-4, -3),
            textcoords="offset points",
            ha="left" if derecha else "right",
            va="bottom" if derecha else "top",
            fontsize=7,
            color=TINTA_SECUNDARIA,
            path_effects=[patheffects.withStroke(linewidth=2.5, foreground="white")],
        )


def ocultar_bordes(eje: Axes) -> None:
    """Oculta los bordes (spines) de un eje."""
    for borde in eje.spines.values():
        borde.set_visible(False)


def formatear_porcentaje(valor: float) -> str:
    """Escribe un porcentaje con un decimal y deja vacíos los ceros."""
    if valor == 0:
        return ""
    return "<0.1" if valor < 0.05 else f"{valor:.1f}"


def graficar_comparacion(experimentos: list[Fila]) -> Figure:
    """Compara los indicadores agregados de cada experimento, uno por panel."""
    indicadores = [
        ("peatones", "Peatones"),
        ("velocidad_media", "Velocidad media (m/s)"),
        ("densidad_media", "Densidad media (personas/m²)"),
        ("flujo", "Flujo (personas/s)"),
        ("distancia_media", "Distancia media (m)"),
        ("tiempo_medio", "Tiempo medio (s)"),
    ]
    figura = Figure(figsize=(ANCHO, 4.2), layout="constrained")
    ejes = figura.subplots(2, 3, sharex=True)
    numeros = [numero(fila["experimento"]) for fila in experimentos]
    for eje, (nombre, titulo) in zip(ejes.flat, indicadores):
        eje.bar(numeros, columna(experimentos, nombre), width=0.6, color=AZUL)
        eje.set_title(titulo)
    for eje in ejes[-1]:
        eje.set_xlabel("Experimento")
    return figura


def graficar_distribuciones(individuales: dict[str, list[Fila]]) -> Figure:
    """Muestra cómo se reparten los indicadores individuales en cada experimento.

    Cada caja va del primer al tercer cuartil y marca la mediana; los puntos son
    peatones que quedan a más de 1.5 rangos intercuartílicos de la caja.
    """
    indicadores = [
        ("velocidad_media", "Velocidad media (m/s)"),
        ("tiempo_total", "Tiempo observado (s)"),
        ("distancia_total", "Distancia recorrida (m)"),
        ("eficiencia", "Eficiencia (desplazamiento / distancia)"),
    ]
    figura = Figure(figsize=(ANCHO, 4.6), layout="constrained")
    ejes = figura.subplots(2, 2, sharex=True)
    numeros = [numero(nombre) for nombre in individuales]
    for eje, (nombre, titulo) in zip(ejes.flat, indicadores):
        valores = [columna(filas, nombre) for filas in individuales.values()]
        eje.boxplot(valores, tick_labels=numeros, **ESTILO_CAJAS)
        eje.set_title(titulo)
    for eje in ejes[-1]:
        eje.set_xlabel("Experimento")
    return figura


def graficar_detenciones(
    experimentos: list[Fila],
    individuales: dict[str, list[Fila]],
) -> Figure:
    """Compara qué parte de los peatones se detiene y cuánto tiempo pasa detenida."""
    numeros = [numero(fila["experimento"]) for fila in experimentos]
    paneles = [
        (
            "Peatones con al menos una detención (%)",
            columna(experimentos, "porcentaje_con_detencion"),
        ),
        (
            "Tiempo detenido, promedio por peatón (%)",
            [
                fmean(columna(individuales[fila["experimento"]], "porcentaje_detenido"))
                for fila in experimentos
            ],
        ),
    ]
    figura = Figure(figsize=(ANCHO, 2.4), layout="constrained")
    ejes = figura.subplots(1, 2, sharex=True)
    for eje, (titulo, valores) in zip(ejes, paneles):
        barras = eje.bar(numeros, valores, width=0.6, color=AZUL)
        eje.bar_label(
            barras,
            labels=[formatear_porcentaje(valor) for valor in valores],
            padding=2,
            fontsize=7,
            color=TINTA_SECUNDARIA,
        )
        eje.margins(y=0.15)
        eje.set_title(titulo)
        eje.set_xlabel("Experimento")
    return figura


def graficar_zonas(
    zonas: dict[str, list[Fila]],
    sentidos: dict[str, int],
    experimentos: list[Fila],
) -> Figure:
    """Muestra la velocidad de cada zona respecto de la media de su experimento.

    Las zonas se ordenan en el sentido de la marcha, de la entrada a la salida,
    porque no todos los experimentos avanzan hacia el mismo lado del corredor.
    """
    inicios = sorted({x for filas in zonas.values() for x in columna(filas, "x_desde")})
    primera = next(iter(zonas.values()))[0]
    ancho_zona = float(primera["x_hasta"]) - float(primera["x_desde"])
    matriz: list[list[float]] = []
    for nombre, filas in zonas.items():
        velocidades = dict(
            zip(columna(filas, "x_desde"), columna(filas, "velocidad_media"))
        )
        media = fmean(velocidades.values())
        relativas = [
            100 * (velocidades[x] / media - 1) if x in velocidades else nan
            for x in inicios
        ]
        if sentidos[nombre] < 0:
            relativas.reverse()
        matriz.append(relativas)

    limite = max(abs(v) for fila in matriz for v in fila if not isnan(v)) or 1
    mapa = LinearSegmentedColormap.from_list("divergente", [ROJO, NEUTRO, AZUL])
    figura = Figure(figsize=(ANCHO, 3.6), layout="constrained")
    eje = figura.subplots()
    imagen = eje.imshow(matriz, cmap=mapa, vmin=-limite, vmax=limite, aspect="auto")
    for i, fila in enumerate(matriz):
        for j, valor in enumerate(fila):
            if not isnan(valor):
                eje.text(
                    j,
                    i,
                    "0" if round(valor) == 0 else f"{valor:+.0f}".replace("-", "−"),
                    ha="center",
                    va="center",
                    fontsize=7,
                    color=color_de_texto(mapa((valor + limite) / (2 * limite))),
                )

    densidades = {
        fila["experimento"]: float(fila["densidad_media"]) for fila in experimentos
    }
    eje.set_xticks(range(len(inicios)), [str(j + 1) for j in range(len(inicios))])
    eje.set_yticks(
        range(len(zonas)),
        [f"{numero(nombre)} ({densidades[nombre]:.2f})" for nombre in zonas],
    )
    eje.set_xlabel(
        f"Tramo de {ancho_zona:g} m en el sentido de la marcha "
        f"(1 = entrada, {len(inicios)} = salida)"
    )
    eje.set_ylabel("Experimento (densidad media, personas/m²)")
    eje.grid(False)
    eje.tick_params(length=0)
    barra = figura.colorbar(imagen, ax=eje, shrink=0.9)
    barra.set_label("Velocidad en el tramo respecto de la media del experimento (%)")
    barra.ax.tick_params(length=0)
    ocultar_bordes(eje)
    ocultar_bordes(barra.ax)
    return figura


def graficar_series(
    series: dict[str, list[Fila]],
    nombre: str,
    titulo_eje: str,
    ventana: float,
) -> Figure:
    """Dibuja la evolución temporal de una métrica, un panel por experimento.

    Cada panel destaca su experimento y deja los demás en gris como referencia.
    Cada punto corresponde al centro de una ventana de tiempo.
    """
    curvas = {
        experimento: (
            [t + ventana / 2 for t in columna(filas, "tiempo_inicio")],
            columna(filas, nombre),
        )
        for experimento, filas in series.items()
    }
    columnas = 3
    filas_paneles = ceil(len(curvas) / columnas)
    figura = Figure(figsize=(ANCHO, 1.5 * filas_paneles + 0.5), layout="constrained")
    ejes = list(
        figura.subplots(
            filas_paneles, columnas, sharex=True, sharey=True, squeeze=False
        ).flat
    )
    for eje, experimento in zip(ejes, curvas):
        for otro, (tiempos, valores) in curvas.items():
            if otro != experimento:
                eje.plot(tiempos, valores, color=GRIS, linewidth=0.6)
        tiempos, valores = curvas[experimento]
        eje.plot(tiempos, valores, color=AZUL, linewidth=1.4)
        eje.set_title(f"Experimento {numero(experimento)}", fontsize=8)
    for eje in ejes[len(curvas):]:
        eje.set_visible(False)
    figura.supxlabel(
        "Tiempo desde el inicio de la grabación (s)", color=TINTA_SECUNDARIA
    )
    figura.supylabel(titulo_eje, color=TINTA_SECUNDARIA)
    return figura


def graficar_diagrama_fundamental(
    experimentos: list[Fila],
    individuales: dict[str, list[Fila]],
    series: dict[str, list[Fila]],
    ventana: float,
) -> Figure:
    """Relaciona la densidad con la velocidad y con el flujo (diagrama fundamental)."""
    nombres = [fila["experimento"] for fila in experimentos]
    densidades = columna(experimentos, "densidad_media")
    velocidades = columna(experimentos, "velocidad_media")
    flujos = columna(experimentos, "flujo")
    desviaciones = [
        pstdev(columna(individuales[nombre], "velocidad_media")) for nombre in nombres
    ]
    ventanas = [fila for filas in series.values() for fila in filas]

    figura = Figure(figsize=(ANCHO, 2.9), layout="constrained")
    velocidad, flujo = figura.subplots(1, 2, sharex=True)
    velocidad.errorbar(
        densidades,
        velocidades,
        yerr=desviaciones,
        fmt="o",
        color=AZUL,
        ecolor=AZUL_MEDIO,
        elinewidth=1,
        markersize=5,
        markeredgecolor="white",
        markeredgewidth=1,
        label="Media del experimento\n± 1 desviación estándar entre peatones",
    )
    rotular_puntos(velocidad, nombres, densidades, velocidades)
    velocidad.set_title("Velocidad según densidad")
    velocidad.set_ylabel("Velocidad media (m/s)")
    velocidad.legend(loc="upper right")

    flujo.scatter(
        columna(ventanas, "densidad"),
        columna(ventanas, "flujo"),
        s=7,
        color=GRIS,
        linewidths=0,
        label=f"Ventana de {ventana:g} s",
    )
    flujo.scatter(
        densidades,
        flujos,
        s=30,
        color=AZUL,
        edgecolors="white",
        linewidths=1,
        zorder=3,
        label="Experimento completo",
    )
    rotular_puntos(flujo, nombres, densidades, flujos)
    flujo.set_title("Flujo según densidad")
    flujo.set_ylabel("Flujo (personas/s)")
    flujo.legend(loc="upper left")

    for eje in (velocidad, flujo):
        eje.set_xlabel("Densidad (personas/m²)")
        eje.set_xlim(left=0)
        eje.set_ylim(bottom=0)
    return figura


def graficar_trayectorias(
    experimentos: list[Fila],
    zonas: dict[str, list[Fila]],
    sentidos: dict[str, int],
    espacial: AnalisisEspacial,
    contexto: ContextoPipeline,
) -> Figure:
    """Dibuja las trayectorias de los experimentos de menor y mayor densidad media.

    Carga los datos originales con las mismas etapas del pipeline y marca el
    área donde se mide la densidad, la línea donde se cuenta el flujo y los
    límites de las zonas.
    """
    ordenados = sorted(experimentos, key=lambda fila: float(fila["densidad_media"]))
    elegidos = {fila["experimento"]: fila for fila in (ordenados[0], ordenados[-1])}
    cargados = CargaExperimentos().ejecutar(None, contexto)
    preparados = PreparacionTrayectorias().ejecutar(
        [experimento for experimento in cargados if experimento.nombre in elegidos],
        contexto,
    )
    limites = sorted(
        {
            x
            for filas in zonas.values()
            for campo in ("x_desde", "x_hasta")
            for x in columna(filas, campo)
        }
    )
    (x_min, x_max), (y_min, y_max) = espacial.area_x, espacial.area_y

    figura = Figure(figsize=(ANCHO, 6.0), layout="constrained")
    ejes = figura.subplots(
        len(preparados), 1, sharex=True, sharey=True, squeeze=False
    )[:, 0]
    for eje, experimento in zip(ejes, preparados):
        segmentos = [
            [(o.x, o.y) for o in trayectoria.observaciones]
            for trayectoria in experimento.trayectorias
        ]
        eje.add_collection(
            LineCollection(segmentos, colors=AZUL, linewidths=0.35, alpha=0.35)
        )
        for x in limites:
            eje.axvline(x, color=GRIS, linewidth=0.6, zorder=0)
        eje.add_patch(
            Rectangle(
                (x_min, y_min),
                x_max - x_min,
                y_max - y_min,
                fill=False,
                edgecolor=TINTA,
                linewidth=1.1,
                zorder=3,
            )
        )
        eje.axvline(espacial.linea_x, color=ROJO, linewidth=1.3, zorder=4)
        # Antes de matplotlib 3.11, add_collection no ajustaba la vista a los datos
        eje.autoscale_view()
        densidad = float(elegidos[experimento.nombre]["densidad_media"])
        flecha = "→" if sentidos[experimento.nombre] > 0 else "←"
        eje.set_title(
            f"Experimento {numero(experimento.nombre)} · "
            f"{len(experimento.trayectorias)} peatones · "
            f"densidad media {densidad:.2f} personas/m² · sentido de marcha {flecha}"
        )
        eje.set_aspect("equal")
        eje.grid(False)
        eje.set_ylabel("y (m)")
    ejes[-1].set_xlabel("x (m)")
    figura.legend(
        handles=[
            Line2D([], [], color=AZUL, linewidth=1, label="Trayectoria de un peatón"),
            Rectangle(
                (0, 0), 1, 1, fill=False, edgecolor=TINTA, linewidth=1.1,
                label="Área de medición de densidad",
            ),
            Line2D(
                [], [], color=ROJO, linewidth=1.3, label="Línea de conteo del flujo"
            ),
            Line2D([], [], color=GRIS, linewidth=0.6, label="Límite entre zonas"),
        ],
        loc="outside lower center",
        ncols=4,
    )
    return figura


def main(argumentos: Sequence[str] | None = None) -> int:
    """Lee los resultados del pipeline y guarda un PNG por gráfico."""
    configuracion = crear_parser().parse_args(argumentos)
    entrada: Path = configuracion.input
    try:
        experimentos = leer_csv(entrada / "resultados_experimentos.csv")
        individuales = agrupar_por_experimento(
            leer_csv(entrada / "resultados_individuales.csv")
        )
        zonas = agrupar_por_experimento(leer_csv(entrada / "resultados_zonas.csv"))
        series = agrupar_por_experimento(leer_csv(entrada / "series_tiempo.csv"))
    except FileNotFoundError as error:
        print(f"No se encontró {error.filename}. Ejecute primero main.py.")
        return 1

    sentidos = {
        nombre: sentido_de_marcha(filas) for nombre, filas in individuales.items()
    }
    # Mismos parámetros por defecto con que main.py crea la etapa espacial
    espacial = AnalisisEspacial()
    ventana = espacial.ventana_serie

    graficos: dict[str, Callable[[], Figure]] = {
        "comparacion_experimentos.png": lambda: graficar_comparacion(experimentos),
        "distribuciones_individuales.png": lambda: graficar_distribuciones(
            individuales
        ),
        "detenciones.png": lambda: graficar_detenciones(experimentos, individuales),
        "velocidad_por_zona.png": lambda: graficar_zonas(zonas, sentidos, experimentos),
        "serie_densidad.png": lambda: graficar_series(
            series, "densidad", "Densidad (personas/m²)", ventana
        ),
        "serie_flujo.png": lambda: graficar_series(
            series, "flujo", "Flujo (personas/s)", ventana
        ),
        "diagrama_fundamental.png": lambda: graficar_diagrama_fundamental(
            experimentos, individuales, series, ventana
        ),
    }
    if configuracion.datos.is_dir():
        contexto = ContextoPipeline(
            ruta_entrada=configuracion.datos, ruta_salida=configuracion.output
        )
        graficos["trayectorias.png"] = lambda: graficar_trayectorias(
            experimentos, zonas, sentidos, espacial, contexto
        )
    else:
        print(
            f"No se encontró {configuracion.datos}: "
            "se omite el gráfico de trayectorias."
        )

    configuracion.output.mkdir(parents=True, exist_ok=True)
    with style.context(ESTILO):
        for nombre, graficar in graficos.items():
            ruta = configuracion.output / nombre
            graficar().savefig(ruta)
            print(f"Gráfico guardado: {ruta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
