#! /usr/bin/python3
##! /usr/bin/python
# Change the above line to point to the location of your python executable
#----------------------------------------------------------------------------------------
# Name:
#        pltRet.py
#
# Purpose:
#       This program is use to plot individual results of sfit4
#           -- Jacobian Matrix
#           -- Fit retrievals/residuals in all micro-windows
#           -- Averaging Kernels (Matrix, vmr, and unitless)
#           -- Profiles of all gases in mixing ratios
#           -- Profile error are shown if error are calculated 
#           -- Cumulative sum of DOF profile
#           -- Summary Files, including error summary if present, are printed in terminal
#
#
# External called functions:
#        This program calls dataOutClass
#
#
# Notes:
#       1) Options include:
#            -i <dir>  : Data directory. Optional: default is current working directory
#            -S        : Flag to save results in pltRet.pdf. Optional: default is False and show windows
#            -?        : Show all flags
#
#
# Usage:
#      >> pltRet.py
#
# Examples:
#      Runs pltRet.py for current working director
#      >> pltRet.py
#
#      Runs pltRet.py for specific Directory and save figures in pltRet.pdf
#      >> pltRet.py -S
#
#     Runs pltRet.py for specific Directory
#      >> pltRet.py -i /c2h6/version/20170117.172219/
#
#
# Version History:
#       Created, May, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
#       Version history stored in git repository
#
#       Modified, June, 2018 Ivan Ortega (iortega@ucar.edu)
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

import matplotlib.animation as animation
import matplotlib
from cycler import cycler
import matplotlib.dates as md
from matplotlib.dates import DateFormatter, MonthLocator, YearLocator, DayLocator, HourLocator, MinuteLocator
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FormatStrFormatter, MultipleLocator,AutoMinorLocator,ScalarFormatter
from matplotlib.backends.backend_pdf import PdfPages 
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import matplotlib.gridspec as gridspec


try:
    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning) 
except:
    pass

#------------------------
# Define helper functions
#------------------------
def usage():
        print ('pltRet.py [-i <str> ] ')
        print ('-i <dir>     Data directory. Optional: default is current working directory')
        print ('-f <str>     Run optional Flags: p = profiles only, s = fit only (and Jacobian), k = averaging kernel, b = read/plot bnr; Deafuls is plot all except bnr')
        print ('-S           Flag to save results in pltRet.pdf. Optional: default is False')
        sys.exit()


def main(argv):

        #----------------
        # Initializations
        #----------------
        #------------
        # Directories
        #------------
        wrkDir    = os.getcwd()                              # Set current directory as the data directory
        saveFlg   = False
       
        #--------------------------------
        # Retrieve command line arguments
        #--------------------------------
        try:
                opts, args = getopt.getopt(sys.argv[1:], 'i:f:S?')

        except getopt.GetoptError as err:
                print (str(err))
                usage()
                sys.exit()

        prfFlg  = True
        spcFlg  = True
        akFlg   = True
        bnrFlg  = False

        #-----------------------------
        # Parse command line arguments
        #-----------------------------
        for opt, arg in opts:
                # Data directory
                if opt == '-i':
                    wrkDir = arg
                    dc.ckDir(wrkDir,exitFlg=True)
                elif opt == '-S':

                    saveFlg = True

                elif opt == '-f':
                    
                    flgs = list(arg)
                    
                    for f in flgs:
                        if   f.lower() == 'p': 
                            prfFlg  = True
                            spcFlg  = False
                            akFlg   = False
                        elif f.lower() == 's': 
                            prfFlg  = False
                            spcFlg  = True
                            akFlg   = False

                        elif f.lower() == 'k': 
                            prfFlg  = False
                            spcFlg  = False
                            akFlg   = True

                        elif f.lower() == 'b': 
                            bnrFlg   = True
            
                        else: print ('{} not an option for -f ... ignored'.format(f))

                elif opt == '-?':
                    usage()
                    sys.exit()                        

                else:
                    print ('Unhandled option: {}'.format(opt))
                    sys.exit()


        if not(wrkDir.endswith('/')): wrkDir = wrkDir + '/'


        #-----------------------------------------
        # Assume that the sfit4.ctl file is in the 
        # working directory
        #-----------------------------------------
        ctlFile = wrkDir + 'sfit4.ctl'
        
        #----------------------
        # Initialize Plot Class
        #----------------------
        if saveFlg:
            pltFile = 'pltRet.pdf'
            gas = dc.PlotData(wrkDir,ctlFile,saveFlg=saveFlg, outFname=wrkDir+pltFile)
        else:       
            gas = dc.PlotData(wrkDir,ctlFile)


        #----------------------
        # Call to plot profiles
        #----------------------
        if bnrFlg:
            try:
                gas.pltbnr()
            except: print ('\n*************ERROR IN PLOTTING BNR****************\n') 

        #--------------------------
        # Call to plot spectral fit
        #--------------------------
        if spcFlg: 
            try: gas.pltSpectra()
            except: print ('\n*************ERROR IN PLOTTING FIT****************\n') 

        #----------------------
        # Call to plot profiles
        #----------------------
        if prfFlg:
            try:
                gas.pltPrf(allGas=True,errFlg=True)
            except:
                gas.pltPrf(allGas=True)
        
        #-----------------
        # Call to plot AVK
        #-----------------
        if akFlg:
            if ('gas.profile.list' in gas.ctl) and gas.ctl['gas.profile.list']:  
                try:gas.pltAvk()   
                except: print ('\n*************ERROR IN AK****************\n')

        #-----------------------------
        # Print summary file to screen
        #-----------------------------
        try:
            with open(wrkDir+'summary','r') as fopen: info = fopen.read()
            
            print ('\n******************SUMMARY FILE*********************\n')
            print (info)
            print ('\n****************END OF SUMMARY FILE****************\n')

            fig, ax = plt.subplots(figsize=(10,8))  

            ax.text(0.0,0.05,info, ha='left', fontsize=10, color='b')
           
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
            ax.axis('off')

            
            if saveFlg: gas.pdfsav.savefig(fig,dpi=200)
            else:           plt.show(block=False) 

        except: 
            print ('\n*************ERROR IN SUMMARY****************\n')

        #-----------------------------
        # Print Error summary file to screen
        #-----------------------------
        try:
            with open(wrkDir+'Errorsummary.output','r') as fopen: info = fopen.read()
        
            print ('\n******************SUMMARY ERROR*********************\n')
            print (info)
            print ('\n****************END OF SUMMARY ERROR****************\n')

            fig, ax = plt.subplots(figsize=(10,8))    

            ax.text(0.0,0.05,info, ha='left', fontsize=10, color='b')
            
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
            ax.axis('off')

            if saveFlg: gas.pdfsav.savefig(fig,dpi=200)
            else:           plt.show(block=False) 

        except:
            print ('\n*************ERROR IS NOT CALCULATED****************\n')


        #--------------------------------
        # Pause so user can look at plots
        #--------------------------------
        if saveFlg: 
            gas.closeFig()
            print ('\n****************PDF FILE SAVED****************\n')
            print (wrkDir+pltFile)
            print ('\n*********************END**********************\n')
            
        else:
            try:user_input = raw_input('Press any key to exit >>> ')
            except: 
                user_input = input('Press any key to exit >>> ')
            sys.exit() 


if __name__ == "__main__":
        main(sys.argv[1:])
