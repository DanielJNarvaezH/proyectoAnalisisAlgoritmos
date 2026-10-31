"""
(Opcional) E2E del backend Flask. Solo corre si se define API_URL, p. ej.:
    API_URL=https://mi-backend.onrender.com pytest tests/e2e -m api
El README solo documenta el despliegue de Streamlit; este archivo cubre el caso
en que el backend tambien este publicado.
"""

import os

import pytest
import requests

import golden

API_URL = os.environ.get("API_URL", "").rstrip("/")
pytestmark = [pytest.mark.api,
              pytest.mark.skipif(not API_URL, reason="API_URL no definida")]


def get(ruta, **params):
    return requests.get(f"{API_URL}{ruta}", params=params, timeout=120)


def test_flujo_api_cuatro_modulos():
    arts = get("/articulos").json()
    assert len(arts) == golden.TOTAL_ARTICULOS

    top = get("/ranking", algoritmo="counting", top=5).json()
    assert [(r["termino"], r["frecuencia"]) for r in top["ranking"]] == golden.TOP5
    assert top["terminos_distintos"] == golden.TERMINOS_DISTINTOS
    for alg in ("radix", "bucket"):
        assert get("/ranking", algoritmo=alg, top=5).json()["ranking"] == top["ranking"]

    b = get("/busqueda", patron=top["ranking"][1]["termino"]).json()
    assert b["todas_coinciden"] is True
    assert b["total_ocurrencias"] == golden.BUSQUEDAS[("education", False)][0]
    elegidos = [a["numero"] for a in b["articulos"]][:3]

    s = get("/similitud", articulos=",".join(map(str, elegidos))).json()
    assert set(s["clasicos"]) == {"Levenshtein", "Needleman-Wunsch", "Coseno TF-IDF", "Jaccard"}
    assert set(s["ia"]) == set(golden.MODELOS_IA)

    for criterio in ("single", "complete", "average"):
        c = get("/clustering", criterio=criterio).json()
        assert len(c["matriz_enlace"]) == golden.TOTAL_ARTICULOS - 1
        assert -1.0 <= c["correlacion_cofenetica"] <= 1.0


@pytest.mark.parametrize("ruta,params", [
    ("/busqueda", {}), ("/clustering", {"criterio": "x"}),
    ("/ranking", {"algoritmo": "x"}), ("/ranking", {"top": "abc"}),
    ("/similitud", {"articulos": "1"}), ("/similitud", {"articulos": "1,999"}),
])
def test_api_rechaza_entradas_invalidas(ruta, params):
    r = get(ruta, **params)
    assert r.status_code == 400 and "error" in r.json()