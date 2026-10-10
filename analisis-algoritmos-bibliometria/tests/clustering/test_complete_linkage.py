"""
Pruebas unitarias para src/clustering/complete_linkage.py

Ejecutar desde la raiz del proyecto:

    .\\venv\\Scripts\\python.exe -m unittest tests/clustering/test_complete_linkage.py -v
"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from clustering.aglomerativo import cortar_en_k_grupos
from clustering.complete_linkage import (
    actualizar_enlace_completo,
    complete_linkage,
    distancia_enlace_completo,
)
from clustering.single_linkage import single_linkage

# Mismo ejemplo de 5 elementos que en test_single_linkage.py (A=0 ... E=4),
# resuelto a mano con enlace completo:
#   1. A+B a 2                         -> grupo 5 = {A, B}
#   2. D+E a 3                         -> grupo 6 = {D, E}
#   3. Candidatos: C-{D,E} = max(4, 5) = 5;  C-{A,B} = max(6, 5) = 6;
#                  {A,B}-{D,E} = max(10, 9, 9, 8) = 10
#      -> C+{D,E} a 5                  -> grupo 7 = {C, D, E}
#   4. {A,B}+{C,D,E} a max(6, 10, 9, 5, 9, 8) = 10 -> grupo 8 = todos
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


def _miembros_por_id(historial, n):
    miembros = {i: [i] for i in range(n)}
    for f in historial:
        miembros[f["nuevo_grupo"]] = f["miembros"]
    return miembros


class TestCriterio(unittest.TestCase):
    def test_definicion_es_el_maximo_entre_pares(self):
        # {A, B} vs {C, D, E}: max(6, 10, 9, 5, 9, 8) = 10
        self.assertEqual(distancia_enlace_completo([0, 1], [2, 3, 4], EJEMPLO), 10)

    def test_regla_de_actualizacion(self):
        self.assertEqual(actualizar_enlace_completo(4, 5), 5)
        self.assertEqual(actualizar_enlace_completo(7, 3), 7)


class TestEjemploResueltoAMano(unittest.TestCase):
    def setUp(self):
        self.historial = complete_linkage(EJEMPLO)

    def test_orden_y_distancias_de_las_fusiones(self):
        resumen = [(f["grupo_a"], f["grupo_b"], f["distancia"]) for f in self.historial]
        self.assertEqual(resumen, [(0, 1, 2), (3, 4, 3), (2, 6, 5), (5, 7, 10)])

    def test_miembros_y_tamanos(self):
        self.assertEqual(self.historial[2]["miembros"], [2, 3, 4])
        self.assertEqual([f["tamano"] for f in self.historial], [2, 2, 3, 5])

    def test_mismos_grupos_que_single_pero_otras_alturas(self):
        # En este ejemplo los dos criterios fusionan lo mismo, pero a otras
        # distancias: la ultima fusion ocurre a 5 (single) y a 10 (complete)
        simple = single_linkage(EJEMPLO)
        self.assertEqual([f["miembros"] for f in simple],
                         [f["miembros"] for f in self.historial])
        self.assertEqual(simple[-1]["distancia"], 5)
        self.assertEqual(self.historial[-1]["distancia"], 10)

    def test_cortar_en_dos_grupos(self):
        self.assertEqual(cortar_en_k_grupos(self.historial, 5, 2), [[0, 1], [2, 3, 4]])


class TestPropiedades(unittest.TestCase):
    def test_regla_coincide_con_definicion(self):
        """En cada fusion, la distancia usada debe ser la de la definicion."""
        generador = random.Random(11)
        for _ in range(30):
            n = generador.randint(3, 12)
            m = _matriz_aleatoria(generador, n)
            historial = complete_linkage(m)
            miembros = _miembros_por_id(historial, n)
            for f in historial:
                esperado = distancia_enlace_completo(
                    miembros[f["grupo_a"]], miembros[f["grupo_b"]], m)
                self.assertAlmostEqual(f["distancia"], esperado)

    def test_distancia_de_fusion_es_el_diametro_del_grupo(self):
        """La altura de cada fusion es la mayor distancia dentro del grupo creado."""
        generador = random.Random(13)
        for _ in range(30):
            n = generador.randint(3, 12)
            m = _matriz_aleatoria(generador, n)
            for f in complete_linkage(m):
                g = f["miembros"]
                diametro = max(m[a][b] for a in g for b in g)
                self.assertAlmostEqual(f["distancia"], diametro)

    def test_distancias_no_decrecen(self):
        generador = random.Random(17)
        for _ in range(30):
            m = _matriz_aleatoria(generador, generador.randint(3, 12))
            distancias = [f["distancia"] for f in complete_linkage(m)]
            self.assertEqual(distancias, sorted(distancias))

    def test_no_sufre_efecto_cadena(self):
        # Puntos en una recta 0, 1, 2, 3, 10. El enlace simple los encadena a
        # distancia 1; el completo ve la distancia entre los extremos del grupo.
        posiciones = [0, 1, 2, 3, 10]
        m = [[abs(p - q) for q in posiciones] for p in posiciones]
        distancias = [f["distancia"] for f in complete_linkage(m)]
        self.assertEqual(distancias, [1, 1, 3, 10])

    def test_no_modifica_la_matriz(self):
        copia = [fila[:] for fila in EJEMPLO]
        complete_linkage(EJEMPLO)
        self.assertEqual(EJEMPLO, copia)

    def test_matriz_invalida(self):
        with self.assertRaises(ValueError):
            complete_linkage([[0, 1], [2, 0]])


if __name__ == "__main__":
    unittest.main()
