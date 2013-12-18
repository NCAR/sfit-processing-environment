#----------------------------------------------------------------------------------------
# Name:
#        <variable>
#
# Purpose:
#       This is the main input file for sfit4Layer1 processing. Contains directories, flags,
#       etc for processing Layer 1. 
#           
#
# Notes:
#       1) The input file is read in as a python file, therefore you should follow python
#          syntax when editing.
#       2) The extension of this file should be .py !!!!
#       3) The hbin file must be created prior to running Layer1
#       4) The following inputs need to be specified through the ctl file and are not currently
#          part of the input file:
#              -- Station layer file
#              -- Solarlines file
#              -- Hbin (linelist) file
#              -- Sa input matrix file (if used)
#              -- Isotope file (if used)
#
# Version History:
#       Created, May, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
#
#
# References:
#
#----------------------------------------------------------------------------------------


#---------
# Location 
#---------
loc = 'mlo'

#------------------------------
# Date Range of data to process
#------------------------------
# Starting 
iyear = 2012               # Year
imnth = 1                  # Month
iday  = 1                  # Day

# Ending
fyear = 2012               # Year
fmnth = 3                  # Month
fday  = 26                 # Day


#------------
# directories
#------------
BaseDirInput     = '/Users/ebaumer/Data/TestBed/Input/'            # Input base directory
BaseDirOutput    = '/Users/ebaumer/Data/TestBed/Output/'           # Output base directory
binDir           = '/Users/ebaumer/Code/sfit-core-code/src/'              # binary directory
ilsDir           = ''                                              # ILS file(s). Options:
                                                                   #   1) Use empty string ('') to indicate no ILS file!!
                                                                   #   2) If string points to directory finds ils file closest in date (ils file name must be in format: *ilsYYYYMMDD.*)
                                                                   #   3) If string points to specific file, this ils file is used for all data processing
                                                                   
RatioDir         = '/Users/ebaumer/Data/TestBed/fltrFiles/'        # Directory for ratio files ** Currently NOT used **
logDirOutput     = '/Users/ebaumer/Data/TestBed/'       # Directory to write log files and list files

#------
# Files
#------
# FORMAT=>[Control file Path/name, Filter ID, Version Name] 
#             Control file Path/name (str) -- full name and path to control file 
#             Version Name (str) -- Version name of control file. Used to create directory under timestamp directory
ctlList   = [['/Users/ebaumer/Data/TestBed/ctlFiles/sfit4.ctl','','VerA']]


spcdbFile = '/Users/ebaumer/Data/TestBed/HRspDB_mlo_2012.dat'           # Spectral DB File
WACCMfile = '/Users/ebaumer/Data/TestBed/waccm/WACCMref_V6.MLO'         # WACCM profile to use
sbCtlFile = '/Users/ebaumer/Data/TestBed/sb.ctl'                        # Control file for error analysis

# Optional files


#--------------------
# Flags and Constants
#--------------------
coaddFlg    = 0                                                # Flag to indicate processing coadded spectra                                                 
ilsFlg      = 1                                                # ILS file flag: 1 = Use ils file/directory specified in ilsDir string
                                                               #                0 = No ils is specified in input file. What is specified in ctl file is used

pspecFlg    = 1                                                # 1 = run pspec,    0 = do not run pspec
refmkrFlg   = 1                                                # 1 = run refmaker, 0 = do not run refmaker
sfitFlg     = 1                                                # 1 = run sfit,     0 = do not run sfit
lstFlg      = 1                                                # Flag to create list file. Output file which has meta data and a list of all directories processed
errFlg      = 1                                                # 1 = run error analysis, 0 = do not run error analysis
zptFlg      = 1                                                # 1 = Use new ZPT.nmc files, 0 = use old zpt-120 files

refMkrLvl   = 0                                                # Version of reference maker to use. 
                                                               #    0 = Use pre-existing zpt file. Concatonate with water and WACCM profiles
                                                               #    1 = Use pre-existing zpt file. Concatonate with water and WACCM profiles. Replace
                                                               #        surface pressure and temperature with values in database file. If those values
                                                               #        are not present, then default to original zpt file

wVer        = 2                                                # Version of water profile to use.
                                                               #    <0 => Get the latest water version file
                                                               #   >=0 => Get user specified water version file. Latest file is taken if unable to find user specified
#------------------
# Pspec input flags
#------------------
nBNRfiles = 1                                                  # Number of BNR files to include in pspec input         

outFlg    = 1                                                  # Pspec output flag
                                                               #     1 = output t15asc file (ascii)
                                                               #     2 = output bnr file (binary)
                                                               #     3 = output binary and ascii file

verbFlg   = 2                                                  # Pspec verbosity output flag
                                                               #     0 = no stdout from baseline correction or zero bnr or block output for plotting
                                                               #     1 = stdout from bc and zeroed bnr but no blockout
                                                               #     2 = stdout from zeroed bnr and blockout for plotting
                                                               
nterpFlg  = 1                                                  # nterp -  zero fill factor
                                                               #     = 0 - skip resample & resolution degradation (regardless of sfit4.ctl:band.n.max_opd value)
                                                               #     = 1 - minimally sample at opdmax
                                                               #     > 1 - interpolate nterp-1 points upon minimal sampled spacing
                                                               #           note: OPD is taken from sfit4.ctl:band.n.max_opd value

ratioFlg  = 0                                                  # rflag - ratio flag, to ratio the spectra with another low resolution spectral file (eg spectral envelope)
                                                               #     = 0 - no ratio
                                                               #     = 1 - ratio, file is a bnr of same type as fflag below, expected to be resolution of ~10cm-1 

fileFlg   = 0                                                  # fflag - file open flag
                                                               #     = 0 for fortran unformatted file
                                                               #     = 1 for open as steam or binary or c-type file (gfortran uses stream)

zFlg      = 2                                                  # zflag - zero offset
                                                               #     = 0 no zero offset,
                                                               #     = 1 try w/ baselincorrect,
                                                               #     0 < z < 1 use this value,
                                                               #     = 2 use optimized 2nd polynomial fit to fully absorbed regions in 10m region
                                                               
#---------------------------------------------
# filter bands and regions for calculating SNR
# These values are used in creating the pspec 
# input file. Edit at your own risk
#---------------------------------------------
fltrBndInputs = "9 \n\
f1  4038.727 4038.871 \n\
f2  3381.155 3381.536 \n\
f3  2924.866 2925.100 \n\
f4  2526.228 2526.618 \n\
f5  1985.260 1985.510 \n\
f6  1139.075 1139.168 \n\
f8  907.854  907.977  \n\
fa  4884.51  4885.2   \n\
h6  1033.4  1033.6    \n"








