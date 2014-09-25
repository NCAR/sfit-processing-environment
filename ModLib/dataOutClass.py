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
#       Created, October, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
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
import math
import sys
import numpy as np
import os
import csv
import itertools
from collections import OrderedDict
from os import listdir
from os.path import isfile, join
import re
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
        self.readPbpFlg     = False
        self.readSpectraFlg = False
        self.readsummaryFlg = False
        self.readRefPrfFlg  = False
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


    def fltrData(self,gasName,mxrms=1.0,mxsza=80.0,rmsFlg=True,tcFlg=True,pcFlg=True,cnvrgFlg=True,szaFlg=False):
        
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
            
            sza_inds = np.where(self.pbp['sza'] > mxsza)[0]
            print 'Total number of observations with SZA greater than {0:} = {1:}'.format(mxsza,len(sza_inds))
            self.inds = np.union1d(sza_inds,self.inds)
        
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
            for indMain,sngDir in enumerate(self.dirLst):
    
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
                    indFitSNR= lines[ind2].strip().split().index('FIT_SNR') - 9          # Subtract 9 because INIT_SNR is on seperate line therefore must re-adjust index
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
                    if self.dirFlg: self.summary.setdefault('date',              []).append( self.dirDateTime[indMain] )

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
        retrvdAll   = ['Z','ZBAR','TEMPERATURE','PRESSURE','AIRMASS']   # These profiles will always be retrieved


        if not fname: 
            if   retapFlg == 1: fname = 'rprfs.table'
            elif retapFlg == 0: fname = 'aprfs.table'        


        #--------------------------------------
        # Add user specified retrieved gas list 
        # to standard retrievals
        #--------------------------------------
        retrvdAll.extend(rtrvGasList)
        
        #-----------------------------------
        # Loop through collected directories
        #-----------------------------------
        for indMain,sngDir in enumerate(self.dirLst):       
            
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
                        self.deflt.setdefault(rtrvdSing,[]).append([ float(row.strip().split()[defltParm.index(rtrvdSing.upper())]) for row in defltLines[4:] ] )
    
                    #-------------------------------
                    # Get date and time of retrieval
                    #-------------------------------
                    if self.dirFlg: self.deflt.setdefault('date',     []).append( self.dirDateTime[indMain] )

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
        for gas in rtrvGasList:
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
        for indMain,sngDir in enumerate(self.dirLst):          
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
                if self.dirFlg: self.error.setdefault('date',     []).append( self.dirDateTime[indMain] )

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

        if not fname: fname = 'pbpfile'
        
        #-----------------------------------
        # Loop through collected directories
        #-----------------------------------
        for indMain,sngDir in enumerate(self.dirLst):      
            
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
            nbands = int(lines[1].strip().split()[1])
            
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
            if self.dirFlg: self.pbp.setdefault('date', []).append( self.dirDateTime[indMain] )                            
    
       # if self.dirFlg: self.pbp = sortDict(self.pbp, 'date')
        
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
            if self.dirFlg: self.spc.setdefault('date',     []).append( self.dirDateTime[indMain] )           
                
                
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
    
    def __init__(self,dataDir,ctlF,spcDBfile,statLyrFile,iyear,imnth,iday,fyear,fmnth,fday,incr=1):
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
        self.readprfs([self.PrimaryGas,'H2O'],retapFlg=1)          # Retrieved Profiles
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
        self.HDFsurfP      = np.squeeze(self.refPrf['PRESSURE'][:,-1])                                         # Surface Pressure from Pressure profile
        self.HDFsurfT      = np.squeeze(self.refPrf['TEMPERATURE'][:,-1])                                          # Surface Temperature from temperature profile
        self.HDFh2oVMR     = np.asarray(self.rprfs['H2O'])                                              # Retrieved H2O profile [VMR]
        self.HDFaltBnds    = np.vstack((self.alt[:-1],self.alt[1:]))        

        # Error 
        self.HDFak        = np.asarray(self.error['AVK_vmr'])                                          # Averaging Kernel [VMR/VMR]
        self.HDFsysErr    = np.asarray(self.error['Total_Systematic_Error_VMR'])                       # Total Systematic error covariance matrix [VMR]
        self.HDFrandErr   = np.asarray(self.error['Total_Random_Error_VMR'])                           # Total Random error covariance matrix [VMR]
        self.HDFtcSysErr  = np.asarray(self.error['Total systematic uncertainty'])                     # Total column systematic error [mol cm^-2]
        self.HDFtcRanErr  = np.asarray(self.error['Total random uncertainty'])                         # Total column random error [mol cm^-2]
                        
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
                self.HDFinstAlt = np.array(tempSpecDB['Alt'] / 1000.0)
            self.HDFintT[i] = tempSpecDB['Dur']
            self.HDFazi[i]  = tempSpecDB['SAzm']
            
                
            
    def fltrHDFdata(self,maxRMS,maxSZA,rmsF,tcF,pcF,cnvF,szaF):

        #----------------------------------------------------
        # Print total number of observations before filtering
        #----------------------------------------------------
        print 'Number of total observations before filtering = {}'.format(len(self.HDFdates))
        
        #--------------------
        # Call to filter data
        #--------------------
        self.fltrData(self.PrimaryGas, mxrms=maxRMS, mxsza=maxSZA, rmsFlg=rmsF, tcFlg=tcF,pcFlg=pcF,cnvrgFlg=cnvF,szaFlg=szaF)
        
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
        
#------------------------------------------------------------------------------------------------------------------------------        
class PlotData(ReadOutputData):

    def __init__(self,dataDir,ctlF,iyear=False,imnth=False,iday=False,fyear=False,fmnth=False,fday=False,incr=1,outFname=''):
        primGas = ''
        #------------------------------------------------------------
        # If outFname is specified, plots will be saved to this file,
        # otherwise plots will be displayed to screen
        #------------------------------------------------------------
        if outFname: self.pdfsav = PdfPages(outFname)
        else:        self.pdfsav = False
        
        super(PlotData,self).__init__(dataDir,primGas,ctlF,iyear,imnth,iday,fyear,fmnth,fday,incr)
        
    def closeFig(self):
        self.pdfsav.close()
    
    def pltSpectra(self,fltr=False,maxRMS=1.0):
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
            nlyrs   = int(lines[1].strip().split()[-1])
            nstrt   = int(lines[1].strip().split()[-2])
            JacbMat = np.array( [ [ float(x) for x in line.strip().split()[nstrt:(nstrt+nlyrs)] ] for line in lines[3:] ] )        
        
        #--------------------
        # Call to filter data
        #--------------------
        if fltr: self.fltrData(self.PrimaryGas,mxrms=maxRMS,rmsFlg=True,tcFlg=True,pcFlg=True,cnvrgFlg=True)
        else: self.inds = np.array([]) 
        
        if self.empty: return False
        
        #------------
        # Get spectra
        #------------
        dataSpec = OrderedDict()
        gasSpec  = OrderedDict()
        for x in mw:  # Loop through micro-windows
            dataSpec['Obs_'+x]        = np.delete(self.pbp['Obs_'+x],self.inds,axis=0)
            dataSpec['Fitted_'+x]     = np.delete(self.pbp['Fitted_'+x],self.inds,axis=0)
            dataSpec['Difference_'+x] = np.delete(self.pbp['Difference_'+x]*100.0,self.inds,axis=0)
            dataSpec['WaveN_'+x]      = self.spc['MW_'+x]
            dataSpec['All_'+x]        = np.delete(self.spc['All_'+x],self.inds,axis=0)
            if self.solarFlg: dataSpec['Sol_'+x]        = np.delete(self.spc['Solar_'+x],self.inds,axis=0)
    
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
            gasSpec = {gas.upper()+'_'+x:np.mean(gasSpec[gas.upper()+'_'+x],axis=0) for x in mwList for gas in mwList[x]}   
        else:
            for x in gasSpec: gasSpec[x] = gasSpec[x][0]
 
        #----------------------------------------
        # Plot Jacobian only if there are
        # profile retrievals and single retrieval
        #----------------------------------------
        if ('gas.profile.list' in self.ctl) and self.ctl['gas.profile.list'] and (len(self.dirLst) == 1):
            fig1   = plt.figure()
            gs1    = gridspec.GridSpec(2,numMW,height_ratios=(1,60))
            levels = np.arange(np.round(np.min(JacbMat),decimals=3)-0.001,np.round(np.max(JacbMat),decimals=3)+0.001,0.001)
            ipnt   = 0
            for i,x in enumerate(mwList):
                npnts = np.shape(dataSpec['WaveN_'+x])[0]
                ax    = plt.subplot(gs1[1,i])
                im    = ax.contourf(dataSpec['WaveN_'+x],Z,np.transpose(JacbMat[ipnt:(ipnt+npnts),:]),levels,cmap=mplcm.jet) 
                ipnt += npnts
                ax.grid(True)
                if i == 0: ax.set_ylabel('Altitude [km]')
                ax.xaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    
            fig1.text(0.5,0.04,'Wavenumber [cm$^{-1}$]',ha='center',va='center')
            fig1.autofmt_xdate()
            caxb = fig1.add_axes([0.2,0.9,0.6,0.05])
            fig1.colorbar(im,cax=caxb,orientation='horizontal')
                
            if self.pdfsav: self.pdfsav.savefig(fig1,dpi=200)
            else:           plt.show(block=False)         
 
        #--------------------------------
        # Plot data for each micro-window
        #--------------------------------            
        for x in mwList:
            fig  = plt.figure()
            gs   = gridspec.GridSpec(2,1,height_ratios=[1,3])
            ax1  = plt.subplot(gs[0])
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

            ax2.legend(prop={'size':9},loc='upper center', bbox_to_anchor=(0.5, 1.065),
                      fancybox=True, ncol=len(mwList[x])+3)  
            ax1.tick_params(axis='x',which='both',labelsize=8)
            ax1.tick_params(axis='y',which='both',labelsize=8)
            ax2.tick_params(axis='x',which='both',labelsize=8)
   
            if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
            else:           plt.show(block=False)            
        
    def pltPrf(self,fltr=False,maxRMS=1.0,allGas=True,sclfct=1.0,sclname='ppv',pltStats=True,errFlg=False):
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
        aprPrf[self.PrimaryGas] = np.asarray(self.aprfs[self.PrimaryGas][0,:]) * sclfct
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
        if fltr: self.fltrData(self.PrimaryGas,mxrms=maxRMS,rmsFlg=True,tcFlg=True,pcFlg=True,cnvrgFlg=True)
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
                aprPrf[gas.upper()] = np.asarray(self.aprfs[gas.upper()][0,:]) * sclfct
                rPrf[gas.upper()]   = np.asarray(self.rprfs[gas.upper()]) * sclfct
                localGasList.append(gas)
                
        #----------------------------
        # Remove inds based on filter
        #----------------------------
        nfltr   = len(self.inds)
        rms     = np.delete(rms,self.inds)
        ntot    = len(rms)
        sza     = np.delete(sza,self.inds)
        if len(self.dirLst) > 1: dates   = np.delete(dates,self.inds)
        dofs    = np.delete(dofs,self.inds)
        totClmn = np.delete(totClmn,self.inds)
        rPrfMol = np.delete(rPrfMol,self.inds,axis=0)
        for gas in rPrf:
            rPrf[gas]  = np.delete(rPrf[gas],self.inds,axis=0)
            
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
            prfMean = {gas:np.mean(rPrf[gas],axis=0) for gas in rPrf}
            prfSTD  = {gas:np.std(rPrf[gas],axis=0) for gas in rPrf}
        
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
                ax2.plot(prfMean[gas],alt,color='k',label=gas+' Retrieved Profile Mean')
                ax2.fill_betweenx(alt,prfMean[gas]-prfSTD[gas],prfMean[gas]+prfSTD[gas],alpha=0.5,color='0.75')   
            else:
                ax1.plot(rPrf[gas][0],alt,color='k',label=gas)
                ax2.plot(rPrf[gas][0],alt,color='k',label=gas)
                 
            ax1.plot(aprPrf[gas],alt,color='r',label='A priori')
            ax2.plot(aprPrf[gas],alt,color='r',label='A priori')
            
            ax1.grid(True,which='both')
            ax2.grid(True,which='both')
            
            ax1.legend(prop={'size':9})
            ax2.legend(prop={'size':9})     
            ax1.text(-0.1,1.1, 'Number of Obs Filtered        = '+str(nfltr),ha='left',va='center',transform=ax1.transAxes,fontsize=8)
            ax1.text(-0.1,1.05,'Number of Obs After Filtering = '+str(ntot), ha='left',va='center',transform=ax1.transAxes,fontsize=8)
            
            
            ax1.set_ylabel('Altitude [km]')
            ax1.set_xlabel('VMR ['+sclname+']')
            ax2.set_xlabel('Log Scale VMR ['+sclname+']')
            ax2.set_xscale('log')
            
            ax1.tick_params(axis='x',which='both',labelsize=8)
            ax2.tick_params(axis='x',which='both',labelsize=8)
            plt.suptitle(gas, fontsize=16)

            if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
            else:      plt.show(block=False)   
            
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
    
                ax1.set_color_cycle( [scalarMap.to_rgba(x) for x in rms] )
                ax2.set_color_cycle( [scalarMap.to_rgba(x) for x in rms] )
                
                for i in range(len(rms)):
                    ax1.plot(rPrf[gas][i,:],alt,linewidth=0.75)
                    ax2.plot(rPrf[gas][i,:],alt,linewidth=0.75)
                    
                ax1.plot(aprPrf[gas],alt,'k--',linewidth=4,label='A priori')
                ax2.plot(aprPrf[gas],alt,'k--',linewidth=4,label='A priori')
                
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
    
                ax1.set_color_cycle( [scalarMap.to_rgba(x) for x in sza] )
                ax2.set_color_cycle( [scalarMap.to_rgba(x) for x in sza] )
                
                for i in range(len(sza)):
                    ax1.plot(rPrf[gas][i,:],alt,linewidth=0.75)
                    ax2.plot(rPrf[gas][i,:],alt,linewidth=0.75)
                    
                ax1.plot(aprPrf[gas],alt,'k--',linewidth=4,label='A priori')
                ax2.plot(aprPrf[gas],alt,'k--',linewidth=4,label='A priori')
                
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
    
                ax1.set_color_cycle( [scalarMap.to_rgba(x) for x in month] )
                ax2.set_color_cycle( [scalarMap.to_rgba(x) for x in month] )
                
                for i in range(len(month)):
                    ax1.plot(rPrf[gas][i,:],alt,linewidth=0.75)
                    ax2.plot(rPrf[gas][i,:],alt,linewidth=0.75)
                
                ax1.plot(aprPrf[gas],alt,'k--',linewidth=4,label='A priori')
                ax2.plot(aprPrf[gas],alt,'k--',linewidth=4,label='A priori')
                
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
                
                    fig,ax1  = plt.subplots()
                    ax1.plot(mnthMean,alt,color='k',label='Monthly Mean Profile, Nobs = '+str(len(inds)))
                    ax1.fill_betweenx(alt,mnthMean-mnthSTD,mnthMean+mnthSTD,alpha=0.5,color='0.75')  
                    ax1.plot(aprPrf[gas],alt,color='r',label='A Priori Profile')
                    ax1.set_title('Month = '+str(m))
                    ax1.set_ylabel('Altitude [km]')
                    ax1.set_xlabel('VMR ['+sclname+']')    
                    ax1.grid(True,which='both')
                    ax1.legend(prop={'size':9})
                    
                    if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                    else:           plt.show(block=False)                         
                    
                #-------------------------------------
                # Plot statistics of multiple profiles
                #-------------------------------------
                if pltStats:
                    #-----------------
                    # Get day of year 
                    #-----------------
                    doy   = np.array([d.timetuple().tm_yday for d in dates])
             
                    # Figure 1
                    fig,(ax1,ax2)  = plt.subplots(2,1,sharex=True)
                    if yrsFlg:
                        tcks = range(np.min(years),np.max(years)+2)
                        norm = colors.BoundaryNorm(tcks,cm.N)                        
                        sc1 = ax1.scatter(sza,rms,c=years,cmap=cm,norm=norm)
                        ax2.scatter(sza,dofs,c=years,cmap=cm,norm=norm)
                    else:
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
 
                    if yrsFlg:
                        cbar = fig.colorbar(sc1, cax=cax, ticks=tcks, norm=norm, format='%4i')                           
                        cbar.set_label('Year')
                        plt.setp(cbar.ax.get_yticklabels()[-1], visible=False)
                    else:      
                        cbar = fig.colorbar(sc1, cax=cax,format='%3i')
                        cbar.set_label('DOY')
                        #plt.setp(cbar.ax.get_yticklabels()[-1], visible=False)
                    
                    if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                    else:           plt.show(block=False)                      

                    # Figure 2
                    fig,(ax1,ax2)  = plt.subplots(2,1)
                    ax1.scatter(sza,totClmn)
                    ax2.scatter(doy,sza)
                    ax1.grid(True,which='both')
                    ax2.grid(True,which='both')
                    ax1.set_xlabel('SZA')
                    ax2.set_xlabel('DOY')
                    ax1.set_ylabel('Total Column')
                    ax2.set_ylabel('SZA')
                
                    ax1.tick_params(axis='x',which='both',labelsize=8)
                    ax2.tick_params(axis='x',which='both',labelsize=8)   
                    
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
                    ax1.errorbar(mnthMean,alt,fmt=None,xerr=rand_std,ecolor='r',label='Total Random Error')
                    ax1.fill_betweenx(alt,mnthMean-rand_max,mnthMean+rand_max,alpha=0.5,color='0.75')  
                    ax1.set_title('Random Error')
                else:
                    ax1.plot(rPrfMol[0],alt,color='k',label=gas+' Retrieved Profile')
                    ax1.errorbar(rPrfMol[0],alt,fmt=None,xerr=rand_err[0],ecolor='r',label='Total Random Error')
                    ax1.fill_betweenx(alt,rPrfMol[0]-tot_err[0],rPrfMol[0]+tot_err[0],alpha=0.5,color='0.75')
                    ax1.set_title('Errorbars = Random Error\nShadded Region = Total Error',multialignment='center',fontsize=10)
                    
                ax1.set_ylabel('Altitude [km]')
                ax1.set_xlabel('molecules cm$^{-2}$')      
                ax1.grid(True,which='both')                
                
                if len(self.dirLst) > 1:
                    ax2.plot(mnthMean,alt,color='k',label=gas+' Retrieved Monthly Mean')
                    ax2.errorbar(mnthMean,alt,fmt=None,xerr=sys_std,ecolor='r',label='Total Systematic Error')
                    ax2.fill_betweenx(alt,mnthMean-sys_max,mnthMean+sys_max,alpha=0.5,color='0.75')      
                    ax2.set_title('Systematic Error')
                else:
                    ax2.plot(rPrfMol[0],alt,color='k',label=gas+' Retrieved Profile')
                    ax2.errorbar(rPrfMol[0],alt,fmt=None,xerr=sys_err[0],ecolor='r',label='Total Systematic Error')
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
                    ax1.errorbar(mnthMean,alt,fmt=None,xerr=tot_std,ecolor='r',label='Total Error')
                    ax1.fill_betweenx(alt,mnthMean-tot_max,mnthMean+tot_max,alpha=0.5,color='0.75')                
                    ax1.set_title('Total Error')
                    ax1.set_ylabel('Altitude [km]')
                    ax1.set_xlabel('molecules cm$^{-2}$')   
                    ax1.grid(True,which='both')
                    
                    if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                    else:           plt.show(block=False)              
                    
                    
                #---------------------------------------------
                # Plot individual components of error analysis
                #---------------------------------------------
                #-------
                # Random
                #-------
                fig,ax1  = plt.subplots()           
                
                #---------------------------------
                # Plot systematic error components
                #---------------------------------                
                for k in rand_cmpnts:
                    if len(self.dirLst) > 1:
                        errPlt = np.mean(np.sqrt(rand_cmpnts[k]),axis=0)
                        retPrf = np.mean(rPrfMol,axis=0)
                    else:
                        errPlt = rand_cmpnts[k][0]
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
    
                if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                else:           plt.show(block=False)   
                
                #-----------
                # Systematic
                #-----------                
                fig,ax1  = plt.subplots()        
                                
                #-----------------------------
                # Plot random error components
                #-----------------------------
                for k in sys_cmpnts:
                    if len(self.dirLst) > 1:
                        errPlt = np.mean(np.sqrt(sys_cmpnts[k]),axis=0)
                        retPrf = np.mean(rPrfMol,axis=0)
                    else:
                        errPlt = sys_cmpnts[k][0]
                        retPrf = rPrfMol[0]
                    
                    #-------------------------------------------------
                    # Normalize error as fraction of retrieved profile
                    #-------------------------------------------------
                    errPlt = errPlt / retPrf         
                        
                    ax1.plot(errPlt,alt,linewidth=0.75, label=k)
    
                #------------------------
                # Plot total random error
                #------------------------
                sysMean  = np.mean(sys_err,axis=0) / retPrf
                ax1.plot(sysMean,alt,linewidth=0.75, label='Total Systematic Error')

                ax1.set_ylabel('Altitude [km]')
                ax1.set_xlabel('Fraction of Retrieved Profile')             
                ax1.grid(True,which='both')
                ax1.legend(prop={'size':9})
                
                ax1.tick_params(axis='both',which='both',labelsize=8) 
                ax1.set_title('Systematic Error Components')
    
                if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
                else:           plt.show(block=False)                 
                                   

    def pltAvk(self,fltr=False,maxRMS=1.0,errFlg=False,partialCols=False):
        ''' Plot Averaging Kernel. Only for single retrieval '''
        
        print '\nPlotting Averaging Kernel........\n'
        
        if fltr: self.fltrData(self.PrimaryGas,mxrms=maxRMS,rmsFlg=True,tcFlg=True,pcFlg=True,cnvrgFlg=True)
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
        alt = np.asarray(self.rprfs['Z'][0,:])
        
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
        ax.set_color_cycle([scalarMap.to_rgba(x) for x in alt])
        
        for i in range(len(alt)):
            ax.plot(avkSCF[i,:],alt)
            
        ax.set_ylabel('Altitude [km]')
        ax.set_xlabel('Averaging Kernels')
        ax.grid(True)
        cbar = fig.colorbar(scalarMap,orientation='vertical')
        cbar.set_label('Altitude [km]')
        ax.set_title('Averaging Kernels Scale Factor')
        
        axb.plot(np.sum(avkSCF,axis=0),alt,color='k')
        axb.grid(True)
        axb.set_xlabel('Averaging Kernel Area')
        axb.tick_params(axis='x',which='both',labelsize=8)        

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
        ax.set_color_cycle([scalarMap.to_rgba(x) for x in alt])
        
        for i in range(len(alt)):
            ax.plot(avkVMR[i,:],alt)
            
        ax.set_ylabel('Altitude [km]')
        ax.set_xlabel('Averaging Kernels')
        ax.grid(True)
        cbar = fig.colorbar(scalarMap,orientation='vertical')
        cbar.set_label('Altitude [km]')
        ax.set_title('Averaging Kernels VMR')
        
        axb.plot(np.sum(avkVMR,axis=0),alt,color='k')
        axb.grid(True)
        axb.set_xlabel('Averaging Kernel Area')
        axb.tick_params(axis='x',which='both',labelsize=8)        

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
                ax1.fill_betweenx(xval,pcol[0],pcol[1],alpha=0.5,color='0.75')  
                ind1     = nearestind(pcol[0], alt)
                ind2     = nearestind(pcol[1], alt)
                dofsPcol = dofs_cs[ind2] - dofs_cs[ind1]
                ax1.text(0.15,(pcol[0]+pcol[1])/2.0, 
                         'Approximate DOFs for layer {1:}-{2:}[km] = {3:}'.format(pcol[0],pcol[1],dofsPcol),
                         fontsize=9)
        ax1.set_title('DOFs Profile')
        ax1.set_ylabel('Altitude [km]')
        ax1.set_xlabel('Cumulative Sum of DOFS')    
        ax1.grid(True,which='both')
        ax1.legend(prop={'size':9})
        
        if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
        else:           plt.show(block=False)                         
        
        
    def pltTotClmn(self,fltr=False,maxRMS=1.0,errFlg=False):
        ''' Plot Time Series of Total Column '''
        
        print '\nPrinting Total Column Plots.....\n'
        
        aprPrf = {}
        rPrf   = {}
        
        #------------------------------------------
        # Get Profile and Summary information. Need
        # profile info for filtering
        #------------------------------------------
        if not self.readPrfFlgRet[self.PrimaryGas]: self.readprfs([self.PrimaryGas],retapFlg=1)   # Retrieved Profiles
        if self.empty: return False
        if not self.readsummaryFlg:                 self.readsummary()                            # Summary File info
        if not self.readPbpFlg:                     self.readPbp()                                # Pbp file info
        sza = self.pbp['sza']
        
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
            
        #--------------------
        # Call to filter data
        #--------------------
        if fltr: self.fltrData(self.PrimaryGas,mxrms=maxRMS,rmsFlg=True,tcFlg=True,pcFlg=True,cnvrgFlg=True)
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
        dofs    = np.delete(dofs,self.inds)
        chi2y   = np.delete(chi2y,self.inds)
        for i in range(1,nbands+1):
            snr[i]     = np.delete(snr[i],self.inds)
            fitsnr[i]  = np.delete(fitsnr[i],self.inds)
        
        if errFlg: 
            tot_std    = np.delete(tot_std,self.inds)
            tot_rnd    = np.delete(tot_rnd,self.inds)
            for k in randErrs:
                randErrs[k] = np.delete(randErrs[k],self.inds)
                randErrs[k] = randErrs[k] / totClmn * 100.00  # Convert total random error components to 
            
        #----------------------------
        # Determine if multiple years
        #----------------------------
        years = [ singDate.year for singDate in dates]      # Find years for all date entries
        if len(list(set(years))) > 1: yrsFlg = True         # Determine all unique years
        else:                         yrsFlg = False

        #-----------------
        # Plot time series
        #-----------------
        clmap        = 'jet'
        cm           = plt.get_cmap(clmap)    
        yearsLc      = YearLocator()
        monthsAll    = MonthLocator()
        #months       = MonthLocator(bymonth=1,bymonthday=1)
        months       = MonthLocator()
        DateFmt      = DateFormatter('%m\n%Y')        
        
        fig1,ax1 = plt.subplots()
        ax1.plot(dates,totClmn,'k.',markersize=4)
        ax1.grid(True)
        ax1.set_ylabel('Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
        ax1.set_xlabel('Date [MM]')
        ax1.set_title('Time Series of Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
        
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
        
        #-------------------------------------
        # Plot time series of Monthly Averages
        #-------------------------------------
        mnthVals = mnthlyAvg(totClmn,dates,dateAxis=1, meanAxis=0)
    
        fig1,ax1 = plt.subplots()
        ax1.plot(mnthVals['dates'],mnthVals['mnthlyAvg'],'k.',markersize=4)
        ax1.errorbar(mnthVals['dates'],mnthVals['mnthlyAvg'],yerr=mnthVals['std'],fmt='k.',markersize=4,ecolor='grey')
        ax1.grid(True)
        ax1.set_ylabel('Monthly Averaged Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
        ax1.set_xlabel('Date [MM]')
        ax1.set_title('Monthly Averaged Time Series of Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
        
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
        
        #----------------------------------
        # Plot time series with Total Error
        #----------------------------------
        if errFlg:    
            fig1,ax1 = plt.subplots()
            ax1.plot(dates,totClmn,'k.',markersize=4)
            ax1.errorbar(dates,totClmn,yerr=tot_std,fmt='k.',markersize=4,ecolor='red')
            ax1.grid(True)
            ax1.set_ylabel('Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
            ax1.set_xlabel('Date [MM]')
            ax1.set_title('Time Series of Retrieved Total Column with Total Error\n[molecules cm$^{-2}$]',multialignment='center')
            
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
            
            #-----------------------------------
            # Plot time series with Random Error
            #-----------------------------------            
            fig1,ax1 = plt.subplots()
            ax1.plot(dates,totClmn,'k.',markersize=4)
            ax1.errorbar(dates,totClmn,yerr=tot_rnd,fmt='k.',markersize=4,ecolor='red')
            ax1.grid(True)
            ax1.set_ylabel('Retrieved Total Column\n[molecules cm$^{-2}$]',multialignment='center')
            ax1.set_xlabel('Date [MM]')
            ax1.set_title('Time Series of Retrieved Total Column with Random Error\n[molecules cm$^{-2}$]',multialignment='center')
            
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
                           
            #-----------------------------------------------
            # Plot total error as a fraction of total column
            #-----------------------------------------------
            totErr_frac = tot_std / totClmn * 100.0
            ranErr_frac = tot_rnd / totClmn * 100.0
            fig, ax = plt.subplots()           
            ax.plot(dates,totErr_frac,'k.',markersize=4)
            ax.grid(True)
            ax.set_ylabel('Total Error as Precentage of Total Column [%]')
            ax.set_xlabel('Date [MM]')
            ax.set_title('Total Error as % of Retrieved Total Column')
            
            if yrsFlg:
                #plt.xticks(rotation=45)
                ax.xaxis.set_major_locator(yearsLc)
                ax.xaxis.set_minor_locator(months)
                #ax.xaxis.set_minor_formatter(DateFormatter('%m'))
                ax.xaxis.set_major_formatter(DateFmt) 
                #ax.xaxis.set_tick_params(which='major', pad=15)  
                ax.xaxis.set_tick_params(which='major',labelsize=8)
                ax.xaxis.set_tick_params(which='minor',labelbottom='off')
            else:
                ax.xaxis.set_major_locator(monthsAll)
                ax.xaxis.set_major_formatter(DateFmt)
                ax.set_xlim((dt.date(years[0],1,1), dt.date(years[0],12,31)))
                ax1.xaxis.set_minor_locator(AutoMinorLocator())
                fig.autofmt_xdate()
            
            if self.pdfsav: self.pdfsav.savefig(fig,dpi=200)
            else:           plt.show(block=False)     
            
            #------------------------------------------------
            # Plot random error as a fraction of total column
            #------------------------------------------------
            fig, ax = plt.subplots()           
            ax.plot(dates,ranErr_frac,'k.',markersize=4)
            ax.grid(True)
            ax.set_ylabel('Random Error as Precentage of Total Column [%]')
            ax.set_xlabel('Date [MM]')
            ax.set_title('Random Error as % of Retrieved Total Column')
            
            if yrsFlg:
                #plt.xticks(rotation=45)
                ax.xaxis.set_major_locator(yearsLc)
                ax.xaxis.set_minor_locator(months)
                #ax.xaxis.set_minor_formatter(DateFormatter('%m'))
                ax.xaxis.set_major_formatter(DateFmt) 
                #ax.xaxis.set_tick_params(which='major', pad=15)  
                ax.xaxis.set_tick_params(which='major',labelsize=8)
                ax.xaxis.set_tick_params(which='minor',labelbottom='off')
            else:
                ax.xaxis.set_major_locator(monthsAll)
                ax.xaxis.set_major_formatter(DateFmt)
                ax.set_xlim((dt.date(years[0],1,1), dt.date(years[0],12,31)))
                ax1.xaxis.set_minor_locator(AutoMinorLocator())
                fig.autofmt_xdate()
            
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
        ax1.set_xlabel('Date [MM]')
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
            ax1.set_ylabel('Percent Total Column Error',fontsize=9)
            ax2.set_ylabel('Percent Random Error',fontsize=9)
                    
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
                ax1.set_ylabel('Percent Error of Total Column',fontsize=9)
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
                     