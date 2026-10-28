"""
Radix Sort (tarea ORD-3, seguimiento)
=====================================

Ordenamiento por digitos (LSD, del menos significativo al mas significativo),
implementado desde cero segun:

  - Cormen, T. H., Leiserson, C. E., Rivest, R. L. y Stein, C. (2022).
    Introduction to Algorithms (4.a ed.). MIT Press. Seccion 8.3, "Radix
    sort" (procedimiento RADIX-SORT y Lema 8.3).
  - Knuth, D. E. (1998). The Art of Computer Programming, Vol. 3: Sorting and
    Searching (2.a ed.). Addison-Wesley. Seccion 5.2.5, "Sorting by
    distribution".

Idea: una clave entera de d digitos en base b se ordena con d pasadas. En la
pasada i (i = 0 para las unidades, 1 para las decenas, ...) se ordenan los
elementos SOLO por su i-esimo digito, con un ordenamiento estable. Como cada
pasada es estable, al terminar la pasada i los elementos quedan ordenados por
sus i + 1 digitos menos significativos (Cormen et al., 2022, Lema 8.3, por
induccion sobre i). Despues de la ultima pasada quedan ordenados por la clave
completa.

El ordenamiento estable de cada pasada es Counting Sort (ORD-2) con k = b - 1,
porque un digito en base b toma valores entre 0 y b - 1:

    digito_i(v) = (v // b^i) % b

Complejidad: d pasadas de Counting Sort, cada una O(n + b):
    O(d * (n + b))
Con b = 10 y claves hasta k, d = numero de digitos de k = floor(log10(k)) + 1.
Si d es constante (las frecuencias del corpus tienen a lo sumo 2 digitos) y
b = 10, el tiempo es O(n). Ninguna pasada compara elementos entre si.

Aplicacion al seguimiento: igual que en Counting Sort y Bucket Sort, se ordena
por la clave transformada k - frecuencia para obtener el ranking de mayor a
menor sin perder la estabilidad. Con el corpus actual, k = 86, asi que la
clave tiene d = 2 digitos y bastan 2 pasadas.

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\ordenamiento\\radix_sort.py
"""

import os
import sys

# Asegurar la correcta importacion desde la raiz de src
RAIZ_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ_SRC not in sys.path:
    sys.path.insert(0, RAIZ_SRC)

from ordenamiento.counting_sort import counting_sort, frecuencia_maxima  # noqa: E402
from ordenamiento.frecuencias import obtener_lista_frecuencias  # noqa: E402

TOP = 15
BASE = 10


def cantidad_digitos(valor, base=BASE):
    """Numero de digitos de un entero no negativo en la base dada (0 tiene 1 digito)."""
    if valor < 0:
        raise ValueError("cantidad_digitos requiere un entero no negativo")
    digitos = 1
    while valor >= base:
        valor //= base
        digitos += 1
    return digitos


def digito(valor, posicion, base=BASE):
    """Digito en la posicion dada (0 = unidades) de un entero no negativo."""
    return (valor // base ** posicion) % base


def radix_sort(elementos, clave, valor_maximo, base=BASE):
    """
    Radix Sort LSD estable y ascendente (no modifica la entrada).

    Parametros
    ----------
    elementos : list
        Elementos a ordenar.
    clave : funcion
        clave(elemento) -> entero entre 0 y valor_maximo.
    valor_maximo : int
        Mayor valor posible de la clave; determina cuantas pasadas se hacen.
    base : int
        Base de los digitos (por defecto 10).
    """
    if not isinstance(valor_maximo, int) or valor_maximo < 0:
        raise ValueError("valor_maximo debe ser un entero no negativo")
    if not isinstance(base, int) or base < 2:
        raise ValueError("la base debe ser un entero mayor o igual a 2")
    if not elementos:
        return []

    # Validar las claves una vez: deben ser enteros entre 0 y valor_maximo.
    # Sin esta validacion, una clave negativa produciria digitos validos
    # (en Python, (-3 // 1) % 10 = 7) y se ordenaria mal sin avisar.
    for elemento in elementos:
        valor = clave(elemento)
        if not isinstance(valor, int) or isinstance(valor, bool):
            raise TypeError(f"Radix Sort requiere claves enteras, se recibio {valor!r}")
        if valor < 0 or valor > valor_maximo:
            raise ValueError(f"La clave {valor} esta fuera del rango 0..{valor_maximo}")

    resultado = list(elementos)
    # Una pasada estable de Counting Sort por cada digito, de unidades hacia arriba
    for posicion in range(cantidad_digitos(valor_maximo)):
        resultado = counting_sort(
            resultado,
            lambda e, p=posicion: digito(clave(e), p, base),
            base - 1,
        )
    return resultado


def ordenar_por_frecuencia(pares, k):
    """
    Ranking de terminos: pares (termino, frecuencia) de mayor a menor
    frecuencia, estable. Usa la clave transformada k - frecuencia, igual que
    Counting Sort (ORD-2) y Bucket Sort (ORD-4).
    """
    if not pares:
        return []
    # La clave transformada k - frecuencia tambien esta entre 0 y k
    return radix_sort(pares, lambda par: k - par[1], k)


# Nombre usado en la version inicial (y en su prueba de integracion)
ordenar_por_frecuencia_radix = ordenar_por_frecuencia


def main():
    pares = obtener_lista_frecuencias()
    k = frecuencia_maxima(pares)
    d = cantidad_digitos(k)
    ranking = ordenar_por_frecuencia(pares, k)

    print("=== [ORD-3] RADIX SORT LSD: RANKING DE TERMINOS (BASE 10) ===")
    print(f"n = {len(pares)} terminos | k = {k} | d = {d} digitos -> {d} pasadas de Counting Sort")
    print(f"Complejidad O(d * (n + b)) = O({d} * ({len(pares)} + {BASE}))\n")
    print(f"Top {TOP}:")
    for posicion, (termino, frecuencia) in enumerate(ranking[:TOP], start=1):
        print(f"  {posicion:>2}. {termino:15} {frecuencia}")


if __name__ == "__main__":
    main()
