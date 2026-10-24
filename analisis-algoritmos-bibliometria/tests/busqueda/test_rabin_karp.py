"""
Pruebas unitarias para src/busqueda/rabin_karp.py (BUS-3)

Ejecutar desde la raiz del proyecto:

    .\\venv\\Scripts\\python.exe -m unittest tests/busqueda/test_rabin_karp.py -v
"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from busqueda.rabin_karp import (
    buscar,
    buscar_con_estadisticas,
    hash_polinomial,
    potencia_modular,
    siguiente_hash,
)


def busqueda_ingenua(texto, patron):
    """Referencia para las pruebas: compara el patron en cada posicion."""
    m = len(patron)
    return [i for i in range(len(texto) - m + 1) if texto[i:i + m] == patron]


class TestHash(unittest.TestCase):
    def test_hash_del_ejemplo_de_cormen(self):
        # Digitos en base 10, modulo 13: 31415 mod 13 = 7
        self.assertEqual(hash_polinomial("31415", 10, 13, int), 7)

    def test_horner_calculado_a_mano(self):
        # "ab" con base 256: 97*256 + 98 = 24930; mod 101 = 84
        self.assertEqual(hash_polinomial("ab", 256, 101), (97 * 256 + 98) % 101)

    def test_potencia_modular(self):
        # 10^4 = 10000; 10000 mod 13 = 3
        self.assertEqual(potencia_modular(10, 4, 13), 3)
        self.assertEqual(potencia_modular(256, 0, 101), 1)

    def test_rolling_hash_del_ejemplo_de_cormen(self):
        # De "31415" (hash 7) a "14152": sale '3', entra '2', h = 10^4 mod 13 = 3
        # (10 * (7 - 3*3) + 2) mod 13 = (-18) mod 13 = 8 = 14152 mod 13
        self.assertEqual(siguiente_hash(7, "3", "2", 3, 10, 13, int), 8)
        self.assertEqual(hash_polinomial("14152", 10, 13, int), 8)

    def test_rolling_hash_coincide_con_el_calculo_directo(self):
        generador = random.Random(101)
        for _ in range(30):
            texto = "".join(generador.choice("abcdefgh") for _ in range(generador.randint(5, 50)))
            m = generador.randint(1, 5)
            primo = generador.choice([13, 101, 1_000_000_007])
            h = potencia_modular(256, m - 1, primo)
            t = hash_polinomial(texto[:m], 256, primo)
            for s in range(len(texto) - m):
                t = siguiente_hash(t, texto[s], texto[s + m], h, 256, primo)
                self.assertEqual(t, hash_polinomial(texto[s + 1:s + 1 + m], 256, primo))


class TestEjemploDeCormen(unittest.TestCase):
    """Figura 32.5 de Cormen et al. (2022): digitos, base 10, modulo 13."""

    def setUp(self):
        self.r = buscar_con_estadisticas("2359023141526739921", "31415",
                                         base=10, primo=13, valor=int)

    def test_ocurrencia_valida(self):
        self.assertEqual(self.r["posiciones"], [6])

    def test_colision_detectada_y_descartada(self):
        # "67399" mod 13 = 7, igual que "31415": colision en la posicion 12
        self.assertEqual(self.r["colisiones"], [12])

    def test_estadisticas(self):
        self.assertEqual(self.r["hash_patron"], 7)
        self.assertEqual(self.r["ventanas"], 15)
        # 5 comparaciones al verificar la ocurrencia + 1 al descartar la colision
        self.assertEqual(self.r["comparaciones"], 6)


class TestBuscar(unittest.TestCase):
    def test_varias_ocurrencias(self):
        self.assertEqual(buscar("AI in education: AI tools and AI ethics", "AI"), [0, 17, 30])

    def test_ocurrencias_solapadas(self):
        self.assertEqual(buscar("aaaa", "aa"), [0, 1, 2])
        self.assertEqual(buscar("abababa", "aba"), [0, 2, 4])

    def test_casos_borde(self):
        self.assertEqual(buscar("generative models", "transformer"), [])
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
        with self.assertRaises(ValueError):
            buscar("texto", "t", base=1)
        with self.assertRaises(ValueError):
            buscar("texto", "t", primo=1)

    def test_coincide_con_la_busqueda_ingenua(self):
        generador = random.Random(103)
        for _ in range(200):
            texto = "".join(generador.choice("abc") for _ in range(generador.randint(0, 60)))
            patron = "".join(generador.choice("abc") for _ in range(generador.randint(1, 5)))
            self.assertEqual(buscar(texto, patron), busqueda_ingenua(texto, patron))

    def test_con_modulo_pequeno_hay_colisiones_pero_el_resultado_es_correcto(self):
        """La verificacion caracter a caracter descarta todas las colisiones."""
        generador = random.Random(107)
        total_colisiones = 0
        for _ in range(100):
            texto = "".join(generador.choice("abcd") for _ in range(generador.randint(10, 80)))
            patron = "".join(generador.choice("abcd") for _ in range(generador.randint(2, 4)))
            r = buscar_con_estadisticas(texto, patron, primo=3)
            total_colisiones += len(r["colisiones"])
            self.assertEqual(r["posiciones"], busqueda_ingenua(texto, patron))
            for s in r["colisiones"]:
                self.assertNotEqual(texto[s:s + len(patron)], patron)
        self.assertGreater(total_colisiones, 0)

    def test_colisiones_y_ocurrencias_son_todas_las_ventanas_con_hash_igual(self):
        texto, patron, primo = "abcabdabcab", "ab", 7
        r = buscar_con_estadisticas(texto, patron, primo=primo)
        p = hash_polinomial(patron, 256, primo)
        esperadas = [s for s in range(len(texto) - 1)
                     if hash_polinomial(texto[s:s + 2], 256, primo) == p]
        self.assertEqual(sorted(r["posiciones"] + r["colisiones"]), esperadas)


if __name__ == "__main__":
    unittest.main()
