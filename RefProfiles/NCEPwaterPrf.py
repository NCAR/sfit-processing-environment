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
import datetime as dt
import sfitClasses as sc
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline as intrpUniSpl
from scipy.interpolate import interp2d
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import scipy as sp
from scipy.io import netcdf
import netCDF4 as nc


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
    loc = 'tab'

    #------------------------------------
    # Version number to append water file
    #------------------------------------
    verW = 'v3'

    #-----------------------------------------
    # Interpolation flag for NCEP re-analysis:
    # False = Nearest point. True = linear
    #-----------------------------------------
    interpFlg = True

    #---------------------
    # Interpolation things
    #---------------------
    nSkip      = 3            # Number of points to skip when merging WACCM and NCEP profiles
    intrpOrder = 1            # Order of interpolation
    logFlg     = True         # Flag to do interpolation of log of water

    #-----------------------
    # Date Range of interest
    #-----------------------
    iyear          = 2018
    imnth          = 1
    iday           = 1
    fyear          = 2018
    fmnth          = 12
    fday           = 31

    #-------------------------------
    # NCEP Reanalysis data directory
    #-------------------------------
    NCEPdirShum = '/data1/ancillary_data/NCEPdata/NCEP_Shum/'
    NCEPdirHgt  = '/data1/ancillary_data/NCEPdata/NCEP_hgt/'

    #---------------
    # Data Directory
    #---------------
    dataDir  = '/data1/'+loc.lower()+'/'
    #dataDir  = '/data1/iortega/WYO/'


    #-------------------------
    # WACCM monthly means file
    #-------------------------
    WACCMfile = '/data/Campaign/'+loc.upper()+'/waccm/WACCM_pTW-meanV6.'+loc.upper()

    #---------------------
    # Establish date range
    #---------------------
    dRange = sc.DateRange(iyear,imnth,iday,fyear,fmnth,fday)

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
        sLat = 76.52
        sLon = 291.23               # 68.77 W = (360.0 - 68.77) = 291.23 E

    elif loc.lower() == 'mlo':
        Z = np.array([ 120.0000,    110.0000,    100.0000,     95.0000,     90.0000,
                        85.0000,     80.0000,     75.0000,     70.0000,     65.0000,
                        60.0000,     55.0000,     50.0000,     48.0000,     46.0000,
                        44.0000,     42.0000,     40.0000,     38.0000,     36.0000,
                        34.0000,     32.0000,     30.0000,     28.0000,     26.0000,
                        24.0000,     22.0000,     20.0000,     18.0000,     16.0000,
                        14.0000,     12.0000,     10.0000,      9.0000,      8.0000,
                         7.0000,      6.0000,      5.0000,      4.0000,      3.3960])

        sLat = 19.4
        sLon = 204.43                # 155.57 W = (360 - 155.57) = 204.43 E

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

        sLat = 40.4
        sLon = 254.76                # 105.24 W = (360 - 105.24) = 254.76 E

        ###sLat = 42.73
        ###sLon = 253.68               #WYOBA


    #----------------------------
    # File and directory checking
    #----------------------------
    ckDir(NCEPdirShum,exitFlg=True)
    ckDir(NCEPdirHgt,exitFlg=True)
    ckDir(dataDir,exitFlg=True)
    ckFile(WACCMfile,exitFlg=True)

    #--------------------------------------------------------------------
    # Read WACCM monthly mean data. WACCM monthly mean file is ascending,
    # adjust so that it is descending. Also units are in km.
    #--------------------------------------------------------------------
    with open(WACCMfile, 'r') as fopen:
        lines = fopen.readlines()

    nlyrs = int(lines[0].strip().split()[0])
    s_ind  = 3
    Z      = np.flipud( np.array( [ float(row.strip().split()[0]) for row in lines[s_ind:nlyrs+s_ind] ] ) )
    waccmT = np.flipud( np.array( [ [float(x) for x in line.strip().split()[1:]] for line in lines[s_ind:nlyrs+s_ind] ] ) )
    s_ind  = 3 + nlyrs + 2
    waccmP = np.flipud( np.array( [ [float(x) for x in line.strip().split()[1:]] for line in lines[s_ind:nlyrs+s_ind] ] ) )
    s_ind  = 3 + nlyrs + 2 + nlyrs + 2
    waccmW = np.flipud( np.array( [ [float(x) for x in line.strip().split()[1:]] for line in lines[s_ind:nlyrs+s_ind] ] ) )

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

    #--------------------------------------------------------
    # Loop through folders for individual years. This is done
    # because NCEP NetCDF files are by year. Therefore only
    # have to open and read yearly NCEP file once
    #--------------------------------------------------------
    yrList = dRange.yearList()

    for year in yrList:

        #-----------------------------
        # Find all folders within year
        #-----------------------------
        dirListYr = np.array([d for d in dirLst if int(os.path.basename(d[:-1])[0:4]) == year])

        #-------------------------------
        # Open and read year NetCDF file
        #-------------------------------
        shumFile  = NCEPdirShum + 'shum.'+str(year)+'.nc'
        ghghtFile = NCEPdirHgt  + 'hgt.' +str(year)+'.nc'

        #-----------------------
        # Specific humidity file
        #-----------------------
        #with netcdf.netcdf_file(shumFile,'r',mmap=False) as shumF:      # Can only be done with scipy Ver > 0.12.0
        #shumF = netcdf.netcdf_file(shumFile,'r',mmap=False)
        shumObj  = nc.Dataset(shumFile,'r')
        PlvlShum = shumObj.variables['level']               # Starts at the surface
        timeShum = shumObj.variables['time']                # hours since 1-1-1 00:00:0.0
        latShum  = shumObj.variables['lat']                 # degrees_north
        lonShum  = shumObj.variables['lon']                 # degrees_east
        shum     = shumObj.variables['shum']                # Units: [kg/kg]. Dimensions: [time][vert][lat][lon] Only goes to 300mb!!

        PlvlShum = PlvlShum[:]
        timeShum = timeShum[:]
        latShum  = latShum[:]
        lonShum  = lonShum[:]
        shum     = shum[:]

        shumObj.close()

        #----------------------------------------
        # Convert Specific humidity from kg/kg to
        # molecules/molecules
        #----------------------------------------
        shum = shum * 1.608

        #-----------------------------------------------
        # If not interpolating point in NCEP re-analysis
        # find closes lat lon indicies
        #-----------------------------------------------
        if not interpFlg:
            latind = findCls(latShum,sLat)
            lonind = findCls(lonShum,sLon)

        #------------------------------------------------------
        # Convert hours since 1-1-1 00:00:00 to datetime object
        # NCEP reanalysis uses udunits for encoding times,
        # meaning they don't follow standard leap year
        # convention (whatever this means?). Must follow some
        # leap year convention, but not clear. Therefore, take
        # the first time in file as 1-1-YEAR.
        #------------------------------------------------------
        timeHrs = timeShum - timeShum[0]
        timeAll = np.array([dt.datetime(year,1,1)+dt.timedelta(hours=int(h)) for h in timeHrs])

        #-------------------------
        # Geopotential Height file
        #-------------------------
        #with netcdf.netcdf_file(ghghtFile,'r',mmap=False) as gHghtF:      # Can only be done with scipy Ver > 0.12.0
        #gHghtF = netcdf.netcdf_file(ghghtFile,'r',mmap=False)
        gHghtF   = nc.Dataset(ghghtFile,'r')
        hgt      = gHghtF.variables['hgt']                # Height in [meters]. Dimensions: [time][vert][lat][lon]
        PlvlHght = gHghtF.variables['level']

        hgt      = hgt[:]
        PlvlHght = PlvlHght[:]

        gHghtF.close()
        #------------------------------------------
        # Loop through all folders in specific year
        #------------------------------------------
        for sngDir in dirListYr:

            #----------------------------
            # Get date in datetime format
            #----------------------------
            oneDay = dt.datetime(int(os.path.basename(sngDir[:-1])[0:4]),int(os.path.basename(sngDir[:-1])[4:6]),int(os.path.basename(sngDir[:-1])[6:8]))

            #--------------------------------------------------
            # Find month index for monthly WACCM water profiles
            #--------------------------------------------------
            mnthInd = oneDay.month - 1     # -1 because January is in the 0th column

            #--------------------------------------
            # Get hgt and specific humidity for day
            #--------------------------------------
            ind        = np.where(timeAll == oneDay)[0]
            dayHghtMat = np.squeeze(hgt[ind,:,:,:])
            dayShumMat = np.squeeze(shum[ind,:,:,:])

            #-----------------------------------------------------------
            # 'Unpack' the data => (data[int])*scale_factor + add_offset
            #-----------------------------------------------------------
            #dayHghtMat = dayHghtMat * hgt.scale_factor + hgt.add_offset
            #dayShumMat = dayShumMat * shum.scale_factor + shum.add_offset

            #-----------------------------------------------------
            # For each level interpolate hgt and specific humidity
            # based on latitude and longitude of site
            #-----------------------------------------------------
            dayHgt  = np.zeros(np.shape(dayShumMat)[0])
            dayShum = np.zeros(np.shape(dayShumMat)[0])
            for lvl in range(0,np.shape(dayShumMat)[0]):

                dayHgtLvl    = np.squeeze(dayHghtMat[lvl,:,:])
                if interpFlg: dayHgt[lvl] = interp2d(lonShum,latShum,dayHgtLvl,kind='linear',bounds_error=True)(sLon,sLat)
                else:         dayHgt[lvl] = dayHgtLvl[latind,lonind]

                dayShumLvl   = np.squeeze(dayShumMat[lvl,:,:])
                if interpFlg: dayShum[lvl] = interp2d(lonShum,latShum,dayShumLvl,kind='linear',bounds_error=True)(sLon,sLat)
                else:         dayShum[lvl] = dayShumLvl[latind,lonind]

            dayHgt.astype(float)
            dayShum.astype(float)
            dayHgt  = dayHgt / 1000.0            # Convert height units [m] => [km]

            #---------------------------------------------------------
            # Construct specific humidity and height profiles for
            # interpolation on to the sfit input grid which is the
            # same as the WACCM height in monthly profile file.
            # NCEP reanalysis data only goes to 300mb therefore,
            # merge with monthly averaged WACCM water profiles > 300mb
            #---------------------------------------------------------
            NCEPtop = dayHgt[-1]
            topInd  = np.argmin( abs(Z - NCEPtop) )   # Where top of NCEP reanalysis fits in WACCM grid height

            #Zin  = np.concatenate( ( Z[0:(topInd-nSkip)]             , np.flipud(dayHgt)) , axis=1 )
            #SHin = np.concatenate( ( waccmW[0:(topInd-nSkip),mnthInd], np.flipud(dayShum)), axis=1 )
            
            #Remove axis=1
            Zin  = np.concatenate( ( Z[0:(topInd-nSkip)]             , np.flipud(dayHgt)))
            SHin = np.concatenate( ( waccmW[0:(topInd-nSkip),mnthInd], np.flipud(dayShum)))

            #--------------------------------------------------------------
            # Interpolate to specific humidity on WACCM grid. X data must
            # be increasing => flip dimensions and then flip back
            #--------------------------------------------------------------
            if logFlg:
                SHout  = np.exp(np.flipud( intrpUniSpl( np.flipud(Zin), np.log(np.flipud(SHin)), k=intrpOrder )( np.flipud(Z) ) ) )
            else:
                SHout  = np.flipud( intrpUniSpl( np.flipud(Zin), np.flipud(SHin), k=intrpOrder )( np.flipud(Z) ) )

            #---------------------
            # Write out water file
            #---------------------
            with open(sngDir+'w-120.'+verW,'w') as fopen:
                fopen.write('    1     H2O from NCEP reanalysis and WACCM V6 monthly mean \n')

                for row in segmnt(SHout,5):
                    strformat = ','.join('{:>12.4E}' for i in row) + ', \n'
                    fopen.write(strformat.format(*row))

            #--------------------
            # Create plots to pdf
            #COMMENTED BELOW BY IVAN: CHECK MATPLOT PLT ERROR
            #--------------------
            pdfsav = PdfPages(sngDir+'WaterProfile.pdf')

            fig1,ax1 = plt.subplots()
            ax1.plot(SHout,Z,'rx-', label='Interpolated SH')
            ax1.plot(waccmW[:,mnthInd],Z,'bx-',label='WACCM V6 SH')
            ax1.plot(dayShum,dayHgt,'kx-',label='NCEP Reanalysis SH')
            ax1.grid(True,which='both')
            ax1.legend(prop={'size':9})
            ax1.set_ylabel('Altitude [km]')
            ax1.set_xlabel('VMR [ppv]')
            ax1.tick_params(axis='x',which='both',labelsize=8)
            ax1.set_ylim((Z[-1],60))
            ax1.set_xlim((0,np.max((waccmW[-1,mnthInd],dayShum[-1]))))
            ax1.set_title(oneDay)

            pdfsav.savefig(fig1,dpi=250)

            fig2,ax2 = plt.subplots()
            ax2.plot(SHout,Z,'rx-', label='Interpolated SH')
            ax2.plot(waccmW[:,mnthInd],Z,'bx-',label='WACCM V6 SH')
            ax2.plot(dayShum,dayHgt,'kx-',label='NCEP Reanalysis SH')
            ax2.grid(True,which='both')
            ax2.legend(prop={'size':9})
            ax2.set_ylabel('Altitude [km]')
            ax2.set_xlabel('log VMR [ppv]')
            ax2.tick_params(axis='x',which='both',labelsize=8)
            ax2.set_xscale('log')
            ax2.set_ylim((Z[-1],60))
            ax2.set_xlim((0,np.max((waccmW[-1,mnthInd],dayShum[-1]))))
            ax2.set_title(oneDay)

            pdfsav.savefig(fig2,dpi=250)

            pdfsav.close()

            print 'Finished processing folder: {}'.format(sngDir)
            #########


if __name__ == "__main__":
    main()