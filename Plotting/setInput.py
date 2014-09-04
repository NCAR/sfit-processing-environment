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

maxrms     = 1.70                  # Max Fit RMS to filter data. Data is filtered according to <= maxrms
sclfct     = 1.0E9                 # Scale factor to apply to vmr plots (ppmv=1.0E6, ppbv=1.0E9, etc)
sclfctName = 'ppbv'                # Name of scale factor for labeling plots

#----------------------
# Date range to process
#----------------------
iyear      = 1999
imnth      = 1
iday       = 1
fyear      = 2013
fmnth      = 12
fday       = 31

#------------
# Directories
#------------
retDir = '/data1/ebaumer/'+loc.lower()+'/'+gasName.lower()+'/'+ver+'/'  


#------
# Files
#------
ctlFile  = '/data1/ebaumer/'+loc.lower()+'/'+gasName.lower()+'/'+'x.'+gasName.lower()+'/sfit4.ctl'
pltFile  = '/data1/ebaumer/'+loc.lower()+'/'+gasName.lower()+'/' + ver + '/Plots/' + loc + '_' + gasName + '_' + ver + '.pdf'

       
