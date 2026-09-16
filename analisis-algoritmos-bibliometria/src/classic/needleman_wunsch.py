"""
Requerimiento 1 - Algoritmo Clásico de Similitud: Needleman-Wunsch
============================================================================

Implementado desde cero con programación dinámica (sin usar librerías que
resuelvan el algoritmo directamente, como Biopython.pairwise2, parasail, etc.).

A diferencia de Levenshtein (que solo da una distancia), Needleman-Wunsch
realiza un ALINEAMIENTO GLOBAL entre dos secuencias: construye una matriz de
puntuación y luego hace "backtracking" (retroceso) sobre ella para reconstruir
explícitamente cómo quedaron alineados los elementos de ambas secuencias
(incluyendo los huecos/gaps que se insertaron).

Funciona a nivel de caracteres (strings) o de palabras/tokens (listas),
igual que el módulo de Levenshtein, porque solo depende de la comparación
de igualdad entre elementos.

Esquema de puntuación (parámetros configurables):
    match    = +1   (los dos elementos son iguales)
    mismatch = -1   (los dos elementos son distintos, pero se alinean)
    gap      = -2   (insertar un hueco en una de las dos secuencias)

Recurrencia utilizada para la matriz de puntuación S:
    S[i][0] = i * gap
    S[0][j] = j * gap
    S[i][j] = max(
        S[i-1][j-1] + (match si A[i-1] == B[j-1] si no mismatch),  # diagonal
        S[i-1][j]   + gap,                                          # arriba
        S[i][j-1]   + gap,                                          # izquierda
    )

El backtracking parte de la esquina inferior derecha (S[n][m]) y va hacia
S[0][0], eligiendo en cada paso de qué celda vino el valor óptimo.
"""
from __future__ import annotations
from typing import Sequence, List, Tuple


GAP = "-"  # símbolo usado para representar un hueco en el alineamiento


def build_score_matrix(
    seq_a: Sequence,
    seq_b: Sequence,
    match: int = 1,
    mismatch: int = -1,
    gap: int = -2,
) -> List[List[int]]:
    """
    Construye y retorna la matriz de puntuación S, de tamaño (n+1) x (m+1),
    usada por Needleman-Wunsch.

    Se expone por separado (no solo el score final) porque el proyecto exige
    poder mostrar el llenado paso a paso de la matriz en el caso de estudio
    del documento técnico.

    Parámetros
    ----------
    seq_a, seq_b : Sequence
        Las dos secuencias a alinear (strings o listas de tokens).
    match, mismatch, gap : int
        Puntajes del esquema de alineamiento.

    Retorna
    -------
    List[List[int]]
        Matriz S donde S[i][j] es el puntaje óptimo de alinear los primeros
        i elementos de seq_a con los primeros j elementos de seq_b.
    """
    n, m = len(seq_a), len(seq_b)

    S = [[0] * (m + 1) for _ in range(n + 1)]

    # Casos base: alinear un prefijo de A contra "nada" son puros gaps.
    for i in range(n + 1):
        S[i][0] = i * gap
    for j in range(m + 1):
        S[0][j] = j * gap

    # Llenado de la matriz mediante la recurrencia
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            puntaje_diagonal = S[i - 1][j - 1] + (
                match if seq_a[i - 1] == seq_b[j - 1] else mismatch
            )
            puntaje_arriba = S[i - 1][j] + gap       # A[i-1] alineado con un gap
            puntaje_izquierda = S[i][j - 1] + gap    # B[j-1] alineado con un gap

            S[i][j] = max(puntaje_diagonal, puntaje_arriba, puntaje_izquierda)

    return S


def traceback(
    seq_a: Sequence,
    seq_b: Sequence,
    S: List[List[int]],
    match: int = 1,
    mismatch: int = -1,
    gap: int = -2,
) -> Tuple[List, List]:
    """
    Reconstruye el alineamiento óptimo recorriendo la matriz S desde la
    esquina inferior derecha S[n][m] hasta S[0][0] (backtracking).

    En cada celda se decide de cuál de las tres celdas vecinas vino el
    puntaje óptimo, siguiendo el mismo orden de prioridad que build_score_matrix
    (diagonal > arriba > izquierda) para que el resultado sea determinista.

    Retorna
    -------
    Tuple[List, List]
        (alineado_a, alineado_b): dos secuencias de igual longitud, donde
        GAP ("-") indica un hueco insertado en esa posición.
    """
    n, m = len(seq_a), len(seq_b)
    i, j = n, m

    alineado_a: List = []
    alineado_b: List = []

    while i > 0 or j > 0:
        actual = S[i][j]

        if i > 0 and j > 0:
            costo = match if seq_a[i - 1] == seq_b[j - 1] else mismatch
            if actual == S[i - 1][j - 1] + costo:
                # Vino de la diagonal: ambos elementos se alinean entre sí
                alineado_a.append(seq_a[i - 1])
                alineado_b.append(seq_b[j - 1])
                i -= 1
                j -= 1
                continue

        if i > 0 and actual == S[i - 1][j] + gap:
            # Vino de arriba: elemento de A alineado con un gap en B
            alineado_a.append(seq_a[i - 1])
            alineado_b.append(GAP)
            i -= 1
            continue

        # En otro caso, vino de la izquierda: elemento de B alineado con un gap en A
        alineado_a.append(GAP)
        alineado_b.append(seq_b[j - 1])
        j -= 1

    # Se construyó de atrás hacia adelante, hay que invertir
    alineado_a.reverse()
    alineado_b.reverse()
    return alineado_a, alineado_b


def needleman_wunsch_score(
    seq_a: Sequence,
    seq_b: Sequence,
    match: int = 1,
    mismatch: int = -1,
    gap: int = -2,
) -> int:
    """Retorna únicamente el puntaje óptimo de alineamiento global S[n][m]."""
    n, m = len(seq_a), len(seq_b)
    S = build_score_matrix(seq_a, seq_b, match, mismatch, gap)
    return S[n][m]


def needleman_wunsch_alignment(
    seq_a: Sequence,
    seq_b: Sequence,
    match: int = 1,
    mismatch: int = -1,
    gap: int = -2,
) -> Tuple[List, List, int]:
    """
    Ejecuta el algoritmo completo: construye la matriz de puntuación y hace
    el backtracking para obtener el alineamiento explícito.

    Retorna
    -------
    Tuple[List, List, int]
        (alineado_a, alineado_b, score_final)
    """
    S = build_score_matrix(seq_a, seq_b, match, mismatch, gap)
    alineado_a, alineado_b = traceback(seq_a, seq_b, S, match, mismatch, gap)
    n, m = len(seq_a), len(seq_b)
    return alineado_a, alineado_b, S[n][m]


def needleman_wunsch_similarity(
    seq_a: Sequence,
    seq_b: Sequence,
    match: int = 1,
    mismatch: int = -1,
    gap: int = -2,
) -> float:
    """
    Convierte el alineamiento en una similitud normalizada en [0, 1]:

        similitud = (# posiciones donde coinciden, sin contar gaps)
                    / (longitud total del alineamiento)

    Es decir, qué proporción del alineamiento óptimo quedó formada por
    coincidencias reales entre A y B.

    Si ambas secuencias son vacías, se define la similitud como 1.0.
    """
    if len(seq_a) == 0 and len(seq_b) == 0:
        return 1.0

    alineado_a, alineado_b, _ = needleman_wunsch_alignment(
        seq_a, seq_b, match, mismatch, gap
    )

    longitud_alineamiento = len(alineado_a)
    coincidencias = sum(
        1
        for a, b in zip(alineado_a, alineado_b)
        if a == b and a != GAP and b != GAP
    )

    return coincidencias / longitud_alineamiento


def similarity_matrix(
    corpus_tokens: Sequence[Sequence[str]],
    match: int = 1,
    mismatch: int = -1,
    gap: int = -2,
) -> List[List[float]]:
    """
    Calcula la matriz de similitud (Needleman-Wunsch) para un conjunto de N
    documentos ya tokenizados (ej. 'abstract_preprocesado' de los 20 artículos).

    Retorna
    -------
    List[List[float]]
        Matriz N x N simétrica con la similitud entre cada par de documentos
        (la diagonal siempre vale 1.0).
    """
    n_docs = len(corpus_tokens)
    matriz = [[0.0] * n_docs for _ in range(n_docs)]

    for i in range(n_docs):
        matriz[i][i] = 1.0
        for j in range(i + 1, n_docs):
            sim = needleman_wunsch_similarity(
                corpus_tokens[i], corpus_tokens[j], match, mismatch, gap
            )
            matriz[i][j] = sim
            matriz[j][i] = sim  # la similitud es simétrica

    return matriz


def imprimir_alineamiento(alineado_a: List, alineado_b: List) -> None:
    """Utilidad para mostrar el alineamiento de forma legible en consola."""
    linea_a = " ".join(str(x) for x in alineado_a)
    linea_b = " ".join(str(x) for x in alineado_b)
    print(linea_a)
    print(linea_b)


if __name__ == "__main__":
    # Demostración rápida y manual con un caso simple, verificable a mano.
    a = ["gato", "come", "pescado"]
    b = ["perro", "come", "pescado", "fresco"]

    print("Secuencia A:", a)
    print("Secuencia B:", b)

    S = build_score_matrix(a, b)
    print("\nMatriz de puntuación:")
    for fila in S:
        print(fila)

    alineado_a, alineado_b, score = needleman_wunsch_alignment(a, b)
    print("\nAlineamiento óptimo (score = {}):".format(score))
    imprimir_alineamiento(alineado_a, alineado_b)

    print("\nSimilitud normalizada:", round(needleman_wunsch_similarity(a, b), 4))
