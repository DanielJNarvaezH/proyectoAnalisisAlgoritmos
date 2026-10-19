"""
Pruebas unitarias para src/ordenamiento/bucket_sort.py (ORD-4)

Ejecutar desde la raiz del proyecto:

    .\\venv\\Scripts\\python.exe -m unittest tests/ordenamiento/test_bucket_sort.py -v
"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from ordenamiento.bucket_sort import (
    bucket_sort,
    distribuir,
    ocupacion_cubetas,
    ordenar_por_frecuencia,
    parametros_cubetas,
)
from ordenamiento.counting_sort import ordenar_por_frecuencia as counting_por_frecuencia


class TestParametros(unittest.TestCase):
    def test_raiz_cuadrada_por_defecto(self):
        # k = 86: sqrt(87) = 9,33 -> m = 10 cubetas; w = ceil(87 / 10) = 9
        self.assertEqual(parametros_cubetas(86), (10, 9))

    def test_raiz_exacta(self):
        # k = 15: sqrt(16) = 4 -> m = 4, w = 4
        self.assertEqual(parametros_cubetas(15), (4, 4))

    def test_m_se_limita_a_k_mas_uno(self):
        self.assertEqual(parametros_cubetas(5, num_cubetas=100), (6, 1))

    def test_una_sola_cubeta(self):
        self.assertEqual(parametros_cubetas(9, num_cubetas=1), (1, 10))

    def test_cubetas_cubren_todo_el_rango(self):
        for k in range(0, 120):
            for m in (None, 1, 2, 3, 7, 50):
                cubetas, ancho = parametros_cubetas(k, m)
                self.assertGreaterEqual(cubetas * ancho, k + 1)

    def test_valores_invalidos(self):
        with self.assertRaises(ValueError):
            parametros_cubetas(-1)
        with self.assertRaises(ValueError):
            parametros_cubetas(5, num_cubetas=0)


class TestDistribucion(unittest.TestCase):
    def test_ejemplo_a_mano(self):
        # k = 8, m = 3 -> w = 3: cubetas [0-2], [3-5], [6-8]
        claves = [7, 1, 4, 0, 8, 3, 2]
        cubetas, w = distribuir(claves, lambda x: x, 8, num_cubetas=3)
        self.assertEqual(w, 3)
        self.assertEqual(cubetas, [[1, 0, 2], [4, 3], [7, 8]])

    def test_conserva_el_orden_de_llegada(self):
        elementos = [("a", 1), ("b", 1), ("c", 1)]
        cubetas, _ = distribuir(elementos, lambda e: e[1], 4, num_cubetas=2)
        self.assertEqual(cubetas[0], elementos)


class TestBucketSort(unittest.TestCase):
    def test_ejemplo_a_mano(self):
        claves = [7, 1, 4, 0, 8, 3, 2]
        self.assertEqual(bucket_sort(claves, lambda x: x, 8, num_cubetas=3),
                         [0, 1, 2, 3, 4, 7, 8])

    def test_es_estable(self):
        elementos = [("a1", 2), ("b", 0), ("a2", 2), ("c", 5), ("a3", 2)]
        resultado = bucket_sort(elementos, lambda e: e[1], 5, num_cubetas=2)
        self.assertEqual([e[0] for e in resultado], ["b", "a1", "a2", "a3", "c"])

    def test_casos_borde(self):
        self.assertEqual(bucket_sort([], lambda x: x, 0), [])
        self.assertEqual(bucket_sort([3], lambda x: x, 3), [3])
        self.assertEqual(bucket_sort([2, 2, 2], lambda x: x, 2), [2, 2, 2])

    def test_no_modifica_la_entrada(self):
        a = [3, 1, 2]
        bucket_sort(a, lambda x: x, 3)
        self.assertEqual(a, [3, 1, 2])

    def test_coincide_con_la_referencia_con_cualquier_numero_de_cubetas(self):
        generador = random.Random(67)
        for _ in range(60):
            k = generador.randint(0, 100)
            a = [generador.randint(0, k) for _ in range(generador.randint(0, 200))]
            for m in (None, 1, 2, 5, k + 1):
                # sorted() se usa SOLO en la prueba, como referencia
                self.assertEqual(bucket_sort(a, lambda x: x, k, m), sorted(a))

    def test_clave_fuera_de_rango(self):
        with self.assertRaises(ValueError):
            bucket_sort([1, 9], lambda x: x, 5)

    def test_clave_no_entera(self):
        with self.assertRaises(TypeError):
            bucket_sort([2.5], lambda x: x, 5)


class TestOrdenarPorFrecuencia(unittest.TestCase):
    def test_mayor_a_menor_con_empates(self):
        pares = [("x", 1), ("y", 3), ("z", 1), ("w", 3), ("v", 2)]
        self.assertEqual([t for t, _ in ordenar_por_frecuencia(pares)],
                         ["y", "w", "v", "x", "z"])

    def test_mismo_ranking_que_counting_sort(self):
        """Los dos algoritmos son estables: deben producir el mismo ranking."""
        generador = random.Random(71)
        for _ in range(40):
            pares = [(f"t{i}", generador.randint(1, 90)) for i in range(generador.randint(1, 400))]
            for m in (None, 1, 4, 13):
                self.assertEqual(ordenar_por_frecuencia(pares, m), counting_por_frecuencia(pares))

    def test_distribucion_sesgada_como_en_el_corpus(self):
        # Muchas frecuencias 1 (ley de Zipf): el resultado debe seguir siendo correcto
        pares = [(f"t{i}", 1) for i in range(500)] + [("ai", 86), ("education", 57)]
        ranking = ordenar_por_frecuencia(pares)
        self.assertEqual(ranking[:2], [("ai", 86), ("education", 57)])
        self.assertEqual(ranking[2:], [(f"t{i}", 1) for i in range(500)])

    def test_lista_vacia(self):
        self.assertEqual(ordenar_por_frecuencia([]), [])


class TestOcupacion(unittest.TestCase):
    def test_suma_de_ocupacion_es_n_y_rangos_cubren_las_frecuencias(self):
        pares = [("a", 9), ("b", 1), ("c", 5), ("d", 1), ("e", 0)]
        ocupacion = ocupacion_cubetas(pares, num_cubetas=2)
        self.assertEqual(sum(c for _, _, c in ocupacion), 5)
        # k = 9, w = 5: cubeta 0 -> claves 0-4 -> frecuencias 5-9; cubeta 1 -> frecuencias 0-4
        self.assertEqual(ocupacion, [(5, 9, 2), (0, 4, 3)])


if __name__ == "__main__":
    unittest.main()
