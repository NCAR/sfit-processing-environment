#! /usr/bin/python3
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
# Notes:
#       1) Command line arguments
#            -d <20180515> or <20180515_20180530>  : Flag to specify input Dates. If not Date is specified current date is used.
#            -s             : Flag Must include location: mlo/tab/fl0 (only for otserver)
#            -?             : Show all flags'
#      2)  Compatible with python 2.7 or later
#
#----------------------------------------------------------------------------------------


                        #-------------------------#
                        # Import Standard modules #
                        #-------------------------#
import os, sys
sys.path.append((os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "ModLib")))
from os import walk
from os import listdir
from os.path import isfile, join, isdir
import shutil
import datetime as dt
import DateRange as dr
import getopt

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
        print ('File %s does not exist' % (fName))
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

def usage():
    ''' Prints to screen standard program usage'''
    print ('mvSpectra.py [-s tab/mlo/fl0 -d 20180515 -?]')
    print ('  -s             : Flag Must include location: mlo/tab/fl0 (only for otserver)')
    print ('  -d <20180515> or <20180515_20180530>  : Flag to specify input Dates. If not Date is specified current date is used.')
    print ('  -?             : Show all flags')
    print ('Note: Input and Output paths are hardcoded in mvSpectra.py')


def main(argv):

    #--------------------------------
    # Retrieve command line arguments
    #--------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:d:?:')

    except getopt.GetoptError as err:
        print (str(err))
        usage()
        sys.exit()

    #-----------------------------
    # Parse command line arguments
    #-----------------------------
    for opt, arg in opts:
        # Check input file flag and path
        if opt == '-s':

            loc = arg.lower()

        elif opt == '-d':

            if len(arg) == 8:

                dates   = arg.strip().split()

                iyear   = int(dates[0][0:4])
                imnth   = int(dates[0][4:6])
                iday    = int(dates[0][6:8])

                fyear   = int(dates[0][0:4])
                fmnth   = int(dates[0][4:6])
                fday    = int(dates[0][6:8])


            elif len(arg) == 17:

                dates   = arg.strip().split()

                iyear   = int(dates[0][0:4])
                imnth   = int(dates[0][4:6])
                iday    = int(dates[0][6:8])

                fyear   = int(dates[0][9:13])
                fmnth   = int(dates[0][13:15])
                fday    = int(dates[0][15:17])


            else:
                print ('Error in input date')
                usage()
                sys.exit()

        elif opt == '-?':
            usage()
            sys.exit()

        else:
            print ('Unhandled option: ' + opt)
            sys.exit()


    #-------
    # Inputs
    #-------
    inPath  = '/ya4/id/' + loc.lower() + '/'     # Input directory
    outPath = '/data1/'  + loc.lower() + '/'       # Working directory

    #-------------------
    # Call to date class
    #-------------------

    DOI      = dr.DateRange(iyear, imnth, iday, fyear, fmnth, fday)
    daysList = DOI.dateList

    #----------------------
    # Loop through day list
    #----------------------
    for i,snglDay in enumerate(daysList):

        #---------------------------------
        # Determine input/output directory
        #---------------------------------
        mnthstr = "{0:02d}".format(snglDay.month)
        yearstr = "{0:02d}".format(snglDay.year)
        daystr  = "{0:02d}".format(snglDay.day)
        yyyymmddstr = yearstr + mnthstr + daystr
        inDir       = inPath + yyyymmddstr + '/'
        outDir      = outPath + yyyymmddstr + '/'

        print ('Copying folder: {} to {}'.format(inDir,outDir))

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

                print ('Copying folder: {} to {}'.format(join(inDir,f),join(outDir,f)))

                for k in fnamesDel:
                    shutil.copy(join(join(inDir,f),k),join(join(outDir,f),k))
                    os.chmod(join(join(outDir,f),k), 0o766)

            #----------------------------------------------------
            #Copy files
            #----------------------------------------------------

            else:  
 
                try: shutil.copy(join(inDir,f),join(outDir,f))
                except IOError: print ('Unable to move file: {} to {}'.format(join(inDir,f),join(outDir,f)))
                os.chmod(join(outDir,f), 0o766)

if __name__ == "__main__":
    main(sys.argv[1:])

