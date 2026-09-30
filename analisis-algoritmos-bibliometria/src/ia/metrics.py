import numpy as np

def similitud_coseno_vectorial(emb_a, emb_b):
    """Calcula la similitud coseno entre dos vectores numéricos."""
    norm_a = np.linalg.norm(emb_a)
    norm_b = np.linalg.norm(emb_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(emb_a, emb_b) / (norm_a * norm_b))

def distancia_euclidiana_vectorial(emb_a, emb_b):
    """Calcula la distancia euclidiana estándar entre dos vectores numéricos."""
    return float(np.linalg.norm(np.array(emb_a) - np.array(emb_b)))

def calcular_matrices_embeddings(embeddings_lista):
    """
    Genera matrices cuadradas de similitud coseno y distancia euclidiana
    para una lista de vectores (embeddings).
    """
    n = len(embeddings_lista)
    matriz_coseno = np.zeros((n, n))
    matriz_euclidiana = np.zeros((n, n))
    matriz_euclidiana_sim = np.zeros((n, n))  # Versión normalizada como similitud

    for i in range(n):
        for j in range(n):
            emb_i = embeddings_lista[i]
            emb_j = embeddings_lista[j]

            # 1. Coseno
            sim_cos = similitud_coseno_vectorial(emb_i, emb_j)
            matriz_coseno[i][j] = sim_cos

            # 2. Euclidiana
            dist_euc = distancia_euclidiana_vectorial(emb_i, emb_j)
            matriz_euclidiana[i][j] = dist_euc

            # 3. Euclidiana Convertida a Similitud: 1 / (1 + d)
            matriz_euclidiana_sim[i][j] = 1 / (1 + dist_euc)

    return matriz_coseno.tolist(), matriz_euclidiana.tolist(), matriz_euclidiana_sim.tolist()
