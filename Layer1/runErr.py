#! /usr/bin/python3
#----------------------------------------------------------------------------------------
# Name:
#        runErr.py
#
# Purpose:
#       Wrapper to run python errAnalysis
#
#
#
# Notes:
#       1)
#			
#
#
# Version History:
#       Created, May, 2014  Eric Nussbaumer (ebaumer@ucar.edu)
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

                                #-------------------------#
                                # Import Standard modules #
                                #-------------------------#

import os, sys
sys.path.append((os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "ModLib")))
import sfitClasses as sc
from Layer1Mods_v2 import errAnalysis
from dataOutClass import _DateRange as dRange

                                #--------------------------#
                                #                          #
                                #  -- Helper functions --  #
                                #                          #
                                #--------------------------#
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
        
def ckDir(dirName,logFlg=False,exit=False):
    ''' '''
    if not os.path.exists( dirName ):
        print ('Input Directory %s does not exist' % (dirName))
        if logFlg: logFlg.error('Directory %s does not exist' % dirName)
        if exit: sys.exit()
        return False
    else:
        return True 
    
                                #----------------------------#
                                #                            #
                                #        --- Main---         #
                                #                            #
                                #----------------------------#    
    
    
def main():
    
    #--------------------------------
    # Initialize date and insitu vars
    #--------------------------------
    loc        = 'fl0'
    gas        = 'ocs'
    ver        = 'Current_v9'
    #sbFileName = '/data/pbin/Dev_Ivan/Layer1/sbDefaults.ctl'
    dataDir    = '/data1/ebaumer/'+loc.lower()+'/'+gas.lower()+'/'+ver+'/'
    
    sbFileName = '/data1/ebaumer/fl0/ocs/x.ocs/sb_v8.ctl'
    iyear      = 2010
    imnth      = 1
    iday       = 1
    fyear      = 2019
    fmnth      = 12
    fday       = 31    
        
    #--------------------------
    # Check if directory exists
    #--------------------------
    ckDir(dataDir,exit=True)
    
    #-------------------------------
    # Check existance of sb.ctl file
    #-------------------------------
    ckFile(sbFileName,exit=True)
    
    #---------------------
    # Establish date range
    #---------------------
    dates = dRange(iyear, imnth, iday, fyear, fmnth, fday)
    
    #----------------------------------------------------
    # Initialize Sb ctl file. Assuming in single location
    #----------------------------------------------------
    sbCtlFile = sc.CtlInputFile(sbFileName)
    sbCtlFile.getInputs()    

    # if 'sbdefflg' in sbCtlFile.inputs:

    #     if sbCtlFile.inputs['sbdefflg'][0] == 'T':

    #         if ckFile(sbCtlFile.inputs['sbdefaults'][0], exit=True):

    #             sbDefCtlFileName = sbCtlFile.inputs['sbdefaults'][0]
    #             sbctldefaults = sc.CtlInputFile(sbDefCtlFileName)
    #             sbctldefaults.getInputs()
        
    #     else: sbctldefaults = False

    # else: sbctldefaults = False

    
    #--------------------------------------------
    # Walk through first level of directories and
    # collect directory names for processing
    #--------------------------------------------
    #for drs in os.walk(dataDir).next()[1]: 
    for drs in next(iter(os.walk(dataDir)))[1]:  

        #-------------------------------------------
        # Test directory to make sure it is a number
        #-------------------------------------------
        try:    int(drs[0:4])
        except: continue

        #------------------------------------------------------
        # Make sure directory falls within specified date range
        #------------------------------------------------------
        if dates.inRange(int(drs[0:4]), int(drs[4:6]), int(drs[6:8]) ):  

            #---------------------------
            # sfit and sb ctl file names
            #---------------------------
            curDir      = dataDir + drs + '/'
            ctlFileName = curDir + 'sfit4.ctl'
            
            #---------------------------------
            # Check sfit4.ctl and Sb.ctl files
            #---------------------------------
            if not ckFile(ctlFileName): continue
            
            #-----------------------------------
            # Initialize sfit and sb ctl classes
            #-----------------------------------
            ctlFile = sc.CtlInputFile(ctlFileName)
            ctlFile.getInputs()

            if 'file.in.sbdflt' in ctlFile.inputs:
                if ckFile(ctlFile.inputs['file.in.sbdflt'][0], exit=True): 
                    sbCtlFileName = ctlFile.inputs['file.in.sbdflt'][0]
                    sbCtlFile = sc.CtlInputFile(sbCtlFileName)
                    sbCtlFile.getInputs()

            else:
                print('Error: file.in.sbdflt is missing in {}'.format(ctlFile))
                #exit()
            
            #-------------------
            # Run error analysis
            #-------------------
            print (curDir)
            rtn = errAnalysis(ctlFile,sbCtlFile,False,curDir)
            #errAnalysis( ctlFileGlb, SbctlFileVars, False, wrkOutputDir3, logFile )
            if not rtn: print ('Unable to run error analysis in directory = {}'.format(curDir))

            
        
            
if __name__ == "__main__":
    main()
