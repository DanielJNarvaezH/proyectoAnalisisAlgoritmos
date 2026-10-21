import time
import pandas as pd
import matplotlib.pyplot as plt

# 1. Importar los algoritmos y los datos
# Asegúrate de que frecuencias.py exponga la lista del corpus completo (ej. lista_frecuencias)
from frecuencias import obtener_lista_frecuencias
from bucket_sort import ordenar_por_frecuencia as bucket_por_frecuencia
from counting_sort import ordenar_por_frecuencia as counting_por_frecuencia
from radix_sort import ordenar_por_frecuencia_radix

# Configuración del experimento
REPETICIONES = 5  # Número de repeticiones para obtener el promedio
algoritmos = {
    "Bucket Sort": bucket_por_frecuencia,
    "Counting Sort": counting_por_frecuencia,
    "Radix Sort": ordenar_por_frecuencia_radix
}

resultados_tiempos = {}
top_15_por_algoritmo = {}

print("Iniciando medición empírica...")

# 2. Bucle de medición de tiempos
for nombre, algoritmo in algoritmos.items():
    tiempos = []

    for i in range(REPETICIONES):
        # Hacemos una copia limpia de los datos en cada iteración
        datos_copia = obtener_lista_frecuencias().copy()

        # Medición en alta resolución
        inicio = time.perf_counter()
        # Nota: Ajusta los parámetros según cómo reciba los datos tu función de ordenamiento
        lista_ordenada = algoritmo(datos_copia)
        fin = time.perf_counter()

        # Convertir a milisegundos
        tiempo_ms = (fin - inicio) * 1000
        tiempos.append(tiempo_ms)

    # Calcular el promedio (en milisegundos)
    promedio_ms = sum(tiempos) / REPETICIONES
    resultados_tiempos[nombre] = promedio_ms

    # Suponiendo ordenamiento descendente (mayor a menor frecuencia), extraemos los primeros 15
    # Si tus algoritmos ordenan de menor a mayor, usa: lista_ordenada[-15:][::-1]
    top_15_por_algoritmo[nombre] = lista_ordenada[:15]

    print(f"⏱️ {nombre}: {promedio_ms:.4f} ms (Promedio de {REPETICIONES} ejecuciones)")

print("\n--- RESULTADOS ---")

# 3. Mostrar la tabla de tiempos
df_tiempos = pd.DataFrame(list(resultados_tiempos.items()), columns=["Algoritmo", "Tiempo Promedio (ms)"])
print("\nTabla de Tiempos:")
print(df_tiempos.to_string(index=False))

# 4. Mostrar los Top 15 términos obtenidos por cada algoritmo
print("\nTop 15 Términos por Algoritmo:")
for nombre, top in top_15_por_algoritmo.items():
    print(f"\n📌 {nombre}:")
    for idx, item in enumerate(top, 1):
        # Asumiendo que el item es una tupla o lista tipo (término, frecuencia)
        print(f"  {idx}. {item[0]} -> {item[1]} ocurrencias")

# 5. Generar el Gráfico de Barras solicitado
plt.figure(figsize=(8, 5))
plt.bar(df_tiempos["Algoritmo"], df_tiempos["Tiempo Promedio (ms)"], color=['skyblue', 'lightgreen', 'salmon'])
plt.ylabel('Tiempo Promedio (ms)')
plt.title('Comparación Empírica de Tiempos de Ejecución')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Guardar el gráfico en la carpeta del proyecto
plt.savefig('docs/grafico_tiempos_ord5.png')
print("\n📊 Gráfico guardado con éxito como 'grafico_tiempos_ord5.png'")
plt.show()
