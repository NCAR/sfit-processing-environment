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
import hdfsave
                            
                            
def main():
    
    gasName        = 'CO'                                        # This is the target gas for retrieval
    idlFname       = '/Users/ebaumer/Data/1999_2012_TAB_CO.sav'   # This is path and name of the IDL save file we use to store the data
    outDir         = '/Users/ebaumer/Data/HDF/'                   # This is the directory where the HDF file will be written to
    loc            = 'THULE'                                      # This is the location of the instrument
    sfitVer        = '0.9.4.3'                                    # This is the version of sfit4 used for the retrievals
    iyear          = 1999
    imonth         = 1
    iday           = 1
    fyear          = 1999
    fmonth         = 12
    fday           = 31
   
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
    myhdf.initIDL(idlFname,iyear,imonth,iday,fyear,fmonth,fday)

    #--------------------------------------------
    # Here we are actually creating the HDF file.
    # We can create either and HDF4 or HDF5 file
    #--------------------------------------------
    myhdf.createHDF4()
    #myhdf.createHDF5()
    
if __name__ == "__main__":
    main()
