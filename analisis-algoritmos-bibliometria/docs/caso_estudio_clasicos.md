# Caso de Estudio — Algoritmos Clásicos de Similitud

## 1. Selección del caso de estudio (CAS-1)

Se utilizarán los **artículos 2 y 9** del corpus, puesto que los resultados
preliminares obtenidos con `classics.py` (CLA-5) muestran alta variación
entre los cuatro algoritmos clásicos para este par, lo que los hace
especialmente útiles para ilustrar las diferencias de comportamiento entre
métricas basadas en edición (Levenshtein, Needleman-Wunsch) y métricas
basadas en conjuntos/vectores (Jaccard, TF-IDF + Coseno).

| # | Título | Tokens preprocesados (`abstract_preprocesado`) |
|---|--------|--------------------------------------------------|
| 2 | *Systematic literature review on opportunities, challenges, and future research recommendations of artificial intelligence in education* | 77 tokens |
| 9 | *AI technologies for education: Recent research & future directions* | 111 tokens |

## 2. Nota metodológica: fragmento representativo

Levenshtein y Needleman-Wunsch requieren, para *n* y *m* elementos, una
matriz de (n+1) × (m+1) celdas. Con los abstracts completos (77 × 111 =
8.547 celdas) el llenado paso a paso no es documentable ni verificable a
mano. Por eso, para la **demostración matemática** se usa un fragmento
real y contiguo de 6 tokens de cada abstract; el **resultado final**
reportado en la sección 5 sí corresponde al cálculo sobre los abstracts
completos.

El fragmento se eligió porque contiene una coincidencia interna de 4
tokens consecutivos (`artificial intelligence education aied`), lo cual
permite ilustrar claramente tanto el costo de una sustitución como el de
una coincidencia exacta dentro de la misma matriz.

- **Fragmento A** — artículo 2, tokens [0:6]: `application, artificial, intelligence, education, aied, emerge`
- **Fragmento B** — artículo 9, tokens [9:15]: `study, artificial, intelligence, education, aied, publish`

## 3. Algoritmo de Levenshtein — demostración paso a paso

**Recurrencia:**
```
D[i][0] = i
D[0][j] = j
D[i][j] = D[i-1][j-1]                              si A[i-1] == B[j-1]
D[i][j] = 1 + min(D[i-1][j], D[i][j-1], D[i-1][j-1])  en otro caso
```

**Matriz de programación dinámica** (filas = Fragmento A, columnas = Fragmento B):

|              | ε | study | artificial | intelligence | education | aied | publish |
|--------------|---|---|---|---|---|---|---|
| **ε**              | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
| **application**    | 1 | 1 | 2 | 3 | 4 | 5 | 6 |
| **artificial**     | 2 | 2 | **1** | 2 | 3 | 4 | 5 |
| **intelligence**   | 3 | 3 | 2 | **1** | 2 | 3 | 4 |
| **education**      | 4 | 4 | 3 | 2 | **1** | 2 | 3 |
| **aied**           | 5 | 5 | 4 | 3 | 2 | **1** | 2 |
| **emerge**         | 6 | 6 | 5 | 4 | 3 | 2 | **2** |

*(en negrita: la diagonal que forma el camino óptimo de retroceso)*

**Camino óptimo (backtracking desde D[6][6] hasta D[0][0]):** el recorrido
es puramente diagonal. Generado automáticamente con `traceback()` de
`src/classic/levenshtein.py` (ver sección 6):

| Paso | A[i-1] | B[j-1] | ¿Coinciden? | Costo | D acumulado |
|------|--------|--------|-------------|-------|--------------|
| 1 | application | study | No | +1 (sustitución) | 1 |
| 2 | artificial | artificial | Sí | +0 (coincidencia) | 1 |
| 3 | intelligence | intelligence | Sí | +0 (coincidencia) | 1 |
| 4 | education | education | Sí | +0 (coincidencia) | 1 |
| 5 | aied | aied | Sí | +0 (coincidencia) | 1 |
| 6 | emerge | publish | No | +1 (sustitución) | 2 |

**Resultado sobre el fragmento:**
- Distancia de Levenshtein = **2**
- Similitud normalizada = 1 − 2/max(6,6) = **0.6667**

## 4. Algoritmo de Needleman-Wunsch — demostración paso a paso

**Esquema de puntuación:** match = +1, mismatch = −1, gap = −2

**Recurrencia:**
```
S[i][0] = i · gap
S[0][j] = j · gap
S[i][j] = max( S[i-1][j-1] + (match si A[i-1]==B[j-1] si no mismatch),
               S[i-1][j] + gap,
               S[i][j-1] + gap )
```

**Matriz de puntuación:**

|              | ε | study | artificial | intelligence | education | aied | publish |
|--------------|---|---|---|---|---|---|---|
| **ε**              | 0 | -2 | -4 | -6 | -8 | -10 | -12 |
| **application**    | -2 | -1 | -3 | -5 | -7 | -9 | -11 |
| **artificial**     | -4 | -3 | **0** | -2 | -4 | -6 | -8 |
| **intelligence**   | -6 | -5 | -2 | **1** | -1 | -3 | -5 |
| **education**      | -8 | -7 | -4 | -1 | **2** | 0 | -2 |
| **aied**           | -10 | -9 | -6 | -3 | 0 | **3** | 1 |
| **emerge**         | -12 | -11 | -8 | -5 | -2 | 1 | **2** |

*(en negrita: la diagonal del alineamiento óptimo)*

**Alineamiento óptimo obtenido por backtracking:**

```
Fragmento A:  application  artificial  intelligence  education  aied  emerge
Fragmento B:  study        artificial  intelligence  education  aied  publish
              (sust. -1)   (match +1)  (match +1)    (match +1) (match +1) (sust. -1)
```

Suma de puntajes: −1 + 1 + 1 + 1 + 1 − 1 = **2** ✔ (coincide con S[6][6])

**Resultado sobre el fragmento:**
- Score de alineamiento global = **2**
- Similitud normalizada (coincidencias / longitud del alineamiento) = 4/6 = **0.6667**

## 5. Resultado final sobre el caso de estudio completo (artículos 2 y 9)

Calculado sobre los `abstract_preprocesado` completos (77 vs. 111 tokens),
con las mismas funciones de `src/classic/`:

| Algoritmo | Métrica bruta | Similitud normalizada |
|-----------|----------------|------------------------|
| Levenshtein | Distancia = 101 (sobre máx. 111 elementos) | **0.0901** |
| Needleman-Wunsch | Score de alineamiento = −125 (10 coincidencias en un alineamiento de 111 posiciones) | **0.0901** |

**Lectura del resultado:** ambos algoritmos coinciden en una similitud
baja (~9%) entre los artículos 2 y 9 a nivel de edición de tokens. Esto
es consistente con que, aunque ambos abstracts tratan el mismo tema (IA
en educación) y comparten vocabulario clave (`artificial`,
`intelligence`, `education`, `aied`, `technology`, `review`...), el
**orden** en que aparecen las palabras es muy distinto de un abstract a
otro — y Levenshtein/Needleman-Wunsch son sensibles al orden posicional,
a diferencia de Jaccard (que ignora el orden) o TF-IDF+Coseno (que
compara distribución de frecuencias, también sin importar el orden).
Ese contraste es justamente lo que en CAS-3 se documentará al comparar
contra Jaccard y TF-IDF, y en el análisis crítico del Sprint 3 al
comparar clásicos vs. IA.

## 6. Evidencia reproducible

Todos los valores de este documento (matrices, caminos de backtracking y
resultado final) se pueden regenerar ejecutando:

```
.\venv\Scripts\python.exe notebooks/caso_estudio_cas2.py
```

El script no recibe parámetros: carga directamente los artículos 2 y 9
del corpus, reconstruye el mismo fragmento usado en las secciones 3 y 4,
e imprime en consola las matrices, el camino óptimo (backtracking) y el
resultado final sobre los abstracts completos. Tanto Levenshtein como
Needleman-Wunsch reconstruyen su camino automáticamente mediante sus
respectivas funciones `traceback()`, definidas en
`src/classic/levenshtein.py` y `src/classic/needleman_wunsch.py` — el
camino no se transcribe a mano, se genera con el mismo algoritmo que
calcula la matriz.
