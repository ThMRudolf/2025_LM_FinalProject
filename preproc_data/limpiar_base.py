import pandas as pd

# ---------------------------------------------------------
# Renombrar columnas
# ---------------------------------------------------------
def renombrar_cols(dataframes):
    # 1.- Añadir columna 'source_file' con 'carpeta1-carpeta2-carpeta3-...'
    for fname, df in dataframes.items():
        source_file = "-".join(fname.parts)
        #eliminamos nombre_archivo.csv para dejar solo las carpetas
        source_file = "-".join(fname.parts[:-1])
        # Añadimos la columna source file al DataFrame
        df['source_file'] = source_file
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