#----------------------------------------------------------------------------------------
# Name:
#        input_HDFCreate.py
#
# Purpose:
#        This is the input file for HDFCreate.py
#
#----------------------------------------------------------------------------------------
loc          = 'mlo'                  # Name of station location
gasName      = 'c2h6'                 # Name of gas
ver          = 'Current_newSA'        # Name of retrieval version to process
ctlF         = 'sfit4.ctl'            # Name of ctl file
hdfMeta      = '/data/hdfsaveMLO.py'        # Python File Nme with Meta Data

#------
#Some Meta-data for hdf file (Global Attributes) --> More in hdfsave.py
#------
sfitVer      = '0.9.4.4'
fileVer      = '003'   
locID        = 'MAUNA.LOA.HI'         # OPTIONAL FOR NCAR USERS              
projectID    = ' '

#------
#Python Flg: if True Use Python Interface; if False use IDL Interface
#------
pyFlg        = True                   # If True Use Python Interface; if False use IDL Interface (IDL option not working yet)

#------
# If pyFlg is True the below files are needed
#------
spcDBFile    = 'HRspDB_mlo_1995_2017.dat'                                     
statLyrFile  = 'station.layers'  

#------
# If pyFlg is False the below IDL file is neede
#------
idlFname       = ' '

#----------------------
# Date range
#----------------------
iyear        = 2017
fyear        = 2017

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

maxRMS       = 1.0                    # Max Fit RMS to filter data. Data is filtered according to <= maxrms
minDOF       = 0.9                    # Min DOFs for filtering
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


       
