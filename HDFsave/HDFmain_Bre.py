#! /usr/bin/python2
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
#
#----------------------------------------------------------------------------------------                              

import sys, os
import datetime
sys.path.append(os.path.join(os.path.dirname(__file__),'..','ModLib'))
sys.path.append(os.path.join(os.path.dirname(__file__),'..','HDFsave'))
import hdfsave

                            
def main(args):
    if len(args) != 8:
        print ('call as HDFmain_Bre Datadir HDFDir location gas YYYYMMDD (start) YYYYMMDD (end) nrt|final|cams27')
        return()

    script_dir = os.path.dirname(args[0])
    quality        = 'final'
    dataDir        = args[1]+'/'
    outDir         = args[2]+'/'
    loc1           = args[3]
    gasName        = args[4]  # This is the target gas for retrieval
    quality        = args[7].lower()
    version        = 'Current'
    sfitVer        = '0.9'                      # This is the version of sfit4 used for the retrievals
    sdate = datetime.datetime.strptime(args[5],'%Y%m%d')
    edate = datetime.datetime.strptime(args[6],'%Y%m%d')
    iyear          = sdate.year
    imonth         = sdate.month
    iday           = sdate.day
    fyear          = edate.year
    fmonth         = edate.month
    fday           = edate.day
    maxRMS         = 100.0
    maxSZA         = 90.0
    rmsFlag        = True
    tcFlag         = True
    pcFlag         = True
    cnvFlag        = True
    szaFlag        = True
    validFlag      = True
    minDOFs        = 1.0
    maxDOFs        = 6.0
    dofFlag        = False
    co2Flag        = False
    minCO2         = 0
    maxCO2         = 1e26
    minVMR         = -1.0e-7
    maxVMR         = 2.0e-5
    maxCHI2        = 9e99
    maxTCTotErr    = 9e99
    granularity    = 'yearly'
    mtype          = 'stationary'
    source         = 'sun'

    if quality != 'nrt' and quality !='final' and quality != 'cams27':
        print ('quality has to be nrt, final or cams27, not %s'%quality)
        exit()

    
    if loc1.lower() == 'bre' or loc1.lower() == 'bremen':
        loc            = 'BREMEN'
        instrument         = 'IUP001'
        attribute_file = os.path.join(script_dir, 'bremen_attr.txt.%s'%quality)
    elif loc1.lower() == 'nya':    
        loc            = 'NY.ALESUND'
        instrument         = 'AWI001'
        attribute_file = os.path.join(script_dir, 'nyalesund_attr.txt.%s'%quality)
        if gasName.lower() == 'h2o':
            source = 'sun'
            maxCHI2 = 50.0
            maxDOFs = 4.0
            maxVMR = 1.0e-2

    elif loc1.lower() == 'cruise':    
        loc            = 'POLARSTERN'
        instrument         = 'AWI027'
        mtype = 'mobile'
        attribute_file = os.path.join(script_dir, 'polarstern_attr.txt.%s'%quality)

    elif loc1.lower() == 'ps106':    
        loc            = 'POLARSTERN'
        instrument         = 'IUP004'
        if gasName.lower() == 'h2o':
            source = 'Atmosphere'
            maxCHI2 = 50.0
            maxDOFs = 2.5
            maxVMR = 1.0e-2
        else:
            source = 'Atmosphere'
        mtype = 'mobile'
        attribute_file = os.path.join(script_dir, 'ps106_attr.txt.%s'%quality)

    elif loc1.lower() == 'pmb':    
        loc            = 'PARAMARIBO'
        attribute_file = os.path.join(script_dir, 'paramaribo.txt.%s'%quality)

        if sdate.year < 2012 and edate.year > 2012:
            print ('different PMB containers during the envisaged time')
            return
        
        if sdate.year < 2012:
            instrument         = 'AWI019'
        else:
            instrument         = 'AWI028'
    elif loc1.lower() == 'ispra':
        loc = 'ISPRA'
        instrument        = 'iup003'
        attribute_file = os.path.join(script_dir, 'ispra_attr.txt.%s'%quality)
    elif loc1.lower() == 'jfj':
        loc            = 'Jungfraujoch'
        instrument         = 'ULG002'
        attribute_file = os.path.join(script_dir, 'jungfraujoch_final.txt')
    elif loc1.lower() == 'palau':
        loc            = 'Palau'
        instrument         = 'AWI019'
        attribute_file = os.path.join(script_dir, 'palau.txt.%s'%quality)


    if gasName.lower() == 'nh3':
        gasName        = 'NH3'
        maxSZA         = 90.0
        maxCHI2        = 50.0
        minVMR         = -1e-9
        minDOFs        = 0.8
        rmsFlag        = True
        tcFlag         = False
        pcFlag         = False
        cnvFlag        = True
        szaFlag        = True
        validFlag      = True

    if gasName.lower() == 'pan':
        gasName        = 'PAN'
        maxSZA         = 90.0
        maxCHI2        = 100.0
        if loc1.lower() == 'bremen':
            maxCHI2         = 35.0
            

    if gasName.lower() == 'o3':
        gasName        = 'O3'
        maxSZA         = 90.0
        rmsFlag        = True
        tcFlag         = False
        pcFlag         = False
        cnvFlag        = True
        szaFlag        = True
        validFlag      = True
        maxCHI2        = 10.0
        minVMR         = -1e-7
    if quality.lower()=='cams27':
        maxSZA = 83
        minDOFs = 2.5
        maxDOFs = 6.5
        dofFlag = True


    if gasName.lower() == 'ch4':
        gasName        = 'CH4'
        maxSZA         = 90.0
        rmsFlag        = True
        tcFlag         = False
        pcFlag         = False
        cnvFlag        = True
        szaFlag        = True
        validFlag      = True
        maxCHI2        = 20.0
        maxTCTotErr    = 1.0e19
        minVMR         = -1e-7
        maxVMR         = 2.0e-5
        if quality.lower()=='cams27':
            maxSZA = 83
            minDOFs = 1.5
            dofFlag = True


    if gasName.lower() == 'ccl4':
        gasName        = 'CCl4'
        maxSZA         = 90.0
        maxCHI2        = 20.0
        maxVMR         = 4.0e-9
        minVMR         = -1.0e-11
        rmsFlag        = False
        tcFlag         = False
        pcFlag         = False
        cnvFlag        = True
        szaFlag        = True
        validFlag      = True
        minDOFs        = 0.8
        dofFlag        = False
        co2Flag        = False
        
    if gasName.lower() == 'hf':
        gasName        = 'HF'
        tcFlag         = False
        minDOFs        = 1.0
        dofFlag        = True
        if loc == 'BREMEN':
            maxCHI2        = 100.0
        else:
            maxCHI2        = 10.0
        maxVMR         = 6e-9
        minVMR         = -1e-10
        minCO2         = 6.5e21
        maxCO2         = 8.5e23
        co2f           = True

    if gasName.lower() == 'hcl':
        gasName        = 'HCl'
        tcFlag         = False
        minDOFs        = 0.7
        dofFlag        = True
        maxCHI2        = 5.0
        maxVMR         = 6e-9
        minVMR         = -2e-12
        minCO2         = -5e22
        maxCO2         = 1.5e23
        co2f           = True
        cnvFlag        = True

    if gasName.lower() == 'hcn':
        gasName        = 'HCN'
        tcFlag         = False
        pcFlag         = False
        minDOFs        = 1.0
        dofFlag        = True
        maxCHI2        = 5.0
        maxVMR         = 1e-9
        minVMR         = -1e-11
        co2f           = False
        cnvFlag        = True

    if gasName.lower() == 'clono2':
        gasName        = 'ClONO2'
        tcFlag         = False
        dofFlag        = True
        maxCHI2        = 2.0
        maxVMR         = 5e-9
        minVMR         = -1e-10
        minDOFs        = 1.0

    if gasName.lower() == 'c2h6':
        gasName        = 'C2H6'
        tcFlag         = False
        minDOFs        = 0.5
        maxCHI2        = 100.0
        maxVMR         = 5e-8
        minVMR         = -1e-9

    if gasName.lower() == 'ccl2f2' or gasName.lower() == 'cfc12' : # CFC-12
        gasName        = 'CFC12'
        tcFlag         = False
        tcFlag         = False
        pcFlag         = False
        minDOFs        = 1.0
        maxCHI2        = 20.0
        maxVMR         = 3e-9
        minVMR         = -1e-10
        minCO2         = 1e22
        maxCO2         = 2e23

    if gasName.lower() == 'chf2cl' or gasName.lower() == 'cfc22': # CFC-22
        gasName        = 'CFC22'
        tcFlag         = False
        pcFlag         = False
        minDOFs        = 1.0
        maxCHI2        = 20.0
        maxVMR         = 3e-9
        minVMR         = -1e-10
        minCO2         = 1e22
        maxCO2         = 10e22
        
    if gasName.lower() == 'ccl3f' or gasName.lower() == 'cfc11': # CFC-11
        gasName        = 'CFC11'
        tcFlag         = False
        pcFlag         = False
        minDOFs        = 1.0
        maxCHI2        = 20.0
        maxVMR         = 3e-9
        minVMR         = -2e-10
        minCO2         = 1e22
        maxCO2         = 10e22

    if gasName.lower() == 'ocs':
        gasName        = 'OCS'
        tcFlag         = False
        minDOFs        = 0.8
        maxCHI2        = 4.0
        maxVMR         = 1e-6
        minVMR         = -1e-11
        dofFlag        = True
        cnvFlag        = True
        validFlag      = True


    if gasName.lower() == 'co':
        gasName        = 'CO'
        tcFlag         = False
        pcFlag         = False
        dofFlag        = True
        if quality.lower()=='cams27':
            minDOFs = 1.5
            dofFlag = True
        else:
            minDOFs        = 0.8
        maxCHI2        = 1000.0
        maxVMR         = 1e-4
        minVMR         = -1e-7
        cnvFlag        = True
        validFlag      = True

    if gasName.lower() == 'n2o':
        gasName        = 'N2O'
        tcFlag         = False
        pcFlag         = False
        minDOFs        = 1.0
        if loc == 'BREMEN' or loc == 'PARAMARIBO':
            maxCHI2        = 10.0
        else:
            maxCHI2        = 2.0
            maxVMR         = 1e-6
        minVMR         = -1e-10
        dofFlag        = True
        cnvFlag        = True
        validFlag      = True

    if gasName.lower() == 'hno3':
        gasName        = 'HNO3'
        tcFlag         = False
        pcFlag         = False
        if loc == 'PARAMARIBO':
            minDOFs        = 0.0
        else:
            minDOFs        = 1.0
        maxCHI2        = 5.0
        maxVMR         = 1e-6
        minVMR         = -1e-9
        dofFlag        = True
        cnvFlag        = True
        validFlag      = True
        minCO2         = -3e23
        maxCO2         = 3e23
        co2f           = True

    if gasName.lower() == 'no2':
        gasName        = 'NO2'
        maxCHI2        = 5.0
        minDOFs        = 0.5
        minVMR         = -1e-10
        dofFlag        = True
        cnvFlag        = True
        validFlag      = True
        
    if gasName.lower() == 'h2co':
        gasName        = 'H2CO'
        maxCHI2        = 10.0
        minVMR         = -1e-11
        maxDOFs        = 2.0
        dofFlag        = True
        cnvFlag        = True
        validFlag      = True


    if instrument.lower() == 'iup004':
        if gasName.lower() == 'CH4':
            gasName = 'CH4'
            maxCHI2 = 2.0
            cnvFlag = True
            valifFlag = True
        
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

    myhdf = hdfsave.HDFsave(gasName,outDir,sfitVer,loc,instrument,attribute_file,granularity,mtype,source,dType='float32')
    
    #------------------------------------------------
    # Here we initialize the HDF object with our data
    # using our pre-defined interface
    #------------------------------------------------

    if maxCHI2 < 9e99:
        chiFlg = True
    
    myhdf.initPy(dataDir, ctlF,  spcDBfile, statLyrFile,iyear, imonth,
                 iday,   fyear, fmonth, fday, mxRMS=maxRMS, mxSZA=maxSZA,
                 rmsFlg=rmsFlag, tcFlg=tcFlag,pcFlg=pcFlag,cnvFlg=cnvFlag,
                 szaFlg=szaFlag, validFlg=validFlag,chiFlg=chiFlg,maxCHI2=maxCHI2,
                 minVMR=minVMR,maxVMR=maxVMR,dofFlg=dofFlag,minDOF=minDOFs,maxDOF=maxDOFs,
                 co2Flag=co2Flag,minCO2=minCO2,maxCO2=maxCO2,
                 maxTCTotErr=maxTCTotErr)

    #--------------------------------------------
    # Here we are actually creating the HDF file.
    # We can create either and HDF4 or HDF5 file
    #--------------------------------------------
    filename = myhdf.createHDF4()
    #myhdf.createHDF5()
    
    print ('Finished creating HDF file')
    return(filename)
    
if __name__ == "__main__":
    filename = main(sys.argv)
