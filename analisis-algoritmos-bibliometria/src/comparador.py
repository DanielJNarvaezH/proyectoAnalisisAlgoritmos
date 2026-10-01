"""
Comparador integrado del Requerimiento 1 (CLA-5 + IA-4)
=======================================================

Permite seleccionar dinamicamente dos o mas articulos del corpus y calcula
la similitud entre sus abstracts con los 6 algoritmos del Requerimiento 1:

  Clasicos (Sprint 2, sobre `abstract_preprocesado`):
    1. Levenshtein          3. Coseno con TF-IDF
    2. Needleman-Wunsch     4. Jaccard

  IA (Sprint 3, sobre los embeddings precalculados en data/embeddings/):
    5. Word2Vec (IA-2)      6. all-mpnet-base-v2 (IA-3)
    Para cada uno: similitud coseno, distancia euclidiana y similitud
    euclidiana 1 / (1 + d), implementadas a mano en src/ia/metricas.py.

Los embeddings se leen de los archivos JSON: este modulo no carga gensim
ni sentence-transformers, asi que funciona sin los modelos descargados.

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\comparador.py          (pide los articulos)
    .\\venv\\Scripts\\python.exe src\\comparador.py 2 9      (los recibe directo)

La funcion comparar_articulos() hace todo el calculo sin entrada ni salida
por consola, para poder reutilizarla en el backend (DEP-1) y en CMP-1.
"""

import json
import os
import sys

RAIZ_SRC = os.path.abspath(os.path.dirname(__file__))
if RAIZ_SRC not in sys.path:
    sys.path.insert(0, RAIZ_SRC)

from classic.jaccard import matriz_jaccard  # noqa: E402
from classic.levenshtein import similarity_matrix as matriz_levenshtein  # noqa: E402
from classic.needleman_wunsch import similarity_matrix as matriz_needleman  # noqa: E402
from classic.tfidf_cosine import matriz_similitud, vectorizar_tfidf  # noqa: E402
from ia.embeddings_w2v import RAIZ, cargar_embeddings  # noqa: E402
from ia.metricas import matrices_embeddings  # noqa: E402

RUTA_CORPUS = os.path.join(RAIZ, "data", "corpus_preprocesado.json")

# Modelos de IA: nombre para mostrar -> archivo de embeddings
MODELOS_IA = {
    "Word2Vec": os.path.join(RAIZ, "data", "embeddings", "word2vec.json"),
    "MPNet": os.path.join(RAIZ, "data", "embeddings", "mpnet.json"),
}


# ---------------------------------------------------------------------------
# 1. Carga de datos
# ---------------------------------------------------------------------------

def cargar_corpus(ruta=RUTA_CORPUS):
    with open(ruta, "r", encoding="utf-8") as archivo:
        return {doc["numero"]: doc for doc in json.load(archivo)}


def cargar_modelos_ia(rutas=MODELOS_IA):
    """
    Retorna {nombre_modelo: {numero_articulo: vector}} con los modelos cuyo
    archivo existe. Si falta alguno, se avisa y se compara sin el.
    """
    modelos = {}
    for nombre, ruta in rutas.items():
        if os.path.exists(ruta):
            modelos[nombre] = cargar_embeddings(ruta)
        else:
            print(f"Aviso: no se encontro {ruta}; se omite el modelo {nombre}.")
    return modelos


# ---------------------------------------------------------------------------
# 2. Calculo (sin entrada ni salida por consola)
# ---------------------------------------------------------------------------

def comparar_articulos(numeros, corpus, modelos_ia):
    """
    Calcula todas las matrices de similitud para los articulos `numeros`.

    Parametros
    ----------
    numeros : list[int]
        Numeros de los articulos, en el orden en que se mostraran.
    corpus : dict
        {numero: articulo} del corpus preprocesado.
    modelos_ia : dict
        {nombre_modelo: {numero: vector}}, como lo retorna cargar_modelos_ia().

    Retorna
    -------
    dict con "clasicos" ({algoritmo: matriz}) e "ia"
    ({modelo: {"coseno", "distancia_euclidiana", "similitud_euclidiana"}}).
    """
    faltantes = [n for n in numeros if n not in corpus]
    if faltantes:
        raise ValueError(f"Articulos inexistentes en el corpus: {faltantes}")
    if len(numeros) < 2:
        raise ValueError("Se necesitan al menos 2 articulos para comparar")

    tokens = [corpus[n]["abstract_preprocesado"] for n in numeros]
    _, tfidf = vectorizar_tfidf(tokens)
    _, jaccard = matriz_jaccard(tokens)

    resultado = {
        "clasicos": {
            "Levenshtein": matriz_levenshtein(tokens),
            "Needleman-Wunsch": matriz_needleman(tokens),
            "Coseno TF-IDF": matriz_similitud(tfidf),
            "Jaccard": jaccard,
        },
        "ia": {},
    }

    for nombre, vectores in modelos_ia.items():
        sin_vector = [n for n in numeros if n not in vectores]
        if sin_vector:
            raise ValueError(f"El modelo {nombre} no tiene vector para: {sin_vector}")
        resultado["ia"][nombre] = matrices_embeddings([vectores[n] for n in numeros])

    return resultado


def resumen_par(resultado):
    """
    Para una comparacion de exactamente 2 articulos, una fila por algoritmo
    con su similitud (y la distancia euclidiana en los modelos de IA).
    Es la tabla base del caso de estudio (CMP-1).
    """
    filas = []
    for algoritmo, m in resultado["clasicos"].items():
        filas.append({"algoritmo": algoritmo, "tipo": "Clasico",
                      "similitud": m[0][1], "distancia": None})
    for modelo, matrices in resultado["ia"].items():
        filas.append({"algoritmo": f"{modelo} (coseno)", "tipo": "IA",
                      "similitud": matrices["coseno"][0][1],
                      "distancia": matrices["distancia_euclidiana"][0][1]})
        filas.append({"algoritmo": f"{modelo} (euclidiana 1/(1+d))", "tipo": "IA",
                      "similitud": matrices["similitud_euclidiana"][0][1],
                      "distancia": matrices["distancia_euclidiana"][0][1]})
    return filas


# ---------------------------------------------------------------------------
# 3. Salida por consola
# ---------------------------------------------------------------------------

def imprimir_matriz(nombre, matriz, indices):
    print(f"\n--- {nombre} ---")
    encabezado = "Art.\t" + "\t".join(f"[{i}]" for i in indices)
    print(encabezado)
    print("-" * (len(encabezado) + 8))
    for i, fila in enumerate(matriz):
        print(f"[{indices[i]}]\t" + "\t".join(f"{valor:.4f}" for valor in fila))


def imprimir_resultado(numeros, resultado):
    print("\n==================== ALGORITMOS CLASICOS ====================")
    for algoritmo, m in resultado["clasicos"].items():
        imprimir_matriz(f"SIMILITUD {algoritmo.upper()}", m, numeros)

    print("\n================ MODELOS DE IA (EMBEDDINGS) =================")
    for modelo, matrices in resultado["ia"].items():
        imprimir_matriz(f"{modelo.upper()}: SIMILITUD COSENO", matrices["coseno"], numeros)
        imprimir_matriz(f"{modelo.upper()}: DISTANCIA EUCLIDIANA",
                        matrices["distancia_euclidiana"], numeros)
        imprimir_matriz(f"{modelo.upper()}: SIMILITUD EUCLIDIANA 1/(1+d)",
                        matrices["similitud_euclidiana"], numeros)

    if len(numeros) == 2:
        print(f"\n=========== RESUMEN: ARTICULO {numeros[0]} vs ARTICULO {numeros[1]} ===========")
        print(f"{'Algoritmo':32} {'Tipo':8} {'Similitud':>9}  {'Distancia':>9}")
        for fila in resumen_par(resultado):
            distancia = f"{fila['distancia']:.4f}" if fila["distancia"] is not None else "-"
            print(f"{fila['algoritmo']:32} {fila['tipo']:8} "
                  f"{fila['similitud']:>9.4f}  {distancia:>9}")


def leer_numeros(argumentos, disponibles):
    """Numeros desde la linea de comandos o, si no hay, preguntando al usuario."""
    if argumentos:
        texto = " ".join(argumentos)
    else:
        print(f"Articulos disponibles: {disponibles}")
        texto = input("Numeros de los articulos a comparar (ej: 2, 9): ")
    return [int(parte) for parte in texto.replace(",", " ").split()]


def main():
    corpus = cargar_corpus()
    modelos_ia = cargar_modelos_ia()

    print("=== COMPARADOR DE SIMILITUD TEXTUAL (Requerimiento 1) ===")
    try:
        numeros = leer_numeros(sys.argv[1:], sorted(corpus))
        resultado = comparar_articulos(numeros, corpus, modelos_ia)
    except ValueError as error:
        print(f"Error: {error}")
        return

    imprimir_resultado(numeros, resultado)


if __name__ == "__main__":
    main()
