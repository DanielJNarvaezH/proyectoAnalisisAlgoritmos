"""
Pruebas unitarias para src/ordenamiento/counting_sort.py (ORD-2)

Ejecutar desde la raiz del proyecto:

    .\\venv\\Scripts\\python.exe -m unittest tests/ordenamiento/test_counting_sort.py -v
"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ordenamiento.counting_sort import (
    counting_sort,
    frecuencia_maxima,
    ordenar_por_frecuencia,
)
from ordenamiento.frecuencias import contar_frecuencias

CORPUS = [
    {"numero": 1, "abstract_preprocesado": ["ai", "education", "ai", "review"]},
    {"numero": 2, "abstract_preprocesado": ["student", "ai", "review", "chatbot"]},
]


class TestCountingSortGenerico(unittest.TestCase):
    def test_ejemplo_de_cormen_figura_8_2(self):
        # A = <2, 5, 3, 0, 2, 3, 0, 3>, k = 5  ->  <0, 0, 2, 2, 3, 3, 3, 5>
        a = [2, 5, 3, 0, 2, 3, 0, 3]
        self.assertEqual(counting_sort(a, lambda x: x, 5), [0, 0, 2, 2, 3, 3, 3, 5])

    def test_es_estable(self):
        # Mismas claves: deben conservar el orden de entrada (a1 antes que a2)
        elementos = [("a1", 1), ("b", 0), ("a2", 1), ("c", 2), ("a3", 1)]
        resultado = counting_sort(elementos, lambda e: e[1], 2)
        self.assertEqual([e[0] for e in resultado], ["b", "a1", "a2", "a3", "c"])

    def test_no_modifica_la_entrada(self):
        a = [3, 1, 2]
        counting_sort(a, lambda x: x, 3)
        self.assertEqual(a, [3, 1, 2])

    def test_casos_borde(self):
        self.assertEqual(counting_sort([], lambda x: x, 0), [])
        self.assertEqual(counting_sort([4], lambda x: x, 4), [4])
        self.assertEqual(counting_sort([0, 0, 0], lambda x: x, 0), [0, 0, 0])

    def test_coincide_con_la_referencia_en_datos_aleatorios(self):
        generador = random.Random(59)
        for _ in range(50):
            k = generador.randint(0, 100)
            a = [generador.randint(0, k) for _ in range(generador.randint(0, 200))]
            # sorted() se usa SOLO en la prueba, como referencia
            self.assertEqual(counting_sort(a, lambda x: x, k), sorted(a))

    def test_clave_fuera_de_rango(self):
        with self.assertRaises(ValueError):
            counting_sort([1, 6], lambda x: x, 5)
        with self.assertRaises(ValueError):
            counting_sort([-1], lambda x: x, 5)

    def test_clave_no_entera(self):
        with self.assertRaises(TypeError):
            counting_sort([1.5], lambda x: x, 5)

    def test_k_invalido(self):
        with self.assertRaises(ValueError):
            counting_sort([1], lambda x: x, -1)


class TestOrdenarPorFrecuencia(unittest.TestCase):
    def test_mayor_a_menor(self):
        pares = [("a", 2), ("b", 5), ("c", 1), ("d", 3)]
        self.assertEqual([t for t, _ in ordenar_por_frecuencia(pares)], ["b", "d", "a", "c"])

    def test_empates_conservan_el_orden_de_entrada(self):
        pares = [("x", 1), ("y", 3), ("z", 1), ("w", 3), ("v", 2)]
        self.assertEqual([t for t, _ in ordenar_por_frecuencia(pares)],
                         ["y", "w", "v", "x", "z"])

    def test_ejemplo_del_corpus(self):
        ranking = ordenar_por_frecuencia(contar_frecuencias(CORPUS))
        self.assertEqual(ranking, [("ai", 3), ("review", 2), ("education", 1),
                                   ("student", 1), ("chatbot", 1)])

    def test_coincide_con_ordenamiento_estable_de_referencia(self):
        generador = random.Random(61)
        for _ in range(30):
            pares = [(f"t{i}", generador.randint(1, 40)) for i in range(generador.randint(1, 300))]
            # Referencia: sorted() es estable, con clave -frecuencia (solo en la prueba)
            esperado = sorted(pares, key=lambda p: -p[1])
            self.assertEqual(ordenar_por_frecuencia(pares), esperado)

    def test_frecuencia_maxima(self):
        self.assertEqual(frecuencia_maxima([("a", 2), ("b", 7), ("c", 1)]), 7)

    def test_lista_vacia(self):
        self.assertEqual(ordenar_por_frecuencia([]), [])


if __name__ == "__main__":
    unittest.main()
