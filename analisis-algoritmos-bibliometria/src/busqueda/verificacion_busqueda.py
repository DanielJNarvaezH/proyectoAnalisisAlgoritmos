# Importar las funciones de búsqueda de tus archivos locales
# Asegúrate de ajustar el nombre de la función según cómo las hayas definido
import sys
import os
import json

from kmp import buscar as kmp_buscar          # Debe retornar una lista de índices
from rabin_karp import buscar as rk_buscar    # Debe retornar una lista de índices
from boyer_moore import buscar as bm_buscar   # Debe retornar una lista de índices

def buscar_y_verificar(abstracts, patron, case_sensitive=False):
    """
    Localiza las ocurrencias de un patrón en una lista de abstracts
    usando 3 algoritmos y verifica que los resultados coincidan.
    """
    resultados_totales = {}
    todas_coinciden = True

    print(f"--- Iniciando búsqueda del patrón: '{patron}' ---")
    if case_sensitive:
        print(f"Configuración: Distingue mayúsculas\n")
    else:
        print(f"Configuración: NO distingue mayúsculas\n")

    for i, texto_original in enumerate(abstracts, 1):
        # 1. Definir si se busca en el texto original o si se normaliza (mayúsculas/minúsculas)
        if not case_sensitive:
            texto_busqueda = texto_original.lower()
            patron_busqueda = patron.lower()
        else:
            texto_busqueda = texto_original
            patron_busqueda = patron

        # 2. Ejecutar los 3 algoritmos para el abstract actual
        # (Se asume que devuelven listas de índices, ej:)
        res_kmp = kmp_buscar(texto_busqueda, patron_busqueda)
        res_rk = rk_buscar(texto_busqueda, patron_busqueda)
        res_bm = bm_buscar(texto_busqueda, patron_busqueda)

        # 3. Verificar que las ocurrencias coincidan exactamente
        coinciden = (res_kmp == res_rk == res_bm)

        if not coinciden:
            todas_coinciden = False

        # Guardar resultados del abstract para el reporte
        resultados_totales[f"Abstract {i}"] = {
            "coinciden": coinciden,
            "ocurrencias_encontradas": len(res_kmp),
            "indices": res_kmp if coinciden else {"KMP": res_kmp, "RK": res_rk, "BM": res_bm}
        }

        # Imprimir estatus por cada abstract
        status = "✅ COINCIDEN" if coinciden else "❌ DISCREPANCIA"
        print(f"Abstract {i:02d}: {status} | Ocurrencias: {len(res_kmp)}")

    # 4. Verificación global del experimento
    print("\n=========================================")
    if todas_coinciden:
        print("🎉 ¡ÉXITO GLOBAL! Los 3 algoritmos coincidieron en todos los abstracts.")
    else:
        print("⚠️ ALERTA: Hubo discrepancias en las salidas de los algoritmos. Revisa el diccionario de resultados.")
    print("=========================================")

    return resultados_totales


# --- EJEMPLO DE USO ---
if __name__ == "__main__":
    ruta_json = "data/corpus_preprocesado.json"

    # 1. Validar que el archivo exista en la ruta
    if not os.path.exists(ruta_json):
        print(f"❌ Error: No se encontró el archivo '{ruta_json}' en el directorio actual.")
        sys.exit(1)

    # 2. Cargar los datos desde el archivo JSON
    with open(ruta_json, 'r', encoding='utf-8') as archivo:
        articulos = json.load(archivo)

    # 3. Extraer únicamente el campo 'abstract' de cada artículo
    # (Soporta si el JSON es una lista de diccionarios)
    lista_abstracts = [art["abstract"] for art in articulos if "abstract" in art]

    # Patrón de búsqueda de prueba (por argumento o por defecto)
    patron_a_buscar = sys.argv[1] if len(sys.argv) > 1 else "learning"

    # Ejecución del experimento
    reporte = buscar_y_verificar(lista_abstracts, patron_a_buscar, case_sensitive=False)