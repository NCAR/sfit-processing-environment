import tables as h5
import numpy as np

class load_tmph5:




    def __init__(self, filename):
        self.vars = {'dnum':'mdate',
                     'Z': 'Z',
                     'T': 'T',
                     'P': 'P',
                     'col_rt':'col_rt',
                     'pcol_rt':'pcol_rt',
                     'col_ap':'col_ap',    
                     'c2y':'chi_2_y',
                     'vmr_rt': 'vmr_rt',
                     'ivmr_rt': 'ivmr_rt',
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
                     'col_co2':'',   
                     'col_h2o':'',
                     'dofs':'dofs',
                     'spectra':'spectra',
                     'directories': 'directories',
                     'auxnames':'auxnames',
                     'aux_ap':'aux_ap',
                     'aux_rt': 'aux_rt',
                     'iter':'iter',
                     'itmx':'itmx',
                     'avk_col':'avk_col',
                     'gasnames','gasnames'}

        self.h5f = h5.File(filename)
        self.dnum = self.h5f.root.mdate[:]
        self.Z = self.h5f.root.Z[:]
        self.valid = np.array(range(0,len(self.dnum)))



    def __del__(self):
        self.h5f.close()

    def get_values(self):
        return(self.vars.keys())
        
    def return_value(self, value):
        if value not in self.vars.keys():
            print 'value %s not defined in tmp.h5'%(value)
            return

        # values not in the scheme
        if value == 'err_tot':
            return(np.sqrt(diag(self.h5f.root.cov_vmr_ran[:,:,self.valid] +
                                self.h5f.root.cov_vmr_sys[:,:,self.valid])))

        igasnames =self.h5f.root.gasnames[:]
        
        if value == 'col_co2':
            return(self.h5f.root.icol_rt[igasnames.index('CO2')-1,self.valid])
        if value == 'col_h2o' and 'H2O' in igasnames:
            return(self.h5f.root.icol_rt[igasnames.index('H2O')-1,self.valid])
        if value == 'col_hdo' and 'HDO' in igasnames:
            return(self.h5f.root.icol_rt[igasnames.index('HDO')-1,self.valid])
        if value == 'auxnames':
            return(self.h5f.root.auxnames)
        if value == 'Z':
            return(self.h5f.root.Z)
        
        val = self.vars[value]
        exec('dims = self.h5f.root.'+val+'[:].shape')
        if len(dims) == 1:
            str = 'valb = self.h5f.root.'+val+'[self.valid]'
        elif len(dims) == 2:
            str = 'valb = self.h5f.root.'+val+'[:,self.valid]'
        elif len(dims) == 3:
            str = 'valb = self.h5f.root.'+val+'[:,:,self.valid]'
        print str
        exec(str)
        return(valb)
            

    def set_valid(self, ind = -1):
        # keeps only entries which are in ind. This may be used to 
        # sort or weed the data.
        if ind == -1:
            self.valid = np.array(range(0,len(self.dnum)))
            
        self.valid = ind

        
    def average(self, dnum, val, err_val):
        dd_mean = list(set(dnum.round()))
        val_mean = np.zeros(0)
        val_error = np.zeros(0)

        for ndd in dd_mean:
            inds = np.int16(np.nonzero(abs(ndd - dnum)<1))
            val_mean = np.hstack((val_mean, np.mean(val[inds])))
            val_error = np.hstack((val_error, np.std(val[inds])))

        # set entries which are calculated
        dnum = np.array(dd_mean).copy()
        val_mean = val_mean.copy()
        val_error = val_error.copy()

        return (dnum,val_mean,val_error)

    def get_partial_columns(self,zrange,Xvar=False, apriori=False,
                            average='none'):
        ind1 = np.where(np.all((self.Z > zrange[0],self.Z < zrange[1]),axis=0))[0]
        if apriori:
            a = self.h5f.root.pcol_ap[:]
        else:
            a = self.h5f.root.pcol_rt[:]

        pcolrt = np.sum(a[np.ix_(ind1,self.valid)],axis=0)
        tmp = self.h5f.root.pcol_ran[:]
        err_ran = np.sum(tmp[np.ix_(ind1,self.valid)],axis=0)
        tmp = self.h5f.root.pcol_sys[:]
        err_sys = np.sum(tmp[np.ix_(ind1,self.valid)],axis=0)
        pcoltot = np.sqrt(err_ran*err_ran + err_sys*err_sys)
        if Xvar:
            ac = self.h5f.root.air_mass[:]
            pcolrt = pcolrt/np.sum(ac[np.ix_(ind1,self.valid)],axis=0)
            pcoltot = pcoltot/np.sum(ac[np.ix_(ind1,self.valid)],axis=0)

        if average == 'none':
            return(self.dnum[self.valid], pcolrt, pcoltot)
        else:
            dnum, pcolrt, pcoltot = self.average(self.dnum[self.valid], pcolrt, pcoltot)
            return(dnum, pcolrt, pcoltot)

    def get_partial_avk(self,zrange,norm=False):
        ind1 = np.where(np.all((self.Z > zrange[0],self.Z < zrange[1]),axis=0))[0]
        if norm:
            a = self.h5f.root.avk[:,:,self.valid]
        else:
            a = self.h5f.root.avk_col[:,:,self.valid]
        a = np.sum(a[ind1,:,:], axis=0)

        return(self.dnum[self.valid], a)
