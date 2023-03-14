#! /usr/bin/python3
##! /usr/bin/python 
# Change the above line to point to the location of your python executable
#----------------------------------------------------------------------------------------
# Name:
#        ckRets.py
#
# Purpose:
#       This program is use to check retrievl folders  
#           - If summary file is not found or with error, it will delete the directory (DEFAULT)
#           - OPTIONAL to check for Error summary
#           - Recommended when issues arise when using pltSet.py (e.g., error while reading summary files)
#
# External called functions:
#        This program calls dataOutClass
#
# Notes:
#       1) Options include:
#            -i <setInput.py> : Input File (python syntax) - tipically the same input as in pltSet.py (setInput.py)
#            -?               : Show all flags
#
#
# Modify inputs below
#
# Version History:
#       Created, Dec 2020, Ivan Ortega (iortega@ucar.edu)
#       
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
    print ('ckRets.py -i <inputfile> -?')
    print ('  -i <file> : Run ckRets.py with specified input file (typically the setInput.py)')
    print ('  -e        : optional: check for error summary file, if not error summary it will delete folder\n              Default is to check only for summary file')
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

    mainInF  = False

    #--------------------------------
    # Retrieve command line arguments
    #--------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:e?')

    except getopt.GetoptError as err:
        print (str(err))
        usage()
        sys.exit()

    errFlg = False

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

            mainInF  = True     

        elif opt == '-e':
            errFlg = True

        elif opt == '-?':
            usage()
            sys.exit()

        else:
            print ('Unhandled option: ' + opt)
            sys.exit()


    if not mainInF:
        print('Error! usage:') 
        usage()
        exit()


    #---------------------------------
    # Check for the existance of files 
    # directories from input file
    #---------------------------------
    ckDir(pltInputs['retDir'], exit=True)
    ckFile(pltInputs['ctlFile'], exit=True)
    
    #-------------------------
    # Create Instance of Class
    #-------------------------
    gas = dc.ckRetrievals(pltInputs['retDir'],pltInputs['ctlFile'],iyear=pltInputs['iyear'],imnth=pltInputs['imnth'],iday=pltInputs['iday'],
                fyear=pltInputs['fyear'],fmnth=pltInputs['fmnth'],fday=pltInputs['fday'])

    #----------------------
    # Call to check quality, e.g., if Summary is not good/present it will remove the directory
    #----------------------
    gas.ckSummary()
    if errFlg: gas.ckErrorSummary()


if __name__ == "__main__":
    main(sys.argv[1:])
