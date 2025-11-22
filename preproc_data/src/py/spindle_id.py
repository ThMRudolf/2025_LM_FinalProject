import numpy as np
import pandas as pd

class SpindleSystemID:
    """
    Performs system identification on spindle data to identify
    the dynamic parameters J (inertia) and B (viscous damping).

    Model:
        J * domega_dt + B * omega = Torque
    """

    def __init__(self, method="ols", regularization=0.0):
        """
        method: "ols", "ridge"
        regularization: ridge coefficient λ (only used when method="ridge")
        """
        self.method = method
        self.regularization = regularization
        self.J_ = None
        self.B_ = None

    def estimate(self, df):
        """
        df must contain:
            - omega_rad_s
            - T_Nm
            - time
        """

        omega = df["omega_rad_s"].values
        torque = df["T_Nm"].values
        t = df["time"].values

        # Compute derivative dω/dt numerically
        domega_dt = np.gradient(omega, t)

        # Regression matrix
        # T = J * domega_dt + B * omega
        A = np.column_stack([domega_dt, omega])
        y = torque

        if self.method == "ols":
            theta, *_ = np.linalg.lstsq(A, y, rcond=None)

        elif self.method == "ridge":
            λ = self.regularization
            ATA = A.T @ A + λ * np.eye(2)
            ATy = A.T @ y
            theta = np.linalg.solve(ATA, ATy)

        else:
            raise ValueError("Unknown method. Use 'ols' or 'ridge'.")

        self.J_ = float(theta[0])
        self.B_ = float(theta[1])

        return self.J_, self.B_

    def predict_torque(self, df):
        """
        Using the fitted model, predict torque from ω and dω/dt.
        """
        if self.J_ is None:
            raise RuntimeError("Call estimate() first.")

        omega = df["omega_rad_s"].values
        t = df["time"].values
        domega_dt = np.gradient(omega, t)

        return self.J_ * domega_dt + self.B_ * omega

    def summary(self):
        return {
            "J_estimated": self.J_,
            "B_estimated": self.B_,
            "units": {
                "J": "kg·m²",
                "B": "N·m·s/rad"
            }
        }
