#----------------------------------------------------------------------------------------
# Name:
#        dataOutClass.py
#
# Purpose:
#       This is a collection of classes and functions used for processing and ploting 
#       sfit output
#
#
# Notes:
#
#
# Version History:
#       Created, October, 2013  Eric Nussbaumer (ebaumer@ucar.edu) & Modified/edited Ivan Ortega
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

import datetime as dt
import time
import math
import sys
import numpy as np
import os
import csv
import itertools
from collections import OrderedDict
import os
from os import listdir
from os.path import isfile, join
import re
from scipy.integrate import simps
import matplotlib.animation as animation
import matplotlib
from cycler import cycler
import matplotlib.dates as md
from matplotlib.dates import DateFormatter, MonthLocator, YearLocator, DayLocator, HourLocator, MinuteLocator
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FormatStrFormatter, MultipleLocator,AutoMinorLocator,ScalarFormatter
from matplotlib.backends.backend_pdf import PdfPages 
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mtick


#----------------------------------------------------------------------------------------
# TO PLOT CLASSIC STYLE (https://matplotlib.org/users/dflt_style_changes.html)
#----------------------------------------------------------------------------------------
matplotlib.style.use('classic')  
#----------------------------------------------------------------------------------------



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
        print 'Input Directory %s does not exist' % (dirName)
        if logFlg: logFlg.error('Directory %s does not exist' % dirName)
        if exitFlg: sys.exit()
        return False
    else:
        return True   

def ckFile(fName,logFlg=False,exitFlg=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print 'File %s does not exist' % (fName)
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
        print errmsg
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
        print "Must specify at least one bound in dbFilterUL"
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
        print 'Data sets must have same size in corrcoef: xData = {}, yData = {}'.format(xData.shape[0],yData.shape[0])
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
                              data * weights, rcond=None)

    
    params = results[0]
    intercept = params[0]
    slope = params[1]
    pfourier = params[2:]
    
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
            print line
            exit()  

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
            print 'Error!! Year must be type int for daysInYear'
            return False


#------------------------------------------------------------------------------------------------------------------------------                     
class ReadOutputData(_DateRange):

    def __init__(self,dataDir,primGas='',ctlF='',iyear=False,imnth=False,iday=False,fyear=False,fmnth=False,fday=False,incr=1):
        
        if (not primGas) and (not ctlF):
            print 'Either primGas or ctlF needs to be specify'
            return False
        
        self.PrimaryGas = primGas            
        self.dirLst     = []
        self.fltrFlg    = False
        
        #------------------------------
        # Set flags to indicate whether 
        # data has been read
        #------------------------------
        self.readPbpFlg               = False
        self.readSpectraFlg           = False
        self.readsummaryFlg           = False
        self.readRefPrfFlg            = False
        self.readStateVecFlg          = False
        self.readErrorFlg             = {}
        self.readErrorFlg['totFlg']   = False
        self.readErrorFlg['sysFlg']   = False
        self.readErrorFlg['randFlg']  = False
        self.readErrorFlg['vmrFlg']   = False
        self.readErrorFlg['avkFlg']   = False
        self.readErrorFlg['KbFlg']    = False
        self.readPrfFlgApr            = {}
        self.readPrfFlgRet            = {}

        #---------------------------------
        # Test if date range given. If so 
        # create a list of directories to 
        # read data from
        #---------------------------------
        if all([iyear,imnth,iday,fyear,fmnth,fday]): 
            
            # check if '/' is included at end of path
            if not( dataDir.endswith('/') ):
                dataDir = dataDir + '/'           
                
            # Check if directory exits
            ckDir(dataDir,exitFlg=True)
            
            self.dirDateTime = []
            self.dirFlg      = True
            
            _DateRange.__init__(self, iyear, imnth, iday, fyear, fmnth, fday, incr=1)
            
            #--------------------------------------------
            # Walk through first level of directories and
            # collect directory names for processing
            #--------------------------------------------
            for drs in os.walk(dataDir).next()[1]: 
                
                #-------------------------------------------
                # Test directory to make sure it is a number
                #-------------------------------------------
                try:    int(drs[0:4])
                except: continue

                if _DateRange.inRange(self, int(drs[0:4]), int(drs[4:6]), int(drs[6:8]) ):
                    #-----------------------------------------------------------------------------------
                    # Some directories have values of 60 for seconds. This throws an error in date time. 
                    # Seconds can only go from 0-59. If this is case reduce seconds by 1. This is a 
                    # temp solution until coadd can be fixed.
                    #-----------------------------------------------------------------------------------
                    if drs[13:] == '60': ss = int(drs[13:]) - 1
                    else:                ss = int(drs[13:]) 
                    self.dirDateTime.append(dt.datetime(int(drs[0:4]), int(drs[4:6]), int(drs[6:8]), int(drs[9:11]), int(drs[11:13]), ss ) )
                    self.dirLst.append(dataDir+drs+'/')            
            
            #----------------------------------------------------------------------------
            # This is important in keeping all the gathered data in order (i.e. profiles,
            # summary, etc.). The sorted directory is carried through and dates are
            # collected in the summary and the profile gather
            #----------------------------------------------------------------------------
            self.dirLst.sort()
            
        #-----------------
        # Single Directory
        #-----------------
        else: 
            self.dirLst = [dataDir]
            self.dirFlg = False
            
        #-----------------------
        # Read ctl File if given
        #-----------------------
        if ctlF: 
            (self.PrimaryGas,self.ctl) = readCtlF(ctlF)     
            #-------------------
            # Construct Gas list
            #-------------------
            self.gasList = []
            if 'gas.profile.list' in self.ctl: self.gasList += self.ctl['gas.profile.list'] 
            if 'gas.column.list' in self.ctl:  self.gasList += self.ctl['gas.column.list']
            if not self.gasList: 
                print 'No gases listed in column or profile list....exiting'
                sys.exit()
                
            self.gasList = filter(None,self.gasList)  # Filter out all empty strings
            self.ngas    = len(self.gasList)   
            
            for gas in self.gasList:
                self.readPrfFlgApr[gas.upper()] = False
                self.readPrfFlgRet[gas.upper()] = False
                
        else:
            self.readPrfFlgApr[self.PrimaryGas] = False
            self.readPrfFlgRet[self.PrimaryGas] = False


    def fltrData(self,gasName,mxrms=1.0,minsza=0.0,mxsza=80.0,minDOF=1.0,maxCHI=2.0,minTC=1.0E15,maxTC=1.0E16,mnthFltr=[1,2,3,4,5,6,7,8,9,10,11,12],
                 rmsFlg=True,tcFlg=True,pcFlg=True,cnvrgFlg=True,szaFlg=False,dofFlg=False,chiFlg=False,tcMinMaxFlg=False,mnthFltFlg=False, h2oFlg=False):
        
        #------------------------------------------
        # If filtering has already been done return
        #------------------------------------------
        if self.fltrFlg: return True

        #--------------------------------
        # Filtering has not yet been done
        #--------------------------------
        self.inds = []

        #------------
        # Filter Data
        #------------
        nobs = len(np.asarray(self.summary[gasName+'_FITRMS']))
        print 'Number of total observations before filtering = {}'.format(nobs)
                
        #---------------------------------
        # Filter based on specified months
        #---------------------------------
        if mnthFltFlg:
            mnthFltr = np.asarray(mnthFltr)
            rminds   = []
            dates    = np.array(self.summary["date"])
            months   = np.array([day.month for day in dates])
            
            for i,month in enumerate(months):
                if month not in mnthFltr: rminds.append(i)
            
            rminds = np.asarray(rminds)
            print ('Total number observations found outside of specified months = {}'.format(len(rminds)))
            self.inds = np.union1d(rminds, self.inds)
        
        #-----------------------------
        # Find total column amount < 0
        #-----------------------------
        if tcFlg:
            if not gasName+'_RetColmn' in self.summary:
                print 'TotColmn values do not exist...exiting..'
                sys.exit()
                
            indsT =  np.where(np.asarray(self.summary[gasName+'_RetColmn']) <= 0.0)[0]
            print ('Total number observations found with negative total column amount = {}'.format(len(indsT)))
            self.inds = np.union1d(indsT, self.inds)
        
        #---------------------------------------------
        # Find total column amount < minTC and > maxTC
        #---------------------------------------------
        if tcMinMaxFlg:
            if not gasName+'_RetColmn' in self.summary:
                print 'TotColmn values do not exist...exiting..'
                sys.exit()
                
            indsT1 = np.where(np.asarray(self.summary[gasName+'_RetColmn']) < minTC)[0]
            indsT2 = np.where(np.asarray(self.summary[gasName+'_RetColmn']) > maxTC)[0]
            indsT  = np.union1d(indsT1,indsT2)
            print "Total number of observations found with total column < minTotalColumn = {}".format(len(indsT1))
            print "Total number of observations found with total column > maxTotalColumn = {}".format(len(indsT2))
            self.inds = np.union1d(indsT, self.inds)        
                
        #-----------------------------
        # Find data with fit RMS > X
        #-----------------------------
        if rmsFlg:
            if not gasName+'_FITRMS' in self.summary:
                print 'RMS values do not exist...exiting..'
                sys.exit()            
                
            indsT = np.where(np.asarray(self.summary[gasName+'_FITRMS']) >= mxrms)[0]
            print ('Total number observations found above max rms value = {}'.format(len(indsT)))
            self.inds = np.union1d(indsT, self.inds)
            
        #------------------------------
        # Find values above max chi_2_y
        #------------------------------
        if chiFlg:
            if not gasName+"_CHI_2_Y" in self.summary:
                print 'CHI_2_Y values do not exist...exiting..'
                sys.exit()            
                
            indsT = np.where(np.asarray(self.summary[gasName+"_CHI_2_Y"]) >= maxCHI)[0]
            print ('Total number observations found above max chi_2_y value = {}'.format(len(indsT)))
            self.inds = np.union1d(indsT, self.inds)            
                    
        #-----------------------------------
        # Find any partial column amount < 0
        #-----------------------------------
        if pcFlg:
            if not gasName in self.rprfs:
                print 'Profile values do not exist...exiting..'
                sys.exit()   
                
            rprf_neg = np.asarray(self.rprfs[gasName]) <= 0
            indsT = np.where( np.sum(rprf_neg,axis=1) > 0 )[0]
            print ('Total number observations found with negative partial column = {}'.format(len(indsT)))
            self.inds = np.union1d(indsT, self.inds)
            
        #-------------------------------------
        # Find observations with SZA > max SZA
        #-------------------------------------
        if szaFlg:
            if 'sza' not in self.pbp:
                print 'SZA not found.....exiting'
                sys.exit()  
            
            sza_inds1 = np.where(self.pbp['sza'] > mxsza)[0]
            sza_inds2 = np.where(self.pbp['sza'] < minsza)[0]
            sza_inds  = np.union1d(sza_inds1, sza_inds2)
            print 'Total number of observations with SZA greater than {0:} = {1:}'.format(mxsza,len(sza_inds1))
            print 'Total number of observations with SZA less than    {0:} = {1:}'.format(minsza,len(sza_inds2))
            self.inds = np.union1d(sza_inds,self.inds)
        
        #--------------------------
        # Filter data based on DOFs
        #--------------------------
        if dofFlg:
            if not gasName+'_DOFS_TRG' in self.summary:
                print 'DOFs values do not exist...exiting..'
                sys.exit() 
                
            indsT = np.where(np.asarray(self.summary[gasName+'_DOFS_TRG']) < minDOF)[0]
            print ('Total number observations found below minimum DOFs = {}'.format(len(indsT)))
            self.inds = np.union1d(indsT, self.inds)

        #--------------------------
        # Filter data based on Negative Water Column
        #--------------------------
        if h2oFlg:
            if not 'H2O_tot_col' in self.rprfs:
                print 'H2O total column do not exist...exiting..'
                sys.exit()

            indsT =  np.where(np.asarray(self.rprfs['H2O_tot_col']) < 0.0)[0]
            print ('Total number observations found with negative water vapor columns = {}'.format(len(indsT)))
            self.inds = np.union1d(indsT, self.inds)
  
        
        #------------------------------------
        # Find retrievals where not converged
        #------------------------------------
        if cnvrgFlg:
            if not gasName+'_CONVERGED' in self.summary:
                print 'Converged values do not exist...exiting..'
                sys.exit()
                
            indsT = np.where( np.asarray(self.summary[gasName+'_CONVERGED']) == 'F')[0]
            print ('Total number observations that did not converge = {}'.format(len(indsT)))    
            self.inds = np.union1d(indsT, self.inds)
    
        self.inds = np.array(self.inds)
        print 'Total number of observations filtered = {}'.format(len(self.inds))
        
        self.fltrFlg = True
        
        if nobs == len(self.inds):
            print '!!!! All observations have been filtered....'
            self.empty = True
            return False
        else: self.empty = False
                
            
    def readStatLyrs(self,fname):
        ''' Reads the station layers file '''
        
        #--------------------
        # Check if file exits
        #--------------------
        ckFile(fname,exitFlg=True)

        #--------------------
        # Read data from file
        #--------------------
        with open(fname,'r') as fopen: lines = fopen.readlines()
        
        #---------------
        # Assign heights
        #---------------
        altTemp  = [float(row.strip().split()[1]) for row in lines[3:] ]
        thckTemp = [float(row.strip().split()[2]) for row in lines[3:] ]
        grthTemp = [float(row.strip().split()[3]) for row in lines[3:] ]
        midTemp  = [float(row.strip().split()[4]) for row in lines[3:] ]
        
        self.alt     = np.asarray(altTemp)
        self.thckAlt = np.asarray(thckTemp)
        self.grthAlt = np.asarray(grthTemp)
        self.midAlt  = np.asarray(midTemp)
        

    def readRefPrf(self,fname=''):
            ''' Reads in reference profile, an input file for sfit4 (raytrace) '''
            self.refPrf = {}
                
            parms = ['ALTITUDE','PRESSURE','TEMPERATURE']
            
            if not fname: fname = 'reference.prf'
            
            #------------------------------------
            # Loop through collected directories
            # self.dirLst has already been sorted
            #------------------------------------
            for indMain,sngDir in enumerate(self.dirLst):
                
                #-----------------------------------------
                # Check for the existance of summary file
                # If does not exist then retrieval was not
                # completed...skip 
                #-----------------------------------------
                if not os.path.isfile(sngDir + 'summary'): continue 
    
                try:
                    with open(sngDir + fname,'r') as fopen: lines = fopen.readlines()
                                    
                    #----------------------------------------
                    # Get Altitude, Pressure, and Temperature
                    # from reference.prf file
                    #----------------------------------------
                    nlyrs  = int(lines[0].strip().split()[1])
                    nlines = int(np.ceil(nlyrs/5.0))
                    
                    for ind,line in enumerate(lines):
                        if any(p in line for p in parms):
                            val = [x for x in parms if x in line][0]
                            self.refPrf.setdefault(val,[]).append([float(x[:-1]) for row in lines[ind+1:ind+nlines+1] for x in row.strip().split()])

                except Exception as errmsg:
                    print errmsg
                    continue
    
            self.readRefPrfFlg = True
            
            #------------------------
            # Convert to numpy arrays
            # and sort based on date
            #------------------------
            for k in self.refPrf:
                self.refPrf[k] = np.asarray(self.refPrf[k])

    def readsummary(self,fname=''):
            ''' Reads in summary data from SFIT output '''
            self.summary = {}
                
            if not fname: fname = 'summary'
            
            #-----------------------------------
            # Loop through collected directories
            #-----------------------------------
            for sngDir in self.dirLst:
    
                try:
                    with open(sngDir + fname,'r') as fopen: lines = fopen.readlines()
    
                    #--------------------------------
                    # Get retrieved column amount for 
                    # each gas retrieved
                    #--------------------------------
                    ind1       = [ind for ind,line in enumerate(lines) if 'IRET' in line][0]
                    ngas       = int(lines[ind1-1].strip())
                    indGasName = lines[ind1].strip().split().index('GAS_NAME')
                    indRETCOL  = lines[ind1].strip().split().index('RET_COLUMN')
                    indAPRCOL  = lines[ind1].strip().split().index('APR_COLUMN')

    
                    for i in range(ind1+1,ind1+ngas+1):
                        gasname = lines[i].strip().split()[indGasName]
                        self.summary.setdefault(gasname.upper()+'_RetColmn',[]).append(float(lines[i].strip().split()[indRETCOL]))
                        self.summary.setdefault(gasname.upper()+'_AprColmn',[]).append(float(lines[i].strip().split()[indAPRCOL]))

    
                    #---------------------------------------------------------
                    # Get NPTSB, FOVDIA, and INIT_SNR
                    # Currently set up to read SNR from summary file where the
                    # summary file format has INIT_SNR on the line below IBAND 
                    #---------------------------------------------------------
                    ind2     = [ind for ind,line in enumerate(lines) if 'IBAND' in line][0]  
                    self.nbands = int(lines[ind2-1].strip().split()[0])
                    indNPTSB = lines[ind2].strip().split().index('NPTSB')
                    indFOV   = lines[ind2].strip().split().index('FOVDIA')
                    indSNR   = lines[ind2].strip().split().index('INIT_SNR') - 9         # Subtract 9 because INIT_SNR is on seperate line therefore must re-adjust index
                    #indFitSNR= lines[ind2].strip().split().index('FIT_SNR') - 9          # Subtract 9 because INIT_SNR is on seperate line therefore must re-adjust index
                    indFitSNR= lines[ind2].strip().split().index('MEAN_SNR') - 9          # Subtract 9 because INIT_SNR is on seperate line therefore must re-adjust index
                    lend     = [ind for ind,line in enumerate(lines) if 'FITRMS' in line][0] - 1


                    for lnum in range(ind2+1,lend,2):
                        band = lines[lnum].strip().split()[0] # Get band number
                        self.summary.setdefault('nptsb_'+band,[]).append(  float( lines[lnum].strip().split()[indNPTSB] ) )
                        self.summary.setdefault('FOVDIA_'+band,[]).append( float( lines[lnum].strip().split()[indFOV]   ) )
                        self.summary.setdefault('SNR_'+band,[]).append(    float( lines[lnum+1].strip().split()[indSNR] ) )       # Add 1 to line number because INIT_SNR exists on next line
                        self.summary.setdefault('FIT_SNR_'+band,[]).append(float( lines[lnum+1].strip().split()[indFitSNR] ) )    # Add 1 to line number because FIT_SNR exists on next line
                    
                    #----------------------------------------------------------------
                    # Get fit rms, chi_y^2, degrees of freedom target, converged flag
                    #----------------------------------------------------------------
                    ind2       = [ind for ind,line in enumerate(lines) if 'FITRMS' in line][0]
                   
                    indRMS     = lines[ind2].strip().split().index('FITRMS')
                    indCHIY2   = lines[ind2].strip().split().index('CHI_2_Y')
                    indDOFtrgt = lines[ind2].strip().split().index('DOFS_TRG')
                    indCNVRG   = lines[ind2].strip().split().index('CONVERGED')
    
                    self.summary.setdefault(self.PrimaryGas.upper()+'_FITRMS'   ,[]).append( float( lines[ind2+1].strip().split()[indRMS]     ) )
                    self.summary.setdefault(self.PrimaryGas.upper()+'_CHI_2_Y'  ,[]).append( float( lines[ind2+1].strip().split()[indCHIY2]   ) )
                    self.summary.setdefault(self.PrimaryGas.upper()+'_DOFS_TRG' ,[]).append( float( lines[ind2+1].strip().split()[indDOFtrgt] ) )
                    self.summary.setdefault(self.PrimaryGas.upper()+'_CONVERGED',[]).append(        lines[ind2+1].strip().split()[indCNVRG]     )
                                         
                    if self.dirFlg: 
                        dirname = os.path.basename(os.path.normpath(sngDir)) 
                        self.summary.setdefault('date',[]).append( dt.datetime(int(dirname[0:4]), int(dirname[4:6]), int(dirname[6:8]), 
                                                                               int(dirname[9:11]), int(dirname[11:13]), int(dirname[13:])))

                except Exception as errmsg:
                    print errmsg
                    continue
    
            self.readsummaryFlg = True
            #------------------------
            # Convert to numpy arrays
            # and sort based on date
            #------------------------
            for k in self.summary:
                self.summary[k] = np.asarray(self.summary[k])
    
            if self.dirFlg: self.summary = sortDict(self.summary, 'date')
            else:           return self.summary


            
            
    def readprfs(self,rtrvGasList,fname='',retapFlg=1):
        ''' Reads in retrieved profile data from SFIT output. Profiles are given as columns. Each row corresponds to
                to an altitude layer [nLayers,nObservations]
                retapFlg determines whether retrieved profiles (=1) or a priori profiles (=0) are read'''
        self.deflt = {}

        #retrvdAll   = ['Z','ZBAR','TEMPERATURE','PRESSURE','AIRMASS', 'H2O']   # These profiles will always be read
        #if rtrvGasList[0].upper() == 'H2O': retrvdAll   = ['Z','ZBAR','TEMPERATURE','PRESSURE','AIRMASS']   # These profiles will always be read
        #else: retrvdAll   = ['Z','ZBAR','TEMPERATURE','PRESSURE','AIRMASS', 'H2O']

        if "H2O" in rtrvGasList: retrvdAll = ['Z','ZBAR','TEMPERATURE','PRESSURE','AIRMASS']
        else: retrvdAll   = ['Z','ZBAR','TEMPERATURE','PRESSURE','AIRMASS', 'H2O']

        if not fname: 
            if   retapFlg == 1: fname = 'rprfs.table'
            elif retapFlg == 0: fname = 'aprfs.table'        


        #--------------------------------------
        # Add user specified retrieved gas list 
        # to standard retrievals
        #--------------------------------------
        # orginalRtrvGasList = rtrvGasList
        # rtrvGasList = [g.upper() for g in rtrvGasList if g.upper() != 'H2O']   # Remove water from gas list since this read by default
        
        retrvdAll.extend(rtrvGasList)

        #-----------------------------------
        # Loop through collected directories
        #-----------------------------------
        for sngDir in self.dirLst:       
            
            try:
                with open(sngDir + fname,'r') as fopen:
                    
                    defltLines = fopen.readlines()        
    
                    #--------------------------------
                    # Get Names of profiles retrieved
                    #--------------------------------
                    defltParm = defltLines[3].strip().split()
    
                    #----------------------------------------
                    # Loop through retrieved profiles to read
                    #----------------------------------------

                    for rtrvdSing in retrvdAll:
                        
                        self.deflt.setdefault(rtrvdSing,[]).append([ np.float_(row.strip().split()[defltParm.index(rtrvdSing.upper())]) for row in defltLines[4:] ] )

    
                    #-------------------------------
                    # Get date and time of retrieval
                    #-------------------------------
                    if self.dirFlg: 
                        dirname = os.path.basename(os.path.normpath(sngDir)) 
                        self.deflt.setdefault('date',[]).append( dt.datetime(int(dirname[0:4]), int(dirname[4:6]), int(dirname[6:8]), 
                                                                             int(dirname[9:11]), int(dirname[11:13]), int(dirname[13:])))

            except Exception as errmsg:
                print errmsg
                continue                            

        #----------------------------
        # Test if Dictionary is empty
        #----------------------------
        if not self.deflt: 
            print 'No Profiles exist...exiting'
            self.empty = True
            return  #sys.exit()
        else: self.empty = False
        
        #-----------------------
        # Convert to numpy array 
        #-----------------------
        for rtrvdSing in retrvdAll:
            #self.deflt[rtrvdSing] = np.transpose( np.asarray( self.deflt[rtrvdSing] ) )
            self.deflt[rtrvdSing] = np.asarray( self.deflt[rtrvdSing] )
  
        if self.dirFlg: self.deflt['date'] = np.asarray( self.deflt['date'] )
  
        #--------------------------------------------------------
        # If retrieved profiles is a gas, get total column amount
        #--------------------------------------------------------
        for i, gas in enumerate(rtrvGasList):

            self.deflt[gas+'_tot_col'] = np.sum(self.deflt[gas] * self.deflt['AIRMASS'], axis=1)

           
        #-------------------------------------------
        # Assign to aprfs or rprfs according to flag
        #-------------------------------------------
        if retapFlg == 1: 
            try:
                self.rprfs
                gen = (g for g in retrvdAll if g not in self.rprfs)
                for g in gen: self.rprfs[g] = self.deflt[g]
                
            except: self.rprfs = self.deflt
            for gas in retrvdAll: self.readPrfFlgRet[gas.upper()] = True
            
        elif retapFlg == 0: 
            try:
                self.aprfs
                gen = (g for g in retrvdAll if g not in self.aprfs)
                for g in gen: self.aprfs[g] = self.deflt[g]
                
            except: self.aprfs = self.deflt
            for gas in retrvdAll: self.readPrfFlgApr[gas.upper()] = True
            
        if self.dirFlg: del self.deflt
        else:           return self.deflt        
             
    
    def readStateVec(self,fname=""):
        ''' Read retrieved parameters in state vector (not includinng profiles)'''
        
        if not fname: fname = "statevec"
        self.statevec = {}
        
        #-----------------------------------
        # Loop through collected directories
        #-----------------------------------
        for sngDir in self.dirLst:
    
            try:
                with open(sngDir + fname,'r') as fopen: lines = fopen.readlines()
        
                #--------------------------------------------------
                # Find location of non profile retrieved parameters
                # These are burried near the end of the file
                #--------------------------------------------------
                # Determine number of layers
                #---------------------------
                nlyrs  = int(lines[1].strip().split()[0])
                nlines = int(np.ceil(nlyrs/5.0))
                
                #------------------------------------
                # Determine number of retrieved gases
                #------------------------------------
                nskip = nlines*3+6
                ngas  = int(lines[nskip].strip().split()[0])
                
                #--------------------------------------------------------
                # Finally find number of non profile retrieved parameters
                #--------------------------------------------------------
                nskip += 2*ngas*(3+nlines) + 2
                nparms = int(lines[nskip].strip().split()[0])
                
                #----------------------------------------
                # Get retrieved parameters (not a priori)
                #----------------------------------------
                nlines = int(np.ceil(nparms/5.0))
                parms = []
                vals  = []
                
                for lineNum in range(0,nlines):
                    parms.extend(lines[nskip+lineNum+1].strip().split())
                    skipVal = nskip + lineNum + nlines*3 - 1
                    vals.extend(lines[skipVal].strip().split())
                    
                vals = [float(val) for val in vals]
    
                for key,val in zip(*(parms,vals)):
                    self.statevec.setdefault(key,[]).append(val)
                    
            except Exception as errmsg:
                print errmsg
                continue            
    
        #------------------------
        # Convert to numpy arrays
        # and sort based on date
        #------------------------
        for k in self.statevec:
            self.statevec[k] = np.asarray(self.statevec[k])    
            
        self.readStateVecFlg = True
   
    
    def readError(self,totFlg=True,sysFlg=False,randFlg=False,vmrFlg=False,avkFlg=False,KbFlg=False):
        ''' Reads in error analysis data from Layer1 output '''
        self.error   = {}
        self.Kb      = {}
        self.sysErr  = {}
        self.randErr = {}
        self.sysErrDiag  = {}
        self.randErrDiag = {}
            
        #-----------------------------------
        # Loop through collected directories
        #-----------------------------------
        for sngDir in self.dirLst:          
            #-------------------------------
            # Read error summary information
            #-------------------------------
            try:
                with open(sngDir + 'Errorsummary.output','r') as fopen:
                    errSumLines = fopen.readlines()        

                #---------------------------------------------------------
                # Loop through summary information. Does not include units
                #---------------------------------------------------------
                for line in errSumLines[3:]:
                    header = line.strip().split('=')[0].strip()
                    val    = float(line.strip().split('=')[1].split()[0])
                    self.error.setdefault(header,[]).append( val )

                #-------------------------------
                # Get date and time of retrieval
                #-------------------------------
                if self.dirFlg: 
                    dirname = os.path.basename(os.path.normpath(sngDir)) 
                    self.error.setdefault('date',[]).append( dt.datetime(int(dirname[0:4]), int(dirname[4:6]), int(dirname[6:8]), 
                                                                         int(dirname[9:11]), int(dirname[11:13]), int(dirname[13:])))

            except Exception as errmsg:
                print errmsg
                continue                            

            #-------------------------
            # Read in averaging kernel
            #-------------------------
            if avkFlg:
                try:
                    with open(sngDir + 'avk.output','r') as fopen:
                        lines = fopen.readlines() 

                    for ind,line in enumerate(lines):
                        if 'nrows' in line: nrows = int(lines[2].strip().split('=')[1])

                        elif line.strip() == 'AVK_scale_factor':
                            totRand = np.array( [ [ float(x) for x in line.strip().split() ] for line in lines[ind+1:ind+1+nrows] ] )
                            self.error.setdefault('AVK_scale_factor',[]).append(totRand)      
                        elif line.strip() == 'AVK_VMR':
                            totRand = np.array( [ [ float(x) for x in line.strip().split() ] for line in lines[ind+1:ind+1+nrows] ] )
                            self.error.setdefault('AVK_vmr',[]).append(totRand)                            

                except Exception as errmsg:
                    print errmsg
                    continue                  
                
            #------------------
            # Read in Kb matrix
            #------------------
            if KbFlg:                
                #------------------
                # Read in Kb matrix
                #------------------    
                lines    = tryopen(sngDir + 'kb.output')
                Kb_param = lines[2].strip().split()
                
                #---------------------------------------------------------------
                # Some parameter names in the Kb file are appended by either 
                # micro-window or gas name. If they are appended by micro-window
                # strip this and just keep parameter name so that we may group
                # the micro-windows under one key
                #---------------------------------------------------------------
                for ind,val in enumerate(Kb_param):
                    if len(val.split('_')) == 2:
                        pname,appnd = val.split('_')
                        try:               int(appnd); val = pname
                        except ValueError: pass
                    Kb_param[ind] = val
            
                Kb_unsrt = np.array([[float(x) for x in row.split()] for row in lines[3:]])
            
                #----------------------------------
                # Create a dictionary of Kb columns
                # A list of numpy arrays is created
                # for repeated keys
                #----------------------------------
                for k in set(Kb_param):
                    inds = [i for i, val in enumerate(Kb_param) if val == k]
                    self.Kb.setdefault(k,[]).append(Kb_unsrt[:,inds])
            
                #--------------------------------------
                # Un-nest numpy arrays in Kb dictionary
                #--------------------------------------
                #for k in self.Kb: self.Kb[k] = self.Kb[k][0]   # Check this                

            #------------------------
            # Read in error matricies
            #------------------------
            # Total Error: 2 matricies (systematic and random)
            if totFlg:
                try:
                    with open(sngDir + 'Stotal.output','r') as fopen:
                        lines = fopen.readlines()        

                    #-------------------------------------------------
                    # Read total Systematic and Random Error Matricies
                    #-------------------------------------------------
                    for ind,line in enumerate(lines):
                        if 'nrows' in line: nrows = int(lines[2].strip().split('=')[1])

                        elif line.strip() == 'Random':
                            totRand = np.array( [ [ float(x) for x in line.strip().split() ] for line in lines[ind+1:ind+1+nrows] ] )
                            self.error.setdefault('Total_Random_Error',[]).append(totRand)

                        elif line.strip() == 'Systematic':
                            totSys = np.array( [ [ float(x) for x in line.strip().split() ] for line in lines[ind+1:ind+1+nrows] ] )
                            self.error.setdefault('Total_Systematic_Error',[]).append(totSys)                            

                except Exception as errmsg:
                    print errmsg
                    continue                    

                #--------------------------------------------
                # If VMR flag is set to true, read vmr values
                #--------------------------------------------
                if vmrFlg:
                    try:
                        with open(sngDir + 'Stotal.vmr.output','r') as fopen:
                            lines = fopen.readlines()        

                        #-------------------------------------------------
                        # Read total Systematic and Random Error Matricies
                        #-------------------------------------------------
                        for ind,line in enumerate(lines):
                            if 'nrows' in line: nrows = int(lines[2].strip().split('=')[1])

                            elif line.strip() == 'Random':
                                totRand = np.array( [ [ float(x) for x in line.strip().split() ] for line in lines[ind+1:ind+1+nrows] ] )
                                self.error.setdefault('Total_Random_Error_VMR',[]).append(totRand)

                            elif line.strip() == 'Systematic':
                                totSys = np.array( [ [ float(x) for x in line.strip().split() ] for line in lines[ind+1:ind+1+nrows] ] )
                                self.error.setdefault('Total_Systematic_Error_VMR',[]).append(totSys)                            

                    except Exception as errmsg:
                        print errmsg
                        continue                    

            # Systematic Error 
            if sysFlg:
                try:
                    with open(sngDir + 'Ssystematic.output','r') as fopen:
                        lines = fopen.readlines()        

                    #--------------------------------------
                    # Read total Systematic Error Matricies
                    #--------------------------------------
                    for ind,line in enumerate(lines):
                        if 'nrows' in line: nrows = int(lines[2].strip().split('=')[1])

                        elif not line.strip().startswith('#') and len(line.strip().split()) == 1:
                            errLbl  = line.strip().split()[0].strip()
                            errmtrx = np.array( [ [ float(x) for x in line.strip().split() ] for line in lines[ind+1:ind+1+nrows] ] )
                            self.sysErr.setdefault(errLbl+'_Systematic_Error',[]).append(errmtrx)
                            self.sysErrDiag.setdefault(errLbl+'_Systematic_Error',[]).append(np.diag(errmtrx))

                        else: continue


                except Exception as errmsg:
                    print errmsg
                    continue                    

                #--------------------------------------------
                # If VMR flag is set to true, read vmr values
                #--------------------------------------------
                if vmrFlg:
                    try:
                        with open(sngDir + 'Ssystematic.vmr.output','r') as fopen:
                            lines = fopen.readlines()        

                        #--------------------------------------------
                        # Read total Systematic Error Matricies (VMR)
                        #--------------------------------------------
                        for ind,line in enumerate(lines):
                            if 'nrows' in line: nrows = int(lines[2].strip().split('=')[1])

                            elif not line.strip().startswith('#') and len(line.strip().split()) == 1:
                                errLbl  = line.strip().split()[0].strip()
                                errmtrx = np.array( [ [ float(x) for x in line.strip().split() ] for line in lines[ind+1:ind+1+nrows] ] )
                                self.sysErr.setdefault(errLbl+'_Systematic_Error_VMR',[]).append(errmtrx)
                                self.sysErrDiag.setdefault(errLbl+'_Systematic_Error_VMR',[]).append(np.diag(errmtrx))
                                
                            else: continue                        

                    except Exception as errmsg:
                        print errmsg
                        continue                  

            # Systematic Error 
            if randFlg:
                try:
                    with open(sngDir + 'Srandom.output','r') as fopen:
                        lines = fopen.readlines()        

                    #--------------------------------------
                    # Read total Systematic Error Matricies
                    #--------------------------------------
                    for ind,line in enumerate(lines):
                        if 'nrows' in line: nrows = int(lines[2].strip().split('=')[1])

                        elif not line.strip().startswith('#') and len(line.strip().split()) == 1:
                            errLbl  = line.strip().split()[0].strip()
                            errmtrx = np.array( [ [ float(x) for x in line.strip().split() ] for line in lines[ind+1:ind+1+nrows] ] )
                            self.randErr.setdefault(errLbl+'_Random_Error',[]).append(errmtrx)
                            self.randErrDiag.setdefault(errLbl+'_Random_Error',[]).append(np.diag(errmtrx))

                        else: continue

                except Exception as errmsg:
                    print errmsg
                    continue                    

                #--------------------------------------------
                # If VMR flag is set to true, read vmr values
                #--------------------------------------------
                if vmrFlg:
                    try:
                        with open(sngDir + 'Srandom.vmr.output','r') as fopen:
                            lines = fopen.readlines()        

                        #--------------------------------------------
                        # Read total Systematic Error Matricies (VMR)
                        #--------------------------------------------
                        for ind,line in enumerate(lines):
                            if 'nrows' in line: nrows = int(lines[2].strip().split('=')[1])

                            elif not line.strip().startswith('#') and len(line.strip().split()) == 1:
                                errLbl  = line.strip().split()[0].strip()
                                errmtrx = np.array( [ [ float(x) for x in line.strip().split() ] for line in lines[ind+1:ind+1+nrows] ] )
                                self.randErr.setdefault(errLbl+'_Random_Error_VMR',[]).append(errmtrx)
                                self.randErrDiag.setdefault(errLbl+'_Random_Error_VMR',[]).append(np.diag(errmtrx))

                            else: continue                        

                    except Exception as errmsg:
                        print errmsg
                        continue                 

        #----------
        # Set flags
        #----------
        if totFlg:  self.readErrorFlg['totFlg']   = True
        if sysFlg:  self.readErrorFlg['sysFlg']   = True
        if randFlg: self.readErrorFlg['randFlg']  = True
        if vmrFlg:  self.readErrorFlg['vmrFlg']   = True
        if avkFlg:  self.readErrorFlg['avkFlg']   = True
        if KbFlg:   self.readErrorFlg['KbFlg']    = True        

        #-----------------------------------
        # Convert date values to numpy array 
        #-----------------------------------
        for k in self.error:
            if k =='date': self.error[k] = np.asarray(self.error[k])        
    

    def readPbp(self,fname=''):
        ''' Reads data from the pbp file'''
        self.pbp = {}

        if not fname: fname = 'pbpfile.out'
        
        #-----------------------------------
        # Loop through collected directories
        #-----------------------------------
        for sngDir in self.dirLst:      
            
            #-------------------------------------
            # Catch error for opening/reading file
            #-------------------------------------    
            try:
                with open(sngDir + fname,'r') as fopen: lines = fopen.readlines()   

            except Exception as errmsg:
                print errmsg
                continue       
            
            #--------------------
            # Get Number of bands
            #--------------------
            #nbands = int(lines[1].strip().split()[1])
            nbands = int(lines[1].strip().split()[0])   #IVAN - Change to read the first number, some retrieval fails for certain windows


            #-------------------------------------------------------
            # Loop through bands. Header of first band is on line[3]
            #-------------------------------------------------------
            lstart = 3
            for i in range(1,nbands+1):
                #--------------------------
                # Read header for each band
                #--------------------------
                # Only take the SZA from first micro-window
                if i == 1: self.pbp.setdefault('sza',[]).append( float(lines[lstart].strip().split()[0])/ 1000.0 )
                # Read the SAA
                if i == 1: self.pbp.setdefault('saa',[]).append( float(lines[lstart-1].strip().split()[3].split(':')[1]))

                nspac = float(lines[lstart].strip().split()[1])
                npnts = int(lines[lstart].strip().split()[2])
                iWN   = float(lines[lstart].strip().split()[3])
                fWN   = float(lines[lstart].strip().split()[4])

                #--------------------------------------------------------------------
                # Determine the number of lines for each band. From lines 363 and 364 
                # of writeout.f90, 12 spectral points are written for each line
                #--------------------------------------------------------------------
                nlines = int( math.ceil( float(lines[lstart].strip().split()[2])/ 12.0) )
                mw     = lines[lstart].strip().split()[6]
                if not 'wavenumber_'+mw in self.pbp: self.pbp.setdefault('wavenumber_'+mw,[]).append(np.linspace(iWN,fWN,num=npnts))
                
                #---------------------------------------------------------------------
                # Read in observed, fitted, and difference spectra for particular band
                #---------------------------------------------------------------------
                self.pbp.setdefault('Obs_'+mw,[]).append([float(x) for row in lines[lstart+1:(lstart+1+nlines*3):3] for x in row.strip().split()[1:] ])
                self.pbp.setdefault('Fitted_'+mw,[]).append([float(x) for row in lines[lstart+2:(lstart+2+nlines*3):3] for x in row.strip().split() ])
                self.pbp.setdefault('Difference_'+mw,[]).append([float(x) for row in lines[lstart+3:(lstart+3+nlines*3):3] for x in row.strip().split() ])
                
                #----------------------------------------
                # Set new line number start for next band
                #----------------------------------------
                lstart += nlines*3+2
                                      
            #-------------------------------
            # Get date and time of retrieval
            #-------------------------------
            if self.dirFlg: 
                dirname = os.path.basename(os.path.normpath(sngDir)) 
                self.pbp.setdefault('date',[]).append( dt.datetime(int(dirname[0:4]), int(dirname[4:6]), int(dirname[6:8]), 
                                                                   int(dirname[9:11]), int(dirname[11:13]), int(dirname[13:])))                        
    
       # if self.dirFlg: self.pbp = sortDict(self.pbp, 'date')

       #--------------------------
       # For NCAR sites - Convert SAA to 0.0- North
       #--------------------------
        for i, az in enumerate(self.pbp['saa']):
           if az >= 180.0:
               self.pbp['saa'][i] = np.abs(360. - az  - 180.)
           elif az < 180.0:
               self.pbp['saa'][i] = 180.0 + az


        
        #------------------------
        # Convert to numpy arrays
        # and sort based on date
        #------------------------
        for k in self.pbp:
            self.pbp[k] = np.asarray(self.pbp[k])    
            
        self.readPbpFlg = True
        
        if not self.dirFlg: return self.pbp
    
    def readSpectra(self,rtrvGasList):
        ''' Reads data from spectral files'''
        self.spc = {}
        
        #-----------------------------------
        # Loop through collected directories
        #-----------------------------------
        for indMain,sngDir in enumerate(self.dirLst):            
        
            #--------------------------------------
            # Read in Spectral file with all gasses
            #--------------------------------------
            fnames = [ sngDir+f for f in listdir(sngDir) if ( isfile(join(sngDir,f)) and f.startswith('spc.all.') ) ]
            
            #-----------------------------------------------------
            # If no files found retrieval probably not successfull
            #-----------------------------------------------------
            if len(fnames) == 0: continue
            
            #----------------------------------
            # Determine number of micro-windows
            #----------------------------------
            if not 'nMW' in vars(): 
                nMW = len(fnames)
                nstr = ['{:02d}'.format(f) for f in range(1,nMW+1)]
            
            self.spc['nMW'] = nMW
            
            #---------------------------
            # Loop through micro-windows
            #---------------------------
            for n in nstr:
                
                nsng = str(int(n))
                #-----------------------------------------
                # Open and read all spec.all.*.final files
                #-----------------------------------------                
                with open(sngDir+'spc.all.'+n+'.01.final','r') as fopen: lines = fopen.readlines()
                
                #----------------------------------------------
                # Create list of micro-window wavenumber points
                #----------------------------------------------
                if not 'MW_'+nsng in self.spc:
                    LWN   = float(lines[1].strip().split()[0])
                    UWN   = float(lines[1].strip().split()[1])
                    spac  = float(lines[1].strip().split()[2])
                    npnts = float(lines[1].strip().split()[3])
                    self.spc['MW_'+nsng] = np.linspace(LWN,UWN,num=npnts)
                    
                #---------------------------
                # Read spectral transmission
                #---------------------------
                self.spc.setdefault('All_' + nsng,[]).append([float(x.strip()) for x in lines[2:] ])
                         
                #-----------------------------------------
                # Open and read all spec.sol.*.final files
                #-----------------------------------------     
                try:
                    with open(sngDir+'spc.sol.'+n+'.01.final','r') as fopen: lines = fopen.readlines()
                    self.spc.setdefault('Solar_'+nsng,[]).append([float(x.strip()) for x in lines[2:] ])   
                    self.solarFlg = True
                except:
                    self.solarFlg = False
              
                #----------------------------------------------
                # Read in Spectral file for all retrieved gases
                #----------------------------------------------
                for gas in rtrvGasList:                
                    try:
                        with open(sngDir+'spc.'+gas.upper()+'.'+n+'.01.final','r') as fopen: lines = fopen.readlines()
                    except Exception: continue  
                        
                    self.spc.setdefault(gas.upper()+'_'+nsng,[]).append([float(x.strip()) for x in lines[2:] ])

            #-------------------------------
            # Get date and time of retrieval
            #-------------------------------
            if self.dirFlg: 
                dirname = os.path.basename(os.path.normpath(sngDir)) 
                self.spc.setdefault('date',[]).append( dt.datetime(int(dirname[0:4]), int(dirname[4:6]), int(dirname[6:8]), 
                                                                  int(dirname[9:11]), int(dirname[11:13]), int(dirname[13:])))          
                
                
        #if self.dirFlg: self.spc = sortDict(self.spc, 'date',excld=['nMW'])
            
        #------------------------
        # Convert to numpy arrays
        # and sort based on date
        #------------------------
        for k in self.spc:
            self.spc[k] = np.asarray(self.spc[k])    
            
        self.readSpectraFlg = True
        
        if not self.dirFlg: return self.spc        

#------------------------------------------------------------------------------------------------------------------------------    
class DbInputFile(_DateRange):
    '''
    This class deals with reading and filtering the spectral database file.
    '''    
    def __init__(self,fname):
        self.dbName      = fname
        self.dbInputs    = {}
        self.dbFltInputs = {}

    def getInputs(self):
        ''' Get db spectral observations and put into a dictionary. We
            Are assuming the first line of db are the keys. Also, assuming
            that the delimiter is a single space. csv reader automatically
            reads everything in as a string. Certain values must be converted
            to floats'''
        with open(self.dbName,'rb') as fname:
            # Currently only reads white space delimited file. Need to make general****
            reader = csv.DictReader(fname,delimiter=' ',skipinitialspace=True)                   # Read csv file
            for row in reader:
                #------------------------------------------------------
                # DictReader will add a None key and value if there are
                # extra spaces at the end of database line.
                #------------------------------------------------------
                if None in row: del row[None]                    

                for col,val in row.iteritems():
                    try:
                        val = float(val)                                                         # Convert string to float
                    except ValueError:
                        pass

                    self.dbInputs.setdefault(col,[]).append(val)                                 # Construct input dictionary                  
                    if '' in self.dbInputs: del self.dbInputs['']                                # Sometimes empty key is created (not sure why). This removes it.

    def dbFilterDate(self,fltDict=False):#=self.dbInputs):
        ''' Filter spectral db dicitonary based on date range class previously established'''
        inds = []

        if not fltDict:
            fltDict = self.dbInputs

        for ind,val in enumerate(fltDict['Date']):
            valstr   = str(int(val))
            datestmp = [int(valstr[0:4]),int(valstr[4:6]),int(valstr[6:])]                       # Convert date to integer
            
            if self.inRange(datestmp[0], datestmp[1], datestmp[2]): inds.append(ind)             # Check if date stamp in spectral db is within range
                
        dbFltInputs = dict((key, [val[i] for i in inds]) for (key, val) in fltDict.iteritems())  # Rebuild filtered dictionary. Syntax compatible with python 2.6   
        #dbFltInputs = {key: [val[i] for i in inds] for key, val in fltDict.iteritems()}         # Rebuild filtered dictionary. Not compatible with python 2.6
        return dbFltInputs

    def dbFindDate(self,singlDate,fltDict=False):
        ''' Grab a specific date and time from dictionary '''

        if not fltDict:
            fltDict = self.dbInputs

        for ind,(date,time) in enumerate(itertools.izip(fltDict['Date'],fltDict['Time'])):
            date = str(int(date))
            HH   = time.strip().split(':')[0]
            MM   = time.strip().split(':')[1]
            SS   = time.strip().split(':')[2]
            #-----------------------------------------------------------------------------------
            # Some directories have values of 60 for seconds. This throws an error in date time. 
            # Seconds can only go from 0-59. If this is case reduce seconds by 1. This is a 
            # temp solution until coadd can be fixed.
            #-----------------------------------------------------------------------------------    
            if SS == '60': SS = '59'

            DBtime = dt.datetime(int(date[0:4]),int(date[4:6]),int(date[6:]),int(HH),int(MM),int(SS))

            if DBtime == singlDate:
                dbFltInputs = dict((key, val[ind] ) for (key, val) in fltDict.iteritems())
                return dbFltInputs

        return False

    def dbFilterNu(self,nuUpper,nuLower,fltDict=False):#=self.dbInputs):
        ''' Filter spectral db dictionary based on wavenumber region derived from ctl files '''
        inds = []

        if not fltDict:
            fltDict = self.dbInputs

        for ind,(val1,val2) in enumerate(itertools.izip(fltDict['LWN'],fltDict['HWN'])):
            if ( nuLower >= val1 and nuUpper <= val2 ):                                          # Check if wavenumber is within range of ctl files
                inds.append(ind)

        dbFltInputs = dict((key, [val[i] for i in inds]) for (key, val) in fltDict.iteritems())   # Rebuild filtered dictionary. Syntax compatible with python 2.6
        #dbFltInputs = {key: [val[i] for i in inds] for key, val in fltDict.iteritems()}         # Rebuild filtered dictionary. Not compatible with python 2.6
        return dbFltInputs

    def dbFilterFltrID(self,fltrID,fltDict=False):
        ''' Filter spectral DB dictionary based on filter ID specification'''
        inds = []

        if not fltDict: fltDict = self.dbInputs

        for ind,val in enumerate(fltDict['Flt']):
            try:
                if str(int(val)) == str(fltrID):
                    inds.append(ind)
            except ValueError:
                if str(val) == str(fltrID):
                    inds.append(ind)                

        dbFltInputs = dict((key, [val[i] for i in inds]) for (key, val) in fltDict.iteritems())   # Rebuild filtered dictionary. Syntax compatible with python 2.6

        return dbFltInputs
    
#------------------------------------------------------------------------------------------------------------------------------

class GatherHDF(ReadOutputData,DbInputFile):
    
    def __init__(self,dataDir,ctlF,spcDBfile,statLyrFile,iyear,imnth,iday,fyear,fmnth,fday,errFlg=True,incr=1):
        primGas = ''

        #-----------------------------------------
        # Check existance of directories and files
        #-----------------------------------------
        ckDir(dataDir, exitFlg=True)
        ckFile(ctlF, exitFlg=True)
        ckFile(spcDBfile, exitFlg=True)
        
        #---------------
        # ReadOutputData
        #---------------
        ReadOutputData.__init__(self,dataDir,primGas,ctlF,iyear,imnth,iday,fyear,fmnth,fday,incr)    

        #------------
        # DbInputFile
        #------------
        DbInputFile.__init__(self,spcDBfile)

        #-----------------------------------------------------------------------------
        # Gather Retrieval output data, filter set, and then find corresponding specDB
        # entries for specDB data
        #-----------------------------------------------------------------------------
        if "H2O" not in self.PrimaryGas:
            self.readprfs([self.PrimaryGas,'H2O'],retapFlg=1)          # Retrieved Profiles
        else:
            self.readprfs([self.PrimaryGas],retapFlg=1)          # Retrieved Profiles

        #self.readprfs([self.PrimaryGas],retapFlg=1)          # Retrieved Profiles
        self.readprfs([self.PrimaryGas],retapFlg=0)                # A priori Profiles
        self.readsummary()                                         # Summary file information
        self.readError(totFlg=True,avkFlg=True,vmrFlg=True)        # Read Error Data
        self.readPbp()                                             # Read pbp file for sza
        self.readStatLyrs(statLyrFile)                             # Read station layer file
        self.readRefPrf()                                          # Read reference.prf file
        
        #-------------------------------------
        # Assign values to temporary variables
        #-------------------------------------
        # Profile
        self.HDFtempPrf    = np.asarray(self.rprfs['TEMPERATURE'])                                      # Temperature Profile [K]
        self.HDFpressPrf   = np.asarray(self.rprfs['PRESSURE'])                                         # Pressure Profile [hPa]
        self.HDFz          = np.asarray(self.rprfs['ZBAR'][0,:])                                        # Altitude [??]
        self.HDFairMass    = np.asarray(self.rprfs['AIRMASS'])                                          # AirMass
        self.HDFrGasPrfVMR = np.asarray(self.rprfs[self.PrimaryGas])                                    # Retrieved primary gas profile [VMR]
        self.HDFaGasPrfVMR = np.asarray(self.aprfs[self.PrimaryGas])                                    # A priori primary gas profile [VMR]
        self.HDFrGasPrfMol = self.HDFrGasPrfVMR * self.HDFairMass                                       # Retrieved primary gas profile [mol cm^-2]
        self.HDFaGasPrfMol = self.HDFaGasPrfVMR * self.HDFairMass                                       # A priori primary gas profile [mol cm^-2]
        self.HDFsurfP      = np.squeeze(self.refPrf['PRESSURE'][:,-1])                                  # Surface Pressure from Pressure profile
        self.HDFsurfT      = np.squeeze(self.refPrf['TEMPERATURE'][:,-1])                               # Surface Temperature from temperature profile
        self.HDFh2oVMR     = np.asarray(self.rprfs['H2O'])                                              # Retrieved H2O profile [VMR]
        self.HDFaltBnds    = np.vstack((self.alt[:-1],self.alt[1:]))        

        # Error 
        if errFlg:
            self.HDFak        = np.asarray(self.error['AVK_vmr'])                                          # Averaging Kernel [VMR/VMR]
            self.HDFsysErr    = np.asarray(self.error['Total_Systematic_Error_VMR'])                       # Total Systematic error covariance matrix [VMR]
            self.HDFrandErr   = np.asarray(self.error['Total_Random_Error_VMR'])                           # Total Random error covariance matrix [VMR]
            self.HDFtcSysErr  = np.asarray(self.error['Total systematic uncertainty'])                     # Total column systematic error [mol cm^-2]
            self.HDFtcRanErr  = np.asarray(self.error['Total random uncertainty'])                         # Total column random error [mol cm^-2]
        else:
            dim1 = np.shape(self.HDFtempPrf)[0]
            dim2 = np.shape(self.HDFtempPrf)[1]
            dim3 = np.shape(self.HDFtempPrf)[1]
            self.HDFak        = np.empty([dim1,dim2,dim3])                                                # Averaging Kernel [VMR/VMR]
            self.HDFsysErr    = np.empty([dim1,dim2,dim3])                                                # Total Systematic error covariance matrix [VMR]
            self.HDFrandErr   = np.empty([dim1,dim2,dim3])                                                # Total Random error covariance matrix [VMR]
            self.HDFtcSysErr  = np.empty([dim1])                                                          # Total column systematic error [mol cm^-2]
            self.HDFtcRanErr  = np.empty([dim1])                                                          # Total column random error [mol cm^-2]
            self.HDFak.fill(-9.0E4)
            self.HDFsysErr.fill(-9.0E4)
            self.HDFrandErr.fill(-9.0E4)
            self.HDFtcSysErr.fill(-9.0E4)
            self.HDFtcRanErr.fill(-9.0E4)
                        
        # Total Column
        self.HDFretTC     = np.asarray(self.rprfs[self.PrimaryGas+'_tot_col'])                          # Primary gas retrieved total column
        self.HDFaprTC     = np.asarray(self.aprfs[self.PrimaryGas+'_tot_col'])                          # Primary gas a priori total column
        self.HDFh2oTC     = np.asarray(self.rprfs['H2O_tot_col'])                                       # Primary gas a priori total column       
        
        # Misc
        self.HDFdates     = np.asarray(self.rprfs['date'])                                              # Date stamp of retrieval
        self.HDFsza       = np.asarray(self.pbp['sza'])                                                 # Solar Zenith Angle

        #----------------------------------------
        # Calculate total column averaging kernel
        #----------------------------------------
        nobs            = len(self.HDFdates)
        nlyrs           = len(self.HDFz)
        self.HDFavkTC   = np.zeros((nobs,nlyrs))
        for i in range(0,nobs):
            AirMtemp  = np.squeeze(self.HDFairMass[i,:])
            akTemp    = np.squeeze(self.HDFak[i,:,:])
            AirMinv   = np.diag(1.0/AirMtemp)
            self.HDFavkTC[i,:] = np.dot(np.dot(AirMtemp,akTemp),AirMinv)
                
        #---------------------------------------
        # Convert dates to Julian Day since 2000
        #---------------------------------------        
        self.HDFdatesJD2K = np.array([(x - dt.datetime(2000,1,1)).total_seconds()/dt.timedelta(1).total_seconds() for x in self.HDFdates])         
        
        #-----------------------------
        # Find Spectral DB information
        #-----------------------------
        specDB        = self.getInputs()        
        self.HDFintT  = np.zeros(nobs)
        self.HDFazi   = np.zeros(nobs)
        
        for i,val in enumerate(self.HDFdates):
            tempSpecDB = self.dbFindDate(self.HDFdates[i])
           
            if i == 0:
                self.HDFlat     = np.array(tempSpecDB['N_Lat'])

                self.HDFlon     = np.array(tempSpecDB['W_Lon'])

                print '\nLongitude [W_Lon] in database: {}'.format(self.HDFlon)

                #-----------------------------
                # In the Database the Longitude is defined as positive West. 
                # Hence, to comply with GEOMS needs to be converted to positive East
                #-----------------------------                
                if (self.HDFlon > 0.) &  (self.HDFlon <= 180.):
                    self.HDFlon     = self.HDFlon*(-1.0)

                elif (self.HDFlon > 180.) &  (self.HDFlon <= 360.):
                    self.HDFlon     = 360.0 - self.HDFlon

                elif (self.HDFlon < 0.) &  (self.HDFlon >= -180.):
                    self.HDFlon     = self.HDFlon*(-1.0)

                elif (self.HDFlon < -180.) &  (self.HDFlon >= -360.):
                    self.HDFlon     = (360.0 + self.HDFlon)*(-1.0)

                else:
                    user_input = raw_input('Paused processing....\n Input specific longitude for HDF file: >>> ')
                    self.HDFlon = np.array(user_input)

                print 'Longitude [E_Lon] in HDF file: {}'.format(self.HDFlon)

                self.HDFinstAlt = np.array(tempSpecDB['Alt'] / 1000.0)
            
            self.HDFintT[i] = tempSpecDB['Dur']
            self.HDFazi[i]  = tempSpecDB['SAzm']

        #----------------------------------------------
        # In the Database Solar Azimuth is defined as positive South. 
        # Convert to North Solar Azimuth (2016 GEOMS CONVENTION)
        #----------------------------------------------
        print '\nConverting S-Azimuth to N-Azimuth....\n'
        
        for i, az in enumerate(self.HDFazi):
            if az >= 180.0:
                self.HDFazi[i] = np.abs(360. - az - 180.)
            elif az < 180.0:
                self.HDFazi[i] = 180. + az
            
                
            
    def fltrHDFdata(self,maxRMS,minSZA,maxSZA,minDOF,maxCHI,minTC,maxTC,dofF,rmsF,tcF,pcF,cnvF,szaF,chiFlg,tcMMflg, h2oFlg):

        #----------------------------------------------------
        # Print total number of observations before filtering
        #----------------------------------------------------
        print 'Number of total observations before filtering = {}'.format(len(self.HDFdates))
        
        #--------------------
        # Call to filter data
        #--------------------
        self.fltrData(self.PrimaryGas,mxrms=maxRMS,minsza=minSZA,mxsza=maxSZA,minDOF=minDOF,maxCHI=maxCHI,minTC=minTC,maxTC=maxTC,
                      dofFlg=dofF,rmsFlg=rmsF,tcFlg=tcF,pcFlg=pcF,cnvrgFlg=cnvF,szaFlg=szaF,chiFlg=chiFlg,tcMinMaxFlg=tcMMflg, h2oFlg=h2oFlg)     
              
        #------------
        # Remove data
        #------------
        self.HDFtempPrf     = np.delete(self.HDFtempPrf,self.inds,axis=0)
        self.HDFpressPrf    = np.delete(self.HDFpressPrf,self.inds,axis=0)
        self.HDFairMass     = np.delete(self.HDFairMass,self.inds,axis=0)
        self.HDFrGasPrfVMR  = np.delete(self.HDFrGasPrfVMR,self.inds,axis=0)
        self.HDFaGasPrfVMR  = np.delete(self.HDFaGasPrfVMR,self.inds,axis=0)
        self.HDFrGasPrfMol  = np.delete(self.HDFrGasPrfMol,self.inds,axis=0)
        self.HDFaGasPrfMol  = np.delete(self.HDFaGasPrfMol,self.inds,axis=0)
        self.HDFh2oVMR      = np.delete(self.HDFh2oVMR,self.inds,axis=0)
        self.HDFsurfP       = np.delete(self.HDFsurfP,self.inds)
        self.HDFsurfT       = np.delete(self.HDFsurfT,self.inds)
        self.HDFak          = np.delete(self.HDFak,self.inds, axis=0)
        self.HDFsysErr      = np.delete(self.HDFsysErr,self.inds, axis=0)
        self.HDFrandErr     = np.delete(self.HDFrandErr,self.inds, axis=0)
        self.HDFtcSysErr    = np.delete(self.HDFtcSysErr,self.inds)
        self.HDFtcRanErr    = np.delete(self.HDFtcRanErr,self.inds)
        self.HDFavkTC       = np.delete(self.HDFavkTC,self.inds,axis=0)
        self.HDFretTC       = np.delete(self.HDFretTC,self.inds)
        self.HDFaprTC       = np.delete(self.HDFaprTC,self.inds)
        self.HDFh2oTC       = np.delete(self.HDFh2oTC,self.inds)
        self.HDFdates       = np.delete(self.HDFdates,self.inds)
        self.HDFintT        = np.delete(self.HDFintT,self.inds)
        self.HDFazi         = np.delete(self.HDFazi,self.inds)
        self.HDFdatesJD2K   = np.delete(self.HDFdatesJD2K,self.inds)
        self.HDFsza         = np.delete(self.HDFsza,self.inds)
   
        print 'Number of observations after filtering = {}'.format(len(self.HDFdates))   
        
        #-------------------------------------------
        # Determine if there are any negative TC H2O
        #-------------------------------------------
        ind = np.where(self.HDFh2oTC < 0.0)[0]
        if len(ind) > 0: 
            print '\n\n***********************************'
            print 'Retrievals found with negative H2O total column values!!!'
            print 'Number of retrievals found = {}'.format(len(ind))
            print 'Dates: '
            for i in ind:
                print self.HDFdates[i]
            print '***********************************\n\n'

        
#------------------------------------------------------------------------------------------------------------------------------        
class PlotData(ReadOutputData):

    def __init__(self,dataDir,ctlF,iyear=False,imnth=False,iday=False,fyear=False,fmnth=False,fday=False,incr=1, saveFlg=False, outFname=''):
        primGas = ''
        #------------------------------------------------------------
        # If outFname is specified, plots will be saved to this file,
        # otherwise plots will be displayed to screen
        #------------------------------------------------------------
        if saveFlg: self.pdfsav = PdfPages(outFname)
        else:       self.pdfsav = False
        
        super(PlotData,self).__init__(dataDir,primGas,ctlF,iyear,imnth,iday,fyear,fmnth,fday,incr)
        
    def closeFig(self):
        self.pdfsav.close()
    
    def pltSpectra(self,fltr=False,minSZA=0.0,maxSZA=80.0,maxRMS=1.0,minDOF=1.0,maxCHI=2.0,minTC=1.0E15,maxTC=1.0E16,mnthFltr=[1,2,3,4,5,6,7,8,9,10,11,12],
                   dofFlg=False,rmsFlg=True,tcFlg=True,pcFlg=True,szaFlg=False,chiFlg=False,cnvrgFlg=True,tcMMflg=False,mnthFltFlg=False):
        ''' Plot spectra and fit and Jacobian matrix '''
    
        print '\nPlotting Spectral Data...........\n'
        
        #------------------------
        # Determine Micro-windows
        #------------------------
        mw    = [str(int(x)) for x in self.ctl['band']]     
        numMW = len(mw)

        
        #---------------------------------------
        # Get profile, summary and spectral data
        #---------------------------------------
        if not self.readPrfFlgRet[self.PrimaryGas]: self.readprfs([self.PrimaryGas],retapFlg=1)   # Retrieved Profiles
        if self.empty: return False
        if not self.readsummaryFlg: self.readsummary()                                      # Summary File info
        if not self.readPbpFlg:     self.readPbp()                                          # observed, fitted, and difference spectra
        if not self.readSpectraFlg: self.readSpectra(self.gasList)                          # Spectra for each gas
        
        Z = np.asarray(self.rprfs['Z'][0,:])          # get altitude
        
        #------------------------------------------
        # Read Jacobian Matrix for single retrieval
        #------------------------------------------
        if len(self.dirLst) == 1:
            lines   = tryopen(self.dirLst[0]+self.ctl['file.out.k_matrix'][0])
            
            nlyrs   = int(lines[1].strip().split()[3])
            nstrt   = int(lines[1].strip().split()[2])
            JacbMat = np.array( [ [ float(x) for x in line.strip().split()[nstrt:(nstrt+nlyrs)] ] for line in lines[3:] ] )   
        
        #--------------------
        # Call to filter data
        #--------------------
        if fltr: self.fltrData(self.PrimaryGas,mxrms=maxRMS,minsza=minSZA,mxsza=maxSZA,minDOF=minDOF,maxCHI=maxCHI,minTC=minTC,maxTC=maxTC,mnthFltr=mnthFltr,
                               dofFlg=dofFlg,rmsFlg=rmsFlg,tcFlg=tcFlg,pcFlg=pcFlg,szaFlg=szaFlg,cnvrgFlg=cnvrgFlg,chiFlg=chiFlg,tcMinMaxFlg=tcMMflg,mnthFltFlg=mnthFltFlg)
        else: self.inds = np.array([]) 
        
        if self.empty: return False
        
        #---------------------
        # Get SZA for Plotting
        #---------------------
        sza = np.delete(self.pbp["sza"],self.inds)
        
        #------------
        # Get spectra
        #------------
        dataSpec  = OrderedDict()
        gasSpec   = OrderedDict()
        gasAbs    = OrderedDict()
        gasAbsSNR = OrderedDict()

        
        for x in mw:  # Loop through micro-windows
            dataSpec['Obs_'+x]        = np.delete(self.pbp['Obs_'+x],self.inds,axis=0)
            dataSpec['Fitted_'+x]     = np.delete(self.pbp['Fitted_'+x],self.inds,axis=0)
            dataSpec['Difference_'+x] = np.delete(self.pbp['Difference_'+x]*100.0,self.inds,axis=0)
            dataSpec['WaveN_'+x]      = self.spc['MW_'+x]
            dataSpec['All_'+x]        = np.delete(self.spc['All_'+x],self.inds,axis=0)
            if self.solarFlg: dataSpec['Sol_'+x]        = np.delete(self.spc['Solar_'+x],self.inds,axis=0)
    
        #------------------------------
        # Get dates for timeseries plot
        #------------------------------
        if len(self.dirLst) > 1: 
            dates = np.delete(self.pbp["date"],self.inds)
        
            #----------------------------
            # Determine if multiple years
            #----------------------------
            years = [ singDate.year for singDate in dates]      # Find years for all date entries
            if len(list(set(years))) > 1: yrsFlg = True         # Determine all unique years
            else:                         yrsFlg = False        
    
        #----------------------------------------
        # Loop through gases and micro-windows
        # Not all gasses are in each micro-window
        # Determine which gasses belong to which
        # micro-window
        #----------------------------------------
        mwList = OrderedDict()        # Use ordered dictionary so that micro-window plots print in order
        for x in mw: mwList[x] = self.ctl['band.'+x+'.gasb']
        #mwList  = {x:self.ctl['band.'+x+'.gasb'] for x in mw}
        gasSpec = {gas.upper()+'_'+m:np.delete(self.spc[gas.upper()+'_'+m],self.inds,axis=0) for m in mwList for gas in mwList[m]}  

        #---------------------
        # Calculate Statistics
        #---------------------
        for x in mw:  # Loop through micro-windows

            #-------------------------------------------------------------
            # Calculate the total Observed absorption in micro-window
            # This must be done first because below code modifies dataSpec
            #-------------------------------------------------------------
            gasAbs["Total_"+x] = simps(1.0 - dataSpec['Obs_'+x],x=dataSpec['WaveN_'+x],axis=1)               
                        
            if len(self.dirLst) > 1:
                dataSpec['Obs_'+x]        = np.mean(dataSpec['Obs_'+x],axis=0)
                dataSpec['Fitted_'+x]     = np.mean(dataSpec['Fitted_'+x],axis=0)
                dataSpec['Difference_'+x] = np.mean(dataSpec['Difference_'+x],axis=0)
                dataSpec['All_'+x]        = np.mean(dataSpec['All_'+x],axis=0)
                if self.solarFlg:dataSpec['Sol_'+x]        = np.mean(dataSpec['Sol_'+x],axis=0)    
                dataSpec['DifSTD_'+x]     = np.std(dataSpec['Difference_'+x],axis=0)
                
            else:
                dataSpec['Obs_'+x]        = dataSpec['Obs_'+x][0]
                dataSpec['Fitted_'+x]     = dataSpec['Fitted_'+x][0]
                dataSpec['Difference_'+x] = dataSpec['Difference_'+x][0]
                dataSpec['All_'+x]        = dataSpec['All_'+x][0]
                if self.solarFlg:dataSpec['Sol_'+x]        = dataSpec['Sol_'+x][0]
                                
            if len(self.dirLst) > 1:

                if self.PrimaryGas+"_"+x in gasSpec:  
                #---------------------------------------------------
                # Calculate the integrate absorption for primary gas
                #---------------------------------------------------               
                    gasAbs[self.PrimaryGas+"_"+x] = simps(1.0 - gasSpec[self.PrimaryGas+"_"+x],x=dataSpec['WaveN_'+x],axis=1)       
                
                #-----------------------------------
                # Calculate the peak absorption of 
                # primary gas for each micro-window
                #-----------------------------------
                    gasAbs[self.PrimaryGas+"_trans_"+x] = 1.0 - np.min(gasSpec[self.PrimaryGas+"_"+x],axis=1)
                
                #---------------------------------------------
                # Determine product of SNR and Peak Absorption
                #---------------------------------------------
                    tempSNR  = np.delete(self.summary["SNR_"+x],self.inds)
                    gasAbsSNR[self.PrimaryGas+"_"+x] = gasAbs[self.PrimaryGas+"_"+x] * tempSNR 
                        
  
        if len(self.dirLst) > 1:
            gasSpec = {gas.upper()+'_'+x:np.mean(gasSpec[gas.upper()+'_'+x],axis=0) for x in mwList for gas in mwList[x]}   
        else:
            for x in gasSpec: gasSpec[x] = gasSpec[x][0]

        #---------------------------
        self.dataSpec = dataSpec
        self.mwList   = mwList
        self.gasSpec  = gasSpec
        self.gasAbs   = gasAbs

        #---------------------------
 
        #---------------------------
        # Date locators for plotting
        #---------------------------
        clmap        = 'bwr'
        cm           = plt.get_cmap(clmap)              
        yearsLc      = YearLocator()
        monthsAll    = MonthLocator()
        #months       = MonthLocator(bymonth=1,bymonthday=1)
        months       = MonthLocator()
        DateFmt      = DateFormatter('%m\n%Y')      
 
        #----------------------------------------
        # Plot Jacobian only if there are
        # profile retrievals and single retrieval
        #----------------------------------------
        if ('gas.profile.list' in self.ctl) and self.ctl['gas.profile.list'] and (len(self.dirLst) == 1):
            fig1   = plt.figure()
            gs1    = gridspec.GridSpec(2,numMW,height_ratios=(1,60))
            
            #levels = np.arange(np.round(np.min(JacbMat),decimals=3)-0.001, np.round(np.max(JacbMat),decimals=3)+0.001, np.round(  (np.round(np.max(JacbMat),decimals=3) - np.round(np.min(JacbMat),decimals=3) )/20., decimals=4))
           
            ipnt   = 0
            for i,x in enumerate(mwList):
                npnts = np.shape(dataSpec['WaveN_'+x])[0]
                ax    = plt.subplot(gs1[1,i])
                im    = ax.contourf(dataSpec['WaveN_'+x],Z,np.transpose(JacbMat[ipnt:(ipnt+npnts),:]), 100, cmap=cm) 

                norm  = matplotlib.colors.Normalize(vmin=im.cvalues.min(), vmax=im.cvalues.max())
                
                sm = plt.cm.ScalarMappable(norm=norm, cmap=cm)
                
                sm.set_array([])

                ipnt += npnts
                ax.grid(True)
                if i == 0: ax.set_ylabel('Altitude [km]')
                ax.xaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    
            fig1.text(0.5,0.04,'Wavenumber [cm$^{-1}$]',ha='center',va='center')
            fig1.autofmt_xdate()
            caxb = fig1.add_axes([0.15,0.9,0.7,0.03])
            #fig1.colorbar(im,cax=caxb,orientation='horizontal')
            fig1.colorbar(sm,  cax=caxb,orientation='horizontal')
            plt.suptitle('Jacobian Matrix')
                
            if self.pdfsav: self.pdfsav.savefig(fig1,dpi=200)
            else:           plt.show(block=False)

        
        #--------------------------------
        # Plot data for each micro-window
        #--------------------------------            
        for x in mwList:
            fig, (ax1, ax2)  = plt.subplots(2, figsize=(12,7), sharex=True)

            gs   = gridspec.GridSpec(2,1,height_ratios=[1,3])
            ax1  = plt.subplot(gs[0], sharex=ax2)
            ax2  = plt.subplot(gs[1],sharex=ax1)
            ax1.plot(dataSpec['WaveN_'+x],dataSpec['Difference_'+x],color='k')
            ax1.axhline(y=0,color='r')
            if len(self.dirLst) > 1: ax1.fill_between(dataSpec['WaveN_'+x],dataSpec['Difference_'+x]-dataSpec['DifSTD_'+x],dataSpec['Difference_'+x]+dataSpec['DifSTD_'+x],alpha=0.5,color='0.75')
            ax1.grid(True)
            ax1.set_ylabel('% Difference')
            ax1.set_title('Micro-Window '+ x)
            ax1.set_xlim((np.min(dataSpec['WaveN_'+x]),np.max(dataSpec['WaveN_'+x])))
            ax1.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))
            ax1.xaxis.set_minor_locator(AutoMinorLocator())
            plt.tick_params(which='minor',length=4,color='b')
            
            ax2.plot(dataSpec['WaveN_'+x],dataSpec['Obs_'+x],label='Observed')
            ax2.plot(dataSpec['WaveN_'+x],dataSpec['Fitted_'+x],label='Fitted')
            if self.solarFlg: ax2.plot(dataSpec['WaveN_'+x],dataSpec['Sol_'+x],label='Solar')
            sclfct = 0.0
            for g in mwList[x]: 
                sclfct += 0.02
                ax2.plot(dataSpec['WaveN_'+x],gasSpec[g.upper()+'_'+x]+(gasSpec[g.upper()+'_'+x]*sclfct),label=g.upper())
            
            ax2.grid(True)
            ax2.set_xlabel('Wavenumber [cm$^{-1}$]')
            ax2.set_ylabel('Transmission (Arbitrary)')
            #ax2.set_ylim(bottom=0.0)
            ax2.set_xlim((np.min(dataSpec['WaveN_'+x]),np.max(dataSpec['WaveN_'+x])))

            ax2.legend(prop={'size':10},loc='upper center', bbox_to_anchor=(0.5, 1.065),
                      fancybox=True, ncol=len(mwList[x])+3)  
            ax1.tick_params(axis='x',which='both',labelsize=12)
            ax1.tick_params(axis='y',which='both',labelsize=12)
            ax2.tick_params(axis='x',which='both',labelsize=12)
            ax1.tick_params(axis='y',which='both',labelsize=12)
   
            if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
            else:           plt.show(block=False)

            
            
            #---------------------------------------------------------------
            # Plot time series of integrated absorption for each microwindow
            # Colored by SZA if multiple directories
            #---------------------------------------------------------------   
            if len(self.dirLst) > 1:
                if self.PrimaryGas+"_"+x in gasSpec:
                    fig,ax1  = plt.subplots()
                    tcks = range(np.int(np.floor(np.min(sza))),np.int(np.ceil(np.max(sza)))+2)
                    norm = colors.BoundaryNorm(tcks,cm.N)                        
                    sc1  = ax1.scatter(dates,gasAbs[self.PrimaryGas+"_"+x],c=sza,cmap=cm,norm=norm)
                        
                    ax1.grid(True,which='both')
                    ax1.set_xlabel('Date')
                    ax1.set_ylabel('Integrated Spectral Absorption',fontsize=9)
                    ax1.set_title("Fractional Integrated Spectral Absorption\nMicro-window {}".format(x),multialignment='center')        
                    ax1.tick_params(axis='x',which='both',labelsize=8)
                    
                    fig.subplots_adjust(right=0.82)
                    cax  = fig.add_axes([0.86, 0.1, 0.03, 0.8])
                        
                    cbar = fig.colorbar(sc1, cax=cax, format='%2i')
                    cbar.set_label('SZA')    
                    
                    if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                    else:           plt.show(block=False)   
    
                
                    #--------------------------------------------------------------------------
                    # Plot time series of fractional integrated absorption for each microwindow
                    #---------------------------------------------------------------    
                    fig1,ax1 = plt.subplots()
                    ax1.plot(dates,gasAbs[self.PrimaryGas+"_"+x]/gasAbs["Total_"+x],'k.',markersize=4)
                    ax1.grid(True)
                    ax1.set_ylabel("Fractional Integrated Spectral Absorption")
                    ax1.set_xlabel('Date [MM]')
                    ax1.set_title("Fractional Integrated Spectral Absorption\nMicro-window {}".format(x),multialignment='center')
                    
                    if yrsFlg:
                        #plt.xticks(rotation=45)
                        ax1.xaxis.set_major_locator(yearsLc)
                        ax1.xaxis.set_minor_locator(months)
                        #ax1.xaxis.set_minor_formatter(DateFormatter('%m'))
                        ax1.xaxis.set_major_formatter(DateFmt) 
                        #ax1.xaxis.set_tick_params(which='major', pad=15)  
                        ax1.xaxis.set_tick_params(which='major',labelsize=8)
                        ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
                    else:
                        ax1.xaxis.set_major_locator(monthsAll)
                        ax1.xaxis.set_major_formatter(DateFmt)
                        ax1.set_xlim((dt.date(years[0],1,1), dt.date(years[0],12,31)))
                        ax1.xaxis.set_minor_locator(AutoMinorLocator())
                        fig1.autofmt_xdate()
                    
                    if self.pdfsav: self.pdfsav.savefig(fig1,dpi=200)
                    else:           plt.show(block=False)          
                
                    #----------------------------------------------
                    # Plot time series of peak absorption times SNR
                    #----------------------------------------------
                    fig1,ax1 = plt.subplots()
                    ax1.plot(dates,gasAbsSNR[self.PrimaryGas+"_"+x],'k.',markersize=4)
                    ax1.grid(True)
                    ax1.set_ylabel("Peak Spectral Absorption * SNR")
                    ax1.set_xlabel('Date [MM]')
                    ax1.set_title("Peak Spectral Absorption * SNR\nMicro-window {}".format(x),multialignment='center')
                    
                    if yrsFlg:
                        #plt.xticks(rotation=45)
                        ax1.xaxis.set_major_locator(yearsLc)
                        ax1.xaxis.set_minor_locator(months)
                        #ax1.xaxis.set_minor_formatter(DateFormatter('%m'))
                        ax1.xaxis.set_major_formatter(DateFmt) 
                        #ax1.xaxis.set_tick_params(which='major', pad=15)  
                        ax1.xaxis.set_tick_params(which='major',labelsize=8)
                        ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
                    else:
                        ax1.xaxis.set_major_locator(monthsAll)
                        ax1.xaxis.set_major_formatter(DateFmt)
                        ax1.set_xlim((dt.date(years[0],1,1), dt.date(years[0],12,31)))
                        ax1.xaxis.set_minor_locator(AutoMinorLocator())
                        fig1.autofmt_xdate()
                    
                    if self.pdfsav: self.pdfsav.savefig(fig1,dpi=200)
                    else:           plt.show(block=False)               
            
            
        
    def pltPrf(self,fltr=False,minSZA=0.0,maxSZA=80.0,maxRMS=1.0,minDOF=1.0,maxCHI=2.0,minTC=1.0E15,maxTC=1.0E16,dofFlg=False,rmsFlg=True,tcFlg=True,mnthFltr=[1,2,3,4,5,6,7,8,9,10,11,12],
               pcFlg=True,cnvrgFlg=True,allGas=True,sclfct=1.0,sclname=' ',pltStats=True,szaFlg=False,errFlg=False,chiFlg=False,tcMMflg=False,mnthFltFlg=False):
        ''' Plot retrieved profiles '''
        
        
        print '\nPrinting Profile Plots.......\n'
        
        aprPrf       = {}
        rPrf         = {}
        localGasList = [self.PrimaryGas]
        
        #-------------------------------------------------------
        # Get profile, summary for Primary gas.... for filtering
        #-------------------------------------------------------
        if not self.readPrfFlgRet[self.PrimaryGas]: self.readprfs([self.PrimaryGas],retapFlg=1)   # Retrieved Profiles
        if self.empty: return False
        if not self.readPrfFlgApr[self.PrimaryGas]: self.readprfs([self.PrimaryGas],retapFlg=0)   # Apriori Profiles
        aprPrf[self.PrimaryGas] = np.asarray(self.aprfs[self.PrimaryGas]) * sclfct
        rPrf[self.PrimaryGas]   = np.asarray(self.rprfs[self.PrimaryGas]) * sclfct
        rPrfMol                 = np.asarray(self.rprfs[self.PrimaryGas]) * np.asarray(self.rprfs['AIRMASS'])
        if len(self.dirLst) > 1: dates                   = self.rprfs['date'] 

        alt = np.asarray(self.rprfs['Z'][0,:])

        

        if not self.readsummaryFlg: self.readsummary()                                      # Summary File info
        rms     = np.asarray(self.summary[self.PrimaryGas+'_FITRMS'])
        dofs    = np.asarray(self.summary[self.PrimaryGas+'_DOFS_TRG'])
        totClmn = np.asarray(self.summary[self.PrimaryGas.upper()+'_RetColmn'])

        
        if not self.readPbpFlg: self.readPbp()                                              # Pbp file info
        sza   = self.pbp['sza']
        saa   = self.pbp['saa']

                 
        if errFlg:                                    # Error info
            
            if not all((self.readErrorFlg['totFlg'],self.readErrorFlg['sysFlg'],self.readErrorFlg['randFlg'])):
                self.readError(totFlg=True,sysFlg=True,randFlg=True,vmrFlg=False,avkFlg=False,KbFlg=False) 
            
            npnts    = np.shape(self.error['Total_Random_Error'])[0]
            nlvls    = np.shape(alt)[0]
            rand_err = np.zeros((npnts,nlvls))
            sys_err  = np.zeros((npnts,nlvls))
            
            for i in range(npnts):
                rand_err[i,:] = np.diag(self.error['Total_Random_Error'][i][:,:])
                sys_err[i,:]  = np.diag(self.error['Total_Systematic_Error'][i][:,:])
                
            tot_err  = np.sqrt(rand_err + sys_err)            
            rand_err = np.sqrt(rand_err)
            sys_err  = np.sqrt(sys_err)
            
            rand_cmpnts = self.randErrDiag
            sys_cmpnts  = self.sysErrDiag
            
        #--------------------
        # Call to filter data
        #--------------------
        if fltr: self.fltrData(self.PrimaryGas,mxrms=maxRMS,minsza=minSZA,mxsza=maxSZA,minDOF=minDOF,maxCHI=maxCHI,minTC=minTC,maxTC=maxTC,mnthFltr=mnthFltr,
                               dofFlg=dofFlg,rmsFlg=rmsFlg,tcFlg=tcFlg,pcFlg=pcFlg,szaFlg=szaFlg,cnvrgFlg=cnvrgFlg,chiFlg=chiFlg,tcMinMaxFlg=tcMMflg,mnthFltFlg=mnthFltFlg)
        else:    self.inds = np.array([]) 
        
        if self.empty: return False
        
        #--------------------------------------------------------
        # Get profile data for other gases if allGas flag is True
        #--------------------------------------------------------
        if allGas:
            nonPgas = (gas for gas in self.gasList if gas != self.PrimaryGas)
            for gas in nonPgas:
                if not self.readPrfFlgRet[gas.upper()]: self.readprfs([gas.upper()],retapFlg=1)   # Retrieved Profiles
                if not self.readPrfFlgApr[gas.upper()]: self.readprfs([gas.upper()],retapFlg=0)   # Apriori Profiles
                aprPrf[gas.upper()] = np.asarray(self.aprfs[gas.upper()]) * sclfct
                rPrf[gas.upper()]   = np.asarray(self.rprfs[gas.upper()]) * sclfct
                localGasList.append(gas)
                
        #----------------------------
        # Remove inds based on filter
        #----------------------------
        nfltr   = len(self.inds)

        rms     = np.delete(rms,self.inds)
        ntot    = len(rms)
        sza     = np.delete(sza,self.inds)
        saa     = np.delete(saa,self.inds)
        if len(self.dirLst) > 1: dates   = np.delete(dates,self.inds)
        dofs    = np.delete(dofs,self.inds)
        totClmn = np.delete(totClmn,self.inds)
        rPrfMol = np.delete(rPrfMol,self.inds,axis=0)
        for gas in rPrf:
            rPrf[gas]    = np.delete(rPrf[gas],self.inds,axis=0)
            aprPrf[gas]  = np.delete(aprPrf[gas],self.inds,axis=0)
            
        if errFlg:
            rand_err = np.delete(rand_err,self.inds,axis=0)
            sys_err  = np.delete(sys_err,self.inds,axis=0)  
            tot_err  = np.delete(tot_err,self.inds,axis=0)  
            
            for k in sys_cmpnts:
                sys_cmpnts[k] = np.delete(sys_cmpnts[k],self.inds,axis=0)
                
            for k in rand_cmpnts:
                rand_cmpnts[k] = np.delete(rand_cmpnts[k],self.inds,axis=0)
                
        #---------------------
        # Calculate statistics
        #---------------------
        if len(self.dirLst) > 1:
            prfMean    = {gas:np.mean(rPrf[gas],axis=0) for gas in rPrf}
            prfSTD     = {gas:np.std(rPrf[gas],axis=0) for gas in rPrf}

            aprPrfMean = {gas:np.mean(aprPrf[gas],axis=0) for gas in rPrf}
            aprPrfSTD  = {gas:np.std(aprPrf[gas],axis=0) for gas in rPrf}
        
        #----------------------------
        # Determine if multiple years
        #----------------------------
        if len(self.dirLst) > 1:
            years = [ singDate.year for singDate in dates]      # Find years for all date entries
            if len(list(set(years))) > 1: yrsFlg = True         # Determine all unique years
            else:                         yrsFlg = False
        
        #---------------------------
        # Plot Profiles for each gas
        #---------------------------       
        for gas in localGasList:
            #-------------------------------
            # Single Profile or Mean Profile
            #-------------------------------
            fig,(ax1,ax2) = plt.subplots(1,2,sharey=True)
            if len(self.dirLst) > 1:
                ax1.plot(prfMean[gas],alt,color='k',label=gas+' Retrieved Profile Mean')
                ax1.fill_betweenx(alt,prfMean[gas]-prfSTD[gas],prfMean[gas]+prfSTD[gas],alpha=0.5,color='0.75')

                ax1.plot(aprPrfMean[gas],alt,color='r',label='A priori')
                ax1.fill_betweenx(alt,aprPrfMean[gas]-aprPrfSTD[gas],aprPrfMean[gas]+aprPrfSTD[gas],alpha=0.2,color='r')
               
                ax2.plot(prfMean[gas],alt,color='k',label=gas+' Retrieved Profile Mean')
                ax2.fill_betweenx(alt,prfMean[gas]-prfSTD[gas],prfMean[gas]+prfSTD[gas],alpha=0.5,color='0.75')

                ax2.plot(aprPrfMean[gas],alt,color='r',label='A priori')
                ax2.fill_betweenx(alt,aprPrfMean[gas]-aprPrfSTD[gas],aprPrfMean[gas]+aprPrfSTD[gas],alpha=0.2,color='r')   
            else:
                ax1.plot(rPrf[gas][0],alt,color='k',label=gas)
                ax2.plot(rPrf[gas][0],alt,color='k',label=gas)

                ax1.plot(aprPrf[gas][0],alt, color='r',label='A priori')
                ax2.plot(aprPrf[gas][0],alt, color='r',label='A priori')
            
            ax1.grid(True,which='both')
            ax2.grid(True,which='both')
            
            ax1.legend(prop={'size':9})
            ax2.legend(prop={'size':9}) 

            if fltr:  
                ax1.text(-0.1,1.09, 'Max RMS = '+str(maxRMS),ha='left',va='center',transform=ax1.transAxes,fontsize=6)
                ax1.text(-0.1,1.07, 'Min DOF = '+str(minDOF), ha='left',va='center',transform=ax1.transAxes,fontsize=6)
                ax1.text(-0.1,1.05, 'Number of Obs Filtered        = '+str(nfltr),ha='left',va='center',transform=ax1.transAxes,fontsize=6)
                ax1.text(-0.1,1.03,'Number of Obs After Filtering = '+str(ntot), ha='left',va='center',transform=ax1.transAxes,fontsize=6)
         
            ax1.set_ylabel('Altitude [km]')
            ax1.set_xlabel('VMR ['+sclname+']')
            ax2.set_xlabel('Log Scale VMR ['+sclname+']')
            ax2.set_xscale('log')
            
            ax1.tick_params(axis='x',which='both',labelsize=8)
            ax2.tick_params(axis='x',which='both',labelsize=8)
            plt.suptitle(gas, fontsize=16)

            if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
            else:      plt.show(block=False)

            #np.savetxt('test.out', zip(alt, rPrf['H2O'][0]*1e6,aprPrf['H2O']*1e6) , delimiter='\t')

    
            #------------------
            # Multiple Profiles
            #------------------
            if len(self.dirLst) > 1:
                clmap = 'jet'
                
                #------------------------------
                # Profiles as a function of RMS
                #------------------------------
                fig,(ax1,ax2)  = plt.subplots(1,2,sharey=True)
                cm             = plt.get_cmap(clmap)
                cNorm          = colors.Normalize( vmin=np.nanmin(rms), vmax=np.nanmax(rms) )
                scalarMap      = mplcm.ScalarMappable( norm=cNorm, cmap=cm )
                
                scalarMap.set_array(rms)
    
                #ax1.set_color_cycle( [scalarMap.to_rgba(x) for x in rms] )
                #ax2.set_color_cycle( [scalarMap.to_rgba(x) for x in rms] )

                ax1.set_prop_cycle( cycler('color', [scalarMap.to_rgba(x) for x in rms] ) )
                ax2.set_prop_cycle( cycler('color', [scalarMap.to_rgba(x) for x in rms] ) )
                
                for i in range(len(rms)):
                    ax1.plot(rPrf[gas][i,:],alt,linewidth=0.75)
                    ax2.plot(rPrf[gas][i,:],alt,linewidth=0.75)

                    
                ax1.plot(aprPrfMean[gas],alt,'k--',linewidth=4,label='A priori')
                ax1.fill_betweenx(alt,aprPrfMean[gas]-aprPrfSTD[gas],aprPrfMean[gas]+aprPrfSTD[gas],alpha=0.25,color='0.75')

                ax2.plot(aprPrfMean[gas],alt,'k--',linewidth=4,label='A priori')
                ax2.fill_betweenx(alt,aprPrfMean[gas]-aprPrfSTD[gas],aprPrfMean[gas]+aprPrfSTD[gas],alpha=0.25,color='0.75')
                
                ax1.set_ylabel('Altitude [km]')
                ax1.set_xlabel('VMR ['+sclname+']')
                ax2.set_xlabel('Log VMR ['+sclname+']')
                
                ax1.grid(True,which='both')
                ax2.grid(True,which='both')
                ax2.set_xscale('log')
                
                cbar = fig.colorbar(scalarMap,orientation='vertical')
                cbar.set_label('RMS')
                
                ax1.legend(prop={'size':9})
                ax2.legend(prop={'size':9})
                
                ax1.tick_params(axis='x',which='both',labelsize=8)
                ax2.tick_params(axis='x',which='both',labelsize=8)  
                plt.suptitle(gas, fontsize=16)
    
                if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                else:           plt.show(block=False)         
                
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
                    ax1.plot(rPrf[gas][i,:],alt,linewidth=0.75)
                    ax2.plot(rPrf[gas][i,:],alt,linewidth=0.75)

                ax1.plot(aprPrfMean[gas],alt,'k--',linewidth=4,label='A priori')
                ax1.fill_betweenx(alt,aprPrfMean[gas]-aprPrfSTD[gas],aprPrfMean[gas]+aprPrfSTD[gas],alpha=0.5,color='0.75')

                ax2.plot(aprPrfMean[gas],alt,'k--',linewidth=4,label='A priori')
                ax2.fill_betweenx(alt,aprPrfMean[gas]-aprPrfSTD[gas],aprPrfMean[gas]+aprPrfSTD[gas],alpha=0.5,color='0.75')
                    
                #ax1.plot(aprPrf[gas],alt,'k--',linewidth=4,label='A priori')
                #ax2.plot(aprPrf[gas],alt,'k--',linewidth=4,label='A priori')
                
                ax1.set_ylabel('Altitude [km]')
                ax1.set_xlabel('VMR ['+sclname+']')
                ax2.set_xlabel('Log VMR ['+sclname+']')
                
                ax1.grid(True,which='both')
                ax2.grid(True,which='both')
                ax2.set_xscale('log')
                
                cbar = fig.colorbar(scalarMap,orientation='vertical')
                cbar.set_label('SZA')
                
                ax1.legend(prop={'size':9})
                ax2.legend(prop={'size':9})
                
                ax1.tick_params(axis='x',which='both',labelsize=8)
                ax2.tick_params(axis='x',which='both',labelsize=8)  
                plt.suptitle(gas, fontsize=16)
    
                if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                else:           plt.show(block=False)  
                
                #--------------------------------
                # Profiles as a function of Month
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
                    ax1.plot(rPrf[gas][i,:],alt,linewidth=0.75)
                    ax2.plot(rPrf[gas][i,:],alt,linewidth=0.75)
                
                
                ax1.plot(aprPrfMean[gas],alt,'k--',linewidth=4,label='A priori')
                ax1.fill_betweenx(alt,aprPrfMean[gas]-aprPrfSTD[gas],aprPrfMean[gas]+aprPrfSTD[gas],alpha=0.5,color='0.75')

                ax2.plot(aprPrfMean[gas],alt,'k--',linewidth=4,label='A priori')
                ax2.fill_betweenx(alt,aprPrfMean[gas]-aprPrfSTD[gas],aprPrfMean[gas]+aprPrfSTD[gas],alpha=0.5,color='0.75')
                #ax1.plot(aprPrf[gas],alt,'k--',linewidth=4,label='A priori')
                #ax2.plot(aprPrf[gas],alt,'k--',linewidth=4,label='A priori')
                
                ax1.set_ylabel('Altitude [km]')
                ax1.set_xlabel('VMR ['+sclname+']')
                ax2.set_xlabel('Log VMR ['+sclname+']')
                
                ax1.grid(True,which='both')
                ax2.grid(True,which='both')
                ax2.set_xscale('log')
                
                cbar = fig.colorbar(scalarMap,orientation='vertical')
                cbar.set_label('Month')
                
                ax1.legend(prop={'size':9})
                ax2.legend(prop={'size':9})
                
                ax1.tick_params(axis='x',which='both',labelsize=8)
                ax2.tick_params(axis='x',which='both',labelsize=8)  
                plt.suptitle(gas, fontsize=16)
    
                if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                else:           plt.show(block=False)               
                
                #-------------------------------
                # Plot average profiles by month
                #-------------------------------
                months = np.asarray([d.month for d in dates])
                
                for m in list(set(month)):
                    inds     = np.where(months == m)[0]
                    mnthMean = np.mean(rPrf[gas][inds,:],axis=0)
                    mnthSTD  = np.std(rPrf[gas][inds,:],axis=0)

                    mnthMeanApr = np.mean(aprPrf[gas][inds,:],axis=0)
                    mnthSTDApr  = np.std(aprPrf[gas][inds,:],axis=0)

                
                    fig,(ax1,ax2)  = plt.subplots(1,2,sharey=True)
                    ax1.plot(mnthMean,alt,color='k',label='Monthly Mean Profile, Nobs = '+str(len(inds)))
                    ax1.fill_betweenx(alt,mnthMean-mnthSTD,mnthMean+mnthSTD,alpha=0.5,color='0.75')

                    ax1.plot(mnthMeanApr,alt,color='r',label='Monthly Mean A priori Profile')
                    ax1.fill_betweenx(alt,mnthMeanApr-mnthSTDApr,mnthMeanApr+mnthSTDApr,alpha=0.25,color='r')  

                    ax2.plot(mnthMean,alt,color='k',label='Monthly Mean Profile, Nobs = '+str(len(inds)))
                    ax2.fill_betweenx(alt,mnthMean-mnthSTD,mnthMean+mnthSTD,alpha=0.5,color='0.75')

                    ax2.plot(mnthMeanApr,alt,color='r',label='Monthly Mean A priori Profile')
                    ax2.fill_betweenx(alt,mnthMeanApr-mnthSTDApr,mnthMeanApr+mnthSTDApr,alpha=0.25,color='r')    
                    
                    #ax1.plot(aprPrf[gas],alt,color='r',label='A Priori Profile')

                    plt.suptitle('Month = '+str(m), fontsize=16)
                    
                    #ax1.set_title('Month = '+str(m))
                    ax1.set_ylabel('Altitude [km]')
                    ax1.set_xlabel('VMR ['+sclname+']')    
                    ax1.grid(True,which='both')
                    ax1.legend(prop={'size':9})

                    ax2.set_xlabel('VMR ['+sclname+']')    
                    ax2.grid(True,which='both')
                    ax2.legend(prop={'size':9})
                    ax2.set_xscale('log')
                    
                    if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                    else:           plt.show(block=False)


                #-------------------------------
                # Plot average profiles by month (AGU)
                #-------------------------------
                # years = np.asarray([d.year for d in dates])

                # indY1 = np.where(years <= 2015)[0]
                # indY2 = np.where(years == 2016)[0]


                # months1 = np.asarray([d.month for d in dates[indY1]])
                # months2 = np.asarray([d.month for d in dates[indY2]])
                
                # for m in list(set(month)):
                #     inds1     = np.where(months1 == m)[0]
                #     mnthMean1 = np.mean(rPrf[gas][indY1[inds1],:],axis=0)
                #     mnthSTD1  = np.std(rPrf[gas][indY1[inds1],:],axis=0)

                #     inds2     = np.where(months2 == m)[0]
                #     mnthMean2 = np.mean(rPrf[gas][indY2[inds2],:],axis=0)
                #     mnthSTD2  = np.std(rPrf[gas][indY2[inds2],:],axis=0)
                
                #     fig,ax1  = plt.subplots()
                #     ax1.plot(mnthMean1,alt,color='k',label='1999 - 2015')
                #     ax1.fill_betweenx(alt,mnthMean1-mnthSTD1,mnthMean1+mnthSTD1,alpha=0.5,color='0.75')  

                #     ax1.plot(mnthMean2,alt,color='green',label='2016')
                #     ax1.fill_betweenx(alt,mnthMean2-mnthSTD2,mnthMean2+mnthSTD2,alpha=0.5, facecolor='green', color='0.75')

                #     ax1.plot(aprPrf[gas],alt,color='r',label='A Priori')
                    
                #     ax1.set_title('Month = '+str(m))
                #     ax1.set_ylabel('Altitude [km]')
                #     ax1.set_xlabel('VMR ['+sclname+']')    
                #     ax1.grid(True,which='both')
                #     ax1.legend(prop={'size':10})
                #     ax1.set_ylim(0,60)
                    
                #     if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                #     else:           plt.show(block=False)
                    
                   
                #-------------------------------------
                # 
                #-------------------------------------
                if pltStats:
                    #-----------------
                    # Get day of year 
                    #-----------------
                    doy   = np.array([d.timetuple().tm_yday for d in dates])
             
                    #-----------------
                    # RMS and DOF as a function of SZA color coded by DOY 
                    #-----------------
                    fig,(ax1,ax2)  = plt.subplots(2,1,sharex=True)

                    #tcks = range(np.min(doy),np.max(doy)+2)
                    #norm = colors.BoundaryNorm(tcks,cm.N)                          
                    sc1 = ax1.scatter(sza,rms,c=doy,cmap=cm)
                    ax2.scatter(sza,dofs,c=doy,cmap=cm)      
                        
                    ax1.grid(True,which='both')
                    ax2.grid(True,which='both')                    
                    ax2.set_xlabel('SZA')
                    ax1.set_ylabel('RMS')
                    ax2.set_ylabel('DOFS')
                
                    ax1.tick_params(axis='x',which='both',labelsize=8)
                    ax2.tick_params(axis='x',which='both',labelsize=8)  
                    
                    fig.subplots_adjust(right=0.82)
                    cax  = fig.add_axes([0.86, 0.1, 0.03, 0.8])
 
                    cbar = fig.colorbar(sc1, cax=cax,format='%3i')
                    cbar.set_label('DOY')
                    #plt.setp(cbar.ax.get_yticklabels()[-1], visible=False)
                    
                    if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                    else:           plt.show(block=False)

                    #-----------------
                    # RMS and DOF as a function of SZA color coded by Year (if more than 1 year) 
                    #-----------------

                    if yrsFlg:

                        fig,(ax1,ax2)  = plt.subplots(2,1,sharex=True)
                        
                        tcks = range(np.min(years),np.max(years)+2)
                        norm = colors.BoundaryNorm(tcks,cm.N)                       
                        sc1 = ax1.scatter(sza,rms,c=years,cmap=cm,norm=norm)
                        ax2.scatter(sza,dofs,c=years,cmap=cm,norm=norm)   
                            
                        ax1.grid(True,which='both')
                        ax2.grid(True,which='both')                    
                        ax2.set_xlabel('SZA')
                        ax1.set_ylabel('RMS')
                        ax2.set_ylabel('DOFS')
                    
                        ax1.tick_params(axis='x',which='both',labelsize=8)
                        ax2.tick_params(axis='x',which='both',labelsize=8)  
                        
                        fig.subplots_adjust(right=0.82)
                        cax  = fig.add_axes([0.86, 0.1, 0.03, 0.8])
     
                        cbar = fig.colorbar(sc1, cax=cax, ticks=tcks, norm=norm, format='%4i')                           
                        cbar.set_label('Year')
                        plt.setp(cbar.ax.get_yticklabels()[-1], visible=False)
                        
                        if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                        else:           plt.show(block=False)


                    #-----------------
                    # Total Column as a function of SZA and SAA color coded by DOY 
                    #-----------------                   
                    fig,(ax1,ax2)  = plt.subplots(2,1)
                         
                    sc1 = ax1.scatter(sza,totClmn,c=doy,cmap=cm)
                    ax2.scatter(saa,totClmn,c=doy,cmap=cm)

                    ax1.grid(True,which='both')
                    ax2.grid(True,which='both')
                    ax1.set_xlabel('SZA')
                    #ax2.set_xlabel('DOY')
                    ax2.set_xlabel('SAA')
                    ax1.set_ylabel('Total Column')
                    ax2.set_ylabel('Total Column')
                    #ax2.set_ylabel('SZA')
                
                    ax1.tick_params(axis='x',which='both',labelsize=8)
                    ax2.tick_params(axis='x',which='both',labelsize=8)

                    fig.subplots_adjust(right=0.82)
                    cax  = fig.add_axes([0.86, 0.1, 0.03, 0.8])
                    
                    cbar = fig.colorbar(sc1, cax=cax,format='%3i')
                    cbar.set_label('DOY')
                    
                    if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                    else:           plt.show(block=False)

                    #-----------------
                    # Total Column as a function of SZA and SAA color coded by Year (if more than 1 year) 
                    #-----------------                   
                    if yrsFlg:
                        fig,(ax1,ax2)  = plt.subplots(2,1)

                        tcks = range(np.min(years),np.max(years)+2)
                        norm = colors.BoundaryNorm(tcks,cm.N)                       
                        sc1 = ax1.scatter(sza,totClmn,c=years,cmap=cm,norm=norm)
                        ax2.scatter(saa,totClmn,c=years,cmap=cm,norm=norm)
                   
                        ax1.grid(True,which='both')
                        ax2.grid(True,which='both')
                        ax1.set_xlabel('SZA')
                        #ax2.set_xlabel('DOY')
                        ax2.set_xlabel('SAA')
                        ax1.set_ylabel('Total Column')
                        ax2.set_ylabel('Total Column')
                        #ax2.set_ylabel('SZA')
                        
                        ax1.tick_params(axis='x',which='both',labelsize=8)
                        ax2.tick_params(axis='x',which='both',labelsize=8)

                        fig.subplots_adjust(right=0.82)
                        cax  = fig.add_axes([0.86, 0.1, 0.03, 0.8])
                        
                        cbar = fig.colorbar(sc1, cax=cax, ticks=tcks, norm=norm, format='%4i')                           
                        cbar.set_label('Year')
                        plt.setp(cbar.ax.get_yticklabels()[-1], visible=False)
                        
                        if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                        else:           plt.show(block=False)                       

            #------------------------------
            # Plot Errors On (mean) Profile
            #------------------------------
            if errFlg and (gas.lower() == self.PrimaryGas.lower()):   
                if len(self.dirLst) > 1:
                    #-------------------
                    # Plot on total mean
                    #-------------------
                    mnthMean = np.mean(rPrfMol,axis=0)
                    
                    #----------------------------------
                    # Find mean and max error components
                    #----------------------------------
                    rand_std = np.mean(rand_err,axis=0)
                    sys_std  = np.mean(sys_err,axis=0)
                    tot_std  = np.mean(tot_err,axis=0)
                    rand_max = np.max(rand_err,axis=0)
                    sys_max  = np.max(sys_err,axis=0)
                    tot_max  = np.max(tot_err,axis=0)         
                
                #-------------------------------------------------------
                # Plot mean systematic and random errors on mean profile
                #-------------------------------------------------------
                fig,(ax1,ax2)  = plt.subplots(1,2, sharey=True)
                if len(self.dirLst) > 1:
                    ax1.plot(mnthMean,alt,color='k',label=gas+' Retrieved Monthly Mean')
                    ax1.errorbar(mnthMean,alt,fmt='none',xerr=rand_std,ecolor='r',label='Total Random Error')
                    ax1.fill_betweenx(alt,mnthMean-rand_max,mnthMean+rand_max,alpha=0.5,color='0.75')  
                    ax1.set_title('Random Error')
                else:
                    ax1.plot(rPrfMol[0],alt,color='k',label=gas+' Retrieved Profile')
                    ax1.errorbar(rPrfMol[0],alt,fmt='none',xerr=rand_err[0],ecolor='r',label='Total Random Error')
                    ax1.fill_betweenx(alt,rPrfMol[0]-tot_err[0],rPrfMol[0]+tot_err[0],alpha=0.5,color='0.75')
                    ax1.set_title('Errorbars = Random Error\nShadded Region = Total Error',multialignment='center',fontsize=10)
                    
                ax1.set_ylabel('Altitude [km]')
                ax1.set_xlabel('molecules cm$^{-2}$')      
                ax1.grid(True,which='both')                
                
                if len(self.dirLst) > 1:
                    ax2.plot(mnthMean,alt,color='k',label=gas+' Retrieved Monthly Mean')
                    ax2.errorbar(mnthMean,alt,fmt='none',xerr=sys_std,ecolor='r',label='Total Systematic Error')
                    ax2.fill_betweenx(alt,mnthMean-sys_max,mnthMean+sys_max,alpha=0.5,color='0.75')      
                    ax2.set_title('Systematic Error')
                else:
                    ax2.plot(rPrfMol[0],alt,color='k',label=gas+' Retrieved Profile')
                    ax2.errorbar(rPrfMol[0],alt,fmt='none',xerr=sys_err[0],ecolor='r',label='Total Systematic Error')
                    ax2.fill_betweenx(alt,rPrfMol[0]-tot_err[0],rPrfMol[0]+tot_err[0],alpha=0.5,color='0.75')       
                    ax2.set_title('Errorbars = Systematic Error\nShadded Region = Total Error',multialignment='center',fontsize=10)
                
                ax2.set_xlabel('molecules cm$^{-2}$')                                         
                ax2.grid(True,which='both')
                
                if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                else:           plt.show(block=False)                         
                                                 
                if len(self.dirLst) > 1:
                    #-------------------------------------------------------
                    # Plot mean systematic and random errors on mean profile
                    #-------------------------------------------------------
                    fig,ax1  = plt.subplots()
                    ax1.plot(mnthMean,alt,color='k',label=gas+' Retrieved Monthly Mean')
                    ax1.errorbar(mnthMean,alt,fmt='none',xerr=tot_std,ecolor='r',label='Total Error')
                    ax1.fill_betweenx(alt,mnthMean-tot_max,mnthMean+tot_max,alpha=0.5,color='0.75')                
                    ax1.set_title('Total Error')
                    ax1.set_ylabel('Altitude [km]')
                    ax1.set_xlabel('molecules cm$^{-2}$')   
                    ax1.grid(True,which='both')
                    
                    if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                    else:           plt.show(block=False)

                #-------------------------------------------------------
                # Plot individual components of error analysis
                #-------------------------------------------------------
                fig,(ax1,ax2)  = plt.subplots(1,2, sharey=True)
                #---------------------------------
                # Plot systematic error components
                #---------------------------------                
                for k in rand_cmpnts:
                    if len(self.dirLst) > 1:
                        errPlt = np.mean(np.sqrt(rand_cmpnts[k]),axis=0)
                        retPrf = np.mean(rPrfMol,axis=0)
                    else:
                        errPlt = np.sqrt(rand_cmpnts[k][0])
                        retPrf = rPrfMol[0]
                    
                    #-------------------------------------------------
                    # Normalize error as fraction of retrieved profile
                    #-------------------------------------------------
                    errPlt = errPlt / retPrf         
                        
                    ax1.plot(errPlt,alt,linewidth=0.75, label=k)
                    
                #------------------------
                # Plot total random error
                #------------------------
                randMean = np.mean(rand_err,axis=0) / retPrf
                ax1.plot(randMean,alt,linewidth=0.75, label='Total Random Error')                

                ax1.set_ylabel('Altitude [km]')
                ax1.set_xlabel('Fraction of Retrieved Profile')             
                ax1.grid(True,which='both')
                ax1.legend(prop={'size':9})
                
                ax1.tick_params(axis='both',which='both',labelsize=8) 
                ax1.set_title('Random Error Components')               
                
                #-----------------------------
                # Plot random error components
                #-----------------------------
                for k in sys_cmpnts:
                    if len(self.dirLst) > 1:
                        errPlt = np.mean(np.sqrt(sys_cmpnts[k]),axis=0)
                        retPrf = np.mean(rPrfMol,axis=0)
                    else:
                        errPlt = np.sqrt(sys_cmpnts[k][0])
                        retPrf = rPrfMol[0]
                    
                    #-------------------------------------------------
                    # Normalize error as fraction of retrieved profile
                    #-------------------------------------------------
                    errPlt = errPlt / retPrf         
                        
                    ax2.plot(errPlt,alt,linewidth=0.75, label=k)
    
                #------------------------
                # Plot total random error
                #------------------------
                sysMean  = np.mean(sys_err,axis=0) / retPrf
                ax2.plot(sysMean,alt,linewidth=0.75, label='Total Systematic Error')

                ax2.set_xlabel('Fraction of Retrieved Profile')             
                ax2.grid(True,which='both')
                ax2.legend(prop={'size':9})
                
                ax2.tick_params(axis='both',which='both',labelsize=8) 
                ax2.set_title('Systematic Error Components')
                
                if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                else:           plt.show(block=False)                 
                    
                    
                # #---------------------------------------------
                # # Plot individual components of error analysis
                # #---------------------------------------------
                # #-------
                # # Random
                # #-------
                # fig,ax1  = plt.subplots()           
                
                # #---------------------------------
                # # Plot systematic error components
                # #---------------------------------                
                # for k in rand_cmpnts:
                #     if len(self.dirLst) > 1:
                #         errPlt = np.mean(np.sqrt(rand_cmpnts[k]),axis=0)
                #         retPrf = np.mean(rPrfMol,axis=0)
                #     else:
                #         errPlt = rand_cmpnts[k][0]
                #         retPrf = rPrfMol[0]
                    
                #     #-------------------------------------------------
                #     # Normalize error as fraction of retrieved profile
                #     #-------------------------------------------------
                #     errPlt = errPlt / retPrf         
                        
                #     ax1.plot(errPlt,alt,linewidth=0.75, label=k)
                    
                # #------------------------
                # # Plot total random error
                # #------------------------
                # randMean = np.mean(rand_err,axis=0) / retPrf
                # ax1.plot(randMean,alt,linewidth=0.75, label='Total Random Error')                

                # ax1.set_ylabel('Altitude [km]')
                # ax1.set_xlabel('Fraction of Retrieved Profile')             
                # ax1.grid(True,which='both')
                # ax1.legend(prop={'size':9})
                
                # ax1.tick_params(axis='both',which='both',labelsize=8) 
                # ax1.set_title('Random Error Components')
    
                # if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                # else:           plt.show(block=False)   
                
                # #-----------
                # # Systematic
                # #-----------                
                # fig, ax1  = plt.subplots()        
                                
                # #-----------------------------
                # # Plot random error components
                # #-----------------------------
                # for k in sys_cmpnts:
                #     if len(self.dirLst) > 1:
                #         errPlt = np.mean(np.sqrt(sys_cmpnts[k]),axis=0)
                #         retPrf = np.mean(rPrfMol,axis=0)
                #     else:
                #         errPlt = sys_cmpnts[k][0]
                #         retPrf = rPrfMol[0]
                    
                #     #-------------------------------------------------
                #     # Normalize error as fraction of retrieved profile
                #     #-------------------------------------------------
                #     errPlt = errPlt / retPrf         
                        
                #     ax1.plot(errPlt,alt,linewidth=0.75, label=k)
    
                # #------------------------
                # # Plot total random error
                # #------------------------
                # sysMean  = np.mean(sys_err,axis=0) / retPrf
                # ax1.plot(sysMean,alt,linewidth=0.75, label='Total Systematic Error')

                # ax1.set_ylabel('Altitude [km]')
                # ax1.set_xlabel('Fraction of Retrieved Profile')             
                # ax1.grid(True,which='both')
                # ax1.legend(prop={'size':9})
                
                # ax1.tick_params(axis='both',which='both',labelsize=8) 
                # ax1.set_title('Systematic Error Components')
    
                # if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                # else:           plt.show(block=False)

                                   

    def pltAvk(self,fltr=False,minSZA=0.0,maxSZA=80.0,maxRMS=1.0,minDOF=1.0,maxCHI=2.0,minTC=1.0E15,maxTC=1.0E16,mnthFltr=[1,2,3,4,5,6,7,8,9,10,11,12],
               dofFlg=False,errFlg=False,szaFlg=False,partialCols=False,cnvrgFlg=True,pcFlg=True,tcFlg=True,rmsFlg=True,chiFlg=False,tcMMflg=False,mnthFltFlg=False):
        ''' Plot Averaging Kernel. Only for single retrieval '''
        
        print '\nPlotting Averaging Kernel........\n'
        
        if fltr: self.fltrData(self.PrimaryGas,mxrms=maxRMS,minsza=minSZA,mxsza=maxSZA,minDOF=minDOF,maxCHI=maxCHI,minTC=minTC,maxTC=maxTC,mnthFltr=mnthFltr,
                               dofFlg=dofFlg,rmsFlg=rmsFlg,tcFlg=tcFlg,pcFlg=pcFlg,szaFlg=szaFlg,cnvrgFlg=cnvrgFlg,chiFlg=chiFlg,tcMinMaxFlg=tcMMflg,mnthFltFlg=mnthFltFlg)
        else:    self.inds = np.array([]) 
        
        if self.empty: return False    
            
        #-------------------------------------------------
        # Determine if AVK has been created via sfit4 core
        # code or via python error analysis
        #-------------------------------------------------     
        if errFlg:   # Read AVK from error output
            if not any((self.readErrorFlg['vmrFlg'],self.readErrorFlg['avkFlg'])):
                self.readError(totFlg=False,sysFlg=False,randFlg=False,vmrFlg=True,avkFlg=True,KbFlg=False)
            
            if not self.error: 
                print 'No Error output files found for AVK plot...exiting..'
                sys.exit()   
                
            #---------------------
            # Get averaging kernel
            #---------------------   
            if len(self.dirLst) > 1:
                avkSCF  = np.delete(np.asarray(self.error['AVK_scale_factor']),self.inds,axis=0)
                avkVMR  = np.delete(np.asarray(self.error['AVK_vmr']),self.inds,axis=0)                    
                avkSCF  = np.mean(avkSCF,axis=0)    
                avkVMR  = np.mean(avkVMR,axis=0)              
            else:
                avkSCF  = self.error['AVK_scale_factor'][0][:,:]
                avkVMR  = self.error['AVK_vmr'],axis=0[0][:,:]        
                
            dofs    = np.trace(avkSCF)
            dofs_cs = np.cumsum(np.diag(avkSCF)[::-1])[::-1]            
            
        else:        # Read AVK from sfit4 output (only contains scaled AVK)
            avkSCF = []
            for d in self.dirLst:
                lines  = tryopen( d + self.ctl['file.out.ak_matrix'][0])
                if not lines: continue
                avkSCF.append(np.array( [ [ float(x) for x in line.strip().split() ] for line in lines[2:] ] ))
                
            if not self.readPrfFlgApr[self.PrimaryGas]: self.readprfs([self.PrimaryGas],retapFlg=0)   # Apriori Profiles
            
            if len(avkSCF) == 1: 
                avkSCF      = avkSCF[0]
                n_layer     = np.shape(avkSCF)[0]
                Iapriori    = np.zeros((n_layer,n_layer))
                IaprioriInv = np.zeros((n_layer,n_layer))
                np.fill_diagonal(Iapriori,self.aprfs[self.PrimaryGas.upper()])
                np.fill_diagonal(IaprioriInv, 1.0 / (self.aprfs[self.PrimaryGas.upper()]))
                avkVMR      = np.dot(np.dot(Iapriori,avkSCF),IaprioriInv)            
                dofs        = np.trace(avkSCF)
                dofs_cs     = np.cumsum(np.diag(avkSCF)[::-1])[::-1]   
                
            else:                
                avkSCF  = np.asarray(avkSCF)
                nobs    = np.shape(avkSCF)[0]
                n_layer = np.shape(avkSCF)[1]
                avkVMR  = np.zeros((nobs,n_layer,n_layer))
                for obs in range(0,nobs):
                    Iapriori        = np.zeros((n_layer,n_layer))
                    IaprioriInv     = np.zeros((n_layer,n_layer))
                    np.fill_diagonal(Iapriori,self.aprfs[self.PrimaryGas.upper()][obs])
                    np.fill_diagonal(IaprioriInv, 1.0 / (self.aprfs[self.PrimaryGas.upper()][obs]))
                    avkVMR[obs,:,:] = np.dot(np.dot(Iapriori,np.squeeze(avkSCF[obs,:,:])),IaprioriInv)          
                
                avkSCF  = np.delete(avkSCF,self.inds,axis=0)
                avkVMR  = np.delete(avkVMR,self.inds,axis=0)
                avkSCF  = np.mean(avkSCF,axis=0)
                avkVMR  = np.mean(avkVMR,axis=0)
                dofs    = np.trace(avkSCF)
                dofs_cs = np.cumsum(np.diag(avkSCF)[::-1])[::-1]



        #-------------
        # Get Altitude
        #-------------
        if not self.readPrfFlgRet[self.PrimaryGas]: self.readprfs([self.PrimaryGas],retapFlg=1)   # Retrieved Profiles
        alt     = np.asarray(self.rprfs['Z'][0,:])
        Airmass = np.asarray(self.rprfs['AIRMASS'])
        Airmass = np.mean(Airmass, axis=0)
        
        #--------
        # Ploting
        #--------
        #-----------
        # AVK Matrix
        #-----------
        levels1 = np.arange(np.round(np.min(avkSCF),decimals=3),np.round(np.max(avkSCF),decimals=3),0.001)
        levels2 = np.arange(np.round(np.min(avkVMR),decimals=3),np.round(np.max(avkVMR),decimals=3),0.001)
        
        fig,(ax1,ax2) = plt.subplots(1,2,sharey=True)
        cax1          = ax1.contourf(alt,alt,avkSCF,levels1,cmap=mplcm.jet)
        cax2          = ax2.contourf(alt,alt,avkVMR,levels2,cmap=mplcm.jet)
        
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
        
        #-------------------------------------------------
        # Averaging Kernel Smoothing Function (row of avk)
        #-------------------------------------------------
        clmap     = 'jet'
        # Scale Factor AVK
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
            ax.plot(avkSCF[i,:],alt)
            
        ax.set_ylabel('Altitude [km]')
        ax.set_xlabel('Averaging Kernels')
        ax.grid(True)
        cbar = fig.colorbar(scalarMap,orientation='vertical')
        cbar.set_label('Altitude [km]')
        ax.set_title('Averaging Kernels Scale Factor')

        #----------------------------------------
        # Calculate total column averaging kernel
        #----------------------------------------
        AirMinv   = np.diag(1.0/Airmass)

        avkTC    = np.dot(np.dot(Airmass,avkSCF),AirMinv)
        
        #axb.plot(np.sum(avkSCF,axis=0),alt,color='k')
        axb.plot(avkTC, alt,color='k')
        axb.grid(True)
        #axb.set_xlabel('Averaging Kernel Area')
        axb.set_xlabel('Total Column AK')
        #axb.tick_params(axis='x',which='both',labelsize=8)    
        axb.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.1f'))      
        axb.tick_params(axis='x', which='major', labelrotation=45) 

        if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
        else:           plt.show(block=False)         
        
        #----------------------------------------
        # VMR AVK
        #----------------------------------------
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
            ax.plot(avkVMR[i,:],alt)
            
        ax.set_ylabel('Altitude [km]')
        ax.set_xlabel('Averaging Kernels')
        ax.grid(True)
        cbar = fig.colorbar(scalarMap,orientation='vertical')
        cbar.set_label('Altitude [km]')
        ax.set_title('Averaging Kernels VMR')

        avkTCvmr    = np.dot(np.dot(Airmass,avkVMR),AirMinv)
        
        axb.plot(avkTCvmr,alt,color='k')
        #axb.plot(np.sum(avkVMR,axis=0),alt,color='k')
        axb.grid(True)
        axb.set_xlabel('Total Column AK')
        #axb.tick_params(axis='x',which='both',labelsize=8)  
        axb.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.1f'))     
        axb.tick_params(axis='x', which='major',labelrotation=45)  

        if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
        else:           plt.show(block=False)


        #--------------------------------------
        # Plot cumulative sum of DOFs with user 
        # selected partial column area
        #--------------------------------------
        fig,ax1  = plt.subplots()
        ax1.plot(dofs_cs,alt,color='k',label='Cumulative Sum of DOFS (starting at surface)')
        xval = range(0,int(np.ceil(max(dofs_cs)))+2)
        if partialCols:
            for pcol in partialCols: 
                ind1 = nearestind(pcol[0], alt)
                ind2 = nearestind(pcol[1], alt)                
                ax1.fill_between(xval,alt[ind1],alt[ind2],alpha=0.5,color='0.75')  
                ax1.axhline(alt[ind2],color='k',linestyle='--')
                dofsPcol = dofs_cs[ind2] - dofs_cs[ind1]
                ax1.text(0.15,(alt[ind1]+alt[ind2])/2.0, 
                         'DOFs for layer {0:.2f}-{1:.2f}[km] = {2:.3f}'.format(alt[ind1],alt[ind2],dofsPcol),
                         fontsize=9)
        ax1.set_title('DOFs Profile')
        ax1.set_ylabel('Altitude [km]')
        ax1.set_xlabel('Cumulative Sum of DOFS')    
        ax1.set_ylim((0,60))
        ax1.grid(True,which='both')
        ax1.legend(prop={'size':9})
        
        if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
        else:           plt.show(block=False)                         
        
        
    def pltTotClmn(self,fltr=False,minSZA=0.0,maxSZA=80.0,maxRMS=1.0,minDOF=1.0,maxCHI=2.0,minTC=1.0E15,maxTC=1.0E16,mnthFltr=[1,2,3,4,5,6,7,8,9,10,11,12],
                   dofFlg=False,errFlg=False,szaFlg=False,sclfct=1.0,sclname='ppv',
                   partialCols=False,cnvrgFlg=True,pcFlg=True,tcFlg=True,rmsFlg=True,chiFlg=False,tcMMflg=False,mnthFltFlg=False):
        ''' Plot Time Series of Total Column '''
        
        print '\nPrinting Total Column Plots.....\n'
        
        #------------------------------------------
        # Get Profile and Summary information. Need
        # profile info for filtering
        #------------------------------------------
        if not self.readPrfFlgRet[self.PrimaryGas]: self.readprfs([self.PrimaryGas],retapFlg=1)   # Retrieved Profiles
        if not self.readPrfFlgApr[self.PrimaryGas]: self.readprfs([self.PrimaryGas],retapFlg=0)   # Apriori Profiles
        try:    
            if not self.readPrfFlgApr['H2O']:           self.readprfs(['H2O'],retapFlg=0)             # Apriori H2O Profiles
        except: self.readprfs(['H2O'],retapFlg=0)
        if self.empty: return False
        if not self.readsummaryFlg:                 self.readsummary()                            # Summary File info
        if not self.readPbpFlg:                     self.readPbp()                                # Pbp file info
        self.readPbp()
        sza   = self.pbp['sza']
        saa   = self.pbp['saa']
        
        if errFlg:
            if not self.readErrorFlg['totFlg']:
                #-----------------------------------
                # Grab total random error components
                #-----------------------------------
                self.readError(totFlg=True,sysFlg=False,randFlg=False,vmrFlg=False,avkFlg=False,KbFlg=False)
            tempKeys = self.error.keys()
            randErrs = {}
            for k in tempKeys:
                if 'Total random uncertainty' in k: randErrs[k] = np.array(self.error[k])

            # print '***********************'
            # print '   Mean Total Errors   '
            # print '***********************'
            # tempKeys.sort()

            # ind = np.where(np.asarray(self.error['Measurement error (Sm)']) < 300.0)[0]
    
            # for k in tempKeys: 
            #     if not ('Primary gas') in k:
            #         if not ('date') in k: 
                        
            #             print '{:50s}  = {:15.3E}'.format(k, np.mean(np.array(self.error[k])[ind]))
        
        #--------------------
        # Call to filter data
        #--------------------
        if fltr: self.fltrData(self.PrimaryGas,mxrms=maxRMS,minsza=minSZA,mxsza=maxSZA,minDOF=minDOF,maxCHI=maxCHI,minTC=minTC,maxTC=maxTC,mnthFltr=mnthFltr,
                               dofFlg=dofFlg,rmsFlg=rmsFlg,tcFlg=tcFlg,pcFlg=pcFlg,szaFlg=szaFlg,cnvrgFlg=cnvrgFlg,chiFlg=chiFlg,tcMinMaxFlg=tcMMflg,mnthFltFlg=mnthFltFlg)     
        else:    self.inds = np.array([]) 
        
        if self.empty: return False          
        
        #--------------------------
        # Get total column and date
        #--------------------------
        totClmn = np.asarray(self.summary[self.PrimaryGas.upper()+'_RetColmn'])
        dates   = np.asarray(self.summary['date'])

        rms     = np.asarray(self.summary[self.PrimaryGas.upper()+'_FITRMS'])
        dofs    = np.asarray(self.summary[self.PrimaryGas.upper()+'_DOFS_TRG'])
        chi2y   = np.asarray(self.summary[self.PrimaryGas.upper()+'_CHI_2_Y'])
        nbands  = self.nbands
        Airmass = np.asarray(self.rprfs['AIRMASS'])
        rPrf    = np.asarray(self.rprfs[self.PrimaryGas]) * sclfct
        rPrfDry = np.asarray(self.rprfs[self.PrimaryGas]) / (1.0 - np.asarray(self.aprfs['H2O']))* sclfct
        rPrfMol = np.asarray(self.rprfs[self.PrimaryGas]) * Airmass
        alt     = np.asarray(self.rprfs['Z'][0,:])
        
        snr    = {}
        fitsnr = {}
        for i in range(1,nbands+1):
            snr[i]     = np.asarray(self.summary['SNR_'+str(i)])
            fitsnr[i]  = np.asarray(self.summary['FIT_SNR_'+str(i)])

        
        #-----------------
        # Get Total Errors 
        #-----------------
        if errFlg:
            tot_rnd = np.array(self.error['Total random uncertainty'])
            tot_sys = np.array(self.error['Total systematic uncertainty'])
            tot_std = np.sqrt(tot_rnd**2 + tot_sys**2)
                
        #---------------------------------
        # Remove data based on filter inds
        #---------------------------------
        totClmn = np.delete(totClmn,self.inds)
        dates   = np.delete(dates,self.inds)
        rms     = np.delete(rms,self.inds)
        sza     = np.delete(sza,self.inds)
        saa     = np.delete(saa,self.inds)
        dofs    = np.delete(dofs,self.inds)
        chi2y   = np.delete(chi2y,self.inds)
        rPrf    = np.delete(rPrf,self.inds,axis=0)
        rPrfDry = np.delete(rPrfDry,self.inds,axis=0)
        rPrfMol = np.delete(rPrfMol,self.inds,axis=0)
        Airmass = np.delete(Airmass,self.inds,axis=0)
        
        for i in range(1,nbands+1):
            snr[i]     = np.delete(snr[i],self.inds)
            fitsnr[i]  = np.delete(fitsnr[i],self.inds)
        
        if errFlg: 
            tot_std    = np.delete(tot_std,self.inds)
            tot_rnd    = np.delete(tot_rnd,self.inds)
            for k in randErrs:
                randErrs[k] = np.delete(randErrs[k],self.inds)
                randErrs[k] = np.divide(randErrs[k], totClmn) * 100.00  # Convert total random error components to 
   
        #----------------------------
        # DETERMINE FORMAT OF X-AXIS
        #----------------------------

        #----------------------------
        # Determine if multiple years
        #----------------------------
        yrsFlg   = False
        monthFlg = False

        years = [ singDate.year for singDate in dates]      # Find years for all date entries
        
        if len(list(set(years))) > 1:  yrsFlg    = True         # Determine all unique years
        else: 
            months = [ singDate.month for singDate in dates]
            if len(list(set(months))) > 1:  monthFlg    = True
           
        #-----------------
        # Plot time series
        #-----------------
        clmap        = 'jet'
        cm           = plt.get_cmap(clmap)    
        #months       = MonthLocator(bymonth=1,bymonthday=1)

        if yrsFlg: 
            majorLc      = YearLocator()
            majorFmt     = DateFormatter('%Y')
            minorLc      = MonthLocator()
            minorFmt     = DateFormatter('%m')
            xlabel       = 'Year'

        if monthFlg:
            majorLc      = MonthLocator()
            majorFmt     = DateFormatter('%m')
            minorLc      = AutoMinorLocator()  
            minorFmt     = DateFormatter('%d')
            xlabel       = 'Month'

        else:      

            diffDates    = abs((dt.date(dates[0].year, dates[0].month, dates[0].day) - dt.date(dates[-1].year, dates[-1].month, dates[-1].day)).days)

            if diffDates == 0:
                majorLc       = HourLocator()
                majorFmt      = DateFormatter('%H')
                #minorLc       = AutoMinorLocator()
                xlabel        = 'Hour'

            elif (diffDates > 0) and (diffDates <= 4):
                majorLc       = DayLocator(interval=1)
                majorFmt      = DateFormatter('%m/%d')  
                minorLc       = HourLocator()
                xlabel        = 'Day [Hour]'

            elif (diffDates > 4) and (diffDates <= 7):
                majorLc       = DayLocator(interval=1)
                majorFmt      = DateFormatter('%m/%d')  
                minorLc       = AutoMinorLocator()
                xlabel        = 'Day [Hour]'

            elif (diffDates > 7) and (diffDates <= 15):
                majorLc       = DayLocator(interval=2)
                majorFmt      = DateFormatter('%m/%d')  
                minorLc       = DayLocator()
                xlabel        = 'Day [Hour]' 

            elif (diffDates > 15) and (diffDates <= 31):
                majorLc       = DayLocator(interval=4)
                majorFmt      = DateFormatter('%m/%d')  
                minorLc       = DayLocator()
                xlabel        = 'Day [Hour]' 

        #----------------------------
        #             PLOTS
        #----------------------------

        #----------------------------
        # time Series of Retrieved Total Column
        #----------------------------
        fig1,ax1 = plt.subplots()
        ax1.plot(dates,totClmn,'k.',markersize=6)
        ax1.grid(True)
        ax1.set_ylabel('Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
        ax1.set_xlabel(xlabel)
        ax1.set_title('Time Series of Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
        
        if yrsFlg:
            #plt.xticks(rotation=45)
            ax1.xaxis.set_major_locator(majorLc)
            ax1.xaxis.set_minor_locator(minorLc)
            ax1.xaxis.set_major_formatter(majorFmt) 
            ax1.xaxis.set_tick_params(which='major',labelsize=8)
            ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
        else:
            ax1.xaxis.set_major_locator(majorLc)
            ax1.xaxis.set_major_formatter(majorFmt)
            #ax1.xaxis.set_minor_locator(minorLc)
        
        if self.pdfsav: self.pdfsav.savefig(fig1,dpi=200)
        else:           plt.show(block=False)    
                
        #--------------------------------------
        # Plot time series color coded with SZA
        #--------------------------------------    
        tcks = range(np.int(np.floor(np.min(sza))),np.int(np.ceil(np.max(sza)))+2)
        norm = colors.BoundaryNorm(tcks,cm.N)   
        
        fig1,ax1 = plt.subplots()
        ax1.plot(dates,totClmn,'',markersize=0, linestyle='none')
        sc1 = ax1.scatter(dates,totClmn,c=sza,cmap=cm,norm=norm)
        ax1.grid(True)
        ax1.set_ylabel('Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
        ax1.set_xlabel(xlabel)
        ax1.set_title('Time Series of Retrieved Total Column with SZA\n[molecules cm$^{-2}$]',multialignment='center')
        
        if yrsFlg:
            #plt.xticks(rotation=45)
            ax1.xaxis.set_major_locator(majorLc)
            ax1.xaxis.set_minor_locator(minorLc)
            ax1.xaxis.set_major_formatter(majorFmt) 
            ax1.xaxis.set_tick_params(which='major',labelsize=8)
            ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
        else:
            ax1.xaxis.set_major_locator(majorLc)
            ax1.xaxis.set_major_formatter(majorFmt)
            #ax1.xaxis.set_minor_locator(minorLc)
        
        fig1.subplots_adjust(right=0.82)
        cax  = fig1.add_axes([0.86, 0.1, 0.03, 0.8])
            
        cbar = fig1.colorbar(sc1, cax=cax, format='%2i')
        cbar.set_label('SZA')    
        
        if self.pdfsav: self.pdfsav.savefig(fig1,dpi=200)
        else:           plt.show(block=False) 
 
        #--------------------------------------
        # Plot time series color coded with SAA
        #--------------------------------------    
        tcks = range(np.int(np.floor(np.min(saa))),np.int(np.ceil(np.max(saa)))+2)
        norm = colors.BoundaryNorm(tcks,cm.N)
        
        fig1,ax1 = plt.subplots()
        ax1.plot(dates,totClmn,'',markersize=0 ,linestyle='none')
        sc1 = ax1.scatter(dates,totClmn,c=saa,cmap=cm,norm=norm)
        ax1.grid(True)
        ax1.set_ylabel('Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
        ax1.set_xlabel(xlabel)
        ax1.set_title('Time Series of Retrieved Total Column with SAA\n[molecules cm$^{-2}$]',multialignment='center')
        
        if yrsFlg:
            #plt.xticks(rotation=45)
            ax1.xaxis.set_major_locator(majorLc)
            ax1.xaxis.set_minor_locator(minorLc)
            ax1.xaxis.set_major_formatter(majorFmt) 
            ax1.xaxis.set_tick_params(which='major',labelsize=8)
            ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
        else:
            ax1.xaxis.set_major_locator(majorLc)
            ax1.xaxis.set_major_formatter(majorFmt)
            #ax1.xaxis.set_minor_locator(minorLc)
            #fig1.autofmt_xdate()
        
        fig1.subplots_adjust(right=0.82)
        cax  = fig1.add_axes([0.86, 0.1, 0.03, 0.8])
            
        cbar = fig1.colorbar(sc1, cax=cax, format='%2i')
        cbar.set_label('SAA (Relative to North)')    
        
        if self.pdfsav: self.pdfsav.savefig(fig1,dpi=200)
        else:           plt.show(block=False)  

        #--------------------------------------
        # Plot time series color coded with RMS
        #--------------------------------------         
        norm = colors.Normalize( vmin=np.nanmin(rms), vmax=np.nanmax(rms) )
      
        fig1,ax1 = plt.subplots()
        ax1.plot(dates,totClmn,'',markersize=0,  linestyle='none')
        sc1 = ax1.scatter(dates,totClmn,c=rms,cmap=cm,norm=norm)
        ax1.grid(True)
        ax1.set_ylabel('Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
        ax1.set_xlabel(xlabel)
        ax1.set_title('Time Series of Retrieved Total Column with RMS\n[molecules cm$^{-2}$]',multialignment='center')
        
        if yrsFlg:
            #plt.xticks(rotation=45)
            ax1.xaxis.set_major_locator(majorLc)
            ax1.xaxis.set_minor_locator(minorLc)
            ax1.xaxis.set_major_formatter(majorFmt) 
            ax1.xaxis.set_tick_params(which='major',labelsize=8)
            ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
        else:
            ax1.xaxis.set_major_locator(majorLc)
            ax1.xaxis.set_major_formatter(majorFmt)
            #ax1.xaxis.set_minor_locator(minorLc)
        
        fig1.subplots_adjust(right=0.82)
        cax  = fig1.add_axes([0.86, 0.1, 0.03, 0.8])
            
        cbar = fig1.colorbar(sc1, cax=cax)
        cbar.set_label('RMS')    
        
        if self.pdfsav: self.pdfsav.savefig(fig1,dpi=200)
        else:           plt.show(block=False)

        #--------------------------------------
        # Plot time series color coded with DOF
        #--------------------------------------         
        norm = colors.Normalize( vmin=np.nanmin(dofs), vmax=np.nanmax(dofs) )
      
        fig1,ax1 = plt.subplots()
        ax1.plot(dates,totClmn,'',markersize=0 ,linestyle='none')
        sc1 = ax1.scatter(dates,totClmn,c=dofs,cmap=cm,norm=norm)
        ax1.grid(True)
        ax1.set_ylabel('Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
        ax1.set_xlabel(xlabel)
        ax1.set_title('Time Series of Retrieved Total Column with DOF\n[molecules cm$^{-2}$]',multialignment='center')
        
        if yrsFlg:
            #plt.xticks(rotation=45)
            ax1.xaxis.set_major_locator(majorLc)
            ax1.xaxis.set_minor_locator(minorLc)
            ax1.xaxis.set_major_formatter(majorFmt) 
            ax1.xaxis.set_tick_params(which='major',labelsize=8)
            ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
        else:
            ax1.xaxis.set_major_locator(majorLc)
            ax1.xaxis.set_major_formatter(majorFmt)
            #ax1.xaxis.set_minor_locator(minorLc)
        
        fig1.subplots_adjust(right=0.82)
        cax  = fig1.add_axes([0.86, 0.1, 0.03, 0.8])
            
        cbar = fig1.colorbar(sc1, cax=cax)
        cbar.set_label('DOF')    
        
        if self.pdfsav: self.pdfsav.savefig(fig1,dpi=200)
        else:           plt.show(block=False)   

        #-----------------------------------
        # Plot trend analysis of time series
        #-----------------------------------
        # Actual data
        #------------
        try:
            dateYearFrac = toYearFraction(dates)
            weights      = np.ones_like(dateYearFrac)
            res          = fit_driftfourier(dateYearFrac, totClmn, weights, 2)
            f_drift, f_fourier, f_driftfourier = res[3:6]
        
        
            fig1,ax1 = plt.subplots()
            ax1.scatter(dates,totClmn,s=4,label='data')
            ax1.plot(dates,f_drift(dateYearFrac),label='Fitted Anual Trend')
            ax1.plot(dates,f_driftfourier(dateYearFrac),label='Fitted Anual Trend + intra-annual variability')
            ax1.grid(True)
            ax1.set_ylim([np.min(totClmn)-0.1*np.min(totClmn), np.max(totClmn)+0.15*np.max(totClmn)])
            ax1.set_ylabel('Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
            ax1.set_xlabel(xlabel)
            ax1.set_title('Trend Analysis with Boot Strap Resampling\nIndividual Retrievals',multialignment='center')
            ax1.text(0.02,0.94,"Fitted trend -- slope: {0:.3E} ({1:.3f}%)".format(res[1],res[1]/np.mean(totClmn)*100.0),transform=ax1.transAxes)
            ax1.text(0.02,0.9,"Fitted intercept at xmin: {:.3E}".format(res[0]),transform=ax1.transAxes)
            ax1.text(0.02,0.86,"STD of residuals: {0:.3E} ({1:.3f}%)".format(res[6],res[6]/np.mean(totClmn)*100.0),transform=ax1.transAxes) 
            
            if yrsFlg:
                #plt.xticks(rotation=45)
                ax1.xaxis.set_major_locator(majorLc)
                ax1.xaxis.set_minor_locator(minorLc)
                ax1.xaxis.set_major_formatter(majorFmt) 
                ax1.xaxis.set_tick_params(which='major',labelsize=8)
                ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
            else:
                ax1.xaxis.set_major_locator(majorLc)
                ax1.xaxis.set_major_formatter(majorFmt)
                #ax1.xaxis.set_minor_locator(minorLc)
            
            if self.pdfsav: self.pdfsav.savefig(fig1,dpi=200)
            else:           plt.show(block=False)       
  
            #------
            # Daily
            #------
            dailyVals = dailyAvg(totClmn,dates,dateAxis=1, meanAxis=0)
            dateYearFrac = toYearFraction(dailyVals['dates'])
            weights      = np.ones_like(dateYearFrac)
            res          = fit_driftfourier(dateYearFrac, dailyVals['dailyAvg'], weights, 2)
            f_drift, f_fourier, f_driftfourier = res[3:6]
            
            fig1,ax1 = plt.subplots()
            ax1.scatter(dailyVals['dates'],dailyVals['dailyAvg'],s=4,label='data')
            ax1.plot(dailyVals['dates'],f_drift(dateYearFrac),label='Fitted Anual Trend')
            ax1.plot(dailyVals['dates'],f_driftfourier(dateYearFrac),label='Fitted Anual Trend + intra-annual variability')
            ax1.grid(True)
            ax1.set_ylim([np.min(dailyVals['dailyAvg'])-0.1*np.min(dailyVals['dailyAvg']), np.max(dailyVals['dailyAvg'])+0.15*np.max(dailyVals['dailyAvg'])])
            ax1.set_ylabel('Daily Averaged Total Column\n[molecules cm$^{-2}$]',multialignment='center')
            ax1.set_xlabel(xlabel)
            ax1.set_title('Trend Analysis with Boot Strap Resampling\nDaily Averaged Retrievals',multialignment='center')
            ax1.text(0.02,0.94,"Fitted trend -- slope: {0:.3E} ({1:.3f}%)".format(res[1],res[1]/np.mean(dailyVals['dailyAvg'])*100.0),transform=ax1.transAxes)
            ax1.text(0.02,0.9,"Fitted intercept at xmin: {:.3E}".format(res[0]),transform=ax1.transAxes)
            ax1.text(0.02,0.86,"STD of residuals: {0:.3E} ({1:.3f}%)".format(res[6],res[6]/np.mean(dailyVals['dailyAvg'])*100.0),transform=ax1.transAxes)   
        
            if yrsFlg:
                #plt.xticks(rotation=45)
                ax1.xaxis.set_major_locator(majorLc)
                ax1.xaxis.set_minor_locator(minorLc)
                ax1.xaxis.set_major_formatter(majorFmt) 
                ax1.xaxis.set_tick_params(which='major',labelsize=8)
                ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
            else:
                ax1.xaxis.set_major_locator(majorLc)
                ax1.xaxis.set_major_formatter(majorFmt)
                ax1.xaxis.set_minor_locator(minorLc)
                
            if self.pdfsav: self.pdfsav.savefig(fig1,dpi=200)
            else:           plt.show(block=False)            
            
            #--------
            # Monthly
            #--------
            mnthlyVals = mnthlyAvg(totClmn,dates,dateAxis=1, meanAxis=0)
            dateYearFrac = toYearFraction(mnthlyVals['dates'])
            weights      = np.ones_like(dateYearFrac)
            res          = fit_driftfourier(dateYearFrac, mnthlyVals['mnthlyAvg'], weights, 2)
            f_drift, f_fourier, f_driftfourier = res[3:6]
            
            fig1,ax1 = plt.subplots()
            ax1.scatter(mnthlyVals['dates'],mnthlyVals['mnthlyAvg'],s=4,label='data')
            ax1.plot(mnthlyVals['dates'],f_drift(dateYearFrac),label='Fitted Anual Trend')
            ax1.plot(mnthlyVals['dates'],f_driftfourier(dateYearFrac),label='Fitted Anual Trend + intra-annual variability')
            ax1.grid(True)
            ax1.set_ylim([np.min(mnthlyVals['mnthlyAvg'])-0.1*np.min(mnthlyVals['mnthlyAvg']), np.max(mnthlyVals['mnthlyAvg'])+0.15*np.max(mnthlyVals['mnthlyAvg'])])
            ax1.set_ylabel('Monthly Averaged Total Column\n[molecules cm$^{-2}$]',multialignment='center')
            ax1.set_xlabel(xlabel)
            ax1.set_title('Trend Analysis with Boot Strap Resampling\Monthly Averaged Retrievals',multialignment='center')
            ax1.text(0.02,0.94,"Fitted trend -- slope: {0:.3E} ({1:.3f}%)".format(res[1],res[1]/np.mean(mnthlyVals['mnthlyAvg'])*100.0),transform=ax1.transAxes)
            ax1.text(0.02,0.9,"Fitted intercept at xmin: {:.3E}".format(res[0]),transform=ax1.transAxes)
            ax1.text(0.02,0.86,"STD of residuals: {0:.3E} ({1:.3f}%)".format(res[6],res[6]/np.mean(mnthlyVals['mnthlyAvg'])*100.0),transform=ax1.transAxes)  
        
            if yrsFlg:
                #plt.xticks(rotation=45)
                ax1.xaxis.set_major_locator(majorLc)
                ax1.xaxis.set_minor_locator(minorLc)
                ax1.xaxis.set_major_formatter(majorFmt) 
                ax1.xaxis.set_tick_params(which='major',labelsize=8)
                ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
            else:
                ax1.xaxis.set_major_locator(majorLc)
                ax1.xaxis.set_major_formatter(majorFmt)
                ax1.xaxis.set_minor_locator(minorLc)
                
            if self.pdfsav: self.pdfsav.savefig(fig1,dpi=200)
            else:           plt.show(block=False)                 
        
        except: pass 
        
        #------------------------------------
        # Plot time series of partial columns
        #------------------------------------
        if partialCols:
            for pcol in partialCols:
                ind1 = nearestind(pcol[0], alt)
                ind2 = nearestind(pcol[1], alt)               
                vmrP = np.average(rPrf[:,ind2:ind1],axis=1,weights=Airmass[:,ind2:ind1]) 
                vmrPDry = np.average(rPrfDry[:,ind2:ind1],axis=1,weights=Airmass[:,ind2:ind1]) 
                sumP = np.sum(rPrfMol[:,ind2:ind1],axis=1)
                fig,(ax1,ax2)  = plt.subplots(2,1,sharex=True)
                ax1.plot(dates,vmrPDry,'k.',markersize=4)
                ax2.plot(dates,sumP,'k.',markersize=4)
                ax1.grid(True)
                ax2.grid(True)
                ax1.set_ylabel('VMR ['+sclname+'] Dry Air')
                ax2.set_ylabel('Retrieved Partial Column\n[molecules cm$^{-2}$]',multialignment='center')
                ax1.set_title('Partial Column Weighted VMR and molecules cm$^{-2}$\nAltitude Layer '+str(alt[ind1])+'[km] - '+str(alt[ind2])+'[km]',
                              multialignment='center',fontsize=12)
                ax2.set_xlabel(xlabel)
                
                if yrsFlg:
                    #plt.xticks(rotation=45)
                    ax1.xaxis.set_major_locator(majorLc)
                    ax1.xaxis.set_minor_locator(minorLc)
                    ax1.xaxis.set_major_formatter(majorFmt) 
                    ax1.xaxis.set_tick_params(which='major',labelsize=8)
                    ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
                else:
                    ax1.xaxis.set_major_locator(majorLc)
                    ax1.xaxis.set_major_formatter(majorFmt)
                    #ax1.xaxis.set_minor_locator(minorLc)
                
                if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                else:           plt.show(block=False)            
          
        #-------------------------------------
        # Plot time series of Monthly Averages
        #-------------------------------------
        try:
			mnthVals = mnthlyAvg(totClmn,dates,dateAxis=1, meanAxis=0)
	
			fig1,ax1 = plt.subplots()
			ax1.plot(mnthVals['dates'],mnthVals['mnthlyAvg'],'k.',markersize=4)
			ax1.errorbar(mnthVals['dates'],mnthVals['mnthlyAvg'],yerr=mnthVals['std'],fmt='k.',markersize=4,ecolor='grey')
			ax1.grid(True)
			ax1.set_ylabel('Monthly Averaged Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
			ax1.set_xlabel(xlabel)
			ax1.set_title('Monthly Averaged Time Series of Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
		
			if yrsFlg:
				#plt.xticks(rotation=45)
				ax1.xaxis.set_major_locator(majorLc)
				ax1.xaxis.set_minor_locator(minorLc)
				ax1.xaxis.set_major_formatter(majorFmt) 
				ax1.xaxis.set_tick_params(which='major',labelsize=8)
				ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
			else:
				ax1.xaxis.set_major_locator(majorLc)
				ax1.xaxis.set_major_formatter(majorFmt)
				#ax1.xaxis.set_minor_locator(minorLc)

		
			if self.pdfsav: self.pdfsav.savefig(fig1,dpi=200)
			else:           plt.show(block=False)
        except: pass        
        
        #----------------------------------
        # Plot time series with Total Error
        #----------------------------------
        if errFlg:    
            fig1,ax1 = plt.subplots()
            ax1.plot(dates,totClmn,'k.',markersize=4)
            ax1.errorbar(dates,totClmn,yerr=tot_std,fmt='k.',markersize=4,ecolor='red')
            ax1.grid(True)
            ax1.set_ylabel('Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
            ax1.set_xlabel(xlabel)
            ax1.set_title('Time Series of Retrieved Total Column with Total Error\n[molecules cm$^{-2}$]',multialignment='center')
            
            if yrsFlg:
                ax1.xaxis.set_major_locator(majorLc)
                ax1.xaxis.set_minor_locator(minorLc)
                ax1.xaxis.set_major_formatter(majorFmt) 
                ax1.xaxis.set_tick_params(which='major',labelsize=8)
                ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
            else:
                ax1.xaxis.set_major_locator(majorLc)
                ax1.xaxis.set_major_formatter(majorFmt)
                #ax1.xaxis.set_minor_locator(minorLc)
            
            if self.pdfsav: self.pdfsav.savefig(fig1,dpi=200)
            else:           plt.show(block=False)        
            
            #-----------------------------------
            # Plot time series with Random Error
            #-----------------------------------            
            fig1,ax1 = plt.subplots()
            ax1.plot(dates,totClmn,'k.',markersize=4)
            ax1.errorbar(dates,totClmn,yerr=tot_rnd,fmt='k.',markersize=4,ecolor='red')
            ax1.grid(True)
            ax1.set_ylabel('Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
            ax1.set_xlabel(xlabel)
            ax1.set_title('Time Series of Retrieved Total Column with Random Error\n[molecules cm$^{-2}$]',multialignment='center')
            
            if yrsFlg:
                ax1.xaxis.set_major_locator(majorLc)
                ax1.xaxis.set_minor_locator(minorLc)
                ax1.xaxis.set_major_formatter(majorFmt) 
                ax1.xaxis.set_tick_params(which='major',labelsize=8)
                ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
            else:
                ax1.xaxis.set_major_locator(majorLc)
                ax1.xaxis.set_major_formatter(majorFmt)
                #ax1.xaxis.set_minor_locator(minorLc)
            
            if self.pdfsav: self.pdfsav.savefig(fig1,dpi=200)
            else:           plt.show(block=False)              
                           
            #-----------------------------------------------
            # Plot total error as a fraction of total column
            #-----------------------------------------------
            totErr_frac = tot_std / totClmn * 100.0
            ranErr_frac = tot_rnd / totClmn * 100.0
            fig, ax1 = plt.subplots()           
            ax1.plot(dates,totErr_frac,'k.',markersize=4)
            ax1.grid(True)
            ax1.set_ylabel('Total Error as Precentage of Total Column [%]')
            ax1.set_xlabel(xlabel)
            ax1.set_title('Total Error as % of Retrieved Total Column')
            
            if yrsFlg:
                ax1.xaxis.set_major_locator(majorLc)
                ax1.xaxis.set_minor_locator(minorLc)
                ax1.xaxis.set_major_formatter(majorFmt) 
                ax1.xaxis.set_tick_params(which='major',labelsize=8)
                ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
            else:
                ax1.xaxis.set_major_locator(majorLc)
                ax1.xaxis.set_major_formatter(majorFmt)
                #ax1.xaxis.set_minor_locator(minorLc)
            
            if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
            else:           plt.show(block=False)     
            
            #------------------------------------------------
            # Plot random error as a fraction of total column
            #------------------------------------------------
            fig, ax1 = plt.subplots()           
            ax1.plot(dates,ranErr_frac,'k.',markersize=4)
            ax1.grid(True)
            ax1.set_ylabel('Random Error as Precentage of Total Column [%]')
            ax1.set_xlabel(xlabel)
            ax1.set_title('Random Error as % of Retrieved Total Column')
            
            if yrsFlg:
                ax1.xaxis.set_major_locator(majorLc)
                ax1.xaxis.set_minor_locator(minorLc)
                ax1.xaxis.set_major_formatter(majorFmt) 
                ax1.xaxis.set_tick_params(which='major',labelsize=8)
                ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
            else:
                ax1.xaxis.set_major_locator(majorLc)
                ax1.xaxis.set_major_formatter(majorFmt)
                #ax1.xaxis.set_minor_locator(minorLc)
            
            if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
            else:           plt.show(block=False) 
                
        #----------------------------
        # Plot time series of daily SNR, RMS, and DOF
        #----------------------------
        fig, ax = plt.subplots(3,1,sharex=True)
        clr = ('k', 'r', 'b', 'g', 'gray' )

        for i in range(1, nbands+1):
        #for i in range(1, 2):          
            #ax[0].plot(dates,snr[i],'k.', color=clr[i-1], label= 'band '+str(i),markersize=4)
            ax[0].plot(dates, snr[i], 'k.', color=clr[i-1],markersize=4, label='band {}'.format(i))
            #ax[0].errorbar(mnthVals['dates'],mnthVals['mnthlyAvg'],yerr=mnthVals['std'],ecolor=clr[i-1])
            #ax[0].scatter(mnthVals['dates'],mnthVals['mnthlyAvg'],facecolors=clr[i-1], edgecolors='black', s=35,  label='band {}'.format(i))
            #ax[0].set_ylim(0, 5000)
        ax[0].legend(prop={'size':8})
        ax[0].grid(True)
        ax[0].set_ylabel('SNR')
        ax[0].set_title('Time Series of SNR')
        #ax[0].legend(prop={'size':12})

        ax[1].plot(dates ,rms,'k.', markersize=4)
        ax[1].grid(True)
        ax[1].set_title('Time Series of RMS')
        ax[1].set_ylabel('RMS')

        ax[2].plot(dates ,dofs,'k.', markersize=4)
        ax[2].grid(True)
        ax[2].set_title('Time Series of DOF')
        ax[2].set_ylabel('DOF')
        ax[2].set_xlabel(xlabel)
        
        for pp in range(1,3):
        
            if yrsFlg:
                #plt.xticks(rotation=45)
                ax[pp].xaxis.set_major_locator(majorLc)
                ax[pp].xaxis.set_minor_locator(minorLc)
                ax[pp].xaxis.set_major_formatter(majorFmt) 
                ax[pp].xaxis.set_tick_params(which='major',labelsize=8)
                ax[pp].xaxis.set_tick_params(which='minor',labelbottom='off')
            else:
                ax[pp].xaxis.set_major_locator(majorLc)
                ax[pp].xaxis.set_major_formatter(majorFmt)
                #ax[pp].xaxis.set_minor_locator(minorLc)
        
        if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
        else:           plt.show(block=False)   

        #----------------------------
        # Plot time series of Monthly SNR, RMS, and DOF
        #----------------------------
        if len(list(set(months))) > 1:

            fig, ax = plt.subplots(3,1,sharex=True)
            clr = ('k', 'r', 'b', 'g', 'gray' )

            for i in range(1, nbands+1):
            #for i in range(1, 2):
                mnthVals = mnthlyAvg(snr[i],dates,dateAxis=1, meanAxis=0)           
                #ax[0].plot(dates,snr[i],'k.', color=clr[i-1], label= 'band '+str(i),markersize=4)
                ax[0].plot(mnthVals['dates'],mnthVals['mnthlyAvg'],'', linestyle='None', color=clr[i-1],markersize=0)
                ax[0].errorbar(mnthVals['dates'],mnthVals['mnthlyAvg'], linestyle='None', yerr=mnthVals['std'],ecolor=clr[i-1])
                ax[0].scatter(mnthVals['dates'],mnthVals['mnthlyAvg'],facecolors=clr[i-1], edgecolors='black', s=35,  label='band {}'.format(i))
                #ax[0].set_ylim(0, 5000)
            ax[0].legend(prop={'size':8})
            ax[0].grid(True)
            ax[0].set_ylabel('SNR')
            ax[0].set_title('Monthly Averaged Time Series of SNR')
            #ax[0].legend(prop={'size':12})

            mnthVals = mnthlyAvg(rms,dates,dateAxis=1, meanAxis=0) 
            #ax[1].plot(dates,rms,'k.',markersize=4)
            ax[1].plot(mnthVals['dates'],mnthVals['mnthlyAvg'],'',linestyle='None', markersize=0)
            ax[1].errorbar(mnthVals['dates'],mnthVals['mnthlyAvg'],linestyle='None', yerr=mnthVals['std'],ecolor='red')
            ax[1].scatter(mnthVals['dates'],mnthVals['mnthlyAvg'],facecolors='red', edgecolors='black', s=35)
            ax[1].grid(True)
            ax[1].set_title('Monthly Averaged Time Series of RMS')
            ax[1].set_ylabel('RMS')

            mnthVals = mnthlyAvg(dofs,dates,dateAxis=1, meanAxis=0)

            ax[2].plot(mnthVals['dates'],mnthVals['mnthlyAvg'],'',linestyle='None', markersize=0)
            ax[2].errorbar(mnthVals['dates'],mnthVals['mnthlyAvg'],linestyle='None', yerr=mnthVals['std'],ecolor='red')
            ax[2].scatter(mnthVals['dates'],mnthVals['mnthlyAvg'],facecolors='red', edgecolors='black', s=35)
            ax[2].grid(True)
            ax[2].set_title('Monthly Averaged Time Series of DOF')
            ax[2].set_ylabel('DOF')
            ax[2].set_xlabel(xlabel)
     
            for pp in range(1,3):
      
                if yrsFlg:
                    #plt.xticks(rotation=45)
                    ax[pp].xaxis.set_major_locator(majorLc)
                    ax[pp].xaxis.set_minor_locator(minorLc)
                    ax[pp].xaxis.set_major_formatter(majorFmt) 
                    ax[pp].xaxis.set_tick_params(which='major',labelsize=8)
                    ax[pp].xaxis.set_tick_params(which='minor',labelbottom='off')
                else:
                    ax[pp].xaxis.set_major_locator(majorLc)
                    ax[pp].xaxis.set_major_formatter(majorFmt)
                    #ax[pp].xaxis.set_minor_locator(minorLc)

            #fig.subplots_adjust(bottom=0.15,top=0.95, left=0.1, right=0.97)
            
            if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
            else:           plt.show(block=False)       
            
        #----------------------------
        # Plot time series of CHI_2_Y
        #----------------------------
        fig, ax1 = plt.subplots()           
        ax1.plot(dates,chi2y,'k.',markersize=4)
        ax1.grid(True)
        ax1.set_ylabel(r'$\chi_y^{2}$')
        ax1.set_xlabel(xlabel)
        ax1.set_title(r'$\chi_y^{2}$')
        
        if yrsFlg:
            #plt.xticks(rotation=45)
            ax1.xaxis.set_major_locator(majorLc)
            ax1.xaxis.set_minor_locator(minorLc)
            ax1.xaxis.set_major_formatter(majorFmt) 
            ax1.xaxis.set_tick_params(which='major',labelsize=8)
            ax1.xaxis.set_tick_params(which='minor',labelbottom='off')
        else:
            ax1.xaxis.set_major_locator(majorLc)
            ax1.xaxis.set_major_formatter(majorFmt)
            #ax1.xaxis.set_minor_locator(minorLc)
        
        if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
        else:           plt.show(block=False)          

        #--------------------------------------------
        # Plot Histograms (SZA,FITRMS, DOFS, Chi_2_Y)
        #--------------------------------------------
        fig,ax = plt.subplots(2,2)
        
        ax[0,0].hist(sza,histtype='step')
        ax[0,1].hist(rms,histtype='step')
        ax[1,0].hist(dofs,histtype='step')
        ax[1,1].hist(chi2y,histtype='step')
        
        ax[0,0].set_ylabel('Density per bin')
        ax[0,1].set_ylabel('Density per bin')
        ax[1,0].set_ylabel('Density per bin')
        ax[1,1].set_ylabel('Density per bin')
        
        ax[0,0].set_xlabel('Solar Zenith Angle')
        ax[0,1].set_xlabel('Fit RMS')
        ax[1,0].set_xlabel('DOFS')
        ax[1,1].set_xlabel('CHI_2_Y')
        
        ax[0,0].tick_params(axis='both',which='both',labelsize=8)
        ax[1,0].tick_params(axis='both',which='both',labelsize=8)
        ax[0,1].tick_params(axis='both',which='both',labelsize=8)
        ax[1,1].tick_params(axis='both',which='both',labelsize=8)
        
        ax[0,0].set_ylim(bottom=0)
        
        ax[0,0].grid(True)
        ax[0,1].grid(True)
        ax[1,0].grid(True)
        ax[1,1].grid(True)
        
        plt.ylim(ymin=0)
        plt.tight_layout()

        if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
        else:           plt.show(block=False)   
        
        #-----------------------------
        # plot histogram of SNR values
        #-----------------------------
        for i in range(1, nbands+1):
            fig  = plt.figure()
            gs   = gridspec.GridSpec(2,1)
            ax1  = plt.subplot(gs[0])
            ax2  = plt.subplot(gs[1],sharex=ax1)
            
            n1,_,_ = ax1.hist(snr[i],histtype='step')
            n2,_,_ = ax2.hist(fitsnr[i],histtype='step')
            
            ax1.set_ylabel('Density per bin')
            ax2.set_ylabel('Density per bin')
            
            ax1.set_xlabel('Pspec Calculated SNR',fontsize=8)
            ax2.set_xlabel('Fit Residual Calculated SNR',fontsize=8)
            ax1.set_ylim(bottom=0,top=np.max(n1)+10)
            ax2.set_ylim(bottom=0,top=np.max(n2)+10)
            ax1.grid(True)
            ax2.grid(True)
            ax1.tick_params(axis='x',which='both',labelsize=8)
            ax2.tick_params(axis='x',which='both',labelsize=8)
            ax1.tick_params(axis='y',which='both',labelsize=8)
            ax2.tick_params(axis='y',which='both',labelsize=8)            
            ax1.set_title('SNR Histogram for Band = '+str(i), fontsize=10)
            
            #plt.tight_layout()
                        
            if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
            else:           plt.show(block=False)  
        #----------------------------
        # Plot total columns by month
        #----------------------------
        month    = np.array([d.month for d in dates])
        mnthSort = list(set(month))
        mnthMean = np.zeros(len(mnthSort))
        mnthSTD  = np.zeros(len(mnthSort))
        
        for i,m in enumerate(mnthSort):
            inds        = np.where(month == m)[0]
            mnthMean[i] = np.mean(totClmn[inds])
            mnthSTD[i]  = np.std(totClmn[inds])   
            
        fig,ax1  = plt.subplots()
        ax1.plot(mnthSort,mnthMean,'k.',markersize=6)
        ax1.errorbar(mnthSort,mnthMean,yerr=mnthSTD,fmt='k.',markersize=6,ecolor='red')     
        ax1.grid(True,which='both')
        ax1.set_ylabel('Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
        ax1.set_xlabel('Month')
        ax1.set_title('Retrieved Monthly Mean with Standard Deviation')
        ax1.set_xlim((0,13))
        ax1.set_xticks(range(1,13))

        if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
        else:           plt.show(block=False) 

        #--------------------------
        # Plot total columns by DOY
        #--------------------------
        #----------------
        # Get day of year
        #----------------
        doy     = np.array([d.timetuple().tm_yday for d in dates])   
        doyLst  = list(set(doy))
        doyMean = np.zeros(len(doyLst))
        
        for i,day in enumerate(doyLst):
            inds       = np.where(doy == day)[0]
            doyMean[i] = np.mean(totClmn[inds])
            
        fig,ax1  = plt.subplots()
        ax1.plot(doyLst,doyMean,'kx',markersize=6) 
        ax1.grid(True,which='both')
        ax1.set_ylabel('Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
        ax1.set_xlabel('DOY')
        ax1.set_title('Retrieved DOY Mean')
        ax1.set_xlim((0,366))
        #ax1.set_xticks(range(1,366))        
            
        if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
        else:           plt.show(block=False)    
        
        if errFlg:      
            #-------------------------------------
            # Plot % total and random error vs SZA
            #-------------------------------------            
            fig,(ax1,ax2)  = plt.subplots(2,1,sharex=True)
            if yrsFlg:
                tcks = range(np.min(years),np.max(years)+2)
                norm = colors.BoundaryNorm(tcks,cm.N)                        
                sc1  = ax1.scatter(sza,totErr_frac,c=years,cmap=cm,norm=norm)
                ax2.scatter(sza,ranErr_frac,c=years,cmap=cm,norm=norm)
            else:
                #tcks = range(np.min(doy),np.max(doy)+2)
                #norm = colors.BoundaryNorm(tcks,cm.N)                                
                sc1 = ax1.scatter(sza,totErr_frac,c=doy,cmap=cm)
                ax2.scatter(sza,ranErr_frac,c=doy,cmap=cm)      
                
            ax1.grid(True,which='both')
            ax2.grid(True,which='both')   
            ax2.set_xlabel('SZA')
            ax1.set_ylabel('Total Column Error [%]',fontsize=9)
            ax2.set_ylabel('Random Error [%]',fontsize=9)
                    
            ax1.tick_params(axis='x',which='both',labelsize=8)
            ax2.tick_params(axis='x',which='both',labelsize=8)  
            
            fig.subplots_adjust(right=0.82)
            cax  = fig.add_axes([0.86, 0.1, 0.03, 0.8])
            
            if yrsFlg:
                cbar = fig.colorbar(sc1, cax=cax, ticks=tcks, norm=norm, format='%4i')                           
                cbar.set_label('Year')
                plt.setp(cbar.ax.get_yticklabels()[-1], visible=False)
            else:      
                cbar = fig.colorbar(sc1, cax=cax, format='%3i')
                cbar.set_label('DOY')    
                #plt.setp(cbar.ax.get_yticklabels()[-1], visible=False)
            
            if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
            else:           plt.show(block=False)   
            
            #------------------------------------------------
            # Plot fraction of random error components vs SZA
            #------------------------------------------------
            for k in randErrs:
                errLabel = k.strip().split()[-1]
                fig,ax1  = plt.subplots()
                if yrsFlg:
                    tcks = range(np.min(years),np.max(years)+2)
                    norm = colors.BoundaryNorm(tcks,cm.N)                        
                    sc1  = ax1.scatter(sza,randErrs[k],c=years,cmap=cm,norm=norm)
                else:                             
                    sc1 = ax1.scatter(sza,randErrs[k],c=doy,cmap=cm)   
                    
                ax1.grid(True,which='both')
                ax1.set_ylabel('Error of Total Column [%]',fontsize=9)
                ax1.set_xlabel('SZA',fontsize=9)
                ax1.set_title(k)
                ax1.tick_params(axis='x',which='both',labelsize=8)
                
                fig.subplots_adjust(right=0.82)
                cax  = fig.add_axes([0.86, 0.1, 0.03, 0.8])
                
                if yrsFlg:
                    cbar = fig.colorbar(sc1, cax=cax, ticks=tcks, norm=norm, format='%4i')                           
                    cbar.set_label('Year')
                    plt.setp(cbar.ax.get_yticklabels()[-1], visible=False)
                else:      
                    cbar = fig.colorbar(sc1, cax=cax, format='%3i')
                    cbar.set_label('DOY')    
                
                if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                else:           plt.show(block=False)              
        

            #--------------------------------------
            # Plot Measurement error vs SZA and RMS
            #--------------------------------------           
            # These plots do not seem to tell interesting
            # story
            #----------------------------------------------
            #fig,(ax1,ax2)  = plt.subplots(1,2,sharey=True)
            #if yrsFlg:
                #tcks = range(np.min(years),np.max(years)+2)
                #norm = colors.BoundaryNorm(tcks,cm.N)                        
                #sc1  = ax1.scatter(sza,totMeasErr,c=years,cmap=cm,norm=norm)
                #ax2.scatter(rms,totMeasErr,c=years,cmap=cm,norm=norm)
            #else:
                ##tcks = range(np.min(doy),np.max(doy)+2)
                ##norm = colors.BoundaryNorm(tcks,cm.N)                                
                #sc1 = ax1.scatter(sza,totMeasErr,c=doy,cmap=cm)
                #ax2.scatter(rms,totMeasErr,c=doy,cmap=cm)      
                
            #ax1.grid(True,which='both')
            #ax2.grid(True,which='both')   
            #ax2.set_xlabel('SZA')
            #ax1.set_xlabel('RMS')
            #ax1.set_ylabel('Measurement Uncertainty [Fraction of Total Column]')
        
            #ax1.tick_params(axis='x',which='both',labelsize=8)
            #ax2.tick_params(axis='x',which='both',labelsize=8)  
            
            #fig.subplots_adjust(right=0.82)
            #cax  = fig.add_axes([0.86, 0.1, 0.03, 0.8])
            
            #if yrsFlg:
                #cbar = fig.colorbar(sc1, cax=cax, ticks=tcks, norm=norm, format='%4i')                           
                #cbar.set_label('Year')
                #plt.setp(cbar.ax.get_yticklabels()[-1], visible=False)
            #else:      
                #cbar = fig.colorbar(sc1, cax=cax, format='%3i')
                #cbar.set_label('DOY')    
                ##plt.setp(cbar.ax.get_yticklabels()[-1], visible=False)
            
            #if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
            #else:           plt.show(block=False) 

    #def pltSummary(self,errFlg=False):    

    #    if not self.readsummaryFlg:                 self.readsummary()

    #    print self.summary

                     