#! /usr/bin/python3
##! /usr/local/python-2.7/bin/python

#----------------------------------------------------------------------------------------
# Name:
#      retWaterPrf.py
#
# Purpose:
#      This program creates water profiles (w-120)for input into reference profiles from
#          retrieved water profiles
#
#
# Input files:
#       1)
#
# Output files:
#       1)
#
#
# Notes:
#       1)
#
# References:
#
#----------------------------------------------------------------------------------------


                        #-------------------------#
                        # Import Standard modules #
                        #-------------------------#
import os, sys
sys.path.append((os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "ModLib")))
import datetime                                            as dt
import dataOutClass                                        as dc
import numpy                                               as np
from scipy.interpolate import InterpolatedUnivariateSpline as intrpUniSpl
import matplotlib.pyplot                                   as plt
from matplotlib.backends.backend_pdf import PdfPages
import getopt

plt.rcParams.update({'figure.max_open_warning': 0})


#------------------------
# Define helper functions
#------------------------
def usage():
    print('retWaterPrf.py -s <loc>  -v <version> -d <20190101_20191231> -?] \n\n'
         '-s <loc>                               : Location (three letter id, eg., fl0, mlo)\n'
         '-v <version>                           : Version of water vapor\n'
         '-d <20190101> or <20190101_20191231>   : Date or Date range\n'
         'Note: hardcoded inputs are included')

    sys.exit()

                        #-------------------------------------#
                        # Define helper functions and classes #
                        #-------------------------------------#

def ckDir(dirName,exitFlg=False):
    ''' '''
    if not os.path.exists( dirName ):
        print ('Input Directory %s does not exist' % (dirName))
        if exitFlg: sys.exit()
        return False
    else:
        return True

def ckFile(fName,exitFlg=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print ('File %s does not exist' % (fName))
        if exitFlg: sys.exit()
        return False
    else:
        return True

def segmnt(seq,n):
    '''Yeilds successive n-sized segments from seq'''
    try:
        xrange
    except NameError:
        xrange = range
        
    for i in xrange(0,len(seq),n): yield seq[i:i+n]

def findCls(dataArray, val):
    ''' Returns the indice and closest value in dataArray to val'''
    return np.argmin(abs(val-dataArray))


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
        opts, args = getopt.getopt(sys.argv[1:], 's:d:v:?')

    except getopt.GetoptError as err:
        print (str(err))
        usage()
        sys.exit()

    #-----------------------------
    # Parse command line arguments
    #-----------------------------
    for opt, arg in opts:
        # Check input file flag and path
        if opt == '-s':

            loc = arg.lower()

        elif opt == '-v':

            ver = arg

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
                print ('Error in input date')
                usage()
                sys.exit()

        elif opt == '-?':
            usage()
            sys.exit()

        else:
            print ('Unhandled option: ' + opt)
            sys.exit()


    #----------------
    # Initializations
    #----------------
    #loc        = 'fl0'                 # Name of station location
    gasName    = 'h2o'                 # Name of gas
    
    #ver        = 'Current_NCEP'         # Name of retrieval version to process
    #ver        = 'Current_v10'         # Name of retrieval version to process
    #ver        = 'Current_v6_50'         # Name of retrieval version to process
    
    #verW       = 'v77'                 # version 99 is used for individual retrievals at specific times
    verW       = 'v99'                 # version 99 is used for individual retrievals at specific times
    
    #ctlF       = 'sfit4_v10.ctl'
    if loc == 'fl0': ctlF       = 'sfit4.ctl'
    else:            ctlF       = 'sfit4_v1.ctl'
    #ctlF       = 'sfit4_v1.ctl'

    #------
    # Flags
    #------
    fltrFlg    = True               # Flag to filter the data
    maxrms     = 2                  # Max Fit RMS to filter data. Data is filtered according to <= maxrms
    pltFlg     = True
    logFlg     = True         # Flag to do interpolation of log of water

    #-------------------
    # Interpolation Oder
    #-------------------
    intrpOrder = 1            # Order of interpolation

    #-----------------------
    # Date Range of interest
    #-----------------------
    #iyear          = 2018
    #imnth          = 12
    #iday           = 1
    #fyear          = 2018
    #fmnth          = 12
    #fday           = 31

    #---------------------
    # Input Data Directory
    #---------------------
    retDir  = '/data1/ebaumer/'+loc.lower()+'/'+gasName.lower()+'/'+ver+'/'     # Retrieval data directory

    #----------------------
    # Output Data Directory
    #----------------------
    dataDir  = '/data1/'+loc.lower()+'/'

    #------
    # Files
    #------
    ctlFile  = '/data1/ebaumer/'+loc.lower()+'/'+gasName.lower()+'/'+'x.'+gasName.lower()+'/'+ctlF

    #---------------------------------------
    # Altitude levels for different stations
    #---------------------------------------
    if loc.lower() == 'tab':
        Z = np.array([ 120.0000,    110.0000,    100.0000,     95.0000,     90.0000,
                        85.0000,     80.0000,     75.0000,     70.0000,     65.0000,
                        60.0000,     55.0000,     50.0000,     48.0000,     46.0000,
                        44.0000,     42.0000,     40.0000,     38.0000,     36.0000,
                        34.0000,     32.0000,     30.0000,     28.0000,     26.0000,
                        24.0000,     22.0000,     20.0000,     18.0000,     16.0000,
                        14.0000,     12.0000,     10.0000,      9.0000,      8.0000,
                         7.0000,      6.0000,      5.0000,      4.0000,      3.0000,
                         2.0000,      1.0000,      0.2250   ])
        sLat = 76.52
        sLon = 291.23               # 68.77 W = (360.0 - 68.77) = 291.23 E

    elif loc.lower() == 'mlo':
        Z = np.array([ 120.0000,    110.0000,    100.0000,     95.0000,     90.0000,
                        85.0000,     80.0000,     75.0000,     70.0000,     65.0000,
                        60.0000,     55.0000,     50.0000,     48.0000,     46.0000,
                        44.0000,     42.0000,     40.0000,     38.0000,     36.0000,
                        34.0000,     32.0000,     30.0000,     28.0000,     26.0000,
                        24.0000,     22.0000,     20.0000,     18.0000,     16.0000,
                        14.0000,     12.0000,     10.0000,      9.0000,      8.0000,
                         7.0000,      6.0000,      5.0000,      4.0000,      3.3960])

        sLat = 19.4
        sLon = 204.43                # 155.57 W = (360 - 155.57) = 204.43 E

    elif loc.lower() == 'fl0':
        Z = np.array([ 120.0000,    110.0000,    100.0000,     94.0000,     90.0000,
                        85.0000,     80.0000,     75.0000,     70.0000,     65.0000,
                        60.0000,     55.0000,     50.0000,     48.0000,     46.0000,
                        44.0000,     42.0000,     40.0000,     38.0000,     36.0000,
                        34.0000,     32.0000,     30.0000,     28.0000,     26.0000,
                        24.0000,     22.0000,     20.0000,     18.0000,     16.0000,
                        14.0000,     12.0000,     10.0000,      9.0000,      8.0000,
                         7.0000,      6.0000,      5.0000,      4.0000,      3.0000,
                         2.0000,      1.6120])

        sLat = 40.4
        sLon = 254.76                # 105.24 W = (360 - 105.24) = 254.76 E

    #----------------------------
    # File and directory checking
    #----------------------------
    ckDir(retDir,exitFlg=True)
    ckDir(dataDir,exitFlg=True)
    ckFile(ctlFile,exitFlg=True)

    #-------------------------------------
    # Create instance of output data class
    #-------------------------------------
    statDataCl = dc.ReadOutputData(retDir,'',ctlFile,iyear,imnth,iday,fyear,fmnth,fday)

    #--------------
    # Read profiles
    #--------------
    statDataCl.readprfs([statDataCl.PrimaryGas],retapFlg=1)         # Retrieved Profiles

    #----------------------------------
    # Read Summary data (For filtering)
    #----------------------------------
    statDataCl.readsummary()

    #----------------------------
    # Get retrieved water profile
    #----------------------------
    H2OrPrf = np.asarray(statDataCl.rprfs['H2O'])
    dates   = np.asarray(statDataCl.rprfs['date'])
    alt     = np.asarray(statDataCl.rprfs['ZBAR'][0,:])

    #--------------------
    # Call to filter data
    #--------------------
    if fltrFlg: statDataCl.fltrData(statDataCl.PrimaryGas,mxrms=maxrms,rmsFlg=True,tcFlg=True,pcFlg=True,cnvrgFlg=True)
    else:       statDataCl.inds = np.array([])

    #-----------------------------------
    # Remove profiles based on filtering
    #-----------------------------------
    H2OrPrf = np.delete(H2OrPrf,statDataCl.inds,axis=0)
    dates   = np.delete(dates,statDataCl.inds)

    #---------------------------
    # Iterate through retrievals
    #---------------------------
    for i,sngDay in enumerate(dates):

        #----------------------------
        # Get corresponding directory
        #----------------------------
        baseDir = dataDir + '{0:04d}{1:02d}{2:02d}/'.format(sngDay.year,sngDay.month,sngDay.day)
        ckDir(baseDir,exitFlg=True)

        #-----------------------------------
        # Interpolate retrieved profile onto
        # sfit input grid
        #-----------------------------------
        if logFlg:
            H2Oout = np.exp(np.flipud( intrpUniSpl( np.flipud(alt), np.log(np.flipud(H2OrPrf[i])), k=intrpOrder )( np.flipud(Z) ) ) )
        else:
            H2Oout = np.flipud( intrpUniSpl( np.flipud(alt), np.flipud(H2OrPrf[i]), k=intrpOrder )( np.flipud(Z) ) )

        #---------------------
        # Write out water file
        #---------------------
        tstamp = '{0:04d}{1:02d}{2:02d}.{3:02d}{4:02d}{5:02d}'.format(sngDay.year,sngDay.month,sngDay.day,sngDay.hour,sngDay.minute,sngDay.second)

        with open(baseDir+'w-120.'+tstamp+'.'+verW,'w') as fopen:
            fopen.write('    1     H2O from sfit4 retrieval \n')

            for row in segmnt(H2Oout,5):
                strformat = ','.join('{:>12.4E}' for i in row) + ', \n'
                fopen.write(strformat.format(*row))

        #--------------------
        # Create plots to pdf
        #--------------------
        if pltFlg:
            pdfsav = PdfPages(baseDir+'Ret_'+tstamp+'_WaterProfile.pdf')

            fig1,ax1 = plt.subplots()
            ax1.plot(H2Oout,Z,'rx-', label='Interpolated Water Profile')
            ax1.plot(H2OrPrf[i],alt,'bx-',label='Original Retrieved Water Profile')
            ax1.grid(True,which='both')
            ax1.legend(prop={'size':9})
            ax1.set_ylabel('Altitude [km]')
            ax1.set_xlabel('VMR')
            ax1.tick_params(axis='x',which='both',labelsize=8)
            ax1.set_ylim((Z[-1],60))
            #ax1.set_xlim((0,np.max((waccmW[-1,mnthInd],dayShum[-1]))))
            ax1.set_title(sngDay)

            pdfsav.savefig(fig1,dpi=250)

            pdfsav.close()


if __name__ == "__main__":
    main(sys.argv[1:])