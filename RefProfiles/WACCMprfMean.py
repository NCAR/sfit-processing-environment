#! /usr/bin/python3
#----------------------------------------------------------------------------------------
# Name:
#        WACCMprfMean.py
#
# Purpose:
#       Create Mean profile based in climatology provided from WACCM
#
# Usage:
#       WACCMprfMean.py
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
    #                                      HARD CODED INPUTS
    #
    #---------------------------------------------------------------------------------------------

    #------------------------
    # WACCM files
    #------------------------
    inputDir   = '/data/Campaign/TAB/waccm/Thule.V6/'

    #------------------------
    # In case a gas is not in WACCM use this reference file (example can be provided)
    #------------------------
    reffile    = '/data/Campaign/TAB/waccm/reference.prf.REFC1.3_v2'   

    #------------------------
    # Single Output file
    #------------------------
    outputFile = '/data/Campaign/TAB/waccm/WACCMref_V6.TAB_v1p0'

    #------------------------
    # Header for WACCM (Comment for all WACCM species)
    #------------------------
    ctitle     = ' WACCM-V4 CESM REFC1.3 1980-2020 CCMVal/CCMI, 2012' 
    
    #------------------------
    # Order of Gases: FOR SFIT4 V1.0x
    #------------------------
    gases =      ['H2O',     'CO2',     'O3',     'N2O',     'CO',      #1-5
                  'CH4',     'O2',      'NO',     'SO2',     'NO2',     #6-10 
                  'NH3',     'HNO3',    'OH',     'HF',      'HCL',     #11-15
                  'HBR',     'HI',      'CLO',    'OCS',     'CH2O',    #16-20 
                  'HOCL',    'HO2',     'H2O2',   'HONO',    'HO2NO2',  #21-25
                  'N2O5',    'CLONO2',  'HCN',    'CH3F',    'CH3CL',   #26-30
                  'CF4',     'CCL2F2',  'CCL3F',  'CH3CCL3', 'CCL4',    #31-35
                  'COF2',    'COCLF',   'C2H6',   'C2H4',    'C2H2',    #36-40 
                  'N2',      'CHF2CL',  'COCL2',  'CH3BR',   'CH3I',    #41-45
                  'HCOOH',   'H2S',     'CHCL2F', 'O2CIA',   'SF6',     #46-50
                  'NF3',     'N2CIA',   'OTHER',  'OTHER',   'PH3',     #51-55
                  'OTHER',   'OTHER',   'OCLO',   'F134A',   'C3H8',    #56-60
                  'F142B',   'CFC113',  'F141B',  'CH3OH',   'OTHER',   #61-65
                  'OTHER',   'PAN',     'CH3CHO' ,'CH3CN',   'CHF3',    #66-70
                  'CH3COOH', 'C5H8',    'MVK',    'MACR',    'C3H6',    #71-75
                  'C4H8',    'OTHER',   'OTHER',  'OTHER',   'OTHER',   #76-80
                  'OTHER',   'OTHER',   'OTHER',  'OTHER',   'OTHER',   #81-85
                  'OTHER',   'OTHER',   'OTHER',  'OTHER',   'OTHER',   #86-90
                  'OTHER',   'OTHER',   'OTHER',  'OTHER',   'OTHER',   #91-95
                  'OTHER',   'OTHER',   'OTHER',  'OTHER']              #96-99


    #------------------------
    # OLD
    #------------------------
    #gases=['H2O','CO2','O3','N2O','CO','CH4','O2','NO','SO2','NO2',
    #    'NH3','HNO3','OH','HF','HCL','HBR','HI','CLO','OCS','H2CO',
    #    'HOCL','HO2','H2O2','HONO','HO2NO2','N2O5','CLONO2','HCN','CH3F','CH3CL',
    #    'CF4','CFC12','CFC11','CH3CCL3','CCL4','COF2','COCLF','C2H6','C2H4','C2H2',
    #    'N2','HCFC22','COCL2','CH3BR','CH3I','HCOOH','H2S','CHCL2F','O2','SF6',
    #    'NF3']

    #---------------------------------------------------------------------------------------------
    #
    #                                      START
    #
    #---------------------------------------------------------------------------------------------

    if not( inputDir.endswith('/') ):
        inputDir = inputDir + '/'

    #-----------------
    # Open output file 
    #-----------------
    with open(outputFile,'w+') as fout:

        for indF,gas in enumerate(gases):

            print('\n{}: {}'.format(indF+1, gas))

            #-------------------------------------------
            # Open and read  .refprfs
            #-------------------------------------------
            ifile=inputDir+gas+'.refprfs'

            if gas == 'CH2O': gas = 'H2CO'
            
            
            if ckFile(ifile, exit=False):

                print('Using: {}'.format(ifile))
            
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

                data_mean = np.mean(data, axis=0)

                for row in segmnt(data_mean, 5):
                    strformat = ','.join('{:>12.3E}' for i in row) + ', \n'
                    fout.write(strformat.format(*row))

            else:

                print('Using: {}'.format(reffile))
                
                #-------------------------------------------
                #if gas is not in waccm folder use reference profile
                #-------------------------------------------
                if indF+1 < 10:
                    line1='    '+str(indF+1)+'     '+gas+' '+reffile+'\n'

                else:
                    line1='   '+str(indF+1)+'     '+gas+' '+reffile+'\n'

                fout.write(line1)
            
                ckFile(reffile,exit=True)
                refprf = readRefPrf(fname=reffile, parms = [gas.upper()])
                refprf =  np.asarray(refprf[gas.upper()][0]) 
                

                for row in segmnt(refprf, 5):
                    strformat = ','.join('{:>12.3E}' for i in row) + ', \n'
                    fout.write(strformat.format(*row))

            
if __name__ == "__main__":
    main()