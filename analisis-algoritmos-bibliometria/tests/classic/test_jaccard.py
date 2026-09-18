"""
Pruebas unitarias para jaccard_manual.py

Ejecutar desde la raíz del proyecto (la carpeta que contiene tanto
jaccard_manual.py como tests/):

    python -m unittest discover -s tests -v
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..",  ".." , "src"))

from classic.jaccard import (
    tokenizar,
    generar_ngramas,
    texto_a_conjunto,
    jaccard,
    matriz_jaccard,
)


class TestTokenizar(unittest.TestCase):

    def test_tokenizar_string(self):
        self.assertEqual(tokenizar("Hola Mundo"), ["hola", "mundo"])

    def test_tokenizar_lista_ya_tokenizada(self):
        self.assertEqual(tokenizar(["Hola", "MUNDO"]), ["hola", "mundo"])


class TestGenerarNgramas(unittest.TestCase):

    def test_unigramas(self):
        tokens = ["a", "b", "c"]
        resultado = generar_ngramas(tokens, n=1)
        self.assertEqual(resultado, [("a",), ("b",), ("c",)])

    def test_bigramas(self):
        tokens = ["a", "b", "c"]
        resultado = generar_ngramas(tokens, n=2)
        self.assertEqual(resultado, [("a", "b"), ("b", "c")])

    def test_n_mayor_que_tokens_retorna_vacio(self):
        tokens = ["a", "b"]
        self.assertEqual(generar_ngramas(tokens, n=5), [])

    def test_n_invalido_lanza_error(self):
        with self.assertRaises(ValueError):
            generar_ngramas(["a", "b"], n=0)


class TestTextoAConjunto(unittest.TestCase):

    def test_conjunto_unigramas(self):
        conjunto = texto_a_conjunto("perro gato perro", n=1)
        self.assertEqual(conjunto, {("perro",), ("gato",)})

    def test_acepta_tokens_ya_preprocesados(self):
        conjunto = texto_a_conjunto(["perro", "gato"], n=1)
        self.assertEqual(conjunto, {("perro",), ("gato",)})


class TestJaccard(unittest.TestCase):

    def test_conjuntos_identicos(self):
        a = {"perro", "gato"}
        self.assertEqual(jaccard(a, a), 1.0)

    def test_conjuntos_disjuntos(self):
        a = {"perro"}
        b = {"gato"}
        self.assertEqual(jaccard(a, b), 0.0)

    def test_ambos_vacios(self):
        self.assertEqual(jaccard(set(), set()), 0.0)

    def test_valor_conocido(self):
        # A = {a,b,c}, B = {b,c,d} -> interseccion={b,c}(2), union={a,b,c,d}(4)
        a = {"a", "b", "c"}
        b = {"b", "c", "d"}
        self.assertAlmostEqual(jaccard(a, b), 2 / 4, places=6)

    def test_acepta_listas_no_solo_sets(self):
        # Debe funcionar aunque no se pase explícitamente un set
        resultado = jaccard(["a", "b"], ["a", "b"])
        self.assertEqual(resultado, 1.0)


class TestMatrizJaccard(unittest.TestCase):

    def test_diagonal_es_uno(self):
        corpus = ["perro gato", "gato pajaro", "perro pajaro"]
        _, matriz = matriz_jaccard(corpus, n=1)
        for i in range(len(matriz)):
            self.assertAlmostEqual(matriz[i][i], 1.0, places=6)

    def test_matriz_es_simetrica(self):
        corpus = ["perro gato", "gato pajaro", "perro pajaro"]
        _, matriz = matriz_jaccard(corpus, n=1)
        n = len(matriz)
        for i in range(n):
            for j in range(n):
                self.assertAlmostEqual(matriz[i][j], matriz[j][i], places=6)

    def test_funciona_con_bigramas(self):
        corpus = ["perro corre rapido", "perro corre lento"]
        _, matriz = matriz_jaccard(corpus, n=2)
        # Comparten el bigrama ("perro", "corre") de 2 bigramas cada uno
        # interseccion=1, union=3 -> 1/3
        self.assertAlmostEqual(matriz[0][1], 1 / 3, places=6)


if __name__ == "__main__":
    unittest.main()