from pypdf import PdfReader
import os
import re
import pandas as pd


CARPETA_PDFS = "analisis-algoritmos-bibliometria/data/pdfs"


def extraer_texto(pdf_path):
    """Extrae todo el texto del PDF."""

    reader = PdfReader(pdf_path)

    texto = ""

    for pagina in reader.pages:
        texto_pagina = pagina.extract_text()

        if texto_pagina:
            texto += texto_pagina + "\n"

    return texto


def extraer_autores(texto):
    """Intenta obtener los autores."""

    lineas = [
        linea.strip()
        for linea in texto.split("\n")
        if linea.strip()
    ]

    if len(lineas) < 2:
        return ""

    # Buscar Abstract
    posicion_abstract = -1

    for i, linea in enumerate(lineas):
        if linea.lower() in ["abstract", "abstract."]:
            posicion_abstract = i
            break

    # Si encontramos Abstract, las líneas entre título y abstract
    # pueden contener los autores.
    if posicion_abstract > 1:

        posibles_autores = lineas[1:posicion_abstract]

        # Eliminamos líneas muy largas
        posibles_autores = [
            linea for linea in posibles_autores
            if len(linea) < 150
        ]

        return " ".join(posibles_autores)

    return ""


def extraer_abstract(texto):
    """Extrae el contenido del abstract."""

    # Buscar diferentes formas de escribir Abstract
    patrones = [
        r"(?i)\babstract\b[:.\s]*(.*?)(?=\bkeywords?\b|\bintroduction\b|\b1\.\s*introduction\b)",
        r"(?i)\babstract\b[:.\s]*(.*?)(?=\n\s*\n)",
    ]

    for patron in patrones:

        resultado = re.search(
            patron,
            texto,
            re.DOTALL
        )

        if resultado:
            abstract = resultado.group(1)

            # Limpiar espacios
            abstract = re.sub(
                r"\s+",
                " ",
                abstract
            ).strip()

            return abstract

    return ""


resultados = []


# Recorrer todos los archivos de la carpeta
for archivo in os.listdir(CARPETA_PDFS):

    if archivo.lower().endswith(".pdf"):

        ruta_pdf = os.path.join(
            CARPETA_PDFS,
            archivo
        )

        # El numero y el titulo vienen en el nombre de cada PDF entregado
        # por el docente (p. ej. "1. Artificial intelligence literacy....pdf").
        numero_y_titulo = os.path.splitext(archivo)[0]

        print(f"Procesando: {archivo}")

        try:

            texto = extraer_texto(ruta_pdf)

            autores = extraer_autores(texto)
            abstract = extraer_abstract(texto)

            resultados.append({
                "archivo": numero_y_titulo,
                "autores": "Autores: " + autores,
                "abstract": "Abstractas: " + abstract
            })

        except Exception as e:

            print(f"Error en {archivo}: {e}")

            resultados.append({
                "archivo": numero_y_titulo,
                "autores": "",
                "abstract": ""
            })


# Crear DataFrame
df = pd.DataFrame(resultados)


# Guardar resultados
df.to_csv(
    "analisis-algoritmos-bibliometria/data/raw/articulos_extraidos.csv",
    index=False,
    encoding="utf-8-sig"
)


print("\nProceso terminado.")
print(f"Artículos procesados: {len(resultados)}")
print("Archivo generado: articulos_extraidos.csv")