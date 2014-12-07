#! /usr/local/python-2.7/bin/python
# Change the above line to point to the location of your python executable
#----------------------------------------------------------------------------------------
# Name:
#        sfit4Layer1.py
#
# Purpose:
#       This program is the 1st order processing for sfit:
#           -- Runs refmaker to create a reference profile
#           -- Runs pspec to create t15asc file from type bnr
#           -- Runs sfit4
#           -- Creates an output directory structure to host data
#
#
# External called functions:
#        This program calls sfitClasses and Layer1Mods
#
#
# Notes:
#       1) Command line arguments tell the program where the Layer 1
#          input file resides and where to write the log file
#       2) The hbin file must be created prior to running Layer1
#       23 Options include:
#            -i <file> : Flag to specify input file for Layer 1 processing. <file> is full path and filename of input file
#            -l        : Flag to create log files of processing. Path to write log files is specified in input file 
#            -L <0/1>  : Flag to create output list file. Path to write list files is specified in input file. 
#                             0 = Use consistent file name 'testing.lst'
#                             1 = Uses date and time stamp for list file name 'YYYYMMDD_HHMMSS.lst'
#            -P <int>  : Pause run starting at run number <int>. <int> is an integer to start processing at
#            -?        : Show all flags
#
#
# Usage:
#      ./sfit4Layer1 -i <filename> -l -L<0/1> -P<int>
#
# Examples:
#      Runs sfit4Layer1 with input file Layer1input.py and writes log files 
#
#      ./sfit4Layer1 -i /User/testuser/Layer1input.py -l 
#
#
# Version History:
#       Created, May, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
#       Version history stored in git repository
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

import logging
import sys
import os
import getopt
import datetime as dt
import glob
import re
import sfitClasses as sc
import dataOutClass as dc
import shutil
from Layer1Mods import refMkrNCAR, t15ascPrep, errAnalysis
import matplotlib.pyplot as plt



                        #-------------------------#
                        # Define helper functions #
                        #-------------------------#
def usage():
    ''' Prints to screen standard program usage'''
    print 'sfit4Layer1.py -i <file> -l -L0 -P <int> -?'
    print '  -i <file> : Flag to specify input file for Layer 1 processing. <file> is full path and filename of input file'
    print '  -l        : Flag to create log files of processing. Path to write log files is specified in input file '
    print '  -L <0/1>  : Flag to create output list file. Path to write list files is specified in input file'
    print '  -P <int>  : Pause run starting at run number <int>. <int> is an integer to start processing at'
    print '  -?        : Show all flags'

def convertList(varList):
    ''' Converts numbers represented as a string in a list to float '''
    for ind, var in enumerate(varList):
        try:
            varList[ind] = float(var)
        except ValueError:
            pass
    return varList

def ckDirMk(dirName,logFlg=False):
    ''' '''
    if not ( os.path.exists(dirName) ):
        os.makedirs( dirName )
        if logFlg: logFlg.info( 'Created folder %s' % dirName)  
        return False
    else:
        return True
        
def ckDir(dirName,logFlg=False,exit=False):
    ''' '''
    if not os.path.exists( dirName ):
        print 'Input Directory %s does not exist' % (dirName)
        if logFlg: logFlg.error('Directory %s does not exist' % dirName)
        if exit: sys.exit()
        return False
    else:
        return True    

def ckFile(fName,logFlg=False,exit=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print 'File %s does not exist' % (fName)
        if logFlg: logFlg.error('Unable to find file: %s' % fName)
        if exit: sys.exit()
        return False
    else:
        return True    
        
        

                            #----------------------------#
                            #                            #
                            #        --- Main---         #
                            #                            #
                            #----------------------------#

def main(argv):

    #------------------
    # Set default flags
    #------------------
    logFile  = False
    lstFlg   = False
    pauseFlg = False
    
    #--------------------------------
    # Retrieve command line arguments
    #--------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:P:L:l?')

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
            
        # Pause after skip option
        elif opt == '-P':
            if not arg or arg.startswith('-'):
                usage()
                sys.exit()            
            pauseFlg = True
            try:
                nskips = int(arg) - 1
                if nskips < 0: raise ValueError
            except ValueError:
                print 'Argument for -P flag: %s, needs to be an integer > 0' % arg
                sys.exit()
                
        # Show all command line flags
        elif opt == '-?':
            usage()
            sys.exit()
            
        # Option for Log File
        elif opt == '-l':
            logFile = True
            
        # Option for List file
        elif opt == '-L':
            if not arg or arg.startswith('-'):
                usage()
                sys.exit()
            lstFlg      = True
            lstFnameFlg = int(arg)
                                           
        else:
            print 'Unhandled option: ' + opt
            sys.exit()
 
 
    #----------------------------------------------
    # Initialize main input variables as dicitonary
    #----------------------------------------------           
    mainInF.getInputs()    
                                                 
    #--------------------
    # Initialize log file
    #--------------------
    # Write initial log data  
    if logFile:
        log_fpath = mainInF.inputs['logDirOutput']
        
        # check if '/' is included at end of path
        if not( log_fpath.endswith('/') ):
            log_fpath = log_fpath + '/'

        # check if path is valide
        ckDir(log_fpath)   
        
        logFile = logging.getLogger('1')
        logFile.setLevel(logging.INFO)
        hdlr1   = logging.FileHandler(log_fpath + mainInF.inputs['ctlList'][0][2] + '.log',mode='w')
        fmt1    = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s','%a, %d %b %Y %H:%M:%S')
        hdlr1.setFormatter(fmt1)
        logFile.addHandler(hdlr1)  
        logFile.info('**************** Starting Logging ***********************')
        logFile.info('Input data file:        ' + mainInF.fname )
        logFile.info('Log file path:          ' + log_fpath     )
        logFile.info('Station location:       ' + mainInF.inputs['loc'])
        

    #---------------------
    # Initialize list file
    #---------------------
    if lstFlg:
        lst_fpath = mainInF.inputs['logDirOutput']
        
        # check if '/' is included at end of path
        if not( lst_fpath.endswith('/') ):
            lst_fpath = lst_fpath + '/'

        # check if path is valide
        ckDir(lst_fpath)       
        lstFile = logging.getLogger('2')
        lstFile.setLevel(logging.INFO)
        if lstFnameFlg: hdlr2   = logging.FileHandler(lst_fpath + mainInF.inputs['ctlList'][0][2] + '.lst',mode='w')
        else:           hdlr2   = logging.FileHandler(lst_fpath + 'testing.lst',mode='w')
        fmt2    = logging.Formatter('')
        hdlr2.setFormatter(fmt2)
        lstFile.addHandler(hdlr2)   
        
    #-----------------------------
    # Check the existance of files
    #-----------------------------
    # Spectral Database file
    ckFile(mainInF.inputs['spcdbFile'],logFlg=logFile,exit=True)
    
    # WACCM profile file
    #ckFile(mainInF.inputs['WACCMfile'],logFlg=logFile,exit=True)
    
    # ctl files
    for ctlFile in mainInF.inputs['ctlList']:
        ckFile(ctlFile[0],logFlg=logFile,exit=True)
    
    #--------------------------------------------
    # Program Looping structure. See Notes
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
    if not( isinstance(mainInF.inputs['loc'], list) ): mainInF.inputs['loc'] = [mainInF.inputs['loc']]
        
    for loc in mainInF.inputs['loc']:
        
        #-------------------------------------------
        # Check for existance of Input folder. Also,
        # check if '/' is included at end of path
        #-------------------------------------------
        if not( mainInF.inputs['BaseDirInput'].endswith('/') ):
            wrkInputDir1 = mainInF.inputs['BaseDirInput'] + '/'+ loc + '/' 
        else:
            wrkInputDir1 = mainInF.inputs['BaseDirInput'] + loc + '/'
                 
        ckDir( wrkInputDir1, logFlg=logFile, exit=True )
        
        #-----------------------------------------------------------   
        # Check for the existance of Output folder and create if DNE
        # Also, check if '/' is included at end of path
        #-----------------------------------------------------------
        if not( mainInF.inputs['BaseDirOutput'].endswith('/') ):
            wrkOutputDir1 = mainInF.inputs['BaseDirOutput'] + '/'
        else:
            wrkOutputDir1 = mainInF.inputs['BaseDirOutput'] 
            
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
        
        #---------------------------------
        # Initialize error control file
        # instance and get inputs (sb.ctl)
        #---------------------------------
        if mainInF.inputs['errFlg']:
            ckFile(mainInF.inputs['sbCtlFile'],logFlg=logFile,exit=True)
            SbctlFileVars = sc.CtlInputFile(mainInF.inputs['sbCtlFile'])
            SbctlFileVars.getInputs()            
            
        #--------------------------------------
        # Level 2 -- Loop through control files
        #--------------------------------------
        for ctl_ind,ctlFileList in enumerate(mainInF.inputs['ctlList']):
            
            #-----------------------------
            # Initialize ctl file instance
            # and get inputs
            #-----------------------------  
            ctlFile   = ctlFileList[0]
            ctlFileGlb = sc.CtlInputFile(ctlFile,logFile)
            ctlFileGlb.getInputs() 
            
            #-----------------------------
            # Write Meta-data to list file
            #-----------------------------
            if lstFlg:
                lstFile.info('# Begin List File Meta-Data')
                lstFile.info('Start Date     = ' + str(inDateRange.dateList[0])             )
                lstFile.info('End Date       = ' + str(inDateRange.dateList[-1])            )
                lstFile.info('WACCM_File     = ' + mainInF.inputs['WACCMfile']              )
                lstFile.info('ctl_File       = ' + mainInF.inputs['ctlList'][ctl_ind][0]    )
                lstFile.info('FilterID       = ' + mainInF.inputs['ctlList'][ctl_ind][1]    )
                lstFile.info('VersionName    = ' + mainInF.inputs['ctlList'][ctl_ind][2]    )
                lstFile.info('Site           = ' + mainInF.inputs['loc'][0]                 )
                lstFile.info('statnLyrs_file = ' + ctlFileGlb.inputs['file.in.stalayers'][0])
                lstFile.info('primGas        = ' + ctlFileGlb.primGas                       )
                lstFile.info('specDBfile     = ' + mainInF.inputs['spcdbFile']              )
                lstFile.info('Coadd flag     = ' + str(mainInF.inputs['coaddFlg'])          )
                lstFile.info('nBNRfiles      = ' + str(mainInF.inputs['nBNRfiles'])         )
                lstFile.info('ilsFlg         = ' + str(mainInF.inputs['ilsFlg'])            )
                lstFile.info('pspecFlg       = ' + str(mainInF.inputs['pspecFlg'])          )
                lstFile.info('refmkrFlg      = ' + str(mainInF.inputs['refmkrFlg'])         )
                lstFile.info('sfitFlg        = ' + str(mainInF.inputs['sfitFlg'])           )
                lstFile.info('lstFlg         = ' + str(mainInF.inputs['lstFlg'])            )
                lstFile.info('errFlg         = ' + str(mainInF.inputs['errFlg'])            )
                lstFile.info('zptFlg         = ' + str(mainInF.inputs['zptFlg'])            )
                lstFile.info('refMkrLvl      = ' + str(mainInF.inputs['refMkrLvl'])         )
                lstFile.info('wVer           = ' + str(mainInF.inputs['wVer'])              )
                lstFile.info('nbands         = ' + str(len(ctlFileGlb.inputs['band']))      )
                lstFile.info('# End List File Meta-Data')
                lstFile.info('')
                lstFile.info('Date         TimeStamp    Directory ')            
                   
            #----------------------
            # Filtering spectral DB
            #----------------------
            #-------------------------
            # Filter spectral db based
            # on wavenumber bounds in
            # ctl file
            #-------------------------
            # Find the upper and lower bands from the ctl file
            nu = []
            for band in ctlFileGlb.inputs['band']:
                bandstr = str(int(band))
                nu.append(ctlFileGlb.inputs['band.'+bandstr+'.nu_start'][0])
                nu.append(ctlFileGlb.inputs['band.'+bandstr+'.nu_stop'][0] )
            
            nu.sort()                                    # Sort wavenumbers
            nuUpper = nu[-1]                             # Get upper wavenumber
            nuLower = nu[0]                              # Get lower wavenumber
                       
            # Filter spectral DB based on wave number
            dbFltData_2 = dbData.dbFilterNu(nuUpper,nuLower,dbFltData_1)
            
            if not(dbFltData_2): continue                # Test for empty dicitonary (i.e. no data)
            
            #------------------------------------------------------------------------------------------------
            # In addition to filtering db based on wavenumbers in ctl file one can filter spectral db based
            # on filter ID. Using this can help avoid the bug when pspec tries to apply a filter band outside
            # spectral region of a bnr file.
            #------------------------------------------------------------------------------------------------
            if mainInF.inputs['ctlList'][ctl_ind][1]:
                dbFltData_2 = dbData.dbFilterFltrID(mainInF.inputs['ctlList'][ctl_ind][1], dbFltData_2)                
                if not(dbFltData_2): continue                # Test for empty dicitonary (i.e. no data)
                         
            #--------------------------------------------------------
            # Filter database based on forward and backward scan flag
            #--------------------------------------------------------
            if mainInF.inputs['scnFlg'] > 0:
                dbFltData_2 = dbData.dbFilterScn(mainInF.inputs['scnFlg'], dbFltData_2 )
            
            #---------------------------------------------------------------------             
            # Check for the existance of Output folder <Version> and create if DNE
            #---------------------------------------------------------------------
            if mainInF.inputs['ctlList'][ctl_ind][2]:
                wrkOutputDir2 = wrkOutputDir1 + mainInF.inputs['ctlList'][ctl_ind][2] + '/' 
                ckDirMk( wrkOutputDir2, logFile )             
            else:
                wrkOutputDir2 = wrkOutputDir1   
                      
            #-----------------------------------------------
            # Create a folder within the output directory to 
            # store various input files: ctl, hbin, isotope
            #-----------------------------------------------
            ctlPath,ctlFname = os.path.split(mainInF.inputs['ctlList'][ctl_ind][0])                    
            archDir          = wrkOutputDir2 + 'inputFiles' + '/'
            
            if ckDirMk(archDir, logFile):
                for f in glob.glob(archDir + '*'): os.remove(f)
            
            shutil.copy(mainInF.inputs['ctlList'][ctl_ind][0], archDir)       # Copy ctl file
            
            for file in glob.glob(ctlPath + '/*hbin*'):                       # Copy hbin files
                shutil.copy(file, archDir)
            
            for file in glob.glob(ctlPath + '/isotope*'):                     # Copy isotope file
                shutil.copy(file,archDir)            
                         
            #------------------------------------------
            # Level 3 -- Loop through spectral db lines
            #------------------------------------------
            nobs = len(dbFltData_2['Date'])
            for spcDBind in range(0, nobs):  
                
                #-----------------------------------------------------------
                # Grab spectral data base information for specific retrieval
                #-----------------------------------------------------------
                # Get current date and time of spectral database entry
                currntDayStr = str(int(dbFltData_2['Date'][spcDBind]))
                currntDay    = dt.datetime(int(currntDayStr[0:4]),int(currntDayStr[4:6]),int(currntDayStr[6:]),int(dbFltData_2['Time'][spcDBind][0:2]),int(dbFltData_2['Time'][spcDBind][3:5]),int(dbFltData_2['Time'][spcDBind][6:]) )
                # Get dictionary with specific date
                specDBone    = dbData.dbFindDate(currntDay,fltDict=dbFltData_2)                
                
                brkFlg = True    # Flag to break out of while statement
                while True:      # While statement is for the repeat function 
                    print '\n\n\n'
                    print '*************************************************'
                    print '*************Begin New Retrieval*****************'
                    print '*************************************************'                    
                    #-------------------------------------------------------------
                    # If pause after skip flag is initialized, do several things:
                    # 1) Check if number of skips exceeds total number of filtered
                    #    observations
                    # 2) Skip to specified starting point
                    # 3) Pause after first run
                    #-------------------------------------------------------------
                    if pauseFlg and (nskips > len(dbFltData_2['Date'])):
                        print 'Specified starting point in -P option (%d) is greater than number of observations in filtered database (%d)' %(nskips,nobs)
                        if logFile: logFile.critical('Specified starting point in -P option (%d) is greater than number of observations in filtered database (%d)' %(nskips,nobs))
                        sys.exit()
                    
                    if pauseFlg and (spcDBind < nskips): break
                                     
                    # Get date of observations
                    daystr = str(int(dbFltData_2['Date'][spcDBind]))
                    obsDay = dt.datetime(int(daystr[0:4]),int(daystr[4:6]),int(daystr[6:]))
                                
                    #----------------------------------------
                    # Check the existance of input and output 
                    # directory structure
                    #----------------------------------------            
                    # Find year month and day strings
                    yrstr   = "{0:02d}".format(obsDay.year)
                    mnthstr = "{0:02d}".format(obsDay.month)
                    daystr  = "{0:02d}".format(obsDay.day)  
                    datestr = yrstr + mnthstr + daystr
                    
                    # Check for existance of YYYYMMDD Input folder
                    # If this folder does not exist => there is no 
                    # Data for this day
                    wrkInputDir2 = wrkInputDir1 + yrstr + mnthstr + daystr + '/'               
                    ckDir( wrkInputDir2, logFlg=logFile, exit=True )                       
                    
                    #-----------------------------------------
                    # Check for the existance of Output folder 
                    # <Date>.<TimeStamp> and create if DNE
                    #-----------------------------------------
                    wrkOutputDir3 = wrkOutputDir2 + datestr + '.' + "{0:06}".format(int(dbFltData_2['TStamp'][spcDBind])) + '/' 
                    
                    if ckDirMk( wrkOutputDir3, logFile ):
                        # Remove all files in Output directory if previously exists!!
                        for f in glob.glob(wrkOutputDir3 + '*'): os.remove(f)   
                    
                    #-------------------------------
                    # Copy relavent files from input
                    # directory to output directoy
                    #-------------------------------
                    #-----------------------------------
                    # Copy control file to Output folder
                    # First check if location to copy ctl is 
                    # the same location as original ctl file
                    #----------------------------------- 
                    try:
                        shutil.copyfile(mainInF.inputs['ctlList'][ctl_ind][0], wrkOutputDir3 + 'sfit4.ctl')
                    except IOError:
                        print 'Unable to copy template ctl file to working directory: %s' % wrkOutputDir3
                        if logFile: logFile.critical('Unable to copy template ctl file to working directory: %s' % wrkOutputDir3)
                        sys.exit()
                    
                    #-------------------------------------
                    # Copy sb.ctl file to output directory
                    # if error analysis is chosen
                    #-------------------------------------
                    if mainInF.inputs['errFlg']:
                        try:
                            shutil.copyfile(mainInF.inputs['sbCtlFile'], wrkOutputDir3 + 'sb.ctl')
                        except IOError:
                            print 'Unable to copy template sb.ctl file to working directory: %s' % wrkOutputDir3
                            if logFile: logFile.critical('Unable to copy template sb.ctl file to working directory: %s' % wrkOutputDir3)
                            sys.exit()                    
                                           
                    #----------------------------------
                    # Copy hbin details to output folder
                    # ** Assuming that the hbin.dtl and
                    # hbin.input files are in the same
                    # location as the global ctl file
                    #----------------------------------
                    try:
                        shutil.copyfile(ctlPath + '/hbin.dtl', wrkOutputDir3 + '/hbin.dtl')            # Copy hbin.dtl file
                    except IOError:
                        print 'Unable to copy file: %s' % (ctlPath + '/hbin.dtl')
                        if logFile: logFile.error(IOError)
                        
                    try:
                        shutil.copyfile(ctlPath + '/hbin.input', wrkOutputDir3 + '/hbin.input')          # Copy hbin.input file
                    except IOError:
                        print 'Unable to copy file: %s' % (ctlPath + '/hbin.input')
                        if logFile: logFile.error(IOError)
                                       
                          
                    # Create instance of local control file (ctl file in working directory)
                    ctlFileLcl = sc.CtlInputFile(wrkOutputDir3 + 'sfit4.ctl',logFile)
                             
                    #-------------------------------------------------
                    # Determine whether to use ILS file. Empty string
                    # '' => no ILS file.
                    #-------------------------------------------------
                    if mainInF.inputs['ilsDir'] and mainInF.inputs['ilsFlg']:

                        #-------------------------------------------
                        # Determine if ilsDir is a file or directory
                        #-------------------------------------------
                        # If directory.....
                        if os.path.isdir(mainInF.inputs['ilsDir']):
                        
                            # Determine which ILS file to use 
                            ilsFileList = glob.glob(mainInF.inputs['ilsDir'] + 'ils*')
                
                            # Create a date list of ils files present
                            ilsYYYYMMDD = []
                            for ilsFile in ilsFileList:
                                ilsFileNpath = os.path.basename(ilsFile)
                                match = re.match(r'\s*ils(\d\d\d\d)(\d\d)(\d\d).*',ilsFileNpath)
                                ilsYYYYMMDD.append([int(match.group(1)),int(match.group(2)),int(match.group(3))])
                                                
                            ilsDateList = [ dt.date(ilsyear,ilsmonth,ilsday) for ilsyear, ilsmonth, ilsday in ilsYYYYMMDD ]
                            
                            # Find the ils date nearest to the current day
                            nearstDay     = sc.nearestDate(ilsDateList,obsDay.year,obsDay.month,obsDay.day)
                            nearstDayMnth = "{0:02d}".format(nearstDay.month)
                            nearstDayYr   = "{0:02d}".format(nearstDay.year)
                            nearstDayDay  = "{0:02d}".format(nearstDay.day)
                            nearstDaystr  = nearstDayYr + nearstDayMnth + nearstDayDay
                            
                            # Get File path and name for nearest ils file
                            for ilsFile in ilsFileList:
                                if nearstDaystr in os.path.basename(ilsFile):
                                    ilsFname = ilsFile

                        # If file.....
                        elif os.path.isfile(mainInF.inputs['ilsDir']):
                            ilsFname = mainInF.inputs['ilsDir']
                                                          
                        if logFile: logFile.info('Using ils file: ' + ilsFname)
                        
                        # Replace ils file name in local ctl file (within working directory)
                        teststr = [r'file.in.modulation_fcn', r'file.in.phase_fcn']
                        repVal  = [ilsFname        , ilsFname   ]
                        ctlFileLcl.replVar(teststr,repVal)
                    
                    # Write FOV from spectral database file to ctl file (within working directory)
                    ctlFileLcl.replVar([r'band\.\d+\.omega'],[str(specDBone['FOV'])])
                    
                    #---------------------------
                    # Message strings for output
                    #---------------------------    
                    msgstr1 = mainInF.inputs['ctlList'][ctl_ind][0]
                    msgstr2 = datestr+'.'+"{0:06}".format(int(dbFltData_2['TStamp'][spcDBind]))                
                        
                                        #----------------------------#
                                        #                            #
                                        #      --- Run pspec---      #
                                        #                            #
                                        #----------------------------#
                    if mainInF.inputs['pspecFlg']:    
                        print '*****************************************************'
                        print 'Running PSPEC for ctl file: %s' % msgstr1
                        print 'Processing spectral observation date: %s' % msgstr2
                        print '*****************************************************'
                        
                        rtn = t15ascPrep(dbFltData_2, wrkInputDir2, wrkOutputDir3, mainInF, spcDBind, ctl_ind, logFile)
                        
                        if logFile: 
                            logFile.info('Ran PSPEC for ctl file: %s' % msgstr1)
                            logFile.info('Processed spectral observation date: %s' % msgstr2)                    
                                            
                                            
                                        #----------------------------#
                                        #                            #
                                        #    --- Run Refmaker---     #
                                        #                            #
                                        #----------------------------#
                    if mainInF.inputs['refmkrFlg']:                   
                        #-------------
                        # Run Refmaker
                        #-------------
                        print '*****************************************************'
                        print 'Running REFMKRNCAR for ctl file: %s' % msgstr1
                        print 'Processing spectral observation date: %s' % msgstr2
                        print '*****************************************************'
                        
                        rtn = refMkrNCAR(wrkInputDir2, mainInF.inputs['WACCMfile'], wrkOutputDir3, \
                                         mainInF.inputs['refMkrLvl'], mainInF.inputs['wVer'], mainInF.inputs['zptFlg'],\
                                         dbFltData_2, spcDBind, logFile)
                        if logFile: 
                            logFile.info('Ran REFMKRNCAR for ctl file: %s' % msgstr1)
                            logFile.info('Processed spectral observation date: %s' % msgstr2)                    
                                    
                        
                                        #----------------------------#
                                        #                            #
                                        #      --- Run sfit4---      #
                                        #                            #
                                        #----------------------------#
                            
                    #--------------
                    # Call to sfit4
                    #--------------                        
                    if mainInF.inputs['sfitFlg']:
                        print '*****************************************************'
                        print 'Running SFIT4 for ctl file: %s' % msgstr1
                        print 'Processing spectral observation date: %s' % msgstr2
                        print 'Ouput Directory: %s' % wrkOutputDir3
                        print '*****************************************************'
                        
                        if logFile: 
                            logFile.info('Ran SFIT4 for ctl file: %s' % msgstr1)
                            logFile.info('Processed spectral observation date: %s' % msgstr2)
                        
                        #------------------------------
                        # Change working directory to 
                        # output directory to run pspec
                        #------------------------------
                        try:
                            os.chdir(wrkOutputDir3)
                        except OSError as errmsg:
                            if logFile: logFile.error(errmsg)
                            sys.exit()
                            
                        #---------------------
                        # Run sfit4 executable
                        #---------------------
                        sc.subProcRun( [mainInF.inputs['binDir'] + 'sfit4'] ,logFile)
                        
                        #if ( stderr is None or not stderr):
                                #if log_flg:
                                        #logFile.info('Finished running sfit4\n' + stdout)
                        #else:
                                #print 'Error running sfit4!!!'
                                #if log_flg:
                                        #logFile.error('Error running sfit4 \n' + stdout)
                                #sys.exit()   
    
    
                        #-----------------------------------
                        # Change permissions of all files in 
                        # working directory
                        #-----------------------------------
                        for f in glob.glob(wrkOutputDir3 + '*'):
                            os.chmod(f,0777)
    
                        #----------------------------------------------
                        # If succesfull run, write details to list file
                        #----------------------------------------------
                        if lstFlg:
                            fname    = wrkOutputDir3 +'sfit4.dtl'
                            cmpltFlg = False
                            with open(fname,'r') as fopen:
                                for ind,line in enumerate(reversed(fopen.readlines())):
                                    if ind < 10:
                                        if r'RDRV: DONE.' in line: cmpltFlg = True
                                    else: break
                            
                            if cmpltFlg and lstFile:
                                lstFile.info("{0:<13}".format(int(dbFltData_2['Date'][spcDBind])) + "{0:06}".format(int(dbFltData_2['TStamp'][spcDBind])) + '       ' + wrkOutputDir3)
                                
                                  
                                #----------------------------#
                                #                            #
                                #   --- Error Analysis ---   #
                                #                            #
                                #----------------------------#
                        if mainInF.inputs['errFlg']:
                            if logFile: 
                                logFile.info('Ran SFIT4 for ctl file: %s' % msgstr1)                            
                            
                            #-----------------------------------
                            # Enter into Error Analysis function
                            #-----------------------------------
                            rtn = errAnalysis( ctlFileGlb, SbctlFileVars, wrkOutputDir3, logFile )  
                                
                        #---------------------------
                        # Continuation for Pause flg
                        #---------------------------
                        if pauseFlg:
                            while True:
                                user_input = raw_input('Paused processing....\n Enter: 0 to exit, -1 to repeat, 1 to continue to next, 2 to continue all, 3 plot retrieval results\n >>> ')
                                plt.close('all')
                                try:
                                    user_input = int(user_input)
                                    if not any(user_input == val for val in [-1,0,1,2,3]): raise ValueError
                                except ValueError: print 'Please enter -1, 0, 1, 2, or 3'
                                    
                                if   user_input == 0:  sys.exit()           # Exit program
                                elif user_input == 1:                       # Exit while loop (Do not repeat)
                                    brkFlg = True        
                                    break
                                elif user_input == 2:                       # Stop pause and exit while loop
                                    pauseFlg = False
                                    brkFlg   = True
                                    break
                                elif user_input == 3:                       # Plot retrieval results
                                    #----------------------
                                    # Initialize Plot Class
                                    #----------------------                                
                                    gas = dc.PlotData(wrkOutputDir3,wrkOutputDir3+'sfit4.ctl')
                                    #--------------------------
                                    # Call to plot spectral fit
                                    #--------------------------
                                    gas.pltSpectra()                                
                                    #----------------------
                                    # Call to plot profiles
                                    #----------------------
                                    try:
                                        gas.pltPrf(allGas=True,errFlg=True)
                                    except:
                                        gas.pltPrf(allGas=True)
                                    #-----------------
                                    # Call to plot AVK
                                    #-----------------
                                    if ('gas.profile.list' in gas.ctl) and gas.ctl['gas.profile.list']:  gas.pltAvk()                                
                                    #-----------------------------
                                    # Print summary file to screen
                                    #-----------------------------
                                    if ckFile(wrkOutputDir3+'summary'):
                                        with open(wrkOutputDir3+'summary','r') as fopen: info = fopen.read()
                                        
                                        print '****************SUMMARY FILE****************'
                                        print (info)
                                        print '****************END OF SUMMARY FILE****************' 
                               
                                elif user_input == -1:                      # Repeat loop
                                    brkFlg = False 
                                    break
                                    
                        #-----------------------
                        # Exit out of while loop
                        #-----------------------
                        if brkFlg: break


if __name__ == "__main__":
    main(sys.argv[1:])