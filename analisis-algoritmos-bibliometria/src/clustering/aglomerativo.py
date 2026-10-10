"""
Nucleo comun del agrupamiento jerarquico aglomerativo
=====================================================

Algoritmo compartido por los tres criterios de enlace del Requerimiento 2
(single_linkage.py, complete_linkage.py y average_linkage.py). Cada criterio
aporta su propia regla para calcular la distancia entre grupos; este modulo
implementa el procedimiento comun:

  1. Cada elemento empieza como un grupo propio (n grupos).
  2. Se busca el par de grupos con la menor distancia y se fusiona.
  3. Se actualiza la distancia del grupo nuevo a cada grupo restante con la
     regla del criterio: D(A u B, C) = regla(D(A, C), D(B, C), |A|, |B|).
  4. Se repite hasta que queda un solo grupo (n - 1 fusiones).

Complejidad: n - 1 fusiones, cada una con una busqueda O(n^2) del par mas
cercano y una actualizacion O(n): O(n^3) en tiempo y O(n^2) en memoria.

Identificadores (convencion estandar de los dendrogramas): los elementos
originales son 0 .. n-1 y el grupo creado en la fusion t (desde 1) recibe
el identificador n + t - 1. Si dos pares de grupos estan exactamente a la
misma distancia, se fusiona el par con menores identificadores, para que el
resultado sea determinista.
"""

import json
import os
import sys

RAIZ_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ_SRC not in sys.path:
    sys.path.insert(0, RAIZ_SRC)

from clustering.distance_matrix import RAIZ_PROYECTO, cargar_matriz_distancias  # noqa: E402

TOLERANCIA = 1e-9
CARPETA_SALIDA = os.path.join(RAIZ_PROYECTO, "data", "clustering")


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
# 2. Agrupamiento
# ---------------------------------------------------------------------------

def agrupar(matriz, regla_actualizacion):
    """
    Ejecuta el agrupamiento y retorna el historial de las n - 1 fusiones.

    `regla_actualizacion(d_a_c, d_b_c, tamano_a, tamano_b)` calcula la
    distancia del grupo fusionado A u B a otro grupo C.

    Cada paso del historial es un diccionario con:
      - paso: numero de fusion (desde 1)
      - grupo_a, grupo_b: identificadores de los grupos fusionados (a < b)
      - distancia: distancia entre ellos segun el criterio
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
        tamano_a, tamano_b = len(activos[a]), len(activos[b])
        miembros = sorted(activos.pop(a) + activos.pop(b))

        # Actualizar distancias del grupo nuevo a cada grupo restante
        distancias[nuevo] = {}
        for c in activos:
            d_nueva = regla_actualizacion(distancias[a][c], distancias[b][c], tamano_a, tamano_b)
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
# 3. Ejecucion sobre el corpus (comun a los tres criterios)
# ---------------------------------------------------------------------------

def ejecutar_sobre_corpus(nombre, funcion_agrupamiento, archivo_salida, k):
    """Carga la matriz de CLU-1, agrupa, imprime el historial y lo guarda."""
    numeros, matriz = cargar_matriz_distancias()
    n = len(numeros)
    historial = funcion_agrupamiento(matriz)

    miembros = {i: [i] for i in range(n)}
    for fusion in historial:
        miembros[fusion["nuevo_grupo"]] = fusion["miembros"]

    def articulos(identificador):
        return [numeros[i] for i in miembros[identificador]]

    print(f"=== AGRUPAMIENTO JERARQUICO: {nombre.upper()} ===")
    print(f"Articulos: {n} | Fusiones: {len(historial)}\n")
    print(f"{'Paso':>4}  {'Distancia':>9}  Fusion (articulos)")
    for fusion in historial:
        print(f"{fusion['paso']:>4}  {fusion['distancia']:9.4f}  "
              f"{articulos(fusion['grupo_a'])} + {articulos(fusion['grupo_b'])}")

    print(f"\nParticion en {k} grupos:")
    for i, grupo in enumerate(cortar_en_k_grupos(historial, n, k), start=1):
        print(f"  Grupo {i} ({len(grupo)} articulos): {[numeros[j] for j in grupo]}")

    ruta = os.path.join(CARPETA_SALIDA, archivo_salida)
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump({
            "criterio": nombre,
            "metrica": "1 - similitud coseno TF-IDF (CLU-1)",
            "indices_articulos": numeros,
            "historial": historial,
        }, archivo, ensure_ascii=False, indent=2)
    print(f"\nHistorial guardado en: {ruta}")
    return historial
