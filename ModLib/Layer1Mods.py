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
# References:
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
import sfitClasses as sc
import numpy as np
import itertools as it

                                #--------------------------#
                                #                          #
                                #  -- Helper functions --  #
                                #                          #
                                #--------------------------#
def tryopen(fname,lines,rtnFlg,logFile=False):
    try:
        with open(fname, 'r' ) as fopen:
            lines = fopen.readlines()
            rtnFlg = True
    except IOError as errmsg:
        print errmsg
        if logFile: logFile.error(errmsg)
        rtnFlg = False         
    

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
        sys.exit()
        
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
        sys.exit()
        
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
        sys.exit()            

    #---------------------------
    # Grab correct water version
    # based on user input
    #---------------------------
    # Create a list of version number for water files
    r = re.compile(r"([0-9]+)")
    waterVer = [int(r.search(os.path.splitext(wfile)[1]).group(1)) for wfile in waterFiles]
    
    # For wVer < 0 get latest water version file
    if wVer < 0:
        waterInd  = waterVer.index(max(waterVer))
       
    # For wVer >= 0 get user specified water version file   
    else:
        try:
            waterInd = waterVer.index(wVer)
        except ValueError:
            print 'Water version %d not found, using latest version' % wVer
            if logFile: logFile.error('Water version %d not found, using latest version'% wVer)
            waterInd = waterVer.index(max(waterVer))
            
    waterFile = waterFiles[waterInd] 
       
        
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
            nlines = int(nlyrs//5)
            
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
      
    return True    

 
                        #-------------------------#
                        #                         #
                        #    -- t15ascPrep --     #
                        #                         #
                        #-------------------------#    
    
# Copy bnr file to output folder
def t15ascPrep(dbFltData_2, wrkInputDir2, wrkOutputDir5, mainInF, spcDBind, ctl_ind, logFile):
    
    bnrFname = "{0:06}".format(int(dbFltData_2['TStamp'][spcDBind])) + '.bnr'
    
    if not os.path.isfile(wrkOutputDir5+bnrFname):
        try:
            shutil.copy( wrkInputDir2 + bnrFname, wrkOutputDir5 )
        except IOError as errmsg:
            print errmsg
            if logFile: logFile.error(errmsg)
            sys.exit()                    
    
    #--------------------------------------
    # Create pspec.input file for pspec.f90
    #--------------------------------------    
    with open(wrkOutputDir5 + 'pspec.input', 'w') as fname:
        
        # Write header information
        fname.write('# Input file for pspec.f90\n')
        fname.write('# Latitude of Observation [+N, 90 - -90]\n')
        fname.write( str(dbFltData_2['N_Lat'][spcDBind]) + '\n' )
        fname.write('# Longitude of Observation[+E, 0 - 360]\n')
        fname.write( str(dbFltData_2['W_Lon'][spcDBind]) + '\n')
        fname.write('# Altitude of Observation [masl]\n')
        fname.write( str(dbFltData_2['Alt'][spcDBind]) + '\n')
        fname.write('# filter bands and regions for calculating SNR\n')
        fname.write( mainInF.inputs['fltrBndInputs'] )
        fname.write('# number of data blocks in the output ascii file\n')
        fname.write( str(mainInF.inputs['numDataBlks']) + '\n')
        fname.write('# Specify data block (Each block contains at least 2 lines):\n')
        fname.write('# bnr file name\n')
        fname.write('# Radius of Earth (ROE), zero fill factor (nterp), ratioflg (rflag), file open flag (fflag)\n')
        fname.write('# roe - radius of earth [km]\n')
        fname.write('# nterp -  zero fill factor\n')
        fname.write('#     nterp =  0 - skip resample & resolution degradation\n')
        fname.write('#     nterp =  1 - minimally sample at opdmax\n')
        fname.write('#     nterp >  1 - interpolate nterp-1 points upon minimal sampled spacing\n')
        fname.write('#     note: OPDMAX is taken from sfit4.ctl file\n')
        fname.write('# rflag - ratio flag, to ratio the spectra with another low resolution spectral file (eg spectral envelope)\n')
        fname.write('# fflag -  file open flag\n')
        fname.write('#     fflag = 0 for fortran unformatted file\n')
        fname.write('#     fflag = 1 for open as steam or binary or c-type file (gfortran uses stream)\n')
        fname.write('# ratio file name in bnr format\n')
        fname.write('#     if rflag eq 1 this file has to exist\n')
        fname.write('#     skip if rflag eq 0 \n')
        fname.write( bnrFname + '\n') 
        fname.write( str(dbFltData_2['ROE'][spcDBind])          + '   '   +           # ROE
                     str(mainInF.inputs['ctlList'][ctl_ind][1]) + '     ' +           # Zero Fill factor
                     str(mainInF.inputs['ctlList'][ctl_ind][2]) + '     ' +           # Ratio flag
                     str(mainInF.inputs['ctlList'][ctl_ind][3]) +'\n' )               # File open flag
        if mainInF.inputs['ctlList'][ctl_ind][2]:
            fname.write( mainInF.inputs['ctlList'][ctl_ind][4] + '\n' )
        else:
            fname.write('#\n')
    
    #------------------------------
    # Change working directory to 
    # output directory to run pspec
    #------------------------------
    try:
        os.chdir(wrkOutputDir5)
    except OSError as errmsg:
        if logFile: logFile.error(errmsg)
        sys.exit()

        
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
            #sys.exit()                                
        
        
    return True


