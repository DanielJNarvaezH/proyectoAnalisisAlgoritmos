"""
Pruebas unitarias para src/busqueda/kmp.py (BUS-1)

Ejecutar desde la raiz del proyecto:

    .\\venv\\Scripts\\python.exe -m unittest tests/busqueda/test_kmp.py -v
"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from busqueda.kmp import buscar, buscar_con_estadisticas, tabla_prefijos


def busqueda_ingenua(texto, patron):
    """Referencia para las pruebas: compara el patron en cada posicion."""
    m = len(patron)
    return [i for i in range(len(texto) - m + 1) if texto[i:i + m] == patron]


class TestTablaPrefijos(unittest.TestCase):
    def test_ejemplo_de_cormen_figura_32_10(self):
        self.assertEqual(tabla_prefijos("ababaca"), [0, 0, 1, 2, 3, 0, 1])

    def test_ejemplo_resuelto_a_mano(self):
        # a a b a a a b
        # 0 1 0 1 2 2 3   ("aabaaab": el prefijo "aab" es tambien sufijo)
        self.assertEqual(tabla_prefijos("aabaaab"), [0, 1, 0, 1, 2, 2, 3])

    def test_sin_prefijos_repetidos(self):
        self.assertEqual(tabla_prefijos("abcd"), [0, 0, 0, 0])

    def test_un_solo_caracter_repetido(self):
        self.assertEqual(tabla_prefijos("aaaa"), [0, 1, 2, 3])

    def test_un_caracter(self):
        self.assertEqual(tabla_prefijos("a"), [0])

    def test_patron_vacio(self):
        with self.assertRaises(ValueError):
            tabla_prefijos("")

    def test_valores_son_prefijo_y_sufijo_propio(self):
        generador = random.Random(83)
        for _ in range(50):
            patron = "".join(generador.choice("ab") for _ in range(generador.randint(1, 15)))
            pi = tabla_prefijos(patron)
            for q, k in enumerate(pi):
                inicio = patron[:q + 1]
                self.assertLess(k, q + 1)
                self.assertEqual(inicio[:k], inicio[q + 1 - k:])


class TestBuscar(unittest.TestCase):
    def test_ejemplo_de_cormen(self):
        self.assertEqual(buscar("abababacaba", "ababaca"), [2])

    def test_varias_ocurrencias(self):
        texto = "AI in education: AI tools and AI ethics"
        self.assertEqual(buscar(texto, "AI"), [0, 17, 30])

    def test_ocurrencias_solapadas(self):
        self.assertEqual(buscar("aaaa", "aa"), [0, 1, 2])
        self.assertEqual(buscar("abababa", "aba"), [0, 2, 4])

    def test_sin_ocurrencias(self):
        self.assertEqual(buscar("generative models", "transformer"), [])

    def test_patron_mas_largo_que_el_texto(self):
        self.assertEqual(buscar("ai", "aied"), [])

    def test_patron_igual_al_texto(self):
        self.assertEqual(buscar("learning", "learning"), [0])

    def test_distingue_mayusculas(self):
        self.assertEqual(buscar("Learning and learning", "learning"), [13])

    def test_caracteres_acentuados(self):
        self.assertEqual(buscar("búsqueda de patrones en búsqueda", "búsqueda"), [0, 24])

    def test_texto_vacio(self):
        self.assertEqual(buscar("", "a"), [])

    def test_validaciones(self):
        with self.assertRaises(ValueError):
            buscar("texto", "")
        with self.assertRaises(TypeError):
            buscar(None, "a")

    def test_coincide_con_la_busqueda_ingenua(self):
        generador = random.Random(89)
        for _ in range(200):
            texto = "".join(generador.choice("abc") for _ in range(generador.randint(0, 60)))
            patron = "".join(generador.choice("abc") for _ in range(generador.randint(1, 5)))
            self.assertEqual(buscar(texto, patron), busqueda_ingenua(texto, patron))


class TestComplejidad(unittest.TestCase):
    def test_a_lo_sumo_2n_comparaciones(self):
        """Cota de Cormen et al. (2022, sec. 32.4): la busqueda hace <= 2n comparaciones."""
        generador = random.Random(97)
        for _ in range(100):
            texto = "".join(generador.choice("ab") for _ in range(generador.randint(1, 200)))
            patron = "".join(generador.choice("ab") for _ in range(generador.randint(1, 8)))
            resultado = buscar_con_estadisticas(texto, patron)
            self.assertLessEqual(resultado["comparaciones"], 2 * len(texto))

    def test_peor_caso_del_algoritmo_ingenuo_es_lineal(self):
        # Texto "aaa...a" y patron "aaaab": el ingenuo hace ~m comparaciones
        # por posicion; KMP mantiene <= 2n en total
        texto = "a" * 1000
        resultado = buscar_con_estadisticas(texto, "aaaab")
        self.assertEqual(resultado["posiciones"], [])
        self.assertLessEqual(resultado["comparaciones"], 2 * len(texto))

    def test_devuelve_la_tabla_usada(self):
        self.assertEqual(buscar_con_estadisticas("xx", "ababaca")["tabla_prefijos"],
                         [0, 0, 1, 2, 3, 0, 1])


if __name__ == "__main__":
    unittest.main()
