"""
Pruebas unitarias para src/clustering/single_linkage.py

Ejecutar desde la raiz del proyecto:

    .\\venv\\Scripts\\python.exe -m unittest tests/clustering/test_single_linkage.py -v
"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from clustering.single_linkage import (
    actualizar_enlace_simple,
    cortar_en_k_grupos,
    distancia_enlace_simple,
    single_linkage,
    validar_matriz_distancias,
)

# Ejemplo clasico de 5 elementos (A=0, B=1, C=2, D=3, E=4), resuelto a mano:
#   1. A+B a 2          -> grupo 5 = {A, B}
#   2. D+E a 3          -> grupo 6 = {D, E}
#   3. C+{D,E} a min(4, 5) = 4               -> grupo 7 = {C, D, E}
#   4. {A,B}+{C,D,E} a min(6, 10, 9, 5, 9, 8) = 5 -> grupo 8 = todos
EJEMPLO = [
    [0, 2, 6, 10, 9],
    [2, 0, 5, 9, 8],
    [6, 5, 0, 4, 5],
    [10, 9, 4, 0, 3],
    [9, 8, 5, 3, 0],
]


def _miembros_por_id(historial, n):
    miembros = {i: [i] for i in range(n)}
    for f in historial:
        miembros[f["nuevo_grupo"]] = f["miembros"]
    return miembros


class TestCriterio(unittest.TestCase):
    def test_definicion_es_el_minimo_entre_pares(self):
        # {A, B} vs {C, D, E}: min(6, 10, 9, 5, 9, 8) = 5
        self.assertEqual(distancia_enlace_simple([0, 1], [2, 3, 4], EJEMPLO), 5)

    def test_regla_de_actualizacion(self):
        self.assertEqual(actualizar_enlace_simple(4, 5), 4)
        self.assertEqual(actualizar_enlace_simple(7, 3), 3)


class TestEjemploResueltoAMano(unittest.TestCase):
    def setUp(self):
        self.historial = single_linkage(EJEMPLO)

    def test_cantidad_de_fusiones(self):
        self.assertEqual(len(self.historial), 4)

    def test_orden_y_distancias_de_las_fusiones(self):
        resumen = [(f["grupo_a"], f["grupo_b"], f["distancia"]) for f in self.historial]
        self.assertEqual(resumen, [(0, 1, 2), (3, 4, 3), (2, 6, 4), (5, 7, 5)])

    def test_identificadores_y_miembros(self):
        self.assertEqual([f["nuevo_grupo"] for f in self.historial], [5, 6, 7, 8])
        self.assertEqual(self.historial[2]["miembros"], [2, 3, 4])
        self.assertEqual(self.historial[-1]["miembros"], [0, 1, 2, 3, 4])
        self.assertEqual([f["tamano"] for f in self.historial], [2, 2, 3, 5])

    def test_distancias_no_decrecen(self):
        distancias = [f["distancia"] for f in self.historial]
        self.assertEqual(distancias, sorted(distancias))


class TestReglaCoincideConDefinicion(unittest.TestCase):
    def test_matrices_aleatorias(self):
        """En cada fusion, la distancia usada debe ser la de la definicion."""
        generador = random.Random(7)
        for _ in range(30):
            n = generador.randint(3, 12)
            m = [[0.0] * n for _ in range(n)]
            for i in range(n):
                for j in range(i + 1, n):
                    m[i][j] = m[j][i] = generador.random()
            historial = single_linkage(m)
            miembros = _miembros_por_id(historial, n)
            for f in historial:
                esperado = distancia_enlace_simple(
                    miembros[f["grupo_a"]], miembros[f["grupo_b"]], m)
                self.assertAlmostEqual(f["distancia"], esperado)


class TestEmpatesYCasosEspeciales(unittest.TestCase):
    def test_empate_se_resuelve_por_menores_identificadores(self):
        # Todas las distancias iguales: siempre se fusionan los primeros
        m = [[0, 1, 1, 1], [1, 0, 1, 1], [1, 1, 0, 1], [1, 1, 1, 0]]
        resumen = [(f["grupo_a"], f["grupo_b"]) for f in single_linkage(m)]
        self.assertEqual(resumen, [(0, 1), (2, 3), (4, 5)])

    def test_efecto_cadena(self):
        # Puntos en una recta 0, 1, 2, 3, 10: el enlace simple los encadena
        posiciones = [0, 1, 2, 3, 10]
        m = [[abs(p - q) for q in posiciones] for p in posiciones]
        historial = single_linkage(m)
        self.assertEqual([f["distancia"] for f in historial], [1, 1, 1, 7])
        self.assertEqual(historial[2]["miembros"], [0, 1, 2, 3])

    def test_dos_elementos(self):
        historial = single_linkage([[0, 0.4], [0.4, 0]])
        self.assertEqual(len(historial), 1)
        self.assertEqual(historial[0]["distancia"], 0.4)

    def test_no_modifica_la_matriz(self):
        copia = [fila[:] for fila in EJEMPLO]
        single_linkage(EJEMPLO)
        self.assertEqual(EJEMPLO, copia)


class TestValidacion(unittest.TestCase):
    def test_no_cuadrada(self):
        with self.assertRaises(ValueError):
            validar_matriz_distancias([[0, 1, 2], [1, 0, 3]])

    def test_no_simetrica(self):
        with self.assertRaises(ValueError):
            validar_matriz_distancias([[0, 1], [2, 0]])

    def test_diagonal_distinta_de_cero(self):
        with self.assertRaises(ValueError):
            validar_matriz_distancias([[1, 1], [1, 0]])

    def test_distancia_negativa(self):
        with self.assertRaises(ValueError):
            validar_matriz_distancias([[0, -1], [-1, 0]])

    def test_un_solo_elemento(self):
        with self.assertRaises(ValueError):
            single_linkage([[0]])


class TestCortarEnKGrupos(unittest.TestCase):
    def setUp(self):
        self.historial = single_linkage(EJEMPLO)

    def test_dos_grupos(self):
        self.assertEqual(cortar_en_k_grupos(self.historial, 5, 2), [[0, 1], [2, 3, 4]])

    def test_tres_grupos(self):
        self.assertEqual(cortar_en_k_grupos(self.historial, 5, 3), [[0, 1], [2], [3, 4]])

    def test_extremos(self):
        self.assertEqual(cortar_en_k_grupos(self.historial, 5, 1), [[0, 1, 2, 3, 4]])
        self.assertEqual(cortar_en_k_grupos(self.historial, 5, 5), [[0], [1], [2], [3], [4]])

    def test_k_invalido(self):
        with self.assertRaises(ValueError):
            cortar_en_k_grupos(self.historial, 5, 0)
        with self.assertRaises(ValueError):
            cortar_en_k_grupos(self.historial, 5, 6)


if __name__ == "__main__":
    unittest.main()
