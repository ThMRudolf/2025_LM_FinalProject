import numpy as np

class KienzleMillingModel:
    """
    Implements the Kienzle milling cutting-force and torque model.
    Can be reused for single-measurement simulations or batch evaluation.
    """

    def __init__(self, ap, fz, z, 
                 kappa, omega, kc11, mc,
                 rtool, phi_ent, phi_exit):
        """
        Parameters
        ----------
        ap       : float  depth of cut [mm]
        fz       : float  feed per tooth [mm]
        z        : int    number of teeth
        kappa    : float  tool angle [rad]
        omega    : float  spindle angular velocity [rad/s]
        kc11     : float  specific cutting-force coefficient
        mc       : float  Kienzle chip-thickness exponent
        rtool    : float  tool radius [m]
        phi_ent  : float  entry angle [rad]
        phi_exit : float  exit angle [rad]
        """

        self.ap = ap
        self.fz = fz
        self.z = int(z)
        self.kappa = kappa
        self.omega = omega
        self.kc11 = kc11
        self.mc = mc
        self.rtool = rtool
        self.phi_ent = phi_ent
        self.phi_exit = phi_exit

        # Precompute tooth offsets for efficiency
        self.tooth_offsets = np.arange(self.z) * 2*np.pi / self.z


    # -----------------------------------------------------
    # Compute the instantaneous angular position of each tooth
    # -----------------------------------------------------
    def compute_angles(self, t):
        """
        Returns array of angles with shape (n_times, z_teeth)
        """
        t = np.asarray(t)
        phi = self.omega * t                                # spindle angle
        angles = phi[:, None] + self.tooth_offsets[None, :]  # broadcasting
        angles = (angles + 2*np.pi) % (2*np.pi)              # normalize
        return phi, angles


    # -----------------------------------------------------
    # Compute chip thickness (positive)
    # -----------------------------------------------------
    def compute_chip_thickness(self, angles):
        """
        Chip thickness model: h = fz * |sin(angle)|
        """
        return self.fz * np.abs(np.sin(angles))


    # -----------------------------------------------------
    # Compute engagement mask based on entry/exit angles
    # -----------------------------------------------------
    def compute_engagement(self, angles):
        """
        Returns a boolean matrix of shape (n_times, z)
        """
        return (angles >= self.phi_ent) & (angles <= self.phi_exit)


    # -----------------------------------------------------
    # Full Kienzle milling model: computes Fc and Tc
    # -----------------------------------------------------
    def evaluate(self, t):
        """
        Computes torque and force time series.

        Parameters
        ----------
        t : array-like
            Time stamps.

        Returns
        -------
        phi       : spindle angle over time
        Fc        : cutting force [N]
        Tc        : cutting torque [Nm]
        sin_sums  : Σ sin(angle)^(1-mc) per time step
        """

        t = np.asarray(t)

        # Compute angles
        phi, angles = self.compute_angles(t)

        # Engagement mask
        engaged = self.compute_engagement(angles)

        # Chip thickness normalized: sin^(1-mc)
        sin_term = np.abs(np.sin(angles)) ** (1 - self.mc)
        sin_term *= engaged

        # Sum over teeth
        sin_sums = np.sum(sin_term, axis=1)

        # Base Kienzle factor
        base = (
            self.ap
            * (self.fz ** (1 - self.mc))
            * (np.sin(self.kappa) ** (1 - self.mc))
            * self.kc11
        )

        Fc = base * sin_sums
        Tc = Fc * self.rtool

        return phi, Fc, Tc, sin_sums