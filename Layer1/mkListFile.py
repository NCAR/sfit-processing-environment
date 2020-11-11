#! /usr/local/python-2.7/bin/python
# Change the above line to point to the location of your python executable
#----------------------------------------------------------------------------------------
# Name:
#        mkListFile.py
#
# Purpose:
#       This program makes a list file based on a directory structure. Typically, list files
#       are made during processing. This program allows one to make a list file post process.
#
#
#
# Notes:
#       1) Options include:
#            -i <file>      : Path and file name of Layer1 input file
#            -N <file Name> : Path and file name for output list file
#            -d <dir>       : Base directory
#
#
# Usage:
#      ./mkListFile.py -i /data/ebaumer/MLO_input.py -N /data/ebaumer/2008.lst -d /data/ebaumer/2008/
#
#
#
# Version History:
#       Created, Nov, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
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
import sys
import logging
import os
import getopt
import glob
import shutil
import sfitClasses as sc
import datetime as dt
                                #-------------------------#
                                # Define helper functions #
                                #-------------------------#
def usage():
    ''' Prints to screen standard program usage'''
    print 'mkListFile.py -i <file> -N <file> -d <dir> -?'
    print '  -i <file> : Path and file name of Layer1 input file'
    print '  -N <file> : Path and file name for output list file'
    print '  -d <dir>  : Base directory of data'
    print '  -?        : Show all flags'

def ckDir(dirName,exit=False):
    ''' '''
    if not os.path.exists( dirName ):
        print 'Input Directory %s does not exist' % (dirName)
        if exit: sys.exit()
        return False
    else:
        return True

def ckFile(fName,exit=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print 'File %s does not exist' % (fName)
        if exit: sys.exit()
        return False
    else:
        return True    
    
def sortDict(DataDict,keyval):
    ''' Sort all values of dictionary based on values of one key'''
    base = DataDict[keyval]
    for k in DataDict:
        DataDict[k] = [y for (x,y) in sorted(zip(base,DataDict[k]))]
    return DataDict


                                #----------------------------#
                                #                            #
                                #        --- Main---         #
                                #                            #
                                #----------------------------#

def main(argv):
    #--------------------------------
    # Retrieve command line arguments
    #--------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:N:d:?')

    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit()
        
    #-----------------------------
    # Parse command line arguments
    #-----------------------------
    for opt, arg in opts:
        
        # Layer1 input path and name
        if opt == '-i':
            inputFile = arg
            
        # Output list file name and directory    
        elif opt == '-N':
            outputFile = arg
            
        # Base Directory for data
        elif opt == '-d':
            baseDir = arg
                
        # Show all command line flags
        elif opt == '-?':
            usage()
            sys.exit()
                                           
        else:
            print 'Unhandled option: ' + opt
            sys.exit()


    #---------------------------------
    # Initialize list file as log file
    #---------------------------------
    lstFile = logging.getLogger('1')
    lstFile.setLevel(logging.INFO)
    hdlr1   = logging.FileHandler(outputFile, mode='w')
    fmt1    = logging.Formatter('')
    hdlr1.setFormatter(fmt1)
    lstFile.addHandler(hdlr1)   

    #----------------------------------
    # Check the existance of input file
    #----------------------------------
    ckFile(inputFile,exit=True)
    
    #--------------------------------------
    # Check the existance of base directory
    #--------------------------------------
    ckDir(baseDir,exit=True)
    # check if '/' is included at end of path
    if not( baseDir.endswith('/') ):
        baseDir = baseDir + '/'       
    
    #-------------------------
    # Get data from input file
    #-------------------------
    inVars = sc.Layer1InputFile(inputFile)
    inVars.getInputs()

    #--------------------------------
    # Check the existance of ctl file
    #--------------------------------
    ckFile(inVars.inputs['ctlList'][0][0],exit=True)

    #------------------
    # Get ctl file data
    #------------------
    ctlData = sc.CtlInputFile(inVars.inputs['ctlList'][0][0])
    ctlData.getInputs()
    
    #------------------------
    # Write data to list file
    #------------------------
    lstFile.info('# Begin List File Meta-Data'                                 )
    lstFile.info('Start Date     = '                                           )
    lstFile.info('End Date       = '                                           )
    lstFile.info('WACCM_File     = ' + inVars.inputs['WACCMfile']              )
    lstFile.info('ctl_File       = ' + inVars.inputs['ctlList'][0][0]    )
    lstFile.info('FilterID       = ' + inVars.inputs['ctlList'][0][1]    )
    lstFile.info('VersionName    = ' + inVars.inputs['ctlList'][0][2]    )
    lstFile.info('Site           = ' + inVars.inputs['loc']                 )
    lstFile.info('statnLyrs_file = ' + ctlData.inputs['file.in.stalayers'][0])
    lstFile.info('primGas        = ' + ctlData.primGas                       )
    lstFile.info('specDBfile     = ' + inVars.inputs['spcdbFile']              )
    lstFile.info('Coadd flag     = ' + str(inVars.inputs['coaddFlg'])          )
    lstFile.info('nBNRfiles      = ' + str(inVars.inputs['nBNRfiles'])         )
    lstFile.info('ilsFlg         = ' + str(inVars.inputs['ilsFlg'])            )
    lstFile.info('pspecFlg       = ' + str(inVars.inputs['pspecFlg'])          )
    lstFile.info('refmkrFlg      = ' + str(inVars.inputs['refmkrFlg'])         )
    lstFile.info('sfitFlg        = ' + str(inVars.inputs['sfitFlg'])           )
    lstFile.info('lstFlg         = ' + str(inVars.inputs['lstFlg'])            )
    lstFile.info('errFlg         = ' + str(inVars.inputs['errFlg'])            )
    lstFile.info('zptFlg         = ' + str(inVars.inputs['zptFlg'])            )
    lstFile.info('refMkrLvl      = ' + str(inVars.inputs['refMkrLvl'])         )
    lstFile.info('wVer           = ' + str(inVars.inputs['wVer'])              )
    lstFile.info('nbands         = ' + str(len(ctlData.inputs['band']))        )
    lstFile.info('# End List File Meta-Data')
    lstFile.info('')
    lstFile.info('Date         TimeStamp    Directory ')

    #-----------------------------------------------------
    # Loop through directory to find all valid retreivals.
    # Retrieval is valid when summary file exists.
    #-----------------------------------------------------
    #----------------------------------------
    # Walk through first level of directories
    #----------------------------------------
    lstDict = {}
    for drs in os.walk(baseDir).next()[1]:
        YYYYMMDD = drs[0:4]  + drs[4:6]   + drs[6:8]
        hhmmss   = drs[9:11] + drs[11:13] + drs[13:]     
        if os.path.isfile(baseDir + drs + '/summary'):
            lstDict.setdefault('date',[]).append(dt.datetime(int(drs[0:4]), int(drs[4:6]), int(drs[6:8]), int(drs[9:11]), int(drs[11:13]), int(drs[13:]) ))
            lstDict.setdefault('YYYYMMDD',[]).append(YYYYMMDD)
            lstDict.setdefault('hhmmss',[]).append(hhmmss)
            lstDict.setdefault('directory',[]).append(baseDir + drs)
        
    lstDict = sortDict(lstDict,'date')
    for ind,val in enumerate(lstDict['date']):
        lstFile.info("{0:<13}".format(lstDict['YYYYMMDD'][ind]) + "{0:6}".format(lstDict['hhmmss'][ind]) + '       ' + lstDict['directory'][ind]+'/')

if __name__ == "__main__":
    main(sys.argv[1:])
