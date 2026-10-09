"""
Modulo CLU-1: Preprocesamiento y matriz de distancia para clustering
===================================================================

Construye la matriz de distancias para los 20 abstracts del corpus
reutilizando la metrica de similitud Coseno con TF-IDF ya testeada.

Como los algoritmos de clustering necesitan una matriz de DISTANCIAS
(0 = identicos), se transforma la similitud coseno mediante:
    distancia = 1.0 - similitud_coseno

Ruta del archivo: src/clustering/distance_matrix.py
5
"""

import os
import sys
import json

# Asegurar herencia de rutas de la raiz para evitar fallos de importacion
RAIZ_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if RAIZ_PROYECTO not in sys.path:
    sys.path.insert(0, RAIZ_PROYECTO)

# Reutilizamos las funciones del modulo clasico que ya tienes implementado
from src.classic.tfidf_cosine import vectorizar_tfidf, matriz_similitud

# Rutas de datos
RUTA_CORPUS = os.path.join(RAIZ_PROYECTO, "data", "corpus_preprocesado.json")
RUTA_SALIDA_MATRIZ = os.path.join(RAIZ_PROYECTO, "data", "matriz_distancias_clustering.json")

def generar_matriz_distancias_clu1():
    print("=== [CLU-1] GENERANDO MATRIZ DE DISTANCIAS PARA CLUSTERING ===")

    # 1. Cargar el corpus preprocesado
    if not os.path.exists(RUTA_CORPUS):
        raise FileNotFoundError(f"No se encontro el corpus en {RUTA_CORPUS}. Corre el preprocesamiento primero.")

    with open(RUTA_CORPUS, "r", encoding="utf-8") as archivo:
        corpus = json.load(archivo)

    # El requerimiento especifica trabajar sobre los 20 abstracts
    if len(corpus) != 20:
        print(f"Aviso: El corpus actual contiene {len(corpus)} documentos, el enunciado menciona 20.")

    # Ordenar por el numero identificador del articulo para asegurar consistencia indexada
    corpus_ordenado = sorted(corpus, key=lambda x: x["numero"])
    numeros_articulos = [doc["numero"] for doc in corpus_ordenado]
    tokens_articulos = [doc["abstract_preprocesado"] for doc in corpus_ordenado]

    print(f"Procesando {len(corpus_ordenado)} documentos secuencialmente...")

    # 2. Calcular Similitud TF-IDF Coseno usando tus funciones reales
    # vectorizar_tfidf retorna: (vocabulario, matriz_tfidf)
    _, matriz_tfidf = vectorizar_tfidf(tokens_articulos)
    matriz_sim_coseno = matriz_similitud(matriz_tfidf)

    # 3. Transformar la Matriz de Similitud en Matriz de Distancia (1 - Similitud)
    n = len(matriz_sim_coseno)
    matriz_distancias = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            similitud = matriz_sim_coseno[i][j]
            # Control por posibles flotantes marginales fuera de rango [0, 1]
            distancia = max(0.0, 1.0 - similitud)
            matriz_distancias[i][j] = round(distancia, 4)

    # 4. Estructurar el JSON de salida para que el modulo de clustering sepa que fila es que articulo
    datos_salida = {
        "metric_used": "TF-IDF Cosine Distance (1 - Cosine Similarity)",
        "indices_articulos": numeros_articulos,
        "matriz": matriz_distancias
    }

    # Guardar en data/ para el siguiente paso del pipeline
    os.makedirs(os.path.dirname(RUTA_SALIDA_MATRIZ), exist_ok=True)
    with open(RUTA_SALIDA_MATRIZ, "w", encoding="utf-8") as f:
        json.dump(datos_salida, f, indent=4, ensure_ascii=False)

        print(f"¡Éxito! Matriz guardada exitosamente en: {RUTA_SALIDA_MATRIZ}")

    # --- Mostrar la Matriz de Distancias COMPLETA (20x20) ---
    print("\n--- MATRIZ DE DISTANCIAS COMPLETA (20x20) ---")
    encabezado = "Art. ID\t" + "\t".join(f"[{numeros_articulos[i]}]" for i in range(n))
    print(encabezado)
    print("-" * (len(encabezado) + 4))

    for i in range(n):
        # Imprime los 20 valores de la fila correspondientes a los 20 artículos
        fila_str = "\t".join(f"{matriz_distancias[i][j]:.4f}" for j in range(n))
        print(f"[{numeros_articulos[i]}]\t{fila_str}")

if __name__ == "__main__":
    generar_matriz_distancias_clu1()
