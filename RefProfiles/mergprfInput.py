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
loc = 'fl0'                                    # Three letter station identifier

#----------------------------------
# Date Range of data to process
# Data processing includes starting
# and ending dates!!
#----------------------------------
# Starting
iyear = 2017               # Year
imnth = 1                 # Month
iday  = 1                  # Day

# Ending
fyear = 2017               # Year
fmnth = 12                 # Month
fday  = 31                # Day

#------
# Flags
#------
npntSkip = 1
Pintrp   = 3
Tintrp   = 2
mvOld    = False           # Flag to rename previous water profile files. (Files appened with .WACCM5)

#------------
# Directories
#------------
#NCEPDir     = '/Users/ebaumer/Data/TestBed2/'
#outBaseDir  = '/Users/ebaumer/Data/TestBed2/'
NCEPDir    = '/data/Campaign/' + loc.upper() + '/NCEP_nmc/'                                # Directory of NCEP nmc data
outBaseDir = '/data1/' + loc.lower() + '/'
#outBaseDir = '/data1/iortega/WYO/'                                                 # Base directory for output


#------
# Files
#------
#WACCMfile = '/Users/ebaumer/Data/TestBed2/WACCM_pTW-meanV5.MLO'
WACCMfile = '/data/Campaign/' + loc.upper() + '/waccm/WACCM_pTW-meanV6.' + loc.upper()     # WACCM monthly mean file
#WACCMfile = '/data/Campaign/FL0/waccm/WACCM_pTW-meanV6.FL0'








