#! /bira-iasb/softs/19g/py37/bin/python
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
#           4) errAnalysis from Layer1mods.py
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
#       Modified Sep, 2019  Ivan Ortega (iortega@ucar.edu)
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
import glob
import getopt
import sfitClasses as sc
#from Layer1Mods import errAnalysis

#---------------
# python 3 or 2.7
#---------------
try: 
    from tkinter import filedialog
    from tkinter import *

except ImportError:
    from Tkinter import Tk
    import Tkinter, Tkconstants, tkFileDialog

#------------------------
# Define helper functions
#------------------------
def usage(binDirVer):
        print('sfit4Layer0.py -f <str> [-i <dir> [-b <dir/str> -?] \n\n'
             '-i <dir>     Data directory. Optional: default is current working directory\n'
             '-f <str>     Run Flags: Necessary: h = hbin, p = pspec, s = sfit4, e = error analysis, c = clean\n'
             '-b <dir/str> Binary sfit directory. Optional: default is hard-coded in main(). Also accepts v1, v2, etc.\n')
        
        for ver in binDirVer:
            print ('             {}:{}'.format(ver,binDirVer[ver]))

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
        'v5':   '/Users/jamesw/FDP/sfit/400/src/src-irwg14-mp',
        'v6':   '/data/ebaumer/Code/sfit-core-code-Official_Release_1.0/src/'}

        #----------
        # Run flags
        #----------
        hbinFlg  = False                                          # Flag to run hbin
        pspecFlg = False                                          # Flag to run pspec
        sfitFlg  = False                                          # Flag to run sfit4
        errFlg   = False                                          # Flag to run error analysis
        clnFlg   = False                                          # Flag to clean directory of output files listed in ctl file
        pyv2Flg  = False

        #--------------------------------
        # Retrieve command line arguments
        #--------------------------------
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'i:b:f:o?')

        except getopt.GetoptError as err:
            print(str(err))
            usage(binDirVer)
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
                        except KeyError: print('{} not a recognized version for -b option'.format(arg)); sys.exit()

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
                    elif f.lower() == 'c': clnFlg   = True
                    else: print ('{} not an option for -f ... ignored'.format(f))
            elif opt == '-?':
                usage(binDirVer)
                sys.exit()
  
            # Option to import error analysis v2 - temporary
            elif opt == '-o':
                pyv2Flg = True

            else:
                print ('Unhandled option: {}'.format(opt))
                sys.exit()

        if pyv2Flg: from Layer1Mods_v2 import errAnalysis
        else: from Layer1Mods import errAnalysis

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
            try:
                Tk().withdraw()
                ctlFileName = tkFileDialog.askopenfilename(initialdir =wrkDir, title = "Select sfit4 ctl file",filetypes = (("ctl files","*.ctl"),("all files","*.*")))
            except:
                ctlFileName =  filedialog.askopenfilename(initialdir =wrkDir, title = "Select sfit4 ctl file",filetypes = (("ctl files","*.ctl"),("all files","*.*")))


              
        ctlFile = sc.CtlInputFile(ctlFileName)
        ctlFile.getInputs()

        #------------------------
        # Initialize sb ctl class
        #------------------------
        if errFlg:

            if pyv2Flg:

                #------------------------
                #
                #------------------------
                if sc.ckFile(wrkDir+'sb.ctl'): sbCtlFileName = wrkDir + 'sb.ctl'
                else: 

                    try:
                        Tk().withdraw()
                        sbCtlFileName = tkFileDialog.askopenfilename(initialdir =wrkDir, title = "Select sb ctl file",filetypes = (("ctl files","*.ctl"),("all files","*.*")))
                    except:
                        sbCtlFileName =  filedialog.askopenfilename(initialdir =wrkDir, title = "Select sb ctl file",filetypes = (("ctl files","*.ctl"),("all files","*.*")))
                    
                sbCtlFile = sc.CtlInputFile(sbCtlFileName)
                sbCtlFile.getInputs()


                if 'sbdefflg' in sbCtlFile.inputs:

                    if sbCtlFile.inputs['sbdefflg'][0] == 'T':

                        if sc.ckFile(sbCtlFile.inputs['sbdefaults'][0], exitFlg=True):

                            sbDefCtlFileName = sbCtlFile.inputs['sbdefaults'][0]
                            sbctldefaults = sc.CtlInputFile(sbDefCtlFileName)
                            sbctldefaults.getInputs()
                    
                    else: sbctldefaults = False

                else: sbctldefaults = False

            else:

                if sc.ckFile(ctlFile.inputs['file.in.sbdflt'][0]): sbCtlFileName = ctlFile.inputs['file.in.sbdflt'][0]
                    
                else:
                    try:
                        Tk().withdraw()
                        sbCtlFileName = tkFileDialog.askopenfilename(initialdir =wrkDir, title = "Select sb ctl file",filetypes = (("ctl files","*.ctl"),("all files","*.*")))
                    except:
                        sbCtlFileName =  filedialog.askopenfilename(initialdir =wrkDir, title = "Select sb ctl file",filetypes = (("ctl files","*.ctl"),("all files","*.*")))
                
                
                sbCtlFile = sc.CtlInputFile(sbCtlFileName)
                sbCtlFile.getInputs()

            

        #---------------------------
        # Clean up output from sfit4
        #---------------------------
    
        if clnFlg:
            for k in ctlFile.inputs:
                if 'file.out' in k:
                    try:            os.remove(wrkDir + ctlFile.inputs[k][0])
                    except OSError: pass

                for f in glob.glob(wrkDir + 'spc.*'): os.remove(f)
                for f in glob.glob(wrkDir + 'raytrace.*'): os.remove(f)
                for f in glob.glob(wrkDir + '*Error.*'): os.remove(f)
                for f in glob.glob(wrkDir + '*.output'): os.remove(f)

        #----------
        # Run pspec
        #----------
        if pspecFlg:
            print ('*************')
            print ('Running pspec')
            print ('*************')
            rtn = sc.subProcRun( [binDir + 'pspec'] )

        #----------
        # Run hbin
        #----------
        if hbinFlg:
            print ('************')
            print ('Running hbin')
            print ('************')
            rtn = sc.subProcRun( [binDir + 'hbin'] )

        #----------
        # Run sfit4
        #----------
        if sfitFlg:
            print ('************')
            print ('Running sfit')
            print ('************')
            rtn = sc.subProcRun( [binDir + 'sfit4'] )

        #-------------------
        # Run error analysis
        #-------------------
        if errFlg:
            print ('**********************')
            print ('Running error analysis')
            print ('**********************')
            if pyv2Flg: rtn = errAnalysis(ctlFile,sbCtlFile,sbctldefaults,wrkDir)
            else: rtn = errAnalysis(ctlFile,sbCtlFile,wrkDir)



if __name__ == "__main__":
        main(sys.argv[1:])
