"""
Pruebas unitarias para src/comparador.py

Usan un corpus y embeddings pequenos de prueba, sin leer archivos.

Ejecutar desde la raiz del proyecto:

    .\\venv\\Scripts\\python.exe -m unittest tests/test_comparador.py -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from comparador import comparar_articulos, leer_numeros, resumen_par
from classic.jaccard import jaccard, texto_a_conjunto

CORPUS = {
    1: {"numero": 1, "abstract_preprocesado": ["ai", "education", "review"]},
    2: {"numero": 2, "abstract_preprocesado": ["ai", "education", "assessment"]},
    3: {"numero": 3, "abstract_preprocesado": ["chatbot", "student", "writing"]},
}

MODELOS = {
    "ModeloA": {1: [1.0, 0.0], 2: [1.0, 1.0], 3: [0.0, 1.0]},
    "ModeloB": {1: [3.0, 4.0], 2: [3.0, 4.0], 3: [-3.0, -4.0]},
}


class TestCompararArticulos(unittest.TestCase):
    def test_incluye_los_4_clasicos_y_los_modelos_de_ia(self):
        resultado = comparar_articulos([1, 2], CORPUS, MODELOS)
        self.assertEqual(
            set(resultado["clasicos"]),
            {"Levenshtein", "Needleman-Wunsch", "Coseno TF-IDF", "Jaccard"},
        )
        self.assertEqual(set(resultado["ia"]), {"ModeloA", "ModeloB"})
        self.assertEqual(
            set(resultado["ia"]["ModeloA"]),
            {"coseno", "distancia_euclidiana", "similitud_euclidiana"},
        )

    def test_matrices_del_tamano_de_la_seleccion(self):
        resultado = comparar_articulos([1, 2, 3], CORPUS, MODELOS)
        self.assertEqual(len(resultado["clasicos"]["Jaccard"]), 3)
        self.assertEqual(len(resultado["ia"]["ModeloA"]["coseno"]), 3)

    def test_respeta_el_orden_de_seleccion(self):
        resultado = comparar_articulos([3, 1], CORPUS, MODELOS)
        # ModeloB: art. 3 y art. 1 son opuestos
        self.assertAlmostEqual(resultado["ia"]["ModeloB"]["coseno"][0][1], -1.0)

    def test_jaccard_coincide_con_el_modulo_clasico(self):
        resultado = comparar_articulos([1, 2], CORPUS, MODELOS)
        esperado = jaccard(
            texto_a_conjunto(CORPUS[1]["abstract_preprocesado"]),
            texto_a_conjunto(CORPUS[2]["abstract_preprocesado"]),
        )
        self.assertAlmostEqual(resultado["clasicos"]["Jaccard"][0][1], esperado)

    def test_valores_de_ia(self):
        resultado = comparar_articulos([1, 2], CORPUS, MODELOS)
        self.assertAlmostEqual(resultado["ia"]["ModeloA"]["coseno"][0][1], 2 ** -0.5)
        self.assertAlmostEqual(resultado["ia"]["ModeloA"]["distancia_euclidiana"][0][1], 1.0)
        self.assertAlmostEqual(resultado["ia"]["ModeloB"]["similitud_euclidiana"][0][1], 1.0)

    def test_sin_modelos_de_ia_solo_clasicos(self):
        resultado = comparar_articulos([1, 2], CORPUS, {})
        self.assertEqual(resultado["ia"], {})
        self.assertEqual(len(resultado["clasicos"]), 4)

    def test_articulo_inexistente(self):
        with self.assertRaises(ValueError):
            comparar_articulos([1, 99], CORPUS, MODELOS)

    def test_menos_de_dos_articulos(self):
        with self.assertRaises(ValueError):
            comparar_articulos([1], CORPUS, MODELOS)

    def test_modelo_sin_vector_para_un_articulo(self):
        incompleto = {"ModeloC": {1: [1.0, 0.0]}}
        with self.assertRaises(ValueError):
            comparar_articulos([1, 2], CORPUS, incompleto)


class TestResumenPar(unittest.TestCase):
    def test_una_fila_por_clasico_y_dos_por_modelo(self):
        filas = resumen_par(comparar_articulos([1, 2], CORPUS, MODELOS))
        self.assertEqual(len(filas), 4 + 2 * 2)
        self.assertEqual([f["tipo"] for f in filas].count("Clasico"), 4)

    def test_clasicos_sin_distancia(self):
        filas = resumen_par(comparar_articulos([1, 2], CORPUS, MODELOS))
        for fila in filas:
            if fila["tipo"] == "Clasico":
                self.assertIsNone(fila["distancia"])
            else:
                self.assertIsNotNone(fila["distancia"])


class TestLeerNumeros(unittest.TestCase):
    def test_argumentos_separados_por_espacio(self):
        self.assertEqual(leer_numeros(["2", "9"], []), [2, 9])

    def test_argumentos_con_comas(self):
        self.assertEqual(leer_numeros(["2,9,", "14"], []), [2, 9, 14])

    def test_texto_invalido_lanza_value_error(self):
        with self.assertRaises(ValueError):
            leer_numeros(["dos"], [])


if __name__ == "__main__":
    unittest.main()
