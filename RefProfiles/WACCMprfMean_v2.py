#! /usr/bin/python3
#----------------------------------------------------------------------------------------
# Name:
#        WACCMprfMean_v2.py
#
# Purpose:
#       Create Mean profile based in climatology provided from WACCM (pre-made reference profile used in Layer1)
#       For Non-WACCM gases an additional file with profiles is used (site specific)     
#
# Usage:
#       WACCMprfMean_v2.py
#       See Inputs below
#
# Version History:
#
#       Edited, Sep 23, 2020  Ivan Ortega (iortega@ucar.edu) - Update order of gases for sfit4 v1.0x
#----------------------------------------------------------------------------------------

#---------------
# Import modules
#---------------
import datetime as dt
import numpy as np
import sys
import os

#---------------
# Functions
#---------------
def ckFile(fName,logFlg=False,exit=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print ('File %s does not exist' % (fName))
        if logFlg: logFlg.error('Unable to find file: %s' % fName)
        if exit: sys.exit()
        return False
    else: return True

def segmnt(seq,n):
    '''Yeilds successive n-sized segments from seq'''
    try:
        xrange
    except NameError:
        xrange = range
        
    for i in xrange(0,len(seq),n):
        yield seq[i:i+n]  

def readRefPrf(fname='', parms=''):

        ''' Reads in reference profile, an input file for sfit4 (raytrace) '''
        refPrf = {}
        
        try:
            with open(fname,'r') as fopen: lines = fopen.readlines()
                            
            #----------------------------------------
            # Get Altitude, Pressure, and Temperature
            # from reference.prf file
            #----------------------------------------
            nlyrs  = int(lines[0].strip().split()[1])
            nlines = int(np.ceil(nlyrs/5.0))
            
            for ind,line in enumerate(lines):
                if any(p in line for p in parms):

                    val = [x for x in parms if x in line][0]
                   
                    refPrf.setdefault(val,[]).append([float(x[:-1]) for row in lines[ind+1:ind+nlines+1] for x in row.strip().split()])

        except Exception as errmsg:
            print (errmsg)
        
        #------------------------
        # Convert to numpy arrays
        # and sort based on date
        #------------------------
        for k in refPrf:
            refPrf[k] = np.asarray(refPrf[k])

        return refPrf 

#---------------
# Main()
#---------------
def main():
    
    #---------------------------------------------------------------------------------------------
    #
    #                                      INPUTS
    #
    #---------------------------------------------------------------------------------------------

    #------------------------
    # WACCM files
    #------------------------
    #inputDir   = '/data/Campaign/FL0/waccm/Boulder.V6/'
    inputDir   = '/net/nitrogen/ftp/user/jamesw/IRWG/2021/WACCM.v7/Boulder.V7'

    #------------------------
    # In case a gas is not in WACCM use this reference file (example provided but each site is different)
    #------------------------
    reffile    = '/data/Campaign/FL0/waccm/reference.prf.REFC1.3_v2'   

    #------------------------
    # mol_ID file (Order of Gases: FOR SFIT4 V1.0x)
    #------------------------
    gasidFile  = '/data/pbin/Dev_Ivan/RefProfiles/Mol_ID.txt'

    #------------------------
    # Header for WACCM (Comment for all WACCM species)
    #------------------------
    #ctitle     = 'WACCM-V4 CESM REFC1.3 1980-2020 CCMVal/CCMI, 2012' 
    ctitle     ='CMIP6-historical-WACCM + CMIP6-SSP5-8.5-WACCM (1980-2040), 2021'

    #------------------------
    # Single Output file
    #------------------------
    #outputFile = '/data/Campaign/FL0/waccm/WACCMref_V6.FL0_v1p0'
    outputFile = '/data/Campaign/FL0/waccm/WACCMref_V7.FL0'

    #---------------------------------------------------------------------------------------------
    #
    #                                      START
    #
    #---------------------------------------------------------------------------------------------
    
    #------------------------
    # Get ID Gas
    #------------------------
    if ckFile(gasidFile, exit=False):

        with open(gasidFile,'r') as fopen: lines = fopen.readlines()

        gases = []

        for ind,line in enumerate(lines[1:]): gases.append(line.strip().split()[1])

    #------------------------
    if not( inputDir.endswith('/') ):
        inputDir = inputDir + '/'

    #-----------------
    # Open output file 
    #-----------------
    with open(outputFile,'w+') as fout:

        for indF,gas in enumerate(gases):

            if indF >= 1:

                print('\n{}: {}'.format(indF+1, gas))

                #-------------------------------------------
                # Open and read  .refprfs
                #-------------------------------------------

                if gas.upper() == 'H2CO': gasFile = 'CH2O'
                else:                     gasFile = gas


                ifile=inputDir+gasFile+'.txt'
                
                
                if ckFile(ifile, exit=False):

                    print('Using: {}'.format(ifile))

                    refPrf = {}
                
                    with open(ifile,'r') as fopen: lines = fopen.readlines()

                    line2txt = '{:>5}{:>8}{:}{:}\n'.format(indF+1,gas,' ',ctitle)
                        
                    fout.write(line2txt)


                    for ind,line in enumerate(lines):

                        if 'Altitud' in line:
                            nlyrs = int(lines[ind-1].strip().split()[0])
                            nlines = int(np.ceil(nlyrs/5.0))

                        if gasFile in line:

                            refPrf = np.array( [float(x[:-1]) for row in lines[ind+1:ind+nlines+1] for x in row.strip().split()] )

                    for row in segmnt(refPrf, 5):
                        strformat = ','.join('{:>12.3e}' for i in row) + ', \n'
                        fout.write(strformat.format(*row))

                else:

                    print('Using: {}'.format(reffile))
                    
                    #-------------------------------------------
                    #if gas is not in waccm folder use reference profile
                    #-------------------------------------------

                    line2txt = '{:>5}{:>8}{:}{:}\n'.format(indF+1,gas,' ',reffile)

                    fout.write(line2txt)
                
                    ckFile(reffile,exit=True)
                    refprf = readRefPrf(fname=reffile, parms = [gas.upper()])
                    refprf =  np.asarray(refprf[gas.upper()][0]) 
                    

                    for row in segmnt(refprf, 5):
                        strformat = ','.join('{:>12.3e}' for i in row) + ', \n'
                        fout.write(strformat.format(*row))

            
if __name__ == "__main__":
    main()