import tables as h5
import numpy as np

class load_tmph5:

    def __init__(self, filename):
        h5f = h5.File(filename)
        self.dnum = h5f.root.mdate[:]
        self.col_rt = h5f.root.col_rt[:]
        self.col_ap = h5f.root.col_ap[:]
        self.c2y = h5f.root.chi_2_y[:]
        self.err_ran = h5f.root.col_ran[:]
        self.err_sys = h5f.root.col_sys[:]
        self.err_tot = np.sqrt(self.err_ran**2 + self.err_sys**2)
        self.latitude = h5f.root.lat[:]
        self.snr_clc = h5f.root.snr_clc[:]
        self.snr_the = h5f.root.snr_the[:]
        self.aircol = h5f.root.air_col[:]
        self.sza = h5f.root.sza[:]
        self.P_surface = h5f.root.P_s[:]
        igasnames = h5f.root.gasnames[:]
        self.gasname = igasnames[0]
        if 'CO2' in igasnames:
            self.col_co2 = h5f.root.icol_rt[igasnames.index('CO2')-1,:]
        self.spectra = h5f.root.spectra[:]
        h5f.close()


    def valid(self, ind):
        self.dnum      = self.dnum[ind]     
        self.col_rt    = self.col_rt[ind]         
        self.col_ap    = self.col_ap[ind]        
        self.c2y       = self.c2y[ind]           
        self.err_ran   = self.err_ran[ind]       
        self.err_sys   = self.err_sys[ind]       
        self.err_tot   = self.err_tot[ind]       
        self.latitude  = self.latitude[ind]      
        self.snr_clc   = self.snr_clc[ind]       
        self.snr_the   = self.snr_the[ind]       
        self.aircol    = self.aircol[ind]        
        self.sza    = self.sza[ind]        
        self.P_surface = self.P_surface[ind]     
        self.col_co2   = self.col_co2[ind]
        self.spectra = h5f.root.spectra[ind]
