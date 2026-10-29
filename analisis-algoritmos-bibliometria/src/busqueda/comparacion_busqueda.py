"""
Medicion empirica de los algoritmos de busqueda de patrones (tarea BUS-5, R3)
============================================================================

Produce la evidencia del analisis critico del Requerimiento 3
(docs/analisis_busqueda.md): contrasta la complejidad teorica de KMP,
Rabin-Karp y Boyer-Moore con su comportamiento real sobre los 20 abstracts,
separando el PREPROCESAMIENTO del patron de la BUSQUEDA en el texto.

Experimentos:
  1. Preprocesamiento frente a m: tiempo de construir las estructuras
     auxiliares (tabla pi; hash del patron y d^(m-1) mod q; tablas del
     caracter malo y del sufijo bueno) para patrones de longitud creciente.
  2. Corpus: para 8 patrones de distinta longitud, ocurrencias, comparaciones
     de caracteres y tiempo total de buscar en los 20 abstracts. El tiempo de
     busqueda se estima como total - 20 x preprocesamiento, porque cada
     llamada a buscar() reconstruye las tablas del patron.
  3. Escalabilidad frente a n: los 20 abstracts concatenados y repetidos
     1, 2, 4, 8 y 16 veces, con el patron "education".
  4. Peores casos: textos y patrones construidos para llevar a cada
     algoritmo a su cota superior (texto "aaa...a").
  5. Efecto del modulo q de Rabin-Karp sobre las colisiones en el corpus.

Ademas de los tiempos se cuentan las comparaciones de caracteres, una
medida que no depende del equipo. Como referencia se incluye el algoritmo
ingenuo (fuerza bruta), implementado aqui de forma explicita.

Metodologia (la misma del seguimiento, src/ordenamiento/comparacion.py):
time.perf_counter(), ejecuciones de calentamiento que no se cuentan,
algoritmos alternados en cada repeticion y reporte de promedio, desviacion
estandar y minimo.

Resultados: data/resultados/busqueda.json y graficos en docs/busqueda/.

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\busqueda\\comparacion_busqueda.py
    .\\venv\\Scripts\\python.exe src\\busqueda\\comparacion_busqueda.py --rapido
(--rapido usa menos repeticiones, solo para comprobar que todo corre.)
"""

import json
import math
import os
import random
import sys
import time

import matplotlib

matplotlib.use("Agg")  # genera imagenes sin abrir ventanas
import matplotlib.pyplot as plt  # noqa: E402

RAIZ_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(RAIZ_PROYECTO, "src"))

from busqueda import boyer_moore, kmp, rabin_karp  # noqa: E402
from busqueda.verificacion_busqueda import cargar_corpus  # noqa: E402

RUTA_RESULTADOS = os.path.join(RAIZ_PROYECTO, "data", "resultados", "busqueda.json")
CARPETA_GRAFICOS = os.path.join(RAIZ_PROYECTO, "docs", "busqueda")

RAPIDO = "--rapido" in sys.argv
CALENTAMIENTO = 1 if RAPIDO else 3
REPETICIONES_PREPROCESAMIENTO = 20 if RAPIDO else 200
REPETICIONES_CORPUS = 5 if RAPIDO else 30
REPETICIONES_ESCALA = 2 if RAPIDO else 10
REPETICIONES_PEOR_CASO = 2 if RAPIDO else 10

PATRONES = ["AI", "data", "learning", "education", "assessment", "blockchain",
            "artificial intelligence", "generative artificial intelligence"]
LONGITUDES_PREPROCESAMIENTO = [10, 100, 1000, 10000]
ESCALAS = [1, 2, 4, 8, 16]
PATRON_ESCALA = "education"
N_PEOR_CASO = 20000
M_PEOR_CASO = [5, 10, 20, 40]
PRIMOS = [13, 101, rabin_karp.PRIMO]
COLORES = {"Ingenuo": "#9c9c9c", "KMP": "#4c78a8", "Rabin-Karp": "#59a14f", "Boyer-Moore": "#e15759"}


# ---------------------------------------------------------------------------
# 1. Algoritmo ingenuo (solo referencia) y conteo de comparaciones
# ---------------------------------------------------------------------------

def ingenuo_con_estadisticas(texto, patron):
    """Fuerza bruta: prueba cada desplazamiento y compara de izquierda a derecha."""
    n, m = len(texto), len(patron)
    posiciones, comparaciones = [], 0
    for s in range(n - m + 1):
        j = 0
        while j < m:
            comparaciones += 1
            if texto[s + j] != patron[j]:
                break
            j += 1
        if j == m:
            posiciones.append(s)
    return {"posiciones": posiciones, "comparaciones": comparaciones}


BUSQUEDAS = {
    "Ingenuo": ingenuo_con_estadisticas,
    "KMP": kmp.buscar_con_estadisticas,
    "Rabin-Karp": rabin_karp.buscar_con_estadisticas,
    "Boyer-Moore": boyer_moore.buscar_con_estadisticas,
}
ALGORITMOS_R3 = ["KMP", "Rabin-Karp", "Boyer-Moore"]


def preprocesar_kmp(patron):
    return kmp.tabla_prefijos(patron)


def preprocesar_rabin_karp(patron):
    return (rabin_karp.hash_polinomial(patron),
            rabin_karp.potencia_modular(rabin_karp.BASE, len(patron) - 1, rabin_karp.PRIMO))


def preprocesar_boyer_moore(patron):
    return boyer_moore.construir_caracter_malo(patron), boyer_moore.construir_sufijo_bueno(patron)


PREPROCESAMIENTOS = {"KMP": preprocesar_kmp, "Rabin-Karp": preprocesar_rabin_karp,
                     "Boyer-Moore": preprocesar_boyer_moore}


# ---------------------------------------------------------------------------
# 2. Medicion
# ---------------------------------------------------------------------------

def medir_alternando(tareas, repeticiones, calentamiento=CALENTAMIENTO):
    """
    tareas: {nombre: funcion_sin_argumentos}. Alterna las tareas en cada
    repeticion. Retorna {nombre: [tiempo_ms, ...]}.
    """
    for _ in range(calentamiento):
        for funcion in tareas.values():
            funcion()
    tiempos = {nombre: [] for nombre in tareas}
    for _ in range(repeticiones):
        for nombre, funcion in tareas.items():
            inicio = time.perf_counter()
            funcion()
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


def buscar_en_corpus(nombre, textos, patron):
    """Ejecuta un algoritmo sobre todos los textos; retorna (ocurrencias, comparaciones)."""
    ocurrencias, comparaciones = 0, 0
    for texto in textos:
        r = BUSQUEDAS[nombre](texto, patron)
        ocurrencias += len(r["posiciones"])
        comparaciones += r["comparaciones"]
    return ocurrencias, comparaciones


# ---------------------------------------------------------------------------
# 3. Experimentos
# ---------------------------------------------------------------------------

def experimento_preprocesamiento():
    """Tiempo de preprocesamiento frente a m, con patrones aleatorios en minusculas."""
    generador = random.Random(2026)
    resultados = []
    for m in LONGITUDES_PREPROCESAMIENTO:
        patron = "".join(generador.choice("abcdefghijklmnopqrstuvwxyz ") for _ in range(m))
        repeticiones = max(5, REPETICIONES_PREPROCESAMIENTO // max(1, m // 100))
        tareas = {n: (lambda f=f, p=patron: f(p)) for n, f in PREPROCESAMIENTOS.items()}
        tiempos = medir_alternando(tareas, repeticiones)
        fila = {"m": m}
        for nombre in ALGORITMOS_R3:
            fila[nombre] = resumen(tiempos[nombre])
        resultados.append(fila)
    return resultados


def experimento_corpus(textos):
    """Ocurrencias, comparaciones y tiempos sobre los 20 abstracts para cada patron."""
    n_total = sum(len(t) for t in textos)
    resultados = []
    for patron in PATRONES:
        fila = {"patron": patron, "m": len(patron), "n_total": n_total, "algoritmos": {}}
        conteos = {nombre: buscar_en_corpus(nombre, textos, patron) for nombre in BUSQUEDAS}
        ocurrencias = {conteos[nombre][0] for nombre in BUSQUEDAS}
        assert len(ocurrencias) == 1, f"Los algoritmos no coinciden para {patron!r}"
        fila["ocurrencias"] = ocurrencias.pop()

        tareas = {nombre: (lambda nombre=nombre: buscar_en_corpus(nombre, textos, patron))
                  for nombre in BUSQUEDAS}
        tiempos = medir_alternando(tareas, REPETICIONES_CORPUS)
        tareas_pre = {nombre: (lambda f=PREPROCESAMIENTOS[nombre]: f(patron))
                      for nombre in ALGORITMOS_R3}
        tiempos_pre = medir_alternando(tareas_pre, REPETICIONES_PREPROCESAMIENTO)

        for nombre in BUSQUEDAS:
            total = resumen(tiempos[nombre])
            datos = {"comparaciones": conteos[nombre][1],
                     "comparaciones_por_caracter": conteos[nombre][1] / n_total,
                     "total": total}
            if nombre in ALGORITMOS_R3:
                pre = resumen(tiempos_pre[nombre])
                pre_corpus = pre["minimo_ms"] * len(textos)
                datos["preprocesamiento_ms"] = pre["minimo_ms"]
                datos["preprocesamiento_corpus_ms"] = pre_corpus
                datos["busqueda_estimada_ms"] = total["minimo_ms"] - pre_corpus
                datos["porcentaje_preprocesamiento"] = 100 * pre_corpus / total["minimo_ms"]
            fila["algoritmos"][nombre] = datos
        resultados.append(fila)
    return resultados


def experimento_escalabilidad(textos):
    """Tiempo minimo y comparaciones frente a n con el corpus concatenado y repetido."""
    base = " ".join(textos)
    resultados = []
    for factor in ESCALAS:
        texto = " ".join([base] * factor)
        fila = {"factor": factor, "n": len(texto)}
        tareas = {nombre: (lambda nombre=nombre: BUSQUEDAS[nombre](texto, PATRON_ESCALA))
                  for nombre in BUSQUEDAS}
        tiempos = medir_alternando(tareas, REPETICIONES_ESCALA, calentamiento=1)
        for nombre in BUSQUEDAS:
            r = BUSQUEDAS[nombre](texto, PATRON_ESCALA)
            minimo = resumen(tiempos[nombre])["minimo_ms"]
            fila[nombre] = {"minimo_ms": minimo, "us_por_caracter": 1000 * minimo / len(texto),
                            "comparaciones": r["comparaciones"],
                            "comparaciones_por_caracter": r["comparaciones"] / len(texto),
                            "ocurrencias": len(r["posiciones"])}
        resultados.append(fila)
    return resultados


def experimento_peores_casos():
    """
    Texto T = "a" * n con dos patrones:
      - "a" * m: cada ventana es una ocurrencia (n - m + 1 ocurrencias).
        Lleva a Rabin-Karp, al ingenuo y a Boyer-Moore (sin regla de Galil)
        a Theta((n - m + 1) m); KMP sigue siendo lineal.
      - "b" + "a" * (m - 1): ninguna ocurrencia, pero cada ventana coincide en
        m - 1 caracteres. Peor caso del ingenuo si compara de derecha a
        izquierda, y de Boyer-Moore si solo usara el caracter malo.
    """
    texto = "a" * N_PEOR_CASO
    resultados = []
    for m in M_PEOR_CASO:
        for etiqueta, patron in (("a^m", "a" * m), ("b a^(m-1)", "b" + "a" * (m - 1))):
            fila = {"caso": etiqueta, "m": m, "n": N_PEOR_CASO}
            tareas = {nombre: (lambda nombre=nombre, p=patron: BUSQUEDAS[nombre](texto, p))
                      for nombre in BUSQUEDAS}
            tiempos = medir_alternando(tareas, REPETICIONES_PEOR_CASO, calentamiento=1)
            for nombre in BUSQUEDAS:
                r = BUSQUEDAS[nombre](texto, patron)
                fila[nombre] = {"minimo_ms": resumen(tiempos[nombre])["minimo_ms"],
                                "comparaciones": r["comparaciones"],
                                "ocurrencias": len(r["posiciones"])}
            resultados.append(fila)
    return resultados


def experimento_modulo(textos):
    """Colisiones y comparaciones de Rabin-Karp en el corpus segun el modulo q."""
    resultados = []
    for patron in ("education", "learning", "AI"):
        for q in PRIMOS:
            colisiones, comparaciones, ocurrencias = 0, 0, 0
            for texto in textos:
                r = rabin_karp.buscar_con_estadisticas(texto, patron, rabin_karp.BASE, q)
                colisiones += len(r["colisiones"])
                comparaciones += r["comparaciones"]
                ocurrencias += len(r["posiciones"])
            ventanas = sum(max(0, len(t) - len(patron) + 1) for t in textos)
            tiempos = medir_alternando(
                {"rk": lambda q=q, p=patron: [rabin_karp.buscar_con_estadisticas(t, p, rabin_karp.BASE, q)
                                              for t in textos]},
                REPETICIONES_CORPUS)
            resultados.append({"patron": patron, "q": q, "ocurrencias": ocurrencias,
                               "colisiones": colisiones, "colisiones_esperadas": ventanas / q,
                               "comparaciones": comparaciones,
                               "minimo_ms": resumen(tiempos["rk"])["minimo_ms"]})
    return resultados


# ---------------------------------------------------------------------------
# 4. Graficos
# ---------------------------------------------------------------------------

def graficar_corpus(corpus, ruta):
    figura, ejes = plt.subplots(1, 2, figsize=(15, 5.5))
    etiquetas = [f"{f['patron'].replace(' ', chr(10))}\n(m={f['m']})" for f in corpus]
    ancho = 0.2
    for k, nombre in enumerate(BUSQUEDAS):
        x = [i + (k - 1.5) * ancho for i in range(len(corpus))]
        ejes[0].bar(x, [f["algoritmos"][nombre]["total"]["minimo_ms"] for f in corpus],
                    ancho, label=nombre, color=COLORES[nombre])
        ejes[1].bar(x, [f["algoritmos"][nombre]["comparaciones_por_caracter"] for f in corpus],
                    ancho, label=nombre, color=COLORES[nombre])
    for eje, titulo, etiqueta_y in ((ejes[0], "Tiempo minimo en los 20 abstracts", "Tiempo (ms)"),
                                   (ejes[1], "Comparaciones de caracteres por caracter del texto\n"
                                    "(Rabin-Karp: solo verificaciones; ademas hace ~n operaciones de hash)",
                                    "Comparaciones / n")):
        eje.set_xticks(range(len(corpus)))
        eje.set_xticklabels(etiquetas, fontsize=7)
        eje.set_title(titulo)
        eje.set_ylabel(etiqueta_y)
        eje.grid(axis="y", linestyle="--", alpha=0.5)
    ejes[1].axhline(1, color="black", linewidth=0.8, linestyle=":")
    ejes[0].legend()
    figura.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(figura)


def graficar_escalabilidad(escala, ruta):
    figura, ax = plt.subplots(figsize=(8, 5))
    for nombre in BUSQUEDAS:
        ax.plot([f["n"] for f in escala], [f[nombre]["minimo_ms"] for f in escala],
                marker="o", label=nombre, color=COLORES[nombre])
    ax.set_xlabel("Caracteres del texto (n)")
    ax.set_ylabel("Tiempo minimo (ms)")
    ax.set_title(f"Escalabilidad: tiempo frente a n (patron {PATRON_ESCALA!r})")
    ax.grid(linestyle="--", alpha=0.5)
    ax.legend()
    figura.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(figura)


def graficar_preprocesamiento(pre, ruta):
    figura, ax = plt.subplots(figsize=(8, 5))
    for nombre in ALGORITMOS_R3:
        ax.plot([f["m"] for f in pre], [f[nombre]["minimo_ms"] for f in pre],
                marker="o", label=nombre, color=COLORES[nombre])
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Longitud del patron (m)")
    ax.set_ylabel("Tiempo minimo (ms)")
    ax.set_title("Preprocesamiento frente a m (escala log-log; pendiente 1 = lineal)")
    ax.grid(linestyle="--", alpha=0.5, which="both")
    ax.legend()
    figura.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(figura)


def graficar_peores_casos(peores, ruta):
    figura, ax = plt.subplots(figsize=(8, 5))
    filas = [f for f in peores if f["caso"] == "a^m"]
    for nombre in BUSQUEDAS:
        ax.plot([f["m"] for f in filas], [f[nombre]["comparaciones"] for f in filas],
                marker="o", label=nombre, color=COLORES[nombre])
    ax.set_xlabel("Longitud del patron (m)")
    ax.set_ylabel("Comparaciones de caracteres")
    ax.set_title(f"Peor caso: T = a^{N_PEOR_CASO}, P = a^m")
    ax.grid(linestyle="--", alpha=0.5)
    ax.legend()
    figura.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(figura)


# ---------------------------------------------------------------------------
# 5. Ejecucion
# ---------------------------------------------------------------------------

def main():
    corpus = cargar_corpus()
    textos = [a["abstract"] for a in corpus]
    print("=== [BUS-5] MEDICION EMPIRICA DE KMP, RABIN-KARP Y BOYER-MOORE ===")
    print(f"Corpus: {len(textos)} abstracts, {sum(len(t) for t in textos)} caracteres"
          f"{' (modo rapido)' if RAPIDO else ''}\n")

    print("1) Preprocesamiento frente a m (tiempo minimo, ms)")
    pre = experimento_preprocesamiento()
    for f in pre:
        print(f"   m = {f['m']:>6}: " + " | ".join(
            f"{n} {f[n]['minimo_ms']:.4f}" for n in ALGORITMOS_R3))

    print("\n2) Busqueda en los 20 abstracts")
    corp = experimento_corpus(textos)
    for f in corp:
        print(f"   {f['patron']!r} (m = {f['m']}, {f['ocurrencias']} ocurrencias)")
        for nombre in BUSQUEDAS:
            d = f["algoritmos"][nombre]
            extra = (f" | preproc x20 {d['preprocesamiento_corpus_ms']:.4f} ms "
                     f"({d['porcentaje_preprocesamiento']:.1f} %)") if nombre in ALGORITMOS_R3 else ""
            print(f"      {nombre:<12} comp {d['comparaciones']:>6} ({d['comparaciones_por_caracter']:.3f}/car) "
                  f"| min {d['total']['minimo_ms']:.3f} ms | prom {d['total']['promedio_ms']:.3f} "
                  f"+- {d['total']['desviacion_ms']:.3f}{extra}")

    print("\n3) Escalabilidad frente a n (patron 'education', tiempo minimo)")
    esc = experimento_escalabilidad(textos)
    for f in esc:
        print(f"   n = {f['n']:>7}: " + " | ".join(
            f"{n} {f[n]['minimo_ms']:.2f} ms ({f[n]['us_por_caracter']:.3f} us/car, "
            f"{f[n]['comparaciones_por_caracter']:.3f} comp/car)" for n in BUSQUEDAS))

    print(f"\n4) Peores casos (T = 'a' * {N_PEOR_CASO})")
    peor = experimento_peores_casos()
    for f in peor:
        print(f"   P = {f['caso']:<10} m = {f['m']:>2}: " + " | ".join(
            f"{n} {f[n]['comparaciones']} comp, {f[n]['minimo_ms']:.2f} ms" for n in BUSQUEDAS))

    print("\n5) Rabin-Karp: modulo q en el corpus")
    mod = experimento_modulo(textos)
    for f in mod:
        print(f"   {f['patron']!r:<12} q = {f['q']:>13,}: {f['colisiones']:>5} colisiones "
              f"(esperadas {f['colisiones_esperadas']:.1f}) | {f['comparaciones']} comp | "
              f"{f['minimo_ms']:.3f} ms")

    os.makedirs(CARPETA_GRAFICOS, exist_ok=True)
    graficar_preprocesamiento(pre, os.path.join(CARPETA_GRAFICOS, "preprocesamiento.png"))
    graficar_corpus(corp, os.path.join(CARPETA_GRAFICOS, "corpus.png"))
    graficar_escalabilidad(esc, os.path.join(CARPETA_GRAFICOS, "escalabilidad.png"))
    graficar_peores_casos(peor, os.path.join(CARPETA_GRAFICOS, "peor_caso.png"))

    os.makedirs(os.path.dirname(RUTA_RESULTADOS), exist_ok=True)
    with open(RUTA_RESULTADOS, "w", encoding="utf-8") as archivo:
        json.dump({"metodologia": {"calentamiento": CALENTAMIENTO,
                                   "repeticiones_corpus": REPETICIONES_CORPUS,
                                   "repeticiones_escala": REPETICIONES_ESCALA,
                                   "repeticiones_preprocesamiento": REPETICIONES_PREPROCESAMIENTO,
                                   "rapido": RAPIDO},
                   "preprocesamiento": pre, "corpus": corp, "escalabilidad": esc,
                   "peores_casos": peor, "modulo_rabin_karp": mod},
                  archivo, ensure_ascii=False, indent=2)
    print(f"\nResultados guardados en: {RUTA_RESULTADOS}")
    print(f"Graficos guardados en:  {CARPETA_GRAFICOS}")


if __name__ == "__main__":
    main()
