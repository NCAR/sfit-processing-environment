#----------------------------------------------------------------------------------------
# Name:
#        input_HDFRead.py
#
# Purpose:
#        This is the input file for pltHDF.py
#
#----------------------------------------------------------------------------------------

#------------
# Directories
#------------ 

dataDir    = '/data1/temp/harestua/sfit4/hrt/o3/HDF_test'             # DIRECTORY
locID      = 'harestua'                                   # LOCATION ID IN THE HDF FILE
gasName    = 'O3'                                      


#------
# Flags
#------
saveFlg    = True                  # Flag to either save data to pdf file (saveFlg=True) or plot to screen (saveFlg=False)
errorFlg   = True                  # Flag to process error data
fltrFlg    = False                   # Flag to filter the data

dateFlg    = True                   # Flag to filter based on min and max dates
szaFlg     = False                   # Flag to filter based on min and max SZA
dofFlg     = False                   # Flag to filter based on min DOFs
pcNegFlg   = False                  # Flag to filter profiles with negative partial columns
tcNegFlg   = True                   # Flagsag to filter profiles with negative total columns
tcMMFlg    = True                   # Flag to filter based on min and max total column amount

minDOF     = 0.0                    # Min DOFs for filtering
minSZA     = 0.0                    # Min SZA for filtering
maxSZA     = 90.0                   # Max SZA for filtering
maxTC      = 5.0E24                 # Max Total column amount for filtering
minTC      = 0.0                    # Min Total column amount for filtering
sclfct     = 1.0E9                  # Scale factor to apply to vmr plots (ppmv=1.0E6, ppbv=1.0E9, etc)
sclfctName = 'ppbv'                 # Name of scale factor for labeling plots

#----------------------
# Date range to plot
#----------------------
iyear      = 2014	
imonth     = 1
iday       = 1
fyear      = 2014
fmonth     = 12
fday       = 31

if(iyear == fyear):
    pltFile  = dataDir+locID.lower()+'_'+gasName.lower()+'_'+str(iyear)+'.pdf'
else:
    pltFile  = dataDir+locID.lower()+'_'+gasName.lower()+'_'+str(iyear)+'_'+str(fyear)+'.pdf' 
       
