"""
CAS-5 — Evidencia ejecutable del caso de estudio del R3 (KMP y Rabin-Karp)
==========================================================================

Reproduce, corriendo este script, los numeros y tablas documentados en
docs/caso_estudio_busqueda.md (secciones 2 y 3) para el caso definido en
CAS-4:

    patron  P = "education"  (m = 9)
    texto   T = frase continua del abstract original del articulo 17 (n = 117)

Las funciones traza_* repiten, linea por linea, el mismo procedimiento de
src/busqueda/kmp.py y src/busqueda/rabin_karp.py, pero guardando el estado
de cada paso. Al final de cada traza se comprueba con assert que el
resultado (posiciones, comparaciones, colisiones, tablas) es identico al de
las implementaciones reales, de modo que la tabla del documento corresponde
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


if __name__ == "__main__":
    main()
