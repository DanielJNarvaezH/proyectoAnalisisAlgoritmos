import os
import sys
import json

##

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
    Regla del sufijo bueno: Calcula los desplazamientos basados en sufijos que coinciden.
    Retorna una lista 'desplazamientos' de tamaño m + 1.
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
    Búsqueda Boyer-Moore con estadísticas para el análisis (BUS-2, CAS-2).

    Retorna un diccionario con:
      - posiciones: índices donde empieza cada ocurrencia.
      - comparaciones: comparaciones de caracteres realizadas (desde el final).
      - saltos_caracter_malo: veces que se usó la regla del carácter malo.
      - saltos_sufijo_bueno: veces que se usó la regla del sufijo bueno.
    """
    _validar(texto, patron)
    n, m = len(texto), len(patron)

    resultado = {
        "posiciones": [],
        "comparaciones": 0,
        "saltos_caracter_malo": 0,
        "saltos_sufijo_bueno": 0
    }

    if m > n:
        return resultado

    # Preprocesamiento explícito de tablas
    tabla_malo = construir_caracter_malo(patron)
    tabla_bueno = construir_sufijo_bueno(patron)

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