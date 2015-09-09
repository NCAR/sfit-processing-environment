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
from scipy.stats.stats import pearsonr
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import matplotlib.gridspec as gridspec

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


def interpAlt(alt_in, Z, val_in, intrpOrder, logFlg):
    
    if logFlg:                
        val_out  = np.exp(np.flipud( intrpUniSpl( np.flipud(alt_in), np.log(np.flipud(val_in)), k=intrpOrder )( np.flipud(Z) ) ) )
    else:
        val_out  = np.flipud( intrpUniSpl( np.flipud(alt_in), np.flipud(val_in), k=intrpOrder )( np.flipud(Z) ) )        
    
    return val_out


def bias(xData,yData):
    ''' Cacluates the mean value of the residuals. 
    Where xData is observation and yData is the model'''

    #--------------------------------
    # Make sure arrays are numpy type
    #--------------------------------
    yData = np.asarray(yData)
    xData = np.asarray(xData)

    #-------------------------------
    # Make sure arrays are same size
    #-------------------------------
    if ( yData.shape[0] != xData.shape[0] ): 
        print 'Data sets must have same size in corrcoef: xData = {}, yData = {}'.format(xData.shape[0],yData.shape[0])
        sys.exit() 

    biasCalc = sum( yData - xData ) / len(yData) 

    return biasCalc    

def rmse(xData, yData):
    '''Calcuates the RMSE, 
       xData = observed data, yData = modeled data'''

    #--------------------------------
    # Make sure arrays are numpy type
    #--------------------------------
    yData = np.asarray(yData)
    xData = np.asarray(xData)

    #-------------------------------
    # Make sure arrays are same size
    #-------------------------------
    if ( yData.shape[0] != xData.shape[0] ): 
        print 'Data sets must have same size in corrcoef: xData = {}, yData = {}'.format(xData.shape[0],yData.shape[0])
        sys.exit() 

    #---------------------------------
    # Find the residual sum of squares 
    #---------------------------------
    SS_res = sum( (yData - xData)**2 )

    #------------------------------
    # Root Mean Square Error (RMSE)
    #------------------------------
    rmse = np.sqrt( SS_res / len(yData) )

    return rmse
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
    
    #-----------------------
    # Date Range of interest
    #-----------------------
    iyear          = 2013
    imnth          = 1
    iday           = 1
    fyear          = 2013
    fmnth          = 12
    fday           = 31
    
    #---------------
    # Data Directory
    #---------------
    dataDir  = '/Volumes/data1/'+loc.lower()+'/'
    
    #-----------------------------
    # Names of output figure files
    #-----------------------------
    figFnameQ = '/Users/ebaumer/Data/Q_'+loc.lower()+'.pdf'
    figFnameT = '/Users/ebaumer/Data/T_'+loc.lower()+'.pdf'
    
    figFnameQcor = '/Users/ebaumer/Data/Qcorr_'+loc.lower()+'.pdf'
    figFnameTcor = '/Users/ebaumer/Data/Tcorr_'+loc.lower()+'.pdf'
    
    figFnameSTD  = '/Users/ebaumer/Data/STD_'+loc.lower()+'.pdf'
    fdataSTD     = '/Users/ebaumer/Data/STD_'+loc.lower()+'.dat'
    
    #---------------------
    # Establish date range
    #---------------------
    dRange = sc.DateRange(iyear,imnth,iday,fyear,fmnth,fday) 

    #----------------------------
    # File and directory checking
    #----------------------------
    ckDir(dataDir,exitFlg=True)
    
    #---------------------
    # Interpolation things
    #---------------------
    intrpOrder = 1            # Order of interpolation
    logFlg     = False        # Flag to do interpolation of log of water    
    
    #---------------------------------------
    # Altitude levels for different stations
    #---------------------------------------
    if loc.lower() == 'tab':
        Z = np.array([  44.0000,     42.0000,     40.0000,     38.0000,     36.0000, 
                        34.0000,     32.0000,     30.0000,     28.0000,     26.0000, 
                        24.0000,     22.0000,     20.0000,     18.0000,     16.0000, 
                        14.0000,     12.0000,     10.0000,      9.0000,      8.0000, 
                         7.0000,      6.0000,      5.0000,      4.0000,      3.0000, 
                         2.0000,      1.0000,      0.2250   ])
        sLat = 76.52
        sLon = 291.23               # 68.77 W = (360.0 - 68.77) = 291.23 E
        
    elif loc.lower() == 'mlo':
        Z = np.array([  44.0000,     42.0000,     40.0000,     38.0000,     36.0000, 
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
    firstFlg = True
    
    for sngDir in dirLst:
        
        #----------------------------
        # Get date in datetime format
        #----------------------------
        yrstr   = os.path.basename(sngDir[:-1])[0:4]
        mnthstr = os.path.basename(sngDir[:-1])[4:6]
        daystr  = os.path.basename(sngDir[:-1])[6:8]
        oneDay  = dt.datetime(int(yrstr),int(mnthstr),int(daystr))

        #----------------------------------------------------------------
        # Open and read ERA Interim Q and T values for 6 hourly time step
        #----------------------------------------------------------------
        Q_file = sngDir + 'ERA_Interm_Q.' + yrstr + mnthstr + daystr
        T_file = sngDir + 'ERA_Interm_T.' + yrstr + mnthstr + daystr
        
        ckFile(Q_file,exitFlg=True)
        ckFile(T_file,exitFlg=True)
                           
        with open(Q_file,'r') as fopen: lines = fopen.readlines()
        alt_temp  = np.array([ float(x.strip().split(',')[0]) for x in lines[2:] ])
        Q_daily_temp = np.array([ float(x.strip().split(',')[1]) for x in lines[2:] ])
        Q_00_temp = np.array([ float(x.strip().split(',')[2]) for x in lines[2:] ])
        Q_06_temp = np.array([ float(x.strip().split(',')[3]) for x in lines[2:] ])
        Q_12_temp = np.array([ float(x.strip().split(',')[4]) for x in lines[2:] ])
        Q_18_temp = np.array([ float(x.strip().split(',')[5]) for x in lines[2:] ])
        
        with open(T_file,'r') as fopen: lines = fopen.readlines()
        T_daily_temp = np.array([ float(x.strip().split(',')[1]) for x in lines[2:] ])
        T_00_temp = np.array([ float(x.strip().split(',')[2]) for x in lines[2:] ])
        T_06_temp = np.array([ float(x.strip().split(',')[3]) for x in lines[2:] ])
        T_12_temp = np.array([ float(x.strip().split(',')[4]) for x in lines[2:] ])
        T_18_temp = np.array([ float(x.strip().split(',')[5]) for x in lines[2:] ])        
              
        #--------------------------------------------------------------
        # Interpolate to specific humidity on WACCM grid. X data must 
        # be increasing => flip dimensions and then flip back
        #--------------------------------------------------------------
        Q_daily_temp = interpAlt(alt_temp, Z, Q_daily_temp, intrpOrder, logFlg)
        Q_00_temp = interpAlt(alt_temp, Z, Q_00_temp, intrpOrder, logFlg)
        Q_06_temp = interpAlt(alt_temp, Z, Q_06_temp, intrpOrder, logFlg)
        Q_12_temp = interpAlt(alt_temp, Z, Q_12_temp, intrpOrder, logFlg)
        Q_18_temp = interpAlt(alt_temp, Z, Q_18_temp, intrpOrder, logFlg)
        
        T_daily_temp = interpAlt(alt_temp, Z, T_daily_temp, intrpOrder, logFlg)
        T_00_temp = interpAlt(alt_temp, Z, T_00_temp, intrpOrder, logFlg)
        T_06_temp = interpAlt(alt_temp, Z, T_06_temp, intrpOrder, logFlg)
        T_12_temp = interpAlt(alt_temp, Z, T_12_temp, intrpOrder, logFlg)
        T_18_temp = interpAlt(alt_temp, Z, T_18_temp, intrpOrder, logFlg)        
        
        if firstFlg:
            firstFlg = False
            Q_daily = Q_daily_temp
            Q_00 = Q_00_temp
            Q_06 = Q_06_temp
            Q_12 = Q_12_temp
            Q_18 = Q_18_temp
            T_daily = T_daily_temp
            T_00 = T_00_temp
            T_06 = T_06_temp
            T_12 = T_12_temp
            T_18 = T_18_temp          
        else:
            Q_daily = np.vstack((Q_daily,Q_daily_temp))
            Q_00 = np.vstack((Q_00,Q_00_temp))
            Q_06 = np.vstack((Q_06,Q_06_temp))
            Q_12 = np.vstack((Q_12,Q_12_temp))
            Q_18 = np.vstack((Q_18,Q_18_temp))
            T_daily = np.vstack((T_daily,T_daily_temp))
            T_00 = np.vstack((T_00,T_00_temp))
            T_06 = np.vstack((T_06,T_06_temp))
            T_12 = np.vstack((T_12,T_12_temp))
            T_18 = np.vstack((T_18,T_18_temp))           
        
    
    #----------------
    # Find Statistics
    #----------------
    Q_daily_mean = np.mean(Q_daily,axis=0)
    Q_daily_std  = np.std(Q_daily,axis=0)
    Q_00_mean = np.mean(Q_00,axis=0)
    Q_00_std  = np.std(Q_00,axis=0)
    Q_06_mean = np.mean(Q_06,axis=0)
    Q_06_std  = np.std(Q_06,axis=0)
    Q_12_mean = np.mean(Q_12,axis=0)
    Q_12_std  = np.std(Q_12,axis=0)
    Q_18_mean = np.mean(Q_18,axis=0)
    Q_18_std  = np.std(Q_18,axis=0)  
    
    T_daily_mean = np.mean(T_daily,axis=0)
    T_daily_std  = np.std(T_daily,axis=0)    
    T_00_mean = np.mean(T_00,axis=0)
    T_00_std  = np.std(T_00,axis=0)
    T_06_mean = np.mean(T_06,axis=0)
    T_06_std  = np.std(T_06,axis=0)
    T_12_mean = np.mean(T_12,axis=0)
    T_12_std  = np.std(T_12,axis=0)
    T_18_mean = np.mean(T_18,axis=0)
    T_18_std  = np.std(T_18,axis=0)        
    
    T_diff00 = abs(T_daily - T_00)    
    T_diff06 = abs(T_daily - T_06)
    T_diff12 = abs(T_daily - T_12)
    T_diff18 = abs(T_daily - T_18)
    T_diffAll= np.vstack((T_diff00,T_diff06,T_diff12,T_diff18))
    T_diffSTD= np.std(T_diffAll,axis=0)
    
    Q_diff00 = abs(Q_daily - Q_00)    
    Q_diff06 = abs(Q_daily - Q_06)
    Q_diff12 = abs(Q_daily - Q_12)
    Q_diff18 = abs(Q_daily - Q_18)
    Q_diffAll= np.vstack((Q_diff00,Q_diff06,Q_diff12,Q_diff18))
    Q_diffSTD= np.std(Q_diffAll,axis=0)    
    
    #----------------------------
    # Flatten arrays to correlate
    #----------------------------
    Q_daily_flat = Q_daily.flatten()
    Q_00_flat    = Q_00.flatten()
    Q_06_flat    = Q_06.flatten()
    Q_12_flat    = Q_12.flatten()
    Q_18_flat    = Q_18.flatten()
    
    T_daily_flat = T_daily.flatten()
    T_00_flat    = T_00.flatten()
    T_06_flat    = T_06.flatten()
    T_12_flat    = T_12.flatten()
    T_18_flat    = T_18.flatten()
    
    alt_mat      = np.array([Z]*np.shape(Q_00)[0])
    alt_flat     = alt_mat.flatten()
                                     
    #-------------------------------------------
    # Calculate Pearsons correlation coefficient
    #-------------------------------------------
    (R_Q00,_) = pearsonr(Q_00_flat, Q_daily_flat)    
    (R_Q06,_) = pearsonr(Q_06_flat, Q_daily_flat)    
    (R_Q12,_) = pearsonr(Q_12_flat, Q_daily_flat)    
    (R_Q18,_) = pearsonr(Q_18_flat, Q_daily_flat)    
    
    (R_T00,_) = pearsonr(T_00_flat, T_daily_flat)    
    (R_T06,_) = pearsonr(T_06_flat, T_daily_flat)    
    (R_T12,_) = pearsonr(T_12_flat, T_daily_flat)    
    (R_T18,_) = pearsonr(T_18_flat, T_daily_flat)     
    
    #------------------------
    # Calculate RMSE and bias
    #------------------------
    RMSE_Q00 = rmse(Q_00_flat, Q_daily_flat)
    RMSE_Q06 = rmse(Q_06_flat, Q_daily_flat)
    RMSE_Q12 = rmse(Q_12_flat, Q_daily_flat)
    RMSE_Q18 = rmse(Q_18_flat, Q_daily_flat)
    
    RMSE_T00 = rmse(T_00_flat, T_daily_flat)
    RMSE_T06 = rmse(T_06_flat, T_daily_flat)
    RMSE_T12 = rmse(T_12_flat, T_daily_flat)
    RMSE_T18 = rmse(T_18_flat, T_daily_flat)    
    
    bias_Q00 = bias(Q_00_flat, Q_daily_flat)
    bias_Q06 = bias(Q_06_flat, Q_daily_flat)
    bias_Q12 = bias(Q_12_flat, Q_daily_flat)
    bias_Q18 = bias(Q_18_flat, Q_daily_flat)
    
    bias_T00 = bias(T_00_flat, T_daily_flat)
    bias_T06 = bias(T_06_flat, T_daily_flat)
    bias_T12 = bias(T_12_flat, T_daily_flat)
    bias_T18 = bias(T_18_flat, T_daily_flat) 
    
    print 'R_Q00 = {}'.format(R_Q00)
    print 'R_Q06 = {}'.format(R_Q06)
    print 'R_Q12 = {}'.format(R_Q12)
    print 'R_Q18 = {}'.format(R_Q18)
    
    print 'R_T00 = {}'.format(R_T00)
    print 'R_T06 = {}'.format(R_T06)
    print 'R_T12 = {}'.format(R_T12)
    print 'R_T18 = {}'.format(R_T18)    
    
    print 'RMSE_Q00 = {}'.format(RMSE_Q00)
    print 'RMSE_Q06 = {}'.format(RMSE_Q06)
    print 'RMSE_Q12 = {}'.format(RMSE_Q12)
    print 'RMSE_Q18 = {}'.format(RMSE_Q18)    
    
    print 'RMSE_T00 = {}'.format(RMSE_T00)
    print 'RMSE_T06 = {}'.format(RMSE_T06)
    print 'RMSE_T12 = {}'.format(RMSE_T12)
    print 'RMSE_T18 = {}'.format(RMSE_T18)      
    
    print 'bias_Q00 = {}'.format(bias_Q00)
    print 'bias_Q06 = {}'.format(bias_Q06)
    print 'bias_Q12 = {}'.format(bias_Q12)
    print 'bias_Q18 = {}'.format(bias_Q18)    
    
    print 'bias_T00 = {}'.format(bias_T00)
    print 'bias_T06 = {}'.format(bias_T06)
    print 'bias_T12 = {}'.format(bias_T12)
    print 'bias_T18 = {}'.format(bias_T18)      
    
    
    #-----------
    # Write data
    #-----------
    with open(fdataSTD,'w') as fopen:
        fopen.write('Standard Deviation of the absolute value of the Temperature and water profile diurnal cycle\n')
        fopen.write('{0:>20s}{1:>20s}{2:>20s}\n'.format('Height [km]','Temperature [km]','Water [VMR]'))
    
        for row in zip(*(Z,T_diffSTD,Q_diffSTD)):
            strformat = ','.join('{:>20.7E}' for i in row) + ', \n'
            fopen.write(strformat.format(*row))
    
    
    #----------
    # Plot data
    #----------
    pdfsav = PdfPages(figFnameSTD)
    fig,(ax1,ax2) = plt.subplots(1,2,sharey=True)

    ax1.plot(T_diffSTD/T_daily_mean*100.0,Z)
    ax2.plot(Q_diffSTD/Q_daily_mean*100.0,Z)
         
    ax1.grid(True,which='both')   
    ax2.grid(True,which='both')
    ax1.set_ylabel('Altitude [km]')
    ax1.set_xlabel('Temperature [% of Daily Mean]')
    ax2.set_xlabel('Water [% of Daily Mean]')   
    #plt.suptitle('Standard Deviation of Diurnal Cycle for Temperature and Water Profiles \n Mauna Loa, 2013 ',multialignment='center')
    
    ax1.tick_params(axis='x',which='both',labelsize=8)
    ax2.tick_params(axis='x',which='both',labelsize=7)
    

    pdfsav.savefig(fig,dpi=350)    
    pdfsav.close()    
    
    # Q Corr
    pdfsav = PdfPages(figFnameQcor)
    fig,((ax1,ax2),(ax3,ax4))  = plt.subplots(2,2)

    cbar = ax1.scatter(Q_00_flat,Q_daily_flat,c=alt_flat,edgecolors='none',vmin=np.min(Z),vmax=np.max(Z))
    ax1.plot(ax1.get_xlim(), ax1.get_ylim(), ls="--", c=".3")
    ax2.scatter(Q_06_flat,Q_daily_flat,c=alt_flat,edgecolors='none',vmin=np.min(Z),vmax=np.max(Z))
    ax2.plot(ax2.get_xlim(), ax2.get_ylim(), ls="--", c=".3")
    ax3.scatter(Q_12_flat,Q_daily_flat,c=alt_flat,edgecolors='none',vmin=np.min(Z),vmax=np.max(Z))
    ax3.plot(ax3.get_xlim(), ax3.get_ylim(), ls="--", c=".3")
    ax4.scatter(Q_18_flat,Q_daily_flat,c=alt_flat,edgecolors='none',vmin=np.min(Z),vmax=np.max(Z))
    ax4.plot(ax4.get_xlim(), ax4.get_ylim(), ls="--", c=".3")
    
    ax1.set_ylabel('Q at 00 UTC',fontsize=8)
    ax1.set_xlabel('Q Daily Avg',fontsize=8)
    
    ax2.set_ylabel('Q at 06 UTC',fontsize=8)
    ax2.set_xlabel('Q Daily Avg',fontsize=8)
    
    ax3.set_ylabel('Q at 12 UTC',fontsize=8)
    ax3.set_xlabel('Q Daily Avg',fontsize=8)
    
    ax4.set_ylabel('Q at 18 UTC',fontsize=8)
    ax4.set_xlabel('Q Daily Avg',fontsize=8)    

    ax1.text(0.05,0.95,'R = {:4.3f}'.format(R_Q00),fontsize=8,transform=ax1.transAxes)
    ax2.text(0.05,0.95,'R = {:4.3f}'.format(R_Q06),fontsize=8,transform=ax2.transAxes)
    ax3.text(0.05,0.95,'R = {:4.3f}'.format(R_Q12),fontsize=8,transform=ax3.transAxes)
    ax4.text(0.05,0.95,'R = {:4.3f}'.format(R_Q18),fontsize=8,transform=ax4.transAxes)

    ax1.text(0.05,0.87,'RMSE = {0:3.2e} ({1:5.2f}%)'.format(RMSE_Q00,RMSE_Q00/np.mean(Q_daily_flat)*100.),fontsize=8,transform=ax1.transAxes)
    ax2.text(0.05,0.87,'RMSE = {0:3.2e} ({1:5.2f}%)'.format(RMSE_Q06,RMSE_Q06/np.mean(Q_daily_flat)*100.),fontsize=8,transform=ax2.transAxes)
    ax3.text(0.05,0.87,'RMSE = {0:3.2e} ({1:5.2f}%)'.format(RMSE_Q12,RMSE_Q12/np.mean(Q_daily_flat)*100.),fontsize=8,transform=ax3.transAxes)
    ax4.text(0.05,0.87,'RMSE = {0:3.2e} ({1:5.2f}%)'.format(RMSE_Q18,RMSE_Q18/np.mean(Q_daily_flat)*100.),fontsize=8,transform=ax4.transAxes)

    ax1.text(0.05,0.79,'Bias = {0:3.2e} ({1:5.2f}%)'.format(bias_Q00,bias_Q00/np.mean(Q_daily_flat)*100.),fontsize=8,transform=ax1.transAxes)
    ax2.text(0.05,0.79,'Bias = {0:3.2e} ({1:5.2f}%)'.format(bias_Q06,bias_Q06/np.mean(Q_daily_flat)*100.),fontsize=8,transform=ax2.transAxes)
    ax3.text(0.05,0.79,'Bias = {0:3.2e} ({1:5.2f}%)'.format(bias_Q12,bias_Q12/np.mean(Q_daily_flat)*100.),fontsize=8,transform=ax3.transAxes)
    ax4.text(0.05,0.79,'Bias = {0:3.2e} ({1:5.2f}%)'.format(bias_Q18,bias_Q18/np.mean(Q_daily_flat)*100.),fontsize=8,transform=ax4.transAxes)
    
    ax1.grid(True,which='both')
    ax2.grid(True,which='both')
    ax3.grid(True,which='both')
    ax4.grid(True,which='both')
    ax1.tick_params(axis='x',which='both',labelsize=6)
    ax1.tick_params(axis='y',which='both',labelsize=6)    
    ax2.tick_params(axis='x',which='both',labelsize=6)
    ax2.tick_params(axis='y',which='both',labelsize=6) 
    ax3.tick_params(axis='x',which='both',labelsize=6)
    ax3.tick_params(axis='y',which='both',labelsize=6) 
    ax4.tick_params(axis='x',which='both',labelsize=6)
    ax4.tick_params(axis='y',which='both',labelsize=6)     
    
    fig.subplots_adjust(right=0.85)
    cbar_ax = fig.add_axes([0.9, 0.1, 0.03, 0.8])    
    cbarObj = fig.colorbar(cbar,cax=cbar_ax)
    cbarObj.ax.tick_params(labelsize=8)
    cbarObj.solids.set_rasterized(True) 
    
    cbarObj.set_label('Altitude [km]',fontsize=8)
    pdfsav.savefig(fig,dpi=350)
    pdfsav.close()
    
    # T Corr
    pdfsav = PdfPages(figFnameTcor)
    fig,((ax1,ax2),(ax3,ax4))  = plt.subplots(2,2)

    cbar = ax1.scatter(T_00_flat,T_daily_flat,c=alt_flat,edgecolors='none',vmin=np.min(Z),vmax=np.max(Z))
    ax1.plot(ax1.get_xlim(), ax1.get_ylim(), ls="--", c=".3")
    ax2.scatter(T_06_flat,T_daily_flat,c=alt_flat,edgecolors='none',vmin=np.min(Z),vmax=np.max(Z))
    ax2.plot(ax2.get_xlim(), ax2.get_ylim(), ls="--", c=".3")
    ax3.scatter(T_12_flat,T_daily_flat,c=alt_flat,edgecolors='none',vmin=np.min(Z),vmax=np.max(Z))
    ax3.plot(ax3.get_xlim(), ax3.get_ylim(), ls="--", c=".3")
    ax4.scatter(T_18_flat,T_daily_flat,c=alt_flat,edgecolors='none',vmin=np.min(Z),vmax=np.max(Z))
    ax4.plot(ax4.get_xlim(), ax4.get_ylim(), ls="--", c=".3")
    
    ax1.set_ylabel('T at 00 UTC',fontsize=8)
    ax1.set_xlabel('T Daily Avg',fontsize=8)
    
    ax2.set_ylabel('T at 06 UTC',fontsize=8)
    ax2.set_xlabel('T Daily Avg',fontsize=8)
    
    ax3.set_ylabel('T at 12 UTC',fontsize=8)
    ax3.set_xlabel('T Daily Avg',fontsize=8)
    
    ax4.set_ylabel('T at 18 UTC',fontsize=8)
    ax4.set_xlabel('T Daily Avg',fontsize=8)    

    ax1.text(0.05,0.95,'R = {:4.3f}'.format(R_T00),fontsize=8,transform=ax1.transAxes)
    ax2.text(0.05,0.95,'R = {:4.3f}'.format(R_T06),fontsize=8,transform=ax2.transAxes)
    ax3.text(0.05,0.95,'R = {:4.3f}'.format(R_T12),fontsize=8,transform=ax3.transAxes)
    ax4.text(0.05,0.95,'R = {:4.3f}'.format(R_T18),fontsize=8,transform=ax4.transAxes)

    ax1.text(0.05,0.87,'RMSE = {0:5.3f} ({1:5.2f}%)'.format(RMSE_T00,RMSE_T00/np.mean(T_daily_flat)*100.),fontsize=8,transform=ax1.transAxes)
    ax2.text(0.05,0.87,'RMSE = {0:5.3f} ({1:5.2f}%)'.format(RMSE_T06,RMSE_T06/np.mean(T_daily_flat)*100.),fontsize=8,transform=ax2.transAxes)
    ax3.text(0.05,0.87,'RMSE = {0:5.3f} ({1:5.2f}%)'.format(RMSE_T12,RMSE_T12/np.mean(T_daily_flat)*100.),fontsize=8,transform=ax3.transAxes)
    ax4.text(0.05,0.87,'RMSE = {0:5.3f} ({1:5.2f}%)'.format(RMSE_T18,RMSE_T18/np.mean(T_daily_flat)*100.),fontsize=8,transform=ax4.transAxes)

    ax1.text(0.05,0.79,'Bias = {0:5.3f} ({1:5.2f}%)'.format(bias_T00,bias_T00/np.mean(T_daily_flat)*100.),fontsize=8,transform=ax1.transAxes)
    ax2.text(0.05,0.79,'Bias = {0:5.3f} ({1:5.2f}%)'.format(bias_T06,bias_T06/np.mean(T_daily_flat)*100.),fontsize=8,transform=ax2.transAxes)
    ax3.text(0.05,0.79,'Bias = {0:5.3f} ({1:5.2f}%)'.format(bias_T12,bias_T12/np.mean(T_daily_flat)*100.),fontsize=8,transform=ax3.transAxes)
    ax4.text(0.05,0.79,'Bias = {0:5.3f} ({1:5.2f}%)'.format(bias_T18,bias_T18/np.mean(T_daily_flat)*100.),fontsize=8,transform=ax4.transAxes)

    
    ax1.grid(True,which='both')
    ax2.grid(True,which='both')
    ax3.grid(True,which='both')
    ax4.grid(True,which='both')
    ax1.tick_params(axis='x',which='both',labelsize=7)
    ax1.tick_params(axis='y',which='both',labelsize=7)    
    ax2.tick_params(axis='x',which='both',labelsize=7)
    ax2.tick_params(axis='y',which='both',labelsize=7) 
    ax3.tick_params(axis='x',which='both',labelsize=7)
    ax3.tick_params(axis='y',which='both',labelsize=7) 
    ax4.tick_params(axis='x',which='both',labelsize=7)
    ax4.tick_params(axis='y',which='both',labelsize=7)        
    
    fig.subplots_adjust(right=0.85)
    cbar_ax = fig.add_axes([0.9, 0.1, 0.03, 0.8])    
    cbarObj = fig.colorbar(cbar,cax=cbar_ax)
    cbarObj.solids.set_rasterized(True)
    
    cbarObj.set_label('Altitude [km]',fontsize=8)
    cbarObj.ax.tick_params(labelsize=8)
    pdfsav.savefig(fig,dpi=350)
    pdfsav.close()    
    
    # Q
    pdfsav = PdfPages(figFnameQ)
    fig,(ax1,ax2) = plt.subplots(1,2)
    
    ax1.plot(Q_daily_mean,Z,label='Daily')
    ax2.plot(Q_daily_mean,Z,label='Daily')
    #ax1.fill_betweenx(Z,Q_daily_mean-Q_daily_std,Q_daily_mean+Q_daily_std,alpha=0.5,color='0.75')

    ax1.plot(Q_00_mean,Z,label='00 UTC')
    ax2.plot(Q_00_mean,Z,label='00 UTC')
    #ax1.fill_betweenx(Z,Q_00_mean-Q_00_std,Q_00_mean+Q_00_std,alpha=0.5,color='0.75')

    ax1.plot(Q_06_mean,Z,label='06 UTC')
    ax2.plot(Q_06_mean,Z,label='06 UTC')
    #ax1.fill_betweenx(Z,Q_06_mean-Q_06_std,Q_06_mean+Q_06_std,alpha=0.5,color='0.75')
    
    ax1.plot(Q_12_mean,Z,label='12 UTC')
    ax2.plot(Q_12_mean,Z,label='12 UTC')
    #ax1.fill_betweenx(Z,Q_12_mean-Q_12_std,Q_12_mean+Q_12_std,alpha=0.5,color='0.75')
    
    ax1.plot(Q_18_mean,Z,label='18 UTC')
    ax2.plot(Q_18_mean,Z,label='18 UTC')
    #ax1.fill_betweenx(Z,Q_18_mean-Q_18_std,Q_18_mean+Q_18_std,alpha=0.5,color='0.75')    
         
    ax1.grid(True,which='both')
    ax1.legend(prop={'size':9})   
    ax2.grid(True,which='both')
    ax2.legend(prop={'size':9})     
    ax1.set_ylabel('Altitude [km]')
    ax1.set_xlabel('Log VMR')
    ax1.set_xscale('log')
    ax2.set_xlabel('Log VMR')
    ax2.set_xscale('log')    
    ax2.set_ylim([0,10])
    
    ax1.tick_params(axis='x',which='both',labelsize=8)
    ax2.tick_params(axis='x',which='both',labelsize=8)
    #plt.suptitle('Mean and Standard Deviation of Water Profiles Derived from ERA Interim \n Mauna Loa 2013',multialignment='center')

    pdfsav.savefig(fig,dpi=350)
    pdfsav.close()
    
    # T      
    pdfsav = PdfPages(figFnameT)
    fig,(ax1,ax2) = plt.subplots(1,2)

    ax1.plot(T_daily_mean,Z,label='Daily')
    ax2.plot(T_daily_mean,Z,label='Daily')
    #ax1.fill_betweenx(Z,T_daily_mean-T_daily_std,T_daily_mean+T_daily_std,alpha=0.5,color='0.75')

    ax1.plot(T_00_mean,Z,label='00 UTC')
    ax2.plot(T_00_mean,Z,label='00 UTC')
    #ax1.fill_betweenx(Z,T_00_mean-T_00_std,T_00_mean+T_00_std,alpha=0.5,color='0.75')

    ax1.plot(T_06_mean,Z,label='06 UTC')
    ax2.plot(T_06_mean,Z,label='06 UTC')
    #ax1.fill_betweenx(Z,T_06_mean-T_06_std,T_06_mean+T_06_std,alpha=0.5,color='0.75')
    
    ax1.plot(T_12_mean,Z,label='12 UTC')
    ax2.plot(T_12_mean,Z,label='12 UTC')
    #ax1.fill_betweenx(Z,T_12_mean-T_12_std,T_12_mean+T_12_std,alpha=0.5,color='0.75')
    
    ax1.plot(T_18_mean,Z,label='18 UTC')
    ax2.plot(T_18_mean,Z,label='18 UTC')
    #ax1.fill_betweenx(Z,T_18_mean-T_18_std,T_18_mean+T_18_std,alpha=0.5,color='0.75')   
         
    ax1.grid(True,which='both')
    ax1.legend(prop={'size':9})   
    ax2.grid(True,which='both')
    ax2.legend(prop={'size':9})     
    ax1.set_ylabel('Altitude [km]')
    ax1.set_xlabel('Temperature [K]')
    ax2.set_xlabel('Temperature [K]')   
    ax2.set_ylim([0,10])
    
    ax1.tick_params(axis='x',which='both',labelsize=8)
    ax2.tick_params(axis='x',which='both',labelsize=8)
    #plt.suptitle('Mean and Standard Deviation of Temperature Profiles Derived from ERA Interim \n Mauna Loa 2013',multialignment='center')

    pdfsav.savefig(fig,dpi=350)    
    pdfsav.close()
                                                                                    
if __name__ == "__main__":
    main()