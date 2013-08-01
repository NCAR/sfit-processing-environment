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
year = 1999                                    # Year to process

#------
# Flags
#------
readableFlg = True
csvFlg      = True

#------------
# directories
#------------
statDir   = '/Users/ebaumer/Data/TestBed2/mlo/'    # Base directory with all external station data

#------
# Files
#------
specDBFile         = '/Users/ebaumer/Data/TestBed2/mlo/spDB_'+loc.lower()+'_'+str(year)+'.dat'           # Old spectral database file
readableSpecDBFile = '/Users/ebaumer/Data/TestBed2/mlo/HRspDB_'+loc.lower()+'_'+str(year)+'.dat'         # Easily readable new spectral database file
csvSpecDBFile      = '/Users/ebaumer/Data/TestBed2/mlo/CSVspDB_'+loc.lower()+'_'+str(year)+'.dat'        # CSV new spectral database
houseFile          = '/Users/ebaumer/Data/TestBed2/mlo/'+loc.upper()+'_HouseData_'+str(year)+'.dat'      # Yearly house data file

#----------------------
# Number of minutes to
# include for averaging
#----------------------
nmins = 10                                     # Number of minutes for averaging Temperature, Pressure, and RH








