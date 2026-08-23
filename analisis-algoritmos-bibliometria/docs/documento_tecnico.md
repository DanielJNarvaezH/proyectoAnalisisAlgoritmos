# Documento Técnico del Proyecto

**Análisis de Algoritmos en el Contexto de la Bibliometría**
Universidad del Quindío · Programa de Ingeniería de Sistemas y Computación · Semestre 2026-2

**Equipo:** Daniel Josué Narváez Hincapié · Camilo Alberto Ospina

> 📌 Este documento se encuentra en construcción. Las secciones 1 a 3 corresponden al borrador inicial (tarea ARQ-3, Sprint 1). Las secciones restantes se irán completando en los sprints siguientes conforme se implementen los algoritmos, el análisis comparativo, el clustering, el despliegue y el uso de IA generativa (ver tabla de estado al final).

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

## Estado del documento

| Sección | Contenido | Estado | Sprint |
|---|---|---|---|
| 1. Introducción | Contexto y propósito del proyecto | ✅ Completa | Sprint 1 |
| 2. Fuentes de información | Corpus y proceso de obtención | 🟡 Borrador (pendiente corpus real) | Sprint 1 |
| 3. Arquitectura | Módulos y stack tecnológico | ✅ Completa | Sprint 1 |
| 4. Algoritmos clásicos | Implementación, complejidad y caso de estudio | ⬜ Pendiente | Sprint 2 |
| 5. Modelos de IA | Embeddings y análisis comparativo clásicos vs. IA | ⬜ Pendiente | Sprint 3 |
| 6. Clustering jerárquico | Implementación, dendrogramas y métrica de evaluación | ⬜ Pendiente | Sprint 4 |
| 7. Despliegue | Arquitectura de despliegue y guía de uso | ⬜ Pendiente | Sprint 5 |
| 8. Declaración de uso de IA generativa | Herramientas usadas como apoyo al desarrollo | ⬜ Pendiente | Sprint 5 |
| 9. Conclusiones | Cierre general del proyecto | ⬜ Pendiente | Sprint 6 |
