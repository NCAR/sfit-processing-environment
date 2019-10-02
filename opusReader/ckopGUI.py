#! /usr/bin/python
#----------------------------------------------------------------------------------------
# Name:
#        ckopusGUI.py
#
# Purpose:
#       - GUI Python program to check quaility of spectra
#
# Notes:
#       1) 
#
# Version History:
#       Created, July, 2019  Ivan Ortega (iortega@ucar.edu)
#
#----------------------------------------------------------------------------------------

import sys
import os
import ttk
import datetime       as     dt
import Tkinter        as     tk
from time             import sleep
from tkFileDialog     import askopenfilename
from multiprocessing  import Process
from PIL              import ImageTk

import glob
import subprocess as sp
import numpy as np

import matplotlib.dates as md
import matplotlib.dates as md
from matplotlib.dates import DateFormatter, MonthLocator, YearLocator, DayLocator, WeekdayLocator, MONDAY

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FormatStrFormatter, MultipleLocator,AutoMinorLocator,ScalarFormatter
from matplotlib.backends.backend_pdf import PdfPages #to save multiple pages in 1 pdf...
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import matplotlib.gridspec as gridspec

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
#import matplotlib.backends.backend_tkagg as tkagg


import opusClass as op
import shutil
from os.path import isfile, join, isdir
from cycler import cycler
from   matplotlib.dates import DateFormatter, MonthLocator, YearLocator, DayLocator, HourLocator


def ckDir(dirName,exit=False):
    ''' '''
    if not os.path.exists( dirName ):
        print('Input Directory %s does not exist' % (dirName))
        if exit: sys.exit()
        return False
    else:
        return True

def ckFile(fName,exit=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print ('File %s does not exist' % (fName))
        if exit: sys.exit()
        return False
    else:
        return True

def ckDirMk(dirName):
    ''' '''
    if not ( os.path.exists(dirName) ):
        os.makedirs( dirName)
        os.chmod(dirName, 0o777)
    
    else:
        return True

small_Font   = ("Verdana", 9)
Med_FONT     = ("Verdana", 12)
LARGE_FONT   = ("Verdana", 14)

#----------------------------
# READ MEASUREMENT LOG FILE (internal use at NCAR)
#----------------------------
def readMeas(fname):
    
    #----------------------------
    # File and directory checking
    #----------------------------

    vars      = {}
    MeasFlg = False

    #-----------------------------------------------
    # 
    #-----------------------------------------------

    try:
    
        #-------------------
        # Open and read file
        #-------------------
        with open(fname,"r") as fopen: lines = fopen.readlines()
        
        #---------------
        # Read in Header
        #---------------
        #hdrs = [ val for val in lines[0].strip().split()[:]]
        #hdrs   = ['Measurement_Time', 'Filename', 'SNR_RMS', 'Peak_Amplitude', 'Pre_Amp_Gain', 'Signal_Gain']#, 'Ext_E_Rad', 'Ext_E_RadS', 'Ext_W_Rad', 'Ext_E_Rads']
        hdrs   = ['Measurement_Time', 'Filename', 'SNR_RMS', 'Peak_Amplitude', 'Pre_Amp_Gain', 'Signal_Gain']
         
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
        vars['Time_Meas'] = np.array([dt.datetime(2019,7,1, int(line[0:2]),int(line[3:5]),int(line[6:8])) for line in lines[1:-2] ])

        if len(vars['Time_Meas']) >= 1: MeasFlg = True

        for i, v in enumerate(idVal):
            try:
                vars.setdefault(v,[]).append(np.asarray([float(line.strip().split()[i]) for line in lines[1:-2] ]) )
            except:
                vars.setdefault(v,[]).append(np.asarray([line.strip().split()[i] for line in lines[1:-2] ]) )

        for i, v in enumerate(idVal):
            vars[v] = vars[v][0]

        MeasFlg  = True   

        return vars

    except Exception as errmsg:
        print('Error reading Measurement.log: ', errmsg)
        return False


class ckopusGUI(tk.Frame):
    
    def __init__(self,parent):
        tk.Frame.__init__(self,parent,background="white")

        #self.path         = '/ya4/id/'

        self.parent       = parent
        self.initialize()
               
        
    def initialize(self):
        self.grid()
        self.parent.title("NCAR FTS PyCkop GUI")
        #self.pack(fill=tk.BOTH,expand=1)        
        self.addButtons()
        #self.addCheckBox()
        self.addInputBox()
        self.addTextBox1()
        self.addTextBox2()
        
        #self.loopCam()
        self.centerWindow()

        #self.main_container = tk.Frame(self.parent, height=10, width=100)
        #self.main_container.pack(side="top", fill="both", expand=True)
        #self.matplotlib_frame = tk.Frame(self.main_container)

        #self.ReadSpc()
        self.addPltBox()
        self.addPltBox2()
        
    def textCallBack(self,textString):
        self.textBox.insert(tk.END,textString)
        self.textBox.see(tk.END)

    def textCallBack2(self,textString, font=small_Font):
        self.textBox2.insert(tk.END,textString)
        self.textBox2.see(tk.END)

    #def addTextBox1(self, font=small_Font):
    #    self.textBox = tk.Text(self, font=font)
    #    self.textBox.grid(row=5,column=0,columnspan=3,sticky='nsew')

    #def addTextBox2(self, font=small_Font):
    #    self.textBox2 = tk.Text(self, font=font)
    #    self.textBox2.grid(row=5,column=2,columnspan=2,sticky='nsew')

    def addTextBox1(self):
        self.textBox = tk.Text(self, height=20, width=70)
        self.textBox.grid(row=5,column=0,columnspan=3,sticky='nsew')

    def addTextBox2(self):
        self.textBox2 = tk.Text(self, height=20, width=70)
        self.textBox2.grid(row=5,column=3,columnspan=3,sticky='nsew')
        #self.textBox.grid(row=4,column=0)

    def addInputBox(self):
        #-------------------------
        # Add input for angle step
        #-------------------------
        labelSite = tk.Label(self, text="Site", font=Med_FONT)
        labelSite.grid(row=1,column=0)
        self.valSite   = tk.Entry(self, font=Med_FONT, width=12)
        self.valSite.insert(0, "MLO")
        self.valSite.grid(row=2,column=0)

        #-------------------------
        # Add input for angle step
        #-------------------------
        labelDate = tk.Label(self, text="Date", font=Med_FONT)
        labelDate.grid(row=1,column=1)
        self.valDate   = tk.Entry(self, font=Med_FONT, width=12)
        self.valDate.insert(0, "20190709")
        self.valDate.grid(row=2,column=1)

        #-------------------------
        # Add input for angle step
        #-------------------------
        labelGoto = tk.Label(self, text="GoTo", font=Med_FONT)
        labelGoto.grid(row=1,column=2)
        self.valgoto   = tk.Entry(self, font=Med_FONT, width=12)
        self.valgoto.insert(0, 0)
        self.valgoto.grid(row=2,column=2)

        #-------------------------
        # Add input for angle step
        #-------------------------
        labelPath = tk.Label(self, text="Path", font=Med_FONT)
        labelPath.grid(row=1,column=3)
        self.valpath   = tk.Entry(self, font=Med_FONT, width=12)
        self.valpath.insert(0, '/ya4/id/')
        self.valpath.grid(row=2,column=3)

        
      
    def addButtons(self):

        #------------------------
        # Add find ellipse button
        #------------------------
        StartButton =  tk.Button(self,text="Start",command=self.StartButton)
        StartButton.grid(row=3,column=0)

        #--------------------------
        # Add connect to ESP button
        #--------------------------
        #DeleteButton =  tk.Button(self,text="Delete", fg='white', bg='red', command=self.DeleteButton)
        #DeleteButton.grid(row=3,column=1)

        DeleteButton =  tk.Button(self,text="Delete", command=self.DeleteButton)
        DeleteButton.grid(row=3,column=1)
        

        #----------------
        # Add quit button
        #----------------
        quitButton = tk.Button(self,text="Quit",command=self.quitGUI)
        quitButton.grid(row=3,column=2)

        #------------------------
        # Add find ellipse button
        #------------------------
        NextButton =  tk.Button(self,text="Next >",command=self.NextButton)
        NextButton.grid(row=4,column=0)

        #------------------------
        # Add find ellipse button
        #------------------------
        PreviousButton =  tk.Button(self,text="Previous <",command=self.PreviousButton)
        PreviousButton.grid(row=4,column=1)

        #------------------------
        # Add find ellipse button
        #------------------------
        PrintButton =  tk.Button(self,text="Print",command=self.PrintButton)
        PrintButton.grid(row=4,column=2)

        #------------------------
        # Add plt Measurement log
        #------------------------
        PltMeasButton =  tk.Button(self,text="PltLog",command=self.PltMeasButton)
        PltMeasButton.grid(row=4,column=3)

        #------------------------
        # Add Auto Check
        #------------------------
        AutoCheck =  tk.Button(self,text="Auto-Check",command=self.AutoCheck)
        AutoCheck.grid(row=3,column=4)


    def addPltBox(self):

        #self.event_num = int(self.valgoto.get())
        
        #self.fig, self.ax = plt.subplots()

        self.fig, self.ax1  = plt.subplots(figsize=(10,4.5))

        self.plt = []
        
        self.canvas=FigureCanvasTkAgg(self.fig, self.parent)
        self.canvas.get_tk_widget().grid(row=4,column=0)

        #self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


        self.ax1.axis("off")

        #self.toolbar = NavigationToolbar2Tk(self.canvas, self.parent)
        #self.toolbar.update()
        #self.canvas._tkcanvas.pack(anchor=tk.W, side=tk.TOP, fill=tk.BOTH, expand=1)


        
        #canvas.get_tk_widget().grid(row=4,column=0)
        #self.canvas.draw()
        

        #self.line,       = self.ax.plot(self.spc['wn'][self.event_num],self.spc['int'][self.event_num])
        #self.canvas.show()

        #self.plotbutton=tk.Button(self.parent, text="Start", command=lambda: self.plot(canvas,ax))
        #self.plotbutton.grid(row=1,column=2)

        #self.plotbutton=tk.Button(self.parent, text="Delete", command=lambda: self.plot(canvas,ax))
        #self.plotbutton.grid(row=0,column=0)

    def addPltBox2(self):

        #self.event_num = int(self.valgoto.get())
        
        #self.fig, self.ax = plt.subplots()

        self.fig2, self.ax2  = plt.subplots(figsize=(10,3))

        self.plt2 = []
        
        self.canvas2=FigureCanvasTkAgg(self.fig2, self.parent)
        self.canvas2.get_tk_widget().grid(row=5,column=0)

        #self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


        self.ax2.axis("off")

        #self.colormap = plt.cm.gist_ncar

    def quitGUI(self):

        exit()
        self.parent.destroy()

        

    def centerWindow(self):
        w = 1000
        h = 1150
    
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
    
        x = (sw - w)/2
        y = (sh - h)/2
        
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))


    #----------------------
    # Define button actions
    #----------------------
    def StartButton(self):

        self.textBox.delete(1.0,tk.END)
        self.textBox2.delete(1.0,tk.END)

        self.date = self.valDate.get()
        self.site = self.valSite.get()
        self.path = self.valpath.get()

        self.event_num = int(self.valgoto.get())

        if not( self.path.endswith('/') ):
            self.path = self.path + '/'
        
        self.dataDir = self.path + self.site .lower() + '/' + self.date + '/'

        if not ckDir(self.dataDir, exit=False): self.textCallBack("Input Directory {0:} does not exist\n".format(self.dataDir)) 

        #-------------------
        #Creating list of files
        #-------------------
        self.opusFiles = glob.glob(self.dataDir + 's*.*')
        self.opusFiles.sort()


        self.textCallBack("# of OPUS files in {0:} = {1:}\n".format(self.dataDir,len(self.opusFiles))) 

        if len(self.opusFiles) >=1:
            self.readPltSpc()
       
        else: self.textCallBack("Go to Next day!")
            

    #----------------------
    # Define button actions
    #----------------------
    def DeleteButton(self):

        if not( self.dataDir.endswith('/') ):
            self.dataDir = self.dataDir + '/'

        delDir   = self.dataDir + 'deleted'

        ckDirMk(delDir)         
        
        try:
            self.textCallBack2('\nmv file: {} to {}'.format(self.fname, delDir))
            shutil.move(self.fname, delDir)

        except shutil.Error as e:
            self.textCallBack2('\n{}'.format(e))

        #try:
        #    os.chmod(join(delDir,self.opus.name), 0o766)
        #except shutil.Error as e:
        #    self.textCallBack2('\n{}'.format(e))

        #self.NextButton()


    def PrintButton(self):

        file = self.fname + '.dat'

        data = np.asarray([np.asarray(self.opus.spc['w'][self.opus.indsS], dtype=np.float64), np.asarray(self.opus.spc['ORG'][self.opus.indsS], dtype=np.float64)])
        data = data.T

        try:
            self.textCallBack2("\nSaving file: {}".format(file))

            with open(file, 'w+') as i:
                np.savetxt(i, data, fmt=['%.10f','%.15f'])

        except:
            'Error while saving {}'.format(file)




    def readPltSpc(self):

        if self.event_num >= len(self.opusFiles):
            
            self.textCallBack("Even Number > Number of files")
            
            currDay = dt.date(int(self.date[0:4]), int(self.date[4:6]), int(self.date[6:8]))
            nextDay = currDay + dt.timedelta(days=1)

        
            self.valDate.delete(0,20)
            self.valDate.insert(0, str(nextDay.strftime('%Y%m%d')))
            self.StartButton()

        self.textCallBack("OPUS file # {0:} out of {1:}\n".format(self.event_num,len(self.opusFiles))) 


        self.fname = self.opusFiles[self.event_num]

        file_size = os.path.getsize(self.fname)
        
        if file_size/1e6 <= 1.: 
            print ('Size of opus file {} is < 1e6 bytes'.format(self.fname))
            self.DeleteButton()

        else:
            
            self.opus  = op.readOPUS(self.fname)

            self.opus.readspec(verbFlg=False)
            self.opus.readOPT(verbFlg=False)
            self.opus.getspc()
            #opus.opt.sort()

            #-----------------------
            # ControlNCAR -- NCAR specific
            #-----------------------
            self.opus.controlNCAR()

            #-----------------------
            # ControlNCAR -- NCAR specific
            #-----------------------
            self.textCallBack("File: {0:}\n".format(self.fname))

            optOFI = ['APT','BMS','DTC','LPF', 'OPF', 'SRC', 'VEL']

            for k in optOFI:
                self.textCallBack("{0:} = {1:}\n".format(k,self.opus.opt[k])) 

            optOFI = ['TPX','FXV', 'LXV', 'MNY', 'MXY', 'DXU', 'DAT', 'TIM']

            for k in optOFI:
                self.textCallBack("{0:} = {1:}\n".format(k,self.opus.spc[k])) 

            self.textCallBack2("{0:<15} = {1:<.3f}\n".format('Signal (maxY)',self.opus.signal)) 
            self.textCallBack2("{0:<15} = {1:<.5f}\n".format('Noise (rms)  ',self.opus.noiseRMS))
            self.textCallBack2("{0:<15} = {1:<.5f}\n".format('Noise (std)',self.opus.noiseSD)) 
            self.textCallBack2("{0:<15} = {1:<.3f}\n".format('SNR (rms)',self.opus.SNRrms)) 
            self.textCallBack2("{0:<15} = {1:<.3f}\n".format('SNR (std)',self.opus.SNRsd))
            self.textCallBack2("{0:<15} = {1:<.4f}\n".format('Ratio (n/p)',self.opus.Ratio))
            self.textCallBack2("{0:<15} = {1:}\n".format('Quality Comment',self.opus.comment)) 
            self.textCallBack2("{0:<15} = {1:}\n".format('Quality Flag',self.opus.qflag)) 

            # #-------------
            # #-------------
            # #    PLOT
            # #-------------
            # #-------------

            self.ax1.axis('on')
            self.ax1.clear()
            #self.fig.draw()
     
            self.ax1.plot(self.opus.spc['w'][self.opus.indsS], self.opus.spc['ORG'][self.opus.indsS], linewidth=1.0)
            self.ax1.set_title(self.fname)
            #ax.set_xlim((np.min(dataSpec['WaveN_'+x]),np.max(dataSpec['WaveN_'+x])))    
            self.ax1.grid(True, alpha=0.5)
            self.ax1.tick_params(which='both',labelsize=12)
            #ax1.legend(prop={'size':11})
            self.ax1.set_ylabel('Intensity [a.u]', fontsize=12)
            self.ax1.set_xlabel('Wavenumber [cm$^{-1}$]', fontsize=12)
            self.ax1.set_xlim(self.opus.waverange[0], self.opus.waverange[1])
            self.ax1.annotate('SNR$_{0:}$:{1:.1f}'.format('{std}',self.opus.SNRsd), xy=(0.025, 0.95), xycoords='axes fraction', fontsize=14, ha='left')
            self.ax1.annotate('Ratio:{0:.4f}'.format(self.opus.Ratio), xy=(0.025, 0.88), xycoords='axes fraction', fontsize=14, ha='left')
            self.ax1.annotate('qComm:{0:}'.format(self.opus.comment), xy=(0.025, 0.81), xycoords='axes fraction', fontsize=14, ha='left')

            self.fig.subplots_adjust(left=0.1, bottom=0.15, right=0.95, top=0.93)
            #ax1.set_ylim(ymin=)

            #canvas = FigureCanvasTkAgg(fig, self.parent)
            
            #canvas.get_tk_widget().grid(row=4,column=0)
            self.canvas.draw()
            #canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


            # toolbar = NavigationToolbar2Tk(canvas, self.parent)
            # toolbar.update()

            # #canvas._tkcanvas.pack(anchor=tk.W, side=tk.BOTTOM, fill=tk.X, expand=False)
            # canvas._tkcanvas.pack(side=tk.BOTTOM, expand=False)


            #canvas.mpl_connect("key_press_event", self.on_key_press)
#            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            #plt.show(block=True)

            
        #toolbar = NavigationToolbar2TkAgg(canvas, self)
        #toolbar.update()
        #canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        #plt.show(block=False)  


        #user_input = raw_input('Press any key to exit >>> ')
        
        #self.startCkopus()
        #print 'Start Button'

        #self.addPltBox()

    def on_key_press(event):
        print("you pressed {}".format(event.key))
        key_press_handler(event, canvas, toolbar)


    

    #----------------------
    # Define button actions
    #----------------------
    def PltMeasButton(self):

        date = self.valDate.get()
        site = self.valSite.get()
        path = self.valpath.get()

        if not( path.endswith('/') ):
            path = path + '/'
        
        dataDir = path + site .lower() + '/' + date + '/'

        LogFname = dataDir + 'Measurement.log'


        fltid          = ['s0','s1', 's2', 's3', 's4', 's5', 's6', 's9','sa', 'sb']

        if not ckFile(LogFname): print("Measurement Log file {0:} does not exist\n".format(LogFname)) 

        mVars = readMeas(LogFname)

        #fig, ax1 = plt.subplots(figsize=(10,3))

        colormap = plt.cm.gist_ncar

        
        self.ax2.axis('on')
        self.ax2.clear()
       #clrs = plt.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 0.9, len(fltid))])
        self.ax2.set_prop_cycle( cycler('color', [colormap(i) for i in np.linspace(0, 0.9, len(fltid))] ) )


        for i, fl in enumerate(fltid):

            fileName = [str(flt[0:2]) for flt in mVars['Filename']]
            inds = np.where(np.asarray(fileName) == str(fl))[0]

            if len(inds) >= 1:

                pltVal = mVars['SNR_RMS'][inds]
                DT     = mVars['Time_Meas'][inds]

                self.ax2.plot(DT, pltVal, "o" ,markersize=5, linestyle='-', label= fl)

        self.ax2.set_ylabel('SNR', fontsize=12)
        self.ax2.grid(True)
        self.ax2.set_xlabel("UT Time[Hours]", fontsize=12)
        self.ax2.xaxis.set_major_locator(HourLocator())
        self.ax2.xaxis.set_major_formatter(DateFormatter("%H"))
        self.ax2.xaxis.set_minor_locator(AutoMinorLocator())
        self.ax2.tick_params(which='both',labelsize=12)
        #ax1[vi].set_title("Date = {:%Y-%B-%d}".format(self.obsTime[2]))
        self.ax2.legend(prop={'size':9}, loc=1)
        self.fig2.subplots_adjust(left=0.1, bottom=0.19, right=0.95, top=0.93)

        #canvas = FigureCanvasTkAgg(fig, self.parent)
        
        #canvas.get_tk_widget().grid(row=5,column=0)
        #canvas.show()

        self.canvas2.draw()

        # toolbar = NavigationToolbar2Tk(canvas, self.parent)
        # toolbar.update()

        # canvas.mpl_connect("key_press_event", self.on_key_press)

        #plt.show()

        #plt.suptitle("Date = {:%Y-%B-%d}".format(self.vars['DT_Meas'][2]), fontsize=16)

    
        #ax1.set_ylim(ymin=)

    def NextButton(self):

        self.textBox.delete(1.0,tk.END)
        self.textBox2.delete(1.0,tk.END)
        
        self.event_num += 1 
        self.readPltSpc()

    def PreviousButton(self):

        self.textBox.delete(1.0,tk.END)
        self.textBox2.delete(1.0,tk.END)
        
        self.event_num -= 1
        self.readPltSpc()

    def AutoCheck(self):
        print('In Construction')



def main():
    
    #-----------------------
    # Initialize root window
    #-----------------------
    root = tk.Tk()
    #root.geometry('500x500')
    
    #---------------
    # Initialize GUI
    #---------------
    app  = ckopusGUI(root)
    root.mainloop() 

    
if __name__ == "__main__":
    main()

