"""
Pruebas unitarias para src/ordenamiento/radix_sort.py (ORD-3)

Ejecutar desde la raiz del proyecto:

    .\\venv\\Scripts\\python.exe -m unittest tests/ordenamiento/test_radix_sort.py -v
"""

import os
import random
import sys
import unittest
from unittest import mock

# Subimos dos niveles desde tests/ordenamiento/ hasta la raiz y apuntamos a src
RAIZ_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CARPETA_SRC = os.path.join(RAIZ_PROYECTO, "src")
if CARPETA_SRC not in sys.path:
    sys.path.insert(0, CARPETA_SRC)

import ordenamiento.radix_sort as modulo_radix  # noqa: E402
from ordenamiento.counting_sort import ordenar_por_frecuencia as ordenar_con_counting  # noqa: E402
from ordenamiento.frecuencias import obtener_lista_frecuencias  # noqa: E402
from ordenamiento.radix_sort import (  # noqa: E402
    cantidad_digitos,
    digito,
    ordenar_por_frecuencia,
    radix_sort,
)
from ordenamiento.radix_sort import ordenar_por_frecuencia_radix as ordenar_con_radix  # noqa: E402


class TestRadixSortFrecuencias(unittest.TestCase):
    """Pruebas de la version inicial (Camilo Ospina)."""

    def test_lista_vacia(self):
        """Prueba que el algoritmo maneje correctamente una lista vacia."""
        self.assertEqual(ordenar_con_radix([]), [])

    def test_un_solo_elemento(self):
        """Prueba que un unico elemento se mantenga igual."""
        lista = [("inteligencia", 12)]
        self.assertEqual(ordenar_con_radix(lista), [("inteligencia", 12)])

    def test_estabilidad_elementos_duplicados(self):
        """
        Prueba crucial: verifica que ante frecuencias identicas se respete
        estrictamente el orden de entrada original (estabilidad).
        """
        datos_entrada = [("palabra_A", 5), ("palabra_B", 5), ("palabra_C", 5)]
        resultado = ordenar_con_radix(datos_entrada)
        self.assertEqual(resultado[0][0], "palabra_A")
        self.assertEqual(resultado[1][0], "palabra_B")
        self.assertEqual(resultado[2][0], "palabra_C")

    def test_equivalencia_con_counting_sort(self):
        """
        Prueba de integracion con el corpus: Radix Sort y Counting Sort deben
        producir exactamente el mismo ranking.
        """
        pares_corpus = obtener_lista_frecuencias()
        ranking_counting = ordenar_con_counting(pares_corpus)
        ranking_radix = ordenar_con_radix(pares_corpus)
        self.assertEqual(len(ranking_counting), len(ranking_radix))
        for i in range(len(ranking_counting)):
            self.assertEqual(
                ranking_counting[i],
                ranking_radix[i],
                msg=f"Discrepancia en la posicion {i}: "
                    f"Counting={ranking_counting[i]} | Radix={ranking_radix[i]}",
            )


class TestDigitos(unittest.TestCase):
    def test_cantidad_de_digitos(self):
        self.assertEqual(cantidad_digitos(0), 1)
        self.assertEqual(cantidad_digitos(9), 1)
        self.assertEqual(cantidad_digitos(10), 2)
        self.assertEqual(cantidad_digitos(86), 2)
        self.assertEqual(cantidad_digitos(100), 3)

    def test_cantidad_de_digitos_en_base_2(self):
        # 5 = 101 en binario
        self.assertEqual(cantidad_digitos(5, base=2), 3)

    def test_extraer_digito(self):
        self.assertEqual(digito(839, 0), 9)
        self.assertEqual(digito(839, 1), 3)
        self.assertEqual(digito(839, 2), 8)
        self.assertEqual(digito(839, 3), 0)

    def test_valor_negativo(self):
        with self.assertRaises(ValueError):
            cantidad_digitos(-1)


class TestRadixSortGenerico(unittest.TestCase):
    def test_ejemplo_de_cormen_figura_8_3(self):
        a = [329, 457, 657, 839, 436, 720, 355]
        self.assertEqual(radix_sort(a, lambda x: x, 839),
                         [329, 355, 436, 457, 657, 720, 839])

    def test_hace_una_pasada_por_digito(self):
        """Con claves de 2 digitos debe llamar a Counting Sort exactamente 2 veces."""
        with mock.patch.object(modulo_radix, "counting_sort",
                               wraps=modulo_radix.counting_sort) as espia:
            radix_sort([86, 5, 40], lambda x: x, 86)
            self.assertEqual(espia.call_count, 2)
        with mock.patch.object(modulo_radix, "counting_sort",
                               wraps=modulo_radix.counting_sort) as espia:
            radix_sort([839, 5], lambda x: x, 839)
            self.assertEqual(espia.call_count, 3)

    def test_es_estable(self):
        elementos = [("a1", 12), ("b", 3), ("a2", 12), ("c", 40), ("a3", 12)]
        resultado = radix_sort(elementos, lambda e: e[1], 40)
        self.assertEqual([e[0] for e in resultado], ["b", "a1", "a2", "a3", "c"])

    def test_no_modifica_la_entrada(self):
        a = [30, 1, 22]
        radix_sort(a, lambda x: x, 30)
        self.assertEqual(a, [30, 1, 22])

    def test_coincide_con_la_referencia_en_varias_bases(self):
        generador = random.Random(73)
        for _ in range(50):
            maximo = generador.randint(0, 5000)
            a = [generador.randint(0, maximo) for _ in range(generador.randint(0, 200))]
            for base in (2, 10, 16):
                # sorted() se usa SOLO en la prueba, como referencia
                self.assertEqual(radix_sort(a, lambda x: x, maximo, base), sorted(a))

    def test_todas_las_claves_cero(self):
        self.assertEqual(radix_sort([0, 0, 0], lambda x: x, 0), [0, 0, 0])

    def test_clave_negativa(self):
        with self.assertRaises(ValueError):
            radix_sort([3, -3], lambda x: x, 9)

    def test_clave_mayor_que_el_maximo(self):
        with self.assertRaises(ValueError):
            radix_sort([3, 12], lambda x: x, 9)

    def test_clave_no_entera(self):
        with self.assertRaises(TypeError):
            radix_sort([1.5], lambda x: x, 9)

    def test_base_invalida(self):
        with self.assertRaises(ValueError):
            radix_sort([1], lambda x: x, 9, base=1)


class TestOrdenarPorFrecuencia(unittest.TestCase):
    def test_mayor_a_menor_con_empates(self):
        pares = [("x", 1), ("y", 30), ("z", 1), ("w", 30), ("v", 12)]
        self.assertEqual([t for t, _ in ordenar_por_frecuencia(pares)],
                         ["y", "w", "v", "x", "z"])

    def test_mismo_ranking_que_counting_sort_en_datos_aleatorios(self):
        generador = random.Random(79)
        for _ in range(40):
            pares = [(f"t{i}", generador.randint(1, 300)) for i in range(generador.randint(1, 400))]
            self.assertEqual(ordenar_por_frecuencia(pares), ordenar_con_counting(pares))


if __name__ == "__main__":
    unittest.main()
