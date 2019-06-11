#!/usr/bin/python
#----------------------------------------------------------------------------------------
# Name:
#        nrtPreProc.py
#
# Purpose:
#        - near-real-time Retrieval Pre-Processing
#            * Consecutive Pre-processing: 
#            * Copy spectra from ya4 to data1, make sure deleted files are in fact deleted
#            * create spectradatabase
#            * create House Log files
#            * Append house log files to new database
#            # ZPT and NCEP water profiles
# Notes:
#        Make Sure the following steps are followed prior to run:
#        1) ckopus has been performed 
#    
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
    print ' nrtsfit4Layer1.py [-s tab/mlo/fl0 -d 20180515 -?]'
    print ' Retrieval Pre-Processing:' 
    print '     - Copy spectra from ya4 to data1, make sure deleted files are in fact deleted'
    print '     - create spectradatabase'
    print '     - create House Log files'
    print '     - append house log files to new database'           
    print '     - ZPT and NCEP water profiles'
    print ' Arguments:'
    print '  -s <site>                             : Flag to specify location --> tab/mlo/fl0'
    print '  -d <20180515> or <20180515_20180530>  : Flag to specify date(s)'
    print '  -?                                    : Show all flags'
                            
def main(argv):    

    #--------------------------------
    # Retrieve command line arguments
    #--------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:d:?:')

    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit()

    #-----------------------------
    # Parse command line arguments
    #-----------------------------
    for opt, arg in opts:

        if opt == '-s':

            loc = arg.lower()

        elif opt == '-d':

            print arg

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

    print '\n\n'
    print '*************************************************'
    print '*************Begin Pre Processing*****************'
    print '*************************************************'   

    dates = str(iyear)+str(imnth)+str(iday)+'_'+str(fyear)+str(fmnth)+str(fday)

    #doneFile ='/data/pbin/Dev_Ivan/nrtAnalysis/_procdone'+loc

    #if ckFile(doneFile):
    #    os.remove(doneFile)
    
    #----------------
    # Starting mvSpectra.py
    #----------------
    print '\nStarting mvSpectra.py: copying files from ya/id/'+loc+' to /data1/'+loc
    try: 
        os.system('mvSpectra.py -s'+str(loc)+ ' -d '+ dates)
    except OSError as errmsg:
        print errmsg
        sys.exit()

    #----------------
    # Starting delSpcdel.py
    #----------------
    print '\nStarting delSpcdel.py: deleting Files if found in deleted folder'
    try:
        os.system('delSpcdel.py -s'+str(loc)+ ' -d '+ dates)
    except OSError as errmsg:
        print errmsg
        sys.exit()

    #----------------
    # Starting mkSpecDB.py
    #----------------
    spDB     = '/data/Campaign/'+loc.upper()+'/Spectral_DB/spDB_'+loc.lower()+'_RD.dat'
    
    if ckFile(spDB):
        print 'Deleting: '+ spDB
        os.remove(spDB)
    
    print '\nStarting mkSpecDB.py: Initial Spectral Database'
    try: 
        os.system('mkSpecDB.py -s'+str(loc)+ ' -d '+ dates)
    except OSError as errmsg:
        print errmsg
        sys.exit()
    
    #----------------
    # Starting station_house_reader.py
    #----------------
    if loc.lower() != 'fl0':
        House     = '/data/Campaign/'+loc.upper()+'/House_Log_Files/'+loc.upper()+'_HouseData_'+str(iyear)+'.dat'

        if ckFile(House):
            print 'Deleting: '+ House
            os.remove(House)

        print '\nStarting station_house_reader.py: read House Data'
        try:
            os.system('station_house_reader.py -s'+str(loc)+ ' -d '+ dates)
        except OSError as errmsg:
            print errmsg
            sys.exit()

    #----------------
    # Starting read_FL0_EOL_data.py
    #----------------
    if loc.lower() == 'fl0':
        print '\nStarting read_FL0_EOL_data.py: read EOL data'
        os.system('read_FL0_EOL_data.py -y'+str(iyear))

    #----------------
    # Starting mkSpecDB.py
    #----------------
    HRspDB   = '/data/Campaign/'+loc.upper()+'/Spectral_DB/HRspDB_'+loc.lower()+'_RD.dat'
    
    if ckFile(HRspDB):
        print 'Deleting: '+ HRspDB
        os.remove(HRspDB)
    
    print '\nStarting appendSpecDB.py.py: Append Spectral Database File'
    try:
        os.system('appendSpecDB.py -s'+str(loc)+ ' -y '+ str(iyear))
    except OSError as errmsg:
        print errmsg
        sys.exit()

    #----------------
    # Starting read_FL0_EOL_data.py
    #----------------
    if (loc.lower() == 'fl0') & (int(iyear) < 2018):
        print '\nStarting mkCoadSpecDB.py: Coadd Spectral Database Fil'
        os.system('mkCoadSpecDB.py -i CoadSpecDBInputFile.py')

    #----------------
    # Starting NCEPnmcFormat.py 
    #----------------
    print '\nStarting NCEPnmcFormat.py: format the NCEP nmc data'
    try:
        os.system('NCEPnmcFormat.py -s'+str(loc)+ ' -y '+ str(iyear))
    except OSError as errmsg:
        print errmsg
        sys.exit()

    #----------------
    # Starting MergPrf.py
    #----------------
    print '\nStarting MergPrf.py: ZPT and water files from WACCM data'
    try:
        #os.system('MergPrf.py -i /data/pbin/Dev_Ivan/RefProfiles/mergprfInput.py')
        os.system('MergPrf.py -s'+str(loc)+ ' -d '+ str(dates))
    except OSError as errmsg:
        print errmsg
        sys.exit()

    #----------------
    # Starting NCEPwaterPrf.py
    #----------------
    print '\nStarting NCEPwaterPrf.py: daily water profiles from NCEP'
    try:
        os.system('NCEPwaterPrf.py -s'+str(loc)+ ' -d '+ str(dates))
    except OSError as errmsg:
        print errmsg
        sys.exit()

    #----------------
    # Starting ERAwaterPrf.py: IMPORTANT --> Edit Input file Accordingly
    #----------------
    #print '\nStarting ERAwaterPrf.py: daily water profiles from ERA'
    #try:
    #    os.system('ERAwaterPrf.py -s'+str(loc)+ ' -d '+ str(dates))
    #except OSError as errmsg:
    #    print errmsg
    #    sys.exit()

    #f=open(doneFile, 'w')
    #f.close

if __name__ == "__main__":
    main(sys.argv[1:])