"""
Interfaz Streamlit del proyecto
===============================

Permite seleccionar articulos del corpus, ejecutar los 6 algoritmos de
similitud (reutilizando comparador.comparar_articulos) y construir los
dendrogramas con los 3 criterios de enlace del proyecto (reutilizando
src/clustering/*), sin reimplementar nada.

Tambien expone:
  - R3: busqueda de patrones con KMP, Rabin-Karp y Boyer-Moore sobre los
    abstracts (reutiliza src/busqueda/verificacion_busqueda.py).
  - Ranking de terminos por frecuencia con Counting, Radix y Bucket Sort
    (reutiliza src/ordenamiento/*).
La busqueda y el ranking trabajan sobre el corpus completo (20 articulos),
sin depender de la seleccion de la barra lateral.

Uso (desde la carpeta analisis-algoritmos-bibliometria):

    pip install streamlit plotly scipy
    streamlit run app.py
"""

import html
import os
import sys
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

RAIZ = os.path.abspath(os.path.dirname(__file__))
SRC = os.path.join(RAIZ, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from busqueda.kmp import buscar as kmp_buscar  # noqa: E402
from busqueda.verificacion_busqueda import ALGORITMOS as ALGORITMOS_BUSQUEDA  # noqa: E402
from busqueda.verificacion_busqueda import buscar_y_verificar  # noqa: E402
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
from ordenamiento.bucket_sort import ordenar_por_frecuencia as bucket_sort  # noqa: E402
from ordenamiento.counting_sort import frecuencia_maxima  # noqa: E402
from ordenamiento.counting_sort import ordenar_por_frecuencia as counting_sort  # noqa: E402
from ordenamiento.frecuencias import obtener_lista_frecuencias  # noqa: E402
from ordenamiento.radix_sort import ordenar_por_frecuencia as radix_sort  # noqa: E402

CRITERIOS = {
    "single": single_linkage,
    "complete": complete_linkage,
    "average": average_linkage,
}

ORDENAMIENTOS = {
    "Counting Sort": counting_sort,
    "Radix Sort": radix_sort,
    "Bucket Sort": bucket_sort,
}

st.set_page_config(page_title="Bibliometria - Similitud, Clustering, Busqueda y Ranking",
                   layout="wide")


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
# R3: busqueda de patrones
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def ejecutar_busqueda(patron, ignorar_mayusculas, _corpus):
    lista = [_corpus[n] for n in sorted(_corpus)]
    return buscar_y_verificar(lista, patron, ignorar_mayusculas)


@st.cache_data(show_spinner=False)
def medir_busqueda(patron, ignorar_mayusculas, _corpus, repeticiones=30):
    """Tiempo medio (ms) de cada algoritmo recorriendo los abstracts del corpus."""
    textos = [_corpus[n]["abstract"] for n in sorted(_corpus)]
    if ignorar_mayusculas:
        textos = [t.lower() for t in textos]
        patron = patron.lower()
    filas = []
    for nombre, buscar in ALGORITMOS_BUSQUEDA.items():
        for t in textos[:2]:  # calentamiento
            buscar(t, patron)
        inicio = time.perf_counter()
        total = 0
        for _ in range(repeticiones):
            total = sum(len(buscar(t, patron)) for t in textos)
        ms = (time.perf_counter() - inicio) / repeticiones * 1000
        filas.append({"Algoritmo": nombre, "Ocurrencias": total, "Tiempo medio (ms)": ms})
    return filas


def resaltar(texto, posiciones, largo):
    """HTML del abstract con cada ocurrencia marcada (une las que se solapan)."""
    intervalos = []
    for p in posiciones:
        if intervalos and p <= intervalos[-1][1]:
            intervalos[-1][1] = max(intervalos[-1][1], p + largo)
        else:
            intervalos.append([p, p + largo])
    partes, cursor = [], 0
    for ini, fin in intervalos:
        partes.append(html.escape(texto[cursor:ini]))
        partes.append('<mark style="background:#ffd54f;color:#000;padding:0 2px;'
                      f'border-radius:3px">{html.escape(texto[ini:fin])}</mark>')
        cursor = fin
    partes.append(html.escape(texto[cursor:]))
    return '<div style="line-height:1.6">' + "".join(partes) + "</div>"


def seccion_busqueda(corpus):
    st.subheader("Busqueda de patrones (R3)")
    st.caption("KMP, Rabin-Karp y Boyer-Moore (implementados desde cero) buscan el patron "
               "como subcadena exacta en el abstract original de los articulos del corpus "
               "y se verifica que los tres devuelvan las mismas posiciones.")

    c1, c2 = st.columns([3, 1])
    patron = c1.text_input("Patron a buscar", value="education", key="patron_busqueda",
                           placeholder="Ej.: learning, education, AI")
    ignorar = c2.checkbox("Ignorar mayusculas", value=False, key="ignorar_mayus",
                          help="Si no se marca, 'AI' y 'ai' son patrones distintos.")
    if not patron:
        st.info("Escribe un patron para buscarlo en los abstracts.")
        return

    reporte = ejecutar_busqueda(patron, ignorar, corpus)
    total_articulos = len(corpus)

    m1, m2, m3 = st.columns(3)
    m1.metric("Ocurrencias totales", reporte["total_ocurrencias"])
    m2.metric("Articulos con ocurrencias",
              f"{reporte['articulos_con_ocurrencias']} de {total_articulos}")
    m3.metric("Verificacion cruzada",
              "Coinciden" if reporte["todas_coinciden"] else "Discrepan",
              help="KMP, Rabin-Karp y Boyer-Moore deben devolver exactamente las mismas posiciones.")

    if not reporte["todas_coinciden"]:
        st.error("Discrepancias en los articulos "
                 f"{[d['numero'] for d in reporte['discrepancias']]}.")

    if reporte["total_ocurrencias"] == 0:
        st.info(f"El patron {patron!r} no aparece en ningun abstract.")
        return

    arts = reporte["articulos"]
    df = pd.DataFrame({
        "Articulo": [a["numero"] for a in arts],
        "Titulo": [a["titulo"] for a in arts],
        "Ocurrencias": [len(a["posiciones"]) for a in arts],
        "Posiciones": [", ".join(map(str, a["posiciones"])) for a in arts],
    })

    fig = px.bar(df, x=df["Articulo"].astype(str), y="Ocurrencias",
                 hover_data={"Titulo": True}, labels={"x": "Articulo"})
    fig.update_xaxes(type="category")
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=30, b=10),
                      title="Ocurrencias por articulo")
    st.plotly_chart(fig, width="stretch")

    st.dataframe(df, hide_index=True, width="stretch")
    st.caption("Las posiciones son indices desde 0 dentro del abstract original.")

    st.markdown("**Abstracts con el patron resaltado**")
    for i, a in enumerate(arts):
        titulo = a["titulo"] if len(a["titulo"]) <= 80 else a["titulo"][:79] + "..."
        with st.expander(f"[{a['numero']}] {titulo} - {len(a['posiciones'])} ocurrencia(s)",
                         expanded=(i == 0 and len(arts) <= 3)):
            st.html(resaltar(corpus[a["numero"]]["abstract"], a["posiciones"], len(patron)))

    with st.expander("Comparar los tres algoritmos para este patron"):
        filas = pd.DataFrame(medir_busqueda(patron, ignorar, corpus))
        st.dataframe(filas.round({"Tiempo medio (ms)": 4}), hide_index=True, width="stretch",
                     column_config={"Tiempo medio (ms)": st.column_config.NumberColumn(
                         format="%.4f")})
        st.caption(f"Tiempo medio de recorrer los {total_articulos} abstracts (30 repeticiones). "
                   "Para el analisis completo ver docs/analisis_busqueda.md.")


# ---------------------------------------------------------------------------
# Ranking de terminos por frecuencia
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def obtener_frecuencias():
    return obtener_lista_frecuencias()


@st.cache_data(show_spinner=False)
def calcular_ranking(nombre):
    return ORDENAMIENTOS[nombre](obtener_frecuencias())


@st.cache_data(show_spinner=False)
def medir_ordenamientos(repeticiones=30):
    pares = obtener_frecuencias()
    filas, rankings = [], {}
    for nombre, ordenar in ORDENAMIENTOS.items():
        ordenar(pares)  # calentamiento
        inicio = time.perf_counter()
        for _ in range(repeticiones):
            rankings[nombre] = ordenar(pares)
        ms = (time.perf_counter() - inicio) / repeticiones * 1000
        filas.append({"Algoritmo": nombre, "Tiempo medio (ms)": ms})
    todos = list(rankings.values())
    return filas, all(r == todos[0] for r in todos)


def seccion_ranking():
    st.subheader("Ranking de terminos por frecuencia")
    st.caption("Frecuencia de cada termino en el texto preprocesado de los 20 abstracts, "
               "ordenada de mayor a menor con algoritmos sin comparaciones (Counting, Radix "
               "y Bucket Sort). Los empates conservan el orden de primera aparicion (orden estable).")

    pares = obtener_frecuencias()
    total_terminos = len(pares)
    total_tokens = sum(f for _, f in pares)

    c1, c2 = st.columns([1, 2])
    nombre = c1.selectbox("Algoritmo de ordenamiento", list(ORDENAMIENTOS), key="sel_rank")
    top = c2.slider("Terminos a mostrar (top)", 5, min(100, total_terminos), 15, key="top_rank")

    ranking = calcular_ranking(nombre)

    m1, m2, m3 = st.columns(3)
    m1.metric("Terminos distintos (n)", total_terminos)
    m2.metric("Tokens totales", total_tokens)
    m3.metric("Frecuencia maxima (k)", frecuencia_maxima(pares))

    df_top = pd.DataFrame(
        [{"Posicion": i, "Termino": t, "Frecuencia": f}
         for i, (t, f) in enumerate(ranking[:top], start=1)])

    col_tabla, col_graf = st.columns([1, 2])
    col_tabla.dataframe(df_top, hide_index=True, width="stretch", height=min(700, 38 + 35 * top))
    fig = px.bar(df_top, x="Frecuencia", y="Termino", orientation="h", text="Frecuencia")
    fig.update_yaxes(autorange="reversed", type="category")
    fig.update_layout(height=min(700, 80 + 26 * top), margin=dict(l=10, r=10, t=30, b=10),
                      title=f"Top {top} terminos - {nombre}")
    col_graf.plotly_chart(fig, width="stretch")

    st.markdown("**Consultar la posicion de un termino**")
    consulta = st.text_input("Termino (o parte de el)", key="consulta_rank",
                             placeholder="Ej.: learn, education, ethic")
    q = consulta.strip().lower()
    if q:
        hallados = [{"Posicion": i, "Termino": t, "Frecuencia": f}
                    for i, (t, f) in enumerate(ranking, start=1) if kmp_buscar(t, q)]
        if hallados:
            st.dataframe(pd.DataFrame(hallados), hide_index=True, width="stretch")
        else:
            st.info(f"Ningun termino contiene {q!r}.")

    c_a, c_b = st.columns(2)
    with c_a.expander("Comparar los tres algoritmos"):
        filas, iguales = medir_ordenamientos()
        st.dataframe(pd.DataFrame(filas).round(4), hide_index=True, width="stretch",
                     column_config={"Tiempo medio (ms)": st.column_config.NumberColumn(
                         format="%.4f")})
        if iguales:
            st.success("Los tres algoritmos producen exactamente el mismo ranking.")
        else:
            st.error("Los rankings de los tres algoritmos NO coinciden.")
        st.caption("Para el analisis completo ver docs/seguimiento_ordenamiento.md.")
    csv = pd.DataFrame([{"posicion": i, "termino": t, "frecuencia": f}
                        for i, (t, f) in enumerate(ranking, start=1)]).to_csv(index=False)
    c_b.download_button(f"Descargar ranking completo ({total_terminos} terminos, CSV)", csv,
                        file_name="ranking_terminos.csv", mime="text/csv", width="stretch")


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
st.sidebar.caption("La seleccion aplica a Similitudes, Dendrogramas y Articulos. "
                   "Busqueda de patrones y Ranking usan los 20 articulos del corpus.")

# ---------------------------------------------------------------------------
# Cuerpo
# ---------------------------------------------------------------------------

st.title("Similitud, clustering, busqueda de patrones y ranking de terminos")

tab_sim, tab_den, tab_art, tab_bus, tab_rank = st.tabs(
    ["Similitudes", "Dendrogramas", "Articulos", "Busqueda de patrones (R3)",
     "Ranking de terminos"])

# Busqueda y ranking no dependen de la seleccion: se dibujan siempre
with tab_bus:
    seccion_busqueda(corpus)
with tab_rank:
    seccion_ranking()

numeros = st.session_state.get("numeros")
if not numeros:
    for tab in (tab_sim, tab_den, tab_art):
        tab.info("Elige los articulos en la barra lateral y pulsa **Ejecutar algoritmos**.")
    st.stop()

if tuple(seleccion) != numeros:
    for tab in (tab_sim, tab_den, tab_art):
        tab.warning("La seleccion cambio desde la ultima ejecucion. "
                    "Pulsa **Ejecutar algoritmos** para actualizar los resultados.")

numeros = list(numeros)
n = len(numeros)
resultado = ejecutar(tuple(numeros), corpus, modelos_ia)
opciones = matrices_disponibles(resultado)
etiquetas = [str(x) for x in numeros]

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