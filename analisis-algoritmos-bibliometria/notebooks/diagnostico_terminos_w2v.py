"""
Diagnostico: que significado tienen en Word2Vec los terminos del dominio
=========================================================================

Complemento de IA-2. El reporte de cobertura mostro que terminos como
"ai", "gai", "aied" (-> "Aied") y "genai" (-> "Genai") SI existen en el
modelo de Google News (2013). Este script revisa si ese vector corresponde
al significado que tienen en el corpus (inteligencia artificial en
educacion) o a otro (nombres propios, otros idiomas, etc.), mostrando sus
vecinos mas cercanos en el modelo.

Nota: most_similar() de gensim se usa aqui SOLO como herramienta de
diagnostico para interpretar el modelo. No forma parte del calculo de
similitud del proyecto (eso es IA-4, implementado a mano).

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe notebooks\\diagnostico_terminos_w2v.py F:\\modelos-ia\\word2vec-google-news-300.gz
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ia.embeddings_w2v import buscar_vector, cargar_modelo

# Terminos del corpus cuyo significado en el modelo es dudoso, mas dos
# terminos de control cuyo significado deberia ser el esperado.
TERMINOS = ["ai", "aied", "genai", "gai", "chatbot", "education", "assessment"]

# Palabras candidatas para la tabla EXPANSIONES de embeddings_w2v.py, para
# confirmar que su significado en el modelo es el correcto. "generative" se
# conserva aqui como evidencia de por que se descarto (significa exploracion
# minera en el modelo), igual que "higher" (significa "mas alto") y
# "higher_education" (no existe en el modelo).
TERMINOS_EXPANSION = [
    "artificial_intelligence", "chatbot", "higher_education", "higher", "generative",
]
VECINOS = 8


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else None
    modelo = cargar_modelo(ruta_modelo=ruta)

    for termino in TERMINOS:
        _, variante = buscar_vector(termino, modelo)
        if variante is None:
            print(f"\n{termino}: no esta en el modelo")
            continue
        vecinos = modelo.most_similar(variante, topn=VECINOS)
        print(f"\n{termino} (buscado como '{variante}'):")
        print("   " + ", ".join(f"{palabra} ({sim:.2f})" for palabra, sim in vecinos))

    # Referencia: la forma en mayusculas tampoco es confiable
    if "AI" in modelo:
        vecinos = modelo.most_similar("AI", topn=VECINOS)
        print("\nReferencia 'AI' (mayusculas):")
        print("   " + ", ".join(f"{palabra} ({sim:.2f})" for palabra, sim in vecinos))

    print("\n--- Palabras de la tabla de expansiones ---")
    for palabra in TERMINOS_EXPANSION:
        if palabra not in modelo:
            print(f"\n{palabra}: NO esta en el modelo (revisar EXPANSIONES)")
            continue
        vecinos = modelo.most_similar(palabra, topn=VECINOS)
        print(f"\n{palabra}:")
        print("   " + ", ".join(f"{p} ({sim:.2f})" for p, sim in vecinos))


if __name__ == "__main__":
    main()
