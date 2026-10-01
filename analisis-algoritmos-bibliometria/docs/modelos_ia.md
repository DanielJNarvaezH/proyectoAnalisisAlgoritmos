# Selección de Modelos de IA para Similitud Textual (IA-1)

**Requerimiento 1, parte 2 · Sprint 3 · Responsable: Daniel Narváez**

Este documento evalúa los modelos preentrenados candidatos para los dos enfoques de similitud basados en embeddings que exige el Requerimiento 1, y justifica la elección de cada uno. Las tareas IA-2 e IA-3 implementan los modelos elegidos aquí.

---

## 1. Qué exige el enunciado y qué implica

El enunciado pide **dos enfoques de similitud apoyados en embeddings** (representaciones vectoriales densas). Permite usar modelos preentrenados (menciona Word2Vec, FastText y modelos de lenguaje vía APIs o librerías) para vectorizar los abstracts y, después, calcular la similitud métrica (distancia euclidiana o coseno) entre los vectores.

Al mismo tiempo, el proyecto prohíbe usar funciones de alto nivel que implementen directamente los algoritmos solicitados. De ahí sale la división de responsabilidades que sigue todo este documento:

| Paso | Lo aporta | Justificación |
|---|---|---|
| Vectores de palabras o de documento | Modelo preentrenado (librería) | Permitido explícitamente por el enunciado. Entrenar un modelo propio no es viable con este corpus (sección 4.1). |
| Combinar vectores de palabras en un vector de documento (Word2Vec) | Implementación propia | Es parte del diseño algorítmico del enfoque; se programa con estructuras básicas. |
| Similitud coseno y distancia euclidiana | Implementación propia (IA-4) | Es el algoritmo de similitud solicitado. No se usan `model.similarity`, `util.cos_sim`, `sklearn` ni `scipy.spatial`. |
| Matriz de similitud entre N artículos | Implementación propia | Igual que en los algoritmos clásicos (CLA-5). |

Con esto, la IA actúa como apoyo para obtener la representación semántica, y el cálculo de similitud sigue siendo transparente y analizable, en coherencia con lo que se declarará en la sección de uso de IA del documento técnico.

## 2. Características del corpus que condicionan la elección

Las cifras se calcularon sobre `data/corpus.json` y `data/corpus_preprocesado.json` (versión regenerada con la corrección de palabras compuestas):

| Medida | Valor | Por qué importa |
|---|---|---|
| Artículos | 20 | Corpus muy pequeño para entrenar embeddings propios. |
| Tokens preprocesados en total | ≈ 2.500 | Ídem. |
| Vocabulario distinto | 868 términos, 484 de ellos (≈ 56 %) con una sola aparición | Un modelo entrenado aquí vería casi todas las palabras una única vez. |
| Longitud del abstract crudo | 134 a 263 palabras (promedio ≈ 202) | Los modelos de lenguaje truncan la entrada a partir de cierto número de sub-palabras (sección 4.5). |
| Idioma | Inglés | Todos los modelos evaluados tienen versiones preentrenadas en inglés. |

Además, el corpus tiene **términos propios del dominio** que un modelo preentrenado general puede no conocer:

| Término | Apariciones | Artículos donde aparece | Observación |
|---|---|---|---|
| `aied` (AI in Education) | 38 | 7 | Es el 5.º término más frecuente de todo el corpus. |
| `gai` (Generative AI) | 11 | 1 | Sigla. |
| `chatgpt` | 7 | 3 | Término posterior a 2022. |
| `genai` | 5 | 1 | Sigla. |

Estos términos pesan mucho en los algoritmos clásicos (por ejemplo, `aied` es uno de los términos compartidos que explican la similitud TF-IDF entre los artículos 2 y 9). Por eso, cómo trata cada modelo las palabras que no conoce es un criterio central de la evaluación.

## 3. Criterios de evaluación

1. **Calidad semántica** para textos científicos: que abstracts sobre el mismo tema queden cerca aunque usen palabras distintas.
2. **Cobertura del vocabulario del dominio**: comportamiento frente a palabras fuera del vocabulario (OOV) como `aied` o `chatgpt`.
3. **Longitud de entrada**: que el abstract completo quepa en el modelo sin truncarse.
4. **Costo computacional**: tamaño de descarga y memoria necesaria en los equipos del equipo.
5. **Reproducibilidad**: que los resultados se puedan regenerar de forma idéntica, sin depender de un servicio externo.
6. **Aporte al análisis comparativo**: que los dos enfoques elegidos sean conceptualmente distintos entre sí y frente a los clásicos, para que la comparación de CMP-2 diga algo.

## 4. Candidatos evaluados

### 4.1 Word2Vec entrenado sobre el propio corpus — descartado

Entrenar un Word2Vec propio daría control total, pero con ≈ 2.500 tokens y más de la mitad del vocabulario apareciendo una sola vez, el modelo no tendría contextos suficientes para aprender relaciones semánticas estables. Los vectores resultantes reflejarían sobre todo ruido del entrenamiento. Se descarta.

### 4.2 Word2Vec preentrenado — Google News (`word2vec-google-news-300`)

**Qué es.** Modelo de Mikolov et al. (2013), entrenado con la arquitectura *skip-gram* sobre un corpus de noticias de Google de unos 100 mil millones de palabras. Asigna un vector fijo de 300 dimensiones a cada palabra de un vocabulario de unos 3 millones de palabras y frases. El archivo pesa ≈ 1,6 GB.

**Cómo se obtiene un vector por abstract.** Word2Vec produce vectores de *palabras*, no de documentos. El vector del abstract se calcula como el **promedio aritmético** de los vectores de sus tokens:

```
v(d) = (1 / |T|) · Σ v(t)     para cada token t ∈ T, donde T son los tokens de d que existen en el vocabulario del modelo
```

**Ventajas.**
- Es el modelo de embeddings estáticos de referencia y el primero que menciona el enunciado.
- El promedio es un paso sencillo y transparente que se implementa a mano, lo cual se presta para el análisis matemático.
- Carga manejable: gensim permite leer solo las N palabras más frecuentes (parámetro `limit`), reduciendo la memoria si hace falta.

**Limitaciones.**
- **Palabras fuera del vocabulario.** Si una palabra no está en el modelo, no tiene vector y queda excluida del promedio. Se esperaba que `aied`, `chatgpt`, `genai` y `gai` no existieran en un modelo de 2013. La implementación mostró un problema distinto y más sutil: la mayoría sí existe, pero con otro significado (ver sección 8).
- **Vectores estáticos.** Cada palabra tiene un único vector sin importar el contexto (por ejemplo, `model` en "modelo de lenguaje" y en "modelo pedagógico" es el mismo vector).
- **El promedio pierde el orden** de las palabras, igual que TF-IDF y Jaccard.
- El modelo distingue mayúsculas; los tokens del corpus están en minúscula, así que IA-2 debe decidir si prueba también la forma capitalizada cuando la minúscula no existe (por ejemplo `ai` → `AI`).

### 4.3 FastText preentrenado — Facebook (`cc.en.300` / `crawl-300d-2M-subword`)

**Qué es.** Extensión de Word2Vec de Bojanowski et al. (2017). Cada palabra se representa como la suma de los vectores de sus **n-gramas de caracteres** (de 3 a 6 caracteres) más el vector de la palabra completa. Así puede construir un vector incluso para palabras que nunca vio en el entrenamiento.

**Ventajas.**
- Maneja palabras fuera del vocabulario, que es justamente la debilidad de Word2Vec.
- Robusto frente a variantes morfológicas y errores de extracción.

**Limitaciones que pesan en este proyecto.**
- **La capacidad de manejar palabras desconocidas solo existe en el modelo binario completo** (`.bin`, ≈ 7 GB, y requiere una cantidad de memoria RAM similar para cargarlo). Las versiones en texto (`.vec`) y la que se descarga con `gensim.downloader` (`fasttext-wiki-news-subwords-300`) contienen solo los vectores de palabras completas, sin los n-gramas, así que se comportan igual que Word2Vec ante una palabra desconocida.
- **Los términos desconocidos de este corpus son siglas.** Para `aied`, FastText construiría un vector a partir de fragmentos como `aie` o `ied`, que no tienen relación con "AI in Education". El vector existiría, pero su significado sería poco confiable. La ventaja práctica frente a Word2Vec es menor de lo que parece.

### 4.4 Modelos de lenguaje vía librería — `sentence-transformers`

**Qué son.** Modelos basados en la arquitectura Transformer, ajustados para producir directamente un vector por texto completo (Reimers & Gurevych, 2019). A diferencia de Word2Vec y FastText, los vectores son **contextuales**: el significado de cada palabra depende de las palabras que la rodean, y el modelo sí tiene en cuenta el orden.

Se evaluaron tres modelos de la librería:

| Modelo | Dimensión | Entrada máxima | Tamaño aprox. | Observación |
|---|---|---|---|---|
| `all-MiniLM-L6-v2` | 384 | 256 sub-palabras | ≈ 90 MB | Muy liviano y rápido, pero trunca los abstracts más largos del corpus. |
| `all-mpnet-base-v2` | 768 | 384 sub-palabras | ≈ 420 MB | El de mejor calidad general de la familia `all-*`. |
| `allenai-specter` | 768 | 512 sub-palabras | ≈ 440 MB | Especializado en artículos científicos (entrenado con citas entre papers), pero pensado para recibir título + abstract. |

**Sobre la truncación.** Un Transformer divide el texto en sub-palabras (una palabra poco común puede partirse en dos o tres piezas), y lo que exceda la entrada máxima **se descarta en silencio**. Para textos académicos en inglés, cada palabra ocupa en promedio algo más de una sub-palabra, así que los abstracts del corpus (134–263 palabras más la puntuación) ocuparían aproximadamente entre 180 y 380 sub-palabras. Con `all-MiniLM-L6-v2` (256) una buena parte de los abstracts perdería su parte final (normalmente las conclusiones). Con `all-mpnet-base-v2` (384) caben todos o casi todos; el valor exacto se debe medir en IA-3 con el tokenizador del propio modelo.

**Ventajas generales.**
- Capturan paráfrasis y relaciones semánticas que ningún enfoque basado en palabras sueltas detecta.
- Ante una palabra desconocida como `aied`, la dividen en sub-palabras y la interpretan en su contexto ("Artificial Intelligence in Education (AIEd)"), lo que reduce el problema de la sección 2.

**Limitaciones generales.**
- Son una caja negra: no se puede mostrar paso a paso cómo se calcula cada componente del vector, a diferencia del promedio de Word2Vec.
- Requieren PyTorch, que es pesado para instalar y para desplegar.

### 4.5 APIs comerciales de embeddings — descartadas

Servicios como los de OpenAI, Cohere o Voyage producen embeddings de muy buena calidad mediante una llamada HTTP. Se descartan como enfoque principal por cuatro razones:

- **Reproducibilidad.** El proveedor puede actualizar o retirar el modelo, y los resultados del documento técnico dejarían de poder regenerarse.
- **Dependencia de una clave de API y de costos**, que además habría que gestionar como secreto en el despliegue.
- **Opacidad.** El modelo no se puede inspeccionar ni descargar.
- **No aporta frente a `sentence-transformers`** para un corpus de 20 abstracts: la calidad de un modelo local es suficiente y se obtiene sin salir del equipo.

## 5. Cuadro comparativo

| Criterio | Word2Vec (Google News) | FastText (`.bin` completo) | `all-mpnet-base-v2` | API comercial |
|---|---|---|---|---|
| Tipo de vector | Estático, por palabra | Estático, por palabra y sub-palabra | Contextual, por texto | Contextual, por texto |
| Vector del abstract | Promedio propio | Promedio propio | Lo produce el modelo | Lo produce el servicio |
| Palabras desconocidas (`aied`, `chatgpt`) | Se pierden | Vector aproximado por fragmentos | Se interpretan por sub-palabras y contexto | Se interpretan |
| Considera el orden | No | No | Sí | Sí |
| Abstract completo sin truncar | Sí | Sí | Sí o casi (verificar) | Sí |
| Descarga / memoria | ≈ 1,6 GB | ≈ 7 GB | ≈ 420 MB + PyTorch | Ninguna local |
| Reproducible offline | Sí | Sí | Sí | No |
| Explicable paso a paso | Sí (el promedio) | Parcialmente | No | No |

## 6. Decisión

### Enfoque de IA 1 (tarea IA-2, Daniel Narváez): **Word2Vec preentrenado de Google News**

- **Modelo:** `word2vec-google-news-300`, cargado con gensim (`KeyedVectors`).
- **Entrada:** `abstract_preprocesado` (tokens en minúscula, sin *stopwords* y lematizados). Se usa el texto preprocesado porque, al promediar, las *stopwords* aportarían vectores casi iguales en todos los documentos y acercarían artificialmente todos los abstracts entre sí.
- **Vector del documento:** promedio de los vectores de los tokens presentes en el modelo, implementado a mano.
- **Palabras desconocidas:** se excluyen del promedio y se registran. IA-2 debe reportar, por artículo, qué porcentaje de tokens se encontró en el modelo y cuáles faltaron.
- **Siglas del dominio:** se reemplazan por su forma expandida antes de buscarlas (decisión tomada durante IA-2 a partir del diagnóstico de la sección 8).

**Por qué Word2Vec y no FastText.** La ventaja real de FastText (vectores para palabras desconocidas) exige un archivo de ≈ 7 GB y una cantidad de memoria similar, y en este corpus las palabras desconocidas relevantes son siglas, para las cuales los fragmentos de caracteres no aportan un significado confiable. Word2Vec ofrece el mismo tipo de representación (vectores estáticos promediados) con una cuarta parte del costo, y su limitación con el vocabulario del dominio se convierte en un hallazgo medible y útil para el análisis comparativo en lugar de un problema oculto.

**Plan B.** Si en IA-2 la cobertura de tokens resulta muy baja (por ejemplo, menos del 90 % en varios artículos), se reevaluará FastText con el modelo binario completo.

### Enfoque de IA 2 (tarea IA-3, Camilo Ospina): **`sentence-transformers` con `all-mpnet-base-v2`**

- **Modelo:** `sentence-transformers/all-mpnet-base-v2`.
- **Entrada:** el campo `abstract` **original**, sin preprocesar. Los modelos Transformer se entrenaron con texto natural y dependen de las *stopwords*, la puntuación y las formas originales de las palabras para interpretar el contexto; lematizar y eliminar *stopwords* les quitaría justamente la información que los diferencia de Word2Vec. Esta diferencia de entrada respecto a los demás algoritmos debe declararse en el análisis comparativo.
- **Vector del documento:** lo produce el modelo (768 dimensiones).
- **Verificación obligatoria en IA-3:** medir con el tokenizador del modelo cuántas sub-palabras ocupa cada abstract y reportar si alguno supera las 384 y queda truncado.

**Por qué `all-mpnet-base-v2`.** Es el modelo de mayor calidad general de su familia, admite la entrada más larga de los modelos generales (384 sub-palabras, suficiente para el corpus) y es de uso libre y reproducible. `all-MiniLM-L6-v2` se descarta porque truncaría parte de los abstracts, y `allenai-specter` porque está diseñado para recibir título y abstract juntos, mientras que el enunciado centra el análisis en el abstract.

**Plan B.** Si IA-3 detecta que varios abstracts superan las 384 sub-palabras, se puede usar `allenai-specter` (512 sub-palabras) con solo el abstract como entrada, documentando la decisión.

### Por qué esta combinación sirve para el análisis crítico

Los dos enfoques elegidos representan dos generaciones distintas de embeddings, y cada uno se relaciona de forma distinta con los algoritmos clásicos:

| | Clásicos de edición (Levenshtein, NW) | Clásicos vectoriales (TF-IDF, Jaccard) | Word2Vec promediado | `all-mpnet-base-v2` |
|---|---|---|---|---|
| ¿Qué compara? | Secuencias exactas de tokens | Vocabulario compartido | Significado de las palabras | Significado del texto completo |
| ¿Considera el orden? | Sí | No | No | Sí |
| ¿Reconoce sinónimos? | No | No | Sí | Sí |

Esto permite plantear en CMP-2 preguntas concretas. Por ejemplo, si Word2Vec da una similitud mayor que TF-IDF para el mismo par, la diferencia se explica por sinónimos o términos relacionados que TF-IDF trata como palabras distintas. Y si `all-mpnet-base-v2` supera a Word2Vec, la diferencia se atribuye al contexto y al orden.

## 7. Implicaciones técnicas para las siguientes tareas

1. **Embeddings precalculados.** Como el corpus es estático, los vectores de los 20 abstracts se calcularán una sola vez y se guardarán en `data/embeddings/` (por ejemplo, `word2vec.json` y `mpnet.json`, con el `numero` del artículo como clave). IA-4, el clustering y el backend leerán esos archivos sin cargar los modelos, lo que evita llevar gensim, PyTorch ni archivos de gigabytes al despliegue del Sprint 5.
2. **Los modelos no se suben al repositorio.** Se recomienda activar en `.gitignore` las líneas ya previstas (`*.bin`, `*.model`) y agregar la carpeta de caché de modelos que se use.
3. **Dependencias nuevas.** Al implementar IA-2 e IA-3 se agregarán `gensim` y `sentence-transformers` a `requirements.txt`. Hay que verificar que la versión de gensim instalada sea compatible con numpy 2.x (la del entorno actual), porque algunas versiones de gensim exigían numpy 1.x.
4. **Similitud implementada a mano (IA-4).** La similitud coseno y la distancia euclidiana se implementarán en `src/ia/` con operaciones básicas, sin usar las funciones de similitud de las librerías de los modelos.

## 8. Resultados de la implementación (IA-2)

**Implementación:** `src/ia/embeddings_w2v.py` · **Pruebas:** `tests/ia/test_embeddings_w2v.py` · **Resultado:** `data/embeddings/word2vec.json` (20 vectores de 300 dimensiones).

### 8.1 Cobertura del vocabulario

Se cargó el modelo completo (3.000.000 de palabras). La cobertura fue mucho mayor de lo previsto en la sección 4.2:

| Medida | Sin expansión de siglas | Con expansión de siglas (versión final) |
|---|---|---|
| Cobertura global | 2.515 de 2.532 tokens (99,3 %) | 2.525 de 2.532 tokens (99,7 %) |
| Artículos con 100 % de cobertura | 14 de 20 | 17 de 20 |
| Cobertura más baja | Art. 12 (95,0 %) | Art. 12 (96,9 %) |

En la versión final quedan 7 tokens sin vector, cada uno con una sola aparición: `ebscohost`, `openalex`, `researchgate`, `sciencedirect` y `synthesised` (art. 12), `entailment` (art. 5) y `coauthorship` (art. 15). Casi todos son nombres de bases de datos y plataformas, que aportan poco al significado del abstract. Ningún artículo quedó por debajo del 90 %, así que el plan B (FastText) no fue necesario.

Doce tokens se encontraron con otra forma de escritura. Por ejemplo, `nlp` → `NLP` y `scopus` → `Scopus`. También aparecieron formas británicas como `behaviour` → `Behaviour`, porque el modelo se entrenó con noticias mayoritariamente estadounidenses y solo tiene esas formas con mayúscula inicial.

### 8.2 Hallazgo: siglas del dominio con un significado equivocado

Una cobertura alta no garantiza que los vectores signifiquen lo correcto. Con `notebooks/diagnostico_terminos_w2v.py` se revisaron las palabras más cercanas a cada sigla del dominio en el modelo. La función `most_similar` de gensim se usó solo como herramienta de diagnóstico, no para calcular similitudes del proyecto:

| Término del corpus | Apariciones | Forma encontrada | Palabras más cercanas en el modelo | Significado real en el modelo |
|---|---|---|---|---|
| `ai` | 86 | `ai` | `che`, `te`, `essere`, `tutto` | Palabra del italiano |
| `aied` | 38 | `Aied` | `army_Capt._Fatik`, `Ali_Farhood`, `Suq_al_Shiyoukh` | Nombres propios de noticias de Irak |
| `gai` | 11 | `gai` | `banh`, `khao`, `nuong`, `hoa` | Cocina vietnamita |
| `genai` | 5 | `Genai` | `Breona`, `Shundra`, `Marquisha` | Nombres propios de persona |
| *(referencia)* | — | `AI` | `Enemy_AI`, `mechs`, `Steven_Spielberg_Artificial_Intelligence` | Videojuegos y cine |

Como control, los términos generales sí tienen el significado esperado: `assessment` queda cerca de `evaluation` y `appraisal`, `education` cerca de `educational`, y `chatbot` cerca de `chatbots` y `artificial_intelligence`.

El problema es grave porque `ai` es el término más frecuente del corpus y aparece en casi todos los artículos. Sin corrección, el promedio de cada abstract incorporaría un vector de "gramática italiana" en proporción a la frecuencia de `ai`. Eso desviaría todos los embeddings en la misma dirección, sin relación con el tema, y podría inflar la similitud entre artículos por una causa artificial.

Este comportamiento ilustra dos limitaciones de los embeddings estáticos que no se ven en la cobertura: la **polisemia**, porque una sola forma escrita recibe un único vector, el de su uso más frecuente en el corpus de entrenamiento, y la **desactualización**, porque el modelo es de 2013 y no conoce los sentidos que estas siglas adquirieron después.

### 8.3 Corrección: expansión explícita de siglas

Antes de buscar un token en el modelo, se consulta una tabla de expansiones (`EXPANSIONES` en `embeddings_w2v.py`). Si el token está en la tabla, su vector es el promedio de los vectores de las palabras de su expansión. Cada aparición sigue contando como **un** token dentro del promedio del documento, así que el peso relativo de la sigla no cambia.

| Token | Expansión | Motivo |
|---|---|---|
| `ai` | `artificial_intelligence` | Vector equivocado (italiano) |
| `aied` | `artificial_intelligence` + `education` | Vector equivocado (nombres propios) |
| `genai` | `artificial_intelligence` | Vector equivocado (nombres propios) |
| `gai` | `artificial_intelligence` | Vector equivocado (cocina vietnamita) |
| `aihed` | `artificial_intelligence` + `education` | No existe en el modelo; es la sigla de AI in Higher Education en el art. 12 |
| `chatgpt` | `artificial_intelligence` + `chatbot` | No existe en el modelo (es posterior); aparece 5 veces en el art. 19 |

`artificial_intelligence` es una frase que el modelo de Google News guarda como un solo token. Las palabras de las expansiones pasaron el mismo diagnóstico que las siglas: los vecinos de `artificial_intelligence` son `robots`, `algorithms`, `Marvin_Minsky` y `Hans_Moravec`, y `chatbot` queda cerca de `chatbots` y `artificial_intelligence`.

Dos palabras candidatas no pasaron el diagnóstico. `generative`, que se consideró para `genai`, `gai` y `chatgpt`, pertenece en el modelo a la exploración minera (`hydrothermal`, `gold_copper_porphyry`), el uso más común en noticias de 2013. `higher`, que se consideró para `aihed`, significa "más alto" (`lower`, `greater`, `increased`), y la frase `higher_education` no existe en el modelo, así que `aihed` se expandió igual que `aied`. En consecuencia, el embedding no distingue entre IA generativa e IA en general, ni entre educación superior y educación en general, lo cual es una limitación adicional del modelo estático frente al modelo contextual de IA-3.

La corrección se aplica solo en la búsqueda de vectores de Word2Vec. No modifica el corpus preprocesado, así que los algoritmos clásicos siguen trabajando exactamente sobre los mismos tokens. Para poder medir el efecto de la corrección en el análisis comparativo (CMP-2), el script admite la opción `--sin-expansiones`, que reproduce la versión sin corregir.

## 9. Resultados de la implementación (IA-3)

**Implementación:** `src/ia/embeddings_llm.py` · **Pruebas:** `tests/ia/test_embeddings_llm.py` · **Resultado:** `data/embeddings/mpnet.json` (20 vectores de 768 dimensiones).

La tarea partió de una versión inicial de Camilo Ospina que validó el uso de la librería `sentence-transformers`. Sobre ella se aplicaron las decisiones de la sección 6: se cambió el modelo a `all-mpnet-base-v2`, se vectorizó el campo `abstract` original del corpus, el modelo se carga una sola vez, los resultados se guardan en el formato común del proyecto (reutilizando `guardar_embeddings()` de IA-2) y se agregó la verificación de truncamiento.

### 9.1 Verificación de truncamiento

Se contaron las sub-palabras de cada abstract con el tokenizador del propio modelo, incluyendo los tokens especiales de inicio y fin, que también cuentan para el límite:

| Medida | Valor |
|---|---|
| Límite del modelo (`max_seq_length`) | 384 sub-palabras |
| Rango en el corpus | 166 (art. 2) a 383 (art. 12) |
| Promedio | 266,1 sub-palabras |
| Abstracts truncados | Ninguno |

Todos los abstracts se procesan completos, así que el plan B (`allenai-specter`) no fue necesario. El art. 12 queda a una sola sub-palabra del límite. Si en el futuro cambia la extracción del texto, este artículo es el primero que habría que volver a verificar.

El resultado confirma la decisión de la sección 6: con `all-MiniLM-L6-v2` (límite de 256 sub-palabras), 13 de los 20 abstracts habrían perdido su parte final, que suele contener las conclusiones del artículo.

### 9.2 Diferencias de entrada respecto a los demás algoritmos

Este es el único de los seis algoritmos del Requerimiento 1 que recibe el abstract original (con *stopwords*, puntuación, mayúsculas y siglas sin expandir). Los cuatro algoritmos clásicos y Word2Vec trabajan sobre `abstract_preprocesado`. La diferencia es intencional (sección 6), pero debe tenerse en cuenta en el análisis comparativo (CMP-2): parte de la diferencia entre este modelo y los demás se debe a que ve más información del texto, no solo a que sea un modelo distinto.

Además, a diferencia de Word2Vec, este modelo no necesitó expansión de siglas: recibe `Artificial Intelligence in Education (AIEd)` tal como aparece en el abstract, así que puede relacionar la sigla con su significado por el contexto en que aparece.

## 10. Métricas de similitud sobre embeddings (IA-4)

**Implementación:** `src/ia/metricas.py` (métricas) y `src/comparador.py` (integración con la selección dinámica de artículos) · **Pruebas:** `tests/ia/test_metricas.py` y `tests/test_comparador.py`.

La tarea partió de una versión inicial de Camilo Ospina (`metrics.py` y `comparador.py`) que planteaba la estructura correcta: extender el comparador de CLA-5 con las métricas de embeddings y convertir la distancia en similitud con 1/(1+d). Sobre ella se hicieron tres cambios. Primero, las métricas se reimplementaron sin `numpy.dot` ni `numpy.linalg.norm`, porque el coseno y la distancia euclidiana son los algoritmos que pide el requerimiento. Segundo, los vectores se leen de `data/embeddings/`, donde los dejaron IA-2 e IA-3. Tercero, se integraron los dos modelos de IA.

### 10.1 Métricas implementadas

Para dos vectores a y b de dimensión n, todas calculadas con ciclos y `math.sqrt`:

| Métrica | Fórmula | Rango | Valor para textos idénticos |
|---|---|---|---|
| Similitud coseno | (a · b) / (‖a‖ · ‖b‖) | [−1, 1] | 1 |
| Distancia euclidiana | √(Σ (aᵢ − bᵢ)²) | [0, ∞) | 0 |
| Similitud euclidiana | 1 / (1 + d) | (0, 1] | 1 |

La similitud euclidiana es una transformación de la distancia que permite ponerla al lado de las demás similitudes. Su escala depende de la magnitud de los vectores de cada modelo, así que solo es comparable entre artículos de un mismo modelo.

### 10.2 Comparador integrado

`src/comparador.py` permite elegir dos o más artículos del corpus, por consola o como argumentos (`python src/comparador.py 2 9`), y calcula las matrices de los 6 algoritmos. Para los algoritmos de IA calcula las tres métricas de la sección 10.1. Cuando se comparan exactamente dos artículos, imprime además una tabla resumen. El cálculo está en la función `comparar_articulos()`, separado de la entrada y salida por consola, para que el backend del Sprint 5 pueda reutilizarlo. `src/classic/classics.py` (CLA-5) se conserva como el comparador de solo algoritmos clásicos.

### 10.3 Resultado para el caso de estudio (artículos 2 y 9)

| Algoritmo | Tipo | Similitud | Distancia euclidiana |
|---|---|---|---|
| Levenshtein | Clásico | 0,0901 | — |
| Needleman-Wunsch | Clásico | 0,0901 | — |
| Coseno TF-IDF | Clásico | 0,2553 | — |
| Jaccard | Clásico | 0,1583 | — |
| Word2Vec (coseno) | IA | 0,9318 | 0,3806 |
| Word2Vec (euclidiana 1/(1+d)) | IA | 0,7243 | 0,3806 |
| MPNet (coseno) | IA | 0,8376 | 0,5698 |
| MPNet (euclidiana 1/(1+d)) | IA | 0,6370 | 0,5698 |

Los valores de los algoritmos clásicos coinciden con los del caso de estudio del Sprint 2.

### 10.4 Observaciones para el análisis comparativo (CMP-2)

**Los vectores de MPNet tienen norma 1.** El modelo `all-mpnet-base-v2` incluye una capa final que normaliza los vectores, y la generación de IA-3 lo confirmó: la norma es 1,000000 en los 20 artículos. Con vectores de norma 1 se cumple d² = 2 − 2·cos, así que en este modelo la distancia euclidiana es una función directa del coseno y no aporta información nueva. Para el caso de estudio: √(2 − 2 · 0,8376) = 0,5699, que coincide con la distancia calculada. En Word2Vec los vectores no están normalizados, de modo que ahí las dos métricas sí pueden ordenar los pares de forma distinta.

**Los valores absolutos no son comparables entre algoritmos.** Cada algoritmo tiene su propia escala. En particular, el promedio de los vectores de más de cien palabras tiende a producir cosenos altos entre cualquier par de abstracts de un mismo dominio. Por eso un 0,93 en Word2Vec frente a un 0,26 en TF-IDF no indica que Word2Vec considere los artículos "más parecidos". Para comparar algoritmos hay que ubicar el par 2–9 dentro de la distribución de los demás pares del corpus de cada algoritmo, lo cual corresponde a CMP-2.

## 11. Referencias

- Mikolov, T., Chen, K., Corrado, G., & Dean, J. (2013). *Efficient Estimation of Word Representations in Vector Space*. arXiv:1301.3781.
- Bojanowski, P., Grave, E., Joulin, A., & Mikolov, T. (2017). *Enriching Word Vectors with Subword Information*. Transactions of the ACL, 5, 135–146.
- Reimers, N., & Gurevych, I. (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*. EMNLP 2019.
- Song, K., Tan, X., Qin, T., Lu, J., & Liu, T.-Y. (2020). *MPNet: Masked and Permuted Pre-training for Language Understanding*. NeurIPS 2020.
- Cohan, A., Feldman, S., Beltagy, I., Downey, D., & Weld, D. S. (2020). *SPECTER: Document-level Representation Learning using Citation-informed Transformers*. ACL 2020.
- Documentación de Sentence Transformers: https://sbert.net
