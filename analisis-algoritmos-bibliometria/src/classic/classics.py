import json

# === IMPORTANTE: Importa aquí tus funciones desde tus archivos actuales ===
# Ejemplo (descomenta y ajusta según tus nombres de archivos reales):
from levenshtein import similarity_matrix as matriz_levenshtein
from jaccard import matriz_jaccard
from tfidf_cosine import vectorizar_tfidf, matriz_similitud as coseno_matrix
from needleman_wunsch import similarity_matrix as matriz_needleman

# --- Algoritmos clasicos implementados como imports desde sus modulos ya testeados ---

# 1. Jaccard - usa la implementación real de src/classic/jaccard.py
# (Ya importada al inicio como matriz_jaccard)

# 2. Levenshtein - usa la implementación real de src/classic/levenshtein.py
# (Ya importada al inicio como matriz_levenshtein)


# 3. Coseno - usa la implementación real de src/classic/tfidf_cosine.py
# (Ya importada al inicio como coseno_matrix)


# 4. Needleman-Wunsch (usa la implementación real de src/classic/needleman_wunsch.py)
# (Ya importada al inicio como matriz_needleman)


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
    _, m_jaccard = matriz_jaccard(tokens_seleccionados)
    m_levenshtein = matriz_levenshtein(tokens_seleccionados)
    m_needleman = matriz_needleman(tokens_seleccionados)

    # Para coseno necesitamos calcular la matriz TF-IDF de este subconjunto primero
    _, matriz_tfidf = vectorizar_tfidf(tokens_seleccionados)
    m_coseno = coseno_matrix(matriz_tfidf)

    # Mostrar Resultados
    imprimir_matriz("JACCARD", m_jaccard, indices_finales)
    imprimir_matriz("COSENO (TF-IDF)", m_coseno, indices_finales)
    imprimir_matriz("LEVENSHTEIN", m_levenshtein, indices_finales)
    imprimir_matriz("NEEDLEMAN-WUNSCH", m_needleman, indices_finales)

if __name__ == "__main__":
    ejecutar_comparador()
