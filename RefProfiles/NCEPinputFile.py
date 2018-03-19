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
loc = 'fl0'                                    # Three letter station identifier

#----------------
# Year to process
#----------------
years = [2017]                                   # Year to process

#------
# Flags
#------
IntrpFileFlg    = False
NonIntrpFileFlg = True


#--------------------
# Base Data Directory
#--------------------
dataDir   = '/data1/ancillary_data/NCEP_NMC/'    # Base directory with all external station data

#------
# Files
#------
#stationlyrs  = '/Users/ebaumer/Data/TestBed2/station.layers'                                # Station layers file
HgtBaseDir      = '/data/Campaign/'+loc.upper()+'/NCEP_nmc/'   # Height nmc data
TempBaseDir     = '/data/Campaign/'+loc.upper()+'/NCEP_nmc/'   # Temp nmc data
IntrpBaseDir    = '/data/Campaign/'+loc.upper()+'/NCEP_nmc/'   # Interpolated Temperatures








