"""
Visualizacion de los dendrogramas (tarea VIS-1)
===============================================

Dibuja el dendrograma de cada criterio de enlace a partir de las matrices de
enlace calculadas en CLU-5 (data/clustering/matrices_enlace.json) y guarda
las imagenes en docs/dendrogramas/.

scipy.cluster.hierarchy.dendrogram se usa SOLO para dibujar: los arboles se
calculan desde cero en CLU-2, CLU-3 y CLU-4, y su matriz de enlace se
construye y valida en CLU-5. Por eso este modulo lee el JSON ya generado en
lugar de volver a calcular el agrupamiento.

Decisiones de presentacion:
  - Todas las ramas en un mismo color. Por defecto, scipy colorea las
    uniones que quedan por debajo del 70 % de la altura maxima, lo que en
    este corpus pintaba solo el par 2-6 de Complete Linkage y sugeria un
    grupo especial inexistente.
  - El eje vertical empieza cerca de la primera fusion (no en 0), porque
    todas las fusiones ocurren entre 0,66 y 0,98 y, con el eje desde 0, la
    estructura del arbol quedaba comprimida en la parte superior.
  - Los tres dendrogramas individuales usan la misma escala vertical, y se
    genera ademas una figura comparativa con los tres lado a lado.
  - Las hojas se rotulan con el numero real del articulo, no con su indice.

Uso (desde la raiz del proyecto, despues de ejecutar dendrograma.py):

    .\\venv\\Scripts\\python.exe src\\clustering\\visualizacion.py
"""

import json
import os
import sys

import matplotlib

matplotlib.use("Agg")  # genera imagenes sin abrir ventanas (sirve tambien en un servidor)
import matplotlib.pyplot as plt  # noqa: E402
from scipy.cluster.hierarchy import dendrogram  # noqa: E402

RAIZ_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ_SRC not in sys.path:
    sys.path.insert(0, RAIZ_SRC)

from clustering.dendrograma import RUTA_SALIDA as RUTA_MATRICES  # noqa: E402
from clustering.distance_matrix import RAIZ_PROYECTO  # noqa: E402

CARPETA_IMAGENES = os.path.join(RAIZ_PROYECTO, "docs", "dendrogramas")
COLOR = "#1f4e79"
TITULOS = {
    "single": "Single Linkage (enlace simple)",
    "complete": "Complete Linkage (enlace completo)",
    "average": "Average Linkage (enlace promedio)",
}


def cargar_matrices(ruta=RUTA_MATRICES):
    if not os.path.exists(ruta):
        raise FileNotFoundError(
            f"No se encontro {ruta}. Ejecuta primero src/clustering/dendrograma.py (CLU-5)."
        )
    with open(ruta, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def limites_eje(matrices, margen=0.03):
    """Rango vertical comun a todos los dendrogramas."""
    alturas = [fila[2] for z in matrices.values() for fila in z]
    return min(alturas) - margen, max(alturas) + margen


def dibujar(ax, z, etiquetas, titulo, limites):
    dendrogram(
        z,
        labels=etiquetas,
        ax=ax,
        color_threshold=0,
        above_threshold_color=COLOR,
        leaf_rotation=0,
        leaf_font_size=9,
    )
    ax.set_ylim(*limites)
    ax.set_title(titulo, fontsize=12, fontweight="bold")
    ax.set_xlabel("Numero de articulo")
    ax.set_ylabel("Distancia de fusion (1 - coseno TF-IDF)")
    ax.grid(axis="y", linestyle="--", alpha=0.4)


def main():
    datos = cargar_matrices()
    etiquetas = [str(n) for n in datos["indices_articulos"]]
    matrices = datos["matrices"]
    limites = limites_eje(matrices)
    os.makedirs(CARPETA_IMAGENES, exist_ok=True)

    print("=== [VIS-1] DENDROGRAMAS ===")
    for nombre, z in matrices.items():
        figura, ax = plt.subplots(figsize=(11, 5.5))
        dibujar(ax, z, etiquetas, f"Dendrograma - {TITULOS.get(nombre, nombre)}", limites)
        ruta = os.path.join(CARPETA_IMAGENES, f"{nombre}_linkage.png")
        figura.savefig(ruta, dpi=200, bbox_inches="tight")
        plt.close(figura)
        print(f"Guardado: {ruta}")

    figura, ejes = plt.subplots(1, len(matrices), figsize=(18, 5.5), sharey=True)
    for ax, (nombre, z) in zip(ejes, matrices.items()):
        dibujar(ax, z, etiquetas, TITULOS.get(nombre, nombre), limites)
    for ax in ejes[1:]:
        ax.set_ylabel("")
    figura.suptitle("Comparacion de los tres criterios de enlace (misma escala)",
                    fontsize=13, fontweight="bold")
    ruta = os.path.join(CARPETA_IMAGENES, "comparativa.png")
    figura.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(figura)
    print(f"Guardado: {ruta}")


if __name__ == "__main__":
    main()
