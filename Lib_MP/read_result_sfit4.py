import numpy as np
import linecache, string, glob, os
import read_from_file as rn
from sfit4_ctl import sfit4_ctl
import pdb
import fnmatch


reload(rn) # because problem with dreload

class read_table:

    def __init__(self, filename):
        self.table = np.recfromtxt(filename, skiprows=3,names=True)
        self.names = self.table.dtype.names
    
        ll = linecache.getline(filename, 2).strip().split()
        self.retgas = ll[3:]
        self.nr_retgas = string.atoi(ll[2])

    def get_gas_vmr(self, gasname=None):
        if gasname == None:
            gasname = self.retgas[0]
        z = self.table['ZBAR']
        vmr = self.table[gasname]
        return(vmr,z)

    def get_gas_col(self, gasname=None):
        if gasname == None:
            gasname = self.retgas[0]
        z = self.table['ZBAR']
        col = self.table['AIRMASS'] * self.table[gasname]
        return(col,z)

    def get_atmosphere(self):
        z = self.table['ZBAR']
        zb = np.vstack((self.table['Z'], 2.0*z - self.table['Z'])).T 
        p = self.table['PRESSURE']
        t = self.table['TEMPERATURE']
        ac = sum(self.table['AIRMASS'])
        return(z,zb, p,t,ac)


    def get_retrieval_gasnames(self):
        return self.retgas


class Kout:
    def __init__(self, filename):
    
        self.K_frac = np.genfromtxt(filename,skiprows=4)

class avk:
    def __init__(self, filename):
    
        self.AK_frac = np.genfromtxt(filename,skiprows=2)
        self.direc = os.path.dirname(filename)

    def renormalize(self):
        
        ap = read_table(os.path.join(self.direc, 'aprfs.table'))
        prf,z = ap.get_gas_vmr(ap.get_retrieval_gasnames()[0])
        self.AK_vmr = np.dot(np.dot(np.diag(prf),self.AK_frac),np.diag(1/prf))
        prf,z = ap.get_gas_col(ap.get_retrieval_gasnames()[0])
        self.AK_col = np.dot(np.dot(np.diag(prf),self.AK_frac),np.diag(1/prf))


    def avk(self, type='frac', direc = '.'):

        if type == 'vmr':
            try:
                return(self.AK_vmr)
            except:
                self.renormalize()
                return(self.AK_vmr)
        elif type=='column' or type=='col':
            try:
                return(self.AK_col)
            except:
                self.renormalize()
                return(self.AK_col)
        else:
            return(self.AK_frac)


class summary:
    def __init__(self, filename):
        sumf = rn.read_from_file(filename)
        self.header = sumf.get_line()
        nr_spc = int(sumf.next(1).pop(0))
        sumf.skipline(nr_spc)

        nr_retgas = int(sumf.next(1).pop(0))
        sumf.skipline(1)
        self.gas = []
        self.prf = []
        self.apriori = np.zeros(nr_retgas)
        self.retriev = np.zeros(nr_retgas)
        for nr in range(0,nr_retgas):
            int(sumf.next(1).pop(0))
            self.gas.extend(sumf.next(1))
            self.prf.extend(sumf.next(1))
            self.apriori[nr] = sumf.next(1).pop(0)
            self.retriev[nr] = sumf.next(1).pop(0)

        nr_band = int(sumf.next(1).pop(0))
        sumf.skipline(1)
        self.mw_start = np.zeros(nr_band)
        self.mw_stop = np.zeros(nr_band)
        self.spac = np.zeros(nr_band)
        self.points = np.zeros(nr_band)
        self.max_opd = np.zeros(nr_band)
        self.fov = np.zeros(nr_band)
        self.snr_ret = np.zeros(nr_band)
        self.snr_apr = np.zeros(nr_band)

        try:
            for nr in range(0,nr_band):
                sumf.next(1)
                self.mw_start[nr] = sumf.next(1).pop(0)
                self.mw_stop[nr] = sumf.next(1).pop(0)
                self.spac[nr] = sumf.next(1).pop(0)
                self.points[nr] = sumf.next(1).pop(0)
                self.max_opd[nr] = sumf.next(1).pop(0)
                self.fov[nr] = sumf.next(1).pop(0)
                sumf.next(3)
                self.snr_apr[nr] = sumf.next(1).pop(0)
                self.snr_ret[nr] = sumf.next(1).pop(0)
        except:
            pass

        sumf.skipline(1)
        try:
            self.rms = sumf.next(1).pop(0)
            self.chi_y_2 = sumf.next(1).pop(0)
            sumf.next(1)
            self.dofs = sumf.next(1).pop(0)
            sumf.next(1)
            self.iter = sumf.next(1).pop(0)
            self.iter_max = sumf.next(1).pop(0)
            self.converged = sumf.next(1)
            self.div_warn = sumf.next(1)
            del sumf
        except:
            pass

            
        
class error:
    def __init__(self, sb_ctl, direc):
        sbctl = sfit4_ctl()
        if not os.path.isfile(sb_ctl):
            self.flag = False
            return
        sbctl.read_ctl_file(sb_ctl)
        # check if sd.ctl and direc are formally consistent
        self.total_vmr = direc+'/'+sbctl.get_value('file.out.total.vmr')
        self.total_col = direc+'/'+sbctl.get_value('file.out.total')
        self.flag = True
        if not os.path.isfile(self.total_vmr):
            self.flag = False
            

    def read_total_vmr(self):
        if self.flag:
            label, matrix = self.read_error_matrix(self.total_vmr)
            self.S_vmr_ran = matrix[0]
            self.S_vmr_sys = matrix[1]
            self.vmr_ran = np.sqrt(np.diag(matrix[0]))
            self.vmr_sys = np.sqrt(np.diag(matrix[1]))
            return(self.vmr_ran, self.vmr_sys)
        else:
            return(np.nan,np.nan)

    def read_total_pcol(self):
        if self.flag:
            label, matrix = self.read_error_matrix(self.total_col)
            self.S_col_ran = matrix[0]
            self.S_col_sys = matrix[1]
            self.col_ran = np.sqrt(np.diag(matrix[0]))
            self.col_sys = np.sqrt(np.diag(matrix[1]))
            return(self.col_ran, self.col_sys)
        else:
            return(np.nan,np.nan)
    def read_error_matrix(self, filename):
        em = rn.read_from_file(filename)
        label = em.get_line().strip('# ')
        nr_mat = int(em.get_line().partition('=')[2])
        nr_rows = int(em.get_line().partition('=')[2])
        nr_cols = int(em.get_line().partition('=')[2])
        matrix = np.ndarray((nr_mat,nr_rows,nr_cols))
        for nmat in range(0,nr_mat):
            em.get_line()
            mat = em.next(nr_rows*nr_cols)
            matrix[nmat] = np.reshape(mat,(nr_cols, nr_rows))

        return label, matrix

class pbp:
    def __init__(self, filename):
        pbpf = rn.read_from_file(filename)
        self.header = pbpf.get_line()
        nr_mw = int(pbpf.next(1).pop(0))
        pbpf.next(1)
        self.sza = []
        self.mw_res = []
        self.mw_nr = []
        self.mw_start = []
        self.mw_stop = []
        self.obs = []
        self.clc = []
        self.dif = []
        self.nu = []
        for mw in range(0,nr_mw):
            pbpf.skipline(1)
            self.sza.append(pbpf.next(1).pop(0)/1000)
            self.mw_res.extend(pbpf.next(1))
            self.mw_nr.append(int(pbpf.next(1).pop(0)))
            self.mw_start.extend(pbpf.next(1))
            self.mw_stop.extend(pbpf.next(1))
            pbpf.next(4)
            
            self.obs.append([])
            self.clc.append([])
            self.dif.append([])
            self.nu.append([])

            mwnr,mwres = divmod(self.mw_nr[mw],12)
            for mw_nr in range(0,mwnr):
                pbpf.next(1)
                tmp = pbpf.next(36)
                self.obs[mw].extend(tmp[0:12])
                self.clc[mw].extend(tmp[12:24])
                self.dif[mw].extend(tmp[24:])
                
            if mwres > 0:
                pbpf.next(1)
                tmp = pbpf.next(mwres*3)
                self.obs[mw].extend(tmp[0:mwres])
                self.clc[mw].extend(tmp[mwres:2*mwres])
                self.dif[mw].extend(tmp[2*mwres:3*mwres])
            self.obs[mw] = np.array(self.obs[mw])
            self.clc[mw] = np.array(self.clc[mw])
            self.dif[mw] = np.array(self.dif[mw])
            self.nu[mw] = np.array(range(0, self.mw_nr[mw])) * self.mw_res[mw] + self.mw_start[mw]            

        del(pbpf)

class gasspectra:
    def __init__(self, direc):

        self.gas = []
        self.band = []
        self.scan = []
        self.iteration = []

        files = glob.glob(direc + '/spc*')
        for ff in files:
            ascf = rn.read_from_file(ff)
            headerline = ascf.get_line().split()
            mw_start = ascf.next(1).pop(0)
            mw_stop = ascf.next(1).pop(0)
            mw_res = ascf.next(1).pop(0)
            mw_nr = ascf.next(1).pop(0)
            clc = np.array(ascf.next(mw_nr))
            nu = np.array(range(0, mw_nr)) * mw_res + mw_start     
            self.gas.append(headerline[1])
            self.band.append(headerline[3])
            self.scan.append(headerline[5])
            self.iteration.append(headerline[7])


            
            del ascf 
