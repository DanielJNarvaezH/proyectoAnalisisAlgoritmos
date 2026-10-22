"""
Medicion empirica y validacion de los algoritmos de ordenamiento (tarea ORD-5)
==============================================================================

Ejecuta Counting Sort (ORD-2), Radix Sort (ORD-3) y Bucket Sort (ORD-4)
sobre la lista de frecuencias del corpus completo (ORD-1) y produce la
evidencia que pide el seguimiento:

  1. Validacion de resultados: verifica que los tres algoritmos produzcan
     exactamente el mismo ranking completo y muestra el top 15 de cada uno
     lado a lado.
  2. Medicion empirica: tiempo real de ejecucion de cada algoritmo, en
     milisegundos, sobre el corpus completo.
  3. Escalabilidad: tiempo al repetir la lista de terminos 1, 2, 4, 8 y 16
     veces, para contrastar con la complejidad teorica O(n + k): si el tiempo
     crece de forma lineal con n, el tiempo por termino se mantiene constante.
     Aqui se usa el tiempo MINIMO de cada tamano, que es la medicion menos
     afectada por interrupciones del sistema y la que mejor refleja el costo
     propio del algoritmo.

Metodologia de la medicion:
  - Se mide con time.perf_counter(), el reloj de mayor resolucion de Python.
  - Antes de medir se hacen ejecuciones de calentamiento que no se cuentan
    (la primera ejecucion suele ser mas lenta por la carga del codigo).
  - Los algoritmos se ALTERNAN en cada repeticion (Counting, Radix, Bucket,
    Counting, ...), para que una variacion momentanea del equipo afecte a los
    tres por igual y no solo al que se estaba midiendo.
  - Se reportan el promedio, la desviacion estandar y el minimo. El minimo es
    la estimacion menos afectada por interrupciones del sistema operativo.
  - Solo se mide la llamada al ordenamiento; la lectura del corpus y el
    conteo de frecuencias quedan fuera de la medicion.

Resultados: data/resultados/ordenamiento.json y graficos en docs/seguimiento/.

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\ordenamiento\\comparacion.py
"""

import json
import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")  # genera imagenes sin abrir ventanas
import matplotlib.pyplot as plt  # noqa: E402

RAIZ_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ_SRC not in sys.path:
    sys.path.insert(0, RAIZ_SRC)

from ordenamiento.bucket_sort import ordenar_por_frecuencia as bucket_sort  # noqa: E402
from ordenamiento.counting_sort import frecuencia_maxima  # noqa: E402
from ordenamiento.counting_sort import ordenar_por_frecuencia as counting_sort  # noqa: E402
from ordenamiento.frecuencias import RAIZ_PROYECTO, obtener_lista_frecuencias  # noqa: E402
from ordenamiento.radix_sort import ordenar_por_frecuencia as radix_sort  # noqa: E402

ALGORITMOS = {
    "Counting Sort": counting_sort,
    "Radix Sort": radix_sort,
    "Bucket Sort": bucket_sort,
}
TOP = 15
CALENTAMIENTO = 5
REPETICIONES = 100
ESCALAS = [1, 2, 4, 8, 16]
REPETICIONES_ESCALA = 30

RUTA_RESULTADOS = os.path.join(RAIZ_PROYECTO, "data", "resultados", "ordenamiento.json")
CARPETA_GRAFICOS = os.path.join(RAIZ_PROYECTO, "docs", "seguimiento")


# ---------------------------------------------------------------------------
# 1. Medicion
# ---------------------------------------------------------------------------

def medir_alternando(algoritmos, pares, repeticiones, calentamiento=CALENTAMIENTO):
    """
    Tiempos en milisegundos de cada algoritmo, alternandolos en cada
    repeticion. Retorna {nombre: [tiempo_1, ..., tiempo_repeticiones]}.
    """
    for _ in range(calentamiento):
        for funcion in algoritmos.values():
            funcion(pares)

    tiempos = {nombre: [] for nombre in algoritmos}
    for _ in range(repeticiones):
        for nombre, funcion in algoritmos.items():
            inicio = time.perf_counter()
            funcion(pares)
            tiempos[nombre].append((time.perf_counter() - inicio) * 1000)
    return tiempos


def resumen(tiempos):
    """Promedio, desviacion estandar (muestral) y minimo de una lista de tiempos."""
    n = len(tiempos)
    promedio = sum(tiempos) / n
    varianza = sum((t - promedio) ** 2 for t in tiempos) / (n - 1) if n > 1 else 0.0
    minimo = tiempos[0]
    for t in tiempos:
        if t < minimo:
            minimo = t
    return {"promedio_ms": promedio, "desviacion_ms": math.sqrt(varianza), "minimo_ms": minimo}


def escalar(pares, factor):
    """
    Lista de tamano n * factor: la lista original repetida `factor` veces,
    con terminos renombrados para que sean distintos. Conserva la misma
    distribucion de frecuencias y el mismo k, asi que solo cambia n.
    """
    return [(f"{termino}#{copia}", frecuencia)
            for copia in range(factor) for termino, frecuencia in pares]


# ---------------------------------------------------------------------------
# 2. Validacion
# ---------------------------------------------------------------------------

def validar_rankings(algoritmos, pares):
    """Ejecuta los algoritmos y verifica que todos produzcan el mismo ranking."""
    rankings = {nombre: funcion(pares) for nombre, funcion in algoritmos.items()}
    nombres = list(rankings)
    referencia = rankings[nombres[0]]
    for nombre in nombres[1:]:
        if rankings[nombre] != referencia:
            raise AssertionError(f"{nombre} produjo un ranking distinto de {nombres[0]}")
    return rankings


# ---------------------------------------------------------------------------
# 3. Graficos
# ---------------------------------------------------------------------------

def graficar_tiempos(resumenes, ruta):
    nombres = list(resumenes)
    promedios = [resumenes[n]["promedio_ms"] for n in nombres]
    desviaciones = [resumenes[n]["desviacion_ms"] for n in nombres]
    figura, ax = plt.subplots(figsize=(8, 5))
    barras = ax.bar(nombres, promedios, yerr=desviaciones, capsize=6,
                    color=["#4c78a8", "#59a14f", "#e15759"])
    for barra, promedio in zip(barras, promedios):
        ax.annotate(f"{promedio:.3f} ms", (barra.get_x() + barra.get_width() / 2, promedio),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom")
    ax.set_ylabel("Tiempo promedio (ms)")
    ax.set_title(f"Tiempo de ordenamiento del corpus completo "
                 f"({REPETICIONES} repeticiones; barra = desviacion estandar)")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    figura.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(figura)


def graficar_escalabilidad(escalabilidad, ruta):
    figura, ax = plt.subplots(figsize=(8, 5))
    for nombre, puntos in escalabilidad.items():
        ax.plot([p["n"] for p in puntos], [p["minimo_ms"] for p in puntos],
                marker="o", label=nombre)
    ax.set_xlabel("Cantidad de terminos (n)")
    ax.set_ylabel("Tiempo minimo (ms)")
    ax.set_title("Escalabilidad: tiempo frente a n (k constante)")
    ax.grid(linestyle="--", alpha=0.5)
    ax.legend()
    figura.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(figura)


# ---------------------------------------------------------------------------
# 4. Ejecucion
# ---------------------------------------------------------------------------

def main():
    pares = obtener_lista_frecuencias()
    n, k = len(pares), frecuencia_maxima(pares)
    print("=== [ORD-5] MEDICION EMPIRICA Y VALIDACION DE LOS ORDENAMIENTOS ===")
    print(f"Corpus: n = {n} terminos, k = {k}\n")

    # 1. Validacion
    rankings = validar_rankings(ALGORITMOS, pares)
    print(f"1. Validacion: los {len(ALGORITMOS)} algoritmos producen el mismo ranking "
          f"completo ({n} terminos).\n")
    print(f"   Top {TOP} obtenido por cada algoritmo:")
    nombres = list(ALGORITMOS)
    print("   " + f"{'#':>3}  " + "".join(f"{nombre:<22}" for nombre in nombres))
    for i in range(TOP):
        fila = "".join(f"{rankings[nombre][i][0] + ' (' + str(rankings[nombre][i][1]) + ')':<22}"
                       for nombre in nombres)
        print(f"   {i + 1:>3}  {fila}")

    # 2. Tiempos sobre el corpus completo
    tiempos = medir_alternando(ALGORITMOS, pares, REPETICIONES)
    resumenes = {nombre: resumen(t) for nombre, t in tiempos.items()}
    print(f"\n2. Tiempo de ejecucion sobre el corpus completo "
          f"({REPETICIONES} repeticiones, {CALENTAMIENTO} de calentamiento):")
    print(f"   {'Algoritmo':15} {'Promedio (ms)':>14} {'Desv. est. (ms)':>16} {'Minimo (ms)':>12}")
    for nombre, r in resumenes.items():
        print(f"   {nombre:15} {r['promedio_ms']:14.4f} {r['desviacion_ms']:16.4f} "
              f"{r['minimo_ms']:12.4f}")

    # 3. Escalabilidad
    print(f"\n3. Escalabilidad (lista repetida {ESCALAS} veces; k = {k} constante, "
          f"{REPETICIONES_ESCALA} repeticiones; tiempo minimo):")
    print(f"   {'n':>7}  " + "".join(f"{nombre + ' (ms)':>20}" for nombre in nombres)
          + "   us por termino (Counting / Radix / Bucket)")
    escalabilidad = {nombre: [] for nombre in nombres}
    for factor in ESCALAS:
        lista = escalar(pares, factor)
        medidos = medir_alternando(ALGORITMOS, lista, REPETICIONES_ESCALA, calentamiento=2)
        fila_ms, fila_us = "", []
        for nombre in nombres:
            minimo = resumen(medidos[nombre])["minimo_ms"]
            escalabilidad[nombre].append({"n": len(lista), "minimo_ms": minimo})
            fila_ms += f"{minimo:20.4f}"
            fila_us.append(f"{1000 * minimo / len(lista):.3f}")
        print(f"   {len(lista):>7}  {fila_ms}   {' / '.join(fila_us)}")

    # 4. Guardar resultados y graficos
    os.makedirs(CARPETA_GRAFICOS, exist_ok=True)
    graficar_tiempos(resumenes, os.path.join(CARPETA_GRAFICOS, "tiempos_ordenamiento.png"))
    graficar_escalabilidad(escalabilidad, os.path.join(CARPETA_GRAFICOS, "escalabilidad.png"))

    os.makedirs(os.path.dirname(RUTA_RESULTADOS), exist_ok=True)
    with open(RUTA_RESULTADOS, "w", encoding="utf-8") as archivo:
        json.dump({
            "n": n,
            "k": k,
            "repeticiones": REPETICIONES,
            "calentamiento": CALENTAMIENTO,
            "rankings_identicos": True,
            "top": [{"posicion": i + 1, "termino": t, "frecuencia": f}
                    for i, (t, f) in enumerate(rankings[nombres[0]][:TOP])],
            "tiempos": resumenes,
            "escalabilidad": escalabilidad,
        }, archivo, ensure_ascii=False, indent=2)

    print(f"\nGraficos guardados en: {CARPETA_GRAFICOS}")
    print(f"Resultados guardados en: {RUTA_RESULTADOS}")


if __name__ == "__main__":
    main()
