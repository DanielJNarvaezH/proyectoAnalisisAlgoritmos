from collections import Counter
import json
import os


def generar_lista_frecuencias(ruta_json):
    # 1. Verificar si el archivo existe
    if not os.path.exists(ruta_json):
        print(f"Error: No se encontró el archivo en {ruta_json}")
        return

    # 2. Leer el archivo JSON
    with open(ruta_json, "r", encoding="utf-8") as archivo:
        articulos = json.load(archivo)

    # Contador global para almacenar la frecuencia total de todos los artículos
    conteo_total = Counter()

    print(f"=== REPORTE DE FRECUENCIAS POR ARTÍCULO ===")

    # 3. Procesar cada artículo uno por uno
    for articulo in articulos:
        id_articulo = articulo.get("numero", "?")
        titulo_articulo = articulo.get("titulo", "Sin título")[:60]  # Truncado para mejor lectura
        palabras_articulo = articulo.get("abstract_preprocesado", [])

        if isinstance(palabras_articulo, list):
            # Contar frecuencias locales del artículo actual
            conteo_local = Counter(palabras_articulo)

            # Sumar al contador global acumulado
            conteo_total.update(palabras_articulo)

            # Ordenar frecuencias locales: Mayor frecuencia (-x[1]), Desempate alfabético (x[0])
            orden_local = sorted(conteo_local.items(), key=lambda x: (-x[1], x[0]))

            # Imprimir el resultado de este artículo específico
            print(f"\n[Artículo {id_articulo}] {titulo_articulo}...")
            print("-" * 50)
            for termino, frecuencia in orden_local:
                print(f"  {termino}: {frecuencia}")
            print("-" * 50)

    # 4. Ordenar y mostrar la frecuencia total acumulada al final
    orden_total = sorted(conteo_total.items(), key=lambda x: (-x[1], x[0]))

    print(f"\n==================================================")
    print(f"=== FRECUENCIA TOTAL ACUMULADA ({len(articulos)} artículos) ===")
    print(f"==================================================")
    for termino, frecuencia in orden_total:
        print(f"{termino}: {frecuencia}")


if __name__ == "__main__":
    # Ajusta aquí el nombre exacto de tu archivo JSON si es necesario
    ruta_datos = "data/corpus_preprocesado.json"
    generar_lista_frecuencias(ruta_datos)
