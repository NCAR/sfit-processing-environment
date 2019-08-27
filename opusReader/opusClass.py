#----------------------------------------------------------------------------------------
# Name:
#        opusClass.py
#
# Purpose:
#       Read OPUS format
#
# Notes:
#       1) Class developed mainly by Wolfgang Stremme, UNAM, Mexico 
#
# Version History:
#       Modified, July, 2019  Ivan Ortega (iortega@ucar.edu)
#
#----------------------------------------------------------------------------------------

import numpy as np
import get_param_idx 
import struct
import matplotlib.pyplot as plt
import os
import shutil
import sys
import fileinput
import platform
from datetime import datetime, date, time, timedelta
import time
import urllib2
import pickle
import copy
import pyximport; pyximport.install()
#import ifgtoolsc
from scipy.integrate import simps

from sys import platform as _platform
global operatingsystem
operatingsystem=_platform


class readOPUS:

    def __init__(self, fname):
        
        self.filename = fname
        self.name     = os.path.basename(fname)
        self.filter   = self.name[0:2]

        f=open(self.filename,'rb')
        f.seek(0)
        
        field1=np.fromfile(f,dtype='int32',count=1)
        field2=np.fromfile(f,dtype='float64',count=1)
        self.opusversion=field2[0]
        field3=np.fromfile(f,dtype='int32',count=1)
        ipdir=field3[0]
        self.ipdir=ipdir
        field4=np.fromfile(f,dtype='int32',count=1)
        mnbl=field4[0]
        self.mnbl=mnbl
        field5=np.fromfile(f,dtype='int32',count=1)
        nbl=field5[0]
        self.nbl=nbl
        
        blocktyparr=[]
        blocklenarr=[]
        blockpntarr=[]
        for i in range(nbl):
            field6=np.fromfile(f,dtype='int32',count=1)
            blocktyparr.append(field6[0])
            field7=np.fromfile(f,dtype='int32',count=1)
            blocklenarr.append(field7[0])
            field8=np.fromfile(f,dtype='uint32',count=1)
            blockpntarr.append(field8[0])
        f.close()
        
        self.blocktyparr=blocktyparr
        self.blocklenarr=blocklenarr
        self.blockpntarr=blockpntarr
        
        self.readdir()

        self.spcFlg = False
        self.optFlg = False
        self.fftFlg = False
        self.acqFlg = False
        self.opuFlg = False
        self.insFlg = False

    def readdir(self):
        
        blockidarr=[]
        f=open(self.filename,'rb')

        for idx in range(self.nbl):
           
            flag='DBL'
            ipoint=self.blockpntarr[idx]
            nbits=self.blocklenarr[idx]*4
            
            f.seek(ipoint)
            data=f.read(nbits)
            
            if idx==0: flag='DIR'
            if data[0:3] == 'APT': flag= 'OPT'
            if data[0:3] == 'APF': flag= 'FFT'
            if data[0:3] == 'AQM': flag= 'ACQ'
            if data[0:3] == 'BLD': flag= 'OPU'
            if data[0:3] == 'DPF': flag= 'DBS'
            if data[0:3] == 'HFL': flag= 'INS'
            blockidarr.append(flag)

        index1=blockidarr.index('DBS')
        xunit= get_param_idx.get_param_idx(f,index1,'DXU')
        
        if xunit == 'PN':     
            blockidarr[index1]= blockidarr[index1]+'_ifg'
            index1=blockidarr.index('DBL')
            blockidarr[index1]= blockidarr[index1]+'_ifg'
        
        try:
            index1=blockidarr.index('DBS')
        except ValueError:
            print 'EXCEPTION #1 readdir()'
            
        xunit= get_param_idx.get_param_idx(f,index1,'DXU')
        if xunit == 'PN':
            self.doublesided='true'
            blockidarr[index1]= blockidarr[index1]+'_ifg2'
                   
        try:
            index1=blockidarr.index('DBS')
        except ValueError:
            print 'EXCEPTION #2 readdir()'
            
        xunit= get_param_idx.get_param_idx(f,index1,'DXU')
        if xunit == 'PN':
            self.doublesided='true'
            blockidarr[index1]= blockidarr[index1]+'_ifg2'
                          
        try:
            index1=blockidarr.index('DBS')
            xunit= get_param_idx.get_param_idx(f,index1,'DXU')
            if xunit == 'WN':
                blockidarr[index1]= blockidarr[index1]+'_spc2'
            else:
                blockidarr[index1]= blockidarr[index1]+'_dbs'
        except ValueError:
            print 'EXCEPTION #3 readdir()'

        try:
            index1=blockidarr.index('DBS')
            xunit= get_param_idx.get_param_idx(f,index1,'DXU')
            if xunit == 'WN':
                blockidarr[index1]= blockidarr[index1]+'_spc'
            else:
                if xunit == 'PN':
                    print xunit
                else:
                    blockidarr[index1]= blockidarr[index1]+'_dbs'
        except ValueError:
            print 'EXCEPTION #4 readdir()'

        try:
            index1=blockidarr.index('DBS_spc2')
            blockidarr[index1]= 'DBS_spc'
        except ValueError:
            print 'EXCEPTION #5 readdir()'

        f.close 
        self.blockidarr=blockidarr

    def readOPT(self, verbFlg=False):

        self.opt = {}

        optParms = ['APT','BMS','CHN','DTC','HPF', 'LPF', 'OPF', 'PGN', 'RCH', 'RDX', 'SRC', 'VEL', 'SON']

        idx=self.blockidarr.index('OPT')
        ipoint=self.blockpntarr[idx]
        f=open(self.filename,'rb')

        for par in optParms:

            try:

                self.opt.setdefault(par,[]).append(get_param_idx.get_param_idx(f,idx,par))

            except Exception as errmsg:
                print errmsg
                continue

        f.close()

        if verbFlg:

            for par in optParms:
                print par, self.opt[par][0] 

        self.optFlg = True
    
        
    def readFFT(self, verbFlg=False):

        self.fft  ={}

        optParms = ['APF','HFQ','LFQ','NLI','PHR', 'PHZ', 'SPZ', 'ZFF']

        idx=self.blockidarr.index('FFT')
        ipoint=self.blockpntarr[idx]
        f=open(self.filename,'rb')

        for par in optParms:

            try:

                self.fft.setdefault(par,[]).append(get_param_idx.get_param_idx(f,idx,par))

            except Exception as errmsg:
                print errmsg
                continue   

        f.close()

        if verbFlg: 

            for par in optParms:
                print par, self.fft[par][0] 

        self.fftFlg = True
        
        
    def readACQ(self, verbFlg=False):

        self.acq = {}

        optParms = ['AQM','COR','DEL','DLY','HFW', 'LFW', 'NSS', 'PLF', 'RES', 'RGN', 'TDL', 'SGN', 'SG2', 'RG2']

        idx=self.blockidarr.index('ACQ')
        ipoint=self.blockpntarr[idx]
        f=open(self.filename,'rb')

        for par in optParms:

            try:

                self.acq.setdefault(par,[]).append(get_param_idx.get_param_idx(f,idx,par))

            except Exception as errmsg:
                print errmsg
                continue   

        f.close()

        if verbFlg: 

            for par in optParms:
                print par, self.acq[par][0] 

        self.acqFlg = True


    def readOPU(self, verbFlg=False):

        self.opu = {}

        optParms = ['BLD','CPY','DPM','EXP','LCT', 'SFM', 'SNM', 'XPP', 'IST']

        idx=self.blockidarr.index('OPU')
        ipoint=self.blockpntarr[idx]
        f=open(self.filename,'rb')

        for par in optParms:

            try:

                self.opu.setdefault(par,[]).append(get_param_idx.get_param_idx(f,idx,par))

            except Exception as errmsg:
                print errmsg
                continue    
        f.close()
        
        if verbFlg:
            for par in optParms:
                print par, self.opu[par][0] 

        self.opuFlg = True

        
    def readINS(self, verbFlg=False):

        self.ins = {}

        optParms = ['HFL','LFL','LWN','ABP','ASG', 'ARG', 'ASS', 'GFW', 'GBW', 'BFW', 'BBW', 'PKA', 'PKL', 'PRA', 'PRL', 'P2A', 'P2L',
                    'P2R', 'P2K', 'DAQ', 'AG2', 'HUM', 'SSM', 'RSN', 'SRT', 'DUR', 'TSC', 'MVD', 'AN1', 'AN2', 'SRN', 'INS', 'FOC', 'RDY', 'ARS']

        #self.readOPT()
        idx=self.blockidarr.index('INS')
        ipoint=self.blockpntarr[idx]
        f=open(self.filename,'rb')
        f.seek(ipoint)

        for par in optParms:

            try:

                self.ins.setdefault(par,[]).append(get_param_idx.get_param_idx(f,idx,par))

            except Exception as errmsg:
                print errmsg
                continue    

        f.close()

        if verbFlg:
            for par in optParms:
                print par, self.ins[par][0]

        if self.optFlg:
            try:
                self.FOV=float(self.opt['APT'].split()[0])/float(self.ins['FOC'])
                self.SEMIFOV=self.FOV/2.0

            except ValueError:
                print 'Error calculating FOV)'

        self.insFlg = True


    def readspec(self, verbFlg=False):

        self.spc = {}

        optParms = ['DPF','NPT','NSN','TPX','FXV', 'LXV', 'CSF', 'MXY', 'MNY', 'DXU', 'DAT', 'TIM']


        idx=self.blockidarr.index('DBS_spc')
        ipoint=self.blockpntarr[idx]
        f=open(self.filename,'rb')

        for par in optParms:

            try:

                self.spc.setdefault(par,[]).append(get_param_idx.get_param_idx(f,idx,par))

            except Exception as errmsg:
                print errmsg
                continue    

        f.close()

        for k in self.spc:
            
            self.spc[k] = self.spc[k][0]

            if verbFlg:
                print k, self.spc[k]
        
        dummy_v = self.spc['FXV']   
        self.ud_flag = 0
        
        if self.spc['FXV']  > self.spc['LXV']:
            self.spc['FXV'] = self.spc['LXV']
            self.spc['LXV'] = dummy_v
            self.ud_flag = 1

        
    def readspec2(self):
        idx=self.blockidarr.index('DBS_spc2')
        ipoint=self.blockpntarr[idx]
        f=open(self.filename,'rb')

        self.spc2_DPF = get_param_idx.get_param_idx(f,idx,'DPF')
        self.spc2_NPT = get_param_idx.get_param_idx(f,idx,'NPT')
        self.spc2_NSN = get_param_idx.get_param_idx(f,idx,'NSN')
        self.spc2_TPX = get_param_idx.get_param_idx(f,idx,'TPX')
        self.spc2_FXV = get_param_idx.get_param_idx(f,idx,'FXV')
        self.spc2_LXV = get_param_idx.get_param_idx(f,idx,'LXV')
        self.spc2_CSF = get_param_idx.get_param_idx(f,idx,'CSF')
        self.spc2_MXY = get_param_idx.get_param_idx(f,idx,'MXY')
        self.spc2_MNY = get_param_idx.get_param_idx(f,idx,'MNY')
        self.spc2_DXU = get_param_idx.get_param_idx(f,idx,'DXU')
        self.spc2_DAT = get_param_idx.get_param_idx(f,idx,'DAT')
        self.spc2_TIM = get_param_idx.get_param_idx(f,idx,'TIM')
    
        f.close()
       
    def readdbs(self):
        idx=self.blockidarr.index('DBS_dbs')
        ipoint=self.blockpntarr[idx]
        f=open(self.filename,'rb')

        self.dbs_DPF = get_param_idx.get_param_idx(f,idx,'DPF')
        self.dbs_NPT = get_param_idx.get_param_idx(f,idx,'NPT')
        self.dbs_NSN = get_param_idx.get_param_idx(f,idx,'NSN')
        self.dbs_TPX = get_param_idx.get_param_idx(f,idx,'TPX')
        self.dbs_FXV = get_param_idx.get_param_idx(f,idx,'FXV')
        self.dbs_LXV = get_param_idx.get_param_idx(f,idx,'LXV')
        self.dbs_CSF = get_param_idx.get_param_idx(f,idx,'CSF')
        self.dbs_MXY = get_param_idx.get_param_idx(f,idx,'MXY')
        self.dbs_MNY = get_param_idx.get_param_idx(f,idx,'MNY')
        self.dbs_DXU = get_param_idx.get_param_idx(f,idx,'DXU')
        self.dbs_DAT = get_param_idx.get_param_idx(f,idx,'DAT')
        self.dbs_TIM = get_param_idx.get_param_idx(f,idx,'TIM')

        f.close()

    def readifg(self):
        idxdbl=self.blockidarr.index('DBL_ifg')
        idx=self.blockidarr.index('DBS_ifg')
        ipoint=self.blockpntarr[idx]
        f=open(self.filename,'rb')

        self.ifg_DPF = get_param_idx.get_param_idx(f,idx,'DPF')
        self.ifg_NPT = get_param_idx.get_param_idx(f,idx,'NPT')
        self.ifg_NSN = get_param_idx.get_param_idx(f,idx,'NSN')
        self.ifg_TPX = get_param_idx.get_param_idx(f,idx,'TPX')
        self.ifg_FXV = get_param_idx.get_param_idx(f,idx,'FXV')
        self.ifg_LXV = get_param_idx.get_param_idx(f,idx,'LXV')
        self.ifg_CSF = get_param_idx.get_param_idx(f,idx,'CSF')
        self.ifg_MXY = get_param_idx.get_param_idx(f,idx,'MXY')
        self.ifg_MNY = get_param_idx.get_param_idx(f,idx,'MNY')
        self.ifg_DXU = get_param_idx.get_param_idx(f,idx,'DXU')
        self.ifg_DAT = get_param_idx.get_param_idx(f,idx,'DAT')
        self.ifg_TIM = get_param_idx.get_param_idx(f,idx,'TIM')

        f.close()

    def readifg2(self):
        idx=self.blockidarr.index('DBS_ifg2')
        ipoint=self.blockpntarr[idx]
        f=open(self.filename,'rb')

        self.ifg2_DPF = get_param_idx.get_param_idx(f,idx,'DPF')
        self.ifg2_NPT = get_param_idx.get_param_idx(f,idx,'NPT')
        self.ifg2_NSN = get_param_idx.get_param_idx(f,idx,'NSN')
        self.ifg2_TPX = get_param_idx.get_param_idx(f,idx,'TPX')
        self.ifg2_FXV = get_param_idx.get_param_idx(f,idx,'FXV')
        self.ifg2_LXV = get_param_idx.get_param_idx(f,idx,'LXV')
        self.ifg2_CSF = get_param_idx.get_param_idx(f,idx,'CSF')
        self.ifg2_MXY = get_param_idx.get_param_idx(f,idx,'MXY')
        self.ifg2_MNY = get_param_idx.get_param_idx(f,idx,'MNY')
        self.ifg2_DXU = get_param_idx.get_param_idx(f,idx,'DXU')
        self.ifg2_DAT = get_param_idx.get_param_idx(f,idx,'DAT')
        self.ifg2_TIM = get_param_idx.get_param_idx(f,idx,'TIM')

        f.close()

    def getifg(self,write_flag=0):
        idx=self.blockidarr.index('DBL_ifg')
        ipoint=self.blockpntarr[idx]
        npts=self.blocklenarr[idx]
        f=open(self.filename,'rb')
        f.seek(ipoint)

            #offset=np.fromfile(f,dtype='int32',count=10)
        ifg=np.fromfile(f,dtype='float32',count=npts)
        
        xx=0
            #for x in ifg[npts-20:npts]:
            #    if np.abs(x) < 1.0E-30: 
            #        xx=xx+1
        ifg=ifg[0:npts-xx]
        ifgOPUS = copy.deepcopy(ifg)
        self.ifgOPUS = ifgOPUS
        ifg = np.multiply(ifg, self.ifg_CSF)
        ifg[np.size(ifg)/2:np.size(ifg)] = np.flipud(ifg[np.size(ifg)/2:np.size(ifg)])      ### AGREGADO POR JORGE EL 12/01/2017
        self.ifg = ifg.astype(np.float64)
        if write_flag == 1:
            np.save(self.filename+"_specclass_ifg.npy",self.ifg)
            header = {}
            header['PHR'] = self.PHR
            header['GFW'] = self.GFW
            header['GBW'] = self.GBW
            header['HFL'] = self.HFL
            header['LFL'] = self.LFL
            header['AQM'] = self.AQM
            header['NSS'] = self.NSS
            with open(self.filename+"_specclass_header.pkl", 'wb') as f:
                    pickle.dump(header, f, pickle.HIGHEST_PROTOCOL)
    
        f.close()
    
    def getspc(self,write_flag=0):
        
        idx    = self.blockidarr.index('DBL')
        ipoint = self.blockpntarr[idx]
        npts   = self.blocklenarr[idx]
        
        while abs(npts-self.spc['NPT']) > 2:

            self.blockidarr[idx] = 'DBL_X'
            idx    = self.blockidarr.index('DBL')
            ipoint = self.blockpntarr[idx]
            npts   = self.blocklenarr[idx]
        
        f=open(self.filename,'rb')
        f.seek(ipoint)
        
        self.spc['ORG'] = np.fromfile(f,dtype='float32',count=npts)
        
        if self.ud_flag == 1:
            self.spc['ORG'] = np.flipud(self.spc['ORG'])
        
        f.close()
        
        self.dnpt=len(self.spc['ORG'])-self.spc['NPT']

        self.spc['w'] = np.arange(self.spc['NPT']+self.dnpt)*(self.spc['LXV']-self.spc['FXV'])/(self.spc['NPT']+self.dnpt)+self.spc['FXV']
        
        if write_flag == 1:
            
            spc_str = np.empty(len(self.spc['ORG']),dtype=[('spc',float),('w',float)])
            spc_str['w'] = np.arange(self.spc['NPT']+self.dnpt)*(self.spc_LXV-self.spc_FXV)/(self.spc['NPT']+self.dnpt)+self.spc_FXV
            spc_str['spc'] = self.spc['ORG']
            np.save(self.filename+"_specclass_spcorg.npy",spc_str)
        
    def w(self):
        w=np.arange(self.spc['NPT']+self.dnpt)*(self.spc_LXV-self.spc_FXV)/(self.spc['NPT']+self.dnpt)+self.spc_FXV
        self.wavenumber=w
        self.spc_dw=np.abs(w[1]-w[0])
        return w

    def controlNCAR(self):

        noiserange         = [600., 620.]
        self.waverange     = [700, 6000]
        SNR_limit          = 0
        Ratio_limit        = 0.0015

        if self.filter == 's0':
            SNR_limit     = 30.0
            cloud_limit   = 0.2
            RNL_limit     = 0.01  
            self.waverange     = [4900, 7000]  
            

        elif self.filter == 's1':
            SNR_limit     = 50.0
            cloud_limit   = 0.2
            RNL_limit     = 0.01  
            self.waverange     = [3600, 4500]  
            
        elif self.filter == 's2':
            SNR_limit     = 50.0
            cloud_limit   = 0.2
            RNL_limit     = 0.01  
            self.waverange     = [2500, 3700] 
            Ratio_limit        = 0.002 

        elif self.filter == 's3':
            SNR_limit     = 100.0
            cloud_limit   = 0.2
            RNL_limit     = 0.01  
            self.waverange     = [2200, 3300]  

        elif self.filter == 's4':
            SNR_limit     = 50.0
            cloud_limit   = 0.2
            RNL_limit     = 0.01  
            self.waverange     = [1800, 2800]  

        elif self.filter == 's5':
            SNR_limit     = 100.0
            cloud_limit   = 0.2
            RNL_limit     = 0.01  
            self.waverange     = [1700, 2300]  

        elif self.filter == 's6':
            SNR_limit     = 170.0
            cloud_limit   = 0.2
            RNL_limit     = 0.01  
            self.waverange     = [600, 1400]  

        elif self.filter == 's9':
            SNR_limit     = 50.0
            cloud_limit   = 0.2
            RNL_limit     = 0.01  
            self.waverange     = [4100, 5400]  

        elif self.filter == 'sa':
            SNR_limit     = 40.0
            cloud_limit   = 0.2
            RNL_limit     = 0.01  
            self.waverange     = [3700, 4900]  

        elif self.filter == 'sb':
            SNR_limit     = 500.0
            cloud_limit   = 0.2
            RNL_limit     = 0.01  
            self.waverange     = [2600, 2950]  

        else:
            print 'Filter Not Identified'

        self.indsS               = np.where( (self.spc['w'] >= self.waverange[0]) & (self.spc['w'] <= self.waverange[1]) )[0]
        self.indsN               = np.where( (self.spc['w'] >= noiserange[0]) & (self.spc['w'] <= noiserange[1]) )[0]


        self.signal         = np.max(self.spc['ORG'][self.indsS ])
        self.noiseSD        = np.std(self.spc['ORG'][self.indsN])

        res                 = np.nansum( (self.spc['ORG'][self.indsN])**2 )

        #------------------------------
        # 
        #------------------------------
        self.noiseRMS      = np.sqrt( res / len(np.asarray(self.indsN)) )
        self.SNRsd         = self.signal/self.noiseSD
        self.SNRrms        = self.signal/self.noiseRMS

        #------------------------------
        # 
        #------------------------------

        try:

            indsPos = np.where(self.spc['ORG'][self.indsS ] > 0.)[0]
            indsNeg = np.where(self.spc['ORG'][self.indsS ] < 0.)[0]

            AreaPos = simps(self.spc['ORG'][self.indsS][indsPos])
            AreaNeg = simps(np.abs(self.spc['ORG'][self.indsS][indsNeg]))

            self.Ratio  = np.divide(AreaNeg,AreaPos)

        except Exception as errmsg:
            print errmsg
            self.Ratio = 1e-6    

        #------------------------------
        # 
        #------------------------------

        self.qflag     = 0
        self.comment   ='NOT CHECKED'

        if self.SNRsd >= SNR_limit:

            if  self.Ratio <= Ratio_limit:
           
                self.comment   ='OK'
                self.qflag   = 1

            else:

                self.comment   ='NOT OK (Negatives)'
                self.qflag   = 0

        else:
            
            self.comment='NOT OK (noisy?)'
        
   
 





