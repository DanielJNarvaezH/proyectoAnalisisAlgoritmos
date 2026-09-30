"""
Embeddings de documento con Word2Vec preentrenado (tarea IA-2)
==============================================================

Genera un vector de 300 dimensiones por abstract usando el modelo
preentrenado de Google News (word2vec-google-news-300), segun la decision
documentada en docs/modelos_ia.md.

Division de responsabilidades (exigida por el enunciado):
  - El modelo preentrenado (gensim) SOLO aporta el vector de cada palabra.
  - El vector del documento (promedio de los vectores de sus palabras) se
    calcula a mano en este modulo, con listas y ciclos de Python.
  - La similitud coseno / distancia euclidiana NO se calcula aqui: es la
    tarea IA-4, tambien implementada a mano.

Vector del documento:

    v(d) = (1 / |T|) * sum( v(t) )   para t en T

donde T son los tokens de `abstract_preprocesado` que existen en el
vocabulario del modelo. Los tokens que no existen (OOV) se excluyen del
promedio y se registran para reportar la cobertura por articulo.

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\ia\\embeddings_w2v.py
    .\\venv\\Scripts\\python.exe src\\ia\\embeddings_w2v.py --limite 1000000
    .\\venv\\Scripts\\python.exe src\\ia\\embeddings_w2v.py --ruta-modelo F:\\modelos-ia\\word2vec-google-news-300.gz

Con --ruta-modelo se carga un archivo descargado manualmente (por ejemplo con
el navegador, que puede reanudar descargas cortadas), sin usar el
descargador de gensim. URL oficial del archivo (release de gensim-data):
https://github.com/RaRe-Technologies/gensim-data/releases/download/word2vec-google-news-300/word2vec-google-news-300.gz

La primera ejecucion descarga el modelo (~1,6 GB) en la carpeta indicada
por la variable de entorno GENSIM_DATA_DIR (si no esta definida, gensim usa
~/gensim-data, que en Windows queda en el disco C:). El modelo debe quedar
FUERA del repositorio y de carpetas sincronizadas como OneDrive. El
resultado se guarda en data/embeddings/word2vec.json.
"""

import argparse
import json
import os
from datetime import date

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUTA_CORPUS = os.path.join(RAIZ, "data", "corpus_preprocesado.json")
RUTA_SALIDA = os.path.join(RAIZ, "data", "embeddings", "word2vec.json")

NOMBRE_MODELO = "word2vec-google-news-300"
DIMENSION = 300

# Siglas del dominio que SI existen en el modelo, pero con otro significado
# (verificado con notebooks/diagnostico_terminos_w2v.py):
#   "ai"    -> italiano ("che", "essere", "tutto")
#   "Aied"  -> nombres propios de noticias de Irak
#   "Genai" -> nombres propios de persona
#   "gai"   -> cocina vietnamita ("banh", "khao")
#   "AI"    -> videojuegos ("Enemy_AI", "mechs")
# Tambien se expanden terminos del dominio que NO existen en el modelo y son
# centrales en algun articulo: "aihed" (AI in Higher Education, art. 12) y
# "chatgpt" (posterior al modelo; 5 apariciones en el art. 19).
# Antes de buscarlas se reemplazan por su forma expandida. Si la expansion
# tiene varias palabras, el vector del token es el promedio de ellas, de
# modo que cada aparicion sigue contando como UN token en el documento.
# "artificial_intelligence" es una frase de un solo token en Google News.
# Toda palabra de una expansion debe pasar el mismo diagnostico: "generative"
# se descarto porque en el modelo significa exploracion minera
# ("hydrothermal", "gold_copper_porphyry"), y "higher" sola porque significa
# "mas alto" ("lower", "greater"); la frase "higher_education" no existe en
# el modelo, asi que "aihed" se expande igual que "aied".
EXPANSIONES = {
    "ai": ["artificial_intelligence"],
    "aied": ["artificial_intelligence", "education"],
    "genai": ["artificial_intelligence"],
    "gai": ["artificial_intelligence"],
    "aihed": ["artificial_intelligence", "education"],
    "chatgpt": ["artificial_intelligence", "chatbot"],
}


# ---------------------------------------------------------------------------
# 1. Busqueda del vector de una palabra
# ---------------------------------------------------------------------------

def variantes_de_busqueda(token):
    """
    Formas en que se busca un token en el modelo, en orden de preferencia.

    El modelo de Google News distingue mayusculas y los tokens del corpus
    estan en minuscula. Si la forma en minuscula no existe, se prueba la
    capitalizada ("python" -> "Python") y la forma en mayusculas, util para
    siglas ("ai" -> "AI").
    """
    variantes = [token, token.capitalize(), token.upper()]
    unicas = []
    for variante in variantes:
        if variante not in unicas:
            unicas.append(variante)
    return unicas


def buscar_vector(token, vocabulario):
    """
    Busca el vector de un token en el vocabulario del modelo.

    `vocabulario` es cualquier objeto que soporte `palabra in vocabulario`
    y `vocabulario[palabra]` (un KeyedVectors de gensim o un diccionario
    en las pruebas unitarias).

    Retorna (vector_como_lista, variante_encontrada) o (None, None) si
    ninguna variante existe en el modelo.
    """
    for variante in variantes_de_busqueda(token):
        if variante in vocabulario:
            vector = [float(componente) for componente in vocabulario[variante]]
            return vector, variante
    return None, None


# ---------------------------------------------------------------------------
# 2. Vector del documento: promedio implementado a mano
# ---------------------------------------------------------------------------

def promediar_vectores(vectores, dimension):
    """
    Promedio componente a componente de una lista de vectores.

    Si la lista esta vacia (ningun token encontrado en el modelo), retorna
    el vector cero: el documento no tiene representacion semantica, y IA-4
    debe tratar ese caso (el coseno con un vector cero es indefinido).
    """
    suma = [0.0] * dimension
    for vector in vectores:
        if len(vector) != dimension:
            raise ValueError(
                f"Vector de dimension {len(vector)}, se esperaba {dimension}"
            )
        for i in range(dimension):
            suma[i] += vector[i]

    if not vectores:
        return suma

    cantidad = len(vectores)
    return [valor / cantidad for valor in suma]


def vector_expansion(token, vocabulario, expansiones, dimension):
    """
    Vector de un token segun la tabla de expansiones: promedio de los
    vectores de las palabras de su expansion que existan en el modelo.

    Retorna (vector, palabras_usadas) o (None, None) si el token no tiene
    expansion o ninguna de sus palabras esta en el modelo.
    """
    if not expansiones or token not in expansiones:
        return None, None
    vectores = []
    usadas = []
    for palabra in expansiones[token]:
        if palabra in vocabulario:
            vectores.append([float(x) for x in vocabulario[palabra]])
            usadas.append(palabra)
    if not vectores:
        return None, None
    return promediar_vectores(vectores, dimension), usadas


def vector_documento(tokens, vocabulario, dimension=DIMENSION, expansiones=None):
    """
    Calcula el embedding de un documento a partir de sus tokens.

    Retorna un diccionario con:
      - vector: lista de `dimension` floats (promedio de los tokens encontrados)
      - tokens_totales: cantidad de tokens del documento (con repeticiones)
      - tokens_encontrados: cuantos de ellos tienen vector en el modelo
      - cobertura: tokens_encontrados / tokens_totales
      - oov: tokens distintos sin vector, ordenados alfabeticamente
      - variantes: tokens que se encontraron con otra forma (ej. "nlp" -> "NLP")
      - expansiones: tokens reemplazados por su expansion y las palabras usadas

    `expansiones` es un diccionario {token: [palabras]} (ver EXPANSIONES);
    si es None, no se expande ningun token.
    """
    vectores = []
    oov = set()
    variantes = {}
    expandidos = {}

    for token in tokens:
        vector, usadas = vector_expansion(token, vocabulario, expansiones, dimension)
        if vector is not None:
            vectores.append(vector)
            expandidos[token] = usadas
            continue

        vector, variante = buscar_vector(token, vocabulario)
        if vector is None:
            oov.add(token)
            continue
        vectores.append(vector)
        if variante != token:
            variantes[token] = variante

    total = len(tokens)
    encontrados = len(vectores)
    return {
        "vector": promediar_vectores(vectores, dimension),
        "tokens_totales": total,
        "tokens_encontrados": encontrados,
        "cobertura": encontrados / total if total else 0.0,
        "oov": sorted(oov),
        "variantes": dict(sorted(variantes.items())),
        "expansiones": dict(sorted(expandidos.items())),
    }


# ---------------------------------------------------------------------------
# 3. Corpus completo, lectura y escritura de embeddings
# ---------------------------------------------------------------------------

def cargar_corpus(ruta=RUTA_CORPUS):
    with open(ruta, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def generar_embeddings_corpus(corpus, vocabulario, dimension=DIMENSION,
                              expansiones=None):
    """Aplica vector_documento() a cada articulo del corpus preprocesado."""
    articulos = []
    for articulo in corpus:
        resultado = vector_documento(
            articulo["abstract_preprocesado"], vocabulario, dimension, expansiones
        )
        articulos.append({
            "numero": articulo["numero"],
            "titulo": articulo["titulo"],
            **resultado,
        })
    return articulos


def guardar_embeddings(ruta, modelo, dimension, entrada, articulos, extra=None):
    """
    Guarda embeddings en el formato comun del proyecto (IA-2 e IA-3), para
    que IA-4, el clustering y el backend lean ambos modelos de la misma forma:

    {
      "modelo": str, "dimension": int, "entrada": str, "fecha": "AAAA-MM-DD",
      ...campos extra del modelo...,
      "articulos": [ {"numero": int, "titulo": str, "vector": [floats], ...}, ... ]
    }
    """
    datos = {
        "modelo": modelo,
        "dimension": dimension,
        "entrada": entrada,
        "fecha": date.today().isoformat(),
    }
    if extra:
        datos.update(extra)
    datos["articulos"] = articulos

    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def cargar_embeddings(ruta=RUTA_SALIDA):
    """
    Lee un archivo de embeddings y retorna {numero_articulo: vector}.
    Es la funcion que deben usar IA-4, el clustering y el backend.
    """
    with open(ruta, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    return {art["numero"]: art["vector"] for art in datos["articulos"]}


# ---------------------------------------------------------------------------
# 4. Carga del modelo preentrenado (unica parte que usa gensim)
# ---------------------------------------------------------------------------

def cargar_modelo(limite=None, ruta_modelo=None):
    """
    Descarga (solo la primera vez) y carga el modelo de Google News.

    `limite` carga solo las N palabras mas frecuentes del modelo, para
    reducir memoria: el modelo completo (3 millones de palabras) ocupa
    ~3,6 GB de RAM; con limite=1_000_000 ocupa ~1,2 GB.

    `ruta_modelo` permite cargar un archivo .gz o .bin ya descargado; si no
    se indica, se usa el descargador de gensim (que descarga primero a la
    carpeta temporal del sistema y no puede reanudar si la conexion se corta).

    gensim se importa aqui dentro para que el resto del modulo (y sus
    pruebas unitarias) funcione sin tener gensim instalado.
    """
    from gensim.models import KeyedVectors

    if ruta_modelo is None:
        import gensim.downloader as api

        print(f"Carpeta de modelos de gensim: {api.BASE_DIR}")
        ruta_modelo = api.load(NOMBRE_MODELO, return_path=True)
    elif not os.path.isfile(ruta_modelo):
        raise FileNotFoundError(f"No existe el archivo del modelo: {ruta_modelo}")

    print(f"Leyendo modelo desde: {ruta_modelo}")
    return KeyedVectors.load_word2vec_format(
        ruta_modelo, binary=True, limit=limite
    )


# ---------------------------------------------------------------------------
# 5. Reporte en consola
# ---------------------------------------------------------------------------

def imprimir_reporte(articulos):
    print("\n=== Cobertura del vocabulario por articulo ===")
    print(f"{'Art.':>4}  {'Tokens':>6}  {'Encontrados':>11}  {'Cobertura':>9}  OOV")
    for art in articulos:
        oov = ", ".join(art["oov"]) if art["oov"] else "-"
        print(f"{art['numero']:>4}  {art['tokens_totales']:>6}  "
              f"{art['tokens_encontrados']:>11}  {art['cobertura']:>9.1%}  {oov}")

    total = sum(a["tokens_totales"] for a in articulos)
    encontrados = sum(a["tokens_encontrados"] for a in articulos)
    print(f"\nCobertura global: {encontrados}/{total} = {encontrados / total:.1%}")

    variantes = {}
    for art in articulos:
        variantes.update(art["variantes"])
    if variantes:
        print("Tokens encontrados con otra forma:",
              ", ".join(f"{t} -> {v}" for t, v in sorted(variantes.items())))

    expandidos = {}
    for art in articulos:
        expandidos.update(art.get("expansiones", {}))
    if expandidos:
        print("Siglas expandidas:",
              ", ".join(f"{t} -> {' + '.join(p)}" for t, p in sorted(expandidos.items())))

    bajos = [a["numero"] for a in articulos if a["cobertura"] < 0.90]
    if bajos:
        print(f"Articulos con cobertura menor al 90 % (ver plan B en "
              f"docs/modelos_ia.md): {bajos}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument(
        "--limite", type=int, default=None,
        help="Cargar solo las N palabras mas frecuentes del modelo "
             "(por defecto se carga completo, ~3,6 GB de RAM)",
    )
    parser.add_argument(
        "--ruta-modelo", default=None,
        help="Archivo .gz/.bin del modelo ya descargado (evita el "
             "descargador de gensim)",
    )
    parser.add_argument(
        "--sin-expansiones", action="store_true",
        help="No expandir las siglas de EXPANSIONES (solo para comparar "
             "con la version sin correccion)",
    )
    args = parser.parse_args()
    expansiones = None if args.sin_expansiones else EXPANSIONES

    corpus = cargar_corpus()
    print(f"Corpus: {len(corpus)} articulos")
    print(f"Cargando {NOMBRE_MODELO} "
          f"({'completo' if args.limite is None else f'limite {args.limite:,}'}). "
          f"{'' if args.ruta_modelo else 'La primera vez descarga ~1,6 GB...'}")
    modelo = cargar_modelo(args.limite, args.ruta_modelo)
    print(f"Modelo cargado: {len(modelo.key_to_index):,} palabras, "
          f"dimension {modelo.vector_size}")

    articulos = generar_embeddings_corpus(
        corpus, modelo, modelo.vector_size, expansiones
    )
    imprimir_reporte(articulos)

    guardar_embeddings(
        RUTA_SALIDA,
        modelo=NOMBRE_MODELO,
        dimension=modelo.vector_size,
        entrada="abstract_preprocesado",
        articulos=articulos,
        extra={
            "metodo": "promedio aritmetico de los vectores de palabras",
            "limite_vocabulario": args.limite,
            "expansiones": expansiones,
        },
    )
    print(f"\nEmbeddings guardados en: {RUTA_SALIDA}")


if __name__ == "__main__":
    main()
