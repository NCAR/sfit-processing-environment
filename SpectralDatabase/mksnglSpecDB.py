#!/usr/bin/python
##! /usr/local/python-2.7/bin/python

# Change the above line to point to the location of your python executable

#----------------------------------------------------------------------------------------
# Name:
#       
# Purpose:
#       Script to make a single Spectral DB using several yearly files
#
#
# Output files:
#       1) Coadded spectral database file 
#
# Called Python:
#       1) sfitClasses
#       2) DateRange
#
# Notes:
#       1) 
#
#
# Usage:
#     mkCoadSpecDb_flt.py -i <File>>
#              -i           Input file for mkCoadSpecDb_flt.py
#
#
# Version History:
#  1.0     Created, July, 2018  Ivan Ortega (iortega@ucar.edu)
#
#
#----------------------------------------------------------------------------------------


                        #-------------------------#
                        # Import Standard modules #
                        #-------------------------#
import os, sys
sys.path.append((os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "ModLib")))
import itertools
import getopt
import subprocess as sp
import shutil
import datetime as dt
import DateRange as dr
import sfitClasses as sc
import numpy as np
import glob

                        #-------------------------------------#
                        # Define helper functions and classes #
                        #-------------------------------------#
            
                                                     
def usage():
    ''' Prints to screen standard program usage'''
    print 'mksnglSpecDB.py'

        
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
        

                            #----------------------------#
                            #                            #
                            #        --- Main---         #
                            #                            #
                            #----------------------------#

def main():

    #----------------
    # Initializations
    #----------------
    loc           = 'mlo'
    dataDir       = '/data/Campaign/'+loc.upper()+'/Spectral_DB/coadd/'
    iyear         = 2002
    fyear         = 2009

    outputDBfile     = 'CoaddspDB_'+loc.lower()+'_'+str(iyear)+'_'+str(fyear)+'_flt1_1_v2.dat'
    outputDBlogfile  = 'FldrsProc_CoaddspDB_'+loc.lower()+'_'+str(iyear)+'_'+str(fyear)+'_flt1_1_v2.dat'

    
    ckDir(dataDir, exit=True)

    years      = [i +iyear  for i in range((fyear - iyear) +1)]

    i = 0

    with open(dataDir + outputDBfile,'w') as fopen: 

        for y in years:

            file = dataDir + 'CoaddspDB_'+loc.lower()+'_'+str(y)+'_flt1_1_v2.dat'

            if ckFile(file, exit = False):

                i += 1

                with open(file, 'r') as fread:
                    spcdb = fread.readlines()
                
                if i != 1: del(spcdb[0])
                
                for line in spcdb:
                    fopen.write(line)

                ###os.remove(file)

    # with open(dataDir + outputDBlogfile,'w') as fopen: 

    #     for y in years:

    #         file = dataDir + 'FldrsProc_CoaddspDB_'+loc.lower()+'_'+str(y)+'_flt1.list'

    #         if ckFile(file, exit = False):

    #             with open(file, 'r') as fread:
    #                 spcdb = fread.readlines()
                
    #             for line in spcdb:
    #                 fopen.write(line)

    #             ###os.remove(file)

                                                                             
if __name__ == "__main__":
    main()