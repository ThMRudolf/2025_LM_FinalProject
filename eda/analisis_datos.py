import pandas as pd
import random
import datetime

def analizar_duracion_cortes(all_dfs):
    durations = []

    for df in all_dfs:
        # Duración = tiempo final - inicial
        duration = df["time"].iloc[-1] - df["time"].iloc[0]
        durations.append(duration)

    durations = pd.Series(durations)
    metricas_duracion = {
        "min_duration_s": durations.min(),
        "max_duration_s": durations.max(),
        "mean_duration_s": durations.mean(),
        "std_duration_s": durations.std()
    }

    # Calculamos el time-step promedio, mínimo, máximo y desviación estándar de cada serie de tiempo
    time_steps = []
    for df in all_dfs:
        time_diffs = df["time"].diff().dropna()
        time_steps.append(time_diffs)
    all_time_steps = pd.concat(time_steps)
    metrica_time_step = {
        "min_time_step_s": all_time_steps.min(),
        "max_time_step_s": all_time_steps.max(),
        "mean_time_step_s": all_time_steps.mean(),
        "std_time_step_s": all_time_steps.std()
    }
    
    return metricas_duracion, metrica_time_step

def analizar_torque(all_dfs):
    torque_stats = []

    for df in all_dfs:
        stats = {
            "file": df["source_file"].iloc[0],
            "torque_min": df["torque_spindle"].min(),
            "torque_max": df["torque_spindle"].max(),
            "torque_mean": df["torque_spindle"].mean(),
            "torque_std": df["torque_spindle"].std()
        }
        torque_stats.append(stats)

    torque_stats_df = pd.DataFrame(torque_stats)

    # Estadísticas globales
    global_stats = {
        "global_min": torque_stats_df["torque_min"].min(),
        "global_max": torque_stats_df["torque_max"].max(),
        "global_mean": torque_stats_df["torque_mean"].mean(),
        "global_std_mean": torque_stats_df["torque_std"].mean()
    }

    return global_stats

def graficas(all_dfs):
    import matplotlib.pyplot as plt

    # Graficar torque vs tiempo para cada DataFrame
    # ---------------------------------------------------------
    # Seleccionamos 6 dataframes aleatorios para graficar
    sample_dfs = random.sample(list(all_dfs), min(6, len(list(all_dfs))))

    # Dibujamos las 6 gráficas en una figura 2x3
    fig, axs = plt.subplots(3,2, figsize=(12, 10))
    axs = axs.flatten() 
    for i, df in enumerate(sample_dfs):
        axs[i].plot(df["time"], df["torque_spindle"], label="Torque Spindle", color='b')
        axs[i].set_title(f"Torque vs Tiempo ({df['path'].iloc[0]}/{df['source_file'].iloc[0]})")
        axs[i].set_xlabel("Tiempo (s)")
        axs[i].set_ylabel("Torque Spindle")
        axs[i].legend()
        axs[i].grid()

    plt.tight_layout()
    #Guardamos la figura
    #Registramos tiempo actual para el nombre del archivo
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    plt.savefig(f"grafica_torque_vs_tiempo_{timestamp}.png")
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # Histogramas de torque: 
    #Calculamos torque mean, max y std para todos los dataframes
    torque_means = []
    torque_maxs = []
    torque_stds = []
    for df in all_dfs:
        torque_means.append(df["torque_spindle"].mean())
        torque_maxs.append(df["torque_spindle"].max())
        torque_stds.append(df["torque_spindle"].std())
    #Creamos los histogramas
    fig, axs = plt.subplots(1,3, figsize=(18, 5))
    axs[0].hist(torque_means, bins=20, color='g', alpha=0.7)
    axs[0].set_title("Histograma de Torque Mean")
    axs[0].set_xlabel("Torque Mean")
    axs[0].set_ylabel("Frecuencia")
    axs[0].grid()
    axs[1].hist(torque_maxs, bins=20, color='r', alpha=0.7)
    axs[1].set_title("Histograma de Torque Max")
    axs[1].set_xlabel("Torque Max")
    axs[1].set_ylabel("Frecuencia")
    axs[1].grid()
    axs[2].hist(torque_stds, bins=20, color='b', alpha=0.7)
    axs[2].set_title("Histograma de Torque Std")
    axs[2].set_xlabel("Torque Std")
    axs[2].set_ylabel("Frecuencia")
    axs[2].grid()
    plt.tight_layout()
    #Guardamos la figura
    plt.savefig(f"histogramas_torque.png")
    # ---------------------------------------------------------
