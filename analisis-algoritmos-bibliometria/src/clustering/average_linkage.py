"""
Agrupamiento jerarquico con enlace promedio (tarea CLU-4)
=========================================================

Criterio de enlace promedio (average linkage, tambien llamado UPGMA): la
distancia entre dos grupos es el PROMEDIO de las distancias entre todos los
pares formados por un elemento de cada grupo:

    D(A, B) = ( sum { d(a, b) : a en A, b en B } ) / ( |A| * |B| )

Al fusionar A y B, la distancia a otro grupo C se actualiza con la regla
de Lance-Williams para este criterio:

    D(A u B, C) = ( |A| * D(A, C) + |B| * D(B, C) ) / ( |A| + |B| )

Por que funciona: |A| * |C| * D(A, C) es la SUMA de las distancias entre A
y C, y lo mismo para B. La suma entre A u B y C es la suma de ambas, y el
numero de pares es (|A| + |B|) * |C|. Al dividir, |C| se cancela y queda la
formula anterior: un promedio de D(A, C) y D(B, C) ponderado por el tamano
de cada grupo. Las pruebas unitarias verifican que la regla coincide con la
definicion en cada paso.

Comportamiento esperado: es un punto intermedio entre el enlace simple
(minimo) y el completo (maximo). La distancia entre grupos considera a
todos sus elementos, de modo que no se deja arrastrar por un unico par muy
cercano (efecto cadena) ni por un unico par muy lejano.

El procedimiento aglomerativo (busqueda del par mas cercano, fusion,
historial) esta en aglomerativo.py, compartido con los otros criterios.
Complejidad: O(n^3) en tiempo y O(n^2) en memoria.

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\clustering\\average_linkage.py
    .\\venv\\Scripts\\python.exe src\\clustering\\average_linkage.py --k 4
"""

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
    Se usa para documentar y verificar la regla de actualizacion; el
    algoritmo usa la regla, que es mas eficiente.
    """
    if not grupo_a or not grupo_b:
        raise ValueError("Los grupos no pueden estar vacios")

    suma_distancias = 0.0
    for a in grupo_a:
        for b in grupo_b:
            suma_distancias += matriz[a][b]

    total_pares = len(grupo_a) * len(grupo_b)
    return suma_distancias / total_pares


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
