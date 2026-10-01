"""
Metricas de similitud sobre embeddings (tarea IA-4)
===================================================

Similitud coseno y distancia euclidiana entre los vectores generados en
IA-2 (data/embeddings/word2vec.json) e IA-3 (data/embeddings/mpnet.json).

Implementadas a mano con listas, ciclos y math.sqrt, sin numpy ni las
funciones de similitud de gensim o sentence-transformers, porque son
precisamente los algoritmos que pide el Requerimiento 1 y el enunciado no
acepta funciones de alto nivel que los implementen directamente.

Formulas, para dos vectores a y b de dimension n:

    producto punto:      a . b   = sum( a_i * b_i )
    norma:               ||a||   = sqrt( sum( a_i^2 ) )
    similitud coseno:    cos     = (a . b) / (||a|| * ||b||)     en [-1, 1]
    distancia euclidiana:   d    = sqrt( sum( (a_i - b_i)^2 ) )  en [0, inf)
    similitud euclidiana:   s    = 1 / (1 + d)                   en (0, 1]

La similitud euclidiana convierte la distancia (0 = identicos) en una
similitud (1 = identicos) para poder ponerla junto a las demas. Su escala
depende de la magnitud de los vectores de cada modelo, asi que solo es
comparable entre articulos de un mismo modelo, no entre modelos.
"""

import math


def _validar_dimensiones(a, b):
    if len(a) != len(b):
        raise ValueError(
            f"Los vectores tienen dimensiones distintas: {len(a)} y {len(b)}"
        )


def producto_punto(a, b):
    _validar_dimensiones(a, b)
    total = 0.0
    for i in range(len(a)):
        total += a[i] * b[i]
    return total


def norma(a):
    suma_cuadrados = 0.0
    for componente in a:
        suma_cuadrados += componente * componente
    return math.sqrt(suma_cuadrados)


def similitud_coseno(a, b):
    """
    Coseno del angulo entre a y b. Si alguno es el vector cero (un documento
    sin ninguna palabra reconocida por el modelo), el angulo no esta
    definido y se retorna 0.0, el mismo criterio de tfidf_cosine.py.
    """
    _validar_dimensiones(a, b)
    norma_a = norma(a)
    norma_b = norma(b)
    if norma_a == 0.0 or norma_b == 0.0:
        return 0.0
    return producto_punto(a, b) / (norma_a * norma_b)


def distancia_euclidiana(a, b):
    _validar_dimensiones(a, b)
    suma_cuadrados = 0.0
    for i in range(len(a)):
        diferencia = a[i] - b[i]
        suma_cuadrados += diferencia * diferencia
    return math.sqrt(suma_cuadrados)


def similitud_euclidiana(a, b):
    return 1.0 / (1.0 + distancia_euclidiana(a, b))


def matriz(vectores, funcion):
    """
    Matriz n x n con funcion(vectores[i], vectores[j]). Como las tres
    metricas son simetricas, solo se calcula la mitad superior y se copia.
    """
    n = len(vectores)
    resultado = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            valor = funcion(vectores[i], vectores[j])
            resultado[i][j] = valor
            resultado[j][i] = valor
    return resultado


def matrices_embeddings(vectores):
    """
    Las tres matrices de un conjunto de vectores (un modelo):
    similitud coseno, distancia euclidiana y similitud euclidiana.
    """
    return {
        "coseno": matriz(vectores, similitud_coseno),
        "distancia_euclidiana": matriz(vectores, distancia_euclidiana),
        "similitud_euclidiana": matriz(vectores, similitud_euclidiana),
    }
