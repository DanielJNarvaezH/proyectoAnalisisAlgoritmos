"""
Bucket Sort (tarea ORD-4, seguimiento)
======================================

Ordenamiento por cubetas, implementado desde cero segun:

  - Cormen, T. H., Leiserson, C. E., Rivest, R. L. y Stein, C. (2022).
    Introduction to Algorithms (4.a ed.). MIT Press. Seccion 8.4, "Bucket
    sort" (procedimiento BUCKET-SORT).
  - Isaac, E. J. y Singleton, R. C. (1956). Sorting by address calculation.
    Journal of the ACM, 3(3), 169-174 (origen de la idea, citado en las notas
    del capitulo 8 de Cormen et al.).

Idea: repartir los elementos en m cubetas segun el rango de su clave, ordenar
cada cubeta por separado y concatenar las cubetas en orden. Como cada cubeta
cubre un rango de claves menor que el de la siguiente, la concatenacion queda
ordenada sin comparar elementos de cubetas distintas.

  1. Distribucion: con claves enteras en 0..k y m cubetas de ancho
     w = ceil((k + 1) / m), la clave v va a la cubeta  v // w.
  2. Ordenamiento interno: cada cubeta i contiene claves en el rango
     [i*w, i*w + w - 1], asi que se ordena con COUNTING SORT (ORD-2) usando
     la clave local v - i*w, que esta en 0..w-1.
  3. Concatenacion: se recorren las cubetas de la 0 a la m - 1.

Diferencia con Cormen et al.: el libro ordena cada cubeta con Insertion Sort,
que SI compara elementos. Aqui se usa Counting Sort, de modo que el algoritmo
completo no hace comparaciones entre elementos, como pide el seguimiento.
Ademas, como agregar a una cubeta conserva el orden de llegada y Counting
Sort es estable, Bucket Sort tambien es ESTABLE: produce exactamente el mismo
ranking que Counting Sort y Radix Sort.

Complejidad: la distribucion es O(n); la cubeta i con n_i elementos se ordena
en O(n_i + w); la concatenacion es O(n). En total:
    O(n + m*w) = O(n + k + m)   (porque m*w < k + 1 + m)
y como m <= k + 1, el tiempo es O(n + k), igual que Counting Sort, en el peor
caso. La memoria es O(n + m + w).

Eleccion de m: se usa m = ceil(sqrt(k + 1)), que equilibra la cantidad de
cubetas (m) con el tamano del arreglo de conteo dentro de cada una (w). Con el
corpus actual, k = 86: m = 10 cubetas de ancho w = 9.

Sobre la distribucion de los datos: el analisis clasico de Bucket Sort
(Cormen et al., 2022, sec. 8.4) supone claves repartidas de forma uniforme.
Las frecuencias de palabras no lo estan: siguen aproximadamente la ley de
Zipf (Manning, Raghavan y Schutze, 2008, Introduction to Information
Retrieval, sec. 5.1.2), y la mayoria de terminos tiene frecuencia 1 o 2.
Por eso casi todos los terminos caen en una sola cubeta. Al ordenar cada
cubeta con Counting Sort, esa concentracion no empeora la complejidad (seria
O(n^2) en el peor caso con Insertion Sort), pero si limita el beneficio de
repartir el trabajo: este modulo reporta la ocupacion de cada cubeta para
mostrarlo.

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\ordenamiento\\bucket_sort.py
"""

import math
import os
import sys

RAIZ_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ_SRC not in sys.path:
    sys.path.insert(0, RAIZ_SRC)

from ordenamiento.counting_sort import counting_sort, frecuencia_maxima  # noqa: E402
from ordenamiento.frecuencias import obtener_lista_frecuencias  # noqa: E402

TOP = 15


def _validar_clave(valor, k):
    if not isinstance(valor, int) or isinstance(valor, bool):
        raise TypeError(f"Bucket Sort requiere claves enteras, se recibio {valor!r}")
    if valor < 0 or valor > k:
        raise ValueError(f"La clave {valor} esta fuera del rango 0..{k}")


def parametros_cubetas(k, num_cubetas=None):
    """
    Retorna (m, w): cantidad de cubetas y ancho de cada una para claves 0..k.
    Por defecto m = ceil(sqrt(k + 1)). m se limita a k + 1 (mas cubetas no
    tendrian claves que recibir).
    """
    if not isinstance(k, int) or k < 0:
        raise ValueError("k debe ser un entero no negativo")
    rango = k + 1
    if num_cubetas is None:
        m = math.isqrt(rango)
        if m * m < rango:
            m += 1  # ceil(sqrt(k + 1)) con aritmetica entera
    else:
        if not isinstance(num_cubetas, int) or num_cubetas < 1:
            raise ValueError("num_cubetas debe ser un entero positivo")
        m = num_cubetas if num_cubetas <= rango else rango
    w = (rango + m - 1) // m  # ceil((k + 1) / m)
    return m, w


def distribuir(elementos, clave, k, num_cubetas=None):
    """
    Paso 1: reparte los elementos en cubetas por rango de clave.
    Retorna (cubetas, w), donde cubetas[i] contiene, en orden de llegada,
    los elementos con clave en [i*w, i*w + w - 1].
    """
    m, w = parametros_cubetas(k, num_cubetas)
    cubetas = [[] for _ in range(m)]
    for elemento in elementos:
        valor = clave(elemento)
        _validar_clave(valor, k)
        cubetas[valor // w].append(elemento)
    return cubetas, w


def bucket_sort(elementos, clave, k, num_cubetas=None):
    """
    Bucket Sort estable y ascendente (no modifica la entrada).

    clave(elemento) debe ser un entero entre 0 y k. Cada cubeta se ordena con
    Counting Sort sobre la clave local (clave - inicio de la cubeta).
    """
    cubetas, w = distribuir(elementos, clave, k, num_cubetas)
    salida = []
    for i in range(len(cubetas)):
        if not cubetas[i]:
            continue
        inicio = i * w
        ordenada = counting_sort(cubetas[i], lambda e, base=inicio: clave(e) - base, w - 1)
        salida.extend(ordenada)
    return salida


def ordenar_por_frecuencia(pares, num_cubetas=None):
    """
    Ranking de terminos: pares (termino, frecuencia) de mayor a menor
    frecuencia, estable. Usa la clave transformada k - frecuencia, igual que
    Counting Sort (ORD-2).
    """
    if not pares:
        return []
    k = frecuencia_maxima(pares)
    return bucket_sort(pares, lambda par: k - par[1], k, num_cubetas)


def ocupacion_cubetas(pares, num_cubetas=None):
    """
    Para el reporte: lista de (frecuencia_min, frecuencia_max, cantidad) por
    cubeta, en el orden en que se concatenan (de mayor a menor frecuencia).
    """
    k = frecuencia_maxima(pares)
    cubetas, w = distribuir(pares, lambda par: k - par[1], k, num_cubetas)
    resultado = []
    for i in range(len(cubetas)):
        clave_min, clave_max = i * w, min(i * w + w - 1, k)
        # clave = k - frecuencia  ->  frecuencia = k - clave
        resultado.append((k - clave_max, k - clave_min, len(cubetas[i])))
    return resultado


def main():
    pares = obtener_lista_frecuencias()
    k = frecuencia_maxima(pares)
    m, w = parametros_cubetas(k)
    ranking = ordenar_por_frecuencia(pares)

    print("=== [ORD-4] BUCKET SORT: RANKING DE TERMINOS ===")
    print(f"n = {len(pares)} terminos | k = {k} | m = {m} cubetas de ancho w = {w}")
    print(f"Complejidad O(n + k) = O({len(pares)} + {k})\n")

    print("Ocupacion de las cubetas (en orden de concatenacion):")
    ocupacion = ocupacion_cubetas(pares)
    mayor = 1
    for _, _, cantidad in ocupacion:
        if cantidad > mayor:
            mayor = cantidad
    for frecuencia_min, frecuencia_max, cantidad in ocupacion:
        barra = "#" * ((50 * cantidad + mayor - 1) // mayor)  # barra proporcional, max. 50
        porcentaje = 100 * cantidad / len(pares)
        print(f"  frecuencias {frecuencia_min:>2}-{frecuencia_max:<2}: {cantidad:>4} terminos "
              f"({porcentaje:5.1f} %) {barra}")

    print(f"\nTop {TOP}:")
    for posicion, (termino, frecuencia) in enumerate(ranking[:TOP], start=1):
        print(f"  {posicion:>2}. {termino:15} {frecuencia}")


if __name__ == "__main__":
    main()
