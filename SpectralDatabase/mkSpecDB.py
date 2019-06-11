#!/usr/bin/python
##! /usr/local/python-2.7/bin/python

# Change the above line to point to the location of your python executable

#----------------------------------------------------------------------------------------
# Name:
#        mkSpecDB.py
#
# Purpose:
#       This program is a wrapper for ckopus. It runs ckopus on multiple spectral observations
#       to create a database file. It will search through directories from a given base directory
#       for file names matching a given tag. If a datafile is found the program will execute ckopus.c 
#       and write out the one line DB string to an output file. Given the output spectral DB this
#       program will determine if that file previously exists. If it does it will append the DB
#       file. If not it will create a new DB file.
#           
#
#
# Input files:
#       2) Input file (Optional)
#
# Output files:
#       1) Spectral database file 
#
# Called Functions:
#       1) No external called functions (other than system functions)
#
#
# Notes:
#       1) Running program with -D option:
#           a) For this option...do not specify the -i option
#           b) For this option...the location of the ckopus executable is hardcoded under 
#              Initializations and Defaults section of main program
#       2) Currently when running ckopus with -C option, ckopus will pass back a return
#          code of 1 or 3 if file is not an OPUS file
#
#
# Usage:
#     mkSpecDB.py -i <File> -D <Directory>
#              -i           Input file for mkSpecDB.py
#              -D           Directory
#
# Examples:
#    ./mkSpecDB.py -i /home/data/DatabaseInputFile.py          -- This runs the program with the input file DatabaseInputFile.py
#    ./mkSpecDB.py -D /home/data/                              -- This creates a file with a list of directories under /home/data/
#                                                                 which have valid OPUS data
#
# Version History:
#  1.0     Created, July, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
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
import sys
import os
from os import walk
import getopt
import subprocess as sp
import shutil
import logging
import datetime as dt
import sfitClasses as sc

                        #-------------------------------------#
                        # Define helper functions and classes #
                        #-------------------------------------#
            
                                                     
def usage():
    ''' Prints to screen standard program usage'''
    print 'mkSpecDB.py -i <File> -D <Directory>'

        
def ckDir(dirName):
    '''Check if a directory exists'''
    if not os.path.exists( dirName ):
        print 'Directory %s does not exist' % (dirName)
        return False
    else:
        return True
        
def ckFile(fName):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print 'File %s does not exist' % (fName)
        sys.exit()       
        
def findFiles(Path):
    ''' Find just files in directory. Does not find files in subdirectories '''
    fnames = []
    for (dirpath, dirnames, filenames) in walk(Path):
        fnames.extend(filenames)
        break
    if dirpath.endswith('/'):
        fnames = [(dirpath + name) for name in filenames]
    else:
        fnames = ['/'.join([dirpath,name]) for name in filenames]      
    return fnames

def checkOPUS(ckopus,indvfile):
    '''Check if file is OPUS file'''
    rtn           = sp.Popen([ckopus,'-C',indvfile], stdout=sp.PIPE, stderr=sp.PIPE)
    stdout,stderr = rtn.communicate()
    rtnCode       = rtn.returncode
    if not (rtnCode == 1 or rtnCode == 3):                    
        return True                                            
    else:
        return False
    
                            #----------------------------#
                            #                            #
                            #        --- Main---         #
                            #                            #
                            #----------------------------#

def main(argv):
    
    #-----------------------------
    # Initializations and defaults
    #-----------------------------
    ckopus = '/data/bin/ckopus'          # Default path for ckopus executable. This is used for commandline option to 
                                         # just create a list of folders with OPUS data in them                                  
    datapath = False
    inpFlg   = False
    
                                                #---------------------------------#
                                                # Retrieve command line arguments #
                                                #---------------------------------#
    #------------------------------------------------------------------------------------------------------------#                                             
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:D:s:d:?:')

    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit()
        
    #-----------------------------
    # Parse command line arguments
    #-----------------------------
    for opt, arg in opts:
        
        #-----------
        # Input file
        #-----------
        if opt == '-i':           
            inputFile = arg
            
            # Check if file exists
            ckFile(inputFile)

            inpFlg  = True
    
        #-------------------------------
        # Option to just create a list
        # of folders that have OPUS files
        #-------------------------------
        elif opt == '-D':
            datapath = arg
            
            # check if '/' is included at end of path
            if not( datapath.endswith('/') ):
                datapath += '/'
                
            # Check if directory exists
            ckDir(datapath)
            
            print 'Searching for ckopus executable file specified in mkSpecDB.py'
            print 'If not found, please change path under Initializations and defaults in python program'
            ckFile(ckopus)                       # Check if ckopus executable file given above under Initializations and defaults
                                                 # exists
            print 'ckopus executable found'  

        elif opt == '-s':  

            loc = arg.lower()

        elif opt == '-d':

            if len(arg) == 8:

                dates   = arg.strip().split()

                iyear   = int(dates[0][0:4])
                imnth   = int(dates[0][4:6])
                iday    = int(dates[0][6:8])

                fyear   = int(dates[0][0:4])
                fmnth   = int(dates[0][4:6])
                fday    = int(dates[0][6:8])


            elif len(arg) == 17:

                dates   = arg.strip().split()

                iyear   = int(dates[0][0:4])
                imnth   = int(dates[0][4:6])
                iday    = int(dates[0][6:8])

                fyear   = int(dates[0][9:13])
                fmnth   = int(dates[0][13:15])
                fday    = int(dates[0][15:17])

        elif opt == '-?':
            usage()
            sys.exit()                                   

        #------------------
        # Unhandled options
        #------------------
        else:
            print 'Unhandled option: ' + opt
            usage()
            sys.exit()
    #------------------------------------------------------------------------------------------------------------#                       

    #------------------------------------
    # If the option to just create a list 
    # of folders with data then execute 
    # the following
    #------------------------------------
    if datapath:
        fname  = datapath + 'Fldrs_with_OPUS_' + dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.list'
        
        with open(fname,'w') as fopen:
            for dirs in os.walk(datapath).next()[1]:
                                        
                #--------------------------------------------------------
                # Test if file is opus type. If the file in not opus type
                # a return code of 1 or 3 is kicked back when the -C
                # option is used
                #--------------------------------------------------------
                # Gather all files within the day directory
                # to test if these are OPUS files
                #------------------------------------------
                fnames = findFiles(datapath+dirs)          
                for indvfile in fnames:
                    if checkOPUS(ckopus,indvfile):                     
                        fopen.write('%s\n' % dirs)
                        break
                    
        print 'Finished creating processed folder list....'
        sys.exit()
        
    #----------------
    # Read input file
    #----------------
    DBinputs = {}

    if inpFlg:
        execfile(inputFile, DBinputs)
        if '__builtins__' in DBinputs:
            del DBinputs['__builtins__'] 

    else:

        #---------------------
        # Three letter station
        # location
        #---------------------
        DBinputs['loc'] = loc

        #----------------------------------
        # Date Range of data to process
        # Data processing includes starting
        # and ending dates!!
        #----------------------------------
        # Starting
        DBinputs['iyear'] = iyear               # Year
        DBinputs['imnth'] = imnth                 # Month
        DBinputs['iday']  = iday                  # Day

        # Ending
        DBinputs['fyear'] = fyear               # Year
        DBinputs['fmnth'] = fmnth                 # Month
        DBinputs['fday']  = fday                 # Day


        #------------
        # directories
        #------------
        DBinputs['dataBaseDir']   = '/data1/'+loc.lower()+'/'                                    # Base directory for OPUS data
        DBinputs['DaysProcDir']   = '/data/Campaign/'+loc.upper()+'/Spectral_DB/'   # Path to write file that contains list of all folders processed

        #------
        # Files
        #------
        DBinputs['outputDBfile']  = '/data/Campaign/'+loc.upper()+'/Spectral_DB/spDB_'+loc.lower()+'_RD.dat'  # Path and filename of spectral database file
        #Fckopus       = '/data/ebaumer/Code/sfit-ckopus/ckopus'
        DBinputs['Fckopus']       = '/data/bin/ckopus'                                                    # ckopus executable file

        #----------------------
        # General Logical Flags
        #----------------------
        DBinputs['DaysProcFlg'] = False              # This flag controls whether a file containing a list of folders processed is written
        DBinputs['bnrWriteFlg'] = True              # This flag controls whether ckopus is called to write bnr files

        #-------------
        # ckopus Flags
        #-------------
        DBinputs['bnrType']    = 'F'                # bnr type ckopus writes (F => Fortran, R => C)
        DBinputs['SBlockType'] = 'NONE'             # Spectral block type [TRAN | SGN2 | IFG2 | EMIS | IFGM | PHAS | SNGC]
                                        # If this value is None or an empty string, the program will take the
                                        # default spectral block type given by ckopus

        #------------------------------------------
        # ckopus notes: Jan 15th 2009 clock changed
        # to UTC time. Prior to that clock was on
        # MLO time.
        #------------------------------------------
        #ckopusFlgs = ['-b2']                # For MLO 2009 - August 2011
        #ckopusFlgs = ['-b6','-U','-pPHAS'] # For MLO 1995 - 2008
        DBinputs['ckopusFlgs'] = ['-b5']               # For MLO after August 2011      
        
    #-----------------------------------
    # Check the existance of directories
    # and files given in input file
    #-----------------------------------
    # Directory for days processed file
    if DBinputs['DaysProcFlg']:                            
        if not ckDir(DBinputs['DaysProcDir']):
            sys.exit()
        # check if '/' is included at end of path
        if not( DBinputs['DaysProcDir'].endswith('/') ):
            DBinputs['DaysProcDir'] = DBinputs['DaysProcDir'] + '/'    
            
    # Base directory for data    
    if not ckDir(DBinputs['dataBaseDir']):                     
        sys.exit()
    # check if '/' is included at end of path
    if not( DBinputs['dataBaseDir'].endswith('/') ):
        DBinputs['dataBaseDir'] = DBinputs['dataBaseDir'] + '/'          
        
    # ckopus executable file    
    ckFile(DBinputs['Fckopus'])                            

    # Directory of output spectral database file
    if not ckDir(os.path.dirname(DBinputs['outputDBfile'])):   
        sys.exit()
                          
    #-------------------
    # Call to date class
    #-------------------
    DOI      = sc.DateRange(DBinputs['iyear'],DBinputs['imnth'],DBinputs['iday'],      # Create a dateRange instance object
                         DBinputs['fyear'],DBinputs['fmnth'],DBinputs['fday'])      
    daysList = DOI.dateList                                                         # Create a list of days within date range
    
    #---------------------------------------------
    # Determine if spectral DB file already exists
    #---------------------------------------------
    if os.path.isfile(DBinputs['outputDBfile']):
        wmode = 'a'
    else:
        wmode = 'w'
    
    #--------------------------------
    # Open Spectral DB file for write
    #--------------------------------   
    with open(DBinputs['outputDBfile'],wmode) as fopen:        
        #-------------------------------------------
        # If spectral DB does not exist write header
        #-------------------------------------------  
        rtn = sp.Popen( [DBinputs['Fckopus'],'-H'], stdout=sp.PIPE, stderr=sp.PIPE )
        stdoutHeader, stderr = rtn.communicate()        
        outstrHdr            = stdoutHeader.strip().split()

        if (wmode == 'w'):                       
            strformat = ['{0:<15}'] + [' {'+str(i)+':<12}' for i in range(1,len(outstrHdr))]
            strformat = ''.join(strformat).lstrip().rstrip() + '\n'            
            
            fopen.write(strformat.format(*outstrHdr))

        #-----------------------------------------    
        # Find FLT ID to change Name (iom, Dec 4 2018)
        #-----------------------------------------
        indFlt = [i for i, s in enumerate(outstrHdr) if s == 'Flt'][0]

        #-----------------------------------------    
        # Search each day directory for data files 
        #-----------------------------------------
        # Initialize process list
        procList = []
        for indvday in daysList:

            print indvday
                        
            # Find year month and day strings
            yrstr   = "{0:02d}".format(indvday.year)
            mnthstr = "{0:02d}".format(indvday.month)
            daystr  = "{0:02d}".format(indvday.day)  
            yyyymmddstr = yrstr + mnthstr + daystr
            
            dayDir = DBinputs['dataBaseDir'] + yyyymmddstr + '/'
            
            if not ckDir(dayDir):
                continue
            
            #------------------------------------------
            # Gather all files within the day directory
            # to test if these are OPUS files
            #------------------------------------------
            fnames = findFiles(dayDir)
                  
            #-----------------------------
            # Loop through all files found
            #-----------------------------
            for indvfile in fnames:
                
                #--------------------------------------------------------
                # Test if file is opus type. If the file in not opus type
                # a return code of 1 or 3 is kicked back when the -C
                # option is used
                #--------------------------------------------------------
                if not checkOPUS(DBinputs['Fckopus'],indvfile):
                    continue
                
                procList.extend([os.path.dirname(indvfile)])
                
                #--------------------------------------
                # For found spectral data files run 
                # ckopus with -D option to get one line 
                # parameter list for database
                #--------------------------------------
                if ( DBinputs['SBlockType'] and isinstance(DBinputs['SBlockType'],str) ):
                    SBlockTemp = DBinputs['SBlockType']
                else:
                    SBlockTemp = 'NONE'                 
                    
                paramList = [DBinputs['Fckopus'],'-S'+DBinputs['loc'],'-D'+SBlockTemp]   # Build initial parameter list for ckopus call
                paramList.extend(DBinputs['ckopusFlgs'])                                 # Add flags from input file to parameter list
                paramList.append(indvfile)                                               # Add OPUS filename to parameter list
                
                #if (DBinputs['loc'].lower() == 'mlo') and (indvday < dt.date(1995,01,01)):
                    #paramList = [DBinputs['Fckopus'],'-S'+DBinputs['loc'],'-U','-t-150',indvfile]
                #else:    
                    #paramList = [DBinputs['Fckopus'],'-S'+DBinputs['loc'],'-D',indvfile]
                    
                rtn = sp.Popen( paramList, stdout=sp.PIPE, stderr=sp.PIPE )
                stdoutParam, stderr = rtn.communicate()
                
                # Some OPUS files may not contain any data and therefore
                # pass back an error
                if 'error' in stdoutParam or not(stdoutParam):
                    continue
                                
                #-----------------------------------------------------
                # Determine if OPUS file is in correct date folder. If 
                # not move to correct folder. This does not guarantee
                # that the file in the wrong directory will be processed
                # if the code has already processed the correct directory
                # the file will not process (Need to fix!!!!!!!!!)
                #-----------------------------------------------------
                # Date from ckopus
                opusFileDate = stdoutParam.strip().split()[5]
                
                # Compare with current directory date
                if opusFileDate == yyyymmddstr: 
                    #---------------------------------------------------
                    # Parse output from ckopus to write to database file
                    # and remove path from filename/path
                    #---------------------------------------------------
                    outstr    = stdoutParam.strip().split()
                    outstr[0] = os.path.split(outstr[0])[1]
                    strformat = ['{0:<15}'] + [' {'+str(i)+':<12}' for i in range(1,len(outstr))]
                    strformat = ''.join(strformat).lstrip().rstrip() + '\n'

                    #--------------------------------------
                    # Do not include spectra different than S* (iom, Dec 4 2018)
                    #--------------------------------------
                    if outstr[0][0].upper() != 'S':
                        continue

                    #--------------------------------------
                    # Replace X for FLT ID in spectrum name
                    #--------------------------------------
                    fltid = outstr[0][1]
                    outstr[indFlt] = fltid.upper()

                    #--------------------------------------
                    # print in file
                    #--------------------------------------                                
                    fopen.write(strformat.format(*outstr))
                                    
                    #fopen.write( stdoutParam )
                else:
                    newDayDir = DBinputs['dataBaseDir'] + opusFileDate + '/'
                    print 'File: ' + dayDir + os.path.basename(indvfile) + ' In wrong directory. Moving to: ' + newDayDir + os.path.basename(indvfile)
                    if ckDir(newDayDir): shutil.move(dayDir + os.path.basename(indvfile), newDayDir + os.path.basename(indvfile))
                    else:              
                        print 'Creating directory: ' + newDayDir 
                        os.mkdir(newDayDir)
                        shutil.move(dayDir + os.path.basename(indvfile), newDayDir + os.path.basename(indvfile))
                    continue
                
                #-----------------------------------
                # Run ckopus to create bnr file type
                # Grab SBlock and TStamp to convert 
                # to bnr type
                #-----------------------------------
                if DBinputs['bnrWriteFlg']:
                    # Get SBlock and TStamp from ckopus -D <file>
                    if not ('SBlock' in locals()):
                        stdoutHeader = stdoutHeader.strip().split()
                        indSBlock    = stdoutHeader.index('SBlock')
                        indTStamp    = stdoutHeader.index('TStamp')
                        
                    singleDBline = stdoutParam.strip().split()
                    TStamp       = singleDBline[indTStamp]
                    
                    if ( DBinputs['SBlockType'] and isinstance(DBinputs['SBlockType'],str) ):
                        SBlock = DBinputs['SBlockType']
                    else:
                        SBlock = singleDBline[indSBlock] 
                    
                    #----------------------------------
                    # Run ckopus to convert to bnr type
                    #----------------------------------
                    #--------------------------------------------
                    # Make sure cwd is same location as OPUS file
                    #--------------------------------------------
                    fpath,_ = os.path.split(indvfile)
                    
                    if not fpath == os.getcwd():
                        os.chdir(fpath)
                        
                    #-------------------------------------------
                    # For mlo prior to 1995 a utc offset must be
                    # applied through ckopus flags
                    #-------------------------------------------
                    paramList = [DBinputs['Fckopus'],'-S'+DBinputs['loc']]   # Build initial parameter list for ckopus call
                    paramList.append('-' + DBinputs['bnrType'] + SBlock)     # Add bnr and spectral block type
                    paramList.extend(DBinputs['ckopusFlgs'])                 # Add flags from input file to parameter list
                    paramList.append(indvfile)                               # Add OPUS filename to parameter list                    
                    
                    
                    #if (DBinputs['loc'].lower() == 'mlo') and (indvday < dt.date(1995,01,01)):
                        #paramList    = [DBinputs['Fckopus'],'-S'+DBinputs['loc'],'-U','-t-150','-'+DBinputs['bnrType']+SBlock,indvfile]
                    #else:    
                        #paramList    = [DBinputs['Fckopus'],'-S'+DBinputs['loc'],'-'+DBinputs['bnrType']+SBlock,indvfile]
                    
                    rtn = sp.Popen( paramList, stdout=sp.PIPE, stderr=sp.PIPE )
                    stdoutParam, stderr = rtn.communicate()       
                    
                    #-----------------------------------------------------
                    # Find name of file. This may not correspond to SBlock
                    # name if SBlock name is set to NONE. Name of file
                    # is printed in stderr of subprocess
                    #-----------------------------------------------------
                    ind = stderr.find('Closed bnr file:')
                    bnrFname = stderr[ind:].strip().split()[-1]
                                        
                    #------------------------------------------------
                    # Change name of file to correspond to time stamp
                    #------------------------------------------------
                    if os.path.isfile('/'.join([fpath,bnrFname])):
                        shutil.move(fpath+'/'+bnrFname, fpath+'/'+TStamp+'.bnr')
                    else:
                        print 'Unable to move file: %s to %s' %(indvfile,fpath+'/'+TStamp+'.bnr')
                    
    #-------------------------------------------
    # Write list of folders that where processed
    #-------------------------------------------
    if DBinputs['DaysProcFlg']:
        #------------------------------        
        # Create a unique ordered set
        #------------------------------
        procList = list(set(procList))    
        procList.sort()
        fProcname = DBinputs['DaysProcDir'] + 'FldrsProc_' + dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.list'
        with open(fProcname,'w') as fopen:
            for item in procList:
                fopen.write('%s\n' % item)
                        
                                                                             
if __name__ == "__main__":
    main(sys.argv[1:])