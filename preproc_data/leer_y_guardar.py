from pathlib import Path
import pandas as pd
from collections import defaultdict
 
# ---------------------------------------------------------
# Localizar todos los archivos CSV dentro de carpeta data
# ---------------------------------------------------------
def leer_todos_csv(data_dir):
    """
    Lee todos los archivos CSV dentro de data_dir y sus subcarpetas.
    
    - Verifica si existen archivos con el mismo nombre (sin incluir su ruta).
    - Carga los CSV en un diccionario usando rutas relativas como claves.
    
    Retorna:
        dataframes: dict[pathlib.Path -> pandas.DataFrame]
    """
    
    data_path = Path(data_dir)

    # Buscar TODOS los .csv recursivamente
    all_csv_files = list(data_path.rglob("*.csv"))

    # --- PASO 1: Detectar archivos con nombres repetidos ---------------------
    # Mapeamos nombre.csv  -> lista de rutas donde aparece
    nombre_to_paths = defaultdict(list)
    for file in all_csv_files:
        nombre_to_paths[file.name].append(file)

    # Buscar nombres repetidos
    nombres_repetidos = {name: paths for name, paths in nombre_to_paths.items() if len(paths) > 1}

    if nombres_repetidos:
        print("\n⚠️  Atención: Se encontraron archivos CSV con nombres repetidos:")
        for name, paths in nombres_repetidos.items():
            print(f"  - {name}:")
            for p in paths:
                print(f"       * {p}")
    else:
        print("✔ Todos los archivos CSV tienen nombres únicos.\n")
    # -------------------------------------------------------------------------

    # --- PASO 2: Leer archivos y guardarlos en un diccionario ----------------
    dataframes = {}

    for file in all_csv_files:
        try:
            # Leemos el CSV
            df = pd.read_csv(file)
            # Guardamos usando la ruta relativa como clave
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

# ---------------------------------------------------------
# Leer los archivos de experimentos desde la carpeta data
# ---------------------------------------------------------
def cargar_experimentos(data_dir):
    """
    Lee todos los archivos Experiment_C*.xlsx dentro de data_dir.
    
    Retorna un único DataFrame concatenado.
    """
    data_path = Path(data_dir)
    excel_files = list(data_path.glob("Experiment_C*.xlsx"))

    if not excel_files:
        print("❌ No se encontraron archivos Experiment_C*.xlsx")
        return None
    
    print(f"✔ Archivos encontrados: {[f.name for f in excel_files]}")

    # Leer y unir todos los excels en un único DF
    df_list = []
    for f in excel_files:
        df_list.append(pd.read_excel(f))

    experiments = pd.concat(df_list, ignore_index=True)

    return experiments