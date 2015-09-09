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
    loc = 'mlo'
    
    #------------------------------------
    # Version number to append water file
    #------------------------------------
    verW = 'v4'
    
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
    logFlg     = False        # Flag to do interpolation of log of water
    
    #-----------------------
    # Date Range of interest
    #-----------------------
    iyear          = 2012
    imnth          = 1
    iday           = 1
    fyear          = 2012
    fmnth          = 12
    fday           = 31
    
    #------------------------------
    # ERA Reanalysis data directory
    #------------------------------
    ERAdir = '/data1/ancillary_data/ERAdata/'
    
    #---------------
    # Data Directory
    #---------------
    dataDir  = '/data1/'+loc.lower()+'/'
    
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
          
    #----------------------------
    # File and directory checking
    #----------------------------
    ckDir(ERAdir,exitFlg=True)
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
    
    
    #------------------------------------------
    # Loop through all folders in specific year
    #------------------------------------------
    for sngDir in dirLst:
        
        #----------------------------
        # Get date in datetime format
        #----------------------------
        oneDay = dt.datetime(int(os.path.basename(sngDir[:-1])[0:4]),int(os.path.basename(sngDir[:-1])[4:6]),int(os.path.basename(sngDir[:-1])[6:8]))

        #--------------------------------------------------
        # Find month index for monthly WACCM water profiles
        #--------------------------------------------------
        mnthInd = oneDay.month - 1     # -1 because January is in the 0th column

        #-------------------------------------------
        # Open daily ERA interm files 00, 06, 12, 18
        #-------------------------------------------
        YYYY = "{0:04d}".format(oneDay.year)
        MM   = "{0:02d}".format(oneDay.month)
        DD   = "{0:02d}".format(oneDay.day)   
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

        Q_00 = f1.variables['Q_GDS4_ISBL']
        Q_06 = f2.variables['Q_GDS4_ISBL']
        Q_12 = f3.variables['Q_GDS4_ISBL']
        Q_18 = f4.variables['Q_GDS4_ISBL']
        
        Z_00 = f1.variables['Z_GDS4_ISBL']
        Z_06 = f2.variables['Z_GDS4_ISBL']
        Z_12 = f3.variables['Z_GDS4_ISBL']
        Z_18 = f4.variables['Z_GDS4_ISBL']
        
        PV_00 = f1.variables['PV_GDS4_ISBL']
        PV_06 = f2.variables['PV_GDS4_ISBL']
        PV_12 = f3.variables['PV_GDS4_ISBL']
        PV_18 = f4.variables['PV_GDS4_ISBL']
        
        T_00  = f1.variables['T_GDS4_ISBL']
        T_06  = f2.variables['T_GDS4_ISBL']
        T_12  = f3.variables['T_GDS4_ISBL']
        T_18  = f4.variables['T_GDS4_ISBL']
        
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
        
        Qint_00 = np.zeros(nlvls)
        Qint_06 = np.zeros(nlvls)
        Qint_12 = np.zeros(nlvls)
        Qint_18 = np.zeros(nlvls)
        
        Tint_00 = np.zeros(nlvls)
        Tint_06 = np.zeros(nlvls)
        Tint_12 = np.zeros(nlvls)
        Tint_18 = np.zeros(nlvls)
        
        PVint_00 = np.zeros(nlvls)
        PVint_06 = np.zeros(nlvls)
        PVint_12 = np.zeros(nlvls)
        PVint_18 = np.zeros(nlvls)        
        
        for lvl in range(0,nlvls):
            HgtOneLvl_00  = np.squeeze(Z_00[lvl,:,:])
            HgtOneLvl_06  = np.squeeze(Z_06[lvl,:,:])
            HgtOneLvl_12  = np.squeeze(Z_12[lvl,:,:])
            HgtOneLvl_18  = np.squeeze(Z_18[lvl,:,:])
            
            Q_OneLvl_00  = np.squeeze(Q_00[lvl,:,:])
            Q_OneLvl_06  = np.squeeze(Q_06[lvl,:,:])
            Q_OneLvl_12  = np.squeeze(Q_12[lvl,:,:])
            Q_OneLvl_18  = np.squeeze(Q_18[lvl,:,:])    
            
            T_OneLvl_00  = np.squeeze(T_00[lvl,:,:])
            T_OneLvl_06  = np.squeeze(T_06[lvl,:,:])
            T_OneLvl_12  = np.squeeze(T_12[lvl,:,:])
            T_OneLvl_18  = np.squeeze(T_18[lvl,:,:])
            
            PV_OneLvl_00  = np.squeeze(PV_00[lvl,:,:])
            PV_OneLvl_06  = np.squeeze(PV_06[lvl,:,:])
            PV_OneLvl_12  = np.squeeze(PV_12[lvl,:,:])
            PV_OneLvl_18  = np.squeeze(PV_18[lvl,:,:])              
            
            if interpFlg: 
                Hgt_00[lvl] = interp2d(lon[:],lat[:],HgtOneLvl_00,kind='linear',bounds_error=True)(sLon,sLat)
                Hgt_06[lvl] = interp2d(lon[:],lat[:],HgtOneLvl_06,kind='linear',bounds_error=True)(sLon,sLat)
                Hgt_12[lvl] = interp2d(lon[:],lat[:],HgtOneLvl_12,kind='linear',bounds_error=True)(sLon,sLat)
                Hgt_18[lvl] = interp2d(lon[:],lat[:],HgtOneLvl_18,kind='linear',bounds_error=True)(sLon,sLat)
                
                Qint_00[lvl] = interp2d(lon[:],lat[:],Q_OneLvl_00,kind='linear',bounds_error=True)(sLon,sLat) 
                Qint_06[lvl] = interp2d(lon[:],lat[:],Q_OneLvl_06,kind='linear',bounds_error=True)(sLon,sLat) 
                Qint_12[lvl] = interp2d(lon[:],lat[:],Q_OneLvl_12,kind='linear',bounds_error=True)(sLon,sLat) 
                Qint_18[lvl] = interp2d(lon[:],lat[:],Q_OneLvl_18,kind='linear',bounds_error=True)(sLon,sLat)  
                
                Tint_00[lvl] = interp2d(lon[:],lat[:],T_OneLvl_00,kind='linear',bounds_error=True)(sLon,sLat) 
                Tint_06[lvl] = interp2d(lon[:],lat[:],T_OneLvl_06,kind='linear',bounds_error=True)(sLon,sLat) 
                Tint_12[lvl] = interp2d(lon[:],lat[:],T_OneLvl_12,kind='linear',bounds_error=True)(sLon,sLat) 
                Tint_18[lvl] = interp2d(lon[:],lat[:],T_OneLvl_18,kind='linear',bounds_error=True)(sLon,sLat) 
                
                PVint_00[lvl] = interp2d(lon[:],lat[:],PV_OneLvl_00,kind='linear',bounds_error=True)(sLon,sLat) 
                PVint_06[lvl] = interp2d(lon[:],lat[:],PV_OneLvl_06,kind='linear',bounds_error=True)(sLon,sLat) 
                PVint_12[lvl] = interp2d(lon[:],lat[:],PV_OneLvl_12,kind='linear',bounds_error=True)(sLon,sLat) 
                PVint_18[lvl] = interp2d(lon[:],lat[:],PV_OneLvl_18,kind='linear',bounds_error=True)(sLon,sLat)                 

            else:         
                Hgt_00[lvl] = HgtOneLvl_00[latind,lonind]  
                Hgt_06[lvl] = HgtOneLvl_06[latind,lonind] 
                Hgt_12[lvl] = HgtOneLvl_12[latind,lonind] 
                Hgt_18[lvl] = HgtOneLvl_18[latind,lonind] 
                
                Qint_00[lvl] = Q_OneLvl_00[latind,lonind]
                Qint_06[lvl] = Q_OneLvl_06[latind,lonind]
                Qint_12[lvl] = Q_OneLvl_12[latind,lonind]
                Qint_18[lvl] = Q_OneLvl_18[latind,lonind]            
                
                Tint_00[lvl] = T_OneLvl_00[latind,lonind]
                Tint_06[lvl] = T_OneLvl_06[latind,lonind]
                Tint_12[lvl] = T_OneLvl_12[latind,lonind]
                Tint_18[lvl] = T_OneLvl_18[latind,lonind] 
                
                PVint_00[lvl] = PV_OneLvl_00[latind,lonind]
                PVint_06[lvl] = PV_OneLvl_06[latind,lonind]
                PVint_12[lvl] = PV_OneLvl_12[latind,lonind]
                PVint_18[lvl] = PV_OneLvl_18[latind,lonind]                 
                           
                           
        #----------------------------------------
        # Convert Specific humidity from kg/kg to 
        # molecules/molecules 
        #----------------------------------------
        Qint_00 = Qint_00 * 1.608
        Qint_06 = Qint_06 * 1.608
        Qint_12 = Qint_12 * 1.608
        Qint_18 = Qint_18 * 1.608
        
        #-------------------------------------
        # Create daily averages of 00,06,12,18
        #-------------------------------------
        Q_day  = np.mean(np.vstack((Qint_00,Qint_06,Qint_12,Qint_18)),axis=0)
        Z_day  = np.mean(np.vstack((Hgt_00,Hgt_06,Hgt_12,Hgt_18)),axis=0)
        T_day  = np.mean(np.vstack((Tint_00,Tint_06,Tint_12,Tint_18)),axis=0)
        PV_day = np.mean(np.vstack((PVint_00,PVint_06,PVint_12,PVint_18)),axis=0)
        
        #--------------------------------
        # Convert Height [m^2 s^-2] => km
        #--------------------------------
        Z_day = Z_day / 9.81 / 1000.0
         
        #---------------------------------------------------------
        # Construct specific humidity and height profiles for 
        # interpolation on to the sfit input grid which is the
        # same as the WACCM height in monthly profile file.
        # NCEP reanalysis data only goes to 300mb therefore, 
        # merge with monthly averaged WACCM water profiles > 300mb            
        #---------------------------------------------------------
        ERAtop = Z_day[0]
        topInd  = np.argmin( abs(Z - ERAtop) )   # Where top of NCEP reanalysis fits in WACCM grid height
        
        Zin  = np.concatenate( ( Z[0:(topInd-nSkip)]             , Z_day), axis=1 )
        SHin = np.concatenate( ( waccmW[0:(topInd-nSkip),mnthInd], Q_day), axis=1 )
        
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
            fopen.write('    1     H2O from ERA reanalysis and WACCM V6 monthly mean \n')
            
            for row in segmnt(SHout,5):
                strformat = ','.join('{:>12.4E}' for i in row) + ', \n'
                fopen.write(strformat.format(*row))     
                
        #------------------------------
        # Write out Temperature, water,
        # and PV every 6 hours
        #------------------------------
        with open(sngDir+'ERA_Interm_PV.'+YYYY+MM+DD,'w') as fopen:
            fopen.write('Daily Averaged and 6 hourly PV from ERA Interim [K m^2 kg^-1 s^-1] \n')
            fopen.write('{0:>20s}{1:>20s}{2:>20s}{3:>20s}{4:>20s}{5:>20s}\n'.format('Height [km]','PV[K m^2 kg^-1 s^-1]','PV at 00','PV at 06','PV at 12','PV at 18'))
            
            for row in zip(*(Z_day,PV_day,PVint_00,PVint_06,PVint_12,PVint_18)):
                strformat = ','.join('{:>20.7E}' for i in row) + ', \n'
                fopen.write(strformat.format(*row))                  

        with open(sngDir+'ERA_Interm_T.'+YYYY+MM+DD,'w') as fopen:
            fopen.write('Daily averaged and 6 Hourly Temperature from ERA Interim [K] \n')
            fopen.write('{0:>15s}{1:>15s}{2:>15s}{3:>15s}{4:>15s}{5:>15s}\n'.format('Height [km]','T [K]','T at 00','T at 06','T at 12','T at 18'))
            
            for row in zip(*(Z_day,T_day,Tint_00,Tint_06,Tint_12,Tint_18)):
                strformat = ','.join('{:>15.7E}' for i in row) + ', \n'
                fopen.write(strformat.format(*row))      
                
        with open(sngDir+'ERA_Interm_Q.'+YYYY+MM+DD,'w') as fopen:
            fopen.write('Daily averaged and 6 hourly specific humidity Q from ERA Interim [VMR] \n')
            fopen.write('{0:>15s}{1:>15s}{2:>15s}{3:>15s}{4:>15s}{5:>15s}\n'.format('Height [km]','Q [VMR]','Q at 00','Q at 06','Q at 12','Q at 18'))
            
            for row in zip(*(Z_day,Q_day,Qint_00,Qint_06,Qint_12,Qint_18)):
                strformat = ','.join('{:>15.7E}' for i in row) + ', \n'
                fopen.write(strformat.format(*row))                   
        
        #--------------------
        # Create plots to pdf
        #--------------------
        pdfsav = PdfPages(sngDir+'WaterProfile_ERA.pdf')
        
        fig1,ax1 = plt.subplots()
        ax1.plot(SHout,Z,'rx-', label='Interpolated SH')
        ax1.plot(waccmW[:,mnthInd],Z,'bx-',label='WACCM V6 SH')
        ax1.plot(Q_day,Z_day,'kx-',label='ERA Reanalysis SH')
        ax1.grid(True,which='both')
        ax1.legend(prop={'size':9})
        ax1.set_ylabel('Altitude [km]')
        ax1.set_xlabel('VMR [ppv]')
        ax1.tick_params(axis='x',which='both',labelsize=8)
        ax1.set_ylim((Z[-1],80))
        ax1.set_xlim((0,np.max((waccmW[-1,mnthInd],Q_day[-1]))))
        ax1.set_title(oneDay)
        
        pdfsav.savefig(fig1,dpi=250)
        
        fig2,ax2 = plt.subplots()
        ax2.plot(SHout,Z,'rx-', label='Interpolated SH')
        ax2.plot(waccmW[:,mnthInd],Z,'bx-',label='WACCM V6 SH')
        ax2.plot(Q_day,Z_day,'kx-',label='ERA Reanalysis SH')
        ax2.grid(True,which='both')
        ax2.legend(prop={'size':9})
        ax2.set_ylabel('Altitude [km]')
        ax2.set_xlabel('log VMR [ppv]')
        ax2.tick_params(axis='x',which='both',labelsize=8)
        ax2.set_xscale('log')
        ax2.set_ylim((Z[-1],80))
        ax2.set_xlim((0,np.max((waccmW[-1,mnthInd],Q_day[-1]))))
        ax2.set_title(oneDay)
        
        pdfsav.savefig(fig2,dpi=250)            
                
        pdfsav.close()
        
        print 'Finished processing folder: {}'.format(sngDir)
                                                                                    
if __name__ == "__main__":
    main()