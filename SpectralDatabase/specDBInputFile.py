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
loc = 'bre'                                                                     lat = 53
lon = -8
alt = 27
utc = +1

#----------------------------------
# Date Range of data to process
# Data processing includes starting
# and ending dates!!
#----------------------------------
# Starting 
iyear = 1995               # Year
imnth = 1                  # Month
iday  = 1                  # Day

# Ending
fyear = 1995               # Year
fmnth = 12                 # Month
fday  = 31                 # Day


#------------
# directories
#------------
dataBaseDir   = '/Volumes/data1/mlo/'                            # Base directory for OPUS data
DaysProcDir   = '/Volumes/data/Campaign/MLO/Spectral_DB/Test/'   # Path to write file that contains list of all folders processed

#------
# Files
#------
outputDBfile  = '/Volumes/data/Campaign/MLO/Spectral_DB/Test/spDB_'+loc+'_'+str(iyear)+'.dat'  # Path and filename of spectral database file
Fckopus       = '/Users/ebaumer/Code/sfit-ckopus/ckopus'                                       # ckopus executable file

#----------------------
# General Logical Flags
#----------------------
DaysProcFlg = True              # This flag controls whether a file containing a list of folders processed is written
bnrWriteFlg = True              # This flag controls whether ckopus is called to write bnr files

#-------------
# ckopus Flags
#-------------
bnrType    = 'F'                # bnr type ckopus writes (F => Fortran, R => C)                 
SBlockType = 'NONE'             # Spectral block type [TRAN | SGN2 | IFG2 | EMIS | IFGM | PHAS | SNGC]
                                # If this value is None or an empty string, the program will take the 
                                # default spectral block type given by ckopus
     
#ckopusFlgs = ['-b3']                           
ckopusFlgs = ['-U','-t-150']    # Additional ckopus flags. Must include '-'. Each flag should be seperated by a comma
                                # and contained within the brackets




