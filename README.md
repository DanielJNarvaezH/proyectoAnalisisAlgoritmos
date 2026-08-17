# Análisis de Algoritmos en el Contexto de la Bibliometría

Similitud Textual y Agrupamiento de Artículos Científicos sobre IA Generativa.

Proyecto final — Análisis de Algoritmos · Universidad del Quindío · Semestre 2026-2.

## Equipo

| Integrante | Rol en el proyecto |
|---|---|
| Daniel Josué Narváez Hincapié | Preprocesamiento, algoritmos clásicos (Levenshtein/Needleman-Wunsch), embeddings Word2Vec/FastText, clustering (Single/Complete Linkage), backend, arquitectura |
| Camilo Alberto Ospina | Extracción de datos, algoritmos clásicos (TF-IDF/Jaccard), embeddings vía LLM, clustering (Average Linkage), frontend, despliegue |

## Descripción del proyecto

El proyecto implementa, **desde cero y sin librerías que resuelvan los algoritmos directamente**, dos grandes bloques:

1. **Similitud textual** entre abstracts de 20 artículos científicos: 4 algoritmos clásicos (Levenshtein, Needleman-Wunsch, TF-IDF + Coseno, Jaccard) y 2 enfoques de IA (embeddings).
2. **Agrupamiento jerárquico (clustering)** de los 20 abstracts: 3 criterios de enlace (Single, Complete, Average Linkage) con su dendrograma y una métrica de evaluación interna.

Todo corre sobre una aplicación desplegada (backend + interfaz) y está documentado en el documento técnico del proyecto.

> Librerías como `pypdf`, `NLTK`/`spaCy`, `NumPy`/`Pandas` sí están permitidas para extracción, preprocesamiento y estructuras de datos. `matplotlib`/`scipy` solo se usan para **graficar**, nunca para calcular similitud o clustering (eso va implementado a mano).

## Estructura del repositorio

```
├── docs/               # Documento técnico, diagramas, casos de estudio, dendrogramas
│   └── dendrogramas/
├── src/                # Código fuente de los algoritmos
│   ├── classic/        # Levenshtein, Needleman-Wunsch, TF-IDF+Coseno, Jaccard
│   ├── ia/              # Embeddings (Word2Vec/FastText, modelo de lenguaje)
│   ├── clustering/      # Single/Complete/Average Linkage, matriz de distancias
│   └── preprocessing.py # Limpieza y normalización de texto
├── data/
│   ├── raw/             # Texto crudo extraído de los 20 PDFs
│   └── corpus/          # Corpus estructurado (JSON/CSV)
├── notebooks/           # Notebooks de exploración y pruebas
├── tests/                # Pruebas unitarias
└── backend/              # API (FastAPI/Flask) que expone los algoritmos
```

## Cómo levantar el proyecto localmente

```bash
# 1. Clonar el repo
git clone https://github.com/<usuario>/analisis-algoritmos-bibliometria.git
cd analisis-algoritmos-bibliometria

# 2. Crear tu propio entorno virtual (no se comparte por Git)
python -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate

# 3. Instalar dependencias (una vez exista requirements.txt, tarea SET-3)
pip install -r requirements.txt
```

## Convenciones de trabajo

### Ramas

Formato: `feat/<componente>`

Ejemplos:
- `feat/preprocesamiento`
- `feat/tfidf-coseno`
- `feat/clustering-single-linkage`
- `feat/backend-api`
- `fix/<descripcion-corta>` para correcciones puntuales
- `docs/<descripcion-corta>` para cambios solo de documentación

`main` siempre debe quedar en estado funcional. Se trabaja en la rama del componente y se integra a `main` cuando la tarea está lista (merge o pull request, según acuerden).

### Formato de commits

Se sigue un estilo tipo *Conventional Commits*:

```
<tipo>(<alcance>): <descripción corta en presente>
```

Tipos usados:
- `feat`: nueva funcionalidad (ej. `feat(clustering): implementar single linkage`)
- `fix`: corrección de errores
- `docs`: cambios en documentación (README, /docs)
- `test`: pruebas unitarias
- `chore`: tareas de mantenimiento (estructura, configuración, dependencias)
- `refactor`: cambios de código que no alteran el comportamiento

Ejemplos reales para este proyecto:
```
chore: estructura inicial del proyecto
feat(preprocessing): tokenización y eliminación de stopwords
feat(classic): implementar algoritmo de Levenshtein con programación dinámica
feat(clustering): construir matriz de distancias TF-IDF
docs(caso-estudio): documentar demostración matemática Levenshtein/NW
```

## Tablero Jira

El tablero de Jira contiene las 6 épicas y todas las tareas del [cronograma del proyecto](./docs/cronograma.md), con sprint, responsable, estimación y prioridad asignados a cada una.

## Documentación técnica

El documento técnico completo (arquitectura, implementación, análisis matemático y crítico, declaración de uso de IA) se encuentra en `/docs/documento_tecnico.md` y se va consolidando sprint a sprint.
