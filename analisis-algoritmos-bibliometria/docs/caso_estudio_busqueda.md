# Caso de Estudio — Búsqueda de Patrones (Requerimiento 3)

Este documento contiene el caso de estudio práctico del Requerimiento 3:
la selección del patrón y del texto (CAS-4), la demostración paso a paso de
KMP y Rabin-Karp (CAS-5) y la de Boyer-Moore (CAS-6). Todos los números de
las secciones 2 y 3 se reproducen con:

```
.\venv\Scripts\python.exe notebooks\caso_estudio_cas5.py            # pasos relevantes
.\venv\Scripts\python.exe notebooks\caso_estudio_cas5.py --completo # todas las iteraciones
```

El script repite el procedimiento de `src/busqueda/kmp.py` y
`src/busqueda/rabin_karp.py` guardando el estado de cada paso, y comprueba con
`assert` que posiciones, comparaciones, colisiones y tablas son idénticas a
las que producen las implementaciones entregadas.

---

## 1. Selección del caso de estudio (CAS-4)

### 1.1 Criterio de búsqueda

* **Texto de búsqueda:** el `abstract` **original** de cada artículo, no el
  preprocesado. El preprocesamiento elimina *stopwords*, signos y aplica
  lematización, de modo que una búsqueda de coincidencia **exacta** sobre él
  no correspondería al texto que el usuario ve en el artículo.
* **Mayúsculas:** se distinguen (comparación carácter a carácter con `==`),
  igual que en los `main()` de los tres algoritmos. Con este criterio el
  patrón `education` aparece **78 veces** en los 20 abstracts.
* **Posiciones:** índices desde 0 **dentro de cada abstract** (no de un texto
  concatenado).

### 1.2 Patrón

| Patrón $P$ | Longitud $m$ | Ocurrencias en el corpus | Artículo con más ocurrencias |
|---|---|---|---|
| `education` | 9 | 78 en 20 abstracts | Artículo 17: 15 ocurrencias |

En el artículo 17 las 15 ocurrencias están en las posiciones 86, 111, 367,
414, 485, 516, 746, 827, 1177, 1218, 1278, 1309, 1379, 1477 y 1508 de su
abstract (1518 caracteres).

### 1.3 Texto: fragmento del abstract del artículo 17

El abstract completo (1518 caracteres, 15 ocurrencias) exige 1658
comparaciones en KMP y 1510 ventanas de hash en Rabin-Karp, lo que no es
demostrable a mano. Por eso, igual que en el caso de estudio del R1
(`caso_estudio_clasicos.md`, sección 2), para la demostración se usa una
**frase real y continua** del abstract, sin modificar:

> To gain an overview of the application of AI-driven educational assessment in STEM education, this research conducted

| Dato | Valor |
|---|---|
| Ubicación en el abstract del artículo 17 | caracteres 433 a 549 (`abstract[433:550]`) |
| Longitud $n$ | 117 caracteres |
| Ocurrencias de `education` en el fragmento | 2, en las posiciones **52** (`educational`) y **83** (`education`) |
| Posiciones equivalentes en el abstract completo | 485 y 516 (433 + 52, 433 + 83) |

Índices de los caracteres alrededor de las ocurrencias:

```
i:  49 50 51 52 53 54 55 56 57 58 59 60 61 62 ...  82 83 84 85 86 87 88 89 90 91 92
T:   e  n  ␣  e  d  u  c  a  t  i  o  n  a  l  ...   ␣  e  d  u  c  a  t  i  o  n  ,
```

### 1.4 Justificación

* **Patrón del dominio.** `education` es uno de los términos centrales del
  corpus (IA generativa aplicada a la educación) y el artículo 17 es el que
  más lo contiene, así que el caso es representativo del uso real de la
  búsqueda.
* **Texto auténtico y demostrable.** Es una sola frase del abstract, sin
  recortes ni uniones, y su tamaño ($n = 117$) permite seguir cada iteración.
* **Dos ocurrencias de naturaleza distinta.** Una dentro de otra palabra
  (`educational`) y una como palabra completa, lo que muestra que la
  coincidencia es de cadenas, no de palabras.
* **Coincidencias parciales.** El texto tiene 11 letras `e`, de las cuales 9
  no inician una ocurrencia; en KMP 8 de ellas producen coincidencias
  parciales seguidas de fallo y la última deja una coincidencia abierta al
  final del texto (sección 2.4). En Boyer-Moore ponen a prueba la regla del
  carácter malo.
* **Colisiones observables en Rabin-Karp.** Con el módulo de demostración
  $q = 101$ el fragmento produce exactamente **2 colisiones** (ventanas 18 y
  65), suficientes para mostrar la verificación sin volver ilegible la tabla;
  con el módulo de producción $q = 1\,000\,000\,007$ no hay ninguna
  (sección 3.8).
* **Limitación reconocida.** Las 9 letras de `education` son distintas, de
  modo que su tabla de prefijos es toda ceros. Para mostrar también cómo KMP
  retrocede dentro del patrón, la sección 2.3 añade el ejemplo clásico
  `ababaca` (Cormen et al., 2022, fig. 32.10).

---

## 2. Knuth-Morris-Pratt (CAS-5)

### 2.1 Idea

El algoritmo ingenuo, cuando falla, vuelve atrás en el texto y repite
comparaciones. KMP **nunca retrocede en el texto**: mantiene $q$, la
cantidad de caracteres del patrón que coinciden hasta ahora, y cuando falla
consulta la tabla de prefijos $\pi$ para saber cuánto del patrón sigue
coincidiendo sin volver a leer el texto.

$$\pi[q] = \text{longitud del prefijo propio más largo de } P[0..q] \text{ que también es sufijo de } P[0..q]$$

### 2.2 Preprocesamiento: tabla de prefijos de `education`

Procedimiento (`kmp.tabla_prefijos`): $k$ es la longitud del prefijo que
coincide; para cada $q = 1, \dots, m-1$, mientras $k > 0$ y
$P[k] \ne P[q]$ se hace $k \leftarrow \pi[k-1]$; si $P[k] = P[q]$ se
incrementa $k$; finalmente $\pi[q] = k$.

| $q$ | $P[q]$ | $k$ al entrar | Comparación | $\pi[q]$ |
|---|---|---|---|---|
| 0 | e | — | (por definición) | 0 |
| 1 | d | 0 | $P[0]=$`e` vs `d`: ≠ | 0 |
| 2 | u | 0 | `e` vs `u`: ≠ | 0 |
| 3 | c | 0 | `e` vs `c`: ≠ | 0 |
| 4 | a | 0 | `e` vs `a`: ≠ | 0 |
| 5 | t | 0 | `e` vs `t`: ≠ | 0 |
| 6 | i | 0 | `e` vs `i`: ≠ | 0 |
| 7 | o | 0 | `e` vs `o`: ≠ | 0 |
| 8 | n | 0 | `e` vs `n`: ≠ | 0 |

$$\pi_{\texttt{education}} = [0, 0, 0, 0, 0, 0, 0, 0, 0] \qquad (m - 1 = 8 \text{ comparaciones})$$

Como `e` no vuelve a aparecer en el patrón, ningún prefijo propio es a la
vez sufijo. Consecuencia para la búsqueda: ante cualquier fallo con $q > 0$,
$q$ vuelve a $\pi[q-1] = 0$ y solo se compara el carácter actual con `e`.

### 2.3 Ejemplo complementario: tabla de prefijos de `ababaca`

| $q$ | $P[q]$ | $k$ al entrar | Comparaciones | $\pi[q]$ |
|---|---|---|---|---|
| 1 | b | 0 | $P[0]=$`a` vs `b`: ≠ | 0 |
| 2 | a | 0 | $P[0]=$`a` vs `a`: = → $k=1$ | 1 |
| 3 | b | 1 | $P[1]=$`b` vs `b`: = → $k=2$ | 2 |
| 4 | a | 2 | $P[2]=$`a` vs `a`: = → $k=3$ | 3 |
| 5 | c | 3 | $P[3]=$`b` vs `c`: ≠ → $k=\pi[2]=1$; $P[1]=$`b` vs `c`: ≠ → $k=\pi[0]=0$; $P[0]=$`a` vs `c`: ≠ | 0 |
| 6 | a | 0 | $P[0]=$`a` vs `a`: = → $k=1$ | 1 |

$$\pi_{\texttt{ababaca}} = [0, 0, 1, 2, 3, 0, 1]$$

La fila $q = 5$ muestra la cadena de retrocesos $k = 3 \to 1 \to 0$: la
misma tabla en construcción se usa para no reexaminar caracteres. Si al
buscar `ababaca` se hubieran reconocido `ababa` ($q = 5$) y el siguiente
carácter del texto no fuera `c`, KMP continuaría con $q = \pi[4] = 3$, es
decir, conservaría `aba` como prefijo ya reconocido en lugar de volver a
empezar.

### 2.4 Recorrido sobre el texto

Procedimiento (`kmp.buscar_con_estadisticas`) para cada $i = 0, \dots, n-1$:

1. Mientras $q > 0$: comparar $P[q]$ con $T[i]$; si coinciden, salir; si no,
   $q \leftarrow \pi[q-1]$.
2. Si $q = 0$: comparar $P[0]$ con $T[i]$; si no coinciden, pasar a $i + 1$.
3. $q \leftarrow q + 1$; si $q = m$, reportar ocurrencia en $s = i - m + 1$ y
   hacer $q \leftarrow \pi[m-1]$.

De las 117 iteraciones, **81** son triviales: $q = 0$, $T[i] \ne$ `e`, una
sola comparación y $q$ sigue en 0. Las **36** restantes son:

| $i$ | $T[i]$ | $q$ al entrar | Comparaciones | $q$ al salir | Evento |
|---|---|---|---|---|---|
| 13 | e | 0 | $P[0]$ = | 1 | inicia coincidencia (`overview`) |
| 14 | r | 1 | $P[1]$ ≠, $P[0]$ ≠ | 0 | fallo: $q \leftarrow \pi[0] = 0$ |
| 17 | e | 0 | $P[0]$ = | 1 | (`overview`) |
| 18 | w | 1 | $P[1]$ ≠, $P[0]$ ≠ | 0 | fallo |
| 25 | e | 0 | $P[0]$ = | 1 | (`the`) |
| 26 | ␣ | 1 | $P[1]$ ≠, $P[0]$ ≠ | 0 | fallo |
| 49 | e | 0 | $P[0]$ = | 1 | (`driven`) |
| 50 | n | 1 | $P[1]$ ≠, $P[0]$ ≠ | 0 | fallo |
| 52 | e | 0 | $P[0]$ = | 1 | |
| 53 | d | 1 | $P[1]$ = | 2 | |
| 54 | u | 2 | $P[2]$ = | 3 | |
| 55 | c | 3 | $P[3]$ = | 4 | |
| 56 | a | 4 | $P[4]$ = | 5 | |
| 57 | t | 5 | $P[5]$ = | 6 | |
| 58 | i | 6 | $P[6]$ = | 7 | |
| 59 | o | 7 | $P[7]$ = | 8 | |
| 60 | n | 8 | $P[8]$ = | 9 → $\pi[8] = 0$ | **ocurrencia en $s = 52$** |
| 67 | e | 0 | $P[0]$ = | 1 | (`assessment`) |
| 68 | s | 1 | $P[1]$ ≠, $P[0]$ ≠ | 0 | fallo |
| 71 | e | 0 | $P[0]$ = | 1 | (`assessment`) |
| 72 | n | 1 | $P[1]$ ≠, $P[0]$ ≠ | 0 | fallo |
| 83 | e | 0 | $P[0]$ = | 1 | |
| 84–90 | d u c a t i o | 1 → 7 | $P[1..7]$ =, una por carácter | 2 → 8 | |
| 91 | n | 8 | $P[8]$ = | 9 → $\pi[8] = 0$ | **ocurrencia en $s = 83$** |
| 100 | e | 0 | $P[0]$ = | 1 | (`research`) |
| 101 | s | 1 | $P[1]$ ≠, $P[0]$ ≠ | 0 | fallo |
| 102 | e | 0 | $P[0]$ = | 1 | (`research`) |
| 103 | a | 1 | $P[1]$ ≠, $P[0]$ ≠ | 0 | fallo |
| 115 | e | 0 | $P[0]$ = | 1 | (`conducted`) |
| 116 | d | 1 | $P[1]$ = | 2 | fin del texto con $q = 2$ |

(Las filas 84–90 agrupan 7 iteraciones idénticas en estructura a las 53–59.)

Observaciones:

* El índice $i$ **solo avanza**: nunca se vuelve a leer un carácter del texto.
  En el fallo de $i = 14$, por ejemplo, el algoritmo ingenuo volvería a
  $i = 14$ para probar la alineación $s = 14$; KMP sabe por $\pi[0] = 0$ que
  la `e` de $i = 13$ no puede iniciar otra coincidencia dentro de lo ya leído
  y solo vuelve a comparar $T[14]$ con $P[0]$.
* Tras cada ocurrencia, $q \leftarrow \pi[8] = 0$: como no hay borde, dos
  ocurrencias de `education` no pueden solaparse.
* El texto termina con $q = 2$ (`ed` de `conducted`): la coincidencia parcial
  queda abierta pero no hay más caracteres.

### 2.5 Conteo de comparaciones

| Concepto | Comparaciones |
|---|---|
| Iteraciones triviales (81 × 1) | 81 |
| Iteraciones con $P[0]$ = o $P[q]$ = (28 × 1) | 28 |
| Coincidencias parciales con fallo (8 × 2) | 16 |
| **Total búsqueda** | **125** $= n + 8$ |
| Preprocesamiento (tabla $\pi$) | 8 $= m - 1$ |

La búsqueda cumple la cota del análisis amortizado, $125 \le 2n = 234$:
cada comparación o avanza $i$, o hace bajar $q$, y $q$ no puede bajar más
veces de las que subió. El total es $\Theta(n + m)$ independientemente del
contenido.

Como contraste, el algoritmo ingenuo sobre el mismo texto hace **133**
comparaciones. La diferencia es pequeña porque `education` no tiene bordes
(no hay solapamientos que aprovechar) y el texto en inglés rara vez
coincide más de un carácter con el patrón; la ventaja de KMP en este caso
es la **garantía**: su costo no puede degradarse a $O(nm)$ aunque el texto
sea adverso, cosa que sí le ocurre al ingenuo. El análisis comparativo
completo con tiempos medidos está en BUS-5 (`analisis_busqueda.md`).

---

## 3. Rabin-Karp (CAS-5)

### 3.1 Idea y parámetros

Rabin-Karp compara **números** en lugar de cadenas: interpreta cada ventana
de $m$ caracteres como un número en base $d$, reducido módulo un primo $q$.
Si el hash de la ventana es distinto del hash del patrón, la ventana se
descarta con una sola comparación entera; si es igual, se verifica carácter
a carácter, porque dos cadenas distintas pueden tener el mismo hash
(**colisión**).

$$\text{hash}(S) = \left(\sum_{j=0}^{m-1} v(S_j)\, d^{\,m-1-j}\right) \bmod q, \qquad v(c) = \text{código ASCII de } c$$

| Parámetro | Valor | Motivo |
|---|---|---|
| $d$ (base) | 256 | tamaño del alfabeto de bytes (`BASE` en `rabin_karp.py`) |
| $q$ (módulo) en la demostración | **101** | primo pequeño: produce colisiones observables y números verificables a mano |
| $q$ en producción | 1 000 000 007 | primo grande (`PRIMO`): colisiones muy improbables |

### 3.2 Preprocesamiento (1): hash del patrón por la regla de Horner

$h_{j+1} = (d \cdot h_j + v(P_j)) \bmod q$, con $h_0 = 0$:

| $j$ | $P_j$ | $v(P_j)$ | $256 \cdot h_j + v(P_j)$ | $\bmod 101$ |
|---|---|---|---|---|
| 0 | e | 101 | $256 \cdot 0 + 101 = 101$ | 0 |
| 1 | d | 100 | $256 \cdot 0 + 100 = 100$ | 100 |
| 2 | u | 117 | $256 \cdot 100 + 117 = 25\,717$ | 63 |
| 3 | c | 99 | $256 \cdot 63 + 99 = 16\,227$ | 67 |
| 4 | a | 97 | $256 \cdot 67 + 97 = 17\,249$ | 79 |
| 5 | t | 116 | $256 \cdot 79 + 116 = 20\,340$ | 39 |
| 6 | i | 105 | $256 \cdot 39 + 105 = 10\,089$ | 90 |
| 7 | o | 111 | $256 \cdot 90 + 111 = 23\,151$ | 22 |
| 8 | n | 110 | $256 \cdot 22 + 110 = 5\,742$ | **86** |

$$p = \text{hash}(\texttt{education}) = 86$$

(Curiosidad del caso: el código ASCII de `e` es 101, igual al módulo, por eso
el primer paso da 0.)

### 3.3 Preprocesamiento (2): factor $h = d^{\,m-1} \bmod q$

`potencia_modular` multiplica y reduce en cada paso para no generar números
grandes:

| Paso | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| $r \cdot 256$ | 256 | 13 824 | 22 528 | 1 280 | 17 408 | 9 216 | 6 400 | 9 472 |
| $\bmod 101$ | 54 | 88 | 5 | 68 | 36 | 25 | 37 | **79** |

$$h = 256^8 \bmod 101 = 79$$

$h$ es el peso del carácter que sale de la ventana.

### 3.4 Preprocesamiento (3): hash de la primera ventana `To␣gain␣a`

| $j$ | $T_j$ | $v$ | $256 \cdot t_j + v$ | $\bmod 101$ |
|---|---|---|---|---|
| 0 | T | 84 | 84 | 84 |
| 1 | o | 111 | 21 615 | 1 |
| 2 | ␣ | 32 | 288 | 86 |
| 3 | g | 103 | 22 119 | 0 |
| 4 | a | 97 | 97 | 97 |
| 5 | i | 105 | 24 937 | 91 |
| 6 | n | 110 | 23 406 | 75 |
| 7 | ␣ | 32 | 19 232 | 42 |
| 8 | a | 97 | 10 849 | **42** |

$t_0 = 42 \ne p = 86$: la ventana $s = 0$ se descarta sin comparar caracteres.

El preprocesamiento completo cuesta $O(m)$: tres recorridos de 9 pasos.

### 3.5 Rolling hash: actualización iterativa

En lugar de recalcular cada ventana en $O(m)$, se obtiene la siguiente en
$O(1)$ quitando el carácter que sale y agregando el que entra
(Cormen et al., 2022, ec. 32.2):

$$t_{s+1} = \big(d\,(t_s - v(T_s)\cdot h) + v(T_{s+m})\big) \bmod q$$

**Ejemplo 1, de $s = 0$ a $s = 1$** (sale `T`, entra `n`):

$$t_1 = \big(256\,(42 - 84 \cdot 79) + 110\big) \bmod 101 = (256 \cdot (-6\,594) + 110) \bmod 101 = -1\,687\,954 \bmod 101 = 59$$

Comprobación: $\text{hash}(\texttt{o␣gain␣an})$ calculado desde cero con
Horner también da 59.

**Ejemplo 2, de $s = 17$ a $s = 18$** (sale `e`, entra `␣`), el paso que
produce la primera colisión:

$$t_{18} = \big(256\,(1 - 101 \cdot 79) + 32\big) \bmod 101 = (256 \cdot (-7\,978) + 32) \bmod 101 = -2\,042\,336 \bmod 101 = 86$$

El valor intermedio es negativo. En Python, `%` con divisor positivo siempre
devuelve un resultado en $[0, q)$, así que $-2\,042\,336 \bmod 101 = 86$
sin ajustes; en lenguajes como Java o C habría que sumar $q$ si el residuo
es negativo.

### 3.6 Hashes de las 109 ventanas ($n - m + 1 = 109$)

Fila $= s$ inicial; columna $= +0 \dots +9$. En **negrita** las ventanas
con $t_s = p = 86$.

| $s$ | +0 | +1 | +2 | +3 | +4 | +5 | +6 | +7 | +8 | +9 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 42 | 59 | 49 | 70 | 12 | 37 | 97 | 90 | 56 | 90 |
| 10 | 16 | 27 | 16 | 53 | 66 | 35 | 71 | 1 | **86** | 67 |
| 20 | 33 | 38 | 15 | 46 | 1 | 79 | 39 | 29 | 56 | 42 |
| 30 | 16 | 100 | 53 | 13 | 55 | 57 | 98 | 1 | 53 | 78 |
| 40 | 50 | 50 | 22 | 64 | 88 | 35 | 11 | 78 | 72 | 61 |
| 50 | 66 | 25 | **86** | 95 | 10 | 87 | 96 | 42 | 3 | 66 |
| 60 | 5 | 68 | 39 | 19 | 65 | **86** | 98 | 11 | 98 | 39 |
| 70 | 35 | 65 | 44 | 15 | 78 | 10 | 39 | 88 | 43 | 23 |
| 80 | 49 | 85 | 25 | **86** | 42 | 1 | 89 | 9 | 81 | 89 |
| 90 | 96 | 8 | 14 | 17 | 49 | 60 | 50 | 77 | 88 | 77 |
| 100 | 6 | 31 | 34 | 17 | 20 | 59 | 17 | 38 | 71 | |

Cada uno de estos 108 valores (después de $t_0$) se obtuvo con una
actualización $O(1)$; el script verifica con `assert` que todos coinciden con
el hash recalculado desde cero.

### 3.7 Verificación de las ventanas con hash igual al del patrón

Solo 4 de las 109 ventanas requieren comparar caracteres:

| $s$ | Ventana | $t_s$ | Verificación carácter a carácter | Comparaciones | Resultado |
|---|---|---|---|---|---|
| 18 | `w␣of␣the␣` | 86 | $T[18] =$ `w` ≠ $P[0] =$ `e` | 1 | **colisión** (falso positivo) |
| 52 | `education` | 86 | 9 caracteres iguales | 9 | **ocurrencia** |
| 65 | `ssessment` | 86 | $T[65] =$ `s` ≠ $P[0] =$ `e` | 1 | **colisión** (falso positivo) |
| 83 | `education` | 86 | 9 caracteres iguales | 9 | **ocurrencia** |

Total: 2 ocurrencias, 2 colisiones y **20** comparaciones de caracteres
(frente a 125 de KMP), más 109 comparaciones de números enteros.

### 3.8 Por qué hay colisión: comprobación desde cero

Hash de `w␣of␣the␣` con Horner, sin rolling hash:

| Carácter | w | ␣ | o | f | ␣ | t | h | e | ␣ |
|---|---|---|---|---|---|---|---|---|---|
| $v$ | 119 | 32 | 111 | 102 | 32 | 116 | 104 | 101 | 32 |
| $256 \cdot t + v$ | 119 | 4 640 | 24 431 | 23 142 | 3 360 | 7 028 | 15 208 | 14 949 | 288 |
| $\bmod 101$ | 18 | 95 | 90 | 13 | 27 | 59 | 58 | 1 | **86** |

Hash de `ssessment`:

| Carácter | s | s | e | s | s | m | e | n | t |
|---|---|---|---|---|---|---|---|---|---|
| $v$ | 115 | 115 | 101 | 115 | 115 | 109 | 101 | 110 | 116 |
| $256 \cdot t + v$ | 115 | 3 699 | 16 229 | 17 779 | 883 | 19 309 | 4 709 | 16 238 | 20 084 |
| $\bmod 101$ | 14 | 63 | 69 | 3 | 75 | 18 | 63 | 78 | **86** |

Ambas cadenas son distintas de `education` pero, como números en base 256,
dejan el mismo residuo módulo 101. Esto es inevitable: hay $256^9 \approx
4{,}7 \times 10^{21}$ cadenas posibles de 9 bytes y solo 101 residuos; por
eso la verificación carácter a carácter es obligatoria para que el
algoritmo sea correcto (algoritmo de tipo Las Vegas: siempre correcto, con
tiempo variable).

### 3.9 Efecto del módulo $q$

Mismo texto y patrón, $d = 256$:

| $q$ | $\text{hash}(P)$ | Ocurrencias | Colisiones | Comparaciones de caracteres |
|---|---|---|---|---|
| 13 | 0 | 52, 83 | **11** (2, 6, 51, 58, 62, 73, 76, 78, 82, 94, 107) | 29 |
| 101 | 86 | 52, 83 | **2** (18, 65) | 20 |
| 1 000 000 007 | 429 120 780 | 52, 83 | **0** | 18 |

Con un hash uniforme se esperan unas $(n - m + 1)/q$ colisiones:
$109/13 \approx 8{,}4$ y $109/101 \approx 1{,}1$, del orden de lo observado
(11 y 2), y $109/10^9 \approx 10^{-7}$ con el primo de producción. El
resultado (las posiciones) es el mismo con los tres módulos; lo que cambia
es el trabajo de verificación, que en el peor caso (todas las ventanas
colisionan) lleva el algoritmo a $O((n - m + 1)\,m)$. Con $q$ grande el
tiempo esperado es $O(n + m)$ más $O(m)$ por ocurrencia real. Esta es la
razón por la que la aplicación usa $q = 1\,000\,000\,007$ y el valor 101 se
emplea solo en esta demostración.

---

## 4. Boyer-Moore (CAS-6)

*Sección a cargo de Camilo (CAS-6): llenado de las tablas del carácter malo y
del sufijo bueno de `education` y gráfico de cada iteración con su
desplazamiento sobre el mismo fragmento (sección 1.3). Sobre este texto la
implementación hace 32 comparaciones de caracteres.*

---

## Referencias

* Cormen, T. H., Leiserson, C. E., Rivest, R. L. y Stein, C. (2022).
  *Introduction to Algorithms* (4.ª ed.). MIT Press. Secciones 32.2
  (Rabin-Karp) y 32.4 (Knuth-Morris-Pratt).
* Karp, R. M. y Rabin, M. O. (1987). Efficient randomized pattern-matching
  algorithms. *IBM Journal of Research and Development*, 31(2), 249-260.
* Knuth, D. E., Morris, J. H. y Pratt, V. R. (1977). Fast pattern matching
  in strings. *SIAM Journal on Computing*, 6(2), 323-350.
