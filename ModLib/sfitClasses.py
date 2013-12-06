#----------------------------------------------------------------------------------------
# Name:
#        sfitClass.py
#
# Purpose:
#       This is a collection of classes and functions used in layer 1 processing of sfit4
#
#
# External Subprocess Calls:
#	Only python internal modules called		
#
#
#
# Notes:
#       1) The majority of these classes are related to different types of input files:
#            -- Ctl file
#	     -- Spectral DB file		
#            -- Layer 1 input file
#
#
# Version History:
#       Created, May, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
#
#
# References:
#
#----------------------------------------------------------------------------------------

import datetime
import re
import csv
import itertools
import sys
import subprocess
import numpy as np

                                            #------------------#
                                            # Define functions #
                                            #------------------#
def subProcRun( fname, logFlg=False ):
    '''This runs a system command and directs the stdout and stderr'''
    #rtn = subprocess.Popen( fname, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
    rtn = subprocess.Popen( fname, stderr=subprocess.PIPE )
    outstr = ''
    for line in iter(rtn.stderr.readline, b''):
        print 'STDERR from SFIT4: ' + line.rstrip()
        if logFlg: outstr += line
        
    if logFlg: logFlg.info(outstr)
    
    return True

def nearestDate(daysList, year, month, day=1):
    ''' Finds the nearest date from a list of days based on a given year, month, and day'''
    testDate = datetime.date(year, month, day)
    return min( daysList, key=lambda x:abs(x-testDate) )

def sortDict(DataDict,keyval):
    ''' Sort all values of dictionary based on values of one key'''
    base = DataDict[keyval]
    for k in DataDict:
        DataDict[k] = [y for (x,y) in sorted(zip(base,DataDict[k]))]
    return DataDict

                                                #----------------#
                                                # Define classes #
                                                #----------------#
                                                
#-----------------------------------------------------------------------------------------------                                                
class DateRange:
    '''
    This is an extension of the datetime module.
    Adds functionality to create a list of days.
    '''
    def __init__(self,iyear,imnth,iday,fyear,fmnth,fday, incr=1):
        self.i_date   = datetime.date(iyear,imnth,iday)                                                     # Initial Day
        self.f_date   = datetime.date(fyear,fmnth,fday)                                                     # Final Day
        self.dateList =[self.i_date + datetime.timedelta(days=i) for i in range(0, self.numDays(), incr)]   # Incremental day list from initial to final day
    
    def numDays(self):
        '''Counts the number of days between start date and end date'''
        return (self.f_date + datetime.timedelta(days=1) - self.i_date).days
    
    def inRange(self,crntyear,crntmonth,crntday):
        '''Determines if a specified date is within the date ranged initialized'''
        crntdate = datetime.date(crntyear,crntmonth,crntday)
        if self.i_date <= crntdate <= self.f_date:
            return True
        else:
            return False

    def nearestDate(self, year, month, day=1, daysList=False):
        ''' Finds the nearest date from a list of days based on a given year, month, and day'''
        testDate = datetime.date(year, month, day)
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
        

#-------------------------------------------InputFile-------------------------------------------------------
class InputFile:
    ''' Class for input files with generic method to check the existance of file'''
    def __init__(self,fname,logFile=False):
        self.fname = fname
        try:
            with open(fname): pass
        except IOError as errmsg:
            print 'Unable to find',fname
            if logFile: logFile.error(errmsg)
            sys.exit()         

#----------------------------------------Layer1InputFile-------------------------------------------------------
class Layer1InputFile(InputFile):
    '''
    This class deals with batch processing Layer 1
    input files. Reads in input values. Input file 
    is treated as an actual python script and 
    inputs are read in using execfile
    '''   
    def __init__(self,fname,logFile=False):
        InputFile.__init__(self,fname,logFile)
        self.inputs  = {}
        #try:
            #with open(self.fname): pass
        #except IOError as errmsg:
            #print 'Unable to find',self.fname
            #if self.logFile: self.logFile.error(errmsg)
            #sys.exit()
            
    def getInputs(self,logFile=False):
        ''' Layer 1 input file is treated as a python
            script '''
        try:
            execfile(self.fname, self.inputs)
        except IOError as errmsg:
            print errmsg
            if logFile: logFile.error(errmsg)
            sys.exit()
            
        if '__builtins__' in self.inputs:
            del self.inputs['__builtins__']          
            
#----------------------------------------CtlInputFile-------------------------------------------------------
class CtlInputFile(InputFile):
    '''
    This class deals with reading in ctl files to dictionary and replacing
    values in ctl file
    '''

    def __init__(self,fname,logFile=False):
        InputFile.__init__(self,fname,logFile)
        self.inputs = {}
                   
                   
    def __convrtD(self,rhs):
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
        
        
    def getInputs(self):
        '''Ingests ctl file inputs to a dictionary with the ctl file
           parameter as the key'''
        with open(self.fname) as fopen:
            
            gas_flg = True
            
            for line in fopen:
                
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
                    
                    
                    self.inputs[lhs] = [self.__convrtD(val) for val in rhs]
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
                        #self.inputs[lhs] = rhs
                    
                else:                                                        # Handle multiple line assignments
                    rhs = line.strip().split()             
                    
                    try:
                        rhs = [float(ind) for ind in rhs]
                    except ValueError:
                        pass
                    
                    self.inputs[lhs] += rhs          
                    
                #----------------------    
                # Primary Retrieval Gas
                #----------------------
                # Search for primary retrieval gas in gas.column.list or gas.profile.list
                # The first gas listed is considered the primary retrieval gas
                if gas_flg:
                    match = re.match(r'\s*gas\.\w+\.list\s*=\s*(\w+)', line)
                    if match:
                        self.primGas = match.group(1)
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
        #self.nuUpper = nu[-1]  # Pull off upper wavenumber
        #self.nuLower = nu[0]   # Pull off lower wavenumber
        
    def replVar(self,teststr,repVal):
        '''
        Replaces a value in the ctl file based on parameter name
        '''
        with open(self.fname,'r') as fopen:  
            lines = fopen.readlines()
            
        for i,line in enumerate(lines):
            for singStr,singVal in zip(teststr,repVal):                      # Loop through a list of strings to replace
                if singStr in line and not line.lstrip().startswith('#'):    # Determine if line contains string and is not a comment
                    lines[i] = re.sub(r'=.*', r'= ' + singVal, line)
                    
        with open(self.fname, 'w') as fopen:
            fopen.writelines(lines)
            
#--------------------------------------DbInputFile---------------------------------------------------------
class DbInputFile(InputFile):
    '''
    This class deals with reading and filtering 
    the spectral database file.
    '''    
    def __init__(self,fname,logFile=False):
        ''' Initializations '''
        InputFile.__init__(self,fname,logFile)
        self.dbInputs    = {}
        self.dbFltInputs = {}
            
    def getInputs(self):
        ''' Get db spectral observations and put into a dictionary. We
            Are assuming the first line of db are the keys. Also, assuming
            that the delimiter is a single space. csv reader automatically
            reads everything in as a string. Certain values must be converted
            to floats'''
        with open(self.fname,'rb') as fname:
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

    def dbFilterDate(self,DateRangeClass,fltDict=False):#=self.dbInputs):
        ''' Filter spectral db dicitonary based on date range class previously established'''
        inds = []
        
        if not fltDict:
            fltDict = self.dbInputs
            
        for ind,val in enumerate(fltDict['Date']):
            valstr = str(int(val))
            datestmp = [int(valstr[0:4]),int(valstr[4:6]),int(valstr[6:])]                       # Convert date to integer
            #datestmp = [int(x) for x in val.split('/')]                                         # Convert date to integer (For date delimited by '/'
            if DateRangeClass.inRange(datestmp[0], datestmp[1], datestmp[2]):                    # Check if date stamp in spectral db is within range
                inds.append(ind)
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
            
            DBtime = datetime.datetime(int(date[0:4]),int(date[4:6]),int(date[6:]),int(HH),int(MM),int(SS))
            
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
    
#---------------------------------------GasPrfs--------------------------------------------------------
class GasPrfs(InputFile):
    ''' This class gets the Zbar, P, Airmass and VMR of specified gas for 
        both retrieved and a prior states'''
    
    def __init__(self,rprfsFile,aprfsFile,gas, npFlg=False, logFile=False):
        
        InputFile.__init__(self,rprfsFile,logFile)
        self.rprfsFile = self.fname
        
        InputFile.__init__(self,aprfsFile,logFile)
        self.aprfsFile = self.fname
        
        del self.fname
        
        #---------------------------
        # Get retrieved profile data
        #---------------------------
        with open(rprfsFile,'r') as fopen:
            rprfsLines = fopen.readlines()
        
        rprfsParm = rprfsLines[3].strip().split()
        
        #--------------------------
        # Get a priori profile data
        #--------------------------
        with open(aprfsFile,'r') as fopen:
            aprfsLines = fopen.readlines()
    
        aprfsParm = aprfsLines[3].strip().split()
        
        #------
        # Get Z
        #------
        self.Z = [ float(row.strip().split()[rprfsParm.index('Z')]) for row in rprfsLines[4:] ]        
        if npFlg: self.Z = np.asarray(self.Z)
        
        #---------
        # Get ZBAR
        #---------
        self.Zbar = [ float(row.strip().split()[rprfsParm.index('ZBAR')]) for row in rprfsLines[4:] ]
        if npFlg: self.Zbar = np.asarray(self.Zbar)
        
        #----------------
        # Get Temperature
        #----------------
        self.T = [ float(row.strip().split()[rprfsParm.index('TEMPERATURE')]) for row in rprfsLines[4:] ]   
        if npFlg: self.T = np.asarray(self.T)
        
        #-------------
        # Get Pressure
        #-------------        
        self.P = [ float(row.strip().split()[rprfsParm.index('PRESSURE')]) for row in rprfsLines[4:] ]
        if npFlg: self.P = np.asarray(self.P)
        
        #------------
        # Get Airmass
        #------------        
        self.Airmass = [ float(row.strip().split()[rprfsParm.index('AIRMASS')]) for row in rprfsLines[4:] ]        
        if npFlg: self.Airmass = np.asarray(self.Airmass)
        
        #--------------------------
        # Get gas retrieved profile
        #--------------------------
        self.Rprf = [ float(row.strip().split()[rprfsParm.index(gas.upper())]) for row in rprfsLines[4:] ]
        if npFlg: self.Rprf = np.asarray(self.Rprf)
        
        #-------------------------
        # Get gas a priori profile
        #-------------------------
        self.Aprf = [ float(row.strip().split()[aprfsParm.index(gas.upper())]) for row in aprfsLines[4:] ]        
        if npFlg: self.Aprf = np.asarray(self.Aprf)
                 