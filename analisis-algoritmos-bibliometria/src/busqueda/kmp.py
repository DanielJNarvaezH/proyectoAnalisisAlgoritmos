"""
Algoritmo de Knuth-Morris-Pratt (tarea BUS-1, Requerimiento 3)
===============================================================

Busqueda de todas las ocurrencias exactas de un patron en un texto,
implementada desde cero (sin find(), index(), in ni expresiones regulares)
segun:

  - Knuth, D. E., Morris, J. H. y Pratt, V. R. (1977). Fast pattern matching
    in strings. SIAM Journal on Computing, 6(2), 323-350.
  - Cormen, T. H., Leiserson, C. E., Rivest, R. L. y Stein, C. (2022).
    Introduction to Algorithms (4.a ed.). MIT Press. Seccion 32.4
    (procedimientos COMPUTE-PREFIX-FUNCTION y KMP-MATCHER).

Idea: el algoritmo ingenuo, cuando falla una comparacion, retrocede en el
texto y vuelve a empezar una posicion mas adelante, repitiendo comparaciones
que ya hizo. KMP nunca retrocede en el texto: cuando falla, usa lo que ya
sabe del patron para decidir cuanto del patron sigue coincidiendo.

1. Preprocesamiento: tabla de prefijos (funcion de fallo) pi del patron P,
   de longitud m. Para cada posicion q (desde 0):

       pi[q] = longitud del prefijo propio mas largo de P[0..q] que tambien
               es sufijo de P[0..q]

   Ejemplo (Cormen et al., 2022, fig. 32.10): P = "ababaca" ->
   pi = [0, 0, 1, 2, 3, 0, 1]. En la posicion 4 ("ababa"), el prefijo "aba"
   tambien es sufijo, asi que pi[4] = 3.

2. Busqueda: se recorre el texto una sola vez, manteniendo q = cantidad de
   caracteres del patron que coinciden hasta ahora. Si el siguiente caracter
   no coincide, q retrocede a pi[q - 1] (el patron se "desliza" sin volver
   atras en el texto). Si q llega a m, hay una ocurrencia.

Complejidad (Cormen et al., 2022, sec. 32.4, por analisis amortizado):
  - Preprocesamiento: O(m).
  - Busqueda: O(n), con a lo sumo 2n comparaciones de caracteres, porque
    cada comparacion o avanza en el texto o hace retroceder a q, y q no puede
    retroceder mas veces de las que avanzo.
  - Total: O(n + m), sin importar el contenido del texto ni del patron.
  - Memoria adicional: O(m) para la tabla de prefijos.

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\busqueda\\kmp.py "learning"
"""

import json
import os
import sys

RAIZ_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUTA_CORPUS = os.path.join(RAIZ_PROYECTO, "data", "corpus_preprocesado.json")


def _validar(texto, patron):
    if not isinstance(texto, str) or not isinstance(patron, str):
        raise TypeError("El texto y el patron deben ser cadenas")
    if len(patron) == 0:
        raise ValueError("El patron no puede estar vacio")


# ---------------------------------------------------------------------------
# 1. Preprocesamiento: tabla de prefijos (funcion de fallo)
# ---------------------------------------------------------------------------

def tabla_prefijos(patron):
    """
    Tabla de prefijos pi del patron (COMPUTE-PREFIX-FUNCTION, indices desde 0).
    pi[q] = longitud del prefijo propio mas largo de patron[0..q] que tambien
    es sufijo de patron[0..q].
    """
    if len(patron) == 0:
        raise ValueError("El patron no puede estar vacio")
    m = len(patron)
    pi = [0] * m
    k = 0  # longitud del prefijo que coincide hasta ahora
    for q in range(1, m):
        while k > 0 and patron[k] != patron[q]:
            k = pi[k - 1]
        if patron[k] == patron[q]:
            k += 1
        pi[q] = k
    return pi


# ---------------------------------------------------------------------------
# 2. Busqueda
# ---------------------------------------------------------------------------

def buscar_con_estadisticas(texto, patron):
    """
    Busqueda KMP con estadisticas para el analisis (BUS-5, CAS-5).

    Retorna un diccionario con:
      - posiciones: indices (desde 0) donde empieza cada ocurrencia, en orden;
        incluye ocurrencias que se solapan
      - comparaciones: comparaciones de caracteres entre texto y patron
      - tabla_prefijos: la tabla pi usada
    """
    _validar(texto, patron)
    pi = tabla_prefijos(patron)
    n, m = len(texto), len(patron)

    posiciones = []
    comparaciones = 0
    q = 0  # caracteres del patron que coinciden hasta ahora
    for i in range(n):
        # Mientras el siguiente caracter no coincida, deslizar el patron
        while q > 0:
            comparaciones += 1
            if patron[q] == texto[i]:
                break
            q = pi[q - 1]
        else:
            # q == 0: se compara contra el primer caracter del patron
            comparaciones += 1
            if patron[0] != texto[i]:
                continue
        q += 1
        if q == m:
            posiciones.append(i - m + 1)
            q = pi[q - 1]  # seguir buscando (permite ocurrencias solapadas)

    return {"posiciones": posiciones, "comparaciones": comparaciones, "tabla_prefijos": pi}


def buscar(texto, patron):
    """Posiciones (desde 0) de todas las ocurrencias de patron en texto."""
    return buscar_con_estadisticas(texto, patron)["posiciones"]


# ---------------------------------------------------------------------------
# 3. Demostracion sobre los abstracts del corpus
# ---------------------------------------------------------------------------

def main():
    patron = sys.argv[1] if len(sys.argv) > 1 else "learning"
    print("=== [BUS-1] KNUTH-MORRIS-PRATT ===")
    print(f"Patron: {patron!r} (m = {len(patron)})")
    print(f"Tabla de prefijos: {tabla_prefijos(patron)}\n")

    with open(RUTA_CORPUS, "r", encoding="utf-8") as archivo:
        corpus = json.load(archivo)

    total, comparaciones, caracteres = 0, 0, 0
    print("Ocurrencias en el abstract original (distingue mayusculas):")
    for articulo in corpus:
        resultado = buscar_con_estadisticas(articulo["abstract"], patron)
        total += len(resultado["posiciones"])
        comparaciones += resultado["comparaciones"]
        caracteres += len(articulo["abstract"])
        if resultado["posiciones"]:
            print(f"  Art. {articulo['numero']:>2}: {len(resultado['posiciones'])} "
                  f"en {resultado['posiciones']}")
    print(f"\nTotal: {total} ocurrencias en {len(corpus)} abstracts")
    print(f"Comparaciones: {comparaciones} para {caracteres} caracteres de texto "
          f"({comparaciones / caracteres:.2f} por caracter; la cota teorica es 2)")


if __name__ == "__main__":
    main()
