"""
Pruebas unitarias para src/clustering/evaluacion.py

Ejecutar desde la raiz del proyecto:

    .\\venv\\Scripts\\python.exe -m unittest tests/clustering/test_evaluacion.py -v
"""

import math
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from clustering.complete_linkage import complete_linkage
from clustering.dendrograma import altura_de_union, construir_matriz_enlace
from clustering.evaluacion import (
    correlacion_cofenetica,
    correlacion_pearson,
    evaluar,
    indice_silueta,
    matriz_cofenetica,
    silueta_por_elemento,
)
from clustering.single_linkage import single_linkage

# Mismo ejemplo de 5 elementos (A=0 ... E=4) de las pruebas de los criterios
EJEMPLO = [
    [0, 2, 6, 10, 9],
    [2, 0, 5, 9, 8],
    [6, 5, 0, 4, 5],
    [10, 9, 4, 0, 3],
    [9, 8, 5, 3, 0],
]

# Cuatro puntos en una recta: 0, 1, 10, 11
RECTA = [[abs(p - q) for q in (0, 1, 10, 11)] for p in (0, 1, 10, 11)]


def _matriz_aleatoria(generador, n):
    m = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            m[i][j] = m[j][i] = generador.random()
    return m


class TestMatrizCofenetica(unittest.TestCase):
    def test_ejemplo_resuelto_a_mano(self):
        # Single linkage: A-B a 2, D-E a 3, C se une a {D,E} a 4, todo a 5
        c = matriz_cofenetica(construir_matriz_enlace(single_linkage(EJEMPLO)), 5)
        self.assertEqual(c[0][1], 2)
        self.assertEqual(c[3][4], 3)
        self.assertEqual(c[2][3], 4)
        self.assertEqual(c[2][4], 4)
        self.assertEqual(c[0][4], 5)
        self.assertEqual(c[1][2], 5)

    def test_simetrica_con_diagonal_cero(self):
        c = matriz_cofenetica(construir_matriz_enlace(complete_linkage(EJEMPLO)), 5)
        for i in range(5):
            self.assertEqual(c[i][i], 0)
            for j in range(5):
                self.assertEqual(c[i][j], c[j][i])

    def test_coincide_con_altura_de_union(self):
        generador = random.Random(43)
        for _ in range(10):
            n = generador.randint(3, 10)
            z = construir_matriz_enlace(complete_linkage(_matriz_aleatoria(generador, n)))
            c = matriz_cofenetica(z, n)
            for i in range(n):
                for j in range(i + 1, n):
                    self.assertEqual(c[i][j], altura_de_union(z, n, i, j))


class TestCorrelacion(unittest.TestCase):
    def test_pearson_perfecta_positiva(self):
        self.assertAlmostEqual(correlacion_pearson([1, 2, 3], [2, 4, 6]), 1.0)

    def test_pearson_perfecta_negativa(self):
        self.assertAlmostEqual(correlacion_pearson([1, 2, 3], [3, 2, 1]), -1.0)

    def test_pearson_valor_conocido(self):
        # x = [1, 2, 3], y = [1, 3, 2]: cov = 1, var_x = var_y = 2 -> 0.5
        self.assertAlmostEqual(correlacion_pearson([1, 2, 3], [1, 3, 2]), 0.5)

    def test_pearson_variable_constante(self):
        with self.assertRaises(ValueError):
            correlacion_pearson([1, 1, 1], [1, 2, 3])

    def test_cpcc_es_uno_si_las_distancias_ya_son_las_del_arbol(self):
        # Una matriz cofenetica es ultrametrica: el single linkage la reproduce
        # exactamente, asi que su CPCC con ella misma es 1
        cofenetica = matriz_cofenetica(construir_matriz_enlace(single_linkage(EJEMPLO)), 5)
        z = construir_matriz_enlace(single_linkage(cofenetica))
        self.assertAlmostEqual(correlacion_cofenetica(cofenetica, z), 1.0)

    def test_cpcc_entre_menos_uno_y_uno(self):
        generador = random.Random(47)
        for _ in range(10):
            m = _matriz_aleatoria(generador, generador.randint(4, 10))
            cpcc = correlacion_cofenetica(m, construir_matriz_enlace(single_linkage(m)))
            self.assertTrue(-1.0 <= cpcc <= 1.0)


class TestSilueta(unittest.TestCase):
    def test_ejemplo_resuelto_a_mano(self):
        # Grupos {0, 1} y {10, 11}:
        #   punto 0:  a = 1, b = (10 + 11) / 2 = 10.5 -> s = 9.5 / 10.5 = 19/21
        #   punto 1:  a = 1, b = (9 + 10) / 2  = 9.5  -> s = 8.5 / 9.5  = 17/19
        #   los puntos 10 y 11 son simetricos a 1 y 0
        s = silueta_por_elemento(RECTA, [[0, 1], [2, 3]])
        self.assertAlmostEqual(s[0], 19 / 21)
        self.assertAlmostEqual(s[1], 17 / 19)
        self.assertAlmostEqual(s[2], 17 / 19)
        self.assertAlmostEqual(s[3], 19 / 21)
        self.assertAlmostEqual(indice_silueta(RECTA, [[0, 1], [2, 3]]), (19 / 21 + 17 / 19) / 2)

    def test_mala_particion_tiene_silueta_negativa(self):
        # Mezclar puntos lejanos en el mismo grupo empeora la silueta
        self.assertLess(indice_silueta(RECTA, [[0, 2], [1, 3]]), 0)

    def test_elemento_solo_tiene_silueta_cero(self):
        s = silueta_por_elemento(RECTA, [[0], [1, 2, 3]])
        self.assertEqual(s[0], 0.0)

    def test_k_fuera_de_rango(self):
        with self.assertRaises(ValueError):
            indice_silueta(RECTA, [[0, 1, 2, 3]])
        with self.assertRaises(ValueError):
            indice_silueta(RECTA, [[0], [1], [2], [3]])

    def test_particion_incompleta(self):
        with self.assertRaises(ValueError):
            silueta_por_elemento(RECTA, [[0, 1], [2]])

    def test_entre_menos_uno_y_uno(self):
        generador = random.Random(53)
        for _ in range(10):
            n = generador.randint(4, 10)
            m = _matriz_aleatoria(generador, n)
            elementos = list(range(n))
            generador.shuffle(elementos)
            corte = generador.randint(1, n - 1)
            valor = indice_silueta(m, [elementos[:corte], elementos[corte:]])
            self.assertTrue(-1.0 <= valor <= 1.0)


class TestEvaluar(unittest.TestCase):
    def test_estructura_del_resultado(self):
        resultado = evaluar(EJEMPLO, k_minimo=2, k_maximo=3)
        self.assertEqual(set(resultado), {"single", "complete", "average"})
        for datos in resultado.values():
            self.assertEqual(set(datos["silueta"]), {2, 3})
            self.assertTrue(-1.0 <= datos["cpcc"] <= 1.0)

    def test_k_maximo_se_limita_a_n_menos_uno(self):
        resultado = evaluar(EJEMPLO, k_minimo=2, k_maximo=10)
        self.assertEqual(max(resultado["single"]["silueta"]), 4)


if __name__ == "__main__":
    unittest.main()
