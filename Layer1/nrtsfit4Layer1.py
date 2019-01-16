#!/usr/bin/python
#----------------------------------------------------------------------------------------
# Name:
#        nrtsfit4Layer1.py
#
# Purpose:
#        - Retrieval Processing
#            * Consecutive Pre-processing 
#            * Analysis of h2o using NCEP
#            * Creation of Water Profiles v99 
#
#Notes:
#        Make Sure the following steps are followed prior to run:
#        1) ckopus has been performed 
#        2) Edit Inputs in mvSpectra.py
#        3) Edit e.g., specDBInputFile_MLO.dat
#        4) Edit station_house_reader.py
#        5) Edit appndSpecDBInputFile
#        6) Edit NCEPinputFile.py
#        7) Edit mergprfInput.py
#        8) Edit NCEPwaterPrf.py
#        9) Edit ERAwaterPrf.py  --> If using this note that cnvrtNC.py need to be run beforehand separately.     
#        9) Edit, sfit4Layer1 input file, E.g., MLO_H2O_Input.py file
#        10) Edit retWaterPrf.py
#        11) Edit retWaterPrfDaily.py
#
#       * For details see the "Optical Techniques FTS Profile Retrieval Strategy" document
#
#
# Version History:
#       Created, April, 2018  Ivan Ortega (iortega@ucar.edu)
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
    print ' nrtsfit4Layer1.py [-s tab/mlo/fl0 -y 2018 -?]'
    print ' Retrieval Processing' 
    print ' *Consecutive Pre-processing'
    print ' *Analysis of h2o using NCEP'
    print ' *Creation of Water Profiles v99'
    print ' Arguments:'
    print '  -s <site>  : Flag to specify location --> tab/mlo/fl0'
    print '  -y <year>  : Flag to specify year'
    print '  -?         : Show all flags'
                            
def main(argv):    

    #----------------
    # Initializations
    #----------------
    #loc    = 'tab'
    #year   = 2018

    #--------------------------------
    # Retrieve command line arguments
    #--------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:y:?')

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

            loc = arg

        elif opt == '-y':

            year = int(arg)

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
    
    #----------------
    # Starting mvSpectra.py: IMPORTANT --> Modify Inputs in mvSpectra.py
    #----------------
    print '\nStarting mvSpectra.py: copying files from ya/id/'+loc+' to /data1/'+loc
    try: 
        os.system('mvSpectra.py')
    except OSError as errmsg:
        print errmsg
        sys.exit()

    #----------------
    # Starting delSpcdel.py: Nothing to Do
    #----------------
    print '\nStarting delSpcdel.py: deleting Files if found in deleted folder'
    try:
        os.system('delSpcdel.py -y'+str(year)+ ' -s'+loc)
    except OSError as errmsg:
        print errmsg
        sys.exit()

    #----------------
    # Starting mkSpecDB.py: IMPORTANT --> Since spDB is removed Modify specDBInputFile every year Only
    #----------------
    spDB     = '/data/Campaign/'+loc.upper()+'/Spectral_DB/spDB_'+loc.lower()+'_'+str(year)+'.dat'
    
    if ckFile(spDB):
        print 'Deleting: '+ spDB
        os.remove(spDB)
    
    print '\nStarting mkSpecDB.py: Initial Spectral Database'
    try: 
        os.system('mkSpecDB.py -i /data/Campaign/'+loc.upper()+'/Spectral_DB/'+'specDBInputFile_'+loc.upper()+'.py')
    except OSError as errmsg:
        print errmsg
        sys.exit()
    
    #----------------
    # Starting station_house_reader.py: IMPORTANT --> Since HouseData is removed Modify inputs in station_house_reader every year Only
    #----------------
    if loc.lower() != 'fl0':
        House     = '/data/Campaign/'+loc.upper()+'/House_Log_Files/'+loc.upper()+'_HouseData_'+str(year)+'.dat'

        if ckFile(House):
            print 'Deleting: '+ House
            os.remove(House)

        print '\nStarting station_house_reader.py: read House Data'
        try:
            os.system('station_house_reader.py')
        except OSError as errmsg:
            print errmsg
            sys.exit()

    #----------------
    # Starting read_FL0_EOL_data.py
    #----------------
    if loc.lower() == 'fl0':
        print '\nStarting read_FL0_EOL_data.py: read EOL data'
        os.system('read_FL0_EOL_data.py')

    #----------------
    # Starting mkSpecDB.py: IMPORTANT --> Si nce HRDB is removed Modify appndSpecDBInputFile every year Only
    #----------------
    HRspDB   = '/data/Campaign/'+loc.upper()+'/Spectral_DB/HRspDB_'+loc.lower()+'_'+str(year)+'.dat'
    
    if ckFile(HRspDB):
        print 'Deleting: '+ HRspDB
        os.remove(HRspDB)
    
    print '\nStarting appendSpecDB.py.py: Append Spectral Database File'
    try:
        os.system('appendSpecDB.py -i /data/Campaign/'+loc.upper()+'/Spectral_DB/'+'appndSpecDBInputFile.py')
    except OSError as errmsg:
        print errmsg
        sys.exit()

    #----------------
    # Starting read_FL0_EOL_data.py
    #----------------
    if (loc.lower() == 'fl0') & (int(year) < 2018):
        print '\nStarting mkCoadSpecDB.py: Coadd Spectral Database Fil'
        os.system('mkCoadSpecDB.py -i CoadSpecDBInputFile.py')

    #----------------
    # Starting NCEPnmcFormat.py --> Modify Initializations
    #----------------
    print '\nStarting NCEPnmcFormat.py: format the NCEP nmc data'
    try:
        os.system('NCEPnmcFormat.py -i /data/pbin/Dev_Ivan/RefProfiles/NCEPinputFile.py')
    except OSError as errmsg:
        print errmsg
        sys.exit()

    #----------------
    # Starting MergPrf.py: IMPORTANT --> Edit Input file Accordingly
    #----------------
    print '\nStarting MergPrf.py: ZPT and water files from WACCM data'
    try:
        os.system('MergPrf.py -i /data/pbin/Dev_Ivan/RefProfiles/mergprfInput.py')
    except OSError as errmsg:
        print errmsg
        sys.exit()

    #----------------
    # Starting NCEPwaterPrf.py: IMPORTANT --> Edit Input file Accordingly
    #----------------
    print '\nStarting NCEPwaterPrf.py: daily water profiles from NCEP'
    try:
        os.system('NCEPwaterPrf.py')
    except OSError as errmsg:
        print errmsg
        sys.exit()

    #----------------
    # Starting ERAwaterPrf.py: IMPORTANT --> Edit Input file Accordingly
    #----------------
    print '\nStarting NCEPwaterPrf.py: daily water profiles from NCEP'
    try:
        os.system('ERAwaterPrf.py')
    except OSError as errmsg:
        print errmsg
        sys.exit()

    print '\n\n'
    print '***********************************************************************'
    print '*************Begin sfit4Layer1 Analysis of Water Vapor*****************'
    print '***********************************************************************'  

    #----------------
    # Starting sfit4Layer1.py: IMPORTANT --> Edit Input file Accordingly
    #----------------
    print '\nStarting sfit4Layer1.py: h2o analysis'
    try:
        os.system('sfit4Layer1.py -i /data1/ebaumer/'+loc.lower()+'/h2o/'+loc.upper()+'_H2O_Input.py')
    except OSError as errmsg:
        print errmsg
        sys.exit()

    #----------------
    # Starting retWaterPrf.py: IMPORTANT --> Edit Input file Accordingly
    #----------------
    print '\nStarting retWaterPrf.py: Create Water Profiles in data directory'
    try:
        os.system('retWaterPrf.py')
    except OSError as errmsg:
        print errmsg
        sys.exit()

    #----------------
    # Starting retWaterPrfDaily.py: --> Edit Input file Accordingly
    #----------------
    print '\nStarting retWaterPrfDaily.py: Create Water Profiles in data directory'
    try:
        os.system('retWaterPrfDaily.py')
    except OSError as errmsg:
        print errmsg
        sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])