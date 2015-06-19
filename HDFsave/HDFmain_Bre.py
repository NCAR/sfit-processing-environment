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
    if len(args) != 7:
        print 'call as HDFmain_Bre Datadir HDFDir location gas YYYYMMDD (start) YYYYMMDD (end)'
        return()
        
    script_dir = os.path.dirname(sys.argv[0])
    dataDir        = args[1]
    outDir         = args[2]
    loc1           = args[3]
    gasName        = args[4]  # This is the target gas for retrieval
    version        = 'Current'
    sfitVer        = '0.9.4.4'                      # This is the version of sfit4 used for the retrievals
    sdate = datetime.datetime.strptime(args[5],'%Y%m%d')
    edate = datetime.datetime.strptime(args[6],'%Y%m%d')
    iyear          = sdate.year
    imonth         = sdate.month
    iday           = sdate.day
    fyear          = edate.year
    fmonth         = edate.month
    fday           = edate.day
    maxRMS         = 1.0
    maxSZA         = 90.0
    rmsFlag        = True
    tcFlag         = False
    pcFlag         = False
    cnvFlag        = False
    szaFlag        = True
    validFlag      = True
    minDOFs        = 1.0
    dofFlag        = False
    co2Flag        = False
    minCO2         = 0
    maxCO2         = 1e26
    minVMR         = -1.0e-7
    maxVMR         = 2.0e-5
    
    if loc1.lower() == 'bre':
        loc            = 'BREMEN'
        source         = 'IUP001'
        attribute_file = os.path.join(script_dir, 'bremen_attr.txt')
    elif loc1.lower() == 'nya':    
        loc            = 'NY.ALESUND'
        source         = 'AWI001'
        attribute_file = os.path.join(script_dir, 'nyalesund_attr.txt')
    elif loc1.lower() == 'cruise':    
        loc            = 'POLARSTERN'
        source         = 'AWI027'
        attribute_file = os.path.join(script_dir, 'bremen_attr.txt')
    elif loc1.lower() == 'pmb':    
        loc            = 'PARAMARIBO'
        source         = 'AWI019'
        attribute_file = os.path.join(script_dir, 'bremen_attr.txt')
        # source         = 'AWI028'

    if gasName.lower() == 'o3':
        maxRMS         = 5.0 # in percent
        maxSZA         = 90.0
        rmsFlag        = True
        tcFlag         = True
        pcFlag         = True
        cnvFlag        = True
        szaFlag        = True
        validFlag      = True
        maxCHI2        = 5.0
        minCO2         = 6.5e21
        maxCO2         = 8.5e21

    if gasName.lower() == 'ccl4':
        maxSZA         = 90.0
        maxCHI2        = 10.0
        maxVMR         = 4.0e-9
        minVMR         = -1.0e-11
        rmsFlag        = False
        tcFlag         = False
        pcFlag         = False
        cnvFlag        = True
        szaFlag        = True
        validFlag      = True
        minDOFs        = 0.8
        dofFlag        = True
        co2Flag        = True
        minCO2         = 6.5e21
        maxCO2         = 8.5e21
        
   
   
    #---------------------
    # For python interface
    #---------------------

    ddir = os.path.abspath(os.path.curdir)
    ctlF           = dataDir+'/sfit4.ctl'
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

    myhdf.initPy(dataDir, ctlF,  spcDBfile, statLyrFile,iyear, imonth,
                 iday,   fyear, fmonth, fday, mxRMS=maxRMS, mxSZA=maxSZA,
                 rmsFlg=rmsFlag, tcFlg=tcFlag,pcFlg=pcFlag,cnvFlg=cnvFlag,
                 szaFlg=szaFlag, validFlg=validFlag,maxCHI2=maxCHI2,
                 minVMR=minVMR,maxVMR=maxVMR,dofFlg=dofFlag,minDOF=minDOFs,
                 co2Flag=co2Flag,minCO2=minCO2,maxCO2=maxCO2)

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
