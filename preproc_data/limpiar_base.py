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
    #Añadimos parámetro z y diametro (d)
    z = 2
    d = 40
    for key in map_params.keys():
        map_params[key]["z"] = z
        map_params[key]["d_mm"] = d
    
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
    # Parametros para archivos carpeta PLAN
    ae = 38
    ap=2
    f = 632
    z = 2
    N = 2108
    d = 40
    #Buscamos archivos que contengan 'Plan' en su ruta
    for path_key, df in dataframes.items():
        if 'Plan' in str(path_key):
            # Añadir nuevas columas con los parámetros fijos
            df['Ae_mm'] = ae
            df['Ap_mm'] = ap
            df['f_mm_min'] = f
            df['N_rpm'] = N
            df['z'] = z
            df['d_mm'] = d

    print("✔ Parámetros agregados correctamente a todos los traces correspondientes.\n")

    return dataframes

#---------------------------------------------------------
# Revisar archivos sin parámetros
#---------------------------------------------------------
def revisar_archivos_sin_parametros(dataframes, columnas_parametros):
    """
    Revisa si cada DataFrame contiene todas las columnas de parámetros.
    Retorna una lista con los nombres de archivos que NO tienen todas las columnas.
    """
    archivos_faltantes = []

    for fname, df in dataframes.items():
        faltantes = [col for col in columnas_parametros if col not in df.columns]
        if faltantes:
            archivos_faltantes.append((fname, faltantes))

    # Imprimir reporte
    if archivos_faltantes:
        count = len(archivos_faltantes)
        print(f" - {count} ⚠ ARCHIVOS SIN PARÁMETROS COMPLETOS:")
    else:
        print("\n✔ Todos los archivos contienen las columnas de parámetros.")

    # Si el número de archivos faltantes es pequeño, los eliminamos del dataframes
    if len(archivos_faltantes) > 0 and len(archivos_faltantes) <= 5:
        for fname, _ in archivos_faltantes:
            del dataframes[fname]
            print(f"   • {fname} eliminado del conjunto de datos.")
    else: 
        print("Demasiados archivos faltantes")
    # Return lista de archivos problemáticos
    return dataframes






