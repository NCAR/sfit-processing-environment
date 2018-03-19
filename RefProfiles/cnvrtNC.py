#!/usr/bin/python
##! /usr/local/python-2.7/bin/python

#----------------------------------------------------------------------------------------
# Name:
#      ERAwaterPrf.py
#
# Purpose:
#      This program creates water VMR from NCEP daily water data and writes an output file
#      in standard reference.profile format
#           
#
# Input files:
#       1) NCEP specific humidity and geopotential height NetCDF files
#
# Output files:
#       1) 
#
#
# Notes:
#       1)
#
#
# Usage:
#
#
# Version History:
#  1.0     Created, June, 2014  Eric Nussbaumer (ebaumer@ucar.edu)
#
#
# References:
#
#----------------------------------------------------------------------------------------


                        #-------------------------#
                        # Import Standard modules #
                        #-------------------------#
import sys
import os
import shutil
import subprocess
import logging
import datetime as dt
import sfitClasses as sc
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline as intrpUniSpl
from scipy.interpolate import interp2d
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import scipy as sp
from scipy.io import netcdf

                        #-------------------------------------#
                        # Define helper functions and classes #
                        #-------------------------------------#
                        
def subProcRun( fnameIn, outDir, logFlg=False ):
    '''This runs a system command and directs the stdout and stderr'''
    #rtn = subprocess.Popen( fnameIn, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
    rtn = subprocess.Popen( 'ncl_convert2nc ' + fnameIn + ' -o ' + outDir, shell=True, stderr=subprocess.PIPE )
    outstr = ''
    for line in iter(rtn.stderr.readline, b''):
        print 'STDERR from {}: '.format(fnameIn) + line.rstrip()
        if logFlg: outstr += line

    if logFlg: logFlg.info(outstr)

    return True

def ckDir(dirName,exitFlg=False):
    ''' '''
    if not os.path.exists( dirName ):
        print 'Input Directory %s does not exist' % (dirName)
        if exitFlg: sys.exit()
        return False
    else:
        return True   

def ckFile(fName,exitFlg=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print 'File %s does not exist' % (fName)
        if exitFlg: sys.exit()
        return False
    else:
        return True 
                
def segmnt(seq,n):
    '''Yeilds successive n-sized segments from seq'''
    for i in xrange(0,len(seq),n): yield seq[i:i+n]

def findCls(dataArray, val):
    ''' Returns the indice and closest value in dataArray to val'''
    return np.argmin(abs(val-dataArray))
    

                            #----------------------------#
                            #                            #
                            #        --- Main---         #
                            #                            #
                            #----------------------------#
                            
def main():
    
    
    #-----------------------
    # Date Range of interest
    #-----------------------
    iyear          = 2017
    imnth          = 11
    iday           = 1
    fyear          = 2017
    fmnth          = 12
    fday           = 31
    
    #-----------------------
    # File name for log file
    #-----------------------
    logFname = '/data1/ancillary_data/ERAdata/ncLog4.log'

    #---------------------
    # Establish date range
    #---------------------
    dRange = sc.DateRange(iyear,imnth,iday,fyear,fmnth,fday) 
    
    #------------------------------
    # ERA Reanalysis data directory
    #------------------------------
    ERAdir = '/data1/ancillary_data/ERAdata/'
    #ERAdir = '/data1/ancillary_data/ERAdata/wind/'   ->Use for Wind in TAB

        
    #----------------------------
    # File and directory checking
    #----------------------------
    ckDir(ERAdir,exitFlg=True)
    
    #--------------------
    # Initialize log file
    #--------------------
    lFile = logging.getLogger('1')
    lFile.setLevel(logging.INFO)
    hdlr1 = logging.FileHandler(logFname,mode='w')
    fmt1  = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s','%a, %d %b %Y %H:%M:%S')
    hdlr1.setFormatter(fmt1)    
    lFile.addHandler(hdlr1)

    #------------------------------------
    # Loop through all days in date range
    #------------------------------------
    for sngDay in dRange.dateList:
        YYYY = "{0:04d}".format(sngDay.year)
        MM   = "{0:02d}".format(sngDay.month)
        DD   = "{0:02d}".format(sngDay.day)         
    
        #------------------------------
        # Name of ERA Interim GRIB file
        #------------------------------
        fName1 = ERAdir + YYYY + MM +'/'+'ei.oper.an.pl.regn128sc.'+YYYY+MM+DD+'00'
        fName2 = ERAdir + YYYY + MM +'/'+'ei.oper.an.pl.regn128sc.'+YYYY+MM+DD+'06'
        fName3 = ERAdir + YYYY + MM +'/'+'ei.oper.an.pl.regn128sc.'+YYYY+MM+DD+'12'
        fName4 = ERAdir + YYYY + MM +'/'+'ei.oper.an.pl.regn128sc.'+YYYY+MM+DD+'18'

        #------------------------------------
        #Use for Wind in TAB
        #------------------------------------
        #fName1 = ERAdir + YYYY + MM +'/'+'ei.oper.an.pv.regn128sc.'+YYYY+MM+DD+'00'
        #fName2 = ERAdir + YYYY + MM +'/'+'ei.oper.an.pv.regn128sc.'+YYYY+MM+DD+'06'
        #fName3 = ERAdir + YYYY + MM +'/'+'ei.oper.an.pv.regn128sc.'+YYYY+MM+DD+'12'
        #fName4 = ERAdir + YYYY + MM +'/'+'ei.oper.an.pv.regn128sc.'+YYYY+MM+DD+'18'


        ckFile(fName1, exitFlg=True)
        ckFile(fName2, exitFlg=True)
        ckFile(fName3, exitFlg=True)
        ckFile(fName4, exitFlg=True)
    
        #------------------------------------------
        # Rename ERA Interim file (add .grb at end)
        # so ncl_convert2nc recognizes file
        #------------------------------------------
        shutil.move(fName1,fName1+'.grb')
        shutil.move(fName2,fName2+'.grb')
        shutil.move(fName3,fName3+'.grb')
        shutil.move(fName4,fName4+'.grb')
        
        #-------------------------------------
        # Run NCL program to convert to netCDF
        #-------------------------------------
        subProcRun(fName1+'.grb',ERAdir + YYYY + MM +'/',logFlg=lFile)
        subProcRun(fName2+'.grb',ERAdir + YYYY + MM +'/',logFlg=lFile)
        subProcRun(fName3+'.grb',ERAdir + YYYY + MM +'/',logFlg=lFile)
        subProcRun(fName4+'.grb',ERAdir + YYYY + MM +'/',logFlg=lFile)
    
        #-----------------
        # Remove grib file
        #-----------------
        os.remove(fName1+'.grb')
        os.remove(fName2+'.grb')
        os.remove(fName3+'.grb')
        os.remove(fName4+'.grb')
    
        
        print 'Finished processing day: {}'.format(sngDay)
                                                                                    
if __name__ == "__main__":
    main()