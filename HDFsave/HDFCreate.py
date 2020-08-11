#! /usr/bin/python3
#----------------------------------------------------------------------------------------
# Name:
#        HDFCreate.py
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
import os, sys
sys.path.append((os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "HDFsave")))
import numpy as np
import getopt
import os
import sys

def usage():
    ''' Prints to screen standard program usage'''
    print ('HDFCreate.py -i <inputfile> -?')
    print ('  -i <file> : Run HDFCreate.py with specified input file')
    print ('  -?        : Show all flags')

def ckDir(dirName,logFlg=False,exit=False):
    ''' '''
    if not os.path.exists( dirName ):
        print ('Input Directory %s does not exist' % (dirName))
        if logFlg: logFlg.error('Directory %s does not exist' % dirName)
        if exit: sys.exit()
        return False
    else:
        return True    

def ckFile(fName,logFlg=False,exit=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print ('File %s does not exist' % (fName))
        if logFlg: logFlg.error('Unable to find file: %s' % fName)
        if exit: sys.exit()
        return False
    else:
        return True

def ckDirMk(dirName,logFlg=False):
    ''' '''
    if not ( os.path.exists(dirName) ):
        os.makedirs( dirName )
        if logFlg: logFlg.info( 'Created folder %s' % dirName)  
        return False
    else:
        return True

def checker(Inputs, variables):
    ''' '''
    for v in variables:
        if not v in Inputs:
            print ('Error: Variable %s in Input file is missing' % (v))
            exit()


def main(argv):

    overDFlg = False
    h5Flg    = False
    #--------------------------------
    # Retrieve command line arguments
    #--------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:d:h?')

    except getopt.GetoptError as err:
        print (str(err))
        usage()
        sys.exit()

    #-----------------------------
    # Parse command line arguments
    #-----------------------------
    for opt, arg in opts:
        # Check input file flag and path
        if opt == '-i':

            Inputs = {}

            ckFile(arg,exit=True)

            try:
                execfile(arg, Inputs)
            except IOError as errmsg:
                print (errmsg + ' : ' + arg)
                sys.exit()
            except:
                exec(compile(open(arg, "rb").read(), arg, 'exec'), Inputs)

            if '__builtins__' in Inputs:
                del Inputs['__builtins__'] 

        elif opt == '-d':

            if len(arg) == 8:

                dates   = arg.strip().split()

                iyear   = int(dates[0][0:4])
                imnth   = int(dates[0][4:6])
                iday    = int(dates[0][6:8])

                fyear   = int(dates[0][0:4])
                fmnth   = int(dates[0][4:6])
                fday    = int(dates[0][6:8])


            elif len(arg) == 17:

                dates   = arg.strip().split()

                iyear   = int(dates[0][0:4])
                imnth   = int(dates[0][4:6])
                iday    = int(dates[0][6:8])

                fyear   = int(dates[0][9:13])
                fmnth   = int(dates[0][13:15])
                fday    = int(dates[0][15:17])

            else:
                print ('Error in input date')
                usage()
                sys.exit()

            overDFlg = True

        elif opt == '-h':  
            h5Flg  = True         

        # Show all command line flags
        elif opt == '-?':
            usage()
            sys.exit()

        else:
            print ('Unhandled option: ' + opt)
            sys.exit()
    
    if overDFlg:
        Inputs['iyear'] = iyear
        Inputs['imnth'] = imnth
        Inputs['iday']  = iday
        
        Inputs['fyear'] = fyear
        Inputs['fmnth'] = fmnth
        Inputs['fday']  = fday


    #----------------------
    # Checker
    #----------------------
    variables = ['loc', 'gasName', 'ver', 'ctlFile', 'locID', 'sfitVer', 'fileVer', 'projectID', 'geoms_tmpl', 'geoms_meta', 'pyFlg', 'yrlFlg',
            'spcDBFile', 'statLyrFile', 'iyear', 'fyear', 'errFlg', 'dataDir', 'outDir']
    checker(Inputs, variables)


    #---------------------------------
    # Check for the existance of files 
    # directories from input file
    #---------------------------------
    ckDir(Inputs['dataDir'], exit=True)
    ckFile(Inputs['ctlFile'], exit=True)

    if Inputs['pyFlg']:
        ckFile(Inputs['spcDBFile'], exit=True)
        ckFile(Inputs['statLyrFile'], exit=True)

    ckDirMk(Inputs['outDir'])

    #------------------
    # For IDL interface
    #------------------
    if Inputs['pyFlg'] == False:
        ckFile(Inputs['idlFname'], exit=True)

    #------------------
    # Import hdfsaveLOC.py should exist in order to save Meta Data
    #------------------

    if 'hdfMeta' in Inputs:
        if os.path.isabs(Inputs['hdfMeta']):
            
            sys.path.append(os.path.split(Inputs['hdfMeta'])[0])
            hdfsaveFile = os.path.splitext(os.path.split(Inputs['hdfMeta'])[1])[0]

        else:
            print (Inputs['hdfMeta'])
            hdfsaveFile = os.path.splitext(Inputs['hdfMeta'])[0]
    
    else:    
        hdfsaveFile  = 'hdfsave'+Inputs['loc'].upper()

    try:

        hdfsave =  __import__(hdfsaveFile)

    except Exception as errmsg:
        print ('!Error while importing hdfsave: {} !!!'.format(hdfsaveFile))
        exit()

    #------------------
    #
    #------------------
    if 'dQuality' in Inputs: dQuality = Inputs['dQuality']
    else: dQuality =False

    #------------------------------------------------------------
    # Here we create an instance of the HDFsave object. We define
    # that the data written to the HDF file will be REAL (float32)
    # precision. You can also define DOUBLE (float64). Note the
    # variable DATETIME will always be written as a DOUBLE as
    # specified in GEOMS: http://avdc.gsfc.nasa.gov/index.php?site=1989220925
    #------------------------------------------------------------
    
    myhdf = hdfsave.HDFsave(Inputs['gasName'],Inputs['outDir'], Inputs['sfitVer'], Inputs['locID'], Inputs['fileVer'], Inputs['projectID'],  
                            Inputs['geoms_tmpl'], Inputs['geoms_meta'], dType='float32', h5Flg=h5Flg, quality=dQuality)


    if Inputs['yrlFlg']:

        years          = np.arange(Inputs['iyear'], Inputs['fyear']+1, 1)
        ErrYearFlg = False
        ErrYear    = []


        for year in years:
        
            iyear          = year
            imonth         = 1
            iday           = 1
            fyear          = year
            fmonth         = 12
            fday           = 31

            #------------------------------------------------
            # Here we initialize the HDF object with our data
            # using our pre-defined interface
            #------------------------------------------------
            if Inputs['pyFlg'] == False:
                print ('\n')
                print ('*************************************************')
                print ('*************Using IDL Interface*****************')
                print ('*************************************************')
                print ('\n')
                
                myhdf.initIDL(Inputs['idlFname'],iyear,imonth,iday,fyear,fmonth,fday)
            
            if Inputs['pyFlg'] == True:
                print ('\n')
                print ('*************************************************')
                print ('*************Using Python Interface**************')
                print ('*************************************************')
                print ('\n') 

                print("Creating HDF file for year: " + str(year) + '\n')

                myhdf.initPy(Inputs['dataDir'],Inputs['ctlFile'],Inputs['spcDBFile'],Inputs['statLyrFile'],iyear,imonth,iday,fyear,fmonth,fday,
                    mxRMS=Inputs['maxRMS'], minDOF=Inputs['minDOF'],maxDOF=Inputs['maxDOF'],minSZA=Inputs['minSZA'],mxSZA=Inputs['maxSZA'],maxCHI=Inputs['maxCHI'],minTC=Inputs['minTC'],
                    maxTC=Inputs['maxTC'], dofFlg=Inputs['dofFlg'],rmsFlg=Inputs['rmsFlg'],tcFlg=Inputs['tcNegFlg'],pcFlg=Inputs['pcNegFlg'],cnvFlg=Inputs['cnvrgFlg'],
                    szaFlg=Inputs['szaFlg'], chiFlg=Inputs['chiFlg'],errFlg=Inputs['errFlg'],tcMMflg=Inputs['tcMMFlg'], h2oFlg=Inputs['h2oFlg'], geomsTmpl=Inputs['geoms_tmpl'])
         
            #--------------------------------------------
            # Here we are actually creating the HDF file.
            # We can create either and HDF4 or HDF5 file
            #--------------------------------------------
            if h5Flg: myhdf.createHDF5(geomsTmpl=Inputs['geoms_tmpl'])
            else:     myhdf.createHDF4(geomsTmpl=Inputs['geoms_tmpl'])

            print ('\nHDF created for year: {}'.format(iyear))

        if ErrYearFlg:
            for y in ErrYear:
                print ('\nError detected in year: {}'.format(y))
        else:
            print ('\nHDF file(s) successfully created\n')

    else:

        idateStr = "{0:04d}{1:02d}{2:02d}".format(Inputs['iyear'],Inputs['imnth'],Inputs['iday'])
        fdateStr = "{0:04d}{1:02d}{2:02d}".format(Inputs['fyear'],Inputs['fmnth'],Inputs['fday'])


        myhdf.initPy(Inputs['dataDir'],Inputs['ctlFile'],Inputs['spcDBFile'],Inputs['statLyrFile'],Inputs['iyear'],Inputs['imnth'],Inputs['iday'],Inputs['fyear'],Inputs['fmnth'],Inputs['fday'],
            mxRMS=Inputs['maxRMS'], minDOF=Inputs['minDOF'],maxDOF=Inputs['maxDOF'],minSZA=Inputs['minSZA'],mxSZA=Inputs['maxSZA'],maxCHI=Inputs['maxCHI'],minTC=Inputs['minTC'],
            maxTC=Inputs['maxTC'], dofFlg=Inputs['dofFlg'],rmsFlg=Inputs['rmsFlg'],tcFlg=Inputs['tcNegFlg'],pcFlg=Inputs['pcNegFlg'],cnvFlg=Inputs['cnvrgFlg'],
            szaFlg=Inputs['szaFlg'], chiFlg=Inputs['chiFlg'],errFlg=Inputs['errFlg'],tcMMflg=Inputs['tcMMFlg'], h2oFlg=Inputs['h2oFlg'],  geomsTmpl=Inputs['geoms_tmpl'])

        if h5Flg: myhdf.createHDF5(geomsTmpl=Inputs['geoms_tmpl'])
        else:     myhdf.createHDF4(geomsTmpl=Inputs['geoms_tmpl'])

        print ('\nHDF file(s) successfully created\n')
    


if __name__ == "__main__":
    main(sys.argv[1:])
