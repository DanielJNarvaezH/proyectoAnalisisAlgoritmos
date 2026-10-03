# Reporte Comparativo de Similitud Textual: Artículo 2 vs Artículo 9

Este documento presenta los resultados de la comparación de similitud textual entre el **Artículo 2** y el **Artículo 9** utilizando tanto algoritmos clásicos (léxicos/sintácticos) como modelos basados en Inteligencia Artificial (semánticos/embeddings).

---

## 📊 Tabla Resumen de Resultados

La siguiente tabla unifica las métricas obtenidas por cada uno de los enfoques evaluados:

| Algoritmo | Tipo | Similitud (0 a 1) | Distancia Euclidiana |
| :--- | :--- | :---: | :---: |
| **Levenshtein** | Clásico | 0.0901 | - |
| **Needleman-Wunsch** | Clásico | 0.0901 | - |
| **Coseno TF-IDF** | Clásico | 0.2553 | - |
| **Jaccard** | Clásico | 0.1583 | - |
| **Word2Vec (Coseno)** | IA | 0.9318 | 0.3806 |
| **Word2Vec (Euclidiana $1/(1+d)$)** | IA | 0.7243 | 0.3806 |
| **MPNet (Coseno)** | IA | 0.8376 | 0.5698 |
| **MPNet (Euclidiana $1/(1+d)$)** | IA | 0.6370 | 0.5698 |

---

## 🔬 Detalle de Matrices por Algoritmo

### 1. Algoritmos Clásicos

#### Similitud Levenshtein / Needleman-Wunsch
*Miden la distancia de edición y el alineamiento entre las secuencias de **tokens** (palabras) de los abstracts preprocesados, no entre caracteres. Ambos usan programación dinámica; por qué coinciden en este caso se analiza en `docs/analisis_comparativo.md`.*

| Art. ID | [2] | [9] |
| :--- | :---: | :---: |
| **[2]** | 1.0000 | 0.0901 |
| **[9]** | 0.0901 | 1.0000 |

#### Similitud Coseno TF-IDF
*Mide la coincidencia de palabras clave ponderadas por su rareza en el corpus.*

| Art. ID | [2] | [9] |
| :--- | :---: | :---: |
| **[2]** | 1.0000 | 0.2553 |
| **[9]** | 0.2553 | 1.0000 |

#### Similitud Jaccard
*Mide la intersección sobre la unión de palabras únicas.*

| Art. ID | [2] | [9] |
| :--- | :---: | :---: |
| **[2]** | 1.0000 | 0.1583 |
| **[9]** | 0.1583 | 1.0000 |

---

### 2. Modelos de Inteligencia Artificial (Embeddings)

#### Word2Vec

* **Similitud Coseno:**

  | Art. ID | [2] | [9] |
  | :--- | :---: | :---: |
  | **[2]** | 1.0000 | 0.9318 |
  | **[9]** | 0.9318 | 1.0000 |

* **Distancia Euclidiana:**

  | Art. ID | [2] | [9] |
  | :--- | :---: | :---: |
  | **[2]** | 0.0000 | 0.3806 |
  | **[9]** | 0.3806 | 0.0000 |

* **Similitud Euclidiana $1/(1+d)$:**

  | Art. ID | [2] | [9] |
  | :--- | :---: | :---: |
  | **[2]** | 1.0000 | 0.7243 |
  | **[9]** | 0.7243 | 1.0000 |

#### MPNet

* **Similitud Coseno:**

  | Art. ID | [2] | [9] |
  | :--- | :---: | :---: |
  | **[2]** | 1.0000 | 0.8376 |
  | **[9]** | 0.8376 | 1.0000 |

* **Distancia Euclidiana:**

  | Art. ID | [2] | [9] |
  | :--- | :---: | :---: |
  | **[2]** | 0.0000 | 0.5698 |
  | **[9]** | 0.5698 | 0.0000 |

* **Similitud Euclidiana $1/(1+d)$:**

  | Art. ID | [2] | [9] |
  | :--- | :---: | :---: |
  | **[2]** | 1.0000 | 0.6370 |
  | **[9]** | 0.6370 | 1.0000 |
