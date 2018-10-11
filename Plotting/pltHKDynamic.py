#! /usr/bin/python
#----------------------------------------------------------------------------------------
# Name:
#        pltHKDynamic.py
#
# Purpose:
#       This program is used to plot house keeping variables from daily folders:
#
# External called functions:
#        This program calls standard python modules, e.g., numpy, matplotlib
#
# Notes:
#       1) Path of directory and Variables of interest are hard coded below
#
#       2) See in Main() syntax for variables to be plotted in lef/right axis
#
#       3 Options include:
#            -d <YYYYMMDD>    : Flag to specify input Date. If not Date is specified current date is used.
#            -S               : Flag to create PDF file in data directory
#            -m <Seconds>     : Flag to specify Dynamic Time in N seconds to create plot. Defauls is not Dynamic
#            -l               : Flag Must include location: mlo/tab/fl0 (only for otserver)'
#            -?               : Show all flags
#
#
# Examples:
#        To run a specific date and save PDF:
#        1) >> python pltHKDynamic -d <20180515> -S 
#
#        To create a PDF every 1h and save PDF of current date (and following dates)
#        2) >> python pltHKDynamic -m3600 -S
#
#
# Version History:
#       Created, June, 2018  Ivan Ortega (iortega@ucar.edu)
#       --> house.log files created prior to Aug 2018 had some headers issues (this script might not work)
#    
#
#----------------------------------------------------------------------------------------

    #-------------------------#
    # Import Standard modules #
    #-------------------------#
import sys
import os
import numpy    as np
import datetime as dt
import matplotlib.dates as md
from   matplotlib.dates import DateFormatter, MonthLocator, YearLocator, DayLocator, HourLocator
from   matplotlib.ticker import FormatStrFormatter, MultipleLocator, AutoMinorLocator, ScalarFormatter
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from   matplotlib.backends.backend_pdf import PdfPages
import matplotlib.gridspec as gridspec
import time
from cycler import cycler
import getopt
    
    
def usage():
    ''' Prints to screen standard program usage'''
    print 'pltHKDinamyc.py [-d 20180515 -m30 -S -?]'
    print '  -d <20180515>  : Flag to specify input Date. If not Date is specified current date is used.'
    print '  -m <30>        : Flag to specify Dynamic Time in N seconds to create plot of current day. Defauls is not Dynamic'
    print '  -S             : Flag to Save PDF. Default is not to save PDF'
    print '  -l             : Flag Must include location: mlo/tab/fl0 (only for otserver)'
    print '  -?             : Show all flags'

def ckFile(fName,exitFlg=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print 'File %s does not exist' % (fName)
        if exitFlg: sys.exit()
        return False
    else:
        return True  

def ckDir(dirName,exitFlg=False):
    ''' Check the existence of a directory'''
    if not os.path.exists( dirName ):
        print 'Input Directory %s does not exist' % (dirName)
        if exitFlg:      sys.exit()
        return False
    else:
        return True


class RemoteHK():

    def __init__(self,Dir='', iyear='',iday='', imnth='', pdfFlg=False, DynamicFlg=False):

        self.dir        = Dir
        self.pdfFlg     = pdfFlg
        self.DynamicFlg = DynamicFlg

        self.date       = str(iyear) + str(imnth) + str(iday) 
        self.iyear      = iyear
        self.imnth      = imnth
        self.iday       = iday

        #----------------------------
        # File and directory checking
        #----------------------------
        ckDir(self.dir,exitFlg=True)


    def openFig(self):
    
        pdfPath  = self.dir + self.date
        pdfFile  = pdfPath + "/HousePlots.pdf"
                
        ckDir(os.path.dirname(pdfFile),exitFlg=True)
        self.pdfSave = PdfPages(pdfFile)

    def closeFig(self):
        self.pdfSave.close()
        print 'PDF saved'
    
    #----------------------------
    # READ HK DEF
    #----------------------------
    def readHK(self, showID=False):
        
        self.hkFlg  = False

        #-----------------------------------------------
        # 
        #-----------------------------------------------
        self.fname = self.dir + self.date + '/house.log'
        
        
        if ckFile(self.fname, exitFlg=False):

            self.vars = {}
    
            #-------------------
            # Open and read file
            #-------------------
            with open(self.fname,"r") as fopen: lines = fopen.readlines()
            
            #---------------
            # Read in Header
            #---------------
            for line in lines:
                if line.strip().startswith("#$"):
                    hdrs = [ val for val in line.strip().split()[3:]]
             
            #-------------------------
            # Choose variables to plot
            #-------------------------
            ii    = []
            idVal = []
            for i,v in enumerate(hdrs):
                ii.append(ii)
                idVal.append(v)
                if showID: print "{0:4}= {1:}".format(i,v)
          

            #----------------------
            # Read in date and time
            #----------------------
            self.obsTime = np.array([dt.datetime(int(line[0:4]),int(line[4:6]),int(line[6:8]),
                                        int(line[9:11]),int(line[12:14]),int(line[15:17])) for line in lines[:-2] if (not line.startswith("#"))])

            for i, v in enumerate(idVal):
                try:
                    self.vars.setdefault(v,[]).append(np.array([float(line.strip().split()[i+2]) for line in lines[:-2] if not line.startswith("#")]))
                except ValueError:
                    self.vars.setdefault(v,[]).append(np.array([line.strip().split()[i+2] for line in lines[:-2] if not line.startswith("#")]))
            
            self.hkFlg  = True

        else:
            print 'File Not Found or empy: ', self.fname 

    #----------------------------
    # READ HK DEF
    #----------------------------
    def readMeas(self):
        
        #----------------------------
        # File and directory checking
        #----------------------------

        self.vars      = {}
        self.pltsnrFlg = False

        #-----------------------------------------------
        # 
        #-----------------------------------------------
        self.fname = self.dir + self.date + '/Measurement.log'

        #---------------
        # Handling Error in format
        #---------------
        site = os.path.dirname(self.fname).split('/')[3]

        
        if ckFile(self.fname, exitFlg=False):

            #-------------------
            # Open and read file
            #-------------------
            with open(self.fname,"r") as fopen: lines = fopen.readlines()
            
            #---------------
            # Read in Header
            #---------------
            #hdrs = [ val for val in lines[0].strip().split()[:]]
            if site.lower() == 'mlo':
                hdrs   = ['Measurement_Time', 'Filename', 'SNR_RMS', 'Peak_Amplitude', 'Pre_Amp_Gain', 'Signal_Gain', 'Ext_E_Rad', 'Ext_E_RadS', 'Ext_W_Rad', 'Ext_E_Rads']
            elif site.lower() == 'tab':
                hdrs   = ['Measurement_Time', 'Filename', 'SNR_RMS', 'Peak_Amplitude', 'Pre_Amp_Gain', 'Signal_Gain', 'Solar_Sensor_Nom', 'Solar_Sensor_Flip']

             
            #-------------------------
            # Choose variables to plot
            #-------------------------
            ii    = []
            idVal = []
            for i,v in enumerate(hdrs):
                ii.append(ii)
                idVal.append(v)      

            #----------------------
            # Read in date and time
            #----------------------
            self.vars['DT_Meas'] = np.array([dt.datetime(int(self.iyear),int(self.imnth),int(self.iday),
                                        int(line[0:2]),int(line[3:5]),int(line[6:8])) for line in lines[1:-2] ])

            if len(self.vars['DT_Meas']) > 1: self.pltsnrFlg = True

            for i, v in enumerate(idVal):
                try:
                    self.vars.setdefault(v,[]).append(np.asarray([float(line.strip().split()[i]) for line in lines[1:-2] ]) )
                except:
                    self.vars.setdefault(v,[]).append(np.asarray([line.strip().split()[i] for line in lines[1:-2] ]) )

        else:
            print 'File Not Found: ', self.fname
           
    #----------------------------
    # PLOT HK DEF
    #----------------------------
    def plt_HK(self, Groups= False, Groups_Lab= False, showID=False):

        self.readHK(showID=showID)

        if self.hkFlg:
          
            if Groups:

                clr1           = ['b', 'g', 'brown', 'yellow']
                clr2           = ['r', 'k', 'b', 'g']

                Npanels        = len(Groups)

                fig1, ax1 = plt.subplots(Npanels, figsize=(8,10), sharex=True)

                for vi, varsGroup in enumerate(Groups):

                    if len(varsGroup) == 1:
                        for i, v in enumerate(varsGroup):

                            for j, k in enumerate(v):

                                pltVal  = np.asarray(self.vars[k][0])
                                if pltVal.dtype is np.dtype(np.float64):
                                    ax1[vi].plot(self.obsTime,pltVal,"." ,markersize=4, label = k, color=clr1[j])
                                else:
                                    pltVal2 = []
                                    for vs in pltVal:
                                        
                                        try:
                                            if vs.lower() == 'open':
                                                pltVal2.append(1)
                                            elif vs.lower() == 'close':
                                                pltVal2.append(0)
                                            elif vs.lower() == 'clos':
                                                pltVal2.append(0)
                                            elif vs.lower() == 'unkn':
                                                pltVal2.append(-1)
                                            elif vs.lower() == 'on':
                                                pltVal2.append(1)
                                            elif vs.lower() == 'off':
                                                pltVal2.append(0)
                                            else:
                                                pltVal2.append(-1) 
                                        except ValueError:
                                            print 'ValueError'

                                    ax1[vi].plot(self.obsTime,pltVal2,"." ,markersize=4, label= k, color=clr1[j])
                                    ax1[vi].text(0.05,0.8,'0 = OFF/CLOSE', transform=ax1[vi].transAxes, )
                                    ax1[vi].text(0.05,0.7,'1 = ON/OPEN', transform=ax1[vi].transAxes)
                                    ax1[vi].text(0.05,0.6,'-1 = UNKN/OTHER', transform=ax1[vi].transAxes)

                    elif len(varsGroup) == 2:
                        axr = ax1[vi].twinx()
                        for i, v in enumerate(varsGroup):

                            if i == 0:
                                for j, k in enumerate(v):
                                    pltVal  = np.asarray(self.vars[k][0])

                                    ax1[vi].plot(self.obsTime,pltVal,"." ,markersize=4, label = k, color=clr1[j])

                            if i == 1:

                                for j, k in enumerate(v):
                                    pltVal  = np.asarray(self.vars[k][0])
                                    axr.plot(self.obsTime,pltVal,"." ,markersize=4, label = k, color=clr2[j])

                    #----------
                    ax1[vi].set_ylabel(Groups_Lab[vi][0])
                    ax1[vi].grid(True)
                    ax1[-1].set_xlabel("UT Time[Hours]")
                    ax1[vi].xaxis.set_major_locator(HourLocator())
                    ax1[vi].xaxis.set_major_formatter(DateFormatter("%H"))
                    ax1[vi].xaxis.set_minor_locator(AutoMinorLocator())
                    #ax1[vi].set_title("Date = {:%Y-%B-%d}".format(self.obsTime[2]))
                    ax1[vi].legend(prop={'size':9}, loc=3)
                    #ax1.set_ylim(6.5, 7.5)
                    
                    if len(varsGroup) == 2: 
                        axr.set_ylabel(Groups_Lab[vi][1])
                        axr.legend(prop={'size':9}, loc=4)

                plt.suptitle("Date = {:%Y-%B-%d}".format(self.obsTime[2]), fontsize=16)

                #fig1.autofmt_xdate()
                fig1.subplots_adjust(left=0.1, bottom=0.05, right=0.9, top=0.95)

                    
                if self.pdfFlg: 
                    self.pdfSave.savefig(fig1,dpi=600, bbox_inches='tight')
                else:
                    plt.show(block=False)

    #----------------------------
    # PLOT MEASUREMENT LOG
    #----------------------------
    def plt_Meas(self, fltid=False):

        self.readMeas()

        if self.pltsnrFlg:
        
            fig1, ax1 = plt.subplots(figsize=(8,5))

            colormap = plt.cm.gist_ncar
            #clrs = plt.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 0.9, len(fltid))])

            ax1.set_prop_cycle( cycler('color', [colormap(i) for i in np.linspace(0, 0.9, len(fltid))] ) )


            for i, fl in enumerate(fltid):

                fileName = [str(flt[0:2]) for flt in self.vars['Filename'][0]]
                inds = np.where(np.asarray(fileName) == str(fl))[0]

                if len(inds) >= 1:

                    pltVal = self.vars['SNR_RMS'][0][inds]
                    DT     = self.vars['DT_Meas'][inds]

                    ax1.plot(DT, pltVal, "o" ,markersize=5, linestyle='-', label= fl)

            ax1.set_ylabel('SNR')
            ax1.grid(True)
            ax1.set_xlabel("UT Time[Hours]")
            ax1.xaxis.set_major_locator(HourLocator())
            ax1.xaxis.set_major_formatter(DateFormatter("%H"))
            ax1.xaxis.set_minor_locator(AutoMinorLocator())
            #ax1[vi].set_title("Date = {:%Y-%B-%d}".format(self.obsTime[2]))
            ax1.legend(prop={'size':9}, loc=1)

            plt.suptitle("Date = {:%Y-%B-%d}".format(self.vars['DT_Meas'][2]), fontsize=16)

            fig1.subplots_adjust(left=0.1, bottom=0.1, right=0.95, top=0.93)

                
            if self.pdfFlg: 
                self.pdfSave.savefig(fig1,dpi=600, bbox_inches='tight')
            else:
                plt.show(block=False)

    
#if __name__ == "__main__":
def main(argv):
    #-------------------------------------------
    # ***** INPUTS ******
    #-------------------------------------------
    #site           = 'tab'
    
    pdfFlg         = False               # SAVE PDF FILE
    DynamicFlg     = False              # DYNAMIC
    sleepTime      = 3600                 # SLEEP TIME IN SECONDS (IF DYNAMIC)

    #-------------------------------------------
    # ***** END OF INPUTS ******
    #-------------------------------------------

    now            = dt.datetime.now()
    iyear          = "{0:04d}".format(now.year)
    iday           = "{0:02d}".format(now.day)
    imnth          = "{0:02d}".format(now.month)

    #--------------------------------
    # Retrieve command line arguments
    #--------------------------------
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:m:l:S?')

    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit()

    #-----------------------------
    # Parse command line arguments
    #-----------------------------
    for opt, arg in opts:
        # Check input file flag and path
        if opt == '-d':

            if len(arg) == 8:

                dates   = arg.strip().split()

                iyear   = str(dates[0][0:4])
                imnth   = str(dates[0][4:6])
                iday    = str(dates[0][6:8])

            else:
                print 'Error in input date'
                usage()
                sys.exit()

        # Pause after skip option
        elif opt == '-S':
            
            pdfFlg = True

        elif opt == '-l':

            site = arg.lower()

        elif opt == '-m':

            DynamicFlg = True
            sleepTime = int(arg)
        # Show all command line flags
        elif opt == '-?':
            usage()
            sys.exit()

        else:
            print 'Unhandled option: ' + opt
            sys.exit()

    try:
        Dir  =  '/ya4/id/' + site +'/'   # PATH
    except:
        raise Exception('Must include site: try -l mlo/tab') 

    fltid          = ['s1', 's2', 's3', 's4', 's5', 's6', 's9', 'sa', 'sb']


     #-------------------------------------------
    # VALUES FOR PLOTS
    #-------------------------------------------

    if site.lower() == 'mlo':
        
        #-------------------------------------------
        # VALUES FOR PLOTS
        #-------------------------------------------
        Group_1       = [ ['szenith'], ['sazimuth']]
        Group_2       = [ ['Extern_E_Radiance', 'Extern_W_Radiance'], ['Extern_E_RadianceS', 'Extern_W_RadianceS']]  # --> USE THIS SYNTAX FOR LEFT AND RIGHT AXIS
        Group_3       = [['LN2_Dewar_Pressure'], ['Optic_Bench_Base_T', 'Beamsplitter_Body_T', 'INSB_Body_T', 'MCT_Body_T' ]]       # --> USE THIS SYNTAX FOR LEFT AXIS ONLY
        Group_4       = [ ['Atm_Wind_Speed'], ['Atm_Temperature', 'Laser_T']] 
        Group_5       = [ ['Vacuum_Valve', 'LN2_Fill_Switch', 'SolSeek_Hatch_Position']]

        # LABELS FOR EACH AXIS OF THE ABOVE GROUPS
        Group_1_label = ['Zenith Angle', 'Azimuth Angle']
        Group_2_label = ['Radiance (large sensors)', 'Radiance (small sensors)']
        Group_3_label = ['LN2 Dewar Pressure', 'Temperature']
        Group_4_label = ['Wind Speed', 'Temperature']
        Group_5_label = ['Switch']

        Groups        = [Group_1, Group_2, Group_3, Group_4, Group_5]
        Groups_Lab    = [Group_1_label, Group_2_label, Group_3_label, Group_4_label, Group_5_label]



    elif site.lower() == 'tab':

        Group_1     = [ ['szenith'], ['sazimuth']] # --> USE THIS SYNTAX FOR LEFT AND RIGHT AXIS
        Group_2     = [ ['FXSOL', 'NXSOL'] ] 
        Group_3     = [['LQN2P']]
        Group_4     = [ ['WSPD'], ['OTEMP', 'ELMOT', 'UPSLT', 'ACTUT' ]] 
        Group_5       = [ ['LQDN2', 'HOPNC']]

        Group_1_label = ['Zenith Angle', 'Azimuth Angle']
        Group_2_label = ['Solar Sensor']
        Group_3_label = ['LN2 Dewar Pressure']
        Group_4_label = ['Wind Speed', 'Temperature']
        Group_5_label = ['Switch']

        Groups        = [Group_1, Group_2, Group_3, Group_4, Group_5]
        Groups_Lab    = [Group_1_label, Group_2_label, Group_3_label, Group_4_label, Group_5_label]

    else:
        print '!! ERROR !!: Include Site:' 
        exit()

    if DynamicFlg:

        while True:

            now = dt.datetime.now()

            iyear = "{0:04d}".format(now.year)
            iday = "{0:02d}".format(now.day-1)
            imnth = "{0:02d}".format(now.month)

            d = RemoteHK(Dir=Dir, iyear=iyear,iday=iday, imnth=imnth, pdfFlg=pdfFlg)

            if pdfFlg: d.openFig()

            print 'Plot HK File on: {}-{}-{}'.format(iyear, imnth, iday)
            print 'plotting Date/Time: {}'.format(now)
            
            d.plt_HK( Groups=Groups , Groups_Lab=Groups_Lab )
            d.plt_Meas(fltid=fltid)

            if pdfFlg: 
                d.closeFig()
            else: 
                user_input = raw_input('Press any key to exit >>> ')
                sys.exit()

            time.sleep(sleepTime)

    else:

        d = RemoteHK(Dir=Dir, iyear=iyear,iday=iday, imnth=imnth, pdfFlg=pdfFlg)
        
        if pdfFlg: d.openFig()

        print 'Plot HK File on: {}-{}-{}'.format(iyear, imnth, iday)
        print 'plotting Date/Time: {}'.format(now)
        
        d.plt_HK(Groups=Groups , Groups_Lab=Groups_Lab, showID=True)
        d.plt_Meas(fltid=fltid)
        
    
        if pdfFlg: 
            d.closeFig()
        else:
            user_input = raw_input('Press any key to exit >>> ')
            sys.exit()  

if __name__ == "__main__":
    main(sys.argv[1:])



            
