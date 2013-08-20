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
#
#
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
iday  = 24                  # Day

# Ending
fyear = 2012               # Yea#r
fmnth = 1                  # Month
fday  = 24                 # Day


#------------
# directories
#------------
BaseDirInput     = '/Users/ebaumer/Data/TestBed/'                           # Input base directory
BaseDirOutput    = '/Users/ebaumer/Data/TestBed/Output/'                    # Output base directory
binDir           = '/Users/ebaumer/Data/TestBed/src/'                    # binary directory
ilsDir           = '/Users/ebaumer/Data/TestBed/ilsFiles/'                  # Directory for ILS files


#------
# Files
#------
# FORMAT=>[Control file Path/name, Zero fill factor, Ratio flag, File open flag, Ratio File Name, Version Name] 
#             Control file Path/name (str) -- full name and path to control file 
#             Zero fill factor (nterp)  (int)
#                  nterp =  0 - skip resample & resolution degradation
#                  nterp =  1 - minimally sample at opdmax
#                  nterp >  1 - interpolate nterp-1 points upon minimal sampled spacing
#                  note: OPDMAX is taken from sfit4.ctl file
#             Ratio flag (rflag) (int)-- flag to indicate whether to ratio the spectra with another low resolution spectral file (eg spectral envelope)
#             File open flag (fflag) (int)
#                  fflag = 0 for fortran unformatted file
#                  fflag = 1 for open as steam or binary or c-type file (gfortran uses stream)
#             Ratio file name in bnr format (str)
#                  if rflag = 1 --> must have filename
#                  if rflag = 0 --> No filename specified
#             Filter ID (fID) (str) -- Filter ID used
ctlList   = [['/Users/ebaumer/Data/TestBed/ctlFiles/sfit4.ctl',1,0,0,'','VerA']]


#ctlList   = [['/Users/ebaumer/Data/TesBed/cntrl/a.ctl',1,0,0,'','VerA'],     # List of control files to process
             #['/Users/ebaumer/Data/TesBed/cntrl/b.ctl',1,0,0,'','VerB'],     # [File_Name, Zero_Fill_Flag, Ratio_Flag, Ratio_File_Name, Version_Name]
             #['/Users/ebaumer/Data/TesBed/cntrl/c.ctl',1,0,0,'','VerC'],
             #['/Users/ebaumer/Data/TesBed/cntrl/d.ctl',1,0,0,'','VerD'] ]

spcdbFile = '/Users/ebaumer/Data/TestBed/mlo/HRspDB_mlo_2012.dat'           # Spectral DB File
WACCMfile = '/Users/ebaumer/Data/TestBed/mlo/waccm/WACCMref_V6.mlo'         # WACCM profile to use


# Optional files
statFile   = '/Users/ebaumer/Data/TestBed/mlo/stations.layers'              # Station layer file

#--------------------
# Flags and Constants
#--------------------
#waterVer         = 2                                                # water version (Not currently used!!!)
#ratio_flg        = 0                                                # ratioflag : 1=ratio, 0=not (Not currently used!!)
#spc_flg          = 0                                                # Flag taken from spcListFile; Data file type (Not currently used!!)
#UTC_shft         = 0                                                # UTC shift to zero (Not currently used!!)                                                                   
#nu_margin        = 2                                                # Margin to extend the total band for pspec based on 
                                                                     # input from ctl file [cm^-1] (Not currently used!!)
numDataBlks      = 1                                                # number of data blocks in the output ascii file
                                                                    # = [# binary formatted spectra] X [# fit regions] (often but not necessarily)
                                                                    # fit regions are read from sfit4.ctl file  
pspecFlg         = 1                                                # 1 = run pspec, 0 = do not run pspec
refmkrFlg        = 1                                                # 1 = run refmaker, 0 = do not run refmaker
sfitFlg          = 1                                                # 1 = run sfit, 0 = do not run sfit
refMkrLvl        = 1
wVer             = 2

#---------------------------------------------
# filter bands and regions for calculating SNR
# These values are used in creating the pspec 
# input file. Edit at your own risk
#---------------------------------------------
fltrBndInputs = "7 \n\
f1  4038.727 4038.871 \n\
f2  3381.155 3381.536 \n\
f3  2924.866 2925.100 \n\
f4  2526.228 2526.618 \n\
f5  1985.260 1985.510 \n\
f6  1139.075 1139.168 \n\
f8  907.854  907.977  \n"



