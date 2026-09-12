import json
import re

articulos = []

with open("analisis-algoritmos-bibliometria/data/raw/articulos_extraidos.csv", "r", encoding="utf-8") as archivo:
    contenido = archivo.read()

# Quitar encabezado
contenido = re.sub(
    r"^\s*archivo\s*,\s*titulo\s*,\s*autores\s*,\s*abstract\s*\n",
    "",
    contenido,
    flags=re.IGNORECASE
)

# Encontrar cada artículo: desde "1." hasta justo antes de "2.", etc.
patron = r"(?m)^\s*(\d+)\.\s*(.*?)(?=^\s*\d+\.\s|\Z)"

coincidencias = re.findall(patron, contenido, flags=re.DOTALL)

for numero, texto in coincidencias:

    # Buscar la marca de autores
    partes_autores = re.split(
        r",\s*Autores:\s*",
        texto,
        maxsplit=1,
        flags=re.IGNORECASE
    )

    if len(partes_autores) != 2:
        print(f"No se pudo procesar el artículo {numero}")
        continue

    titulo = partes_autores[0].strip()
    resto = partes_autores[1]

    # Buscar el comienzo del abstract
    partes_abstract = re.split(
        r",\s*Abstractas:\s*",
        resto,
        maxsplit=1,
        flags=re.IGNORECASE
    )

    if len(partes_abstract) != 2:
        print(f"No se pudo encontrar el abstract del artículo {numero}")
        continue

    autores = partes_abstract[0].strip()
    abstract = partes_abstract[1].strip()

    articulos.append({
        "numero": int(numero),
        "titulo": titulo,
        "autores": autores,
        "abstract": abstract
    })


# Guardar JSON
with open("analisis-algoritmos-bibliometria/data/corpus.json", "w", encoding="utf-8") as archivo:
    json.dump(articulos, archivo, ensure_ascii=False, indent=4)

print(f"Se convirtieron {len(articulos)} artículos.")
print("Archivo creado: corpus.json")