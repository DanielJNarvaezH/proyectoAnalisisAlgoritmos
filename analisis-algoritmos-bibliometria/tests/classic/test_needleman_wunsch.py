"""
Pruebas unitarias para src/classic/needleman_wunsch.py
Ejecutar con:  python -m unittest tests/classic/test_needleman_wunsch.py -v
"""
import unittest
import sys
import os

# Permite ejecutar el archivo directamente sin instalar el proyecto como paquete
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from classic.needleman_wunsch import (
    build_score_matrix,
    traceback,
    needleman_wunsch_score,
    needleman_wunsch_alignment,
    needleman_wunsch_similarity,
    similarity_matrix,
    GAP,
)


class TestScoreMatrix(unittest.TestCase):

    def test_dimensiones_matriz(self):
        a, b = "abc", "de"
        S = build_score_matrix(a, b)
        self.assertEqual(len(S), len(a) + 1)
        self.assertEqual(len(S[0]), len(b) + 1)

    def test_primera_fila_y_columna(self):
        # S[i][0] = i * gap   y   S[0][j] = j * gap
        a, b = "abc", "de"
        gap = -2
        S = build_score_matrix(a, b, gap=gap)
        for i in range(len(a) + 1):
            self.assertEqual(S[i][0], i * gap)
        for j in range(len(b) + 1):
            self.assertEqual(S[0][j], j * gap)

    def test_secuencias_identicas_score_maximo(self):
        # Si A == B, el alineamiento óptimo es todo coincidencias:
        # score = len(A) * match
        a = ["gato", "come", "pescado"]
        S = build_score_matrix(a, a, match=1, mismatch=-1, gap=-2)
        self.assertEqual(S[len(a)][len(a)], len(a) * 1)


class TestNeedlemanWunschScore(unittest.TestCase):

    def test_secuencias_identicas(self):
        a = "gato"
        score = needleman_wunsch_score(a, a, match=1, mismatch=-1, gap=-2)
        self.assertEqual(score, len(a) * 1)

    def test_secuencia_vacia(self):
        # Alinear "" contra una secuencia de largo m son m gaps
        score = needleman_wunsch_score("", "casa", match=1, mismatch=-1, gap=-2)
        self.assertEqual(score, 4 * -2)

    def test_calculo_manual_simple(self):
        # "AG" vs "AC": 1 coincidencia (A) + 1 mismatch (G/C) = 1 - 1 = 0
        # (mejor que alinear con gaps: -2 + -2 = -4, o mixto -2 + 1 = -1)
        score = needleman_wunsch_score("AG", "AC", match=1, mismatch=-1, gap=-2)
        self.assertEqual(score, 0)

    def test_simetria(self):
        a, b = "algoritmo", "logaritmo"
        score_ab = needleman_wunsch_score(a, b)
        score_ba = needleman_wunsch_score(b, a)
        self.assertEqual(score_ab, score_ba)


class TestTraceback(unittest.TestCase):

    def test_alineamiento_secuencias_identicas(self):
        # Si A == B, el alineamiento no debe tener ningún gap
        a = ["gato", "come", "pescado"]
        alineado_a, alineado_b, score = needleman_wunsch_alignment(a, a)
        self.assertNotIn(GAP, alineado_a)
        self.assertNotIn(GAP, alineado_b)
        self.assertEqual(alineado_a, alineado_b)

    def test_longitud_alineamiento_igual_en_ambas_secuencias(self):
        # alineado_a y alineado_b siempre deben quedar de la misma longitud
        a = ["el", "gato", "come", "pescado"]
        b = ["el", "perro", "come", "pescado", "fresco"]
        alineado_a, alineado_b, _ = needleman_wunsch_alignment(a, b)
        self.assertEqual(len(alineado_a), len(alineado_b))

    def test_alineamiento_sin_gaps_reconstruye_longitud_correcta(self):
        # La longitud del alineamiento nunca debe ser menor que la secuencia
        # más larga de las dos entradas (los gaps solo pueden alargarlo)
        a, b = "kitten", "sitting"
        alineado_a, alineado_b, _ = needleman_wunsch_alignment(a, b)
        self.assertGreaterEqual(len(alineado_a), max(len(a), len(b)))

    def test_secuencia_vacia_produce_solo_gaps(self):
        alineado_a, alineado_b, _ = needleman_wunsch_alignment("", "casa")
        self.assertEqual(alineado_a, [GAP, GAP, GAP, GAP])
        self.assertEqual(alineado_b, list("casa"))

    def test_score_del_alineamiento_coincide_con_matriz(self):
        # El score retornado por needleman_wunsch_alignment debe ser igual
        # a S[n][m] calculado por build_score_matrix
        a, b = "universidad", "universo"
        _, _, score_alineamiento = needleman_wunsch_alignment(a, b)
        S = build_score_matrix(a, b)
        self.assertEqual(score_alineamiento, S[len(a)][len(b)])


class TestNeedlemanWunschSimilarity(unittest.TestCase):

    def test_similitud_identicas_es_uno(self):
        self.assertEqual(needleman_wunsch_similarity("hola", "hola"), 1.0)

    def test_similitud_vacias_es_uno(self):
        self.assertEqual(needleman_wunsch_similarity("", ""), 1.0)

    def test_similitud_en_rango_valido(self):
        sim = needleman_wunsch_similarity("universidad", "universo")
        self.assertGreaterEqual(sim, 0.0)
        self.assertLessEqual(sim, 1.0)

    def test_similitud_totalmente_distintas_es_baja(self):
        # Secuencias sin ningún elemento en común: similitud debe ser 0
        sim = needleman_wunsch_similarity(["a", "b"], ["x", "y", "z"])
        self.assertEqual(sim, 0.0)


class TestSimilarityMatrix(unittest.TestCase):

    def test_diagonal_es_uno(self):
        corpus = [["a", "b"], ["c", "d"], ["a", "b", "c"]]
        matriz = similarity_matrix(corpus)
        for i in range(len(corpus)):
            self.assertEqual(matriz[i][i], 1.0)

    def test_matriz_simetrica(self):
        corpus = [["a", "b"], ["c", "d"], ["a", "b", "c"]]
        matriz = similarity_matrix(corpus)
        n = len(corpus)
        for i in range(n):
            for j in range(n):
                self.assertAlmostEqual(matriz[i][j], matriz[j][i])

    def test_tamano_matriz(self):
        corpus = [["a"], ["b"], ["c"], ["d"]]
        matriz = similarity_matrix(corpus)
        self.assertEqual(len(matriz), 4)
        self.assertEqual(len(matriz[0]), 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
