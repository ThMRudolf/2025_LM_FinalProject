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
print("\nNombres de columnas comunes:")
for col in dataframes[next(iter(dataframes))].columns:
        print(f" - {col}")

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
print(f"\nPrimeras filas del DataFrame de ejemplo ({example_fname}):")
print(dataframes[example_fname].head(5))

#---------------------------------------------------------
# Guardar los DataFrames preprocesados
#---------------------------------------------------------
output_dir = Path("./data/clean")
print(f"\nGuardando los DataFrames preprocesados en {output_dir}/...")
for fname, df in dataframes.items():
    # Creamos el directorio padre si no existe
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        # Guardar como CSV sin diferenciación de carpetas
        output_path = output_dir / fname.name
        df.to_csv(output_path, index=False)
    except Exception as e:
        print(f" ⚠ Error guardando {output_path}: {e}")
print("Preprocesamiento completado.")

# #Leemos los dataframes limpios
# dataframes_clean = leer_todos_csv(output_dir)

