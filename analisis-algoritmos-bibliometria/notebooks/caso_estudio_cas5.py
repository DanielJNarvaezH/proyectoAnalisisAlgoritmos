"""
CAS-5 / CAS-6 — Evidencia ejecutable del caso de estudio del R3
==============================================================

Reproduce, corriendo este script, los numeros y tablas documentados en
docs/caso_estudio_busqueda.md para el caso definido en CAS-4:
KMP y Rabin-Karp (CAS-5, secciones 2 y 3) y Boyer-Moore (CAS-6, seccion 4).

    patron  P = "education"  (m = 9)
    texto   T = frase continua del abstract original del articulo 17 (n = 117)

Las funciones traza_* repiten, linea por linea, el mismo procedimiento de
src/busqueda/kmp.py y src/busqueda/rabin_karp.py, pero guardando el estado
de cada paso (y lo mismo para src/busqueda/boyer_moore.py). Al final de
cada traza se comprueba con assert que el resultado (posiciones,
comparaciones, colisiones, saltos, tablas) es identico al de las
implementaciones reales, de modo que la tabla del documento corresponde
exactamente al codigo entregado.

Ejecutar desde la raiz del proyecto:
    .\\venv\\Scripts\\python.exe notebooks\\caso_estudio_cas5.py
    .\\venv\\Scripts\\python.exe notebooks\\caso_estudio_cas5.py --completo
(--completo imprime tambien la tabla de las 117 iteraciones de KMP y de las
109 ventanas de Rabin-Karp; sin el, solo se imprimen los pasos relevantes).
"""
import json
import os
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(RAIZ, "src", "busqueda"))

import boyer_moore  # noqa: E402
import kmp  # noqa: E402
import rabin_karp  # noqa: E402

RUTA_CORPUS = os.path.join(RAIZ, "data", "corpus_preprocesado.json")

# Caso de estudio definido en CAS-4
ARTICULO = 17
PATRON = "education"
FRAGMENTO = ("To gain an overview of the application of AI-driven educational "
             "assessment in STEM education, this research conducted")
BASE = 256          # d: tamano del alfabeto (bytes / ASCII extendido)
PRIMO_DEMO = 101    # q pequeno, elegido para que aparezcan colisiones
PRIMOS_CONTRASTE = (13, 101, rabin_karp.PRIMO)

# Mini ejemplo de Cormen et al. (2022, fig. 32.10) para una tabla pi no trivial
PATRON_CORMEN = "ababaca"
# Mini ejemplo de Boyer-Moore donde el sufijo bueno decide el salto
PATRON_BM_EJEMPLO = "abcab"
TEXTO_BM_EJEMPLO = "aaaabcab"


def cargar_fragmento():
    """Ubica el fragmento en el abstract original del articulo 17 usando KMP."""
    with open(RUTA_CORPUS, "r", encoding="utf-8") as f:
        corpus = json.load(f)
    abstract = next(a["abstract"] for a in corpus if a["numero"] == ARTICULO)
    inicio = kmp.buscar(abstract, FRAGMENTO)
    assert len(inicio) == 1, "El fragmento debe aparecer exactamente una vez"
    return abstract, inicio[0]


def visible(c):
    return "␣" if c == " " else c


# ---------------------------------------------------------------------------
# KMP
# ---------------------------------------------------------------------------

def traza_tabla_prefijos(patron):
    """Mismo ciclo que kmp.tabla_prefijos, guardando k y las comparaciones."""
    m = len(patron)
    pi = [0] * m
    pasos = []
    k = 0
    for q in range(1, m):
        k_inicial, comps = k, []
        while k > 0 and patron[k] != patron[q]:
            comps.append((k, q, False))
            k = pi[k - 1]
        coincide = patron[k] == patron[q]
        comps.append((k, q, coincide))
        if coincide:
            k += 1
        pi[q] = k
        pasos.append({"q": q, "car": patron[q], "k_inicial": k_inicial,
                      "comparaciones": comps, "pi": k})
    assert pi == kmp.tabla_prefijos(patron)
    return pi, pasos


def traza_kmp(texto, patron):
    """Mismo ciclo que kmp.buscar_con_estadisticas, guardando cada iteracion."""
    pi = kmp.tabla_prefijos(patron)
    n, m = len(texto), len(patron)
    filas, posiciones, total = [], [], 0
    q = 0
    for i in range(n):
        q_inicial, comps, evento = q, [], ""
        avanza = True
        while q > 0:
            comps.append((q, patron[q] == texto[i]))
            if patron[q] == texto[i]:
                break
            q = pi[q - 1]
        else:
            comps.append((0, patron[0] == texto[i]))
            if patron[0] != texto[i]:
                avanza = False
        if avanza:
            q += 1
            if q == m:
                posiciones.append(i - m + 1)
                evento = f"OCURRENCIA en s = {i - m + 1}"
                q = pi[q - 1]
        total += len(comps)
        filas.append({"i": i, "car": texto[i], "q_inicial": q_inicial,
                      "comparaciones": comps, "q_final": q, "evento": evento})
    oficial = kmp.buscar_con_estadisticas(texto, patron)
    assert posiciones == oficial["posiciones"] and total == oficial["comparaciones"]
    return filas, posiciones, total


def comparaciones_ingenuo(texto, patron):
    """Algoritmo ingenuo (solo para contrastar el numero de comparaciones)."""
    total = 0
    for s in range(len(texto) - len(patron) + 1):
        for j in range(len(patron)):
            total += 1
            if texto[s + j] != patron[j]:
                break
    return total


# ---------------------------------------------------------------------------
# Rabin-Karp
# ---------------------------------------------------------------------------

def traza_horner(cadena, base, primo):
    """Mismo calculo que rabin_karp.hash_polinomial, paso a paso."""
    h, pasos = 0, []
    for c in cadena:
        nuevo = (base * h + ord(c)) % primo
        pasos.append({"car": c, "ascii": ord(c), "h_anterior": h,
                      "bruto": base * h + ord(c), "h": nuevo})
        h = nuevo
    assert h == rabin_karp.hash_polinomial(cadena, base, primo)
    return h, pasos


def traza_rabin_karp(texto, patron, base, primo):
    """Mismo ciclo que rabin_karp.buscar_con_estadisticas, ventana por ventana."""
    n, m = len(texto), len(patron)
    h = rabin_karp.potencia_modular(base, m - 1, primo)
    p = rabin_karp.hash_polinomial(patron, base, primo)
    t = rabin_karp.hash_polinomial(texto[0:m], base, primo)
    filas, posiciones, colisiones, comparaciones = [], [], [], 0
    for s in range(n - m + 1):
        fila = {"s": s, "ventana": texto[s:s + m], "t": t, "resultado": ""}
        if t == p:
            coincide, hechas = True, 0
            for j in range(m):
                hechas += 1
                if texto[s + j] != patron[j]:
                    coincide = False
                    break
            comparaciones += hechas
            if coincide:
                posiciones.append(s)
                fila["resultado"] = f"hash igual, {hechas} comparaciones: OCURRENCIA"
            else:
                colisiones.append(s)
                fila["resultado"] = (f"hash igual, falla en j = {hechas - 1} "
                                     f"('{texto[s + hechas - 1]}' != '{patron[hechas - 1]}'): COLISION")
        if s < n - m:
            sale, entra = texto[s], texto[s + m]
            nuevo = rabin_karp.siguiente_hash(t, sale, entra, h, base, primo)
            fila.update({"sale": sale, "entra": entra,
                         "bruto": base * (t - ord(sale) * h) + ord(entra), "t_sig": nuevo})
            t = nuevo
        filas.append(fila)
    oficial = rabin_karp.buscar_con_estadisticas(texto, patron, base, primo)
    assert posiciones == oficial["posiciones"]
    assert colisiones == oficial["colisiones"]
    assert comparaciones == oficial["comparaciones"]
    # Comprobacion independiente: cada hash rodante = hash recalculado desde cero
    for fila in filas:
        assert fila["t"] == rabin_karp.hash_polinomial(fila["ventana"], base, primo)
    return {"h": h, "p": p, "filas": filas, "posiciones": posiciones,
            "colisiones": colisiones, "comparaciones": comparaciones}


# ---------------------------------------------------------------------------
# Boyer-Moore (CAS-6)
# ---------------------------------------------------------------------------

def traza_sufijo_bueno(patron):
    """Mismo procedimiento que boyer_moore.construir_sufijo_bueno, con eventos."""
    m = len(patron)
    desplazamientos = [0] * (m + 1)
    f = [0] * (m + 1)
    eventos = []
    i, j = m, m + 1
    f[i] = j
    while i > 0:
        while j <= m and patron[i - 1] != patron[j - 1]:
            if desplazamientos[j] == 0:
                desplazamientos[j] = j - i
                eventos.append(("caso1", i, j, patron[i - 1], patron[j - 1], j - i))
            else:
                eventos.append(("caso1_ya", i, j, patron[i - 1], patron[j - 1], None))
            j = f[j]
        if j <= m:
            eventos.append(("borde", i, j, patron[i - 1], patron[j - 1], None))
        i -= 1
        j -= 1
        f[i] = j
    f_caso1 = f[:]
    j = f[0]
    for i in range(m + 1):
        if desplazamientos[i] == 0:
            desplazamientos[i] = j
            eventos.append(("caso2", i, j, None, None, j))
        if i == j:
            j = f[j]
    assert desplazamientos == boyer_moore.construir_sufijo_bueno(patron)
    return desplazamientos, f_caso1, eventos


def traza_boyer_moore(texto, patron):
    """Mismo ciclo que boyer_moore.buscar_con_estadisticas, alineacion por alineacion."""
    malo = boyer_moore.construir_caracter_malo(patron)
    bueno = boyer_moore.construir_sufijo_bueno(patron)
    n, m = len(texto), len(patron)
    filas, posiciones, comparaciones, saltos_malo, saltos_bueno = [], [], 0, 0, 0
    s = 0
    while s <= n - m:
        j, hechas = m - 1, 0
        while j >= 0:
            hechas += 1
            if patron[j] != texto[s + j]:
                break
            j -= 1
        comparaciones += hechas
        fila = {"s": s, "ventana": texto[s:s + m], "comparaciones": hechas}
        if j < 0:
            posiciones.append(s)
            fila.update(j=None, car=None, salto_malo=None, salto_bueno=bueno[0],
                        salto=bueno[0], regla="ocurrencia")
        else:
            c = texto[s + j]
            sm, sb = j - malo.get(c, -1), bueno[j + 1]
            regla = "caracter malo" if sm >= sb else "sufijo bueno"
            if sm >= sb:
                saltos_malo += 1
            else:
                saltos_bueno += 1
            fila.update(j=j, car=c, salto_malo=sm, salto_bueno=sb, salto=max(sm, sb), regla=regla)
        s += fila["salto"]
        filas.append(fila)
    oficial = boyer_moore.buscar_con_estadisticas(texto, patron)
    assert posiciones == oficial["posiciones"]
    assert comparaciones == oficial["comparaciones"]
    assert saltos_malo == oficial["saltos_caracter_malo"]
    assert saltos_bueno == oficial["saltos_sufijo_bueno"]
    return filas, posiciones, comparaciones


def grafico_alineaciones(texto, patron, filas):
    """Texto con regla de indices y el patron debajo en cada alineacion."""
    margen = " " * 12
    marcas = [" "] * (len(texto) + 3)
    for i in range(0, len(texto), 10):
        for k, d in enumerate(str(i)):
            marcas[i + k] = d
    lineas = [margen + "".join(marcas).rstrip(), margen + "|" + "".join(
        "|" if i % 10 == 0 else "." for i in range(1, len(texto))), margen + texto]
    for k, f in enumerate(filas, 1):
        etiqueta = f"{k:>2} s={f['s']:>3}: "
        marca = "  OCURRENCIA" if f["regla"] == "ocurrencia" else f"  j={f['j']} '{f['car']}'"
        lineas.append(f"{etiqueta:<12}" + " " * f["s"] + patron
                      + " " * (len(texto) - f["s"] - len(patron) + 2) + f"+{f['salto']}{marca}")
    return "\n".join(lineas)


def imprimir_boyer_moore(texto, patron):
    print(f"\nTabla del caracter malo de {patron!r}: {boyer_moore.construir_caracter_malo(patron)}")
    d, f, eventos = traza_sufijo_bueno(patron)
    print(f"Sufijo bueno de {patron!r}: f tras el caso 1 = {f} | desplazamientos = {d}")
    for e in eventos:
        tipo, i, j, a, b, val = e
        if tipo == "caso1":
            print(f"  caso 1: i={i}, j={j}: P[{i-1}]='{a}' != P[{j-1}]='{b}' -> desplazamientos[{j}] = {j}-{i} = {val}")
        elif tipo == "caso1_ya":
            print(f"  caso 1: i={i}, j={j}: P[{i-1}]='{a}' != P[{j-1}]='{b}' (desplazamientos[{j}] ya asignado)")
        elif tipo == "borde":
            print(f"  caso 1: i={i}, j={j}: P[{i-1}]='{a}' == P[{j-1}]='{b}' -> el borde crece")
        else:
            print(f"  caso 2: desplazamientos[{i}] = {val}")
    filas, posiciones, total = traza_boyer_moore(texto, patron)
    for k, fl in enumerate(filas, 1):
        detalle = ("ocurrencia" if fl["regla"] == "ocurrencia" else
                   f"j={fl['j']} '{fl['car']}': malo={fl['salto_malo']}, bueno={fl['salto_bueno']} ({fl['regla']})")
        print(f"  {k:>2} s={fl['s']:>3} '{fl['ventana']}' comp={fl['comparaciones']} {detalle} -> +{fl['salto']}")
    print(f"Ocurrencias: {posiciones} | comparaciones: {total} | alineaciones: {len(filas)}")
    return filas


# ---------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------

def imprimir_pi(patron):
    pi, pasos = traza_tabla_prefijos(patron)
    print(f"\nTabla de prefijos de {patron!r}: {pi}")
    for p in pasos:
        comps = "; ".join(f"P[{k}]='{patron[k]}' vs P[{q}]='{patron[q]}' "
                          f"{'=' if ok else '!='}" for k, q, ok in p["comparaciones"])
        print(f"  q={p['q']} ('{p['car']}'): k={p['k_inicial']} | {comps} -> pi[{p['q']}]={p['pi']}")


def main():
    completo = "--completo" in sys.argv
    abstract, inicio = cargar_fragmento()
    T, P = FRAGMENTO, PATRON
    print("=== CAS-5: caso de estudio del R3 ===")
    print(f"Articulo {ARTICULO}: fragmento en abstract[{inicio}:{inicio + len(T)}] "
          f"(abstract de {len(abstract)} caracteres)")
    print(f"T = {T!r}\nn = {len(T)} | P = {P!r} | m = {len(P)}")

    # --- KMP ---
    print("\n--- KMP: preprocesamiento ---")
    imprimir_pi(P)
    imprimir_pi(PATRON_CORMEN)

    filas, posiciones, total = traza_kmp(T, P)
    print("\n--- KMP: recorrido (iteraciones con q > 0 o con ocurrencia) ---")
    for f in filas:
        if completo or f["q_inicial"] > 0 or f["q_final"] > 0 or f["evento"]:
            comps = ", ".join(f"P[{q}]{'=' if ok else '!='}" for q, ok in f["comparaciones"])
            print(f"  i={f['i']:>3} T[i]='{visible(f['car'])}' q={f['q_inicial']} | {comps} "
                  f"-> q={f['q_final']} {f['evento']}")
    extra = sum(len(f["comparaciones"]) - 1 for f in filas)
    print(f"Ocurrencias: {posiciones} | comparaciones: {total} = n ({len(T)}) + {extra} "
          f"| cota 2n = {2 * len(T)}")
    print(f"Ingenuo sobre el mismo texto: {comparaciones_ingenuo(T, P)} comparaciones")

    # --- Rabin-Karp ---
    print(f"\n--- Rabin-Karp: preprocesamiento (d = {BASE}, q = {PRIMO_DEMO}) ---")
    hp, pasos = traza_horner(P, BASE, PRIMO_DEMO)
    for i, p in enumerate(pasos):
        print(f"  {i}: '{p['car']}' ({p['ascii']}): ({BASE}*{p['h_anterior']} + {p['ascii']}) "
              f"= {p['bruto']} mod {PRIMO_DEMO} = {p['h']}")
    r = traza_rabin_karp(T, P, BASE, PRIMO_DEMO)
    print(f"h = {BASE}^{len(P) - 1} mod {PRIMO_DEMO} = {r['h']} | hash(P) = {r['p']}")
    t0, pasos0 = traza_horner(T[:len(P)], BASE, PRIMO_DEMO)
    print(f"hash de la primera ventana {T[:len(P)]!r}:")
    for i, p in enumerate(pasos0):
        print(f"  {i}: '{visible(p['car'])}' ({p['ascii']}): ({BASE}*{p['h_anterior']} + "
              f"{p['ascii']}) = {p['bruto']} mod {PRIMO_DEMO} = {p['h']}")

    print("\n--- Rabin-Karp: ventanas ---")
    for f in r["filas"]:
        relevante = f["resultado"] or f["s"] < 3 or f["s"] + 1 in r["colisiones"] + r["posiciones"]
        if completo or relevante:
            roll = (f" | sale '{visible(f['sale'])}', entra '{visible(f['entra'])}': "
                    f"{f['bruto']} mod {PRIMO_DEMO} = {f['t_sig']}") if "sale" in f else ""
            print(f"  s={f['s']:>3} '{f['ventana'].replace(' ', '␣')}' t={f['t']:>3}{roll} {f['resultado']}")
    print(f"Ocurrencias: {r['posiciones']} | colisiones: {r['colisiones']} | "
          f"comparaciones: {r['comparaciones']} | ventanas: {len(r['filas'])}")

    print("\n--- Rabin-Karp: efecto del modulo q ---")
    for q in PRIMOS_CONTRASTE:
        o = rabin_karp.buscar_con_estadisticas(T, P, BASE, q)
        print(f"  q = {q:>13,}: hash(P) = {o['hash_patron']:>11,} | ocurrencias {o['posiciones']} "
              f"| colisiones {len(o['colisiones'])} {o['colisiones']} | comparaciones {o['comparaciones']}")

    # --- Boyer-Moore ---
    print("\n--- Boyer-Moore (CAS-6): caso de estudio ---")
    filas = imprimir_boyer_moore(T, P)
    print("\nGrafico de alineaciones:")
    print(grafico_alineaciones(T, P, filas))
    print(f"\n--- Boyer-Moore: ejemplo complementario {PATRON_BM_EJEMPLO!r} en {TEXTO_BM_EJEMPLO!r} ---")
    imprimir_boyer_moore(TEXTO_BM_EJEMPLO, PATRON_BM_EJEMPLO)


if __name__ == "__main__":
    main()
