"""
Pruebas unitarias para src/busqueda/verificacion_busqueda.py (BUS-4)

Ejecutar desde la raiz del proyecto:

    .\\venv\\Scripts\\python.exe -m unittest tests/busqueda/test_verificacion_busqueda.py -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from busqueda.verificacion_busqueda import buscar_en_texto, buscar_y_verificar, cargar_corpus


def busqueda_ingenua(texto, patron):
    m = len(patron)
    return [i for i in range(len(texto) - m + 1) if texto[i:i + m] == patron]


class TestBuscarEnTexto(unittest.TestCase):
    def test_distingue_mayusculas_por_defecto(self):
        posiciones, coinciden, _ = buscar_en_texto("Education and education", "education")
        self.assertEqual(posiciones, [14])
        self.assertTrue(coinciden)

    def test_ignorar_mayusculas(self):
        posiciones, coinciden, _ = buscar_en_texto("Education and education", "EDUCATION", True)
        self.assertEqual(posiciones, [0, 14])
        self.assertTrue(coinciden)

    def test_ocurrencias_solapadas(self):
        posiciones, coinciden, _ = buscar_en_texto("aaaa", "aa")
        self.assertEqual(posiciones, [0, 1, 2])
        self.assertTrue(coinciden)

    def test_patron_vacio(self):
        with self.assertRaises(ValueError):
            buscar_y_verificar([], "")


class TestCorpus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = cargar_corpus()

    def test_caso_de_estudio_education(self):
        reporte = buscar_y_verificar(self.corpus, "education")
        self.assertTrue(reporte["todas_coinciden"])
        self.assertEqual(reporte["total_ocurrencias"], 78)
        art17 = next(a for a in reporte["articulos"] if a["numero"] == 17)
        self.assertEqual(len(art17["posiciones"]), 15)
        self.assertIn(485, art17["posiciones"])
        self.assertIn(516, art17["posiciones"])

    def test_coincide_con_referencia_ingenua(self):
        for patron in ("learning", "AI", "generative", "the", "e"):
            reporte = buscar_y_verificar(self.corpus, patron)
            self.assertTrue(reporte["todas_coinciden"], patron)
            esperado = sum(len(busqueda_ingenua(a["abstract"], patron)) for a in self.corpus)
            self.assertEqual(reporte["total_ocurrencias"], esperado, patron)

    def test_ignorar_mayusculas_encuentra_al_menos_las_mismas(self):
        exacto = buscar_y_verificar(self.corpus, "education")
        sin_mayus = buscar_y_verificar(self.corpus, "education", True)
        self.assertGreaterEqual(sin_mayus["total_ocurrencias"], exacto["total_ocurrencias"])
        self.assertEqual(sin_mayus["total_ocurrencias"], 86)


if __name__ == "__main__":
    unittest.main()
