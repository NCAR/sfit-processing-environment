#!/usr/bin/python
##! /usr/local/python-2.7/bin/python

# Change the above line to point to the location of your python executable

#----------------------------------------------------------------------------------------
# Name:
#        mkCoadSpecDb.py
#
# Purpose:
#       This program creates a database for coadd spectra. It reads the non-coadded 
#       spectral database and coadds two files using coad.c.
#           
#
#
# Input files:
#       1) Input file (Optional)
#       2) Original spectral database
#
# Output files:
#       1) Coadded spectral database file 
#
# Called Functions:
#       1) No external called functions (other than system functions)
#
#
# Notes:
#       1) 
#
#
# Usage:
#     mkCoadSpecDb.py -i <File> -D <Directory>
#              -i           Input file for mkCoadSpecDb.py
#
# Examples:
#    ./mkCoadSpecDb.py -i /home/data/DatabaseInputFile.py          -- This runs the program with the input file DatabaseInputFile.py
#
# Version History:
#  1.0     Created, November, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
#
#
# References:
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

                        #-------------------------------------#
                        # Define helper functions and classes #
                        #-------------------------------------#
            
                                                     
def usage():
    ''' Prints to screen standard program usage'''
    print ('mkSpecDB.py -i <File>')

        
def ckDir(dirName,logFlg=False,exit=False):
    ''' '''
    if not os.path.exists( dirName ):
        print ('Input Directory %s does not exist' % (dirName))
        if logFlg: logFlg.error('Directory %s does not exist' % dirName)
        if exit: sys.exit()
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

def checkOPUS(ckopus,indvfile):
    '''Check if file is OPUS file'''
    rtn           = sp.Popen([ckopus,'-C',indvfile], stdout=sp.PIPE, stderr=sp.PIPE)
    stdout,stderr = rtn.communicate()
    rtnCode       = rtn.returncode
    if not (rtnCode == 1 or rtnCode == 3):                    
        return True                                            
    else:
        return False
    
def findAvgTPRH(val1,val2,misval):
    ''' '''
    if   ( (val1 != misval) and (val2 != misval) ): newVal = ( val1 + val2 ) / 2.0
    elif ( (val1 == misval) and (val2 != misval) ): newVal = val2
    elif ( (val1 != misval) and (val2 == misval) ): newVal = val1
    else:                                          newVal = misval    
    
    return newVal

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
        opts, args = getopt.getopt(sys.argv[1:], 'i:D:')

    except getopt.GetoptError as err:
        print (str(err))
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
            print ('Unhandled option: ' + opt)
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
    # Directory for days processed file
    if DBinputs.inputs['DaysProcFlg']:
        ckDir(DBinputs.inputs['DaysProcDir'], exit=True )
           
        # check if '/' is included at end of path
        if not( DBinputs.inputs['DaysProcDir'].endswith('/') ):
            DBinputs.inputs['DaysProcDir'] = DBinputs.inputs['DaysProcDir'] + '/'    
            
    # Base directory for data    
    ckDir(DBinputs.inputs['dataBaseDir'],exit=True)                     

    # check if '/' is included at end of path
    if not( DBinputs.inputs['dataBaseDir'].endswith('/') ):
        DBinputs.inputs['dataBaseDir'] = DBinputs.inputs['dataBaseDir'] + '/'          
        
    # Check Coadd executable file    
    ckFile(DBinputs.inputs['coaddex'], exit=True )                            

    # Check input spectral database file
    ckFile(DBinputs.inputs['inputDBfile'], exit=True)

    # Directory of output spectral database file
    ckDir(os.path.dirname(DBinputs.inputs['outputDBfile']), exit=True)
                             
    #-------------------------------------
    # Read original spectral database file
    #-------------------------------------
    OrgSpecDB = sc.DbInputFile(DBinputs.inputs['inputDBfile'])
    OrgSpecDB.getInputs()                      
    
    #------------------------------------
    # Initialize processed directory list
    #------------------------------------
    procList = []
    
    #--------------------------------------
    # Open Coadd Spectral DB file for write
    #--------------------------------------
    with open(DBinputs.inputs['outputDBfile'],'w') as fopen:        
        #----------------------------------------
        # Write header to Coadd Spectral DataBase
        # This should be the same as the Original 
        # spectral database
        #----------------------------------------
        with open(DBinputs.inputs['inputDBfile'],'r') as fopen2:
            firstLn = fopen2.readline()
                    
        #-----------------------------------------------
        # Now that we have two files for coadded we need
        # to add another column for Filename1
        #-----------------------------------------------
        firstLn = 'Filename1        ' + firstLn.replace('Filename','Filename2')
        fopen.write(firstLn)
            
            
        #----------------------------------------------
        # Loop through entries in the original spectral
        # database to find coadded files
        #----------------------------------------------
        for ind,fName in enumerate(OrgSpecDB.dbInputs['Filename']):
            
            #------------------------------------------------
            # Check if this is a potential file for coadding:
            #  -- The number of FLSCN must be half of EXSCN
            #------------------------------------------------
            flscn = int(OrgSpecDB.dbInputs['FLSCN'][ind])
            exscn = int(OrgSpecDB.dbInputs['EXSCN'][ind])
            gfw   = int(OrgSpecDB.dbInputs['GFW'][ind])
            gbw   = int(OrgSpecDB.dbInputs['GBW'][ind])

            
            #if (exscn/flscn != 2 ): continue
            if ( np.true_divide(exscn,flscn) != 2 ): continue
            
            #------------------------------------------------------
            # Extract the base file name and the date for filtering
            #------------------------------------------------------
            baseName = OrgSpecDB.dbInputs['Filename'][ind].strip().split('.')[0]
            extName  = OrgSpecDB.dbInputs['Filename'][ind].strip().split('.')[1]
            yyyymmdd = str(int(OrgSpecDB.dbInputs['Date'][ind]))
            yearstr  = yyyymmdd[0:4]
            monthstr = yyyymmdd[4:6]
            daystr   = yyyymmdd[6:]
            curDate  = dt.date(int(yearstr),int(monthstr),int(daystr))
            
            #print ind, baseName, extName, yyyymmdd
            #-------------------------------------------------------
            # Construct the bnr file name of the first file to coadd
            #-------------------------------------------------------
            hh1 = OrgSpecDB.dbInputs['Time'][ind][0:2]
            mm1 = OrgSpecDB.dbInputs['Time'][ind][3:5]
            ss1 = OrgSpecDB.dbInputs['Time'][ind][6:]
            bnrFname1 = hh1 + mm1 + ss1 + '.bnr'
            
            #-----------------------------------------------
            # Construct directory location of bnr files from
            # date and input file information
            #-----------------------------------------------
            dayDir = DBinputs.inputs['dataBaseDir'] + yearstr + monthstr + daystr + '/'            
            ckDir(dayDir,exit=True)
            
            procList.append(dayDir)
            
            #----------------------------------------------------
            # Filter original specDB based on current day of file
            #----------------------------------------------------
            inDateRange    = sc.DateRange( int(yearstr),int(monthstr),int(daystr),int(yearstr),int(monthstr),int(daystr) )
            flt1_OrgSpecDB = OrgSpecDB.dbFilterDate(inDateRange)
            
            #---------------------------------------------
            # Find filenames that match base and have the 
            # extension of (n+1), where n is the extension
            # of the original filename
            #---------------------------------------------
            # Construct file name of coadded partner

            newFname = baseName + '.' + str( int(extName) + 1 )
            indFind  = [i for i,dum in enumerate(flt1_OrgSpecDB['Filename']) if dum.endswith(newFname) ]
            if not indFind: continue
            if len(indFind) > 1: 
                print ('More than one match found for: ' + newFname + ' Date: ' + yearstr + monthstr + daystr + ' ERROR!!')
                sys.exit()
            indFind = indFind[0]

            #-----------------------------------------
            # Check if this a valid coadded file pair:
            # Number of GFW in first file must equal
            # the number of GBW in second file
            #-----------------------------------------
            if (OrgSpecDB.dbInputs['GFW'][ind] != flt1_OrgSpecDB['GBW'][indFind]): continue
            
            #--------------------------------------------------------
            # Construct the bnr file name of the second file to coadd
            #--------------------------------------------------------
            hh2       = flt1_OrgSpecDB['Time'][indFind][0:2]
            mm2       = flt1_OrgSpecDB['Time'][indFind][3:5]
            ss2       = flt1_OrgSpecDB['Time'][indFind][6:]
            bnrFname2 = hh2 + mm2 + ss2 + '.bnr'            
            
            #---------------------------------------------------------
            # Check if the second coadded file is within 10 minutes of
            # the first. This will ensure that the files are pairs
            #---------------------------------------------------------
            time1 = float(hh1) * 60.0 + float(mm1) + float(ss2) / 60.0   
            time2 = float(hh2) * 60.0 + float(mm2) + float(ss2) / 60.0   
            if abs(time2 - time1) > 10: continue
        
            #------------------------------------------------------------
            # Construct the coadd input file in the appropriate directory
            #------------------------------------------------------------
            with open(dayDir + 'coad.i', 'w') as coaddInput:
                coaddInput.write('2\n')
                coaddInput.write(dayDir + bnrFname1 + '\n')
                coaddInput.write(dayDir + bnrFname2 + '\n')
            
            #--------------------------------------------------
            # Call coadd executable, rename bnr file, and read
            # coadd output file for coadd spectral database
            # Make sure cwd is same location as OPUS file
            #--------------------------------------------------          
            if not dayDir == os.getcwd():
                os.chdir(dayDir)            
            
            paramList = [DBinputs.inputs['coaddex'],'-S' + DBinputs.inputs['loc'],'-TOPU', '-c']
            rtn       = sp.Popen(paramList, stdout=sp.PIPE, stderr=sp.PIPE)
            stdoutCom, stderrCom = rtn.communicate()
            
            #----------------------------
            # Read output file from coadd
            #----------------------------
            with open(dayDir + 'coad.out', 'r') as fopen3:
                coadOut = fopen3.readlines()
            
            #--------------------------------------
            # Check if coad successfully ran. A 
            # sucessful run happens when at the 
            # end of coad.err the following line
            # is present: Closed bnr file: temp.bnr
            #--------------------------------------
            with open(dayDir + 'coad.err', 'r') as fopenCerr: coadErr = fopenCerr.readlines()
            if (not coadErr) or (not 'Closed bnr file: temp.bnr' in coadErr[-1]):
                print ('Error processing coad files for {}'.format(dayDir))
                print (coadErr)
                continue
            
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
            
            #-----------------------------------------------
            # Change name of new bnr file based on timestamp
            #-----------------------------------------------
            if os.path.isfile(dayDir + 'temp.bnr'):
                shutil.move(dayDir + 'temp.bnr', dayDir + TstampNew + '.bnrc')
            else:
                print ('Unable to move file: %s to %s' %(dayDir + TstampNew + '.bnrc') )           
                
            #------------------------------------------------------------------------
            # Find the averages for surface temperature, pressure and RH measurements
            #------------------------------------------------------------------------
            # Check if any measurements are missing
            HouseTemp1 = OrgSpecDB.dbInputs['HouseTemp'][ind]
            HouseTemp2 = flt1_OrgSpecDB['HouseTemp'][indFind]
            HousePres1 = OrgSpecDB.dbInputs['HousePres'][ind]
            HousePres2 = flt1_OrgSpecDB['HousePres'][indFind]
            HouseRH1   = OrgSpecDB.dbInputs['HouseRH'][ind]
            HouseRH2   = flt1_OrgSpecDB['HouseRH'][indFind]
            
            ExtStatTemp1 = OrgSpecDB.dbInputs['ExtStatTemp'][ind]
            ExtStatTemp2 = flt1_OrgSpecDB['ExtStatTemp'][indFind]
            ExtStatPres1 = OrgSpecDB.dbInputs['ExtStatPres'][ind]
            ExtStatPres2 = flt1_OrgSpecDB['ExtStatPres'][indFind]
            ExtStatRH1   = OrgSpecDB.dbInputs['ExtStatRH'][ind]
            ExtStatRH2   = flt1_OrgSpecDB['ExtStatRH'][indFind]
            
            HouseTempNew   = findAvgTPRH( HouseTemp1,   HouseTemp2,   -9999 )
            HousePresNew   = findAvgTPRH( HousePres1,   HousePres2,   -9999 )
            HouseRHNew     = findAvgTPRH( HouseRH1,     HouseRH2,     -99   )
            ExtStatTempNew = findAvgTPRH( ExtStatTemp1, ExtStatTemp2, -9999 )
            ExtStatPresNew = findAvgTPRH( ExtStatPres1, ExtStatPres2, -9999 )
            ExtStatRHNew   = findAvgTPRH( ExtStatRH1,   ExtStatRH2,   -99   )
            
            #--------------------------------------------
            # Write new line to coadded spectral database
            #--------------------------------------------
            # [ OPUS_filename1, OPUS_filename2, Site, SBlock, TOffs, TStamp, Date, Time, SNR, N_Lat, W_Lon, Alt, SAzm,
            #   SZen, ROE, Dur, Reso, Apd, FOV, LWN, HWN, Flt, MaxY, MinY, FLSCN, EXSCN, GFW, GBW, HouseTemp, HousePres,
            #   HouseRH, ExtStatTemp, ExtStatPres, ExtStatRH, Ext_Solar_Sens, Quad_Sens, Det_Intern_T_Swtch              ]
            
            try: Flt = int(OrgSpecDB.dbInputs['Flt'][ind])
            except ValueError: Flt = OrgSpecDB.dbInputs['Flt'][ind]
            
            coaddLine = [OrgSpecDB.dbInputs['Filename'][ind], newFname, OrgSpecDB.dbInputs['Site'][ind],OrgSpecDB.dbInputs['SBlock'][ind],
                         '-999',TstampNew,dateNew,TstampNewf,'-999',OrgSpecDB.dbInputs['N_Lat'][ind],OrgSpecDB.dbInputs['W_Lon'][ind],
                         OrgSpecDB.dbInputs['Alt'][ind], azmOut,szaOut,roeOut,durOut,OrgSpecDB.dbInputs['Reso'][ind],
                         apdOut, fovOut, lwavOut, uwavOut, Flt, maxYout, minYout,'-999',
                         int(OrgSpecDB.dbInputs['EXSCN'][ind]),int(OrgSpecDB.dbInputs['GFW'][ind]),int(flt1_OrgSpecDB['GBW'][indFind]),
                         HouseTempNew, HousePresNew, HouseRHNew, ExtStatTempNew, ExtStatPresNew, ExtStatRHNew, '-9999', '-9999','-9999']
            
            strformat = ['{0:<17}','{1:<15}'] + [' {'+str(i)+':<12}' for i in range(2,len(coaddLine))]
            strformat = ''.join(strformat).lstrip().rstrip() + '\n'
            
            fopen.write(strformat.format(*coaddLine))
               
            #----------------------------------------------
            # Remove the second coadded file in the orginal
            # spectral database dictionary so we do loop
            # on this file. First find where second file
            # maps to in original spectral DB dictionary
            #----------------------------------------------
            # Loop through origin dictionary
            indMap = [i for i,(Tstamp,date) in enumerate(itertools.izip(OrgSpecDB.dbInputs['TStamp'],OrgSpecDB.dbInputs['Date'])) \
                      if (flt1_OrgSpecDB['TStamp'][indFind] == Tstamp and flt1_OrgSpecDB['Date'][indFind] == date)]
            indMap = indMap[0]
            # Remove index from original DB dictionary
            for k in OrgSpecDB.dbInputs:
                del OrgSpecDB.dbInputs[k][indMap]
        
                        
    #-------------------------------------------
    # Write list of folders that where processed
    #-------------------------------------------
    if DBinputs.inputs['DaysProcFlg']:
        #------------------------------        
        # Create a unique ordered set
        #------------------------------
        procList = list(set(procList))    
        procList.sort()
        fProcname = DBinputs.inputs['DaysProcDir'] + 'FldrsProc_' + dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.list'
        with open(fProcname,'w') as fopen:
            for item in procList:
                fopen.write('%s\n' % item)
                        
                                                                             
if __name__ == "__main__":
    main(sys.argv[1:])