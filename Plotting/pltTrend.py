#! /usr/bin/python
#----------------------------------------------------------------------------------------
# Name:
#        pltTrend.py
#
# Purpose:
#       Trend analysis with bootstrap resampling
#
#
#
# Notes:
#       
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
#-----------------------------------------------------------------------------------------

#---------------
# Import modules
#---------------
import sys
import os
import getopt
from   dataOutClass import *
import time

def main(argv):
    
    #--------------------------------------------------------------
    # Names... These are only needed to construct
    # file name and directories in this input file.
    # If you specify files and directories directly you
    # don't need these (e.g. they are not used in plotting program)
    #--------------------------------------------------------------
    loc        = 'tab'                 # Name of station location
    gasName    = 'ccl4'                # Name of gas
    ver        = 'Current'             # Name of retrieval version to process
    ctlFile    = "sfit4.ctl"           # Name of control file
    
    #------------------
    # Data Filter Flags
    #------------------
    saveFlg    = True                  # Flag to either save data to pdf file (saveFlg=True) or plot to screen (saveFlg=False)
    fltrFlg    = True                  # Flag to filter the data
    szaFlg     = True                  # Flag to filter based on min and max SZA
    dofFlg     = True                  # Flag to filter based on min DOFs
    pcNegFlg   = True                  # Flag to filter profiles with negative partial columns
    tcNegFlg   = True                  # Flag to filter profiles with negative total columns
    cnvrgFlg   = True                  # Flag to filter profiles that did not converge
    rmsFlg     = True                  # Flag to filter based on max RMS
    chiFlg     = True                  # Flag to filter based on max CHI_2_Y
    
    maxRMS     = 2.00                  # Max Fit RMS to filter data. Data is filtered according to <= maxrms
    minDOF     = 0.7                   # Min DOFs for filtering
    minSZA     = 55.0                  # Min SZA for filtering
    maxSZA     = 85.0                  # Max SZA for filtering
    maxCHI     = 2.0
    sclfct     = 1.0E9                 # Scale factor to apply to vmr plots (ppmv=1.0E6, ppbv=1.0E9, etc)
    sclfctName = 'ppbv'                # Name of scale factor for labeling plots
    
    #----------------------
    # Date range to process
    #----------------------
    iyear      = 1999
    imnth      = 1
    iday       = 1
    fyear      = 2014
    fmnth      = 12
    fday       = 31    
    
    #-------------------------
    # Number of Trend Segments
    #-------------------------
    nTrends    = 2
    
    #--------------------------------------------
    # Start and stop dates for each trend segment
    #--------------------------------------------
    iTrendYear = [1999,2009]
    iTrendMnth = [1   ,1]
    iTrendDay  = [1   ,1]
    fTrendYear = [2009,2014]
    fTrendMnth = [12  ,12]
    fTrendDay  = [31  ,31]
    
    
    #------------
    # Directories
    #------------
    retDir = '/Volumes/data1/ebaumer/'+loc.lower()+'/'+gasName.lower()+'/'+ver+'/'  
    
    #------
    # Files
    #------
    ctlFile  = '/Volumes/data1/ebaumer/'+loc.lower()+'/'+gasName.lower()+'/'+'x.'+gasName.lower()+'/'+ctlFile
    pltFile  = '/Volumes/data1/ebaumer/'+loc.lower()+'/' + 'Plots/' + loc + '_' + gasName + '_' + ver + 'Trend.pdf'    
    
    




