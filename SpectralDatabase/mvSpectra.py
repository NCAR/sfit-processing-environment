#! /usr/bin/python2.7
##! /usr/local/python-2.7/bin/python
# Change the above line to point to the location of your python executable
#----------------------------------------------------------------------------------------
# Name:
#        mvSpectra.py
#
# Purpose:
#       This program moves spectra from input directory to working directory.
#
# Usage:
#       Copy files from /ya4/id/mlo(tab,fl0) to /data1/mlo(tab, fl0)
#
#----------------------------------------------------------------------------------------


                        #-------------------------#
                        # Import Standard modules #
                        #-------------------------#
import sys
import os
from os import walk
from os import listdir
from os.path import isfile, join, isdir
import shutil
import datetime as dt
import DateRange as dr

                        #-------------------------------------#
                        # Define helper functions and classes #
                        #-------------------------------------#


def ckDir(dirName,logFlg=False,exit=False):
    ''' '''
    if not os.path.exists( dirName ):
        #print 'Input Directory %s does not exist' % (dirName)
        if logFlg: logFlg.error('Directory %s does not exist' % dirName)
        if exit: sys.exit()
        return False
    else:
        return True

def ckDirMk(dirName,logFlg=False):
    ''' '''
    if not ( os.path.exists(dirName) ):
        os.makedirs( dirName)
        os.chmod(dirName, 0o777)
        if logFlg: logFlg.info( 'Created folder %s' % dirName)
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

def findFiles(Path):
    ''' Find just files in directory. Does not find files in subdirectories '''
    fnames = []
    for (dirpath, dirnames, filenames) in walk(Path):
        fnames.extend(filenames)
        break
    if dirpath.endswith('/'):
        fnames = [(dirpath + name) for name in filenames]
    else:
        fnames = ['/'.join([dirpath,name]) for name in filenames]
    return fnames

                            #----------------------------#
                            #                            #
                            #        --- Main---         #
                            #                            #
                            #----------------------------#

def main():

    #-------
    # Inputs
    #-------
    loc     = 'mlo'
    inPath  = '/ya4/id/' + loc.lower() + '/'     # Input directory
    outPath = '/data1/' + loc.lower() + '/'       # Working directory

    iyear   = 2018 
    imonth  = 5
    iday    = 29

    fyear   = 2018
    fmonth  = 5
    fday    = 31

    #-------------------
    # Call to date class
    #-------------------
    DOI      = dr.DateRange(iyear, imonth, iday, fyear, fmonth, fday)
    daysList = DOI.dateList

    #----------------------
    # Loop through day list
    #----------------------
    for i,snglDay in enumerate(daysList):

        print snglDay

        #---------------------------------
        # Determine input/output directory
        #---------------------------------
        mnthstr = "{0:02d}".format(snglDay.month)
        yearstr = "{0:02d}".format(snglDay.year)
        daystr  = "{0:02d}".format(snglDay.day)
        yyyymmddstr = yearstr + mnthstr + daystr
        inDir       = inPath + yyyymmddstr + '/'
        outDir      = outPath + yyyymmddstr + '/'

        #------------------------------
        # If input directory is missing
        # skip to next day
        #------------------------------
        if not ckDir(inDir, exit=False): continue

        #---------------------------------
        # Check if output directory exists
        #---------------------------------
        ckDirMk(outDir)

        #-----------------------------------------
        # Get a list of files from input directory
        #-----------------------------------------
        #fnames = [ f for f in listdir(inDir) if ( isfile(join(inDir,f)) and not f.startswith('.') ) ]
        fnames = [ f for f in listdir(inDir) if (join(inDir,f) and not f.startswith('.') ) ]
        
        #----------------------------------------------------
        # Copy files from input directory to output directory
        #----------------------------------------------------
        for f in fnames:

            #----------------------------------------------------
            #Copy Folders, i.e. deleted folder
            #----------------------------------------------------
            
            if isdir(join(inDir,f)):
                ckDirMk(join(outDir,f))

                fnamesDel = [ k for k in listdir(join(inDir,f)) if (join(join(inDir,k),k) and not k.startswith('.') ) ]

                for k in fnamesDel:
                    shutil.copy(join(join(inDir,f),k),join(join(outDir,f),k))
                    os.chmod(join(join(outDir,f),k), 0o766)

            #----------------------------------------------------
            #Copy files
            #----------------------------------------------------

            else:  
 
                try: shutil.copy(join(inDir,f),join(outDir,f))
                except IOError: print 'Unable to move file: {} to {}'.format(join(inDir,f),join(outDir,f))
                os.chmod(join(outDir,f), 0o766)

if __name__ == "__main__":
    main()





