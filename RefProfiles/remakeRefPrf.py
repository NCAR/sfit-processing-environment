#! /usr/bin/python3
#----------------------------------------------------------------------------------------
# Name:
#        remakeRefPrf.py
#
# Purpose:
#       Re-arrange a reference.prf using the latest mol_ID.txt
#
# Usage:
#       remakeRefPrf.py
#       See Inputs below
#
# Version History:
#
#       Created, Sep 24, 2020  Ivan Ortega (iortega@ucar.edu)
#----------------------------------------------------------------------------------------

#---------------
# Import modules
#---------------
import datetime as dt
import numpy as np
import sys
import os
import getopt
import shutil

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

        findFlg = False
        
        try:
            with open(fname,'r') as fopen: lines = fopen.readlines()
                            
            #----------------------------------------
            # Get Altitude, Pressure, and Temperature
            # from reference.prf file
            #----------------------------------------
            nlyrs  = int(lines[0].strip().split()[1])
            nlines = int(np.ceil(nlyrs/5.0))
            
            for ind,line in enumerate(lines):

                lineWords = line.strip().split()

                if parms in lineWords:

                    lineStr = line

                    refPrf = lines[ind+1:ind+nlines+1]

                    findFlg = True                    

        except Exception as errmsg:
            print (errmsg)
                
        #------------------------
        # Convert to numpy arrays
        # and sort based on date
        #------------------------
        if findFlg:
            return lineStr, refPrf
        
        else:

            refPrftemp  = np.zeros((nlyrs))
            refPrf      = []

            for row in segmnt(refPrftemp, 5):
                strformat = ','.join('{:>12.4e}' for i in row) + ', \n'
                refPrf.append(strformat.format(*row))

            lineStr       = '     Created for sfit4 - remakeRefPrf.py\n'

            return lineStr, refPrf

#---------------
# Main()
#---------------
def main(argv):
    
    #---------------------------------------------------------------------------------------------
    #
    #                                      INPUTS
    #
    #---------------------------------------------------------------------------------------------

    #------------------------
    # mol_ID file (Order of Gases: FOR SFIT4 V1.0x)
    #------------------------
    gasidFile  = '/data/pbin/Dev_Ivan/RefProfiles/Mol_ID.txt'
    refprfFile = 'reference.prf'                  

    #---------------------------------
    # Retrieve command line arguments 
    #---------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'r:i:c?:')

    except getopt.GetoptError as err:
        print (str(err))
        usage()
        sys.exit()
        
    #-----------------------------
    # Parse command line arguments
    #-----------------------------
    for opt, arg in opts:
        
        #-----------
        # Input file
        #-----------
        if opt == '-i':           
            gasidFile = arg
            inpFlg  = True

        elif opt == '-r':
            refprfFile = arg

        elif opt == '-c':
            makecpFlg = True
            

    ckFile(gasidFile,exit=True)
    ckFile(refprfFile,exit=True)


    #---------------------------------------------------------------------------------------------
    #
    #                                      START
    #
    #---------------------------------------------------------------------------------------------
    
    #------------------------
    # Get ID Gas
    #------------------------
    with open(gasidFile,'r') as fopen: lines = fopen.readlines()

    gases = []

    for ind,line in enumerate(lines[1:]): gases.append(line.strip().split()[1])

    #------------------------
    #
    #------------------------
    with open(refprfFile,'r') as fopen: lines = fopen.readlines()

    #-----------------
    # Open output file 
    #-----------------
    with open('reference_v1x.prf','w+') as fout:

        fout.write(lines[0])
        nlayers = int(lines[0].strip().split()[1])


        #for apt in ['ALTITUDE', 'PRESSURE', 'TEMPERATURE']:
        for apt in ['altitudes', 'pressure', 'temperature']:
        #for apt in ['Z(km)', 'P(mb)', 'T(K)']:

            lineStr,  refprf = readRefPrf(fname=refprfFile, parms = apt)

            if apt == 'TEMPERATURE': line2txt = '{:>16}{:}{:}\n'.format(apt,' ',lineStr)
            else:                    line2txt = '{:>13}{:}{:}\n'.format(apt,' ',lineStr)

            fout.write(lineStr)

            for i in range(int(nlayers/5)+1):
                fout.write(refprf[i])

        for indF,gas in enumerate(gases):

            lineStr, refprf = readRefPrf(fname=refprfFile, parms = gas)

            lineStr = lineStr[14:]
            lineStr = lineStr.strip()

            line2txt = '{:>5}{:>8}{:}{:}\n'.format(indF+1,gas,' ',lineStr)
            fout.write(line2txt)


            for i in range(int(nlayers/5)+1):
                fout.write(refprf[i])


    #os.remove("reference.prf")
    
    #try:
    #    shutil.copy('reference_tmp.prf', 'reference.prf')
    #except IOError as e:
    #    print("Unable to copy file. %s" % e)

    #os.remove("reference_tmp.prf")

            
if __name__ == "__main__":
    main(sys.argv[1:])