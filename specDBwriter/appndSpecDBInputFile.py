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
loc = 'tab'                                    # Three letter station identifier                               

#----------------
# Year to process
#----------------
year = 1999                                    # Year to process

#------
# Flags
#------
readableFlg = True                             # Flag to create human readable DB
csvFlg      = True                             # Flag to create comma seperated DB

#------------
# directories
#------------
#statDir   = '/data/tools/gsfc/mlo/cmdl/Minute_Data/'   # Base directory with all external station data (mlo)
#statDir   = '/data/tools/gsfc/fl0/eol/'                # Base directory with all external station data (fl0)
statDir    = ''                                         # TAB has no external station data -- set to empty string

#------
# Files
#------
specDBFile         = '/data/Campaign/'+loc.upper()+'/Spectral_DB/spDB_'+loc.lower()+'_'+str(year)+'.dat'           # Old spectral database file
readableSpecDBFile = '/data/Campaign/'+loc.upper()+'/Spectral_DB/HRspDB_'+loc.lower()+'_'+str(year)+'.dat'         # Easily readable new spectral database file
csvSpecDBFile      = '/data/Campaign/'+loc.upper()+'/Spectral_DB/CSVspDB_'+loc.lower()+'_'+str(year)+'.dat'        # CSV new spectral database
houseFile          = '/data/Campaign/'+loc.upper()+'/House_Log_Files/'+loc.upper()+'_HouseData_'+str(year)+'.dat'  # Yearly house data file

#----------------------
# Number of minutes to
# include for averaging
#----------------------
#nminsStation = 10       # Number of minutes for averaging Temperature, Pressure, and RH from external station data (MLO)
nminsStation = 90        # Number of minutes for averaging Temperature, Pressure, and RH from external station data (TAB)
nminsHouse   = 10        # Number of minutes for averaging Temperature, Pressure, and RH from House log data 








