#----------------------------------------------------------------------------------------
# Name:
#        input_HDFCreate.py
#
# Purpose:
#        This is the input file for HDFCreate.py
#
# Notes:
#        1) It will try to upload Meta Data from a python file in the form: hdfsaveLOC, where LOC is the three letter ID, e.g., hdfsaveMLO for Mauna Loa
#       
# Version History:
#       Created, 2014   Nussbaumer Eric 
#       Modified, 2019/2020, Ivan Ortega (iortega@ucar.edu)
#
#----------------------------------------------------------------------------------------
loc          = 'tab'                # Name of station location; 
gasName      = 'co'                 # Name of gas
ver          = 'ATM18-Ret-2017'         # Name of retrieval version to process
ctlF         = 'sfit4_v3.ctl'       # Name of ctl file

#------
# id name in the HDF file
#------
locID        = 'THULE'             # IF USING 003 TEMPLATE IT NOW ACCEPTS EXTRA CHARACTERS; E.G., RD_THULE       

#------
# Some Meta-data for hdf file (Global Attributes) --> More in hdfsave.py
#------
sfitVer      = '0.9.4.4'			# sfit4 version
fileVer      = '004'                # HDF version
projectID    = ' '                  # Name of the project; space if none

#------
# GEOMS information
#------
geoms_tmpl   = '003'                # 002 or 003; GEOMS TEMPLATE: currently GEOMS-TE-FTIR-002, but new geoms GEOMS-TE-FTIR-003, is required (2020))
geoms_meta   = '04R998'             # Use 04R010 for GEOMS-TE-FTIR-002; and 04R998 or later for GEOMS-TE-FTIR-003

#------
# Python Flg: if True Use Python Interface (); if False use IDL Interface (not incorporated yet)
#------
pyFlg        = True            

#------
# yearly Flag: If True will create yearly files from Jan 1 to Dec 31 using initial and final years; if False will create use single file from date range below      
#------
yrlFlg       = False                   

#------
# SpcDatabase
#------
spcDBFile    = 'HRspDB_tab_2015_2019.dat'	# Spectral database (change below absolute paths); needed for Lat/Lon/Alt/Duration/Azimuth; headers in database are case sensitive                                      
statLyrFile  = 'station.layers'     # station layer file

#------
# Files
#-----
spcDBFile     = '/data/Campaign/'+loc.upper()+'/Spectral_DB/HRspDB_tab_2015_2019.dat'                 # Path for the database
statLyrFile   = '/data/Campaign/'+loc.upper()+'/local/station.layers'                                 # Path for station layers
ctlFile       = '/data1/ebaumer/'+loc.lower()+'/'+gasName.lower()+'/'+'x.'+gasName.lower()+'/'+ctlF   # Path for ctl file

#----------------------
# Date range
#----------------------        
iyear        = 2017
imnth        = 3
iday         = 1

fyear        = 2017
fmnth        = 3
fday         = 30

#------
# Flags
#------
errFlg       = True
szaFlg       = True                   # Flag to filter based on min and max SZA
dofFlg       = True                   # Flag to filter based on min DOFs
pcNegFlg     = True                   # Flag to filter profiles with negative partial columns
tcNegFlg     = True                   # Flagsag to filter profiles with negative total columns
tcMMFlg      = False                  # Flag to filter based on min and max total column amount
cnvrgFlg     = True                   # Flag to filter profiles that did not converge
rmsFlg       = True                   # Flag to filter based on max RMS
chiFlg       = False                  # Flag to filter based on max CHI_2_Y
h2oFlg       = True                   # Flag to filter Negative Water Vapor Columns
bckgFlg      = False                  # Flag to filter based on slope and/or curvature (first micro-window)


maxRMS       = 1.5                    # Max Fit RMS to filter data. Data is filtered according to <= maxrms
minDOF       = 0.9                    # Min DOFs for filtering
maxDOF       = 10.0                   # Max DOFs for filtering
minSZA       = 0.0                    # Min SZA for filtering
maxSZA       = 90.0                   # Max SZA for filtering
maxCHI       = 2.0                    # Max CHI_y_2 value
maxTC        = 5.0E24                 # Max Total column amount for filtering
minTC        = 0.0                    # Min Total column amount for filtering
minSlope     = 0.0                    # Min slope
maxSlope     = 1.0					  # Max slope
minCurv      = 0.0					  # Min Curvature
maxCurv      = 1.0					  # Max Curvature

#------------
# Directories
#------------
dataDir      = '/data1/ebaumer/'+loc.lower()+'/testbed/'+gasName.lower()+'/'+ver+'/'         # Directory with retrievals
outDir       = '/data1/ebaumer/'+loc.lower()+'/'+gasName.lower()+'/HDF_'+ver+'/'     # Output Directory
#outDir       = 'hdf_GEOMS-TE-FTIR-003/'     # Output Directory

#------
# OPTIONAL
#-----
#dQuality = 'RD'            # Data_Source; e.g. RD (Rapid Delivery)
#hdfMeta  = 'hdfsaveMLO'    # Input file with metedata; if not included here the script will try to find it as hdfsaveLOC

