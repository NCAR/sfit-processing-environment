#! /usr/bin/python2.7

#----------------------------------------------------------------------------------------
# Name:
#        sfit4Layer1.py
#
# Purpose:
#       This program is the 1st order processing for sfit:
#           
#
#
# Input files:
#			1) 
#
#
# Output files:
#
#
#
# Notes:
#       1) 
#
#
# Usage:
#
#
#
# Examples:
#
#
#
#
# Version History:
#       Created, May, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
#
#
# References:
#
#----------------------------------------------------------------------------------------


                        #-------------------------#
                        # Import Standard modules #
                        #-------------------------#

import logging
import sys
import os
import getopt
import datetime as dt
import glob
import re
import sfitClasses as sc
import shutil
from Layer1Mods import refMkrNCAR, t15ascPrep


                        #-------------------------#
                        # Define helper functions #
                        #-------------------------#
def usage():
    ''' Prints to screen standard program usage'''
    print 'sfit4Layer1.py -i <file> -l <path> --bnr_off '

def convertList(varList):
    ''' Converts numbers represented as a string in a list to float '''
    for ind, var in enumerate(varList):
        try:
            varList[ind] = float(var)
        except ValueError:
            pass
    return varList

def ckDirMk(dirName,logFile=False):
    ''' '''
    if not ( os.path.exists(dirName) ):
        os.makedirs( dirName )
        if logFile: logFile.info( 'Created folder %s' % dirName )         
        
def ckDir(dirName,logFile=False):
    ''' '''
    if not os.path.exists( dirName ):
        print 'Input Directory %s does not exist' % (dirName)
        if logFile: logFile.error('Directory %s does not exist' % dirName )
        sys.exit()         
        

                            #----------------------------#
                            #                            #
                            #        --- Main---         #
                            #                            #
                            #----------------------------#

def main(argv):

    #------------------
    # Set default flags
    #------------------
    logFile = False

    #--------------------------------
    # Retrieve command line arguments
    #--------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:l:','bnr_off')

    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit()
        
    #-----------------------------
    # Parse command line arguments
    #-----------------------------
    for opt, arg in opts:
        # Check input file flag and path
        if opt == '-i':

            # Input file instance
            mainInF = sc.Layer1InputFile(arg)
            
        # Check log file flag and path
        elif opt == '-l':
            log_fpath = arg

            # check if '/' is included at end of path
            if not( log_fpath.endswith('/') ):
                log_fpath = log_fpath + '/'

            # check if path is valide
            ckDir(log_fpath)
                
            logging.basicConfig(level    = logging.INFO,
                                format   = '%(asctime)s %(levelname)-8s %(message)s',
                                datefmt  = '%a, %d %b %Y %H:%M:%S',
                                filename = log_fpath + 'sfit4Lyr1_logfile_' + 
                                dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.log',
                                filemode = 'w' )          
            logFile = logging.getLogger(__name__)
                           
        else:
            print 'Unhandled option: ' + opt
            sys.exit()
            
                                     
    #--------------------
    # Initialize log file
    #--------------------
    # Write initial log data  
    if logFile:
        logFile.info('Input data file ' + mainInF.fname )
        logFile.info('Log file path '   + log_fpath          )


    #----------------------------------------------
    # Initialize main input variables as dicitonary
    #----------------------------------------------           
    mainInF.getInputs(logFile)              

    #--------------------------------------------
    # Program Looping strucutre. See Notes
    #  |
    #   > Fle structure:
    #      Level1 - LOC             (Input/Output)
    #       Level2 - ctl file         (Output)
    #        Level3 - Spectral db     (Output)
    #          --Check I/O directory structure
    #--------------------------------------------
    
    # Establish Date Range
    inDateRange = sc.DateRange(mainInF.inputs['iyear'],mainInF.inputs['imnth'],mainInF.inputs['iday'],
                            mainInF.inputs['fyear'],mainInF.inputs['fmnth'],mainInF.inputs['fday'])
        
    
    #--------------------
    # Level 1 -- LOC
    #--------------------
    if not( isinstance(mainInF.inputs['loc'], list) ): mainInF.inputs['loc'] =[mainInF.inputs['loc']]
        
    for loc in mainInF.inputs['loc']:
        
        # Check for existance of Input folder
        wrkInputDir1 = mainInF.inputs['BaseDirInput'] + loc + '/'        
        ckDir( wrkInputDir1, logFile )
            
        # Check for the existance of Output folder and create if DNE
        wrkOutputDir1 = mainInF.inputs['BaseDirOutput'] + loc + '/'
        ckDirMk( wrkOutputDir1, logFile )
                 
        #--------------------------------------
        # Find spectral db file and initialize
        # instance and get inputs
        #--------------------------------------                       
        dbData = sc.DbInputFile(mainInF.inputs['spcdbFile'],logFile)
        dbData.getInputs()
        
        #-----------------------------
        # Initial filter of data based
        # on input date range
        #-----------------------------
        dbFltData_1 = dbData.dbFilterDate(inDateRange)
        

        #--------------------------------------
        # Level 2 -- Loop through control files
        #--------------------------------------
        for ctl_ind,ctlFileList in enumerate(mainInF.inputs['ctlList']):
                
            #-----------------------------
            # Initialize ctl file instance
            # and get inputs
            #-----------------------------  
            ctlFile   = ctlFileList[0]
            ctlFileCl = sc.CtlInputFile(ctlFile,logFile)
            ctlFileCl.getInputs()
                                
            #-------------------------
            # Filter spectral db based
            # on wavenumber bounds in
            # ctl file
            #-------------------------
            # Find the upper and lower bands from the ctl file
            nu = []
            for band in ctlFileCl.inputs['band']:
                bandstr = str(int(band))
                nu.append(ctlFileCl.inputs['band.'+bandstr+'.nu_start'][0])
                nu.append(ctlFileCl.inputs['band.'+bandstr+'.nu_stop'][0] )
            
            nu.sort()                                    # Sort wavenumbers
            nuUpper = nu[-1]                             # Get upper wavenumber
            nuLower = nu[0]                              # Get lower wavenumber
                       
            # Filter spectral DB based on wave number
            dbFltData_2 = dbData.dbFilterNu(nuUpper,nuLower,dbFltData_1)
            
            if not(dbFltData_2): continue                # Test for empty dicitonary (i.e. no data)
             
            
            #------------------------------------------
            # Level 3 -- Loop through spectral db lines
            #------------------------------------------
            for ind in range(0, len(dbFltData_2['Date'])):  
                
                # Get date of observations
                daystr = str(int(dbFltData_2['Date'][ind]))
                day    = dt.datetime(int(daystr[0:4]),int(daystr[4:6]),int(daystr[6:]))
                            
                #----------------------------------------
                # Check the existance of input and output 
                # directory structure
                #----------------------------------------            
                # Find year month and day strings
                yrstr   = "{0:02d}".format(day.year)
                mnthstr = "{0:02d}".format(day.month)
                daystr  = "{0:02d}".format(day.day)   
                
                # Check for existance of YYYYMMDD Input folder
                # If this folder does not exist => there is no 
                # Data for this day
                wrkInputDir2 = wrkInputDir1 + yrstr + mnthstr + daystr + '/'               
                ckDir( wrkInputDir2, logFile )                       
                
                # Check for the existance of YYYYMMDD Output folder and create if DNE
                wrkOutputDir2 = wrkOutputDir1 + yrstr + mnthstr + daystr + '/'  
                ckDirMk( wrkOutputDir2, logFile )    
                
                # Check for the existance of Output folder <GAS> and create if DNE
                wrkOutputDir3 = wrkOutputDir2 + ctlFileCl.primGas + '/' 
                ckDirMk( wrkOutputDir3, logFile )                     
        
                # Check for the existance of Output folder <TimeStamp> and create if DNE
                wrkOutputDir4 = wrkOutputDir3 + str(int(dbFltData_2['TStamp'][ctl_ind])) + '/' 
                ckDirMk( wrkOutputDir4, logFile )               
                
                # Check for the existance of Output folder <Version> and create if DNE
                wrkOutputDir5 = wrkOutputDir4 + mainInF.inputs['ctlList'][ctl_ind][4] + '/' 
                ckDirMk( wrkOutputDir5, logFile )          
                
                #-------------------------------
                # Copy relavent files from input
                # directory to output directoy
                #-------------------------------
                # Copy control file to Output folder
                # First check if location to copy ctl is 
                # the same location as original ctl file
                ctlPath,ctlFname = os.path.split(mainInF.inputs['ctlList'][ctl_ind][0])
                if not( ctlPath in wrkOutputDir5 ):
                    shutil.copyfile(mainInF.inputs['ctlList'][ctl_ind][0], wrkOutputDir5 + 'sfit4.ctl')
                         
                # Determine which ILS file to use 
                ilsFileList = glob.glob(mainInF.inputs['ilsDir'] + 'ils*')
                
                # Create a date list of ils files present
                ilsMnthYr = []
                for ilsFile in ilsFileList:
                    ilsFileNpath = os.path.basename(ilsFile)
                    match = re.match(r'\s*ils(\d\d)(\d\d\d\d).*',ilsFileNpath)
                    ilsMnthYr.append([int(match.group(1)),int(match.group(2))])
                                    
                ilsDateList = [ dt.date(year,month,1) for month, year in ilsMnthYr ]
                
                # Find the ils date nearest to the current day
                nearstDay = sc.nearestDate(ilsDateList,day.year,day.month)
                nearstDayMnth = "{0:02d}".format(nearstDay.month)
                nearstDayYr   = "{0:02d}".format(nearstDay.year)
                
                # Create ils file name including path
                ilsFname = mainInF.inputs['ilsDir'] + 'ils' + nearstDayMnth + nearstDayYr + '.dat'
                
                # Replace ils file name in ctl file
                teststr = ['file.in.modulation_fcn', 'file.in.phase_fcn']
                repVal  = [ilsFname        , ilsFname   ]
                ctlFileCl.replVar(teststr,repVal)

                    
                                    #----------------------------#
                                    #                            #
                                    #      --- Run pspec---      #
                                    #                            #
                                    #----------------------------#
                if mainInF.inputs['pspecFlg']:
                    
                    rtn = t15ascPrep(dbFltData_2, wrkInputDir2, wrkOutputDir5, mainInF, ctl_ind, logFile)
                                        
                                        
                                    #----------------------------#
                                    #                            #
                                    #    --- Run Refmaker---     #
                                    #                            #
                                    #----------------------------#
                if mainInF.inputs['refmkrFlg']:
                    
                    #-------------
                    # Run Refmaker
                    #-------------
                    rtn = refMkrNCAR(wrkInputDir2, mainInF.inputs['WACCMpath'], wrkOutputDir5, logFile)
                                
                    
                                    #----------------------------#
                                    #                            #
                                    #      --- Run sfit4---      #
                                    #                            #
                                    #----------------------------#
                        
                #--------------
                # Call to sfit4
                #--------------                        
                if mainInF.inputs['sfitFlg']:
                    print 'Running sfit4 for ctl file: ' + mainInF.inputs['ctlList'][ctl_ind][0]
                    
                    #------------------------------
                    # Change working directory to 
                    # output directory to run pspec
                    #------------------------------
                    try:
                        os.chdir(wrkOutputDir5)
                    except OSError as errmsg:
                        if logFile: logging.error(errmsg)
                        sys.exit()
                        
                    #---------------------
                    # Run sfit4 executable
                    #---------------------
                    stdout,stderr = sc.subProcRun( [mainInF.inputs['binDir'] + 'sfit4'] )
                    
                    if logFile: logFile.info( '\n' + stdout + stderr )
                    
                    #if ( stderr is None or not stderr):
                            #if log_flg:
                                    #logFile.info('Finished running sfit4\n' + stdout)
                    #else:
                            #print 'Error running sfit4!!!'
                            #if log_flg:
                                    #logFile.error('Error running sfit4 \n' + stdout)
                            #sys.exit()   




if __name__ == "__main__":
    main(sys.argv[1:])