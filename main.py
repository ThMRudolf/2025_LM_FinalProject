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
### @tmr, 03.12.2025
from preproc_data.src.py.kienzle_model import KienzleMillingModel
from preproc_data.src.py.preprocess_data import PreprocessData
from preproc_data.src.py.get_experim_data import GetExperimData
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
# 6. add data of Kienzle model
#---------------------------------------------------------
# Parámetros del modelo Kienzle (ejemplo)

## read in the process parameters from a excel file
## @tmr
tool_type = 'C1030' # insert tool type here C4240 Plan
param_experim_data_file = f'data/parameterize_experiment/Experiment_{tool_type}.xlsx'

params_df = GetExperimData(param_experim_data_file, tool_type)
params_df.set_material_parameters(kc11 = 1800, mc = 0.25)
params_df.set_tool_parameters(rtool = 20, kappa = 45)
df = params_df.get_experiment_param()
results = []
#tool_type = 'C1030'  # insert tool type here C4240
#param_experim_all_files = f'../../../data/parameterize_experiment/Experiment_{tool_type}.xlsx'
record_type = 'all' #'Plan' # 'all'
file_folder = f'data/raw/{tool_type}/{record_type}/' #f'../../../data/raw/{tool_type}/all/'
#C:\Users\thmru\github\2025_LM_FinalProject\data\raw\C1030\all
output_dir = Path("./data/clean")
for idx, row in df.iterrows():
    # 1. Read real measurement file
    fname = row["SinuTraceFile (*.csv)"]
    file_path = file_folder  + row["SinuTraceFile (*.csv)"]
    print(f"Processing measurement {idx}: {file_path}")
    real = pd.read_csv(file_path)
    t = real["time"].values
    iq_real = real["iqAx4"].values

    # 2. Extract parameters
    ap = row["Ap (mm)"]
    fz = row["fz (mm/tooth)"]                     # already in dataframe
    z  = int(row["z"])
    kappa = row["kappa (rad)"]
    omega = row["omega (rad/s)"]
    kc11 = row["kc11"]
    mc = row["mc"]
    rtool = row["rtool (m)"]
    phi_ent = row["phi_ent_rad"]
    phi_exit = row["phi_exit_rad"]

    # 3. Calculate model torque on same time stamps
    kienzle_model = KienzleMillingModel(ap, fz, z, kappa, omega, kc11, mc, rtool, phi_ent, phi_exit)
    phi, Fc, Tc, sin_sums = kienzle_model.evaluate(t)

    # 4. Create synchronized output dataframe
    out = pd.DataFrame({
        "time": t,
        "Tc_model": Tc,
        "Iq_real": iq_real,
        "phi": phi,
        "sin_sums": sin_sums,
        "measurement_id": row["SinuTraceFile (*.csv)"]
    })

    # 5. Save result file per measurement
    # fname = f"../../../data/preprocessed/Mill/measurement_{idx:03d}_training_data.csv"
    output_path = output_dir / fname
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)

    results.append(fname)
    
print(f"\nGuardando los DataFrames preprocesados en {output_dir}/...")
results[:5]   # show first few generated files

#---------------------------------------------------------
# 6. Guardar los DataFrames preprocesados
#---------------------------------------------------------
#output_dir = Path("./data/clean")
#print(f"\nGuardando los DataFrames preprocesados en {output_dir}/...")
#for fname, df in dataframes.items():
#    output_path = output_dir / fname
#    # Creamos el directorio padre si no existe
#    output_path.parent.mkdir(parents=True, exist_ok=True)
#    try:
#        # Guardar como CSV sin índice
#        df.to_csv(output_path, index=False)
#    except Exception as e:
#        print(f" ⚠ Error guardando {output_path}: {e}")
#print("Preprocesamiento completado.")

#Leemos los dataframes limpios
#dataframes_clean = leer_todos_csv(output_dir)

