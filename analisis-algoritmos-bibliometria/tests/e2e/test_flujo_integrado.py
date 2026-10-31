"""
Flujo integrado de los cuatro modulos en UNA sola sesion de usuario.

  4. Ranking  -> el usuario descubre el termino mas frecuente (tras 'ai')
  3. Busqueda -> localiza ese termino en los abstracts (KMP/RK/BM coinciden)
  1. Similitud -> compara 3 de los articulos que lo contienen (6 algoritmos)
  2. Clustering -> agrupa esos mismos articulos y dibuja los dendrogramas

Lo que sale de un modulo alimenta al siguiente, de modo que se comprueba la
coherencia de extremo a extremo y no solo cada pieza por separado.
"""

import re

import pytest
from playwright.sync_api import expect

import golden
from conftest import TIMEOUT_CALCULO_MS
from helpers import (buscar_patron, descargar_ranking, ejecutar_algoritmos, elegir_opcion,
                     grupos_de_expander, ir_a_tab, seleccionar_articulos,
                     valores_heatmap, verificar_metrica)


@pytest.mark.flujo
def test_flujo_completo_ranking_busqueda_similitud_clustering(app, page):
    # ---- Modulo 4: ranking --------------------------------------------------
    panel = ir_a_tab(app, "Ranking de terminos")
    elegir_opcion(app, "Algoritmo de ordenamiento", "Radix Sort")
    panel = ir_a_tab(app, "Ranking de terminos")
    ranking = descargar_ranking(page, panel)
    assert [(t, f) for _, t, f in ranking[:5]] == golden.TOP5
    termino = ranking[1][1]                      # 2.o termino: 'education'
    assert termino == "education"

    # ---- Modulo 3: busqueda del termino ------------------------------------
    panel = ir_a_tab(app, "Busqueda de patrones")
    buscar_patron(app, panel, termino)
    ocurrencias, con_ocurrencias = golden.BUSQUEDAS[(termino, False)]
    verificar_metrica(panel, "Ocurrencias totales", str(ocurrencias))
    verificar_metrica(panel, "Verificacion cruzada", "Coinciden")
    # numeros de articulo que contienen el termino, leidos de los expanders
    resumenes = panel.get_by_test_id("stExpander").filter(
        has_text=re.compile(r"\[\d+\] .* - \d+ ocurrencia")).locator("summary").all_inner_texts()
    articulos = [int(re.search(r"\[(\d+)\]", r).group(1)) for r in resumenes]
    assert len(articulos) == con_ocurrencias
    elegidos = articulos[:3]

    # ---- Modulo 1: similitud entre esos articulos ---------------------------
    seleccionar_articulos(app, elegidos)
    ejecutar_algoritmos(app)
    panel = ir_a_tab(app, "Similitudes")
    for nombre in ["Levenshtein", "Needleman-Wunsch", "Coseno TF-IDF", "Jaccard",
                   "Word2Vec - coseno", "MPNet - coseno"]:
        elegir_opcion(app, "Algoritmo / modelo", nombre)
        valores = valores_heatmap(app, 9)
        assert [valores[0], valores[4], valores[8]] == ["1.00"] * 3, nombre
        assert all(0.0 <= float(v) <= 1.0 for v in valores), nombre

    # la pestana Articulos muestra exactamente los elegidos
    panel = ir_a_tab(app, "Articulos")
    for n in elegidos:
        expect(panel.get_by_test_id("stExpander").filter(has_text=re.compile(rf"\[{n}\] "))).to_have_count(1)
    expect(panel.get_by_test_id("stExpander")).to_have_count(len(elegidos))

    # ---- Modulo 2: clustering de esos mismos articulos ----------------------
    panel = ir_a_tab(app, "Dendrogramas")
    expect(panel.get_by_role("heading", name=re.compile("Evaluacion y particion en k = 2"))
           ).to_be_visible(timeout=TIMEOUT_CALCULO_MS)
    expect(panel.get_by_test_id("stImage")).to_have_count(3)
    for criterio in golden.GRUPOS_K4:
        grupos = grupos_de_expander(app, golden.TITULOS_CRITERIO[criterio])
        assert len(grupos) == 2                                   # k = 2 con 3 articulos
        assert set().union(*grupos) == set(elegidos)              # misma poblacion de entrada

    # ---- Vuelta al modulo 4: el ranking sigue intacto tras todo el flujo ---
    panel = ir_a_tab(app, "Ranking de terminos")
    verificar_metrica(panel, "Terminos distintos", str(golden.TERMINOS_DISTINTOS))


@pytest.mark.flujo
def test_busqueda_y_ranking_no_dependen_de_la_seleccion_lateral(app, page):
    """Con solo 2 articulos seleccionados, R3 y el ranking siguen usando los 20."""
    seleccionar_articulos(app, [2, 9])
    ejecutar_algoritmos(app)
    panel = ir_a_tab(app, "Busqueda de patrones")
    buscar_patron(app, panel, "education")
    verificar_metrica(panel, "Articulos con ocurrencias", "18 de 20")
    panel = ir_a_tab(app, "Ranking de terminos")
    verificar_metrica(panel, "Tokens totales", str(golden.TOKENS_TOTALES))