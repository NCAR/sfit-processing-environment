#! /usr/local/python-2.7/bin/python
##! /usr/local/bin/python2.7
# Change the above line to point to the location of your python executable
#----------------------------------------------------------------------------------------
# Name:
#        pltSet.py
#
# Purpose:
#
#
#----------------------------------------------------------------------------------------


#---------------
# Import modules
#---------------
import sys
import os
import getopt
import dataOutClass as dc
import time


def usage():
    ''' Prints to screen standard program usage'''
    print 'pltSet.py -i <inputfile> -?'
    print '  -i <file> : Run pltSet.py with specified input file'
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
            
            pltInputs = {}
            
            ckFile(arg,exit=True)

            try:
                execfile(arg, pltInputs)
            except IOError as errmsg:
                print errmsg + ' : ' + arg
                sys.exit()
    
            if '__builtins__' in pltInputs:
                del pltInputs['__builtins__']               

                
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
    ckDir(pltInputs['retDir'], exit=True)
    ckFile(pltInputs['ctlFile'], exit=True)
    if pltInputs['saveFlg']:  ckDir(os.path.dirname(os.path.realpath(pltInputs['pltFile'])),exit=True)

    #-------------------------
    # Create Instance of Class
    #-------------------------
    gas = dc.PlotData(pltInputs['retDir'],pltInputs['ctlFile'],iyear=pltInputs['iyear'],imnth=pltInputs['imnth'],iday=pltInputs['iday'],
                      fyear=pltInputs['fyear'],fmnth=pltInputs['fmnth'],fday=pltInputs['fday'],outFname=pltInputs['pltFile'])
    
    #----------------------
    # Call to plot profiles
    #----------------------
    gas.pltPrf(fltr=pltInputs['fltrFlg'],allGas=False,sclfct=pltInputs['sclfct'],sclname=pltInputs['sclfctName'],
               errFlg=pltInputs['errorFlg'],minSZA=pltInputs['minSZA'],maxSZA=pltInputs['maxSZA'],maxRMS=pltInputs['maxRMS'],minTC=pltInputs['minTC'],maxTC=pltInputs['maxTC'],
               minDOF=pltInputs['minDOF'],maxCHI=pltInputs['maxCHI'],dofFlg=pltInputs['dofFlg'],rmsFlg=pltInputs['rmsFlg'],tcFlg=pltInputs['tcNegFlg'],
               pcFlg=pltInputs['pcNegFlg'],szaFlg=pltInputs['szaFlg'],cnvrgFlg=pltInputs['cnvrgFlg'],chiFlg=pltInputs['chiFlg'],tcMMflg=pltInputs['tcMMFlg'])
    
    #-----------------
    # Call to plot AVK
    #-----------------
    try:
    	gas.pltAvk(fltr=pltInputs['fltrFlg'],errFlg=pltInputs['errorFlg'],partialCols=pltInputs['pCols'],
	           minSZA=pltInputs['minSZA'],maxSZA=pltInputs['maxSZA'],maxRMS=pltInputs['maxRMS'],minTC=pltInputs['minTC'],maxTC=pltInputs['maxTC'],
	           minDOF=pltInputs['minDOF'],maxCHI=pltInputs['maxCHI'],dofFlg=pltInputs['dofFlg'],rmsFlg=pltInputs['rmsFlg'],
	           tcFlg=pltInputs['tcNegFlg'],pcFlg=pltInputs['pcNegFlg'],szaFlg=pltInputs['szaFlg'],
	           chiFlg=pltInputs['chiFlg'],cnvrgFlg=pltInputs['cnvrgFlg'],tcMMflg=pltInputs['tcMMFlg'])
    except:
	print "Unable to plot AVK!!" 

    #-------------------
    # Plot total columns
    #-------------------
    gas.pltTotClmn(fltr=pltInputs['fltrFlg'],sclfct=pltInputs['sclfct'],sclname=pltInputs['sclfctName'],
                   partialCols=pltInputs['pCols'],errFlg=pltInputs['errorFlg'],minSZA=pltInputs['minSZA'],minTC=pltInputs['minTC'],maxTC=pltInputs['maxTC'],
                   maxSZA=pltInputs['maxSZA'],maxRMS=pltInputs['maxRMS'],minDOF=pltInputs['minDOF'],maxCHI=pltInputs['maxCHI'],
                   dofFlg=pltInputs['dofFlg'],rmsFlg=pltInputs['rmsFlg'],tcFlg=pltInputs['tcNegFlg'],
                   pcFlg=pltInputs['pcNegFlg'],szaFlg=pltInputs['szaFlg'],chiFlg=pltInputs['chiFlg'],cnvrgFlg=pltInputs['cnvrgFlg'],tcMMflg=pltInputs['tcMMFlg'])
    
    #------------------
    # Plot Spectral fit
    #------------------
    gas.pltSpectra(fltr=pltInputs['fltrFlg'],minSZA=pltInputs['minSZA'],maxSZA=pltInputs['maxSZA'],minTC=pltInputs['minTC'],maxTC=pltInputs['maxTC'],
                   maxRMS=pltInputs['maxRMS'],minDOF=pltInputs['minDOF'],maxCHI=pltInputs['maxCHI'],dofFlg=pltInputs['dofFlg'],
                   rmsFlg=pltInputs['rmsFlg'],tcFlg=pltInputs['tcNegFlg'],pcFlg=pltInputs['pcNegFlg'],
                   szaFlg=pltInputs['szaFlg'],chiFlg=pltInputs['chiFlg'],cnvrgFlg=pltInputs['cnvrgFlg'],tcMMflg=pltInputs['tcMMFlg'])
    
    if pltInputs['saveFlg']: gas.closeFig()
    
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
		               minDOF=pltInputs['minDOF'],maxCHI=pltInputs['maxCHI'],dofFlg=pltInputs['dofFlg'],rmsFlg=pltInputs['rmsFlg'],tcFlg=pltInputs['tcNegFlg'],
		               pcFlg=pltInputs['pcNegFlg'],szaFlg=pltInputs['szaFlg'],chiFlg=pltInputs['chiFlg'],cnvrgFlg=pltInputs['cnvrgFlg'],tcMMflg=pltInputs['tcMMFlg'])
                    gas.pltTotClmn(fltr=pltInputs['fltrFlg'],sclfct=pltInputs['sclfct'],sclname=pltInputs['sclfctName'],
		                   partialCols=pltInputs['pCols'],errFlg=pltInputs['errorFlg'],minSZA=pltInputs['minSZA'],minTC=pltInputs['minTC'],maxTC=pltInputs['maxTC'],
		                   maxSZA=pltInputs['maxSZA'],maxRMS=pltInputs['maxRMS'],minDOF=pltInputs['minDOF'],maxCHI=pltInputs['maxCHI'],
		                   dofFlg=pltInputs['dofFlg'],rmsFlg=pltInputs['rmsFlg'],tcFlg=pltInputs['tcNegFlg'],
		                   pcFlg=pltInputs['pcNegFlg'],szaFlg=pltInputs['szaFlg'],chiFlg=pltInputs['chiFlg'],cnvrgFlg=pltInputs['cnvrgFlg'],tcMMflg=pltInputs['tcMMFlg'])
                    if pltInputs['saveFlg']: gasYr.closeFig()
    
    print('\nFinished Plots.......\n')

    #--------------------------------
    # Pause so user can look at plots
    #--------------------------------
    if not pltInputs['saveFlg']:
            user_input = raw_input('Press any key to exit >>> ')
            sys.exit()           # Exit program        


if __name__ == "__main__":
        main(sys.argv[1:])
