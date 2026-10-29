"""
Backend / API del proyecto (tarea DEP-1)
========================================

Expone con Flask los algoritmos ya implementados en src/, sin reimplementar
nada:

  GET /articulos                         lista de los 20 articulos (numero y titulo)
  GET /similitud?articulos=2,9           R1: matrices de similitud (4 clasicos + 2 de IA)
  GET /clustering?criterio=single        R2: matriz de enlace y correlacion cofenetica
  GET /busqueda?patron=education         R3: ocurrencias con KMP, Rabin-Karp y Boyer-Moore
  GET /ranking?algoritmo=counting&top=15 Seguimiento: ranking de terminos

Parametros opcionales:
  /clustering: criterio = single | complete | average (por defecto: single)
  /busqueda:   ignorar_mayusculas = true | false (por defecto: false)
  /ranking:    algoritmo = counting | radix | bucket (por defecto: counting); top (por defecto: 15)

Ejecutar desde la raiz del proyecto:

    .\\venv\\Scripts\\python.exe backend\\app.py

y abrir en el navegador, por ejemplo, http://127.0.0.1:5000/articulos
"""

import os
import sys

from flask import Flask, jsonify, request

RAIZ_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(RAIZ_PROYECTO, "src"))

from busqueda.verificacion_busqueda import buscar_y_verificar  # noqa: E402
from clustering.average_linkage import average_linkage  # noqa: E402
from clustering.complete_linkage import complete_linkage  # noqa: E402
from clustering.dendrograma import construir_matriz_enlace  # noqa: E402
from clustering.distance_matrix import cargar_matriz_distancias  # noqa: E402
from clustering.evaluacion import correlacion_cofenetica  # noqa: E402
from clustering.single_linkage import single_linkage  # noqa: E402
from comparador import cargar_corpus, cargar_modelos_ia, comparar_articulos  # noqa: E402
from ordenamiento.bucket_sort import ordenar_por_frecuencia as bucket_sort  # noqa: E402
from ordenamiento.counting_sort import ordenar_por_frecuencia as counting_sort  # noqa: E402
from ordenamiento.frecuencias import obtener_lista_frecuencias  # noqa: E402
from ordenamiento.radix_sort import ordenar_por_frecuencia as radix_sort  # noqa: E402

CRITERIOS = {"single": single_linkage, "complete": complete_linkage, "average": average_linkage}
ORDENAMIENTOS = {"counting": counting_sort, "radix": radix_sort, "bucket": bucket_sort}

# Datos que no cambian: se cargan una sola vez al iniciar el servidor
CORPUS = cargar_corpus()                     # {numero: articulo}
MODELOS_IA = cargar_modelos_ia()             # embeddings precalculados de data/embeddings/
INDICES_CLUSTERING, DISTANCIAS = cargar_matriz_distancias()
FRECUENCIAS = obtener_lista_frecuencias()

app = Flask(__name__)
app.json.ensure_ascii = False  # tildes legibles en las respuestas
app.json.sort_keys = False


def error(mensaje, codigo=400):
    return jsonify({"error": mensaje}), codigo


@app.get("/")
def inicio():
    return jsonify({"endpoints": ["/articulos", "/similitud?articulos=2,9",
                                  "/clustering?criterio=single", "/busqueda?patron=education",
                                  "/ranking?algoritmo=counting&top=15"]})


@app.get("/articulos")
def articulos():
    return jsonify([{"numero": n, "titulo": CORPUS[n]["titulo"]} for n in sorted(CORPUS)])


@app.get("/similitud")
def similitud():
    texto = request.args.get("articulos", "")
    try:
        numeros = [int(parte) for parte in texto.split(",") if parte.strip()]
        resultado = comparar_articulos(numeros, CORPUS, MODELOS_IA)
    except ValueError as e:
        return error(f"Parametro 'articulos' invalido: {e}. Ejemplo: /similitud?articulos=2,9")
    return jsonify({"articulos": numeros, **resultado})


@app.get("/clustering")
def clustering():
    criterio = request.args.get("criterio", "single")
    if criterio not in CRITERIOS:
        return error(f"criterio debe ser uno de {list(CRITERIOS)}")
    historial = CRITERIOS[criterio](DISTANCIAS)
    z = construir_matriz_enlace(historial)
    return jsonify({"criterio": criterio,
                    "articulos": INDICES_CLUSTERING,
                    "matriz_enlace": z,
                    "correlacion_cofenetica": correlacion_cofenetica(DISTANCIAS, z)})


@app.get("/busqueda")
def busqueda():
    patron = request.args.get("patron", "")
    if not patron:
        return error("Falta el parametro 'patron'. Ejemplo: /busqueda?patron=education")
    ignorar = request.args.get("ignorar_mayusculas", "false").lower() == "true"
    corpus = [CORPUS[n] for n in sorted(CORPUS)]
    return jsonify(buscar_y_verificar(corpus, patron, ignorar))


@app.get("/ranking")
def ranking():
    algoritmo = request.args.get("algoritmo", "counting")
    if algoritmo not in ORDENAMIENTOS:
        return error(f"algoritmo debe ser uno de {list(ORDENAMIENTOS)}")
    try:
        top = int(request.args.get("top", 15))
    except ValueError:
        return error("top debe ser un numero entero")
    resultado = ORDENAMIENTOS[algoritmo](FRECUENCIAS)
    return jsonify({"algoritmo": algoritmo,
                    "terminos_distintos": len(resultado),
                    "ranking": [{"posicion": i + 1, "termino": t, "frecuencia": f}
                                for i, (t, f) in enumerate(resultado[:top])]})


if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5000))  # PORT lo define el servicio de despliegue
    app.run(host="0.0.0.0", port=puerto)
