import re
import numpy as np
import pandas as pd
from pathlib import Path
from spindle_id import SpindleSystemID

class MachineToolParser:
    """
    Reads Siemens .TEA files (axis + drive), extracts MD parameters,
    and converts NCK raw servo signals to physical units.
    
    Supports multiple machine tools and arbitrary DRx drive indices.
    """

    # ---------------------------------------------------------
    # 1) INIT
    # ---------------------------------------------------------
    def __init__(self, tea_axis_path, tea_drive_path, drive="DR4"):
        self.drive = drive.upper()
        self.axis_params = self._read_tea_file(tea_axis_path)
        self.drive_params = self._read_tea_file(tea_drive_path)

        # Extract motor/drive physics
        self.md = self._extract_drive_parameters(self.drive_params, self.drive)

    # ---------------------------------------------------------
    # 2) TEA-FILE READER
    # ---------------------------------------------------------
    def _read_tea_file(self, path):
        """
        Reads a SINUMERIK .TEA parameter file and returns:
        
        {
            "$MD_MOTOR_NOMINAL_CURRENT[DR4]": 59.0,
            "$MD_MOTOR_INERTIA[DR4]": 0.036,
            ...
        }
        """

        params = {}

        pattern = re.compile(
            r'^\s*N\d+\s+(\$[A-Z0-9_]+(?:\[[^\]]+\])?)\s*=\s*(.+?)\s*$'
        )

        with open(path, "r", errors="ignore") as f:
            for line in f:
                m = pattern.match(line)
                if m:
                    key = m.group(1).strip()
                    raw_val = m.group(2).strip()

                    # Convert values
                    if raw_val.startswith("'") and raw_val.endswith("'"):
                        val = raw_val.strip("'")
                    else:
                        try:
                            if "." in raw_val:
                                val = float(raw_val)
                            else:
                                val = int(raw_val)
                        except:
                            val = raw_val

                    params[key] = val

        return params

    # ---------------------------------------------------------
    # 3) DRIVE PARAM EXTRACTION
    # ---------------------------------------------------------
    def _extract_drive_parameters(self, params, drive):
        """
        Collects physics-relevant MD parameters.
        Works with motor M1 and fallback to M2.
        """

        def g(name):
            return (
                params.get(f"{name}[{drive}]")
                or params.get(f"{name}_M2[{drive}]")
                or None
            )

        extracted = {
            "motor_nominal_current_A": g("$MD_MOTOR_NOMINAL_CURRENT"),
            "motor_nominal_power_kW": g("$MD_MOTOR_NOMINAL_POWER"),
            "motor_rated_speed_rpm":  g("$MD_MOTOR_RATED_SPEED"),
            "motor_max_speed_rpm":    g("$MD_MOTOR_MAX_ALLOWED_SPEED"),
            "motor_inertia_kgm2":     g("$MD_MOTOR_INERTIA"),
            "inverter_rated_current_A": g("$MD_INVERTER_RATED_CURRENT"),
            "current_limit_pct": g("$MD_CURRENT_LIMIT"),
            "torque_limit_pct":  g("$MD_TORQUE_LIMIT_1"),
            "power_limit_pct":   g("$MD_POWER_LIMIT_1"),
            "enc_res_motor":     g("$MD_ENC_RESOL_MOTOR"),
        }

        return extracted

    # ---------------------------------------------------------
    # 4) RAW-TO-PHYSICS CONVERSION
    # ---------------------------------------------------------
    def convert_signals(self, df):
        """
        Convert raw NCK signals to physical units:
        rpm, rad/s, A, W, Nm.

        Required df columns:
            ActVelMot32
            ActCurr32
            ActPower32
        """

        # 1) SPEED			
        df["rpm"] = 0.1 * df["velAx4"]
        df["omega_rad_s"] = df["rpm"] * (2*np.pi/60.0)

        # 2) CURRENT
        I_nom = self.md["motor_nominal_current_A"]
        df["I_pct"] = df["iqAx4"] / 10.0
        df["I_A"] = df["I_pct"] / 100.0 * I_nom

        # 3) POWER
        P_nom = self.md["motor_nominal_power_kW"]
        df["P_pct"] = df["powerAx4"] / 10.0
        df["P_kW"] = df["P_pct"] / 100.0 * P_nom
        df["P_W"] = df["P_kW"] * 1000.0

        # 4) TORQUE
        df["T_Nm"] = 9550.0 * df["P_kW"] / df["rpm"].clip(lower=1e-3)
        
        # 5) Derivatives
        df["domega_rad_s2"] = np.gradient(df["omega_rad_s"], df["time"])
        df["domega_rad_s2_clean"] = pd.Series(df["domega_rad_s2"]).replace([np.inf, -np.inf], np.nan).interpolate().values
        return df

    # ---------------------------------------------------------
    # 5) FULL PIPELINE: CSV → PHYSICS
    # ---------------------------------------------------------
    def process_csv(self, csv_path):
        """
        Reads your logged NCK CSV file and returns a dataframe
        with added physical-unit columns.
        """
        df = pd.read_csv(csv_path)
        df = self.convert_signals(df)
        return df
    # ---------------------------------------------------------
    # 6) Identify spindle dynamics
    # Uses the SpindleSystemID class to estimate 
    # ---------------------------------------------------------
    def identify_spindle_dynamics(self, df, method="ols", regularization=0.0):
        """
        Run system identification on the given dataframe (already converted).
        Returns J and B.
        """
        sid = SpindleSystemID(method=method, regularization=regularization)
        J, B = sid.estimate(df)
        return J, B, sid
