"""
Pruebas unitarias para src/ia/embeddings_llm.py

Usan un modelo y un tokenizador falsos, asi que no requieren
sentence-transformers, PyTorch ni descargar el modelo.

Ejecutar desde la raiz del proyecto:

    .\\venv\\Scripts\\python.exe -m unittest tests/ia/test_embeddings_llm.py -v
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ia.embeddings_llm import (
    analizar_truncamiento,
    contar_subpalabras,
    generar_embeddings_corpus,
)
from ia.embeddings_w2v import cargar_embeddings, guardar_embeddings


class TokenizadorFalso:
    """Una sub-palabra por palabra, mas los tokens especiales de inicio y fin."""

    def __call__(self, texto, add_special_tokens=True):
        ids = list(range(len(texto.split())))
        if add_special_tokens:
            ids = [-1] + ids + [-2]
        return {"input_ids": ids}


class ModeloFalso:
    """Imita la interfaz de SentenceTransformer que usa el modulo."""

    def __init__(self, max_seq_length=6):
        self.tokenizer = TokenizadorFalso()
        self.max_seq_length = max_seq_length
        self.llamadas_encode = 0

    def encode(self, textos, show_progress_bar=False):
        self.llamadas_encode += 1
        # Vector de 3 dimensiones: [palabras, caracteres, 1.0]
        return [[float(len(t.split())), float(len(t)), 1.0] for t in textos]


CORPUS = [
    {"numero": 1, "titulo": "A", "abstract": "AI in education",
     "abstract_preprocesado": ["ai", "education"]},
    {"numero": 2, "titulo": "B", "abstract": "one two three four five six seven",
     "abstract_preprocesado": ["one", "two"]},
]


class TestContarSubpalabras(unittest.TestCase):
    def test_incluye_tokens_especiales(self):
        # 3 palabras + inicio + fin
        self.assertEqual(contar_subpalabras("AI in education", TokenizadorFalso()), 5)

    def test_texto_vacio_solo_tokens_especiales(self):
        self.assertEqual(contar_subpalabras("", TokenizadorFalso()), 2)


class TestAnalizarTruncamiento(unittest.TestCase):
    def test_resumen_y_truncados(self):
        resumen = analizar_truncamiento({1: 100, 2: 400, 3: 384}, 384)
        self.assertEqual(resumen["minimo"], 100)
        self.assertEqual(resumen["maximo"], 400)
        self.assertAlmostEqual(resumen["promedio"], 884 / 3)
        self.assertEqual(resumen["truncados"], [2])

    def test_exactamente_en_el_limite_no_se_trunca(self):
        self.assertEqual(analizar_truncamiento({1: 384}, 384)["truncados"], [])

    def test_sin_articulos(self):
        self.assertEqual(analizar_truncamiento({}, 384)["truncados"], [])


class TestGenerarEmbeddingsCorpus(unittest.TestCase):
    def test_usa_el_abstract_original_no_el_preprocesado(self):
        articulos = generar_embeddings_corpus(CORPUS, ModeloFalso())
        # "AI in education" tiene 3 palabras y 15 caracteres
        self.assertEqual(articulos[0]["vector"], [3.0, 15.0, 1.0])

    def test_un_resultado_por_articulo_con_su_numero(self):
        articulos = generar_embeddings_corpus(CORPUS, ModeloFalso())
        self.assertEqual([a["numero"] for a in articulos], [1, 2])
        self.assertEqual([a["titulo"] for a in articulos], ["A", "B"])

    def test_codifica_todo_en_una_sola_llamada(self):
        modelo = ModeloFalso()
        generar_embeddings_corpus(CORPUS, modelo)
        self.assertEqual(modelo.llamadas_encode, 1)

    def test_vector_es_lista_de_floats(self):
        vector = generar_embeddings_corpus(CORPUS, ModeloFalso())[0]["vector"]
        self.assertIsInstance(vector, list)
        self.assertTrue(all(isinstance(x, float) for x in vector))

    def test_marca_truncamiento(self):
        # max 6: art. 1 ocupa 5 (completo), art. 2 ocupa 9 (truncado)
        articulos = generar_embeddings_corpus(CORPUS, ModeloFalso(max_seq_length=6))
        self.assertEqual(articulos[0]["subpalabras"], 5)
        self.assertFalse(articulos[0]["truncado"])
        self.assertEqual(articulos[1]["subpalabras"], 9)
        self.assertTrue(articulos[1]["truncado"])

    def test_archivo_compatible_con_cargar_embeddings(self):
        articulos = generar_embeddings_corpus(CORPUS, ModeloFalso())
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "mpnet.json")
            guardar_embeddings(ruta, "falso", 3, "abstract", articulos,
                               extra={"max_seq_length": 6})
            with open(ruta, encoding="utf-8") as archivo:
                datos = json.load(archivo)
            self.assertEqual(datos["entrada"], "abstract")
            vectores = cargar_embeddings(ruta)
            self.assertEqual(vectores[1], [3.0, 15.0, 1.0])


if __name__ == "__main__":
    unittest.main()
