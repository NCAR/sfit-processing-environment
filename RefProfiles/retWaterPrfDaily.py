#!/usr/bin/python
##! /usr/local/python-2.7/bin/python

#----------------------------------------------------------------------------------------
# Name:
#      NCEPwaterPrf.py
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
import glob
import datetime          as dt
import sfitClasses       as sc
import numpy             as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages



                        #-------------------------------------#
                        # Define helper functions and classes #
                        #-------------------------------------#

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

    #---------
    # Location
    #---------
    loc = 'fl0'

    #------------------------------------
    # Version number to append water file
    #------------------------------------
    verW = 'v5'

    #------
    # Flags
    #------
    pltFlg = True

    #-----------------------
    # Date Range of interest
    #-----------------------
    iyear          = 2018
    imnth          = 10
    iday           = 1
    fyear          = 2018
    fmnth          = 11
    fday           = 30

    #---------------------------------------
    # Size of altitude grid for each station
    #---------------------------------------
    #---------------------------------------
    # Altitude levels for different stations
    #---------------------------------------
    if loc.lower() == 'tab':
        Z = np.array([ 120.0000,    110.0000,    100.0000,     95.0000,     90.0000,
                        85.0000,     80.0000,     75.0000,     70.0000,     65.0000,
                        60.0000,     55.0000,     50.0000,     48.0000,     46.0000,
                        44.0000,     42.0000,     40.0000,     38.0000,     36.0000,
                        34.0000,     32.0000,     30.0000,     28.0000,     26.0000,
                        24.0000,     22.0000,     20.0000,     18.0000,     16.0000,
                        14.0000,     12.0000,     10.0000,      9.0000,      8.0000,
                         7.0000,      6.0000,      5.0000,      4.0000,      3.0000,
                         2.0000,      1.0000,      0.2250   ])

    elif loc.lower() == 'mlo':
        Z = np.array([ 120.0000,    110.0000,    100.0000,     95.0000,     90.0000,
                        85.0000,     80.0000,     75.0000,     70.0000,     65.0000,
                        60.0000,     55.0000,     50.0000,     48.0000,     46.0000,
                        44.0000,     42.0000,     40.0000,     38.0000,     36.0000,
                        34.0000,     32.0000,     30.0000,     28.0000,     26.0000,
                        24.0000,     22.0000,     20.0000,     18.0000,     16.0000,
                        14.0000,     12.0000,     10.0000,      9.0000,      8.0000,
                         7.0000,      6.0000,      5.0000,      4.0000,      3.3960])

    elif loc.lower() == 'fl0':
        Z = np.array([ 120.0000,    110.0000,    100.0000,     94.0000,     90.0000,
                        85.0000,     80.0000,     75.0000,     70.0000,     65.0000,
                        60.0000,     55.0000,     50.0000,     48.0000,     46.0000,
                        44.0000,     42.0000,     40.0000,     38.0000,     36.0000,
                        34.0000,     32.0000,     30.0000,     28.0000,     26.0000,
                        24.0000,     22.0000,     20.0000,     18.0000,     16.0000,
                        14.0000,     12.0000,     10.0000,      9.0000,      8.0000,
                         7.0000,      6.0000,      5.0000,      4.0000,      3.0000,
                         2.0000,      1.6120])

    nlvls = len(Z)

    #---------------
    # Data Directory
    #---------------
    dataDir  = '/data1/'+loc.lower()+'/'

    #---------------------
    # Establish date range
    #---------------------
    dRange = sc.DateRange(iyear,imnth,iday,fyear,fmnth,fday)

    #----------------------------
    # File and directory checking
    #----------------------------
    ckDir(dataDir,exitFlg=True)

    #--------------------------------------------
    # Walk through first level of directories in
    # data directory and collect directory names
    #--------------------------------------------
    dirLst = []
    for drs in os.walk(dataDir).next()[1]:

        #-------------------------------------------
        # Test directory to make sure it is a number
        #-------------------------------------------
        try:    int(drs[0:4])
        except: continue

        if dRange.inRange( int(drs[0:4]), int(drs[4:6]), int(drs[6:8]) ): dirLst.append(dataDir+drs+'/')

    dirLst.sort()

    #-----------------------------------------------
    # Loop through all directories within time frame
    #-----------------------------------------------
    for sngDir in dirLst:

        #----------------------------
        # Get date in datetime format
        #----------------------------
        oneDay = dt.datetime(int(os.path.basename(sngDir[:-1])[0:4]),int(os.path.basename(sngDir[:-1])[4:6]),int(os.path.basename(sngDir[:-1])[6:8]))

        #---------------------------------------------
        # Search for all individual retrieval profiles
        #---------------------------------------------
        zptFiles = glob.glob(sngDir + 'w-120.*.v99')

        nfiles = len(zptFiles)
        if nfiles == 0: continue

        sngH2O = np.zeros((nfiles,nlvls))

        for i,sngFile in enumerate(zptFiles):
            with open(sngFile,'r') as fopen: lines = fopen.readlines()

            sngH2O[i,:] = np.array([float(x) for line in lines[1:] for x in line.strip().split(',')[:-1]])

        dailyH2O = np.mean(sngH2O,axis=0)

        #---------------------
        # Write out water file
        #---------------------
        with open(sngDir+'w-120.'+verW,'w') as fopen:
            #fopen.write('    1     Daily H2O profile from individual retrievals \n')
            fopen.write('    1     H2O Daily profile from individual retrievals \n')

            for row in segmnt(dailyH2O,5):
                strformat = ','.join('{:>12.4E}' for i in row) + ', \n'
                fopen.write(strformat.format(*row))

        #--------------------
        # Create plots to pdf
        #--------------------
        if pltFlg:

            pdfsav = PdfPages(sngDir+'DailyH2Oprf_v5.pdf')

            fig1,ax1 = plt.subplots()
            ax1.plot(dailyH2O,Z,label='Daily Averaged Retrieved H2O')

            for i,sngFile in enumerate(zptFiles):
                ax1.plot(sngH2O[i,:],Z,label=os.path.basename(sngFile))

            ax1.grid(True,which='both')
            ax1.legend(prop={'size':9})
            ax1.set_ylabel('Altitude [km]')
            ax1.set_xlabel('VMR [ppv]')
            ax1.tick_params(axis='x',which='both',labelsize=8)
            ax1.set_ylim((Z[-1],60))
            ax1.set_title(oneDay)

            pdfsav.savefig(fig1,dpi=250)


            pdfsav.close()

        print 'Finished processing folder: {}'.format(sngDir)

if __name__ == "__main__":
    main()