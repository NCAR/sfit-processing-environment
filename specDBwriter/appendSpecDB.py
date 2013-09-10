#! /usr/local/python-2.7/bin/python

#----------------------------------------------------------------------------------------
# Name:
#        appendSpecDB.py
#
# Purpose:
#       This program appends already created spectral database files with house and 
#       station outside pressure, temperature, and relative humidity
#           
#
#
# Input files:
#       1) Input file
#       2) Spectral DB file
#       3) House log file
#       4) External station file
#
# Output files:
#       1) Spectral database file 
#
# Called Functions:
#       1) No external called functions (other than system functions)
#
#
# Notes:
#       1) MLO data has E_radians and W_radians readings. Which one to use depends on if the
#          sun is in the eastern or western hemisphere. Hemisphere can be derived looking at 
#          solar azimuth angle:
#                                    N(180)
#                                      |
#                                      |
#                           W(90)------|-------E(270)
#                                      |
#                                      |
#                                     S(0)
#          If Sazm < 180 use W_radians
#          If Sazm > 180 use E_radians
#
#
# 
#
# Usage:
#     appendSpecDB.py -i <File> 
#              -i           Input file for mkSpecDB.py
#
# Examples:
#    ./mkSpecDB.py -i /home/data/DatabaseInputFile.py          -- This runs the program with the input file DatabaseInputFile.py
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
import datetime as dt
import DateRange as dr
import itertools as it
from glob import glob
import numpy as np
import csv

                        #-------------------------------------#
                        # Define helper functions and classes #
                        #-------------------------------------#
            
                                                     
def usage():
    ''' Prints to screen standard program usage'''
    print 'mkSpecDB.py -i <File> -D <Directory>'

        
def ckDir(dirName):
    '''Check if a directory exists'''
    if not os.path.exists( dirName ):
        print 'Directory %s does not exist' % (dirName)
        return False
    else:
        return True
        
def ckFile(fName,exit=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print 'File %s does not exist' % (fName)
        if exit:
            sys.exit()
        return False
    else:
        return True
        
def filterDict(dataDict,idate,fdate):
    ''' Filter dicitonary for values between idate and fdate'''
    inds   = []
    
    for ind,val in enumerate(dataDict['DateTime']):                            
        if idate <= val <= fdate:                                                   # Check if date-time is within range
            inds.append(ind)
            
    fltDic = {key: [val[i] for i in inds] for key, val in dataDict.iteritems()}     # Rebuild filtered dictionary. Not compatible with python 2.6
    return fltDic
        
def sortDict(DataDict,keyval):
    ''' Sort all values of dictionary based on values of one key'''
    base = DataDict[keyval]
    for k in DataDict:
        DataDict[k] = [y for (x,y) in sorted(zip(base,DataDict[k]))]
    return DataDict
        
                            #----------------------------#
                            #                            #
                            #        --- Main---         #
                            #                            #
                            #----------------------------#

def main(argv):
    
    #-----------------------------
    # Initializations and defaults
    #-----------------------------
    statDirFlg = False             # Flag to indicate the presence of external station data
    houseFlg   = False             # Flag to indicate the presence of house data
    
                                                #---------------------------------#
                                                # Retrieve command line arguments #
                                                #---------------------------------#
    #------------------------------------------------------------------------------------------------------------#                                             
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:D:')

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
            
            # Check if file exists
            ckFile(inputFile,True)
            
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
    DBinputs = {}
    execfile(inputFile, DBinputs)
    if '__builtins__' in DBinputs:
        del DBinputs['__builtins__']       
        
    #-----------------------------------
    # Check the existance of directories
    # and files given in input file
    #-----------------------------------
    # Directory for external station data  <optional>
    if 'statDir' in DBinputs and DBinputs['statDir']:                           
        if not ckDir(DBinputs['statDir']):
            sys.exit()
        # check if '/' is included at end of path
        if not( DBinputs['statDir'].endswith('/') ):
            DBinputs['statDir'] = DBinputs['statDir'] + '/'    
        statDirFlg = True
         
        
    # Spectral DB File
    ckFile(DBinputs['specDBFile'])   
    
    # House log file <optional>
    if 'houseFile' in DBinputs and DBinputs['houseFile']:
        if ckFile(DBinputs['houseFile']): houseFlg = True
        
    #-------------------------
    # Open and read SpecDBfile
    #-------------------------
    specDBinputs = {}
    with open(DBinputs['specDBFile'],'r') as fopen:
        reader = csv.DictReader(fopen, delimiter=' ',skipinitialspace=True)
        DBfieldNames = reader.fieldnames
        for row in reader:
            for key,val in row.iteritems():
                specDBinputs.setdefault(key,[]).append(val)
                 
    #---------------------------------------------
    # Create a DateTime entry in SpecDB dictionary
    #---------------------------------------------
    DBdatetime = [dt.datetime(int(date[0:4]),int(date[4:6]),int(date[6:8]),int(time[0:2]),int(time[3:5]),int(time[6:8])) \
                              for date,time in it.izip(specDBinputs['Date'],specDBinputs['Time'])]
    specDBinputs.setdefault('DateTime',[]).extend(DBdatetime)    
      
           
    #-------------------------------------------
    # Open and read house log data if applicable
    #-------------------------------------------
    #   LABEL                       Units          Column    Missing Value
    #---------------------------------------------------------------------
    #   Date                        YYYYMMDD       1         NA           
    #   Time                        HH:MM:SS       2         NA                 
    #   Outside_T                   C              12        -9999               
    #   Atm_Press                   mbar           15        -9999        
    #   Outside_RH                  %              16        -9999            
    #---------------------------------------------------------------------    
    if houseFlg:
        try:
            with open(DBinputs['houseFile'],'r') as fopen:
                houseData = {}
                reader = csv.reader(fopen,delimiter='\t')
                for row in reader:
                    if not row[0].startswith('#'):
                        houseData.setdefault('DateTime',[]).append(dt.datetime(int(row[0][0:4]),int(row[0][4:6]),int(row[0][6:8]),\
                                                                               int(row[1][0:2]),int(row[1][3:5]),int(row[1][6:8])))
                        
                        if DBinputs['loc'].lower() == 'mlo':
                            houseData.setdefault('Temp',[]).append(float(row[10]))
                            houseData.setdefault('RH',[]).append(float(row[12]))      
                            houseData.setdefault('E_Radiance',[]).append(float(row[29]))
                            houseData.setdefault('W_Radiance',[]).append(float(row[30]))
                            
                            # These values are not present in the mlo house log data
                            houseData.setdefault('Pres',[]).append(-9999)
                            houseData.setdefault('Det_Intern_T_Swtch',[]).append(-9999)
                            houseData.setdefault('Ext_Solar_Sens',[]).append(-9999)
                            #houseData.setdefault('Quad_Sens',[]).append(-9999)                            
                            
                        elif DBinputs['loc'].lower() == 'tab':
                            houseData.setdefault('Temp',[]).append(float(row[11]))
                            houseData.setdefault('Pres',[]).append(float(row[14]))
                            houseData.setdefault('RH',[]).append(float(row[15]))      
                            houseData.setdefault('Det_Intern_T_Swtch',[]).append(float(row[20]))
                            houseData.setdefault('Ext_Solar_Sens',[]).append(float(row[26]))
                            houseData.setdefault('Quad_Sens',[]).append(float(row[27]))     
                          
        except IOError:
            print 'Unable to find house data file: %s' % DBinputs['houseFile']
            
    #--------------------------------------------------
    # Open and read external station data if applicable
    #--------------------------------------------------
    if statDirFlg:
        if DBinputs['loc'].lower() == 'mlo':
            #   LABEL                       Units          Column    Missing Value
            #---------------------------------------------------------------------
            #   Year                        YYYY            2         NA           
            #   Month                       MM              3         NA                 
            #   Day                         DD              4         NA               
            #   Hour                        HH              5         NA       
            #   Minute                      MM              6         NA   
            #   Barometric Pressure         hPa             9        -999.90
            #   Temperature at 2m           C               10       -999.9
            #   Relative Humidity           %               13       -99
            #---------------------------------------------------------------------                                 
            cmdlFiles = glob( DBinputs['statDir'] + str(DBinputs['year']) + '/' + \
                              'met_mlo_insitu_1_obop_minute_'+ str(DBinputs['year']) + '*')
            
            if not len(cmdlFiles) == 0:
                statData = {}
                for cmdlFile in cmdlFiles:
                    with open(cmdlFile, 'r') as fopen:
                        reader = csv.reader(fopen,delimiter=' ',skipinitialspace=True)
                        for row in reader:
                            statData.setdefault('DateTime',[]).append(dt.datetime(int(row[1]),int(row[2]),int(row[3]),\
                                                                                  int(row[4]),int(row[5]),0))
                            statData.setdefault('Pres',[]).append(float(row[9]))
                            statData.setdefault('Temp',[]).append(float(row[10]))
                            statData.setdefault('RH',[]).append(float(row[13]))
                            
        elif DBinputs['loc'].lower() == 'fl0':
            #   LABEL                       Units          Column    Missing Value
            #---------------------------------------------------------------------
            #   Year                        YYYY            1         NA           
            #   Month                       MM              2         NA                 
            #   Day                         DD              3         NA               
            #   Hour                        HH              4         NA       
            #   Minute                      MM              5         NA   
            #   Barometric Pressure         mbar            8        -999.90
            #   Temperature                 C               6        -999.9
            #   Relative Humidity           %               7        -99
            #---------------------------------------------------------------------                   
            eolFile =  DBinputs['statDir'] + 'fl0_met_data_' + str(DBinputs['year']) + '.txt'
            if ckFile(eolFile):
                statData = {}
                with open(eolFile,'r') as fopen:
                    reader = csv.reader(fopen,delimiter=' ',skipinitialspace=True)
                    reader.next()         # Skip first row
                    for row in reader:
                        statData.setdefault('DateTime',[]).append(dt.datetime(int(row[0]),int(row[1]),int(row[2]),\
                                                                              int(row[3]),int(row[4]),0))
                        statData.setdefault('Pres',[]).append(float(row[7]))
                        statData.setdefault('Temp',[]).append(float(row[5]))
                        statData.setdefault('RH',[]).append(float(row[6]))                        

    #---------------------------------------------------------------
    # Cycle through each spectral DB entry and find corresponding
    # house and external station data. This depends on the averaging
    # time set in the user input file. If no data exits set values
    # to -999. Also, remove -999 values from house and external data
    #---------------------------------------------------------------
    for ind,dateTime in enumerate(specDBinputs['DateTime']):        
        idate     = dateTime
        fdateH    = dateTime + dt.timedelta(minutes=DBinputs['nminsHouse'])
        fdateS    = dateTime + dt.timedelta(minutes=DBinputs['nminsStation'])
              
        #----------------------------------
        # If no house data exists for
        # the year fill with missing values
        #----------------------------------
        if not 'houseData' in vars():
            specDBinputs.setdefault('HouseTemp',[]).append('-9999')
            specDBinputs.setdefault('HousePres',[]).append('-9999')
            specDBinputs.setdefault('HouseRH',[]).append('-99')
            specDBinputs.setdefault('Ext_Solar_Sens',[]).append('-9999')
            specDBinputs.setdefault('Quad_Sens',[]).append('-9999')
            specDBinputs.setdefault('Det_Intern_T_Swtch',[]).append('-9999')            
        
        else:
            # Filter house data dictionary
            fltrdData = filterDict(houseData,idate,fdateH)  
            # Find averages
            HouseTemp = np.array(fltrdData['Temp'])
            HousePres = np.array(fltrdData['Pres'])
            HouseRH   = np.array(fltrdData['RH']  )
            SolarSen  = np.array(fltrdData['Ext_Solar_Sens'])
            DetIntT   = np.array(fltrdData['Det_Intern_T_Swtch'])
            
            #--------------------------------------------------------------
            # If processing mlo have to determine whether to use E_radiance
            # or W_radiance for the Ext_Solar_Sens depending on Sazim angle
            #--------------------------------------------------------------
            if DBinputs['loc'].lower() == 'mlo':
                Sazm  = float(specDBinputs['SAzm'][ind])
                if Sazm <= 180:  QuadSen   = np.array(fltrdData['W_Radiance'])
                else:            QuadSen   = np.array(fltrdData['W_Radiance'])         
            else:                QuadSen   = np.array(fltrdData['Quad_Sens'])         
            
            avgTemp   = np.mean(HouseTemp[HouseTemp > -50 ])
            avgPres   = np.mean(HousePres[HousePres >= 0   ])
            avgRH     = np.mean(HouseRH[HouseRH     >= 0   ])
            avgSS     = np.mean(SolarSen[SolarSen   >= 0   ])
            avgQS     = np.mean(QuadSen[QuadSen     >= 0   ])
            avgDIT    = np.mean(DetIntT[DetIntT     >= 0   ])
            
            if np.isnan(avgTemp): avgTemp = '-9999'     
            else: avgTemp = str(round(avgTemp,2))
            if np.isnan(avgPres): avgPres = '-9999'
            else: avgPres = str(round(avgPres,2))
            if np.isnan(avgRH):   avgRH   = '-99'
            else: avgRH = str(round(avgRH,2)) 
            if np.isnan(avgSS):   avgSS   = '-9999'
            else: avgSS = str(round(avgSS,2))
            if np.isnan(avgQS):   avgQS   = '-9999'
            else: avgQS = str(round(avgQS,2))
            if np.isnan(avgDIT):   avgDIT   = '-9999'
            else: avgDIT = str(round(avgDIT,2))
                    
            # Assign averages to main dictionary
            specDBinputs.setdefault('HouseTemp',[]).append(avgTemp)
            specDBinputs.setdefault('HousePres',[]).append(avgPres)
            specDBinputs.setdefault('HouseRH',[]).append(avgRH)   
            specDBinputs.setdefault('Ext_Solar_Sens',[]).append(avgSS)   
            specDBinputs.setdefault('Quad_Sens',[]).append(avgQS)   
            specDBinputs.setdefault('Det_Intern_T_Swtch',[]).append(avgDIT)   
    
        #---------------------------------------
        # If no external station data exists for
        # the year fill with missing values
        #---------------------------------------            
        if not 'statData' in vars():
            specDBinputs.setdefault('ExtStatTemp',[]).append('-9999')
            specDBinputs.setdefault('ExtStatPres',[]).append('-9999')
            specDBinputs.setdefault('ExtStatRH',[]).append('-99')   

        else:
            # Filter external station data dictionary
            fltrdData = filterDict(statData,idate,fdateS)     
            # Find averages
            StatTemp  = np.array(fltrdData['Temp'])
            StatPres  = np.array(fltrdData['Pres'])
            StatRH    = np.array(fltrdData['RH']  )
            avgTemp   = np.mean(StatTemp[StatTemp > -50 ])
            avgPres   = np.mean(StatPres[StatPres > 0   ])
            avgRH     = np.mean(StatRH[StatRH     >= 0   ])
            if np.isnan(avgTemp): avgTemp = '-9999'     
            else: avgTemp = str(round(avgTemp,2))
            if np.isnan(avgPres): avgPres = '-9999'
            else: avgPres = str(round(avgPres,2))
            if np.isnan(avgRH):   avgRH   = '-99'
            else: avgRH = str(round(avgRH,2))        

            # Assign averages to main dictionary
            specDBinputs.setdefault('ExtStatTemp',[]).append(avgTemp)
            specDBinputs.setdefault('ExtStatPres',[]).append(avgPres)
            specDBinputs.setdefault('ExtStatRH',[]).append(avgRH)   
                        
    #-----------------------------------
    # Write new data to spectral DB file
    #-----------------------------------
    # Append spectral DB file header with new house and external station data variables
    DBfieldNames.extend(['HouseTemp','HousePres','HouseRH','ExtStatTemp','ExtStatPres','ExtStatRH','Ext_Solar_Sens','Quad_Sens','Det_Intern_T_Swtch'])
    
    # Sort specDBinputs based on DateTime key
    specDBinputs = sortDict(specDBinputs,'DateTime')
    
    # Remove DateTime key and values for writing to spectral database file
    del specDBinputs['DateTime']
    
    # Seperate out file name from path/filename in 'Filename' field
    specDBinputs['Filename'] = [os.path.split(fname)[1] for fname in specDBinputs['Filename']]

    # Create an order of keys to write spectral db file
    order = {DBfieldNames[i]:i for i in range(len(DBfieldNames))}
    
    #----------------------------------
    # Create human easily readable file
    # This assumes that you know in 
    # advanced the number of columns
    #----------------------------------
    if DBinputs['readableFlg']:
        with open(DBinputs['readableSpecDBFile'], 'wb') as fopen:
            #strformat = '{0:<15} {1:<10} {2:<10} {3:<10} {4:<10} {5:<10} {6:<10} {7:<10} {8:<10} {9:<10} {10:<10} {11:<10} {12:<10} {13:<10} {14:<10} {15:<10} '+\
            #            '{16:<10} {17:<10} {18:<10} {19:<10} {20:<5} {21:<13} {22:<13} {23:<10} {24:<10} {25:<10} {26:<10} {27:<10} {28:<10} {29:<10} {30:<15} {31:<15} {32:<15} \n'      
            strformat = ['{0:<15}'] + [' {'+str(i)+':<12}' for i in range(1,len(DBfieldNames))]
            strformat = ''.join(strformat).lstrip().rstrip() + '\n'
            
            fopen.write(strformat.format(*[k for k in sorted(specDBinputs,key=order.get)]))
            for row in zip(*[specDBinputs[k] for k in sorted(specDBinputs, key=order.get)]):
                fopen.write(strformat.format(*row))
            #fopen.writelines(strformat.format(zip([specDBinputs[k] for k in sorted(specDBinputs, key=order.get)])))
               
    # Create csv file
    if DBinputs['csvFlg']:
        with open(DBinputs['csvSpecDBFile'], 'wb') as fopen:
            writer = csv.writer(fopen, delimiter=',',lineterminator='\n')
            writer.writerow([k for k in sorted(specDBinputs,key=order.get)])                       # Write header to file
            writer.writerows(zip(*(specDBinputs[k] for k in sorted(specDBinputs, key=order.get)))) # Write data to file
                                                                              
if __name__ == "__main__":
    main(sys.argv[1:])