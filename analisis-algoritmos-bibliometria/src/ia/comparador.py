import json

# === IMPORTS CLÁSICOS (CLA-5) ===
from src.classic.levenshtein import similarity_matrix as matriz_levenshtein
from src.classic.jaccard import matriz_jaccard
from src.classic.tfidf_cosine import vectorizar_tfidf, matriz_similitud as coseno_matrix
from src.classic.needleman_wunsch import similarity_matrix as matriz_needleman

# === IMPORTS EMBEDDINGS (IA-4) ===
# Asegúrate de ajustar la ruta de importación según tu estructura de carpetas
from metrics import calcular_matrices_embeddings

def imprimir_matriz(nombre, matriz, indices):
    print(f"\n--- MATRIZ DE SIMILITUD: {nombre} ---")
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

    articulos_validos = []
    for num in numeros_seleccionados:
        if num in articulos_dict:
            articulos_validos.append(articulos_dict[num])
        else:
            print(f"Advertencia: El artículo con número {num} no existe en el corpus. Será omitido.")

    if len(articulos_validos) < 2:
        print("Error: No quedan suficientes artículos válidos para realizar la comparación.")
        return

    # 1. Extraer tokens para algoritmos clásicos
    tokens_seleccionados = [doc["abstract_preprocesado"] for doc in articulos_validos]
    indices_finales = [doc["numero"] for doc in articulos_validos]

    # 2. Extraer embeddings para algoritmos vectoriales modernos (IA-4)
    # Validamos que los documentos contengan el campo de embeddings
    if not all("embedding" in doc for doc in articulos_validos):
        print("Error: Uno o más artículos seleccionados no tienen un vector de 'embedding' generado.")
        return

    embeddings_seleccionados = [doc["embedding"] for doc in articulos_validos]

    print(f"\nProcesando comparación para los artículos: {indices_finales}...")

    # === Ejecutar Métricas Clásicas (CLA-5) ===
    _, m_jaccard = matriz_jaccard(tokens_seleccionados)
    m_levenshtein = matriz_levenshtein(tokens_seleccionados)
    m_needleman = matriz_needleman(tokens_seleccionados)
    _, matriz_tfidf = vectorizar_tfidf(tokens_seleccionados)
    m_coseno_tfidf = coseno_matrix(matriz_tfidf)

    # === Ejecutar Métricas de Embeddings (IA-4) ===
    m_coseno_emb, m_euclidiana_dist, m_euclidiana_sim = calcular_matrices_embeddings(embeddings_seleccionados)

    # === Mostrar Resultados ===
    print("\n=================== MÉTRICAS CLÁSICAS ===================")
    imprimir_matriz("JACCARD", m_jaccard, indices_finales)
    imprimir_matriz("COSENO (TF-IDF)", m_coseno_tfidf, indices_finales)
    imprimir_matriz("LEVENSHTEIN", m_levenshtein, indices_finales)
    imprimir_matriz("NEEDLEMAN-WUNSCH", m_needleman, indices_finales)

    print("\n================ MÉTRICAS DE EMBEDDINGS =================")
    imprimir_matriz("COSENO (EMBEDDINGS)", m_coseno_emb, indices_finales)
    imprimir_matriz("DISTANCIA EUCLIDIANA (MÉTRICA DE DISTANCIA)", m_euclidiana_dist, indices_finales)
    imprimir_matriz("SIMILITUD EUCLIDIANA [1 / (1 + d)]", m_euclidiana_sim, indices_finales)

if __name__ == "__main__":
    ejecutar_comparador()
