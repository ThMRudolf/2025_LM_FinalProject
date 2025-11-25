import pandas as pd
from pathlib import Path

# ---------------------------------------------------------
# Renombrar columnas
# ---------------------------------------------------------
def renombrar_cols(dataframes):
    # 1.- Añadir columna 'source_file' con 'nombre_archivo.csv' a cada DataFrame
    for fname, df in dataframes.items():
        # Añadimos la columna source file (nombre del archivo) al DataFrame
        df['source_file'] = fname.name
        #Añadimos la columna path (carpeta) al nombre del DataFrame
        df['path'] = str(fname.parent)
    #2.- Renombrar columnas para estandarizarlas
    rename_cols = {
        '+/Nck/!SD/nckServoDataActCurr32 [u1; 1]': 'torque_axis_x', 
        '+/Nck/!SD/nckServoDataActCurr32 [u1; 2]': 'torque_axis_y',
        '+/Nck/!SD/nckServoDataActCurr32 [u1; 3]': 'torque_axis_z',
        '+/Nck/!SD/nckServoDataActCurr32 [u1; 4]': 'torque_spindle',
        '+/Nck/!SD/nckServoDataActPos1stEnc32 [u1; 1]': 'pos_axis_x',
        '+/Nck/!SD/nckServoDataActPos1stEnc32 [u1; 2]': 'pos_axis_y',
        '+/Nck/!SD/nckServoDataActPos1stEnc32 [u1; 3]': 'pos_axis_z',
        '+/Nck/!SD/nckServoDataActVelMot32 [u1; 4]': 'velocity_spindle',
        '+/Channel/!RP/rpa [u1; 15]': 'channel'}
    dataframes_renamed = {}
    for fname, df in dataframes.items():
        df_renamed = df.rename(columns=rename_cols)
        dataframes_renamed[fname] = df_renamed
    print("✔ Se han renombrado las columnas según el mapeo definido.")
    return dataframes_renamed

#---------------------------------------------------------
# Eliminar columnas no necesarias
#---------------------------------------------------------
def eliminar_columnas(dataframes):
    cols_to_remove = [
        'torque_axis_x', 'torque_axis_y', 'torque_axis_z',
        'pos_axis_x', 'pos_axis_y', 'pos_axis_z','channel'
    ]
    dataframes_cleaned = {}
    for fname, df in dataframes.items():
        df_cleaned = df.drop(columns=[col for col in cols_to_remove if col in df.columns])
        dataframes_cleaned[fname] = df_cleaned
    print("✔ Se han eliminado las columnas no necesarias de todos los DataFrames.")
    return dataframes_cleaned

#---------------------------------------------------------
# Insertar Parametros de Preprocesamiento
#---------------------------------------------------------
def insertar_parametros(dataframes, experiments_df):
    """
    Añade columnas Ae, Ap, f y N a cada DataFrame de los traces,
    basándose en el archivo SinuTraceFile indicado en el Excel.
    
    Modifica 'dataframes' en sitio.
    """
    # Normalizar nombre de archivo → facilitar matching
    experiments_df["SinuTraceFile (*.csv)"] = experiments_df["SinuTraceFile (*.csv)"].str.strip()

    # Crear diccionario: filename.csv -> parámetros
    map_params = {
        row["SinuTraceFile (*.csv)"]: {
            "Ae_mm": row["Ae (mm)"],
            "Ap_mm": row["Ap (mm)"],
            "f_mm_min": row["f (mm/min)"],
            "N_rpm": row["N (rpm)"],
        }
        for _, row in experiments_df.iterrows()
    }

    print(f"✔ {len(map_params)} archivos con parámetros definidos en Excel\n")

    # Recorrer todos los dataframes y asignar parámetros si aplica
    for path_key, df in dataframes.items():
        filename = path_key.name  # ej: "Trace_0623_093401.csv"
        
        if filename in map_params:
            params = map_params[filename]

            # Añadir columnas repetidas
            for col_name, value in params.items():
                df[col_name] = value

        else:
            # No pasa nada, simplemente no tiene parámetros
            pass

    print("✔ Parámetros agregados correctamente a todos los traces correspondientes.\n")

    return dataframes







