#! /usr/bin/python2.7
#----------------------------------------------------------------------------------------
# Name:
#         nrtHDFUpload.py
#
# Purpose:
#         Create and upload HDF files 
#
# Notes:  
#         Initially created for nrt analysis
#   
#
# Version History:
#       Created, June, 2019  Ivan Ortega (iortega@ucar.edu)

#----------------------------------------------------------------------------------------

#---------------
# Import modules
#---------------
import sys
import os
import getopt
import ftplib
import glob
from time       import sleep
from subprocess import check_output
import datetime       as     dt
import subprocess
import logging

def ckDir(dirName):
    '''Check if a directory exists'''
    if not os.path.exists( dirName ):
        print 'Directory %s does not exist' % (dirName)
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
        

def usage():
    ''' Prints to screen standard program usage'''
    print ' nrtHDFUpload.py [-s tab/mlo/fl0 -g ch4 -H -U -?]'
    print '  -s <site>                             : Flag to specify location --> tab/mlo/fl0'
    print '  -g <gas>  : Flag to specify date(s)'
    print '  -H        : Flag to create HDF'
    print '  -U        : Flag to upload'
    print '  -l        : Flag to create/append log file'
    print '  -?        : Show all flags'

def ckscreen(screenname):
    
    print '\n**********************Checking screen***************'
    var = check_output(["screen -ls; true"],shell=True)
    if "."+screenname+"\t(" in var:
        print screenname+" is running"
        return True
    else:
        print screenname+" is not running"
        return False
    print '****************************************************'


                                    #----------------------------#
                                    #                            #
                                    #        --- Main---         #
                                    #                            #
                                    #----------------------------#

def upload2FTP(ftpsite='', ftpUsr='', ftpPwd='', ftpFld='', locDir='', locFile='', logFlg = False):

    
    print '\n**************** Start upload2FTP ***********************'
    print 'Uploading HDF file to NDACC: {}'.format(locDir + locFile)

    session = ftplib.FTP(ftpsite,ftpUsr,ftpPwd)

    try:    

        file = open(locDir + locFile,'rb')                  # file to send in binary

        session.storbinary('STOR '+ ftpFld + locFile, file)     # send the file
        file.close()                                    # close file and FTP
        session.quit()

        print 'File succesfully uploaded'
        if logFlg: logFlg.info( 'File succesfully uploaded at FTP %s' % ftpFld) 

    except ftplib.all_errors as e:
        print('FTP error:', e) 
        if logFlg: logFlg.error('FTP error: %s' % e)




def main(argv):

    hdfFlg  = False
    uplFlg  = False
    goFlg   = True
    logFile = False

    #--------------------------------
    # Retrieve command line arguments
    #--------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:g:d:HUl?')

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

            gas = arg.lower()

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

            dates = str(iyear)+str(imnth)+str(iday)+'_'+str(fyear)+str(fmnth)+str(fday) 

        elif opt == '-H':

            hdfFlg  = True

        elif opt == '-U':

            uplFlg  = True

        elif opt == '-l':
            logFile = True

        elif opt == '-?':
            usage()
            sys.exit()

        else:
            print 'Unhandled option: ' + opt
            sys.exit()

    #-----------------------------
    # HARD CODED INPUTS
    #-----------------------------

    ftpUsr     = 'anonymous'
    ftpPwd     = 'iortega@ucar.edu'
    ftpFld     = '/pub/incoming/ndacc/'
    ftpsite    = 'ftp.hq.ncep.noaa.gov'

    pathGas    = '/data1/ebaumer/'+loc+'/'+gas+'/'
    inputHDF   = '/data1/ebaumer/'+loc+'/'+gas+'/input_HDFCreate.py'

    if logFile:

        cmd = ['which', 'nrtLayer1.py']
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        o, e = proc.communicate()

        log_fpath = o.decode('ascii')
        log_fpath = os.path.dirname(log_fpath)


    
    if not hdfFlg and not uplFlg:
        usage()
        exit()

    while True:

        if (ckscreen('nrt'+gas.upper()+loc.upper()) ) or (ckscreen('nrt'+gas.upper()+loc.lower()) ): 
            print '\nWaiting for nrt'+gas.upper()+loc.upper() +' to Finish at {}'.format(dt.datetime.utcnow())
            goFlg = False
            sleep(10)
        
        else:

            if goFlg:

                if logFile:
                
                    # check if '/' is included at end of path
                    if not( log_fpath.endswith('/') ):
                        log_fpath = log_fpath + '/'

                    # check if path is valide
                    ckDir(log_fpath)   

                    if ckFile(log_fpath + loc.upper()+'_'+gas.lower() + '.log'): mode = 'a+'
                    else: mode = 'w'


                    logFile = logging.getLogger('1')
                    logFile.setLevel(logging.INFO)
                    hdlr1   = logging.FileHandler(log_fpath + loc.upper()+'_'+gas.lower() + '.log',mode=mode)
                    fmt1    = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s','%a, %d %b %Y %H:%M:%S')
                    hdlr1.setFormatter(fmt1)
                    logFile.addHandler(hdlr1)  
                    logFile.info('**************** Starting Logging ***********************')
                    logFile.info('Log file path:          ' + log_fpath     )
                    logFile.info('Station location:       ' + loc.upper())
                    logFile.info('Gas Name:               ' + gas.upper())
                    logFile.info('Dates:                  ' + dates)
                    logFile.info('Create HDF:             ' + str(hdfFlg))
                    logFile.info('Upload HDF:             ' + str(uplFlg))

            
                #-----------------------------
                # CREATE HDF FILE
                #-----------------------------
                if hdfFlg:

                    try: 
                         
                        os.system('HDFCreate.py -i '+inputHDF + ' -d '+ dates)
                        if logFile: logFile.info('HDFCreate.py -i '+inputHDF + ' -d '+ dates)
                        
                    except OSError as errmsg:
                        print errmsg
                        if logFile: logFile.error(errmsg)
                        sys.exit()

                    sleep(2)


                #-----------------------------
                # UPLOAD FILES TO ARCHIVE: Path of HDF must initiate with HDF and End with RD
                #-----------------------------
                if uplFlg:

                    listDir = os.listdir(pathGas)

                    for i in listDir:
                        if os.path.isdir(pathGas+i):
                            if i[0:3] == 'HDF':
                                if i[-2:] == 'RD':
                                    ver = i
                    
                    #-----------------------------
                    #
                    #-----------------------------
                    
                    pathHDF = pathGas + ver + '/'

                    if logFile: logFile.info('Version: ' + pathHDF)

                    if not ckDir(pathHDF): exit()

                    listHDF =  glob.glob(pathHDF + '*.hdf')

                    HDFfiles = os.listdir(pathHDF)

                    HDF2upload = []

                    for h in HDFfiles:

                        striyear = h[-41:-10][0:4]
                        strimont = h[-41:-10][4:6]
                        striday  = h[-41:-10][6:8]

                        strfyear = h[-41:-10][17:21]
                        strfmont = h[-41:-10][21:23]
                        strfday  = h[-41:-10][23:25]
                        
                        idateFile = dt.date(int(striyear), int(strimont), int(striday))
                        fdateFile = dt.date(int(strfyear), int(strfmont), int(strfday))


                        if (idateFile >= dt.date(int(iyear), int(imnth), int(iday)) ) & (fdateFile <= dt.date(int(fyear), int(fmnth), int(fday)) ):
                        
                            HDF2upload.append(h)

                    
                    if len(HDF2upload) == 0:
                        print 'No HDFs in date range'
                        if logFile: logFile.error('No HDFs in date range')
                        exit()
                    elif len(HDF2upload) >1:
                        print 'More than one HDFs in date range'
                        if logFile: logFile.error('More than one HDFs in date range')
                        exit()

                    else: 

                        HDF2upload = HDF2upload[0]

                        if logFile: logFile.info('HDF file to upload:      ' + HDF2upload)

                        if not( pathHDF.endswith('/') ):
                                pathHDF = pathHDF + '/'

                        if not( ftpFld.endswith('/') ):
                                ftpFld = ftpFld + '/'

    
                  
                        upload2FTP(ftpsite=ftpsite, ftpUsr=ftpUsr, ftpPwd=ftpPwd, ftpFld=ftpFld, locDir=pathHDF, locFile=HDF2upload, logFlg=logFile)
                    

                exit()
            
            goFlg = True      

if __name__ == "__main__":
    main(sys.argv[1:])