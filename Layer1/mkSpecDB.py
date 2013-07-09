#! /usr/bin/python2.7

#----------------------------------------------------------------------------------------
# Name:
#        mkSpecDB.py
#
# Purpose:
#       This program is a wrapper for ckopus. It runs ckopus on multiple spectral observations
#       to create a database file. It will search through directories from a given base directory
#       for file names matching a given tag. If a datafile is found the program will execute ckopus.c 
#       and write out the one line DB string to an output file. Given the output spectral DB this
#       program will determine if that file previously exists. If it does it will append the DB
#       file. If not it will create a new DB file.
#           
#
#
# Input files:
#       1) ckopus executable file
#       2) Spectral Database file (Optional)
#
# Output files:
#       1) Spectral database file <name designated on command line>
#
# Called Functions:
#       1) No external called functions (other than system functions)
#
#
# Notes:
#       1) This program assumes that there is a common string subset to the name of the 
#          raw OPUS files!!!!!!!! This is set in variable <dataFileTag>. Change if necessary!!!
#
#
# Usage:
#     mkSpecDB.py -s <station tag> -b <file> -d <path> -o <file> --bnr_off
#              -s           Three letter station tag (i.e. mlo,fl0,etc. Needed by ckopus)
#              -b           ckopus executable
#              -d           Base directory for data
#              -o           Output spectral DB file
#              -l           Directory for logfile
#              --bnr_off    Flag to not create bnr files (only creates database file)
#
# Examples:
#    ./mkSpecDB.py -s mlo -b /Home/Code/ckopus -d /Home/Data/mlo/ -o /Home/Data/mlo/SpectralDBfile.txt
#
# Version History:
#  1.0     Created, July, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
#
#
# References:
#
#----------------------------------------------------------------------------------------


                        #-------------------------#
                        # Import Standard modules #
                        #-------------------------#
import sys
import os
import getopt
import subprocess
import shutil
import logging
import datetime as dt
                        #-------------------------#
                        # Define helper functions #
                        #-------------------------#
def usage():
    ''' Prints to screen standard program usage'''
    print 'mkSpecDB.py -s <station tag> -b <file> -d <path> -o <file> -l <path> --bnr_off'

        
def ckDir(dirName):
    '''Check if a directory exists'''
    if not os.path.exists( dirName ):
        print 'Input Directory %s does not exist' % (dirName)
        sys.exit()   
        
def ckFile(fName):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print 'File %s does not exist' % (fName)
        sys.exit()
        
                            #----------------------------#
                            #                            #
                            #        --- Main---         #
                            #                            #
                            #----------------------------#

def main(argv):
    #-------------
    # Set defaults
    #-------------
    dataFileTag = 'fml00'
    bnrWriteFlg = True
    bnrType     = 'F'
    logFile     = False
    
    #--------------------------------
    # Retrieve command line arguments
    #--------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:b:d:o:l:', 'bnr_off')

    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit()
        
    #-----------------------------
    # Parse command line arguments
    #-----------------------------
    for opt, arg in opts:
        
        if opt == '-s':           
            stationTag = arg
            
        # Check path to ckopus executable
        elif opt == '-b':
            # Input file instance
            Fckopus = arg
                                  
            # check if ckopus executable file exists
            ckFile(Fckopus)            
            
        # Check base path to OPUS data
        elif opt == '-d':           
            # OPUS base directory
            dataBaseDir = arg

            # check if '/' is included at end of path
            if not( dataBaseDir.endswith('/') ):
                dataBaseDir = dataBaseDir + '/'
                
            # check if path is valide
            ckDir(dataBaseDir)
                
        # Output Spectral DB file
        elif opt == '-o':        
            # OPUS base directory
            outputDBfile = arg    
        
            # Check if directory exists
            Fpath,Fname = os.path.split(outputDBfile)
            ckDir(Fpath)
            
            # Check if a filename is given in command line for DB
            if not Fname:
                print 'Must give a filename for Output Spectral DB'
                sys.exit()
            
        # Check log file flag and path
        elif opt == '-l':
            log_fpath = arg

            # check if '/' is included at end of path
            if not( log_fpath.endswith('/') ):
                log_fpath = log_fpath + '/'

            # check if path is valide
            ckDir(log_fpath)
                
            logging.basicConfig(level    = logging.INFO,
                                format   = '%(asctime)s %(levelname)-8s %(message)s',
                                datefmt  = '%a, %d %b %Y %H:%M:%S',
                                filename = log_fpath + 'mkDpecDB_logfile_' + 
                                dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.log',
                                filemode = 'w' )          
            logFile = logging.getLogger(__name__)            
              
        elif opt == '--bnr_off':           
            bnrWriteFlg = False
       
        else:
            print 'Unhandled option: ' + opt
            sys.exit()

    
    # Determine if spectral DB file already exists
    if os.path.isfile(outputDBfile):
        wmode = 'a'
        if logFile: logging.info('Appending log file %s' % outputDBfile)
    else:
        wmode = 'w'
        if logFile: logging.info('Create new log file %s' % outputDBfile)
    
    #--------------------------------
    # Open Spectral DB file for write
    #--------------------------------   
    with open(outputDBfile,wmode) as fopen:        
        #-------------------------------------------
        # If spectral DB does not exist write header
        #-------------------------------------------  
        rtn = subprocess.Popen( [Fckopus,'-H'], stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        stdoutHeader, stderr = rtn.communicate()        

        if (wmode == 'w'):                       
            fopen.write(stdoutHeader)
            if logFile: logging.info('Writing header to spectral DB file')
            
        #------------------------------------
        # Find indicies for SBlock and TStamp
        #------------------------------------    
        # Search through data base directory 
        #-----------------------------------        
        for root,dirs,files in os.walk(dataBaseDir):
            
            for indvfile in files:
                
                if dataFileTag in indvfile:             
                    #-------------------------------------------
                    # For found spectral data files run 
                    # ckopus and write to spectral database file
                    #-------------------------------------------
                    paramList = [Fckopus,'-S'+stationTag,'-D','/'.join([root,indvfile])]
                    rtn       = subprocess.Popen( paramList, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
                    stdoutParam, stderr = rtn.communicate()
                    fopen.write( stdoutParam.split('\n')[2]+'\n' )
                    if logFile: logging.info('Writing DB line for file %s' %('/'.join([root,indvfile])))
                    
                    #-----------------------------------
                    # Run ckopus to create bnr file type
                    # Grab SBlock and TStamp to convert 
                    # to bnr type
                    #-----------------------------------
                    if bnrWriteFlg:
                        # Get SBlock and TStamp from ckopus -D <file>
                        stdoutHeader = stdoutHeader.strip().split()
                        indSBlock    = stdoutHeader.index('SBlock')
                        indTStamp    = stdoutHeader.index('TStamp')
                        singleDBline = stdoutParam.split('\n')[2].split()
                        SBlock       = singleDBline[indSBlock]
                        TStamp       = singleDBline[indTStamp]
                        
                        #----------------------------------
                        # Run ckopus to convert to bnr type
                        #----------------------------------
                        paramList    = [Fckopus,'-S'+stationTag,'-'+bnrType+SBlock,'/'.join([root,indvfile])]
                        rtn          = subprocess.Popen( paramList, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
                        stdoutParam, stderr = rtn.communicate()       
                        if logFile: logging.info('Creating bnr file from %s' %('/'.join([root,indvfile]) ) )
                        
                        #------------------------------------------------
                        # Change name of file to correspond to time stamp
                        #------------------------------------------------
                        if os.path.isfile('/'.join([root,SBlock+'.bnr'])):
                            shutil.move(root+'/'+SBlock+'.bnr', root+'/'+TStamp+'.bnr')
                            if logFile: logging.info('Moving file %s to timestamp denoted name %s' %(indvfile,TStamp+'.bnr'))
                        else:
                            print 'Unable to move file: %s to %s' %(indvfile,TStamp+'.bnr')
                            if logFile: logging.error( 'Unable to move file: %s to %s' %(indvfile,TStamp+'.bnr') )
                            
                                          
if __name__ == "__main__":
    main(sys.argv[1:])