"""
Pruebas E2E por modulo sobre la aplicacion desplegada (Streamlit).

  Modulo 1  Similitud textual (4 algoritmos clasicos + 2 modelos de IA)
  Modulo 2  Clustering jerarquico (Single / Complete / Average) + dendrogramas
  Modulo 3  Busqueda de patrones (KMP, Rabin-Karp, Boyer-Moore)
  Modulo 4  Ranking de terminos (Counting, Radix, Bucket Sort)
"""

import re

import pytest
from playwright.sync_api import expect

import golden
from conftest import TIMEOUT_CALCULO_MS, TITULO_APP
from helpers import (buscar_patron, descargar_ranking, ejecutar_algoritmos, elegir_opcion,
                     esperar_listo, grupos_de_expander, ir_a_tab,
                     seleccionar_articulos, valores_heatmap, verificar_metrica)


# ===================================================================== humo
def test_la_app_carga_con_sus_cinco_pestanas(app):
    expect(app.get_by_role("heading", name=TITULO_APP)).to_be_visible()
    for nombre in ["Similitudes", "Dendrogramas", "Articulos", "Busqueda de patrones", "Ranking de terminos"]:
        expect(app.get_by_role("tab", name=re.compile(nombre))).to_be_visible()
    lateral = app.get_by_test_id("stSidebar")
    for modelo in golden.MODELOS_IA:
        expect(lateral).to_contain_text(modelo)


def test_pestanas_dependientes_piden_ejecutar_algoritmos(app):
    for nombre in ["Similitudes", "Dendrogramas", "Articulos"]:
        panel = ir_a_tab(app, nombre)
        expect(panel).to_contain_text("Ejecutar algoritmos")


# ================================================================ modulo 1
@pytest.mark.modulo1
def test_similitud_par_2_9_con_los_seis_algoritmos(app):
    seleccionar_articulos(app, [2, 9])
    ejecutar_algoritmos(app)
    panel = ir_a_tab(app, "Similitudes")
    expect(panel.get_by_role("heading", name="Articulo 2 vs articulo 9")).to_be_visible(
        timeout=TIMEOUT_CALCULO_MS)

    for nombre, esperado in golden.PAR_2_9.items():
        elegir_opcion(app, "Algoritmo / modelo", nombre)
        valores = valores_heatmap(app, 4)
        # matriz 2x2: diagonal + dos veces el valor del par (simetria)
        assert valores.count(esperado) == 2, f"{nombre}: esperaba {esperado} x2 en {valores}"


@pytest.mark.modulo1
def test_similitud_diagonal_unitaria_y_matriz_simetrica_con_tres_articulos(app):
    seleccionar_articulos(app, [1, 2, 3])
    ejecutar_algoritmos(app)
    panel = ir_a_tab(app, "Similitudes")
    elegir_opcion(app, "Algoritmo / modelo", "Coseno TF-IDF")
    valores = valores_heatmap(app, 9)
    diagonal = [valores[0], valores[4], valores[8]]
    assert diagonal == ["1.00"] * 3
    m = [valores[i * 3:(i + 1) * 3] for i in range(3)]
    assert all(m[i][j] == m[j][i] for i in range(3) for j in range(3))


@pytest.mark.modulo1
def test_similitud_exige_minimo_dos_articulos(app):
    seleccionar_articulos(app, [5])
    lateral = app.get_by_test_id("stSidebar")
    expect(lateral).to_contain_text("Selecciona al menos 2 articulos")
    expect(lateral.get_by_role("button", name="Ejecutar algoritmos")).to_be_disabled()


@pytest.mark.modulo1
def test_cambiar_la_seleccion_avisa_que_hay_que_reejecutar(app):
    seleccionar_articulos(app, [2, 9])
    ejecutar_algoritmos(app)
    seleccionar_articulos(app, [2, 9, 10])
    panel = ir_a_tab(app, "Similitudes")
    expect(panel).to_contain_text("La seleccion cambio desde la ultima ejecucion")


# ================================================================ modulo 2
@pytest.mark.modulo2
def test_dendrogramas_tres_criterios_y_particion_k4(app):
    ejecutar_algoritmos(app)  # los 20 articulos (seleccion por defecto)
    panel = ir_a_tab(app, "Dendrogramas")
    expect(panel.get_by_role("heading", name=re.compile("Evaluacion y particion en k = 4"))
           ).to_be_visible(timeout=TIMEOUT_CALCULO_MS)
    # un dendrograma (imagen matplotlib) por criterio de enlace
    expect(panel.get_by_test_id("stImage")).to_have_count(3)

    for criterio, esperado in golden.GRUPOS_K4.items():
        obtenido = grupos_de_expander(app, golden.TITULOS_CRITERIO[criterio])
        assert obtenido == esperado, f"{criterio}: {sorted(map(sorted, obtenido))}"
        assert sum(len(g) for g in obtenido) == golden.TOTAL_ARTICULOS


@pytest.mark.modulo2
def test_dendrograma_con_otra_matriz_base_y_un_solo_criterio(app):
    ejecutar_algoritmos(app)
    panel = ir_a_tab(app, "Dendrogramas")
    elegir_opcion(app, "Matriz base para el clustering", "MPNet - coseno")
    panel = ir_a_tab(app, "Dendrogramas")
    expect(panel.get_by_test_id("stImage")).to_have_count(3)

    # quitar Average y Complete (Backspace borra la ultima etiqueta): queda solo Single
    combo = panel.get_by_test_id("stMultiSelect").filter(has_text="Criterios de enlace").get_by_role("combobox")
    combo.click()
    for _ in range(2):
        combo.press("Backspace")
        esperar_listo(app)
    combo.press("Escape")
    expect(panel.get_by_test_id("stImage")).to_have_count(1)
    grupos = grupos_de_expander(app, "Single")
    assert sum(len(g) for g in grupos) == golden.TOTAL_ARTICULOS
    assert len(grupos) == 4


@pytest.mark.modulo2
def test_dendrograma_requiere_tres_articulos(app):
    seleccionar_articulos(app, [2, 9])
    ejecutar_algoritmos(app)
    panel = ir_a_tab(app, "Dendrogramas")
    expect(panel).to_contain_text("Un dendrograma necesita al menos 3 articulos")


# ================================================================ modulo 3
@pytest.mark.modulo3
@pytest.mark.parametrize("patron,ignorar", list(golden.BUSQUEDAS))
def test_busqueda_conteos_y_verificacion_cruzada(app, patron, ignorar):
    panel = ir_a_tab(app, "Busqueda de patrones")
    buscar_patron(app, panel, patron, ignorar)
    ocurrencias, articulos = golden.BUSQUEDAS[(patron, ignorar)]
    verificar_metrica(panel, "Ocurrencias totales", str(ocurrencias))
    verificar_metrica(panel, "Articulos con ocurrencias", f"{articulos} de {golden.TOTAL_ARTICULOS}")
    verificar_metrica(panel, "Verificacion cruzada", "Coinciden")
    expect(panel.get_by_text("Discrepancias en los articulos")).to_have_count(0)


@pytest.mark.modulo3
def test_busqueda_sin_resultados(app):
    panel = ir_a_tab(app, "Busqueda de patrones")
    buscar_patron(app, panel, golden.PATRON_SIN_RESULTADOS)
    verificar_metrica(panel, "Ocurrencias totales", "0")
    expect(panel).to_contain_text(f"El patron '{golden.PATRON_SIN_RESULTADOS}' no aparece en ningun abstract")


@pytest.mark.modulo3
def test_busqueda_resalta_ocurrencias_en_los_abstracts(app):
    panel = ir_a_tab(app, "Busqueda de patrones")
    buscar_patron(app, panel, "learning")
    detalle = panel.get_by_test_id("stExpander").filter(has_text=re.compile(r"\[\d+\] .* - \d+ ocurrencia"))
    expect(detalle.first).to_be_visible()
    assert detalle.count() == golden.BUSQUEDAS[("learning", False)][1]
    detalle.first.locator("summary").click()
    marcas = detalle.first.locator("mark")
    expect(marcas.first).to_be_visible()
    assert all(t == "learning" for t in marcas.all_inner_texts())


@pytest.mark.modulo3
def test_busqueda_vacia_muestra_indicacion(app):
    panel = ir_a_tab(app, "Busqueda de patrones")
    caja = panel.get_by_label("Patron a buscar")
    caja.fill("")
    caja.press("Enter")
    esperar_listo(app)
    expect(panel).to_contain_text("Escribe un patron para buscarlo en los abstracts")


# ================================================================ modulo 4
@pytest.mark.modulo4
def test_ranking_metricas_y_top5(app, page):
    panel = ir_a_tab(app, "Ranking de terminos")
    verificar_metrica(panel, "Terminos distintos", str(golden.TERMINOS_DISTINTOS))
    verificar_metrica(panel, "Tokens totales", str(golden.TOKENS_TOTALES))
    verificar_metrica(panel, "Frecuencia maxima", str(golden.FRECUENCIA_MAXIMA))
    ranking = descargar_ranking(page, panel)
    assert len(ranking) == golden.TERMINOS_DISTINTOS
    assert [(t, f) for _, t, f in ranking[:5]] == golden.TOP5
    # orden descendente por frecuencia y posiciones consecutivas
    frecs = [f for _, _, f in ranking]
    assert frecs == sorted(frecs, reverse=True)
    assert [p for p, _, _ in ranking] == list(range(1, len(ranking) + 1))
    assert sum(frecs) == golden.TOKENS_TOTALES


@pytest.mark.modulo4
def test_ranking_los_tres_algoritmos_producen_el_mismo_orden(app, page):
    panel = ir_a_tab(app, "Ranking de terminos")
    rankings = {}
    for nombre in golden.ALGORITMOS_RANKING:
        elegir_opcion(app, "Algoritmo de ordenamiento", nombre)
        panel = ir_a_tab(app, "Ranking de terminos")
        expect(panel).to_contain_text(f"Top 15 terminos - {nombre}")
        rankings[nombre] = descargar_ranking(page, panel)
    base = rankings["Counting Sort"]
    assert rankings["Radix Sort"] == base
    assert rankings["Bucket Sort"] == base
    # y la propia app lo confirma en su comparativa
    panel.get_by_test_id("stExpander").filter(has_text="Comparar los tres algoritmos").locator("summary").click()
    expect(panel.get_by_text("Los tres algoritmos producen exactamente el mismo ranking.")).to_be_visible()


@pytest.mark.modulo4
def test_ranking_consulta_de_un_termino(app):
    panel = ir_a_tab(app, "Ranking de terminos")
    caja = panel.get_by_label("Termino (o parte de el)")
    caja.fill("zzzzqq")
    caja.press("Enter")
    esperar_listo(app)
    expect(panel).to_contain_text("Ningun termino contiene 'zzzzqq'")