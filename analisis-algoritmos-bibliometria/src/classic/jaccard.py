"""
Implementación manual del coeficiente de Jaccard
==================================================

Este módulo calcula el coeficiente de Jaccard "desde cero" sobre conjuntos
de tokens o n-gramas obtenidos a partir de textos (por ejemplo, abstracts
ya preprocesados). No se usa ninguna librería que calcule la similitud
de forma automática: solo se usan operaciones básicas de conjuntos.

El coeficiente de Jaccard entre dos conjuntos A y B se define como:

    J(A, B) = |A ∩ B| / |A ∪ B|

Donde:
    - |A ∩ B| es el tamaño de la intersección de los conjuntos
    - |A ∪ B| es el tamaño de la unión de los conjuntos

Si ambos conjuntos están vacíos, se define J(A, B) = 0.0 por convención,
para evitar división por cero.
"""

import re


def tokenizar(texto):
    """
    Convierte un texto (por ejemplo, un abstract) en una lista de tokens.

    Si 'texto' ya viene como lista (ej. abstract_preprocesado, ya
    tokenizado en un sprint anterior), solo se normaliza a minúsculas
    sin volver a aplicar limpieza de puntuación.
    """

    if isinstance(texto, list):
        return [str(token).lower() for token in texto]

    texto = texto.lower()
    texto = re.sub(r"[^a-záéíóúñü0-9\s]", " ", texto)
    tokens = texto.split()
    return tokens


def generar_ngramas(tokens, n=1):
    """
    Genera n-gramas a partir de una lista de tokens.

    Parámetros
    ----------
    tokens : list[str]
        Lista de tokens (palabras) ya preprocesados.
    n : int
        Tamaño del n-grama (1 = unigramas, 2 = bigramas, 3 = trigramas, ...).

    Retorna
    -------
    list[tuple[str, ...]]
        Lista de n-gramas, cada uno representado como una tupla de tokens.
        Se usan tuplas (en vez de strings unidos) para evitar ambigüedades
        al reconstruir conjuntos.
    """
    if n <= 0:
        raise ValueError("n debe ser un entero positivo")

    if len(tokens) < n:
        return []

    ngramas = []
    for i in range(len(tokens) - n + 1):
        ngrama = tuple(tokens[i:i + n])
        ngramas.append(ngrama)

    return ngramas


def texto_a_conjunto(texto, n=1):
    """
    Convierte un texto en un conjunto (set) de n-gramas, listo para
    compararse con el coeficiente de Jaccard.

    Parámetros
    ----------
    texto : str
        Texto de entrada (por ejemplo, un abstract preprocesado).
    n : int
        Tamaño de los n-gramas a generar (por defecto 1 = tokens/palabras).

    Retorna
    -------
    set
        Conjunto de n-gramas únicos presentes en el texto.
    """
    tokens = tokenizar(texto)
    ngramas = generar_ngramas(tokens, n)
    return set(ngramas)


def jaccard(conjunto_a, conjunto_b):
    """
    Calcula el coeficiente de Jaccard entre dos conjuntos.

    J(A, B) = |A ∩ B| / |A ∪ B|

    Parámetros
    ----------
    conjunto_a, conjunto_b : set
        Conjuntos de elementos (tokens o n-gramas) a comparar.

    Retorna
    -------
    float
        Valor entre 0.0 y 1.0. 0.0 si ambos conjuntos están vacíos.
    """
    if not isinstance(conjunto_a, set):
        conjunto_a = set(conjunto_a)
    if not isinstance(conjunto_b, set):
        conjunto_b = set(conjunto_b)

    if not conjunto_a and not conjunto_b:
        return 0.0

    interseccion = conjunto_a & conjunto_b
    union = conjunto_a | conjunto_b

    return len(interseccion) / len(union)


def matriz_jaccard(corpus, n=1):
    """
    Calcula la matriz de similitud de Jaccard entre todos los pares de
    documentos (abstracts) de un corpus.

    Parámetros
    ----------
    corpus : list[str]
        Lista de textos (abstracts preprocesados).
    n : int
        Tamaño de los n-gramas a usar para representar cada documento
        (1 = unigramas/palabras, 2 = bigramas, etc.).

    Retorna
    -------
    conjuntos : list[set]
        Lista de conjuntos de n-gramas, uno por documento.
    matriz : list[list[float]]
        Matriz cuadrada N x N con la similitud de Jaccard entre cada
        par de documentos.
    """
    conjuntos = [texto_a_conjunto(doc, n) for doc in corpus]
    n_docs = len(conjuntos)

    matriz = [[0.0] * n_docs for _ in range(n_docs)]
    for i in range(n_docs):
        for j in range(n_docs):
            matriz[i][j] = jaccard(conjuntos[i], conjuntos[j])

    return conjuntos, matriz


# ---------------------------------------------------------------------
# Ejemplo de uso
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # Ejemplo con abstracts ya preprocesados (minúsculas, sin puntuación)
    abstracts = [
        "algoritmos de aprendizaje automático para clasificacion de texto",
        "modelos de aprendizaje profundo aplicados a clasificacion de imagenes",
        "tecnicas de procesamiento de lenguaje natural para analisis de texto",
    ]

    print("=== Jaccard sobre unigramas (n=1) ===")
    conjuntos_1, matriz_1 = matriz_jaccard(abstracts, n=1)
    for i, conjunto in enumerate(conjuntos_1):
        print(f"Doc {i + 1} tokens: {sorted(conjunto)}")
    print()
    for i, fila in enumerate(matriz_1):
        fila_redondeada = [round(v, 4) for v in fila]
        print(f"Doc {i + 1}: {fila_redondeada}")

    print()
    print("=== Jaccard sobre bigramas (n=2) ===")
    conjuntos_2, matriz_2 = matriz_jaccard(abstracts, n=2)
    for i, fila in enumerate(matriz_2):
        fila_redondeada = [round(v, 4) for v in fila]
        print(f"Doc {i + 1}: {fila_redondeada}")

    print()
    print(f"Jaccard (unigramas) entre Doc 1 y Doc 3: {jaccard(conjuntos_1[0], conjuntos_1[2]):.4f}")