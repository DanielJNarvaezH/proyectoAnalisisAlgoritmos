"""
Pruebas unitarias para src/ia/metricas.py

Ejecutar desde la raiz del proyecto:

    .\\venv\\Scripts\\python.exe -m unittest tests/ia/test_metricas.py -v
"""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ia.metricas import (
    distancia_euclidiana,
    matrices_embeddings,
    matriz,
    norma,
    producto_punto,
    similitud_coseno,
    similitud_euclidiana,
)


class TestOperacionesBasicas(unittest.TestCase):
    def test_producto_punto_calculado_a_mano(self):
        # 1*4 + 2*5 + 3*6 = 32
        self.assertEqual(producto_punto([1, 2, 3], [4, 5, 6]), 32.0)

    def test_norma_triangulo_3_4_5(self):
        self.assertEqual(norma([3, 4]), 5.0)

    def test_norma_vector_cero(self):
        self.assertEqual(norma([0, 0, 0]), 0.0)

    def test_dimensiones_distintas_lanzan_error(self):
        with self.assertRaises(ValueError):
            producto_punto([1, 2], [1, 2, 3])
        with self.assertRaises(ValueError):
            similitud_coseno([1, 2], [1, 2, 3])
        with self.assertRaises(ValueError):
            distancia_euclidiana([1, 2], [1, 2, 3])


class TestSimilitudCoseno(unittest.TestCase):
    def test_vectores_identicos(self):
        self.assertAlmostEqual(similitud_coseno([1, 2, 3], [1, 2, 3]), 1.0)

    def test_misma_direccion_distinta_magnitud(self):
        # El coseno solo mide el angulo, no el tamano
        self.assertAlmostEqual(similitud_coseno([1, 2, 3], [2, 4, 6]), 1.0)

    def test_ortogonales(self):
        self.assertAlmostEqual(similitud_coseno([1, 0], [0, 1]), 0.0)

    def test_opuestos(self):
        self.assertAlmostEqual(similitud_coseno([1, 2], [-1, -2]), -1.0)

    def test_angulo_de_45_grados(self):
        self.assertAlmostEqual(similitud_coseno([1, 0], [1, 1]), 1 / math.sqrt(2))

    def test_vector_cero_retorna_cero(self):
        self.assertEqual(similitud_coseno([0, 0], [1, 2]), 0.0)


class TestEuclidiana(unittest.TestCase):
    def test_distancia_calculada_a_mano(self):
        # sqrt((4-1)^2 + (6-2)^2) = sqrt(9 + 16) = 5
        self.assertEqual(distancia_euclidiana([1, 2], [4, 6]), 5.0)

    def test_distancia_a_si_mismo_es_cero(self):
        self.assertEqual(distancia_euclidiana([1.5, -2.0, 3.0], [1.5, -2.0, 3.0]), 0.0)

    def test_distancia_simetrica(self):
        a, b = [1.0, 7.0, -3.0], [2.0, 0.5, 4.0]
        self.assertEqual(distancia_euclidiana(a, b), distancia_euclidiana(b, a))

    def test_similitud_euclidiana(self):
        # d = 5 -> 1 / (1 + 5)
        self.assertAlmostEqual(similitud_euclidiana([1, 2], [4, 6]), 1 / 6)

    def test_similitud_euclidiana_identicos_es_uno(self):
        self.assertEqual(similitud_euclidiana([3, 4], [3, 4]), 1.0)

    def test_vectores_unitarios_relacion_con_coseno(self):
        # Con vectores de norma 1: d^2 = 2 - 2*cos
        a = [1.0, 0.0]
        b = [math.cos(1.0), math.sin(1.0)]
        d = distancia_euclidiana(a, b)
        self.assertAlmostEqual(d * d, 2 - 2 * similitud_coseno(a, b))


class TestMatrices(unittest.TestCase):
    VECTORES = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]

    def test_tamano_y_simetria(self):
        m = matriz(self.VECTORES, similitud_coseno)
        self.assertEqual(len(m), 3)
        for i in range(3):
            self.assertEqual(len(m[i]), 3)
            for j in range(3):
                self.assertEqual(m[i][j], m[j][i])

    def test_diagonales(self):
        resultado = matrices_embeddings(self.VECTORES)
        for i in range(3):
            self.assertAlmostEqual(resultado["coseno"][i][i], 1.0)
            self.assertEqual(resultado["distancia_euclidiana"][i][i], 0.0)
            self.assertEqual(resultado["similitud_euclidiana"][i][i], 1.0)

    def test_valores_fuera_de_la_diagonal(self):
        resultado = matrices_embeddings(self.VECTORES)
        self.assertAlmostEqual(resultado["coseno"][0][1], 0.0)
        self.assertAlmostEqual(resultado["distancia_euclidiana"][0][1], math.sqrt(2))
        self.assertAlmostEqual(resultado["coseno"][0][2], 1 / math.sqrt(2))


if __name__ == "__main__":
    unittest.main()
