"""
Requerimiento 1 - Algoritmo Clásico de Similitud: Distancia de Levenshtein
============================================================================

Implementado desde cero con programación dinámica (sin usar librerías que
resuelvan el algoritmo directamente, como python-Levenshtein, rapidfuzz, etc.).

La distancia de Levenshtein entre dos secuencias A (largo n) y B (largo m)
es el número mínimo de operaciones de edición (inserción, eliminación,
sustitución) necesarias para transformar A en B.

Funciona tanto a nivel de caracteres (si se le pasan strings) como a nivel
de palabras/tokens (si se le pasan listas), porque solo depende de la
comparación de igualdad entre elementos de las secuencias.

Recurrencia utilizada:
    D[i][0] = i                                   (borrar los primeros i elementos de A)
    D[0][j] = j                                   (insertar los primeros j elementos de B)
    D[i][j] = D[i-1][j-1]                         si A[i-1] == B[j-1]
    D[i][j] = 1 + min(D[i-1][j],    # eliminación
                       D[i][j-1],    # inserción
                       D[i-1][j-1])  # sustitución   en cualquier otro caso
"""
from __future__ import annotations
from typing import Sequence, List


def build_levenshtein_matrix(seq_a: Sequence, seq_b: Sequence) -> List[List[int]]:
    """
    Construye y retorna la matriz de programación dinámica completa (D),
    de tamaño (n+1) x (m+1), usada para calcular la distancia de Levenshtein.

    Se expone por separado (no solo la distancia final) porque el proyecto
    exige poder mostrar el llenado paso a paso de la matriz en el caso de
    estudio (documento técnico).

    Parámetros
    ----------
    seq_a, seq_b : Sequence
        Las dos secuencias a comparar (strings o listas de tokens).

    Retorna
    -------
    List[List[int]]
        Matriz D donde D[i][j] es la distancia de edición entre los primeros
        i elementos de seq_a y los primeros j elementos de seq_b.
    """
    n, m = len(seq_a), len(seq_b)

    # Matriz de (n+1) x (m+1), inicializada en 0
    D = [[0] * (m + 1) for _ in range(n + 1)]

    # Casos base: transformar un prefijo de A en la cadena vacía (o viceversa)
    # cuesta tantas operaciones como elementos tenga ese prefijo.
    for i in range(n + 1):
        D[i][0] = i
    for j in range(m + 1):
        D[0][j] = j

    # Llenado de la matriz mediante la recurrencia
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            costo_sustitucion = 0 if seq_a[i - 1] == seq_b[j - 1] else 1
            D[i][j] = min(
                D[i - 1][j] + 1,                    # eliminación
                D[i][j - 1] + 1,                    # inserción
                D[i - 1][j - 1] + costo_sustitucion,  # sustitución (o coincidencia)
            )

    return D


def traceback(seq_a: Sequence, seq_b: Sequence, D: List[List[int]]) -> List[str]:
    """
    Reconstruye la secuencia de operaciones (backtracking) que explican
    la distancia de Levenshtein, recorriendo la matriz D desde la esquina
    inferior derecha D[n][m] hasta D[0][0].

    En cada celda se decide de cuál de las tres celdas vecinas vino el
    valor óptimo, siguiendo el mismo orden de prioridad que
    build_levenshtein_matrix (diagonal > arriba > izquierda) para que el
    resultado sea determinista.

    Parámetros
    ----------
    seq_a, seq_b : Sequence
        Las mismas secuencias usadas para construir D.
    D : List[List[int]]
        La matriz ya construida con build_levenshtein_matrix(seq_a, seq_b).

    Retorna
    -------
    List[str]
        Lista de operaciones en orden natural (de seq_a hacia seq_b), donde
        cada elemento es una de:
        "coincidencia(x)", "sustitución(x→y)", "eliminación(x)", "inserción(y)".
    """
    n, m = len(seq_a), len(seq_b)
    i, j = n, m
    operaciones: List[str] = []

    while i > 0 or j > 0:
        actual = D[i][j]

        if i > 0 and j > 0:
            costo = 0 if seq_a[i - 1] == seq_b[j - 1] else 1
            if actual == D[i - 1][j - 1] + costo:
                # Vino de la diagonal: coincidencia o sustitución
                if costo == 0:
                    operaciones.append(f"coincidencia({seq_a[i - 1]})")
                else:
                    operaciones.append(f"sustitución({seq_a[i - 1]}→{seq_b[j - 1]})")
                i -= 1
                j -= 1
                continue

        if i > 0 and actual == D[i - 1][j] + 1:
            # Vino de arriba: sobra un elemento de seq_a
            operaciones.append(f"eliminación({seq_a[i - 1]})")
            i -= 1
            continue

        # En otro caso, vino de la izquierda: falta un elemento de seq_b
        operaciones.append(f"inserción({seq_b[j - 1]})")
        j -= 1

    # Se construyó de atrás hacia adelante, hay que invertir
    operaciones.reverse()
    return operaciones


def levenshtein_distance(seq_a: Sequence, seq_b: Sequence) -> int:
    """
    Calcula la distancia de edición (Levenshtein) entre dos secuencias.

    Parámetros
    ----------
    seq_a, seq_b : Sequence
        Las dos secuencias a comparar (ej. abstract_preprocesado de dos artículos).

    Retorna
    -------
    int
        Número mínimo de operaciones (inserción, eliminación, sustitución)
        para transformar seq_a en seq_b.
    """
    n, m = len(seq_a), len(seq_b)
    D = build_levenshtein_matrix(seq_a, seq_b)
    return D[n][m]


def levenshtein_similarity(seq_a: Sequence, seq_b: Sequence) -> float:
    """
    Convierte la distancia de Levenshtein en una similitud normalizada en [0, 1].

        similitud = 1 - distancia / max(len(seq_a), len(seq_b))

    Si ambas secuencias están vacías, se define la similitud como 1.0
    (son idénticas: la secuencia vacía).

    Parámetros
    ----------
    seq_a, seq_b : Sequence

    Retorna
    -------
    float
        1.0 = secuencias idénticas · 0.0 = completamente distintas.
    """
    n, m = len(seq_a), len(seq_b)
    if n == 0 and m == 0:
        return 1.0

    distancia = levenshtein_distance(seq_a, seq_b)
    return 1.0 - (distancia / max(n, m))


def similarity_matrix(corpus_tokens: Sequence[Sequence[str]]) -> List[List[float]]:
    """
    Calcula la matriz de similitud (Levenshtein) para un conjunto de N documentos
    ya tokenizados (ej. la lista de 'abstract_preprocesado' de los 20 artículos).

    Parámetros
    ----------
    corpus_tokens : Sequence[Sequence[str]]
        Lista de N secuencias de tokens, una por documento.

    Retorna
    -------
    List[List[float]]
        Matriz N x N simétrica con la similitud de Levenshtein entre cada par
        de documentos (la diagonal siempre vale 1.0).
    """
    n_docs = len(corpus_tokens)
    matriz = [[0.0] * n_docs for _ in range(n_docs)]

    for i in range(n_docs):
        matriz[i][i] = 1.0
        for j in range(i + 1, n_docs):
            sim = levenshtein_similarity(corpus_tokens[i], corpus_tokens[j])
            matriz[i][j] = sim
            matriz[j][i] = sim  # la similitud es simétrica

    return matriz


if __name__ == "__main__":
    # Demostración rápida y manual con un caso simple, verificable a mano.
    a = ["gato", "come", "pescado"]
    b = ["perro", "come", "pescado", "fresco"]

    print("Secuencia A:", a)
    print("Secuencia B:", b)
    print("\nMatriz de programación dinámica:")
    for fila in build_levenshtein_matrix(a, b):
        print(fila)

    print("\nDistancia de Levenshtein:", levenshtein_distance(a, b))
    print("Similitud normalizada:", round(levenshtein_similarity(a, b), 4))
