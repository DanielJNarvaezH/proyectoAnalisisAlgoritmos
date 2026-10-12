"""
Pruebas unitarias para src/clustering/average_linkage.py

Ejecutar desde la raiz del proyecto:

    .\\venv\\Scripts\\python.exe -m unittest tests/clustering/test_average_linkage.py -v
"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from clustering.average_linkage import (
    actualizar_enlace_promedio,
    average_linkage,
    distancia_enlace_promedio,
)
from clustering.complete_linkage import distancia_enlace_completo
from clustering.single_linkage import distancia_enlace_simple

# Mismo ejemplo de 5 elementos que en los otros criterios (A=0 ... E=4),
# resuelto a mano con enlace promedio:
#   1. A+B a 2                          -> grupo 5 = {A, B}
#   2. Candidatos: {A,B}-C = (6+5)/2 = 5.5; D-E = 3 (el menor)
#      -> D+E a 3                       -> grupo 6 = {D, E}
#   3. Candidatos: C-{D,E} = (4+5)/2 = 4.5; {A,B}-C = 5.5;
#                  {A,B}-{D,E} = (10+9+9+8)/4 = 9
#      -> C+{D,E} a 4.5                 -> grupo 7 = {C, D, E}
#   4. {A,B}-{C,D,E} = (6+10+9+5+9+8)/6 = 47/6 = 7.8333
#      Con la regla: (1 * 5.5 + 2 * 9) / 3 = 23.5 / 3 = 7.8333 (coincide)
EJEMPLO = [
    [0, 2, 6, 10, 9],
    [2, 0, 5, 9, 8],
    [6, 5, 0, 4, 5],
    [10, 9, 4, 0, 3],
    [9, 8, 5, 3, 0],
]


def _matriz_aleatoria(generador, n):
    m = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            m[i][j] = m[j][i] = generador.random()
    return m


class TestCriterio(unittest.TestCase):
    def test_definicion_es_el_promedio_entre_pares(self):
        self.assertAlmostEqual(distancia_enlace_promedio([0, 1], [2, 3, 4], EJEMPLO), 47 / 6)

    def test_grupo_vacio_lanza_error(self):
        with self.assertRaises(ValueError):
            distancia_enlace_promedio([], [1], EJEMPLO)

    def test_regla_con_grupos_del_mismo_tamano_es_el_promedio_simple(self):
        self.assertEqual(actualizar_enlace_promedio(4, 6), 5)

    def test_regla_pondera_por_tamano(self):
        # Grupo A de 3 elementos a distancia 1, grupo B de 1 elemento a distancia 5
        # (3 * 1 + 1 * 5) / 4 = 2
        self.assertEqual(actualizar_enlace_promedio(1, 5, 3, 1), 2)

    def test_promedio_entre_minimo_y_maximo(self):
        generador = random.Random(19)
        for _ in range(50):
            n = generador.randint(4, 10)
            m = _matriz_aleatoria(generador, n)
            elementos = list(range(n))
            generador.shuffle(elementos)
            corte = generador.randint(1, n - 1)
            a, b = elementos[:corte], elementos[corte:]
            self.assertLessEqual(distancia_enlace_simple(a, b, m),
                                 distancia_enlace_promedio(a, b, m))
            self.assertLessEqual(distancia_enlace_promedio(a, b, m),
                                 distancia_enlace_completo(a, b, m))


class TestEjemploResueltoAMano(unittest.TestCase):
    def setUp(self):
        self.historial = average_linkage(EJEMPLO)

    def test_orden_de_las_fusiones(self):
        resumen = [(f["grupo_a"], f["grupo_b"]) for f in self.historial]
        self.assertEqual(resumen, [(0, 1), (3, 4), (2, 6), (5, 7)])

    def test_distancias_de_las_fusiones(self):
        distancias = [f["distancia"] for f in self.historial]
        for obtenido, esperado in zip(distancias, [2, 3, 4.5, 47 / 6]):
            self.assertAlmostEqual(obtenido, esperado)

    def test_miembros_y_tamanos(self):
        self.assertEqual(self.historial[2]["miembros"], [2, 3, 4])
        self.assertEqual([f["tamano"] for f in self.historial], [2, 2, 3, 5])


class TestPropiedades(unittest.TestCase):
    def test_regla_coincide_con_definicion(self):
        """En cada fusion, la distancia usada debe ser la de la definicion."""
        generador = random.Random(23)
        for _ in range(30):
            n = generador.randint(3, 12)
            m = _matriz_aleatoria(generador, n)
            historial = average_linkage(m)
            miembros = {i: [i] for i in range(n)}
            for f in historial:
                esperado = distancia_enlace_promedio(
                    miembros[f["grupo_a"]], miembros[f["grupo_b"]], m)
                self.assertAlmostEqual(f["distancia"], esperado)
                miembros[f["nuevo_grupo"]] = f["miembros"]

    def test_distancias_no_decrecen(self):
        generador = random.Random(29)
        for _ in range(30):
            m = _matriz_aleatoria(generador, generador.randint(3, 12))
            distancias = [f["distancia"] for f in average_linkage(m)]
            for anterior, siguiente in zip(distancias, distancias[1:]):
                self.assertLessEqual(anterior, siguiente + 1e-12)

    def test_no_modifica_la_matriz(self):
        copia = [fila[:] for fila in EJEMPLO]
        average_linkage(EJEMPLO)
        self.assertEqual(EJEMPLO, copia)

    def test_matriz_invalida(self):
        with self.assertRaises(ValueError):
            average_linkage([[0, 1], [2, 0]])


if __name__ == "__main__":
    unittest.main()
