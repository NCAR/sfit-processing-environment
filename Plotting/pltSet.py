#! /usr/bin/python3
##! /usr/bin/python 
# Change the above line to point to the location of your python executable
#----------------------------------------------------------------------------------------
# Name:
#        pltSet.py
#
# Purpose:
#       This program is use to plot multiple sfit4 results. It includes  
#           -- Fit retrievals/residuals in all micro-windows
#           -- Averaging Kernels (Matrix, vmr, and unitless)
#           -- Profiles of all gases in mixing ratios
#           -- Profile error are shown if error are calculated 
#           -- Time Series, trends, etc
#
#
# External called functions:
#        This program calls dataOutClass
#
#
# Notes:
#       1) Options include:
#            -i <setInput.py> : Input File (python syntax) 
#            -?               : Show all flags
#
#
# Usage:
#      >> pltSet.py
#
# Examples:
#      Runs pltSet.py for current working director
#      >> pltSet.py -i setInput.py
#
#
# Version History:
#       Created, May, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
#       Version history stored in git repository
#
#       Modified, Sep 2019, Ivan Ortega (iortega@ucar.edu)
#
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


#---------------
# Import modules
#---------------
import os, sys
sys.path.append((os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "ModLib")))
import getopt
import dataOutClass as dc
import time


def usage():
    ''' Prints to screen standard program usage'''
    print ('pltSet.py -i <inputfile> -?')
    print ('  -i <file> : Run pltSet.py with specified input file')
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

def main(argv):

    #--------------------------------
    # Retrieve command line arguments
    #--------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:q?')

    except getopt.GetoptError as err:
        print (str(err))
        usage()
        sys.exit()

    ckQualityFlg = False

    #-----------------------------
    # Parse command line arguments
    #-----------------------------
    for opt, arg in opts:
        # Check input file flag and path
        if opt == '-i':

            pltInputs = {}

            ckFile(arg,exit=True)

            try:
                execfile(arg, pltInputs)
            except IOError as errmsg:
                print (errmsg + ' : ' + arg)
                sys.exit()
            except:
                exec(compile(open(arg, "rb").read(), arg, 'exec'), pltInputs)

            if '__builtins__' in pltInputs:
                del pltInputs['__builtins__']               

        elif opt == '-?':
            usage()
            sys.exit()

        else:
            print ('Unhandled option: ' + opt)
            sys.exit()


    #---------------------------------
    # Check for the existance of files 
    # directories from input file
    #---------------------------------
    ckDir(pltInputs['retDir'], exit=True)
    ckFile(pltInputs['ctlFile'], exit=True)
    if pltInputs['saveFlg']:  ckDir(os.path.dirname(os.path.realpath(pltInputs['pltFile'])),exit=True)

    #-------------------------
    # Create Instance of Class
    #-------------------------
    gas = dc.PlotData(pltInputs['retDir'],pltInputs['ctlFile'],iyear=pltInputs['iyear'],imnth=pltInputs['imnth'],iday=pltInputs['iday'],
                fyear=pltInputs['fyear'],fmnth=pltInputs['fmnth'],fday=pltInputs['fday'],saveFlg=pltInputs['saveFlg'], outFname=pltInputs['pltFile'])

    #----------------------
    # Call to plot profiles
    #----------------------
    gas.pltPrf(fltr=pltInputs['fltrFlg'],allGas=False,sclfct=pltInputs['sclfct'],sclname=pltInputs['sclfctName'],mnthFltr=pltInputs["mnths"],mnthFltFlg=pltInputs["mnthFlg"],
           errFlg=pltInputs['errorFlg'],minSZA=pltInputs['minSZA'],maxSZA=pltInputs['maxSZA'],maxRMS=pltInputs['maxRMS'],minTC=pltInputs['minTC'],maxTC=pltInputs['maxTC'],
           minDOF=pltInputs['minDOF'], maxDOF=pltInputs['maxDOF'], maxCHI=pltInputs['maxCHI'],dofFlg=pltInputs['dofFlg'],rmsFlg=pltInputs['rmsFlg'],tcFlg=pltInputs['tcNegFlg'],
           pcFlg=pltInputs['pcNegFlg'],szaFlg=pltInputs['szaFlg'],cnvrgFlg=pltInputs['cnvrgFlg'],chiFlg=pltInputs['chiFlg'],tcMMflg=pltInputs['tcMMFlg'],
           bckgFlg=pltInputs['bckgFlg'], minSlope=pltInputs['minSlope'], maxSlope=pltInputs['maxSlope'], minCurv=pltInputs['minCurv'], maxCurv=pltInputs['maxCurv'])


    # #-----------------
    # # Call to plot AVK
    # #-----------------
    try:
        gas.pltAvk(fltr=pltInputs['fltrFlg'],errFlg=pltInputs['errorFlg'],partialCols=pltInputs['pCols'],mnthFltr=pltInputs["mnths"],mnthFltFlg=pltInputs["mnthFlg"],
                  minSZA=pltInputs['minSZA'],maxSZA=pltInputs['maxSZA'],maxRMS=pltInputs['maxRMS'],minTC=pltInputs['minTC'],maxTC=pltInputs['maxTC'],
                  minDOF=pltInputs['minDOF'], maxDOF=pltInputs['maxDOF'],maxCHI=pltInputs['maxCHI'],dofFlg=pltInputs['dofFlg'],rmsFlg=pltInputs['rmsFlg'],
                  tcFlg=pltInputs['tcNegFlg'],pcFlg=pltInputs['pcNegFlg'],szaFlg=pltInputs['szaFlg'],
                  chiFlg=pltInputs['chiFlg'],cnvrgFlg=pltInputs['cnvrgFlg'],tcMMflg=pltInputs['tcMMFlg'],
                  bckgFlg=pltInputs['bckgFlg'], minSlope=pltInputs['minSlope'], maxSlope=pltInputs['maxSlope'], minCurv=pltInputs['minCurv'], maxCurv=pltInputs['maxCurv'])
    except:
        print ("Unable to plot AVK!!")

    #-------------------
    # Plot total columns
    #-------------------
    gas.pltTotClmn(fltr=pltInputs['fltrFlg'],sclfct=pltInputs['sclfct'],sclname=pltInputs['sclfctName'],mnthFltr=pltInputs["mnths"],mnthFltFlg=pltInputs["mnthFlg"],
                   partialCols=pltInputs['pCols'],errFlg=pltInputs['errorFlg'],minSZA=pltInputs['minSZA'],minTC=pltInputs['minTC'],maxTC=pltInputs['maxTC'],
                   maxSZA=pltInputs['maxSZA'],maxRMS=pltInputs['maxRMS'],minDOF=pltInputs['minDOF'],maxCHI=pltInputs['maxCHI'],
                   dofFlg=pltInputs['dofFlg'], maxDOF=pltInputs['maxDOF'],rmsFlg=pltInputs['rmsFlg'],tcFlg=pltInputs['tcNegFlg'],
                   pcFlg=pltInputs['pcNegFlg'],szaFlg=pltInputs['szaFlg'],chiFlg=pltInputs['chiFlg'],cnvrgFlg=pltInputs['cnvrgFlg'],tcMMflg=pltInputs['tcMMFlg'],
                   bckgFlg=pltInputs['bckgFlg'], minSlope=pltInputs['minSlope'], maxSlope=pltInputs['maxSlope'], minCurv=pltInputs['minCurv'], maxCurv=pltInputs['maxCurv'])

    #------------------
    # Plot Spectral fit
    #------------------
    try:
        gas.pltSpectra(fltr=pltInputs['fltrFlg'],minSZA=pltInputs['minSZA'],maxSZA=pltInputs['maxSZA'],minTC=pltInputs['minTC'],maxTC=pltInputs['maxTC'],
                         maxRMS=pltInputs['maxRMS'],minDOF=pltInputs['minDOF'], maxDOF=pltInputs['maxDOF'],maxCHI=pltInputs['maxCHI'],dofFlg=pltInputs['dofFlg'],
                         rmsFlg=pltInputs['rmsFlg'],tcFlg=pltInputs['tcNegFlg'],pcFlg=pltInputs['pcNegFlg'],mnthFltr=pltInputs["mnths"],mnthFltFlg=pltInputs["mnthFlg"],
                         szaFlg=pltInputs['szaFlg'],chiFlg=pltInputs['chiFlg'],cnvrgFlg=pltInputs['cnvrgFlg'],tcMMflg=pltInputs['tcMMFlg'],
                         bckgFlg=pltInputs['bckgFlg'], minSlope=pltInputs['minSlope'], maxSlope=pltInputs['maxSlope'], minCurv=pltInputs['minCurv'], maxCurv=pltInputs['maxCurv'])

    except:
        print ("Unable to plot Mean Fit!!")

    #--------------------
    # Create yearly plots
    #--------------------
    if pltInputs['byYrFlg']:
        for year in gas.yearList():
            if pltInputs['saveFlg']: fname = pltInputs['pltFile'][:-4]+'_'+str(year)+'.pdf'
            else:                    fname = ''
            gasYr = dc.PlotData(pltInputs['retDir'],pltInputs['ctlFile'],iyear=pltInputs['iyear'],imnth=1,iday=1,fyear=year,fmnth=12,fday=31,outFname=fname)
            gas.pltPrf(fltr=pltInputs['fltrFlg'],allGas=False,sclfct=pltInputs['sclfct'],sclname=pltInputs['sclfctName'],
                       errFlg=pltInputs['errorFlg'],minSZA=pltInputs['minSZA'],maxSZA=pltInputs['maxSZA'],maxRMS=pltInputs['maxRMS'],minTC=pltInputs['minTC'],maxTC=pltInputs['maxTC'],
                       minDOF=pltInputs['minDOF'], maxDOF=pltInputs['maxDOF'],maxCHI=pltInputs['maxCHI'],dofFlg=pltInputs['dofFlg'],rmsFlg=pltInputs['rmsFlg'],tcFlg=pltInputs['tcNegFlg'],mnthFltr=pltInputs["mnths"],mnthFltFlg=pltInputs["mnthFlg"],
                       pcFlg=pltInputs['pcNegFlg'],szaFlg=pltInputs['szaFlg'],chiFlg=pltInputs['chiFlg'],cnvrgFlg=pltInputs['cnvrgFlg'],tcMMflg=pltInputs['tcMMFlg'],
                       bckgFlg=pltInputs['bckgFlg'], minSlope=pltInputs['minSlope'], maxSlope=pltInputs['maxSlope'], minCurv=pltInputs['minCurv'], maxCurv=pltInputs['maxCurv'])
            gas.pltTotClmn(fltr=pltInputs['fltrFlg'],sclfct=pltInputs['sclfct'],sclname=pltInputs['sclfctName'],
                           partialCols=pltInputs['pCols'],errFlg=pltInputs['errorFlg'],minSZA=pltInputs['minSZA'],minTC=pltInputs['minTC'],maxTC=pltInputs['maxTC'],
                           maxSZA=pltInputs['maxSZA'],maxRMS=pltInputs['maxRMS'],minDOF=pltInputs['minDOF'], maxDOF=pltInputs['maxDOF'],maxCHI=pltInputs['maxCHI'],
                           dofFlg=pltInputs['dofFlg'],rmsFlg=pltInputs['rmsFlg'],tcFlg=pltInputs['tcNegFlg'],mnthFltr=pltInputs["mnths"],mnthFltFlg=pltInputs["mnthFlg"],
                           pcFlg=pltInputs['pcNegFlg'],szaFlg=pltInputs['szaFlg'],chiFlg=pltInputs['chiFlg'],cnvrgFlg=pltInputs['cnvrgFlg'],tcMMflg=pltInputs['tcMMFlg'],
                           bckgFlg=pltInputs['bckgFlg'], minSlope=pltInputs['minSlope'], maxSlope=pltInputs['maxSlope'], minCurv=pltInputs['minCurv'], maxCurv=pltInputs['maxCurv'])
            if pltInputs['saveFlg']: gasYr.closeFig()

    print('\nFinished Plots.......\n')

    #--------------------------------
    # Pause so user can look at plots
    #--------------------------------
    if pltInputs['saveFlg']: gas.closeFig()
    else: 
        try:    user_input = raw_input('Press any key to exit >>> ')
        except: user_input = input('Press any key to exit >>> ')
        sys.exit()    


if __name__ == "__main__":
    main(sys.argv[1:])
