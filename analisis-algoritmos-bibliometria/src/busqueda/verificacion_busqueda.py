"""
Busqueda sobre los 20 abstracts y verificacion cruzada (tarea BUS-4, R3)
=======================================================================

Localiza todas las ocurrencias de un patron en los abstracts del corpus con
los tres algoritmos implementados desde cero (KMP, Rabin-Karp y Boyer-Moore)
y verifica que los tres devuelven exactamente las mismas posiciones.

Criterio de busqueda (documentado en docs/caso_estudio_busqueda.md, sec. 1.1):
  - Texto: el campo "abstract" ORIGINAL de cada articulo, no el preprocesado,
    porque la coincidencia debe ser exacta sobre el texto que ve el usuario.
  - Mayusculas: se distinguen por defecto (igual que los main() de los tres
    algoritmos). Con ignorar_mayusculas=True se pasan texto y patron a
    minusculas antes de buscar; las posiciones no cambian porque lower() no
    altera la longitud de los caracteres del corpus (se comprueba abajo).
  - Posiciones: indices desde 0 dentro de cada abstract.

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\busqueda\\verificacion_busqueda.py "education"
    .\\venv\\Scripts\\python.exe src\\busqueda\\verificacion_busqueda.py "education" --ignorar-mayusculas
"""

import json
import os
import sys

RAIZ_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUTA_CORPUS = os.path.join(RAIZ_PROYECTO, "data", "corpus_preprocesado.json")

# Importaciones que funcionan igual si se ejecuta este archivo como script
# desde cualquier carpeta o si se importa desde otro modulo (API, interfaz, pruebas).
sys.path.insert(0, os.path.join(RAIZ_PROYECTO, "src"))

from busqueda.boyer_moore import buscar as bm_buscar  # noqa: E402
from busqueda.kmp import buscar as kmp_buscar  # noqa: E402
from busqueda.rabin_karp import buscar as rk_buscar  # noqa: E402

ALGORITMOS = {"KMP": kmp_buscar, "Rabin-Karp": rk_buscar, "Boyer-Moore": bm_buscar}


def cargar_corpus(ruta=RUTA_CORPUS):
    with open(ruta, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def buscar_en_texto(texto, patron, ignorar_mayusculas=False):
    """
    Ejecuta los tres algoritmos sobre un texto.
    Retorna (posiciones, coinciden, por_algoritmo).
    """
    if ignorar_mayusculas:
        texto_busqueda, patron_busqueda = texto.lower(), patron.lower()
        if len(texto_busqueda) != len(texto) or len(patron_busqueda) != len(patron):
            raise ValueError("lower() cambio la longitud del texto; las posiciones no serian validas")
    else:
        texto_busqueda, patron_busqueda = texto, patron

    por_algoritmo = {nombre: f(texto_busqueda, patron_busqueda) for nombre, f in ALGORITMOS.items()}
    resultados = list(por_algoritmo.values())
    coinciden = all(r == resultados[0] for r in resultados)
    return resultados[0], coinciden, por_algoritmo


def buscar_y_verificar(corpus, patron, ignorar_mayusculas=False):
    """
    Busca el patron en el abstract original de cada articulo del corpus.

    corpus: lista de diccionarios con "numero", "titulo" y "abstract".
    Retorna un diccionario con:
      - patron, ignorar_mayusculas
      - articulos: lista con numero, titulo, posiciones y coinciden, solo de
        los articulos con al menos una ocurrencia
      - total_ocurrencias, articulos_con_ocurrencias
      - todas_coinciden: True si los tres algoritmos coincidieron en los 20
      - discrepancias: articulos donde no coincidieron, con el detalle por algoritmo
    """
    if not isinstance(patron, str) or len(patron) == 0:
        raise ValueError("El patron no puede estar vacio")

    articulos, discrepancias, total = [], [], 0
    for articulo in corpus:
        posiciones, coinciden, por_algoritmo = buscar_en_texto(
            articulo["abstract"], patron, ignorar_mayusculas)
        if not coinciden:
            discrepancias.append({"numero": articulo["numero"], "por_algoritmo": por_algoritmo})
        if posiciones:
            total += len(posiciones)
            articulos.append({"numero": articulo["numero"], "titulo": articulo["titulo"],
                              "posiciones": posiciones, "coinciden": coinciden})

    return {"patron": patron, "ignorar_mayusculas": ignorar_mayusculas,
            "articulos": articulos, "total_ocurrencias": total,
            "articulos_con_ocurrencias": len(articulos),
            "todas_coinciden": not discrepancias, "discrepancias": discrepancias}


def main():
    argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
    patron = argumentos[0] if argumentos else "learning"
    ignorar = "--ignorar-mayusculas" in sys.argv

    corpus = cargar_corpus()
    reporte = buscar_y_verificar(corpus, patron, ignorar)

    print("=== [BUS-4] BUSQUEDA Y VERIFICACION EN LOS 20 ABSTRACTS ===")
    print(f"Patron: {patron!r} | "
          f"{'NO distingue' if ignorar else 'distingue'} mayusculas | texto: abstract original\n")
    for a in reporte["articulos"]:
        estado = "OK" if a["coinciden"] else "DISCREPANCIA"
        print(f"  Art. {a['numero']:>2} [{estado}]: {len(a['posiciones'])} en {a['posiciones']}")
    print(f"\nTotal: {reporte['total_ocurrencias']} ocurrencias en "
          f"{reporte['articulos_con_ocurrencias']} de {len(corpus)} abstracts")
    if reporte["todas_coinciden"]:
        print("Verificacion: KMP, Rabin-Karp y Boyer-Moore coinciden en los 20 abstracts.")
    else:
        print("ALERTA: discrepancias en los articulos "
              f"{[d['numero'] for d in reporte['discrepancias']]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
