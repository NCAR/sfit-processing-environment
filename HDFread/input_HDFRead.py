#----------------------------------------------------------------------------------------
# Name:
#        input_HDFRead.py
#
# Purpose:
#        This is the input file for pltHDF.py
#
# Version History:
#       Created, Dec, 2019  Ivan Ortega (iortega@ucar.edu)
#
#---------------------------------------------------------------------------------------- 

#------------
# Directories
#------------ 
loc        = 'tab'                  # location; typically 3 letter id 
gasName    = 'c2h6'                 # gas
ver        = ['Current_v2']         # Version Names; Note: it can be more than one version, must be in []; typically name of the folder containing retrievals
locID      = 'thule'                # ID identifier in HDF file(s); e.g., site name

pathDir    = '/data1/ebaumer/'+loc.lower()+'/'   # Absolute path of directory; typically constructed with the location

#------
# Flags
#------
saveFlg    = True                   # Flag to either save data to pdf file (saveFlg=True) or plot to screen (saveFlg=False)
errorFlg   = True                   # Flag to process error data

fltrFlg    = True                   # Flag to filter the data
dateFlg    = True                  # Flag to filter based on min and max dates; if False will use all HDF files
szaFlg     = False                   # Flag to filter based on min and max SZA
pcNegFlg   = False                  # Flag to filter profiles with negative partial columns
tcNegFlg   = True                   # Flagsag to filter profiles with negative total columns
tcMMFlg    = False                   # Flag to filter based on min and max total column amount

minSZA     = 0.0                    # Min SZA for filtering
maxSZA     = 90.0                   # Max SZA for filtering
maxTC      = 5.0E24                 # Max Total column amount for filtering
minTC      = 0.0                    # Min Total column amount for filtering

sclfct     = 1.0E12                  # Scale factor to apply to vmr plots (ppmv=1.0E6, ppbv=1.0E9, etc)
sclfctName = 'pptv'                 # Name of scale factor for labeling plots

#----------------------
# Date range to plot
#----------------------
iyear      = 2018	
imonth     = 1
iday       = 1
fyear      = 2018
fmonth     = 12
fday       = 31

#----------------------
# Construct directory name with HDF files; typically location and gasname is used in the path
#----------------------
if not( pathDir.endswith('/') ): pathDir = pathDir + '/'        

dataDir    = [pathDir + gasName.lower() +'/HDF_'+v  for v in ver]          

#----------------------
# Name of pdf with plots (saved in current/running directory)
#----------------------
pltFile  = locID.lower()+'_'+gasName.lower()+'.pdf' 
