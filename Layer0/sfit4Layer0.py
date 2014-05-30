#! /usr/bin/python
##! /usr/local/python-2.7/bin/python
##! /usr/bin/python
# Change the above line to point to the location of your python executable
#----------------------------------------------------------------------------------------
# Name:
#        sfit4Layer0.py
#
# Purpose:
#       This file is the zeroth order running of sfit4. It accomplishes the following:
#			1) Calls pspec to convert binary spectra file (bnr) to ascii (t15asc)
#			2) Calls hbin to gather line parameters from hitran
#			3) Calls sfit4
#			4) Calls error analysis from Layer1mods.py
#			5) Clean outputs from sfit4 call
#
#
# External Subprocess Calls:
#			1) pspec executable file from pspec.f90
#			2) hbin  executable file from hbin.f90
#			3) sfit4 executable file from sfit4.f90
#                       4) errAnalysis from Layer1mods.py
#
#
#
# Notes:
#	1) Options include:
#			 -i	<dir>	  : Optional. Data directory. Default is current working directory
#			 -b     <dir/str> : Optional. Binary directory. Default is hard-code.
#			 -f	<str>	  : Run flags, h = hbin, p = pspec, s = sfit4, e = error analysis, c = clean
#
#
# Usage:
# 		./sfit4Layer0.py [options]
#
#
# Examples:
#       1) This example runs hbin, pspec, sfit4, error analys, and cleans working directory prior to execution
#           ./sfit4Layer0.py -f hpsec
#
#       2) This example just runs sfit4
#           ./sfit4Layer0.py -f s
#
#       3) This example cleans the output file created by sfit4 in directory (/User/home/datafiles/) which is not the current directory
#          ./sfit4Layer0.py -i /User/home/datafiles/ -f c
#
# Version History:
#       Created, May, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
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
import sys
import os
import getopt
import sfitClasses as sc
from Layer1Mods import errAnalysis
from Tkinter import Tk
from tkFileDialog import askopenfilename


#------------------------
# Define helper functions
#------------------------
def usage():
        print 'sfit4Layer0.py -f <str> [-i <dir> [-b <dir/str> ] \n'
        print '-i <dir>     Data directory. Optional: default is current working directory'
        print '-b <dir/str> Binary sfit directory. Optional: default is hard-coded in main(). Also accepts v1, v2, etc.'
        print '-f <str>     Run Flags: Necessary: h = hbin, p = pspec, s = sfit4, e = error analysis, c = clean\n'
        sys.exit()


def main(argv):

        #----------------
        # Initializations
        #----------------
         #------------
         # Directories
         #------------
        wrkDir    = os.getcwd()                              # Set current directory as the data directory
        binDir    = '/data/bin'                              # Default binary directory. Used of nothing is specified on command line
        binDirVer = {
        'v1':   '/data/ebaumer/Code/sfit-core-code/src/',    # Version 1 for binary directory (Eric)
        'v2':   '/data/tools/400/sfit-core/src/',             # Version 2 for binary directory (Jim)
        'v3':   '/Users/jamesw/FDP/sfit/400/sfit-core/src/',             # Version 2 for binary directory (Jim)
        'v4':   '/home/ebaumer/Code/sfit4/src/',
        'v5':   '/Users/jamesw/FDP/sfit/400/src/src-irwg14-mp'
        }


         #----------
         # Run flags
         #----------
        hbinFlg  = False                                          # Flag to run hbin
        pspecFlg = False                                          # Flag to run pspec
        sfitFlg  = False                                          # Flag to run sfit4
        errFlg   = False                                          # Flag to run error analysis
        clnFlg   = False                                          # Flag to clean directory of output files listed in ctl file

        #--------------------------------
        # Retrieve command line arguments
        #--------------------------------
        try:
                opts, args = getopt.getopt(sys.argv[1:], 'i:b:f:v')

        except getopt.GetoptError as err:
                print str(err)
                usage()
                sys.exit()

        #-----------------------------
        # Parse command line arguments
        #-----------------------------
        for opt, arg in opts:
                # Data directory
                if opt == '-i':
                        wrkDir = arg
                        sc.ckDir(wrkDir,exitFlg=True)

                # Binary directory
                elif opt == '-b':
                        if not sc.ckDir(arg,exitFlg=False,quietFlg=True):
                                try:             binDir = binDirVer[arg.lower()]
                                except KeyError: print '{} not a recognized version for -b option'.format(arg); sys.exit()

                        else: binDir = arg

                        if not(binDir.endswith('/')): binDir = binDir + '/'

                # Run flags
                elif opt == '-f':
                        flgs = list(arg)
                        for f in flgs:
                                if   f.lower() == 'h': hbinFlg  = True
                                elif f.lower() == 'p': pspecFlg = True
                                elif f.lower() == 's': sfitFlg  = True
                                elif f.lower() == 'e': errFlg   = True
                                elif f.lower() == 'c': clnFile  = True
                                else: print '{} not an option for -f ... ignored'.format(f)

                # Print all versions for binary directories
                elif opt == '-v':
                        for ver in binDirVer:
                                print '{}: {}'.format(ver,binDirVer[ver])
                        sys.exit()

                else:
                        print 'Unhandled option: {}'.format(opt)
                        sys.exit()

        #--------------------------------------
        # If necessary change working directory
        # to directory with input data.
        #--------------------------------------
        if os.path.abspath(wrkDir) != os.getcwd(): os.chdir(wrkDir)
        if not(wrkDir.endswith('/')): wrkDir = wrkDir + '/'

        #--------------------------
        # Initialize sfit ctl class
        #--------------------------
        if sc.ckFile(wrkDir+'sfit4.ctl'): ctlFileName = wrkDir + 'sfit4.ctl'
        else:
                Tk().withdraw()
                ctlFileName = askopenfilename(initialdir=wrkDir,message='Please select sfit ctl file')

        ctlFile = sc.CtlInputFile(ctlFileName)
        ctlFile.getInputs()

        #------------------------
        # Initialize sb ctl class
        #------------------------
        if errFlg:
                if sc.ckFile(wrkDir+'sb.ctl'): sbCtlFileName = wrkDir + 'sb.ctl'
                else:
                        TK().withdraw()
                        sbCtlFileName = askopenfilename(initialdir=wrkDir,message='Please select sb ctl file')

                sbCtlFile = sc.CtlInputFile(sbCtlFileName)
                sbCtlFile.getInputs()

        #---------------------------
        # Clean up output from sfit4
        #---------------------------
        if clnFlg:
                for k in ctlFile.inputs['file.out']:
                        if 'file.out' in k:
                                try:            os.remove(wrkDir + ctlFile.inputs[k])
                                except OSError: pass

        #----------
        # Run pspec
        #----------
        if pspecFlg:
                print '*************'
                print 'Running pspec'
                print '*************'
                rtn = sc.subProcRun( [binDir + 'pspec'] )

        #----------
        # Run hbin
        #----------
        if hbinFlg:
                print '************'
                print 'Running hbin'
                print '************'
                rtn = sc.subProcRun( [binDir + 'hbin'] )

        #----------
        # Run sfit4
        #----------
        if sfitFlg:
                print '************'
                print 'Running sfit'
                print '************'
                rtn = sc.subProcRun( [binDir + 'sfit4'] )

        #-------------------
        # Run error analysis
        #-------------------
        if errFlg:
                print '**********************'
                print 'Running error analysis'
                print '**********************'
                rtn = errAnalysis(ctlFile,sbCtlFile,wrkDir)



if __name__ == "__main__":
        main(sys.argv[1:])
