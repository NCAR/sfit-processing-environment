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


def main(argv):

        #----------------
        # Initializations
        #----------------
        loc        = 'tab'
        gasName    = 'hf'
        ver        = 'Current'
        ctlFile    = '/Volumes/data1/ebaumer/'+loc.lower()+'/'+gasName.lower()+'/'+'x.'+gasName.lower()+'/sfit4.ctl'
        #outdir     = '/Volumes/data1/ebaumer/'+loc.lower()+'/'+gasName.lower()+'/Plots/'
        outdir     = '/Users/ebaumer/Data/'
        maxrms     = 0.60
        sclfct     = 1.0E9  
        sclfctName = 'ppbv'
        saveFlg    = True
        errorFlg   = True
        fltrFlg    = True
        byYrFlg    = False
        
        iyear      = 2012
        imnth      = 1
        iday       = 1
        fyear      = 2013
        fmnth      = 12
        fday       = 31

        fnamePart  = loc + '_' + gasName + '_' + ver + '.pdf'
        
        #---------------
        # Data directory
        #---------------
        RtrvdDir = '/Volumes/data1/ebaumer/'+loc.lower()+'/'+gasName.lower()+'/'+ver+'/'         
        
        #----------------------
        # File to save plots to
        #----------------------
        if saveFlg: fname = outdir + fnamePart
        else:       fname = ''
            
        #-------------------------
        # Create Instance of Class
        #-------------------------
        gas = dc.PlotData(RtrvdDir,ctlFile,iyear=iyear,imnth=imnth,iday=iday,fyear=fyear,fmnth=fmnth,fday=fday,outFname=fname)
        
        #----------------------
        # Call to plot profiles
        #----------------------
        gas.pltPrf(fltr=fltrFlg,maxRMS=maxrms,allGas=False,sclfct=sclfct,sclname=sclfctName,errFlg=errorFlg)
        
        #-------------------
        # Plot total columns
        #-------------------
        gas.pltTotClmn(fltr=fltrFlg,maxRMS=maxrms,errFlg=errorFlg)
        
        #------------------
        # Plot Spectral fit
        #------------------
        gas.pltSpectra(fltr=fltrFlg,maxRMS=maxrms)
        
        if saveFlg: gas.closeFig()
        
        #--------------------
        # Create yearly plots
        #--------------------
        if byYrFlg:
                for year in gas.yearList():
                        if saveFlg: fname = outdir + loc + '_' + gasName + '_' + str(year) + '_' + ver + '.pdf'
                        gasYr = dc.PlotData(RtrvdDir,ctlFile,iyear=year,imnth=1,iday=1,fyear=year,fmnth=12,fday=31,outFname=fname)
                        #gasYr.pltPrf(fltr=fltrFlg,maxRMS=maxrms,allGas=False,sclfct=sclfct,sclname=sclfctName)
                        gasYr.pltTotClmn(fltr=fltrFlg,maxRMS=maxrms,errFlg=False)
                        if errorFlg: gasYr.pltTotClmn(fltr=fltrFlg,maxRMS=maxrms,errFlg=True)
                        if saveFlg: gasYr.closeFig()
        
        print('******************')

        #--------------------------------
        # Pause so user can look at plots
        #--------------------------------
        if not saveFlg:
                user_input = raw_input('Press any key to exit >>> ')
                sys.exit()           # Exit program        


if __name__ == "__main__":
        main(sys.argv[1:])
