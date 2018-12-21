#!/usr/bin/python
##! /usr/local/python-2.7/bin/python

#----------------------------------------------------------------------------------------
# Name:
#        mkCoadSpecDbflt.py
#
# Purpose:
#       - This program creates a database for coadd spectra based on a specific Filter Number. 
#       - It reads the non-coadded spectral database and coadds files using coad.c.
#       - There are General Logical Flags to controls whether a SZA or number of days are used in the process
#       - If DaysFlg is False:  the it coaddss all spectra from one day
#       - If szaFlg is False:  the it coaddss all SZA
#       - If DaysFlg IS True it uses a type of continuous day. 
#
#
# Input files:
#       1) Input file, e.g., see CoadSpecDBInputFile_flt
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
import sys
import os
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
    print 'mkCoadSpecDb_flt.py -i <File>'

        
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

def checkOPUS(ckopus,indvfile):
    '''Check if file is OPUS file'''
    rtn           = sp.Popen([ckopus,'-C',indvfile], stdout=sp.PIPE, stderr=sp.PIPE)
    stdout,stderr = rtn.communicate()
    rtnCode       = rtn.returncode
    if not (rtnCode == 1 or rtnCode == 3):                    
        return True                                            
    else:
        return False
    
def ckDirMk(dirName,logFlg=False):
    ''' '''
    if not ( os.path.exists(dirName) ):
        os.makedirs( dirName )
        if logFlg: logFlg.info( 'Created folder %s' % dirName)  
        return False
    else:
        return True

                            #----------------------------#
                            #                            #
                            #        --- Main---         #
                            #                            #
                            #----------------------------#

def main(argv):

                                                #---------------------------------#
                                                # Retrieve command line arguments #
                                                #---------------------------------#
    #------------------------------------------------------------------------------------------------------------#                                             
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:')

    except getopt.GetoptError as err:
        print str(err)
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
            inputFile = arg
            
        #------------------
        # Unhandled options
        #------------------
        else:
            print 'Unhandled option: ' + opt
            usage()
            sys.exit()
    #------------------------------------------------------------------------------------------------------------#                       
        
    #----------------
    # Read input file
    #----------------
    # Input file instance
    DBinputs = sc.Layer1InputFile(inputFile)    
    DBinputs.getInputs()

      
    #-----------------------------------
    # Check the existance of directories
    # and files given in input file
    #-----------------------------------
    if DBinputs.inputs['DaysProcFlg']:
        ckDir(DBinputs.inputs['outputDBDir'], exit=True )
           
        # check if '/' is included at end of path
        if not( DBinputs.inputs['outputDBDir'].endswith('/') ):
            DBinputs.inputs['outputDBDir'] = DBinputs.inputs['outputDBDir'] + '/'    
            
    # Base directory for data    
    if not( DBinputs.inputs['outputDBDir'].endswith('/') ):
            DBinputs.inputs['outputDBDir'] = DBinputs.inputs['outputDBDir'] + '/'  
    
    ckDir(DBinputs.inputs['dataBaseDir'],exit=True)                     

    # check if '/' is included at end of path
    if not( DBinputs.inputs['dataBaseDir'].endswith('/') ):
        DBinputs.inputs['dataBaseDir'] = DBinputs.inputs['dataBaseDir'] + '/'          
        
    # Check Coadd executable file    
    ckFile(DBinputs.inputs['coaddex'], exit=True )                            

    # Check input spectral database file
    #ckFile(DBinputs.inputs['inputDBfile'], exit=True)
    ckDir(DBinputs.inputs['inputDBDir'], exit=True)

    if not( DBinputs.inputs['inputDBDir'].endswith('/') ):
        DBinputs.inputs['inputDBDir'] = DBinputs.inputs['inputDBDir'] + '/'

    # Directory of output spectral database file
    ckDir(DBinputs.inputs['outputDBDir'],exit=True) 
                             
    
    years     = [i +DBinputs.inputs['iyear']  for i in range((DBinputs.inputs['fyear'] - DBinputs.inputs['iyear']) +1)]

    for y in years:

        print '***************************************'
        print 'Coadding spectra in year: {} '.format(y)
        print '***************************************'



        #-------------------------------------
        # Read original spectral database file
        #-------------------------------------
        inputDBfile = DBinputs.inputs['inputDBDir'] + DBinputs.inputs['inputDBfile'][0]+str(y)+DBinputs.inputs['inputDBfile'][1]

        if not ckFile(inputDBfile, exit=False ) : continue

        OrgSpecDB = sc.DbInputFile(inputDBfile)
        OrgSpecDB.getInputs()

        #-------------------------------------
        # Filter database based on Filter ID
        #-------------------------------------
        flt_OrgSpecDB = OrgSpecDB.dbFilterFltrID(DBinputs.inputs['fltID'])

        outputDBfile   = DBinputs.inputs['outputDBDir'] + DBinputs.inputs['outputDBid'][0] + str(y) + DBinputs.inputs['outputDBid'][1] 

        YearRange    = sc.DateRange( y,1,1, y,12,31 )
        flt_OrgSpecDB = OrgSpecDB.dbFilterDate(YearRange, fltDict=flt_OrgSpecDB)

        #------------------------------------
        # Initialize processed directory list
        #------------------------------------
        procList = []
        bnrList  = []
        
        #--------------------------------------
        # Open Coadd Temporal Spectral DB file for write (this is temporal due that it will loop for sza and later on the new sort in time specra will be created)
        #--------------------------------------
        with open(DBinputs.inputs['outputDBDir']+'temp.dat','w') as fopen:    

            #----------------------------------------
            # Read header of the Original spectral database
            #----------------------------------------
            with open(inputDBfile,'r') as fopen2:
                firstLn = fopen2.readline()
                        
            #-----------------------------------------------
            # Write first spectra and new coadded bnr
            #-----------------------------------------------
            firstLn = firstLn.replace('Filename','FilennewBnr')
            fopen.write(firstLn)

            #-------------------------------------
            # If szaFlg: Filter database based on SZA range
            #-------------------------------------    
            if DBinputs.inputs['szaFlg']:  
            
                for szai in DBinputs.inputs['szaRange']:

                    print '***************************************'
                    print 'Coadding spectra in sza range: {} - {}'.format(szai[0], szai[1])
                    print '***************************************'

                    flt1_OrgSpecDB = OrgSpecDB.dbFilterSZA(szai[0], szai[1] , fltDict=flt_OrgSpecDB)

                               
                    #----------------------------------------------
                    # Loop through entries in the original spectral
                    # database to find coadded files
                    #----------------------------------------------
                    for ind,fName in enumerate(flt1_OrgSpecDB['Filename']):

                        #------------------------------------------------

                        #------------------------------------------------
                        flscn = int(flt1_OrgSpecDB['FLSCN'][ind])
                        exscn = int(flt1_OrgSpecDB['EXSCN'][ind])
                        gfw   = int(flt1_OrgSpecDB['GFW'][ind])
                        gbw   = int(flt1_OrgSpecDB['GBW'][ind])
                        sza   = float(flt1_OrgSpecDB['SZen'][ind])
                        
                        #------------------------------------------------------
                        # Extract the base file name and the date for filtering
                        #------------------------------------------------------
                        baseName = flt1_OrgSpecDB['Filename'][ind].strip().split('.')[0]
                        extName  = flt1_OrgSpecDB['Filename'][ind].strip().split('.')[1]
                        yyyymmdd = str(int(flt1_OrgSpecDB['Date'][ind]))
                        yearstr  = yyyymmdd[0:4]
                        monthstr = yyyymmdd[4:6]
                        daystr   = yyyymmdd[6:]
                        curDate  = dt.date(int(yearstr),int(monthstr),int(daystr))
                        
                        #-------------------------------------------------------
                        # Construct the bnr file name of the first file to coadd
                        #-------------------------------------------------------
                        hh1 = flt1_OrgSpecDB['Time'][ind][0:2]
                        mm1 = flt1_OrgSpecDB['Time'][ind][3:5]
                        ss1 = flt1_OrgSpecDB['Time'][ind][6:]
                        bnrFname1 = hh1 + mm1 + ss1 + '.bnr'

                        #----------------------------------------------------
                        # if DaysFlg: Filter original specDB based on number of days to coadd
                        #----------------------------------------------------
                        if DBinputs.inputs['DaysFlg']:
               
                            date_range = [dt.date(int(yearstr),int(monthstr),int(daystr)) + dt.timedelta(days=x) for x in range(0, DBinputs.inputs['NumDays'])]              
                            inDateRange    = sc.DateRange( date_range[0].year,date_range[0].month,date_range[0].day,date_range[-1].year,date_range[-1].month,date_range[-1].day )
                            
                        else:
                            inDateRange    = sc.DateRange( int(yearstr),int(monthstr),int(daystr),int(yearstr),int(monthstr),int(daystr) )

                        flt2_OrgSpecDB = OrgSpecDB.dbFilterDate(inDateRange, fltDict= flt1_OrgSpecDB)


                        #----------------------------------------------------
                        # if SpccNumFlg:  Minimum Number of Spectra to continue
                        #----------------------------------------------------
                        if DBinputs.inputs['SpccNumFlg']:
                            if len(flt2_OrgSpecDB['Date']) < DBinputs.inputs['NumSpc']: continue

                        #----------------------------------------------------
                        # Create list of files
                        #----------------------------------------------------
                        baseNameList = [s  for s in flt2_OrgSpecDB['Filename']]
                        yyyymmddList = [str(int(d))  for d in flt2_OrgSpecDB['Date']]
                        yearstrList  = [d[0:4] for d in yyyymmddList]
                        monthstrList = [d[4:6] for d in yyyymmddList]
                        daystrList   = [d[6:] for d in yyyymmddList]
                        datesList    = [dt.date(int(d[0:4]),int(d[4:6]),int(d[6:8])) for d in yyyymmddList]

                        hhlist       = [d[0:2]  for d in flt2_OrgSpecDB['Time']]
                        mmlist       = [d[3:5]  for d in flt2_OrgSpecDB['Time']]
                        sslist       = [d[6:]  for d in flt2_OrgSpecDB['Time']]

                        bnrFnameList = [hh + mm + ss + '.bnr' for (hh, mm, ss) in itertools.izip(hhlist, mmlist, sslist)] 

                        #-----------------------------------------------

                        #-----------------------------------------------
                        dayDirList = [DBinputs.inputs['dataBaseDir'] + yyyy + mm + dd + '/'   for (yyyy, mm, dd) in itertools.izip(yearstrList, monthstrList, daystrList)] 

                        for d in dayDirList: ckDir(d,exit=True)

                        listDatesTime = [d  + t for (d,t) in itertools.izip(dayDirList, baseNameList)] 
                    
                        #------------------------------------------------------------
                        # Construct the coadd input file in the appropriate directory
                        #------------------------------------------------------------
                        ckDirMk(DBinputs.inputs['DaysOutDir'])
                        with open(DBinputs.inputs['DaysOutDir'] + 'coad.i', 'w') as coaddInput:
                            coaddInput.write(str(len(bnrFnameList))+'\n')
                            for (di, bn) in zip(dayDirList, bnrFnameList):

                                coaddInput.write(di + bn + '\n')

                        #--------------------------------------------------
                        # Call coadd executable, rename bnr file, and read
                        # coadd output file for coadd spectral database
                        # Make sure cwd is same location as OPUS file
                        #--------------------------------------------------          
                        if not DBinputs.inputs['DaysOutDir'] == os.getcwd():
                            os.chdir(DBinputs.inputs['DaysOutDir'])            
                        
                        paramList = [DBinputs.inputs['coaddex'],'-S' + DBinputs.inputs['loc'],'-TOPU']
                        rtn       = sp.Popen(paramList, stdout=sp.PIPE, stderr=sp.PIPE)
                        stdoutCom, stderrCom = rtn.communicate()
                        
                        #----------------------------
                        # Read output file from coadd
                        #----------------------------
                        with open(DBinputs.inputs['DaysOutDir'] + 'coad.out', 'r') as fopen3:
                            coadOut = fopen3.readlines()
                        
                        #--------------------------------------
                        # Check if coad successfully ran. A 
                        # sucessful run happens when at the 
                        # end of coad.err the following line
                        # is present: Closed bnr file: temp.bnr
                        #--------------------------------------
                        with open(DBinputs.inputs['DaysOutDir'] + 'coad.err', 'r') as fopenCerr: coadErr = fopenCerr.readlines()
                        if (not coadErr) or (not 'Closed bnr file: temp.bnr' in coadErr[-1]):
                            print 'Error processing coad files for {}'.format(DBinputs.inputs['DaysOutDir'])
                            print coadErr
                            continue

                        #----------------------------
                        # Read output parameters 
                        #----------------------------
                        szaOut    = coadOut[0].strip()
                        opdOut    = coadOut[1].strip()
                        fovOut    = coadOut[2].strip()
                        apdOut    = coadOut[3].strip()
                        lwavOut   = coadOut[4].strip()
                        uwavOut   = coadOut[5].strip()
                        TstampOut = coadOut[6].strip()
                        hdrStrOut = coadOut[7].strip()
                        azmOut    = coadOut[8].strip()
                        durOut    = coadOut[9].strip()
                        roeOut    = coadOut[10].strip()
                        maxYout   = coadOut[11].strip()
                        minYout   = coadOut[12].strip()
                       
                        yearNew   = TstampOut.split()[0]
                        monthNew  = TstampOut.split()[1]
                        dayNew    = TstampOut.split()[2]
                        hhNew     = TstampOut.split()[3]
                        mmNew     = TstampOut.split()[4]
                        ssNew     = TstampOut.split()[5].split('.')[0]
                        dateNew   = yearNew + monthNew + dayNew
                        TstampNew = hhNew + mmNew + ssNew
                        TstampNewf= hhNew + ':' + mmNew + ':' + ssNew

                        Newbnr    = TstampNew + '.bnrc'

                        #-----------------------------------------------
                        # remove co
                        #-----------------------------------------------
                        newDir    = DBinputs.inputs['DaysOutDir'] + yearNew + monthNew + dayNew + '/' 
         
                        ckDirMk(newDir)  
                        #if ckDirMk(newDir):
                        #    for f in glob.glob(newDir + '*.bnrc'): os.remove(f)

                        #-----------------------------------------------
                        # Change name of new bnr file based on new timestamp
                        #-----------------------------------------------
                        if os.path.isfile(DBinputs.inputs['DaysOutDir'] + 'temp.bnr'):
                            shutil.move(DBinputs.inputs['DaysOutDir'] + 'temp.bnr', newDir + Newbnr)
                        else:
                            print 'Unable to move file: %s to %s' %(newDir + Newbnr)            
                            
                        #------------------------------------------------------------------------
                        # Find the averages for surface temperature, pressure and RH measurements
                        #------------------------------------------------------------------------
                        HouseTempNew     = np.nanmean(flt2_OrgSpecDB['HouseTemp']);   HouseTempNew   = format(HouseTempNew, '.4g')
                        HousePresNew     = np.nanmean(flt2_OrgSpecDB['HousePres']);   HousePresNew   = format(HousePresNew, '.4g')
                        HouseRHNew       = np.nanmean(flt2_OrgSpecDB['HouseRH']);     HouseRHNew     = format(HouseRHNew, '.4g')
                        ExtStatTempNew   = np.nanmean(flt2_OrgSpecDB['ExtStatTemp']); ExtStatTempNew = format(ExtStatTempNew, '.4g')
                        ExtStatPresNew   = np.nanmean(flt2_OrgSpecDB['ExtStatPres']); ExtStatPresNew = format(ExtStatPresNew, '.4g')
                        ExtStatRHNew     = np.nanmean(flt2_OrgSpecDB['ExtStatRH']);   ExtStatRHNew   = format(ExtStatRHNew, '.4g')

                        #--------------------------------------------
                        # Write new line to coadded spectral database
                        #--------------------------------------------
                        coaddLine = [Newbnr, flt2_OrgSpecDB['Site'][0],flt2_OrgSpecDB['SBlock'][0],
                                     '-999',TstampNew,dateNew,TstampNewf,'-999',flt2_OrgSpecDB['N_Lat'][0],flt2_OrgSpecDB['W_Lon'][0],
                                     flt2_OrgSpecDB['Alt'][0], azmOut,szaOut,roeOut,durOut,OrgSpecDB.dbInputs['Reso'][ind],
                                     apdOut, fovOut, lwavOut, uwavOut, DBinputs.inputs['fltID'], maxYout, minYout,'-999',
                                     int(flt2_OrgSpecDB['EXSCN'][0]),int(flt2_OrgSpecDB['GFW'][0]),int(flt2_OrgSpecDB['GBW'][0]),
                                     HouseTempNew, HousePresNew, HouseRHNew, ExtStatTempNew, ExtStatPresNew, ExtStatRHNew, '-9999', '-9999','-9999']
                        
                        strformat = ['{0:<17}','{1:<15}'] + [' {'+str(i)+':<12}' for i in range(2,len(coaddLine))]
                        #strformat = ['{0:<15}'] + [' {'+str(i)+':<12}' for i in range(2,len(coaddLine))]
                        strformat = ''.join(strformat).lstrip().rstrip() + '\n'
                      
                        fopen.write(strformat.format(*coaddLine))

                        procList.append(listDatesTime)
                        bnrList.append(newDir+Newbnr)
                           
                        #----------------------------------------------
                        # Use this to remove spectra collected in the start and move to next date, i.e., some type of running average)
                        #----------------------------------------------
                        indMap = [i for i, date in enumerate(flt1_OrgSpecDB['Date']) if flt2_OrgSpecDB['Date'][0] == date]
                        indMap = indMap[0]
              
                        for k in flt1_OrgSpecDB:
                           del flt1_OrgSpecDB[k][indMap]

                        #----------------------------------------------
                        # Use this to remove all spectra collected in the coadded process
                        #----------------------------------------------
                        #for j,(Tstamp, date) in enumerate(itertools.izip(flt2_OrgSpecDB['TStamp'],flt2_OrgSpecDB['Date'])):
                        #
                        #    indMap = np.where( (np.asarray(flt1_OrgSpecDB['TStamp']) == float(Tstamp) ) & (np.asarray(flt1_OrgSpecDB['Date']) == float(date)))[0]
                        #    indMap = indMap[0]
                        #
                        #    for k in flt1_OrgSpecDB:
                        #        del flt1_OrgSpecDB[k][indMap]

                        #----------------------------------------------
                        # IF cpPrfFlg
                        #----------------------------------------------

                        if DBinputs.inputs['cpPrfFlg']:
                            orgDataDir = DBinputs.inputs['dataBaseDir'] + dateNew + '/'


                            fw   = glob.glob(orgDataDir + 'w-120*')
                            
                            if len(fw) >= 1:

                                for f in glob.glob(orgDataDir + 'w-120*'): 
                                    shutil.copy2(f, newDir)

                            else: 
                                print "Unable to copy water profiles from. {}, trying. {}".format(orgDataDir, dayDirList[len(dayDirList)/2])
                                
                                for f in glob.glob(dayDirList[len(dayDirList)/2] + 'w-120*'): 

                                    shutil.copy2(f, newDir)
               
                            try:
                            
                                shutil.copy2(orgDataDir + 'ZPT.nmc.120', newDir )

                            except IOError as e:
                    
                                print "Unable to copy file. {}, trying. {}".format(e, dayDirList[len(dayDirList)/2])
                                shutil.copy2(dayDirList[len(dayDirList)/2] + 'ZPT.nmc.120', newDir )

                            except:
                                print("Unexpected error:", sys.exc_info())

                        print newDir

                        #user_input = raw_input('Press any key to exit >>> ')
                        #if ind == 4: exit()

        #-------------------------------------
        # Read original spectral database file
        #-------------------------------------
        FinalSpecDB = sc.DbInputFile(DBinputs.inputs['outputDBDir']+'temp.dat')
        FinalSpecDB.getInputs()

        #Date   = [str(d).split('.')[0] for d in FinalSpecDB.dbInputs['Date'] ]
        #Time   = [str(t).split('.')[0] for t in FinalSpecDB.dbInputs['TStamp'] ]

        try:
      
            base  =  FinalSpecDB.dbInputs['Date']

            for key in FinalSpecDB.dbInputs:
                FinalSpecDB.dbInputs[key] = [y for (x,y) in sorted(zip(base,FinalSpecDB.dbInputs[key]))]


            with open(DBinputs.inputs['outputDBDir']+'temp.dat','r') as fopen2:
                firstLn = fopen2.readline()

            keys =  firstLn.strip().split()

            with open(outputDBfile,'w') as fopen:  
                fopen.write(firstLn)

                for ind,fName in enumerate(FinalSpecDB.dbInputs['Date']):

                    coaddLine = [FinalSpecDB.dbInputs[k][ind] for k in keys]
                    strformat = ['{0:<17}','{1:<15}'] + [' {'+str(i)+':<12}' for i in range(2,len(coaddLine))]
                    strformat = ''.join(strformat).lstrip().rstrip() + '\n'
                    fopen.write(strformat.format(*coaddLine))


            os.remove(DBinputs.inputs['outputDBDir']+'temp.dat')


            procList = [y for (x,y) in sorted(zip(base,procList))]
            bnrList  = [y for (x,y) in sorted(zip(base,bnrList))]
                          
            #-------------------------------------------
            # Write list of folders that where processed
            #-------------------------------------------
            if DBinputs.inputs['DaysProcFlg']:

                #------------------------------        
                # Create a unique ordered set
                #------------------------------

                fProcname = DBinputs.inputs['outputDBDir'] + 'FldrsProc_' + os.path.splitext(os.path.basename(outputDBfile))[0]+'.list'
                with open(fProcname,'w') as fopen:
                    fopen.write('%s\n' % '# DataBase Created Using Input File   : %s'%inputFile)
                    fopen.write('%s\n' % '# DataBase Created Using fltID        : %s'%DBinputs.inputs['fltID'])
                    fopen.write('%s\n' % '# DataBase Created Using inputDBfile  : %s'%DBinputs.inputs['inputDBfile'])
                    fopen.write('%s\n' % '# DataBase Created Using szaFlg       : %s'%DBinputs.inputs['szaFlg'])
                    if DBinputs.inputs['szaFlg']: fopen.write('%s\n' % '# DataBase Created Using SZA range    : %s'%(str(DBinputs.inputs['szaRange'])))
                    fopen.write('%s\n' % '# DataBase Created Using DaysFlg      : %s'%DBinputs.inputs['DaysFlg'])
                    if DBinputs.inputs['DaysFlg']: fopen.write('%s\n' % '# DataBase Created Using NumDays      : %s'%DBinputs.inputs['NumDays'])
                    fopen.write('%s\n' % '# DataBase Created Using SpccNumFlg   : %s'%DBinputs.inputs['SpccNumFlg'])
                    if DBinputs.inputs['SpccNumFlg']: fopen.write('%s\n' % '# DataBase Created Using NumSpc       : %s'%DBinputs.inputs['NumSpc'])

                    for i, item in enumerate(procList):

                        line = [i, 'bnr = '+bnrList[i], 'N = '+str(len(item)) ] + [j for j in item]

                        strformat = ['{0:<5}', '{1:<50}'  '{2:<10}'] +  [' {'+str(ii+3)+':<35}' for ii in range(0,len(item))]
                        strformat = ''.join(strformat).lstrip().rstrip() + '\n'
                        fopen.write(strformat.format(*line))

        except:
            print 'FinalSpecDB for year {} is empty'.format(y)
                        
                                                                             
if __name__ == "__main__":
    main(sys.argv[1:])