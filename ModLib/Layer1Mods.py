# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------------------
# Name:
#        Layer1Mods.py
#
# Purpose:
#       This file contains various modules used by sfit layer 1 processing. These modules 
#       are intended to be user specific. They have been seperated from the main code such
#       that they can easily be tailored to the user. Currently there are two modules:
#       1) reMkrNCAR  -- This is a simple module to build a reference profile.
#       2) t15ascPrep -- This module creates a pspec.input file and runs pspec to create
#                        t15asc files from bnr file type.
#
#
# External Subprocess Calls:
#   1) Call to sfitClasses to run subProcRun. This handles stdout and stderr of a sub-process call      
#
#
# Notes:
#       1)
#           
#
#
# Version History:
#       Created, June, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
#       Modified/Edited, 2019  Bavo Langerock (bavo.langerock@aeronomie.be )
#       Modified/Edited, 2020  Ivan Ortega (iortega@ucar.edu)
#
#
# License:
#    Copyright (c) 2013-2014 NDACC/IRWG
#    This file is part of sfit4.
#
#    sfit4 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    sfit4 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with sfit4.  If not, see <http://www.gnu.org/licenses/>
#
#----------------------------------------------------------------------------------------

                                #-------------------------#
                                # Import Standard modules #
                                #-------------------------#

import os                                
import sys
import fileinput
import re
import glob
import logging
import shutil
import re
from sfitClasses  import ExitError
from numpy        import diag, inf
from numpy        import copy, dot, interp
from numpy.linalg import norm, cholesky
import sfitClasses       as sc
import numpy             as np
import itertools         as it
import printStatmnts     as ps
import datetime          as dt
import h5py
import fnmatch




class DictWithDefaults(dict):
  """dict class with modified getitem to match items to a default"""
  def __init__(self,arg={},defaults={}):
    self.default=defaults.copy()
    dict.__init__(self,arg)
  
  def __getitem__(self,key):
    
    #if dict.has_key(self,key): return dict.__getitem__(self,key)
    if key in dict(self) : return dict.__getitem__(self, key)
   
    else: 
      #wildcards only work for the default dict, priority is given to exact match
      matches=sorted([k for k in self.default if fnmatch.fnmatch(key,k)],key=lambda x: x==key)[::-1]
      if len(matches): 
        #print ('%s->%s'%(key,matches));
        return self.default[matches[0]]
      else: raise KeyError(key)

  def __contains__(self,key):
    #if dict.has_key(self,key): return dict.__contains__(self,key)
    if key in dict(self) : return dict.__contains__(self, key)
   
    else: 
      #wildcards only work for the default dict
      matches=sorted([k for k in self.default if fnmatch.fnmatch(key,k)],key=lambda x: x==key)[::-1]
      if len(matches): 
        #print ('%s->%s'%(key,matches));
        return True
      else: False
  
  def __len__(self): return dict.__len__(self)+dict.__len__(self.default)
  

                                #--------------------------#
                                #                          #
                                #  -- Helper functions --  #
                                #                          #
                                #--------------------------#
def tryopen(fname,hdfkey='',logFile=False):
    """reads data from an ascii file or an hdf5 file (if hdfkey is set)"""
    if not hdfkey: #ASCII 
      try:
        with open(fname, 'r' ) as fopen:
            return fopen.readlines()
      except IOError as errmsg: pass
    else:          #HDF5
      try: 
        with h5py.File(fname,'r') as fopen:
            return fopen[hdfkey][...].astype(dtype=float)
      except (IOError,KeyError) as errmsg: pass
    #if errmsg: print (errmsg)
    if logFile: logFile.error(errmsg)
    return False



                                #-------------------------#
                                #                         #
                                #   -- NCAR Refmaker --   #
                                #                         #
                                #-------------------------#


def refMkrNCAR(zptwPath, WACCMfile, outPath, lvl, wVer, zptFlg, specDB, spcDBind, logFile=False, isoFlg=False):
    ''' Reference maker for NCAR. Insert your own version here. '''
    #----------------------------------------------
    # refMkrNCAR level options for creating 
    # reference.prf
    #
    # Level 0 option:
    #   Use pre-existing zpt file. Concatonate with
    #   water and WACCM profiles. 
    # Level 1 option:
    #   Use pre-existing zpt file. Concatonate with
    #   water and WACCM profiles. Replace surface
    #   pressure and temperature with values in
    #   database file. If those values are not 
    #   present, then default to origianl zpt file
    #----------------------------------------------  

    #--------------------------
    # Determine if paths exists
    #--------------------------    
    try:
        os.path.isdir(zptwPath)     # Path for zpt and water profile
        os.path.isfile(WACCMfile)    # Path for WACCM profile
        os.path.isdir(outPath)      # Outpath for reference.prf
    except OSError as errmsg:
        print (errmsg)
        if logFile: logFile.error(errmsg)
        return False

    #--------------
    # Find ZPT file
    #--------------
    if zptFlg: zptFiles = glob.glob(zptwPath + 'ZPT.nmc*')
    else     : zptFiles = glob.glob(zptwPath + 'zpt-120')

    # If more than one zpt file found trigger warning and use first one 
    if len(zptFiles) > 1:                 
        print ('Found more than one ZPT file. Using file: ' + zptFiles[0])
        if logFile: logFile.info('Using ZPTW file: ' + zptFiles[0])
        zptFile = zptFiles[0]

    # If no zpt files found trigger error    
    elif len(zptFiles) == 0:              
        print ('No zpt files found in: ' + zptwPath)
        if logFile: logFile.error('No zpt files found in: ' + zptwPath)
        return False

    else:
        zptFile = zptFiles[0]

    #------------------------
    # Find water profile file
    #------------------------
    waterFiles = glob.glob(zptwPath + 'w-120*')

    # If no water files found trigger error
    if len(waterFiles) == 0:
        print ('No water files found in: ' + zptwPath)
        if logFile: logFile.error('No water files found in: ' + zptwPath)
        return False            

    #---------------------------
    # Grab correct water version
    # based on user input
    #---------------------------
    # Create a list of version number for water files
    r = re.compile(r"([0-9]+)")

    waterVer = [int(r.search(os.path.splitext(wfile)[1]).group(1)) for wfile in waterFiles]


    #-------------------------------------------
    # For wVer < 0 get latest water version file
    # that is not 99
    #-------------------------------------------
    if wVer < 0:
        waterInd  = waterVer.index(max([val for val in waterVer if val != 99]))

    #----------------------------------------------------
    # For wVer >= 0 get user specified water version file   
    #----------------------------------------------------
    else:
        waterInd = [i for i, ver in enumerate(waterVer) if ver == wVer]
        #waterInd = waterVer.index(wVer)
        
        #------------------------------------------------
        # If water version == 99 find the closest water  to retrieval
        # If water version == 66 (ERA - 6h) find the closest in time to retrieval
        # If water version == 77 find the closest water  to retrieval - Log retrieval
        #------------------------------------------------
        #if waterInd:
        if (len(waterInd) > 0) and (wVer > 6):  #(wVer == 99) or (wVer == 66) or (wVer == 77):

            waterNames = [os.path.basename(waterFiles[i]) for i in waterInd]
            waterDates = [dt.datetime(int(x.strip().split('.')[1][0:4]),int(x.strip().split('.')[1][4:6]),int(x.strip().split('.')[1][6:]),
                                      int(x.strip().split('.')[2][0:2]),int(x.strip().split('.')[2][2:4]),int(x.strip().split('.')[2][4:])) for x in waterNames]
            
            obsDate = dt.datetime(int(str(int(specDB['Date'][spcDBind]))[0:4]),int(str(int(specDB['Date'][spcDBind]))[4:6]),int(str(int(specDB['Date'][spcDBind]))[6:]),
                                  int(specDB['Time'][spcDBind].split(':')[0]),int(specDB['Time'][spcDBind].split(':')[1]),int(specDB['Time'][spcDBind].split(':')[2]))
            
            nearstD  = sc.nearestTime(waterDates,obsDate.year,obsDate.month,obsDate.day,obsDate.hour,obsDate.minute,obsDate.second)    
            indTemp  = waterDates.index(nearstD) 
            waterInd = waterFiles.index(zptwPath+waterNames[indTemp]) 

        #------------------------------------------------

        elif len(waterInd) == 0:
            print ('Water version {0:d} not found, using latest version: {1:d} '.format(wVer,max(waterVer)))
            if logFile: logFile.error('Water version %d not found, using latest version'% wVer)
            waterInd = waterVer.index(max(waterVer))
    
        else: waterInd = waterInd[0]
              
    waterFile = waterFiles[waterInd]
    
    print ('\n')
    print ('Using water file: {}'.format(waterFile))
    print ('\n')


    #----------------------------------
    # Concate ZPT, water, and WACCM  
    # profiles to produce reference.prf
    #----------------------------------
    refFile = outPath + 'reference.prf'

    with open( refFile, 'w') as fout:
        for line in fileinput.input([zptFile,waterFile,WACCMfile]):
            if line.strip():
                fout.write(line)

    #--------------------------------------------
    # Now that reference.prf is created, go back to
    # make necessary changes. This includes adding 
    # the number 99 to first line of file and 
    # inserting database values of temperature and
    # pressure if specified by level option.
    #----------------------------------------------

    #------------------------------
    # Add number 99 to first line
    # of file indicating 99 species
    # included in list
    #------------------------------                 
    with open( refFile, 'r+' ) as fout:
        lines    = fout.readlines()
        lines[0] = lines[0].rstrip() + "{0:5d}".format(99) + '\n'
        # Number of atmospheric layers
        nlyrs    = int(lines[0].split()[1])         

        # For level 1 options
        if lvl == 1:
            # Determine the number of lines in each profile = ceil(nlyrs/5)
            nlines = int(np.ceil(nlyrs/5.0))

            #---------------------------------------------------------
            # Determine if database values of Temperature and Pressure
            # are valid to use. First choice is external station data.
            # If this is not available default to house log data. If 
            # this is not available default to NCEP data.
            #---------------------------------------------------------
            # Temperature
            NCEPtempFlg = False

            if specDB['ExtStatTemp'][spcDBind] == -9999:
                if specDB['HouseTemp'][spcDBind] == -9999:
                    NCEPtempFlg = True

                else:
                    newTemp = specDB['HouseTemp'][spcDBind]
                    newTemp += 273.15                        # Convert [C] => [K]           
                    newTemp = "{0:.4f}".format(newTemp)

            else:
                newTemp = specDB['ExtStatTemp'][spcDBind]
                newTemp += 273.15                            # Convert [C] => [K]
                newTemp = "{0:.4f}".format(newTemp)

            # Pressure
            NCEPpresFlg = False

            if specDB['ExtStatPres'][spcDBind] == -9999:
                if specDB['HousePres'][spcDBind] == -9999:
                    NCEPpresFlg = True

                else:
                    newPres = specDB['HousePres'][spcDBind]
                    newPres = "{0:.4e}".format(newPres)
            else:
                newPres = specDB['ExtStatPres'][spcDBind]
                newPres = "{0:.4e}".format(newPres)

            #-----------------------------------------
            # Replace surface temperature and pressure
            # in reference.prf with external station 
            # or house log data if applicable
            #-----------------------------------------
            for linenum,line in enumerate(lines):
                if NCEPpresFlg == False:
                    if 'pressure' in line.lower():
                        nlnum        = linenum + nlines
                        oldPres      = lines[nlnum].split()[-1].rstrip(',')

                        #----------------------------------------------------
                        # Compare NCEP pressure with new updated pressure
                        #  1) If updated surface pressure is less than NCEP
                        #     one level above surface throw error
                        #  2) If the absolute value of the difference between
                        #     NCEP and external station surface pressure is
                        #     greater than 15 hPa warning is thrown
                        #----------------------------------------------------
                        if (float(lines[nlnum].split()[-2].rstrip(',')) > float(oldPres)):
                            if logFile:
                                logFile.error('Surface pressure error for reference profile: ' + refFile)
                                logFile.error('External surface pressure < NCEP pressure one level above surface => Non-hydrostatic equilibrium!!')
                            print ('Surface pressure error for reference profile: ' + refFile)
                            print ('External surface pressure < NCEP pressure one level above surface => Non-hydrostatic equilibrium!!')
                        elif ( abs(float(oldPres) - float(newPres)) > 15):
                            if logFile:
                                logFile.warning('Surface pressure warning for reference profile: ' + refFile)
                                logFile.warning('Difference between NCEP and external station surface pressure > 15 hPa')
                            print ('Surface pressure warning for reference profile: ' + refFile)
                            print ('Difference between NCEP and external station surface pressure > 15 hPa')

                        lines[nlnum] = lines[nlnum].replace(oldPres,newPres)

                if NCEPtempFlg == False:
                    if 'temper' in line.lower():
                        nlnum        = linenum + nlines
                        oldTemp      = lines[nlnum].split()[-1].rstrip(',')

                        #------------------------------------------------------
                        # Compare NCEP temperature with new updated temperature
                        #  1) If updated surface temperature is less than NCEP
                        #     one level above surface throw error
                        #  2) If the absolute value of the difference between
                        #     NCEP and external station surface temperature is
                        #     greater than 10 DegC warning is thrown
                        #------------------------------------------------------
                        if (float(lines[nlnum].split()[-2].rstrip(',')) > float(oldTemp)):
                            if logFile:
                                logFile.error('Surface Temperature error for reference profile: ' + refFile)
                                logFile.error('External surface Temperature < NCEP Temperature one level above surface => Non-hydrostatic equilibrium!!')
                            print ('Surface Temperature error for reference profile: ' + refFile)
                            print ('External surface temperature < NCEP temperature one level above surface => Non-hydrostatic equilibrium!!')
                        elif ( abs(float(oldTemp) - float(newTemp)) > 10):
                            if logFile:
                                logFile.warning('Surface temperature warning for reference profile: ' + refFile)
                                logFile.warning('Difference between NCEP and external station surface temperature > 10 DegC')
                            print ('Surface temperature warning for reference profile: ' + refFile)
                            print ('Difference between NCEP and external station surface temperature > 10 DegC')                        

                        lines[nlnum] = lines[nlnum].replace(oldTemp,newTemp)                    


    with open( refFile, 'w' ) as fout:
        for line in lines:
            fout.write(line)
        

    return True


                        #-------------------------#
                        #                         #
                        #    -- t15ascPrep --     #
                        #                         #
                        #-------------------------#    

# Copy bnr file to output folder
def t15ascPrep(dbFltData_2, wrkInputDir2, wrkOutputDir5, mainInF, spcDBind, ctl_ind, logFile):

    if mainInF.inputs['coaddFlg']: bnrExt = '.bnrc'
    else:                          bnrExt = '.bnr'

    bnrFname = "{0:06}".format(int(dbFltData_2['TStamp'][spcDBind])) + bnrExt

    if not os.path.isfile(wrkInputDir2 + bnrFname):
        print ('Unable to find bnr file: {}'.format(wrkInputDir2 + bnrFname))
        return False

    #if not os.path.isfile(wrkOutputDir5+bnrFname):
        #try:
            #shutil.copy( wrkInputDir2 + bnrFname, wrkOutputDir5 )
        #except IOError as errmsg:
            #print errmsg
            #if logFile: logFile.error(errmsg)
            #return False                    

    #--------------------------------------
    # Create pspec.input file for pspec.f90
    #--------------------------------------    
    with open(wrkOutputDir5 + 'pspec.input', 'w') as fname:

        # Write header information
        pWrtStr = ps.pspecInputStr()

        fname.writelines(pWrtStr[0:7])
        fname.write( str(dbFltData_2['N_Lat'][spcDBind]) + '\n' )
        fname.writelines(pWrtStr[7:8])
        fname.write( str(dbFltData_2['W_Lon'][spcDBind]) + '\n')
        fname.writelines(pWrtStr[8:9])
        fname.write( str(dbFltData_2['Alt'][spcDBind]) + '\n')
        fname.writelines(pWrtStr[9:19])
        fname.write('{:<5d}{:<5d}\n'.format(mainInF.inputs['outFlg'],mainInF.inputs['verbFlg']))
        fname.writelines(pWrtStr[19:24])
        fname.write( mainInF.inputs['fltrBndInputs'] )
        fname.writelines(pWrtStr[24:26])
        fname.write( str(mainInF.inputs['nBNRfiles']) + '\n')
        fname.writelines(pWrtStr[26:])
        fname.write( wrkInputDir2 + bnrFname + '\n') 
        fname.write( '{0:<10.1f}{1:<5d}{2:<5d}{3:<5d}{4:<5d}'.format(dbFltData_2['ROE'][spcDBind] ,          # ROE
                                                                     mainInF.inputs['nterpFlg']   ,          # nterp
                                                                     mainInF.inputs['ratioFlg']   ,          # rflag
                                                                     mainInF.inputs['fileFlg']    ,          # fflag
                                                                     mainInF.inputs['zFlg'] )        )       # zflag

    #------------------------------
    # Change working directory to 
    # output directory to run pspec
    #------------------------------
    try:
        os.chdir(wrkOutputDir5)
    except OSError as errmsg:
        if logFile: logFile.error(errmsg)
        return False


    #--------------
    # Call to pspec
    #--------------
    print ('Running pspec for ctl file: ' + mainInF.inputs['ctlList'][ctl_ind][0] )
    sc.subProcRun( [mainInF.inputs['binDir'] + 'pspec'] )           # Subprocess call to run pspec

    #if ( stderr is None or not stderr ):
            #if log_flg:
                    #logFile.info( stdout )
                    #logFile.info('Finished running pspec\n' + stdout)
    #else:
            #print 'Error running pspec!!!'
            #if log_flg:
                    #logFile.error('Error running pspec \n' + stdout)
            #return False                                


    return True


                            #-------------------------#
                            #                         #
                            #  -- Error Analysis --   #
                            #                         #
                            #-------------------------#    
def errAnalysis(ctlFileVars, SbctlFileVars, wrkingDir, logFile=False):
    """
    Calculates systematic and random uncertainty covariance matrix 
    using output from sfit4 and sb values from ctl file
    Return: (val1,val2,val3) where:
         val1 is boolean 
    """
    def getSFITversion(wrkingDir):
      """retrieves the version of sfit4 as a 4tuple from the output file"""
      with open(wrkingDir+'sfit4.dtl','r') as fid: header=fid.readline().strip()
      # first integer found is SFIT 4: ('SFIT4:V')
      return tuple(map(int,re.sub('[^0-9.]','',header.strip().split(':')[1]).split('.')))
    version=getSFITversion(wrkingDir)
    
    print ('Detected SFIT4 Version=%s'%(version,))

    #----------------------------------
    # Sb labels: are taken from sbctldefaults which contains either the labels set by the user in his defaults file, or the labels from the Layer1/sbDefaults.ctl file
    #----------------------------------
    Kb_labels = {}
    for i in range(0, len(SbctlFileVars.inputs['kb_info']), 4):
      Kb_labels[SbctlFileVars.inputs['kb_info'][i]] = SbctlFileVars.inputs['kb_info'][i+1]

    #----------------------------------
    # Adapt label definitions according to sfit version
    #----------------------------------
    if version>=(0,9,6,2): Kb_labels['phase_fcn']='EmpPhsFcn'
    if version>(0,9,5,0): 
      for label in ('dwshift','maxopd'): #only these 2?? TODO
        if label in Kb_labels: del Kb_labels[label]

    temp_retrieval_flag=(ctlFileVars.inputs.get('rt.temperature',['F'])[0]=='T') #flag to know if temp is retrieved
    temp_retrieval_tikhonov=(ctlFileVars.inputs.get('rt.temperature.lambda',[0])[0]>0) #flag to know if it is done with tikhonov
    def matPosDefTest(mat):
        ''' Test if matrix is positive definite'''
        
        #----------------------------------
        # First test if matrix is symmetric
        #----------------------------------
        symRslt = np.all(mat.T==mat)

        #-------------------------------
        # Then test if negative eignvalues are close to zero
        #-------------------------------
        l=np.linalg.eigvals(mat)
        #print l[l<0],max(abs(l)),l[l<0]/max(abs(l)),mat.dtype,mat.shape
        eignRslt = np.allclose(0,l[l<0]/max(abs(l)),atol=1.e-6)#,rtol=1e-5/max(abs(l)))
        
        return(symRslt,eignRslt)
        
    def _diagtransform(d,diagA):
        """ Small function that transforms a decomposed covariance matrix S=dd^T with a diagonal transformation A=diag(diagA) """
        sdT=(diagA*(d.T)) #compute (A*d).T using numpy broadcasting 
        sd=sdT.T          #compute (A*d)
        return sd.dot(sdT)#return Add^tA^T
        
    def calcCoVar(coVar,A,retPrfVMR,airMass):
        ''' Calculate covariance matricies in various units, A transfrom coVar units to sfit relative units
        
        covar=covariance matrix to transform
        A=transformation
        retPrfVMR=scaling factor to apply on target vectors of A
        airMass=pc air, to transform between VMR and PC'''
        #print coVar.shape,
        if coVar.shape == 1:
            print ("When does this happen????? shape= %s"%(covar.shape,)) #avoid the dot product in this case... TODO
            Sm   = np.dot(  np.dot( A, coVar ), A.T )                            # Uncertainty covariance matrix [Fractional]
        elif len(coVar.shape)==1: #input is the diagonal for a diagonal covar matrix (e.g. noise)
            #print "diagonal input for calccovar"
            AD=(np.sqrt(coVar)*A)
            #Sm=(coVar*A).dot(A.T) #=A.dot(diag(coVar)).dot(A.T)
        else:
            l,d=np.linalg.eigh(coVar)
            sqrtL=np.sqrt(np.ma.masked_array(l,l<0).filled(0))             #correct for negative eigenvalues and take the sqrt
            D=sqrtL*d                                                      #use numpy broadcasting to calculate d.dot(diag(sqrtL))
            AD=A.dot(D);ADT=AD.T                            #avoid doing the same computation multiple times
            #Sm   = AD.dot(ADT)
        Sm_1 = _diagtransform(AD,retPrfVMR)          #in vmr units
        Sm_2 = _diagtransform(AD,retPrfVMR*airMass)  #in pc units
        Sm_3 = np.sqrt(Sm_2.sum())                   #std on tc  
        #print Sm_3/(retPrfVMR*airMass).sum()*100
        #Sm_1_old= np.dot(  np.dot( np.diag(retPrfVMR), Sm ), np.diag(retPrfVMR) )   # Uncertainty covariance matrix [(VMR)^2]
        #Sm_2_old = np.dot(  np.dot( np.diag(airMass), Sm_1 ), np.diag(airMass)   )   # Uncertainty covariance matrix [(molecules cm^-2)^2]
        #densPrf = retPrfVMR * airMass
        #Sm_3_old = np.sqrt( np.dot( np.dot( densPrf, Sm ), densPrf.T )     )         # Whole column uncertainty [molecules cm^-2]
        #print 'check',np.allclose(Sm_1,Sm_1_old),np.allclose(Sm_2,Sm_2_old),np.allclose(Sm_3,Sm_3_old)
        #Sm_3 = np.sqrt( np.sum( np.diagonal( Sm_2 ) ) )                          # Whole column uncertainty [molecules cm^-2]

        return (Sm_1, Sm_2, Sm_3)     # (Variance, Variance, STD)

    def writeCoVar(fname,header,var,ind):
        ''' Write covariance matricies to files'''
        with open(fname, 'w') as fout:
            fout.write('# ' + header + '\n'                                       )
            fout.write('# nmatr  = {0}\n'.format(len(var)                         ))
            fout.write('# nrows  = {0}\n'.format(var[list(var.keys())[0]][0].shape[0]   ))
            fout.write('# ncols  = {0}\n\n'.format(var[list(var.keys())[0]][0].shape[1] )) 
            for k in var:
                fout.write('{0}\n'.format(k))

                for row in var[k][ind]:
                    strformat = ' '.join('{%d:>12.4E}'%i for i in range(len(row))) + ' \n'
                    fout.write( strformat.format(*row) )

                fout.write('\n\n')    

    def createCovar(std,sbcorkey=None,z=None,Sbctldict={}):
        '''Creates a full covariance matrix out of diagonal and correlation settings from sb.ctl'''
        Sb=np.tensordot(std,std,0) #this is the fully correlated matrix, unchanged for systematic, should be changed for random
        test=list(map(bool,[sbcorkey,not np.array_equal(z,None),len(Sbctldict)]))
        if all(test): 
          corwidthinv=1./Sbctldict[sbcorkey][0] if (sbcorkey in Sbctldict and Sbctldict[sbcorkey][0]!=0.) else 0.
          deltaz=np.tensordot(z,np.ones(z.shape),0)
          deltaz=np.exp(-abs(deltaz-deltaz.T)*corwidthinv)
          if Sb.shape==deltaz.shape: Sb*=np.ma.array(deltaz,mask=deltaz<.01).filled(0)
        elif sum(test): return None
        return Sb


    def paramMap(paramName,Kb_labels):
        '''There is discontinuity between the variable names used in sfit ctl file
           and what is output in kb.output. This function helps map the kb.output
           file variable names to what is used in ctl file. Kb_labels are the 
           parameter names as they appear in the ctl file'''

        Kb_rev=dict(map(lambda x: x[::-1],Kb_labels.items()))
        #----------------------------------
        # Split parameter name if necessary
        #----------------------------------
        
        if len(paramName.split('_')) >=2: paramName,gas = paramName.split('_')[:2];#print paramName

        #--------------------------------------------------------
        # List of parameters as they appear in the Kb.output file 
        #--------------------------------------------------------
        #Kb_labels_orig = ['TEMPERAT','SolLnShft','SolLnStrn','SPhsErr','IWNumShft','DWNumShft','SZA','LineInt','LineTAir','LinePAir','BckGrdSlp','BckGrdCur','EmpApdFcn','EmpPhsFnc','FOV','OPD','ZeroLev']

        #------------------------------------------------------
        # Find index of input paramName. If this is not matched
        # then program returns original paramName. This is for
        # kb.profile.gases
        #------------------------------------------------------
        if paramName not in Kb_rev: return paramName

        if 'gas' in locals(): rtrnVal = Kb_rev[paramName] + '_' + gas
        else:                 rtrnVal = Kb_rev[paramName]
        return rtrnVal

    def readCovarFile(params,Errtype):
        """Reads the matrixes from file objects for the parameters in the params list, which is determined from the e.g. file.in.random key in the ctl file"""
        sbCovar = {}
        ## p can be in ['temperature', 'solshft','solstrnth','phase','wshift','dwshift','sza','lineInt','lineTAir','linePAir','slope','curvature','apod_fcn','phase_fcn','omega','max_opd','zshift']
        for p in params: ## Check
            #----------------------------------------
            # Read in Sb matrix for parameter is list
            #----------------------------------------
            #print 'loading file.in.'+p+'.'+Errtype
            lines = tryopen(SbctlFileVars.inputs['file.in.'+p.lower()+'.'+Errtype][0], hdfkey=p.replace('temperature','T')+'/'+Errtype,logFile=logFile)
            if isinstance(lines,bool):
                print ('file.in.'+p+'.'+Errtype+' missing for observation, directory: ' + wrkingDir)
                if logFile: logFile.error('file.in.'+p+'.'+Errtype+' missing for observation, directory: ' + wrkingDir)
                return False    # Critical file, if missing terminate program
            sbCovar[p] = np.array( [ [ float(x) for x in row.split()] for row in lines ] ) if isinstance(lines,list) else lines
            #-----------------------------------------------------
            # Test if Sb matrix is symmetric and positive definite
            #-----------------------------------------------------
            (symRtn,pdRtn) = matPosDefTest(sbCovar[p])
            if not symRtn: print ("Warning!! The Sb matrix for "+p+" is not symmetric\n\n")
            if not pdRtn:  print ("Warning!! The Sb matrix for "+p+" is not positive definite\n\n")
            if not symRtn or not pdRtn: return False
        return sbCovar


    #----------------------------------------------
    # List of parameters as they appear in ctl file 
    #----------------------------------------------   
    #Kb_labels = ['temperature', 'solshft','solstrnth','phase','wshift','dwshift','sza','lineInt','lineTAir','linePAir','slope','curvature','apod_fcn','phase_fcn','omega','max_opd','zshift'] 
    #------------------------------------------------------
    # Determine number of microwindows and retrieved gasses
    #------------------------------------------------------
    n_window  = len( ctlFileVars.inputs['band'] )
    n_profile = len( ctlFileVars.inputs['gas.profile.list'] )
    n_column  = len( ctlFileVars.inputs['gas.column.list'] )

    #-----------------------------------------------------
    # Primary retrieved gas is assumed to be the first gas 
    # in the profile gas list. If no gases are retrieved 
    # as a profile, the primary gas is assumed to be the 
    # first gas in the column gas list.
    #-----------------------------------------------------
    if (n_profile > 0): primgas = ctlFileVars.inputs['gas.profile.list'][0]
    else:               primgas = ctlFileVars.inputs['gas.column.list'][0]

    #----------------------------------------------
    # Make sure input working directory ends in '/'
    #----------------------------------------------
    if not wrkingDir.endswith('/'): wrkingDir += '/'

    #--------------------------------------------
    # Read values from sfit4 output. Initialize 
    # output class for summary, profiles, and pbp
    #--------------------------------------------
    # Check for succesful retrieval
    if not sc.ckFile(wrkingDir + ctlFileVars.inputs['file.out.summary'][0], exitFlg=False): return False
    sumVars = sc.RetOutput(wrkingDir,logFile)
    rtn = sumVars.readSum(ctlFileVars.inputs['file.out.summary'][0])                           # Read Summary file parameters
    if not rtn: return False                                                                   # Bail if not able to read summary
    sumVars.readPbp(ctlFileVars.inputs['file.out.pbpfile'][0])                                 # Read pbpfile (to get sza)
    sumVars.readPrf(ctlFileVars.inputs['file.out.retprofiles'][0], primgas)                    # Read retreived profile file
    sumVars.readPrf(ctlFileVars.inputs['file.out.aprprofiles'][0], primgas, retapFlg=0)        # Read a priori profile file




    #----------------------------------
    # Insert retrieval grid in sbctldefaults and substitute default values for SbctlFileVars
    #----------------------------------
    z=sumVars.aprfs['Z']

    def _expandgridsinputs(d):
      """dummy function to replace coarse uncertainty input grid in a dict d to the retrieval grid z"""
      gridvars=filter(lambda k: fnmatch.fnmatch(k,'sb.*.grid'),d.keys())


      for gk in list(gridvars):
        grid=d[gk]
        for ErrType in ('random','systematic'):
          defk=gk.replace('grid',ErrType)
          
          d[defk]=interp(z,*zip(*sorted(zip(grid,d[defk]),key=lambda x: x[0])))
        del d[gk]
      return

    #----------------------------------
    # Setup the Sb dictionary as a pair of dictionaries: 
    #   one dict represents the sb.ctl contents, 
    #   the second is the default values dict (which may be empty if eg sbdefflg=F
    # Any exact match with a key in the first (sb.ctl) has priority above any match with a key in the second 
    # default dict. Only the second default dict allows wildcards (microwindows,gases,...).
    # For the second/default dict an exact match will have priority above wildcard matches.
    # Both dicts allow std profile definitions on coarse grids.
    # These are interpolated to the retrieval grid using _expandgridsinputs
    #----------------------------------

    _expandgridsinputs(SbctlFileVars.inputs)
    SbDict = DictWithDefaults({}, defaults=SbctlFileVars.inputs)

    #SbDict = DictWithDefaults(SbctlFileVars.inputs, defaults=SbctlFileVars.inputs)
    #_expandgridsinputs(SbDict) #in the case the user also uses coarse grids...

    #------------------------------------------------------------------------------
    # Read in output files from sfit4 run
    #  -- k.output to calculate averaging kernel
    #  -- d.complete to calculate averaging kernel and measurement error
    #  -- sa.complete to calculate smoothing error
    #  -- summary file for the SNR to calculate the measurement error
    #  -- kb.output for non-retrieved parameter error calculation
    #  -- rprfs.table and aprfs.table for the airmass, apriori and retrieved profiles 
    #------------------------------------------------------------------------------    
    # Read in K matrix
    #------------------
    lines = tryopen(wrkingDir+ctlFileVars.inputs['file.out.k_matrix'][0], logFile) 
    if not lines: 
        print ('file.out.k_matrix missing for observation, directory: ' + wrkingDir)
        if logFile: logFile.error('file.out.k_matrix missing for observation, directory: ' + wrkingDir)
        return False # Critical file, if missing terminate program  

    
   
    K_param = lines[2].strip().split()

    n_wav   = int( lines[1].strip().split()[0] )
    x_start = int( lines[1].strip().split()[2] )
    n_layer = int( lines[1].strip().split()[3] )
    x_stop  = x_start + n_layer
    K = np.array([[float(x) for x in row.split()] for row in lines[3:]])

    #------------------   
    # Read in Sa matrix
    #------------------
    
    lines = tryopen(wrkingDir+ctlFileVars.inputs['file.out.sa_matrix'][0], logFile)
    if not lines: 
        print ('file.out.sa_matrix missing for observation, directory: ' + wrkingDir)
        if logFile: logFile.error('file.out.sa_matrix missing for observation, directory: ' + wrkingDir)
        return False    # Critical file, if missing terminate program    

    sa = np.array( [ [ float(x) for x in row.split()] for row in lines[3:] ] )

    sa_syst=np.zeros(sa.shape)   #create an empty analogue of the sa matrix for systematic contributions

    for gas in ctlFileVars.inputs['gas.profile.list']+['TEMPERATURE']*int(temp_retrieval_flag):

        sbinputforsa=False
        
        sbkey_rand ='sb.%s.%s'%('profile.%s'%gas.lower() if gas.lower()!='temperature' else 'temperature','random')
        sbkey_syst=sbkey_rand.replace('.random','.systematic')
        
        tempcase=(gas=='TEMPERATURE')
        
 
        if tempcase or ( ctlFileVars.inputs['gas.profile.%s.correlation'%gas.lower()][0]=='T' and ctlFileVars.inputs['gas.profile.%s.correlation.type'%gas.lower()][0] in (5,6)):
            sbinputforsa=True #require input for Sb
            print ('   detected %s for %s'%('sa required input' if (tempcase and not temp_retrieval_tikhonov) else 'sainv regularization',gas))
            if  (not tempcase or (tempcase and temp_retrieval_tikhonov)) and sbkey_syst in SbDict and (np.diff(SbDict[sbkey_syst])==0).all(): print('   detected constant std profile for %s: might generate a zero uncertainty in case of Tikhonov'%sbkey_syst)
 
        if (sbkey_rand not in SbctlFileVars.inputs or sbkey_syst not in SbctlFileVars.inputs) and sbinputforsa: print ('Error !! The sb.ctl file must contain information on random & systematic profile uncertainty for %s'%gas);raise ValueError('Missing input in sb.ctl for profile uncertainty for %s because of Tikhonov type retrieval'%gas)

        if sbkey_rand in SbDict: #prefer the sb information above the sa matrix...
            #if gas in ('CH4','HDO'): continue #for debugging .... 
            #else: print gas
            kgas=gas.replace('TEMPERATURE','TEMPERAT')
            sa_idx=np.where(np.array(K_param)==kgas)[0]
            #get the Sb for this gas
            sbcorkey=sbkey_rand.replace('.random','.correlation.width')
            #only take correlation into account if random and if it is a profile (gas or temperature) in KB!!
            if tempcase and SbDict.get(sbkey_rand+'.scaled',['F'])[0]=='F': scale=sumVars.aprfs[gas];#print(scale) #T std profile is given in Kelvin
            else: scale=1
            Sb=createCovar(SbDict[sbkey_rand]/scale,**(dict(sbcorkey=sbcorkey,z=z,Sbctldict=SbDict)))
            if np.array_equal(Sb,None): print ('Error building covariance matrix for %s'%sbcorkey);raise ValueError('Bad setting for %s'%sbcorkey)
            sa[tuple(np.meshgrid(sa_idx,sa_idx,indexing='ij'))]=Sb
        if sbkey_syst in SbDict:
            if tempcase and SbDict.get(sbkey_syst+'.scaled',['F'])[0]=='F': scale=sumVars.aprfs[gas] #T std profile is given in Kelvin
            else: scale=1
            Sb_syst=createCovar(SbDict[sbkey_syst]/scale)
            if np.array_equal(Sb_syst,None): print ('Error building systematic covariance matrix for %s'%sbcorkey);raise ValueError('Bad setting for %s'%sbcorkey)
            #fill the sb in the inintial sa
            sa_syst[tuple(np.meshgrid(sa_idx,sa_idx,indexing='ij'))]=Sb_syst

    
    #-----------------------------------------------------
    # Test if Sa matrix is symmetric and positive definite
    #-----------------------------------------------------
    (symRtn,pdRtn) = matPosDefTest(sa)
    if not symRtn: print ("Warning!! The Sa matrix is not symmetric\n\n")
    if not pdRtn:  print ("Warning!! The Sa matrix is not positive definite\n\n")
    # !!!!!!!!!!! Should we retrun False???  is it possible that the sa is not symmetric? If it is possible, we should solve it (by making it symmetric)


    
    #---------------------------------------------------------------
    # Create Se matrix (Two ways to do this depending on input flg):
    # 1) Read SNR from summary file for each band and each scan.
    #    This value is the SNR from the T15asc file. With this option 
    #    if the user manipulates the snr values it will not be carried
    #    through to the error calculation.
    # 2) Read seinv.output matrix. With this option, if the user 
    #    manipulates snr values for the fit, these changed values 
    #    will be carried through (via seinv.output) to the error
    #    calculations.
    #---------------------------------------------------------------
    #se  = np.zeros((np.sum(sumVars.summary['nptsb'],dtype=int),np.sum(sumVars.summary['nptsb'],dtype=int)), float)



    if SbDict['seinputflg'][0].upper() == 'F':
        snrList    = list(it.chain(*[[snrVal]*int(npnts) for snrVal,npnts in zip(sumVars.summary['SNR'],sumVars.summary['nptsb'])]))
        snrList[:] = [val**-2 for val in snrList]
    else:
        if not sc.ckFile(wrkingDir+ctlFileVars.inputs['file.out.seinv_vector'][0], exitFlg=False,quietFlg=False): return False
        lines      = tryopen(wrkingDir+ctlFileVars.inputs['file.out.seinv_vector'][0], logFile)
        snrList    = np.array([float(x) for line in lines[2:] for x in line.strip().split()])
        snrList[:] = 1.0/snrList
    #np.fill_diagonal(se,snrList)    
    se=np.array(snrList) #avoid setting up a full 2d matrix for this diagonal matrix...

    #-----------------------------------------------------
    # Test if user want to change the Se array
    #-----------------------------------------------------
    user_snr_settings=sorted([int(k.rsplit('.',1)[-1]) for k in SbDict if fnmatch.fnmatch(k,'sb.snr.[0-9]')])
    se_chuncks=sumVars.summary['nptsb']
    c=0
    for i,se_chunck in enumerate(se_chuncks):
      if i+1 in user_snr_settings: 
        se[np.arange(c,c+se_chunck,dtype=int)]=float(SbDict['sb.snr.%d'%(i+1)][0])**-2
        print('Changed SNR for band %s to %s'%(i+1,SbDict['sb.snr.%d'%(i+1)][0]))
      c+=se_chunck    
      
   

    #-----------------------------------------------------
    # Test if Se matrix is symmetric and positive definite
    #-----------------------------------------------------
    #(symRtn,pdRtn) = matPosDefTest(se)
    #if not symRtn: print "Warning!! The Se matrix is not symmetric\n\n"
    #if not pdRtn:  print "Warning!! The Se matrix is not positive definite\n\n"
    # !!!!!!!!!! Should we return False? ->is this possible? se is a diagonal matrix, so no check required...


    #--------------------
    # Read in Gain matrix
    #--------------------
    lines = tryopen(wrkingDir+ctlFileVars.inputs['file.out.g_matrix'][0], logFile)
    if not lines: 
        print ('file.out.g_matrix missing for observation, directory: ' + wrkingDir)
        if logFile: logFile.error('file.out.g_matrix missing for observation, directory: ' + wrkingDir)
        return False    # Critical file, if missing terminate program   

    D = np.array([[float(x) for x in row.split()] for row in lines[3:]])

    #------------------
    # Read in Kb matrix
    #------------------   
    print ('\nLoading kb matrix',)
    lines = tryopen(wrkingDir+ctlFileVars.inputs['file.out.kb_matrix'][0], logFile)
    if not lines: 
        print ('file.out.kb_matrix missing for observation, directory: ' + wrkingDir)
        if logFile: logFile.error('file.out.kb_matrix missing for observation, directory: ' + wrkingDir)
        return False    # Critical file, if missing terminate program   
    else: print ('... done')

    Kb_param = list(map(lambda x: x.replace('PROFILE_',''),lines[2].strip().split()))
    #---------------------------------------------------------------
    # Some parameter names in the Kb file are appended by either 
    # micro-window or gas name. If they are appended by micro-window
    # strip this and just keep parameter name so that we may group
    # the micro-windows under one key (so no grouping for eg lineint,...)
    #---------------------------------------------------------------
    for ind,val in enumerate(Kb_param):
        if len(val.split('_')) >=2:
            pname,appnd = val.split('_')[:2]
            try: int(appnd)
            except ValueError: pass
            else: val = pname #remove the mw index from the labels if integer
        Kb_param[ind] = val 

    Kb_unsrt = np.array([[float(x) for x in row.split()] for row in lines[3:]])

    #----------------------------------
    # Create a dictionary of Kb columns
    # A list of numpy arrays is created
    # for repeated keys
    #----------------------------------
    Kb = {} #keys are the keys used in the ctl file...
    for k in set(Kb_param):
        inds = [i for i, val in enumerate(Kb_param) if val == k]
        Kb.setdefault(paramMap(k,Kb_labels).lower(),[]).append(Kb_unsrt[:,inds])
    #print Kb_param,map(lambda x: (x[0],x[1][0].shape),Kb.items()),Kb_labels

    #--------------------------------------
    # Un-nest numpy arrays in Kb dictionary
    #--------------------------------------
    for k in Kb: Kb[k] = Kb[k][0]   # Check this

    #-------------------------------------
    # Get gain matrix for the retrieved 
    # profile of the gas in questions only
    #-------------------------------------
    Dx = D[x_start:x_stop,:]

    #-----------------------------------------
    # Calculate the unscaled Averaging Kernel: 
    #    AK = D*K
    #-----------------------------------------
    try: AK = np.dot(D,K)
    except ValueError as ve:
        print ('Unable to multiply Gain and K matrix ')
        print ('Gain matrix shape: %s, K matrix shape: %s' %(str(D.shape),str(K.shape)))
        if logFile: logFile.error('Unable to multiple Gain and K matrix; Gain matrix shape: %s, K matrix shape: %s' %(str(D.shape),str(K.shape)) ) 
        raise ve

    #-------------------------------
    # Calculate AVK in VMR/VMR units
    #-------------------------------
    Kx          = K[:,x_start:x_stop]
    #Iapriori    = np.zeros((n_layer,n_layer))
    #IaprioriInv = np.zeros((n_layer,n_layer))
    #np.fill_diagonal(Iapriori,sumVars.aprfs[primgas.upper()])
    #np.fill_diagonal(IaprioriInv, 1.0 / (sumVars.aprfs[primgas.upper()]))
    AKxVMR      =  AK[x_start:x_stop,x_start:x_stop]*np.tensordot(sumVars.aprfs[primgas.upper()],sumVars.aprfs[primgas.upper()]**-1,0) #np.dot(np.dot(Iapriori,Dx),np.dot(Kx,IaprioriInv)) #
    #print np.allclose(AKxVMR,AK[x_start:x_stop,x_start:x_stop]*np.tensordot(sumVars.aprfs[primgas.upper()],sumVars.aprfs[primgas.upper()]**-1,0))

    #-----------------------------------------------
    # Get unscaled Averaging Kernel for the 
    # retrieved profile of the gas in questions only
    #-----------------------------------------------
    AKx = AK[x_start:x_stop,x_start:x_stop]
    #----------------------------------
    # Calculate retrieved total column:
    # molec/cm**2
    #----------------------------------
    retdenscol = sumVars.rprfs[primgas.upper()+'_TC']  

    #---------------------------
    # Determine DOFS for column:
    #
    #---------------------------
    col_dofs = np.trace(AKx)

    #------------------------------------------------------------
    # Initialize dictionary of all calculated random error data,
    # including: convariance matrices, percent errors, and labels
    #------------------------------------------------------------
    S_ran = {}

    #---------------------------------------------------------------
    # Initialize dictionary of all calculated systematic error data,
    # including: convariance matrices, percent errors, and labels
    #---------------------------------------------------------------
    S_sys = {}

    #---------------------------------
    # Calculate Smoothing error                
    #                               T
    #      Ss = (A-I) * Sa * (A-I)
    #---------------------------------
    mat1               = sa[x_start:x_stop,x_start:x_stop]
    mat2               = AKx - np.identity( AKx.shape[0] )
    #print 'systematic smoothing'
    S_ran['smoothing'] = calcCoVar(mat1,mat2,sumVars.aprfs[primgas.upper()],sumVars.aprfs['AIRMASS'])
    S_sys['smoothing'] = calcCoVar(sa_syst[x_start:x_stop,x_start:x_stop],mat2,sumVars.aprfs[primgas.upper()],sumVars.aprfs['AIRMASS'])

    #----------------------------------
    # Calculate Measurement error using 
    # SNR calculated from the spectrum
    #                    T
    #  Sm = Dx * Se * Dx
    #----------------------------------
    #print 'random noise',
    S_ran['measurement'] = calcCoVar(se,Dx,sumVars.aprfs[primgas.upper()],sumVars.aprfs['AIRMASS'])

    #---------------------
    # Interference Errors:
    #---------------------
    #------------------------
    # 1) Retrieval parameters
    #------------------------
    AK_int1                   = AK[x_start:x_stop,0:x_start]  
    Sa_int1                   = sa[0:x_start,0:x_start]
    #print 'random retr. params',
    S_ran['retrieval_parameters'] = calcCoVar(Sa_int1,AK_int1,sumVars.aprfs[primgas.upper()],sumVars.aprfs['AIRMASS'])

    #-----------------------
    # 2) Interfering species
    #-----------------------
    n_int2                     = n_profile + n_column - 1
    n_int2_column              = ( n_profile - 1 +bool(temp_retrieval_flag) ) * n_layer + n_column
    AK_int2                    = AK[x_start:x_stop, x_stop:x_stop + n_int2_column] 
    Sa_int2                    = sa[x_stop:x_stop + n_int2_column, x_stop:x_stop + n_int2_column]
    #print 'random/systematic interfering specs'
    S_ran['interfering_species'] = calcCoVar(Sa_int2,AK_int2,sumVars.aprfs[primgas.upper()],sumVars.aprfs['AIRMASS'])
    S_sys['interfering_species'] = calcCoVar(sa_syst[x_stop:x_stop + n_int2_column, x_stop:x_stop + n_int2_column],AK_int2,sumVars.aprfs[primgas.upper()],sumVars.aprfs['AIRMASS'])
    #******************************************************************************************
    #-------------------------------------------
    # This is temprorary: calculate uncertainty
    # associated with variability of water vapor
    # Assume water is retrieved as profile
    #-------------------------------------------
    #H2Oind = [ind for ind,val in enumerate(K_param) if val == 'H2O']
    #AK_H2O = AK[x_start:x_stop,H2Oind]

    #diagFill = np.array(SbctlFileVars.inputs['sb.h2o.random'])
    #diagFill = diagFill / sumVars.aprfs['H2O']
    #Sb       = np.zeros((AK_H2O.shape[1],AK_H2O.shape[1]))
    #np.fill_diagonal(Sb,diagFill**2)
    #S_ran['H2O'] = calcCoVar(Sb,AK_H2O,sumVars.aprfs[primgas.upper()],sumVars.aprfs['AIRMASS'])
    #******************************************************************************************

    #----------------------------------------------
    # Errors from parameters not retrieved by sfit4
    #----------------------------------------------
    #-------------------------------------------------
    # Determine which microwindows retrieve for zshift
    #-------------------------------------------------
    bands = {}
    for k in ctlFileVars.inputs['band']:
        test1 = ctlFileVars.inputs['band.'+str(int(k))+'.zshift'][0].upper()
        try:    test2 = ctlFileVars.inputs['band.'+str(int(k))+'.zshift.type'][0]            # This parameter might not exist in the ctl file if zshift = false
        except KeyError: test2 = 1 
        if (test1 == 'F' and True+(test2 == 1)): bands.setdefault('zshift',[]).append(int(k))        # only include bands where zshift is NOT retrieved

        #--------------------------------------------------------------------
        # Set band ordering for micro-window dependent Sb's other than zshift
        #--------------------------------------------------------------------
        bands.setdefault('other',[]).append(int(k))

    #-------------------------------------------------------------------
    # Get kb.profile.gas(es) list from sfit4.ctl file. These are used 
    # to calculate errors on profile of gases not retrieved as profiles.
    #-------------------------------------------------------------------
    try:             kb_profile_gas = ctlFileVars.inputs['kb.profile.gas']
    except KeyError: kb_profile_gas = []
    
    #print 'Profile uncertainty for %s'%','.join(kb_profile_gas)

    #----------------------------------------------------------------
    # If file exists that has full covariances of Sb's read this file
    #----------------------------------------------------------------
    sbCovarRand = {}
    sbCovarSys  = {}
    
    if "sb.file.random" in SbctlFileVars.inputs: #the sb.file.random contains a list of parameters for which a file input is provided
        sbCovarRand = readCovarFile(SbctlFileVars.inputs["sb.file.random"],'random')
        if not sbCovarRand: return False # Critical file missing terminate program
    if "sb.file.systematic" in SbctlFileVars.inputs:
        sbCovarSys = readCovarFile(SbctlFileVars.inputs["sb.file.systematic"],'systematic')        
        if not sbCovarSys: return False # Critical file missing terminate program
    if sbCovarSys or sbCovarRand: 'Found covariance matrices for %s (random) and %s (systematic)'%(', '.join(sbCovarRand.keys()),', '.join(sbCovarSys.keys()))
    #--------------------------------
    # Loop through parameter list and
    # determine errors
    # Kbl is the label used in the ctl file
    #--------------------------------

    print ('\nCalculating uncertainty contributions for %s\n'%', '.join(Kb.keys()))

    for Kbl in Kb:
        DK = np.dot(Dx,Kb[Kbl])
        for ErrType in ['random','systematic']:

            #-------------------------------------------
            # Pre-allocate Sb matrix based on size of Kb
            #-------------------------------------------
            Sb    = np.zeros((DK.shape[1],DK.shape[1]))
            sbFlg = False
            try:
                #----------------------------------------------------------------------------------
                # Get elements for Sb matrices. If a file name is present, the file is read as the 
                # Sb matrix. Some special cases require seperate handling
                #----------------------------------------------------------------------------------
                if ErrType == "random":
                    if Kbl.lower() in sbCovarRand:
                        Sb = sbCovarRand[Kbl.lower()]
                        sbFlg = True
                    elif Kbl.upper() in sbCovarRand and Kbl.upper() in [x.upper() for x in kb_profile_gas]: #i do not understand yet when the upper occurs
                        Sb = sbCovarRand[Kbl.upper()]
                        sbFlg = True
                elif ErrType == "systematic":
                    if Kbl.lower() in sbCovarSys: 
                        Sb = sbCovarSys[Kbl.lower()]
                        sbFlg = True   
                    elif Kbl.upper() in sbCovarSys and Kbl.upper() in [x.upper() for x in kb_profile_gas]:
                        Sb = sbCovarSys[Kbl.upper()]
                        sbFlg = True

                        
                if not sbFlg:
                    #-------
                    # Zshift
                    #-------
                    if Kbl.lower() == 'zshift': 
                        diagFill = np.array( [ SbDict['sb.band.'+str(x)+'.zshift.'+ErrType][0]  for x in bands['zshift'] ])
    
                    #---------------------------------
                    # Temperature (in case of scaling)
                    #---------------------------------
                    elif (Kbl.lower() == 'temperature') and (SbDict['sb.temperature.'+ErrType+'.scaled'][0].upper() == 'F'):
                        diagFill = np.array(SbDict['sb.temperature.'+ErrType])
                        if len(diagFill) != len(sumVars.aprfs['TEMPERATURE']): raise ExitError('Number of Sb for temperature, type:'+ErrType+' does not match atmospheric layers!!')
                        diagFill = diagFill / sumVars.aprfs['TEMPERATURE']


                    #------------
                    # Profile Gas
                    #------------
                    elif Kbl.upper() in [x.upper() for x in kb_profile_gas]:
                        diagFill = np.array(SbDict['sb.profile.'+Kbl+'.'+ErrType])
    
                    #-------------------------
                    # SZA (in case of scaling)
                    #-------------------------
                    elif (Kbl.lower() == 'sza') and (SbDict['sb.sza.'+ErrType+'.scaled'][0].upper() == 'F'):
                        if len(SbDict['sb.'+Kbl+'.'+ErrType]) != DK.shape[1]: raise ExitError('Number of specified Sb for SZA, type:'+ErrType+' does not match number of Kb columns!! Check Sb.ctl file.')
                        diagFill = np.array(SbDict['sb.sza.'+ErrType]) / sumVars.pbp['sza'][:Sb.shape[0]] #the shape of the sza in the summary is mw dependent...
    
                    #---------------------------------
                    # Omega (FOV) (in case of scaling)
                    #---------------------------------
                    elif (Kbl.lower() == 'omega') and (SbDict['sb.omega.'+ErrType+'.scaled'][0].upper() == 'F'):
                        if len(SbDict['sb.'+Kbl+'.'+ErrType]) != DK.shape[1]: raise ExitError('Number of specified Sb for omega, type:'+ErrType+' does not match number of Kb columns!! Check Sb.ctl file.')
                        diagFill = np.array(SbDict['sb.omega.'+ErrType]) / sumVars.summary['FOVDIA']
    
                    #----------------
                    # All other cases
                    #----------------
                    else: 
                        #--------------------------------------------------------------------
                        # Catch errors where number of specified Sb does not match Kb columns (in a flexible way)
                        #--------------------------------------------------------------------
                        #print type(Kbl),Kbl,'onee',type(SbDict['sb.'+Kbl+'.'+ErrType]),DK.shape,'ole'
                        #print 'aaaa','sb.'+Kbl+'.'+ErrType,'bbb'
                        sbsize=len(SbDict['sb.'+Kbl+'.'+ErrType])
                        kbsize=DK.shape[1]
                        if sbsize != 1 and sbsize<kbsize: raise ExitError('Number of specified Sb for '+Kbl+', type:'+ErrType+'(=%s) does not match number of Kb columns=%s!! Check Sb.ctl file.'%(sbsize,kbsize,))
                        diagFill = np.array((SbDict['sb.'+Kbl+'.'+ErrType]*(kbsize if sbsize==1 else 1))[:kbsize]) 
                        
    
                    #--------------------------------------
                    # Fill Sb matrix with diagonal elements
                    #--------------------------------------
                    sbcorkey='sb.%s.correlation.width'%Kbl if Kbl.upper() not in map(str.upper,kb_profile_gas) else 'sb.profile.%s.correlation.width'%Kbl
                    Sb=createCovar(diagFill,**(dict(sbcorkey=sbcorkey,z=z,Sbctldict=SbDict) if (ErrType=='random' and (Kbl.upper() in map(str.upper,kb_profile_gas+['TEMPERATURE']))) else {}))
                    if np.array_equal(Sb,None): print('Error building covariance matrix for %s'%sbcorkey);raise ValueError('Bad setting for %s'%sbcorkey)
                    
                #do some post calibration when matrices are read from input files: input files are assumed in SI units (as the data in sumVars.aprfs)... ok?     
                elif Kbl=='temperature' or (Kbl.upper() in kb_profile_gas): 
                  # temperature and profile_gas sb should be put in relative units when read from input file
                  l,d=np.linalg.eigh(Sb)
                  sqrtL=np.sqrt(np.ma.masked_array(l,l<0).filled(0)) #correct for negative eigenvalues and take the sqrt
                  D=sqrtL*d #Sb=D.dot(D.T)
                  DtempT=((sumVars.aprfs[Kbl.upper()]**-1)*(D.T)) # (D.T).dot(diag(temp**-1))
                  Sb=DtempT.T.dot(DtempT)#diag(temp^-1).dot(Sb).dot(diag(temp^-1))

                             
                  
                #-----------------------------------------------------
                # Test if Sb matrix is symmetric and positive definite
                #-----------------------------------------------------
                (symRtn,pdRtn) = matPosDefTest(Sb)
                if not symRtn: print ("Warning!! The Sb matrix is not symmetric\n\n")
                if not pdRtn:  print ("Warning!! The Sb matrix is not positive definite\n\n")

            #-----------------------------------------------
            # Catch instances where DK exists for parameter; 
            # however, no Sb is specified
            #-----------------------------------------------
            except KeyError as kerr:
                print ('Missing Sb for ',repr(kerr))
                if logFile: logFile.error('Covariance matrix for '+Kbl+': Error type -- ' + ErrType+' not calculated. Sb does not exist\n')

            #-----------------------------------
            # Exceptions for terminating program
            #-----------------------------------
            except ExitError as err:
                print (err.msg)
                err.terminate()

            #--------------------------------------
            # Catch all other errors in calculation
            #--------------------------------------
            except: 
                errmsg = sys.exc_info()[1]
                print ('Error calculating error covariance matrix for '+Kbl+': Error type -- ' + ErrType)
                print (errmsg)
                if logFile: logFile.error('Error calculating error covariance matrix for '+Kbl+': Error type -- ' + ErrType+'\n')

            #----------------------------------------------------------------------
            # Check if Error covariance matrix has not been filled from sb.ctl file
            #----------------------------------------------------------------------
            if np.sum(Sb) == 0:
                if (Kbl.lower() == 'zshift') and logFile: 
                    logFile.info('sb.band.x.zshift.'+ErrType+' for all bands where zshift is not retrieved is 0 or not specifed => error covariance matrix not calculated')
                elif (Kbl.upper() in [x.upper() for x in kb_profile_gas]) and logFile:
                    logFile.info('sb.profile.'+Kbl+'.'+ErrType+' is 0 or not specified => error covariance matrix not calculated')          
                elif logFile:               
                    logFile.info('sb.'+Kbl+'.'+ErrType+' is 0 or not specified => error covariance matrix not calculated')

            #----------
            # Calculate
            #----------
            else:
                if ErrType == 'random': S_ran[Kbl] = calcCoVar(Sb,DK,sumVars.aprfs[primgas.upper()],sumVars.aprfs['AIRMASS'])
                else:                   S_sys[Kbl] = calcCoVar(Sb,DK,sumVars.aprfs[primgas.upper()],sumVars.aprfs['AIRMASS'])
                if Kbl.lower() in ('temperature','h2o'): 
                    appc=sumVars.aprfs[primgas.upper()]*sumVars.aprfs['AIRMASS']
                    rtpc=sumVars.rprfs[primgas.upper()]*sumVars.aprfs['AIRMASS']
                    tce=np.sqrt(appc.dot(DK.dot(Sb).dot(DK.T)).dot(appc))
                    #print ('TC error for %-22s: %4.3e[molec/cm^2]\t%4.2f%%'%('%s.%s'%(Kbl,ErrType),tce,tce/rtpc.sum()*100))
                    

    #---------------------------------------------
    # Calculate total systematic and random errors
    #---------------------------------------------
    # Initialize total random and systematic
    S_tot                = {}
    S_tot_rndm_err       = 0
    S_tot_systematic_err = 0

    if  SbDict['vmroutflg'][0].upper() == 'T': 
        S_tot_ran_vmr   = np.zeros((n_layer,n_layer))
        S_tot_sys_vmr   = np.zeros((n_layer,n_layer))

    if  SbDict['molsoutflg'][0].upper() =='T': 
        S_tot_ran_molcs = np.zeros((n_layer,n_layer))
        S_tot_sys_molcs = np.zeros((n_layer,n_layer))

    # Get a list of parameters to include in total error from sb.ctl file
    # Random
    for k in S_ran:
        totkey='sb.total.'+k
        if (totkey in SbDict) and SbDict[totkey][0].upper() == 'T':
            S_tot_rndm_err  += S_ran[k][2]**2 #this is the uncertainty on the total column
            if  SbDict['vmroutflg'][0].upper()  =='T': S_tot_ran_vmr   += S_ran[k][0]
            else:                            S_tot_ran_vmr    = 0
            if  SbDict['molsoutflg'][0].upper() =='T': S_tot_ran_molcs += S_ran[k][1]
            else:                                                    S_tot_ran_molcs  = 0

    S_tot_rndm_err  = np.sqrt(S_tot_rndm_err)

    # Systematic
    for k in S_sys:
        totkey='sb.total.'+k
        if (totkey in SbDict) and SbDict[totkey][0].upper() == 'T' :
            S_tot_systematic_err += S_sys[k][2]**2
            if  SbDict['vmroutflg'][0].upper()  =='T': S_tot_sys_vmr   += S_sys[k][0]
            else:                            S_tot_sys_vmr    = 0
            if  SbDict['molsoutflg'][0].upper() =='T': S_tot_sys_molcs += S_sys[k][1]
            else:                            S_tot_sys_molcs  = 0 

    S_tot_systematic_err = np.sqrt(S_tot_systematic_err)
    S_tot['Random']      = (S_tot_ran_vmr,S_tot_ran_molcs,S_tot_rndm_err)
    S_tot['Systematic']  = (S_tot_sys_vmr,S_tot_sys_molcs,S_tot_systematic_err)

                                        #---------------#
                                        # Write outputs #
                                        #---------------#

    #--------------------------
    # Error summary information
    #--------------------------      
    with open(wrkingDir+SbDict['file.out.error.summary'][0], 'w') as fout:
        fout.write('sfit4 ERROR SUMMARY\n\n')
        fout.write('Primary gas                                       = {0:>15s}\n'.format(primgas.upper())                                  )
        fout.write('Total column amount                               = {0:15.5E} [molecules cm^-2]\n'.format(retdenscol)                    )
        fout.write('DOFs (total column)                               = {0:15.3f}\n'.format(col_dofs)                                        )
        fout.write('Smoothing error (Ss, using sa)                    = {0:15.3f} [%]\n'.format(S_ran['smoothing'][2]        /retdenscol*100))
        fout.write('Measurement error (Sm)                            = {0:15.3f} [%]\n'.format(S_ran['measurement'][2]      /retdenscol*100))
        fout.write('Interference error (retrieved params)             = {0:15.3f} [%]\n'.format(S_ran['retrieval_parameters'][2] /retdenscol*100))
        fout.write('Interference error (interfering spcs)             = {0:15.3f} [%]\n'.format(S_ran['interfering_species'][2]/retdenscol*100))
        
        if not temp_retrieval_flag:
          fout.write('Temperature (Random)                              = {0:15.3f} [%]\n'.format(S_ran['temperature'][2] /retdenscol*100)     )
          fout.write('Temperature (Systematic)                          = {0:15.3f} [%]\n'.format(S_sys['temperature'][2] /retdenscol*100)     )
        if 'h2o' in S_ran: fout.write('Water Vapor (Random)                              = {0:15.3f} [%]\n'.format(S_ran['h2o'][2]/retdenscol*100)              )
        if 'h2o' in S_sys: fout.write('Water Vapor (Systematic)                         = {0:15.3f} [%]\n'.format(S_sys['h2o'][2]/retdenscol*100)              )
        
        fout.write('Total random error                                = {0:15.3f} [%]\n'.format(S_tot['Random'][2]           /retdenscol*100))
        fout.write('Total systematic error                            = {0:15.3f} [%]\n'.format(S_tot['Systematic'][2]       /retdenscol*100))
        fout.write('Total random uncertainty                          = {0:15.3E} [molecules cm^-2]\n'.format(S_tot['Random'][2])            )
        fout.write('Total systematic uncertainty                      = {0:15.3E} [molecules cm^-2]\n'.format(S_tot['Systematic'][2])        )
        for k in S_ran: 
            fout.write('Total random uncertainty {0:<24s} = {1:15.3E} [molecules cm^-2] \t {2:15.3f} [%]\n'.format(k,S_ran[k][2],S_ran[k][2]/retdenscol*100))
        for k in S_sys:
            fout.write('Total systematic uncertainty {0:<20s} = {1:15.3E} [molecules cm^-2] \t {2:15.3f} [%]\n'.format(k,S_sys[k][2],S_sys[k][2]/retdenscol*100))

    #-----------------------------------
    # Write to file covariance matricies
    #-----------------------------------
    if SbDict['out.total'][0].upper() == 'T':
        if SbDict['molsoutflg'][0].upper() == 'T':
            # molecules cm^-2
            fname  = wrkingDir+SbDict['file.out.total'][0]
            header = 'TOTAL RANDOM ERROR COVARIANCE MATRIX IN (MOL CM^-2)^2'
            writeCoVar(fname,header,S_tot,1) 

        if SbDict['vmroutflg'][0].upper() == 'T':
            # vmr
            fname  = wrkingDir+SbDict['file.out.total.vmr'][0]
            header = 'TOTAL RANDOM ERROR COVARIANCE MATRICES IN (VMR)^2 UNITS'
            writeCoVar(fname,header,S_tot,0)    

    if SbDict['out.srandom'][0].upper() == 'T':
        if SbDict['molsoutflg'][0].upper() == 'T':
            # molecules cm^-2
            fname  = wrkingDir+SbDict['file.out.srandom'][0]
            header = 'RANDOM ERROR COVARIANCE MATRIX IN (MOL CM^-2)^2'
            writeCoVar(fname,header,S_ran,1)

        if SbDict['vmroutflg'][0].upper() == 'T':
            # vmr
            fname  = wrkingDir+SbDict['file.out.srandom.vmr'][0]
            header = 'RANDOM ERROR COVARIANCE MATRICES IN (VMR)^2 UNITS'
            writeCoVar(fname,header,S_ran,0)    

    if SbDict['out.ssystematic'][0].upper() == 'T':

        if SbDict['molsoutflg'][0].upper() == 'T':
            # molecules cm^-2
            fname  = wrkingDir+SbDict['file.out.ssystematic'][0]
            header = 'SYSTEMATIC ERROR COVARIANCE MATRIX IN (MOL CM^-2)^2'
            writeCoVar(fname,header,S_sys,1)

        if SbDict['vmroutflg'][0].upper() == 'T':
            # vmr
            fname  = wrkingDir+SbDict['file.out.ssystematic.vmr'][0]
            header = 'SYSTEMATIC ERROR COVARIANCE MATRICES IN (VMR)^2 UNITS'
            writeCoVar(fname,header,S_sys,0)    

    #-----------------------
    # Write Averaging Kernel
    #-----------------------
    fname      = wrkingDir+SbDict['file.out.avk'][0]    
    header     = 'Averaging Kernel for '+ primgas.upper()
    AVK        = {}
    AVK['AVK_scale_factor'] = (AKx,[],[])
    AVK['AVK_VMR']          = (AKxVMR,[],[])
    writeCoVar(fname,header,AVK,0)

    #try: 
    #   raytrace_header,line_of_sight=sumVars.readRaytrace(wrkingDir + 'raytrace.out',longitude=20.,azimuth=20.,target_grid=sumVars.aprfs['Z']*1e3) #raytrace.out is the default...better to take file.out.raytrace? 
    #   print(raytrace_header,line_of_sight)
    #except: pass
    
    return True
