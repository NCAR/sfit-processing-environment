#! /usr/local/python-2.7/bin/python

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

                        #-------------------------------------#
                        # Define helper functions and classes #
                        #-------------------------------------#
        
def ckDir(dirName,exitFlg=False):
    ''' '''
    if not os.path.exists( dirName ):
        print ('Input Directory %s does not exist' % (dirName))
        if exitFlg: sys.exit()
        return False
    else:
        return True   

def ckFile(fName,exitFlg=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print ('File %s does not exist' % (fName))
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
    fmnth          = 12
    fday           = 31
    
    #-------------------------------------
    # Parameters for potential temperature
    #-------------------------------------
    thetaTrgt = 380.0    # Potential Temperature [K]
    P0        = 1000.0   # Referenc Pressure [mbars]
    R_Cp      = 0.286    # R/Cp for air
    
    #---------------------------
    # ERA Interim data directory
    #---------------------------
    ERAdir = '/Volumes/data1/ebaumer/ERAdata/'

    #--------------
    # Out directory
    #--------------
    outDir = '/Volumes/data1/ebaumer/ERAdata/'    

    #---------------------
    # Establish date range
    #---------------------
    dRange = sc.DateRange(iyear,imnth,iday,fyear,fmnth,fday) 
    dayLst = dRange.dateList
    
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
    ckDir(ERAdir,exitFlg=True)
    ckDir(outDir,exitFlg=True)
    
    #-------------------
    # Yearly Output File
    #-------------------
    outFile  = outDir + 'ERA_380K_theta_'+loc.lower()+'_'+str(year)+'.dat'       
        
    #-------------------------------------
    # Create empty Tropopause height array
    #-------------------------------------
    theta_hgt = np.zeros(len(dayLst))    
      
    #------------------
    # Loop through days
    #------------------
    for sngDay in dayLst:
        
        #-------------------------------------------
        # Open daily ERA interm files 00, 06, 12, 18
        #-------------------------------------------
        YYYY = "{0:04d}".format(sngDay.year)
        MM   = "{0:02d}".format(sngDay.month)
        DD   = "{0:02d}".format(sngDay.day)   
        ERA_F1 = ERAdir + YYYY + MM + '/' + 'ei.oper.an.pl.regn128sc.'+YYYY+MM+DD+'00.nc'
        ERA_F2 = ERAdir + YYYY + MM + '/' + 'ei.oper.an.pl.regn128sc.'+YYYY+MM+DD+'06.nc'
        ERA_F3 = ERAdir + YYYY + MM + '/' + 'ei.oper.an.pl.regn128sc.'+YYYY+MM+DD+'12.nc'
        ERA_F4 = ERAdir + YYYY + MM + '/' + 'ei.oper.an.pl.regn128sc.'+YYYY+MM+DD+'18.nc'

        f1 = netcdf.netcdf_file(ERA_F1,'r',mmap=False)
        f2 = netcdf.netcdf_file(ERA_F2,'r',mmap=False)
        f3 = netcdf.netcdf_file(ERA_F3,'r',mmap=False)
        f4 = netcdf.netcdf_file(ERA_F4,'r',mmap=False)
        
        #-----------------------------------
        # Lat and lon should be the same for 
        # all files. Just grab once
        #-----------------------------------
        lat   = f1.variables['g4_lat_1']
        lon   = f1.variables['g4_lon_2']
        Plvl  = f1.variables['lv_ISBL0']
        nlvls = np.shape(Plvl[:])[0]
        
        Z_00  = f1.variables['Z_GDS4_ISBL']
        Z_06  = f2.variables['Z_GDS4_ISBL']
        Z_12  = f3.variables['Z_GDS4_ISBL']
        Z_18  = f4.variables['Z_GDS4_ISBL']
        
        T_00  = f1.variables['T_GDS4_ISBL']
        T_06  = f1.variables['T_GDS4_ISBL']
        T_12  = f1.variables['T_GDS4_ISBL']
        T_18  = f1.variables['T_GDS4_ISBL']
        
        f1.close()
        f2.close()
        f3.close()
        f4.close()
        
        #-----------------------------------------------
        # If not interpolating point in NCEP re-analysis
        # find closes lat lon indicies
        #-----------------------------------------------
        if not interpFlg:
            latind = findCls(lat[:],sLat)
            lonind = findCls(lon[:],sLon)        
        
        #-----------------------------------------------------
        # For each level interpolate hgt and specific humidity 
        # based on latitude and longitude of site
        #-----------------------------------------------------
        Hgt_00  = np.zeros(nlvls)
        Hgt_06  = np.zeros(nlvls)
        Hgt_12  = np.zeros(nlvls)
        Hgt_18  = np.zeros(nlvls)
        
        Tint_00 = np.zeros(nlvls)
        Tint_06 = np.zeros(nlvls)
        Tint_12 = np.zeros(nlvls)
        Tint_18 = np.zeros(nlvls)     
        
        for lvl in range(0,nlvls):
            HgtOneLvl_00  = np.squeeze(Z_00[lvl,:,:])
            HgtOneLvl_06  = np.squeeze(Z_06[lvl,:,:])
            HgtOneLvl_12  = np.squeeze(Z_12[lvl,:,:])
            HgtOneLvl_18  = np.squeeze(Z_18[lvl,:,:])
            
            T_OneLvl_00  = np.squeeze(T_00[lvl,:,:])
            T_OneLvl_06  = np.squeeze(T_06[lvl,:,:])
            T_OneLvl_12  = np.squeeze(T_12[lvl,:,:])
            T_OneLvl_18  = np.squeeze(T_18[lvl,:,:])         
            
            if interpFlg: 
                Hgt_00[lvl] = interp2d(lon[:],lat[:],HgtOneLvl_00,kind='linear',bounds_error=True)(sLon,sLat)
                Hgt_06[lvl] = interp2d(lon[:],lat[:],HgtOneLvl_06,kind='linear',bounds_error=True)(sLon,sLat)
                Hgt_12[lvl] = interp2d(lon[:],lat[:],HgtOneLvl_12,kind='linear',bounds_error=True)(sLon,sLat)
                Hgt_18[lvl] = interp2d(lon[:],lat[:],HgtOneLvl_18,kind='linear',bounds_error=True)(sLon,sLat)
                
                Tint_00[lvl] = interp2d(lon[:],lat[:],T_OneLvl_00,kind='linear',bounds_error=True)(sLon,sLat) 
                Tint_06[lvl] = interp2d(lon[:],lat[:],T_OneLvl_06,kind='linear',bounds_error=True)(sLon,sLat) 
                Tint_12[lvl] = interp2d(lon[:],lat[:],T_OneLvl_12,kind='linear',bounds_error=True)(sLon,sLat) 
                Tint_18[lvl] = interp2d(lon[:],lat[:],T_OneLvl_18,kind='linear',bounds_error=True)(sLon,sLat)              

            else:         
                Hgt_00[lvl] = HgtOneLvl_00[latind,lonind]  
                Hgt_06[lvl] = HgtOneLvl_06[latind,lonind] 
                Hgt_12[lvl] = HgtOneLvl_12[latind,lonind] 
                Hgt_18[lvl] = HgtOneLvl_18[latind,lonind]       
                
                Tint_00[lvl] = T_OneLvl_00[latind,lonind]
                Tint_06[lvl] = T_OneLvl_06[latind,lonind]
                Tint_12[lvl] = T_OneLvl_12[latind,lonind]
                Tint_18[lvl] = T_OneLvl_18[latind,lonind]                 
                           
        #-------------------------------------
        # Create daily averages of 00,06,12,18
        #-------------------------------------
        Z_day  = np.mean(np.vstack((Hgt_00,Hgt_06,Hgt_12,Hgt_18)),axis=0)
        T_day  = np.mean(np.vstack((Tint_00,Tint_06,Tint_12,Tint_18)),axis=0)
        
        #--------------------------------
        # Convert Height [m^2 s^-2] => km
        #--------------------------------
        Z_day = Z_day / 9.81 / 1000.0

        #---------------------------------------------------------
        # Calculate potential temperature for each pressure level:
        #               Po   (R/Cp)
        #  Theta = T *(-----)
        #                P
        #---------------------------------------------------------
        thetaLvl = T_day * (P0 / Plvl[:])**(R_Cp)  

        #------------------------------------
        # Interpolate Tropopause pressure on 
        # height to find height of tropopuase
        #------------------------------------
        theta_hgt[i] = interp1d(thetaLvl,Z_day,kind='linear')(thetaTrgt)

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
