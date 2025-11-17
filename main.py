import pandas as pd
import os
import random

from pathlib import Path

from preproc_data.leer_y_guardar import (
    leer_todos_csv,
    comprobar_columnas_csv)

from preproc_data.limpiar_base import (
    renombrar_cols,
    eliminar_columnas)

from preproc_data.tratar_nulos import (
        imprimir_estadisticas_nulos,
        revisar_nulos_interpolar)
# ---------------------------------------------------------
# 1. Localizar todos los archivos CSV dentro de carpeta data
# ---------------------------------------------------------
data_path = Path("./data/raw")
dataframes = leer_todos_csv(data_path)
# #Buscamos todos los archivos CSV en todas las subcarpetas de data
# dataframes = list(data_path.rglob("*.csv")) 
print(f"Se encontraron {len(dataframes)} archivos CSV.")
# ---------------------------------------------------------
# 2. Leer cada archivo solo para extraer los nombres de columnas
# ---------------------------------------------------------
comprobar_columnas_csv(dataframes)

# ---------------------------------------------------------
# 3. Renombrar columnas para estandarizar nombres
# ---------------------------------------------------------
dataframes = renombrar_cols(dataframes)

# ---------------------------------------------------------
# 4. Eliminar columnas no necesarias
# ---------------------------------------------------------
dataframes = eliminar_columnas(dataframes)
comprobar_columnas_csv(dataframes)
print("\nNombres de columnas comunes:")
for col in dataframes[next(iter(dataframes))].columns:
        print(f" - {col}")

# Mostrar las primeras filas de un DataFrame aleatorio como ejemplo
example_fname = random.choice(list(dataframes.keys()))
print(f"\nPrimeras filas del DataFrame de ejemplo ({example_fname}):")
print(dataframes[example_fname].head(5))

# ---------------------------------------------------------
# 5. Revisar valores nulos e interpolar
# ---------------------------------------------------------
imprimir_estadisticas_nulos(dataframes)
dataframes = revisar_nulos_interpolar(dataframes)

#---------------------------------------------------------
# 6. Guardar los DataFrames preprocesados
#---------------------------------------------------------
output_dir = Path("./data/clean")
print(f"\nGuardando los DataFrames preprocesados en {output_dir}/...")
for fname, df in dataframes.items():
    output_path = output_dir / fname
    # Creamos el directorio padre si no existe
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        # Guardar como CSV sin índice
        df.to_csv(output_path, index=False)
    except Exception as e:
        print(f" ⚠ Error guardando {output_path}: {e}")
print("Preprocesamiento completado.")

#Leemos los dataframes limpios
dataframes_clean = leer_todos_csv(output_dir)

