#!/usr/bin/python
#----------------------------------------------------------------------------------------
# Name:
#        nrtsfit4Layer1.py
#
# Purpose:
#        - near-real-time sfit4Layer1
#            * Analysis of target gas
# Notes:
#        
#       * If target gas is water vapor it will create *v.99 and *.v5 in the daily data directory using the retrievals from NCEP apriori profiles profiles 
#       * For other gases it will identify if water vapor is done before attempting to run analysis
#       * For details see the "Optical Techniques FTS Profile Retrieval Strategy" document
#
#
# Version History:
#       Created, June, 2019  Ivan Ortega (iortega@ucar.edu)
#
#----------------------------------------------------------------------------------------

#---------------
# Import modules
#---------------
import sys
import os
import getopt
import datetime       as     dt
from time       import sleep
from subprocess import check_output

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

def usage():
    ''' Prints to screen standard program usage'''
    print ' nrtsfit4Layer1.py [-s tab/mlo/fl0 -g gas -d 20180515 -?]'
    print ' near-real-time sfit4Layer1' 
    print ' Analysis of target gas'
    print ' Arguments:'
    print ' -s <site>                              : Flag to specify location --> tab/mlo/fl0'
    print ' -g <gas>                               : Flag to specify gas'
    print ' -d <20180515> or <20180515_20180530>  : Flag to specify year'
    print ' -?                                    : Show all flags'

def ckscreen(screenname):
    var = check_output(["screen -ls; true"],shell=True)
    if "."+screenname+"\t(" in var:
        print screenname+" is running"
        return True
    else:
        print screenname+" is not running"
        return False
                            
def main(argv):  
    
    goFlg = True
    #--------------------------------
    # Retrieve command line arguments
    #--------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:d:g:?:')

    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit()


    #-----------------------------
    # Parse command line arguments
    #-----------------------------
    for opt, arg in opts:
        # Check input file flag and path
        if opt == '-s':

            loc = arg.lower()

        elif opt == '-g':

            gas    = arg
            gasFlg = True

        elif opt == '-d':

            if len(arg) == 8:

                dates   = arg.strip().split()

                iyear   = str(dates[0][0:4])
                imnth   = str(dates[0][4:6])
                iday    = str(dates[0][6:8])

                fyear   = str(dates[0][0:4])
                fmnth   = str(dates[0][4:6])
                fday    = str(dates[0][6:8])


            elif len(arg) == 17:

                dates   = arg.strip().split()

                iyear   = str(dates[0][0:4])
                imnth   = str(dates[0][4:6])
                iday    = str(dates[0][6:8])

                fyear   = str(dates[0][9:13])
                fmnth   = str(dates[0][13:15])
                fday    = str(dates[0][15:17])


            else:
                print 'Error in input date'
                usage()
                sys.exit()

        elif opt == '-?':
            usage()
            sys.exit()

        else:
            print 'Unhandled option: ' + opt
            sys.exit()

    dates = str(iyear)+str(imnth)+str(iday)+'_'+str(fyear)+str(fmnth)+str(fday)   

    #doneFilePr  = '/data/pbin/Dev_Ivan/nrtAnalysis/_procdone'+loc
    #doneFileWV  = '/data/pbin/Dev_Ivan/nrtAnalysis/_procdoneWV'+loc

    while True:

        ##if ckFile(doneFilePr):
        if (ckscreen('nrtPre'+loc.lower())) or (ckscreen('nrtPre'+loc.upper())) :

            print '\nWaiting for nrtPre '+loc.upper() +' to Finish at {}'.format(dt.datetime.utcnow())
            goFlg = False
            sleep(10)

        else:

            if goFlg:
         
                print '***********************************************************************'
                print '************* Begin sfit4Layer1 Analysis ******************************'
                print '***********************************************************************' 

                # if gas.lower() == 'h2o':
                #     if ckFile(doneFileWV):
                #         os.remove(doneFileWV) 

                # else: 
                #     if not ckFile(doneFileWV):
                #         print '\nWaiting for Water Vapor to Finish at {}'.format(dt.datetime.utcnow())
                #         sleep(10)
                #         continue

                #--------------------------------
                # The following check whether the analysis is ran through the nrt.sh --> check for screens
                #--------------------------------

                if (ckscreen('nrt'+gas.upper()+loc.upper()) ) or (ckscreen('nrt'+gas.lower()+loc.lower()) ): 

                    if gas.lower() != 'h2o':
                        if (ckscreen('nrtH2O'+loc.lower()) ) or (ckscreen('nrtH2O'+loc.upper())):
                            print '\nWaiting for Water Vapor to Finish at {}'.format(dt.datetime.utcnow())
                            sleep(10)
                            continue
                        
                #----------------
                # Starting sfit4Layer1.py
                #----------------
                print '\nStarting sfit4Layer1.py: {} analysis'.format(gas)
                
                try:
                    os.system('sfit4Layer1.py -i /data1/ebaumer/'+loc.lower()+'/'+gas.lower()+'/'+loc.upper()+'_'+gas.lower()+'_Input_RD.py' + ' -d '+ dates)
                except OSError as errmsg:
                    print errmsg
                    sys.exit()

                if gas.lower() == 'h2o':
          
                    #----------------
                    # Starting retWaterPrf.py
                    #----------------
                    print '\nStarting retWaterPrf.py: Create Water Profiles in data directory'
                    try:
                        os.system('retWaterPrf.py -s'+str(loc)+ ' -d '+ str(dates) + ' -v Current_NCEP')
                    except OSError as errmsg:
                        print errmsg
                        sys.exit()

                    #----------------
                    # Starting retWaterPrfDaily.py
                    #----------------
                    print '\nStarting retWaterPrfDaily.py: Create Water Profiles in data directory'
                    try:
                        os.system('retWaterPrfDaily.py -s'+str(loc)+ ' -d '+ dates)
                    except OSError as errmsg:
                        print errmsg
                        sys.exit()

                    #f=open(doneFileWV, 'w')
                    #f.close

                    print '\nWater Vapor completed'

                exit()

            goFlg = True
                




if __name__ == "__main__":
    main(sys.argv[1:])