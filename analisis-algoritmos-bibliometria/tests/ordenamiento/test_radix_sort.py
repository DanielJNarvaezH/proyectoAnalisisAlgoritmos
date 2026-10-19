import os
import sys
import unittest

# 1. Encontrar la ruta absoluta de la carpeta 'src'
# Subimos dos niveles desde 'tests/ordenamiento/test_radix_sort.py' hasta la raíz, y apuntamos a 'src'
RAIZ_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CARPETA_SRC = os.path.join(RAIZ_PROYECTO, "src")

# 2. Agregar 'src' al inicio de sys.path para que Python encuentre el paquete 'ordenamiento'
if CARPETA_SRC not in sys.path:
    sys.path.insert(0, CARPETA_SRC)

# 3. Ahora las importaciones funcionarán correctamente sin fallar
from ordenamiento.frecuencias import obtener_lista_frecuencias
from ordenamiento.counting_sort import ordenar_por_frecuencia as ordenar_con_counting
from ordenamiento.radix_sort import ordenar_por_frecuencia_radix as ordenar_con_radix


class TestRadixSortFrecuencias(unittest.TestCase):

    def test_lista_vacia(self):
        """Prueba que el algoritmo maneje correctamente una lista vacía."""
        self.assertEqual(ordenar_con_radix([]), [])

    def test_un_solo_elemento(self):
        """Prueba que un único elemento se mantenga igual."""
        lista = [("inteligencia", 12)]
        self.assertEqual(ordenar_con_radix(lista), [("inteligencia", 12)])

    def test_estabilidad_elementos_duplicados(self):
        """
        Prueba crucial: verifica que ante frecuencias idénticas se respete estrictamente
        el orden de entrada original (Estabilidad).
        """
        # Todos tienen la misma frecuencia (5), el orden correcto debe ser el de aparición
        datos_entrada = [
            ("palabra_A", 5),
            ("palabra_B", 5),
            ("palabra_C", 5)
        ]
        resultado = ordenar_con_radix(datos_entrada)

        # Debe mantenerse exactamente el mismo orden relativo de la entrada
        self.assertEqual(resultado[0][0], "palabra_A")
        self.assertEqual(resultado[1][0], "palabra_B")
        self.assertEqual(resultado[2][0], "palabra_C")

    def test_equivalencia_con_counting_sort(self):
        """
        Prueba de integración con el corpus: Radix Sort y Counting Sort deben
        producir exactamente el mismo ranking (mismos términos en las mismas posiciones).
        """
        # 1. Obtener los datos reales del corpus preprocesado
        pares_corpus = obtener_lista_frecuencias()

        # 2. Ordenar con ambos algoritmos independientes
        ranking_counting = ordenar_con_counting(pares_corpus)
        ranking_radix = ordenar_con_radix(pares_corpus)

        # 3. Comprobar que las longitudes coincidan
        self.assertEqual(len(ranking_counting), len(ranking_radix))

        # 4. Validar elemento por elemento (tanto el string como la frecuencia numérica)
        for i in range(len(ranking_counting)):
            self.assertEqual(
                ranking_counting[i],
                ranking_radix[i],
                msg=f"Discrepancia encontrada en la posición {i}: Counting={ranking_counting[i]} | Radix={ranking_radix[i]}"
            )


if __name__ == "__main__":
    unittest.main()
