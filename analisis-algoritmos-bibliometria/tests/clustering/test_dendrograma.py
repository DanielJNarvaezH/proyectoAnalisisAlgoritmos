"""
Pruebas unitarias para src/clustering/dendrograma.py

Ejecutar desde la raiz del proyecto:

    .\\venv\\Scripts\\python.exe -m unittest tests/clustering/test_dendrograma.py -v
"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from clustering.average_linkage import average_linkage
from clustering.complete_linkage import complete_linkage
from clustering.dendrograma import (
    altura_de_union,
    construir_matriz_enlace,
    orden_de_hojas,
    validar_matriz_enlace,
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

# Matriz de enlace de single linkage para EJEMPLO, construida a mano
Z_SINGLE = [
    [0.0, 1.0, 2.0, 2.0],  # fila 0 -> grupo 5 = {A, B}
    [3.0, 4.0, 3.0, 2.0],  # fila 1 -> grupo 6 = {D, E}
    [2.0, 6.0, 4.0, 3.0],  # fila 2 -> grupo 7 = {C, D, E}
    [5.0, 7.0, 5.0, 5.0],  # fila 3 -> grupo 8 = todos
]


def _matriz_aleatoria(generador, n):
    m = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            m[i][j] = m[j][i] = generador.random()
    return m


class TestConstruccion(unittest.TestCase):
    def test_ejemplo_construido_a_mano(self):
        self.assertEqual(construir_matriz_enlace(single_linkage(EJEMPLO)), Z_SINGLE)

    def test_valores_son_float(self):
        for fila in construir_matriz_enlace(complete_linkage(EJEMPLO)):
            self.assertTrue(all(isinstance(x, float) for x in fila))

    def test_alturas_segun_criterio(self):
        # La ultima fusion ocurre a 5 (single), 47/6 (average) y 10 (complete)
        self.assertEqual(construir_matriz_enlace(single_linkage(EJEMPLO))[-1][2], 5)
        self.assertAlmostEqual(construir_matriz_enlace(average_linkage(EJEMPLO))[-1][2], 47 / 6)
        self.assertEqual(construir_matriz_enlace(complete_linkage(EJEMPLO))[-1][2], 10)

    def test_los_tres_criterios_producen_matrices_validas(self):
        generador = random.Random(31)
        for _ in range(20):
            n = generador.randint(2, 15)
            m = _matriz_aleatoria(generador, n)
            for algoritmo in (single_linkage, complete_linkage, average_linkage):
                validar_matriz_enlace(construir_matriz_enlace(algoritmo(m)), n)


class TestValidacion(unittest.TestCase):
    def _invalida(self, z, n=5):
        with self.assertRaises(ValueError):
            validar_matriz_enlace(z, n)

    def test_matriz_correcta_no_lanza_error(self):
        validar_matriz_enlace(Z_SINGLE, 5)

    def test_cantidad_de_filas_incorrecta(self):
        self._invalida(Z_SINGLE[:3])

    def test_columnas_incorrectas(self):
        self._invalida([fila[:3] for fila in Z_SINGLE])

    def test_grupo_que_todavia_no_existe(self):
        self._invalida([[0, 1, 2, 2], [3, 7, 3, 2], [2, 6, 4, 3], [5, 7, 5, 5]])

    def test_grupo_usado_dos_veces(self):
        self._invalida([[0, 1, 2, 2], [0, 4, 3, 2], [2, 6, 4, 3], [5, 7, 5, 5]])

    def test_grupo_consigo_mismo(self):
        self._invalida([[0, 0, 2, 2], [3, 4, 3, 2], [2, 6, 4, 3], [5, 7, 5, 5]])

    def test_tamano_incorrecto(self):
        self._invalida([[0, 1, 2, 2], [3, 4, 3, 2], [2, 6, 4, 4], [5, 7, 5, 5]])

    def test_distancia_que_decrece(self):
        self._invalida([[0, 1, 2, 2], [3, 4, 1, 2], [2, 6, 4, 3], [5, 7, 5, 5]])


class TestOrdenDeHojas(unittest.TestCase):
    def test_ejemplo(self):
        # Raiz 8 = (5, 7); 5 = (A, B); 7 = (C, 6); 6 = (D, E)
        self.assertEqual(orden_de_hojas(Z_SINGLE, 5), [0, 1, 2, 3, 4])

    def test_es_una_permutacion_de_los_elementos(self):
        generador = random.Random(37)
        for _ in range(20):
            n = generador.randint(2, 15)
            z = construir_matriz_enlace(complete_linkage(_matriz_aleatoria(generador, n)))
            self.assertEqual(sorted(orden_de_hojas(z, n)), list(range(n)))

    def test_cada_grupo_queda_contiguo(self):
        # En un dendrograma, los miembros de cada grupo aparecen juntos
        generador = random.Random(41)
        n = 12
        historial = average_linkage(_matriz_aleatoria(generador, n))
        orden = orden_de_hojas(construir_matriz_enlace(historial), n)
        posicion = {elemento: p for p, elemento in enumerate(orden)}
        for fusion in historial:
            posiciones = sorted(posicion[e] for e in fusion["miembros"])
            self.assertEqual(posiciones, list(range(posiciones[0], posiciones[-1] + 1)))


class TestAlturaDeUnion(unittest.TestCase):
    def test_ejemplo_single(self):
        self.assertEqual(altura_de_union(Z_SINGLE, 5, 0, 1), 2)
        self.assertEqual(altura_de_union(Z_SINGLE, 5, 3, 4), 3)
        self.assertEqual(altura_de_union(Z_SINGLE, 5, 2, 3), 4)
        self.assertEqual(altura_de_union(Z_SINGLE, 5, 0, 4), 5)

    def test_simetrica(self):
        self.assertEqual(altura_de_union(Z_SINGLE, 5, 4, 2), altura_de_union(Z_SINGLE, 5, 2, 4))

    def test_ejemplo_complete(self):
        z = construir_matriz_enlace(complete_linkage(EJEMPLO))
        self.assertEqual(altura_de_union(z, 5, 0, 4), 10)


if __name__ == "__main__":
    unittest.main()
