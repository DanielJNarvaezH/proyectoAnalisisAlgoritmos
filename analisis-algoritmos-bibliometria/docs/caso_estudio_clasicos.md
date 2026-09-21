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
Ese contraste se confirma y se cuantifica en la sección 9 (CAS-3), al
comparar contra Jaccard y TF-IDF, y será insumo directo para el análisis
crítico del Sprint 3 al comparar clásicos vs. IA.

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

## 7. Algoritmo TF-IDF + Similitud Coseno — demostración paso a paso (CAS-3)

A diferencia de Levenshtein/Needleman-Wunsch, este enfoque no compara
secuencias posición por posición: convierte cada abstract en un vector
numérico dentro de un vocabulario común, y mide el ángulo entre esos
dos vectores. Se calcula sobre `abstract_preprocesado` completo de los
artículos 2 y 9 (77 y 111 tokens respectivamente), igual que el resto
del caso de estudio.

**Paso 7.1 — Vocabulario y frecuencia de término (TF):** se tokeniza cada
abstract (ya viene tokenizado desde PRE-1) y se cuenta cuántas veces
aparece cada palabra dividido entre el total de palabras del documento.

**Paso 7.2 — IDF (frecuencia inversa de documento), calculado sobre el
par seleccionado:**
```
IDF(t) = log(N / (1 + df(t))) + 1
```
Con N=2 (solo se comparan estos dos documentos, igual que hace
`classics.py`/CLA-5 al comparar un par). Los 19 términos que **comparten**
ambos artículos (aparecen en df=2 de 2 documentos) reciben el mismo IDF,
por ejemplo:

| Término | df | IDF |
|---|---|---|
| `artificial` | 2/2 | 0.5945 |
| `intelligence` | 2/2 | 0.5945 |
| `education` | 2/2 | 0.5945 |
| `aied` | 2/2 | 0.5945 |
| `ai` | 2/2 | 0.5945 |

Los términos que solo aparecen en **uno** de los dos artículos (df=1/2)
reciben un IDF más alto (`log(2/2)+1 = 1.0`), penalizando menos su
exclusividad al ser un corpus de solo 2 documentos.

**Paso 7.3 — Vectores TF-IDF:** multiplicando TF × IDF para cada término
del vocabulario conjunto (120 términos en total), el artículo 2 queda
representado con 57 dimensiones no nulas y el artículo 9 con 82.

**Paso 7.4 — Similitud coseno:**
```
similitud = (A · B) / (||A|| × ||B||)
```

| Cantidad | Valor |
|---|---|
| Producto punto (A · B) | 0.003308 |
| Norma \|\|A\|\| (artículo 2) | 0.122586 |
| Norma \|\|B\|\| (artículo 9) | 0.105717 |
| **Similitud coseno** | **0.2553** |

## 8. Coeficiente de Jaccard — demostración paso a paso (CAS-3)

Jaccard ignora tanto el orden como la frecuencia: solo le importa si una
palabra aparece o no en cada documento.

**Paso 8.1 — Conjuntos de unigramas únicos** (sobre `abstract_preprocesado`):
- Conjunto artículo 2: 57 tokens únicos
- Conjunto artículo 9: 82 tokens únicos

**Paso 8.2 — Intersección y unión:**
- Intersección (términos en ambos): 19 — incluye `artificial`, `intelligence`,
  `education`, `aied`, `ai`, `analysis`, `application`, `content`, `current`, `direction`...
- Unión (términos distintos combinando ambos): 120

**Paso 8.3 — Coeficiente:**
```
J(A, B) = |A ∩ B| / |A ∪ B| = 19 / 120 = 0.1583
```

## 9. Comparativa de resultados del caso de estudio completo (CAS-2 + CAS-3)

| Algoritmo | Similitud (artículos 2 vs 9) | Qué mide |
|-----------|-------------------------------|----------|
| Levenshtein | 0.0901 | Coincidencia exacta de secuencia, penaliza cualquier desfase de orden |
| Needleman-Wunsch | 0.0901 | Igual que Levenshtein, pero con alineamiento explícito y gaps |
| Jaccard | 0.1583 | Presencia/ausencia de vocabulario compartido, ignora orden y frecuencia |
| TF-IDF + Coseno | 0.2553 | Distribución de frecuencias ponderadas por relevancia, ignora orden |

**Lectura honesta del resultado:** ninguno de los cuatro algoritmos
reporta una similitud *alta* entre los artículos 2 y 9 — los cuatro
números están por debajo de 0.30. Lo que sí se observa con claridad es
el **mismo patrón en los cuatro**: los algoritmos sensibles al orden
posicional (Levenshtein, Needleman-Wunsch ≈ 0.09) dan una similitud
notablemente más baja que los que ignoran el orden (Jaccard 0.16,
TF-IDF+Coseno 0.26). Esto es consistente con la hipótesis planteada en
la sección 5: los artículos comparten vocabulario temático
(`artificial`, `intelligence`, `education`, `aied`), pero lo usan en
estructuras de oración muy distintas, por lo que las métricas de edición
"ven" mucho menos parecido que las métricas de conjunto/vector.

TF-IDF+Coseno da el valor más alto de los cuatro porque, a diferencia de
Jaccard, no solo cuenta si un término aparece sino que pondera su
relevancia (vía IDF) y su frecuencia relativa (vía TF) — los términos
compartidos y temáticamente relevantes (`aied`, `artificial`,
`intelligence`) pesan más que términos comunes poco informativos.

## 10. Evidencia reproducible (CAS-3)

Los valores de las secciones 7-9 se pueden regenerar ejecutando:

```
.\venv\Scripts\python.exe notebooks/caso_estudio_cas3.py
```

El script carga `data/corpus_preprocesado.json`, busca los artículos 2 y
9 por su campo `"numero"` (igual que `caso_estudio_cas2.py`), usa
`abstract_preprocesado` de cada uno, y calcula TF-IDF/Coseno y Jaccard
con las implementaciones reales de `src/classic/tfidf_cosine.py` y
`src/classic/jaccard.py` — las mismas que usa `classics.py` (CLA-5) y
que tienen 18 y 16 pruebas unitarias respectivamente.
