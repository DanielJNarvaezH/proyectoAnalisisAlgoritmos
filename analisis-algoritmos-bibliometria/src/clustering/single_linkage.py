"""
Agrupamiento jerarquico con enlace simple (tarea CLU-2)
=======================================================

Implementacion desde cero del agrupamiento jerarquico aglomerativo con el
criterio de enlace simple (single linkage), sobre la matriz de distancias
de CLU-1 (distancia = 1 - similitud coseno TF-IDF).

Algoritmo:
  1. Cada articulo empieza como un grupo propio (n grupos).
  2. Se busca el par de grupos con la menor distancia y se fusiona.
  3. Se actualiza la distancia del grupo nuevo a cada grupo restante.
  4. Se repite hasta que queda un solo grupo (n - 1 fusiones).

Criterio de enlace simple: la distancia entre dos grupos es la MENOR
distancia entre un elemento de uno y un elemento del otro:

    D(A, B) = min { d(a, b) : a en A, b en B }

Gracias a esa definicion, al fusionar A y B no hace falta recalcular las
distancias desde cero; basta la regla de actualizacion

    D(A u B, C) = min( D(A, C), D(B, C) )

porque el minimo sobre A u B es el menor entre el minimo sobre A y el
minimo sobre B. Las pruebas unitarias verifican que la regla coincide con
la definicion en cada paso.

Complejidad: n - 1 fusiones, cada una con una busqueda O(n^2) del par mas
cercano y una actualizacion O(n): O(n^3) en tiempo y O(n^2) en memoria.
Para n = 20 son unas 2.700 comparaciones.

Identificadores (convencion estandar de los dendrogramas): los elementos
originales son 0 .. n-1 y el grupo creado en el paso t (desde 0) recibe el
identificador n + t. Si dos pares de grupos estan exactamente a la misma
distancia, se fusiona el par con menores identificadores, para que el
resultado sea determinista.

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\clustering\\single_linkage.py
    .\\venv\\Scripts\\python.exe src\\clustering\\single_linkage.py --k 4
"""

import argparse
import json
import os
import sys

RAIZ_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ_SRC not in sys.path:
    sys.path.insert(0, RAIZ_SRC)

from clustering.distance_matrix import RAIZ_PROYECTO, cargar_matriz_distancias  # noqa: E402

RUTA_SALIDA = os.path.join(RAIZ_PROYECTO, "data", "clustering", "single_linkage.json")
TOLERANCIA = 1e-9


# ---------------------------------------------------------------------------
# 1. Validacion de la matriz
# ---------------------------------------------------------------------------

def validar_matriz_distancias(matriz):
    """Exige una matriz cuadrada, simetrica, no negativa y con diagonal cero."""
    n = len(matriz)
    if n < 2:
        raise ValueError("Se necesitan al menos 2 elementos para agrupar")
    for i in range(n):
        if len(matriz[i]) != n:
            raise ValueError("La matriz de distancias debe ser cuadrada")
        if abs(matriz[i][i]) > TOLERANCIA:
            raise ValueError(f"La diagonal debe ser 0 (fila {i})")
        for j in range(n):
            if matriz[i][j] < 0:
                raise ValueError(f"Distancia negativa en ({i}, {j})")
            if abs(matriz[i][j] - matriz[j][i]) > TOLERANCIA:
                raise ValueError(f"La matriz no es simetrica en ({i}, {j})")


# ---------------------------------------------------------------------------
# 2. Criterio de enlace simple
# ---------------------------------------------------------------------------

def distancia_enlace_simple(grupo_a, grupo_b, matriz):
    """
    Definicion directa del criterio: menor distancia entre un elemento de
    grupo_a y uno de grupo_b. Se usa para documentar y verificar la regla
    de actualizacion; el algoritmo principal usa la regla, que es mas eficiente.
    """
    menor = None
    for a in grupo_a:
        for b in grupo_b:
            if menor is None or matriz[a][b] < menor:
                menor = matriz[a][b]
    return menor


def actualizar_enlace_simple(d_a_c, d_b_c):
    """Regla de actualizacion: D(A u B, C) = min(D(A, C), D(B, C))."""
    return d_a_c if d_a_c <= d_b_c else d_b_c


# ---------------------------------------------------------------------------
# 3. Agrupamiento jerarquico aglomerativo
# ---------------------------------------------------------------------------

def single_linkage(matriz):
    """
    Ejecuta el agrupamiento y retorna el historial de las n - 1 fusiones.

    Cada paso es un diccionario con:
      - paso: numero de fusion (desde 1)
      - grupo_a, grupo_b: identificadores de los grupos fusionados (a < b)
      - distancia: distancia de enlace simple entre ellos
      - nuevo_grupo: identificador del grupo creado (n + paso - 1)
      - miembros: indices originales del grupo creado, ordenados
      - tamano: cantidad de elementos del grupo creado
    """
    validar_matriz_distancias(matriz)
    n = len(matriz)

    # Grupos activos: identificador -> lista de indices originales
    activos = {i: [i] for i in range(n)}
    # Distancias entre grupos activos: distancias[x][y]
    distancias = {i: {j: matriz[i][j] for j in range(n) if j != i} for i in range(n)}

    historial = []
    for paso in range(1, n):
        # Buscar el par de grupos mas cercano (en caso de empate, el primero
        # en orden de identificadores, porque solo se reemplaza con '<')
        identificadores = sorted(activos)
        mejor = None
        for x in range(len(identificadores)):
            for y in range(x + 1, len(identificadores)):
                a, b = identificadores[x], identificadores[y]
                if mejor is None or distancias[a][b] < mejor[0]:
                    mejor = (distancias[a][b], a, b)
        distancia, a, b = mejor

        # Fusionar a y b en un grupo nuevo
        nuevo = n + paso - 1
        miembros = sorted(activos.pop(a) + activos.pop(b))

        # Actualizar distancias del grupo nuevo a cada grupo restante
        distancias[nuevo] = {}
        for c in activos:
            d_nueva = actualizar_enlace_simple(distancias[a][c], distancias[b][c])
            distancias[nuevo][c] = d_nueva
            distancias[c][nuevo] = d_nueva
            del distancias[c][a]
            del distancias[c][b]
        del distancias[a]
        del distancias[b]
        activos[nuevo] = miembros

        historial.append({
            "paso": paso,
            "grupo_a": a,
            "grupo_b": b,
            "distancia": distancia,
            "nuevo_grupo": nuevo,
            "miembros": miembros,
            "tamano": len(miembros),
        })
    return historial


def cortar_en_k_grupos(historial, n, k):
    """
    Particion en k grupos: el estado del agrupamiento despues de n - k
    fusiones. Retorna una lista de grupos (listas de indices originales),
    ordenada por el menor indice de cada grupo.
    """
    if not 1 <= k <= n:
        raise ValueError(f"k debe estar entre 1 y {n}")
    grupos = {i: [i] for i in range(n)}
    for fusion in historial[: n - k]:
        grupos[fusion["nuevo_grupo"]] = grupos.pop(fusion["grupo_a"]) + grupos.pop(fusion["grupo_b"])
    return sorted((sorted(g) for g in grupos.values()), key=lambda g: g[0])


# ---------------------------------------------------------------------------
# 4. Ejecucion sobre el corpus
# ---------------------------------------------------------------------------

def _a_articulos(indices, numeros):
    return [numeros[i] for i in indices]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=4,
                        help="Numero de grupos para mostrar la particion (por defecto 4)")
    args = parser.parse_args()

    numeros, matriz = cargar_matriz_distancias()
    n = len(numeros)
    historial = single_linkage(matriz)

    print("=== [CLU-2] AGRUPAMIENTO JERARQUICO: ENLACE SIMPLE ===")
    print(f"Articulos: {n} | Fusiones: {len(historial)}\n")
    print(f"{'Paso':>4}  {'Distancia':>9}  Fusion (articulos)")
    for fusion in historial:
        grupo_a = _a_articulos(
            next((f["miembros"] for f in historial if f["nuevo_grupo"] == fusion["grupo_a"]),
                 [fusion["grupo_a"]]), numeros)
        grupo_b = _a_articulos(
            next((f["miembros"] for f in historial if f["nuevo_grupo"] == fusion["grupo_b"]),
                 [fusion["grupo_b"]]), numeros)
        print(f"{fusion['paso']:>4}  {fusion['distancia']:9.4f}  {grupo_a} + {grupo_b}")

    k = args.k
    print(f"\nParticion en {k} grupos:")
    for i, grupo in enumerate(cortar_en_k_grupos(historial, n, k), start=1):
        print(f"  Grupo {i} ({len(grupo)} articulos): {_a_articulos(grupo, numeros)}")

    os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)
    with open(RUTA_SALIDA, "w", encoding="utf-8") as archivo:
        json.dump({
            "criterio": "single linkage",
            "metrica": "1 - similitud coseno TF-IDF (CLU-1)",
            "indices_articulos": numeros,
            "historial": historial,
        }, archivo, ensure_ascii=False, indent=2)
    print(f"\nHistorial guardado en: {RUTA_SALIDA}")


if __name__ == "__main__":
    main()
