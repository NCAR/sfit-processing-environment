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
#       3) The following inputs need to be specified through the ctl file and are not currently
#          part of the input file:
#              -- file.in.sa_matrix
#              -- file.in.isotope
#              -- file.in.solarlines
#              -- file.in.linelist
#
# Version History:
#       Created, May, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
#
#
# License:
#    Copyright (c) 2013-2014 NDACC/IRWG
#    This file is part of sfit4.
#
#    sfit4 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    sfit4 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with sfit4.  If not, see <http://www.gnu.org/licenses/>
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
iyear = 2019               # Year
imnth = 1                  # Month
iday  = 1                  # Day

# Ending
fyear = 2019               # Year
fmnth = 12                 # Month
fday  = 31                 # Day


#------------
# directories
#------------
BaseDirInput     = '/data1/'                                       # Input base directory
BaseDirOutput    = '/data1/ebaumer/tab/co/'                        # Output base directory
binDir           = '/data/ebaumer/Code/sfit-core-code/src/'        # binary directory
ilsDir           = ''         # ILS file(s). Options:
                                                                   #   1) Use empty string ('') to indicate no ILS file!!
                                                                   #   2) If string points to directory finds ils file closest in date (ils file name must be in format: *ilsYYYYMMDD.*)
                                                                   #   3) If string points to specific file, this ils file is used for all data processing

#RatioDir         = '/Users/ebaumer/Data/TestBed/fltrFiles/'       # Directory for ratio files ** Currently NOT used **
logDirOutput     = '/data1/ebaumer/tab/co/'                         # Directory to write log files and list files

#------
# Files
#------
# FORMAT=>    [Control file Path/name, Filter ID, Version Name]
#             Control file Path/name (str) -- Full name and path to control file
#             Filter ID (str)              -- Filter ID
#             Version Name (str)           -- Version name of control file. Used to create directory under timestamp directory
ctlList   = [['/Users/ebaumer/Data/TestBed/ctlFiles/sfit4.ctl','','VerA']]

ctlList   = [['/data1/ebaumer/tab/co/x.co/sfit4_v3.ctl','4','Current_v3'], ['/data1/ebaumer/tab/co/x.co/sfit4_v3.ctl','5','Current_v3']]  # e.g., Filter 4 and 5

spcdbFile = '/data/Campaign/TAB/Spectral_DB/HRspDB_tab_2019.dat'     # Spectral DB File

WACCMfile   = '/data/Campaign/TAB/waccm/WACCMref_V6.TAB'                        # WACCM profile to use
WACCMfolder = '/data/Campaign/TAB/waccm/co/'                                    # WACCM folder with monthly profiles

#--------------------
# Flags and Constants
#--------------------
waccmFlg    = 0                                                # Flag to use WACCM profiles: 0 = Use single WACCM file defined above (WACCMfile)
                                                               #                             1 = Use Monthly mean WACCM profiles in the folder defined above (WACCMfolder)

coaddFlg    = 0                                                # Flag to indicate processing coadded spectra

ilsFlg      = 1                                                # ILS file flag: 1 = Use ils file/directory specified in ilsDir string
                                                               #                0 = No ils is specified in input file. What is specified in ctl file is used

scnFlg      = 0                                                # Flag to use measurement files with only forward or only backward scans
                                                               # 0 = Flag off - does not distinguish between forward and backward scans
                                                               # 1 = Only use files with FOWARD scans
                                                               # 2 = Only use files with BACKWARD scans


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

wVer        = 99                                               # Version of water profile to use.
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





# MLO f2  3586.500 3587.000
# TAB f2  3384.300 3384.500
#     f3  3017.000 3017.500
#     f6  1305.800 1306.000
#     f8  751.300  751.370
