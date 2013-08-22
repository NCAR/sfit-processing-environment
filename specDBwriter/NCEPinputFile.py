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
years = [1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002, \
         2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013 ]                                   # Year to process

#------
# Flags
#------
IntrpFileFlg    = False
NonIntrpFileFlg = True


#--------------------
# Base Data Directory
#--------------------
dataDir   = '/data/tools/NCEP_NMC/'    # Base directory with all external station data

#------
# Files
#------
#stationlyrs  = '/Users/ebaumer/Data/TestBed2/station.layers'                                # Station layers file
HgtBaseDir      = '/data/tools/NCEP_NMC/'+loc.lower()+'/'   # Height nmc data
TempBaseDir     = '/data/tools/NCEP_NMC/'+loc.lower()+'/'   # Temp nmc data
IntrpBaseDir    = '/data/tools/NCEP_NMC/'+loc.lower()+'/'   # Interpolated Temperatures








