"""Acciones reutilizables sobre la interfaz Streamlit (sin logica de pruebas)."""

import csv
import re
import time

from playwright.sync_api import expect

from conftest import TIMEOUT_CALCULO_MS


# ---------------------------------------------------------------- generales
def esperar_listo(app):
    """Espera a que Streamlit termine de re-ejecutar el script."""
    time.sleep(0.5)  # deja que el widget 'Running...' aparezca antes de esperar a que se vaya
    app.get_by_test_id("stStatusWidget").wait_for(state="detached", timeout=TIMEOUT_CALCULO_MS)


def reintentar(leer, condicion, timeout_s=60, descripcion=""):
    """Repite leer() hasta que condicion(valor) sea cierta; devuelve el valor o falla."""
    limite = time.time() + timeout_s
    valor = None
    while time.time() < limite:
        valor = leer()
        if condicion(valor):
            return valor
        time.sleep(0.5)
    raise AssertionError(f"{descripcion or 'condicion'} no se cumplio; ultimo valor: {valor!r}")


def ir_a_tab(app, nombre):
    app.get_by_role("tab", name=re.compile(nombre)).click()
    esperar_listo(app)
    return app.get_by_role("tabpanel")


def metrica(panel, etiqueta):
    """Texto del valor de una st.metric por su etiqueta."""
    m = panel.get_by_test_id("stMetric").filter(has_text=etiqueta)
    return m.get_by_test_id("stMetricValue").inner_text().strip()


def verificar_metrica(panel, etiqueta, esperado):
    """Espera (con reintento) a que la metrica tenga exactamente ese valor."""
    m = panel.get_by_test_id("stMetric").filter(has_text=etiqueta)
    expect(m.get_by_test_id("stMetricValue")).to_have_text(str(esperado), timeout=TIMEOUT_CALCULO_MS)


def elegir_opcion(app, etiqueta, texto):
    """Selecciona 'texto' en el selectbox con esa etiqueta."""
    app.get_by_role("combobox", name=etiqueta).first.click()
    app.get_by_role("option", name=texto, exact=True).click()
    esperar_listo(app)


# ---------------------------------------------------------- barra lateral
def seleccionar_articulos(app, numeros):
    """Deja seleccionados exactamente `numeros` en la barra lateral."""
    lateral = app.get_by_test_id("stSidebar")
    lateral.get_by_role("button", name="Ninguno").click()
    esperar_listo(app)
    combo = lateral.get_by_test_id("stMultiSelect").get_by_role("combobox")
    for n in numeros:
        combo.click()
        combo.fill(f"[{n}]")
        app.get_by_role("option", name=re.compile(rf"^\[{n}\] ")).first.click()
    # el desplegable abierto marca el resto de la pagina como aria-hidden: se cierra
    combo.press("Escape")
    esperar_listo(app)


def ejecutar_algoritmos(app):
    """
    Pulsa 'Ejecutar algoritmos' y espera a que desaparezcan los avisos de
    'elige los articulos' / 'la seleccion cambio'. Reintenta el clic si Streamlit
    lo perdio (p. ej. porque un desplegable aun se estaba cerrando).
    """
    lateral = app.get_by_test_id("stSidebar")
    avisos = app.get_by_text(re.compile(r"Elige los articulos en la barra lateral|La seleccion cambio desde"))
    for _ in range(4):
        lateral.get_by_role("button", name="Ejecutar algoritmos").click()
        esperar_listo(app)
        try:
            expect(avisos).to_have_count(0, timeout=8_000)
            return
        except AssertionError:
            continue
    raise AssertionError("'Ejecutar algoritmos' no produjo resultados tras 4 intentos")


# -------------------------------------------------------------- modulo 1
def valores_heatmap(app, n_celdas):
    """
    Numeros (2 decimales) escritos dentro del mapa de calor de Plotly de la
    pestana Similitudes. Reintenta hasta ver exactamente n_celdas valores, para
    no leer el grafico anterior mientras Streamlit aun redibuja.
    """
    def leer():
        panel = app.get_by_role("tabpanel")
        grafico = panel.locator(".js-plotly-plot").first
        if not grafico.count():
            return []
        textos = grafico.locator("g.heatmaplayer text").evaluate_all("els => els.map(e => e.textContent)")
        return [t.strip() for t in textos if t and re.fullmatch(r"-?\d\.\d\d", t.strip())]
    return reintentar(leer, lambda v: len(v) == n_celdas, timeout_s=90,
                      descripcion=f"mapa de calor con {n_celdas} celdas")


# -------------------------------------------------------------- modulo 2
def grupos_de_expander(app, criterio):
    """
    Lee 'Grupo i (n): [..]' del expander 'Grupos y fusiones - <criterio>' y
    devuelve el conjunto de grupos como frozensets de numeros de articulo.
    """
    exp = app.get_by_test_id("stExpander").filter(
        has_text=re.compile(rf"Grupos y fusiones - .*{criterio}", re.I))
    exp.locator("summary").click()
    expect(exp.get_by_text(re.compile(r"^Grupo 1 "))).to_be_visible()
    grupos = set()
    for linea in exp.get_by_text(re.compile(r"^Grupo \d+ \(\d+\):")).all_inner_texts():
        miembros = re.search(r"\[([\d,\s]*)\]", linea).group(1)
        grupos.add(frozenset(int(x) for x in miembros.split(",") if x.strip()))
    exp.locator("summary").click()  # lo dejamos cerrado
    return grupos


# -------------------------------------------------------------- modulo 3
def buscar_patron(app, panel, patron, ignorar_mayusculas=False):
    caja = panel.get_by_label("Patron a buscar")
    caja.fill(patron)
    caja.press("Enter")
    casilla = panel.get_by_test_id("stCheckbox").filter(has_text="Ignorar mayusculas")
    marcado = casilla.locator('input[type="checkbox"]').is_checked()
    if marcado != ignorar_mayusculas:
        casilla.locator("label").click()
    esperar_listo(app)


# -------------------------------------------------------------- modulo 4
def descargar_ranking(page, panel):
    """Pulsa 'Descargar ranking completo' y devuelve [(posicion, termino, frecuencia)]."""
    with page.expect_download(timeout=60_000) as descarga:
        panel.get_by_test_id("stDownloadButton").get_by_role("button").click()
    ruta = descarga.value.path()
    with open(ruta, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    return [(int(r["posicion"]), r["termino"], int(r["frecuencia"])) for r in filas]