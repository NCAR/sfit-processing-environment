#! /usr/local/python-2.7/bin/python

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
from scipy.interpolate import interp2d, interp1d
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import scipy as sp
#from scipy.io import netcdf
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
    try:
        xrange
    except NameError:
        xrange = range
        
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
    
    #-----------------------------------------
    # Interpolation flag for NCEP re-analysis: 
    # False = Nearest point. True = linear
    #-----------------------------------------
    interpFlg = False
    
    #---------------------
    # Interpolation things
    #---------------------
    nSkip      = 3            # Number of points to skip when merging WACCM and NCEP profiles
    intrpOrder = 1            # Order of interpolation
    logFlg     = True         # Flag to do interpolation of log of water
    
    #-----------------------
    # Date Range of interest
    #-----------------------
    year           = 2014
    
    iyear          = year
    imnth          = 1
    iday           = 1
    fyear          = year
    fmnth          = 10
    fday           = 1
    
    #-------------------------------------
    # Parameters for potential temperature
    #-------------------------------------
    thetaTrgt = 380.0    # Potential Temperature [K]
    P0        = 1000.0   # Referenc Pressure [mbars]
    R_Cp      = 0.286    # R/Cp for air
    
    #-------------------------------
    # NCEP Reanalysis data directory
    #-------------------------------
    NCEPTempdir = '/Volumes/data1/ebaumer/NCEP_Temp/'
    NCEPhgtDir  = '/Volumes/data1/ebaumer/NCEP_hgt/'

    #--------------
    # Out directory
    #--------------
    outDir = '/Volumes/data1/ebaumer/NCEP_Temp/'
    #---------------------
    # Establish date range
    #---------------------
    dRange = sc.DateRange(iyear,imnth,iday,fyear,fmnth,fday) 
    yrList = dRange.yearList()

    #---------------------------------------
    # Altitude levels for different stations
    #---------------------------------------
    if loc.lower() == 'tab':
        sLat = 76.52
        sLon = 291.23               # 68.77 W = (360.0 - 68.77) = 291.23 E
        
    elif loc.lower() == 'mlo':
        sLat = 19.4
        sLon = 204.43                # 155.57 W = (360 - 155.57) = 204.43 E
        
    elif loc.lower() == 'fl0':
        sLat = 40.4
        sLon = 254.76                # 105.24 W = (360 - 105.24) = 254.76 E    
      
    #----------------------------
    # File and directory checking
    #----------------------------
    ckDir(NCEPTempdir,exitFlg=True)
    ckDir(NCEPhgtDir,exitFlg=True)
       
    #-------------------
    # Loop through years
    #-------------------
    for year in yrList:
        
        #-------------------
        # Yearly Output File
        #-------------------
        outFile  = outDir + '380K_theta_'+loc.lower()+'_'+str(iyear)+'.dat'        

        #-------------------------------
        # Open and read year NetCDF file
        #-------------------------------
        trppFile  = NCEPTempdir + 'air.' +str(year)+'.nc'
        ghghtFile = NCEPhgtDir +  'hgt.' +str(year)+'.nc'

        #-------------------------
        # Tropopause Pressure File
        #-------------------------
        #with netcdf.netcdf_file(shumFile,'r',mmap=False) as shumF:      # Can only be done with scipy Ver > 0.12.0
        TempObj  = nc.Dataset(trppFile,'r')
        Temp     = TempObj.variables['air'][:]                 # Mean daily Pressure at Tropopause (Pascals)
        timeTrpp = TempObj.variables['time'][:]                # hours since 1-1-1 00:00:0.0
        latTrpp  = TempObj.variables['lat'][:]                 # degrees_north
        lonTrpp  = TempObj.variables['lon'][:]                 # degrees_east
        TempObj.close()
        
        #-----------------------------------------------------------
        # 'Unpack' the data => (data[int])*scale_factor + add_offset
        #-----------------------------------------------------------
        #TempData = Temp[:,:,:] * Temp.scale_factor + Temp.add_offset    
        
        #-----------------------------------------------
        # If not interpolating point in NCEP re-analysis
        # find closes lat lon indicies
        #-----------------------------------------------
        if not interpFlg:
            latind = findCls(latTrpp,sLat)
            lonind = findCls(lonTrpp,sLon)
        
        #------------------------------------------------------
        # Convert hours since 1-1-1 00:00:00 to datetime object
        # NCEP reanalysis uses udunits for encoding times,
        # meaning they don't follow standard leap year
        # convention (whatever this means?). Must follow some 
        # leap year convention, but not clear. Therefore, take
        # the first time in file as 1-1-YEAR.
        #------------------------------------------------------        
        timeHrs = timeTrpp - timeTrpp[0]                      
        timeAll = np.array([dt.datetime(year,1,1)+dt.timedelta(hours=int(h)) for h in timeHrs])    # This is a datetime object
        dateAll = np.array([dt.date(d.year,d.month,d.day) for d in timeAll])                       # Convert datetime to strictly date
        
        #-------------------------
        # Geopotential Height file
        #-------------------------
        #with netcdf.netcdf_file(ghghtFile,'r',mmap=False) as gHghtF:      # Can only be done with scipy Ver > 0.12.0
        gHghtF       = nc.Dataset(ghghtFile,'r')
        hgt          = gHghtF.variables['hgt'][:]                                # Height in [meters]. Dimensions: [time][vert][lat][lon]
        PlvlHghtData = gHghtF.variables['level'][:]
        gHghtF.close()
        PlvlHghtData.astype(float)
        
        #-------------------------------------------------
        # Calculate coefficient for potential temperature:
        #               Po   (R/Cp)
        #  Theta = T *(-----)
        #                P
        #-------------------------------------------------
        theta_coef = (P0 / PlvlHghtData)**(R_Cp)   #???????????????
        
        #-------------------------------------
        # Create empty Tropopause height array
        #-------------------------------------
        theta_hgt = np.zeros(len(dateAll))

        #------------------------------------------
        # Loop through all folders in specific year
        #------------------------------------------
        for day in dRange.dateList:
            
            #------------------------------
            # Find corresponding date index
            #------------------------------
            i = np.where(dateAll == day)[0]
            
            #-------------------------
            # Get hgt for specific day
            #-------------------------
            dayHghtMat = np.squeeze(hgt[i,:,:,:])
            
            #-----------------------------
            # Get Theta for a specific day
            #-----------------------------
            dayTempMat = np.squeeze(Temp[i,:,:,:])
                        
            #-------------------------------------------
            # For each level interpolate height and Theta
            # based on latitude and longitude of site
            #-------------------------------------------
            dayHgt   = np.zeros(np.shape(dayHghtMat)[0])
            thetaLvl = np.zeros(np.shape(dayHghtMat)[0])
            
            for lvl in range(0,np.shape(dayHghtMat)[0]): 
                #-------
                # Height
                #-------
                dayHgtLvl = np.squeeze(dayHghtMat[lvl,:,:])
                if interpFlg: dayHgt[lvl] = interp2d(lonTrpp[:],latTrpp[:],dayHgtLvl,kind='linear',bounds_error=True)(sLon,sLat)
                else:         dayHgt[lvl] = dayHgtLvl[latind,lonind]  
  
                #------
                # Theta
                #------
                TempDayLvl = np.squeeze(dayTempMat[lvl,:,:])
                if interpFlg: thetaLvl[lvl] = interp2d(lonTrpp[:],latTrpp[:],TempDayLvl,kind='linear',bounds_error=True)(sLon,sLat)
                else:         thetaLvl[lvl] = TempDayLvl[latind,lonind]  
  
            dayHgt.astype(float)
            dayHgt = dayHgt / 1000.0            # Convert height units [m] => [km]
            thetaLvl.astype(float)
            thetaLvl *= theta_coef              # Apply theta coefficient Temperature => Theta
              
            #------------------------------------
            # Interpolate Tropopause pressure on 
            # height to find height of tropopuase
            #------------------------------------
            theta_hgt[i] = interp1d(thetaLvl,dayHgt,kind='linear')(thetaTrgt)

        #----------------------------------------
        # Write Tropopause heights to yearly file
        #----------------------------------------
        with open(outFile,'w') as fopen:
            hdr = 'Date           380K Potential Temperature Height [km]\n'
            fopen.write(hdr)
            strformat = '{0:15}{1:<38}\n'
            for i,indDay in enumerate(timeAll):
                daystr = "{0:04d}{1:02d}{2:02d}".format(indDay.year,indDay.month,indDay.day)
                temp   = [daystr,theta_hgt[i]]
                fopen.write(strformat.format(*temp))
                
                                                                                    
if __name__ == "__main__":
    main()