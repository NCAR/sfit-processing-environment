#! /usr/bin/python2.7

#----------------------------------------------------------------------------------------
# Name:
#        sfit4Layer0.py
#
# Purpose:
#       This file is the zeroth order running of sfit4. It accomplishes the following:
#			1) Calls pspec to convert binary spectra file (bnr) to ascii (t15asc)
#			2) Calls hbin to gather line parameters from hitran
#			3) Calls sfit4
#			4) Clean outputs from sfit4 call
#			5) Creates a log file
#
#
# External Subprocess Calls:
#			1) pspec executable file from pspec.f90
#			2) hbin  executable file from hbin.f90
#			3) sfit4 executable file from sfit4.f90
#
#
#
# Notes:
#       1) Initializations (i.e. setting paths, log files, programs to execute) can 
#          either be done in the command line or in file
#	2) Options include:
#			 -i	<path>	 : Path to input data files
#			 -e     <path>	 : Path to sfit4 executable files
#			 -l	<path>	 : Path to log file 
#			 -c	<path>	 : Clean outputs from sfit4 run
#                        -h              : Displays usage (How to use script)
#			 --log_off	 : Flag to turn loggin off (default is on)
#			 --hbin_off	 : Flag to not run hbin (default is to run)
#			 --pspec_off : Flag to not run pspec (default is to run)
#			 --sfit4_off : Flag to not run sfit4 (default is to run)
#			
#
# Usage:
# 		./sfit4Layer0.py [options]
#
#
# Examples:
#       1) This example runs hbin, pspec, and sfit4 and creates a log file
#           ./sfit4Layer0.py -i /User/home/datafiles/ -e /User/bin/ -l /User/logs/
#
#       2) This example just runs sfit4
#           ./sfit4Layer0.py -i /User/home/datafiles/ -e /User/bin/ --log_off --hbin_off --pspec_off
#
#       3) This example cleans the output file created by sfit4 in directory (/User/home/datafiles/)
#          ./sfit4Layer0.py -c /User/home/datafiles/
#
# Version History:
#       Created, May, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
#
#
# References:
#
#----------------------------------------------------------------------------------------


#---------------
# Import modules
#---------------
import logging
import sys
import os
import getopt
import datetime
import subprocess


#------------------------
# Define helper functions
#------------------------
def usage():
        print 'sfit4Layer0.py -i <path> -e <path> -l <path> ' + \
              '-c <path> --log_off --hbin_off --pspec_off --sfit4_off'
        sys.exit()

def subProcRun( fname ):
        rtn = subprocess.Popen( fname, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        outstr = ''
        while True:
                out = rtn.stdout.read(1)
                if ( out == '' and rtn.poll() != None ):
                        break
                if out != '':
                        outstr += out
                        sys.stdout.write(out)
                        sys.stdout.flush()
        stdout, stderr = rtn.communicate()
        return (outstr,stderr)

def main(argv):				

        #--------------------------------
        # Retrieve command line arguments
        #--------------------------------
        try:
                opts, args = getopt.getopt(sys.argv[1:], 'i:e:l:c:h', 
                                           ['log_off', 'hbin_off', 'pspec_off', 'sfit4_off'])

        except getopt.GetoptError as err:
                print str(err)
                usage()
                sys.exit()

        #---------------------------------------#
        # Set defaults for command line options #
        #---------------------------------------#
        #-------#
        # Paths #
        #-------#
        # Get current working directory
        cwdPath = os.getcwd()
        
        # Set path to sfit4 executable files
        exe_fpath = cwdPath

        # Set path to sfit4 data files
        data_fpath = cwdPath

        # Set Path for log file
        log_fpath = cwdPath

        #-------#
        # Flags #
        #-------#
        log_flg   = False		# Flag for log file
        hbin_flg  = True		# Flag for hbin run
        pspec_flg = True		# Flag for pspec run
        sfit4_flg = True		# Flag for sfit4 run
        cln_flg   = False		# Flag for cleaning sfit4 output

        #-----------------------------
        # Parse command line arguments
        #-----------------------------
        for opt, arg in opts:
                if opt == '-i':
                        data_fpath = arg

                        # check if '/' is included at end of path
                        if not( data_fpath.endswith('/') ):
                                data_fpath = data_fpath + '/'

                        # check if path is valide
                        if not( os.path.isdir(data_fpath) ):
                                print 'Unable to find ' + data_fpath
                                sys.exit()

                        # Set path for log file		
                        log_fpath = data_fpath

                elif opt == '-e':
                        exe_fpath = arg

                        # check if '/' is included at end of path
                        if not( exe_fpath.endswith('/') ):
                                exe_fpath = exe_fpath + '/'			

                        # check if path is valide
                        if not( os.path.isdir(exe_fpath) ):
                                print 'Unable to find ' + exe_fpath
                                sys.exit()

                elif opt == '-l':
                        log_fpath = arg
                        log_flg   = True
                        # check if '/' is included at end of path
                        if not( log_fpath.endswith('/') ):
                                log_fpath = log_fpath + '/'	

                        # check if path is valide				
                        if not( os.path.isdir(log_fpath) ):
                                print 'Unable to find ' + log_fpath
                                sys.exit()	
                elif opt == '-h':
                        usage()
                        sys.exit()

                # Set logical flags		
                elif opt == '--log_off':
                        log_flg = False

                elif opt == '--hbin_off':
                        hbin_flg = False

                elif opt == '--pspec_off':
                        pspec_flg = False

                elif opt == '--sfit4_off':
                        sfit4_flg = False

                elif opt == '-c':
                        cln_flg = True
                        cln_fpath = arg
                        
                        # check if '/' is included at end of path
                        if not( cln_fpath.endswith('/') ):
                                cln_fpath = cln_fpath + '/'			

                        # check if path is valide
                        if not( os.path.isdir(cln_fpath) ):
                                print 'Unable to find ' + cln_fpath
                                sys.exit()                        

                else:
                        print 'Unhandled option: ' + opt
                        sys.exit()	

        #--------------------
        # Initialize log file
        #--------------------
        if log_flg:		
                logging.basicConfig(level    = logging.INFO,
                                    format   = '%(asctime)s %(levelname)-8s %(message)s',
                                    datefmt  = '%a, %d %b %Y %H:%M:%S',
                                    filename = log_fpath + 'sfit4_logfile_' + 
                                    datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.log',
                                    filemode = 'w' )

        # Write initial log data             		
                logging.info('Input data path ' + data_fpath     )
                logging.info('Executable path ' + exe_fpath      )
                logging.info('hbin flag = '     + str(hbin_flg)  )
                logging.info('pspec flag = '    + str(pspec_flg) )
                logging.info('sfit4 flag = '    + str(sfit4_flg) )

        #-------------------------------------------
        # Change working directory to directory with
        # input data. Necessary for running sfit4
        #-------------------------------------------
        os.chdir(data_fpath)


        #---------------------------
        # Clean up output from sfit4
        #---------------------------
        if cln_flg:
                # Create possible list of sfit4 output files to clean
                clnFiles = [ 'pbpfile', 'statevec', 'k.output', 'kb.output','sa.complete',
                             'rprfs.table','aprfs.table','ab.output', 'summary', 'parm.output',
                             'seinv.output', 'sainv.complete', 'smeas.target', 'shat.complete',
                             'ssmooth.target', 'ak.target', 'solar.output' ]

                # Remove applicable files
                for clnFile in clnFiles:
                        try:
                                os.remove(cln_fpath + clnFile)
                        except OSError:
                                pass

        #----------
        # Run pspec
        #----------	
        if pspec_flg:
                print 'Running pspec.....'
                stdout,stderr = subProcRun( [exe_fpath + 'pspec'] )
                                        
                if log_flg:
                        logging.info( '\n' + stdout + stderr )

                #if ( stderr is None or not stderr ):
                        #if log_flg:
                                #logging.info( stdout )
                                #logging.info('Finished running pspec\n' + stdout)
                #else:
                        #print 'Error running pspec!!!'
                        #if log_flg:
                                #logging.error('Error running pspec \n' + stdout)
                        #sys.exit()                        

                        

        #----------
        # Run hbin
        #----------		
        if hbin_flg:
                print 'Running hbin.....'
                stdout,stderr = subProcRun( [exe_fpath + 'hbin'] )

                if log_flg:
                        logging.info( '\n' + stdout + stderr )

                #if ( stderr is None or not stderr ):
                        #if log_flg:
                                #logging.info( stdout )
                                #logging.info('Finished running hbin\n' + stdout)
                #else:
                        #print 'Error running hbin!!!'
                        #if log_flg:
                                #logging.error('Error running hbin \n' + stdout)
                        #sys.exit()       
                        

        #----------
        # Run sfit4
        #----------		
        if sfit4_flg:
                print 'Running sfit4.....'
                stdout,stderr = subProcRun( [exe_fpath + 'sfit4'] )
                                                                
                if log_flg:
                        logging.info( '\n' + stdout + stderr )
                
                #if ( stderr is None or not stderr):
                        #if log_flg:
                                #logging.info('Finished running sfit4\n' + stdout)
                #else:
                        #print 'Error running sfit4!!!'
                        #if log_flg:
                                #logging.error('Error running sfit4 \n' + stdout)
                        #sys.exit()   
                        


if __name__ == "__main__":
        main(sys.argv[1:])
