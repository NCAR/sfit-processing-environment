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
#	1) Call to sfitClasses to run subProcRun. This handles stdout and stderr of a sub-process call		
#
#
# Notes:
#       1)
#			
#
#
# Version History:
#       Created, June, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
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
from numpy        import copy, dot
from numpy.linalg import norm
import sfitClasses       as sc
import numpy             as np
import itertools         as it
import printStatmnts     as ps
import datetime          as dt

from scipy import interpolate

import matplotlib.pyplot as plt


                                #--------------------------#
                                #                          #
                                #  -- Helper functions --  #
                                #                          #
                                #--------------------------#
def tryopen(fname,logFile=False):
    try:
        with open(fname, 'r' ) as fopen:
            return fopen.readlines()
    except IOError as errmsg:
        print errmsg
        if logFile: logFile.error(errmsg)
        return False


class ExceededMaxIterationsError(Exception):
    def __init__(self, msg, matrix=[], iteration=[], ds=[]):
        self.msg = msg
        self.matrix = matrix
        self.iteration = iteration
        self.ds = ds

    def __str__(self):
        return repr(self.msg)


def nearcorr(A, tol=[], flag=0, max_iterations=100, n_pos_eig=0,
             weights=None, verbose=False,
             except_on_too_many_iterations=True):
    """
    X = nearcorr(A, tol=[], flag=0, max_iterations=100, n_pos_eig=0,
        weights=None, print=0)

    Finds the nearest correlation matrix to the symmetric matrix A.

    ARGUMENTS
    ~~~~~~~~~
    A is a symmetric numpy array or a ExceededMaxIterationsError object

    tol is a convergence tolerance, which defaults to 16*EPS.
    If using flag == 1, tol must be a size 2 tuple, with first component
    the convergence tolerance and second component a tolerance
    for defining "sufficiently positive" eigenvalues.

    flag = 0: solve using full eigendecomposition (EIG).
    flag = 1: treat as "highly non-positive definite A" and solve
    using partial eigendecomposition (EIGS). CURRENTLY NOT IMPLEMENTED

    max_iterations is the maximum number of iterations (default 100,
    but may need to be increased).

    n_pos_eig (optional) is the known number of positive eigenvalues
    of A. CURRENTLY NOT IMPLEMENTED

    weights is an optional vector defining a diagonal weight matrix diag(W).

    verbose = True for display of intermediate output.
    CURRENTLY NOT IMPLEMENTED

    except_on_too_many_iterations = True to raise an exeption when
    number of iterations exceeds max_iterations
    except_on_too_many_iterations = False to silently return the best result
    found after max_iterations number of iterations

    ABOUT
    ~~~~~~
    This is a Python port by Michael Croucher, November 2014
    Thanks to Vedran Sego for many useful comments and suggestions.

    Original MATLAB code by N. J. Higham, 13/6/01, updated 30/1/13.
    Reference:  N. J. Higham, Computing the nearest correlation
    matrix---A problem from finance. IMA J. Numer. Anal.,
    22(3):329-343, 2002.
    """

    # If input is an ExceededMaxIterationsError object this
    # is a restart computation
    if (isinstance(A, ExceededMaxIterationsError)):
        ds = copy(A.ds)
        A = copy(A.matrix)
    else:
        ds = np.zeros(np.shape(A))

    eps = np.spacing(1)
    if not np.all((np.transpose(A) == A)):
        raise ValueError('Input Matrix is not symmetric')
    if not tol:
        tol = eps * np.shape(A)[0] * np.array([1, 1])
    if weights is None:
        weights = np.ones(np.shape(A)[0])
    X = copy(A)
    Y = copy(A)
    rel_diffY = inf
    rel_diffX = inf
    rel_diffXY = inf

    Whalf = np.sqrt(np.outer(weights, weights))

    iteration = 0
    while max(rel_diffX, rel_diffY, rel_diffXY) > tol[0]:
        iteration += 1
        if iteration > max_iterations:
            if except_on_too_many_iterations:
                if max_iterations == 1:
                    message = "No solution found in "\
                              + str(max_iterations) + " iteration"
                else:
                    message = "No solution found in "\
                              + str(max_iterations) + " iterations"
                raise ExceededMaxIterationsError(message, X, iteration, ds)
            else:
                # exceptOnTooManyIterations is false so just silently
                # return the result even though it has not converged
                return X

        Xold = copy(X)
        R = X - ds
        R_wtd = Whalf*R
        if flag == 0:
            X = proj_spd(R_wtd)
        elif flag == 1:
            raise NotImplementedError("Setting 'flag' to 1 is currently\
                                 not implemented.")
        X = X / Whalf
        ds = X - R
        Yold = copy(Y)
        Y = copy(X)
        np.fill_diagonal(Y, 1)
        normY = norm(Y, 'fro')
        rel_diffX = norm(X - Xold, 'fro') / norm(X, 'fro')
        rel_diffY = norm(Y - Yold, 'fro') / normY
        rel_diffXY = norm(Y - X, 'fro') / normY

        X = copy(Y)

    return X


def proj_spd(A):
    # NOTE: the input matrix is assumed to be symmetric
    d, v = np.linalg.eigh(A)
    A = (v * np.maximum(d, 0)).dot(v.T)
    A = (A + A.T) / 2
    return(A)



                                #-------------------------#
                                #                         #
                                #   -- NCAR Refmaker --   #
                                #                         #
                                #-------------------------#


def refMkrNCAR(zptwPath, WACCMfile, outPath, lvl, wVer, zptFlg, specDB, spcDBind, logFile=False):
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
        print errmsg
        if logFile: logFile.error(errmsg)
        return False

    #--------------
    # Find ZPT file
    #--------------
    if zptFlg: zptFiles = glob.glob(zptwPath + 'ZPT.nmc*')
    else     : zptFiles = glob.glob(zptwPath + 'zpt-120')

    # If more than one zpt file found trigger warning and use first one 
    if len(zptFiles) > 1:                 
        print 'Found more than one ZPT file. Using file: ' + zptFiles[0]
        if logFile: logFile.info('Using ZPTW file: ' + zptFiles[0])
        zptFile = zptFiles[0]

    # If no zpt files found trigger error    
    elif len(zptFiles) == 0:              
        print 'No zpt files found in: ' + zptwPath
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
        print 'No water files found in: ' + zptwPath
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
        # If water version == 99 find the closest water
        # to retrieval
        #------------------------------------------------
        if waterInd and wVer == 99:
            waterNames = [os.path.basename(waterFiles[i]) for i in waterInd]
            waterDates = [dt.datetime(int(x.strip().split('.')[1][0:4]),int(x.strip().split('.')[1][4:6]),int(x.strip().split('.')[1][6:]),
                                      int(x.strip().split('.')[2][0:2]),int(x.strip().split('.')[2][2:4]),int(x.strip().split('.')[2][4:])) for x in waterNames]
            
            obsDate = dt.datetime(int(str(int(specDB['Date'][spcDBind]))[0:4]),int(str(int(specDB['Date'][spcDBind]))[4:6]),int(str(int(specDB['Date'][spcDBind]))[6:]),
                                  int(specDB['Time'][spcDBind].split(':')[0]),int(specDB['Time'][spcDBind].split(':')[1]),int(specDB['Time'][spcDBind].split(':')[2]))
            
            nearstD  = sc.nearestTime(waterDates,obsDate.year,obsDate.month,obsDate.day,obsDate.hour,obsDate.minute,obsDate.second)    
            indTemp  = waterDates.index(nearstD) 
            waterInd = waterFiles.index(zptwPath+waterNames[indTemp]) 

        #------------------------------------------------
        # If water version == 66 (ERA) find the closest in time to retrieval
        #------------------------------------------------
        elif waterInd and wVer == 66:
            waterNames = [os.path.basename(waterFiles[i]) for i in waterInd]

            waterDates = [dt.datetime(int(x.strip().split('.')[1][0:4]),int(x.strip().split('.')[1][4:6]),int(x.strip().split('.')[1][6:]),
                                      int(x.strip().split('.')[2][0:2]),int(x.strip().split('.')[2][2:4]),int(x.strip().split('.')[2][4:])) for x in waterNames]
            
            obsDate = dt.datetime(int(str(int(specDB['Date'][spcDBind]))[0:4]),int(str(int(specDB['Date'][spcDBind]))[4:6]),int(str(int(specDB['Date'][spcDBind]))[6:]),
                                  int(specDB['Time'][spcDBind].split(':')[0]),int(specDB['Time'][spcDBind].split(':')[1]),int(specDB['Time'][spcDBind].split(':')[2]))
            
            nearstD  = sc.nearestTime(waterDates,obsDate.year,obsDate.month,obsDate.day,obsDate.hour,obsDate.minute,obsDate.second)    
            indTemp  = waterDates.index(nearstD) 
            waterInd = waterFiles.index(zptwPath+waterNames[indTemp])

        #------------------------------------------------

        elif not waterInd:
            print 'Water version {0:d} not found, using latest version: {1:d} '.format(wVer,max(waterVer))
            if logFile: logFile.error('Water version %d not found, using latest version'% wVer)
            waterInd = waterVer.index(max(waterVer))
            
        else: waterInd = waterInd[0]
              
    waterFile = waterFiles[waterInd]
    
    print '\n'
    print 'Using water file: {}'.format(waterFile)
    print '\n'


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
                            print 'Surface pressure error for reference profile: ' + refFile
                            print 'External surface pressure < NCEP pressure one level above surface => Non-hydrostatic equilibrium!!'
                        elif ( abs(float(oldPres) - float(newPres)) > 15):
                            if logFile:
                                logFile.warning('Surface pressure warning for reference profile: ' + refFile)
                                logFile.warning('Difference between NCEP and external station surface pressure > 15 hPa')
                            print 'Surface pressure warning for reference profile: ' + refFile
                            print 'Difference between NCEP and external station surface pressure > 15 hPa'

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
                            print 'Surface Temperature error for reference profile: ' + refFile
                            print 'External surface temperature < NCEP temperature one level above surface => Non-hydrostatic equilibrium!!'
                        elif ( abs(float(oldTemp) - float(newTemp)) > 10):
                            if logFile:
                                logFile.warning('Surface temperature warning for reference profile: ' + refFile)
                                logFile.warning('Difference between NCEP and external station surface temperature > 10 DegC')
                            print 'Surface temperature warning for reference profile: ' + refFile
                            print 'Difference between NCEP and external station surface temperature > 10 DegC'                        

                        lines[nlnum] = lines[nlnum].replace(oldTemp,newTemp)                    


    with open( refFile, 'w' ) as fout:
        for line in lines:
            fout.write(line)
    
    #-------------------------#
    #Auto-Update isotope Prf in the isotope.input --> Initially created and tested for HDO at MLO
    #-------------------------#
    isotopePrep(refFile)
    

    return True

                        #-------------------------#
                        #                         #
                        #    -- isotopePrep --     #
                        #                         #
                        #-------------------------#    

def isotopePrep(refFile):

    print '*****************************************************'
    print                'Running isotopePrep'
    print '*****************************************************'

    parms   = ['ALTITUDE', 'H2O']
    refPrf  = {}

    with open(refFile,'r') as fopen: lines = fopen.readlines()

    #----------------------------------------
    # Get Altitude, Pressure, and Temperature
    # from reference.prf file
    #----------------------------------------
    nlyrs  = int(lines[0].strip().split()[1])
    nlines = int(np.ceil(nlyrs/5.0))
        
    for ind,line in enumerate(lines):
        if any(p in line.strip().split() for p in parms):
            val = [x for x in parms if x in line][0]
            refPrf.setdefault(val,[]).append([float(x[:-1]) for row in lines[ind+1:ind+nlines+1] for x in row.strip().split()])

    for p in parms:
        refPrf[p] = np.asarray(refPrf[p])

    #--------------------------------------
    # Un-nest numpy arrays in parm dictionary
    #--------------------------------------
    for k in parms: refPrf[k] = refPrf[k][0]   

    #--------------
    # Read dD - Matthias
    #--------------
    dDFile='/data1/ebaumer/mlo/hdo/dD_CRprior_ext.txt'

    with open(dDFile, 'r' ) as fopen:
        lines = fopen.readlines()

    altdD     = np.array([[float(x) for x in row.split()[0:1]] for row in lines[1:]])
    dDPrf     = np.array([[float(x) for x in row.split()[1:2]] for row in lines[1:]])

    dDPrf = np.flipud(dDPrf.flatten())
    altdD = np.flipud(altdD.flatten())

    #--------------
    # Read H2O - Matthias
    #--------------
    wpFile='/data1/ebaumer/mlo/hdo/H2O_CRprior_ext.txt'

    with open(wpFile, 'r' ) as fopen:
        lines = fopen.readlines()

    altwp     = np.array([[float(x) for x in row.split()[0:1]] for row in lines[1:]])
    wpPrf      = np.array([[float(x) for x in row.split()[1:2]] for row in lines[1:]])
   
    wpPrf = np.flipud(wpPrf.flatten())
    altwp = np.flipud(altwp.flatten())

    #--------------------------------------
    # Interpolate dDPrf to Ref Prf Altitude
    #--------------------------------------

    dDPrfInt  = interpolate.interp1d(altdD, dDPrf, bounds_error=False, fill_value=(dDPrf[-1], dDPrf[0]))(refPrf[parms[0]])
    wpPrfInt  = interpolate.interp1d(altwp, wpPrf, bounds_error=False, fill_value=(dDPrf[-1], dDPrf[0]))(refPrf[parms[0]])*1e-6

    #--------------------------------------
    # Calculate HDO Prf
    #--------------------------------------
    hdoPrf_1 = (3.1152e-4)*(wpPrfInt)*( (dDPrfInt/1000.0) + 1)
    hdoPrf_1 = hdoPrf_1/3.107e-4

    hdoPrf_2 = (3.1152e-4)*(refPrf[parms[1]])*( (dDPrfInt/1000.0) + 1)
    hdoPrf_2 = hdoPrf_2/3.107e-4

    
    isoFile = '/data1/ebaumer/mlo/hdo/x.hdo/isotope.input2'

    with open(isoFile, 'r+' ) as fout:
        lines    = fout.readlines()
        
        nisot    = int(lines[0].split()[0])
        nlyrs    = int(lines[0].split()[1])
        nlines   = int(np.ceil(nlyrs/5.0))

        for linenum,line in enumerate(lines):
            if (linenum >= 6) & (linenum < 6 + nlyrs):
                nlnum        = linenum + nlyrs
                #oldPrf       = lines[linenum:nlnum]
                #oldPrf       = np.asarray(oldPrf, dtype=float)

                lines[linenum] = str('{0:.4e}'.format(hdoPrf_2[linenum - 6]))+'\n'       


    with open('/data1/ebaumer/mlo/hdo/x.hdo/isotope.input3', 'w' ) as fout:
        for line in lines:
            fout.write(line)

    #---------------------------------
    #Error plots of dD - FTIR
    #---------------------------------
    # fig, ax1 = plt.subplots(1, 2, figsize=(10,7), sharey=True)

    # ax1[0].plot(refPrf[parms[1]]*1e6, refPrf[parms[0]], linewidth=2.0, color='b', label= 'H20 (ERA-I)')
    # ax1[0].plot(hdoPrf_2*1e6, refPrf[parms[0]], linewidth=2.0, color='r', label= 'HDO (scaled)')

    # ax1[0].plot(wpPrfInt*1e6, refPrf[parms[0]], linewidth=2.0, linestyle='--' ,color='b', label='H2O (CRprior)')
    # ax1[0].plot(hdoPrf_1*1e6, refPrf[parms[0]], linewidth=2.0, linestyle='--', color='r', label='HDO (CRprior)')
    
    # ax1[1].plot(refPrf[parms[1]]*1e6, refPrf[parms[0]], linewidth=2.0, color='b')
    # ax1[1].plot(hdoPrf_2*1e6, refPrf[parms[0]], linewidth=2.0, color='r')

    # ax1[1].plot(wpPrfInt*1e6, refPrf[parms[0]], linewidth=2.0, linestyle='--' ,color='b')
    # ax1[1].plot(hdoPrf_1*1e6, refPrf[parms[0]], linewidth=2.0, linestyle='--', color='r')

    # ax1[0].legend(prop={'size':11}, loc=1)

    # ax1[0].set_ylabel('Altitude [km]', fontsize=14)           
    # ax1[0].grid(True,which='both')
    # ax1[0].set_ylim(3, 20)
    # ax1[0].set_xlim(xmin=0)
    # ax1[0].tick_params(which='both',labelsize=14)
    # ax1[0].set_xlabel('VMR [ppm]', fontsize=14)   

    # ax1[1].grid(True,which='both')
    # ax1[1].tick_params(which='both',labelsize=14)
    # ax1[1].set_xscale('log')
    # ax1[1].set_xlabel('VMR [ppm]', fontsize=14)  
         
    # plt.show(block=False)

    #user_input = raw_input('Press any key to exit >>> ')
    #exit()

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
        print 'Unable to find bnr file: {}'.format(wrkInputDir2 + bnrFname)
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
    print 'Running pspec for ctl file: ' + mainInF.inputs['ctlList'][ctl_ind][0] 
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

    def matPosDefTest(mat,findNCMflg=False):
        ''' Test if matrix is positive definite'''
        
        #----------------------------------
        # First test if matrix is symmetric
        #----------------------------------
        symRslt = np.allclose(mat.transpose(),mat)

        #-------------------------------
        # Then test if eignvales are > 0
        #-------------------------------
        eignRslt = np.all(np.linalg.eigvals(mat) > 0)
        
        #-------------------------------------------------
        # If matrix is symmetric but not positive definite
        # we can find the nearest covariance matrix using
        # the method of (Higham, 2002). Not implenmented yet!!!!!!!!
        #-------------------------------------------------
        #if all([symRslt,not eignRslt,findNCMflg]):
            #try:
                #rtnMat = nearcorr(mat)
            #except ExceededMaxIterationsError as e:
                #rtnMat = (symRslt,eignRslt,False)
                
            #return (symRslt,eignRslt,rtnMat)
        
        #----------------------------------------------------------
        # If matrix is symmetric and positive definite, return true
        #----------------------------------------------------------
        #elif all([symRslt,eignRslt]): return (True,True,False)
        
    
        #else: return (symRslt,eignRslt,False)

        return(symRslt,eignRslt)
        

    def calcCoVar(coVar,A,retPrfVMR,airMass):
        ''' Calculate covariance matricies in various units'''

        Sm   = np.dot(  np.dot( A, coVar ), A.T )                                # Uncertainty covariance matrix [Fractional]
        Sm_1 = np.dot(  np.dot( np.diag(retPrfVMR), Sm ), np.diag(retPrfVMR) )   # Uncertainty covariance matrix [(VMR)^2]
        Sm_2 = np.dot(  np.dot( np.diag(airMass), Sm_1 ), np.diag(airMass)   )   # Uncertainty covariance matrix [(molecules cm^-2)^2]
        densPrf = retPrfVMR * airMass
        Sm_3 = np.sqrt( np.dot( np.dot( densPrf, Sm ), densPrf.T )     )         # Whole column uncertainty [molecules cm^-2]
        ##Sm_3 = np.sqrt( np.sum( np.diagonal( Sm_2 ) ) )                          # Whole column uncertainty [molecules cm^-2]
        
        return (Sm_1, Sm_2, Sm_3)     # (Variance, Variance, STD)

    def writeCoVar(fname,header,var,ind):
        ''' Write covariance matricies to files'''
        with open(fname, 'w') as fout:
            fout.write('# ' + header + '\n'                                       )
            fout.write('# nmatr  = {}\n'.format(len(var)                         ))
            fout.write('# nrows  = {}\n'.format(var[var.keys()[0]][0].shape[0]   ))
            fout.write('# ncols  = {}\n\n'.format(var[var.keys()[0]][0].shape[1] )) 
            for k in var:
                fout.write('{}\n'.format(k))

                for row in var[k][ind]:
                    strformat = ' '.join('{:>12.4E}' for i in row) + ' \n'
                    fout.write( strformat.format(*row) )

                fout.write('\n\n')    


    def paramMap(paramName,Kb_labels):
        '''There is discontinuity between the variable names used in sfit ctl file
           and what is output in kb.output. This function helps map the kb.output
           file variable names to what is used in ctl file. Kb_labels are the 
           parameter names as they appear in the ctl file'''

        #----------------------------------
        # Split parameter name if necessary
        #----------------------------------
        if len(paramName.split('_')) == 2: paramName,gas = paramName.split('_')

        #--------------------------------------------------------
        # List of parameters as they appear in the Kb.output file 
        #--------------------------------------------------------
        Kb_labels_orig = ['TEMPERAT','SolLnShft','SolLnStrn','SPhsErr','IWNumShft','DWNumShft','SZA','LineInt','LineTAir','LinePAir','BckGrdSlp','BckGrdCur','EmpApdFcn','EmpPhsFnc','FOV','OPD','ZeroLev']

        #------------------------------------------------------
        # Find index of input paramName. If this is not matched
        # then program returns original paramName. This is for
        # kb.profile.gases
        #------------------------------------------------------
        try:               ind = Kb_labels_orig.index(paramName)
        except ValueError: return paramName

        if 'gas' in locals(): rtrnVal = Kb_labels[ind] + '_' + gas
        else:                 rtrnVal = Kb_labels[ind]

        return rtrnVal


    #----------------------------------------------
    # List of parameters as they appear in ctl file 
    #----------------------------------------------   
    Kb_labels = ['temperature', 'solshft','solstrnth','phase','wshift','dwshift','sza','lineInt','lineTAir','linePAir','slope','curvature','apod_fcn','phase_fcn','omega','max_opd','zshift'] 

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
    
    #------------------------------------------------------------------------------
    # Read in output files from sfit4 run
    #  -- k.output to calculate averaging kernel
    #  -- d.complete to calculate averaging kernel and measurement error
    #  -- sa.complete to calculate smoothing error
    #  -- summary file for the SNR to calculate the measurement error
    #  -- kb.output for non-retrieved parameter error calculation
    #  -- rprfs.table and aprfs.table for the airmass, apriori and retrieved profiles 
    #------------------------------------------------------------------------------    
    # Read in Sa matrix
    #------------------
    lines = tryopen(wrkingDir+ctlFileVars.inputs['file.out.sa_matrix'][0], logFile)
    if not lines: 
        print 'file.out.sa_matrix missing for observation, directory: ' + wrkingDir
        if logFile: logFile.error('file.out.sa_matrix missing for observation, directory: ' + wrkingDir)
        return False    # Critical file, if missing terminate program    

    sa = np.array( [ [ float(x) for x in row.split()] for row in lines[3:] ] )
    
    #-----------------------------------------------------
    # Test if Sa matrix is symmetric and positive definite
    #-----------------------------------------------------
    (symRtn,pdRtn) = matPosDefTest(sa)
    if not symRtn: print "Warning!! The Sa matrix is not symmetric\n\n"
    if not pdRtn:  print "Warning!! The Sa matrix is not positive definite\n\n"
        
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

    se  = np.zeros((int(sum(sumVars.summary['nptsb'])),int(sum(sumVars.summary['nptsb']))), float)

    if SbctlFileVars.inputs['seinputflg'][0].upper() == 'F':
        snrList    = list(it.chain(*[[snrVal]*int(npnts) for snrVal,npnts in it.izip(sumVars.summary['SNR'],sumVars.summary['nptsb'])]))
        snrList[:] = [val**-2 for val in snrList]
    else:
        if not sc.ckFile(wrkingDir+ctlFileVars.inputs['file.out.seinv_vector'][0], exitFlg=False,quietFlg=False): return False
        lines      = tryopen(wrkingDir+ctlFileVars.inputs['file.out.seinv_vector'][0], logFile)
        snrList    = np.array([float(x) for line in lines[2:] for x in line.strip().split()])
        snrList[:] = 1.0/snrList

    np.fill_diagonal(se,snrList)  

    #-----------------------------------------------------
    # Test if Se matrix is symmetric and positive definite
    #-----------------------------------------------------
    (symRtn,pdRtn) = matPosDefTest(se)
    if not symRtn: print "Warning!! The Se matrix is not symmetric\n\n"
    if not pdRtn:  print "Warning!! The Se matrix is not positive definite\n\n"

    #-----------------
    # Read in K matrix
    #-----------------
    lines = tryopen(wrkingDir+ctlFileVars.inputs['file.out.k_matrix'][0], logFile) 
    if not lines: 
        print 'file.out.k_matrix missing for observation, directory: ' + wrkingDir
        if logFile: logFile.error('file.out.k_matrix missing for observation, directory: ' + wrkingDir)
        return False    # Critical file, if missing terminate program   

    K_param = lines[2].strip().split()

    n_wav   = int( lines[1].strip().split()[0] )
    x_start = int( lines[1].strip().split()[2] )
    n_layer = int( lines[1].strip().split()[3] )
    x_stop  = x_start + n_layer
    K       = np.array([[float(x) for x in row.split()] for row in lines[3:]])

    #--------------------
    # Read in Gain matrix
    #--------------------
    lines = tryopen(wrkingDir+ctlFileVars.inputs['file.out.g_matrix'][0], logFile)
    if not lines: 
        print 'file.out.g_matrix missing for observation, directory: ' + wrkingDir
        if logFile: logFile.error('file.out.g_matrix missing for observation, directory: ' + wrkingDir)
        return False    # Critical file, if missing terminate program   

    D = np.array([[float(x) for x in row.split()] for row in lines[3:]])

    #------------------
    # Read in Kb matrix
    #------------------    
    lines = tryopen(wrkingDir+ctlFileVars.inputs['file.out.kb_matrix'][0], logFile)
    if not lines: 
        print 'file.out.kb_matrix missing for observation, directory: ' + wrkingDir
        if logFile: logFile.error('file.out.kb_matrix missing for observation, directory: ' + wrkingDir)
        return False    # Critical file, if missing terminate program   

    Kb_param = lines[2].strip().split()

    #---------------------------------------------------------------
    # Some parameter names in the Kb file are appended by either 
    # micro-window or gas name. If they are appended by micro-window
    # strip this and just keep parameter name so that we may group
    # the micro-windows under one key
    #---------------------------------------------------------------
    for ind,val in enumerate(Kb_param):
        if len(val.split('_')) == 2:
            pname,appnd = val.split('_')
            try:               int(appnd); val = pname
            except ValueError: pass
        Kb_param[ind] = val

    Kb_unsrt = np.array([[float(x) for x in row.split()] for row in lines[3:]])

    #----------------------------------
    # Create a dictionary of Kb columns
    # A list of numpy arrays is created
    # for repeated keys
    #----------------------------------
    Kb = {}
    for k in set(Kb_param):
        inds = [i for i, val in enumerate(Kb_param) if val == k]
        Kb.setdefault(paramMap(k,Kb_labels).lower(),[]).append(Kb_unsrt[:,inds])

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
    except ValueError:
        print 'Unable to multiple Gain and K matrix '
        print 'Gain matrix shape: %s, K matrix shape: %s' %(str(D.shape),str(K.shape))
        if logFile: logFile.error('Unable to multiple Gain and K matrix; Gain matrix shape: %s, K matrix shape: %s' %(str(D.shape),str(K.shape)) ) 

    #-------------------------------
    # Calculate AVK in VMR/VMR units
    #-------------------------------
    Kx          = K[:,x_start:x_stop]
    Iapriori    = np.zeros((n_layer,n_layer))
    IaprioriInv = np.zeros((n_layer,n_layer))
    np.fill_diagonal(Iapriori,sumVars.aprfs[primgas.upper()])
    np.fill_diagonal(IaprioriInv, 1.0 / (sumVars.aprfs[primgas.upper()]))
    AKxVMR      = np.dot(np.dot(Iapriori,Dx),np.dot(Kx,IaprioriInv))

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
    S_sys['smoothing'] = calcCoVar(mat1,mat2,sumVars.aprfs[primgas.upper()],sumVars.aprfs['AIRMASS'])

    #----------------------------------
    # Calculate Measurement error using 
    # SNR calculated from the spectrum
    #                    T
    #  Sm = Dx * Se * Dx
    #----------------------------------
    S_ran['measurement'] = calcCoVar(se,Dx,sumVars.aprfs[primgas.upper()],sumVars.aprfs['AIRMASS'])

    #---------------------
    # Interference Errors:
    #---------------------
    #------------------------
    # 1) Retrieval parameters
    #------------------------
    AK_int1                   = AK[x_start:x_stop,0:x_start]  
    Sa_int1                   = sa[0:x_start,0:x_start]
    S_ran['retrieval_parameters'] = calcCoVar(Sa_int1,AK_int1,sumVars.aprfs[primgas.upper()],sumVars.aprfs['AIRMASS'])

    #-----------------------
    # 2) Interfering species
    #-----------------------
    n_int2                     = n_profile + n_column - 1
    n_int2_column              = ( n_profile - 1 ) * n_layer + n_column
    AK_int2                    = AK[x_start:x_stop, x_stop:x_stop + n_int2_column] 
    Sa_int2                    = sa[x_stop:x_stop + n_int2_column, x_stop:x_stop + n_int2_column]
    S_ran['interfering_species'] = calcCoVar(Sa_int2,AK_int2,sumVars.aprfs[primgas.upper()],sumVars.aprfs['AIRMASS'])


    #******************************************************************************************
    #-------------------------------------------
    # This is temprorary: calculate uncertainty
    # associated with variability of water vapor
    # Assume water is retrieved as profile
    # Note: Used to study the sensitivity of T and Q in the retrieval strategy paper.
    #-------------------------------------------
    # H2Oind = [ind for ind,val in enumerate(K_param) if val == 'H2O']
    # AK_H2O = AK[x_start:x_stop,H2Oind]
    # diagFill = np.array(SbctlFileVars.inputs['sb.h2o.random'])
    # diagFill = diagFill / sumVars.aprfs['H2O']
    # Sb       = np.zeros((AK_H2O.shape[1],AK_H2O.shape[1]))
    # np.fill_diagonal(Sb,diagFill**2)

    # S_ran['H2O'] = calcCoVar(Sb,AK_H2O,sumVars.aprfs[primgas.upper()],sumVars.aprfs['AIRMASS'])

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
        except: test2 = 1 
        if (test1 == 'F' or test2 == 1): bands.setdefault('zshift',[]).append(int(k))        # only include bands where zshift is NOT retrieved

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

    #----------------------------------------------------------------
    # If file exists that has full covariances of Sb's read this file
    #----------------------------------------------------------------
    sbCovarRand = {}
    sbCovarSys  = {}
    
    if "sb.file.random" in ctlFileVars.inputs:
        sbCovarRand = readCovarFile(ctlFileVars.inputs["sb.file.random"])
        
    if "sb.file.systematic" in ctlFileVars.inputs:
        sbCovarSys = readCovarFile(ctlFileVars.inputs["sb.file.systematic"]) 

    #--------------------------------
    # Loop through parameter list and
    # determine errors
    #--------------------------------
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
                # Get elements for Sb matricies. If a file name is present, the file is read as the 
                # Sb matrix. Some special cases require seperate handling
                #----------------------------------------------------------------------------------
                
                if ErrType == "random":
                    if Kbl.lower() in sbCovarRand: 
                        Sb = sbCovarRand[Kbl.lower()]
                        sbFlg = True
                        
                elif ErrType == "systematic":
                    if Kbl.lower() in sbCovarSys: 
                        Sb = sbCovarSys[Kbl.lower()]
                        sbFlg = True    
                
                if not sbFlg:
                    #-------
                    # Zshift
                    #-------
                    if Kbl.lower() == 'zshift':	
                        diagFill = np.array( [ SbctlFileVars.inputs['sb.band.'+str(x)+'.zshift.'+ErrType][0]  for x in bands['zshift'] ])
    
                    #---------------------------------
                    # Temperature (in case of scaling)
                    #---------------------------------
                    elif (Kbl.lower() == 'temperature') and (SbctlFileVars.inputs['sb.temperature.'+ErrType+'.scaled'][0].upper() == 'F'):
                        diagFill = np.array(SbctlFileVars.inputs['sb.temperature.'+ErrType])
                        if len(diagFill) != len(sumVars.aprfs['TEMPERATURE']): raise ExitError('Number of Sb for temperature, type:'+ErrType+' does not match atmospheric layers!!')
                        diagFill = diagFill / sumVars.aprfs['TEMPERATURE']
    
                    #------------
                    # Profile Gas
                    #------------
                    elif Kbl.upper() in [x.upper() for x in kb_profile_gas]:
                        diagFill = np.array(SbctlFileVars.inputs['sb.profile.'+Kbl+'.'+ErrType])
    
                    #-------------------------
                    # SZA (in case of scaling)
                    #-------------------------
                    elif (Kbl.lower() == 'sza') and (SbctlFileVars.inputs['sb.sza.'+ErrType+'.scaled'][0].upper() == 'F'):
                        if len(SbctlFileVars.inputs['sb.'+Kbl+'.'+ErrType]) != DK.shape[1]: raise ExitError('Number of specified Sb for SZA, type:'+ErrType+' does not match number of Kb columns!! Check Sb.ctl file.')
                        diagFill = np.array(SbctlFileVars.inputs['sb.sza.'+ErrType]) / sumVars.pbp['sza']
    
                    #---------------------------------
                    # Omega (FOV) (in case of scaling)
                    #---------------------------------
                    elif (Kbl.lower() == 'omega') and (SbctlFileVars.inputs['sb.omega.'+ErrType+'.scaled'][0].upper() == 'F'):
                        if len(SbctlFileVars.inputs['sb.'+Kbl+'.'+ErrType]) != DK.shape[1]: raise ExitError('Number of specified Sb for omega, type:'+ErrType+' does not match number of Kb columns!! Check Sb.ctl file.')
                        diagFill = np.array(SbctlFileVars.inputs['sb.omega.'+ErrType]) / sumVars.summary['FOVDIA']
    
                    #----------------
                    # All other cases
                    #----------------
                    else: 
                        #--------------------------------------------------------------------
                        # Catch errors where number of specified Sb does not match Kb columns
                        #--------------------------------------------------------------------
                        if len(SbctlFileVars.inputs['sb.'+Kbl+'.'+ErrType]) != DK.shape[1]: raise ExitError('Number of specified Sb for '+Kbl+', type:'+ErrType+' does not match number of Kb columns!! Check Sb.ctl file.')
                        diagFill = np.array(SbctlFileVars.inputs['sb.'+Kbl+'.'+ErrType]) 
    
                    #--------------------------------------
                    # Fill Sb matrix with diagonal elements
                    #--------------------------------------
                    np.fill_diagonal(Sb,diagFill**2)
                
                #-----------------------------------------------------
                # Test if Sb matrix is symmetric and positive definite
                #-----------------------------------------------------
                (symRtn,pdRtn) = matPosDefTest(Sb)
                if not symRtn: print "Warning!! The Sb matrix is not symmetric\n\n"
                if not pdRtn:  print "Warning!! The Sb matrix is not positive definite\n\n"

            #-----------------------------------------------
            # Catch instances where DK exists for parameter; 
            # however, no Sb is specified
            #-----------------------------------------------
            except KeyError:
                if logFile: logFile.error('Covariance matrix for '+Kbl+': Error type -- ' + ErrType+' not calculated. Sb does not exist\n')

            #-----------------------------------
            # Exceptions for terminating program
            #-----------------------------------
            except ExitError as err:
                print err.msg
                err.terminate()

            #--------------------------------------
            # Catch all other errors in calculation
            #--------------------------------------
            except: 
                errmsg = sys.exc_info()[1]
                print 'Error calculating error covariance matrix for '+Kbl+': Error type -- ' + ErrType 
                print errmsg
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

    #---------------------------------------------
    # Calculate total systematic and random errors
    #---------------------------------------------
    # Initialize total random and systematic
    S_tot                = {}
    S_tot_rndm_err       = 0
    S_tot_systematic_err = 0

    if  SbctlFileVars.inputs['vmroutflg'][0].upper() == 'T': 
        S_tot_ran_vmr   = np.zeros((n_layer,n_layer))
        S_tot_sys_vmr   = np.zeros((n_layer,n_layer))

    if  SbctlFileVars.inputs['molsoutflg'][0].upper() =='T': 
        S_tot_ran_molcs = np.zeros((n_layer,n_layer))
        S_tot_sys_molcs = np.zeros((n_layer,n_layer))

    # Get a list of parameters to include in total error from sb.ctl file
    sbTotParms      = [val.strip().split('.')[-1] for val in SbctlFileVars.inputs.keys() if 'sb.total.' in val.lower()]
    
    # Random
    for k in S_ran:
        if (k in sbTotParms) and SbctlFileVars.inputs['sb.total.'+k][0].upper() == 'T' :
            S_tot_rndm_err  += S_ran[k][2]**2
            if  SbctlFileVars.inputs['vmroutflg'][0].upper()  =='T': S_tot_ran_vmr   += S_ran[k][0]
            else:						     S_tot_ran_vmr    = 0
            if  SbctlFileVars.inputs['molsoutflg'][0].upper() =='T': S_tot_ran_molcs += S_ran[k][1]
            else:                                                    S_tot_ran_molcs  = 0

    S_tot_rndm_err  = np.sqrt(S_tot_rndm_err)

    # Systematic
    for k in S_sys:
        if (k in sbTotParms) and SbctlFileVars.inputs['sb.total.'+k][0].upper() == 'T' :
            S_tot_systematic_err += S_sys[k][2]**2
            if  SbctlFileVars.inputs['vmroutflg'][0].upper()  =='T': S_tot_sys_vmr   += S_sys[k][0]
            else:						     S_tot_sys_vmr    = 0
            if  SbctlFileVars.inputs['molsoutflg'][0].upper() =='T': S_tot_sys_molcs += S_sys[k][1]
            else:						     S_tot_sys_molcs  = 0 

    S_tot_systematic_err = np.sqrt(S_tot_systematic_err)
    S_tot['Random']      = (S_tot_ran_vmr,S_tot_ran_molcs,S_tot_rndm_err)
    S_tot['Systematic']  = (S_tot_sys_vmr,S_tot_sys_molcs,S_tot_systematic_err)



                                        #---------------#
                                        # Write outputs #
                                        #---------------#

    #--------------------------
    # Error summary information
    #--------------------------      
    with open(wrkingDir+SbctlFileVars.inputs['file.out.error.summary'][0], 'w') as fout:
        fout.write('sfit4 ERROR SUMMARY\n\n')
        fout.write('Primary gas                                   = {:>15s}\n'.format(primgas.upper())                                  )
        fout.write('Total column amount                           = {:15.5E} [molecules cm^-2]\n'.format(retdenscol)                    )
        fout.write('DOFs (total column)                           = {:15.3f}\n'.format(col_dofs)                                        )
        fout.write('Smoothing error (Ss)                          = {:15.3f} [%]\n'.format(S_sys['smoothing'][2]        /retdenscol*100))
        fout.write('Measurement error (Sm)                        = {:15.3f} [%]\n'.format(S_ran['measurement'][2]      /retdenscol*100))
        fout.write('Interference error (retrieved params)         = {:15.3f} [%]\n'.format(S_ran['retrieval_parameters'][2] /retdenscol*100))
        fout.write('Interference error (interfering spcs)         = {:15.3f} [%]\n'.format(S_ran['interfering_species'][2]/retdenscol*100))
        
        #fout.write('Temperature (Random)                          = {:15.3f} [%]\n'.format(S_ran['temperature'][2] /retdenscol*100)     )
        #fout.write('Water Vapor                                   = {:15.3f} [%]\n'.format(S_ran['H2O'][2]/retdenscol*100)              )
        
        fout.write('Total random error                            = {:15.3f} [%]\n'.format(S_tot['Random'][2]           /retdenscol*100))
        fout.write('Total systematic error                        = {:15.3f} [%]\n'.format(S_tot['Systematic'][2]       /retdenscol*100))
        fout.write('Total random uncertainty                      = {:15.3E} [molecules cm^-2]\n'.format(S_tot['Random'][2])            )
        fout.write('Total systematic uncertainty                  = {:15.3E} [molecules cm^-2]\n'.format(S_tot['Systematic'][2])        )
        for k in S_ran:
            fout.write('Total random uncertainty {:<20s} = {:15.3E} [molecules cm^-2]\n'.format(k,S_ran[k][2]))
        for k in S_sys:
            fout.write('Total systematic uncertainty {:<16s} = {:15.3E} [molecules cm^-2]\n'.format(k,S_sys[k][2])) 

    #-----------------------------------
    # Write to file covariance matricies
    #-----------------------------------
    if SbctlFileVars.inputs['out.total'][0].upper() == 'T':
        if SbctlFileVars.inputs['molsoutflg'][0].upper() == 'T':
            # molecules cm^-2
            fname  = wrkingDir+SbctlFileVars.inputs['file.out.total'][0]
            header = 'TOTAL RANDOM ERROR COVARIANCE MATRIX IN (MOL CM^-2)^2'
            writeCoVar(fname,header,S_tot,1) 

        if SbctlFileVars.inputs['vmroutflg'][0].upper() == 'T':
            # vmr
            fname  = wrkingDir+SbctlFileVars.inputs['file.out.total.vmr'][0]
            header = 'TOTAL RANDOM ERROR COVARIANCE MATRICES IN (VMR)^2 UNITS'
            writeCoVar(fname,header,S_tot,0) 	

    if SbctlFileVars.inputs['out.srandom'][0].upper() == 'T':
        if SbctlFileVars.inputs['molsoutflg'][0].upper() == 'T':
            # molecules cm^-2
            fname  = wrkingDir+SbctlFileVars.inputs['file.out.srandom'][0]
            header = 'RANDOM ERROR COVARIANCE MATRIX IN (MOL CM^-2)^2'
            writeCoVar(fname,header,S_ran,1)

        if SbctlFileVars.inputs['vmroutflg'][0].upper() == 'T':
            # vmr
            fname  = wrkingDir+SbctlFileVars.inputs['file.out.srandom.vmr'][0]
            header = 'RANDOM ERROR COVARIANCE MATRICES IN (VMR)^2 UNITS'
            writeCoVar(fname,header,S_ran,0)	

    if SbctlFileVars.inputs['out.ssystematic'][0].upper() == 'T':

        if SbctlFileVars.inputs['molsoutflg'][0].upper() == 'T':
            # molecules cm^-2
            fname  = wrkingDir+SbctlFileVars.inputs['file.out.ssystematic'][0]
            header = 'SYSTEMATIC ERROR COVARIANCE MATRIX IN (MOL CM^-2)^2'
            writeCoVar(fname,header,S_sys,1)

        if SbctlFileVars.inputs['vmroutflg'][0].upper() == 'T':
            # vmr
            fname  = wrkingDir+SbctlFileVars.inputs['file.out.ssystematic.vmr'][0]
            header = 'SYSTEMATIC ERROR COVARIANCE MATRICES IN (VMR)^2 UNITS'
            writeCoVar(fname,header,S_sys,0)	

    #-----------------------
    # Write Averaging Kernel
    #-----------------------
    fname      = wrkingDir+SbctlFileVars.inputs['file.out.avk'][0]    
    header     = 'Averaging Kernel for '+ primgas.upper()
    AVK        = {}
    AVK['AVK_scale_factor'] = (AKx,[],[])
    AVK['AVK_VMR']          = (AKxVMR,[],[])
    writeCoVar(fname,header,AVK,0)


    return True
