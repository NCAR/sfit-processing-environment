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
                            
def main(args):
    if len(args) != 5:
        print 'call as HDFmain_Bre HDFdir location gas YYYYMMDD (start) YYYYMMDD (end)'
    script_dir = os.path.dirname(sys.argv[0])
    dataDir        = args[1]
    loc1           = args[2]
    gasName        = args[3]  # This is the target gas for retrieval
    version        = 'Current'
    sfitVer        = '0.9.4.4'                      # This is the version of sfit4 used for the retrievals
    sdate = datetime.datetime.strptime(args[4],'%Y%m%d')
    edate = datetime.datetime.strptime(args[5],'%Y%m%d')
    iyear          = sdate.year
    imonth         = sdate.month
    iday           = sdate.day
    fyear          = edate.year
    fmonth         = edate.month
    fday           = edate.day
    maxRMS         = 0.02
    rmsFlag        = True
    tcFlag         = False
    pcFlag         = False
    cnvFlag        = False
    szaFlag        = True
    validFlag      = True

    if loc1.lower() == 'bre':
        loc            = 'BREMEN'
        source         = 'IUP001'
        attribute_file = os.path.join(script_dir, 'bremen_attr.txt')
    elif loc1.lower() == 'nya':    
        loc            = 'NYALESUND'
        source         = 'AWI001'
        attribute_file = os.path.join(script_dir, 'nyalesund_attr.txt')
    elif loc1.lower() == 'cruise':    
        loc            = 'POLARSTERN'
        source         = 'AWI027'
        attribute_file = os.path.join(script_dir, 'bremen_attr.txt')
    elif loc1.lower() == 'pmb':    
        loc            = 'PARAMARIBO'
        source         = 'AWI019'
        # source         = 'AWI028'

    if gasName.lower() == 'o3':
        maxRMS         = 2.0 # in percent
        maxSZA         = 80.0
        rmsFlag        = True
        tcFlag         = True
        pcFlag         = True
        cnvFlag        = True
        szaFlag        = True
        validFlag      = True
        
        
   
    #------------------
    # For IDL interface
    #------------------
    #idlFname       = '/Volumes/data1/ebaumer/'+loc1.lower()+'/'+gasName.lower()+'/1999_2012.sav'  # This is path and name of the IDL save file we use to store the data
    #outDir         = '/Volumes/data1/ebaumer/'+loc1.lower()+'/'+gasName.lower()+'/HDFfiles/'      # This is the directory where the HDF file will be written to
    #outDir         = '/Users/ebaumer/Data/HDF/'                                                  # This is the directory where the HDF file will be written to
   
    #---------------------
    # For python interface
    #---------------------

    ddir = os.path.abspath(os.path.curdir)
    ctlF           = dataDir+'/sfit4.ctl'
    outDir         = '/data/HDFfiles/'
    spcDBfile      = dataDir+'/spectral_database.dat'
    statLyrFile    = dataDir+'/station.layers'
   
   
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
    myhdf.initPy(dataDir, ctlF,  spcDBfile, statLyrFile,iyear, imonth,
                 iday,   fyear, fmonth, fday, mxRMS=maxRMS, mxSZA=maxSZA,
                 rmsFlg=rmsFlag, tcFlg=tcFlag,pcFlg=pcFlag,cnvFlg=cnvFlag,
                 szaFlg=szaFlag, validFlg=validFlag)

    #--------------------------------------------
    # Here we are actually creating the HDF file.
    # We can create either and HDF4 or HDF5 file
    #--------------------------------------------
    myhdf.createHDF4()
    #myhdf.createHDF5()
    
    print 'Finished creating HDF file'
    
    
if __name__ == "__main__":
    import sys, os
    import datetime
    sys.path.append(os.path.join(os.path.dirname(sys.argv[0]),'..','ModLib'))
    import hdfsave as hdfsave
    main(sys.argv)
