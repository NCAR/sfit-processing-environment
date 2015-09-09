#! /usr/bin/python2.7

#----------------------------------------------------------------------------------------
# Name:
#        read_FL0_EOL_data.py
#
# Purpose:
#       The purpose of this program is to read weather station data for fl0 (eol) from daily
#       netcdf files and convert to yearly ascii tables.
#
# Notes:
#       1)Here is a C language description of the data fields:
#       Note that the data for each day starts at
#       00:00 GMT (6:00 PM Mountain Standard Time)
#
#       int base_time ;			Unix time, seconds since 1970
#       int samp_secs ;			Sample interval in seconds
#       float lat ;			Station Latitude in degrees.fraction
#       float lon ;			Station Longitude in degrees.fraction
#       float alt ;			Station Elevation in meters
#       int station ;			Coastal Climate Weather Station ID
#       float time_offset(time) ;	Sample time after beginning of day
#       float tdry(time) ;		Temperature in degrees C
#       float rh(time) ;		Relative humidity in percent
#       float pres(time) ;		Absolute pressure in millibars
#       float cpres0(time) ;		Aeronautical correctted pressure in mb
#       float dp(time) ;		Dew point temperature in degrees C
#       float wdir(time) ;		Wind direction in degrees from North
#       float wspd(time) ;		Wind speed in meters/sec
#       float wmax(time) ;		Maximum wind speed in meters/sec
#       float wsdev(time) ;		Wind speed standard deviation
#       float wchill(time) ;		Wind chill temperature in degrees C
#       float raina(time) ;		Rain accumulation in millimeters, resets hourly
#       float raina24(time) ;		Rain accumulation in millimeters, resets daily
#       float bat(time) ;		Battery voltage in Volts
#
#
#
# Version History:
#       Created, July, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
#
#
# References:
#
#----------------------------------------------------------------------------------------



                                    #-------------------------#
                                    # Import Standard modules #
                                    #-------------------------#
from scipy.io import netcdf
import os
import datetime as dt
import numpy as np
import sys
import glob
                                    #-------------------------#
                                    # Define helper functions #
                                    #-------------------------#

def ckDir(dirName):
    '''Check if a directory exists'''
    if not os.path.exists( dirName ):
        print 'Input Directory %s does not exist' % (dirName)
        sys.exit()   
        
def ckFile(fName):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print 'File %s does not exist' % (fName)
        sys.exit()

         
                                    #----------------------------#
                                    #                            #
                                    #        --- Main---         #
                                    #                            #
                                    #----------------------------#

def main():
                                    
    #----------------
    # Initializations
    #----------------
    dataDir     = '/Volumes/data1/ancillary_data/fl0/eol/'
    dataFileTag = 'flab'
    fileExtTag  = 'cdf'
    outDataDir  = '/Volumes/data1/ancillary_data/fl0/eol/'
    yearstr     = '2015'

    #--------------------------
    # Initialize variable lists
    #--------------------------
    tempList   = []
    timeList   = []
    rhList     = []
    pressList  = []
    tempDPList = []
    rmind      = []

    #--------------------
    # Search through base 
    # directory for files
    #--------------------
    files = glob.glob(dataDir + 'flab.' + yearstr + '*.' + fileExtTag)
    if not files:
        print 'No files found for year: %s' % yearstr
        sys.exit()
    else:
        print ' %d files found for year: %s' % (len(files),yearstr)
    
    #-------------------------
    # Loop through found files
    #-------------------------
    for indvfile in files:                               
            
        cdfname = netcdf.netcdf_file(indvfile,'r',mmap=False)       # Open netcdf file
        # Get variables
        base_time   = cdfname.variables['base_time']
        time_offset = cdfname.variables['time_offset']
        temp        = cdfname.variables['tdry']
        rh          = cdfname.variables['rh']
        press       = cdfname.variables['pres']
        tempDP      = cdfname.variables['dp']
        cdfname.close()
        
        #----------------------------------
        # Create an actual time vector from
        # basetime and offset (unix time)
        #----------------------------------
        total_time = base_time[()] + time_offset.data
        #total_time = [dt.datetime.utcfromtimestamp(indtime) for indtime in total_time]
        total_time = total_time.tolist()                # Convert numpy array to list
        
        #------------------------------------------------------------
        # There seems to be a timing issue in some of the data files.
        # time_offset can have unusually large numbers. Need to check
        # for this and delete observations.
        #------------------------------------------------------------
        for ind, indvtime in enumerate(total_time):
            # Identify erroneous time_offset values
            try:
                total_time[ind] = dt.datetime.utcfromtimestamp(indvtime)
            except ValueError:
                total_time[ind] = -9999
                rmind.append(ind)
        
        #------------------------------------------------------
        # Remove observations with erroneous time_offset values
        #------------------------------------------------------
        total_time[:] = [item for ind,item in enumerate(total_time) if ind not in rmind]   # List
        temp.data     = np.delete(temp.data,rmind)                                         # Numpy array
        rh.data       = np.delete(rh.data,rmind)                                           # Numpy array
        press.data    = np.delete(press.data,rmind)                                        # Numpy array
        tempDP.data   = np.delete(tempDP.data,rmind)                                       # Numpy array
        
        #---------------------
        # Append to main lists
        #---------------------
        timeList.extend(total_time)
        tempList.extend(temp.data)
        rhList.extend(rh.data)
        pressList.extend(press.data)
        tempDPList.extend(tempDP.data)
                                        
    #------------------------
    # Sort list based on time
    # This returns a tuple
    #------------------------
    timeList, tempList, rhList, pressList, tempDPList = zip(*sorted(zip(timeList, tempList, rhList, pressList, tempDPList)))
                
    #-----------------------------------
    # Construct a vector of string years
    #-----------------------------------
    years  = ["{0:02d}".format(indtime.year) for indtime in timeList]
    months = ["{0:02d}".format(indtime.month) for indtime in timeList]
    days   = ["{0:02d}".format(indtime.day) for indtime in timeList]
    hours  = ["{0:02d}".format(indtime.hour) for indtime in timeList]
    minutes= ["{0:02d}".format(indtime.minute) for indtime in timeList]


    #--------------------------
    # Write data to output file
    #--------------------------
    with open(outDataDir+'fl0_met_data_'+years[0]+'.txt', 'w') as fopen:
        fopen.write('Year Month Day Hour Minute Temperature[C] RelativeHumidity[%] Pressure[mbars] DewPointTemperature[C]\n')
        for line in zip(years,months,days,hours,minutes,tempList,rhList,pressList,tempDPList):
            fopen.write('%-4s %-5s %-3s %-4s %-6s %-14.1f %-19.1f %-15.1f %-22.6f\n' % line)


if __name__ == "__main__":
    main()