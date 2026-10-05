# Documento Técnico del Proyecto

**Análisis de Algoritmos en el Contexto de la Bibliometría**
Universidad del Quindío · Programa de Ingeniería de Sistemas y Computación · Semestre 2026-2

**Equipo:** Daniel Josué Narváez Hincapié · Camilo Alberto Ospina

> 📌 Este documento se encuentra en construcción. Las secciones 1 a 3 corresponden al borrador inicial (tarea ARQ-3, Sprint 1), con la sección 2 actualizada en el Sprint 3 con el proceso real de extracción y validación del corpus; la sección 4 se completó en el Sprint 2 (tarea DOC-A1) y la sección 5 en el Sprint 3 (tarea DOC-A2). Las secciones restantes se irán completando en los sprints siguientes conforme se implementen el clustering, el despliegue y la declaración de uso de IA generativa (ver tabla de estado al final).

---

## 1. Introducción

El estudio computacional de textos permite explorar y analizar grandes volúmenes de producción científica mediante métodos cuantitativos y cualitativos, apoyados en fundamentos matemáticos y estadísticos. En este proyecto, dicho estudio se aplica sobre un dominio de conocimiento específico: la **inteligencia artificial generativa**.

El reto central es doble: por un lado, procesar lenguaje natural no estructurado (los abstracts de artículos científicos); por otro, recorrer la transición conceptual desde las estructuras de datos y algoritmos clásicos de similitud textual, hasta los modelos modernos basados en Inteligencia Artificial (embeddings). El proyecto exige que esta transición no se quede en el uso de librerías de alto nivel, sino que cada algoritmo sea implementado explícitamente por el equipo, de forma que su comportamiento interno sea completamente transparente y analizable.

El desarrollo se organiza en torno a tres requerimientos funcionales:

- **Requerimiento 1 — Análisis de Similitud Textual:** selección dinámica de dos o más artículos del corpus, y comparación de sus abstracts mediante 4 algoritmos clásicos (basados en distancia de edición y en modelos de espacio vectorial) y 2 enfoques de Inteligencia Artificial (embeddings), incluyendo la demostración matemática paso a paso sobre un caso de estudio concreto y el análisis crítico comparativo entre ambos enfoques.
- **Requerimiento 2 — Agrupamiento Jerárquico (Clustering):** implementación desde cero de 3 criterios de agrupamiento jerárquico (Single, Complete y Average Linkage) sobre los 20 abstracts, construcción del dendrograma correspondiente a cada uno, y determinación de cuál produce agrupamientos más coherentes mediante una métrica de evaluación interna.
- **Requerimiento 6 — Despliegue y Documentación Técnica:** el proyecto debe quedar desplegado y accesible, soportado por la documentación técnica correspondiente a cada requerimiento.

Este documento técnico consolida, para cada uno de estos requerimientos, la arquitectura, la implementación, el análisis matemático y crítico exigido, y la declaración explícita del uso de herramientas de IA generativa como apoyo al desarrollo (nunca como reemplazo del diseño algorítmico ni del análisis formal solicitado en el curso).

## 2. Fuentes de Información

A diferencia de un proceso tradicional de recolección automatizada sobre bases de datos científicas (como ACM, SAGE o ScienceDirect), este proyecto trabaja sobre un **corpus documental controlado y estático**, suministrado directamente por el docente.

**Características del corpus:**

- **Tamaño:** 20 artículos científicos.
- **Formato de origen:** PDF.
- **Dominio de conocimiento:** inteligencia artificial generativa.
- **Alcance del procesamiento:** el análisis computacional y la implementación de los algoritmos se enfocan de manera estricta y primordial sobre el **abstract (resumen)** de cada artículo. Es el campo de texto sobre el que corren todos los algoritmos de similitud y de clustering.
- **Metadatos adicionales:** título del artículo y autores. Estos no se someten a los algoritmos de similitud/clustering, pero se extraen y se usan como identificadores y para requerimientos funcionales puntuales que exijan cruce de información (por ejemplo, mostrar en la interfaz qué artículo corresponde a cada resultado).

**Proceso de obtención (Sprint 1, épica EPIC-1):**

1. **Extracción (EXT-1, `src/extraer_datos.py`).** Se usa `pypdf` para extraer el texto completo de cada PDF. El título se toma de las primeras líneas del documento, los autores de las líneas entre el título y el encabezado *Abstract*, y el abstract mediante expresiones regulares que capturan el texto entre *Abstract* y *Keywords*/*Introduction*. El resultado crudo queda en `data/raw/articulos_extraidos.csv`.
2. **Estructuración (EXT-2, `src/csv_json.py`).** El CSV se normaliza a `data/corpus.json`, con 20 registros de estructura `{numero, titulo, autores, abstract}`. El campo `numero` (1–20) funciona como identificador único del artículo y es el que usan todos los módulos posteriores para seleccionarlo.
3. **Preprocesamiento (PRE-1, `src/preprocessing.py`).** La función reutilizable `preprocess_text()` aplica, en orden: reconstrucción de ligaduras tipográficas mal extraídas (`arti ﬁcial` → `artificial`, validando contra el diccionario de inglés de NLTK), normalización Unicode NFKC, reconstrucción de palabras partidas por guion de fin de línea (`edu- cational` → `educational`), resolución de palabras compuestas con guion o barra (`problem-solving` → `problem solving`; con prefijos como `inter-` o `non-` se une: `inter-disciplinary` → `interdisciplinary`), minúsculas, tokenización, eliminación de puntuación, números y *stopwords* en inglés (más residuos académicos como `et`, `al`, `fig`), y lematización con desambiguación por categoría gramatical (WordNet + etiquetador POS). El corpus resultante se guarda en `data/corpus_preprocesado.json`, que agrega a cada artículo `abstract_preprocesado` (lista de tokens) y `abstract_preprocesado_texto` (los mismos tokens unidos por espacios).
4. **Validación manual (PRE-2, `docs/validacion_corpus.md`).** Se revisaron los abstracts extraídos contra los PDF originales. El hallazgo principal fue que las palabras compuestas con guion o barra (`English-written`, `meta-analyses`, `Human-AI`, `design/methodology/approach`, entre otras, en 17 de los 20 artículos) quedaban fusionadas en un único token inexistente (`englishwritten`, `metaanalyses`, `humanai`). La corrección se incorporó como regla genérica en el propio preprocesamiento, de modo que el corpus preprocesado se regenera de forma reproducible ejecutando `python src/preprocessing.py`, sin ediciones manuales sobre el JSON. El único caso que no admite regla genérica (artículo 5, `de ﬁ- nitions`, donde coinciden una ligadura y un guion de fin de línea) se corrige mediante una tabla explícita de correcciones puntuales (`CORRECCIONES_PUNTUALES`).

**Características del corpus procesado:**

| Medida | Valor |
|---|---|
| Artículos | 20 |
| Longitud del abstract crudo | 134 a 263 palabras (promedio ≈ 202) |
| Longitud del abstract preprocesado | 77 a 159 tokens (≈ 2.530 en total) |
| Vocabulario (tokens distintos, todo el corpus) | 868 términos, de los cuales 484 (≈ 56 %) aparecen una sola vez |
| Términos más frecuentes | `ai`, `education`, `review`, `research`, `aied`, `assessment` |

## 3. Arquitectura del Sistema

### 3.1 Visión general

El sistema se organiza en tres bloques funcionales, que van desde la preparación de los datos hasta la aplicación desplegada:

1. **Ingesta y Preparación de Datos** — extracción del texto de los PDFs y preprocesamiento de los abstracts.
2. **Motor de Algoritmos** — implementación de los algoritmos clásicos y de IA (Requerimiento 1) y de los algoritmos de clustering jerárquico (Requerimiento 2).
3. **Aplicación** — backend/API que expone los algoritmos y frontend con el que interactúa el usuario (Requerimiento 6).

El diagrama de componentes correspondiente se encuentra en [`/docs/arquitectura.png`](./arquitectura.png) (fuente editable en [`/docs/arquitectura.puml`](./arquitectura.puml)).

### 3.2 Módulos del sistema

| Módulo | Responsable | Descripción |
|---|---|---|
| **Extracción** (`EXT`) | Camilo Ospina | Extrae título, autores y abstract de los 20 PDFs y estructura el corpus en JSON/CSV. |
| **Preprocesamiento** (`PRE`) | Daniel Narváez | Limpieza y normalización del texto de los abstracts (tokenización, stopwords, lematización). Expone una función reutilizable para el resto de módulos. |
| **Algoritmos Clásicos** (`src/classic`) | Daniel Narváez (Levenshtein, Needleman-Wunsch) · Camilo Ospina (TF-IDF+Coseno, Jaccard) | Implementación desde cero de los 4 algoritmos clásicos de similitud textual exigidos por el Requerimiento 1. |
| **Algoritmos de IA** (`src/ia`) | Daniel Narváez (Word2Vec/FastText) · Camilo Ospina (modelo de lenguaje/API) | Generación de embeddings y cálculo de similitud (euclidiana/coseno) entre vectores, Requerimiento 1. |
| **Clustering** (`src/clustering`) | Camilo Ospina (matriz de distancias, Average Linkage) · Daniel Narváez (Single Linkage, Complete Linkage, dendrograma) | Implementación desde cero de los 3 criterios de agrupamiento jerárquico y su correspondiente dendrograma, Requerimiento 2. |
| **Backend / API** (`backend`) | Daniel Narváez | Expone mediante una API los resultados de similitud y clustering, integrando todos los módulos anteriores. |
| **Frontend** | Camilo Ospina | Interfaz para seleccionar artículos, ejecutar los algoritmos y visualizar resultados y dendrogramas. |

### 3.3 Stack tecnológico

Decisión tomada y justificada en la tarea ARQ-2 (Camilo Ospina):

- **Lenguaje:** Python — mismo lenguaje de punta a punta, adecuado para procesamiento de texto (NLTK/spaCy), estructuras de datos para implementar los algoritmos desde cero (NumPy/Pandas) y visualización de apoyo (matplotlib/scipy, usadas únicamente para graficar, nunca para calcular similitud o clustering).
- **Backend:** FastAPI — se prefirió sobre una alternativa serverless (AWS Lambda) porque el tamaño del proyecto no justifica la complejidad adicional de fragmentar la lógica en funciones por endpoint ni de introducir una capa de adaptación (Mangum) para conservar el manejo de rutas, middleware y documentación OpenAPI que FastAPI ya ofrece de forma nativa.
- **Frontend:** Streamlit — permite construir la interfaz en el mismo lenguaje que el resto del proyecto, con integración simple hacia la API y soporte directo para graficar los dendrogramas, sin la curva de aprendizaje adicional que implicaría introducir React para un proyecto de este alcance.
- **Despliegue:** servicio accesible tipo Render/Railway/Docker (a definir en el Sprint 5, tarea DEP-3).
- **Control de versiones:** Git/GitHub, con commits directos sobre `main` (equipo de 2 personas con tareas claramente delimitadas por Jira; ver convenciones en el README del repositorio).
- **Gestión del proyecto:** Jira, con las 6 épicas y todas las tareas del cronograma.

## 4. Algoritmos Clásicos de Similitud Textual (Requerimiento 1, parte 1)

### 4.1 Visión general

El Requerimiento 1 exige la implementación desde cero de 4 algoritmos clásicos de similitud textual, organizados en dos familias según el fundamento matemático que utilizan:

- **Basados en distancia de edición** (comparan las secuencias de tokens posición por posición): Levenshtein y Needleman-Wunsch.
- **Basados en vectorización y conjuntos** (ignoran el orden de las palabras): Similitud del Coseno con TF-IDF y Coeficiente de Jaccard.

Los cuatro se implementaron en `src/classic/` sin usar ninguna librería que resuelva el algoritmo directamente (ni `python-Levenshtein`/`rapidfuzz`, ni `Bio.pairwise2`, ni `TfidfVectorizer` de scikit-learn), únicamente con estructuras de datos básicas de Python. Los cuatro reciben como entrada `abstract_preprocesado` (la lista de tokens ya limpia, sin stopwords y lematizada, construida en PRE-1 y validada en PRE-2), garantizando que las cuatro métricas se calculen sobre exactamente el mismo texto base y sean comparables entre sí.

Los cuatro módulos cuentan con pruebas unitarias: Levenshtein (24 tests), Needleman-Wunsch (19 tests), TF-IDF + Coseno (18 tests) y Jaccard (16 tests). El comparador interactivo `classics.py` (CLA-5) integra los cuatro directamente por import, sin duplicar lógica.

### 4.2 Distancia de Levenshtein

**Fundamento teórico:** mide el número mínimo de operaciones de edición (inserción, eliminación, sustitución) necesarias para transformar una secuencia de tokens A en otra secuencia B. Se implementa mediante programación dinámica, construyendo una matriz D de tamaño `(n+1)×(m+1)` (siendo n y m el número de tokens de cada abstract) con la recurrencia:

```
D[i][0] = i,  D[0][j] = j
D[i][j] = D[i-1][j-1]                                  si A[i-1] == B[j-1]
D[i][j] = 1 + min(D[i-1][j], D[i][j-1], D[i-1][j-1])   en otro caso
```

El camino óptimo (qué operación se aplicó en cada paso) se reconstruye mediante *backtracking* sobre la matriz ya construida (función `traceback()`), retrocediendo desde `D[n][m]` hasta `D[0][0]`.

**Complejidad algorítmica:**
- **Tiempo:** O(n·m) — se llena cada una de las `(n+1)×(m+1)` celdas de la matriz una sola vez, con trabajo constante por celda.
- **Espacio:** O(n·m) — se conserva la matriz completa (no solo la fila anterior) de forma deliberada, para poder mostrar el llenado paso a paso exigido en el caso de estudio; una implementación optimizada solo para obtener la distancia final podría reducirse a O(min(n,m)).

**Implementación:** `src/classic/levenshtein.py` — `build_levenshtein_matrix()`, `traceback()`, `levenshtein_distance()`, `levenshtein_similarity()`, `similarity_matrix()`.

### 4.3 Needleman-Wunsch

**Fundamento teórico:** realiza un alineamiento global entre dos secuencias, similar en mecánica a Levenshtein pero con un esquema de puntuación en vez de costos: coincidencia = +1, sustitución = −1, gap (inserción/eliminación) = −2. Se busca el alineamiento que **maximiza** el puntaje total, en vez de minimizar el costo:

```
S[i][0] = i·gap,  S[0][j] = j·gap
S[i][j] = max( S[i-1][j-1] + (match si A[i-1]==B[j-1], si no mismatch),
               S[i-1][j] + gap,
               S[i][j-1] + gap )
```

A diferencia de Levenshtein, el resultado no es un solo número sino un **alineamiento explícito** de ambas secuencias (con huecos `-` donde fue necesario), reconstruido también por `traceback()`.

**Complejidad algorítmica:**
- **Tiempo:** O(n·m), igual que Levenshtein — misma estructura de matriz y misma cantidad de trabajo por celda.
- **Espacio:** O(n·m), por la misma razón (se conserva la matriz completa para el caso de estudio).

**Implementación:** `src/classic/needleman_wunsch.py` — `build_score_matrix()`, `traceback()`, `needleman_wunsch_alignment()`, `needleman_wunsch_similarity()`, `similarity_matrix()`.

### 4.4 TF-IDF + Similitud del Coseno

**Fundamento teórico:** en vez de comparar las secuencias posición por posición, representa cada abstract como un vector numérico en un espacio de dimensión igual al vocabulario del corpus. Cada componente del vector combina dos factores:
- **TF** (frecuencia de término): `TF(t,d) = conteo(t,d) / total_términos(d)`.
- **IDF** (frecuencia inversa de documento, variante suavizada): `IDF(t) = log(N / (1+df(t))) + 1`, donde N es el número de documentos comparados y df(t) el número de esos documentos en los que aparece t.

La similitud entre dos documentos se calcula como el coseno del ángulo entre sus vectores TF-IDF:

```
similitud(A,B) = (A · B) / (‖A‖ · ‖B‖)
```

Este enfoque ignora completamente el orden de las palabras: solo le importa qué tan parecida es la distribución de vocabulario relevante entre los dos documentos.

**Complejidad algorítmica** (N = documentos comparados, V = tamaño del vocabulario conjunto, L = longitud promedio de un abstract):
- **Tiempo:** construir el vocabulario y el IDF cuesta O(N·L); vectorizar los N documentos cuesta O(N·V) (se recorre el vocabulario completo por cada documento); calcular la similitud coseno de un par cuesta O(V). Para la matriz de similitud completa entre N documentos: O(N²·V).
- **Espacio:** O(N·V) para almacenar la matriz TF-IDF (un vector denso de tamaño V por documento).

**Implementación:** `src/classic/tfidf_cosine.py` — `calcular_tf()`, `calcular_idf()`, `construir_vocabulario()`, `vectorizar_tfidf()`, `similitud_coseno()`, `matriz_similitud()`.

### 4.5 Coeficiente de Jaccard

**Fundamento teórico:** el más simple de los cuatro. Representa cada abstract como un **conjunto** de tokens (o n-gramas) únicos, e ignora tanto el orden como la frecuencia de aparición — solo importa si un término está presente o no:

```
J(A,B) = |A ∩ B| / |A ∪ B|
```

Se implementó de forma parametrizable en el tamaño de n-grama (`n=1` por defecto, unigramas/palabras sueltas), permitiendo también comparar por bigramas o trigramas si se requiere mayor sensibilidad al contexto local.

**Complejidad algorítmica** (N = documentos comparados, L = longitud promedio de un abstract):
- **Tiempo:** construir el conjunto de n-gramas de un documento cuesta O(L); calcular la intersección/unión de dos conjuntos con tablas hash cuesta, en promedio, O(|A|+|B|). Para la matriz de similitud completa entre N documentos: O(N²·L).
- **Espacio:** O(N·L) para almacenar los N conjuntos de tokens.

**Implementación:** `src/classic/jaccard.py` — `tokenizar()`, `generar_ngramas()`, `texto_a_conjunto()`, `jaccard()`, `matriz_jaccard()`.

### 4.6 Resumen comparativo de complejidad

| Algoritmo | Tiempo | Espacio | ¿Sensible al orden? |
|---|---|---|---|
| Levenshtein | O(n·m) | O(n·m) | Sí |
| Needleman-Wunsch | O(n·m) | O(n·m) | Sí |
| TF-IDF + Coseno | O(N²·V) para la matriz completa | O(N·V) | No |
| Jaccard | O(N²·L) para la matriz completa | O(N·L) | No |

*(n, m: longitud en tokens de cada abstract comparado · N: número de documentos · V: tamaño del vocabulario conjunto · L: longitud promedio de un abstract)*

Levenshtein y Needleman-Wunsch escalan con el **producto de las longitudes** de los dos textos comparados, por lo que resultan más costosos cuanto más largos son los abstracts, independientemente de cuántos documentos tenga el corpus. TF-IDF y Jaccard, en cambio, escalan con el **cuadrado del número de documentos**, por lo que resultan más costosos cuando se quiere comparar un corpus grande completo (los 20 artículos entre sí) que cuando se comparan solo 2 o 3 artículos puntuales, como en el caso de estudio.

### 4.7 Resultados sobre el caso de estudio (artículos 2 y 9)

Los cuatro algoritmos se ejecutaron sobre el mismo par de artículos, seleccionado en CAS-1 y documentado en detalle (matrices paso a paso, backtracking y evidencia reproducible) en [`/docs/caso_estudio_clasicos.md`](./caso_estudio_clasicos.md):

| Algoritmo | Similitud (artículos 2 vs 9) |
|---|---|
| Levenshtein | 0.0901 |
| Needleman-Wunsch | 0.0901 |
| Jaccard | 0.1583 |
| TF-IDF + Coseno | 0.2553 |

**Análisis crítico:** ninguno de los cuatro algoritmos reporta una similitud alta entre estos dos artículos (todos por debajo de 0.30), pero se observa un patrón consistente: los algoritmos sensibles al orden posicional (Levenshtein y Needleman-Wunsch, ambos ≈0.09) dan una similitud notablemente más baja que los que ignoran el orden (Jaccard 0.16, TF-IDF+Coseno 0.26). Esto ocurre pese a que ambos abstracts comparten vocabulario temático directamente relevante (`artificial`, `intelligence`, `education`, `aied`), lo cual confirma que la elección del algoritmo no es neutral: Levenshtein/Needleman-Wunsch son apropiados cuando importa la estructura/secuencia exacta del texto, mientras que Jaccard y TF-IDF+Coseno son más apropiados para capturar cercanía temática independientemente de cómo esté redactada cada oración. Esta misma tensión (orden vs. contenido) es el punto de partida para el análisis comparativo frente a los modelos de IA (embeddings) que se documentará en el Sprint 3.

## 5. Modelos de Inteligencia Artificial y Embeddings (Requerimiento 1, parte 2)

Esta sección documenta los dos enfoques de similitud basados en IA exigidos por el Requerimiento 1, las métricas con las que se comparan sus vectores y el análisis comparativo frente a los algoritmos clásicos. El detalle completo está en `docs/modelos_ia.md` (selección, implementación y resultados de los modelos) y en `docs/analisis_comparativo.md` (análisis crítico).

### 5.1 Fundamentos: de la representación léxica a la representación densa

Los modelos de espacio vectorial clásicos, como TF-IDF, asignan una dimensión independiente a cada término del vocabulario. En esa representación, `AI` y `artificial intelligence`, o `students` y `learners`, ocupan dimensiones distintas y ortogonales, así que el modelo no tiene ninguna noción de que significan lo mismo: dos textos que expresan la misma idea con palabras diferentes obtienen similitud 0.

Los **embeddings** resuelven esa limitación representando el texto en un espacio vectorial continuo y denso, de unos cientos de dimensiones, donde la cercanía geométrica refleja similitud de significado. Se apoyan en la **hipótesis distribucional**: las palabras que aparecen en contextos parecidos tienden a tener significados parecidos. Un modelo preentrenado aprende esos vectores a partir de un corpus muy grande y luego se puede usar para representar textos nuevos.

El proyecto usa dos generaciones de embeddings, elegidas para que la comparación sea informativa (ver `docs/modelos_ia.md`, secciones 4 a 6):

| | Word2Vec (IA-2) | all-mpnet-base-v2 (IA-3) |
|---|---|---|
| Tipo de vector | Estático, uno por palabra | Contextual, uno por texto |
| Dimensión | 300 | 768 |
| ¿Considera el orden? | No | Sí |
| Entrada | `abstract_preprocesado` | `abstract` original |
| Vector del abstract | Promedio calculado por el equipo | Producido por el modelo |

Se descartaron entrenar un Word2Vec propio (el corpus tiene apenas 2.532 tokens y más de la mitad de su vocabulario aparece una sola vez), FastText (su ventaja con palabras desconocidas exige un modelo de unos 7 GB) y las APIs comerciales de embeddings (no son reproducibles ni inspeccionables).

### 5.2 Word2Vec preentrenado: vector del documento por promedio (IA-2)

**Implementación:** `src/ia/embeddings_w2v.py` · **Resultado:** `data/embeddings/word2vec.json`

Se usa el modelo `word2vec-google-news-300` (Mikolov et al., 2013), entrenado con la arquitectura *skip-gram* sobre unos 100 mil millones de palabras de noticias. Asigna un vector de 300 dimensiones a cada una de sus 3 millones de palabras y frases.

Como el modelo produce vectores de **palabras**, el vector del abstract se calcula en el sistema como el promedio aritmético de los vectores de sus tokens:

$$\vec{v}(d) = \frac{1}{|T|} \sum_{t \in T} \vec{w}(t)$$

donde $T$ es el conjunto de tokens del abstract (con repeticiones) **que existen en el modelo**. Los tokens que no existen se excluyen del promedio y se registran. Como el modelo distingue mayúsculas y los tokens del corpus están en minúscula, cada token se busca también en su forma capitalizada y en mayúsculas (por ejemplo, `nlp` → `NLP`).

**Hallazgo y corrección: siglas con un significado equivocado.** El 99,3 % de los tokens del corpus existe en el modelo, pero existir no garantiza tener el significado correcto. Al revisar las palabras más cercanas a cada sigla del dominio se encontró que en el modelo `ai` es una palabra del italiano (vecinos: `che`, `essere`, `tutto`), `Aied` y `Genai` son nombres propios, y `gai` pertenece a la cocina vietnamita. Esto es grave porque `ai` es el término más frecuente del corpus. Por eso, antes de buscar estas siglas, el sistema las reemplaza por su forma expandida (`ai` → `artificial_intelligence`, `aied` → `artificial_intelligence` + `education`, entre otras), usando solo palabras cuyo significado en el modelo también se verificó. La tabla completa y su justificación están en `docs/modelos_ia.md`, sección 8.

**Resultado:** cobertura final del 99,7 % (2.525 de 2.532 tokens); los 7 tokens sin vector son en su mayoría nombres de bases de datos (`openalex`, `ebscohost`, `sciencedirect`).

### 5.3 all-mpnet-base-v2: embedding contextual de documento (IA-3)

**Implementación:** `src/ia/embeddings_llm.py` · **Resultado:** `data/embeddings/mpnet.json`

Este modelo usa la arquitectura **Transformer**, basada en **auto-atención**: para representar cada sub-palabra, el modelo pondera todas las demás sub-palabras del texto, de modo que el vector de una palabra depende de su contexto y del orden en que aparece. A diferencia de Word2Vec, la misma palabra recibe vectores distintos en contextos distintos.

- **Entrada:** el campo `abstract` original, sin preprocesar. Las *stopwords*, la puntuación y el orden son justamente la información que el Transformer usa para interpretar el contexto; eliminarlas le quitaría lo que lo diferencia de Word2Vec. Por la misma razón no necesita expansión de siglas: el abstract define `Artificial Intelligence in Education (AIEd)` y el modelo lo interpreta en contexto.
- **Vector del documento:** el modelo lo produce directamente, mediante una capa de *mean pooling* sobre las sub-palabras seguida de una capa de normalización. El sistema verificó que los 20 vectores tienen norma exactamente 1.
- **Verificación de truncamiento:** el modelo solo lee las primeras 384 sub-palabras (`max_seq_length`) y descarta el resto sin avisar. El sistema cuenta las sub-palabras de cada abstract con el tokenizador del propio modelo, incluyendo los tokens especiales de inicio y fin. **Resultado:** los abstracts ocupan entre 166 y 383 sub-palabras (promedio 266,1), así que todos se procesan completos. Con el modelo más liviano `all-MiniLM-L6-v2` (límite de 256), 13 de los 20 abstracts habrían perdido su parte final.

### 5.4 Métricas de similitud sobre embeddings (IA-4)

**Implementación:** `src/ia/metricas.py` · **Integración:** `src/comparador.py`

Para dos vectores $\vec{a}$ y $\vec{b}$ de dimensión $n$, el sistema calcula:

$$\cos(\vec{a}, \vec{b}) = \frac{\sum_{i=1}^{n} a_i b_i}{\sqrt{\sum_{i=1}^{n} a_i^2} \cdot \sqrt{\sum_{i=1}^{n} b_i^2}} \qquad d(\vec{a}, \vec{b}) = \sqrt{\sum_{i=1}^{n} (a_i - b_i)^2} \qquad s(\vec{a}, \vec{b}) = \frac{1}{1 + d(\vec{a}, \vec{b})}$$

La similitud coseno mide el ángulo entre los vectores (1 = misma dirección), la distancia euclidiana mide qué tan lejos quedan sus extremos, y $s$ convierte esa distancia en una similitud en el intervalo (0, 1]. Las tres se implementan con ciclos y `math.sqrt`, sin `numpy` ni las funciones de similitud de las librerías de los modelos. El costo de cada una es $O(n)$.

Como los vectores de MPNet tienen norma 1, en ese modelo se cumple $d^2 = 2 - 2\cos$: la distancia euclidiana es una función exacta del coseno y no aporta información adicional. En Word2Vec los vectores no están normalizados, así que las dos métricas pueden ordenar los pares de forma distinta.

`src/comparador.py` integra los seis algoritmos con la selección dinámica de artículos de CLA-5: permite elegir dos o más artículos y calcula sus matrices de similitud. Los embeddings se leen de los archivos JSON, de modo que la comparación no necesita cargar los modelos.

### 5.5 Justificación del uso de IA como apoyo al diseño algorítmico

El enunciado permite usar modelos preentrenados para vectorizar los abstracts y exige que los algoritmos solicitados se implementen de forma explícita. El proyecto separa esas dos responsabilidades:

| Lo aporta el modelo preentrenado | Lo diseñó e implementó el equipo |
|---|---|
| El vector de cada palabra (Word2Vec) | El promedio que produce el vector del documento |
| El vector de cada texto (MPNet) | La búsqueda por variantes de mayúsculas y la exclusión de palabras desconocidas |
| | La tabla de expansión de siglas y su verificación |
| | La similitud coseno, la distancia euclidiana y las matrices de similitud |
| | La verificación de truncamiento y de normalización |
| | El análisis comparativo y sus herramientas estadísticas |

Los modelos de IA son, por lo tanto, una fuente de **representaciones**: no calculan ninguna similitud del proyecto. Entrenar representaciones propias no era viable con un corpus de 20 abstracts, y los modelos se trataron como componentes que hay que evaluar, no como cajas negras confiables. Esa evaluación es la que detectó que Word2Vec interpretaba mal las siglas del dominio y que los valores absolutos de similitud no son comparables entre algoritmos, y llevó a decisiones de diseño explícitas para corregirlo.

*La declaración de las herramientas de IA generativa usadas como apoyo en el desarrollo del proyecto se presenta en la sección 8.*

### 5.6 Resultados y análisis comparativo: clásicos vs. IA

El análisis completo está en `docs/analisis_comparativo.md` (tarea CMP-2). Para el caso de estudio (artículos 2 y 9):

| Algoritmo | Tipo | Similitud 2–9 | Posición entre los 190 pares del corpus |
|---|---|---|---|
| Levenshtein | Clásico | 0,0901 | 4 (percentil 97,9) |
| Needleman-Wunsch | Clásico | 0,0901 | 7 (percentil 96,3) |
| Coseno TF-IDF | Clásico | 0,2553* | 3 (percentil 98,4) |
| Jaccard | Clásico | 0,1583 | 15 (percentil 92,1) |
| Word2Vec (coseno) | IA | 0,9318 | 18 (percentil 90,5) |
| MPNet (coseno) | IA | 0,8376 | 5 (percentil 97,4) |

\* *Con el IDF calculado sobre los 2 artículos. Con el IDF de los 20 artículos el valor es 0,2823, que es el usado para la posición.*

Conclusiones principales:

1. **Los valores absolutos no son comparables entre algoritmos.** Medidos por su posición en el corpus, los seis coinciden en que el par 2–9 está entre los más parecidos (percentil 90 o superior). La diferencia entre 0,09 y 0,93 es de escala, no de criterio.
2. **Los clásicos miden coincidencia léxica y la IA, cercanía semántica.** En un experimento con dos frases sinónimas sin palabras en común, los cuatro clásicos dan 0 y los modelos de IA alrededor de 0,7.
3. **El preprocesamiento también tiene consecuencias.** Al eliminar *stopwords*, "*AI improves learning*" y "*AI does not improve learning*" quedan idénticas, y todos los algoritmos que trabajan sobre tokens les asignan similitud 1. Solo MPNet, que recibe el texto original, nota la diferencia.
4. **Levenshtein y Needleman-Wunsch son casi equivalentes en este corpus** (correlación de Spearman 0,978). Cuando la alineación óptima no usa huecos extra, ambas similitudes se reducen a $k/m$, lo que explica el 10/111 = 0,0901 del caso de estudio.
5. **Para medir cercanía temática, MPNet es el enfoque más adecuado y TF-IDF el mejor de los clásicos.** MPNet es el que mejor discrimina entre pares; TF-IDF es el clásico cuyo ordenamiento se parece más al de los modelos de IA. Los algoritmos de edición reflejan sobre todo el tipo de estudio (revisión sistemática) más que el tema, y son entre 35 y 130 veces más lentos que el coseno sobre embeddings.

## Estado del documento

| Sección | Contenido | Estado | Sprint |
|---|---|---|---|
| 1. Introducción | Contexto y propósito del proyecto | ✅ Completa | Sprint 1 |
| 2. Fuentes de información | Corpus, proceso de obtención y validación | ✅ Completa | Sprint 1 (actualizada en Sprint 3) |
| 3. Arquitectura | Módulos y stack tecnológico | ✅ Completa | Sprint 1 |
| 4. Algoritmos clásicos | Implementación, complejidad y caso de estudio | ✅ Completa | Sprint 2 |
| 5. Modelos de IA | Embeddings, métricas y análisis comparativo clásicos vs. IA | ✅ Completa | Sprint 3 |
| 6. Clustering jerárquico | Implementación, dendrogramas y métrica de evaluación | ⬜ Pendiente | Sprint 4 |
| 7. Despliegue | Arquitectura de despliegue y guía de uso | ⬜ Pendiente | Sprint 5 |
| 8. Declaración de uso de IA generativa | Herramientas usadas como apoyo al desarrollo | ⬜ Pendiente | Sprint 5 |
| 9. Conclusiones | Cierre general del proyecto | ⬜ Pendiente | Sprint 6 |
