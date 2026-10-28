"""
Pruebas unitarias para src/busqueda/boyer_moore.py (BUS-2)

Ejecutar desde la raiz del proyecto:

    .\\venv\\Scripts\\python.exe -m unittest tests/busqueda/test_boyer_moore.py -v
"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from busqueda.boyer_moore import (
    buscar,
    buscar_con_estadisticas,
    construir_caracter_malo,
    construir_sufijo_bueno,
)


def busqueda_ingenua(texto, patron):
    """Referencia para las pruebas: compara el patron en cada posicion."""
    m = len(patron)
    return [i for i in range(len(texto) - m + 1) if texto[i:i + m] == patron]


class TestTablaCaracterMalo(unittest.TestCase):
    def test_ultima_aparicion_de_cada_caracter(self):
        # A B C D A B D -> A en 0 y 4 (queda 4), B en 1 y 5 (queda 5), C en 2, D en 3 y 6
        self.assertEqual(construir_caracter_malo("ABCDABD"), {"A": 4, "B": 5, "C": 2, "D": 6})

    def test_caracter_repetido(self):
        self.assertEqual(construir_caracter_malo("AAAA"), {"A": 3})


class TestTablaSufijoBueno(unittest.TestCase):
    def test_patron_sin_bordes(self):
        # Desajuste en la ultima posicion: salto 1. Sufijo "D": la otra D (pos. 3)
        # esta precedida por C, distinto de B (pos. 5) -> salto 3. Sin borde: 7.
        self.assertEqual(construir_sufijo_bueno("ABCDABD"), [7, 7, 7, 7, 7, 7, 3, 1])

    def test_patron_con_borde(self):
        # "AB" es prefijo y sufijo de "ABAB": tras una ocurrencia el salto es 2
        self.assertEqual(construir_sufijo_bueno("ABAB"), [2, 2, 2, 4, 1])

    def test_un_solo_caracter_repetido(self):
        self.assertEqual(construir_sufijo_bueno("AAAA"), [1, 1, 2, 3, 4])

    def test_todos_los_saltos_son_positivos(self):
        generador = random.Random(109)
        for _ in range(200):
            patron = "".join(generador.choice("ab") for _ in range(generador.randint(1, 10)))
            tabla = construir_sufijo_bueno(patron)
            self.assertEqual(len(tabla), len(patron) + 1)
            self.assertTrue(all(1 <= salto <= len(patron) for salto in tabla))


class TestBuscar(unittest.TestCase):
    def test_ejemplo_clasico_de_boyer_y_moore(self):
        r = buscar_con_estadisticas("HERE IS A SIMPLE EXAMPLE", "EXAMPLE")
        self.assertEqual(r["posiciones"], [17])
        # Mucho menos que los 24 caracteres del texto: salta bloques completos
        self.assertLess(r["comparaciones"], 24)

    def test_busqueda_basica(self):
        self.assertEqual(buscar("ABAAABCD", "ABC"), [4])

    def test_ocurrencias_solapadas(self):
        self.assertEqual(buscar("ANANAS", "ANA"), [0, 2])
        self.assertEqual(buscar("aaaa", "aa"), [0, 1, 2])

    def test_varias_ocurrencias(self):
        self.assertEqual(buscar("AI in education: AI tools and AI ethics", "AI"), [0, 17, 30])

    def test_casos_borde(self):
        self.assertEqual(buscar("ZZZZZZZZ", "ABC"), [])
        self.assertEqual(buscar("ai", "aied"), [])
        self.assertEqual(buscar("learning", "learning"), [0])
        self.assertEqual(buscar("", "a"), [])

    def test_distingue_mayusculas_y_acentos(self):
        self.assertEqual(buscar("Learning and learning", "learning"), [13])
        self.assertEqual(buscar("búsqueda de patrones en búsqueda", "búsqueda"), [0, 24])

    def test_validaciones(self):
        with self.assertRaises(ValueError):
            buscar("texto", "")
        with self.assertRaises(TypeError):
            buscar(None, "a")

    def test_coincide_con_la_busqueda_ingenua(self):
        generador = random.Random(113)
        for alfabeto in ("ab", "abc", "abcd"):
            for _ in range(300):
                texto = "".join(generador.choice(alfabeto) for _ in range(generador.randint(0, 60)))
                patron = "".join(generador.choice(alfabeto) for _ in range(generador.randint(1, 7)))
                self.assertEqual(buscar(texto, patron), busqueda_ingenua(texto, patron))


class TestEstadisticas(unittest.TestCase):
    def test_devuelve_las_tablas_usadas(self):
        r = buscar_con_estadisticas("xx", "ABAB")
        self.assertEqual(r["tabla_caracter_malo"], {"A": 2, "B": 3})
        self.assertEqual(r["tabla_sufijo_bueno"], [2, 2, 2, 4, 1])

    def test_sublineal_si_el_caracter_no_esta_en_el_patron(self):
        # Cada desajuste con 'x' permite saltar el patron completo
        r = buscar_con_estadisticas("x" * 80 + "learning", "learning")
        self.assertEqual(r["posiciones"], [80])
        self.assertLess(r["comparaciones"], 88 // 2)

    def test_peor_caso_con_muchas_ocurrencias(self):
        # Texto y patron de un solo caracter: cada ocurrencia cuesta m comparaciones
        r = buscar_con_estadisticas("a" * 20, "aaa")
        self.assertEqual(len(r["posiciones"]), 18)
        self.assertEqual(r["comparaciones"], 18 * 3)

    def test_cada_salto_usa_una_regla(self):
        r = buscar_con_estadisticas("HERE IS A SIMPLE EXAMPLE", "EXAMPLE")
        self.assertGreater(r["saltos_caracter_malo"] + r["saltos_sufijo_bueno"], 0)


if __name__ == "__main__":
    unittest.main()
