"""
Pruebas unitarias para tfidf_manual.py

Ejecutar desde la raíz del proyecto (la carpeta que contiene tanto
tfidf_manual.py como tests/):

    python -m unittest discover -s tests -v
"""

import unittest
import math
import sys
import os

# Permite importar tfidf_manual.py: este archivo está en tests/classic/,
# y el módulo real vive en src/, dos niveles arriba.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from tfidf_cosine import (
    tokenizar,
    calcular_tf,
    calcular_idf,
    construir_vocabulario,
    vectorizar_tfidf,
    similitud_coseno,
    matriz_similitud,
)


class TestTokenizar(unittest.TestCase):

    def test_tokenizar_string(self):
        resultado = tokenizar("El Perro corre, rápido!")
        self.assertEqual(resultado, ["el", "perro", "corre", "rápido"])

    def test_tokenizar_lista_ya_tokenizada(self):
        resultado = tokenizar(["Perro", "GATO"])
        self.assertEqual(resultado, ["perro", "gato"])

    def test_tokenizar_string_vacio(self):
        self.assertEqual(tokenizar(""), [])


class TestCalcularTF(unittest.TestCase):

    def test_tf_suma_uno(self):
        tokens = ["a", "b", "a", "c"]
        tf = calcular_tf(tokens)
        self.assertAlmostEqual(sum(tf.values()), 1.0, places=6)

    def test_tf_valores_esperados(self):
        tokens = ["a", "a", "b"]
        tf = calcular_tf(tokens)
        self.assertAlmostEqual(tf["a"], 2 / 3, places=6)
        self.assertAlmostEqual(tf["b"], 1 / 3, places=6)


class TestCalcularIDF(unittest.TestCase):

    def test_termino_en_todos_los_documentos_tiene_idf_bajo(self):
        docs = [["a", "b"], ["a", "c"], ["a", "d"]]
        idf = calcular_idf(docs)
        # "a" aparece en los 3 documentos -> IDF más bajo que términos raros
        self.assertLess(idf["a"], idf["b"])

    def test_idf_formula_manual(self):
        docs = [["a"], ["b"]]
        idf = calcular_idf(docs)
        # N=2, df("a")=1 -> log(2/(1+1)) + 1 = log(1) + 1 = 1.0
        self.assertAlmostEqual(idf["a"], 1.0, places=6)


class TestVocabulario(unittest.TestCase):

    def test_vocabulario_ordenado_sin_duplicados(self):
        docs = [["b", "a"], ["a", "c"]]
        vocab = construir_vocabulario(docs)
        self.assertEqual(vocab, ["a", "b", "c"])


class TestVectorizarTFIDF(unittest.TestCase):

    def test_dimension_vectores_igual_vocabulario(self):
        corpus = ["perro gato", "gato pajaro"]
        vocab, matriz = vectorizar_tfidf(corpus)
        for vector in matriz:
            self.assertEqual(len(vector), len(vocab))

    def test_numero_de_filas_igual_numero_documentos(self):
        corpus = ["a b", "c d", "e f"]
        _, matriz = vectorizar_tfidf(corpus)
        self.assertEqual(len(matriz), 3)

    def test_acepta_tokens_ya_preprocesados(self):
        # abstract_preprocesado como lista de tokens, no como string
        corpus = [["algoritmo", "clasificacion"], ["algoritmo", "regresion"]]
        vocab, matriz = vectorizar_tfidf(corpus)
        self.assertIn("algoritmo", vocab)
        self.assertEqual(len(matriz), 2)


class TestSimilitudCoseno(unittest.TestCase):

    def test_vectores_identicos_similitud_uno(self):
        v = [1.0, 2.0, 3.0]
        self.assertAlmostEqual(similitud_coseno(v, v), 1.0, places=6)

    def test_vectores_ortogonales_similitud_cero(self):
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        self.assertAlmostEqual(similitud_coseno(a, b), 0.0, places=6)

    def test_vector_nulo_retorna_cero(self):
        a = [0.0, 0.0]
        b = [1.0, 2.0]
        self.assertEqual(similitud_coseno(a, b), 0.0)

    def test_dimensiones_distintas_lanza_error(self):
        with self.assertRaises(ValueError):
            similitud_coseno([1, 2], [1, 2, 3])

    def test_valor_conocido(self):
        # Cálculo manual: a=[1,0], b=[1,1] -> coseno = 1/sqrt(2)
        a = [1.0, 0.0]
        b = [1.0, 1.0]
        self.assertAlmostEqual(similitud_coseno(a, b), 1 / math.sqrt(2), places=6)


class TestMatrizSimilitud(unittest.TestCase):

    def test_diagonal_es_uno(self):
        corpus = ["perro gato", "gato pajaro", "perro pajaro"]
        _, matriz_tfidf = vectorizar_tfidf(corpus)
        matriz_sim = matriz_similitud(matriz_tfidf)
        for i in range(len(matriz_sim)):
            self.assertAlmostEqual(matriz_sim[i][i], 1.0, places=6)

    def test_matriz_es_simetrica(self):
        corpus = ["perro gato", "gato pajaro", "perro pajaro"]
        _, matriz_tfidf = vectorizar_tfidf(corpus)
        matriz_sim = matriz_similitud(matriz_tfidf)
        n = len(matriz_sim)
        for i in range(n):
            for j in range(n):
                self.assertAlmostEqual(matriz_sim[i][j], matriz_sim[j][i], places=6)


if __name__ == "__main__":
    unittest.main()