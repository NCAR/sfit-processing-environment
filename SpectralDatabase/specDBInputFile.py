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
loc = 'bre'
lat = 53
lon = -8
alt = 27
utc = 1

#----------------------------------
# Date Range of data to process
# Data processing includes starting
# and ending dates!!
#----------------------------------
# Starting 
iyear = 2014               # Year
imnth = 8                  # Month
iday  = 6
# Ending
fyear = 2014               # Year
fmnth = 8                 # Month
fday  = 6                 # Day


#------------
# directories
#------------
dataBaseDir   = '/data/sfit-processing-test/bre'                            # Base directory for OPUS data
DaysProcDir   = '/data/sfit-processing-test/'   # Path to write file that contains list of all folders processed

#------
# Files
#------
outputDBfile  = '/data/sfit-processing-test/spDB_'+loc+'_'+str(iyear)+'.dat'  # Path and filename of spectral database file
Fckopus       = '/home/mathias/chkopus/ckopus/ckopus'                                       # ckopus executable file

#----------------------
# General Logical Flags
#----------------------
DaysProcFlg = True              # This flag controls whether a file containing a list of folders processed is written
bnrWriteFlg = True              # This flag controls whether ckopus is called to write bnr files

#-------------
# ckopus Flags
#-------------
bnrType    = 'F'                # bnr type ckopus writes (F => Fortran, R => C)                 
SBlockType = 'SNGC'             # Spectral block type [TRAN | SGN2 | IFG2 | EMIS | IFGM | PHAS | SNGC]
                                # If this value is None or an empty string, the program will take the 
                                # default spectral block type given by ckopus

ckopusFlgs = ['']                                
#ckopusFlgs = ['-b3']                           
#ckopusFlgs = ['-U','-t-150']    # Additional ckopus flags. Must include '-'. Each flag should be seperated by a comma
                                # and contained within the brackets




