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
import os, sys
sys.path.append((os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "ModLib")))
import datetime as dt
import sfitClasses as sc
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline as intrpUniSpl
from scipy.interpolate import interp2d, interp1d
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
    loc = 'nya'
    
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
    yyyy           = 2015
    iyear          = yyyy
    imnth          = 1
    iday           = 1
    fyear          = yyyy
    fmnth          = 12
    fday           = 31
    
    #-------------------------------
    # NCEP Reanalysis data directory
    #-------------------------------
    #NCEPTrppdir = '/Volumes/data1/ebaumer/NCEP_trpp/'
    #NCEPhgtDir  = '/Volumes/data1/ebaumer/NCEP_hgt/'
    NCEPTrppdir = '/data1/ancillary_data/NCEPdata/NCEP_trpp/'
    NCEPhgtDir  = '/data1/ancillary_data/NCEPdata/NCEP_hgt/'

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

    elif loc.lower() == 'nya':
        sLat = 78.92
        sLon = 11.93                # 11.93 E     
      
    #----------------------------
    # File and directory checking
    #----------------------------
    ckDir(NCEPTrppdir,exitFlg=True)
    ckDir(NCEPhgtDir,exitFlg=True)
       
    #-------------------
    # Loop through years
    #-------------------
    for year in yrList:
        
        #-------------------
        # Yearly Output File
        #-------------------
        outFile  = '/data1/ancillary_data/NCEPdata/NCEP_trpp/TropHght_'+loc.lower()+'_'+str(iyear)+'.dat'        

        #-------------------------------
        # Open and read year NetCDF file
        #-------------------------------
        trppFile  = NCEPTrppdir + 'pres.tropp.'+str(year)+'.nc'
        ghghtFile = NCEPhgtDir + 'hgt.' +str(year)+'.nc'

        #-------------------------
        # Tropopause Pressure File
        #-------------------------
        #TrppObj  = netcdf.netcdf_file(trppFile,'r',mmap=False)
        TrppObj  = nc.Dataset(trppFile,'r')
        Trpp     = TrppObj.variables['pres']                # Mean daily Pressure at Tropopause (Pascals)
        timeTrpp = TrppObj.variables['time']                # hours since 1-1-1 00:00:0.0
        latTrpp  = TrppObj.variables['lat']                 # degrees_north
        lonTrpp  = TrppObj.variables['lon']                 # degrees_east

        #-----------------------------------------------------------
        # 'Unpack' the data => (data[int])*scale_factor + add_offset
        #-----------------------------------------------------------
        #TrppData = Trpp[:,:,:] * Trpp.scale_factor + Trpp.add_offset    
        TrppData = Trpp[:]     # New files seem to automatically apply scale factor and offset
                        
        TrppData *= 0.01              # Convert [Pascals] => [mbars]
        
        #-----------------------------------------------
        # If not interpolating point in NCEP re-analysis
        # find closes lat lon indicies
        #-----------------------------------------------
        if not interpFlg:
            latind = findCls(latTrpp[:],sLat)
            lonind = findCls(lonTrpp[:],sLon)
        
        #------------------------------------------------------
        # Convert hours since 1-1-1 00:00:00 to datetime object
        # NCEP reanalysis uses udunits for encoding times,
        # meaning they don't follow standard leap year
        # convention (whatever this means?). Must follow some 
        # leap year convention, but not clear. Therefore, take
        # the first time in file as 1-1-YEAR.
        #------------------------------------------------------        
        timeHrs = timeTrpp[:] - timeTrpp[0]                      
        timeAll = np.array([dt.datetime(year,1,1)+dt.timedelta(hours=int(h)) for h in timeHrs])    # This is a datetime object
        dateAll = np.array([dt.date(d.year,d.month,d.day) for d in timeAll])                       # Convert datetime to strictly date
        
        #-------------------------
        # Geopotential Height file
        #-------------------------
        ##with netcdf.netcdf_file(ghghtFile,'r',mmap=False) as gHghtF:      # Can only be done with scipy Ver > 0.12.0
        ##gHghtF   = netcdf.netcdf_file(ghghtFile,'r',mmap=False)
        gHghtF       = nc.Dataset(ghghtFile,'r')
        hgt          = gHghtF.variables['hgt'][:]                                # Height in [meters]. Dimensions: [time][vert][lat][lon]
        PlvlHghtData = gHghtF.variables['level'][:]
        gHghtF.close()
        PlvlHghtData.astype(float)
        
        #-------------------------------------
        # Create empty Tropopause height array
        #-------------------------------------
        Trph     = np.zeros(len(dateAll))     
        TrppSite = np.zeros(len(dateAll))

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
            
            #-----------------------------------------------------------
            # 'Unpack' the data => (data[int])*scale_factor + add_offset
            #-----------------------------------------------------------
            #dayHghtMat = dayHghtMat * hgt.scale_factor + hgt.add_offset
            
            #-------------------------------------------
            # For each level interpolate height based on 
            # latitude and longitude of site
            #-------------------------------------------
            dayHgt  = np.zeros(np.shape(dayHghtMat)[0])
            
            for lvl in range(0,np.shape(dayHghtMat)[0]):      
                dayHgtLvl    = np.squeeze(dayHghtMat[lvl,:,:])
                if interpFlg: dayHgt[lvl] = interp2d(lonTrpp[:],latTrpp[:],dayHgtLvl,kind='linear', bounds_error=True)(sLon,sLat)
                else:         dayHgt[lvl] = dayHgtLvl[latind,lonind]  

               
            dayHgt.astype(float)
            dayHgt  = dayHgt / 1000.0            # Convert height units [m] => [km]
            
            #-------------------------------------------------------------
            # Interpolate Tropopause pressure based on lat and lon of site
            #-------------------------------------------------------------
            TrppDay = np.squeeze(TrppData[i,:,:])
            
            if interpFlg: TrppSite[i] = interp2d(lonTrpp[:],latTrpp[:],TrppDay,kind='linear', bounds_error=True)(sLon,sLat)
            else: TrppSite[i] = TrppDay[latind,lonind] 

            #------------------------------------
            # Interpolate Tropopause pressure on 
            # height to find height of tropopuase
            #------------------------------------     
            #Trph[i] = interp1d(PlvlHghtData,dayHgt, kind='linear')(TrppSite[i])

            ###Combine lists into list of tuples          
            points = zip(PlvlHghtData, dayHgt)
            ### Sort list of tuples by x-value
            points = sorted(points, key=lambda point: point[0])
            ###Split list of tuples into two list of x values any y values
            PlvlHghtData_sort, dayHgt_sort = zip(*points)

            PlvlHghtData_sort = np.asarray(PlvlHghtData_sort)
            dayHgt_sort = np.asarray(dayHgt_sort)

            Trph[i] = interp1d(PlvlHghtData_sort,dayHgt_sort, kind='linear')(TrppSite[i])

        #----------------------------------------
        # Write Tropopause heights to yearly file
        #----------------------------------------
        with open(outFile,'w') as fopen:
            hdr = 'Date                     Tropopause Height [km]   Tropopause Pressure [mbars]\n'
            fopen.write(hdr)
            strformat = ['{'+str(i)+':<25}' for i in range(0,3)]
            strformat = ''.join(strformat).lstrip() + '\n'
            for i,indDay in enumerate(timeAll):
                daystr = "{0:04d}{1:02d}{2:02d}".format(indDay.year,indDay.month,indDay.day)
                temp   = [daystr,Trph[i],TrppSite[i]]
                fopen.write(strformat.format(*temp))
                    
        TrppObj.close()
                                                                                    
if __name__ == "__main__":
    main()
