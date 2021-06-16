#LOAD2160   Load ozone sonde in NASA Ames Format.
#   LOAD2160(NAME) loads the sonde with the filename given in NAME and
#   returns the whole dataset. Sonde must be in NASA Ames Format 2160.
#
#   [V,A,X2,DATE]=LOAD2160(NAME) returns the data in V, auxiliary
#   variables in A, the station name in X2 and the date in DATE.

#	BMSinnhuber, 16.05.95
#                    07.08.95
# modified for python
#       Mathias Palm 2014, 2020

# start with 
# execfile('/home/mathias/load2160.py')
# vals, date, names = load2160('ny050301.b10')
# names contains the dependent variables, vals the independent variable in
# column 1 and the others in the rest.
# date is in datenums (can be converted to a date by dates.num2date

import numpy as np
import sys, os, re
import matplotlib.dates as dates
from tables import open_file, Float32Atom
class sonde():

    def __init__(self, direc, prefix):
        self.basedir = direc
        self.filename_prefix = prefix

        g = re.compile('ny*.b*',re.I)
        self.sondefiles = filter(g.search,os.listdir(direc))

    def convert_sonde_h5(self):

        with open_file('o3sondes.h5','w') as h5file:
            Time  = h5file.create_earray("/", 'dnum', Float32Atom(),([0]), title="Time of measurement", expectedrows=366)
            z = h5file.create_earray("/", 'Z', Float32Atom(),(10000,0), title="Altitude", expectedrows=366)
            T = h5file.create_earray("/", 'T', Float32Atom(),(10000,0), title="Temperature", expectedrows=366)
            o3ppmv = h5file.create_earray("/", 'O3', Float32Atom(),(10000,0), title="O3 PPMV", expectedrows=366)

            for sondefile in self.sondefiles:
                try:
                    vals, mdate, header = self.load2160(sondefile)
                    print(sondefile)
                except:
                    continue

                nr_entry = vals.shape[0]
                Time.append(np.reshape(mdate,(1)))
                nr_entry = vals.shape[0]
                o3 = np.nan*np.ones(10000)
                o3[:nr_entry] = vals[:,5]/vals[:,1]*10 # O3 ppat in mPa, P in hPa
                o3 = np.reshape(o3, (10000,1))
                o3ppmv.append(o3)
                alt = np.nan*np.ones(10000)
                alt[:nr_entry] = vals[:,2]
                alt = np.reshape(alt, (10000,1))
                z.append(alt)
                temp = np.nan*np.ones(10000)
                temp[:nr_entry] = vals[:,3]
                temp = np.reshape(temp, (10000,1))
                T.append(temp)
                
                
    def load2160(self, name):


        #    import ipdb
        #    ipdb.set_trace()
        fid = open(name)
        nlhead = fid.readline()
        ffi = fid.readline() # File format
        ffi = ffi.split()
        ffi = int(ffi[1])
        if ffi != 2160:
            # V = -1
            # A = -1
            # ASTRING = -1
            # X2 = -1
            # DATE = -1
            mdate = -1
            vals = -1
            vname = -1
            fid.close()
            print (name + ' not valid')
            return(vals, mdate, vname)
    
        oname = fid.readline() # Supervisor
        org = fid.readline()   # Organsiation
        sname = fid.readline() # Device
        mname = fid.readline() # Mission name
        f = fid.readline().split()
        ivol = int(f[0]) # No. files
        nvol = int(f[1]) # dito
        f = fid.readline()
        dd = f.split() # Measurement date
        mdate = dates.date2num(dates.datetime.date(int(dd[0]), int(dd[1]), int(dd[2])))
        #    rdate = dates.date2num(dates.datetime.date(int(dd[3]), int(dd[4]), int(dd[5])))
        f = fid.readline()
        dx1 = int(f) # Spacing between values of
        # independent variable (0=varying)
        f = fid.readline()
        lenx2 = int(f) # Length independent variable
        xname = [] # Name independent variable
        l = fid.readline();
        xname.append(l);
        l = fid.readline();
        xname.append(l);
        
        f = fid.readline();
        nv = int(f) # No. dependent variables
        f = fid.readline().split()
        for k in range(0,nv):
            vscal = float(f[k]); # Scale factors
        f = fid.readline().split();
        vmiss = []
        for k in range(0,nv):
            vmiss.append(float(f[k])); # Missing values
        vname = []       # Names of dependent variables
        for n in range(0,nv):
            l = fid.readline()
            vname.append(l)

        f = fid.readline();
        nauxv = int(f) # No. auxiliary variables
        f = fid.readline();
        nauxc = int(f); # No. auxiliary variables being strings
        f = fid.readline().split();
        ascal = []
        while len(f) < nauxv-nauxc:
            f.extend(fid.readline().split())
        for n in range(0, nauxv-nauxc):
            ascal.append(float(f[n])) # Scale factors
        f = fid.readline().split()
        amiss = []
        while len(f) < nauxv-nauxc:
            f.extend(fid.readline().split())
        for n in range(0, nauxv-nauxc):
            amiss.append(float(f[n])) # miss factors
        f = fid.readline().split();
        lena = []
        for n in range(0,nauxv-nauxc):
            lena.append(-1)
        for n in range(nauxv-nauxc, nauxv):
            lena.append(int(f[n-(nauxv-nauxc)]))
        for n in range(nauxv-nauxc, nauxv):   # Missing values for strings
            l = fid.readline();
        aname = []
        for a in range(0,nauxv):
            l = fid.readline();
            aname.append(l);


        f = fid.readline();
        nscoml = int(f); # Length special comment
        if nscoml == '':
            nscoml = 0;
        else:
            scom = [] # Special comment
            for k in range(0,nscoml):
                l = fid.readline();
                scom.append(l);
                print (l)
        f = fid.readline();
        nncoml = int(f) # Length comment
        if nncoml == '':
            nncoml = 0
    
        ncom = []
        for k in range(0,nncoml):
            l = fid.readline();
            ncom.append(l);
    
        l = fid.readline();
        x2 =  l;  # Independent variable 1 (Station name)
        tmpNX = fid.readline().split()# No. values indepedent variable 2
        # (pressure)
        while len(tmpNX) < nauxv-nauxc:
            tmpNX.extend(fid.readline().split())

        nx1 = int(tmpNX[0]);
    
        A = []

        for k in range(0,nauxv-nauxc-1):
            A.append(tmpNX[k])


        # Depending on who did the conversion, this line is different
        if x2.find('Ny-Aalesund') != -1:
            tim = [A[6]]
            mdate = mdate + float(tim[0])/24.0
        elif x2.find('Paramaribo') != -1:
            tim = A[1]
            mdate = mdate + int(tim[0])/24.0
        else:
            mdate = mdate + float(A[1])/24.0

        ASTRING = []
        for a in range(nauxv-nauxc,nauxv):
            l = fid.readline();
            ASTRING.append(l);


        vals = np.zeros((nx1,nv+1))
        for n in range(0,nx1):
            l = fid.readline().split()
            vals[n,:] = np.array(l)

        fid.close()

        return(vals, mdate, vname)
