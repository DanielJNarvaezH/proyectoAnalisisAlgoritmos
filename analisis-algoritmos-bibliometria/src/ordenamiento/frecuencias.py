"""
Lista de frecuencias de terminos del corpus (tarea ORD-1, seguimiento)
======================================================================

Cuenta cuantas veces aparece cada termino en el campo `abstract_preprocesado`
de los 20 articulos y produce la lista de pares (termino, frecuencia) que
ordenan los tres algoritmos del seguimiento (Counting Sort, Radix Sort y
Bucket Sort).

Fuente del concepto: la frecuencia de un termino es el numero de veces que
aparece en un texto, segun la definicion de "term frequency" de
  - Manning, C. D., Raghavan, P. y Schutze, H. (2008). Introduction to
    Information Retrieval. Cambridge University Press. Seccion 6.2, "Term
    frequency and weighting".
Aqui se calcula sobre el corpus completo (la suma de las frecuencias del
termino en los 20 abstracts), que es la lista que pide el seguimiento.

Este modulo SOLO cuenta; no ordena. El ordenamiento por frecuencia es
justamente lo que deben hacer los algoritmos sin comparaciones, asi que
aqui no se usa sorted() ni ninguna otra funcion de ordenamiento.

Criterio de desempate: la lista se entrega en el ORDEN DE PRIMERA APARICION
de cada termino en el corpus (articulo 1 a 20, token por token). Como los
tres algoritmos son estables (conservan el orden relativo de los elementos
con la misma clave), dos terminos con la misma frecuencia quedan en el
ranking en el orden en que aparecieron por primera vez. Asi los tres
algoritmos producen exactamente el mismo resultado, lo que permite validar
uno contra otro.

El conteo usa un diccionario de Python, que conserva el orden de insercion
(garantizado por el lenguaje desde Python 3.7; ver la documentacion oficial
de Python, "Mapping Types - dict").

Complejidad: O(T), con T el total de tokens del corpus (unos 2.500).

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\ordenamiento\\frecuencias.py
"""

import json
import os

RAIZ_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUTA_CORPUS = os.path.join(RAIZ_PROYECTO, "data", "corpus_preprocesado.json")


def cargar_corpus(ruta=RUTA_CORPUS):
    """
    Corpus preprocesado en el orden del archivo, que es el de los numeros de
    articulo (1 a 20, tal como lo genera preprocessing.py).
    """
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontro el corpus en {ruta}")
    with open(ruta, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def contar_frecuencias(corpus):
    """
    Lista de pares (termino, frecuencia) en orden de primera aparicion.
    `corpus` es una lista de articulos con el campo `abstract_preprocesado`.
    """
    conteo = {}
    for articulo in corpus:
        for termino in articulo["abstract_preprocesado"]:
            if termino in conteo:
                conteo[termino] += 1
            else:
                conteo[termino] = 1
    return [(termino, frecuencia) for termino, frecuencia in conteo.items()]


def obtener_lista_frecuencias(ruta=RUTA_CORPUS):
    """Lista de frecuencias del corpus completo, lista para ordenar."""
    return contar_frecuencias(cargar_corpus(ruta))


def main():
    pares = obtener_lista_frecuencias()
    total_tokens = 0
    maxima = 0
    for _, frecuencia in pares:
        total_tokens += frecuencia
        if frecuencia > maxima:
            maxima = frecuencia

    print("=== [ORD-1] LISTA DE FRECUENCIAS DEL CORPUS ===")
    print(f"Tokens totales:            {total_tokens}")
    print(f"Terminos distintos (n):    {len(pares)}")
    print(f"Frecuencia maxima (k):     {maxima}")
    print("\nPrimeros 10 terminos en orden de primera aparicion (sin ordenar):")
    for termino, frecuencia in pares[:10]:
        print(f"  {termino}: {frecuencia}")


if __name__ == "__main__":
    main()
