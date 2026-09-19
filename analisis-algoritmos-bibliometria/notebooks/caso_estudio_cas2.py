"""
CAS-2 — Evidencia ejecutable del caso de estudio (Levenshtein / Needleman-Wunsch)
==================================================================================

Reproduce, corriendo este script, exactamente los números y tablas que están
documentados en /docs/caso_estudio_clasicos.md para los artículos 2 y 9.

No define ninguna lógica nueva de los algoritmos: solo IMPORTA las
implementaciones reales ya probadas de src/classic/ (las mismas que usa
CLA-5 en classics.py) y las aplica sobre:
    (a) el fragmento representativo de 6 tokens usado para la demostración
        manual paso a paso, y
    (b) los abstracts completos de los artículos 2 y 9, para el resultado final.

Ejecutar desde la raíz del proyecto:
    .\\venv\\Scripts\\python.exe notebooks/caso_estudio_cas2.py
"""
import json
import os
import sys

# Permite importar desde src/classic/ (este archivo vive en /notebooks)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "classic"))

from levenshtein import build_levenshtein_matrix, levenshtein_distance, levenshtein_similarity
from needleman_wunsch import build_score_matrix, needleman_wunsch_alignment, needleman_wunsch_similarity

RUTA_CORPUS = os.path.join(os.path.dirname(__file__), "..", "data", "corpus_preprocesado.json")

# Artículos seleccionados en CAS-1 y ventana del fragmento usado en CAS-2
ARTICULOS_SELECCIONADOS = (2, 9)
VENTANA_FRAGMENTO_A = slice(0, 6)   # artículo 2, tokens [0:6]
VENTANA_FRAGMENTO_B = slice(9, 15)  # artículo 9, tokens [9:15]


def cargar_articulos(ruta_corpus, numeros):
    with open(ruta_corpus, "r", encoding="utf-8") as f:
        corpus = json.load(f)
    articulos = {doc["numero"]: doc for doc in corpus}
    faltantes = [n for n in numeros if n not in articulos]
    if faltantes:
        raise ValueError(f"No se encontraron en el corpus los artículos: {faltantes}")
    return {n: articulos[n] for n in numeros}


def imprimir_matriz(nombre_filas, nombre_columnas, matriz):
    ancho = max(len(str(v)) for fila in matriz for v in fila)
    for fila in matriz:
        print("  " + " ".join(str(v).rjust(ancho) for v in fila))


def demostrar_levenshtein(frag_a, frag_b):
    print("\n" + "=" * 70)
    print("LEVENSHTEIN — Fragmento representativo")
    print("=" * 70)
    print("Fragmento A (artículo 2, tokens[0:6]):", frag_a)
    print("Fragmento B (artículo 9, tokens[9:15]):", frag_b)

    D = build_levenshtein_matrix(frag_a, frag_b)
    print("\nMatriz de programación dinámica:")
    imprimir_matriz(frag_a, frag_b, D)

    dist = levenshtein_distance(frag_a, frag_b)
    sim = levenshtein_similarity(frag_a, frag_b)
    print(f"\nDistancia de Levenshtein = {dist}")
    print(f"Similitud normalizada    = {sim:.4f}")
    return dist, sim


def demostrar_needleman_wunsch(frag_a, frag_b, match=1, mismatch=-1, gap=-2):
    print("\n" + "=" * 70)
    print("NEEDLEMAN-WUNSCH — Fragmento representativo")
    print("=" * 70)
    print(f"Esquema de puntuación: match={match}, mismatch={mismatch}, gap={gap}")

    S = build_score_matrix(frag_a, frag_b, match, mismatch, gap)
    print("\nMatriz de puntuación:")
    imprimir_matriz(frag_a, frag_b, S)

    alineado_a, alineado_b, score = needleman_wunsch_alignment(frag_a, frag_b, match, mismatch, gap)
    sim = needleman_wunsch_similarity(frag_a, frag_b, match, mismatch, gap)

    print("\nAlineamiento óptimo (backtracking):")
    print("  A:", " | ".join(alineado_a))
    print("  B:", " | ".join(alineado_b))
    print(f"\nScore de alineamiento = {score}")
    print(f"Similitud normalizada = {sim:.4f}")
    return score, sim


def resultado_final_abstracts_completos(art_a, art_b, num_a, num_b):
    print("\n" + "=" * 70)
    print(f"RESULTADO FINAL — Artículos completos ({num_a} vs {num_b})")
    print("=" * 70)
    print(f"Longitud artículo {num_a}: {len(art_a)} tokens")
    print(f"Longitud artículo {num_b}: {len(art_b)} tokens")

    dist_lev = levenshtein_distance(art_a, art_b)
    sim_lev = levenshtein_similarity(art_a, art_b)
    print(f"\nLevenshtein       -> distancia = {dist_lev:5d}   similitud = {sim_lev:.4f}")

    _, _, score_nw = needleman_wunsch_alignment(art_a, art_b, match=1, mismatch=-1, gap=-2)
    sim_nw = needleman_wunsch_similarity(art_a, art_b, match=1, mismatch=-1, gap=-2)
    print(f"Needleman-Wunsch  -> score     = {score_nw:5d}   similitud = {sim_nw:.4f}")


if __name__ == "__main__":
    num_a, num_b = ARTICULOS_SELECCIONADOS
    articulos = cargar_articulos(RUTA_CORPUS, ARTICULOS_SELECCIONADOS)

    tokens_a = articulos[num_a]["abstract_preprocesado"]
    tokens_b = articulos[num_b]["abstract_preprocesado"]

    frag_a = tokens_a[VENTANA_FRAGMENTO_A]
    frag_b = tokens_b[VENTANA_FRAGMENTO_B]

    print(f"Caso de estudio CAS-1/CAS-2: artículos {num_a} y {num_b}")
    print(f"  [{num_a}] {articulos[num_a]['titulo']}")
    print(f"  [{num_b}] {articulos[num_b]['titulo']}")

    demostrar_levenshtein(frag_a, frag_b)
    demostrar_needleman_wunsch(frag_a, frag_b)
    resultado_final_abstracts_completos(tokens_a, tokens_b, num_a, num_b)
