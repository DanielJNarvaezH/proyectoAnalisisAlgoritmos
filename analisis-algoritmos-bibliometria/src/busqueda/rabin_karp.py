"""
Algoritmo de Rabin-Karp (tarea BUS-3, Requerimiento 3)
======================================================

Busqueda de todas las ocurrencias exactas de un patron en un texto,
implementada desde cero (sin find(), index(), in ni expresiones regulares)
segun:

  - Karp, R. M. y Rabin, M. O. (1987). Efficient randomized pattern-matching
    algorithms. IBM Journal of Research and Development, 31(2), 249-260.
  - Cormen, T. H., Leiserson, C. E., Rivest, R. L. y Stein, C. (2022).
    Introduction to Algorithms (4.a ed.). MIT Press. Seccion 32.2
    (procedimiento RABIN-KARP-MATCHER).

Idea: en lugar de comparar el patron caracter a caracter contra cada ventana
del texto, se compara un NUMERO (hash) que resume cada cadena. Solo cuando
los hashes coinciden se verifican los caracteres.

1. Hash polinomial con aritmetica modular. Cada caracter c tiene un valor
   v(c) (su codigo, ord(c)). Una cadena s_0 s_1 ... s_{m-1} se interpreta como
   un numero en base d, reducido modulo un primo q:

       hash(s) = ( v(s_0)*d^(m-1) + v(s_1)*d^(m-2) + ... + v(s_{m-1}) ) mod q

   Se calcula con la regla de Horner: h = (d*h + v(c)) mod q, caracter por
   caracter, en O(m).

2. Rolling hash. El hash de la ventana siguiente se obtiene del anterior en
   O(1), quitando el caracter que sale y agregando el que entra:

       t_{s+1} = ( d * (t_s - v(T[s]) * h) + v(T[s+m]) ) mod q,
       con h = d^(m-1) mod q   (Cormen et al., 2022, ecuacion 32.2)

3. Verificacion. Si hash(ventana) == hash(patron), la ventana PUEDE ser una
   ocurrencia: como q es finito, dos cadenas distintas pueden tener el mismo
   hash (una COLISION o "spurious hit"). Por eso se verifica caracter a
   caracter; si no coinciden, se cuenta como colision y se descarta.

Complejidad (Cormen et al., 2022, sec. 32.2):
  - Preprocesamiento: O(m) para el hash del patron, el de la primera ventana
    y h = d^(m-1) mod q.
  - Busqueda: O(n - m + 1) actualizaciones del rolling hash, mas O(m) por
    cada verificacion. En el caso esperado, con q grande y pocas colisiones,
    el tiempo es O(n + m) (mas O(m) por cada ocurrencia real). En el peor
    caso, si todas las ventanas coinciden en hash, es O((n - m + 1) * m).
  - Memoria adicional: O(1), aparte de la lista de resultados.

Parametros por defecto: d = 256 y q = 1.000.000.007 (primo), para que las
colisiones sean muy improbables. Un q pequeno (por ejemplo, 13) produce
colisiones a proposito, util para el caso de estudio (CAS-5).

Uso (desde la raiz del proyecto):

    .\\venv\\Scripts\\python.exe src\\busqueda\\rabin_karp.py "learning"
    .\\venv\\Scripts\\python.exe src\\busqueda\\rabin_karp.py "learning" 13
"""

import json
import os
import sys

RAIZ_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUTA_CORPUS = os.path.join(RAIZ_PROYECTO, "data", "corpus_preprocesado.json")

BASE = 256
PRIMO = 1_000_000_007


def _validar(texto, patron, base, primo):
    if not isinstance(texto, str) or not isinstance(patron, str):
        raise TypeError("El texto y el patron deben ser cadenas")
    if len(patron) == 0:
        raise ValueError("El patron no puede estar vacio")
    if not isinstance(base, int) or base < 2:
        raise ValueError("La base debe ser un entero mayor o igual a 2")
    if not isinstance(primo, int) or primo < 2:
        raise ValueError("El modulo debe ser un entero mayor o igual a 2")


# ---------------------------------------------------------------------------
# 1. Hash polinomial y potencia modular (implementados a mano)
# ---------------------------------------------------------------------------

def hash_polinomial(cadena, base=BASE, primo=PRIMO, valor=ord):
    """Hash de una cadena por la regla de Horner: h = (base*h + v(c)) mod primo."""
    h = 0
    for c in cadena:
        h = (base * h + valor(c)) % primo
    return h


def potencia_modular(base, exponente, primo):
    """base^exponente mod primo, multiplicando y reduciendo en cada paso."""
    resultado = 1 % primo
    for _ in range(exponente):
        resultado = (resultado * base) % primo
    return resultado


def siguiente_hash(hash_actual, sale, entra, h, base=BASE, primo=PRIMO, valor=ord):
    """
    Rolling hash: hash de la ventana siguiente a partir de la actual.
    t' = (base * (t - v(sale) * h) + v(entra)) mod primo
    En Python, % siempre da un resultado no negativo, asi que la resta no
    deja valores negativos.
    """
    return (base * (hash_actual - valor(sale) * h) + valor(entra)) % primo


# ---------------------------------------------------------------------------
# 2. Busqueda
# ---------------------------------------------------------------------------

def buscar_con_estadisticas(texto, patron, base=BASE, primo=PRIMO, valor=ord):
    """
    Busqueda Rabin-Karp con estadisticas para el analisis (BUS-5, CAS-5).

    Retorna un diccionario con:
      - posiciones: indices (desde 0) donde empieza cada ocurrencia, en orden;
        incluye ocurrencias que se solapan
      - colisiones: posiciones donde el hash coincidio pero los caracteres no
      - comparaciones: comparaciones de caracteres hechas al verificar
      - ventanas: cantidad de ventanas evaluadas (n - m + 1)
      - hash_patron: hash del patron
    """
    _validar(texto, patron, base, primo)
    n, m = len(texto), len(patron)
    resultado = {"posiciones": [], "colisiones": [], "comparaciones": 0,
                 "ventanas": max(0, n - m + 1), "hash_patron": None}
    if m > n:
        resultado["hash_patron"] = hash_polinomial(patron, base, primo, valor)
        return resultado

    # Preprocesamiento: O(m)
    h = potencia_modular(base, m - 1, primo)
    p = hash_polinomial(patron, base, primo, valor)
    t = hash_polinomial(texto[0:m], base, primo, valor)
    resultado["hash_patron"] = p

    for s in range(n - m + 1):
        if t == p:
            # Verificacion caracter a caracter para descartar colisiones
            coincide = True
            for j in range(m):
                resultado["comparaciones"] += 1
                if texto[s + j] != patron[j]:
                    coincide = False
                    break
            if coincide:
                resultado["posiciones"].append(s)
            else:
                resultado["colisiones"].append(s)
        if s < n - m:
            t = siguiente_hash(t, texto[s], texto[s + m], h, base, primo, valor)
    return resultado


def buscar(texto, patron, base=BASE, primo=PRIMO):
    """Posiciones (desde 0) de todas las ocurrencias de patron en texto."""
    return buscar_con_estadisticas(texto, patron, base, primo)["posiciones"]


# ---------------------------------------------------------------------------
# 3. Demostracion sobre los abstracts del corpus
# ---------------------------------------------------------------------------

def main():
    patron = sys.argv[1] if len(sys.argv) > 1 else "learning"
    primo = int(sys.argv[2]) if len(sys.argv) > 2 else PRIMO
    print("=== [BUS-3] RABIN-KARP ===")
    print(f"Patron: {patron!r} (m = {len(patron)}) | base d = {BASE} | modulo q = {primo}")
    print(f"Hash del patron: {hash_polinomial(patron, BASE, primo)}\n")

    with open(RUTA_CORPUS, "r", encoding="utf-8") as archivo:
        corpus = json.load(archivo)

    total, colisiones, comparaciones = 0, 0, 0
    print("Ocurrencias en el abstract original (distingue mayusculas):")
    for articulo in corpus:
        r = buscar_con_estadisticas(articulo["abstract"], patron, BASE, primo)
        total += len(r["posiciones"])
        colisiones += len(r["colisiones"])
        comparaciones += r["comparaciones"]
        if r["posiciones"] or r["colisiones"]:
            extra = f" | colisiones en {r['colisiones']}" if r["colisiones"] else ""
            print(f"  Art. {articulo['numero']:>2}: {len(r['posiciones'])} "
                  f"en {r['posiciones']}{extra}")
    print(f"\nTotal: {total} ocurrencias y {colisiones} colisiones en {len(corpus)} abstracts")
    print(f"Comparaciones de caracteres (solo en verificaciones): {comparaciones}")


if __name__ == "__main__":
    main()
