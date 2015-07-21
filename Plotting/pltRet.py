#! /usr/local/python-2.7/bin/python
##! /usr/local/bin/python2.7
# Change the above line to point to the location of your python executable
#----------------------------------------------------------------------------------------
# Name:
#        pltRet.py
#
# Purpose:
#
#
#----------------------------------------------------------------------------------------


#---------------
# Import modules
#---------------
import sys
sys.path.append('/data/sfit-processing-environment/ModLib/')
import os
import getopt
import dataOutClass as dc

#------------------------
# Define helper functions
#------------------------
def usage(binDirVer):
        print 'pltRet.py [-i <str> ] \n'
        print '-i <dir>     Data directory. Optional: default is current working directory'    
        sys.exit()


def main(argv):

        #----------------
        # Initializations
        #----------------
        #------------
        # Directories
        #------------
        wrkDir    = os.getcwd()                              # Set current directory as the data directory

        #--------------------------------
        # Retrieve command line arguments
        #--------------------------------
        try:
                opts, args = getopt.getopt(sys.argv[1:], 'i:?')

        except getopt.GetoptError as err:
                print str(err)
                usage(binDirVer)
                sys.exit()

        #-----------------------------
        # Parse command line arguments
        #-----------------------------
        for opt, arg in opts:
                # Data directory
                if opt == '-i':
                        wrkDir = arg
                        dc.ckDir(wrkDir,exitFlg=True)

                elif opt == '-?':
                        usage(binDirVer)
                        sys.exit()                        

                else:
                        print 'Unhandled option: {}'.format(opt)
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
        gas = dc.PlotData(wrkDir,ctlFile)
        
        #--------------------------
        # Call to plot spectral fit
        #--------------------------
        gas.pltSpectra()
        
        #----------------------
        # Call to plot profiles
        #----------------------
        gas.pltPrf(allGas=True)
        
        #-----------------
        # Call to plot AVK
        #-----------------
        if ('gas.profile.list' in gas.ctl) and gas.ctl['gas.profile.list']:  gas.pltAvk()        

        #-----------------------------
        # Print summary file to screen
        #-----------------------------
        with open(wrkDir+'summary','r') as fopen: info = fopen.read()
        
        print '\n****************SUMMARY FILE****************\n'
        print (info)
        print '\n****************END OF SUMMARY FILE****************\n'

        #--------------------------------
        # Pause so user can look at plots
        #--------------------------------
        user_input = raw_input('Press any key to exit >>> ')
        sys.exit()           # Exit program        


if __name__ == "__main__":
        main(sys.argv[1:])
