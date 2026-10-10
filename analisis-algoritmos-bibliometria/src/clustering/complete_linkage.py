"""
Agrupamiento jerarquico con enlace completo (tarea CLU-3)
=========================================================

Criterio de enlace completo (complete linkage): la distancia entre dos
grupos es la MAYOR distancia entre un elemento de uno y un elemento del otro:

    D(A, B) = max { d(a, b) : a en A, b en B }

Al fusionar A y B, la distancia a otro grupo C se actualiza con

    D(A u B, C) = max( D(A, C), D(B, C) )

porque el maximo sobre A u B es el mayor entre el maximo sobre A y el
maximo sobre B. Las pruebas unitarias verifican que la regla coincide con
la definicion en cada paso.

Comportamiento esperado: dos grupos solo se unen cuando TODOS sus elementos
estan relativamente cerca entre si, porque la distancia la decide el par
mas lejano. Por eso tiende a formar grupos compactos y de tamano parecido,
al contrario del efecto cadena del enlace simple. Ademas, la distancia de
cada fusion es el diametro del grupo creado (la mayor distancia interna).

El procedimiento aglomerativo (busqueda del par mas cercano, fusion,
historial) esta en aglomerativo.py, compartido con los otros criterios.
Complejidad: O(n^3) en tiempo y O(n^2) en memoria.

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\clustering\\complete_linkage.py
    .\\venv\\Scripts\\python.exe src\\clustering\\complete_linkage.py --k 4
"""

import argparse
import os
import sys

RAIZ_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ_SRC not in sys.path:
    sys.path.insert(0, RAIZ_SRC)

from clustering.aglomerativo import agrupar, ejecutar_sobre_corpus  # noqa: E402


def distancia_enlace_completo(grupo_a, grupo_b, matriz):
    """
    Definicion directa del criterio: mayor distancia entre un elemento de
    grupo_a y uno de grupo_b. Se usa para documentar y verificar la regla
    de actualizacion; el algoritmo usa la regla, que es mas eficiente.
    """
    mayor = None
    for a in grupo_a:
        for b in grupo_b:
            if mayor is None or matriz[a][b] > mayor:
                mayor = matriz[a][b]
    return mayor


def actualizar_enlace_completo(d_a_c, d_b_c, tamano_a=1, tamano_b=1):
    """
    Regla de actualizacion: D(A u B, C) = max(D(A, C), D(B, C)).
    Los tamanos de los grupos no intervienen en este criterio.
    """
    return d_a_c if d_a_c >= d_b_c else d_b_c


def complete_linkage(matriz):
    """Historial de las n - 1 fusiones con el criterio de enlace completo."""
    return agrupar(matriz, actualizar_enlace_completo)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=4,
                        help="Numero de grupos para mostrar la particion (por defecto 4)")
    args = parser.parse_args()
    ejecutar_sobre_corpus("complete linkage", complete_linkage, "complete_linkage.json", args.k)


if __name__ == "__main__":
    main()
