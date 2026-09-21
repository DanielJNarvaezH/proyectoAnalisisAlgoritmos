# Documento Técnico del Proyecto

**Análisis de Algoritmos en el Contexto de la Bibliometría**
Universidad del Quindío · Programa de Ingeniería de Sistemas y Computación · Semestre 2026-2

**Equipo:** Daniel Josué Narváez Hincapié · Camilo Alberto Ospina

> 📌 Este documento se encuentra en construcción. Las secciones 1 a 3 corresponden al borrador inicial (tarea ARQ-3, Sprint 1); la sección 4 se completó en el Sprint 2 (tarea DOC-A1). Las secciones restantes se irán completando en los sprints siguientes conforme se implementen los modelos de IA, el análisis comparativo, el clustering, el despliegue y el uso de IA generativa (ver tabla de estado al final).

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

1. Extracción de texto crudo (título, autores, abstract) de cada uno de los 20 PDFs (tarea EXT-1).
2. Estructuración del corpus en un formato uniforme JSON/CSV con los campos `{id, titulo, autores, abstract}` (tarea EXT-2).
3. Validación manual de una muestra del corpus contra los PDF originales, para detectar errores de extracción como saltos de línea, caracteres especiales o autores mal separados (tarea PRE-2).
4. Preprocesamiento del texto de los abstracts (tokenización, minúsculas, eliminación de stopwords/puntuación, lematización/stemming) mediante una función reutilizable, empleada por todos los algoritmos posteriores (tarea PRE-1).

> ⚠️ **Estado actual:** al momento de redactar este borrador, el equipo aún no ha recibido los 20 artículos PDF por parte del docente, por lo que las tareas de extracción (EXT-1, EXT-2) y preprocesamiento (PRE-1, PRE-2) todavía no se han ejecutado. Esta sección se actualizará con las decisiones técnicas concretas (librerías finales usadas, estructura exacta del JSON, hallazgos de la validación) una vez el corpus esté disponible y procesado.

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

## Estado del documento

| Sección | Contenido | Estado | Sprint |
|---|---|---|---|
| 1. Introducción | Contexto y propósito del proyecto | ✅ Completa | Sprint 1 |
| 2. Fuentes de información | Corpus y proceso de obtención | 🟡 Borrador (pendiente corpus real) | Sprint 1 |
| 3. Arquitectura | Módulos y stack tecnológico | ✅ Completa | Sprint 1 |
| 4. Algoritmos clásicos | Implementación, complejidad y caso de estudio | ✅ Completa | Sprint 2 |
| 5. Modelos de IA | Embeddings y análisis comparativo clásicos vs. IA | ⬜ Pendiente | Sprint 3 |
| 6. Clustering jerárquico | Implementación, dendrogramas y métrica de evaluación | ⬜ Pendiente | Sprint 4 |
| 7. Despliegue | Arquitectura de despliegue y guía de uso | ⬜ Pendiente | Sprint 5 |
| 8. Declaración de uso de IA generativa | Herramientas usadas como apoyo al desarrollo | ⬜ Pendiente | Sprint 5 |
| 9. Conclusiones | Cierre general del proyecto | ⬜ Pendiente | Sprint 6 |
