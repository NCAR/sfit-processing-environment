#! /usr/bin/python2.7
#----------------------------------------------------------------------------------------
# Name:
#        WACCMprfMonthlyMean.py
#
# Purpose:
#       Create Monthly Mean profiles of a gas of interest based in climatology provided from WACCM
#
# Note:
#       The monthly mean profile is only generated for the gas of interest.
#       All other gases are global mean       
#
# Usage:
#       WACCMprfMonthlyMean.py
#
# Version History:
#       Created, Sep, 2017  Ivan Ortega (iortega@ucar.edu)
#----------------------------------------------------------------------------------------

#---------------
# Import modules
#---------------
import datetime as dt
import numpy as np
import sys
import os
import myfunctions as mf

def ckFile(fName,logFlg=False,exit=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print 'File %s does not exist' % (fName)
        if logFlg: logFlg.error('Unable to find file: %s' % fName)
        if exit: sys.exit()
        return False
    else: return True

def segmnt(seq,n):
    '''Yeilds successive n-sized segments from seq'''
    for i in xrange(0,len(seq),n):
        yield seq[i:i+n]  


def main():
    #-----------------
    #Inputs
    #-----------------
    station    = 'Thule'                                          
    
    inputDir   = '/data/Campaign/TAB/waccm/Thule.V6/'
    
    gasOI      = 'co'  
    
    outputFld  = '/data/Campaign/TAB/waccm/'+ gasOI.lower() + '/'

    reffile    = '/data/Campaign/TAB/waccm/reference.prf.REFC1.3'   #In case a gas is not in WACCM use this reference file
    
    #The order of the following 99 gases is important (see reference.prf.REFC1.3 file)
    gases      = ['H2O','CO2','O3','N2O','CO','CH4','O2','NO','SO2','NO2',
                  'NH3','HNO3','OH','HF','HCL','HBR','HI','CLO','OCS','H2CO',
                  'HOCL','HO2','H2O2','HONO','HO2NO2','N2O5','CLONO2','HCN','CH3F','CH3CL',
                  'CF4','CFC12','CFC11','CH3CCL3','CCL4','COF2','COCLF','C2H6','C2H4','C2H2',
                  'N2','HCFC22','COCL2','CH3BR','CH3I','HCOOH','H2S','CHCL2F','O2','SF6',
                  'NF3', 'OTHER', 'OTHER', 'OTHER', 'OTHER', 'OTHER', 'OTHER','OCLO', 'F134A', 'C3H8', 
                  'F142B', 'CFC113', 'F141B', 'CH3OH', 'OTHER', 'OTHER','PAN', 'CH3CHO', 'CH3CN', 'OTHER', 
                  'CH3COOH', 'C5H8', 'MVK', 'MACR', 'C3H6', 'C4H8','OTHER', 'OTHER', 'OTHER', 'OTHER', 
                  'OTHER', 'OTHER', 'OTHER', 'OTHER', 'OTHER', 'OTHER', 'OTHER','OTHER','OTHER','OTHER',
                  'OTHER','OTHER','OTHER','OTHER','OTHER','OTHER','OTHER','OTHER','OTHER']
    
    #-----------------
    #
    #-----------------
    if not( inputDir.endswith('/') ):
        inputDir = inputDir + '/'

    if not( outputFld.endswith('/') ):
        outputFld = outputFld + '/'

    if not ( os.path.exists(outputFld) ):
        os.makedirs( outputFld )

    #-----------------
    # Comment for WACCM species 
    #----------------- 
    ctitle = ' WACCM-V4 CESM REFC1.3 1980-2020 CCMVal/CCMI, 2012' 

    #-----------------
    # Open output file 
    #-----------------

    for mnth in range(1, 13):

        outputFile = outputFld + 'WACCMref_V6-'+"{0:02d}".format(mnth)+'.dat'

        with open(outputFile,'w+') as fout:

            for indF,gas in enumerate(gases):

                #-------------------------------------------
                #skip water profile
                #-------------------------------------------
                if indF >= 1: 

                    #-------------------------------------------
                    # Open and read Temperature File (T.refprfs)
                    #-------------------------------------------
                    ifile=inputDir+gas+'.refprfs'
                    
                    #-------------------------------------------
                    #if gas is in waccm folder
                    #-------------------------------------------
                    if ckFile(ifile, exit=False):
                    
                        with open(ifile,'r') as fopen:
                            lines = fopen.readlines()
                            
                        if indF+1 < 10:
                            line1='    '+str(indF+1)+'     '+gas+ctitle+'\n'   #The spaces in the output is important

                        else:
                            line1='   '+str(indF+1)+'     '+gas+ctitle+'\n'

                        fout.write(line1)

                        #-------------------------------------------
                        # Get altitudes. These are reversed compared
                        # to output so we must flip
                        #-------------------------------------------
                        alt    = np.array([float(x) for x in lines[1].strip().split()])
                        
                        #-------------------
                        # Get list of months
                        #-------------------
                        months = np.array([int(line.strip().split()[0].split('/')[1]) for line in lines[2:]] )
                        
                        #-------------
                        # Read in data
                        #-------------
                        data    = np.array( [ [ float(x) for x in row.strip().split()[1:]] for row in lines[2:]] )

                        #-------------------------------------------
                        #if gas is not gas of interest calculate global mean
                        #-------------------------------------------
                        if gas.lower() != gasOI.lower():

                            data_mean = np.mean(data, axis=0)
                            for row in segmnt(data_mean, 5):
                                strformat = ','.join('{:>12.3E}' for i in row) + ', \n'
                                fout.write(strformat.format(*row))
                        else:
                            #----------------------
                            # Find monthly averages
                            #----------------------
                            inds      = np.where(months == mnth)[0]
                            data_mean = np.mean(data[inds,:], axis=0)  # [month, altitude]

                            for row in segmnt(data_mean, 5):
                                strformat = ','.join('{:>12.3E}' for i in row) + ', \n'
                                fout.write(strformat.format(*row))
                    else:
                        #-------------------------------------------
                        #if gas is not in waccm folder use reference profile
                        #-------------------------------------------
                        if indF+1 < 10:
                            line1='    '+str(indF+1)+'     '+gas+ reffile+'\n'

                        else:
                            line1='   '+str(indF+1)+'     '+gas+ reffile+'\n'

                        fout.write(line1)
                    
                        ckFile(reffile,exit=True)
                        refprf = mf.readRefPrf(fname=reffile, parms = [gas.upper()])
                        refprf =  np.asarray(refprf[gas.upper()][0]) 

                        for row in segmnt(refprf, 5):
                            strformat = ','.join('{:>12.3E}' for i in row) + ', \n'
                            fout.write(strformat.format(*row))

            
if __name__ == "__main__":
    main()