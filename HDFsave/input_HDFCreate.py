#----------------------------------------------------------------------------------------
# Name:
#        input_HDFCreate.py
#
# Purpose:
#        This is the input file for HDFCreate.py
#
#----------------------------------------------------------------------------------------
loc          = 'tab'                  # Name of station location
gasName      = 'co'                 # Name of gas
ver          = 'Current_B3_RD'        # Name of retrieval version to process
ctlF         = 'sfit4_v3.ctl'            # Name of ctl file

#------
#Some Meta-data for hdf file (Global Attributes) --> More in hdfsave.py
#------
sfitVer      = '0.9.4.4'
fileVer      = '004'                # Updated October 2017
projectID    = 'QA4ECV'

#------
#Python Flg: if True Use Python Interface; if False use IDL Interface
#------
pyFlg        = True

#------
# If pyFlg is True the below files are needed
#------
#spcDBFile    = 'CoaddspDB_tab_1999_2014.dat'
spcDBFile    = 'HRspDB_tab_RD.dat'        
#spcDBFile    = 'HRspDB_tab_2018.dat'                                     
statLyrFile  = 'station.layers'  

#------
# If pyFlg is False the below IDL file is neede
#------
idlFname       = ' '

#----------------------
# Date range
#----------------------
iyear        = 2019
fyear        = 2019

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

maxRMS       = 2.5                    # Max Fit RMS to filter data. Data is filtered according to <= maxrms
minDOF       = 1.0                    # Min DOFs for filtering
minSZA       = 0.0                    # Min SZA for filtering
maxSZA       = 90.0                   # Max SZA for filtering
maxCHI       = 2.0                    # Max CHI_y_2 value
maxTC        = 5.0E24                 # Max Total column amount for filtering
minTC        = 0.0                    # Min Total column amount for filtering

#------------
# Directories
#------------
dataDir      = '/data1/ebaumer/'+loc.lower()+'/'+gasName.lower()+'/'+ver+'/' 
outDir       = '/data1/ebaumer/'+loc.lower()+'/'+gasName.lower()+'/HDF_'+ver+'/' 

#------
# Files
#-----
spcDBFile     = '/data/Campaign/'+loc.upper()+'/Spectral_DB/'+spcDBFile  
statLyrFile  = '/data/Campaign/'+loc.upper()+'/local/'+statLyrFile
ctlFile      = '/data1/ebaumer/'+loc.lower()+'/'+gasName.lower()+'/'+'x.'+gasName.lower()+'/'+ctlF


#------
# OPTIONAL
#-----

dSource = 'RD'    # Data_Source - Created for Rapid Delivery

       
