"""
preprocessing.py

Modulo de preprocesamiento de texto (tarea PRE-1).

Provee una funcion reutilizable, `preprocess_text`, que limpia y normaliza
el abstract de un articulo cientifico dejandolo listo para ser consumido
por los algoritmos de similitud clasicos (CLA-*), los modelos de IA (IA-*)
y el modulo de clustering (CLU-*).

Pasos de preprocesamiento aplicados:
    1. Normalizacion Unicode y reconstruccion de palabras partidas:
       pypdf extrajo varias ligaduras tipograficas (fi, fl...) insertando
       ademas un espacio espurio justo antes de ellas cuando estan en
       mitad de palabra (ej. "arti ﬁcial" -> deberia ser "artificial",
       "signi ﬁcant" -> "significant"). Se reconstruyen estos casos
       verificando contra un diccionario de ingles (nltk.corpus.words)
       si el fragmento de la ligadura es o no una palabra valida por si
       sola: si NO lo es (ej. "ficial"), se une con el prefijo anterior;
       si SI lo es (ej. "field", "findings"), se deja como dos palabras
       distintas porque realmente lo son (ej. "research field").
       Tambien se reconstruyen palabras partidas por guion de fin de
       linea (ej. "long-\nterm" -> "long-term" o "important" partido).
    2. Minusculas.
    3. Tokenizacion y eliminacion de puntuacion/numeros (se conservan solo
       tokens alfabeticos).
    4. Eliminacion de stopwords en ingles (los abstracts del corpus estan
       en ingles) mas una pequeña lista adicional de residuos tipicos de
       escritura academica (ej. "et", "al", "fig", "eq").
    5. Lematizacion (por defecto) o stemming, segun el parametro `method`.

Uso tipico desde otro modulo:

    from src.preprocessing import preprocess_text

    tokens = preprocess_text(abstract)          # lista de tokens limpios
    texto  = " ".join(tokens)                   # si se necesita como string

Uso como script (genera un corpus preprocesado para inspeccion / PRE-2):

    python src/preprocessing.py
"""

from __future__ import annotations

import json
import re
import string
import unicodedata
from pathlib import Path
from typing import Literal

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize

# ---------------------------------------------------------------------------
# Descarga de recursos NLTK, con degradacion controlada.
#
# El servidor de datos de NLTK (raw.githubusercontent.com) a veces falla de
# forma temporal (error 503 "Backend.max_conn reached"), fuera del control
# del equipo. En vez de detener todo el script con un traceback, cada
# recurso "de lujo" (que mejora la calidad pero no es indispensable) se
# marca como disponible o no, y las funciones que lo usan cambian
# automaticamente a una alternativa mas simple si no esta disponible.
# Basta con volver a correr el script cuando el servidor se recupere para
# obtener la version completa sin cambiar nada en el codigo.
# ---------------------------------------------------------------------------

def _disponible(ruta_recurso: str, nombre_paquete: str) -> bool:
    """Intenta encontrar el recurso; si falta, intenta descargarlo una vez.
    Devuelve True/False segun quede disponible, sin lanzar excepciones."""
    try:
        nltk.data.find(ruta_recurso)
        return True
    except LookupError:
        try:
            nltk.download(nombre_paquete, quiet=True)
            nltk.data.find(ruta_recurso)
            return True
        except Exception:
            return False


# Indispensables para el funcionamiento minimo (tokenizar + stopwords).
_TIENE_PUNKT = _disponible("tokenizers/punkt_tab", "punkt_tab") or _disponible(
    "tokenizers/punkt", "punkt"
)
_TIENE_STOPWORDS = _disponible("corpora/stopwords", "stopwords")

# "De lujo": mejoran la calidad del preprocesamiento pero tienen alternativa.
_TIENE_WORDNET = _disponible("corpora/wordnet", "wordnet")
_TIENE_OMW = _disponible("corpora/omw-1.4", "omw-1.4")
_TIENE_TAGGER = _disponible(
    "taggers/averaged_perceptron_tagger_eng", "averaged_perceptron_tagger_eng"
) or _disponible("taggers/averaged_perceptron_tagger", "averaged_perceptron_tagger")
_TIENE_VOCABULARIO = _disponible("corpora/words", "words")

if not _TIENE_PUNKT:
    print(
        "[preprocessing] Aviso: no se pudo descargar el tokenizador 'punkt_tab' "
        "(posible falla temporal del servidor de NLTK). Se usara una "
        "tokenizacion simple de respaldo (separar por palabras alfabeticas)."
    )
if not _TIENE_WORDNET:
    print(
        "[preprocessing] Aviso: no se pudo descargar 'wordnet' (posible falla "
        "temporal del servidor de NLTK). Se usara stemming en vez de "
        "lematizacion para esta ejecucion. Vuelve a correr el script mas "
        "tarde para obtener lematizacion."
    )
if not _TIENE_VOCABULARIO:
    print(
        "[preprocessing] Aviso: no se pudo descargar el diccionario 'words' "
        "(posible falla temporal del servidor de NLTK). La correccion de "
        "ligaduras partidas (ej. 'arti ficial' -> 'artificial') se hara de "
        "forma mas simple, sin verificar contra diccionario."
    )
if not _TIENE_TAGGER:
    print(
        "[preprocessing] Aviso: no se pudo descargar el etiquetador POS. "
        "La lematizacion (si esta disponible) se hara sin desambiguar por "
        "categoria gramatical (un poco menos precisa, pero funcional)."
    )


# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------

IDIOMA = "english"

# Residuos comunes de escritura academica que NLTK no considera stopwords
# pero que no aportan valor semantico para similitud/clustering.
STOPWORDS_ADICIONALES = {
    "et", "al", "fig", "figure", "table", "eq", "ie", "eg",
    "http", "https", "doi", "www",
}

if _TIENE_STOPWORDS:
    STOPWORDS_EN = set(stopwords.words(IDIOMA)) | STOPWORDS_ADICIONALES
else:
    # Lista minima de respaldo por si tampoco se pudo descargar 'stopwords'.
    print(
        "[preprocessing] Aviso: no se pudo descargar 'stopwords'. Se usa una "
        "lista reducida de respaldo; vuelve a correr el script mas tarde "
        "para obtener la lista completa de NLTK."
    )
    STOPWORDS_EN = {
        "a", "an", "the", "and", "or", "but", "of", "in", "on", "to", "for",
        "with", "is", "are", "was", "were", "be", "been", "being", "this",
        "that", "these", "those", "it", "its", "as", "by", "at", "from",
        "we", "our", "their", "which", "also", "can", "has", "have", "had",
    } | STOPWORDS_ADICIONALES

# Diccionario de ingles usado unicamente para decidir si un fragmento
# generado por una ligadura mal extraida es o no una palabra real.
# Si no esta disponible, la correccion de ligaduras simplemente se hace
# sin esa verificacion extra (ver _reconstruir_ligaduras_partidas).
_VOCABULARIO_INGLES: set[str] = set()
if _TIENE_VOCABULARIO:
    from nltk.corpus import words as nltk_words
    _VOCABULARIO_INGLES = set(w.lower() for w in nltk_words.words())

_lematizador = WordNetLemmatizer()
_stemmer = PorterStemmer()

# Traduccion de etiquetas POS de NLTK al formato que espera WordNet,
# para que la lematizacion sea mas precisa (ej. "studies" -> "study",
# no "studie").
_POS_WORDNET = {"J": "a", "V": "v", "N": "n", "R": "r"}


def _pos_a_wordnet(tag: str) -> str:
    return _POS_WORDNET.get(tag[0].upper(), "n")


# ---------------------------------------------------------------------------
# Pasos individuales (expuestos por si algun modulo los necesita por separado)
# ---------------------------------------------------------------------------

def _es_palabra_valida(palabra: str) -> bool:
    """True si `palabra` (o su singular simple) existe en el diccionario ingles.
    Si el diccionario no esta disponible (fallo de descarga), devuelve
    siempre False y la reconstruccion de ligaduras se hace de forma mas
    simple (ver nota en _reconstruir_ligaduras_partidas)."""
    if not _TIENE_VOCABULARIO:
        return False
    palabra = palabra.lower()
    if palabra in _VOCABULARIO_INGLES:
        return True
    if palabra.endswith("s") and palabra[:-1] in _VOCABULARIO_INGLES:
        return True  # plural simple, ej. "findings" -> "finding"
    return False


def _reconstruir_ligaduras_partidas(texto: str) -> str:
    """
    Corrige el espacio espurio que pypdf inserta antes de una ligadura
    (fi, fl, ffi...) cuando esta va en mitad de palabra.

    Solo une el prefijo con el fragmento si el fragmento, ya con la
    ligadura corregida, NO es una palabra valida por si sola (lo que
    indica que en realidad es un pedazo de una palabra mas larga, ej.
    "arti" + "ficial" -> "artificial"). Si el fragmento SI es una
    palabra valida (ej. "field", "findings"), se respeta el espacio
    porque de verdad son dos palabras distintas (ej. "research field").

    Si el diccionario de ingles no esta disponible (fallo de descarga),
    esta reconstruccion "inteligente" se omite por completo para no
    arriesgarse a fusionar por error palabras reales (ej. "research" +
    "field"); en ese caso la ligadura igual queda corregida a nivel de
    caracter mas adelante, en normalizar_unicode, mediante NFKC.
    """
    if not _TIENE_VOCABULARIO:
        return texto

    patron = re.compile(r"(\w+)(\s+)([\ufb00-\ufb06]\w*)")

    def _reemplazar(coincidencia: re.Match) -> str:
        prefijo, _, fragmento_liga = coincidencia.groups()
        fragmento_normalizado = unicodedata.normalize("NFKC", fragmento_liga)
        if _es_palabra_valida(fragmento_normalizado):
            return coincidencia.group(0)
        return prefijo + fragmento_liga

    return patron.sub(_reemplazar, texto)


def _reconstruir_saltos_de_linea(texto: str) -> str:
    """Reune palabras partidas por guion de fin de linea (ej. 'long-\\nterm')
    solo cuando la union sin guion forma una palabra valida del diccionario.
    Se omite si el diccionario no esta disponible (ver nota arriba)."""
    if not _TIENE_VOCABULARIO:
        return texto

    def _reemplazar(coincidencia: re.Match) -> str:
        junto = coincidencia.group(1) + coincidencia.group(2)
        if _es_palabra_valida(junto):
            return junto
        return coincidencia.group(0)

    return re.sub(r"(\w+)-\s+(\w+)", _reemplazar, texto)


def normalizar_unicode(texto: str) -> str:
    """
    Corrige ligaduras (ﬁ, ﬂ...) mal extraidas del PDF, reconstruye palabras
    partidas por espacios/guiones espurios, y homogeniza espacios.

    Nota: se detecto un unico caso residual en el corpus (articulo 5,
    "de fi- nitions" -> deberia ser "definitions") donde la ligadura y un
    salto de linea con guion caen sobre la misma palabra; por su rareza
    (1 caso en ~4000 palabras del corpus) no se resuelve con una regla
    generica y queda anotado para revision manual en la tarea PRE-2.
    """
    texto = _reconstruir_ligaduras_partidas(texto)
    texto = unicodedata.normalize("NFKC", texto)
    texto = _reconstruir_saltos_de_linea(texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def tokenizar_y_limpiar(texto: str) -> list[str]:
    """Minusculas + tokeniza + elimina puntuacion y numeros (solo alfabeticos).

    Intenta usar el tokenizador de NLTK; si falla en tiempo de ejecucion
    porque falta un recurso (ej. 'punkt_tab' no se pudo descargar), cae
    automaticamente a una tokenizacion simple por expresion regular que
    no depende de ningun dato descargado."""
    texto = texto.lower()

    try:
        tokens = word_tokenize(texto)
    except LookupError:
        tokens = re.findall(r"[a-zA-Z]+", texto)

    tabla_puntuacion = str.maketrans("", "", string.punctuation)
    tokens_limpios = []
    for token in tokens:
        token = token.translate(tabla_puntuacion)
        if token.isalpha() and len(token) > 1:
            tokens_limpios.append(token)
    return tokens_limpios


def eliminar_stopwords(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t not in STOPWORDS_EN]


def lematizar(tokens: list[str]) -> list[str]:
    """Lematiza con desambiguacion por categoria gramatical (POS) cuando el
    etiquetador esta disponible; si falla en tiempo de ejecucion (falta
    el tagger o wordnet), cae a stemming para esos tokens en vez de
    detener el proceso."""
    try:
        etiquetas = nltk.pos_tag(tokens)
        return [
            _lematizador.lemmatize(token, _pos_a_wordnet(tag))
            for token, tag in etiquetas
        ]
    except LookupError:
        pass

    try:
        return [_lematizador.lemmatize(token) for token in tokens]
    except LookupError:
        return aplicar_stemming(tokens)


def aplicar_stemming(tokens: list[str]) -> list[str]:
    return [_stemmer.stem(token) for token in tokens]


# ---------------------------------------------------------------------------
# Funcion principal reutilizable
# ---------------------------------------------------------------------------

def preprocess_text(
    texto: str,
    method: Literal["lemma", "stem"] = "lemma",
) -> list[str]:
    """
    Preprocesa un abstract y devuelve la lista de tokens limpios y normalizados.

    Esta es la funcion que deben importar los algoritmos de similitud
    (clasicos e IA) y de clustering.

    Parameters
    ----------
    texto : str
        Texto crudo del abstract (tal como viene en corpus.json).
    method : "lemma" | "stem"
        "lemma" (por defecto) usa lematizacion (WordNetLemmatizer, con
        desambiguacion por categoria gramatical). "stem" usa stemming
        (PorterStemmer), mas agresivo/rapido pero puede producir raices
        no siempre legibles (ej. "studies" -> "studi").

    Returns
    -------
    list[str]
        Tokens limpios, en minuscula, sin stopwords ni puntuacion, y
        lematizados/derivados segun `method`.
    """
    texto = normalizar_unicode(texto)
    tokens = tokenizar_y_limpiar(texto)
    tokens = eliminar_stopwords(tokens)

    if method == "lemma":
        tokens = lematizar(tokens)  # cae solo a stemming si wordnet/tagger fallan
    elif method == "stem":
        tokens = aplicar_stemming(tokens)
    else:
        raise ValueError(f"method debe ser 'lemma' o 'stem', se recibio: {method!r}")

    return tokens


def preprocess_corpus(
    ruta_entrada: str | Path,
    ruta_salida: str | Path | None = None,
    method: Literal["lemma", "stem"] = "lemma",
) -> list[dict]:
    """
    Aplica preprocess_text sobre el campo 'abstract' de cada articulo del
    corpus y agrega el resultado como 'abstract_preprocesado' (lista de
    tokens) y 'abstract_preprocesado_texto' (los tokens unidos en un
    string, util para algoritmos que esperan texto plano como TF-IDF).

    Si se indica `ruta_salida`, tambien guarda el resultado en un JSON
    (util para la validacion manual de PRE-2 y para no recalcular en
    cada ejecucion de los algoritmos).
    """
    ruta_entrada = Path(ruta_entrada)
    with open(ruta_entrada, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    for articulo in corpus:
        tokens = preprocess_text(articulo["abstract"], method=method)
        articulo["abstract_preprocesado"] = tokens
        articulo["abstract_preprocesado_texto"] = " ".join(tokens)

    if ruta_salida is not None:
        ruta_salida = Path(ruta_salida)
        ruta_salida.parent.mkdir(parents=True, exist_ok=True)
        with open(ruta_salida, "w", encoding="utf-8") as f:
            json.dump(corpus, f, ensure_ascii=False, indent=4)

    return corpus


# ---------------------------------------------------------------------------
# Ejecucion como script: genera el corpus preprocesado para los 20 abstracts.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    RUTA_CORPUS = Path(__file__).resolve().parent.parent / "data" / "corpus.json"
    RUTA_SALIDA = Path(__file__).resolve().parent.parent / "data" / "corpus_preprocesado.json"

    corpus_procesado = preprocess_corpus(RUTA_CORPUS, RUTA_SALIDA, method="lemma")

    print(f"Articulos preprocesados: {len(corpus_procesado)}")
    print(f"Archivo generado: {RUTA_SALIDA}")

    ejemplo = corpus_procesado[0]
    print("\n--- Ejemplo (articulo 1) ---")
    print("Abstract original (primeros 200 caracteres):")
    print(ejemplo["abstract"][:200], "...")
    print("\nTokens preprocesados (primeros 30):")
    print(ejemplo["abstract_preprocesado"][:30])
