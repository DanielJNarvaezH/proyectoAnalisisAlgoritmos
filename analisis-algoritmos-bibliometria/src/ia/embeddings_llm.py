from sentence_transformers import SentenceTransformer

def generar_embeddings(textos):
    # 1. Cargas un modelo preentrenado (este es muy bueno y ligero)
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # 2. Generas los números (embeddings) para tus textos
    embeddings = model.encode(textos)

    return embeddings

# Ejemplo de uso:
mis_textos = ["Me gusta la inteligencia artificial", "Amo programar en Python"]
vectores = generar_embeddings(mis_textos)
print(vectores) # Verás listas largas de números decimals
