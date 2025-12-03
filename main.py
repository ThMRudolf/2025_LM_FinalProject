import pandas as pd
import os
import random

from pathlib import Path

from preproc_data.leer_y_guardar import (
    leer_todos_csv,
    comprobar_columnas_csv,
    cargar_experimentos)

from preproc_data.limpiar_base import (
    renombrar_cols,
    eliminar_columnas,
    insertar_parametros)

from preproc_data.tratar_nulos import (
        imprimir_estadisticas_nulos,
        revisar_nulos_interpolar)

from eda.analisis_datos import( 
     analizar_duracion_cortes,
     analizar_torque, 
     graficas)
# ---------------------------------------------------------
# Localizar todos los archivos CSV dentro de carpeta data
# ---------------------------------------------------------
data_path = Path("./data/raw")
dataframes = leer_todos_csv(data_path)
print(f"Se encontraron {len(dataframes)} archivos CSV.")

# ---------------------------------------------------------
# Leer cada archivo solo para extraer los nombres de columnas
# ---------------------------------------------------------
comprobar_columnas_csv(dataframes)

# ---------------------------------------------------------
# Renombrar columnas para estandarizar nombres
# ---------------------------------------------------------
dataframes = renombrar_cols(dataframes)

# ---------------------------------------------------------
# Eliminar columnas no necesarias
# ---------------------------------------------------------
dataframes = eliminar_columnas(dataframes)
comprobar_columnas_csv(dataframes)
# print("\nNombres de columnas comunes:")
# for col in dataframes[next(iter(dataframes))].columns:
#         print(f" - {col}")

# ---------------------------------------------------------
# Revisar valores nulos e interpolar
# ---------------------------------------------------------
imprimir_estadisticas_nulos(dataframes)
dataframes = revisar_nulos_interpolar(dataframes)

#---------------------------------------------------------
# Insertar Parametros de Preprocesamiento
#---------------------------------------------------------
parametros = cargar_experimentos("./data")
dataframes = insertar_parametros(dataframes, parametros)

# Mostrar las primeras filas de un DataFrame aleatorio como ejemplo
example_fname = random.choice(list(dataframes.keys()))
# print(f"\nPrimeras filas del DataFrame de ejemplo ({example_fname}):")
# print(dataframes[example_fname].head(5))

#---------------------------------------------------------
# Guardar los DataFrames preprocesados
#---------------------------------------------------------
# output_dir = Path("./data/clean")
# print(f"\nGuardando los DataFrames preprocesados en {output_dir}/...")
# for fname, df in dataframes.items():
#     # Creamos el directorio padre si no existe
#     output_dir.mkdir(parents=True, exist_ok=True)
#     try:
#         # Guardar como CSV sin diferenciación de carpetas
#         output_path = output_dir / fname.name
#         df.to_csv(output_path, index=False)
#     except Exception as e:
#         print(f" ⚠ Error guardando {output_path}: {e}")
# print("Preprocesamiento completado.")

# #Leemos los dataframes limpios
# dataframes_clean = leer_todos_csv(output_dir)

# ---------------------------------------------------------
# Análisis de los datos preprocesados
# ---------------------------------------------------------
# results_time = analizar_duracion_cortes(dataframes.values())
# print("Duración de los cortes:")
# #Imprimimos en forma de tabla
# for key, value in results_time.items():
#     print(f" - {key}: {value:.2f} s")

# torque_global = analizar_torque(dataframes.values())
# print("\nEstadísticas globales de torque:")
# for key, value in torque_global.items():
#     print(f" - {key}: {value:.2f}")

#Gráficas
#graficas(dataframes.values())


# ---------------------------------------------------------
# Reducción de los tiempos en los datos (solo quedarse con los primeros 18 seg
# ---------------------------------------------------------
dataframes_reducidos = {}
for fname, df in dataframes.items():
    df_reducido = df[df['time'] <= 18].copy()
    dataframes_reducidos[fname] = df_reducido
results_time_reduc = analizar_duracion_cortes(dataframes_reducidos.values())
print("Duración de los cortes con tiempos reducidos:")
#Imprimimos en forma de tabla
for key, value in results_time_reduc.items():
    print(f" - {key}: {value:.2f} s")

torque_global_red = analizar_torque(dataframes_reducidos.values())
print("\nEstadísticas globales de torque con tiempos reducidos:")
for key, value in torque_global_red.items():
    print(f" - {key}: {value:.2f}")

graficas(dataframes_reducidos.values())

