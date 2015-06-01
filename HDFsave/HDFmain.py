#! /usr/local/python-2.7/bin/python
#----------------------------------------------------------------------------------------
# Name:
#        HDFmain.py
#
# Purpose:
#       Main program to create GEOMS format HDF files
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
#----------------------------------------------------------------------------------------                              
#import hdfsaveTAB as hdfsave
#import hdfsaveMLO as hdfsave        
import hdfsaveFL0 as hdfsave
                            
def main():
    loc1           = 'fl0'
    gasName        = 'c2h6'                         # This is the target gas for retrieval
    version        = 'Current_250'
    if loc1.lower() == 'tab':
        loc            = 'THULE'
    elif loc1.lower() == "mlo":    
        loc            = 'MAUNA.LOA.HI'                                               
    else: 
        loc            = "BOULDER.COLORADO"
    sfitVer        = '0.9.4.4'                      # This is the version of sfit4 used for the retrievals
    year           = 1999
    iyear          = year
    imonth         = 1
    iday           = 1
    fyear          = year
    fmonth         = 12
    fday           = 31
   
    #------------------
    # For IDL interface
    #------------------
    #idlFname       = '/Volumes/data1/ebaumer/'+loc1.lower()+'/'+gasName.lower()+'/1999_2012.sav'  # This is path and name of the IDL save file we use to store the data
    #outDir         = '/Volumes/data1/ebaumer/'+loc1.lower()+'/'+gasName.lower()+'/HDFfiles/'      # This is the directory where the HDF file will be written to
    #outDir         = '/Users/ebaumer/Data/HDF/'                                                  # This is the directory where the HDF file will be written to
   
    #---------------------
    # For python interface
    #---------------------
    dataDir        = '/data1/ebaumer/'+loc1.lower()+'/'+gasName.lower()+'/'+version+'/'
    ctlF           = '/data1/ebaumer/'+loc1.lower()+'/'+gasName.lower()+'/x.'+gasName.lower()+'/sfit4.ctl'
    outDir         = '/data1/ebaumer/'+loc1.lower()+'/'+gasName.lower()+'/HDFfiles/'
    #spcDBfile      = '/data/Campaign/'+loc1.upper()+'/Spectral_DB/CoaddspDB_tab_1999_2014.dat'
    spcDBfile      = '/data/Campaign/'+loc1.upper()+'/Spectral_DB/HRspDB_mlo_1995_2014.dat'
    statLyrFile    = '/data/Campaign/'+loc1.upper()+'/local/station.layers'
    maxRMS         = 1.6
    minDOFs        = 1.0
    dofFlag        = False
    rmsFlag        = True
    tcFlag         = True
    pcFlag         = True
    cnvFlag        = True
    szaFlag        = False
   
   
    print("Creating HDF file")
    
    #------------------------------------------------------------
    # Here we create an instance of the HDFsave object. We define
    # that the data written to the HDF file will be REAL (float32)
    # precision. You can also define DOUBLE (float64). Note the
    # variable DATETIME will always be written as a DOUBLE as 
    # specified in GEOMS: http://avdc.gsfc.nasa.gov/index.php?site=1989220925
    #------------------------------------------------------------
    myhdf = hdfsave.HDFsave(gasName,outDir,sfitVer,loc,dType='float32')
    
    #------------------------------------------------
    # Here we initialize the HDF object with our data
    # using our pre-defined interface
    #------------------------------------------------
    #myhdf.initDummy()
    #myhdf.initIDL(idlFname,iyear,imonth,iday,fyear,fmonth,fday)
    myhdf.initPy(dataDir, ctlF,  spcDBfile, statLyrFile,iyear, imonth, iday,   fyear, fmonth, fday,
                 mxRMS=maxRMS,minDOF=minDOFs,dofFlg=dofFlag, rmsFlg=rmsFlag,tcFlg=tcFlag,pcFlg=pcFlag,cnvFlg=cnvFlag,szaFlg=szaFlag)

    #--------------------------------------------
    # Here we are actually creating the HDF file.
    # We can create either and HDF4 or HDF5 file
    #--------------------------------------------
    myhdf.createHDF4()
    #myhdf.createHDF5()
    
    print 'Finished creating HDF file'
    
    
if __name__ == "__main__":
    main()
