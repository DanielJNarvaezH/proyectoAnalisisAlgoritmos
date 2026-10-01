"""
Embeddings de documento con un modelo de lenguaje (tarea IA-3)
==============================================================

Genera un vector de 768 dimensiones por abstract con el modelo
`sentence-transformers/all-mpnet-base-v2`, segun la decision documentada
en docs/modelos_ia.md (seccion 6).

Diferencias con IA-2 (Word2Vec), ambas justificadas en docs/modelos_ia.md:
  - Entrada: el campo `abstract` ORIGINAL, sin preprocesar. Un Transformer
    usa las stopwords, la puntuacion y el orden de las palabras para
    interpretar el contexto; lematizar o quitar stopwords le quitaria
    justamente la informacion que lo diferencia de Word2Vec.
  - El vector del documento lo produce el propio modelo (incluye su capa
    de pooling), porque es un modelo entrenado para representar textos
    completos. El enunciado permite usar modelos preentrenados para
    vectorizar los abstracts.
  - La similitud coseno / distancia euclidiana NO se calcula aqui: es la
    tarea IA-4, implementada a mano (no se usa util.cos_sim).

Verificacion de truncamiento (obligatoria segun IA-1): el modelo solo lee
las primeras `max_seq_length` sub-palabras (384) y descarta el resto sin
avisar. Este script cuenta las sub-palabras de cada abstract con el
tokenizador del propio modelo y reporta si alguno queda truncado.

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\ia\\embeddings_llm.py

La primera ejecucion descarga el modelo (~420 MB) en la cache de Hugging
Face, indicada por la variable de entorno HF_HOME (si no esta definida,
queda en el disco C:, en ~/.cache/huggingface). El resultado se guarda en
data/embeddings/mpnet.json, con el mismo formato que word2vec.json.
"""

import os
import sys

# Permite importar el paquete `ia` tanto al ejecutar este archivo como
# script como al importarlo desde las pruebas.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ia.embeddings_w2v import RAIZ, cargar_corpus, guardar_embeddings  # noqa: E402
from ia.metricas import norma  # noqa: E402

NOMBRE_MODELO = "sentence-transformers/all-mpnet-base-v2"
RUTA_SALIDA = os.path.join(RAIZ, "data", "embeddings", "mpnet.json")


# ---------------------------------------------------------------------------
# 1. Verificacion de truncamiento
# ---------------------------------------------------------------------------

def contar_subpalabras(texto, tokenizador):
    """
    Cantidad de sub-palabras que ocupa un texto en el modelo, incluyendo
    los tokens especiales de inicio y fin que agrega el tokenizador (el
    limite max_seq_length del modelo tambien los cuenta).
    """
    return len(tokenizador(texto, add_special_tokens=True)["input_ids"])


def analizar_truncamiento(longitudes, maximo):
    """
    Dado {numero_articulo: subpalabras}, retorna un resumen con la longitud
    minima, maxima y promedio, y la lista de articulos que superan `maximo`
    (esos quedan truncados: el modelo ignora lo que sobra).
    """
    valores = list(longitudes.values())
    if not valores:
        return {"minimo": 0, "maximo": 0, "promedio": 0.0, "truncados": []}
    return {
        "minimo": min(valores),
        "maximo": max(valores),
        "promedio": sum(valores) / len(valores),
        "truncados": sorted(n for n, cantidad in longitudes.items() if cantidad > maximo),
    }


# ---------------------------------------------------------------------------
# 2. Generacion de embeddings del corpus
# ---------------------------------------------------------------------------

def generar_embeddings_corpus(corpus, modelo):
    """
    Vectoriza el `abstract` original de cada articulo.

    `modelo` es un SentenceTransformer (o un objeto falso en las pruebas)
    con los atributos `tokenizer` y `max_seq_length` y el metodo `encode`.
    Los 20 abstracts se codifican en una sola llamada (por lotes), que es
    mas eficiente que llamar al modelo una vez por articulo.
    """
    textos = [articulo["abstract"] for articulo in corpus]
    vectores = modelo.encode(textos, show_progress_bar=False)

    articulos = []
    for articulo, vector in zip(corpus, vectores):
        subpalabras = contar_subpalabras(articulo["abstract"], modelo.tokenizer)
        articulos.append({
            "numero": articulo["numero"],
            "titulo": articulo["titulo"],
            "vector": [float(componente) for componente in vector],
            "subpalabras": subpalabras,
            "truncado": subpalabras > modelo.max_seq_length,
        })
    return articulos


# ---------------------------------------------------------------------------
# 3. Carga del modelo (unica parte que usa sentence-transformers)
# ---------------------------------------------------------------------------

def cargar_modelo():
    """
    Descarga (solo la primera vez) y carga el modelo. Se importa aqui dentro
    para que el resto del modulo, sus pruebas y los modulos que lo importen
    funcionen sin tener instalado sentence-transformers ni PyTorch.
    """
    from sentence_transformers import SentenceTransformer

    cache = os.environ.get("HF_HOME", "(no definida: ~/.cache/huggingface)")
    print(f"Cache de Hugging Face (HF_HOME): {cache}")
    return SentenceTransformer(NOMBRE_MODELO)


# ---------------------------------------------------------------------------
# 4. Reporte en consola
# ---------------------------------------------------------------------------

def imprimir_reporte(articulos, maximo):
    print("\n=== Longitud de cada abstract en sub-palabras ===")
    print(f"{'Art.':>4}  {'Sub-palabras':>12}  Estado")
    for art in articulos:
        estado = "TRUNCADO" if art["truncado"] else "completo"
        print(f"{art['numero']:>4}  {art['subpalabras']:>12}  {estado}")

    resumen = analizar_truncamiento(
        {a["numero"]: a["subpalabras"] for a in articulos}, maximo
    )
    print(f"\nLimite del modelo: {maximo} sub-palabras")
    print(f"Rango: {resumen['minimo']} a {resumen['maximo']} "
          f"(promedio {resumen['promedio']:.1f})")
    if resumen["truncados"]:
        print(f"Articulos truncados: {resumen['truncados']} "
              f"(ver plan B en docs/modelos_ia.md)")
    else:
        print("Ningun abstract supera el limite: todos se procesan completos.")


def main():
    corpus = cargar_corpus()
    print(f"Corpus: {len(corpus)} articulos")
    print(f"Cargando {NOMBRE_MODELO}. La primera vez descarga ~420 MB...")
    modelo = cargar_modelo()
    # sentence-transformers 6 renombro get_sentence_embedding_dimension()
    # a get_embedding_dimension(); se usa la que exista en la version instalada.
    obtener_dimension = getattr(modelo, "get_embedding_dimension", None) \
        or modelo.get_sentence_embedding_dimension
    dimension = obtener_dimension()
    print(f"Modelo cargado: dimension {dimension}, "
          f"entrada maxima {modelo.max_seq_length} sub-palabras")

    articulos = generar_embeddings_corpus(corpus, modelo)
    imprimir_reporte(articulos, modelo.max_seq_length)

    # El modelo puede incluir una capa que normaliza los vectores a norma 1;
    # se mide en vez de suponerlo, porque cambia la interpretacion de la
    # distancia euclidiana (con norma 1, d^2 = 2 - 2*coseno).
    normas = [norma(art["vector"]) for art in articulos]
    print(f"\nNorma de los vectores: {min(normas):.6f} a {max(normas):.6f}")

    guardar_embeddings(
        RUTA_SALIDA,
        modelo=NOMBRE_MODELO,
        dimension=dimension,
        entrada="abstract",
        articulos=articulos,
        extra={
            "metodo": "embedding de documento producido por el modelo "
                      "(mean pooling de all-mpnet-base-v2)",
            "max_seq_length": modelo.max_seq_length,
            "norma_minima": min(normas),
            "norma_maxima": max(normas),
        },
    )
    print(f"\nEmbeddings guardados en: {RUTA_SALIDA}")


if __name__ == "__main__":
    main()
