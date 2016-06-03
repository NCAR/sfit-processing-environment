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
if __name__ != "__main__":
    import hdfsave as hdfsave
#import hdfsaveMLO as hdfsave                            
                            
def main():
    loc1           = 'lau'
    gasName        = 'nh3'                         # This is the target gas for retrieval
    version        = 'Current'
    source         = 'Lauder'
    sfitVer        = '0.9.4.4'                      # This is the version of sfit4 used for the retrievals
    year           = 2004
    iyear          = year
    imonth         = 1
    iday           = 1
    fyear          = 2014
    fmonth         = 6
    fday           = 1
   
   
    #---------------------
    # For python interface
    #---------------------
    script_dir = os.path.dirname(sys.argv[0])
    ddir = os.path.abspath(os.path.curdir)
    dataDir        = ddir
    ctlF           = ddir+'/sfit4.ctl'
    outDir         = '/data/HDFfiles/'
    spcDBfile      = ddir+'/spectral_database.dat'
    statLyrFile    = ddir+'/station.layers'
    attribute_file = os.path.join(script_dir, 'lauder_attr.txt')
    maxRMS         = 1.6
    rmsFlag        = False
    tcFlag         = False
    pcFlag         = False
    cnvFlag        = False
    szaFlag        = False
    validFlag      = True
   
   
    print("Creating HDF file")
    
    #------------------------------------------------------------
    # Here we create an instance of the HDFsave object. We define
    # that the data written to the HDF file will be REAL (float32)
    # precision. You can also define DOUBLE (float64). Note the
    # variable DATETIME will always be written as a DOUBLE as 
    # specified in GEOMS: http://avdc.gsfc.nasa.gov/index.php?site=1989220925
    #------------------------------------------------------------
    myhdf = hdfsave.HDFsave(gasName,outDir,sfitVer,loc,source,attribute_file,dType='float32')
    
    #------------------------------------------------
    # Here we initialize the HDF object with our data
    # using our pre-defined interface
    #------------------------------------------------
    #myhdf.initDummy()
    #myhdf.initIDL(idlFname,iyear,imonth,iday,fyear,fmonth,fday)
    myhdf.initPy(dataDir, ctlF,  spcDBfile, statLyrFile,iyear, imonth, iday,   fyear, fmonth, fday,
                 mxRMS=maxRMS, rmsFlg=rmsFlag,tcFlg=tcFlag,pcFlg=pcFlag,cnvFlg=cnvFlag,szaFlg=szaFlag, validFlg=validFlag)

    #--------------------------------------------
    # Here we are actually creating the HDF file.
    # We can create either and HDF4 or HDF5 file
    #--------------------------------------------
    myhdf.createHDF4()
    #myhdf.createHDF5()
    
    print 'Finished creating HDF file'
    
    
if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(sys.argv[0]),'..','ModLib'))
    import hdfsave as hdfsave
    main()
