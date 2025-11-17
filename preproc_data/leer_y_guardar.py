from pathlib import Path
import pandas as pd
 
# ---------------------------------------------------------
# Localizar todos los archivos CSV dentro de carpeta data
# ---------------------------------------------------------
def leer_todos_csv(data_dir):
    data_path = Path(data_dir)
    all_csv_files = list(data_path.rglob("*.csv"))

    dataframes = {}
    for file in all_csv_files:
        try:
            df = pd.read_csv(file)
            dataframes[file.relative_to(data_path)] = df
        except Exception as e:
            print(f"Error al leer {file}: {e}")

    return dataframes


# ---------------------------------------------------------
# Leer cada archivo solo para extraer los nombres de columnas
# ---------------------------------------------------------

def comprobar_columnas_csv(dataframes):

    column_sets = {fname: list(df.columns) for fname, df in dataframes.items()}

    unique_structures = set(tuple(cols) for cols in column_sets.values())
    if len(unique_structures) == 1:
        #Las columnas son iguales en todos los DataFrames
        reference = list(unique_structures)[0]
    else:
        print("⚠ Se encontraron diferencias en los nombres de columnas.\n")
        reference = list(unique_structures)[0]

        for fname, cols in column_sets.items():
            if tuple(cols) != reference:
                print(f" - {fname} tiene columnas distintas:")
                print(f"   {cols}")
