"""
Implementación manual de TF-IDF y similitud coseno
====================================================

Este módulo construye la vectorización TF-IDF "desde cero", sin usar
librerías que lo hagan automáticamente (como TfidfVectorizer de sklearn),
y calcula la similitud coseno entre los vectores resultantes.

Solo se usan librerías estándar de Python (math, re, collections) para
operaciones básicas; toda la lógica de TF, IDF y similitud coseno está
implementada manualmente.
"""

import re
import math
from collections import Counter


def tokenizar(texto):
    """
    Convierte un texto en una lista de tokens (palabras) en minúsculas,
    eliminando signos de puntuación y caracteres no alfanuméricos.
    """
    texto = texto.lower()
    # Solo conserva letras (incluye acentos y ñ), números y espacios
    texto = re.sub(r"[^a-záéíóúñü0-9\s]", " ", texto)
    tokens = texto.split()
    return tokens


def calcular_tf(tokens):
    """
    Calcula la frecuencia de término (TF) para un documento.

    TF(t, d) = (número de veces que aparece t en d) / (total de términos en d)

    Retorna un diccionario {termino: tf}.
    """
    total_terminos = len(tokens)
    conteo = Counter(tokens)
    tf = {termino: cuenta / total_terminos for termino, cuenta in conteo.items()}
    return tf


def calcular_idf(documentos_tokenizados):
    """
    Calcula la frecuencia inversa de documento (IDF) para cada término
    presente en el corpus.

    IDF(t) = log( N / (1 + df(t)) ) + 1

    Donde:
      - N es el número total de documentos
      - df(t) es el número de documentos que contienen el término t

    Se usa la variante "suavizada" (+1 en el denominador y +1 al final)
    para evitar división por cero y evitar que términos presentes en
    todos los documentos tengan IDF = 0.

    Retorna un diccionario {termino: idf}.
    """
    N = len(documentos_tokenizados)
    df = Counter()

    for tokens in documentos_tokenizados:
        terminos_unicos = set(tokens)
        for termino in terminos_unicos:
            df[termino] += 1

    idf = {}
    for termino, frecuencia_doc in df.items():
        idf[termino] = math.log(N / (1 + frecuencia_doc)) + 1

    return idf


def construir_vocabulario(documentos_tokenizados):
    """
    Construye el vocabulario global (lista ordenada de términos únicos)
    a partir de todos los documentos del corpus.
    """
    vocabulario = set()
    for tokens in documentos_tokenizados:
        vocabulario.update(tokens)
    return sorted(vocabulario)


def vectorizar_tfidf(corpus):
    """
    Construye manualmente la matriz TF-IDF para un corpus de documentos.

    Parámetros
    ----------
    corpus : list[str]
        Lista de documentos (cada uno como una cadena de texto).

    Retorna
    -------
    vocabulario : list[str]
        Lista ordenada de términos que forman las columnas de la matriz.
    matriz_tfidf : list[list[float]]
        Matriz donde cada fila es el vector TF-IDF de un documento,
        alineado con el orden de 'vocabulario'.
    """
    # 1. Tokenizar todos los documentos
    documentos_tokenizados = [tokenizar(doc) for doc in corpus]

    # 2. Construir vocabulario global
    vocabulario = construir_vocabulario(documentos_tokenizados)

    # 3. Calcular IDF para cada término del vocabulario
    idf = calcular_idf(documentos_tokenizados)

    # 4. Calcular TF-IDF para cada documento
    matriz_tfidf = []
    for tokens in documentos_tokenizados:
        tf = calcular_tf(tokens)
        vector = []
        for termino in vocabulario:
            tf_termino = tf.get(termino, 0.0)
            idf_termino = idf.get(termino, 0.0)
            vector.append(tf_termino * idf_termino)
        matriz_tfidf.append(vector)

    return vocabulario, matriz_tfidf


def similitud_coseno(vector_a, vector_b):
    """
    Calcula la similitud coseno entre dos vectores numéricos.

    similitud = (A . B) / (||A|| * ||B||)

    Retorna un valor entre 0 y 1 (0 = totalmente distintos,
    1 = idénticos en dirección). Si alguno de los vectores es nulo
    (norma 0), retorna 0.0 para evitar división por cero.
    """
    if len(vector_a) != len(vector_b):
        raise ValueError("Los vectores deben tener la misma dimensión")

    producto_punto = sum(a * b for a, b in zip(vector_a, vector_b))
    norma_a = math.sqrt(sum(a ** 2 for a in vector_a))
    norma_b = math.sqrt(sum(b ** 2 for b in vector_b))

    if norma_a == 0 or norma_b == 0:
        return 0.0

    return producto_punto / (norma_a * norma_b)


def matriz_similitud(matriz_tfidf):
    """
    Calcula la matriz de similitud coseno entre todos los pares de
    documentos de una matriz TF-IDF.

    Retorna una lista de listas (matriz cuadrada N x N), donde N es
    el número de documentos.
    """
    n_docs = len(matriz_tfidf)
    matriz = [[0.0] * n_docs for _ in range(n_docs)]

    for i in range(n_docs):
        for j in range(n_docs):
            matriz[i][j] = similitud_coseno(matriz_tfidf[i], matriz_tfidf[j])

    return matriz


# ---------------------------------------------------------------------
# Ejemplo de uso
# ---------------------------------------------------------------------
if __name__ == "__main__":
    corpus = [
        "El perro corre en el parque",
        "El gato duerme en la casa",
        "El perro y el gato juegan en el parque",
    ]

    vocabulario, matriz_tfidf = vectorizar_tfidf(corpus)

    print("Vocabulario:")
    print(vocabulario)
    print()

    print("Matriz TF-IDF (una fila por documento):")
    for i, vector in enumerate(matriz_tfidf):
        vector_redondeado = [round(v, 4) for v in vector]
        print(f"Doc {i + 1}: {vector_redondeado}")
    print()

    print("Similitud coseno entre documentos:")
    matriz_sim = matriz_similitud(matriz_tfidf)
    for i, fila in enumerate(matriz_sim):
        fila_redondeada = [round(v, 4) for v in fila]
        print(f"Doc {i + 1}: {fila_redondeada}")

    print()
    print(f"Similitud entre Doc 1 y Doc 3: {similitud_coseno(matriz_tfidf[0], matriz_tfidf[2]):.4f}")