import pandas as pd
import numpy as np

# ---------------------------------------------------------
# Extraer estadísticas de nulos
# ---------------------------------------------------------
def imprimir_estadisticas_nulos(dataframes):
    """
    Calcula e imprime el total y porcentaje de valores nulos por columna
    """
    if not isinstance(dataframes, dict):
        raise TypeError("dataframes debe ser un diccionario nombre->DataFrame")

    from collections import defaultdict

    nulls = defaultdict(int)
    totals = defaultdict(int)

    # Agregar conteos por columna a través de todos los dataframes
    for df in dataframes.values():
        if df is None:
            continue
        if not isinstance(df, pd.DataFrame):
            continue
        n_rows = len(df)
        for col in df.columns:
            nulls[col] += int(df[col].isnull().sum())
            totals[col] += n_rows

    # Si no hay columnas, informar y devolver DataFrame vacío
    if len(totals) == 0:
        print("No se encontraron columnas en los DataFrames proporcionados.")
        return 
    # Construir y mostrar resultados
    for col in sorted(totals.keys()):
        n = nulls[col]
        t = totals[col]
        pct = (n / t * 100) if t > 0 else 0.0
        if (n > 0):
            print(f"-Para la variable {col} hay {n} valores nulos que corresponden al {pct:.2f}% de los valores de toda la base para esa columna")
    return 
# ---------------------------------------------------------
# Revisar y tratar valores nulos
# ---------------------------------------------------------
def revisar_nulos_interpolar(dataframes):

    dataframes_nulos = dataframes.copy()
    for df in dataframes_nulos.values():
        nulos_por_col = df.isnull().sum()
        columnas_con_nulos = nulos_por_col[nulos_por_col > 0]
        # Si hay columnas con nulos, intentar interpolar
        if not columnas_con_nulos.empty:
            for col in columnas_con_nulos.index:
                # Intentar interpolar si es numérica
                if pd.api.types.is_numeric_dtype(df[col]):
                    # Evitar la asignación encadenada que causa FutureWarning
                    interpolated = df[col].interpolate(method='linear', limit_direction='both')
                    df[col] = interpolated
                else:
                    print(f" ⚠ Columna '{col}' no es numérica; no se puede interpolar.")
    print("✔ Se ha completado la revisión e interpolación de nulos.")
    return dataframes_nulos
