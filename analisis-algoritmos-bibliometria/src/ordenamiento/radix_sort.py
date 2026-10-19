import os
import sys

# Asegurar la correcta importación desde la raíz de src
RAIZ_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ_SRC not in sys.path:
    sys.path.insert(0, RAIZ_SRC)

# Importamos la función genérica y las utilidades requeridas
from ordenamiento.frecuencias import obtener_lista_frecuencias
from ordenamiento.counting_sort import counting_sort, frecuencia_maxima

TOP = 15


def radix_sort(elementos, clave, valor_maximo):
    """
    Radix Sort LSD en base 10.
    Ordena la lista de forma estable utilizando la función genérica counting_sort.

    Parámetros
    ----------
    elementos : list
        Lista de pares (termino, frecuencia) a ordenar.
    clave_transformada : función
        Función que calcula el valor numérico entero a evaluar por dígitos (e.g., k - frec).
    valor_maximo : int
        El valor máximo que puede tomar la clave transformada (determina cuántas pasadas dar).
    """
    if not elementos:
        return []

    # Trabajamos sobre una copia para no alterar la lista original si se desea preservar,
    # emulando el comportamiento no-mutante de tu counting_sort.
    resultado = list(elementos)

    # Iteramos dígito por dígito utilizando potencias de 10 (exp = 1, 10, 100...)
    exp = 1
    while valor_maximo / exp > 0:
        # En cada pasada por dígito (LSD), invocamos a tu counting_sort genérico.
        # k siempre es 9 porque los dígitos van estrictamente del 0 al 9 en base 10.
        # La clave extrae únicamente el dígito de la posición actual.
        resultado = counting_sort(
            elementos=resultado,
            clave=lambda x: (clave(x) // exp) % 10,
            k=9
        )
        exp *= 10

    return resultado


def ordenar_por_frecuencia_radix(pares):
    """
    Genera el Ranking de términos utilizando Radix Sort LSD en base 10.
    Aplica la transformación k - frecuencia para mantener el orden de MAYOR a MENOR
    y conservar de manera idéntica la estabilidad del sistema.
    """
    if not pares:
        return []
    k = frecuencia_maxima(pares)

    # La clave transformada es (k - frecuencia) para que el mayor sea 0 y quede arriba.
    # El valor máximo de esta clave transformada también es k.
    return radix_sort(pares, lambda par: k - par[1], k)


def main():
    pares = obtener_lista_frecuencias()
    k = frecuencia_maxima(pares)
    ranking = ordenar_por_frecuencia_radix(pares)

    print("=== [ORD-3] RADIX SORT: RANKING DE TERMINOS (BASE 10) ===")
    print(f"n = {len(pares)} terminos | k = {k} (frecuencia maxima)")
    print("Algoritmo por digitos LSD estable utilizando subrutina Counting Sort.\n")
    print(f"Top {TOP}:")
    for posicion, (termino, frecuencia) in enumerate(ranking[:TOP], start=1):
        print(f"  {posicion:>2}. {termino:15} {frecuencia}")


if __name__ == "__main__":
    main()
