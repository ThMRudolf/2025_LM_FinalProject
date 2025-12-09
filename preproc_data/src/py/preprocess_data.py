import numpy as np
import pandas as pd
from scipy.signal import correlate

class PreprocessData:
    """
    Class for preprocessing data for milling simulations.
    """

    def __init__(self, fs):
        """
        Initialize with raw data.

        Parameters
        ----------
        data : array-like
            Raw measurement data.
        """
        self.fs = fs  # Sampling frequency
        #self.real_signal = np.asarray(real_signal) 
        #self.model_signal = np.asarray(model_signal)

    def normalize(self, signal):
        """
        Normalize the data to zero mean and unit variance.
        """
        mean_signal = np.mean(signal)
        std_signal = np.std(signal)
        normalized_signal = (signal - mean_signal) / std_signal
        return normalized_signal
    
    def set_time(self, time):
        self.time = np.asarray(time)
    
    def set_real_signal(self, real_signal):
        self.real_signal = np.asarray(real_signal)

    def set_model_signal(self, model_signal):
        self.model_signal = np.asarray(model_signal)

    def estimate_delay(self, threshold_factor=4, window_length=0.3):
        """
        Estimate the time delay between real and model force signals.
    
        Parameters
        ----------
        real_force : array-like
            Real measured force signal (1D).
        model_force : array-like
            Model-predicted force signal (1D), same sampling rate preferred.
        fs : float
            Sampling frequency [Hz].
        threshold_factor : float
            Multiplier for noise level to detect cutting onset.
        window_length : float
            Length (in seconds) of steady-window used for correlation.

        Returns
        -------
        tau : float
        Time delay [seconds], positive means: model must be shifted RIGHT.
        lag_samples : int
        Delay in samples.
        """
        fs = self.fs
        real_force = np.asarray(self.real_signal)
        model_force = np.asarray(self.model_signal)

        # -------------------------------------------------------------
        # 1. Detect cutting onset
        # -------------------------------------------------------------
        noise_level = np.std(real_force[:int(0.1 * len(real_force))])  # first 10% = noise
        threshold = threshold_factor * noise_level

        above = np.where(np.abs(real_force) > threshold)[0]
        if len(above) == 0:
            raise ValueError("No cutting onset detected.")
        start_idx = max(above[0] - int(0.02 * fs), 0)   # small buffer before onset

        # -------------------------------------------------------------
        # 2. Crop both signals to same window
        # -------------------------------------------------------------
        N_window = int(window_length * fs)

        if start_idx + N_window > len(real_force):
            raise ValueError("Recording too short after onset.")

        real_crop = real_force[start_idx:start_idx + N_window]
        model_crop = model_force[start_idx:start_idx + N_window]

        # -------------------------------------------------------------
        # 3. Normalize (zero-mean)
        # -------------------------------------------------------------
        r = real_crop - np.mean(real_crop)
        m = model_crop - np.mean(model_crop)

        # -------------------------------------------------------------
        # 4. Cross-correlation
        # -------------------------------------------------------------
        corr = correlate(r, m, mode='full')
        lags = np.arange(-len(r) + 1, len(m))

        lag_samples = lags[np.argmax(corr)]
        tau = lag_samples / fs

        return tau, lag_samples, start_idx


    def find_constant_fs_region(self, tolerance=0.0001, bootstrap=30):
        """
        time: 1D array of time stamps
        tolerance: relative tolerance for dt deviations (0.001 = 0.1%)
        bootstrap: number of initial samples used to estimate dt_ref
        
        Returns:
            start_idx (int), end_idx (int)
        """
        time = self.time
        #print(f"Time data length: {len(time)}, data tpye: {type(time)}")
        time = np.asarray(time)
        #print(f"Time data length: {len(time)}, data tpye: {type(time)}")
        if len(time) < 3:
            return 0, len(time)-1

        # Zeitdifferenzen berechnen
        dt = np.diff(time)

        # Referenz-Sampling-Zeit aus den ersten Samples schätzen
        k = min(bootstrap, len(dt))
        dt_ref = np.median(dt[:k])

        # Relative Abweichung berechnen
        rel_dev = (dt - dt_ref) / dt_ref

        # Indexe, an denen die Toleranz verletzt wird
        bad = np.where(rel_dev > tolerance)[0]

        if len(bad) == 0:
            # Alles konstant 
            return 0, len(time) - 1

        # Erster Verstoß → davor endet der gültige Bereich
        end_idx = bad[0]

        return 0, end_idx
    
    def shift_signal(self, x, lag_samples):
        # positive lag means: model should be shifted to the right
        return np.roll(x, lag_samples)
