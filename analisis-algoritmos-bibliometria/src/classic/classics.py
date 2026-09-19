import json
import math
from typing import List, Sequence

# === IMPORTANTE: Importa aquí tus funciones desde tus archivos actuales ===
# Ejemplo (descomenta y ajusta según tus nombres de archivos reales):
from levenshtein import similarity_matrix as matriz_levenshtein
from jaccard import matriz_jaccard
from tfidf_cosine import matriz_similitud as coseno_matrix, similitud_coseno

# --- AUXILIAR PARA TF-IDF (Por si no tienes el vectorizador a la mano) ---
def calcular_matriz_tfidf(corpus_tokens: List[List[str]]) -> List[List[float]]:
    """Calcula una matriz TF-IDF simple a partir de listas de tokens."""
    n_docs = len(corpus_tokens)
    # 1. Calcular DF (Document Frequency)
    vocabulario = sorted(list(set(token for doc in corpus_tokens for token in doc)))
    df = {token: 0 for token in vocabulario}
    for doc in corpus_tokens:
        for token in set(doc):
            df[token] += 1

    # 2. Calcular TF-IDF para cada documento
    matriz_tfidf = []
    for doc in corpus_tokens:
        vector = []
        tf = {token: doc.count(token) for token in set(doc)}
        for token in vocabulario:
            if token in tf:
                tf_val = tf[token]
                idf_val = math.log(n_docs / df[token]) + 1
                vector.append(tf_val * idf_val)
            else:
                vector.append(0.0)
        matriz_tfidf.append(vector)
    return matriz_tfidf

# --- TUS FUNCIONES ADAPTADAS / COPIADAS ---

# 1. Jaccard (Basado en tu imagen)
def jaccard(conjunto_a, conjunto_b):
    if not isinstance(conjunto_a, set): conjunto_a = set(conjunto_a)
    if not isinstance(conjunto_b, set): conjunto_b = set(conjunto_b)
    if not conjunto_a and not conjunto_b: return 0.0
    interseccion = conjunto_a & conjunto_b
    union = conjunto_a | conjunto_b
    return len(interseccion) / len(union)

def matriz_jaccard_local(corpus_tokens):
    n_docs = len(corpus_tokens)
    matriz = [[0.0] * n_docs for _ in range(n_docs)]
    for i in range(n_docs):
        for j in range(n_docs):
            matriz[i][j] = jaccard(corpus_tokens[i], corpus_tokens[j])
    return matriz

# 2. Levenshtein - usa la implementación real de src/classic/levenshtein.py
# (Ya importada al inicio como matriz_levenshtein)


# 3. Coseno (Basado en tu imagen)
def similitud_coseno(vector_a, vector_b):
    if len(vector_a) != len(vector_b):
        raise ValueError("Los vectores deben tener la misma dimensión")
    producto_punto = sum(a * b for a, b in zip(vector_a, vector_b))
    norma_a = math.sqrt(sum(a ** 2 for a in vector_a))
    norma_b = math.sqrt(sum(b ** 2 for b in vector_b))
    if norma_a == 0 or norma_b == 0: return 0.0
    return producto_punto / (norma_a * norma_b)

def matriz_coseno(matriz_tfidf):
    n_docs = len(matriz_tfidf)
    matriz = [[0.0] * n_docs for _ in range(n_docs)]
    for i in range(n_docs):
        for j in range(n_docs):
            matriz[i][j] = similitud_coseno(matriz_tfidf[i], matriz_tfidf[j])
    return matriz

# 4. Needleman-Wunsch (usa la implementación real de src/classic/needleman_wunsch.py)
from needleman_wunsch import needleman_wunsch_alignment, needleman_wunsch_similarity, GAP

def matriz_needleman(corpus_tokens: Sequence[Sequence[str]]) -> List[List[float]]:
    n_docs = len(corpus_tokens)
    matriz = [[0.0] * n_docs for _ in range(n_docs)]
    for i in range(n_docs):
        matriz[i][i] = 1.0
        for j in range(i + 1, n_docs):
            sim = needleman_wunsch_similarity(corpus_tokens[i], corpus_tokens[j])
            matriz[i][j] = sim
            matriz[j][i] = sim
    return matriz


# --- FUNCIÓN PRINCIPAL DE CONSOLA ---
def imprimir_matriz(nombre, matriz, indices):
    print(f"\n--- MATRIZ DE SIMILITUD: {nombre} ---")
    # Imprimir encabezado de columnas
    header = "Art. ID\t" + "\t".join(f"[{idx}]" for idx in indices)
    print(header)
    print("-" * (len(header) + 8))

    for i, fila in enumerate(matriz):
        fila_str = "\t".join(f"{valor:.4f}" for valor in fila)
        print(f"[{indices[i]}]\t{fila_str}")

def ejecutar_comparador():
    ruta_json = "data/corpus_preprocesado.json"

    try:
        with open(ruta_json, "r", encoding="utf-8") as f:
            corpus = json.load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta_json}' en el directorio actual.")
        return

    # Mapear los artículos por su campo "numero"
    articulos_dict = {doc["numero"]: doc for doc in corpus}

    print("=== COMPARADOR DE ARTÍCULOS DE ARTIFICIAL INTELLIGENCE ===")
    print(f"Artículos disponibles en el corpus: {list(articulos_dict.keys())}")

    entrada = input("\nIngresa los números de los artículos a comparar (separados por coma, ej: 1, 2, 3): ")
    try:
        numeros_seleccionados = [int(n.strip()) for n in entrada.split(",") if n.strip()]
    except ValueError:
        print("Error: Ingresa números válidos estructurados por comas.")
        return

    if len(numeros_seleccionados) < 2:
        print("Error: Debes seleccionar al menos 2 artículos para comparar.")
        return

    # Validar que existan los artículos elegidos
    articulos_validos = []
    for num in numeros_seleccionados:
        if num in articulos_dict:
            articulos_validos.append(articulos_dict[num])
        else:
            print(f"Advertencia: El artículo con número {num} no existe en el corpus. Será omitido.")

    if len(articulos_validos) < 2:
        print("Error: No quedan suficientes artículos válidos para realizar la comparación.")
        return

    # Extraer los tokens preprocesados correspondientes
    tokens_seleccionados = [doc["abstract_preprocesado"] for doc in articulos_validos]
    indices_finales = [doc["numero"] for doc in articulos_validos]

    print(f"\nProcesando comparación para los artículos: {indices_finales}...")

    # Ejecutar métricas
    m_jaccard = matriz_jaccard_local(tokens_seleccionados)
    m_levenshtein = matriz_levenshtein(tokens_seleccionados)
    m_needleman = matriz_needleman(tokens_seleccionados)

    # Para coseno necesitamos calcular la matriz TF-IDF de este subconjunto primero
    matriz_tfidf = calcular_matriz_tfidf(tokens_seleccionados)
    m_coseno = matriz_coseno(matriz_tfidf)

    # Mostrar Resultados
    imprimir_matriz("JACCARD", m_jaccard, indices_finales)
    imprimir_matriz("COSENO (TF-IDF)", m_coseno, indices_finales)
    imprimir_matriz("LEVENSHTEIN", m_levenshtein, indices_finales)
    imprimir_matriz("NEEDLEMAN-WUNSCH", m_needleman, indices_finales)

if __name__ == "__main__":
    ejecutar_comparador()
