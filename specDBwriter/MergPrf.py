#! /usr/local/python-2.7/bin/python

#----------------------------------------------------------------------------------------
# Name:
#      MergPrf.py
#
# Purpose:
#      This program creates zpt and water profile based on NCEP nmc and WACCM data. 
#           
#
# Input files:
#       1) NCEP nmc daily values
#       2) WACCM monthly means
#
# Output files:
#       1) 
#
# Called Functions:
#       1) No external called functions (other than system functions)
#
#
# Notes:
#       1) The altitude grid is taken from WACCM monthly mean file.
#
#
# Usage:
#     MergPrf.py -i <File> -l
#              -i           Input file for MergPrf.py
#
# Examples:
#    ./MergPrf.py -i /home/data/mergprfInput.py          -- This runs the program with the input file mergprfInput.py
#
# Version History:
#  1.0     Created, Sept, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
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
import logging
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline as intrpUniSpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

                        #-------------------------------------#
                        # Define helper functions and classes #
                        #-------------------------------------#
            
                                                     
def usage():
    ''' Prints to screen standard program usage'''
    print 'NCEPnmcFormat.py -i <File>'

        
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
                
def segmnt(seq,n):
    '''Yeilds successive n-sized segments from seq'''
    for i in xrange(0,len(seq),n):
        yield seq[i:i+n]

                            #----------------------------#
                            #                            #
                            #        --- Main---         #
                            #                            #
                            #----------------------------#

def main(argv):
    
    #------------------
    # Set default flags
    #------------------
    logFile  = False    
    
    #---------------------------------
    # Retrieve command line arguments 
    #---------------------------------
    #------------------------------------------------------------------------------------------------------------#                                             
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:l')

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
            
        # Option for Log File
        elif opt == '-l':
            logFile = True        
            
        #------------------
        # Unhandled options
        #------------------
        else:
            print 'Unhandled option: ' + opt
            usage()
            sys.exit()
    #------------------------------------------------------------------------------------------------------------#                                
       
    #---------------------------------------
    # Hard coded NCEP pressure values [mbar]
    #---------------------------------------
    nmcPress = np.array([0.4,1.0,2.0,5.0,10.0,30.0,50.0,70.0,100.0,150.0,200.0,250.0,300.0,400.0,500.0,700.0,850.0,1000.0])
       
    #----------------
    # Read input file
    #----------------
    inputs = {}
    execfile(inputFile, inputs)
    if '__builtins__' in inputs:
        del inputs['__builtins__']       
        
    #-----------------------------------
    # Check the existance of directories
    # and files given in input file
    #-----------------------------------
    # Check directory of NCEP nmc data                         
    if not ckDir(inputs['NCEPDir']):
        print 'NCEP nmc directory does not exist: ' + inputs['NCEPDir']
        sys.exit()
        
    # check if '/' is included at end of path
    if not( inputs['NCEPDir'].endswith('/') ):
        inputs['NCEPDir'] = inputs['NCEPDir'] + '/'   
        
    # Check directory for output                         
    if not ckDir(inputs['outBaseDir']):
        print 'Output base directory does not exist: ' + inputs['outBaseDir']
        sys.exit()
        
    # check if '/' is included at end of path
    if not( inputs['outBaseDir'].endswith('/') ):
        inputs['outBaseDir'] = inputs['outBaseDir'] + '/'       

    # Check for station layer file if doing interpolation 
    ckFile(inputs['WACCMfile'],True)
    
    #--------------------
    # Initialize log file
    #--------------------
    if logFile:   
        logFile = logging.getLogger('1')
        logFile.setLevel(logging.INFO)
        hdlr1   = logging.FileHandler(inputs['outBaseDir'] + 'MissingNMCzpt.log',mode='w')
        fmt1    = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s','%a, %d %b %Y %H:%M:%S')
        hdlr1.setFormatter(fmt1)
        logFile.addHandler(hdlr1)  
        logFile.info('**************** Starting Logging ***********************')
        logFile.info('Start year, month, day: {:4}, {:02}, {:02}'.format(inputs['iyear'],inputs['imnth'],inputs['iday'] ) )
        logFile.info('End year, month, day:   {:4}, {:02}, {:02}'.format(inputs['fyear'],inputs['fmnth'],inputs['fday'] ) )
        logFile.info('Station location:       ' + inputs['loc'])       
    
    #-------------------
    # Call to date class
    #-------------------
    DOI      = dr.DateRange(inputs['iyear'],inputs['imnth'],inputs['iday'],         # Create a dateRange instance object
                            inputs['fyear'],inputs['fmnth'],inputs['fday'])      
    daysList = DOI.dateList                                                         # Create a list of days within date range    
       
    #----------------------------------
    # Initialize missing count based on 
    # how many years present
    #----------------------------------
    years = DOI.yearList()
    misngCnt = {}
    for y in years: misngCnt.setdefault(y,0)
    
    #--------------------------------------------------------------------
    # Read WACCM monthly mean data. WACCM monthly mean file is ascending,
    # adjust so that it is descending. Also units are in km.
    #--------------------------------------------------------------------
    with open(inputs['WACCMfile'], 'r') as fopen:
        lines = fopen.readlines()
        
    nlyrs = int(lines[0].strip().split()[0])
    s_ind  = 3
    Z      = np.flipud( np.array( [ float(row.strip().split()[0]) for row in lines[s_ind:nlyrs+s_ind] ] ) )
    waccmT = np.flipud( np.array( [ [float(x) for x in line.strip().split()[1:]] for line in lines[s_ind:nlyrs+s_ind] ] ) )
    s_ind  = 3 + nlyrs + 2
    waccmP = np.flipud( np.array( [ [float(x) for x in line.strip().split()[1:]] for line in lines[s_ind:nlyrs+s_ind] ] ) )
    s_ind  = 3 + nlyrs + 2 + nlyrs + 2
    waccmW = np.flipud( np.array( [ [float(x) for x in line.strip().split()[1:]] for line in lines[s_ind:nlyrs+s_ind] ] ) )
    
    #----------------------
    # Loop through day list
    #----------------------
    for i,snglDay in enumerate(daysList):       
        waccmFlg = False
        
        #------------------------------------
        # Open and read yearly NCEP nmc files
        #------------------------------------
        if (i == 0 or (snglDay.year != daysList[i-1].year) ):
            NMChgtFname  = inputs['NCEPDir'] + 'HgtNMC_' +  inputs['loc'].lower() + '_' + str(snglDay.year) + '.dat'
            NMCTempFname = inputs['NCEPDir'] + 'TempNMC_' + inputs['loc'].lower() + '_' + str(snglDay.year) + '.dat'

            #-------------------------------------
            # NCEP nmc height data along with date
            # Convert [m] => [km]
            #-------------------------------------
            with open(NMChgtFname, 'r') as fopen:
                lines = fopen.readlines()
                
            nmcDate    = np.array([dt.date(int(line.strip().split()[0][0:4]),
                                           int(line.strip().split()[0][4:6]),
                                           int(line.strip().split()[0][6:])) for line in lines if not('#' in line)])
            nmcHgtData = np.array( [ [float(x) for x in line.strip().split()[1:]] for line in lines if not('#' in line) ] )
            nmcHgtData[:] = nmcHgtData / 1000.0   # Convert [m] => [km]
            
            #--------------------------------
            # NCEP nmc Temperature data along 
            #--------------------------------
            with open(NMCTempFname, 'r') as fopen:
                lines = fopen.readlines()
            
            nmcTempData = np.array( [ [float(x) for x in line.strip().split()[1:]] for line in lines if not('#' in line) ] )
                        
        #--------------------------------------------------
        # Merge Pressure, Temperatuer, and H2O data
        # from WACCM and NCEP nmc. 
        # Note: NCEP nmc has some missing values (-999.999)
        # Must provide one empty data point between WACCM
        # and NCEP nmc for interpolation
        #--------------------------------------------------        
        #--------------------------------
        # Get NCEP nmc and WACCM profiles
        # according to date
        #--------------------------------
        dateInd = np.where(nmcDate == snglDay)[0][0]
        mnthInd = snglDay.month      
        
        #-------------------------------------
        # If date is entirely missing from nmc
        # use WACCM
        #-------------------------------------
        if not(dateInd):
            misngCnt[snglDay.year] += 1
            PressOut = waccmP[:,mnthInd]
            TempOut  = waccmT[:,mnthInd]     
            waccmFlg = True
        
        else:            
            # NCEP nmc
            tmpNMCPres   = nmcPress
            heightNMCprf = nmcHgtData[dateInd,:]
            tempNMCprf   = nmcTempData[dateInd,:]
            
            #-----------------------------------------
            # Look for missing values in NCEP nmc data
            # If only one missing value...remove, 
            # otherwise use WACCM data. Count number
            # of times per year WACCM is used
            #-----------------------------------------
            misHgt = np.where(heightNMCprf < -900)[0]
            misT   = np.where(tempNMCprf   < -900)[0]
            misAll = np.union1d( misHgt, misT )
          
            #---------------------------------------------
            # If union of missing temperatures and heights
            # is greater than 2 then use WACCM
            #---------------------------------------------
            if len( misAll ) > 2:
                misngCnt[snglDay.year] += 1
                PressOut = waccmP[:,mnthInd]
                TempOut  = waccmT[:,mnthInd]
                waccmFlg = True
            
            #-----------------------------------------------------------
            # If only two or none values missing, remove and interpolate
            #-----------------------------------------------------------
            else:
                tmpNMCPres[:]   = np.delete(tmpNMCPres,  misAll)
                heightNMCprf[:] = np.delete(heightNMCprf,misAll)       
                     
                #----------------------------------------------------
                # Construct Height/Pressure profile for interpolation
                #----------------------------------------------------
                # Find top of NMC data
                nmcTop = heightNMCprf[0]
                
                # Where top of NMC fits in WACCM grid
                topInd = np.argmin( abs( Z - heightNMCprf[0] ) )
    
                # Take two points above top and concatonate 
                heightIn = np.concatenate( (Z[0:(topInd-inputs['npntSkip'])]             ,heightNMCprf), axis=1 )
                pressIn  = np.concatenate( (waccmP[0:(topInd-inputs['npntSkip']),mnthInd],nmcPress)    , axis=1 )
                tempIn   = np.concatenate( (waccmT[0:(topInd-inputs['npntSkip']),mnthInd],tempNMCprf)  , axis=1 )
                
                #------------------------------------------------------------------
                # Interpolate to grid. X data must be increasing => flip dimensions
                # and then flip back
                #------------------------------------------------------------------
                PressOut = np.flipud( intrpUniSpl( np.flipud(heightIn), np.flipud(pressIn), k=inputs['Pintrp'] )( np.flipud(Z) ) )
                TempOut  = np.flipud( intrpUniSpl( np.flipud(heightIn), np.flipud(tempIn),  k=inputs['Tintrp'] )( np.flipud(Z) ) )

        #--------------------------------------
        # Write to log if NCEP data is not used
        #--------------------------------------
        if waccmFlg and logFile: logFile.error('NCEP nmc data not complete, WACCM profiles used for date: ' + str(snglDay) )    
            
        #-------------------
        # Write output files
        #-------------------
        mnthstr = "{0:02d}".format(snglDay.month)
        yearstr = "{0:02d}".format(snglDay.year)
        daystr  = "{0:02d}".format(snglDay.day)        
        outDir  = inputs['outBaseDir'] + yearstr+mnthstr+daystr + '/'
         
        #-------------------
        # Write out ZPT file
        #-------------------
        with open(outDir+'ZPT.nmc.120', 'w') as fopen:
            fopen.write("{0:>5}{1:>5} \n".format(1,nlyrs))
            
            # Write altitude
            fopen.write("     ALTITUDE [km] \n")
            for row in segmnt(Z, 5):
                strformat = ','.join('{:>12.4f}' for i in row) + ', \n'
                fopen.write(strformat.format(*row))
            
            # Write Pressure
            if waccmFlg: fopen.write("     PRESSURE from WACCM V5 monthly mean [mbar] \n")
            else:        fopen.write("     PRESSURE from interpolated NCEP nmc (up to {:5.2f}km) and WACCM V5 monthly mean [mbar] \n".format(nmcTop))
            for row in segmnt(PressOut,5):
                strformat = ','.join('{:>12.4E}' for i in row) + ', \n'
                fopen.write(strformat.format(*row))                
                                                                              
            # Write Temperature
            if waccmFlg: fopen.write("     TEMPERATURE from WACCM V5 monthly mean [C] \n")
            else:        fopen.write("     TEMPERATURE from interpolated NCEP nmc (up to {:5.2f}km) and WACCM V5 monthly mean [C] \n".format(nmcTop))
            for row in segmnt(TempOut,5):
                strformat = ','.join('{:>12.4f}' for i in row) + ', \n'
                fopen.write(strformat.format(*row))       
                           
        #---------------------
        # Write out water file
        #---------------------                
        with open(outDir+'w-120.v1','w') as fopen:
            fopen.write('    1     H2O from WACCM V5 monthly mean \n')
            for row in segmnt(waccmW[:,mnthInd],5):
                strformat = ','.join('{:>12.4f}' for i in row) + ', \n'
                fopen.write(strformat.format(*row))              
            
        #--------------------
        # Create plots to pdf
        #--------------------
        if not waccmFlg:
            # Pressure
            plt.plot(PressOut,Z,'rx-', label='Interpolated Pressure')
            plt.plot(waccmP[:,mnthInd],Z,'bx-',label='WACCM V5 Pressure')
            plt.plot(tmpNMCPres,heightNMCprf,'kx-',label='NCEP nmc Pressure')
            plt.legend()
            plt.xlabel('Pressure [mbar]')
            plt.ylabel('log(Height) [km]')
            plt.xscale('log')
            #plt.yscale('log')
            plt.ylim( Z[-1], Z[0] )
            ax = plt.gca()
            ax.set_title('Pressure vs Height for Date:{}, K = {:2.0f}, nskips = {:2.0f}'.format(str(snglDay),inputs['Pintrp'],inputs['npntSkip']))
            #ax.xaxis.set_major_locator(MultipleLocator(25))
            #ax.xaxis.set_minor_locator(MultipleLocator(5))
            plt.savefig(outDir+'PressureFigure.pdf',bbox_inches='tight')
            plt.close()
            
            # Temperature
            plt.plot(TempOut,Z,'rx-', label='Interpolated Temperature')
            plt.plot(waccmT[:,mnthInd],Z,'bx-',label='WACCM V5 Temperature')
            plt.plot(tempNMCprf,heightNMCprf,'kx-',label='NCEP nmc Temperature')
            plt.legend()
            plt.xlabel('Temperature [C]')
            plt.ylabel('Height [km]')
            #plt.yscale('log')
            plt.ylim( Z[-1], Z[0] )
            ax = plt.gca()
            ax.xaxis.set_major_locator(MultipleLocator(25))
            ax.xaxis.set_minor_locator(MultipleLocator(5))    
            ax.set_title('Temperature vs Height for Date:{}, K = {:2.0f}, nskips = {:2.0f}'.format(str(snglDay),inputs['Tintrp'],inputs['npntSkip']))
            plt.savefig(outDir+'TemperatureFigure.pdf',bbox_inches='tight')
            plt.close()
                   
    #-------------------------------------
    # Print out number of days where NCEP
    # nmc data is incomplete => WACCM used
    #-------------------------------------
    if logFile:
            for yrs in misngCnt:
                logFile.info('Missing days for year ({:4}) = {:4}'.format(yrs,misngCnt[yrs]))
                
            
                                                                              
if __name__ == "__main__":
    main(sys.argv[1:])
    
    
    
#**************************************************************************************    
# OLD CODE.... MAYBE USE LATER....
#if (len(misHgt) == 1) or (misHgt[0] == 0 and ( sum( misHgt - range(0,len(misHgt)) ) ) ):
#
# If more than one missing value and is sandwiched between
# values then remove values and create two profiles:
# 1) Profile based only on WACCM data
# 2) Profile where missing NMC is filled with WACCM
#elif (len(misHgt) != 0):    
#    
#     If all values are missing, only use WACCM data
#    if ( len(misHgt) == len(heightNMCprf) ): misAllFlg = True
#    else:
#        upprHgt = heightNMCprf[misHgt[0]-1]
#        if misHgt[-1] == (len(heightNMCprf)-1): lwrHgt  = heightNMCprf[misHgt[-1]]
#        else:                                   lwrHgt  = heightNMCprf[misHgt[-1]-1]
#        
#        tmpNMCPres[:]   = np.delete(tmpNMCPres,  misHgt)
#        heightNMCprf[:] = np.delete(heightNMCprf,misHgt)    
#        misFlg = True
#**************************************************************************************    