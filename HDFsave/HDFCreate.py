#! /usr/bin/python
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
#import hdfsaveTAB as hdfsave
#import hdfsaveMLO as hdfsave
#import hdfsaveFL0 as hdfsave
import numpy as np
import getopt
import os
import sys

def usage():
    ''' Prints to screen standard program usage'''
    print 'HDFCreate.py -i <inputfile> -?'
    print '  -i <file> : Run HDFCreate.py with specified input file'
    print '  -?        : Show all flags'

def ckDir(dirName,logFlg=False,exit=False):
    ''' '''
    if not os.path.exists( dirName ):
        print 'Input Directory %s does not exist' % (dirName)
        if logFlg: logFlg.error('Directory %s does not exist' % dirName)
        if exit: sys.exit()
        return False
    else:
        return True    

def ckFile(fName,logFlg=False,exit=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print 'File %s does not exist' % (fName)
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

def main(argv):

    #--------------------------------
    # Retrieve command line arguments
    #--------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:?')

    except getopt.GetoptError as err:
        print str(err)
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
                print errmsg + ' : ' + arg
                sys.exit()

            if '__builtins__' in Inputs:
                del Inputs['__builtins__']               

        # Show all command line flags
        elif opt == '-?':
            usage()
            sys.exit()

        else:
            print 'Unhandled option: ' + opt
            sys.exit()


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

    years          = np.arange(Inputs['iyear'], Inputs['fyear']+1, 1)

    #------------------
    # For IDL interface
    #------------------
    if Inputs['pyFlg'] == False:
        ckFile(Inputs['idlFname'], exit=True)
    
    if Inputs['loc'].lower() == 'tab':
        loc            = 'THULE'
        import hdfsaveTAB as hdfsave
    elif Inputs['loc'].lower() == "mlo":
        loc            = 'MAUNA.LOA.HI'
        import hdfsaveMLO as hdfsave
    else:
        loc            = "BOULDER.COLORADO"
        import hdfsaveFL0 as hdfsave

    sfitVer        = Inputs['sfitVer']                      # This is the version of sfit4 used for the retrievals
    
    for year in years:
    
        iyear          = year
        imonth         = 1
        iday           = 1
        fyear          = year
        fmonth         = 12
        fday           = 31

        print("Creating HDF file for year: " + str(year))

        #------------------------------------------------------------
        # Here we create an instance of the HDFsave object. We define
        # that the data written to the HDF file will be REAL (float32)
        # precision. You can also define DOUBLE (float64). Note the
        # variable DATETIME will always be written as a DOUBLE as
        # specified in GEOMS: http://avdc.gsfc.nasa.gov/index.php?site=1989220925
        #------------------------------------------------------------
        
        myhdf = hdfsave.HDFsave(Inputs['gasName'],Inputs['outDir'],sfitVer,loc,dType='float32')

        #------------------------------------------------
        # Here we initialize the HDF object with our data
        # using our pre-defined interface
        #------------------------------------------------
        if Inputs['pyFlg'] == False:
            print '\n'
            print '*************************************************'
            print '*************Using IDL Interface*****************'
            print '*************************************************'
            print '\n'
            
            myhdf.initIDL(Inputs['idlFname'],iyear,imonth,iday,fyear,fmonth,fday)
        
        if Inputs['pyFlg'] == True:
            print '\n'
            print '*************************************************'
            print '*************Using Python Interface**************'
            print '*************************************************'
            print '\n' 

            myhdf.initPy(Inputs['dataDir'],Inputs['ctlFile'],Inputs['spcDBFile'],Inputs['statLyrFile'],iyear,imonth,iday,fyear,fmonth,fday,
                    mxRMS=Inputs['maxRMS'], minDOF=Inputs['minDOF'],minSZA=Inputs['minSZA'],mxSZA=Inputs['maxSZA'],maxCHI=Inputs['maxCHI'],minTC=Inputs['minTC'],
                    maxTC=Inputs['maxTC'], dofFlg=Inputs['dofFlg'],rmsFlg=Inputs['rmsFlg'],tcFlg=Inputs['tcNegFlg'],pcFlg=Inputs['pcNegFlg'],cnvFlg=Inputs['cnvrgFlg'],
                    szaFlg=Inputs['szaFlg'], chiFlg=Inputs['chiFlg'],errFlg=Inputs['errFlg'],tcMMflg=Inputs['tcMMFlg'], h2oFlg=Inputs['h2oFlg'])

        #--------------------------------------------
        # Here we are actually creating the HDF file.
        # We can create either and HDF4 or HDF5 file
        #--------------------------------------------
        myhdf.createHDF4()
        #myhdf.createHDF5()

    print 'Finished creating HDF file'


if __name__ == "__main__":
    main(sys.argv[1:])
