import numpy as np
import read_from_file as rn
import os, string
from read_result_sfit4 import statevec

def create_station_layer(z, st_file):
    # create the sfit4 station layer profile from altitudes Z

    if z[0] < z[1]:
        z = z[::-1]

    z_lay = np.zeros((len(z),5))
    z_lay[:,0] = np.array(range(1,len(z)+1))
    z_lay[:,1] = z

    z_lay[0:-1,2] = np.abs(np.diff(z))
    z_lay[-1,2] = 0
    
    z_lay[0:-2,3] = z_lay[0:-2,2] / z_lay[1:-1,2]
    z_lay[-2:,3] = 0

    z_lay[0:-1,4] = 0.5 * (z_lay[0:-1,1] + z_lay[1:,1])


#    z_lay = np.flipud(z_lay)

    with open(st_file, 'w') as fid:
        fid.write('created by sfit4_setup.py:create_station_layer\n')
        fid.write('     %d\n'%(len(z)))
        fid.write('    i     level     thick    growth    midpnt\n')
        
        np.savetxt(fid, z_lay, fmt = '%5d %12.4f %12.4f %12.4f %12.4f')


class reference_prf:
    def __init__(self):
        self.gas_default = ['H2O',     'CO2',     'O3',     'N2O',     'CO',     
                            'CH4',     'O2',      'NO',     'SO2',     'NO2',      
                            'NH3',     'HNO3',    'OH',     'HF',      'HCL',     
                            'HBR',     'HI',      'CLO',    'OCS',     'CH2O',     
                            'HOCL',    'HO2',     'H2O2',   'HONO',    'HO2NO2',  
                            'N2O5',    'CLONO2',  'HCN',    'CH3F',    'CH3CL',    
                            'CF4',     'CCL2F2',  'CCL3F',  'CH3CCL3', 'CCL4',    
                            'COF2',    'COCLF',   'C2H6',   'C2H4',    'C2H2',     
                            'N2',      'CHF2CL',  'COCL2',  'CH3BR',   'CH3I',    
                            'HCOOH',   'H2S',     'CHCL2F', 'O2CIA',   'SF6',      
                            'NF3',     'OTHER',   'OTHER',  'OTHER',   'OTHER',   
                            'OTHER',   'OTHER',   'OCLO',   'F134A',   'C3H8',     
                            'F142B',   'CFC113',  'F141B',  'CH3OH',   'CH3CNPL', 
                            'C2H6PL',  'PAN',     'CH3CHO' ,'CH3CN',   'CHF3',    
                            'CH3COOH', 'C5H8',    'MVK',    'MACR',    'C3H6',    
                            'C4H8',    'OTHER',   'OTHER',  'OTHER',   'OTHER',    
                            'OTHER',   'OTHER',   'OTHER',  'OTHER',   'OTHER',   
                            'OTHER',   'OTHER',   'OTHER',  'OTHER',   'OTHER',    
                            'OTHER',   'OTHER',   'OTHER',  'OTHER',   'OTHER',   
                            'OTHER',   'OTHER',   'OTHER',  'OTHER']
    
    def split_reference_prf(self, reffile, refdir):

        self.read_reference_prf(reffile)
        self.write_reference_split(refdir)

    def write_reference_split(self, refdir):
        
        for n in range(1,self.nr_gas):
            sname = '%02d_%s'%(self.gas_nr[n-1],self.gasname[n-1])
            spec_dir = os.path.join(refdir,sname)
            os.path.isdir(refdir) or os.makedirs(refdir)
            np.savetxt(spec_dir,np.vstack((self.z,self.vmr[n-1,:])).transpose())

    def read_reference_split(self,refdir,z):
        # Reads numbered and named VMRs from directory refdir and interpolated the values 
        # to a given altitude grid z

        files = os.listdir(refdir)
        files.sort()

        self.z = z
        self.nr_gas = len(files)
        self.nr_layers = z.size
        self.gas=np.zeros(self.nr_gas)
        self.gasname = []
        self.notes = []
        self.vmr = np.zeros((self.nr_gas, self.nr_layers))

        for file in files:
            if os.path.isdir(file):
                continue
            t = np.loadtxt(refdir+'/'+file)
            nr_gas = int(file[0:2])
            self.gas[nr_gas-1] = nr_gas
            self.gasname.append(file[3:].rstrip())
            self.notes.append('created by sfit4_setup.py')            
            if not np.all(np.diff(t[:,0]) > 0):
                t = np.flipud(t)
            self.vmr[nr_gas-1,:] = np.interp(z, t[:,0], t[:,1])

    def insert_pt(self, zpt):
        # interpolates the in columns 2 and 3 of zpt given pressure and temperature
        # to the grid used here

        print(self.t)
        if not np.all(np.diff(zpt[0:10,0]) > 0):
            zpt = np.flipud(zpt)
            print(zpt)
        ind = np.where((self.z>np.min(zpt[:,0])) & (self.z<np.max(zpt[:,0])))[0]
        self.t[ind] = np.interp(self.z[ind], zpt[:,0], zpt[:,2])
        self.p[ind] = np.exp(np.interp(self.z[ind], zpt[:,0], np.log(zpt[:,1])))

        print (self.t)

    def insert_vmr_from_file(self, prffile, gas_nr, gas_name, note):
        # reads the two column profile (z,vmr) from prffile, interpolates 
        # it to the altitude grid contained in self.z and inserts gas_nr, gas_name, notes and vmr in self

        t = np.loadtxt(prffile)
        vmr = np.interp(self.z[::-1],t[::-1,0], t[::-1,1])
        self.vmr[gas_nr-1,:] = vmr[::-1]
        self.gasname[gas_nr-1]=gas_name
        self.notes[gas_nr-1] = note

    def insert_vmr_from_statevec(self, stvfile):
        # reads the statevec file (created by sfit4) and
        # inserts the VMR into the reference profile
        
        stv = statevec(stvfile)
        for gasname, vmr in zip(stv.gas, stv.rt_vmr):
            vmr_n = np.array([stv.Z, stv.rt_vmr[0]]).T
            gas_nr = self.gasname.index(gasname)+1
            self.insert_vmr(vmr_n, gas_nr, gasname, 'inserted from statevec')
        
    def insert_vmr(self, prf, gas_nr, gas_name, note):
        # reads the two column profile (z,vmr) from prf, interpolates 
        # it to the altitude grid contained in self.z and inserts gas_nr, gas_name, notes and vmr in self

        
        vmr = np.interp(self.z[::-1],prf[:,0], prf[:,1],left = -1.0, right=-1.0)
        ind = np.where(vmr[::-1] == -1)[0]
        vmr2 = np.interp(self.z[ind], self.z[::-1], self.vmr[gas_nr-1,::-1])
        self.vmr[gas_nr-1,:] = vmr[::-1]
        self.vmr[gas_nr-1,ind] = vmr2
        self.gasname[gas_nr-1]=gas_name
        self.notes[gas_nr-1] = note
        

#     def insert_statevec(self, stvfile):
#         x = stv.stv(stvfile)
        
#         for n in range(0,len(x.gas)):
#             ind = self.gasname.index(x.gas[n])
#             vmr = np.interp(self.z[::-1],np.array(x.Z[::-1]), np.array(x.rt_vmr[n][::-1]))
#             self.vmr[ind,:] = vmr[::-1]

    def read_reference_prf(self, reffile, nopt=False):
        reff = rn.read_from_file(reffile)
        tmp_nr = reff.next(1).pop(0)
        nr_layers = reff.next(1).pop(0)
        self.nr_layers = nr_layers
        nr_gas = reff.next(1).pop(0)
        self.nr_gas = nr_gas
        reff.skipline(1)
        self.z = np.array(reff.next(nr_layers))
        #        header = reff.next(1)
        if not nopt:
            reff.skipline(1)
            self.p = np.array(reff.next(nr_layers))
            reff.skipline(1)
            self.t = np.array(reff.next(nr_layers))
        
        self.gas_nr = np.zeros(nr_gas)
        self.gasname = []
        self.notes =[]
        self.vmr = np.zeros((nr_gas, nr_layers))
        
        for n in range(0,nr_gas):
#            import ipdb
#            ipdb.set_trace()
            self.gas_nr[n] = reff.next(1).pop(0)
            self.gasname.extend(reff.next(1))
            ll = reff.get_line(only_remainder=True)
            print (self.gasname[-1], ll)
            self.notes.append(ll)#reff.get_line())
#            reff.skip_reminder_of_line()
            self.vmr[n,0:nr_layers] = np.array(reff.next(nr_layers))
#            reff.skip_reminder_of_line()

        del reff
        
    def get_gas_from_refprofile(self, gasname, z=np.array([])):
        if self.gasname.count == 0:
            print ('Gas '+gansmae+' not in reference file')
        ind = self.gasname.index(gasname)
        vmr = self.vmr[ind]
        if z.size > 0:
            vmr = np.interp(z, np.flipud(self.z), np.flipud(vmr))
        return(list(vmr))



    def write_reference_prf(self, prffile, nopt=False):
        
        fid = open(prffile, 'w')
        line = '%5d%6d%6d\n' % (1,self.nr_layers,self.nr_gas)
        fid.write(line)
        line = '    ALTITUDE\n'
        fid.write(line)
        for n in range(0,self.nr_layers,5):
            line = ''.join(map (lambda x:'%11.3e,'%x, self.z[n:np.min((n+5,self.nr_layers))]))
            fid.write(' '+line+'\n')
        if not nopt:
            line = '    PRESSURE\n'
            fid.write(line)
            for n in range(0,self.nr_layers,5):
                line = ''.join(map (lambda x:'%11.3e,'%x, self.p[n:np.min((n+5,self.nr_layers))]))
                fid.write(' '+line+'\n')
            line = '    TEMPERATURE\n'
            fid.write(line)
            for n in range(0,self.nr_layers,5):
                line = ''.join(map (lambda x:'%11.3e,'%x, self.t[n:np.min((n+5,self.nr_layers))]))
                fid.write(' '+line+'\n')

        for gas in range(0,self.nr_gas):
            line = '%5d%8s %s' %(self.gas_nr[gas],self.gasname[gas],self.notes[gas])
            fid.write(line+'\n')
            for n in range(0,self.nr_layers,5):
                line = ''.join(map (lambda x:'%11.3e,'%x, 
                                        self.vmr[gas,n:np.min((n+5,self.nr_layers))]))
                fid.write(' '+line+'\n')


        fid.close()

    def create_ref_from_WACCM(self, direc,default=None):
        # inserts WACCM output in reference. gasnames musst be defined already
        # interpolates to the altitude grid already defined in the class

        if (default != None):
            defref = reference_prf()
            defref.read_reference_prf(default)
        else:
            defref = -1
            
            
        self.nr_gas = len(self.gas_default)
        self.gas_nr = np.zeros(self.nr_gas)
        self.gasname = []
        self.notes = []
        alts, vmr, note = self.load_waccmfile('%s/%s.txt'%(direc,'T'))
        self.nr_layers = len(alts)
        self.t = np.array(vmr)
        self.z = np.array(alts)
        alts, vmr, note = self.load_waccmfile('%s/%s.txt'%(direc,'P'))
        self.p = np.array(vmr)
        self.vmr = np.zeros((self.nr_gas, self.nr_layers))
        for nr in range(0,self.nr_gas):
            waccm_file = '%s/%s.txt'%(direc,self.gas_default[nr])
            self.gas_nr[nr] = nr + 1
            if self.gas_default[nr] == 'CH2O':
                self.gas_default[nr] = 'H2CO'
            self.gasname.append(self.gas_default[nr])
            self.notes.append('created by sfit4_setup')
            if os.path.exists(waccm_file):
                print (waccm_file)
                alts, vmr, note = self.load_waccmfile(waccm_file)
                self.vmr[nr,0:self.nr_layers] = vmr
                self.notes[-1] = note
            else:
                if (defref != -1):
                    self.vmr[nr,0:self.nr_layers] = defref.get_gas_from_refprofile(self.gas_default[nr], z=self.z)
                    self.notes[-1] = 'copied from default.ref'
                else:
                    self.notes[-1] = 'create by sfit4_setup'

    def load_waccmfile(self, filename):
        # loads the second block formatted for reference.prf from the respective file
        wfile = rn.read_from_file(filename)
        wfile.skipline()
        nr = wfile.next(1).pop()
        wfile.next(nr*5)
        nr = wfile.next(1).pop()
        wfile.skipline()
        alt = np.array(wfile.next(nr))
        line = wfile.get_line().strip()
        gas,tmp,note = line.partition(' ')
        vmr = wfile.next(nr)
        return(alt, vmr, note)


class sfit4_ctl:

    def __init(self):
        pass


    def read_ctl_file(self, ctlfile):

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
        if tag in self.value:
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
        if tag in self.value:
            self.value[tag] = value.strip()
        else:
            print ('key ' + tag.strip() + ' not found')

    def replace_in_file(self, ctlfile, newtag, newvalue):
        newvalue = str(newvalue)
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
        fid = open(ctlfile, 'w')
        for k,v in self.value.items():
            fid.write(k + ' = ' + v + '\n')

        fid.close()
