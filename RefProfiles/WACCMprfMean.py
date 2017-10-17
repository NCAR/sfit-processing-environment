#! /usr/bin/python2.7
#----------------------------------------------------------------------------------------
# Name:
#        WACCMprfMean.py
#
# Purpose:
#       Create Mean profile based in climatology provided from WACCM
#
# Usage:
# 		WACCMprfMean.py
#
# Version History:
#       Created, July, 2011  Ivan Ortega (iortega@ucar.edu)
#----------------------------------------------------------------------------------------

#---------------
# Import modules
#---------------
import datetime as dt
import numpy as np
import sys
import os

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
    station    = 'Boulder'
    inputDir   = '/data/Campaign/FL0/waccm/Boulder.V6/'
    outputFile = '/data/Campaign/FL0/waccm/WACCMref_V6-Test.FL0'
    
    gases=['H2O','CO2','O3','N2O','CO','CH4','O2','NO','SO2','NO2',
        'NH3','HNO3','OH','HF','HCL','HBR','HI','CLO','OCS','H2CO',
        'HOCL','HO2','H2O2','HONO','HO2NO2','N2O5','CLONO2','HCN','CH3F','CH3CL',
        'CF4','CFC12','CFC11','CH3CCL3','CCL4','COF2','COCLF','C2H6','C2H4','C2H2',
        'N2','HCFC22','COCL2','CH3BR','CH3I','HCOOH','H2S','CHCL2F','O2','SF6',
        'NF3']

    if not( inputDir.endswith('/') ):
        inputDir = inputDir + '/'

    #-----------------
    # Comment for all species 
    #----------------- 
    ctitle=' WACCM-V4 CESM REFC1.3 1980-2020 CCMVal/CCMI, 2012' 

    #-----------------
    # Open output file 
    #-----------------
    with open(outputFile,'w+') as fout:

	    for indF,gas in enumerate(gases):

	    	#-------------------------------------------
	        # Open and read Temperature File (T.refprfs)
	        #-------------------------------------------
	        ifile=inputDir+gas+'.refprfs'
	        
	        
	        if ckFile(ifile, exit=False):
	        
		        with open(ifile,'r') as fopen:
		            lines = fopen.readlines()
		            
		        line1='    '+str(indF+1)+'     '+gas+ctitle+'\n'
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
	        

if __name__ == "__main__":
    main()