import tables as h5
import numpy as np
import time_series as ts

class load_tmph5:




    def __init__(self, filename):
        self.vars = {'dnum':'mdate',
                     'col_rt':'col_rt',
                     'col_ap':'col_ap',    
                     'c2y':'chi_2_y',       
                     'err_ran':'col_ran',   
                     'err_sys':'col_sys',   
                     'err_tot':'',   
                     'latitude':'lat',  
                     'snr_clc':'snr_clc',   
                     'snr_the':'snr_the',   
                     'aircol':'air_col',    
                     'sza':'sza',
                     'P_surface':'P_s', 
                     'col_co2':'',   
                     'col_h2o':'',
                     'dofs':'dofs',
                     'spectra':'spectra',
                     'directories': 'directories'};

        h5f = h5.File(filename)
        for i in self.vars.keys():
            if len(self.vars[i]) > 0:
                val = self.vars[i]
                str = 'self.'+i+' = h5f.root.'+val+'[:]'
                exec(str)
        # Construct and evaluate lines like

        # not in the scheme
        self.spectra = np.array(self.spectra)
        self.directories = np.array(self.directories)
        self.err_tot = np.sqrt(self.err_ran**2 + self.err_sys**2)
        igasnames = h5f.root.gasnames[:]
        self.gasname = igasnames[0]
        if 'CO2' in igasnames:
            self.col_co2 = h5f.root.icol_rt[igasnames.index('CO2')-1,:]
        if 'H2O' in igasnames:
            self.col_h2o = h5f.root.icol_rt[igasnames.index('H2O')-1,:]
        h5f.close()


    def valid(self, ind):
        # keeps only entries which are in ind. This may be used to 
        # sort or weed the data.
        for i in self.vars.keys():
#            if len(self.vars[i]) > 0:
#                val = self.vars[i]
            str = 'self.'+i+' = self.'+i+'[ind]'
            exec(str)

    def average(self):
        dd_mean = list(set(self.dnum.round()))
        col_mean = np.zeros(0)
        ac_mean = np.zeros(0)
        esys_mean = np.zeros(0)

        for ndd in dd_mean:
            inds = np.int16(np.nonzero(abs(ndd - self.dnum)<1))
            col_mean = np.hstack((col_mean, np.mean(self.col_rt[inds], axis=1)))
            ac_mean =  np.hstack((ac_mean, np.mean(self.aircol[inds], axis=1)))
            esys_mean = np.hstack((esys_mean, np.linalg.norm(self.err_sys[inds])/inds.size))
        # Delete all other entries
        for i in self.vars.keys():
            exec('del self.'+i)

        # set entries which are calculated
        self.dnum = np.array(dd_mean).copy()
        self.col_rt = col_mean.copy()
        self.aircol = ac_mean.copy()
        self.err_sys = esys_mean.copy()

