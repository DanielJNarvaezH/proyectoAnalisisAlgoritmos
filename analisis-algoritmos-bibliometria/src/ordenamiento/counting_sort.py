"""
Counting Sort (tarea ORD-2, seguimiento)
========================================

Ordenamiento por conteo, implementado desde cero segun:

  - Cormen, T. H., Leiserson, C. E., Rivest, R. L. y Stein, C. (2022).
    Introduction to Algorithms (4.a ed.). MIT Press. Seccion 8.2, "Counting
    sort" (procedimiento COUNTING-SORT).
  - Knuth, D. E. (1998). The Art of Computer Programming, Vol. 3: Sorting and
    Searching (2.a ed.). Addison-Wesley. Seccion 5.2 ("distribution counting").
  Ambos atribuyen la idea original a H. H. Seward (1954).

Idea: si las claves son enteros en el rango 0..k, no hace falta comparar
elementos entre si. Basta con:
  1. Contar cuantos elementos tienen cada clave:        conteo[v]
  2. Acumular los conteos:  conteo[v] = cantidad de elementos con clave <= v,
     que es la posicion final del ultimo elemento con clave v.
  3. Recorrer la entrada DE ATRAS HACIA ADELANTE y colocar cada elemento en
     la posicion conteo[clave] - 1, decrementando conteo[clave].

El recorrido inverso del paso 3 hace al algoritmo ESTABLE: entre elementos
con la misma clave, el que aparece despues en la entrada se coloca primero
en la ultima posicion disponible, asi que conservan su orden relativo.

Complejidad: el paso 1 recorre los n elementos, el paso 2 recorre las k + 1
claves y el paso 3 recorre otra vez los n elementos: O(n + k) en tiempo y
O(n + k) en memoria (arreglo de conteos y arreglo de salida). Ninguno de los
pasos compara dos elementos entre si, por eso no esta sujeto a la cota
inferior Omega(n log n) de los ordenamientos por comparacion (Cormen et al.,
2022, sec. 8.1). Si k = O(n), el tiempo es O(n).

Aplicacion al seguimiento: los elementos son pares (termino, frecuencia) y
la clave es la frecuencia. Para ordenar de MAYOR a MENOR sin perder la
estabilidad se usa la clave transformada k - frecuencia: la frecuencia mas
alta se convierte en la clave 0 y queda al principio. Con el corpus actual,
n = 868 terminos y k = 86 (frecuencia maxima, del termino "ai").

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\ordenamiento\\counting_sort.py
"""

import os
import sys

RAIZ_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ_SRC not in sys.path:
    sys.path.insert(0, RAIZ_SRC)

from ordenamiento.frecuencias import obtener_lista_frecuencias  # noqa: E402

TOP = 15


def _validar_clave(valor, k):
    if not isinstance(valor, int) or isinstance(valor, bool):
        raise TypeError(f"Counting Sort requiere claves enteras, se recibio {valor!r}")
    if valor < 0 or valor > k:
        raise ValueError(f"La clave {valor} esta fuera del rango 0..{k}")


def counting_sort(elementos, clave, k):
    """
    Counting Sort estable y ascendente.

    Parametros
    ----------
    elementos : list
        Elementos a ordenar (no se modifica).
    clave : funcion
        clave(elemento) -> entero entre 0 y k.
    k : int
        Clave maxima posible.

    Retorna una lista nueva con los elementos ordenados por clave ascendente;
    los elementos con la misma clave conservan su orden de entrada.

    Es generica para que Radix Sort (ORD-3) pueda usarla en cada digito.
    """
    if not isinstance(k, int) or k < 0:
        raise ValueError("k debe ser un entero no negativo")
    n = len(elementos)

    # Paso 1: contar cuantos elementos tienen cada clave
    conteo = [0] * (k + 1)
    claves = [0] * n
    for i in range(n):
        valor = clave(elementos[i])
        _validar_clave(valor, k)
        claves[i] = valor
        conteo[valor] += 1

    # Paso 2: acumular -> conteo[v] = cantidad de elementos con clave <= v
    for v in range(1, k + 1):
        conteo[v] += conteo[v - 1]

    # Paso 3: colocar de atras hacia adelante (garantiza la estabilidad)
    salida = [None] * n
    for i in range(n - 1, -1, -1):
        conteo[claves[i]] -= 1
        salida[conteo[claves[i]]] = elementos[i]
    return salida


def frecuencia_maxima(pares):
    """k = mayor frecuencia de la lista (un recorrido lineal, O(n))."""
    maxima = 0
    for _, frecuencia in pares:
        if frecuencia > maxima:
            maxima = frecuencia
    return maxima


def ordenar_por_frecuencia(pares):
    """
    Ranking de terminos: pares (termino, frecuencia) de mayor a menor
    frecuencia, estable (los empates conservan el orden de entrada).
    Usa la clave transformada k - frecuencia sobre counting_sort.
    """
    if not pares:
        return []
    k = frecuencia_maxima(pares)
    return counting_sort(pares, lambda par: k - par[1], k)


def main():
    pares = obtener_lista_frecuencias()
    k = frecuencia_maxima(pares)
    ranking = ordenar_por_frecuencia(pares)

    print("=== [ORD-2] COUNTING SORT: RANKING DE TERMINOS ===")
    print(f"n = {len(pares)} terminos | k = {k} (frecuencia maxima)")
    print(f"Complejidad O(n + k) = O({len(pares)} + {k})\n")
    print(f"Top {TOP}:")
    for posicion, (termino, frecuencia) in enumerate(ranking[:TOP], start=1):
        print(f"  {posicion:>2}. {termino:15} {frecuencia}")


if __name__ == "__main__":
    main()
