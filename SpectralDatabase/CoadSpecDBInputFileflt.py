#----------------------------------------------------------------------------------------
# Name:
#        <variable>
#
# Purpose:
#       This is the main input file for mkCoadSpecDbflt.py.
#
# Notes:
#       1) The input file is read in as a python file, therefore you should follow python
#          syntax when editing.
#       2) The extension of this file should be .py !!!!
#
# Version History:
#       Created, July, 2018  Ivan Ortega (iortega@ucar.edu)
#
#----------------------------------------------------------------------------------------

#---------------------
# Three letter station location, year and FLT ID
#---------------------
loc           = 'mlo'
iyear         = 2002
fyear         = 2009
fltID         = '1'

#------------
# directories
#------------
dataBaseDir   = '/data1/'+loc.lower()+'/'                       # Base directory for OPUS data
#DaysProcDir   = '/data/Campaign/'+loc.upper()+'/Spectral_DB/'   # Path to write file that contains list of all folders processed
DaysOutDir    = '/data1/coadded/'+loc.lower()+'/'               # Path of coadded directories             

#------
# Files
#------
#inputDBfile   = '/data/Campaign/'+loc.upper()+'/Spectral_DB/HRspDB_'+loc.lower()+'_'+year+'.dat'     # Path and filename of Original spectral database file (non-coadded)

inputDBDir    = '/data/Campaign/'+loc.upper()+'/Spectral_DB/'   
inputDBfile   = ['HRspDB_'+loc.lower()+'_' , '.dat']  
coaddex       = '/data/ebaumer/Code/sfit-ckopus/coad'                                                # coadd executable file

#----------------------
# General Logical Flags
#----------------------
DaysProcFlg   = True                   # This flag controls whether a file containing a list of folders processed is written

szaFlg        = True                   # If False will coadd all SZA
#szaRange      = [ [70, 75]]
#szaRange      = [ [40, 43], [43, 46], [46,49], [49, 52], [52, 55], [55, 58],  [58, 61], [61, 64], [64, 67], [67, 70], [70, 73], [73, 76], [76, 79], [79,81], [81, 84] ,[84, 87], [87, 90] ]  # Ranges of SZAs

szaRange      = [ [40, 45], [45, 50], [50, 55], [55, 60], [60, 65], [65, 70], [70, 75], [75, 80], [80, 85], [85, 90]]  # Ranges of SZAs

DaysFlg       = True                   # If FALSE will coadd daily
NumDays       = 14

SpccNumFlg   = True                    # Only continue if number of spectra is greater or equal to this number
NumSpc       = 4

cpPrfFlg     = True                  # Flag to copy profiles (water, waccm and zpt) from dataBaseDir to new DaysOutDir
 
outputDBDir  = '/data/Campaign/'+loc.upper()+'/Spectral_DB/coadd/'
outputDBid   = ['CoaddspDB_'+loc.lower()+'_' , '_flt'+fltID+'_1_v2.dat']  # Path and filename of Output spectral database file (coadded)






