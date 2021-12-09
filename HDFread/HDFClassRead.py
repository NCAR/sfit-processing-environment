#----------------------------------------------------------------------------------------
# Name:
#        HDFClassRead.py
#
# Purpose:
#       This is a collection of classes and functions used for processing and ploting HDF files
#
#
# Notes:
#
#
# Version History:
#       Created, Dec, 2016  Ivan Ortega (iortega@ucar.edu)
#
#
# License:
#    Copyright (c) 2013-2014 NDACC/IRWG
#    This file is part of sfit4.
#
#    sfit4 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    sfit4 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with sfit4.  If not, see <http://www.gnu.org/licenses/>
#
#----------------------------------------------------------------------------------------

import sys
import os
sys.path.append((os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "HDFsave")))
sys.path.append((os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "ExternalData")))

import datetime as dt
import time
import math
import numpy as np
import csv
import itertools
from collections import OrderedDict
from os import listdir
from os.path import isfile, join
import re
#import hdfBaseRetDat

from scipy.integrate import simps
import matplotlib.animation as animation
import matplotlib
import matplotlib.dates as md
from matplotlib.dates import DateFormatter, MonthLocator, YearLocator
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FormatStrFormatter, MultipleLocator,AutoMinorLocator,ScalarFormatter
from matplotlib.backends.backend_pdf import PdfPages #to save multiple pages in 1 pdf...
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import matplotlib.gridspec as gridspec
import matplotlib.gridspec as gridspec
import glob

from pyhdf.SD import SD, SDC
from pyhdf.SD import *
#import coda
from cycler import cycler
np.warnings.filterwarnings('ignore')
import h5py



                                            #------------------#
                                            # Define functions #
                                            #------------------#

def nearestDate(daysList, year, month, day=1):
    ''' Finds the nearest date from a list of days based on a given year, month, and day'''
    testDate = dt.date(year, month, day)
    return min( daysList, key=lambda x:abs(x-testDate) )

def nearestind(val,array):
    ''' Returns the index in array for closest value to val'''
    return (np.abs(array-val)).argmin()

def daysList(timeList):
    ''' Finds a unique set of days within a listof dates '''
    dateList = [dt.date(x.year,x.month,x.day) for x in timeList]
    dateList = np.unique(dateList)
    
    return np.sort(dateList)

def sortDict(DataDict,keyval,excld=[]):
    ''' Sort all values of dictionary based on values of one key'''
    base = DataDict[keyval]
    for k in DataDict:
        if k not in excld: DataDict[k] = [y for (x,y) in sorted(zip(base,DataDict[k]))]
    return DataDict

def ckDir(dirName,logFlg=False,exitFlg=False):
    ''' '''
    if not os.path.exists( dirName ):
        print ('Input Directory %s does not exist' % (dirName))
        if logFlg: logFlg.error('Directory %s does not exist' % dirName)
        if exitFlg: sys.exit()
        return False
    else:
        return True   

def ckFile(fName,logFlg=False,exitFlg=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print ('File %s does not exist' % (fName))
        if logFlg: logFlg.error('Unable to find file: %s' % fName)
        if exitFlg: sys.exit()
        return False
    else:
        return True   
    
def tryopen(fname):
    ''' Try to open a file and read contents'''
    try:
        with open(fname, 'r' ) as fopen:
            return fopen.readlines()
    except IOError as errmsg:
        print (errmsg)
        return False

def convrtD(rhs):
    '''This identifies numbers specified in scientific notation with d 
       for double precision and converts them to floats'''
    if 'd' in rhs.lower():                               # Test and handle strings containing D (ie 1.0D0)
        mant,trsh,expo = rhs.lower().partition('d')
        try:
            rhs = float(mant)*10**int(expo)
        except ValueError:
            pass
    else:                                                # Handle strings => number
        try:
            rhs = float(rhs)
        except ValueError:
            pass        

    return rhs

def dbFilterUL(fltrParam,lwrVal=False,uprVal=False):
    ''' Filter the output data based on upper an lower value and
        return the corresponding indicies'''
    inds = []

    #-------------------------------------------
    # At least one bound must be set. Check this
    #-------------------------------------------
    if (not lwrVal) and (not uprVal):
        print ("Must specify at least one bound in dbFilterUL")
        return

    #----------------------------------------
    # Case where lower value is not specified
    #----------------------------------------
    if not lwrVal:
        for ind,val in enumerate(fltrParam):
            if val <= uprVal: inds.append(ind)

    #----------------------------------------
    # Case where upper value is not specified
    #----------------------------------------
    elif not uprVal:
        for ind,val in enumerate(fltrParam):
            if val <= lwrVal: inds.append(ind)

    #---------------------------------------------
    # Case where lower and upper val are specified
    #---------------------------------------------
    else:
        for ind,val in enumerate(fltrParam):
            if ( val >= lwrVal and val <= uprVal ): inds.append(ind)

    return inds


def dbFilterTF(fltrParam,fltrVal):
    ''' Filter the output data based on True False value
        and return the corresponding indicies'''
    inds = []

    #------------------------------
    # Find cases that match fltrVal
    #------------------------------
    for ind,val in enumerate(fltrParam):
        if val == fltrVal: inds.append(ind)

    return inds


def getintrsct(vals1,vals2):
    ''' Return the indicies of vals1 and vals2 for the intersection '''

    intrsctVals = np.intersect1d(vals1,vals2)
    inds1       = np.nonzero( np.in1d( vals1, intrsctVals ) )[0]
    inds2       = np.nonzero( np.in1d( vals2, intrsctVals ) )[0]

    return (inds1,inds2)


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
        print ('Data sets must have same size in corrcoef: xData = {}, yData = {}'.format(xData.shape[0],yData.shape[0]))
        sys.exit() 

    biasCalc = sum( yData - xData ) / len(yData) 

    return biasCalc    

def rmse(xData, yData):
    '''Calcuates the RMSE and Persons correlation coefficient, 
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
        print ('Data sets must have same size in corrcoef: xData = {}, yData = {}'.format(xData.shape[0],yData.shape[0]))
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


def toYearFraction(dates):
    ''' Convert datetime to year and fraction of year'''

    #def sinceEpoch(date): # returns seconds since epoch
        #return time.mktime(date.timetuple())
    #s = sinceEpoch
    ep_fnc = lambda x: time.mktime(x.timetuple())
    
    retrnDates = np.zeros(len(dates))
    
    for i,sngDate in enumerate(dates):
        year = sngDate.year
        startOfThisYear = dt.datetime(year=year, month=1, day=1)
        startOfNextYear = dt.datetime(year=year+1, month=1, day=1)
    
        yearElapsed = ep_fnc(sngDate) - ep_fnc(startOfThisYear)
        yearDuration = ep_fnc(startOfNextYear) - ep_fnc(startOfThisYear)
        fraction = yearElapsed/yearDuration
        retrnDates[i] = sngDate.year + fraction

    return retrnDates


def dailyAvg(data, dates, dateAxis=1, meanAxis=0, quad=0):
    ''' Creates daily averages of specified quantity'''

    #-----------------------------
    # Initialize output dictionary
    #-----------------------------
    outdata = {}
    dataAvg = []
    cnt     = []
    std     = []

    #-----------------------------------------
    # Convert date time input to strictly date
    #-----------------------------------------
    dates_daily = np.asarray([dt.date(d.year,d.month,d.day) for d in dates])

    #-----------------------------
    # Ensure data is a numpy array
    #-----------------------------
    data = np.asarray(data)

    #--------------------------------------
    # Create a list of days to loop through
    #--------------------------------------
    uniqueDays = list(set(dates_daily))          # Find a list of unique days
    uniqueDays.sort()
    uniqueDays = np.asarray(uniqueDays)    

    #-------------------------
    # Loop through unique days
    #-------------------------
    for indDay in uniqueDays:

        inds = np.where(dates_daily == indDay)[0]                                       # Index for values to use as daily average
       
        if data.ndim == 1:                                                              # For single dimension array   
            if quad == 1: dataAvg.append( np.sqrt(np.sum(data[inds]**2)) / len(inds) )  # Find daily average (sqrt(sum(x^2))/N)
            else:         dataAvg.append( np.mean(data[inds]) )                         # Find daily average (straight mean)
            std.append(np.std(data[inds]))                                              # Find standard deviation
            
        else:                                                                           # For multi-Dimension array
            s           = [slice(None)] * data.ndim
            s[dateAxis] = inds
            tempMat     = data[s]
            if quad == 1: dataAvg.append( np.sqrt(np.sum(tempMat,axis=meanAxis) / len(inds)))
            else:         dataAvg.append( np.mean(tempMat,axis=meanAxis) )
            std.append(np.std(tempMat,axis=meanAxis))                                  # Find standard deviation
        
        cnt.append(len(inds))                                                         # Number of observations used in daily average

    cnt     = np.asarray(cnt)
    dataAvg = np.asarray(dataAvg)
    std     = np.asarray(std)

    outdata['dailyAvg'] = dataAvg
    outdata['dates']    = uniqueDays
    outdata['cnt']      = cnt
    outdata['std']      = std

    return outdata


def mnthlyAvg(data, dates, dateAxis=1, meanAxis=0, quad=0):
    ''' Creates monthly averages of specified quantity'''

    #-----------------------------
    # Initialize output dictionary
    #-----------------------------
    outdata = {}
    dataAvg = []
    cnt     = []
    std     = []

    #-----------------------------------------
    # Convert date time input to strictly date
    #-----------------------------------------
    dates_mnthly = np.asarray([dt.date(d.year,d.month,1) for d in dates])

    #-----------------------------
    # Ensure data is a numpy array
    #-----------------------------
    data = np.asarray(data)

    #----------------------------------------
    # Create a list of months to loop through
    #----------------------------------------
    uniqueMnths = list(set(dates_mnthly))          # Find a list of unique months
    uniqueMnths.sort()
    uniqueMnths = np.asarray(uniqueMnths)    

    #---------------------------
    # Loop through unique months
    #---------------------------
    for indDay in uniqueMnths:

        inds = np.where(dates_mnthly == indDay)[0]                                      # Index for values to use as monhtly average
        
        if data.ndim == 1:                                                              # For single dimension array   
            if quad == 1: dataAvg.append( np.sqrt(np.sum(data[inds]**2)) / len(inds) )  # Find monthly average (sqrt(sum(x^2))/N)
            else:         dataAvg.append( np.mean(data[inds]) )                         # Find monthly average (straight mean)
            std.append(np.std(data[inds]))                                              # Find standard deviation
            
        else:                                                                           # For multi-Dimension array
            s           = [slice(None)] * data.ndim
            s[dateAxis] = inds
            tempMat     = data[s]
            if quad == 1: dataAvg.append( np.sqrt(np.sum(tempMat,axis=meanAxis) / len(inds)))
            else:         dataAvg.append( np.mean(tempMat,axis=meanAxis) )
            std.append(np.std(tempMat,axis=meanAxis))                                  # Find standard deviation    

        cnt.append(len(inds))                                                          # Number of observations used in monhtly average

    cnt     = np.asarray(cnt)
    dataAvg = np.asarray(dataAvg)
    std     = np.asarray(std)

    outdata['mnthlyAvg'] = dataAvg
    outdata['dates']     = uniqueMnths
    outdata['cnt']       = cnt
    outdata['std']       = std

    return outdata


def allMnthAvg(data, dates):
    ''' Creates monthly averages of specified quantity'''

    #-----------------------------
    # Initialize output dictionary
    #-----------------------------
    outdata = {}
    dataAvg = []
    cnt     = []
    std     = []
    mnths   = np.array(range(1,13))

    #-----------------------------
    # Ensure data is a numpy array
    #-----------------------------
    data = np.asarray(data)

    #------------------------------
    # Loop through months (Jan-Dec)
    #------------------------------
    monthlist = np.array([d.month for d in dates])   # Create a month list

    for indMnth in mnths:
        inds = np.where(monthlist == indMnth)[0]     # Index for values to use as monhtly average
        dataAvg.append(np.mean(data[inds]))          # Find monhtly average
        cnt.append(len(inds))                        # Number of observations used in monhtly average
        std.append(np.std(data[inds]))               # Find standard deviation

    cnt     = np.asarray(cnt)
    dataAvg = np.asarray(dataAvg)
    std     = np.asarray(std)

    outdata['mnthlyAvg'] = dataAvg
    outdata['month']     = mnths
    outdata['cnt']       = cnt
    outdata['std']       = std

    return outdata


def readParm(fname):
    ''' Function to read parm.output file '''

    #--------------
    # Read all file
    #--------------
    with open(fname, 'r' ) as fopen:
        lines = fopen.readlines()

    params = lines[3].strip().split()
    data   = np.array([[float(x) for x in row.split()[1:]] for row in lines[4:]])

    #-----------------------------------------------------------
    # Create a dictionary where keys are header of parm.out file
    # A list of numpy arrays is created for repeated keys
    #-----------------------------------------------------------
    parm = {}
    for k in set(params):
        inds = [i for i, val in enumerate(params) if val == k]
        parm.setdefault(k,[]).append(data[:,inds])

    #--------------------------------------
    # Un-nest numpy arrays in parm dictionary
    #--------------------------------------
    for k in parm: parm[k] = parm[k][0]   # Check this

    return parm


def wet_to_dry_vmr(f_wet,f_H2O):
    ''' Convert wet VMR to dry VMR '''
    
    #----------------------------------------
    # Convert wet vmr to dry:
    #   --- f_gas(dry)= f_gas(wet)/ (1-f_H2O)
    #----------------------------------------
    f_dry    = f_wet / (1.0 - f_H2O)    
    
    return f_dry


def lyrVMR(lAlt,hAlt,Z,prf,airmass,sclfct):
    ''' Find layer mixing ratio and convert to ppx (based on scale factor sclfct)'''
    
    Zlwr     = (np.abs(Z-lAlt)).argmin()
    Zupr     = (np.abs(Z-hAlt)).argmin()
    part_VMR = np.asarray( np.average(rprf1[Zlwr:Zupr,:], axis=0, weights=Airmass1[Zlwr:Zupr,:] ) ) * sclfct 
    
    return part_VMR

def readCtlF(ctlF):
    ''' Read .ctl file'''
    
    ctl = {}
    lines = tryopen(ctlF)
    
    if lines:
        gas_flg = True
        
        for line in lines:
            line = line.strip()  

            #---------------------------------------------
            # Lines which start with comments and comments
            # embedded within lines
            #---------------------------------------------                
            if line.startswith('#'): continue                # For lines which start with comments
            if '#' in line: line = line.partition('#')[0]    # For comments embedded in lines

            #-------------------
            # Handle empty lines
            #-------------------
            if len(line) == 0: continue

            #--------------------------
            # Populate input dictionary
            #--------------------------
            if '=' in line:
                lhs,_,rhs = line.partition('=')
                lhs       = lhs.strip()
                rhs       = rhs.strip().split()


                ctl[lhs] = [convrtD(val) for val in rhs]
                #for rhs_part in rhs:                          
                    #if 'd' in rhs_part.lower():                               # Test and handle strings containing D (ie 1.0D0)
                        #mant,trsh,expo = rhs_part.lower().partition('d')
                        #try:
                            #rhs_part = float(mant)*10**int(expo)
                        #except ValueError:
                            #pass
                    #else:                                                # Handle strings => number
                        #try:
                            #rhs_part = [float(ind) for ind in rhs_part]
                        #except ValueError:
                            #pass
                    #ctl[lhs] = rhs

            else:                                                        # Handle multiple line assignments
                rhs = line.strip().split()             

                try:
                    rhs = [float(ind) for ind in rhs]
                except ValueError:
                    pass

                ctl[lhs] += rhs          

            #----------------------    
            # Primary Retrieval Gas
            #----------------------
            # Search for primary retrieval gas in gas.column.list or gas.profile.list
            # The first gas listed is considered the primary retrieval gas
            if gas_flg:
                match = re.match(r'\s*gas\.\w+\.list\s*=\s*(\w+)', line)
                if match:
                    PrimaryGas = match.group(1)
                    gas_flg = False

            #----------------   
            # Spectral Region
            #----------------                
            # Find number of bands
            #match = re.match(r'\s*band\s*=\s*(.+)',line)
            #if match:
                #bands = match.group(1).split()
                #bnd_flg = True

            # Find the upper and lower bands for set including all regions    
            #if bnd_flg:
                #for band in bands:
                    #match = re.match(r'\s*band.' + band + '.nu_\w+\s*=\s*(.*)',line)
                    #if match:
                        #nu.append(float(match.group(1)))

    #nu.sort()              # Sort wavenumbers
    #nuUpper = nu[-1]  # Pull off upper wavenumber
    #nuLower = nu[0]   # Pull off lower wavenumber  
    
    if not gas_flg: return (PrimaryGas,ctl)
    else:           return ctl
    

#---------------------------------
# A simple code for finding linear 
# trend with prediciton intervals
#---------------------------------



#-------------------------------------
# Code to do boot strap trend analysis
#-------------------------------------
def fourier_basis(x, degree, half_period):
    """Returns a 2-d array of fourier basis."""
    A = np.ones((x.size, 2 * degree + 1))
    
    for d in range(1, degree + 1):
        A[:, 2*d-1] = np.cos(d * np.pi * x / half_period)
        A[:, 2*d] = np.sin(d * np.pi * x / half_period)
    
    return A


def fit_driftfourier(x, data, weights, degree, half_period=0.5):
    """
    Fit y = f(x - x.min()) to data where f is given by
    fourier series + drift.
    
    Parameters
    ----------
    x : 1-d array
        x-coordinates
    data : 1-d array
        data values
    weights : 1-d array
        weights (>=0)
    degree : int
        degree of fourier series
    half_period : float
        half period
    
    Returns
    -------
    intercept : float
        intercept at x.min()
    slope : float
        slope (drift) for the normalized data
        (x - x.min())
    pfourier : 1-d array
        Fourier series parameters for the
        normalized data
    f_drift : callable
        Can be used to calculate the drift
        given any (non-normalized) x
    f_fourier : callable
        Can be used to calculate fourier series
    f_driftfourier : callable
        Can be used to calculate drift + fourier
    residual_std : float
        estimated standard deviation of residuals
    A : 2-d array
        matrix of "coefficients"
    
    """
    xmin = x.min()
    xnorm = x - xmin
    
    # coefficient matrix
    A = np.ones((x.size, 2 * degree + 2))
    A[:, 1] = xnorm
    A[:, 2:] = fourier_basis(xnorm, degree, half_period)[:, 1:]
    
    # linear weighted least squares
    results = np.linalg.lstsq(A * weights[:, np.newaxis],
                              data * weights)
    
    params    = results[0]
    intercept = params[0]
    slope     = params[1]
    pfourier  = params[2:]
    
    f_drift = lambda t: slope * (t - xmin) + intercept
    f_fourier = lambda t: np.sum(fourier_basis(t - xmin, degree,
                                               half_period)[:, 1:]
                                 * pfourier[np.newaxis, :],
                                 axis=1) + intercept
    f_driftfourier = lambda t: f_drift(t) + f_fourier(t) - intercept
    
    residual_std = np.sqrt(results[1][0] / (x.size - 2 * degree + 2)) 
    
    return (intercept, slope, pfourier,
            f_drift, f_fourier, f_driftfourier,
            residual_std, A)


def cf_driftfourier(x, data, weights, degree,
                    half_period=0.5, nboot=5000,
                    percentiles=(2.5, 50., 97.5)):
    """
    Calculate confidence intervals for the fitted
    parameters from fourier series + drift modelling,
    using bootstrap resampling.
    
    Parameters
    ----------
    nboot : int
        number of bootstrap replicates
    percentiles : sequence of floats
        percentiles of parameter estimate
        distributions to return 
    
    Returns
    -------
    perc : dict
        percentiles for of each parameter
        distribution
    intercept : 1-d array
        intercept estimates from bootstraped
        datasets.
    slope : 1-d array
        slope estimates
    pfourier : 2-d array
        fourier parameters estimates
    
    See Also
    --------
    :func:`fit_driftfourier`
    """
    
    # 1st fit without bootstraping
    results = fit_driftfourier(x, data, weights,
                               degree, half_period)
    f_driftfourier = results[5]
    A = results[7]
    model = f_driftfourier(x)
    residuals = data - model
    
    # generate bootstrap resamples of residuals
    # and new datasets from these resamples
    boot_dataset = np.empty((x.size, nboot))
    for i in range(nboot):
        resample_i = np.floor(np.random.rand(x.size) * x.size).astype(int)
        resample_residuals = residuals[resample_i]
        boot_dataset[:, i] = model + resample_residuals
    
    # fit all bootstrap datasets
    results_boot = np.linalg.lstsq(A * weights[:, np.newaxis],
                                   boot_dataset * weights[:, np.newaxis])
    
    params_boot = results_boot[0]
    
    # compute percentiles
    perc_boot = np.column_stack(np.percentile(params_boot,
                                              percentiles, axis=1))
    
    perc = {'intercept' : perc_boot[0],
            'slope' : perc_boot[1],
            'pfourier' : perc_boot[2:]}
    
    intercept = params_boot[0]
    slope = params_boot[1]
    pfourier = params_boot[2:]
    
    return perc, intercept, slope, pfourier

def readstatlayer(stfile):
    ''' Read the stat layer'''

    stlay = {}
    lines = tryopen(stfile)
    
    if lines:
        
        for line in lines:
            line = line.strip()

            #---------------------------------------------
            # Lines which start with comments and comments
            # embedded within lines
            #---------------------------------------------                
            if line.startswith('#'): continue                # For lines which start with comments
            if '#' in line: line = line.partition('#')[0]    # For comments embedded in lines
            #-------------------
            # Handle empty lines
            #-------------------
            if len(line) == 0: continue

def jd_to_date(jd):
    """
    Convert Julian Day to date.
    
    Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet', 
        4th ed., Duffet-Smith and Zwart, 2011.
    
    Parameters
    ----------
    jd : float
        Julian Day
        
    Returns
    -------
    year : int
        Year as integer. Years preceding 1 A.D. should be 0 or negative.
        The year before 1 A.D. is 0, 10 B.C. is year -9.
        
    month : int
        Month as integer, Jan = 1, Feb. = 2, etc.
    
    day : float
        Day, may contain fractional part.
        
    Examples
    --------
    Convert Julian Day 2446113.75 to year, month, and day.
    
    >>> jd_to_date(2446113.75)
    (1985, 2, 17.25)
    
    """
    jd = jd + 0.5
    
    F, I = math.modf(jd)
    I = int(I)
    
    A = math.trunc((I - 1867216.25)/36524.25)
    
    if I > 2299160:
        B = I + 1 + A - math.trunc(A / 4.)
    else:
        B = I
        
    C = B + 1524
    
    D = math.trunc((C - 122.1) / 365.25)
    
    E = math.trunc(365.25 * D)
    
    G = math.trunc((C - E) / 30.6001)
    
    day = C - E + F - math.trunc(30.6001 * G)
    
    if G < 13.5:
        month = G - 1
    else:
        month = G - 13
        
    if month > 2.5:
        year = D - 4716
    else:
        year = D - 4715
        
    return year, month, day

def days_to_hmsm(days):
    """
    Convert fractional days to hours, minutes, seconds, and microseconds.
    Precision beyond microseconds is rounded to the nearest microsecond.
    
    Parameters
    ----------
    days : float
        A fractional number of days. Must be less than 1.
        
    Returns
    -------
    hour : int
        Hour number.
    
    min : int
        Minute number.
    
    sec : int
        Second number.
    
    micro : int
        Microsecond number.
        
    Raises
    ------
    ValueError
        If `days` is >= 1.
        
    Examples
    --------
    >>> days_to_hmsm(0.1)
    (2, 24, 0, 0)
    
    """
    hours = days * 24.
    hours, hour = math.modf(hours)
    
    mins = hours * 60.
    mins, min = math.modf(mins)
    
    secs = mins * 60.
    secs, sec = math.modf(secs)
    
    micro = round(secs * 1.e6)
    
    return int(hour), int(min), int(sec), int(micro)

def jd_to_datetime(jd, MJD2000=True):
    """
    Convert a Julian Day to an `jdutil.datetime` object.

    if MJD2000=True Computes the UT date/time from JDF/MJD2000
    
    Parameters
    ----------
    jd : float
        Julian day.
        
    Returns
    -------
    dt : `jdutil.datetime` object
        `jdutil.datetime` equivalent of Julian day.
    
    Examples
    --------
    >>> jd_to_datetime(2446113.75)
    datetime(1985, 2, 17, 6, 0)
    
    """
    #1999, 10, 11, 14, 20, 41
    j0        = 2451544.5
    jd        = np.asarray(jd)

    if MJD2000: jd    = jd + j0
    else:       jd    = jd
    
    da    = [jd_to_date(d) for d in jd]
    da    = np.asarray(da)
    
    year  = da[:, 0]
    month = da[:, 1]
    day   = da[:, 2]
   
    frac_days,day = np.modf(day)
    day       = np.asarray(day, dtype=int)

    ti    = [days_to_hmsm(fd) for fd in frac_days]
    ti    = np.asarray(ti)

    hour  = ti[:, 0]
    min   = ti[:, 1]
    sec   = ti[:, 2]

    datestimes = [dt.datetime(int(y), int(month[i]), int(day[i]), int(hour[i]), int(min[i]), int(sec[i])) for i, y in enumerate(year)]
    
    return datestimes

def jdf_2_datetime(jdf, MJD2000=True):
    #----------------------------------------
    #Computes the UT date/time from JDF/MJD2000
    #----------------------------------------
    jdf = np.asarray(jdf)
    j0        =  2451544.50

    if MJD2000: jdhold    = jdf + j0
    else: jdhold=jdf

    jdi       = np.asarray(jdhold, dtype=int)
    df        = jdhold-jdi
    
    #Determine hh, mm, ss, ms
    hh        = (df+0.5)*24.0
    q         = np.where(hh >= 24.0)[0]
    
    if len(q) >= 1:
        hh[q]  = hh[q]-24.0
        jdi[q] = jdi[q] + 1

    t1  =  hh
    hh  =  np.asarray(t1, dtype=int)
    t2  =  (t1-hh)*60.0
    mn  =  np.asarray(t2, dtype=int)
    t3  = (t2-mn)*60.0
    ss  = t3

    #Determine YYYY, MM, DD
    t1=jdi+np.int(68569)
    t2=(np.int(4)*t1)/np.int(146097)
    t1=t1-(np.int(146097)*t2+np.int(3))/np.int(4)
    t3=(np.int(4000)*(t1+np.int(1)))/np.int(1461001)
    t1=t1-(np.int(1461)*t3)/np.int(4) + np.int(31)
    t4=(np.int(80)*t1)/np.int(2447)

    dd=t1-(np.int(2447)*t4)/np.int(80)
    t1=t4/np.int(11)
    mm=t4+np.int(2)-np.int(12)*t1
    yyyy=np.int(100)*(t2-np.int(49))+t3+t1

    mm   =  np.asarray(mm, dtype=int)
    dd   =  np.asarray(dd, dtype=int)
    yyyy =  np.asarray(yyyy, dtype=int)

    datestimes = [dt.datetime(int(y), int(mm[i]), int(dd[i]), int(hh[i]), int(mn[i]), int(ss[i])) for i, y in enumerate(yyyy)]

    return datestimes
    
    

                                                #----------------#
                                                # Define classes #
                                                #----------------#

#------------------------------------------------------------------------------------------------------------------------------    
class _DateRange(object):
    '''
    This is an extension of the datetime module.
    Adds functionality to create a list of days.
    '''
    def __init__(self,iyear,imnth,iday,fyear,fmnth,fday, incr=1):
        self.i_date   = dt.date(iyear,imnth,iday)                                                     # Initial Day
        self.f_date   = dt.date(fyear,fmnth,fday)                                                     # Final Day
        self.dateList =[self.i_date + dt.timedelta(days=i) for i in range(0, self.numDays(), incr)]   # Incremental day list from initial to final day

    def numDays(self):
        '''Counts the number of days between start date and end date'''
        return (self.f_date + dt.timedelta(days=1) - self.i_date).days

    def inRange(self,crntyear,crntmonth,crntday):
        '''Determines if a specified date is within the date ranged initialized'''
        crntdate = dt.date(crntyear,crntmonth,crntday)
        if self.i_date <= crntdate <= self.f_date:
            return True
        else:
            return False

    def nearestDate(self, year, month, day=1, daysList=False):
        ''' Finds the nearest date from a list of days based on a given year, month, and day'''
        testDate = dt.date(year, month, day)
        if not daysList:
            daysList = self.dateList
        return min( daysList, key=lambda x:abs(x-testDate) )

    def yearList(self):
        ''' Gives a list of unique years within DateRange '''
        years = [ singDate.year for singDate in self.dateList]               # Find years for all date entries
        years = list(set(years))                                             # Determine all unique years
        years.sort()
        return years

    def daysInYear(self,year):
        ''' Returns an ordered list of days from DateRange within a specified year '''
        if isinstance(year,int):
            newyears = [inYear for inYear in self.dateList if inYear.year == year]
            return newyears
        else:
            print ('Error!! Year must be type int for daysInYear')
            return False


#------------------------------------------------------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------------------------------------------------------                     
class ReadHDFData():

    def __init__(self, dataDir, locID, primGas='', geomsTmpl='002'):


        self.PrimaryGas = primGas

        self.dataDir    = dataDir
        self.locID      = locID
        self.geoms      = int(geomsTmpl)


        self.HDF     = {}

        
        Vars = {}
        
        Vars.setdefault(self.getDatetimeName(),[])
        Vars.setdefault(self.getLatitudeInstrumentName(),[])
        Vars.setdefault(self.getLongitudeInstrumentName(),[])
        Vars.setdefault(self.getAltitudeInstrumentName(),[])
        Vars.setdefault(self.getSurfacePressureIndependentName(),[])
        Vars.setdefault(self.getSurfaceTemperatureIndependentName(),[])
        Vars.setdefault(self.getAltitudeName(),[])
        Vars.setdefault(self.getAltitudeBoundariesName(),[])
        Vars.setdefault(self.getPressureIndependentName(),[])
        Vars.setdefault(self.getTemperatureIndependentName(),[])
        Vars.setdefault(self.getAngleSolarAzimuthName(),[])
        Vars.setdefault(self.getAngleSolarZenithAstronomicalName(),[])
        Vars.setdefault(self.getIntegrationTimeName(),[])
        Vars.setdefault(primGas.upper()+'.'+self.getColumnAbsorptionSolarName(),[])
        
        Vars.setdefault(primGas.upper()+'.'+self.getColumnAbsorptionSolarAvkName(),[])
        Vars.setdefault(primGas.upper()+'.'+self.getColumnAbsorptionSolarUncertaintyRandomName(),[])
        Vars.setdefault(primGas.upper()+'.'+self.getColumnAbsorptionSolarUncertaintySystematicName(),[])

          
        
        if int(self.geoms) <= 2:
           

            Vars.setdefault(primGas.upper()+'.'+self.getColumnAbsorptionSolarAprioriName(),[])
            Vars.setdefault(self.getH2oMixingRatioAbsorptionSolarName(),[])
            Vars.setdefault(self.getH2oColumnAbsorptionSolarName(),[])   
            Vars.setdefault(primGas.upper()+'.'+self.getMixingRatioAbsorptionSolarName(),[])
            Vars.setdefault(primGas.upper()+'.'+self.getMixingRatioAbsorptionSolarAprioriName(),[])
            Vars.setdefault(primGas.upper()+'.'+self.getMixingRatioAbsorptionSolarAvkName(),[])
            Vars.setdefault(primGas.upper()+'.'+self.getMixingRatioAbsorptionSolarUncertaintyRandomName(),[])
            Vars.setdefault(primGas.upper()+'.'+self.getMixingRatioAbsorptionSolarUncertaintySystematicName(),[])   
            Vars.setdefault(primGas.upper()+'.'+self.getColumnPartialAbsorptionSolarName(),[])
            Vars.setdefault(primGas.upper()+'.'+self.getColumnPartialAbsorptionSolarAprioriName(),[])

        #-------------------------
        # 003
        #-------------------------
        else:
            Vars.setdefault(primGas.upper()+'.'+self.getColumnAprioriName(),[])
            Vars.setdefault(primGas.upper()+'.'+self.getMixingRatioAbsorptionSolarDryName(),[])
            Vars.setdefault(primGas.upper()+'.'+self.getMixingRatioAprioriDryName(),[])
            Vars.setdefault(primGas.upper()+'.'+self.getMixingRatioAbsorptionSolarAvkDryName(),[])
            Vars.setdefault(primGas.upper()+'.'+self.getMixingRatioAbsorptionSolarUncertaintyRandomDryName(),[])
            Vars.setdefault(primGas.upper()+'.'+self.getMixingRatioAbsorptionSolarUncertaintySystematicDryName(),[])
            Vars.setdefault(primGas.upper()+'.'+self.getMixingRatioAprioriDryName(),[])
            Vars.setdefault(self.getH2oMixingRatioVolumeDryAprioriName(),[])
            Vars.setdefault(self.getH2oColumnAprioriName(),[])




        #---------------------------------
        #
        #---------------------------------
        DirFiles = []


        if isinstance(dataDir, list):
            #print('is instance')
            for d in dataDir:
                if not( d.endswith('/') ):
                    d = d + '/'

                DirFiles.append(glob.glob(d + '*.'+primGas.lower()+ '*'+locID+'*.hdf'))
                #DirFiles.append(glob.glob(d + '*'+locID+'*.hdf'))
                if not DirFiles[0]:
                    DirFiles = []
                    DirFiles.append(glob.glob(d + '*'+locID+'*.hdf'))

        else:
            #print('is NOT an instance')

            if not( dataDir.endswith('/') ):
                dataDir = dataDir + '/'

            
            DirFiles.append(glob.glob(dataDir + '*.'+primGas.lower()+ '*'+locID+'*.hdf'))
            if not DirFiles[0]:
                DirFiles = []
                DirFiles.append(glob.glob(dataDir + '*'+locID+'*.hdf'))
        
    
        DirFiles = [item for DirFiles in DirFiles for item in DirFiles]

        DirFiles.sort()
  
        for drs in DirFiles:

            print ('\nReading HDF File: %s' % (drs))

            #--------------------------
            #TEST FOR HDF5 
            #--------------------------
            #file    = h5py.File(drs, 'r')
 
            #for var in Vars.keys():
            #    print var
            #    data = file[var]
            #    self.HDF.setdefault(var,[]).append(data)
            #exit()
            #--------------------------
           
            ckFile(drs)

            hdfid = SD(drs, SDC.READ)
            
            for var in Vars.keys():

                try:
                    #print(var)
                    data        = hdfid.select(var)
                    #units       = data.units
                    units       = data.VAR_UNITS
                    conv        = data.VAR_SI_CONVERSION.strip().split(';')

                    self.HDF.setdefault(var,[]).append(data)
                    self.HDF.setdefault(var+'VAR_SI_CONVERSION',[]).append(conv)
                    self.HDF.setdefault(var+'VAR_UNITS',[]).append(units)
            
                except Exception as errmsg:
                    print (errmsg, ' : ', var)
                    #exit()
        #---------------------------------
        #FLATTENED THE ARRAYS
        #---------------------------------
        for var in Vars.keys():
           try:
               self.HDF[var] = list(itertools.chain.from_iterable(self.HDF[var]))
               self.HDF[var] = np.asarray(self.HDF[var])
           except Exception: continue

        #print '\nVariables in HDF Files: {}'.format(Vars.keys())
        #exit()
        
    def getDatetimeName(self):
        return 'DATETIME'

    def getLatitudeInstrumentName(self):
        return 'LATITUDE.INSTRUMENT'

    def getLongitudeInstrumentName(self):
        return 'LONGITUDE.INSTRUMENT'

    def getAltitudeInstrumentName(self):
        return 'ALTITUDE.INSTRUMENT'

    def getSurfacePressureIndependentName(self):
        return 'SURFACE.PRESSURE_INDEPENDENT'

    def getSurfaceTemperatureIndependentName(self):
        return 'SURFACE.TEMPERATURE_INDEPENDENT'

    def getAltitudeName(self):
        return 'ALTITUDE'

    def getAltitudeBoundariesName(self):
        return 'ALTITUDE.BOUNDARIES'

    def getPressureIndependentName(self):
        return 'PRESSURE_INDEPENDENT'

    def getTemperatureIndependentName(self):
        return 'TEMPERATURE_INDEPENDENT'

    def getMixingRatioAbsorptionSolarName(self):
        return 'MIXING.RATIO.VOLUME_ABSORPTION.SOLAR'

    def getMixingRatioAbsorptionSolarAprioriName(self):
        return 'MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_APRIORI'

    def getMixingRatioAbsorptionSolarAvkName(self):
        return 'MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_AVK'

    def getIntegrationTimeName(self):
        return 'INTEGRATION.TIME'

    def getMixingRatioAbsorptionSolarUncertaintyRandomName(self):
        return 'MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.COVARIANCE'

    def getMixingRatioAbsorptionSolarUncertaintySystematicName(self):
        return 'MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_UNCERTAINTY.SYSTEMATIC.COVARIANCE'

    def getColumnPartialAbsorptionSolarName(self):
        return 'COLUMN.PARTIAL_ABSORPTION.SOLAR'

    def getColumnPartialAbsorptionSolarAprioriName(self):
        return 'COLUMN.PARTIAL_ABSORPTION.SOLAR_APRIORI'

    def getColumnAbsorptionSolarName(selfself):
        return 'COLUMN_ABSORPTION.SOLAR'

    def getColumnAbsorptionSolarAprioriName(self):
        return 'COLUMN_ABSORPTION.SOLAR_APRIORI'

    def getColumnAbsorptionSolarAvkName(self):
        return 'COLUMN_ABSORPTION.SOLAR_AVK'

    def getColumnAbsorptionSolarUncertaintyRandomName(self):
        return 'COLUMN_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD'

    def getColumnAbsorptionSolarUncertaintySystematicName(self):
        return 'COLUMN_ABSORPTION.SOLAR_UNCERTAINTY.SYSTEMATIC.STANDARD'

    def getAngleSolarZenithAstronomicalName(self):
        return 'ANGLE.SOLAR_ZENITH.ASTRONOMICAL'

    def getAngleSolarAzimuthName(self):
        return 'ANGLE.SOLAR_AZIMUTH'

    def getH2oMixingRatioAbsorptionSolarName(self):
        return 'H2O.MIXING.RATIO.VOLUME_ABSORPTION.SOLAR'

    def getH2oColumnAbsorptionSolarName(self):
        return 'H2O.COLUMN_ABSORPTION.SOLAR'

    #--------------------------------
    # 003
    #--------------------------------
    def getMixingRatioAbsorptionSolarDryName(self):
        return 'MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR'

    def getMixingRatioAprioriDryName(self):
        return 'MIXING.RATIO.VOLUME.DRY_APRIORI'

    def getMixingRatioAbsorptionSolarAvkDryName(self):
        return 'MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_AVK'

    def getMixingRatioAbsorptionSolarUncertaintyRandomDryName(self):
        return 'MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.COVARIANCE'

    def getMixingRatioAbsorptionSolarUncertaintySystematicDryName(self):
        return 'MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.SYSTEMATIC.COVARIANCE'

    def getColumnPartialAprioriName(self):
        return 'COLUMN.PARTIAL_APRIORI'

    def getColumnAprioriName(self):
        return 'COLUMN_APRIORI'

    def getDryAirColumnPartialName(self):
        return 'DRY.AIR.COLUMN.PARTIAL_INDEPENDENT'

    def getH2oMixingRatioVolumeDryAprioriName(self):
        return 'H2O.MIXING.RATIO.VOLUME.DRY_APRIORI'

    def getH2oColumnAprioriName(self):
        return 'H2O.COLUMN_APRIORI'

    def getMixingRatioAprioriDrySourceName(self):
        return 'MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE'

    def fltrData(self,gasName, iyear=False, imonth=False, iday=False, fyear=False, fmonth=False, fday=False, minsza=0.0,mxsza=80.0,minTC=1.0E15,maxTC=1.0E16,
                 tcFlg=True,pcFlg=True,szaFlg=False,tcMMFlg=False, dateFlg=False):
        
        #--------------------------------
        # Filtering has not yet been done
        #--------------------------------
        self.inds = []

        #------------
        # Filter Data
        #------------
        nobs = len(np.asarray(self.HDF[self.getDatetimeName()]))
        print ('\nNumber of total observations before filtering = {}'.format(nobs))

        #-----------------------------
        # Find dates out of range
        #-----------------------------
        if dateFlg:

            idate    = dt.date(iyear, imonth, iday)
            fdate    = dt.date(fyear, fmonth, fday)
            #dates     = jdf_2_datetime(self.HDF[self.getDatetimeName()])
            dates    = jd_to_datetime(self.HDF[self.getDatetimeName()])
            dates2   = [dt.date(d.year, d.month, d.day) for d in dates]

            dates2   = np.asarray(dates2)

            indsT1   =  np.where(np.asarray(dates2) < idate)[0]
            indsT2   =  np.where(np.asarray(dates2) > fdate)[0]
            indsT    = np.union1d(indsT1,indsT2)
    
            print ('Total number observations below date {} = {}'.format(idate, len(indsT1)))
            print ('Total number observations above date {} = {}'.format(fdate, len(indsT2)))
            self.inds = np.union1d(indsT, self.inds) 
     
        #-----------------------------
        # Find total column amount < 0
        #-----------------------------
        if tcFlg:
                
            indsT =  np.where(np.asarray(self.HDF[self.PrimaryGas.upper()+'.'+self.getColumnAbsorptionSolarName()]) <= 0.0)[0]
            print ('Total number observations found with negative total column amount = {}'.format(len(indsT)))
            self.inds = np.union1d(indsT, self.inds)
        
        #---------------------------------------------
        # Find total column amount < minTC and > maxTC
        #---------------------------------------------
        if tcMMFlg:
       
            indsT1 = np.where(np.asarray(self.HDF[self.PrimaryGas.upper()+'.'+self.getColumnAbsorptionSolarName()]) < minTC)[0]
            indsT2 = np.where(np.asarray(self.HDF[self.PrimaryGas.upper()+'.'+self.getColumnAbsorptionSolarName()]) > maxTC)[0]
            indsT  = np.union1d(indsT1,indsT2)
            print ("Total number of observations found with total column < minTotalColumn = {}".format(len(indsT1)))
            print ("Total number of observations found with total column > maxTotalColumn = {}".format(len(indsT2)))
            self.inds = np.union1d(indsT, self.inds)        
                     
        #-----------------------------------
        # Find any partial column amount < 0
        #-----------------------------------
        if pcFlg:
      
            rprf_neg = np.asarray(self.HDF[self.PrimaryGas.upper()+'.'+self.getMixingRatioAbsorptionSolarName()]) <= 0.0
            indsT = np.where( np.sum(rprf_neg,axis=1) > 0 )[0]
            print ('Total number observations found with negative partial column = {}'.format(len(indsT)))
            self.inds = np.union1d(indsT, self.inds)
            
        #-------------------------------------
        # Find observations with SZA > max SZA
        #-------------------------------------
        if szaFlg:
  
            sza_inds1 = np.where(self.HDF[self.getAngleSolarZenithAstronomicalName()] > mxsza)[0]
            sza_inds2 = np.where(self.HDF[self.getAngleSolarZenithAstronomicalName()] < minsza)[0]
            sza_inds  = np.union1d(sza_inds1, sza_inds2)
            print ('Total number of observations with SZA greater than {0:} = {1:}'.format(mxsza,len(sza_inds1)))
            print ('Total number of observations with SZA less than    {0:} = {1:}'.format(minsza,len(sza_inds2)))
            self.inds = np.union1d(sza_inds,self.inds)

    
        self.inds = np.array(self.inds, dtype=int)

        print ('Total number of observations filtered = {}'.format(len(self.inds)))
        
        self.fltrFlg = True
        
        if nobs == len(self.inds):
            print ('!!!! All observations have been filtered....')
            self.empty = True
            return False
        else: self.empty = False
     


class PlotHDF(ReadHDFData):

    def __init__(self,dataDir, locID, gasName, saveFlg=False, outFname='', geomsTmpl='002'):
       
        primGas = gasName
        #------------------------------------------------------------
        # If outFname is specified, plots will be saved to this file,
        # otherwise plots will be displayed to screen
        #------------------------------------------------------------
        if saveFlg:  self.pdfsav = PdfPages(outFname)
        else:        self.pdfsav = False

        self.dataDir = dataDir

        #---------------
        # ReadOutputData
        #---------------
        ReadHDFData.__init__(self,dataDir,locID, primGas, geomsTmpl=geomsTmpl)   
       
        
    def closeFig(self):
        self.pdfsav.close()

    


    def PltHDFSet(self,fltr=False, iyear=False, imonth=False, iday=False, fyear=False, fmonth=False, fday=False, minSZA=0.0,maxSZA=90.0,minDOF=1.0,minTC=0,maxTC=1.0E25,dofFlg=False,tcFlg=True,
               pcFlg=True,sclfct=1.0,sclname='ppv',szaFlg=False,errFlg=False,tcMMFlg=False, dateFlg=False):
        ''' Plot retrieved profiles '''
        
        
        #----------------------------------------
        #DEFINE VARIABLES
        #----------------------------------------
        #try:
        datesJD2K    = self.HDF[self.getDatetimeName()]
        ##dates        = jdf_2_datetime(datesJD2K)  # python 2.7 only
        dates        = jd_to_datetime(datesJD2K)    # python 2.7 and 3
        alt          = self.HDF[self.getAltitudeName()]
        sza          = self.HDF[self.getAngleSolarZenithAstronomicalName()]
        if self.geoms <= 2:
            conv         = self.HDF[self.PrimaryGas.upper()+'.'+self.getMixingRatioAbsorptionSolarName()+'VAR_SI_CONVERSION']            
            rPrf         = self.HDF[self.PrimaryGas.upper()+'.'+self.getMixingRatioAbsorptionSolarName()]*float(conv[0][1])*sclfct
            aprPrf       = self.HDF[self.PrimaryGas.upper()+'.'+self.getMixingRatioAbsorptionSolarAprioriName()]*float(conv[0][1])*sclfct
            avkVMR       = self.HDF[self.PrimaryGas.upper()+'.'+self.getMixingRatioAbsorptionSolarAvkName()]
        
        else:
            conv         = self.HDF[self.PrimaryGas.upper()+'.'+self.getMixingRatioAbsorptionSolarDryName()+'VAR_SI_CONVERSION']            
            rPrf         = self.HDF[self.PrimaryGas.upper()+'.'+self.getMixingRatioAbsorptionSolarDryName()]*float(conv[0][1])*sclfct
            aprPrf       = self.HDF[self.PrimaryGas.upper()+'.'+self.getMixingRatioAprioriDryName()]*float(conv[0][1])*sclfct
            avkVMR       = self.HDF[self.PrimaryGas.upper()+'.'+self.getMixingRatioAbsorptionSolarAvkDryName()]
        

        totClmn      = self.HDF[self.PrimaryGas.upper()+'.'+self.getColumnAbsorptionSolarName()]
        #convTC       = self.HDF[self.PrimaryGas.upper()+'.'+self.getColumnAbsorptionSolarName()+'VAR_UNITS']
          
        

        lat          = self.HDF[self.getLatitudeInstrumentName()]
        lon          = self.HDF[self.getLongitudeInstrumentName()]
        altinstr     = self.HDF[self.getAltitudeInstrumentName()]


        #except Exception as errmsg:
        #    print '\nError: ', errmsg
        

        nobs         = rPrf.shape[0]
        n_layer      = rPrf.shape[1]
        #----------------------------------------
        #SOME GROUPS DEFINE DIFFERENT ALTITUDE
        #----------------------------------------
        if alt.shape[0] == nobs:
            alt          = alt[0, :]
        else:
            alt          = alt[0:n_layer]

        #----------------------------------------
        # print ('\nLatitude        = {}'.format(lat[0]))
        # print ('Longitude         = {}'.format(lon[0]))
        # print ('Altitude of Instr = {}'.format(altinstr[0]))        
        #----------------------------------------

        #----------------------------------------
        #CALCULATE SCALING FACTOR AK
        #----------------------------------------
        try:
            avkSCF  = np.zeros((nobs,n_layer,n_layer))

            for obs in range(0,nobs):
                Iapriori        = np.zeros((n_layer,n_layer))
                IaprioriInv     = np.zeros((n_layer,n_layer))
                np.fill_diagonal(Iapriori, aprPrf[obs])
                np.fill_diagonal(IaprioriInv, 1.0 / (aprPrf[obs]))
                avkSCF[obs,:,:] = np.dot(np.dot(IaprioriInv,np.squeeze(avkVMR[obs,:,:])),Iapriori)

            dofs         = np.asarray([np.trace(aki) for aki in avkSCF])
        except Exception as errmsg:
            print ('\nError: ', errmsg)

        #----------------------------------------
        #OBTAIN ERROR VARIABLES
        #---------------------------------------- 
        if errFlg:                                    # Error info

            tot_rnd      = self.HDF[self.PrimaryGas.upper()+'.'+self.getColumnAbsorptionSolarUncertaintyRandomName()]
            tot_sys      = self.HDF[self.PrimaryGas.upper()+'.'+self.getColumnAbsorptionSolarUncertaintySystematicName()]
            tot_std      = np.sqrt(tot_rnd**2 + tot_sys**2)

            npnts    = np.shape(tot_std)[0]
            nlvls    = np.shape(alt)[0]
            vmr_rnd_err = np.zeros((npnts,nlvls))
            vmr_sys_err  = np.zeros((npnts,nlvls))

            for i in range(npnts):
                if self.geoms <= 2:
                    conv    = self.HDF[self.PrimaryGas.upper()+'.'+self.getMixingRatioAbsorptionSolarUncertaintyRandomName()+'VAR_SI_CONVERSION']  
                    cov_rnd = self.HDF[self.PrimaryGas.upper()+'.'+self.getMixingRatioAbsorptionSolarUncertaintyRandomName()]
                    cov_sys = self.HDF[self.PrimaryGas.upper()+'.'+self.getMixingRatioAbsorptionSolarUncertaintySystematicName()]
                else:
                    conv    = self.HDF[self.PrimaryGas.upper()+'.'+self.getMixingRatioAbsorptionSolarUncertaintyRandomDryName()+'VAR_SI_CONVERSION']  
                    cov_rnd = self.HDF[self.PrimaryGas.upper()+'.'+self.getMixingRatioAbsorptionSolarUncertaintyRandomDryName()]
                    cov_sys = self.HDF[self.PrimaryGas.upper()+'.'+self.getMixingRatioAbsorptionSolarUncertaintySystematicDryName()]

     
                vmr_rnd_err[i,:] = np.diag(cov_rnd[i][:,:])*float(conv[0][1])#*(sclfct**2)
                vmr_sys_err[i,:] = np.diag(cov_sys[i][:,:])*float(conv[0][1])#*(sclfct**2)

            vmr_tot_err  = np.sqrt(vmr_rnd_err + vmr_sys_err) *(sclfct)
            vmr_rnd_err  = np.sqrt(vmr_rnd_err)*(sclfct)
            vmr_sys_err  = np.sqrt(vmr_sys_err)*(sclfct)


        #----------------------------------------
        # Call to filter data
        #----------------------------------------
        if fltr: self.fltrData(self.PrimaryGas, iyear=iyear, imonth=imonth, iday=iday, fyear=fyear, fmonth=fmonth, fday=fday, minsza=minSZA,mxsza=maxSZA,minTC=minTC,maxTC=maxTC,
                               tcFlg=tcFlg,pcFlg=pcFlg,szaFlg=szaFlg,tcMMFlg=tcMMFlg, dateFlg=dateFlg)
        else:    self.inds = np.array([]) 
        
        try:
            dates    = np.delete(dates, self.inds)
            sza      = np.delete(sza, self.inds)
            totClmn  = np.delete(totClmn, self.inds)
            rPrf     = np.delete(rPrf, self.inds, axis=0)
            avkVMR   = np.delete(avkVMR, self.inds, axis=0)
            avkSCF   = np.delete(avkSCF, self.inds, axis=0)

        except Exception as errmsg:
            print ('\nError: ', errmsg)


        if errFlg:
            try:
                vmr_rnd_err  = np.delete(vmr_rnd_err,self.inds,axis=0)
                vmr_sys_err  = np.delete(vmr_sys_err,self.inds,axis=0)  
                vmr_tot_err  = np.delete(vmr_tot_err,self.inds,axis=0)

                tot_rnd      = np.delete(tot_rnd,self.inds)
                tot_sys      = np.delete(tot_sys,self.inds)
                tot_std      = np.delete(tot_std,self.inds)
            except Exception as errmsg:
                print ('\nError: ', errmsg)

        try: 
            prfMean    = np.nanmean(rPrf,axis=0)
            prfSTD     = np.nanstd(rPrf,axis=0)
            avkVMRAv   = np.nanmean(avkVMR, axis=0)
            avkSCFAv   = np.nanmean(avkSCF, axis=0)
            MeanTotCol = np.nanmean(totClmn, axis=0)
            dofs_cs = np.cumsum(np.diag(avkSCFAv)[::-1])[::-1]
        except Exception as errmsg:
            print ('\nError: ', errmsg)

        if errFlg:
            try:
                prfMean_Err = np.nanmean(vmr_tot_err,axis=0)
                prfMean_rnd = np.nanmean(vmr_rnd_err,axis=0)
                prfMean_sys = np.nanmean(vmr_sys_err,axis=0)

                Mean_Err    = np.nanmean(tot_std,axis=0)
                Mean_rnd    = np.nanmean(tot_rnd,axis=0)
                Mean_sys    = np.nanmean(tot_sys,axis=0)

                # print ('\nMean Rnd Total Column Error: {0:.3e} [molec/cm2]'.format(Mean_rnd))
                # print ('Mean Sys Total Column Error: {0:.3e} [molec/cm2]'.format(Mean_sys))
                # print ('Mean Total Column Error:     {0:.3e} [molec/cm2]'.format(Mean_Err))
                # print ('Fraction of total error:     {0:.3e}'.format(Mean_Err/MeanTotCol))

                #print 'Mean Rnd Total Column Error: {0:} [{1:4s}]'.format(prfMean_Err*sclfct, sclname)
            except Exception as errmsg:
                print ('\nError: ', errmsg)

        #----------------------------
        # Determine if multiple years
        #----------------------------
        
        years = [ singDate.year for singDate in dates]      # Find years for all date entries
        if len(list(set(years))) > 1: yrsFlg = True         # Determine all unique years
        else:                         yrsFlg = False

        
        #----------------------------------------------------------------------------------------------------------------------------------------------------------------
        #                                                           PLOTS
        #----------------------------------------------------------------------------------------------------------------------------------------------------------------
        print ('\nPrinting Plots.......\n')
        
        #-------------------------------
        # Single Profile or Mean Profile
        #-------------------------------
        try: 
            fig,(ax1,ax2) = plt.subplots(1,2,sharey=True)
            if int(nobs) > 1:
                ax1.plot(prfMean,alt,color='k',label='Retrieved Profile Mean')
                ax1.fill_betweenx(alt,prfMean-prfSTD,prfMean+prfSTD,alpha=0.5,color='0.75')
                ax2.plot(prfMean,alt,color='k',label='Retrieved Profile Mean')
                ax2.fill_betweenx(alt,prfMean-prfSTD,prfMean+prfSTD,alpha=0.5,color='0.75')   
            else:
                ax1.plot(rPrf[0],alt,color='k',label=self.PrimaryGas.upper())
                ax2.plot(rPrf[0],alt,color='k',label=self.PrimaryGas.upper())
                 
            ax1.plot(np.mean(aprPrf, axis=0),alt,color='r',label='A priori')
            ax2.plot(np.mean(aprPrf, axis=0),alt,color='r',label='A priori')
            
            ax1.grid(True,which='both')
            ax2.grid(True,which='both')
            
            ax1.legend(prop={'size':10})
            ax1.text(-0.1,1.05,'Number of Obs = '+str(rPrf.shape[0]), ha='left',va='center',transform=ax1.transAxes,fontsize=10)
            
            ax1.set_ylabel('Altitude [km]')
            ax1.set_xlabel('VMR ['+sclname+']')
            ax2.set_xlabel('Log Scale VMR ['+sclname+']')
            ax2.set_xscale('log')
            
            ax1.tick_params(axis='x',which='both',labelsize=12)
            ax2.tick_params(axis='x',which='both',labelsize=12)
            plt.suptitle(self.PrimaryGas.upper(), fontsize=16)

            if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
            else:      plt.show(block=False)

        except Exception:
            print ('Error in PrfMean plot: PrfMean Not found')
              
        #------------------
        # Multiple Profiles
        #------------------
        try:
            if int(nobs) > 1:
                clmap = 'jet'
                
                #------------------------------
                # Profiles as a function of SZA
                #------------------------------
                fig,(ax1,ax2)  = plt.subplots(1,2,sharey=True)
                cm             = plt.get_cmap(clmap)
                cNorm          = colors.Normalize( vmin=np.nanmin(sza), vmax=np.nanmax(sza) )
                scalarMap      = mplcm.ScalarMappable( norm=cNorm, cmap=cm )
                
                scalarMap.set_array(sza)

                #ax1.set_color_cycle( [scalarMap.to_rgba(x) for x in sza] )
                #ax2.set_color_cycle( [scalarMap.to_rgba(x) for x in sza] )

                ax1.set_prop_cycle( cycler('color', [scalarMap.to_rgba(x) for x in sza] ) )
                ax2.set_prop_cycle( cycler('color', [scalarMap.to_rgba(x) for x in sza] ) )
                
                for i in range(len(sza)):
                    ax1.plot(rPrf[i,:],alt,linewidth=0.75)
                    ax2.plot(rPrf[i,:],alt,linewidth=0.75)
                    
                ax1.plot(aprPrf[0, :],alt,'k--',linewidth=4,label='A priori')
                ax2.plot(aprPrf[0, :],alt,'k--',linewidth=4,label='A priori')
                
                ax1.set_ylabel('Altitude [km]')
                ax1.set_xlabel('VMR ['+sclname+']')
                ax2.set_xlabel('Log VMR ['+sclname+']')
                
                ax1.grid(True,which='both')
                ax2.grid(True,which='both')
                ax2.set_xscale('log')
                
                cbar = fig.colorbar(scalarMap,orientation='vertical')
                cbar.set_label('SZA')
                
                ax1.legend(prop={'size':10})
                ax2.legend(prop={'size':10})
                
                ax1.tick_params(axis='x',which='both',labelsize=12)
                ax2.tick_params(axis='x',which='both',labelsize=12)  
                plt.suptitle(self.PrimaryGas.upper(), fontsize=16)

                if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                else:           plt.show(block=False)  
                
                #--------------------------------
                #Profiles as a function of Month
                #--------------------------------
                month = np.array([d.month for d in dates])
                fig,(ax1,ax2)  = plt.subplots(1,2,sharey=True)
                cm             = plt.get_cmap(clmap)
                cNorm          = colors.Normalize( vmin=1, vmax=12 )
                scalarMap      = mplcm.ScalarMappable( norm=cNorm, cmap=cm )
                
                scalarMap.set_array(month)

                #ax1.set_color_cycle( [scalarMap.to_rgba(x) for x in month] )
                #ax2.set_color_cycle( [scalarMap.to_rgba(x) for x in month] )

                ax1.set_prop_cycle( cycler('color', [scalarMap.to_rgba(x) for x in month] ) )
                ax2.set_prop_cycle( cycler('color', [scalarMap.to_rgba(x) for x in month] ) )
                
                for i in range(len(month)):
                    ax1.plot(rPrf[i,:],alt,linewidth=0.75)
                    ax2.plot(rPrf[i,:],alt,linewidth=0.75)
                
                ax1.plot(aprPrf[0,:],alt,'k--',linewidth=4,label='A priori')
                ax2.plot(aprPrf[0,:],alt,'k--',linewidth=4,label='A priori')
                
                ax1.set_ylabel('Altitude [km]')
                ax1.set_xlabel('VMR ['+sclname+']')
                ax2.set_xlabel('Log VMR ['+sclname+']')
                
                ax1.grid(True,which='both')
                ax2.grid(True,which='both')
                ax2.set_xscale('log')
                
                cbar = fig.colorbar(scalarMap,orientation='vertical')
                cbar.set_label('Month')
                
                ax1.legend(prop={'size':9})
                #ax2.legend(prop={'size':9})
                
                ax1.tick_params(axis='x',which='both',labelsize=8)
                ax2.tick_params(axis='x',which='both',labelsize=8)  
                plt.suptitle(self.PrimaryGas.upper(), fontsize=16)

                if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                else:           plt.show(block=False)


                #--------------------------------
                #Profiles as a function of Year if multiple years
                #--------------------------------
                if yrsFlg:
                    year           = np.array([d.year for d in dates])
                    fig,(ax1,ax2)  = plt.subplots(1,2,sharey=True)
                    cm             = plt.get_cmap(clmap)
                    cNorm          = colors.Normalize( vmin=np.nanmin(year), vmax=np.nanmax(year) )
                    scalarMap      = mplcm.ScalarMappable( norm=cNorm, cmap=cm )
                    
                    scalarMap.set_array(year)

                    ax1.set_prop_cycle( cycler('color', [scalarMap.to_rgba(x) for x in year] ) )
                    ax2.set_prop_cycle( cycler('color', [scalarMap.to_rgba(x) for x in year] ) )
                    
                    for i in range(len(year)):
                        ax1.plot(rPrf[i,:],alt,linewidth=0.75)
                        ax2.plot(rPrf[i,:],alt,linewidth=0.75)
                    
                    ax1.plot(aprPrf[0,:],alt,'k--',linewidth=4,label='A priori')
                    ax2.plot(aprPrf[0,:],alt,'k--',linewidth=4,label='A priori')
                    
                    ax1.set_ylabel('Altitude [km]')
                    ax1.set_xlabel('VMR ['+sclname+']')
                    ax2.set_xlabel('Log VMR ['+sclname+']')
                    
                    ax1.grid(True,which='both')
                    ax2.grid(True,which='both')
                    ax2.set_xscale('log')
                    
                    cbar = fig.colorbar(scalarMap,orientation='vertical')
                    cbar.set_label('Year')
                    
                    ax1.legend(prop={'size':9})
                    #ax2.legend(prop={'size':9})
                    
                    ax1.tick_params(axis='x',which='both',labelsize=8)
                    ax2.tick_params(axis='x',which='both',labelsize=8)  
                    plt.suptitle(self.PrimaryGas.upper(), fontsize=16)

                    if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                    else:           plt.show(block=False)
           
                #-------------------------------
                #Plot average profiles by month
                #-------------------------------
                months = np.asarray([d.month for d in dates])
                
                for m in list(set(month)):
                    inds     = np.where(months == m)[0]
                    mnthMean = np.nanmean(rPrf[inds,:],axis=0)
                    mnthSTD  = np.nanstd(rPrf[inds,:],axis=0)
                
                    fig,ax1  = plt.subplots()
                    ax1.plot(mnthMean,alt,color='k',label='Monthly Mean Profile, Nobs = '+str(len(inds)))
                    ax1.fill_betweenx(alt,mnthMean-mnthSTD,mnthMean+mnthSTD,alpha=0.5,color='0.75')  
                    ax1.plot(aprPrf[0,:],alt,color='r',label='A Priori Profile')
                    ax1.set_title('Month = '+str(m))
                    ax1.set_ylabel('Altitude [km]')
                    ax1.set_xlabel('VMR ['+sclname+']')    
                    ax1.grid(True,which='both')
                    ax1.legend(prop={'size':9})
                    
                    if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                    else:           plt.show(block=False)

        except Exception:
            print ('Error in Profiles plot')

        if errFlg:
            try:
                #----------------------------------
                # Find mean and max error components
                #----------------------------------
                rand_max = np.max(vmr_rnd_err,axis=0)
                rand_std = np.std(vmr_rnd_err,axis=0)
                
                sys_max  = np.max(vmr_sys_err,axis=0)
                sys_std  = np.std(vmr_sys_err,axis=0)
                
                tot_max  = np.max(vmr_tot_err,axis=0)

                #-------------------------------------------------------
                # Plot mean systematic and random errors on mean profile
                #-------------------------------------------------------
                fig,(ax1,ax2)  = plt.subplots(1,2, sharey=True)
               
                #ax1.plot(prfMean,alt,color='k',label=self.PrimaryGas.upper()+' Retrieved Monthly Mean')
                ax1.errorbar(prfMean,alt,xerr=prfMean_rnd,ecolor='r',label='Total Random Error')
                ax1.fill_betweenx(alt,prfMean-rand_std,prfMean+rand_std,alpha=0.5,color='0.75')  
                ax1.set_title('Random Error')
                    
                ax1.set_ylabel('Altitude [km]')
                ax1.set_xlabel('VMR')      
                ax1.grid(True,which='both')                
                
                #ax2.plot(prfMean,alt,color='k',label=self.PrimaryGas.upper()+' Retrieved Monthly Mean')
                ax2.errorbar(prfMean,alt,xerr=prfMean_sys,ecolor='r',label='Total Systematic Error')
                ax2.fill_betweenx(alt,prfMean-sys_std,prfMean+sys_std,alpha=0.5,color='0.75')      
                ax2.set_title('Systematic Error')

                ax2.set_xlabel('VMR')                                         
                ax2.grid(True,which='both')
                
                if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                else:           plt.show(block=False) 

        
            except Exception:
                print ('Error in Uncertainty Profiles plot')

        #-----------
        # AVK Matrix
        #-----------
        try:

            levels1 = np.arange(np.round(np.min(avkSCFAv),decimals=3),np.round(np.max(avkSCFAv),decimals=3),0.001)
            levels2 = np.arange(np.round(np.min(avkVMRAv),decimals=3),np.round(np.max(avkVMRAv),decimals=3),0.001)
            
            fig,(ax1,ax2) = plt.subplots(1,2,sharey=True)
            cax1          = ax1.contourf(alt,alt,avkSCFAv,levels1, cmap=mplcm.jet)
            cax2          = ax2.contourf(alt,alt,avkVMRAv, levels2, cmap=mplcm.jet)
            
            divider1      = make_axes_locatable(ax1)
            divider2      = make_axes_locatable(ax2)
            cb1           = divider1.append_axes("right",size="10%",pad=0.05)
            cb2           = divider2.append_axes("right",size="10%",pad=0.05)
            cbar1         = plt.colorbar(cax1,cax=cb1)
            cbar2         = plt.colorbar(cax2,cax=cb2)
            cbar1.ax.tick_params(labelsize=8)
            cbar2.ax.tick_params(labelsize=8)
            
            ax1.grid(True)
            ax2.grid(True)
            
            ax1.set_xlabel('Altitude [km]')
            ax1.set_ylabel('Altitude [km]')        
            ax2.set_xlabel('Altitude [km]')
            ax1.yaxis.set_tick_params(which='major',labelsize=8)
            ax2.yaxis.set_tick_params(which='major',labelsize=8)
            ax1.xaxis.set_tick_params(which='major',labelsize=8)
            ax2.xaxis.set_tick_params(which='major',labelsize=8)         
            
            ax1.set_title('Averaging Kernel Matrix (Scale Factor)',fontsize=9)
            ax2.set_title('Averaging Kernel Matrix (VMR)',fontsize=9)
            
            if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
            else:           plt.show(block=False)

        except Exception:
            print ('Error in AKSC and AKVMR plot')


        #-----------
        # AVK Matrix
        #-----------

        try:
            levels2 = np.arange(np.round(np.min(avkVMRAv),decimals=2),np.round(np.max(avkVMRAv),decimals=2),0.005)
            
            fig, ax2      = plt.subplots()
           
            cax2          = ax2.contourf(alt,alt,avkVMRAv, levels2, cmap=mplcm.jet)
            divider2      = make_axes_locatable(ax2)
            cb2           = divider2.append_axes("right",size="7.0%",pad=0.05)
            cbar2         = plt.colorbar(cax2,cax=cb2)
            cbar2.ax.tick_params(labelsize=12)
            ax2.grid(True)
            
            ax2.set_ylabel('Altitude [km]')        
            ax2.set_xlabel('Altitude [km]')
           
            ax2.yaxis.set_tick_params(which='major',labelsize=12)
            ax2.xaxis.set_tick_params(which='major',labelsize=12)         
            
            ax2.set_title('Averaging Kernel Matrix (VMR)')
            
            if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
            else:           plt.show(block=False) 


            # VMR AVK
            fig       = plt.figure()
            gs        = gridspec.GridSpec(1,2,width_ratios=[3,1])
            ax        = plt.subplot(gs[0])
            axb       = plt.subplot(gs[1])
            cm        = plt.get_cmap(clmap)
            cNorm     = colors.Normalize(vmin=np.min(alt), vmax=np.max(alt))
            scalarMap = mplcm.ScalarMappable(norm=cNorm,cmap=clmap)
            scalarMap.set_array(alt)

            #ax.set_color_cycle([scalarMap.to_rgba(x) for x in alt])
            ax.set_prop_cycle( cycler('color', [scalarMap.to_rgba(x) for x in alt] ) )


            
            for i in range(len(alt)):
                ax.plot(avkVMRAv[i,:],alt)
                
            ax.set_ylabel('Altitude [km]')
            ax.set_xlabel('Averaging Kernels')
            ax.grid(True)
            cbar = fig.colorbar(scalarMap,orientation='vertical')
            cbar.set_label('Altitude [km]')
            ax.set_title('Averaging Kernels VMR')
            
            axb.plot(np.sum(avkVMRAv,axis=0),alt,color='k')
            axb.grid(True)
            axb.set_xlabel('Averaging Kernel Area')
            axb.tick_params(axis='x',which='both',labelsize=8)        

            if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
            else:           plt.show(block=False)

        except Exception:
            print ('Error in AKVMR plot')


        #----------------------------
        # Determine if multiple years
        #----------------------------
        years = [ singDate.year for singDate in dates]      # Find years for all date entries
        if len(list(set(years))) > 1: yrsFlg = True         # Determine all unique years
        else:                         yrsFlg = False

        #-----------------
        # Time Series of Total Columns
        #-----------------
        clmap        = 'jet'
        cm           = plt.get_cmap(clmap)    
        yearsLc      = YearLocator()
        monthsAll    = MonthLocator()
        #months       = MonthLocator(bymonth=1,bymonthday=1)
        months       = MonthLocator()
        if yrsFlg: DateFmt      = DateFormatter('%Y')
        else:      DateFmt      = DateFormatter('%m\n%Y') 

        try:     
        
            fig1,ax1 = plt.subplots()
            ax1.plot(dates,totClmn,'k.',markersize=4)
            ax1.grid(True)
            ax1.set_ylabel('Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
            ax1.set_xlabel('Date [MM]')
            ax1.set_title('Time Series of Retrieved Total Column',multialignment='center')
            
            if yrsFlg:
                #plt.xticks(rotation=45)
                ax1.xaxis.set_major_locator(yearsLc)
                ax1.xaxis.set_minor_locator(months)
                #ax1.xaxis.set_minor_formatter(DateFormatter('%m'))
                ax1.xaxis.set_major_formatter(DateFmt) 
                #ax1.xaxis.set_tick_params(which='major', pad=15)  
                ax1.xaxis.set_tick_params(which='major',labelsize=8)
                ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
                fig1.autofmt_xdate()
            else:
                ax1.xaxis.set_major_locator(monthsAll)
                ax1.xaxis.set_major_formatter(DateFmt)
                ax1.set_xlim((dt.date(years[0],1,1), dt.date(years[0],12,31)))
                ax1.xaxis.set_minor_locator(AutoMinorLocator())
                fig1.autofmt_xdate()
            
            if self.pdfsav: self.pdfsav.savefig(fig1,dpi=200)
            else:           plt.show(block=False)

        except Exception:
            print ('Error in Column plots: all ata')

        try:
            #------
            # Time Series of Daily Averaged Total Column
            #------
            dailyVals    = dailyAvg(totClmn,dates,dateAxis=1, meanAxis=0)
            dateYearFrac = toYearFraction(dailyVals['dates'])
            weights      = np.ones_like(dateYearFrac)
            res          = fit_driftfourier(dateYearFrac, dailyVals['dailyAvg'], weights, 2)
            f_drift, f_fourier, f_driftfourier = res[3:6]
            
            fig1,ax1 = plt.subplots()
            ax1.scatter(dailyVals['dates'],dailyVals['dailyAvg'],s=12, facecolor='white',edgecolor='k', label='data')
            #ax1.plot(dailyVals['dates'],f_drift(dateYearFrac),label='Fitted Anual Trend')
            #ax1.plot(dailyVals['dates'],f_driftfourier(dateYearFrac),label='Fitted Anual Trend + intra-annual variability')
            ax1.grid(True)
            ax1.set_ylim([np.min(dailyVals['dailyAvg'])-0.1*np.min(dailyVals['dailyAvg']), np.max(dailyVals['dailyAvg'])+0.15*np.max(dailyVals['dailyAvg'])])
            ax1.set_ylabel('Daily Averaged Total Column\n[molecules cm$^{-2}$]',multialignment='center')
            ax1.set_xlabel('Date [MM]')
            ax1.set_title('Time Series of Daily Averaged Total Column',multialignment='center')
            #ax1.text(0.02,0.94,"Fitted trend -- slope: {0:.3E} ({1:.3f}%)".format(res[1],res[1]/np.mean(dailyVals['dailyAvg'])*100.0),transform=ax1.transAxes)
            #ax1.text(0.02,0.9,"Fitted intercept at xmin: {:.3E}".format(res[0]),transform=ax1.transAxes)
            #ax1.text(0.02,0.86,"STD of residuals: {0:.3E} ({1:.3f}%)".format(res[6],res[6]/np.mean(dailyVals['dailyAvg'])*100.0),transform=ax1.transAxes)   
            
            if yrsFlg:
                #plt.xticks(rotation=45)
                ax1.xaxis.set_major_locator(yearsLc)
                ax1.xaxis.set_minor_locator(months)
                #ax1.xaxis.set_minor_formatter(DateFormatter('%m'))
                ax1.xaxis.set_major_formatter(DateFmt) 
                #ax1.xaxis.set_tick_params(which='major', pad=15)  
                ax1.xaxis.set_tick_params(which='major',labelsize=8)
                ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
                fig1.autofmt_xdate() 
            else:
                ax1.xaxis.set_major_locator(monthsAll)
                ax1.xaxis.set_major_formatter(DateFmt)
                ax1.set_xlim((dt.date(years[0],1,1), dt.date(years[0],12,31)))
                ax1.xaxis.set_minor_locator(AutoMinorLocator())
                fig1.autofmt_xdate()    
                
            if self.pdfsav: self.pdfsav.savefig(fig1,dpi=200)
            else:           plt.show(block=False)

        except Exception:
            print ('Error in Column plots: daily columns')

            #------
            # Time Series of Monthly Averaged Total Column
            #------
        try:
            mnthlyVals = mnthlyAvg(totClmn,dates,dateAxis=1, meanAxis=0)
            dateYearFrac = toYearFraction(mnthlyVals['dates'])
            weights      = np.ones_like(dateYearFrac)
            res          = fit_driftfourier(dateYearFrac, mnthlyVals['mnthlyAvg'], weights, 2)
            f_drift, f_fourier, f_driftfourier = res[3:6]
            
            fig1,ax1 = plt.subplots()
            ax1.scatter(mnthlyVals['dates'],mnthlyVals['mnthlyAvg'],s=12, facecolor='white',edgecolor='k', label='data')
            #ax.scatter(Dates, Anomaly, s=20, facecolor='lightgray', edgecolor='k',alpha=0.85)
            #ax1.plot(mnthlyVals['dates'],f_drift(dateYearFrac),label='Fitted Anual Trend')
            #ax1.plot(mnthlyVals['dates'],f_driftfourier(dateYearFrac),label='Fitted Anual Trend + intra-annual variability')
            ax1.grid(True)
            ax1.set_ylim([np.min(mnthlyVals['mnthlyAvg'])-0.1*np.min(mnthlyVals['mnthlyAvg']), np.max(mnthlyVals['mnthlyAvg'])+0.15*np.max(mnthlyVals['mnthlyAvg'])])
            ax1.set_ylabel('Monthly Averaged Total Column\n[molecules cm$^{-2}$]',multialignment='center')
            ax1.set_xlabel('Date [MM]')
            ax1.set_title('Time Series of Monthly Averaged Total Column',multialignment='center')
            #ax1.text(0.02,0.94,"Fitted trend -- slope: {0:.3E} ({1:.3f}%)".format(res[1],res[1]/np.mean(mnthlyVals['mnthlyAvg'])*100.0),transform=ax1.transAxes)
            #ax1.text(0.02,0.9,"Fitted intercept at xmin: {:.3E}".format(res[0]),transform=ax1.transAxes)
            #ax1.text(0.02,0.86,"STD of residuals: {0:.3E} ({1:.3f}%)".format(res[6],res[6]/np.mean(mnthlyVals['mnthlyAvg'])*100.0),transform=ax1.transAxes)  
            
            if yrsFlg:
                #plt.xticks(rotation=45)
                ax1.xaxis.set_major_locator(yearsLc)
                ax1.xaxis.set_minor_locator(months)
                #ax1.xaxis.set_minor_formatter(DateFormatter('%m'))
                ax1.xaxis.set_major_formatter(DateFmt) 
                #ax1.xaxis.set_tick_params(which='major', pad=15)  
                ax1.xaxis.set_tick_params(which='major',labelsize=8)
                ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
                fig1.autofmt_xdate() 
            else:
                ax1.xaxis.set_major_locator(monthsAll)
                ax1.xaxis.set_major_formatter(DateFmt)
                ax1.set_xlim((dt.date(years[0],1,1), dt.date(years[0],12,31)))
                ax1.xaxis.set_minor_locator(AutoMinorLocator())
                fig1.autofmt_xdate()        
                
            if self.pdfsav: self.pdfsav.savefig(fig1,dpi=200)
            else:           plt.show(block=False)

        except Exception:
            print ('Error in Column plots: Monthly columns')    

        