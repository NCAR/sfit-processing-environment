#! /usr/local/python-2.7/bin/python

#----------------------------------------------------------------------------------------
# Name:
#        pullAncillaryData.py
#
# Purpose:
#       This program pulls remote data from MLO and TAB sites. To be used in under cron.
#           
#
# Notes:
#       1) Command line arguments
#            -d   YYYYMMDD       : Specify the start and stop date to get data.
#                                  Default is previous utc day
#
# Usage:
#     pullRemoteData.py 
#
# Examples:
#    ./pullRemoteData.py 
#
# Version History:
#  1.0     Created, November, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
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

                            #-------------------------#
                            # Define helper functions #
                            #-------------------------#
                            
def usage():
    ''' Prints to screen standard program usage'''
    print 'pullAncillaryData.py [-d YYYYMMDD_YYYMMDD]'                            

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
            try:    os.chmod(path, 0o777)   
            except: pass    

def ckDirMk(dirName,logFlg=False):
    ''' '''
    if not ( os.path.exists(dirName) ):
        os.makedirs( dirName, mode=0777 )
        if logFlg: logFlg.info( 'Created folder {}'.format(dirName))
        return False
    else:
        return True
                            #----------------------------#
                            #                            #
                            #        --- Main---         #
                            #                            #
                            #----------------------------#

def main(argv):

    dateFlg = False
    mloFlg  = True
    tabFlg  = True
                                                #---------------------------------#
                                                # Retrieve command line arguments #
                                                #---------------------------------#
    #------------------------------------------------------------------------------------------------------------#                                             
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:')

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
        if opt == '-d':           
            
            if not arg:
                print 'Date fromat must be YYYMMDD'
                sys.exit()
                
            dateFlg = True
            dates   = arg.strip()

            iyear   = int(dates[0:4])
            imnth   = int(dates[4:6])
            iday    = int(dates[6:])
          
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
    # NCEP nmc
    NCEPhgtDir  = '/data1/ancillary_data/NCEP_NMC/height/'
    NCEPtempDir = '/data1/ancillary_data/NCEP_NMC/temp/'

    # NCEP reanalysis
    NCEPreDir1  = '/data1/ancillary_data/NCEPdata/NCEP_hgt/'
    NCEPreDir2  = '/data1/ancillary_data/NCEPdata/NCEP_Shum/'
    NCEPreDir3  = '/data1/ancillary_data/NCEPdata/NCEP_Temp/'
    NCEPreDir4  = '/data1/ancillary_data/NCEPdata/NCEP_trpp/'
    
    # ERA reanalysis
    ERAreDir    = '/data1/ancillary_data/ERAdata/'
    
    # FL0 EOL data
    FL0_eolDir  = '/data1/ancillary_data/fl0/eol/'
    
    # MLO CMDL data
    MLO_cmdlDir1 = '/data1/ancillary_data/mlo/cmdl/Hourly_Data/'
    MLO_cmdlDir2 = '/data1/ancillary_data/mlo/cmdl/Minute_Data/'
    
    # Log File name
    logFname     = '/data1/ebaumer/pullAncillaryData.log'
    
    #------------------------------------
    # Get the current date and time (UTC)
    #------------------------------------
    curntDateUTC = dt.datetime.utcnow()
        
    #--------------------------------------------
    # Get date list:
    # -- If command line arguments are used then
    #    datelist corresponds to list of days 
    #    given in command line
    # -- If no command line arguments then create
    #    list starting from previous UTC date
    #    extending back ndaysbck
    #--------------------------------------------
    if dateFlg: curntDateUTC = dt.date(iyear,imnth,iday)    

    #------------------------------------
    # Start log information for this pull
    #------------------------------------
    logFilePull = logging.getLogger('1')
    logFilePull.setLevel(logging.INFO)
    hdlr1   = logging.FileHandler(logFname, mode='a+')
    fmt1    = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s','%a, %d %b %Y %H:%M:%S')
    hdlr1.setFormatter(fmt1)
    logFilePull.addHandler(hdlr1)  
    logFilePull.info('**************** Starting Logging for New Day ***********************')
    logFilePull.info('Current Time (UTC):        ' + str(curntDateUTC) )    

    #----------
    # Pull Data
    #----------
    #-----------------
    # Get Current Year
    #-----------------
    yrstr = '{:4d}'.format(curntDateUTC.year)
    
    # NCEP nmc
    # Check if directories exist
    ckDirMk(NCEPhgtDir+yrstr+'/',logFlg=logFilePull)
    ckDirMk(NCEPtempDir+yrstr+'/',logFlg=logFilePull)
    
    cmnd = ['wget','-r','-l1','-nd','-N','--no-parent','-A*.nmc', '-P'+NCEPhgtDir+yrstr+'/', 'ftp://ftp.cpc.ncep.noaa.gov/ndacc/ncep/height/'+yrstr+'/'  ]
    (stdoutInfo,stderrInfo) = subProcRun( cmnd, logFilePull )
    chMod(NCEPhgtDir+yrstr+'/')    
    
    cmnd = ['wget','-r','-l1','-nd','-N','--no-parent','-A*.nmc', '-P'+NCEPtempDir+yrstr+'/', 'ftp://ftp.cpc.ncep.noaa.gov/ndacc/ncep/temp/'+yrstr+'/'  ]
    (stdoutInfo,stderrInfo) = subProcRun( cmnd, logFilePull )
    chMod(NCEPtempDir+yrstr+'/')
    
    # NCEP reanalysis
    cmnd = ['wget','-r','-l1','-nd','-N','--no-parent','-Ahgt.*.nc', '-P'+NCEPreDir1, 'ftp://ftp.cdc.noaa.gov/Datasets/ncep.reanalysis.dailyavgs/pressure/'  ]
    (stdoutInfo,stderrInfo) = subProcRun( cmnd, logFilePull )
    chMod(NCEPreDir1)    
    
    cmnd = ['wget','-r','-l1','-nd','-N','--no-parent','-Ashum.*.nc', '-P'+NCEPreDir2, 'ftp://ftp.cdc.noaa.gov/Datasets/ncep.reanalysis.dailyavgs/pressure/'  ]
    (stdoutInfo,stderrInfo) = subProcRun( cmnd, logFilePull )
    chMod(NCEPreDir2)    
    
    cmnd = ['wget','-r','-l1','-nd','-N','--no-parent','-Aair.*.nc', '-P'+NCEPreDir3, 'ftp://ftp.cdc.noaa.gov/Datasets/ncep.reanalysis.dailyavgs/pressure/'  ]
    (stdoutInfo,stderrInfo) = subProcRun( cmnd, logFilePull )
    chMod(NCEPreDir3)        
    
    cmnd = ['wget','-r','-l1','-nd','-N','--no-parent','-Apres.*.nc', '-P'+NCEPreDir4, 'ftp://ftp.cdc.noaa.gov/Datasets/ncep.reanalysis.dailyavgs/tropopause/'  ]
    (stdoutInfo,stderrInfo) = subProcRun( cmnd, logFilePull )
    chMod(NCEPreDir4)     
    
    # fl0 EOL
    cmnd = ['wget','-r','-l1','-nd','-N','--no-parent','-Aflab.'+yrstr+'*.cdf', '-P'+FL0_eolDir, 'ftp://ftp.eol.ucar.edu/pub/archive/weather/foothills/'  ]
    (stdoutInfo,stderrInfo) = subProcRun( cmnd, logFilePull )
    chMod(NCEPreDir4)    
    
    # MLO cmdl hourly
    cmnd = ['wget','-r','-l1','-nd','-N','--no-parent','-Amet_mlo_insitu_1_obop_hour_'+yrstr+'.txt', '-P'+MLO_cmdlDir1, 'ftp://aftp.cmdl.noaa.gov/data/meteorology/in-situ/mlo/'  ]
    (stdoutInfo,stderrInfo) = subProcRun( cmnd, logFilePull )
    chMod(MLO_cmdlDir1)       
    
    # MLO cmdl minute
    cmnd = ['wget','-r','-l1','-nd','-N','--no-parent','-Amet_mlo_insitu_1_obop_minute_'+yrstr+'*.txt', '-P'+MLO_cmdlDir2, 'ftp://aftp.cmdl.noaa.gov/data/meteorology/in-situ/mlo/'+yrstr+'/'  ]
    (stdoutInfo,stderrInfo) = subProcRun( cmnd, logFilePull )
    chMod(MLO_cmdlDir2)      

    # ERA Interim data
    # This needs a RSA key to be set up....

    
if __name__ == "__main__":
    main(sys.argv[1:])
