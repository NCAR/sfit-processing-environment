#!/usr/bin/python
##! /usr/local/python-2.7/bin/python

#----------------------------------------------------------------------------------------
# Name:
#        NCEPnmcFormat.py
#
# Purpose:
#       
#           
#
#
# Input files:
#       1) 
#
# Output files:
#       1) 
#
# Called Functions:
#       1) No external called functions (other than system functions)
#
#
# Notes:
#       1) 
#
#
# Usage:
#     appendSpecDB.py -i <File> 
#              -i           Input file for mkSpecDB.py
#
# Examples:
#    ./mkSpecDB.py -i /home/data/DatabaseInputFile.py          -- This runs the program with the input file DatabaseInputFile.py
#
# Version History:
#  1.0     Created, July, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
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
import getopt
import datetime as dt
import itertools as it
from glob import glob
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline as intrpUniSpl
import csv

                        #-------------------------------------#
                        # Define helper functions and classes #
                        #-------------------------------------#
            
                                                     
def usage():
    ''' Prints to screen standard program usage'''
    print 'NCEPnmcFormat.py -i <File>'

        
def ckDir(dirName):
    '''Check if a directory exists'''
    if not os.path.exists( dirName ):
        print 'Directory %s does not exist' % (dirName)
        return False
    else:
        return True
        
def ckFile(fName,exit=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print 'File %s does not exist' % (fName)
        if exit:
            sys.exit()
        return False
    else:
        return True
                
def readNMCFile(fname,dataDict,statstr,dateTime):
    # Determine station string to search for
    if   statstr.lower() == 'mlo': srchstr = 'Mauna L'
    elif statstr.lower() == 'tab': srchstr = 'Thule'
    elif statstr.lower() == 'fl0': srchstr = 'Bolder'
    elif statstr.lower() == 'eur': srchstr = 'Eureka'
    
    #if 'PressureLevels' in dataDict: pFlg = False
    #else: pFlg = True
    
    with open(fname, 'r') as fopen:
        for line in fopen:
            if srchstr in line:
                getlines = list(it.islice(fopen,4,22))
                for getline in getlines:
                    linesplit = getline.strip().split()
                    # Key value is DateTime
                    dataDict.setdefault(dateTime,[]).append(linesplit[2])
                    # Add Pressure levels as Key:value
                    #if pFlg: dataDict.setdefault('PressureLevels',[]).append(linesplit[0])
                    
                #yrstr   = "{0:02d}".format(dateTime.year)
                #mnthstr = "{0:02d}".format(dateTime.month)
                #daystr  = "{0:02d}".format(dateTime.day)                 
                #dataDict.setdefault('YYYYMMDD',[]).append(yrstr+mnthstr+daystr)
                return dataDict
        dataDict.setdefault(dateTime,[]).extend([-999.99]*18)
        return dataDict
            

                            #----------------------------#
                            #                            #
                            #        --- Main---         #
                            #                            #
                            #----------------------------#

def main(argv):
    
    #-----------------------------
    # Initializations and defaults
    #-----------------------------

    
                                                #---------------------------------#
                                                # Retrieve command line arguments #
                                                #---------------------------------#
    #------------------------------------------------------------------------------------------------------------#                                             
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:D:')

    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit()
        
    #-----------------------------
    # Parse command line arguments
    #-----------------------------
    for opt, arg in opts:
        
        #-----------
        # Input file
        #-----------
        if opt == '-i':           
            inputFile = arg
            
            # Check if file exists
            ckFile(inputFile,True)
            
        #------------------
        # Unhandled options
        #------------------
        else:
            print 'Unhandled option: ' + opt
            usage()
            sys.exit()
    #------------------------------------------------------------------------------------------------------------#                       
       
    #----------------
    # Read input file
    #----------------
    inputs = {}
    execfile(inputFile, inputs)
    if '__builtins__' in inputs:
        del inputs['__builtins__']       
        
    #-----------------------------------
    # Check the existance of directories
    # and files given in input file
    #-----------------------------------
    # Check base directory of NCEP nmc data
    if 'dataDir' in inputs and inputs['dataDir']:                           
        if not ckDir(inputs['dataDir']):
            sys.exit()
        # check if '/' is included at end of path
        if not( inputs['dataDir'].endswith('/') ):
            inputs['dataDir'] = inputs['dataDir'] + '/'    

    # Check for station layer file if doing interpolation 
    if inputs['IntrpFileFlg']: ckFile(inputs['stationlyrs'],True)
       
    #-------------------
    # Loop through years
    #-------------------
    for curYear in inputs['years']:
       
        #-------------------------------
        # Open and read nmc height files
        #-------------------------------
        nmcHgtFiles = glob( inputs['dataDir'] + 'height' + '/' + str(curYear) + '/ht*.nmc')
        
        if len(nmcHgtFiles) == 0:
            print 'No .nmc files found in: '+ inputs['dataDir'] + 'height' + '/' + str(curYear)
            sys.exit()
            
        nmcHgtData  = {}
        
        for hgtfile in nmcHgtFiles:        
            _,hgtFname = os.path.split(hgtfile) 
            year = int(curYear)
            
            dateTime   = dt.date(year,int(hgtFname[4:6]),int(hgtFname[6:8]))
            nmcHgtData = readNMCFile(hgtfile,nmcHgtData,inputs['loc'],dateTime)
    
        #------------------------------------
        # Open and read nmc TEmperature files
        #------------------------------------
        nmcTempFiles = glob( inputs['dataDir'] + 'temp' + '/' + str(curYear) + '/te*.nmc')
        nmcTempData  = {}
        
        for TempFile in nmcTempFiles:        
            _,TempFname = os.path.split(TempFile) 
            year = int(curYear)
            
            dateTime   = dt.date(year,int(TempFname[4:6]),int(TempFname[6:8]))
            nmcTempData = readNMCFile(TempFile,nmcTempData,inputs['loc'],dateTime)
    
        #-----------------------------------------------
        # Interpolate Temperature data to station layers
        #-----------------------------------------------
        if inputs['IntrpFileFlg']:
            # Read station layers file
            statLayers = []
            
            with open(inputs['stationlyrs'],'r') as fopen:
                for line in fopen:
                    if 'level' in line: 
                        getlines = list(it.islice(fopen,0,None))
                        
                        for getline in getlines:
                            linesplit = getline.strip().split()
                            # Grab station levels 1=top level, 2=thickness,3 = growth, -1 or 4= midpoint
                            statLayers.append(float(linesplit[1]))
                            
            statLayers.sort()
            
            # Get Xnew
            statLayers = np.array(statLayers)
            
            #------------------------------
            # Loop through daily nmc values
            #------------------------------
            TempNewDict = {}
            for datekey in nmcHgtData:
                try:
                    TempData = np.array(map(float,nmcTempData[datekey]))
                    HgtData  = (np.array(map(float, nmcHgtData[datekey]))) / 1000   # Convert [m] -> [km]
                    #-------------------------------------------------------
                    # The temperature and height data is read in starting at
                    # highest point going to lowest point. This needs to be 
                    # reversed for the interpolation. Must be increasing.
                    #-------------------------------------------------------
                    TempData = TempData[::-1]
                    HgtData  = HgtData[::-1]
                    
                    
                except KeyError:
                    continue
                
                #-------------------------------------------------
                # Create new temperature profiles based on station
                # layers and nmc data. Use Interpolated Univariate
                # Spline
                #-------------------------------------------------
                TempNewDict.setdefault(datekey,[]).extend(intrpUniSpl(HgtData,TempData,k=3)(statLayers))
    
                   
        #------------------------------------------
        # Write files: nmc_height, nmc_temperature,
        # interpolated_temperature
        #------------------------------------------
        strformat = [' {'+str(i)+':<10}' for i in range(0,19)]
        strformat = ''.join(strformat).lstrip() + '\n'
        
        if inputs['NonIntrpFileFlg']:
            #----------------
            # NMC height file
            #----------------
            with open(inputs['HgtBaseDir']+'HgtNMC_'+inputs['loc'].lower()+'_'+str(year)+'.dat' , 'w') as fopen:
                # Write header
                fopen.write('#   LABEL                       Units          Column    Missing Value\n')
                fopen.write('#---------------------------------------------------------------------\n')
                fopen.write('#   Date                        YYYYMMDD       1         NA           \n')
                fopen.write('#   Height at 0.4mb             m              2         -999         \n')
                fopen.write('#   Height at 1mb               m              3         -999         \n')
                fopen.write('#   Height at 2mb               m              4         -999         \n')
                fopen.write('#   Height at 5mb               m              5         -999         \n')
                fopen.write('#   Height at 10mb              m              6         -999         \n')
                fopen.write('#   Height at 30mb              m              7         -999         \n')
                fopen.write('#   Height at 50mb              m              8         -999         \n')
                fopen.write('#   Height at 70mb              m              9         -999         \n')
                fopen.write('#   Height at 100mb             m              10        -999         \n')
                fopen.write('#   Height at 150mb             m              11        -999         \n')
                fopen.write('#   Height at 200mb             m              12        -999         \n')
                fopen.write('#   Height at 250mb             m              13        -999         \n')
                fopen.write('#   Height at 300mb             m              14        -999         \n')
                fopen.write('#   Height at 400mb             m              15        -999         \n')
                fopen.write('#   Height at 500mb             m              16        -999         \n')
                fopen.write('#   Height at 700mb             m              17        -999         \n')
                fopen.write('#   Height at 850mb             m              18        -999         \n')
                fopen.write('#   Height at 1000mb            m              19        -999         \n')
                fopen.write('#---------------------------------------------------------------------\n')
    
                for k,val in iter(sorted(nmcHgtData.iteritems())):
                    
                    YYYYMMDD = "{0:02d}".format(k.year)+"{0:02d}".format(k.month)+"{0:02d}".format(k.day) 
                    val.insert(0,YYYYMMDD)
                    fopen.write(strformat.format(*val))    
                    
            #--------------                
            # NMC Temp file
            #--------------
            with open(inputs['TempBaseDir']+'TempNMC_'+inputs['loc'].lower()+'_'+str(year)+'.dat', 'w') as fopen:
                # Write header
                fopen.write('#   LABEL                       Units          Column    Missing Value\n')
                fopen.write('#---------------------------------------------------------------------\n')
                fopen.write('#   Date                        YYYYMMDD       1         NA           \n')
                fopen.write('#   Temperature at 0.4mb        C              2         -999         \n')
                fopen.write('#   Temperature at 1mb          C              3         -999         \n')
                fopen.write('#   Temperature at 2mb          C              4         -999         \n')
                fopen.write('#   Temperature at 5mb          C              5         -999         \n')
                fopen.write('#   Temperature at 10mb         C              6         -999         \n')
                fopen.write('#   Temperature at 30mb         C              7         -999         \n')
                fopen.write('#   Temperature at 50mb         C              8         -999         \n')
                fopen.write('#   Temperature at 70mb         C              9         -999         \n')
                fopen.write('#   Temperature at 100mb        C              10        -999         \n')
                fopen.write('#   Temperature at 150mb        C              11        -999         \n')
                fopen.write('#   Temperature at 200mb        C              12        -999         \n')
                fopen.write('#   Temperature at 250mb        C              13        -999         \n')
                fopen.write('#   Temperature at 300mb        C              14        -999         \n')
                fopen.write('#   Temperature at 400mb        C              15        -999         \n')
                fopen.write('#   Temperature at 500mb        C              16        -999         \n')
                fopen.write('#   Temperature at 700mb        C              17        -999         \n')
                fopen.write('#   Temperature at 850mb        C              18        -999         \n')
                fopen.write('#   Temperature at 1000mb       C              19        -999         \n')
                fopen.write('#---------------------------------------------------------------------\n')
    
                for k,val in iter(sorted(nmcTempData.iteritems())):
                    
                    YYYYMMDD = "{0:02d}".format(k.year)+"{0:02d}".format(k.month)+"{0:02d}".format(k.day) 
                    #---------------------------------------------------------------------------
                    # According to temp_adjustment.doc, the temperature needs to be adjusted for
                    # for the upper part of the atmosphere:
                    # Period 10: 9/20/88 to 4/30/2001
                    #
                    # ******************************
                    # **  5MB  ------------  2.2  **
                    # **  2MB  ------------ -2.4  **
                    # **  1MB  ------------ -6.2  **
                    # ** .4MB  ------------  3.5  **
                    # ******************************
                    #
                    #---------------------------------------------------------------------------
                    if dt.date(1998,9,20) <= k <= dt.date(2001,4,30):
                        val[0:4] = [float(tval) for tval in val[0:4]]
                        
                        if val[0] != -999: val[0] +=  3.5
                        if val[1] != -999: val[1] += -6.2
                        if val[2] != -999: val[2] += -2.4
                        if val[3] != -999: val[3] +=  2.2
                       
                        val[0:4] = [str(tval) for tval in val[0:4]]
                        
                    val.insert(0,YYYYMMDD)
                    fopen.write(strformat.format(*val))         
     
            #------------------------------
            # Interpolated temperature file
            #------------------------------
            if inputs['IntrpFileFlg']:
                strformat = [' {'+str(i)+':<10}' for i in range(0,len(statLayers)+1)]
                strformat = ''.join(strformat).lstrip() + '\n'
                
                with open(inputs['IntrpBaseDir']+'TempIntrp_'+inputs['loc'].lower()+'_'+str(year)+'.dat', 'w') as fopen:
                    # Write header
                    header = [ str(layer)+' km' for layer in statLayers]
                    header.insert(0,'YYYYMMDD')
                    fopen.write(strformat.format(*header))
                
                    for k,val in iter(sorted(TempNewDict.iteritems())):
                        
                        val      = [str(round(v,2)) for v in val] 
                        YYYYMMDD = "{0:02d}".format(k.year)+"{0:02d}".format(k.month)+"{0:02d}".format(k.day) 
                        val.insert(0,YYYYMMDD)
                        fopen.write(strformat.format(*val))                    
                
                                                                              
if __name__ == "__main__":
    main(sys.argv[1:])