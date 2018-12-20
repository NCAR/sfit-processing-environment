import tables as h5
import numpy as np

class load_tmph5:




    def __init__(self, filename):
        self.vars = {'dnum':'mdate',
                     'Z': 'Z',
                     'col_rt':'col_rt',
                     'pcol_rt':'pcol_rt',
                     'col_ap':'col_ap',    
                     'c2y':'chi_2_y',
                     'vmr_rt': 'vmr_rt',
                     'vmr_ap': 'vmr_ap',
                     'err_ran':'col_ran',   
                     'err_sys':'col_sys',   
                     'err_tot':'',
                     'vmr_ran':'cov_vmr_ran',
                     'vmr_sys':'cov_vmr_sys',
                     'latitude':'lat',
                     'longitude':'lon',  
                     'snr_clc':'snr_clc',   
                     'snr_the':'snr_the',   
                     'aircol':'air_col',    
                     'sza':'sza',
                     'P_surface':'P_s',
                     'T_surface':'T_s', 
                     'col_co2':'',   
                     'col_h2o':'',
                     'dofs':'dofs',
                     'spectra':'spectra',
                     'directories': 'directories',
#                     'auxname':'auxnames',
#                     'aux_ap':'aux_ap',
#                     'aux_rt': 'aux_rt',
                     'P': 'P',
                     'iter':'iter',
                     'itmx':'itmx',
                     'avk_vmr':'avk_vmr',
                     'avk_pcol':'avk_col',
                     'avk_col':'',
                     'gasnames':'gasnames'}

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
        self.err_tot[np.isnan(self.err_tot)] = 1e99
        igasnames = h5f.root.gasnames[:]
        self.gasname = igasnames[0]
        self.col_co2 = 0
#        if 'CO2' in igasnames:
        for co2name in [s for s in igasnames if s.find('CO2')==0]:
            self.col_co2 = self.col_co2+h5f.root.icol_rt[igasnames.index(co2name)-1,:]

        if 'H2O' in igasnames:
            self.col_h2o = h5f.root.icol_rt[igasnames.index('H2O')-1,:]

        if 'HDO' in igasnames:
            self.col_hdo = h5f.root.icol_rt[igasnames.index('HDO')-1,:]
        self.get_column_avk()
            
        h5f.close()


        

    def valid(self, ind):
        # keeps only entries which are in ind. This may be used to 
        # sort or weed the data.
        for i in self.vars.keys():
#            if len(self.vars[i]) > 0:
#                val = self.vars[i]

            ind = np.array(ind)
            str = 'a = type(self.'+i+')'
            try:
                exec(str)
            except:
                continue
            if i == 'Z':
                continue
            if a == type(np.ndarray([])):
                str = 'l = len(self.'+i+'.shape)'
                try:
                    exec(str)
                except:
                    continue
                if l == 2:
                    str = 'self.'+i+' = self.'+i+'[:,ind]'
                else:
                    str = 'self.'+i+' = self.'+i+'[ind]'
                    #            else:
                    #                    str = 'self.'+i+' = self.'+i+'[ind]'
                try:
                    exec(str)
                except:
                    continue

    def average(self, range='daily'):

        dd_mean = list(set(self.dnum.round()))
        col_mean = np.zeros(0)
        pcol_mean = np.zeros((self.pcol_rt.shape[0],0))
        vmr_ap_mean = np.zeros((self.vmr_ap.shape[0],0))
        ac_mean = np.zeros(0)
        esys_mean = np.zeros(0)
        eran_mean = np.zeros(0)
        lat_mean = np.zeros(0)
        lon_mean = np.zeros(0)
        P_mean = np.zeros((self.P.shape[0],0))
        avk_vmr_mean = np.zeros((self.avk_vmr.shape[0], self.avk_vmr.shape[1],0))
        Z = self.Z

        for ndd in dd_mean:
            inds = np.int16(np.nonzero(abs(ndd - self.dnum)<1))
            col_mean = np.hstack((col_mean, np.mean(self.col_rt[inds], axis=1)))
            ac_mean =  np.hstack((ac_mean, np.mean(self.aircol[inds], axis=1)))
            esys_mean = np.hstack((esys_mean, np.linalg.norm(self.err_sys[inds])/inds.size))
            eran_mean = np.hstack((eran_mean, np.linalg.norm(self.err_ran[inds])/inds.size))
            lat_mean = np.hstack((lat_mean, np.mean(self.latitude[inds], axis=1)))
            lon_mean = np.hstack((lon_mean, np.mean(self.longitude[inds], axis=1)))
            pcol_mean = np.hstack((pcol_mean, np.mean(self.pcol_rt[:,inds[0]], axis=1,keepdims=True)))
            vmr_ap_mean = np.hstack((vmr_ap_mean, np.mean(self.vmr_ap[:,inds[0]], axis=1,keepdims=True)))
            P_mean = np.hstack((P_mean, np.mean(np.log(self.P[:,inds[0]]), axis=1,keepdims=True)))
            avk_vmr_mean = np.dstack((avk_vmr_mean, np.mean(self.avk_vmr[:,:,inds[0]], axis=2,keepdims=True)))

            
        # Delete all other entries
        for i in self.vars.keys():
            try:
                exec('del self.'+i)
            except:
                continue

        # set entries which are calculated
        self.dnum = np.array(dd_mean).copy()
        self.col_rt = col_mean.copy()
        self.aircol = ac_mean.copy()
        self.err_sys = esys_mean.copy()
        self.err_ran = eran_mean.copy()
        self.latitude = lat_mean.copy()
        self.longitude = lon_mean.copy()
        self.pcol_rt = pcol_mean.copy()
        self.vmr_ap_mean = vmr_ap_mean.copy()
        self.P_mean = np.exp(P_mean.copy())
        self.avk_vmr_mean = avk_vmr_mean.copy()
        self.Z = Z

    def get_column_avk(self):
        self.avk_col = np.sum(self.avk_pcol,axis=1)

        
    def get_partial_columns(self,zrange, apriori=False):
        ind1 = np.where(np.all((self.Z > zrange[0],self.Z < zrange[1]),axis=0))[0]
        if apriori:
            pcolrt = np.sum(self.pcol_ap[ind1,:],axis=0)
        else:
            pcolrt = np.sum(self.pcol_rt[ind1,:],axis=0)

        return(self.dnum, pcolrt)
