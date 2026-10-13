"""
Evaluacion interna de los agrupamientos jerarquicos (tarea EVA-1)
=================================================================

Compara la coherencia de los tres criterios de enlace (single, complete y
average) con dos metricas de evaluacion interna, implementadas a mano. Son
"internas" porque solo usan los datos (la matriz de distancias de CLU-1) y
el resultado del agrupamiento, sin etiquetas externas de referencia.

1. Correlacion cofenetica (CPCC, metrica principal)
   La distancia cofenetica c(i, j) entre dos elementos es la altura a la que
   el dendrograma los une por primera vez. La CPCC es la correlacion de
   Pearson entre las distancias originales d(i, j) y las cofeneticas c(i, j)
   sobre todos los pares i < j:

       CPCC = sum((d - d_media) * (c - c_media))
              / sqrt( sum((d - d_media)^2) * sum((c - c_media)^2) )

   Un valor cercano a 1 indica que el arbol conserva fielmente las
   distancias reales. Evalua la jerarquia COMPLETA, sin elegir un numero de
   grupos, por eso es la metrica principal para comparar los dendrogramas.

2. Indice de silueta (metrica complementaria)
   Evalua una PARTICION en k grupos (un corte del arbol). Para cada
   elemento i:
       a(i) = distancia promedio de i a los demas elementos de su grupo
       b(i) = menor distancia promedio de i a los elementos de otro grupo
       s(i) = (b(i) - a(i)) / max(a(i), b(i))
   Si i esta solo en su grupo, s(i) = 0 (convencion de Rousseeuw, 1987).
   El indice es el promedio de s(i): va de -1 a 1, y es mayor cuando los
   grupos son compactos y estan bien separados.

Complejidad: la matriz cofenetica se construye en O(n^2) recorriendo las
fusiones (cada par se asigna una sola vez); la CPCC es O(n^2); la silueta
de una particion es O(n^2).

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\clustering\\evaluacion.py
"""

import json
import math
import os
import sys

RAIZ_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ_SRC not in sys.path:
    sys.path.insert(0, RAIZ_SRC)

from clustering.aglomerativo import CARPETA_SALIDA, cortar_en_k_grupos  # noqa: E402
from clustering.dendrograma import ALGORITMOS, construir_matriz_enlace  # noqa: E402
from clustering.distance_matrix import cargar_matriz_distancias  # noqa: E402

RUTA_SALIDA = os.path.join(CARPETA_SALIDA, "evaluacion.json")
K_MINIMO = 2
K_MAXIMO = 8


# ---------------------------------------------------------------------------
# 1. Correlacion cofenetica
# ---------------------------------------------------------------------------

def matriz_cofenetica(z, n):
    """
    Matriz n x n de distancias cofeneticas a partir de la matriz de enlace.

    Se recorren las fusiones en orden: cuando se unen los grupos A y B a
    altura h, todos los pares (a, b) con a en A y b en B quedan unidos por
    primera vez, asi que c(a, b) = h. Cada par se asigna exactamente una vez.
    """
    miembros = {i: [i] for i in range(n)}
    c = [[0.0] * n for _ in range(n)]
    for t, (a, b, altura, _) in enumerate(z):
        grupo_a, grupo_b = miembros.pop(int(a)), miembros.pop(int(b))
        for i in grupo_a:
            for j in grupo_b:
                c[i][j] = altura
                c[j][i] = altura
        miembros[n + t] = grupo_a + grupo_b
    return c


def pares_superiores(matriz):
    """Valores de la mitad superior (i < j) en orden de filas."""
    n = len(matriz)
    return [matriz[i][j] for i in range(n) for j in range(i + 1, n)]


def correlacion_pearson(x, y):
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("Se necesitan dos listas de la misma longitud (al menos 2 valores)")
    media_x = sum(x) / len(x)
    media_y = sum(y) / len(y)
    covarianza = 0.0
    varianza_x = 0.0
    varianza_y = 0.0
    for xi, yi in zip(x, y):
        covarianza += (xi - media_x) * (yi - media_y)
        varianza_x += (xi - media_x) ** 2
        varianza_y += (yi - media_y) ** 2
    if varianza_x == 0 or varianza_y == 0:
        raise ValueError("La correlacion no esta definida si una variable es constante")
    return covarianza / math.sqrt(varianza_x * varianza_y)


def correlacion_cofenetica(distancias, z):
    """CPCC entre la matriz de distancias original y la cofenetica del arbol z."""
    cofenetica = matriz_cofenetica(z, len(distancias))
    return correlacion_pearson(pares_superiores(distancias), pares_superiores(cofenetica))


# ---------------------------------------------------------------------------
# 2. Indice de silueta
# ---------------------------------------------------------------------------

def silueta_por_elemento(distancias, grupos):
    """
    s(i) de cada elemento para una particion `grupos` (lista de listas de
    indices). Retorna una lista indexada por elemento.
    """
    n = len(distancias)
    grupo_de = {}
    for g, grupo in enumerate(grupos):
        for i in grupo:
            grupo_de[i] = g
    if sorted(grupo_de) != list(range(n)):
        raise ValueError("La particion debe contener cada elemento exactamente una vez")

    s = [0.0] * n
    for i in range(n):
        propio = grupos[grupo_de[i]]
        if len(propio) == 1:
            continue  # convencion: s(i) = 0 para un elemento solo en su grupo
        a = sum(distancias[i][j] for j in propio if j != i) / (len(propio) - 1)
        b = None
        for g, grupo in enumerate(grupos):
            if g == grupo_de[i]:
                continue
            promedio = sum(distancias[i][j] for j in grupo) / len(grupo)
            if b is None or promedio < b:
                b = promedio
        mayor = a if a > b else b
        s[i] = (b - a) / mayor if mayor > 0 else 0.0
    return s


def indice_silueta(distancias, grupos):
    """Promedio de s(i) sobre todos los elementos. Requiere 2 <= k <= n - 1."""
    if not 2 <= len(grupos) <= len(distancias) - 1:
        raise ValueError("La silueta requiere entre 2 y n - 1 grupos")
    s = silueta_por_elemento(distancias, grupos)
    return sum(s) / len(s)


# ---------------------------------------------------------------------------
# 3. Evaluacion de los tres criterios sobre el corpus
# ---------------------------------------------------------------------------

def evaluar(distancias, algoritmos=ALGORITMOS, k_minimo=K_MINIMO, k_maximo=K_MAXIMO):
    """
    Retorna {criterio: {"cpcc", "silueta": {k: valor}, "grupos": {k: grupos}}}.
    """
    n = len(distancias)
    resultado = {}
    for nombre, algoritmo in algoritmos.items():
        historial = algoritmo(distancias)
        z = construir_matriz_enlace(historial)
        siluetas, particiones = {}, {}
        for k in range(k_minimo, min(k_maximo, n - 1) + 1):
            grupos = cortar_en_k_grupos(historial, n, k)
            particiones[k] = grupos
            siluetas[k] = indice_silueta(distancias, grupos)
        resultado[nombre] = {
            "cpcc": correlacion_cofenetica(distancias, z),
            "silueta": siluetas,
            "grupos": particiones,
        }
    return resultado


def main():
    numeros, distancias = cargar_matriz_distancias()
    resultado = evaluar(distancias)
    nombres = list(resultado)

    print("=== [EVA-1] EVALUACION INTERNA DE LOS AGRUPAMIENTOS ===\n")
    print("1. Correlacion cofenetica (CPCC): fidelidad del arbol a las distancias")
    for nombre in sorted(nombres, key=lambda x: resultado[x]["cpcc"], reverse=True):
        print(f"   {nombre:10} {resultado[nombre]['cpcc']:.4f}")
    mejor_cpcc = max(nombres, key=lambda x: resultado[x]["cpcc"])
    print(f"   -> Mayor CPCC: {mejor_cpcc}")

    print("\n2. Indice de silueta por numero de grupos k")
    ks = list(resultado[nombres[0]]["silueta"])
    print("   " + f"{'k':>3}" + "".join(f"{n:>11}" for n in nombres))
    for k in ks:
        print("   " + f"{k:>3}" + "".join(f"{resultado[n]['silueta'][k]:11.4f}" for n in nombres))
    for nombre in nombres:
        mejor_k = max(ks, key=lambda k: resultado[nombre]["silueta"][k])
        tamanos = sorted((len(g) for g in resultado[nombre]["grupos"][mejor_k]), reverse=True)
        print(f"   {nombre:10} mejor silueta en k = {mejor_k}: "
              f"{resultado[nombre]['silueta'][mejor_k]:.4f} (tamanos {tamanos})")

    salida = {
        "metrica_distancia": "1 - similitud coseno TF-IDF (CLU-1)",
        "indices_articulos": numeros,
        "criterios": {
            nombre: {
                "cpcc": datos["cpcc"],
                "silueta": {str(k): v for k, v in datos["silueta"].items()},
                "grupos": {str(k): [[numeros[i] for i in g] for g in gs]
                           for k, gs in datos["grupos"].items()},
            }
            for nombre, datos in resultado.items()
        },
    }
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    with open(RUTA_SALIDA, "w", encoding="utf-8") as archivo:
        json.dump(salida, archivo, ensure_ascii=False, indent=2)
    print(f"\nResultados guardados en: {RUTA_SALIDA}")


if __name__ == "__main__":
    main()
