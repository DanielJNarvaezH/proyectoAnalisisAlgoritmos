"""
Fixtures de las pruebas E2E sobre la aplicacion desplegada.

Variables de entorno:
  APP_URL    URL de la app Streamlit (por defecto, la desplegada en Streamlit Cloud).
  HEADED     "1" para ver el navegador.
  SLOWMO     milisegundos de pausa entre acciones (depuracion).
  API_URL    (opcional) URL del backend Flask; activa tests/e2e/test_api_backend.py.
"""

import os
import time

import pytest
from playwright.sync_api import expect, sync_playwright

APP_URL = os.environ.get("APP_URL", "https://bibliometria-algoritmos.streamlit.app/")
TIEMPO_ARRANQUE_S = 240       # una app dormida en Streamlit Cloud puede tardar minutos
TIMEOUT_ACCION_MS = 60_000
TIMEOUT_CALCULO_MS = 150_000  # 20 articulos x Levenshtein/Needleman-Wunsch desde cero

TITULO_APP = "Similitud, clustering, busqueda de patrones y ranking de terminos"


def pytest_configure(config):
    expect.set_options(timeout=TIMEOUT_ACCION_MS)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Si una prueba falla, guarda una captura en tests/e2e/artifacts/."""
    salida = yield
    informe = salida.get_result()
    pagina = item.funcargs.get("page") if hasattr(item, "funcargs") else None
    if informe.when == "call" and informe.failed and pagina is not None:
        carpeta = os.path.join(os.path.dirname(__file__), "artifacts")
        os.makedirs(carpeta, exist_ok=True)
        nombre = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in item.name)
        try:
            pagina.screenshot(path=os.path.join(carpeta, f"{nombre}.png"), full_page=True)
        except Exception:
            pass


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        navegador = p.chromium.launch(
            headless=os.environ.get("HEADED") != "1",
            slow_mo=int(os.environ.get("SLOWMO", "0")),
        )
        yield navegador
        navegador.close()


@pytest.fixture
def page(browser):
    contexto = browser.new_context(
        viewport={"width": 1600, "height": 1300},
        accept_downloads=True,
        locale="es-CO",
    )
    contexto.set_default_timeout(TIMEOUT_ACCION_MS)
    pagina = contexto.new_page()
    yield pagina
    contexto.close()


def _abrir_app(page):
    """
    Abre la URL y devuelve el 'contenedor' sobre el que se localizan los widgets:
      - en Streamlit Cloud la app vive dentro de un iframe -> FrameLocator
      - en local (o si la app no usa iframe) -> la propia Page
    Si la app estaba dormida, pulsa 'Yes, get this app back up!' y espera.
    """
    page.goto(APP_URL, wait_until="domcontentloaded")
    limite = time.time() + TIEMPO_ARRANQUE_S
    while time.time() < limite:
        despertar = page.get_by_role("button", name="Yes, get this app back up!")
        if despertar.count() and despertar.first.is_visible():
            despertar.first.click()
        contenedores = [page]
        if page.locator('iframe[title="streamlitApp"]').count():
            contenedores.insert(0, page.frame_locator('iframe[title="streamlitApp"]'))
        for c in contenedores:
            try:
                if c.get_by_role("heading", name=TITULO_APP).is_visible():
                    return c
            except Exception:
                pass
        page.wait_for_timeout(2000)
    pytest.fail(f"La app no cargo en {TIEMPO_ARRANQUE_S}s ({APP_URL})")


@pytest.fixture
def app(page):
    contenedor = _abrir_app(page)
    # La pagina ya esta; esperamos a que Streamlit termine el primer 'run'
    estado = contenedor.get_by_test_id("stStatusWidget")
    expect(estado).to_have_count(0, timeout=TIMEOUT_CALCULO_MS)
    return contenedor