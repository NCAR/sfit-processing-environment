#! /usr/bin/python
# #! /usr/local/python-2.7/bin/python

#----------------------------------------------------------------------------------------
# Name:
#        delSpcdel.py
#
# Purpose:
#       - This program makes sure that spectra deleted from ckopus are actually deleted.
#       - We found this handy when sync is done again to ya4 after deleting spectra.
#       - Use this program before creating the yearly SpcDatabase
# Notes:
#       1) Command line arguments
#            -y   YYYY                 : Specify the year.
#            -s     tab/mlo/fl0        : Specify the location to process either tab/mlo/fl0
#                                    
#
# Usage:
#     delSpcdel.py
#
#
# Version History:
#  1.0     Created, November, 2016, June  Ivan Ortega (iortega@ucar.edu)
#
#----------------------------------------------------------------------------------------


                            #-------------------------#
                            # Import Standard modules #
                            #-------------------------#

import datetime as dt
import sys
import os
import itertools
import getopt
import shutil
import subprocess as sp
import logging
import glob

                            #-------------------------#
                            # Define helper functions #
                            #-------------------------#

def usage():
    ''' Prints to screen standard program usage'''
    print 'delSpcdel.py [-y YYYY -s tab/mlo/fl0]'

def subProcRun( sysCall, logF=False, shellFlg=False ):
    '''This runs a system command and directs the stdout and stderr'''
    rtn = sp.Popen( sysCall, stdout=sp.PIPE, stderr=sp.PIPE, shell=shellFlg )
    stdoutInfo, stderrInfo = rtn.communicate()

    if logF:
        if stdoutInfo: logF.info( stdoutInfo )
        if stderrInfo: logF.error( stderrInfo )

    return (stdoutInfo,stderrInfo)

def dateList(iyear,imnth,iday,fyear,fmnth,fday):
    i_date = dt.date(iyear,imnth,iday)
    f_date = dt.date(fyear,fmnth,fday)
    ndays  = (f_date + dt.timedelta(days=1) - i_date).days
    Dlist  = [i_date + dt.timedelta(days=i) for i in range(0, ndays, 1)]
    return Dlist

def chMod(PrntPath):
    for dirpath, dirnames, filenames in os.walk(PrntPath):
        try:    os.chmod(dirpath,0o777)
        except: pass
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            try:    os.chmod(path, 0o666)
            except: pass

def ckDir(dirName,logFlg=False,exit=False):
    ''' '''
    if not os.path.exists( dirName ):
        print 'Input Directory %s does not exist' % (dirName)
        if logFlg: logFlg.error('Directory %s does not exist' % dirName)
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

    tabFlg = False
    mloFlg = False
    fl0Flg = False

                                                #---------------------------------#
                                                # Retrieve command line arguments #
                                                #---------------------------------#
    #------------------------------------------------------------------------------------------------------------#
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'y:s:')

    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit()

    
    #-----------------------------
    # Parse command line arguments
    #-----------------------------
    for opt, arg in opts:

        #-----------
        # Start Date
        #-----------
        if opt == '-y':

            if len(arg) == 4:

                dates   = arg.strip().split('_')

                iyear   = int(dates[0][0:4])
                imnth   = int(1)
                iday    = int(1)

                fyear   = iyear
                fmnth   = int(12)
                fday    = int(31)

            else:
                print 'Error in input year'
                usage()
                sys.exit()


        #------------------
        # Single site usage
        #------------------
        elif opt == '-s':

            if   arg.strip().lower() == 'mlo': 
                mloFlg = True
                site   = 'mlo'
            elif arg.strip().lower() == 'tab':
                tabFlg = True
                site  = 'tab'
            elif arg.strip().lower() == 'fl0': 
                fl0Flg = True
                site   = 'fl0'
            else:
                print 'Site: ' + arg + ' not recognized. Options: mlo or tab or fl0'
                sys.exit()

        #------------------
        # Unhandled options
        #------------------
        else:
            print 'Unhandled option: ' + opt
            usage()
            sys.exit()
    #------------------------------------------------------------------------------------------------------------#

    #-------------------
    # Set some constants
    #-------------------
    locBaseDir  = '/data1/'                                        # Local base data directory
    if site == 'mlo': logFname = locBaseDir + 'mlo_del2del.log'                   # MLO log file path and name
    if site == 'tab': logFname = locBaseDir + 'tab_del2del.log'                   # TAB log file path and name
    if site == 'fl0': logFname = locBaseDir + 'fl0_del2del.log'                   # TAB log file path and name
   
    #------------------------------------
    # Get the current date and time (UTC)
    #------------------------------------
    curntDateUTC = dt.datetime.utcnow()

    #--------------------------------------------
    # Get date list:
    #--------------------------------------------
    Listdays = dateList(iyear,imnth,iday,fyear,fmnth,fday)

    #------------------------------------------
    # Start log information for this pull (MLO)
    #------------------------------------------
    fmt1    = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s','%a, %d %b %Y %H:%M:%S')

    logFile = logging.getLogger('1')
    logFile.setLevel(logging.INFO)
    hdlr1   = logging.FileHandler(logFname, mode='a+')
    hdlr1.setFormatter(fmt1)
    logFile.addHandler(hdlr1)
    logFile.info('**************** Starting Logging ***********************')
    logFile.info('Current Time (UTC):        ' + str(curntDateUTC) )

    #----------
    # Pull Data
    #----------
    for indvDay in Listdays:

        YYYYstr  = "{0:4d}".format( indvDay.year)
        MMstr    = "{0:02d}".format(indvDay.month)
        DDstr    = "{0:02d}".format(indvDay.day)
        YYYYMMDD = YYYYstr + MMstr + DDstr

        #--------------------------------------------
        # Spectra Dir:
        #--------------------------------------------
        dirSpc    = locBaseDir + site +'/' + YYYYMMDD +'/'
        spc = glob.glob(dirSpc+ 's*')
        spc = [os.path.basename(f) for f in spc]
        
        if ckDir(dirSpc):

            #--------------------------------------------
            # Spectra deleted Dir:
            #--------------------------------------------
            dirSpcDel = locBaseDir + site + '/' + YYYYMMDD +'/deleted/'

            if ckDir(dirSpcDel):

                spcDeleted = glob.glob(dirSpcDel+ 's*')
                spcDeleted = [os.path.basename(f) for f in spcDeleted]

                for s in spcDeleted:
                    #--------------------------------------------
                    # Remove if needed:
                    #--------------------------------------------
                    if s in spc:
                        print "Found File in Deleted folder: {}".format(dirSpc + s)
                        if logFile: logFile.info('Deleting File: ' + dirSpc + s)
                        os.remove(dirSpc + s)


if __name__ == "__main__":
    main(sys.argv[1:])
