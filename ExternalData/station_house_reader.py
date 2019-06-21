#! /usr/bin/python
#----------------------------------------------------------------------------------------
# Name:
#        station_house_reader.py
#
# Purpose:
#        The purpose of this program is to daily house.log data from mlo and convert to
#        a yearly ascii table. 
#
# Notes:
#
#
#
# Version History:
#       Created, July, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
#
#
# References:
#
#----------------------------------------------------------------------------------------



                                    #-------------------------#
                                    # Import Standard modules #
                                    #-------------------------#
import os
import datetime as dt
import sys
import glob
import DateRange as dr
import HouseReaderC as hr
import csv
import getopt
                                    #-------------------------#
                                    # Define helper functions #
                                    #-------------------------#

def ckDir(dirName):
    '''Check if a directory exists'''
    if not os.path.exists( dirName ):
        print 'Directory %s does not exist' % (dirName)
        return False
    else:
        return True
        
def ckFile(fName):
    '''Check if a file exists'''
    if not os.path.isfile(fName)    :
        print 'File %s does not exist' % (fName)
        sys.exit()

def usage():
    ''' Prints to screen standard program usage'''
    print ' station_house_reader.py [-s tab/mlo/fl0 -d 20180515_20180530 -?]'
    print '  -s <site>                             : Flag to specify location --> tab/mlo/fl0'
    print '  -d <20180515> or <20180515_20180530>  : Flag to specify date(s)'
    print '  -?                                    : Show all flags'


         
                                    #----------------------------#
                                    #                            #
                                    #        --- Main---         #
                                    #                            #
                                    #----------------------------#

def main(argv):

    #--------------------------------
    # Retrieve command line arguments
    #--------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:d:?')

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

        elif opt == '-d':

            if len(arg) == 8:

                dates   = arg.strip().split()

                iyear   = int(dates[0][0:4])
                imnth   = int(dates[0][4:6])
                iday    = int(dates[0][6:8])

                fyear   = int(dates[0][0:4])
                fmnth   = int(dates[0][4:6])
                fday    = int(dates[0][6:8])


            elif len(arg) == 17:

                dates   = arg.strip().split()

                iyear   = int(dates[0][0:4])
                imnth   = int(dates[0][4:6])
                iday    = int(dates[0][6:8])

                fyear   = int(dates[0][9:13])
                fmnth   = int(dates[0][13:15])
                fday    = int(dates[0][15:17])


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
                                    
    #----------------
    # Initializations
    #----------------
    statstr     = loc
    dataDir     = '/data1/'+statstr.lower()+'/'
    #dataDir     = '/ya4/id/'+statstr.lower()+'/'
    outDataDir  = '/data/Campaign/'+statstr.upper()+'/House_Log_Files/'
    
    #------------------------------
    # Date Range of data to process
    #------------------------------
    # Starting 
    #iyear = 2018               # Year
    #imnth = 1                 # Month
    #iday  = 1                  # Day
    
    # Ending
    #fyear = 2018               # Year
    #fmnth = 12                 # Month
    #fday  = 31                 # Day
    
    #-------------------
    # Call to date class
    #-------------------
    DOI = dr.DateRange(iyear,imnth,iday,fyear,fmnth,fday)
        
    #----------------------------
    # Create list of unique years
    #----------------------------
    years = DOI.yearList()
    
    #------------------
    # Loop through year
    #------------------
    for indvYear in years:
        #------------------------
        # Name of house data file
        #------------------------
        houseFileNew = outDataDir + statstr.upper() + '_HouseData_' + str(indvYear) + '.dat'
        
        #---------------------------------------------------
        # Determine if yearly house data file already exists
        #---------------------------------------------------
        if os.path.isfile(houseFileNew):
            wmode = 'ab'
        else:
            wmode = 'wb'        
    
        #--------------------------------------
        # Create house data dictionary instance
        #--------------------------------------
        if (statstr.lower() == 'mlo'):
            houseData = hr.MLOread()
        elif (statstr.lower() == 'tab'):
            houseData = hr.TABread()
            
        #--------------------------------------
        # Loop through days/folders within year
        #--------------------------------------
        daysYear = DOI.daysInYear(indvYear)        # Create a list of days within one year
        
        for indvDay in daysYear:

            print indvDay
            
            # Find year month and day strings
            yrstr   = "{0:02d}".format(indvDay.year)
            mnthstr = "{0:02d}".format(indvDay.month)
            daystr  = "{0:02d}".format(indvDay.day)  
            
            dayDir = dataDir + yrstr + mnthstr + daystr + '/'
            
            if not ckDir(dayDir):
                continue
            
            #--------------------------------------------
            # Log files changed name after Jan 21st, 2009
            #--------------------------------------------
            if (statstr.lower() == 'mlo'):
                
                if indvDay < dt.date(2009,1,21):
                    srchstr = yrstr + mnthstr + daystr + '.wth'
                
                elif indvDay >= dt.date(2019,05,03):
                    
                    srchstr  = 'house.log'
                    srchstr2 = 'houseMet.log'

                else:
                    srchstr = 'house.log'

            elif (statstr.lower() == 'tab'):
                srchstr = 'house.log'
                
            #------------------------
            # Look for house log file
            #------------------------
            houseFile = glob.glob( dayDir + srchstr )
                    
            if not houseFile:
                continue
            
            houseFile = houseFile[0]
            
            #--------------------------------------
            # Determine which house log file reader 
            # to use based on date range
            #--------------------------------------
            if (statstr.lower() == 'mlo'):
                # Format A for date < 20090121
                if indvDay < dt.date(2009,1,21):
                    houseData.formatA(houseFile,indvDay.year,indvDay.month,indvDay.day)
                    
                # Format B for 20090121 <= date < 20090320
                elif dt.date(2009,1,21) <= indvDay < dt.date(2009,3,20):
                    houseData.formatB(houseFile,indvDay.year,indvDay.month,indvDay.day)
                    
                # Format C for 20090320 <= date < 20110802
                elif dt.date(2009,3,20) <= indvDay < dt.date(2011,8,2):
                    houseData.formatC(houseFile,indvDay.year,indvDay.month,indvDay.day)

                # Format D for 20110802 <= date < 20171210
                elif dt.date(2011,8,2) <= indvDay < dt.date(2017,12,10):
                    houseData.formatD(houseFile,indvDay.year,indvDay.month,indvDay.day)

                elif dt.date(2011,8,2) <= indvDay < dt.date(2019,05,02):
                    houseData.formatD(houseFile,indvDay.year,indvDay.month,indvDay.day)

                elif indvDay >= dt.date(2019,05,03):
                    houseFileMet = glob.glob( dayDir + srchstr2 )[0]

                    houseData.formatF(houseFile,houseFileMet, indvDay.year,indvDay.month,indvDay.day)

                # Format D for date >= 20171210
                #elif indvDay >= dt.date(2017,12,10):
                #    houseData.formatD(houseFile,indvDay.year,indvDay.month,indvDay.day)

          
            elif (statstr.lower() == 'tab'):
                # Format A for (TAB) date < 20150101
                if indvDay < dt.date(2015,1,1):
                    houseData.formatA(houseFile,indvDay.year,indvDay.month,indvDay.day)
               # Format A for (TAB) date >= 20150101
                elif indvDay >= dt.date(2015,1,1):
                    houseData.formatB(houseFile,indvDay.year,indvDay.month,indvDay.day)    
             
        #------------------------
        # Sort data based on date
        #------------------------

        houseData.sortData()
        
        #-----------------------------------------
        # Open output file for year and write data
        #-----------------------------------------
        with open(houseFileNew, wmode) as fopen:
            writer = csv.writer(fopen, delimiter='\t',lineterminator='\n')
            
            if (wmode == 'wb') and (statstr.lower() == 'mlo'):
                
                #-------------
                # Print header
                #-------------
                fopen.write('#   LABEL                       Units          Column    Missing Value\n')
                fopen.write('#---------------------------------------------------------------------\n')
                fopen.write('#   Date                        YYYYMMDD       1         NA           \n')
                fopen.write('#   Time                        HH:MM:SS       2         NA           \n')
                fopen.write('#   LN2_Dewar_P_volt            volts          3         -9999        \n')
                fopen.write('#   LN2_Dewar_P_psi             PSI            4         -9999        \n')
                fopen.write('#   Optic_Bench_Baseplate_T     C              5         -9999        \n')
                fopen.write('#   Beamsplitter_T              C              6         -9999        \n')
                fopen.write('#   Front_T                     C              7         -9999        \n')
                fopen.write('#   InSb_T                      C              8         -9999        \n')
                fopen.write('#   MCT_T                       C              9         -9999        \n')
                fopen.write('#   Laser_T                     C              10        -9999        \n')
                fopen.write('#   Outside_T                   C              11        -9999        \n')
                fopen.write('#   Brucker_Optical_RH          %              12        -9999        \n')
                fopen.write('#   Outside_RH                  %              13        -9999        \n')
                fopen.write('#   Wind_Speed_volt             volts          14        -9999        \n')
                fopen.write('#   Wind_Speed_mph              MPH            15        -9999        \n')
                fopen.write('#   WindDir_volt                volts          16        -9999        \n')
                fopen.write('#   WindDir_E_of_N              deg            17        -9999        \n')
                fopen.write('#   Mid_IR_Cooler               bit            18         9           \n')
                fopen.write('#   LN2_Fill                    bit            19         9           \n')
                fopen.write('#   Hatch_Relay                 bit            20         9           \n')
                fopen.write('#   Solar_Seeker_ON_Relay       bit            21         9           \n')
                fopen.write('#   Solar_Seeker_OFF_Relay      bit            22         9           \n')
                fopen.write('#   Dyn_Mirror_Pwr              bit            23         9           \n')
                fopen.write('#   DEC_A_Plug_Strip            bit            24         9           \n')
                fopen.write('#   28V_Solar_Seeker_Pwr        bit            25         9           \n')
                fopen.write('#   Hatch_Position_bit          bit            26         9           \n')
                fopen.write('#   Hatch_Position_volt         volt           27        -9999        \n')
                fopen.write('#   UTC_offset                  HH             28        -9999        \n')
                fopen.write('#   DOY                         DDD            29        -999         \n')                
                fopen.write('#   E_Radiance                  volts          30        -9999        \n')
                fopen.write('#   W_Radiance                  volts          31        -9999        \n')
                fopen.write('#   Atm_Press                   mbar           32        -9999        \n')
                fopen.write('#---------------------------------------------------------------------\n')
 
            elif (wmode == 'wb') and (statstr.lower() == 'tab'):
                #-------------
                # Print header
                #-------------
                fopen.write('#   LABEL                       Units          Column    Missing Value\n')
                fopen.write('#---------------------------------------------------------------------\n')
                fopen.write('#   Date                        YYYYMMDD       1         NA           \n')
                fopen.write('#   Time                        HH:MM:SS       2         NA           \n')
                fopen.write('#   Opt_Bnch_Src_T              C              3         -9999        \n')
                fopen.write('#   Beamsplitter_T              C              4         -9999        \n')
                fopen.write('#   Det_Dewar_T                 C              5         -9999        \n')
                fopen.write('#   Opt_Bnch_Det_T              C              6         -9999        \n')
                fopen.write('#   Dolores_Int_HD_T            C              7         -9999        \n')
                fopen.write('#   Dolores_Trans_T             C              8         -9999        \n')
                fopen.write('#   Room_Box_T                  C              9         -9999        \n')
                fopen.write('#   Elec_T                      C              10        -9999        \n')
                fopen.write('#   Dolores_CPU_T               C              11        -9999        \n')
                fopen.write('#   Outside_T                   C              12        -9999        \n')
                fopen.write('#   WindDir_W_of_S              DegW           13        -9999        \n')
                fopen.write('#   Wind_Speed_mps              ms^-1          14        -9999        \n')
                fopen.write('#   Atm_Press                   mbar           15        -9999        \n')
                fopen.write('#   Outside_RH                  %              16        -9999        \n')
                fopen.write('#   Bruker_Optical_RH           %              17        -9999        \n')
                fopen.write('#   LN2_Dewar_P                 psi            18        -9999        \n')
                fopen.write('#   LasA_Rect                   volts          19        -9999        \n')
                fopen.write('#   LasB_Rect                   volts          20        -9999        \n')
                fopen.write('#   Det_Intern_T_Swtch          volts          21        -9999        \n')
                fopen.write('#   Det_InSb_DC_Level           volts          22        -9999        \n')
                fopen.write('#   Elev_angle                  volts          23        -9999        \n')
                fopen.write('#   Azimuth                     volts          24        -9999        \n')
                fopen.write('#   Clin_Roll                   volts          25        -9999        \n')
                fopen.write('#   Clin_Pitch                  volts          26        -9999        \n')
                fopen.write('#   Ext_Solar_Sens              volts          27        -9999        \n')
                fopen.write('#   Quad_Sens                   volts          28        -9999        \n')
                fopen.write('#   Temp_El_Motor               C              29        -9999        \n')
                fopen.write('#   Temp_Upper_Seal             C              30        -9999        \n')
                fopen.write('#   Temp_Lower_Seal             C              31        -9999        \n')
                fopen.write('#   Temp_Lin_Actuator           C              32        -9999        \n')
                fopen.write('#---------------------------------------------------------------------\n')          
                   
 
 
            #----------------------------------------------
            # Remove DateTime key and value from dictionary 
            # for writing to file. This was used just for
            # sorting the data
            #----------------------------------------------
            houseData.data.pop('DateTime',None)
                
            #-------------------------------------
            # Create order of key to write to file
            #-------------------------------------
            if (statstr.lower() == 'mlo'):
                order = {'Date':0,'Time':1,'LN2_Dewar_P_volt':2,'LN2_Dewar_P_psi':3,\
                         'Optic_Bench_Baseplate_T':4,'Beamsplitter_T':5,'Front_T':6,'InSb_T':7,\
                         'MCT_T':8,'Laser_T':9,'Outside_T':10,'Brucker_Optical_RH':11,\
                         'Outside_RH':12,'Wind_Speed_volt':13,'Wind_Speed_mph':14,'WindDir_volt':15,\
                         'WindDir_E_of_N':16,'Mid_IR_Cooler':17,'LN2_Fill':18,'Hatch_Relay':19,\
                         'Solar_Seeker_ON_Relay':20,'Solar_Seeker_OFF_Relay':21,'Dyn_Mirror_Pwr':22,\
                         'DEC_A_Plug_Strip':23,'28V_Solar_Seeker_Pwr':24,'Hatch_Position_bit':25,\
                         'Hatch_Position_volt':26,'UTC_offset':27,'DOY':28,'E_Radiance':29,'W_Radiance':30, 'Atm_Press':31}
            elif (statstr.lower() == 'tab'):
                order = {'Date':0,'Time':1,'Opt_Bnch_Src_T':2,'Beamsplitter_T':3,\
                         'Det_Dewar_T':4,'Opt_Bnch_Det_T':5,'Dolores_Int_HD_T':6,'Dolores_Trans_T':7,\
                         'Room_Box_T':8,'Elec_T':9,'Dolores_CPU_T':10,'Outside_T':11,\
                         'WindDir_W_of_S':12,'Wind_Speed_mps':13,'Atm_Press':14,'Outside_RH':15,\
                         'Bruker_Optical_RH':16,'LN2_Dewar_P':17,'LasA_Rect':18,'LasB_Rect':19,\
                         'Det_Intern_T_Swtch':20,'Det_InSb_DC_Level':21,'Elev_angle':22,\
                         'Azimuth':23,'Clin_Roll':24,'Clin_Pitch':25,\
                         'Ext_Solar_Sens':26,'Quad_Sens':27, 'Temp_El_Motor':28, 'Temp_Upper_Seal':29,'Temp_Lower_Seal':30, 'Temp_Lin_Actuator':31}            
            
            #-----------------------------
            # Write dictionary out to file
            #-----------------------------
            writer.writerows(zip(*(houseData.data[k] for k in sorted(houseData.data, key=order.get))))
        

if __name__ == "__main__":
    main(sys.argv[1:])