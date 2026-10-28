# CAS-4 Selección del caso de estudio del R3

## 1. Patrón Elegido
* **Patrón:** `education`
* **Longitud ($m$):** 9 caracteres

## 2. Párrafo del Abstract Seleccionado (Artículo 17)
Se selecciona el **Artículo 17** debido a que es el documento con mayor cantidad de apariciones del patrón en todo el conjunto de datos de prueba.

A continuación se presenta un fragmento representativo del abstract original donde ocurren múltiples de estas coincidencias (las posiciones exactas registradas en el índice global son: 86, 111, 367, 414, 485, 516, 746, 827, 1177, 1218, 1278, 1309, 1379, 1477, 1508):

> "technology, has been widely used in STEM education to promote the educational assessment.  Although AI-driven edu- cational assessment has the potential to.  examine the field of AI-driven educational assessment. Furthermore, the educational and technological effects of applying AI-driven educational assessment in STEM education. practice and research of AI-driven educational assessment in STEM education."


## 3. Justificación de la Elección
La elección del **Artículo 17** y el patrón **`education`** como caso de estudio se fundamenta en los siguientes criterios técnicos observados en las pruebas de rendimiento:

* **Máxima densidad de ocurrencias:** El Artículo 17 contiene **15 ocurrencias** del patrón. Es el volumen más alto registrado en un solo abstract dentro de los 20 analizados (el total global es de 78).
* **Estrés de verificación:** Al tener tantas ocurrencias válidas, algoritmos como *Rabin-Karp* se ven forzados a realizar múltiples verificaciones explícitas de caracteres (702 comparaciones totales), lo que permite evaluar el impacto del cálculo de hashes sin el ruido de colisiones falsas (0 colisiones registradas).
* **Evaluación de saltos en Boyer-Moore:** Con una longitud de patrón $m = 9$, el algoritmo *Boyer-Moore* ejecutó **370 comparaciones** en este artículo específico. Esto permite contrastar eficientemente la efectividad de sus reglas de salto (*Bad Character* y *Good Suffix*) frente al recorrido lineal de *KMP* (el cual promedió 1.10 comparaciones por carácter a nivel global).
* **Validación de consistencia:** Este caso garantiza que las optimizaciones de saltos y el preprocesamiento de tablas de los tres algoritmos mantengan una precisión del 100% bajo un escenario de alta frecuencia de aciertos.
