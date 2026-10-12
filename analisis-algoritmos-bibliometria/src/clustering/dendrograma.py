"""
Estructura del dendrograma: matriz de enlace (tarea CLU-5)
==========================================================

Convierte el historial de fusiones de cada algoritmo de agrupamiento (CLU-2,
CLU-3, CLU-4) en una MATRIZ DE ENLACE (linkage matrix), el formato estandar
para representar un arbol jerarquico y graficarlo como dendrograma (VIS-1).

La matriz de enlace Z tiene n - 1 filas, una por fusion, en el orden en que
ocurrieron. La fila t (desde 0) describe la creacion del grupo n + t:

    Z[t] = [ grupo_a, grupo_b, distancia, tamano ]

  - grupo_a, grupo_b: identificadores de los grupos fusionados. Los valores
    menores que n son elementos originales (hojas del arbol); un valor
    n + s se refiere al grupo creado en la fila s.
  - distancia: altura de la fusion en el dendrograma.
  - tamano: cantidad de elementos originales del grupo creado.

Es el mismo formato que usa scipy.cluster.hierarchy.dendrogram, que en el
proyecto se usa SOLO para dibujar (VIS-1): el arbol se calcula en CLU-2,
CLU-3 y CLU-4, y su estructura se construye y valida en este modulo.

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\clustering\\dendrograma.py
"""

import json
import os
import sys

RAIZ_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ_SRC not in sys.path:
    sys.path.insert(0, RAIZ_SRC)

from clustering.aglomerativo import CARPETA_SALIDA  # noqa: E402
from clustering.average_linkage import average_linkage  # noqa: E402
from clustering.complete_linkage import complete_linkage  # noqa: E402
from clustering.distance_matrix import cargar_matriz_distancias  # noqa: E402
from clustering.single_linkage import single_linkage  # noqa: E402

RUTA_SALIDA = os.path.join(CARPETA_SALIDA, "matrices_enlace.json")
TOLERANCIA = 1e-12

ALGORITMOS = {
    "single": single_linkage,
    "complete": complete_linkage,
    "average": average_linkage,
}


# ---------------------------------------------------------------------------
# 1. Construccion y validacion de la matriz de enlace
# ---------------------------------------------------------------------------

def construir_matriz_enlace(historial):
    """
    Matriz de enlace a partir del historial de fusiones de aglomerativo.py.
    Los valores se guardan como float, igual que en el formato estandar.
    """
    return [
        [float(f["grupo_a"]), float(f["grupo_b"]), float(f["distancia"]), float(f["tamano"])]
        for f in historial
    ]


def validar_matriz_enlace(z, n):
    """
    Verifica que z represente un arbol jerarquico valido sobre n elementos:
      - tiene n - 1 filas de 4 columnas;
      - cada fila solo usa elementos originales o grupos creados en filas
        anteriores, y cada uno se usa exactamente una vez;
      - el tamano de cada grupo es la suma de los tamanos de sus dos partes;
      - las distancias no decrecen (sin inversiones), condicion necesaria
        para que el dendrograma se dibuje correctamente.
    """
    if len(z) != n - 1:
        raise ValueError(f"La matriz de enlace debe tener {n - 1} filas, tiene {len(z)}")

    tamanos = {i: 1 for i in range(n)}
    usados = set()
    distancia_anterior = None
    for t, fila in enumerate(z):
        if len(fila) != 4:
            raise ValueError(f"La fila {t} debe tener 4 columnas")
        a, b, distancia, tamano = int(fila[0]), int(fila[1]), fila[2], int(fila[3])
        for grupo in (a, b):
            if grupo not in tamanos:
                raise ValueError(f"Fila {t}: el grupo {grupo} todavia no existe")
            if grupo in usados:
                raise ValueError(f"Fila {t}: el grupo {grupo} ya se fusiono antes")
        if a == b:
            raise ValueError(f"Fila {t}: un grupo no se puede fusionar consigo mismo")
        if tamano != tamanos[a] + tamanos[b]:
            raise ValueError(f"Fila {t}: el tamano {tamano} no es {tamanos[a]} + {tamanos[b]}")
        if distancia < 0:
            raise ValueError(f"Fila {t}: distancia negativa")
        if distancia_anterior is not None and distancia < distancia_anterior - TOLERANCIA:
            raise ValueError(f"Fila {t}: la distancia decrece (inversion en el arbol)")
        usados.update((a, b))
        tamanos[n + t] = tamano
        distancia_anterior = distancia


# ---------------------------------------------------------------------------
# 2. Recorrido del arbol
# ---------------------------------------------------------------------------

def orden_de_hojas(z, n):
    """
    Orden de izquierda a derecha de los elementos originales en el
    dendrograma: recorrido en profundidad desde la raiz (el ultimo grupo
    creado), visitando primero grupo_a y luego grupo_b.

    Se usa una pila en lugar de recursion para no depender del limite de
    recursion de Python con arboles grandes.
    """
    raiz = n + len(z) - 1
    orden = []
    pila = [raiz]
    while pila:
        nodo = pila.pop()
        if nodo < n:
            orden.append(nodo)
        else:
            a, b = int(z[nodo - n][0]), int(z[nodo - n][1])
            pila.append(b)  # se apila primero b para visitar a antes
            pila.append(a)
    return orden


def altura_de_union(z, n, i, j):
    """
    Distancia a la que los elementos i y j quedan por primera vez en el
    mismo grupo (su distancia cofenetica): la altura del primer grupo que
    los contiene a ambos.
    """
    grupo_de = {k: k for k in range(n)}
    for t, fila in enumerate(z):
        a, b = int(fila[0]), int(fila[1])
        nuevo = n + t
        for k in range(n):
            if grupo_de[k] in (a, b):
                grupo_de[k] = nuevo
        if grupo_de[i] == grupo_de[j] == nuevo:
            return fila[2]
    raise ValueError("Los elementos nunca se unen")


# ---------------------------------------------------------------------------
# 3. Ejecucion sobre el corpus
# ---------------------------------------------------------------------------

def main():
    numeros, matriz = cargar_matriz_distancias()
    n = len(numeros)

    salida = {
        "formato": "fila t = [grupo_a, grupo_b, distancia, tamano]; "
                   "valores < n son articulos (indice en indices_articulos), "
                   "n + s es el grupo creado en la fila s",
        "metrica": "1 - similitud coseno TF-IDF (CLU-1)",
        "indices_articulos": numeros,
        "matrices": {},
        "orden_hojas": {},
    }

    print("=== [CLU-5] MATRICES DE ENLACE PARA LOS DENDROGRAMAS ===")
    for nombre, algoritmo in ALGORITMOS.items():
        z = construir_matriz_enlace(algoritmo(matriz))
        validar_matriz_enlace(z, n)
        hojas = orden_de_hojas(z, n)
        salida["matrices"][nombre] = z
        salida["orden_hojas"][nombre] = [numeros[i] for i in hojas]

        print(f"\n--- {nombre.upper()} LINKAGE (valida: {n - 1} filas) ---")
        print(f"{'Fila':>4}  {'grupo_a':>7}  {'grupo_b':>7}  {'distancia':>9}  {'tamano':>6}")
        for t, (a, b, d, tam) in enumerate(z):
            print(f"{t:>4}  {int(a):>7}  {int(b):>7}  {d:9.4f}  {int(tam):>6}")
        print(f"Orden de los articulos en el dendrograma: {salida['orden_hojas'][nombre]}")

    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    with open(RUTA_SALIDA, "w", encoding="utf-8") as archivo:
        json.dump(salida, archivo, ensure_ascii=False, indent=2)
    print(f"\nMatrices guardadas en: {RUTA_SALIDA}")


if __name__ == "__main__":
    main()
