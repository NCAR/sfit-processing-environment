import numpy as np
import linecache, string, glob, os
import read_from_file as rn
import pdb
import fnmatch


#reload(rn) # because problem with dreload

# class read_stationlayer():
#     def __init__(self,filename):
#         stl = np.recfromtxt(filename, skip_header=2,names=True)
#         self.z = stl[]
#         self.z_thick = stl['thick']
#         self.z_growth = stl[:,3]
#         self.z_mid = stl[:,4]
        

class sfit4_ctl:

    def __init(self):
        pass


    def read(self, ctlfile):

        fid = open(ctlfile, 'r')
        
        self.value = {}
        old_tag = ''
        for line in fid:
            line = line.strip()
#            pdb.set_trace()
            if line.find('#')>-1:
                line = line[0:line.find('#')].strip()
            if len(line)==0:
                if len(old_tag) > 0:
                    self.value[old_tag] += ' ' + line.strip().strip()
                continue;
            if line.find('=') == -1:
                self.value[old_tag] += ' ' + line.strip().strip()
                continue
            tags = line.split('=')
            old_tag = tags[0].strip()
            if len(tags) == 2:
                self.value[tags[0].strip()] = tags[1].strip()


        fid.close()

    def get_value(self, tag):

        tag = tag.strip()
        if self.value.has_key(tag):
            return self.value[tag].strip()
        else:
            print ('key ' + tag.strip() + ' not found')
            return(-1)

    def get_keys(self, level=''):
        # gets all keys under key level
        # e.g. for key file.out.summary 
        # get_keys('file.out') it returns ['summary']
        # if level is not given, it returns all keys
        res = []
        if level.endswith('.'):
            level = level[0:-1]
        else:
            level = level+'.'            
        for v in self.value.keys():
            if level == '.':
                key = v
            else:
                key = v.partition(level)[2]
            if key != '':
                res.append(key)
        return(res)
        
    def replace(self, tag, value):

        
        tag = tag.strip()
        if self.value.has_key(tag):
            self.value[tag] = value.strip()
        else:
            print ('key ' + tag.strip() + ' appended')
            

            
    def replace_in_file(self, ctlfile, newtag, newvalue):
        fido = open(ctlfile, 'r')
        value = ''
        tag = ''
        newlines = []
        flag = False
        for line in fido:
            line = line.strip()
            comment = ''
            if line.find('#')>-1:
                #comment = line[line.find('#'):]
                line = line[0:line.find('#')].strip()
            if len(line)==0:
                if len(value) > 0:
                    newlines.append(tag + ' = ' + value + 
                                    ' ' + comment + '\n')
                    value = ''
                    comment = ''
                elif len(comment)>0:
                    newlines.append(comment + '\n')
                    comment = ''
                continue
            old_line = line
            if len(value)> 0 and line[0].isalpha():
                if (tag == newtag):
 #                   print tag
                    newlines.append(tag + ' = ' + newvalue +
                                ' ' + comment + '\n')
                else:
#                    print tag
                    newlines.append(tag + ' = ' + value + 
                                ' ' + comment + '\n')
#                print tag + ' = '  + value + '\n'
                value = ''
                comment = ''
            if line.find('=') == -1: 
                if tag == newtag:
                    dum = line.strip().strip()
                else:
                    value  += ' ' + line.strip().strip()
                    value = value.strip()
#                    print value 
                continue
            tags = line.split('=')
            tag = tags[0].strip()
            value = tags[1].strip()
            if tag.lower() == newtag.strip().lower():
                value = newvalue
                flag = True

        # last line has not yet been written!
        if len(value) > 0:
            newlines.append(tag + ' = ' + value + 
                            ' ' + comment + '\n')
            

        if not flag:
            newlines.append(newtag + ' = ' + newvalue + '\n')
        fido.close()
        fidn = open(ctlfile, 'w')
        fidn.writelines(newlines)
        fidn.close()


    def write(self, ctlfile):
        order = ['file', 'file.in','file.out','gas','fw','rt','band','sp','out','kb']
        
        fid = open(ctlfile, 'w')
        for k,v in self.value.iteritems():
            fid.write(k + ' = ' + v + '\n')

        fid.close()


class read_table:

    def __init__(self, filename):
        self.table = np.recfromtxt(filename, skip_header=3,names=True)
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
        ac = self.table['AIRMASS']
        return(z,zb, p,t,ac)

    def calc_hfunction(self,p_surf=-1):
        z,zb, p,t,ac = self.get_atmosphere()
        if p_surf == -1:
            p_surf = p[-1]

        h = np.zeros(p.size)
        h[:-1] = -p[:-1] + (p[1:] - p[:-1])/np.log(p[1:]/p[:-1])
        h[1:] += p[1:] - (p[1:] - p[:-1])/np.log(p[1:]/p[:-1])
        h /= p_surf
        return(h)
        
    
    def get_retrieval_gasnames(self):
        return self.retgas


class calc_diagnostics(sfit4_ctl):

    def __init__(self):
        self.F_K = False
        self.F_SA = False
        self.F_SE = False
        self.ctl = sfit4_ctl()
        self.ctl.read('sfit4.ctl')
        
    def read_Kmatrix(self, filename):

        self.K_frac = np.genfromtxt(filename,skip_header=3)
        self.F_K = True
        
    def read_sainv_matrix(self, filename):
        self.sainv = np.genfromtxt(filename,skip_header=3)
        # if TP is used, construct the inverse SA matrix
#        self.sainv = np.linalg.inv(self.sa)
        self.F_SA = True
        
    def read_seinv_matrix(self, filename):
        self.seinv = np.genfromtxt(filename,skip_header=2)
        self.F_SE = True
        
    def calc_AVK(self):
        if self.F_K and self.F_SE and self.F_SA:
            KS = np.dot(self.K_frac.T,np.diag(self.seinv))
            KSK = np.dot(KS, self.K_frac)

            self.AK_frac = np.dot(np.linalg.inv(self.sainv + KSK), KSK)

        else:
            print ('read K, SA and SE matrix first')
            
                    
class Kout:
    # read K and Kb matrix. the keys are the names of the statevector entries the column resonds to.
    def __init__(self, filename):
    
        self.K_frac = np.genfromtxt(filename,skip_header=2,names=True)

    def get_keys(self):
        return(self.K_frac.dtype.names)

    def get_data(self, key):
        return(self.K_frac[key])

    def get_alldata(self, keyroot):
        keys = self.get_keys()
        data = np.zeros((0,self.K_frac[keys[0]].size))
        for kk in keys:
            if kk.find(keyroot) == -1:
                continue
            data=np.vstack((data,self.K_frac[kk]))

        return(data)


    
class avk:
    def __init__(self, filename, prfsfile):
    
        avk = rn.read_from_file(filename)
        l1 = avk.get_line()
#        import ipdb
#        ipdb.set_trace()
        if l1.find('SFIT4') > -1:
            self.AK_frac = np.genfromtxt(filename,skip_header=2)
        else:
            nmat = int(avk.get_line().split('=')[1])
            nrow = int(avk.get_line().split('=')[1])
            ncol = int(avk.get_line().split('=')[1])
            avk.skipline(1)
            self.AK_frac = np.array(avk.next(nrow*ncol))
            self.AK_frac = np.reshape(self.AK_frac,(nrow,ncol))
        self.direc = os.path.dirname(filename)
        self.prfsfile = prfsfile

    def renormalize(self):
        
#        import ipdb
#        ipdb.set_trace()
        ap = read_table(self.prfsfile)
        prf,z = ap.get_gas_vmr(ap.get_retrieval_gasnames()[0])
        print(prf.size)
        self.AK_vmr = np.dot(np.dot(np.diag(prf),self.AK_frac),np.diag(1/prf))
        prf,z = ap.get_gas_col(ap.get_retrieval_gasnames()[0])
        self.AK_col = np.dot(np.dot(np.diag(prf),self.AK_frac),np.diag(1/prf))
        self.z = z

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
        head1 = sumf.get_line().split()
        self.gas = []
        self.prf = []
        self.cell = []
        self.apriori = np.zeros(nr_retgas)
        self.retriev = np.zeros(nr_retgas)
        for nr in range(0,nr_retgas):
            int(sumf.next(1).pop(0))
            self.gas.extend(sumf.next(1))
            self.prf.extend(sumf.next(1))
            if head1.count('IFCELL') > 0:
                 self.cell.extend(sumf.next(1))
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
                sumf.skip_reminder_of_line()
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

            
        
class error(read_table):
    def __init__(self, dir, sbctl='sb.ctl', rprfs='rprfs.table'):
        direc = dir
        sb_ctl = sfit4_ctl()
        if not os.path.isfile(sbctl):
            self.flag = False
            return
        sb_ctl.read(sbctl)
        # check if sb.ctl and direc are formally consistent
        self.total_vmr = direc+'/'+sb_ctl.get_value('file.out.total.vmr')
        self.total_col = direc+'/'+sb_ctl.get_value('file.out.total')
        self.ran_vmr = direc+'/'+sb_ctl.get_value('file.out.srandom.vmr')
        self.sys_vmr = direc+'/'+sb_ctl.get_value('file.out.ssystematic.vmr')
        self.ran_col = direc+'/'+sb_ctl.get_value('file.out.srandom')
        self.sys_col = direc+'/'+sb_ctl.get_value('file.out.ssystematic')
        self.avk = direc+'/'+sb_ctl.get_value('file.out.avk')
        self.rprfs = direc+'/'+rprfs
        
        
        if os.path.exists(self.total_vmr) \
           and os.path.exists(self.total_col) \
           and os.path.exists(self.ran_vmr) \
           and os.path.exists(self.sys_vmr) \
           and os.path.exists(self.ran_col) \
           and os.path.exists(self.sys_col)\
           and os.path.exists(self.rprfs)\
           and os.path.exists(self.avk):
            self.flag = True
            read_table.__init__(self, self.rprfs)
        else:
            self.flag = False
#        self.shat = direc+'/'+sbctl.get_value('file.out.shat_matrix')

            

    def read_total_vmr(self):
        if self.flag:
            label, matrix = self.read_error_matrix(self.total_vmr)
            self.S_vmr_ran = matrix[0]
            self.S_vmr_sys = matrix[1]
            self.vmr_ran = np.sqrt(np.abs(np.diag(matrix[0])))
            self.vmr_sys = np.sqrt(np.abs(np.diag(matrix[1])))
            return(self.vmr_ran, self.vmr_sys)
        else:
            return(np.nan,np.nan)

    def read_total_pcol(self):
        if self.flag:
            label, matrix = self.read_error_matrix(self.total_col)
            self.S_col_ran = matrix[0]
            self.S_col_sys = matrix[1]
            self.col_ran = np.sqrt(np.abs(np.diag(matrix[0])))
            self.col_sys = np.sqrt(np.abs(np.diag(matrix[1])))
            return(self.col_ran, self.col_sys)
        else:
            return(np.nan,np.nan)

    def read_total_col(self):
        if self.flag:
            label, matrix = self.read_error_matrix(self.total_col)
            self.S_col_ran = matrix[0]
            self.S_col_sys = matrix[1]
            ll = np.ones((matrix[0].shape[0],1))
            self.col_ran = np.sqrt(np.abs(np.dot(ll.T,np.dot(self.S_col_ran,ll))))
            self.col_sys = np.sqrt(np.abs(np.dot(ll.T,np.dot(self.S_col_sys,ll))))
            return(self.col_ran, self.col_sys)
        else:
            return(np.nan,np.nan)


    def read_matrix_random_vmr(self):
        label, matrix = self.read_error_matrix(self.ran_vmr)
        return(label,matrix)

    def read_matrix_system_vmr(self):
        label, matrix = self.read_error_matrix(self.sys_vmr)
        return(label,matrix)

    def read_matrix_random_pcol(self):
        try:
            label, matrix = self.read_error_matrix(self.ran_col)
            return(label,matrix)
        except:
            (-1,-1)

    def read_matrix_system_pcol(self):
        label, matrix = self.read_error_matrix(self.sys_col)
        return(label,matrix)

    def read_error_matrix(self, filename):
        if not self.flag:
            return(np.nan,np.nan)
        em = rn.read_from_file(filename)
        em.get_line()
        nr_mat = int(em.get_line().partition('=')[2])
        nr_rows = int(em.get_line().partition('=')[2])
        nr_cols = int(em.get_line().partition('=')[2])
        matrix = np.ndarray((nr_mat,nr_rows,nr_cols))
        label = []
        for nmat in range(0,nr_mat):
            label.append(em.get_line())
            mat = em.next(nr_rows*nr_cols)
            matrix[nmat] = np.reshape(mat,(nr_cols, nr_rows))

        return label, matrix

    

    
class pbp:
    def __init__(self, filename):
        pbpf = rn.read_from_file(filename)
        self.header = pbpf.get_line()
        nr_mw = int(pbpf.next(1).pop(0))
        self.nr_mw = nr_mw
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

        
        sum = summary(direc+'/summary')

        self.gas = []
        self.band = []
        self.scan = []
        self.iteration = []
        self.clc = []
        self.nu = []
        files = []
        for fn in sum.gas:
            files.extend(glob.glob(direc + '/spc.' + fn + '*'))
        files.extend(glob.glob(direc + '/spc.all*'))
        files.extend(glob.glob(direc + '/spc.REST*'))
        if os.path.exists(direc+'/spc.CON.01.01.final'):
            files.extend(glob.glob(direc + '/spc.CON*'))
        if os.path.exists(direc+'/spc.MTCKD.01.01.final'):
            files.extend(glob.glob(direc + '/spc.MTCKD*'))
        # Order gas files by target, interfering, ALL, REST 
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
            self.band.append(int(headerline[3]))
            self.scan.append(int(headerline[5]))
            self.iteration.append(int(headerline[7]))
            self.clc.append(clc)
            self.nu.append(nu)

            
            del ascf 


class statevec:
    def __init__(self, filename):

        stvf = rn.read_from_file(filename)
        
        stvf.skipline()
        self.nr_layer = stvf.next(1).pop(0)
        stvf.next(1).pop(0)
        stvf.next(1).pop(0)
        self.tretflag = stvf.next(1).pop(0)
        stvf.next(1).pop(0)
        stvf.next(1).pop(0)
        stvf.skipline()
        self.Z = stvf.next(self.nr_layer)
        stvf.skipline()
        self.P = stvf.next(self.nr_layer)
        stvf.skipline()
        self.T = stvf.next(self.nr_layer)
        if self.tretflag == 'T':
            stvf.skipline()
            self.Tret = stvf.next(self.nr_layer)
        
        nr_gas = stvf.next(1).pop(0)
        self.ap_col = []
        self.ap_vmr = []
        self.rt_col = []
        self.rt_vmr = []
        self.gas = []
        for gas in range(0,nr_gas):
            stvf.skipline()
            self.gas.append(stvf.next(1).pop(0))
            self.ap_col.extend(stvf.next(1))
            self.ap_vmr.append(stvf.next(self.nr_layer))
            stvf.skipline()
            stvf.skipline()
            self.rt_col.extend(stvf.next(1))
            self.rt_vmr.append(stvf.next(self.nr_layer))

        nr_aux = stvf.next(1).pop(0)
        self.aux = []
        self.ap_aux = []
        self.rt_aux = []
        for aux in range(0,nr_aux):
            self.aux.append(stvf.next(1).pop(0))
        for aux in range(0,nr_aux):
            self.ap_aux.append(stvf.next(1).pop(0))
        for aux in range(0,nr_aux):
            self.rt_aux.append(stvf.next(1).pop(0))
        del stvf
