"""
Algoritmo de Boyer-Moore (tarea BUS-2, Requerimiento 3)
=======================================================

Busqueda de todas las ocurrencias exactas de un patron en un texto,
implementada desde cero (sin find(), index(), in ni expresiones regulares)
segun:

  - Boyer, R. S. y Moore, J. S. (1977). A fast string searching algorithm.
    Communications of the ACM, 20(10), 762-772.
  - Gusfield, D. (1997). Algorithms on Strings, Trees, and Sequences.
    Cambridge University Press. Seccion 2.2 (regla del caracter malo y regla
    fuerte del sufijo bueno).

Idea: el patron se alinea con el texto y se compara DE DERECHA A IZQUIERDA.
Cuando hay un desajuste, dos reglas indican cuanto se puede desplazar el
patron sin saltarse ninguna ocurrencia, y se usa el mayor de los dos saltos.

1. Regla del caracter malo. Si el desajuste ocurre en la posicion j del
   patron con el caracter c del texto, se alinea c con su aparicion mas a la
   derecha en el patron. La tabla guarda R(c) = ultima posicion de c en el
   patron (-1 si no aparece) y el salto es j - R(c). Si c no esta en el
   patron, el patron salta completo por encima de c.

2. Regla del sufijo bueno. Si los caracteres patron[j+1 .. m-1] ya
   coincidieron (el "sufijo bueno") y luego hay un desajuste en j, se desplaza
   el patron hasta la siguiente aparicion de ese sufijo en el patron que NO
   este precedida por el mismo caracter patron[j] (regla fuerte); si no existe,
   hasta el prefijo mas largo del patron que coincida con un final del sufijo.
   La tabla desplazamientos[j + 1] guarda ese salto. Se construye con el
   arreglo f, donde f[i] es la posicion donde empieza el borde (prefijo que
   tambien es sufijo) mas ancho de patron[i .. m-1]:
     - Caso 1: el sufijo vuelve a aparecer en otra parte del patron.
     - Caso 2: solo un prefijo del patron coincide con la cola del sufijo.

   Al encontrar una ocurrencia completa, el patron avanza desplazamientos[0].

Complejidad:
  - Preprocesamiento: O(m + s) para la tabla del caracter malo (s = caracteres
    distintos del patron) y O(m) para la del sufijo bueno.
  - Busqueda: en el mejor caso, cerca de n/m comparaciones, porque el patron
    salta bloques completos del texto; en texto natural tiende a ser
    sublineal. En el peor caso, al reportar TODAS las ocurrencias, puede
    llegar a O(n * m) (por ejemplo, texto "aaaa...a" y patron "aaa").
  - Memoria adicional: O(m + s).

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\busqueda\\boyer_moore.py "learning"
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
# 1. Construcción de Tablas Precomputadas (Explícitas)
# ---------------------------------------------------------------------------

def construir_caracter_malo(patron):
    """
    Regla del carácter malo: R(c) es la posición más a la derecha de 'c' en el patrón.
    Si el carácter no existe en el patrón, se asume -1.
    """
    tabla = {}
    for i, c in enumerate(patron):
        tabla[c] = i
    return tabla


def construir_sufijo_bueno(patron):
    """
    Regla (fuerte) del sufijo bueno: calcula los desplazamientos basados en
    sufijos que coinciden. Retorna una lista 'desplazamientos' de tamaño m + 1:
    desplazamientos[j + 1] es el salto cuando el desajuste ocurre en la
    posición j (con patron[j+1..m-1] ya coincidiendo), y desplazamientos[0]
    es el salto después de una ocurrencia completa.

    f[i] es la posición donde empieza el borde más ancho de patron[i..m-1]
    (un borde es un prefijo que también es sufijo).
    """
    m = len(patron)
    desplazamientos = [0] * (m + 1)
    f = [0] * (m + 1)

    # Caso 1: El sufijo vuelve a aparecer en otra parte del patrón
    i = m
    j = m + 1
    f[i] = j
    while i > 0:
        while j <= m and patron[i - 1] != patron[j - 1]:
            if desplazamientos[j] == 0:
                desplazamientos[j] = j - i
            j = f[j]
        i -= 1
        j -= 1
        f[i] = j

    # Caso 2: Solo un prefijo del patrón coincide con la cola del sufijo
    j = f[0]
    for i in range(m + 1):
        if desplazamientos[i] == 0:
            desplazamientos[i] = j
        if i == j:
            j = f[j]

    return desplazamientos


# ---------------------------------------------------------------------------
# 2. Motor de Búsqueda con Estadísticas
# ---------------------------------------------------------------------------

def buscar_con_estadisticas(texto, patron):
    """
    Búsqueda Boyer-Moore con estadísticas para el análisis (BUS-5, CAS-6).

    Retorna un diccionario con:
      - posiciones: índices donde empieza cada ocurrencia.
      - comparaciones: comparaciones de caracteres realizadas (desde el final).
      - saltos_caracter_malo: veces que se usó la regla del carácter malo.
      - saltos_sufijo_bueno: veces que se usó la regla del sufijo bueno.
      - tabla_caracter_malo: tabla R(c) usada.
      - tabla_sufijo_bueno: tabla de desplazamientos usada.
    """
    _validar(texto, patron)
    n, m = len(texto), len(patron)

    resultado = {
        "posiciones": [],
        "comparaciones": 0,
        "saltos_caracter_malo": 0,
        "saltos_sufijo_bueno": 0,
    }

    # Preprocesamiento explícito de tablas
    tabla_malo = construir_caracter_malo(patron)
    tabla_bueno = construir_sufijo_bueno(patron)
    resultado["tabla_caracter_malo"] = tabla_malo
    resultado["tabla_sufijo_bueno"] = tabla_bueno

    if m > n:
        return resultado

    s = 0  # Desplazamiento del patrón con respecto al texto
    while s <= n - m:
        j = m - 1

        # Boyer-Moore compara de derecha a izquierda
        while j >= 0:
            resultado["comparaciones"] += 1
            if patron[j] != texto[s + j]:
                break
            j -= 1

        if j < 0:
            # ¡Ocurrencia encontrada!
            resultado["posiciones"].append(s)
            # Salto determinado por el sufijo completo
            s += tabla_bueno[0]
        else:
            # Desajuste detectado en la posición 'j'
            caracter_malo = texto[s + j]

            # Calcular saltos individuales de cada regla
            salto_malo = j - tabla_malo.get(caracter_malo, -1)
            salto_bueno = tabla_bueno[j + 1]

            # Se elige el máximo salto para avanzar de manera segura
            if salto_malo >= salto_bueno:
                resultado["saltos_caracter_malo"] += 1
                s += salto_malo
            else:
                resultado["saltos_sufijo_bueno"] += 1
                s += salto_bueno

    return resultado


def buscar(texto, patron):
    """Posiciones (desde 0) de todas las ocurrencias de patron en texto."""
    return buscar_con_estadisticas(texto, patron)["posiciones"]

def main():
    # 1. Configuración de parámetros por consola o por defecto
    patron = sys.argv[1] if len(sys.argv) > 1 else "learning"

    print("=== [BUS-2] BOYER-MOORE ===")
    print(f"Patrón: {patron!r} (m = {len(patron)})")

    # 2. Intentar cargar el archivo corpus_preprocesado.json
    try:
        with open(RUTA_CORPUS, "r", encoding="utf-8") as archivo:
            corpus = json.load(archivo)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo del corpus en la ruta: {RUTA_CORPUS}")
        print("Por favor verifica que la estructura de carpetas sea la correcta.")
        return

    # Métrica acumuladoras para el análisis de rendimiento
    total_ocurrencias = 0
    total_comparaciones = 0
    total_saltos_malo = 0
    total_saltos_bueno = 0

    print("\nOcurrencias en el abstract original (distingue mayúsculas):")

    # 3. Procesamiento del corpus artículo por artículo
    for articulo in corpus:
        r = buscar_con_estadisticas(articulo["abstract"], patron)

        # Acumular estadísticas globales
        total_ocurrencias += len(r["posiciones"])
        total_comparaciones += r["comparaciones"]
        total_saltos_malo += r["saltos_caracter_malo"]
        total_saltos_bueno += r["saltos_sufijo_bueno"]

        # Imprimir resultados del artículo si se encontró algo
        if r["posiciones"]:
            print(f"  Art. {articulo['numero']:>2}: {len(r['posiciones'])} "
                  f"en {r['posiciones']} | Comparaciones en este art: {r['comparaciones']}")

    # 4. Reporte final detallado de rendimiento del algoritmo
    print(f"\n================ RESUMEN DE RENDIMIENTO ================")
    print(f"Total: {total_ocurrencias} ocurrencias encontradas en {len(corpus)} abstracts.")
    print(f"Comparaciones totales de caracteres: {total_comparaciones}")
    print(f"Saltos ejecutados por Carácter Malo: {total_saltos_malo}")
    print(f"Saltos ejecutados por Sufijo Bueno:  {total_saltos_bueno}")
    print(f"========================================================")

if __name__ == "__main__":
    main()