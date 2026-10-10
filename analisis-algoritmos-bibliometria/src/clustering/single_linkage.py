"""
Agrupamiento jerarquico con enlace simple (tarea CLU-2)
=======================================================

Criterio de enlace simple (single linkage): la distancia entre dos grupos
es la MENOR distancia entre un elemento de uno y un elemento del otro:

    D(A, B) = min { d(a, b) : a en A, b en B }

Gracias a esa definicion, al fusionar A y B no hace falta recalcular las
distancias desde cero; basta la regla de actualizacion

    D(A u B, C) = min( D(A, C), D(B, C) )

porque el minimo sobre A u B es el menor entre el minimo sobre A y el
minimo sobre B. Las pruebas unitarias verifican que la regla coincide con
la definicion en cada paso.

Comportamiento esperado: basta con que UN par de elementos este cerca para
unir dos grupos completos, lo que produce el "efecto cadena": grupos
alargados que van absorbiendo elementos uno a uno.

El procedimiento aglomerativo (busqueda del par mas cercano, fusion,
historial) esta en aglomerativo.py, compartido con los otros criterios.
Complejidad: O(n^3) en tiempo y O(n^2) en memoria.

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\clustering\\single_linkage.py
    .\\venv\\Scripts\\python.exe src\\clustering\\single_linkage.py --k 4
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


def distancia_enlace_simple(grupo_a, grupo_b, matriz):
    """
    Definicion directa del criterio: menor distancia entre un elemento de
    grupo_a y uno de grupo_b. Se usa para documentar y verificar la regla
    de actualizacion; el algoritmo usa la regla, que es mas eficiente.
    """
    menor = None
    for a in grupo_a:
        for b in grupo_b:
            if menor is None or matriz[a][b] < menor:
                menor = matriz[a][b]
    return menor


def actualizar_enlace_simple(d_a_c, d_b_c, tamano_a=1, tamano_b=1):
    """
    Regla de actualizacion: D(A u B, C) = min(D(A, C), D(B, C)).
    Los tamanos de los grupos no intervienen en este criterio.
    """
    return d_a_c if d_a_c <= d_b_c else d_b_c


def single_linkage(matriz):
    """Historial de las n - 1 fusiones con el criterio de enlace simple."""
    return agrupar(matriz, actualizar_enlace_simple)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=4,
                        help="Numero de grupos para mostrar la particion (por defecto 4)")
    args = parser.parse_args()
    ejecutar_sobre_corpus("single linkage", single_linkage, "single_linkage.json", args.k)


if __name__ == "__main__":
    main()
