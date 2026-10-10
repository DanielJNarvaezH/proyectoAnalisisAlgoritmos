"""
Modulo CLU-1: Preprocesamiento y matriz de distancia para clustering
===================================================================

Construye la matriz de distancias para los 20 abstracts del corpus
reutilizando la metrica de similitud Coseno con TF-IDF ya testeada.

Como los algoritmos de clustering necesitan una matriz de DISTANCIAS
(0 = identicos), se transforma la similitud coseno mediante:
    distancia = 1.0 - similitud_coseno

La matriz se guarda con precision completa: redondearla crearia empates
artificiales entre distancias distintas, y en el agrupamiento jerarquico
un empate puede cambiar el orden de las fusiones. Solo se redondea al
imprimir.

Ruta del archivo: src/clustering/distance_matrix.py
"""

import json
import os
import sys

RAIZ_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ_SRC not in sys.path:
    sys.path.insert(0, RAIZ_SRC)

from classic.tfidf_cosine import matriz_similitud, vectorizar_tfidf  # noqa: E402

RAIZ_PROYECTO = os.path.abspath(os.path.join(RAIZ_SRC, ".."))
RUTA_CORPUS = os.path.join(RAIZ_PROYECTO, "data", "corpus_preprocesado.json")
RUTA_SALIDA_MATRIZ = os.path.join(RAIZ_PROYECTO, "data", "matriz_distancias_clustering.json")


def construir_matriz_distancias(corpus):
    """
    Retorna (numeros_articulos, matriz_distancias) a partir del corpus
    preprocesado, ordenado por numero de articulo.
    """
    corpus_ordenado = sorted(corpus, key=lambda x: x["numero"])
    numeros_articulos = [doc["numero"] for doc in corpus_ordenado]
    tokens_articulos = [doc["abstract_preprocesado"] for doc in corpus_ordenado]

    # vectorizar_tfidf retorna: (vocabulario, matriz_tfidf)
    _, matriz_tfidf = vectorizar_tfidf(tokens_articulos)
    matriz_sim_coseno = matriz_similitud(matriz_tfidf)

    n = len(matriz_sim_coseno)
    matriz_distancias = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            # Control por posibles flotantes marginales fuera de rango [0, 1]
            matriz_distancias[i][j] = 0.0 if i == j else max(0.0, 1.0 - matriz_sim_coseno[i][j])
    return numeros_articulos, matriz_distancias


def cargar_matriz_distancias(ruta=RUTA_SALIDA_MATRIZ):
    """
    Lee la matriz generada por este modulo. Retorna (numeros_articulos, matriz).
    Es la funcion que usan los algoritmos de clustering (CLU-2, CLU-3, CLU-4).
    """
    with open(ruta, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    return datos["indices_articulos"], datos["matriz"]


def generar_matriz_distancias_clu1():
    print("=== [CLU-1] GENERANDO MATRIZ DE DISTANCIAS PARA CLUSTERING ===")

    if not os.path.exists(RUTA_CORPUS):
        raise FileNotFoundError(f"No se encontro el corpus en {RUTA_CORPUS}. Corre el preprocesamiento primero.")

    with open(RUTA_CORPUS, "r", encoding="utf-8") as archivo:
        corpus = json.load(archivo)

    # El requerimiento especifica trabajar sobre los 20 abstracts
    if len(corpus) != 20:
        print(f"Aviso: El corpus actual contiene {len(corpus)} documentos, el enunciado menciona 20.")

    print(f"Procesando {len(corpus)} documentos secuencialmente...")
    numeros_articulos, matriz_distancias = construir_matriz_distancias(corpus)

    # Estructurar el JSON de salida para que el modulo de clustering sepa que fila es que articulo
    datos_salida = {
        "metric_used": "TF-IDF Cosine Distance (1 - Cosine Similarity)",
        "indices_articulos": numeros_articulos,
        "matriz": matriz_distancias,
    }

    os.makedirs(os.path.dirname(RUTA_SALIDA_MATRIZ), exist_ok=True)
    with open(RUTA_SALIDA_MATRIZ, "w", encoding="utf-8") as f:
        json.dump(datos_salida, f, indent=4, ensure_ascii=False)
    print(f"¡Éxito! Matriz guardada exitosamente en: {RUTA_SALIDA_MATRIZ}")

    # --- Mostrar la Matriz de Distancias COMPLETA (20x20), redondeada solo al imprimir ---
    n = len(matriz_distancias)
    print("\n--- MATRIZ DE DISTANCIAS COMPLETA (20x20) ---")
    encabezado = "Art. ID\t" + "\t".join(f"[{numeros_articulos[i]}]" for i in range(n))
    print(encabezado)
    print("-" * (len(encabezado) + 4))
    for i in range(n):
        fila_str = "\t".join(f"{matriz_distancias[i][j]:.4f}" for j in range(n))
        print(f"[{numeros_articulos[i]}]\t{fila_str}")


if __name__ == "__main__":
    generar_matriz_distancias_clu1()
