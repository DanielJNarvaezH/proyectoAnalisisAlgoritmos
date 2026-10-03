"""
Analisis comparativo: algoritmos clasicos vs. modelos de IA (tarea CMP-2)
=========================================================================

Genera la evidencia cuantitativa de docs/analisis_comparativo.md:

  1. Distribucion de la similitud en los 190 pares del corpus para cada
     algoritmo, y posicion del caso de estudio (articulos 2 y 9) en ella.
     Esto permite comparar algoritmos con escalas distintas.
  2. Pares que cada algoritmo considera mas parecidos (coherencia semantica).
  3. Concordancia entre algoritmos: correlacion de Spearman sobre los 190 pares
     (si dos algoritmos ordenan los pares de la misma forma, valor cercano a 1).
  4. Tiempos de ejecucion: matriz completa del corpus y un solo par.
  5. (Opcional, requiere los modelos) Tiempo de generacion de embeddings y un
     experimento controlado con frases disenadas para separar la sensibilidad
     lexica de la semantica: sinonimos, orden invertido, negacion y temas
     distintos.

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe notebooks\\analisis_comparativo.py
    .\\venv\\Scripts\\python.exe notebooks\\analisis_comparativo.py --ruta-w2v F:\\modelos-ia\\word2vec-google-news-300.gz

Con --ruta-w2v se cargan los dos modelos (Word2Vec tarda unos minutos) y se
ejecuta la parte 5. Los resultados se guardan en
data/resultados/analisis_comparativo.json.

La correlacion de Spearman, las estadisticas y los rangos son herramientas
del analisis (no algoritmos del Requerimiento 1) y tambien se calculan a mano.
"""

import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from classic.jaccard import jaccard, matriz_jaccard, texto_a_conjunto  # noqa: E402
from classic.levenshtein import levenshtein_similarity  # noqa: E402
from classic.levenshtein import similarity_matrix as matriz_levenshtein  # noqa: E402
from classic.needleman_wunsch import needleman_wunsch_similarity  # noqa: E402
from classic.needleman_wunsch import similarity_matrix as matriz_needleman  # noqa: E402
from classic.tfidf_cosine import matriz_similitud, vectorizar_tfidf  # noqa: E402
from classic.tfidf_cosine import similitud_coseno as coseno_tfidf  # noqa: E402
from comparador import cargar_corpus, cargar_modelos_ia  # noqa: E402
from ia.embeddings_w2v import RAIZ  # noqa: E402
from ia.metricas import matriz, similitud_coseno, similitud_euclidiana  # noqa: E402

CASO = (2, 9)
REPETICIONES_PAR = 20
RUTA_SALIDA = os.path.join(RAIZ, "data", "resultados", "analisis_comparativo.json")

FRASES_EXPERIMENTO = [
    ("Sinonimos (parafrasis)",
     "Students use chatbots to improve their writing skills.",
     "Learners employ conversational agents to enhance their essay composition."),
    ("Orden invertido",
     "The teacher evaluates the artificial intelligence system.",
     "The artificial intelligence system evaluates the teacher."),
    ("Negacion",
     "Generative AI improves student learning outcomes.",
     "Generative AI does not improve student learning outcomes."),
    ("Temas distintos",
     "Generative AI tools support assessment in higher education.",
     "Soil erosion reduces crop yields in tropical regions."),
]


# ---------------------------------------------------------------------------
# Herramientas estadisticas (a mano)
# ---------------------------------------------------------------------------

def media(valores):
    return sum(valores) / len(valores)


def desviacion(valores):
    m = media(valores)
    return math.sqrt(sum((v - m) ** 2 for v in valores) / len(valores))


def rangos(valores):
    """Rango de cada valor (1 = menor); los empates reciben el rango promedio."""
    orden = sorted(range(len(valores)), key=lambda i: valores[i])
    resultado = [0.0] * len(valores)
    i = 0
    while i < len(orden):
        j = i
        while j + 1 < len(orden) and valores[orden[j + 1]] == valores[orden[i]]:
            j += 1
        rango_promedio = (i + j) / 2 + 1
        for k in range(i, j + 1):
            resultado[orden[k]] = rango_promedio
        i = j + 1
    return resultado


def pearson(x, y):
    mx, my = media(x), media(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    return num / den if den else 0.0


def spearman(x, y):
    return pearson(rangos(x), rangos(y))


# ---------------------------------------------------------------------------
# 1-3. Matrices del corpus completo, distribuciones y concordancia
# ---------------------------------------------------------------------------

def calcular_matrices(numeros, corpus, modelos):
    """{algoritmo: (matriz, segundos)} sobre todos los articulos de `numeros`."""
    tokens = [corpus[n]["abstract_preprocesado"] for n in numeros]
    resultado = {}

    def medir(nombre, funcion):
        inicio = time.perf_counter()
        m = funcion()
        resultado[nombre] = (m, time.perf_counter() - inicio)

    medir("Levenshtein", lambda: matriz_levenshtein(tokens))
    medir("Needleman-Wunsch", lambda: matriz_needleman(tokens))
    medir("Coseno TF-IDF", lambda: matriz_similitud(vectorizar_tfidf(tokens)[1]))
    medir("Jaccard", lambda: matriz_jaccard(tokens)[1])
    if "Word2Vec" in modelos:
        v = [modelos["Word2Vec"][n] for n in numeros]
        medir("Word2Vec coseno", lambda: matriz(v, similitud_coseno))
        medir("Word2Vec euclidiana", lambda: matriz(v, similitud_euclidiana))
    if "MPNet" in modelos:
        v = [modelos["MPNet"][n] for n in numeros]
        medir("MPNet coseno", lambda: matriz(v, similitud_coseno))
    return resultado


def pares(m, numeros):
    """Lista de ((a, b), valor) de la mitad superior de la matriz."""
    return [((numeros[i], numeros[j]), m[i][j])
            for i in range(len(numeros)) for j in range(i + 1, len(numeros))]


def analizar_distribucion(lista_pares, caso):
    valores = [v for _, v in lista_pares]
    valor_caso = dict(lista_pares)[caso]
    ordenados = sorted(lista_pares, key=lambda p: p[1], reverse=True)
    posicion = [p for p, _ in ordenados].index(caso) + 1
    return {
        "minimo": min(valores),
        "maximo": max(valores),
        "media": media(valores),
        "desviacion": desviacion(valores),
        "valor_caso": valor_caso,
        "posicion_caso": posicion,
        "total_pares": len(valores),
        "percentil_caso": 100 * sum(1 for v in valores if v < valor_caso) / len(valores),
        "z_caso": (valor_caso - media(valores)) / desviacion(valores),
        "top": [{"par": list(p), "valor": v} for p, v in ordenados[:5]],
    }


# ---------------------------------------------------------------------------
# 4. Tiempo de un solo par
# ---------------------------------------------------------------------------

def tiempos_par(caso, corpus, modelos, repeticiones=REPETICIONES_PAR):
    a = corpus[caso[0]]["abstract_preprocesado"]
    b = corpus[caso[1]]["abstract_preprocesado"]
    funciones = {
        "Levenshtein": lambda: levenshtein_similarity(a, b),
        "Needleman-Wunsch": lambda: needleman_wunsch_similarity(a, b),
        "Coseno TF-IDF": lambda: coseno_tfidf(*vectorizar_tfidf([a, b])[1]),
        "Jaccard": lambda: jaccard(texto_a_conjunto(a), texto_a_conjunto(b)),
    }
    for nombre in ("Word2Vec", "MPNet"):
        if nombre in modelos:
            va, vb = modelos[nombre][caso[0]], modelos[nombre][caso[1]]
            funciones[f"{nombre} coseno"] = (lambda x=va, y=vb: similitud_coseno(x, y))
    resultado = {}
    for nombre, funcion in funciones.items():
        inicio = time.perf_counter()
        for _ in range(repeticiones):
            funcion()
        resultado[nombre] = (time.perf_counter() - inicio) / repeticiones
    return resultado


# ---------------------------------------------------------------------------
# 5. Generacion de embeddings y experimento controlado (requiere modelos)
# ---------------------------------------------------------------------------

def generacion_y_experimento(corpus, ruta_w2v):
    from ia.embeddings_llm import cargar_modelo as cargar_mpnet
    from ia.embeddings_w2v import EXPANSIONES, cargar_modelo as cargar_w2v, vector_documento
    from preprocessing import preprocess_text

    tiempos = {}
    articulos = list(corpus.values())

    inicio = time.perf_counter()
    w2v = cargar_w2v(ruta_modelo=ruta_w2v)
    tiempos["Word2Vec: carga del modelo"] = time.perf_counter() - inicio
    inicio = time.perf_counter()
    for art in articulos:
        vector_documento(art["abstract_preprocesado"], w2v, w2v.vector_size, EXPANSIONES)
    tiempos["Word2Vec: vectorizar 20 abstracts"] = time.perf_counter() - inicio

    inicio = time.perf_counter()
    mpnet = cargar_mpnet()
    tiempos["MPNet: carga del modelo"] = time.perf_counter() - inicio
    inicio = time.perf_counter()
    mpnet.encode([art["abstract"] for art in articulos], show_progress_bar=False)
    tiempos["MPNet: vectorizar 20 abstracts"] = time.perf_counter() - inicio

    experimento = []
    for caso, texto_a, texto_b in FRASES_EXPERIMENTO:
        tok_a, tok_b = preprocess_text(texto_a), preprocess_text(texto_b)
        v_a = vector_documento(tok_a, w2v, w2v.vector_size, EXPANSIONES)["vector"]
        v_b = vector_documento(tok_b, w2v, w2v.vector_size, EXPANSIONES)["vector"]
        e_a, e_b = mpnet.encode([texto_a, texto_b], show_progress_bar=False)
        experimento.append({
            "caso": caso,
            "texto_a": texto_a,
            "texto_b": texto_b,
            "tokens_a": tok_a,
            "tokens_b": tok_b,
            "Levenshtein": levenshtein_similarity(tok_a, tok_b),
            "Needleman-Wunsch": needleman_wunsch_similarity(tok_a, tok_b),
            "Coseno TF-IDF": coseno_tfidf(*vectorizar_tfidf([tok_a, tok_b])[1]),
            "Jaccard": jaccard(texto_a_conjunto(tok_a), texto_a_conjunto(tok_b)),
            "Word2Vec coseno": similitud_coseno(v_a, v_b),
            "MPNet coseno": similitud_coseno([float(x) for x in e_a], [float(x) for x in e_b]),
        })
    return tiempos, experimento


# ---------------------------------------------------------------------------
# Reporte
# ---------------------------------------------------------------------------

def titulo_corto(corpus, n, largo=55):
    titulo = corpus[n]["titulo"].replace("\n", " ")
    return titulo if len(titulo) <= largo else titulo[: largo - 3] + "..."


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ruta-w2v", default=None,
                        help="Ruta del modelo Word2Vec; activa la parte 5")
    args = parser.parse_args()

    corpus = cargar_corpus()
    modelos = cargar_modelos_ia()
    numeros = sorted(corpus)
    salida = {"caso": list(CASO)}

    print("=== 1. DISTRIBUCION EN LOS 190 PARES Y POSICION DEL CASO 2-9 ===")
    print("(TF-IDF usa aqui el IDF de los 20 articulos; en el caso de estudio del")
    print(" Sprint 2 se calculo solo con los 2 articulos, por eso su valor cambia)\n")
    matrices = calcular_matrices(numeros, corpus, modelos)
    distribuciones, lista_por_algoritmo = {}, {}
    print(f"{'Algoritmo':22} {'Min':>7} {'Max':>7} {'Media':>7} {'Desv':>7} "
          f"{'Caso':>7} {'Pos.':>8} {'Perc.':>6} {'z':>6}")
    for nombre, (m, _) in matrices.items():
        lista = pares(m, numeros)
        lista_por_algoritmo[nombre] = lista
        d = analizar_distribucion(lista, CASO)
        distribuciones[nombre] = d
        print(f"{nombre:22} {d['minimo']:7.4f} {d['maximo']:7.4f} {d['media']:7.4f} "
              f"{d['desviacion']:7.4f} {d['valor_caso']:7.4f} "
              f"{d['posicion_caso']:>3}/{d['total_pares']:<4} {d['percentil_caso']:5.1f}% "
              f"{d['z_caso']:6.2f}")
    salida["distribuciones"] = distribuciones

    print("\n=== 2. LOS 5 PARES MAS PARECIDOS SEGUN CADA ALGORITMO ===")
    for nombre, d in distribuciones.items():
        print(f"\n{nombre}:")
        for item in d["top"]:
            a, b = item["par"]
            print(f"  {a:>2}-{b:<2} {item['valor']:.4f}  | {titulo_corto(corpus, a)}")
            print(f"  {'':5} {'':6}  | {titulo_corto(corpus, b)}")

    print("\n=== 3. CONCORDANCIA ENTRE ALGORITMOS (Spearman sobre los 190 pares) ===")
    nombres = list(lista_por_algoritmo)
    cortos = [n.replace("Needleman-Wunsch", "NW").replace("Coseno TF-IDF", "TF-IDF")
              .replace("Levenshtein", "Lev").replace(" coseno", " cos")
              .replace(" euclidiana", " euc").replace("Word2Vec", "W2V") for n in nombres]
    print(f"{'':10}" + "".join(f"{c:>10}" for c in cortos))
    concordancia = {}
    for i, n1 in enumerate(nombres):
        fila = []
        for n2 in nombres:
            rho = spearman([v for _, v in lista_por_algoritmo[n1]],
                           [v for _, v in lista_por_algoritmo[n2]])
            fila.append(rho)
            concordancia.setdefault(n1, {})[n2] = rho
        print(f"{cortos[i]:10}" + "".join(f"{r:10.3f}" for r in fila))
    salida["spearman"] = concordancia

    print("\n=== 4. TIEMPOS DE EJECUCION (solo el calculo de similitud) ===")
    t_par = tiempos_par(CASO, corpus, modelos)
    print(f"{'Algoritmo':22} {'Matriz 20x20 (s)':>17} {'Un par, 2-9 (ms)':>17}")
    tiempos = {}
    for nombre, (_, segundos) in matrices.items():
        ms_par = t_par[nombre] * 1000 if nombre in t_par else None
        tiempos[nombre] = {"matriz_20x20_s": segundos, "par_ms": ms_par}
        par_txt = f"{ms_par:17.3f}" if ms_par is not None else f"{'-':>17}"
        print(f"{nombre:22} {segundos:17.4f} {par_txt}")
    salida["tiempos_similitud"] = tiempos

    if args.ruta_w2v:
        print("\n=== 5a. TIEMPO DE GENERACION DE EMBEDDINGS ===")
        t_gen, experimento = generacion_y_experimento(corpus, args.ruta_w2v)
        for nombre, segundos in t_gen.items():
            print(f"{nombre:36} {segundos:9.2f} s")
        salida["tiempos_generacion"] = t_gen

        print("\n=== 5b. EXPERIMENTO CONTROLADO: SENSIBILIDAD LEXICA VS SEMANTICA ===")
        columnas = ["Levenshtein", "Needleman-Wunsch", "Coseno TF-IDF", "Jaccard",
                    "Word2Vec coseno", "MPNet coseno"]
        for fila in experimento:
            print(f"\n{fila['caso']}:")
            print(f"  A: {fila['texto_a']}\n     tokens: {fila['tokens_a']}")
            print(f"  B: {fila['texto_b']}\n     tokens: {fila['tokens_b']}")
            print("  " + "  ".join(f"{c.split()[0][:11]}={fila[c]:.3f}" for c in columnas))
        salida["experimento"] = experimento
    else:
        print("\n(Parte 5 omitida: ejecuta con --ruta-w2v para medir la generacion de")
        print(" embeddings y correr el experimento controlado)")

    os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)
    with open(RUTA_SALIDA, "w", encoding="utf-8") as archivo:
        json.dump(salida, archivo, ensure_ascii=False, indent=2)
    print(f"\nResultados guardados en: {RUTA_SALIDA}")


if __name__ == "__main__":
    main()
