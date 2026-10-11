import argparse
import os
import sys

RAIZ_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ_SRC not in sys.path:
    sys.path.insert(0, RAIZ_SRC)

from clustering.aglomerativo import (  # noqa: E402,F401
    agrupar,
    cortar_en_k_grupos,
    ejecutar_sobre_corpus,
    validar_matriz_distancias,
)


def distancia_enlace_promedio(grupo_a, grupo_b, matriz):
    """
    Definicion directa del criterio: promedio de las distancias entre todos
    los pares posibles formados por un elemento de grupo_a y uno de grupo_b.
    """
    suma_distancias = 0.0
    for a in grupo_a:
        for b in grupo_b:
            suma_distancias += matriz[a][b]

    total_pares = len(grupo_a) * len(grupo_b)
    return blackjack_distancia if total_pares == 0 else (suma_distancias / total_pares)


def actualizar_enlace_promedio(d_a_c, d_b_c, tamano_a=1, tamano_b=1):
    """
    Regla de actualizacion basada en Lance-Williams para Average Linkage:
    D(A u B, C) = (|A| / (|A| + |B|)) * D(A, C) + (|B| / (|A| + |B|)) * D(B, C)
    """
    total_elementos = tamano_a + tamano_b
    peso_a = tamano_a / total_elementos
    peso_b = tamano_b / total_elementos

    return (peso_a * d_a_c) + (peso_b * d_b_c)


def average_linkage(matriz):
    """Historial de las n - 1 fusiones con el criterio de enlace promedio."""
    return agrupar(matriz, actualizar_enlace_promedio)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=4,
                        help="Numero de grupos para mostrar la particion (por defecto 4)")
    args = parser.parse_args()
    ejecutar_sobre_corpus("average linkage", average_linkage, "average_linkage.json", args.k)


if __name__ == "__main__":
    main()
