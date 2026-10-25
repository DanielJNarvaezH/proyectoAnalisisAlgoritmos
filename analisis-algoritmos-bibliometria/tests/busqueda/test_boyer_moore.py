import os
import unittest

"""
Para correr python -m tests.busqueda.test_boyer_moore
que normal no funciona
"""

RAIZ_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.busqueda.boyer_moore import buscar_con_estadisticas, buscar

class TestBoyerMoore(unittest.TestCase):
    def test_busqueda_basica(self):
        texto = "ABAAABCD"
        patron = "ABC"
        res = buscar_con_estadisticas(texto, patron)
        self.assertIn(4, res["posiciones"])

    def test_multiples_ocurrencias(self):
        texto = "ANANAS"
        patron = "ANA"
        # Debe capturar índices 0 y 2 (incluso si se solapan)
        self.assertEqual(buscar(texto, patron), [0, 2])

    def test_caracter_inexistente(self):
        texto = "ZZZZZZZZ"
        patron = "ABC"
        self.assertEqual(buscar(texto, patron), [])

if __name__ == "__main__":
    unittest.main()
