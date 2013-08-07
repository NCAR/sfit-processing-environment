#----------------------------------------------------------------------------------------
# Name:
#        <variable>
#
# Purpose:
#       This is the main input file for ckopus. 
#           
#
# Notes:
#       1) The input file is read in as a python file, therefore you should follow python
#          syntax when editing.
#       2) The extension of this file should be .py !!!!
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

#---------------------
# Three letter station
# location
#---------------------
loc = 'mlo'                                    # Three letter station identifier                               

#----------------
# Year to process
#----------------
year = 1992                                    # Year to process

#------
# Flags
#------
IntrpFileFlg    = True
NonIntrpFileFlg = True


#--------------------
# Base Data Directory
#--------------------
dataDir   = '/Users/ebaumer/Data/TestBed2/'    # Base directory with all external station data

#------
# Files
#------
stationlyrs  = '/Users/ebaumer/Data/TestBed2/station.layers'                                # Station layers file
HgtFile      = '/Users/ebaumer/Data/TestBed2/HgtNMC_'+loc.lower()+'_'+str(year)+'.dat'      # Height nmc data
TempFile     = '/Users/ebaumer/Data/TestBed2/TempNMC_'+loc.lower()+'_'+str(year)+'.dat'     # Temp nmc data
IntrpFile    = '/Users/ebaumer/Data/TestBed2/TempIntrp_'+loc.lower()+'_'+str(year)+'.dat'   # Interpolated Temperatures








