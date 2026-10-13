# EVA-2: Análisis y Conclusión del Mejor Algoritmo de Clustering

## 1. Introducción y Objetivo
El propósito de este análisis es evaluar de forma comparativa los agrupamientos jerárquicos aglomerativos obtenidos mediante los enfoques de **Single Linkage**, **Complete Linkage** y **Average Linkage**. El algoritmo se aplicó sobre un corpus de \(n = 20\) artículos, utilizando como métrica de disimilitud `1 - similitud coseno TF-IDF` (donde distancias cercanas a 0 implican alta similitud semántica y cercanas a 1, total disimilitud).

---

## 2. Resultados del Historial de Fusiones

### A. Single Linkage (Mínima Distancia)
Muestra un comportamiento patológico de **encadenamiento (*chaining*)**. A partir de la fila 8, el algoritmo deja de buscar relaciones grupales internas y se limita a absorber elementos individuales uno por uno al clúster gigante unificado. Esto se evidencia al ver cómo el tamaño del grupo incrementa estrictamente de a un elemento por fila (+1) desde la fila 9 hasta el final:
* Fila 9: `tamano = 11`
* Fila 10: `tamano = 12`
* ...
* Fila 18 (unión final): Fusiona el elemento `3` con el grupo acumulado de tamaño `19` a una distancia de `0.9041`.

### B. Complete Linkage (Máxima Distancia)
Evita el encadenamiento forzando uniones de grupos compactos, pero sufre de saltos bruscos en las distancias debido a su sensibilidad a elementos atípicos (*outliers*). Las fusiones finales ocurren a distancias extremadamente altas y muy cercanas entre sí (`0.9733` y `0.9760` en las últimas dos filas), lo que indica que se están forzando uniones entre clústeres que semánticamente tienen muy poco o nada en común.

### C. Average Linkage (Distancia Promedio)
Consigue el comportamiento más equilibrado y balanceado. Permite que clústeres pequeños se consoliden de forma independiente antes de unirse al grupo mayor (por ejemplo, en la fila 13 une un grupo de tamaño 9 con otro grupo para formar un sub-bloque de tamaño 16). La progresión de las distancias es suave y escalonada, cerrando la última fusión a `0.9378`, un umbral más bajo y representativo que el criterio estricto de Complete Linkage.

---

## 3. Análisis Comparativo de las Estructuras (Dendrogramas)

| Criterio de Evaluación | Single Linkage | Complete Linkage | Average Linkage |
| :--- | :---: | :---: | :---: |
| **Distancia Mínima de Unión** | 0.6613 (Fila 0) | 0.6613 (Fila 0) | 0.6613 (Fila 0) |
| **Distancia Máxima (Raíz)** | 0.9041 (Fila 18) | 0.9760 (Fila 18) | 0.9378 (Fila 18) |
| **Estructura del Árbol** | Altamente asimétrica (Línea continua) | Compacta pero estirada al final | Jerárquica y balanceada por bloques |
| **Presencia de Chaining** | **Sí (Crítico)** | No | No |

---

## 4. Conclusión: El Mejor Algoritmo

Con base en la inspección de las matrices de enlace y las dinámicas de fusión, se concluye que **Average Linkage produce los agrupamientos más coherentes**.

### Sustentación Técnica:
1. **Representatividad Semántica:** Al calcular el promedio de todas las distancias par a par entre los miembros de dos clústeres, mitiga el sesgo "optimista" de Single Linkage (que une grupos por dos elementos cercanos aunque el resto esté lejos) y el sesgo "pesimista" de Complete Linkage (que separa grupos por culpa de un solo par lejano).
2. **Estructura Jerárquica Real:** Es el único algoritmo que refleja agrupaciones intermedias sanas y balanceadas en el corpus sin caer en el efecto de fila india que inutiliza el propósito práctico de subdividir temáticas en un árbol de decisión.
