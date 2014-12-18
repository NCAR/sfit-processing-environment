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
loc  = 'tab'                                                                      
year = '2002'

#------------
# directories
#------------
dataBaseDir   = '/Users/ebaumer/Data/tab/'                           # Base directory for OPUS data
DaysProcDir   = '/Users/ebaumer/Data/tab/'                           # Path to write file that contains list of all folders processed

#------
# Files
#------
inputDBfile   = '/Users/ebaumer/Data/HRspDB_'+loc.lower()+'_'+year+'.dat'      # Path and filename of Original spectral database file (non-coadded)
outputDBfile  = '/Users/ebaumer/Data/CoaddspDB_'+loc.lower()+'_'+year+'.dat'   # Path and filename of Output spectral database file (coadded)
coaddex       = '/Users/ebaumer/Code/sfit-ckopus/coad'                         # coadd executable file

#----------------------
# General Logical Flags
#----------------------
DaysProcFlg = True              # This flag controls whether a file containing a list of folders processed is written

#------------
# coadd Flags
#------------





