   
import numpy as np
import pandas as pd

class GetExperimData:
    def __init__(self, str2file, tool_type):
        self.tool_type = tool_type
        self.str2file = str2file
    def get_output_angle(self, ae, rtool):
        """ Get output angle with given entrance angle 0 [rad]. """
        dtool = 2 * rtool
        if (ae > dtool):
            raise ValueError("ae cannot be larger than tool diameter")
        if(ae>=rtool):
            kath = rtool-(dtool-ae)
            phi_out = np.pi - np.arccos(kath/rtool)
        else:
            kath = rtool - ae
            phi_out = np.arccos(kath/rtool)
        return phi_out
    def set_material_parameters(self, kc11 = 1800, mc = 0.25):
        self.kc11 = kc11
        self.mc = mc
    def set_tool_parameters(self, rtool = 20, kappa = 45):
        self.rtool = rtool
        self.kappa = kappa

    def get_experiment_param(self):
        ## read in the process parameters from a excel file
        params_df = pd.read_excel(self.str2file, index_col=0)
    
        params_df['phi_exit_rad'] = params_df.apply(lambda row: self.get_output_angle(row['Ae (mm)']/1000, self.rtool/1000), axis=1)
        params_df['phi_ent_rad'] = np.deg2rad(0.0)  # assuming constant entry angle of 0 degree

        params_df['rtool (m)'] = self.rtool
        params_df['omega (rad/s)'] = 2 * np.pi * params_df['N (rpm)'] / 60
        params_df['z'] = 2
        params_df['kappa (rad)'] = np.deg2rad(self.kappa)  # assuming constant tool angle of 45 degree
        params_df['kc11'] = self.kc11  # example value
        params_df['mc'] = self.mc    # example value
        params_df['fz (mm/tooth)'] = params_df['f (mm/min)']/(params_df['N (rpm)']*params_df['z'])  #  

        return params_df