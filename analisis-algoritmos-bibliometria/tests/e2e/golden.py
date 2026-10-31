"""
Valores de referencia (golden values) de las pruebas E2E.

Se calcularon ejecutando el propio codigo de src/ sobre data/corpus_preprocesado.json
y data/embeddings/*.json, de modo que la aplicacion desplegada debe reproducirlos
exactamente (los algoritmos son deterministas). Si el corpus cambia, hay que
regenerarlos.
"""

TOTAL_ARTICULOS = 20
MODELOS_IA = ["Word2Vec", "MPNet"]

# --- Modulo 1: similitud entre los articulos 2 y 9 (celda fuera de la diagonal, 2 decimales)
PAR_2_9 = {
    "Levenshtein": "0.09",
    "Needleman-Wunsch": "0.09",
    "Coseno TF-IDF": "0.26",
    "Jaccard": "0.16",
    "Word2Vec - coseno": "0.93",
    "Word2Vec - similitud euclidiana": "0.72",
    "Word2Vec - distancia euclidiana": "0.38",
    "MPNet - coseno": "0.84",
    "MPNet - similitud euclidiana": "0.64",
    "MPNet - distancia euclidiana": "0.57",
}

# --- Modulo 2: particion en k = 4 grupos con la matriz base "Coseno TF-IDF" y 20 articulos
GRUPOS_K4 = {
    "single": {
        frozenset([1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20]),
        frozenset([4]), frozenset([18]), frozenset([19]),
    },
    "complete": {
        frozenset([1, 3, 4, 8, 10, 13]),
        frozenset([2, 5, 6, 7, 9, 12, 15, 18, 20]),
        frozenset([11, 14, 16, 17]),
        frozenset([19]),
    },
    "average": {
        frozenset([1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20]),
        frozenset([4]), frozenset([18]), frozenset([19]),
    },
}
# Textos de los titulos de cada criterio en el expander "Grupos y fusiones - ..."
TITULOS_CRITERIO = {"single": "Single", "complete": "Complete", "average": "Average"}

# --- Modulo 3: (patron, ignorar_mayusculas) -> (ocurrencias, articulos con ocurrencias)
BUSQUEDAS = {
    ("education", False): (78, 18),
    ("AI", False): (143, 19),
    ("ai", False): (27, 13),
    ("AI", True): (170, 20),
    ("learning", False): (37, 10),
}
PATRON_SIN_RESULTADOS = "zzzzqq"

# --- Modulo 4: ranking de terminos (corpus preprocesado)
TERMINOS_DISTINTOS = 868
TOKENS_TOTALES = 2532
FRECUENCIA_MAXIMA = 86
TOP5 = [("ai", 86), ("education", 57), ("review", 48), ("research", 46), ("aied", 38)]
ALGORITMOS_RANKING = ["Counting Sort", "Radix Sort", "Bucket Sort"]