#----------------------------------------------------------------------------------------
# Name:
#        setInput.py
#
# Purpose:
#        This is the input file for pltSet.py
#
#----------------------------------------------------------------------------------------



#--------------------------------------------------------------
# Names... These are only needed to construct
# file name and directories in this input file.
# If you specify files and directories directly you
# don't need these (e.g. they are not used in plotting program)
#--------------------------------------------------------------
loc        = 'tab'                 # Name of station location
gasName    = 'ch4'                 # Name of gas
ver        = 'Current'             # Name of retrieval version to process

#------
# Flags
#------
saveFlg    = True                  # Flag to either save data to pdf file (saveFlg=True) or plot to screen (saveFlg=False)
errorFlg   = False                 # Flag to process error data
fltrFlg    = True                  # Flag to filter the data
byYrFlg    = False                 # Flag to create plots for each individual year in date range
szaFlg     = False                 # Flag to filter based on min and max SZA
dofFlg     = False                 # Flag to filter based on min DOFs
pcNegFlg   = True                  # Flag to filter profiles with negative partial columns
tcNegFlg   = True                  # Flag to filter profiles with negative total columns
cnvrgFlg   = True                  # Flag to filter profiles that did not converge
rmsFlg     = True                  # Flag to filter based on max RMS
chiFlg     = False                 # Flag to filter based on max CHI_2_Y

maxRMS     = 1.70                  # Max Fit RMS to filter data. Data is filtered according to <= maxrms
minDOF     = 1.0                   # Min DOFs for filtering
minSZA     = 0.0                   # Min SZA for filtering
maxSZA     = 80.0                  # Max SZA for filtering
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

#----------------------------
# Partial Columns Bounds [km] 
# [lower bound, upper bound]
# To turn off set to False
#----------------------------
pCols = [[0.0,8.0],[8.0,16.0],[16.0,25.0]]

#------------
# Directories
#------------
retDir = '/Volumes/data1/ebaumer/'+loc.lower()+'/'+gasName.lower()+'/'+ver+'/'  


#------
# Files
#------
ctlFile  = '/Volumes/data1/ebaumer/'+loc.lower()+'/'+gasName.lower()+'/'+'x.'+gasName.lower()+'/sfit4.ctl'
pltFile  = '/Volumes/data1/ebaumer/'+loc.lower()+'/' + 'Plots/' + loc + '_' + gasName + '_' + ver + '.pdf'

       
