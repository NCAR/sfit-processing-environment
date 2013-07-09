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
import sfitClasses as sc

                                #-------------------------#
                                #                         #
                                #   -- NCAR Refmaker --   #
                                #                         #
                                #-------------------------#


def refMkrNCAR(zptwPath, WACCMpath, outPath, logging=False):
    ''' '''
    #--------------------------
    # Determine if paths exists
    #--------------------------    
    try:
        os.path.isdir(zptwPath)
        os.path.isdir(WACCMpath)
        os.path.isdir(outPath)
    except OSError as errmsg:
        print errmsg
        if logging: logging.error(errmsg)
        sys.exit()
    

    #---------------
    # Find ZPTW file
    #---------------
    zptwFile = glob.glob(zptwPath + 'zptw*')
    if len(zptwFile) > 1:                 # If more than one zptw file found trigger warning and use first one
        print 'Found more than one ZPTW file. Using file: ' + zptwFile[0]
        if logging: logging.info('Using ZPTW file: ' + zptwFile[0])
        zptwFile = zptwFile[0]
    elif len(zptwFile) == 0:              # If no zptw files found trigger error
        print 'No ZPTW files found in: ' + zptwPath
        if logging: logging.error('No ZPTW files found in: ' + zptwPath)
        sys.exit()
    else:
        zptwFile = zptwFile[0]
    
    #----------------
    # Find WACCM File
    #----------------
    WACCMfile = glob.glob(WACCMpath + 'WACCMref*.MLO')
    if len(WACCMfile) > 1:                 # If more than one WACCM file found trigger warning and use first one
        print 'Found more than one WACCM file. Using file: ' + WACCMfile[0]
        if logging: logging.info('Using WACCM file: ' + WACCMfile[0])
        WACCMfile = WACCMfile[0]
    elif len(WACCMfile) == 0:              # If no zptw files found trigger error
        print 'No WACCM files found in: ' + WACCMpath
        if logging: logging.error('No WACCM files found in: ' + WACCMfile)
        sys.exit()    
    else:
        WACCMfile = WACCMfile[0]
        
    #----------------------------
    # Concate ZPTW and WACCM file 
    # to produce reference.prf
    #----------------------------
    refFile = outPath + 'reference.prf'
    with open( refFile, 'w') as fout:
        for line in fileinput.input([zptwFile,WACCMfile]):
            fout.write(line)
    
    
    #------------------------------
    # Add number 99 to first line
    # of file indicating 99 species
    # included in list
    #------------------------------        
    with open( refFile, 'r+' ) as fout:
        lines    = fout.readlines()
        lines[0] = lines[0].rstrip() + "{0:5d}".format(99) + '\n'
        
    with open( refFile, 'w' ) as fout:
        for line in lines:
            fout.write(line)
      
    return True
                            
                        #-------------------------#
                        #                         #
                        #   -- NCAR Refmaker --   #
                        #                         #
                        #-------------------------#    
    
# Copy bnr file to output folder
def t15ascPrep(dbFltData_2, wrkInputDir2, wrkOutputDir5, mainInF, ctl_ind, logging):
    
    bnrFname = str(int(dbFltData_2['TStamp'][ctl_ind])) + '.bnr'
    
    if not os.path.isfile(wrkOutputDir5+bnrFname):
        try:
            shutil.copy( wrkInputDir2 + bnrFname, wrkOutputDir5 )
        except IOError as errmsg:
            print errmsg
            if logging: logging.error(errmsg)
            sys.exit()                    
    
    #--------------------------------------
    # Create pspec.input file for pspec.f90
    #--------------------------------------    
    with open(wrkOutputDir5 + 'pspec.input', 'w') as fname:
        
        # Write header information
        fname.write('# Input file for pspec.f90\n')
        fname.write('# Latitude of Observation [+N, 90 - -90]\n')
        fname.write( str(dbFltData_2['N_Lat'][ctl_ind]) + '\n' )
        fname.write('# Longitude of Observation[+E, 0 - 360]\n')
        fname.write( str(dbFltData_2['W_Lon'][ctl_ind]) + '\n')
        fname.write('# Altitude of Observation [masl]\n')
        fname.write( str(dbFltData_2['Alt'][ctl_ind]) + '\n')
        fname.write('# filter bands and regions for calculating SNR\n')
        fname.write( mainInF.inputs['fltrBndInputs'] )
        fname.write('# number of data blocks in the output ascii file\n')
        fname.write( str(mainInF.inputs['numDataBlks']) + '\n')
        fname.write('# Specify data block:\n')
        fname.write('# bnr file name\n')
        fname.write('# Radius of Earth, zero fill factor, ratioflg\n')
        fname.write('# Ratio file name (bnr format) if ratioflag eq 1, skip if 0\n')
        fname.write( bnrFname + '\n') 
        fname.write( str(dbFltData_2['ROE'][ctl_ind]) + '   ' + str(mainInF.inputs['ctlList'][ctl_ind][1]) + \
                     '     ' + str(mainInF.inputs['ctlList'][ctl_ind][2]) + '\n' )
        if mainInF.inputs['ctlList'][ctl_ind][2]:
            fname.write( mainInF.inputs['ctlList'][ctl_ind][3] + '\n' )
        else:
            fname.write('#\n')
    
    #------------------------------
    # Change working directory to 
    # output directory to run pspec
    #------------------------------
    try:
        os.chdir(wrkOutputDir5)
    except OSError as errmsg:
        if logging: logging.error(errmsg)
        sys.exit()

        
    #--------------
    # Call to pspec
    #--------------
    print 'Running pspec for ctl file: ' + mainInF.inputs['ctlList'][ctl_ind][0] 
    stdout,stderr = sc.subProcRun( [mainInF.inputs['binDir'] + 'pspec'] )           # Subprocess call to run pspec
                    
    if logging: logging.info( '\n' + stdout + stderr )

    #if ( stderr is None or not stderr ):
            #if log_flg:
                    #logging.info( stdout )
                    #logging.info('Finished running pspec\n' + stdout)
    #else:
            #print 'Error running pspec!!!'
            #if log_flg:
                    #logging.error('Error running pspec \n' + stdout)
            #sys.exit()                                
        
        
    return True
