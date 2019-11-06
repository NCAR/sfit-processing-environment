#----------------------------------------------------------------------------------------
# Name:
#        HouseReaderC.py
#
# Purpose:
#       This is a collection of classes and functions used in layer 1 processing of sfit4
#
#
# External Subprocess Calls:
#	Only python internal modules called		
#
#
#
# Notes:
#       1) The majority of these classes are related to different types of input files:
#            -- Ctl file
#	     -- Spectral DB file		
#            -- Layer 1 input file
#
#
# Version History:
#       Created, May, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
#
#
# References:
#
#----------------------------------------------------------------------------------------

import datetime as dt
import re
import csv
from itertools import islice
import sys
import subprocess  
import numpy as np
import time
from scipy import interpolate
from scipy.interpolate import interp1d

def tryopen(fname):
    ''' Try to open a file and read contents'''
    try:
        with open(fname, 'r' ) as fopen:
            return fopen.readlines()
    except IOError as errmsg:
        print (errmsg)
        return False

def toYearFraction(dates):
    ''' Convert datetime to year and fraction of year'''

    #def sinceEpoch(date): # returns seconds since epoch
        #return time.mktime(date.timetuple())
    #s = sinceEpoch
    ep_fnc = lambda x: time.mktime(x.timetuple())
    
    retrnDates = np.zeros(len(dates))
    
    for i,sngDate in enumerate(dates):
        year = sngDate.year
        startOfThisYear = dt.datetime(year=year, month=1, day=1)
        startOfNextYear = dt.datetime(year=year+1, month=1, day=1)
    
        yearElapsed = ep_fnc(sngDate) - ep_fnc(startOfThisYear)
        yearDuration = ep_fnc(startOfNextYear) - ep_fnc(startOfThisYear)
        fraction = yearElapsed/yearDuration
        retrnDates[i] = sngDate.year + fraction


    return retrnDates




class MLOread():
    '''  Class for reading MLO house data  '''    
    def __init__(self):
        ''' Initializations '''
        #-------------------------------------
        # initialize dictionary for house data
        #-------------------------------------
        self.data = {'DateTime':[],                         # Internallly used for sorting entries
                     'Date':[],                             # 
                     'Time':[],
                     'LN2_Dewar_P_volt':[],
                     'LN2_Dewar_P_psi':[],
                     'Optic_Bench_Baseplate_T':[],
                     'Beamsplitter_T':[],
                     'Front_T':[],
                     'InSb_T':[],
                     'MCT_T':[],
                     'Laser_T':[],
                     'Outside_T':[],
                     'Brucker_Optical_RH':[],
                     'Outside_RH':[],
                     'Wind_Speed_volt':[],
                     'Wind_Speed_mph':[],
                     'WindDir_volt':[],
                     'WindDir_E_of_N':[],
                     'Mid_IR_Cooler':[],
                     'LN2_Fill':[],
                     'Hatch_Relay':[],
                     'Solar_Seeker_ON_Relay':[],
                     'Solar_Seeker_OFF_Relay':[],
                     'Dyn_Mirror_Pwr':[],
                     '28V_Solar_Seeker_Pwr':[],
                     'DEC_A_Plug_Strip':[],
                     'Hatch_Position_bit':[],
                     'Hatch_Position_volt':[],
                     'UTC_offset':[],
                     'DOY':[],
                     'E_Radiance':[],
                     'W_Radiance':[],
                     'Atm_Press':[]}
        
            
    def formatA(self,fileName,year,month,day):
        ''' '''
        #------------------------
        # Open file and read data
        #------------------------
        data = tryopen(fileName)

        if data:
            
            #--------------------
            # Remove white spaces
            #--------------------
            data[:] = [ row.strip().split(',') for row in data ]              
        
            #---------------------------------
            # Determine number of observations
            #---------------------------------
            npoints = len(data)
            
            #-------------------
            # Create a list time
            #-------------------
            times = [row[0].split()[0] for row in data]

            #------------------------------------------------
            # Create DateTime entry in Dictionary for sorting
            #------------------------------------------------
            try:
                self.data['DateTime'].extend([dt.datetime(year,month,day,int(time[0:2]),int(time[3:5]),int(time[6:8])) for time in times])
                  
                #--------------------------------
                # Find year month and day strings
                #--------------------------------
                yrstr   = "{0:02d}".format(year)
                mnthstr = "{0:02d}".format(month)
                daystr  = "{0:02d}".format(day)  
                
                #------------------
                # Update dictionary
                #------------------
                self.data['Date'].extend([yrstr+mnthstr+daystr]*npoints)            
                self.data['Time'].extend(times)            
                self.data['LN2_Dewar_P_volt'].extend([-9999]*npoints)   
                self.data['LN2_Dewar_P_psi'].extend([-9999]*npoints)   
                self.data['Optic_Bench_Baseplate_T'].extend([-9999]*npoints)   
                self.data['Beamsplitter_T'].extend([row[12] for row in data])   
                self.data['Front_T'].extend([row[13] for row in data])   
                self.data['InSb_T'].extend([row[10] for row in data])   
                self.data['MCT_T'].extend([row[11] for row in data])   
                self.data['Laser_T'].extend([row[18] for row in data])   
                self.data['Outside_T'].extend([row[19] for row in data])              
                self.data['Brucker_Optical_RH'].extend([-9999]*npoints)
                self.data['Outside_RH'].extend([row[20] for row in data])
                self.data['Wind_Speed_volt'].extend([-9999]*npoints)
                self.data['Wind_Speed_mph'].extend([row[22] for row in data])
                self.data['WindDir_volt'].extend([row[17] for row in data])  
                self.data['WindDir_E_of_N'].extend([-9999]*npoints) 
                self.data['Mid_IR_Cooler'].extend([9]*npoints)
                self.data['LN2_Fill'].extend([9]*npoints)
                self.data['Hatch_Relay'].extend([9]*npoints)
                self.data['Solar_Seeker_ON_Relay'].extend([9]*npoints)
                self.data['Solar_Seeker_OFF_Relay'].extend([9]*npoints)
                self.data['Dyn_Mirror_Pwr'].extend([9]*npoints)
                self.data['28V_Solar_Seeker_Pwr'].extend([9]*npoints)
                self.data['DEC_A_Plug_Strip'].extend([9]*npoints)
                self.data['Hatch_Position_bit'].extend([9]*npoints)
                self.data['Hatch_Position_volt'].extend([row[23] for row in data])
                self.data['UTC_offset'].extend([-99]*npoints)
                self.data['DOY'].extend([-999]*npoints)
                self.data['E_Radiance'].extend([row[15] for row in data])
                self.data['W_Radiance'].extend([row[16] for row in data])
                self.data['Atm_Press'].extend([-9999]*npoints)

            except:
                print ('Error in reading file: %s' % fileName)
                pass
                #sys.exit() 
        
        
            
    def formatB(self,fileName,year,month,day):
        ''' '''
        #------------------------
        # Open file and read data
        #------------------------
        data = tryopen(fileName)

        if data:       

            #--------------------------
            # Remove header information 
            #--------------------------
            data[:] = [ row.strip().split() for row in data if len(row.strip().split()) == 28 and not 'ADC.VLU' in row ]
                                   
            #---------------------------------
            # Determine number of observations
            #---------------------------------
            npoints = len(data)
                   
            #------------------------------------------------
            # Create DateTime entry in Dictionary for sorting
            #------------------------------------------------
            self.data['DateTime'].extend([dt.datetime(year,month,day,int(time[0][0:2]),int(time[0][3:5]),int(time[0][6:8])) for time in data])
            
            #--------------------------------
            # Find year month and day strings
            #--------------------------------
            yrstr   = "{0:02d}".format(year)
            mnthstr = "{0:02d}".format(month)
            daystr  = "{0:02d}".format(day)  
            
            #------------------
            # Update dictionary
            #------------------
            self.data['Date'].extend([yrstr+mnthstr+daystr]*npoints)            
            self.data['Time'].extend([row[0] for row in data])            
            self.data['LN2_Dewar_P_volt'].extend([row[2] for row in data])   
            self.data['LN2_Dewar_P_psi'].extend([-9999]*npoints)   
            self.data['Optic_Bench_Baseplate_T'].extend([-9999]*npoints)   
            self.data['Beamsplitter_T'].extend([row[14] for row in data])   
            self.data['Front_T'].extend([row[15] for row in data])   
            self.data['InSb_T'].extend([row[12] for row in data])   
            self.data['MCT_T'].extend([row[13] for row in data])   
            self.data['Laser_T'].extend([row[21] for row in data])   
            self.data['Outside_T'].extend([row[22] for row in data])              
            self.data['Brucker_Optical_RH'].extend([row[17] for row in data])
            self.data['Outside_RH'].extend([row[22] for row in data])
            self.data['Wind_Speed_volt'].extend([row[25] for row in data])
            self.data['Wind_Speed_mph'].extend([-9999]*npoints)
            self.data['WindDir_volt'].extend([row[19] for row in data])  
            self.data['WindDir_E_of_N'].extend([-9999]*npoints) 
            self.data['Mid_IR_Cooler'].extend([9]*npoints)
            self.data['LN2_Fill'].extend([9]*npoints)
            self.data['Hatch_Relay'].extend([9]*npoints)
            self.data['Solar_Seeker_ON_Relay'].extend([9]*npoints)
            self.data['Solar_Seeker_OFF_Relay'].extend([9]*npoints)
            self.data['Dyn_Mirror_Pwr'].extend([9]*npoints)
            self.data['28V_Solar_Seeker_Pwr'].extend([9]*npoints)
            self.data['DEC_A_Plug_Strip'].extend([9]*npoints)
            self.data['Hatch_Position_bit'].extend([9]*npoints)
            self.data['Hatch_Position_volt'].extend([row[25] for row in data])
            self.data['UTC_offset'].extend([-99]*npoints)
            self.data['DOY'].extend([-999]*npoints)
            self.data['E_Radiance'].extend([row[17] for row in data])
            self.data['W_Radiance'].extend([row[18] for row in data])
            self.data['Atm_Press'].extend([-9999]*npoints)
            
    def formatC(self,fileName,year,month,day):
        ''' '''
        #------------------------
        # Open file and read data
        #------------------------        
        data = tryopen(fileName)

        if data:

            #--------------------------
            # Remove header information 
            #--------------------------
            data[:] = [ row.strip().split() for row in data if len(row.strip().split()) == 28 ]
                                   
            #---------------------------------
            # Determine number of observations
            #---------------------------------
            npoints = len(data)
                   
            #------------------------------------------------
            # Create DateTime entry in Dictionary for sorting
            #------------------------------------------------
            self.data['DateTime'].extend([dt.datetime(year,month,day,int(time[0][0:2]),int(time[0][3:5]),int(time[0][6:8])) for time in data])
            
            #--------------------------------
            # Find year month and day strings
            #--------------------------------
            yrstr   = "{0:02d}".format(year)
            mnthstr = "{0:02d}".format(month)
            daystr  = "{0:02d}".format(day)  
            
            #------------------
            # Update dictionary
            #------------------
            self.data['Date'].extend([yrstr+mnthstr+daystr]*npoints)            
            self.data['Time'].extend([row[0] for row in data])       
            
            #---------------------------------------------------
            # LN2 Dewar pressure changes units volts <= 20090820
            # psi >= 20090901
            #---------------------------------------------------
            if dt.date(year,month,day) <= dt.date(2009,8,20):
                self.data['LN2_Dewar_P_volt'].extend([row[2] for row in data])   
                self.data['LN2_Dewar_P_psi'].extend([-9999]*npoints)   
            else:
                self.data['LN2_Dewar_P_volt'].extend([-9999]*npoints)  
                self.data['LN2_Dewar_P_psi'].extend([row[2] for row in data])          
           
            self.data['Optic_Bench_Baseplate_T'].extend([-9999]*npoints)   
            self.data['Beamsplitter_T'].extend([row[14] for row in data])   
            self.data['Front_T'].extend([row[15] for row in data])   
            self.data['InSb_T'].extend([row[12] for row in data])   
            self.data['MCT_T'].extend([row[13] for row in data])   
            self.data['Laser_T'].extend([row[21] for row in data])   
            self.data['Outside_T'].extend([row[22] for row in data])              
            self.data['Brucker_Optical_RH'].extend([row[17] for row in data])
            self.data['Outside_RH'].extend([row[22] for row in data])
            self.data['Wind_Speed_volt'].extend([row[25] for row in data])
            self.data['Wind_Speed_mph'].extend([-9999]*npoints)
            self.data['WindDir_volt'].extend([row[19] for row in data])  
            self.data['WindDir_E_of_N'].extend([-9999]*npoints) 
            self.data['Mid_IR_Cooler'].extend([9]*npoints)
            self.data['LN2_Fill'].extend([9]*npoints)
            self.data['Hatch_Relay'].extend([9]*npoints)
            self.data['Solar_Seeker_ON_Relay'].extend([9]*npoints)
            self.data['Solar_Seeker_OFF_Relay'].extend([9]*npoints)
            self.data['Dyn_Mirror_Pwr'].extend([9]*npoints)
            self.data['28V_Solar_Seeker_Pwr'].extend([9]*npoints)
            self.data['DEC_A_Plug_Strip'].extend([9]*npoints)
            self.data['Hatch_Position_bit'].extend([9]*npoints)
            self.data['Hatch_Position_volt'].extend([-9999]*npoints)
            self.data['UTC_offset'].extend([-99]*npoints)
            self.data['DOY'].extend([-999]*npoints)
            self.data['E_Radiance'].extend([row[17] for row in data])
            self.data['W_Radiance'].extend([row[18] for row in data])
            self.data['Atm_Press'].extend([-9999]*npoints)
            
            
    def formatD(self,fileName,year,month,day):
        ''' '''
        #------------------------
        # Open file and read data
        #------------------------        
        data = tryopen(fileName)

      
        if data:                
                
            #--------------------------
            # Remove header information 
            #--------------------------
            data[:] = [ row.strip().split() for row in data if not '#' in row and len(row.strip().split()) >= 30 ]

                                   
            #---------------------------------
            # Determine number of observations
            #---------------------------------
            npoints = len(data)
                   
            #------------------------------------------------
            # Create DateTime entry in Dictionary for sorting
            #------------------------------------------------
            try:
                self.data['DateTime'].extend([dt.datetime(int(time[0][0:4]),int(time[0][4:6]),int(time[0][6:8]),\
                                                          int(time[1][0:2]),int(time[1][3:5]),int(time[1][6:8])) for time in data])            
                
                #------------------
                # Update dictionary
                #------------------
                self.data['Date'].extend([row[0] for row in data])            
                self.data['Time'].extend([row[1] for row in data])            
                self.data['LN2_Dewar_P_volt'].extend([-9999]*npoints)   
                self.data['LN2_Dewar_P_psi'].extend([row[2] for row in data])   
                self.data['Optic_Bench_Baseplate_T'].extend([row[3] for row in data])   
                self.data['Beamsplitter_T'].extend([row[4] for row in data])   
                self.data['Front_T'].extend([-9999]*npoints)   
                self.data['InSb_T'].extend([row[5] for row in data])   
                self.data['MCT_T'].extend([row[6] for row in data])   
                self.data['Laser_T'].extend([row[16] for row in data])   
                self.data['Outside_T'].extend([row[17] for row in data])              
                self.data['Brucker_Optical_RH'].extend([row[7] for row in data])
                self.data['Outside_RH'].extend([row[12] for row in data])
                self.data['Wind_Speed_volt'].extend([-9999]*npoints)
                self.data['Wind_Speed_mph'].extend([row[14] for row in data])
                self.data['WindDir_volt'].extend([-9999]*npoints)  
                self.data['WindDir_E_of_N'].extend([row[15] for row in data]) 
                self.data['Mid_IR_Cooler'].extend([row[19][1] for row in data])
                self.data['LN2_Fill'].extend([row[19][2] for row in data])
                self.data['Hatch_Relay'].extend([row[20][2] for row in data])
                self.data['Solar_Seeker_ON_Relay'].extend([row[21][0] for row in data])
                self.data['Solar_Seeker_OFF_Relay'].extend([row[21][1] for row in data])
                self.data['Dyn_Mirror_Pwr'].extend([row[21][2] for row in data])
                self.data['28V_Solar_Seeker_Pwr'].extend([row[22][2] for row in data])
                self.data['DEC_A_Plug_Strip'].extend([row[21][3] for row in data])
                self.data['Hatch_Position_bit'].extend([row[22][0] for row in data])
                self.data['Hatch_Position_volt'].extend([-999]*npoints)
                self.data['UTC_offset'].extend([row[24] for row in data])
                self.data['DOY'].extend([row[25] for row in data])
                self.data['E_Radiance'].extend([row[8] for row in data])
                self.data['W_Radiance'].extend([row[9] for row in data])  
                self.data['Atm_Press'].extend([-9999]*npoints)     

            except:
                print ('Error in reading file: %s' % fileName)
                pass
                #sys.exit()


    def formatE(self,fileName,year,month,day):
        ''' '''       
        #------------------------
        # Open file and read data
        #------------------------        
        data = tryopen(fileName)
                
        #--------------------------
        # Remove header information 
        #--------------------------
        data[:] = [ row.strip().split() for row in data if not '#' in row and len(row.strip().split()) == 42 ]
                               
        #---------------------------------
        # Determine number of observations
        #---------------------------------
        npoints = len(data)
               
        #------------------------------------------------
        # Create DateTime entry in Dictionary for sorting
        #------------------------------------------------
        try:
            self.data['DateTime'].extend([dt.datetime(int(time[0][0:4]),int(time[0][4:6]),int(time[0][6:8]),\
                                                      int(time[1][0:2]),int(time[1][3:5]),int(time[1][6:8])) for time in data])
        except:
            print ('Error in reading file: %s' % fileName)
            sys.exit()            
            
        #------------------
        # Update dictionary
        #------------------
        self.data['Date'].extend([row[0] for row in data])            
        self.data['Time'].extend([row[1] for row in data])            
        self.data['LN2_Dewar_P_volt'].extend([-9999]*npoints)   
        self.data['LN2_Dewar_P_psi'].extend([row[2] for row in data])   
        self.data['Optic_Bench_Baseplate_T'].extend([row[3] for row in data])   
        self.data['Beamsplitter_T'].extend([row[4] for row in data])   
        self.data['Front_T'].extend([-9999]*npoints)   
        self.data['InSb_T'].extend([row[5] for row in data])   
        self.data['MCT_T'].extend([row[6] for row in data])   
        self.data['Laser_T'].extend([row[16] for row in data])   
        self.data['Outside_T'].extend([row[17] for row in data])              
        self.data['Brucker_Optical_RH'].extend([row[7] for row in data])
        self.data['Outside_RH'].extend([row[12] for row in data])
        self.data['Wind_Speed_volt'].extend([-9999]*npoints)
        self.data['Wind_Speed_mph'].extend([row[14] for row in data])
        self.data['WindDir_volt'].extend([-9999]*npoints)  
        self.data['WindDir_E_of_N'].extend([row[15] for row in data]) 
        self.data['Mid_IR_Cooler'].extend([row[19][1] for row in data])
        self.data['LN2_Fill'].extend([row[19][2] for row in data])
        self.data['Hatch_Relay'].extend([row[20][2] for row in data])
        self.data['Solar_Seeker_ON_Relay'].extend([row[21][0] for row in data])
        self.data['Solar_Seeker_OFF_Relay'].extend([row[21][1] for row in data])
        self.data['Dyn_Mirror_Pwr'].extend([row[21][2] for row in data])
        self.data['28V_Solar_Seeker_Pwr'].extend([row[22][2] for row in data])
        self.data['DEC_A_Plug_Strip'].extend([row[21][3] for row in data])
        self.data['Hatch_Position_bit'].extend([row[22][0] for row in data])
        self.data['Hatch_Position_volt'].extend([-999]*npoints)
        self.data['UTC_offset'].extend([row[36] for row in data])
        self.data['DOY'].extend([row[37] for row in data])
        self.data['E_Radiance'].extend([row[8] for row in data])
        self.data['W_Radiance'].extend([row[9] for row in data])     
    
    def formatF(self,fileName,fileNameMet,year,month,day):
        ''' '''
        #------------------------
        # Open house file and read data
        #------------------------        
        data = tryopen(fileName)

        if data:

            

           #--------------------------
            # Remove header information 
            #--------------------------
            data[:] = [ row.strip().split() for row in data if not '#' in row and len(row.strip().split()) >= 30 ]

                                   
            #---------------------------------
            # Determine number of observations
            #---------------------------------
            npoints = len(data)
                   
            #------------------------------------------------
            # Create DateTime entry in Dictionary for sorting
            #------------------------------------------------
            try:
                print('House File: {}'.format(fileName))

                self.data['DateTime'].extend([dt.datetime(int(time[0][0:4]),int(time[0][4:6]),int(time[0][6:8]),\
                                                              int(time[1][0:2]),int(time[1][3:5]),int(time[1][6:8])) for time in data])

              

                datehouse  = [dt.datetime(int(time[0][0:4]),int(time[0][4:6]),int(time[0][6:8]),\
                                                              int(time[1][0:2]),int(time[1][3:5]),int(time[1][6:8])) for time in data]   

                doyhouse = toYearFraction(datehouse)         
                
                #------------------
                # Update dictionary
                #------------------
                self.data['Date'].extend([row[0] for row in data])            
                self.data['Time'].extend([row[1] for row in data])            
                self.data['LN2_Dewar_P_volt'].extend([-9999]*npoints)   
                self.data['LN2_Dewar_P_psi'].extend([row[2] for row in data])   
                self.data['Optic_Bench_Baseplate_T'].extend([row[3] for row in data])   
                self.data['Beamsplitter_T'].extend([row[4] for row in data])   
                self.data['Front_T'].extend([-9999]*npoints)   
                self.data['InSb_T'].extend([row[5] for row in data])   
                self.data['MCT_T'].extend([row[6] for row in data])   
                self.data['Laser_T'].extend([row[15] for row in data])   
                #self.data['Outside_T'].extend([row[17] for row in data])              
                self.data['Brucker_Optical_RH'].extend([row[7] for row in data])
                #self.data['Outside_RH'].extend([row[12] for row in data])
                self.data['Wind_Speed_volt'].extend([-9999]*npoints)
                #self.data['Wind_Speed_mph'].extend([row[14] for row in data])
                self.data['WindDir_volt'].extend([-9999]*npoints)  
                #self.data['WindDir_E_of_N'].extend([row[15] for row in data]) 

                self.data['Mid_IR_Cooler'].extend([row[19][1] for row in data])
                self.data['LN2_Fill'].extend([row[19][2] for row in data])
                self.data['Hatch_Relay'].extend([row[20][2] for row in data])
                self.data['Solar_Seeker_ON_Relay'].extend([row[21][0] for row in data])
                self.data['Solar_Seeker_OFF_Relay'].extend([row[21][1] for row in data])
                self.data['Dyn_Mirror_Pwr'].extend([row[21][2] for row in data])
                self.data['28V_Solar_Seeker_Pwr'].extend([row[22][2] for row in data])
                self.data['DEC_A_Plug_Strip'].extend([row[21][3] for row in data])
                self.data['Hatch_Position_bit'].extend([row[22][0] for row in data])


                #self.data['Mid_IR_Cooler'].extend([row[24] for row in data])
                #self.data['LN2_Fill'].extend([row[25] for row in data])
                #self.data['Hatch_Relay'].extend([row[20][2] for row in data])
                #self.data['Solar_Seeker_ON_Relay'].extend([row[31][0] for row in data])
                #self.data['Solar_Seeker_OFF_Relay'].extend([row[32][1] for row in data])
                #self.data['Dyn_Mirror_Pwr'].extend([-9999]*npoints)  
                #self.data['28V_Solar_Seeker_Pwr'].extend([row[35] for row in data])
                #self.data['DEC_A_Plug_Strip'].extend([row[33] for row in data])
                #self.data['Hatch_Position_bit'].extend([row[34] for row in data])
                self.data['Hatch_Position_volt'].extend([-9999]*npoints)
                self.data['UTC_offset'].extend([row[36] for row in data])
                self.data['DOY'].extend([row[37] for row in data])
                self.data['E_Radiance'].extend([row[8] for row in data])
                self.data['W_Radiance'].extend([row[9] for row in data]) 
                #self.data['E_Radiance'].extend([row[10] for row in data])
                #self.data['W_Radiance'].extend([row[11] for row in data]) 

            
            except:
                print ('Error in reading file: %s' % fileName)
                pass

            #------------------------
            # Open house met file and read data
            #------------------------ 

            data2 = tryopen(fileNameMet)[1:]

            if data2:    

                try:    

                    print('Meteo File: {}'.format(fileNameMet))

                    data2[:] = [ row.strip().split() for row in data2 if not '#' in row ]

                    Date = [row[0] for row in data2]
                    Time = [row[1] for row in data2]
                    Temp = [row[2] for row in data2]
                    RelH = [row[3] for row in data2]
                    Pres = [row[4] for row in data2]
                    WinS = [row[5] for row in data2]
                    WinG = [row[6] for row in data2]
                    WinD = [row[7] for row in data2]

                    dateT =  [dt.datetime(int(time[0][0:4]),int(time[0][4:6]),int(time[0][6:8]),\
                                                              int(time[1][0:2]),int(time[1][3:5]),int(time[1][6:8])) for time in data2]


                    doyMet = toYearFraction(dateT)
     
                    Temp = np.asarray(Temp, dtype=np.float)
                    RelH = np.asarray(RelH, dtype=np.float)
                    Pres = np.asarray(Pres, dtype=np.float)
                    WinS = np.asarray(WinS, dtype=np.float)
                    WinD = np.asarray(WinD, dtype=np.float)

                    try:

                        Temp_i           = interp1d(doyMet, Temp, axis=0, fill_value=(Temp[0], Temp[-1]), bounds_error=False, kind='nearest')(doyhouse )
                        RelH_i           = interp1d(doyMet, RelH, axis=0, fill_value=(RelH[0], RelH[-1]), bounds_error=False, kind='nearest')(doyhouse )
                        Pres_i           = interp1d(doyMet, Pres, axis=0, fill_value=(Pres[0], Pres[-1]), bounds_error=False, kind='nearest')(doyhouse )
                        WinS_i           = interp1d(doyMet, WinS, axis=0, fill_value=(WinS[0], WinS[-1]), bounds_error=False, kind='nearest')(doyhouse )
                        WinD_i           = interp1d(doyMet, WinD, axis=0, fill_value=(WinD[0], WinD[-1]), bounds_error=False, kind='nearest')(doyhouse )

                    except:

                        Temp_i           = np.interp(doyhouse, doyMet, Temp, left=Temp[0], right= Temp[-1])
                        RelH_i           = np.interp(doyhouse, doyMet, RelH, left=RelH[0], right= RelH[-1])
                        Pres_i           = np.interp(doyhouse, doyMet, Pres, left=Pres[0], right= Pres[-1])
                        WinS_i           = np.interp(doyhouse, doyMet, WinS, left=WinS[0], right= WinS[-1])
                        WinD_i           = np.interp(doyhouse, doyMet, WinD, left=WinD[0], right= WinD[-1])

                    

                    WinS_i = 2.237 * WinS_i # Conversion m/s to miles/h
                    WinS_i = ["{0:.3f}".format(i) for i in WinS_i]

                    Temp_i = ["{0:.3f}".format(i) for i in Temp_i]
                    RelH_i = ["{0:.3f}".format(i) for i in RelH_i]
                    Pres_i = ["{0:.3f}".format(i) for i in Pres_i]
                    WinD_i = ["{0:.3f}".format(i) for i in WinD_i]

                    #self.data['Date'].extend(["{0:02d}".format(indvDate.year)+"{0:02d}".format(indvDate.month)+"{0:02d}".format(indvDate.day) for indvDate in datetimeTemp])

                except:
                    print ('Error in reading file: %s' % fileNameMet)
                    pass

            try:

 
                self.data['Outside_T'].extend([i for i in Temp_i]) 
                self.data['Outside_RH'].extend([i for i in RelH_i]) 
                self.data['Atm_Press'].extend([i for i in Pres_i]) 
                self.data['Wind_Speed_mph'].extend([i for i in WinS_i]) 
                self.data['WindDir_E_of_N'].extend([i for i in WinD_i]) 

            except:
                print ('Error interpolating Met to house time : %s' % fileNameMet)
                pass


            
                #sys.exit()
            
        
    def sortData(self):
        ''' '''
        base = self.data['DateTime']
        for key in self.data:
            self.data[key] = [y for (x,y) in sorted(zip(base,self.data[key]))]
            

class TABread():
    '''  Class for reading TAB house data  '''    
    def __init__(self):
        ''' Initializations '''
        #-------------------------------------
        # initialize dictionary for house data
        #-------------------------------------
        self.data = {'DateTime':[],                         
                     'Date':[],                              
                     'Time':[],
                     'Opt_Bnch_Src_T':[],
                     'Beamsplitter_T':[],
                     'Det_Dewar_T':[],
                     'Opt_Bnch_Det_T':[],
                     'Dolores_Int_HD_T':[],
                     'Dolores_Trans_T':[],
                     'Room_Box_T':[],
                     'Elec_T':[],
                     'Dolores_CPU_T':[],
                     'Outside_T':[],
                     'WindDir_W_of_S':[],
                     'Wind_Speed_mps':[],
                     'Atm_Press':[],
                     'Outside_RH':[],
                     'Bruker_Optical_RH':[],
                     'LN2_Dewar_P':[],
                     'LasA_Rect':[],
                     'LasB_Rect':[],
                     'Det_Intern_T_Swtch':[],
                     'Det_InSb_DC_Level':[],
                     'Elev_angle':[],
                     'Azimuth':[],
                     'Clin_Roll':[],
                     'Clin_Pitch':[],
                     'Ext_Solar_Sens':[],
                     'Quad_Sens':[],
                     'Temp_El_Motor':[],
                     'Temp_Upper_Seal':[],
                     'Temp_Lower_Seal':[],
                     'Temp_Lin_Actuator':[]}
        
    def __TABmatch(self,matchStrList,subline):
        match = re.search(matchStrList[0]+r'.*?=([-+]?[0-9]*\.[0-9]+|[-+]?[0-9]+)',subline)
        if match:
            if '.' in match.group(1):
                self.data[matchStrList[1]].append(float(match.group(1)))      
            else:
                self.data[matchStrList[1]].append(int(match.group(1)))
                    
            
    def formatA(self,fileName,year,month,day):
        ''' '''
        #------------------------
        # Open file and read data
        #------------------------
        data = tryopen(fileName)
      
        if data:   
            
            #-----------------------------------------
            # Some house log files have only one entry
            # and no header. These files seems to have
            # an inconstistant time stamp. Throw these
            # observations out.
            #-----------------------------------------
            if len(data) <= 50:
                print ('Error in reading file: %s' % fileName)
                return
                  
            #-----------------------------------
            # Sort through data for observations
            # These begin with *
            #-----------------------------------
            timeMin = []
            
            for ind,line in enumerate(data):
                if '*' in line and (line.strip().split()[0] == '*'):
                    #------------------------------
                    # Get the minute since start of 
                    # day for observation
                    #------------------------------
                    timeMin.append(dt.timedelta(minutes=int(line.strip().split()[1])))
                    
                    #-------------------------------------
                    # Grab data for particular observation
                    #-------------------------------------             
                    subsetData = data[ind+1:ind+28]
                    #----------------------------
                    # Parse data from observation
                    #----------------------------
                    matchStrList = [[r'BRUKER LASA RECTIFIED'      ,'LasA_Rect'         ],
                                    [r'BRUKER LASB RECTIFIED'      ,'LasB_Rect'         ],
                                    [r'OPTIC BENCH SRC SIDE'       ,'Opt_Bnch_Src_T'    ],
                                    [r'BEAM SPLITTER ASSEMB'       ,'Beamsplitter_T'    ],
                                    [r'DETECTOR DEWAR BODY'        ,'Det_Dewar_T'       ],
                                    [r'OPTIC BENCH DET SIDE'       ,'Opt_Bnch_Det_T'    ],
                                    [r'DOLORES INTERNAL'           ,'Dolores_Int_HD_T'  ],
                                    [r'DOLORES AQP7'               ,'Dolores_Trans_T'   ],
                                    [r'ROOM BOX'                   ,'Room_Box_T'        ],
                                    [r'BRUKER ELECTRONICS'         ,'Elec_T'            ],
                                    [r'DOLORES CPU'                ,'Dolores_CPU_T'     ],
                                    [r'DETECTOR INTERN TEMP'       ,'Det_Intern_T_Swtch'],
                                    [r'DETECTOR INSB DC LEVEL'     ,'Det_InSb_DC_Level' ],
                                    [r'BRUKER OPTIC BENCH RH'      ,'Bruker_Optical_RH' ],
                                    [r'ELEVATION ANGLE'            ,'Elev_angle'        ],
                                    [r'AZIMUTH'                    ,'Azimuth'           ],
                                    [r'WIND DIRECTION FROM'        ,'WindDir_W_of_S'    ],
                                    [r'WIND SPEED'                 ,'Wind_Speed_mps'    ],
                                    [r'ATMOSPHERIC PRESSURE'       ,'Atm_Press'         ], 
                                    [r'OUTSIDE TEMPERATURE'        ,'Outside_T'         ],
                                    [r'OUTSIDE RELATIVE HUMIDIT'   ,'Outside_RH'        ],
                                    [r'LN2 DEWAR PRESSURE'         ,'LN2_Dewar_P'       ],
                                    [r'CLINOMETER ROLL'            ,'Clin_Roll'         ],
                                    [r'CLINOMETER PITCH'           ,'Clin_Pitch'        ],
                                    [r'EXTERNAL SOLAR SENSOR'      ,'Ext_Solar_Sens'    ],
                                    [r'GUIDER QUAD SENSOR SUM'     ,'Quad_Sens'         ]]
                    
                    for subline in subsetData:
                        for singlMatchStr in matchStrList:                
                            self.__TABmatch(singlMatchStr,subline)
                         
            #------------------------------------------------
            # Create DateTime entry in Dictionary for sorting
            #------------------------------------------------
            datetimeTemp = [dt.datetime(year,month,day)+indvDtime for indvDtime in timeMin]
            self.data['DateTime'].extend(datetimeTemp)   
            
            #------------------------------------------
            # Create Date and Time entries based on the
            # DateTime entry
            #------------------------------------------
            self.data['Date'].extend(["{0:02d}".format(indvDate.year)+"{0:02d}".format(indvDate.month)+"{0:02d}".format(indvDate.day) for indvDate in datetimeTemp])
            self.data['Time'].extend(["{0:02d}".format(indvDate.hour)+':'+"{0:02d}".format(indvDate.minute)+':'+"{0:02d}".format(indvDate.second) for indvDate in datetimeTemp])

    #-----------------------  
    # ADDED FORMAT B FOR TAB. USED AFTER 2015 --- IVAN
    #----------------------
    def formatB(self,fileName,year,month,day):
        ''' '''
        #------------------------
        # Open file and read data
        #------------------------        

        data = tryopen(fileName)
      
        if data:                
            #--------------------------
            # Remove header information 
            #--------------------------
            data[:] = [ row.strip().split() for row in data if not '#' in row and len(row.strip().split()) == 28 ]
                                   
            #---------------------------------
            # Determine number of observations
            #---------------------------------
            npoints = len(data)
                   
            #------------------------------------------------
            # Create DateTime entry in Dictionary for sorting
            #------------------------------------------------
            try:
                self.data['DateTime'].extend([dt.datetime(int(time[0][0:4]),int(time[0][4:6]),int(time[0][6:8]),\
                                                          int(time[1][0:2]),int(time[1][3:5]),int(time[1][6:8])) for time in data])           
                
                #------------------
                # Update dictionary
                #------------------
                self.data['Date'].extend([row[0] for row in data])            
                self.data['Time'].extend([row[1] for row in data])            
                self.data['Opt_Bnch_Src_T'].extend([-9999]*npoints)   
                self.data['Beamsplitter_T'].extend([-9999]*npoints)   
                self.data['Det_Dewar_T'].extend([-9999]*npoints)   
                self.data['Opt_Bnch_Det_T'].extend([-9999]*npoints)  
                self.data['Dolores_Int_HD_T'].extend([-9999]*npoints) 
                self.data['Dolores_Trans_T'].extend([-9999]*npoints)
                self.data['Room_Box_T'].extend([-9999]*npoints)   
                self.data['Elec_T'].extend([-9999]*npoints)
                self.data['Dolores_CPU_T'].extend([-9999]*npoints)        
                self.data['Outside_T'].extend([row[11] for row in data])  
                self.data['WindDir_W_of_S'].extend([row[8] for row in data])  
                self.data['Wind_Speed_mps'].extend([row[9] for row in data])         
                self.data['Atm_Press'].extend([row[10] for row in data])   
                self.data['Outside_RH'].extend([row[12] for row in data])
                self.data['Bruker_Optical_RH'].extend([-9999]*npoints) 
                self.data['LN2_Dewar_P'].extend([row[13] for row in data])
                self.data['LasA_Rect'].extend([-9999]*npoints) 
                self.data['LasB_Rect'].extend([-9999]*npoints)
                self.data['Det_Intern_T_Swtch'].extend([-9999]*npoints)
                self.data['Det_InSb_DC_Level'].extend([-9999]*npoints)
                self.data['Elev_angle'].extend([-9999]*npoints) 
                self.data['Azimuth'].extend([row[27] for row in data])
                self.data['Clin_Roll'].extend([-9999]*npoints)
                self.data['Clin_Pitch'].extend([-9999]*npoints)
                
                FXSOL = [row[2] for row in data]
                NXSOL = [row[3] for row in data]

                #    if FXSOL >= NXSOL:
                self.data['Ext_Solar_Sens'].extend([row[2] for row in data])
                #    else: 
                #self.data['Ext_Solar_Sens'].extend([row[3] for row in data])  

                self.data['Quad_Sens'].extend([-9999]*npoints)
                self.data['Temp_El_Motor'].extend([row[4] for row in data])
                self.data['Temp_Upper_Seal'].extend([row[5] for row in data])
                self.data['Temp_Lower_Seal'].extend([row[6] for row in data])
                self.data['Temp_Lin_Actuator'].extend([row[7] for row in data])

            except:
                print ('Error in reading file: %s' % fileName)
                pass 


##############        
    def sortData(self):
        ''' '''
        base = self.data['DateTime']
        for key in self.data:
            self.data[key] = [y for (x,y) in sorted(zip(base,self.data[key]))]