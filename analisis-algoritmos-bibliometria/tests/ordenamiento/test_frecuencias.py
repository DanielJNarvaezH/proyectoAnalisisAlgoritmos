"""
Pruebas unitarias para src/ordenamiento/frecuencias.py (ORD-1)

Ejecutar desde la raiz del proyecto:

    .\\venv\\Scripts\\python.exe -m unittest tests/ordenamiento/test_frecuencias.py -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ordenamiento.frecuencias import contar_frecuencias

CORPUS = [
    {"numero": 1, "abstract_preprocesado": ["ai", "education", "ai", "review"]},
    {"numero": 2, "abstract_preprocesado": ["student", "ai", "review", "chatbot"]},
]


class TestFrecuencias(unittest.TestCase):
    def test_conteo(self):
        conteo = dict(contar_frecuencias(CORPUS))
        self.assertEqual(conteo, {"ai": 3, "education": 1, "review": 2,
                                  "student": 1, "chatbot": 1})

    def test_orden_de_primera_aparicion(self):
        terminos = [t for t, _ in contar_frecuencias(CORPUS)]
        self.assertEqual(terminos, ["ai", "education", "review", "student", "chatbot"])

    def test_suma_de_frecuencias_es_el_total_de_tokens(self):
        total = sum(f for _, f in contar_frecuencias(CORPUS))
        self.assertEqual(total, 8)

    def test_corpus_vacio(self):
        self.assertEqual(contar_frecuencias([]), [])

    def test_no_ordena_por_frecuencia(self):
        # "ai" (3) aparece primero solo porque es el primer termino del corpus;
        # "review" (2) queda despues de "education" (1): la lista no esta ordenada
        terminos = [t for t, _ in contar_frecuencias(CORPUS)]
        self.assertLess(terminos.index("education"), terminos.index("review"))


if __name__ == "__main__":
    unittest.main()
