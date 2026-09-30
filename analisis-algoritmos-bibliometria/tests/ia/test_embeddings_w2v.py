"""
Pruebas unitarias para src/ia/embeddings_w2v.py

Usan un vocabulario falso (diccionario) en lugar del modelo de Google News,
asi que no requieren gensim ni descargar el modelo.

Ejecutar desde la raiz del proyecto:

    .\\venv\\Scripts\\python.exe -m unittest tests/ia/test_embeddings_w2v.py -v
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ia.embeddings_w2v import (
    buscar_vector,
    cargar_embeddings,
    generar_embeddings_corpus,
    guardar_embeddings,
    promediar_vectores,
    variantes_de_busqueda,
    vector_documento,
    vector_expansion,
)

# Vocabulario falso de dimension 3, con mayusculas como en Google News
VOCAB = {
    "education": [1.0, 0.0, 0.0],
    "learning": [0.0, 1.0, 0.0],
    "student": [0.0, 0.0, 1.0],
    "AI": [2.0, 2.0, 2.0],
    "Python": [3.0, 0.0, 3.0],
    "ai": [9.0, 9.0, 9.0],  # sentido equivocado, como en Google News
    "artificial_intelligence": [0.0, 0.0, 4.0],
    "generative": [2.0, 0.0, 0.0],
}

EXPANSIONES_PRUEBA = {
    "ai": ["artificial_intelligence"],
    "aied": ["artificial_intelligence", "education"],
    "gai": ["generative", "artificial_intelligence"],
    "xyz": ["palabra_inexistente"],
}


class TestVariantesDeBusqueda(unittest.TestCase):
    def test_orden_minuscula_capitalizada_mayuscula(self):
        self.assertEqual(variantes_de_busqueda("ai"), ["ai", "Ai", "AI"])

    def test_sin_duplicados(self):
        self.assertEqual(variantes_de_busqueda("a"), ["a", "A"])


class TestBuscarVector(unittest.TestCase):
    def test_encuentra_forma_exacta(self):
        vector, variante = buscar_vector("education", VOCAB)
        self.assertEqual(vector, [1.0, 0.0, 0.0])
        self.assertEqual(variante, "education")

    def test_encuentra_sigla_en_mayusculas(self):
        vector, variante = buscar_vector("nlp", {"NLP": [2.0, 2.0, 2.0]})
        self.assertEqual(vector, [2.0, 2.0, 2.0])
        self.assertEqual(variante, "NLP")

    def test_encuentra_forma_capitalizada(self):
        _, variante = buscar_vector("python", VOCAB)
        self.assertEqual(variante, "Python")

    def test_token_inexistente(self):
        self.assertEqual(buscar_vector("aied", VOCAB), (None, None))

    def test_retorna_lista_de_floats(self):
        vector, _ = buscar_vector("student", VOCAB)
        self.assertIsInstance(vector, list)
        self.assertTrue(all(isinstance(x, float) for x in vector))


class TestPromediarVectores(unittest.TestCase):
    def test_promedio_calculado_a_mano(self):
        vectores = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [2.0, 2.0, 2.0]]
        # (1+0+2)/3 = 1, (0+1+2)/3 = 1, (0+0+2)/3 = 0.666...
        resultado = promediar_vectores(vectores, 3)
        self.assertAlmostEqual(resultado[0], 1.0)
        self.assertAlmostEqual(resultado[1], 1.0)
        self.assertAlmostEqual(resultado[2], 2 / 3)

    def test_un_solo_vector_se_conserva(self):
        self.assertEqual(promediar_vectores([[4.0, 5.0, 6.0]], 3), [4.0, 5.0, 6.0])

    def test_lista_vacia_retorna_vector_cero(self):
        self.assertEqual(promediar_vectores([], 3), [0.0, 0.0, 0.0])

    def test_dimension_incorrecta_lanza_error(self):
        with self.assertRaises(ValueError):
            promediar_vectores([[1.0, 2.0]], 3)

    def test_no_modifica_los_vectores_de_entrada(self):
        vectores = [[1.0, 2.0, 3.0]]
        promediar_vectores(vectores, 3)
        self.assertEqual(vectores, [[1.0, 2.0, 3.0]])


class TestVectorDocumento(unittest.TestCase):
    def test_excluye_oov_del_promedio(self):
        resultado = vector_documento(["education", "aied", "learning"], VOCAB, 3)
        self.assertEqual(resultado["vector"], [0.5, 0.5, 0.0])
        self.assertEqual(resultado["oov"], ["aied"])

    def test_conteos_y_cobertura(self):
        resultado = vector_documento(["education", "aied", "aied", "python"], VOCAB, 3)
        self.assertEqual(resultado["tokens_totales"], 4)
        self.assertEqual(resultado["tokens_encontrados"], 2)
        self.assertAlmostEqual(resultado["cobertura"], 0.5)

    def test_tokens_repetidos_pesan_mas(self):
        # "education" dos veces: (1+1+0)/3, (0+0+1)/3
        resultado = vector_documento(["education", "education", "learning"], VOCAB, 3)
        self.assertAlmostEqual(resultado["vector"][0], 2 / 3)
        self.assertAlmostEqual(resultado["vector"][1], 1 / 3)

    def test_registra_variantes_usadas(self):
        resultado = vector_documento(["python", "education"], VOCAB, 3)
        self.assertEqual(resultado["variantes"], {"python": "Python"})

    def test_documento_sin_tokens_conocidos(self):
        resultado = vector_documento(["aied", "genai"], VOCAB, 3)
        self.assertEqual(resultado["vector"], [0.0, 0.0, 0.0])
        self.assertEqual(resultado["cobertura"], 0.0)
        self.assertEqual(resultado["oov"], ["aied", "genai"])

    def test_documento_vacio(self):
        resultado = vector_documento([], VOCAB, 3)
        self.assertEqual(resultado["tokens_totales"], 0)
        self.assertEqual(resultado["cobertura"], 0.0)


class TestExpansiones(unittest.TestCase):
    def test_expansion_de_una_palabra(self):
        vector, usadas = vector_expansion("ai", VOCAB, EXPANSIONES_PRUEBA, 3)
        self.assertEqual(vector, [0.0, 0.0, 4.0])
        self.assertEqual(usadas, ["artificial_intelligence"])

    def test_expansion_de_dos_palabras_es_su_promedio(self):
        # (artificial_intelligence + education) / 2 = ([0,0,4] + [1,0,0]) / 2
        vector, _ = vector_expansion("aied", VOCAB, EXPANSIONES_PRUEBA, 3)
        self.assertEqual(vector, [0.5, 0.0, 2.0])

    def test_token_sin_expansion(self):
        self.assertEqual(
            vector_expansion("education", VOCAB, EXPANSIONES_PRUEBA, 3), (None, None)
        )

    def test_expansion_sin_palabras_en_el_modelo(self):
        self.assertEqual(
            vector_expansion("xyz", VOCAB, EXPANSIONES_PRUEBA, 3), (None, None)
        )

    def test_expansion_tiene_prioridad_sobre_la_forma_directa(self):
        # "ai" existe en VOCAB con sentido equivocado; con expansiones se ignora
        resultado = vector_documento(["ai"], VOCAB, 3, EXPANSIONES_PRUEBA)
        self.assertEqual(resultado["vector"], [0.0, 0.0, 4.0])
        self.assertEqual(resultado["expansiones"], {"ai": ["artificial_intelligence"]})

    def test_sin_expansiones_usa_la_forma_directa(self):
        resultado = vector_documento(["ai"], VOCAB, 3)
        self.assertEqual(resultado["vector"], [9.0, 9.0, 9.0])
        self.assertEqual(resultado["expansiones"], {})

    def test_token_expandido_cuenta_como_un_solo_token(self):
        # aied (1 token, vector [0.5,0,2]) + education ([1,0,0]) -> promedio de 2
        resultado = vector_documento(["aied", "education"], VOCAB, 3, EXPANSIONES_PRUEBA)
        self.assertEqual(resultado["tokens_encontrados"], 2)
        self.assertEqual(resultado["vector"], [0.75, 0.0, 1.0])


class TestCorpusYArchivo(unittest.TestCase):
    CORPUS = [
        {"numero": 1, "titulo": "A", "abstract_preprocesado": ["education", "student"]},
        {"numero": 2, "titulo": "B", "abstract_preprocesado": ["learning", "aied"]},
    ]

    def test_un_resultado_por_articulo_con_su_numero(self):
        articulos = generar_embeddings_corpus(self.CORPUS, VOCAB, 3)
        self.assertEqual([a["numero"] for a in articulos], [1, 2])
        self.assertEqual(articulos[1]["vector"], [0.0, 1.0, 0.0])

    def test_guardar_y_cargar_ida_y_vuelta(self):
        articulos = generar_embeddings_corpus(self.CORPUS, VOCAB, 3)
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "sub", "prueba.json")
            guardar_embeddings(ruta, "falso", 3, "abstract_preprocesado",
                               articulos, extra={"limite_vocabulario": None})
            with open(ruta, encoding="utf-8") as archivo:
                datos = json.load(archivo)
            self.assertEqual(datos["modelo"], "falso")
            self.assertEqual(datos["dimension"], 3)
            self.assertIn("limite_vocabulario", datos)

            vectores = cargar_embeddings(ruta)
            self.assertEqual(set(vectores), {1, 2})
            self.assertEqual(vectores[1], [0.5, 0.0, 0.5])


if __name__ == "__main__":
    unittest.main()
