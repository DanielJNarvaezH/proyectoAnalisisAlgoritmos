# Análisis de Algoritmos en el Contexto de la Bibliometría

Similitud textual, agrupamiento, búsqueda de patrones y ranking de términos sobre artículos científicos de IA generativa.

Proyecto final — Análisis de Algoritmos · Universidad del Quindío · Semestre 2026-2.

## Contenido

1. [Aplicación desplegada](#aplicación-desplegada)
2. [Descripción del proyecto](#descripción-del-proyecto)
3. [Estructura del repositorio](#estructura-del-repositorio)
4. [Instalación](#instalación)
5. [Ejecución local](#ejecución-local)
6. [Generación de embeddings](#generación-de-embeddings)
7. [Pruebas](#pruebas)
8. [Equipo y convenciones de trabajo](#equipo)
9. [Documentación técnica](#documentación-técnica)

---

## Aplicación desplegada

🔗 **https://bibliometria-algoritmos.streamlit.app/**

La aplicación corre en Streamlit Community Cloud y no necesita instalación: basta abrir el enlace en el navegador.

| Pestaña | Qué hace |
|---|---|
| **Similitudes** | Compara los artículos seleccionados con 6 algoritmos: Levenshtein, Needleman-Wunsch, TF-IDF + Coseno, Jaccard y embeddings de IA (Word2Vec y MPNet) |
| **Dendrogramas** | Clustering jerárquico con Single, Complete y Average Linkage, con evaluación y partición en *k* grupos |
| **Artículos** | Título, autores y abstract de los artículos seleccionados |
| **Búsqueda de patrones** | Busca un patrón en los abstracts con KMP, Rabin-Karp y Boyer-Moore, y verifica que los tres coincidan |
| **Ranking de términos** | Ordena los términos por frecuencia con Counting, Radix y Bucket Sort |

**Cómo usarla**

1. En la barra lateral elige los artículos (por defecto están los 20) y pulsa **Ejecutar algoritmos**. Esto alimenta *Similitudes*, *Dendrogramas* y *Artículos*.
2. *Búsqueda de patrones* y *Ranking de términos* trabajan siempre sobre los 20 artículos y no dependen de la selección ni del botón.

**Notas**

- Si la app lleva un tiempo sin visitas, Streamlit Cloud la pone a dormir. Pulsa **"Yes, get this app back up!"** y espera uno o dos minutos.
- Los embeddings de los modelos de IA están **precalculados** en `data/embeddings/`; la aplicación no descarga ni ejecuta los modelos.

---

## Descripción del proyecto

El proyecto implementa **desde cero**, sin librerías que resuelvan los algoritmos directamente, cuatro bloques sobre 20 abstracts:

1. **Similitud textual:** 4 algoritmos clásicos (Levenshtein, Needleman-Wunsch, TF-IDF + Coseno, Jaccard) y 2 enfoques de IA (embeddings Word2Vec y MPNet, con coseno y distancia euclidiana calculados a mano).
2. **Agrupamiento jerárquico:** Single, Complete y Average Linkage, con dendrograma y métricas de evaluación interna.
3. **Búsqueda de patrones:** KMP, Rabin-Karp y Boyer-Moore, con verificación cruzada.
4. **Ranking de términos:** Counting Sort, Radix Sort y Bucket Sort.

> `pypdf`, `NLTK`, `NumPy` y `Pandas` se usan para extracción, preprocesamiento y estructuras de datos. `matplotlib`, `plotly` y `scipy` solo sirven para **graficar**, nunca para calcular similitud ni clustering. Los modelos preentrenados (`gensim`, `sentence-transformers`) solo aportan los vectores; el promedio de documento, el coseno y la distancia euclidiana se implementan a mano.

---

## Estructura del repositorio

```
proyectoAnalisisAlgoritmos/
├── README.md
├── requirements.txt                 # Pipeline de datos y embeddings
├── LICENSE
├── .github/workflows/e2e.yml        # Pruebas E2E programadas
└── analisis-algoritmos-bibliometria/
    ├── app.py                       # Interfaz Streamlit (la app desplegada)
    ├── requirements.txt             # Dependencias de la app
    ├── requirements-backend.txt     # Dependencias del backend Flask
    ├── backend/app.py               # API Flask que expone los algoritmos
    ├── src/
    │   ├── extraer_datos.py         # PDFs -> CSV
    │   ├── csv_json.py              # CSV -> corpus.json
    │   ├── preprocessing.py         # Limpieza y lematización
    │   ├── comparador.py            # Orquesta los 6 algoritmos de similitud
    │   ├── classic/                 # Levenshtein, Needleman-Wunsch, TF-IDF, Jaccard
    │   ├── ia/                      # Embeddings (Word2Vec, MPNet) y métricas
    │   ├── clustering/              # Single/Complete/Average Linkage, dendrograma, evaluación
    │   ├── busqueda/                # KMP, Rabin-Karp, Boyer-Moore
    │   └── ordenamiento/            # Counting, Radix, Bucket Sort y frecuencias
    ├── data/
    │   ├── corpus.json              # Corpus estructurado
    │   ├── corpus_preprocesado.json # Abstracts lematizados
    │   ├── embeddings/              # word2vec.json, mpnet.json
    │   ├── clustering/              # Matrices de enlace y evaluación
    │   ├── resultados/              # Resultados de análisis comparativo
    │   └── raw/                     # CSV extraído de los PDFs
    ├── notebooks/                   # Scripts de análisis y casos de estudio
    ├── docs/                        # Documento técnico, diagramas, dendrogramas
    └── tests/                       # Unitarias por módulo + e2e/
```

---

## Instalación

**Requisitos:** Python 3.10 o superior y Git.

```bash
# 1. Clonar el repositorio
git clone https://github.com/DanielJNarvaezH/proyectoAnalisisAlgoritmos.git
cd proyectoAnalisisAlgoritmos

# 2. Crear el entorno virtual (no se comparte por Git)
python -m venv venv
```

Activar el entorno:

```powershell
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```
```bash
# Linux / macOS
source venv/bin/activate
```

> En PowerShell, si la activación falla por permisos: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

Hay dos archivos de dependencias, según lo que vayas a hacer:

| Para… | Instala |
|---|---|
| Solo ejecutar la aplicación y las pruebas | `pip install -r analisis-algoritmos-bibliometria/requirements.txt` |
| Regenerar datos o embeddings (incluye `gensim` y `sentence-transformers`, pesados) | `pip install -r requirements.txt` |
| Ejecutar además el backend Flask | `pip install -r analisis-algoritmos-bibliometria/requirements-backend.txt` |

Para la mayoría de los casos basta la primera línea:

```bash
pip install -r analisis-algoritmos-bibliometria/requirements.txt
```

NLTK descarga sus recursos (stopwords, WordNet, etc.) automáticamente la primera vez que se usa `preprocessing.py`.

---

## Ejecución local

Todos los comandos se ejecutan desde la carpeta del proyecto, con el entorno virtual activo:

```bash
cd analisis-algoritmos-bibliometria
```

### Aplicación Streamlit

```bash
streamlit run app.py
```

Se abre en http://localhost:8501. Usa los datos y embeddings ya incluidos en `data/`, por lo que no necesita descargar ningún modelo.

### Backend Flask (opcional)

```bash
pip install -r requirements-backend.txt
python backend/app.py
```

Queda en http://127.0.0.1:5000 (el puerto se puede cambiar con la variable `PORT`). Endpoints:

| Endpoint | Descripción |
|---|---|
| `GET /articulos` | Lista de los 20 artículos |
| `GET /similitud?articulos=2,9` | Matrices de similitud (4 clásicos + 2 de IA) |
| `GET /clustering?criterio=single` | Matriz de enlace y correlación cofenética (`single`, `complete`, `average`) |
| `GET /busqueda?patron=education` | Ocurrencias con KMP, Rabin-Karp y Boyer-Moore (`ignorar_mayusculas=true`) |
| `GET /ranking?algoritmo=counting&top=15` | Ranking de términos (`counting`, `radix`, `bucket`) |

### Pipeline de datos (opcional)

El repositorio ya trae `corpus.json` y `corpus_preprocesado.json`; solo necesitas esto para reconstruirlos. Los scripts de extracción usan rutas relativas a la **raíz del repositorio** (`proyectoAnalisisAlgoritmos/`), y los PDFs originales deben estar en `analisis-algoritmos-bibliometria/data/pdfs/` (esa carpeta no se versiona).

```bash
# Desde la raíz del repositorio
python analisis-algoritmos-bibliometria/src/extraer_datos.py   # PDFs -> data/raw/articulos_extraidos.csv
python analisis-algoritmos-bibliometria/src/csv_json.py        # CSV  -> data/corpus.json

# Desde analisis-algoritmos-bibliometria/
python src/preprocessing.py                                    # corpus.json -> corpus_preprocesado.json
```

Requiere `pip install -r requirements.txt` (el de la raíz).

---

## Generación de embeddings

Los embeddings ya están calculados y versionados en `data/embeddings/`. Solo hay que regenerarlos si cambia el corpus o el preprocesamiento. Requiere `pip install -r requirements.txt` (el de la raíz) y ejecutar desde `analisis-algoritmos-bibliometria/`.

| | Word2Vec | MPNet |
|---|---|---|
| Script | `src/ia/embeddings_w2v.py` | `src/ia/embeddings_llm.py` |
| Modelo | `word2vec-google-news-300` | `sentence-transformers/all-mpnet-base-v2` |
| Dimensión | 300 | 768 |
| Entrada | `abstract_preprocesado` (tokens lematizados) | `abstract` original, sin preprocesar |
| Vector del documento | Promedio de vectores de palabra, calculado a mano | Lo produce el modelo (mean pooling) |
| Descarga inicial | ~1,6 GB | ~420 MB |
| Memoria | ~3,6 GB de RAM (modelo completo) | Moderada |
| Salida | `data/embeddings/word2vec.json` | `data/embeddings/mpnet.json` |

### Word2Vec

```bash
python src/ia/embeddings_w2v.py
```

Opciones:

| Opción | Efecto |
|---|---|
| `--limite N` | Carga solo las N palabras más frecuentes del modelo (menos RAM). Ej.: `--limite 1000000` |
| `--ruta-modelo ARCHIVO` | Usa un `.gz`/`.bin` ya descargado, sin el descargador de gensim |
| `--sin-expansiones` | No expande las siglas del dominio (solo para comparar) |

Si la descarga automática se corta, baja el archivo con el navegador (reanuda descargas) desde
https://github.com/RaRe-Technologies/gensim-data/releases/download/word2vec-google-news-300/word2vec-google-news-300.gz
y ejecuta:

```bash
python src/ia/embeddings_w2v.py --ruta-modelo "D:\modelos-ia\word2vec-google-news-300.gz"
```

Al terminar imprime un reporte de cobertura por artículo y avisa de los que quedan por debajo del 90 %.

### MPNet

```bash
python src/ia/embeddings_llm.py
```

Verifica además si algún abstract supera las 384 sub-palabras del modelo (se truncaría sin aviso) y reporta la norma de los vectores.

### Dónde se guardan los modelos

Ambos modelos se descargan a una caché fuera del repositorio. Para controlarla, define la variable **antes** de ejecutar:

```powershell
# Windows (PowerShell)
$env:GENSIM_DATA_DIR = "D:\modelos-ia"
$env:HF_HOME = "D:\modelos-ia\huggingface"
```
```bash
# Linux / macOS
export GENSIM_DATA_DIR=~/modelos-ia
export HF_HOME=~/modelos-ia/huggingface
```

Sin ellas, gensim usa `~/gensim-data` y Hugging Face `~/.cache/huggingface`. **Mantén los modelos fuera del repositorio y de carpetas sincronizadas como OneDrive**: pesan gigabytes.

### Después de regenerar

Los resultados de similitud y clustering con IA cambian al regenerar los embeddings. Si usas las pruebas E2E, actualiza los valores de Word2Vec y MPNet en `tests/e2e/golden.py` (`PAR_2_9`) y revisa los resultados de `data/clustering/` y `data/resultados/` con los scripts de `notebooks/`.

---

## Pruebas

```bash
cd analisis-algoritmos-bibliometria

# Unitarias (rápidas)
python -m pytest tests --ignore=tests/e2e -v

# End-to-end sobre la app desplegada (lentas)
pip install -r tests/e2e/requirements-e2e.txt
python -m playwright install chromium
cd tests/e2e
python -m pytest -m "not api" -v
```

Las E2E recorren los cuatro módulos sobre la URL desplegada. Para probar una copia local, define `APP_URL=http://localhost:8501/` (en PowerShell: `$env:APP_URL = "http://localhost:8501/"`). Detalles y solución de errores en `tests/e2e/README.md`.

---

## Equipo

| Integrante | Rol en el proyecto |
|---|---|
| Daniel Josué Narváez Hincapié | Preprocesamiento; Levenshtein y Needleman-Wunsch; Word2Vec; Single y Complete Linkage, dendrograma y evaluación; KMP y Rabin-Karp; Counting y Bucket Sort; API Flask; arquitectura; despliegue; documentación técnica |
| Camilo Alberto Ospina | Extracción de datos; TF-IDF + Coseno y Jaccard; MPNet; matriz de distancias, Average Linkage y dibujo de dendrogramas; Boyer-Moore y verificación de la búsqueda; frecuencias y Radix Sort; interfaz Streamlit; pruebas E2E |

## Convenciones de trabajo

### Ramas

Dado que el equipo es de 2 personas y las tareas están claramente repartidas por componente (ver Jira), se trabaja **directamente sobre `main`**, sin ramas por funcionalidad. Cada quien comitea y hace push de su propia tarea cuando la termina.

- Antes de empezar, hacer **Fetch origin / Pull** para traer los últimos cambios del compañero.
- Evitar editar el mismo archivo al mismo tiempo que el otro integrante.
- Comitear con frecuencia y en unidades pequeñas (una tarea o subtarea por commit).
- Si surge un conflicto de merge, se resuelve entre los dos antes de seguir.

### Formato de commits

Estilo *Conventional Commits*:

```
<tipo>(<alcance>): <descripción corta en presente>
```

Tipos: `feat` (funcionalidad), `fix` (corrección), `docs` (documentación), `test` (pruebas), `chore` (mantenimiento), `refactor` (sin cambio de comportamiento).

```
chore: estructura inicial del proyecto
feat(preprocessing): tokenización y eliminación de stopwords
feat(clustering): construir matriz de distancias TF-IDF
docs(caso-estudio): documentar demostración matemática Levenshtein/NW
```

## Documentación técnica

El documento técnico completo (arquitectura, implementación, análisis matemático y crítico, declaración de uso de IA) está en [`analisis-algoritmos-bibliometria/docs/documento_tecnico.md`](analisis-algoritmos-bibliometria/docs/documento_tecnico.md). Las decisiones sobre los modelos de IA están en `docs/modelos_ia.md`.