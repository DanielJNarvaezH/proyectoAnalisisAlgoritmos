"""
CAS-3 — Evidencia ejecutable del caso de estudio (TF-IDF + Coseno / Jaccard)
==================================================================================

Reproduce, corriendo este script, los números que se documentan en
/docs/caso_estudio_clasicos.md (secciones 7-9) para los artículos 2 y 9.

Usa exclusivamente `abstract_preprocesado` (el corpus ya limpio, sin
stopwords y lematizado, construido en PRE-1 y validado en PRE-2), para
ser consistente con CAS-1/CAS-2 y con los números ya verificados en
classics.py (CLA-5): Jaccard = 0.1583, Coseno TF-IDF = 0.2553.

No define ninguna lógica nueva de los algoritmos: solo IMPORTA las
implementaciones reales de src/classic/tfidf_cosine.py y
src/classic/jaccard.py.

Ejecutar desde la raíz del proyecto:
    .\\venv\\Scripts\\python.exe notebooks/caso_estudio_cas3.py
"""
import json
import os
import sys

# Permite importar desde src/classic/ (este archivo vive en /notebooks)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "classic"))

from tfidf_cosine import calcular_idf, construir_vocabulario, vectorizar_tfidf, similitud_coseno
from jaccard import texto_a_conjunto, jaccard

RUTA_CORPUS = os.path.join(os.path.dirname(__file__), "..", "data", "corpus_preprocesado.json")

# Mismos artículos seleccionados en CAS-1 y usados en CAS-2
ARTICULOS_SELECCIONADOS = (2, 9)


def cargar_articulos(ruta_corpus, numeros):
    with open(ruta_corpus, "r", encoding="utf-8") as f:
        corpus = json.load(f)
    articulos = {doc["numero"]: doc for doc in corpus}
    faltantes = [n for n in numeros if n not in articulos]
    if faltantes:
        raise ValueError(f"No se encontraron en el corpus los artículos: {faltantes}")
    return {n: articulos[n] for n in numeros}


def encabezado(titulo):
    print("\n" + "=" * 70)
    print(titulo)
    print("=" * 70)


def demostrar_tfidf_coseno(tokens_a, tokens_b, num_a, num_b):
    encabezado(f"TF-IDF + SIMILITUD COSENO — artículos {num_a} vs {num_b}")

    print(f"Tokens artículo {num_a} (primeros 10):", tokens_a[:10])
    print(f"Tokens artículo {num_b} (primeros 10):", tokens_b[:10])

    # IDF calculado sobre el subconjunto de 2 documentos seleccionados,
    # igual que hace classics.py (CLA-5) al comparar un par de artículos.
    docs_tokenizados = [tokens_a, tokens_b]
    vocabulario = construir_vocabulario(docs_tokenizados)
    idf = calcular_idf(docs_tokenizados)

    print(f"\nTamaño del vocabulario conjunto: {len(vocabulario)} términos")

    terminos_compartidos = sorted(set(tokens_a) & set(tokens_b))
    print(f"\nTérminos compartidos entre ambos ({len(terminos_compartidos)}), con su IDF:")
    for t in terminos_compartidos[:10]:
        print(f"  - '{t}': df=2/2 -> IDF = {idf[t]:.4f}")
    if len(terminos_compartidos) > 10:
        print(f"  ... ({len(terminos_compartidos) - 10} términos más omitidos)")

    _, matriz_tfidf = vectorizar_tfidf(docs_tokenizados)
    vec_a, vec_b = matriz_tfidf[0], matriz_tfidf[1]

    no_cero_a = {vocabulario[i]: round(vec_a[i], 4) for i in range(len(vocabulario)) if vec_a[i] > 0}
    no_cero_b = {vocabulario[i]: round(vec_b[i], 4) for i in range(len(vocabulario)) if vec_b[i] > 0}
    print(f"\nVector TF-IDF artículo {num_a} (términos no nulos): {len(no_cero_a)} dimensiones")
    print(f"Vector TF-IDF artículo {num_b} (términos no nulos): {len(no_cero_b)} dimensiones")

    producto_punto = sum(x * y for x, y in zip(vec_a, vec_b))
    norma_a = sum(x ** 2 for x in vec_a) ** 0.5
    norma_b = sum(y ** 2 for y in vec_b) ** 0.5
    sim = similitud_coseno(vec_a, vec_b)

    print(f"\nProducto punto (A . B)  = {producto_punto:.6f}")
    print(f"Norma ||A||             = {norma_a:.6f}")
    print(f"Norma ||B||             = {norma_b:.6f}")
    print(f"Similitud coseno        = {sim:.4f}")
    return sim


def demostrar_jaccard(tokens_a, tokens_b, num_a, num_b, n=1):
    encabezado(f"COEFICIENTE DE JACCARD — artículos {num_a} vs {num_b}")

    conjunto_a = texto_a_conjunto(tokens_a, n=n)
    conjunto_b = texto_a_conjunto(tokens_b, n=n)

    print(f"Cardinalidad conjunto artículo {num_a}: {len(conjunto_a)} unigramas únicos")
    print(f"Cardinalidad conjunto artículo {num_b}: {len(conjunto_b)} unigramas únicos")

    interseccion = conjunto_a & conjunto_b
    union = conjunto_a | conjunto_b

    print(f"\nIntersección (primeros 10): {sorted(interseccion)[:10]}")
    print(f"Tamaño de la intersección = {len(interseccion)}")
    print(f"Tamaño de la unión        = {len(union)}")

    coef = jaccard(conjunto_a, conjunto_b)
    print(f"\nJ(A, B) = {len(interseccion)} / {len(union)} = {coef:.4f}")
    return coef


if __name__ == "__main__":
    num_a, num_b = ARTICULOS_SELECCIONADOS
    articulos = cargar_articulos(RUTA_CORPUS, ARTICULOS_SELECCIONADOS)

    tokens_a = articulos[num_a]["abstract_preprocesado"]
    tokens_b = articulos[num_b]["abstract_preprocesado"]

    print(f"Caso de estudio CAS-1/CAS-3: artículos {num_a} y {num_b}")
    print(f"  [{num_a}] {articulos[num_a]['titulo']}")
    print(f"  [{num_b}] {articulos[num_b]['titulo']}")

    sim_coseno = demostrar_tfidf_coseno(tokens_a, tokens_b, num_a, num_b)
    sim_jaccard = demostrar_jaccard(tokens_a, tokens_b, num_a, num_b)

    encabezado("RESUMEN")
    print(f"TF-IDF + Coseno -> similitud = {sim_coseno:.4f}")
    print(f"Jaccard         -> similitud = {sim_jaccard:.4f}")
