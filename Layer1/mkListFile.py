#!/usr/bin/python
##! /usr/local/python-2.7/bin/python
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
#      mkListFile.py -i /data/ebaumelsr/MLO_input.py -N /data/ebaumer/2008.lst -d /data/ebaumer/2008/
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
import os, sys
sys.path.append((os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "ModLib")))
import logging
import getopt
import glob
import shutil
import sfitClasses as sc
import datetime as dt
import numpy as np
                                #-------------------------#
                                # Define helper functions #
                                #-------------------------#
def usage():
    ''' Prints to screen standard program usage'''
    print ('mkListFile.py -i <file> -N <file> -d <dir> -?')
    print ('  -i <file> : Path and file name of Layer1 input file')
    print ('  -N <file> : Path and file name for output list file')
    print ('  -d <dir>  : Base directory of data (absolute path)')
    print ('  -?        : Show all flags')

def ckDir(dirName,exit=False):
    ''' '''
    if not os.path.exists( dirName ):
        print ('Input Directory %s does not exist' % (dirName))
        if exit: sys.exit()
        return False
    else:
        return True

def ckFile(fName,exit=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print ('File %s does not exist' % (fName))
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
        print (str(err))
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
            print ('Unhandled option: ' + opt)
            sys.exit()

    
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

    if not 'outputFile' in locals():
        version = baseDir.strip().split('/')[-2]
        outputFile =  version+'_latest.lst'  

    #---------------------------------
    #listdir = os.listdir(baseDir)
    #AllDir  = [d for d in listdir if len(d) == 15]

    # iyear  = AllDir[0][0:4]
    # imnth  = AllDir[0][4:6]
    # iday   = AllDir[0][6:8]

    # fyear  = AllDir[-1][0:4]
    # fmnth  = AllDir[-1][4:6]
    # fday   = AllDir[-1][6:8]
    #---------------------------------


    #---------------------------------
    # Initialize list file as log file
    #---------------------------------
    lstFile = logging.getLogger('1')
    lstFile.setLevel(logging.INFO)
    hdlr1   = logging.FileHandler(outputFile, mode='w')
    fmt1    = logging.Formatter('')
    hdlr1.setFormatter(fmt1)
    lstFile.addHandler(hdlr1)


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
    lstFile.info('# Begin List File Meta-Data' )
    lstFile.info('Start Date     = ' + str(inVars.inputs['iyear']) +  str(inVars.inputs['imnth']).zfill(2) +  str(inVars.inputs['iday']).zfill(2)  )
    lstFile.info('End Date       = ' + str(inVars.inputs['fyear']) +  str(inVars.inputs['fmnth']).zfill(2) +  str(inVars.inputs['fday']).zfill(2)  )
    #lstFile.info('Start Date     = ' + iyear +  imnth.zfill(2) +  iday.zfill(2)  )
    #lstFile.info('End Date       = ' + fyear +  fmnth.zfill(2) +  fday.zfill(2)  )
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

    msg_snr      =  "     ".join([str('SNR_band_'+str(n+1)) for n in range(len(ctlData.inputs['band']))])
    msg_fit_snr  =  "     ".join([str('FIT_SNR_band_'+str(n+1)) for n in range(len(ctlData.inputs['band']))])
    lstFile.info("{0:<13}".format('Date') + "{0:15}".format('TimeStamp') +"{0:60}".format('Directory') + "{0:35}".format(msg_snr) + "{0:37}".format(msg_fit_snr) + "{0:10}".format('RMS'))

    #START AND FINAL DATE TO CREATE THE LIST (IVAN)
    sdate = str(inVars.inputs['iyear']) + str(inVars.inputs['imnth']).zfill(2)   + str(inVars.inputs['iday']).zfill(2)
    fdate = str(inVars.inputs['fyear']) + str(inVars.inputs['fmnth']).zfill(2)   + str(inVars.inputs['fday']).zfill(2)

    print ('list created from '+sdate +'to '+ fdate)
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

            #print(baseDir)
            #print(drs)

            ret = sc.RetOutput(baseDir + drs)
            ret.readSum('summary')
            
            nmw = len(ctlData.inputs['band'])
            

            #try:
            lstDict.setdefault('date',[]).append(dt.datetime(int(drs[0:4]), int(drs[4:6]), int(drs[6:8]), int(drs[9:11]), int(drs[11:13]), int(drs[13:]) ))
            lstDict.setdefault('YYYYMMDD',[]).append(YYYYMMDD)
            lstDict.setdefault('hhmmss',[]).append(hhmmss)
            lstDict.setdefault('directory',[]).append(baseDir + drs)
            lstDict.setdefault('RMS',[]).append(ret.summary['FITRMS'][0])

            for n in range(nmw):
                lstDict.setdefault('SNR_'+str(n+1),[]).append(ret.summary['SNR_'+str(n+1)][0])
                lstDict.setdefault('FIT_SNR_'+str(n+1),[]).append(ret.summary['FIT_SNR_'+str(n+1)][0])

            #except: pass

    #print(lstDict['SNR_'+str(1)][0])
    #exit()
    lstDict = sortDict(lstDict,'date')
    for ind,val in enumerate(lstDict['date']):
        #msg = header + "".join([str(i) for i in x])
        #snr = [lstDict['SNR_1'][ind] for n in range(nmw)]

        snr     = "     ".join(["{:10}".format(str(np.round(lstDict['SNR_'+str(n+1)][ind], 3))) for n in range(nmw)])
        fit_snr = "     ".join(["{:14}".format(str(np.round(lstDict['FIT_SNR_'+str(n+1)][ind], 3))) for n in range(nmw)])
  
        #if int(lstDict['YYYYMMDD'][ind]) >= int(sdate) and int(lstDict['YYYYMMDD'][ind]) <= int(fdate):
        lstFile.info("{0:<13}".format(lstDict['YYYYMMDD'][ind]) + "{0:15}".format(lstDict['hhmmss'][ind]) +"{0:60}".format(lstDict['directory'][ind]+'/') + "{0:35}".format(snr) + "{0:35}".format(fit_snr) + "{0:10}".format(lstDict['RMS'][ind])  )

if __name__ == "__main__":
    main(sys.argv[1:])
