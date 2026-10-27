"""
Interfaz Streamlit del proyecto
===============================

Permite seleccionar articulos del corpus, ejecutar los 6 algoritmos de
similitud (reutilizando comparador.comparar_articulos) y construir los
dendrogramas con los 3 criterios de enlace del proyecto (reutilizando
src/clustering/*), sin reimplementar nada.

Uso (desde la carpeta analisis-algoritmos-bibliometria):

    pip install streamlit plotly scipy
    streamlit run app.py
"""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

RAIZ = os.path.abspath(os.path.dirname(__file__))
SRC = os.path.join(RAIZ, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from clustering.aglomerativo import cortar_en_k_grupos  # noqa: E402
from clustering.average_linkage import average_linkage  # noqa: E402
from clustering.complete_linkage import complete_linkage  # noqa: E402
from clustering.dendrograma import construir_matriz_enlace, validar_matriz_enlace  # noqa: E402
from clustering.evaluacion import correlacion_cofenetica, indice_silueta  # noqa: E402
from clustering.single_linkage import single_linkage  # noqa: E402
from clustering.visualizacion import TITULOS, dibujar, limites_eje  # noqa: E402
from comparador import (  # noqa: E402
    cargar_corpus,
    cargar_modelos_ia,
    comparar_articulos,
    resumen_par,
)

CRITERIOS = {
    "single": single_linkage,
    "complete": complete_linkage,
    "average": average_linkage,
}

st.set_page_config(page_title="Bibliometria - Similitud y Clustering", layout="wide")


# ---------------------------------------------------------------------------
# Carga y calculo (con cache)
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Cargando corpus y embeddings...")
def cargar_datos():
    return cargar_corpus(), cargar_modelos_ia()


@st.cache_data(show_spinner="Ejecutando algoritmos de similitud...")
def ejecutar(numeros, _corpus, _modelos):
    # `numeros` es una tupla (hashable) para que st.cache_data pueda cachear
    return comparar_articulos(list(numeros), _corpus, _modelos)


def matrices_disponibles(resultado):
    """
    Aplana el resultado a {nombre: (matriz, es_distancia)} para poder
    elegir cualquiera como entrada de las tablas y del clustering.
    """
    opciones = {}
    for algoritmo, m in resultado["clasicos"].items():
        opciones[algoritmo] = (np.array(m), False)
    for modelo, ms in resultado["ia"].items():
        opciones[f"{modelo} - coseno"] = (np.array(ms["coseno"]), False)
        opciones[f"{modelo} - similitud euclidiana"] = (np.array(ms["similitud_euclidiana"]), False)
        opciones[f"{modelo} - distancia euclidiana"] = (np.array(ms["distancia_euclidiana"]), True)
    return opciones


def a_distancias(matriz, es_distancia):
    """Las similitudes del proyecto estan en [0, 1]: distancia = 1 - similitud."""
    d = matriz.copy() if es_distancia else np.clip(1.0 - matriz, 0.0, None)
    np.fill_diagonal(d, 0.0)  # evita 1e-16 por redondeo en la diagonal
    return d.tolist()


def titulo_corto(corpus, n, largo=55):
    t = corpus[n]["titulo"]
    return t if len(t) <= largo else t[: largo - 1] + "..."


# ---------------------------------------------------------------------------
# Barra lateral: seleccion y ejecucion
# ---------------------------------------------------------------------------

corpus, modelos_ia = cargar_datos()
todos = sorted(corpus)

st.sidebar.header("Seleccion de articulos")
col_a, col_b = st.sidebar.columns(2)
if col_a.button("Todos", width="stretch"):
    st.session_state["seleccion"] = todos
if col_b.button("Ninguno", width="stretch"):
    st.session_state["seleccion"] = []

seleccion = st.sidebar.multiselect(
    "Articulos a comparar",
    options=todos,
    default=todos,
    key="seleccion",
    format_func=lambda n: f"[{n}] {titulo_corto(corpus, n)}",
)

if len(seleccion) < 2:
    st.sidebar.warning("Selecciona al menos 2 articulos.")

if st.sidebar.button("Ejecutar algoritmos", type="primary", disabled=len(seleccion) < 2,
                     width="stretch"):
    st.session_state["numeros"] = tuple(seleccion)

st.sidebar.caption(f"Modelos de IA cargados: {', '.join(modelos_ia) or 'ninguno'}")

# ---------------------------------------------------------------------------
# Cuerpo
# ---------------------------------------------------------------------------

st.title("Similitud textual y clustering de articulos")

numeros = st.session_state.get("numeros")
if not numeros:
    st.info("Elige los articulos en la barra lateral y pulsa **Ejecutar algoritmos**.")
    st.stop()

if tuple(seleccion) != numeros:
    st.warning("La seleccion cambio desde la ultima ejecucion. "
               "Pulsa **Ejecutar algoritmos** para actualizar los resultados.")

numeros = list(numeros)
n = len(numeros)
resultado = ejecutar(tuple(numeros), corpus, modelos_ia)
opciones = matrices_disponibles(resultado)
etiquetas = [str(x) for x in numeros]

tab_sim, tab_den, tab_art = st.tabs(["Similitudes", "Dendrogramas", "Articulos"])

# ---- Pestana 1: similitudes -------------------------------------------------
with tab_sim:
    if n == 2:
        st.subheader(f"Articulo {numeros[0]} vs articulo {numeros[1]}")
        filas = pd.DataFrame(resumen_par(resultado)).rename(columns={
            "algoritmo": "Algoritmo", "tipo": "Tipo",
            "similitud": "Similitud", "distancia": "Distancia"})
        st.dataframe(filas, hide_index=True, width="stretch",
                     column_config={"Similitud": st.column_config.ProgressColumn(
                         "Similitud", min_value=0.0, max_value=1.0, format="%.4f")})

    nombre = st.selectbox("Algoritmo / modelo", list(opciones), key="sel_sim")
    matriz, es_dist = opciones[nombre]

    escala = "Viridis_r" if es_dist else "Viridis"
    fig = px.imshow(
        matriz, x=etiquetas, y=etiquetas, color_continuous_scale=escala,
        text_auto=".2f" if n <= 12 else False, aspect="equal",
        labels=dict(x="Articulo", y="Articulo",
                    color="Distancia" if es_dist else "Similitud"),
    )
    fig.update_xaxes(type="category", side="top")
    fig.update_yaxes(type="category")
    fig.update_layout(height=min(900, 140 + 38 * n), margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig, width="stretch")

    if n > 2:
        st.markdown("**Pares " + ("mas cercanos" if es_dist else "mas similares") + "**")
        pares = [(numeros[i], numeros[j], matriz[i][j])
                 for i in range(n) for j in range(i + 1, n)]
        pares.sort(key=lambda p: p[2], reverse=not es_dist)
        st.dataframe(
            pd.DataFrame(pares[:10], columns=["Articulo A", "Articulo B",
                                              "Distancia" if es_dist else "Similitud"]),
            hide_index=True, width="stretch")

    with st.expander("Ver matriz como tabla"):
        st.dataframe(pd.DataFrame(matriz, index=etiquetas, columns=etiquetas).round(4),
                     width="stretch")

# ---- Pestana 2: dendrogramas ------------------------------------------------
with tab_den:
    if n < 3:
        st.info("Un dendrograma necesita al menos 3 articulos.")
    else:
        c1, c2, c3 = st.columns([2, 2, 1])
        base = c1.selectbox("Matriz base para el clustering", list(opciones),
                            index=list(opciones).index("Coseno TF-IDF"), key="sel_den")
        criterios = c2.multiselect("Criterios de enlace", list(CRITERIOS),
                                   default=list(CRITERIOS),
                                   format_func=lambda c: TITULOS[c])
        k = c3.slider("Grupos (k)", 2, n - 1, min(4, n - 1)) if n > 3 else 2
        if n == 3:
            c3.caption("k = 2 (con 3 articulos solo hay un corte valido)")

        if not criterios:
            st.warning("Elige al menos un criterio de enlace.")
        else:
            matriz, es_dist = opciones[base]
            distancias = a_distancias(matriz, es_dist)
            st.caption("Distancia = " + ("la distancia euclidiana tal cual."
                                         if es_dist else "1 - similitud."))

            historiales = {c: CRITERIOS[c](distancias) for c in criterios}
            enlaces = {}
            for c, h in historiales.items():
                z = construir_matriz_enlace(h)
                validar_matriz_enlace(z, n)
                enlaces[c] = z

            limites = limites_eje(enlaces)
            columnas = st.columns(len(criterios))
            for col, c in zip(columnas, criterios):
                fig, ax = plt.subplots(figsize=(6 if len(criterios) > 1 else 10, 4.5))
                dibujar(ax, enlaces[c], etiquetas, TITULOS[c], limites)
                ax.set_ylabel("Distancia de fusion")
                col.pyplot(fig, width="stretch")
                plt.close(fig)

            # Evaluacion y cortes
            st.subheader(f"Evaluacion y particion en k = {k} grupos")
            filas, grupos_por_criterio = [], {}
            for c in criterios:
                grupos = cortar_en_k_grupos(historiales[c], n, k)
                grupos_por_criterio[c] = grupos
                filas.append({
                    "Criterio": TITULOS[c],
                    "CPCC (cofenetica)": correlacion_cofenetica(distancias, enlaces[c]),
                    f"Silueta (k={k})": indice_silueta(distancias, grupos),
                })
            st.dataframe(pd.DataFrame(filas).round(4), hide_index=True,
                         width="stretch")
            st.caption("CPCC: mas cerca de 1 = el arbol conserva mejor las distancias. "
                       "Silueta: de -1 a 1, mayor = grupos mas compactos y separados.")

            for c in criterios:
                with st.expander(f"Grupos y fusiones - {TITULOS[c]}"):
                    for i, g in enumerate(grupos_por_criterio[c], start=1):
                        st.write(f"**Grupo {i}** ({len(g)}): {[numeros[j] for j in g]}")
                    miembros = {j: [j] for j in range(n)}
                    for f in historiales[c]:
                        miembros[f["nuevo_grupo"]] = f["miembros"]
                    pasos = pd.DataFrame([{
                        "Paso": f["paso"],
                        "Distancia": round(f["distancia"], 4),
                        "Fusion": f"{[numeros[j] for j in miembros[f['grupo_a']]]} + "
                                  f"{[numeros[j] for j in miembros[f['grupo_b']]]}",
                    } for f in historiales[c]])
                    st.dataframe(pasos, hide_index=True, width="stretch")

# ---- Pestana 3: articulos ---------------------------------------------------
with tab_art:
    for x in numeros:
        art = corpus[x]
        with st.expander(f"[{x}] {art['titulo']}"):
            st.caption(art["autores"])
            st.write(art["abstract"])