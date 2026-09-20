import sys
import os
import math
import json

# Añadir la raíz del proyecto al path para poder importar desde la carpeta 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar las funciones desde tus módulos originales en src/classic/
from src.classic.tfidf_cosine import (
    tokenizar as tokenizar_tfidf,
    calcular_tf,
    calcular_idf,
    construir_vocabulario,
    vectorizar_tfidf,
    similitud_coseno
)
from src.classic.jaccard import (
    texto_a_conjunto,
    jaccard
)

def encabezado_seccion(titulo):
    print("\n" + "="*70)
    print(f" {titulo.upper()} ")
    print("="*70)

def cargar_articulos_desde_json():
    """
    Busca y carga el archivo corpus en la carpeta data/.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    rutas_posibles = [
        os.path.join(base_dir, 'data', 'corpus_preprocesado.json'),
        os.path.join(base_dir, 'data', 'corpus.json')
    ]

    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            with open(ruta, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                if isinstance(datos, dict):
                    for clave in ['documentos', 'corpus', 'articulos']:
                        if clave in datos and isinstance(datos[clave], list):
                            return datos[clave]
                    return list(datos.values())
                return datos

    raise FileNotFoundError("No se encontró 'corpus_preprocesado.json' o 'corpus.json' en la carpeta data/")

def obtener_texto_util(articulo):
    """
    Extrae de forma segura el texto relevante de un objeto diccionario.
    Prioriza el abstract/resumen, si no existe usa el título.
    """
    if isinstance(articulo, str):
        return articulo
    elif isinstance(articulo, list):
        return " ".join(str(x) for x in articulo)
    elif isinstance(articulo, dict):
        # Intentar extraer contenido por prioridades de claves comunes
        for clave in ['abstract', 'resumen', 'texto', 'content', 'description']:
            if clave in articulo and articulo[clave]:
                val = articulo[clave]
                return " ".join(val) if isinstance(val, list) else str(val)

        # Si no tiene abstract, usamos el título
        if 'titulo' in articulo and articulo['titulo']:
            return str(articulo['titulo'])

        # Si no encuentra claves conocidas, une todos los valores de tipo string/lista
        valores = []
        for v in articulo.values():
            if isinstance(v, str):
                valores.append(v)
            elif isinstance(v, list):
                valores.append(" ".join(str(x) for x in v))
        return " ".join(valores)
    return str(articulo)

def mostrar_paso_a_paso_articulos(corpus, idx_a=1, idx_b=8):
    """
    Muestra la ejecución paso a paso de TF-IDF, Similitud Coseno y Jaccard
    enfocándose específicamente en los artículos seleccionados.
    """
    art_2_dict = corpus[idx_a]
    art_9_dict = corpus[idx_b]

    # Extraer el texto real para procesar
    art_2_texto = obtener_texto_util(art_2_dict)
    art_9_texto = obtener_texto_util(art_9_dict)

    # Preparar corpus de texto plano para alimentar los algoritmos clásicos
    corpus_texto = [obtener_texto_util(doc) for doc in corpus]

    # =========================================================================
    # SECCIÓN 1: TF-IDF & SIMILITUD COSENO
    # =========================================================================
    encabezado_seccion("1. TRAZA COMPLETA: TF-IDF Y SIMILITUD COSENO (ART. 2 vs ART. 9)")

    print(f"• Detalle Art. 2: {art_2_dict.get('titulo', 'Sin título')[:90]}...")
    print(f"• Detalle Art. 9: {art_9_dict.get('titulo', 'Sin título')[:90]}...\n")

    # Procesamos el corpus de texto plano
    docs_tokenizados = [tokenizar_tfidf(txt) for txt in corpus_texto]
    vocabulario = construir_vocabulario(docs_tokenizados)
    idf_dicc = calcular_idf(docs_tokenizados)
    vocab_sistema, matriz_tfidf = vectorizar_tfidf(corpus_texto)

    tokens_2 = docs_tokenizados[idx_a]
    tokens_9 = docs_tokenizados[idx_b]

    print("-> PASO 1.1: Tokenización de los objetivos:")
    print(f"   Tokens Art 2 (primeros 15): {tokens_2[:15]}")
    print(f"   Tokens Art 9 (primeros 15): {tokens_9[:15]}\n")

    print("-> PASO 1.2: Valores IDF de los tokens compartidos o relevantes (Muestra):")
    tokens_interes = set(tokens_2).union(set(tokens_9))
    # Mostramos los primeros 10 términos ordenados para no saturar la consola
    for t in sorted(tokens_interes)[:10]:
        df_t = sum(1 for tokens in docs_tokenizados if t in tokens)
        print(f"   - '{t}': df={df_t} de {len(corpus)} docs -> IDF = {idf_dicc.get(t, 1.0):.4f}")
    print("   ... (más términos omitidos para simplificar salida) ...\n")

    print("-> PASO 1.3: Vectores TF-IDF Resultantes (Solo términos con valor > 0):")
    vec_2 = matriz_tfidf[idx_a]
    vec_9 = matriz_tfidf[idx_b]

    print("   [Art 2]: ", {vocab_sistema[i]: round(vec_2[i], 4) for i in range(len(vocab_sistema)) if vec_2[i] > 0})
    print("   [Art 9]: ", {vocab_sistema[i]: round(vec_9[i], 4) for i in range(len(vocab_sistema)) if vec_9[i] > 0})

    print("\n-> PASO 1.4: Cálculo de Similitud Coseno:")
    producto_punto = sum(a * b for a, b in zip(vec_2, vec_9))
    norma_2 = math.sqrt(sum(x**2 for x in vec_2))
    norma_9 = math.sqrt(sum(x**2 for x in vec_9))
    sim_cos = similitud_coseno(vec_2, vec_9)

    print(f"   - Producto punto (∑ A_i * B_i) = {producto_punto:.6f}")
    print(f"   - Norma Art 2 (||A||) = {norma_2:.6f}")
    print(f"   - Norma Art 9 (||B||) = {norma_9:.6f}")
    print(f"   => SIMILITUD COSENO = {sim_cos:.6f}")

    # =========================================================================
    # SECCIÓN 2: COEFICIENTE DE JACCARD
    # =========================================================================
    encabezado_seccion("2. TRAZA COMPLETA: COEFICIENTE DE JACCARD (ART. 2 vs ART. 9)")

    conjunto_2 = texto_a_conjunto(art_2_texto, n=1)
    conjunto_9 = texto_a_conjunto(art_9_texto, n=1)

    print("-> PASO 2.1: Tamaño de los Conjuntos de Unigramas Únicos:")
    print(f"   Cardinalidad de conjunto Art 2 = {len(conjunto_2)}")
    print(f"   Cardinalidad de conjunto Art 9 = {len(conjunto_9)}\n")

    interseccion = conjunto_2.intersection(conjunto_9)
    union = conjunto_2.union(conjunto_9)

    print("-> PASO 2.2: Operaciones de Conjuntos:")
    print(f"   - Intersección (A ∩ B) [Elementos compartidos]: {sorted(list(interseccion))[:10]} ...")
    print(f"     Tamaño de la intersección = {len(interseccion)}")
    print(f"   - Tamaño de la Unión (A ∪ B) [Total elementos únicos] = {len(union)}")

    print("\n-> PASO 2.3: Coeficiente Resultante:")
    coef_jaccard = jaccard(conjunto_2, conjunto_9)
    print(f"   Fórmula: J(A, B) = |A ∩ B| / |A ∪ B|")
    print(f"   J(Art 2, Art 9) = {len(interseccion)} / {len(union)} = {coef_jaccard:.6f}")


if __name__ == "__main__":
    try:
        corpus_total = cargar_articulos_desde_json()

        if len(corpus_total) < 9:
            print(f"⚠️ Alerta: El corpus solo contiene {len(corpus_total)} elementos. Se requiere un mínimo de 9.")
            sys.exit(1)

        mostrar_paso_a_paso_articulos(corpus_total, idx_a=1, idx_b=8)

    except FileNotFoundError as e:
        print(f"❌ Error de archivo: {e}")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")
