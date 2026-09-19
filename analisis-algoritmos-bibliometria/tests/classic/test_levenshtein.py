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
    traceback,
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


class TestTraceback(unittest.TestCase):

    def test_secuencias_identicas_solo_coincidencias(self):
        # Si A == B, el camino debe ser puro "coincidencia", sin sustituciones,
        # inserciones ni eliminaciones
        a = ["gato", "come", "pescado"]
        D = build_levenshtein_matrix(a, a)
        operaciones = traceback(a, a, D)
        self.assertTrue(all(op.startswith("coincidencia") for op in operaciones))

    def test_longitud_camino_igual_o_mayor_que_la_secuencia_mas_larga(self):
        # El camino no puede ser más corto que la secuencia más larga
        a, b = "kitten", "sitting"
        D = build_levenshtein_matrix(a, b)
        operaciones = traceback(a, b, D)
        self.assertGreaterEqual(len(operaciones), max(len(a), len(b)))

    def test_suma_de_costos_coincide_con_la_distancia(self):
        # La cantidad de operaciones que NO son "coincidencia" debe ser
        # exactamente igual a la distancia de Levenshtein
        a, b = "gato", "pato"
        D = build_levenshtein_matrix(a, b)
        operaciones = traceback(a, b, D)
        costo_total = sum(1 for op in operaciones if not op.startswith("coincidencia"))
        self.assertEqual(costo_total, levenshtein_distance(a, b))

    def test_caso_solo_inserciones(self):
        # "gato" -> "gatos": debe aparecer una única inserción, sin eliminaciones
        a, b = "gato", "gatos"
        D = build_levenshtein_matrix(a, b)
        operaciones = traceback(a, b, D)
        self.assertEqual(sum(1 for op in operaciones if op.startswith("inserción")), 1)
        self.assertEqual(sum(1 for op in operaciones if op.startswith("eliminación")), 0)

    def test_caso_solo_eliminaciones(self):
        # "gatos" -> "gato": debe aparecer una única eliminación, sin inserciones
        a, b = "gatos", "gato"
        D = build_levenshtein_matrix(a, b)
        operaciones = traceback(a, b, D)
        self.assertEqual(sum(1 for op in operaciones if op.startswith("eliminación")), 1)
        self.assertEqual(sum(1 for op in operaciones if op.startswith("inserción")), 0)

    def test_caso_solo_sustitucion(self):
        # "gato" -> "pato": debe aparecer una única sustitución
        a, b = "gato", "pato"
        D = build_levenshtein_matrix(a, b)
        operaciones = traceback(a, b, D)
        sustituciones = [op for op in operaciones if op.startswith("sustitución")]
        self.assertEqual(len(sustituciones), 1)
        self.assertEqual(sustituciones[0], "sustitución(g→p)")

    def test_orden_natural_de_izquierda_a_derecha(self):
        # El primer elemento del camino debe corresponder al inicio de las
        # secuencias, no al final (verifica que se hizo el reverse())
        a, b = "gato", "pato"
        D = build_levenshtein_matrix(a, b)
        operaciones = traceback(a, b, D)
        self.assertTrue(operaciones[0].startswith("sustitución"))
        self.assertTrue(operaciones[-1].startswith("coincidencia"))


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
