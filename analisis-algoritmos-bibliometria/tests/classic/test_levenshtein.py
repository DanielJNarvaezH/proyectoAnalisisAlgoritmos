"""
Pruebas unitarias para src/classic/levenshtein.py
Ejecutar con:  python -m unittest tests/test_levenshtein.py -v
"""
import unittest
import sys
import os

# Permite ejecutar el archivo directamente sin instalar el proyecto como paquete
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from classic.levenshtein import (
    levenshtein_distance,
    levenshtein_similarity,
    build_levenshtein_matrix,
    similarity_matrix,
)


class TestLevenshteinDistance(unittest.TestCase):

    def test_secuencias_identicas(self):
        # Distancia entre una secuencia y sí misma siempre es 0
        self.assertEqual(levenshtein_distance("gato", "gato"), 0)
        self.assertEqual(levenshtein_distance(["a", "b", "c"], ["a", "b", "c"]), 0)

    def test_secuencia_vacia(self):
        # Transformar "" en una secuencia de largo m cuesta m inserciones
        self.assertEqual(levenshtein_distance("", "casa"), 4)
        self.assertEqual(levenshtein_distance("casa", ""), 4)
        self.assertEqual(levenshtein_distance("", ""), 0)

    def test_una_sustitucion(self):
        # "gato" -> "pato": una sola sustitución (g por p)
        self.assertEqual(levenshtein_distance("gato", "pato"), 1)

    def test_una_insercion(self):
        # "gato" -> "gatos": una sola inserción (s al final)
        self.assertEqual(levenshtein_distance("gato", "gatos"), 1)

    def test_una_eliminacion(self):
        # "gatos" -> "gato": una sola eliminación (s al final)
        self.assertEqual(levenshtein_distance("gatos", "gato"), 1)

    def test_caso_clasico_kitten_sitting(self):
        # Ejemplo clásico de la literatura: distancia = 3
        # kitten -> sitten (sustitución k->s)
        # sitten -> sittin (sustitución e->i)
        # sittin -> sitting (inserción g)
        self.assertEqual(levenshtein_distance("kitten", "sitting"), 3)

    def test_nivel_palabra_tokens(self):
        # El algoritmo debe funcionar igual con listas de tokens (palabras)
        a = ["el", "gato", "come", "pescado"]
        b = ["el", "perro", "come", "pescado", "fresco"]
        # sustituir "gato" por "perro" (1) + insertar "fresco" (1) = 2
        self.assertEqual(levenshtein_distance(a, b), 2)

    def test_simetria(self):
        # La distancia entre A y B debe ser igual a la distancia entre B y A
        a, b = "algoritmo", "logaritmo"
        self.assertEqual(levenshtein_distance(a, b), levenshtein_distance(b, a))

    def test_dimensiones_matriz(self):
        # La matriz debe tener tamaño (n+1) x (m+1)
        a, b = "abc", "de"
        matriz = build_levenshtein_matrix(a, b)
        self.assertEqual(len(matriz), len(a) + 1)
        self.assertEqual(len(matriz[0]), len(b) + 1)

    def test_primera_fila_y_columna(self):
        # D[i][0] = i  y  D[0][j] = j  (casos base)
        a, b = "abc", "de"
        matriz = build_levenshtein_matrix(a, b)
        for i in range(len(a) + 1):
            self.assertEqual(matriz[i][0], i)
        for j in range(len(b) + 1):
            self.assertEqual(matriz[0][j], j)


class TestLevenshteinSimilarity(unittest.TestCase):

    def test_similitud_identicas_es_uno(self):
        self.assertEqual(levenshtein_similarity("hola", "hola"), 1.0)

    def test_similitud_vacias_es_uno(self):
        self.assertEqual(levenshtein_similarity("", ""), 1.0)

    def test_similitud_en_rango_valido(self):
        # La similitud siempre debe estar entre 0 y 1
        sim = levenshtein_similarity("universidad", "universo")
        self.assertGreaterEqual(sim, 0.0)
        self.assertLessEqual(sim, 1.0)

    def test_similitud_calculo_manual(self):
        # "gato" vs "pato": distancia 1, max(len)=4 -> similitud = 1 - 1/4 = 0.75
        self.assertAlmostEqual(levenshtein_similarity("gato", "pato"), 0.75)


class TestSimilarityMatrix(unittest.TestCase):

    def test_diagonal_es_uno(self):
        corpus = [["a", "b"], ["c", "d"], ["a", "b", "c"]]
        matriz = similarity_matrix(corpus)
        for i in range(len(corpus)):
            self.assertEqual(matriz[i][i], 1.0)

    def test_matriz_simetrica(self):
        corpus = [["a", "b"], ["c", "d"], ["a", "b", "c"]]
        matriz = similarity_matrix(corpus)
        n = len(corpus)
        for i in range(n):
            for j in range(n):
                self.assertAlmostEqual(matriz[i][j], matriz[j][i])

    def test_tamano_matriz(self):
        corpus = [["a"], ["b"], ["c"], ["d"]]
        matriz = similarity_matrix(corpus)
        self.assertEqual(len(matriz), 4)
        self.assertEqual(len(matriz[0]), 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
