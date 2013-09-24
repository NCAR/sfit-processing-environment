#----------------------------------------------------------------------------------------
# Name:
#        <variable>
#
# Purpose:
#       This is the main input file for MergPrf.py
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
#       Created, Sept, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
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

#----------------------------------
# Date Range of data to process
# Data processing includes starting
# and ending dates!!
#----------------------------------
# Starting 
iyear = 2006               # Year
imnth = 1                  # Month
iday  = 1                  # Day

# Ending
fyear = 2006               # Year
fmnth = 1                 # Month
fday  = 20                 # Day

#------
# Flags
#------
npntSkip = 1
Pintrp   = 3
Tintrp   = 1

#------------
# Directories
#------------
NCEPDir     = '/Users/ebaumer/Data/TestBed2/'
outBaseDir  = '/Users/ebaumer/Data/TestBed2/'
#NCEPDir    = '/data/Campaign/' + loc.upper() + '/NCEP_nmc/'                                # Directory of NCEP nmc data
#outBaseDir = '/data1/' + loc.lower() + '/'                                                 # Base directory for output

#------
# Files
#------
WACCMfile = '/Users/ebaumer/Data/TestBed2/WACCM_pTW-meanV5.MLO'
#WACCMfile = '/data/Campaign/' + loc.upper() + '/waccm/WACCM_pTW-meanV5.' + loc.upper()     # WACCM monthly mean file








