# Análisis Crítico Comparativo: Algoritmos Clásicos vs. Modelos de IA (CMP-2)

**Requerimiento 1 · Sprint 3 · Responsable: Daniel Narváez**

Este documento compara los resultados de los seis algoritmos de similitud del Requerimiento 1 en cuatro ejes: coherencia semántica, sensibilidad léxica frente a semántica, tiempos de ejecución, y ventajas y desventajas. Parte del caso de estudio (artículos 2 y 9, consolidado en `docs/classic_vs_ai.md`, CMP-1) y lo amplía con evidencia de todo el corpus y con un experimento controlado.

**Evidencia:** `notebooks/analisis_comparativo.py` · **Resultados completos:** `data/resultados/analisis_comparativo.json`

---

## 1. Punto de partida: el caso de estudio

| Algoritmo | Tipo | Entrada | Similitud 2–9 |
|---|---|---|---|
| Levenshtein | Clásico | Tokens preprocesados | 0,0901 |
| Needleman-Wunsch | Clásico | Tokens preprocesados | 0,0901 |
| Coseno TF-IDF | Clásico | Tokens preprocesados | 0,2553 |
| Jaccard | Clásico | Tokens preprocesados | 0,1583 |
| Word2Vec (coseno) | IA | Tokens preprocesados | 0,9318 |
| MPNet (coseno) | IA | Abstract original | 0,8376 |

A primera vista, los modelos de IA parecen considerar los artículos casi idénticos y los clásicos, casi sin relación. **Esa lectura es incorrecta.** Cada algoritmo tiene su propia escala, y un valor absoluto solo tiene sentido comparado con los demás valores del mismo algoritmo. Por eso el análisis se apoya en la distribución de los 190 pares posibles del corpus.

## 2. Coherencia semántica

### 2.1 Posición del caso de estudio en el corpus

Para cada algoritmo se calcularon los 190 pares de artículos y se ubicó el par 2–9 en esa distribución:

| Algoritmo | Mínimo | Máximo | Media | Valor 2–9 | Posición 2–9 | Percentil |
|---|---|---|---|---|---|---|
| Levenshtein | 0,0081 | 0,1176 | 0,0451 | 0,0901 | 4 de 190 | 97,9 % |
| Needleman-Wunsch | 0,0000 | 0,1176 | 0,0458 | 0,0901 | 7 de 190 | 96,3 % |
| Coseno TF-IDF | 0,0240 | 0,3387 | 0,1156 | 0,2823 | 3 de 190 | 98,4 % |
| Jaccard | 0,0375 | 0,1963 | 0,1119 | 0,1583 | 15 de 190 | 92,1 % |
| Word2Vec (coseno) | 0,8084 | 0,9518 | 0,8916 | 0,9318 | 18 de 190 | 90,5 % |
| Word2Vec (euclidiana) | 0,6185 | 0,7602 | 0,6863 | 0,7243 | 28 de 190 | 85,3 % |
| MPNet (coseno) | 0,3456 | 0,8882 | 0,6445 | 0,8376 | 5 de 190 | 97,4 % |

*En esta tabla, TF-IDF usa el IDF calculado con los 20 artículos, por eso el valor del par 2–9 es 0,2823 y no 0,2553. El caso de estudio del Sprint 2 calculó el IDF solo con los dos artículos comparados. Con N = 2, todo término compartido recibe el mismo peso bajo (log(2/3) + 1 ≈ 0,59), mientras que con N = 20 el peso de cada término depende de qué tan común es en todo el corpus. TF-IDF es el único de los seis algoritmos cuyo resultado para un par depende de qué otros documentos se incluyan.*

**Lectura:** con la escala corregida, **los seis algoritmos coinciden en que el par 2–9 es de los más parecidos del corpus**: todos lo ubican por encima del percentil 85. La diferencia entre 0,09 y 0,93 no era un desacuerdo sobre el par, sino una diferencia de escala. Esto también valida la elección del caso de estudio: es un par representativo de artículos relacionados.

**Rango útil de cada escala.** Word2Vec concentra los 190 pares entre 0,81 y 0,95. El par menos parecido del corpus obtiene 0,81, y en el experimento de la sección 3 dos frases sin ninguna relación obtienen 0,26. Su escala está comprimida, así que discrimina poco entre artículos. MPNet usa un rango mucho más amplio (0,35 a 0,89) y asigna −0,04 a frases sin relación, lo que le da más poder de discriminación. Entre los clásicos, TF-IDF tiene el rango más amplio en términos relativos (de 0,02 a 0,34).

### 2.2 ¿Qué pares considera más parecidos cada algoritmo?

| Algoritmo | Los 3 pares más parecidos | Qué tienen en común |
|---|---|---|
| Levenshtein | 2–20, 2–15, 12–20 | Todos son revisiones sistemáticas |
| Needleman-Wunsch | 2–20, 12–20, 2–15 | Todos son revisiones sistemáticas |
| Coseno TF-IDF | 2–6, 6–9, 2–9 | Panoramas generales de IA en educación |
| Jaccard | 2–6, 2–10, 2–18 (los 5 incluyen el art. 2) | El artículo 2, el abstract más corto |
| Word2Vec (coseno) | 9–18, 2–5, 2–18 | Panoramas generales de IA en educación |
| MPNet (coseno) | 12–20, 6–9, 5–9 | Revisiones y panoramas de la investigación en IA educativa |

De aquí salen tres observaciones:

1. **Levenshtein y Needleman-Wunsch detectan sobre todo el género del texto.** Los cuatro artículos de sus pares más parecidos (2, 12, 15 y 20) son revisiones sistemáticas, y los cuatro contienen la secuencia *systematic review*. Una distancia de edición premia las palabras que aparecen **en el mismo orden**, y en un abstract esas secuencias repetidas suelen corresponder al tipo de estudio más que a su tema. Además, sus valores son tan bajos (todos por debajo de 0,12) que la diferencia entre un par y otro depende de muy pocas coincidencias.
2. **Jaccard tiene un sesgo por longitud.** Sus cinco pares más parecidos incluyen el artículo 2, que tiene el abstract más corto del corpus (77 tokens). Como Jaccard divide la intersección entre la unión, un conjunto pequeño produce uniones pequeñas y similitudes altas con casi cualquier otro documento. El resultado refleja la longitud del abstract más que su contenido.
3. **El par 12–20 es un consenso.** Aparece entre los 5 más parecidos para Levenshtein, Needleman-Wunsch, Word2Vec y MPNet (en MPNet es el primero). Los dos artículos son revisiones de la investigación en inteligencia artificial educativa ("*A meta systematic review of artificial intelligence…*" y "*Systematic review of research on artificial intelligence…*"). Cuando algoritmos tan distintos coinciden, el parecido es robusto.

### 2.3 Concordancia entre algoritmos

La correlación de Spearman mide si dos algoritmos **ordenan** los 190 pares de la misma forma, sin importar la escala (1 = mismo orden, 0 = sin relación):

| | Lev | NW | TF-IDF | Jaccard | W2V cos | W2V euc | MPNet |
|---|---|---|---|---|---|---|---|
| **Levenshtein** | 1,000 | 0,978 | 0,491 | 0,344 | 0,257 | 0,228 | 0,266 |
| **Needleman-Wunsch** | 0,978 | 1,000 | 0,488 | 0,345 | 0,259 | 0,231 | 0,264 |
| **Coseno TF-IDF** | 0,491 | 0,488 | 1,000 | 0,601 | 0,569 | 0,533 | 0,592 |
| **Jaccard** | 0,344 | 0,345 | 0,601 | 1,000 | 0,449 | 0,392 | 0,419 |
| **Word2Vec (coseno)** | 0,257 | 0,259 | 0,569 | 0,449 | 1,000 | 0,968 | 0,562 |
| **Word2Vec (euclidiana)** | 0,228 | 0,231 | 0,533 | 0,392 | 0,968 | 1,000 | 0,493 |
| **MPNet (coseno)** | 0,266 | 0,264 | 0,592 | 0,419 | 0,562 | 0,493 | 1,000 |

- **Levenshtein y Needleman-Wunsch son casi el mismo algoritmo en este corpus (0,978).** La sección 2.4 lo demuestra.
- **Los algoritmos de edición casi no se relacionan con los de IA (≈ 0,26).** Miden cosas distintas: orden de las palabras frente a significado.
- **TF-IDF es el clásico más cercano a la IA** (0,57 con Word2Vec y 0,59 con MPNet). Es el que mejor aproxima el ordenamiento semántico sin usar modelos preentrenados.
- **Los dos modelos de IA coinciden solo moderadamente entre sí (0,562).** Representar el significado con un promedio de palabras sueltas no produce el mismo resultado que hacerlo con un modelo que lee el texto en contexto.
- **En Word2Vec, coseno y euclidiana casi coinciden (0,968), pero no del todo**, porque sus vectores no tienen norma 1. En MPNet la distancia euclidiana no se incluyó: con norma 1 es una función exacta del coseno (ver `docs/modelos_ia.md`, sección 10.4).

### 2.4 Por qué Levenshtein y Needleman-Wunsch dan el mismo valor en el caso de estudio

Sean *n* y *m* las longitudes de las dos secuencias de tokens (*n ≤ m*). Toda alineación está formada por columnas de tres tipos: *k* coincidencias, *s* sustituciones y huecos. Como la secuencia corta necesita al menos *m − n* huecos para igualar la larga, se puede escribir el total de huecos como *(m − n) + 2h*, donde *h* es el número de huecos "extra" en cada secuencia. La longitud de la alineación es *L = m + h*.

- **Levenshtein** minimiza el costo *s* + huecos = *L − k*. Su similitud es 1 − *d* / *m*.
- **Needleman-Wunsch** (coincidencia +1, sustitución −1, hueco −2) maximiza el puntaje *k − s − 2·huecos*, que simplificando queda como *2k − 3h* más una constante. Su similitud es *k / L*.

Si la alineación óptima no usa huecos extra (*h = 0*), entonces *L = m* y las dos similitudes se reducen a la misma expresión:

```
Levenshtein:       1 − d/m = 1 − (m − k)/m = k/m
Needleman-Wunsch:  k/L     = k/m
```

En el caso de estudio, *m* = 111 tokens (artículo 9) y la alineación óptima tiene *k* = 10 coincidencias sin huecos extra, por eso ambos dan **10/111 = 0,0901**.

Las dos similitudes divergen cuando conviene agregar huecos extra para lograr más coincidencias. Levenshtein acepta un hueco extra por cada coincidencia adicional (su objetivo pondera *k* y *h* por igual), mientras que Needleman-Wunsch, con estas penalizaciones, exige más (*2k − 3h*). En textos poco parecidos rara vez conviene, y por eso la correlación entre ambos es 0,978. El experimento de "orden invertido" (sección 3) muestra un caso donde sí divergen.

## 3. Sensibilidad léxica frente a semántica: experimento controlado

Los abstracts reales mezclan muchos efectos a la vez. Para aislarlos se diseñaron cuatro pares de frases, cada uno pensado para separar un comportamiento. Las frases pasan por el mismo preprocesamiento que el corpus: los algoritmos clásicos y Word2Vec reciben los tokens, y MPNet recibe el texto original.

| Caso | Frase A | Frase B |
|---|---|---|
| Sinónimos | *Students use chatbots to improve their writing skills.* | *Learners employ conversational agents to enhance their essay composition.* |
| Orden invertido | *The teacher evaluates the artificial intelligence system.* | *The artificial intelligence system evaluates the teacher.* |
| Negación | *Generative AI improves student learning outcomes.* | *Generative AI does not improve student learning outcomes.* |
| Temas distintos | *Generative AI tools support assessment in higher education.* | *Soil erosion reduces crop yields in tropical regions.* |

| Caso | Lev | NW | TF-IDF | Jaccard | Word2Vec | MPNet | Comportamiento ideal |
|---|---|---|---|---|---|---|---|
| Sinónimos | 0,000 | 0,000 | 0,000 | 0,000 | **0,693** | **0,745** | Alta |
| Orden invertido | 0,200 | 0,000 | 1,000 | 1,000 | 1,000 | 0,924 | Media: mismas palabras, sentido distinto |
| Negación | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 0,927 | Baja: sentido opuesto |
| Temas distintos | 0,000 | 0,000 | 0,000 | 0,000 | 0,263 | **−0,044** | Cercana a 0 |

**Sinónimos.** Las dos frases dicen lo mismo sin compartir una sola palabra. Los cuatro clásicos dan 0, porque solo reconocen palabras idénticas. Los dos modelos de IA reconocen la equivalencia (0,69 y 0,75). Es la diferencia central entre sensibilidad **léxica** y **semántica**.

**Orden invertido.** Las frases usan exactamente las mismas palabras, pero cambia quién evalúa a quién.
- TF-IDF, Jaccard y Word2Vec dan 1,000: los tres representan el texto como una **bolsa de palabras** (o un promedio de ellas) y no ven el orden.
- MPNet baja a 0,924: percibe el cambio de orden, aunque de forma leve.
- Levenshtein (0,200) y Needleman-Wunsch (0,000) reaccionan de forma desproporcionada, porque para ellos el orden lo es todo. El caso además muestra cómo divergen (sección 2.4). Levenshtein encuentra una alineación de costo 4 que empareja las tres palabras comunes (*artificial intelligence system*). En Needleman-Wunsch, esa alineación y la de "todo sustituciones" empatan con puntaje −5, y al reconstruir el camino se prefiere la diagonal, así que reporta 0 coincidencias aunque las dos frases tengan las mismas palabras.

**Negación.** Es el hallazgo más importante del experimento. Las dos frases afirman cosas opuestas, pero tras el preprocesamiento quedan **idénticas**: `['generative', 'ai', 'improve', 'student', 'learn', 'outcome']`. *does* y *not* están en la lista de *stopwords* de NLTK y se eliminan. En consecuencia, los cuatro clásicos y Word2Vec dan 1,000. **La pérdida no la causa el algoritmo de similitud, sino el preprocesamiento**, y afecta a todos los que trabajan sobre tokens. MPNet recibe el texto original y baja a 0,927, lo que muestra que detecta la diferencia, aunque débilmente: un valor tan alto para frases opuestas también es una limitación de los embeddings de oraciones, que tienden a reflejar el tema más que la polaridad.

**Temas distintos.** Es el caso de control. Los clásicos dan 0, porque no hay palabras en común, y MPNet da −0,044, prácticamente sin relación. Word2Vec da 0,263: al promediar vectores de palabras, dos textos cualesquiera conservan cierta similitud de fondo. Esto explica por qué en el corpus su valor mínimo es 0,81.

## 4. Tiempos de ejecución

Medidos en el equipo de desarrollo (CPU, sin GPU), sobre los mismos datos.

### 4.1 Cálculo de la similitud

| Algoritmo | Matriz 20×20 (190 pares) | Un par (2–9) | Complejidad por par |
|---|---|---|---|
| Levenshtein | 1,536 s | 4,952 ms | O(n·m) |
| Needleman-Wunsch | 2,014 s | 6,924 ms | O(n·m) + reconstrucción O(n + m) |
| Coseno TF-IDF | 0,143 s | 0,443 ms | O(N·V) para vectorizar + O(V) por par |
| Jaccard | 0,007 s | 0,121 ms | O(n + m) |
| Word2Vec (coseno) | 0,012 s | 0,056 ms | O(d), d = 300 |
| MPNet (coseno) | 0,032 s | 0,142 ms | O(d), d = 768 |

*n* y *m* son las longitudes en tokens de los dos abstracts (77 a 159), *N* el número de documentos, *V* el tamaño del vocabulario y *d* la dimensión del embedding.

Los algoritmos de programación dinámica son los más lentos por amplio margen: entre 35 y 130 veces más que el coseno sobre embeddings, según el modelo y si se mide un par o la matriz completa. Su costo crece con el **producto** de las longitudes (un par de 111 × 77 tokens llena una matriz de unas 8.700 celdas). Needleman-Wunsch tarda un poco más que Levenshtein porque, además de llenar la matriz, reconstruye la alineación para contar las coincidencias. Una vez que los vectores existen, la similitud entre embeddings es de las operaciones más rápidas, porque su costo solo depende de la dimensión fija *d*.

### 4.2 Generación de embeddings (costo previo de los modelos de IA)

| Paso | Tiempo |
|---|---|
| Word2Vec: cargar el modelo (1,6 GB) | 72,98 s |
| Word2Vec: vectorizar los 20 abstracts | 0,10 s |
| MPNet: cargar la librería y el modelo | 177,74 s |
| MPNet: vectorizar los 20 abstracts | 16,75 s |

El costo de los modelos de IA está concentrado **antes** del cálculo de similitud. Word2Vec tarda en cargar un archivo de 3 millones de vectores, pero luego vectorizar es casi instantáneo (es una búsqueda en una tabla). En MPNet, los 178 s de carga incluyen importar PyTorch y verificar el modelo en Hugging Face; leer solo los pesos tomó pocos segundos. Su costo real está en vectorizar: unos 0,8 s por abstract, porque un Transformer compara cada sub-palabra con todas las demás en cada capa, con un costo O(L²) en la longitud L del texto.

**Decisión de diseño que se deriva:** como el corpus es estático, los embeddings se calculan una sola vez y se guardan en `data/embeddings/` (ver `docs/modelos_ia.md`, sección 7). Así, en la aplicación desplegada el costo de los modelos de IA en cada consulta se reduce al del coseno, el más bajo de la tabla 4.1. Los algoritmos clásicos, en cambio, se calculan en cada consulta porque no necesitan modelos.

## 5. Ventajas y desventajas

| Algoritmo | Ventajas | Desventajas |
|---|---|---|
| **Levenshtein** | Totalmente interpretable: la matriz y la secuencia de operaciones se pueden mostrar paso a paso. Sensible al orden. | Mide estructura y no tema: sus pares más parecidos comparten fórmulas metodológicas. Es el más lento, O(n·m). Sobrerreacciona a cambios de orden. Ignora sinónimos. |
| **Needleman-Wunsch** | Produce una alineación explícita que muestra qué tokens coinciden. Penalizaciones configurables. | Casi equivalente a Levenshtein en este corpus (Spearman 0,978). Los empates en la reconstrucción pueden ocultar coincidencias (orden invertido: 0,000). El más lento. |
| **Coseno TF-IDF** | El clásico más cercano a la IA (Spearman ≈ 0,58). Pondera los términos por su rareza, así que los términos comunes pesan poco. Rápido e interpretable. | Su valor depende de qué documentos forman el corpus (0,2553 frente a 0,2823 para el mismo par). Ignora el orden y los sinónimos. |
| **Jaccard** | El más simple y el más rápido de los clásicos. Fácil de explicar. | Sesgado por la longitud: favorece a los abstracts cortos. No pondera términos: una palabra común cuenta igual que una técnica. |
| **Word2Vec** | Reconoce sinónimos y palabras relacionadas (0,693 en el experimento). Vectorización casi instantánea una vez cargado. El promedio es explicable paso a paso. | Escala comprimida (0,81 a 0,95 en el corpus): discrimina poco. Ignora el orden. Modelo de 2013: siglas del dominio con significados equivocados (sección 8 de `modelos_ia.md`). Carga de 1,6 GB. |
| **MPNet** | El de mayor poder de discriminación (rango de 0,35 a 0,89; −0,04 para temas distintos). Reconoce sinónimos, percibe el orden y es el único que nota la negación. Entiende las siglas por su contexto. Pares más parecidos temáticamente coherentes. | Caja negra: no se puede mostrar cómo se obtiene cada componente del vector. El más costoso de vectorizar, O(L²). Requiere PyTorch. Detecta la negación solo débilmente (0,927). Limitado a 384 sub-palabras. |

## 6. Conclusiones

1. **Los valores absolutos de similitud no son comparables entre algoritmos.** Comparados por su posición en la distribución del corpus, los seis coinciden en que el par 2–9 está entre los más parecidos (percentil 85 o superior).
2. **Clásicos e IA responden a preguntas distintas.** Los clásicos miden coincidencia **léxica** (qué palabras se comparten y, en los de edición, en qué orden). Los modelos de IA miden cercanía **semántica**. El experimento lo muestra de forma directa: con sinónimos, los clásicos dan 0 y la IA alrededor de 0,7.
3. **Para el objetivo bibliométrico, agrupar artículos por tema, MPNet es el enfoque más adecuado.** Es el que mejor discrimina, sus pares más parecidos son temáticamente coherentes y es el único sensible al orden y a la negación. Su costo se resuelve precalculando los embeddings.
4. **Entre los clásicos, TF-IDF es el más adecuado** para medir tema: es el que más se acerca al ordenamiento de los modelos de IA y es rápido. Levenshtein y Needleman-Wunsch son poco apropiados para comparar abstracts por tema, porque detectan estructura y no contenido. Jaccard está sesgado por la longitud de los textos.
5. **El preprocesamiento también es una decisión de diseño con consecuencias.** Eliminar *stopwords* hace que frases opuestas sean indistinguibles para todos los algoritmos que trabajan sobre tokens. Este efecto no se debe a los algoritmos de similitud, y es una de las razones por las que MPNet recibe el texto original.
6. **La IA apoya, pero no reemplaza, el análisis algorítmico.** Los modelos de IA solo se usaron para obtener representaciones vectoriales. La similitud se calculó con implementaciones propias, y fue el análisis de esas implementaciones lo que permitió detectar los problemas de escala, las siglas mal interpretadas por Word2Vec y el efecto de la negación.

Estas conclusiones son un insumo para el Sprint 4: el agrupamiento jerárquico necesita una matriz de distancias (CLU-1), y este análisis indica que TF-IDF, entre los clásicos, y MPNet, entre los modelos de IA, son las representaciones que mejor reflejan la cercanía temática entre abstracts.

## 7. Limitaciones del análisis

- El corpus tiene 20 artículos (190 pares) de un mismo dominio, así que las distribuciones y correlaciones describen este corpus y no se pueden generalizar sin más.
- El experimento controlado usa cuatro pares de frases cortas, diseñados para ilustrar comportamientos, no para medirlos estadísticamente.
- Los tiempos dependen del equipo y varían entre ejecuciones, especialmente los de carga de modelos. Deben leerse como órdenes de magnitud.
- MPNet recibe más información que los demás algoritmos (el texto original, sin preprocesar). Parte de su ventaja proviene de esa diferencia de entrada, que es intencional (ver `docs/modelos_ia.md`, sección 9.2).
