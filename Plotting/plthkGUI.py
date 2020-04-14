#! /usr/bin/python
#----------------------------------------------------------------------------------------
# Name:
#        plthkGUI.py
#
# Purpose:
#       Program to plot HK and automatically updates
#
# Notes:
#       1) It will create plots within one hour from last entry in house files
#
#
#----------------------------------------------------------------------------------------
import sys
import os
import datetime       as     dt

try:
    import Tkinter as tk # this is for python2
    import ttk
    from tkFileDialog     import askopenfilename
except:
    import tkinter as tk # this is for python3
    from tkinter import ttk

from time             import sleep
from multiprocessing  import Process

import glob
import subprocess as sp
import numpy as np

import matplotlib

import matplotlib.dates as md
from matplotlib.dates import DateFormatter, MonthLocator, YearLocator, DayLocator, WeekdayLocator, MONDAY

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FormatStrFormatter, MultipleLocator,AutoMinorLocator,ScalarFormatter
from matplotlib.backends.backend_pdf import PdfPages 
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.cm as mplcm
import matplotlib.colors as colors
import matplotlib.gridspec as gridspec

import matplotlib.backends.backend_tkagg as tkagg

import shutil
from os.path import isfile, join, isdir


def ckDir(dirName,exit=False):
    ''' '''
    if not os.path.exists(dirName):
        print ('Input Directory %s does not exist' % (dirName))
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

class appGUI(tk.Frame):
    
    def __init__(self,parent):
        
        tk.Frame.__init__(self,parent,background="white")

        #-------------------------------------------
        #   ********* HARD CODED INPUT *********
        #-------------------------------------------
        #self.dir            = '/home/tabftir/daily/'    # path 
        self.dir            = '/ya4/id/tab/'    # path 

        #-------------------------------------------
        # VARIABLES 
        #-------------------------------------------
        Group_1        = [ ['szenith'] ] 
        Group_2        = [ ['FXSOL', 'NXSOL'] ] 
        Group_3        = [ ['WSPD'] ] 
        Group_4        = [ ['OTEMP', 'ELMOT', 'UPSLT', 'ACTUT', 'LOSLT' ] ]  
        Group_5        = [ ['LQDN2', 'HOPNC'] ]
        
        #-------------------------------------------
        # LABELS FOR EACH AXIS OF THE ABOVE GROUPS
        #-------------------------------------------
        Group_1_label  = ['Zenith Angle']
        Group_2_label  = ['Solar Sensor']
        Group_3_label  = ['Wind Speed [m/s]']
        Group_4_label  = ['Temperature [C]']
        Group_5_label  = ['Switch']

        #-------------------------------------------
        #      
        #-------------------------------------------
        self.Groups        = [Group_1, Group_2, Group_3, Group_4, Group_5]
        self.Groups_Lab    = [Group_1_label, Group_2_label, Group_3_label, Group_4_label, Group_5_label]
        
        self.parent       = parent
        self.initialize()
    
    def initialize(self):

        self.grid()
        self.parent.title("HK-GUI")      
        self.addPltBox()
        self.addInputBox()
        self.addButtons()
       
    def addPltBox(self):
        
        Npanels             = len(self.Groups)
        self.clr1           = ['r', 'b', 'g', 'brown', 'aqua', 'yellow']

        self.ini   = 0  
    
        self.fig1, self.ax1  = plt.subplots(Npanels, figsize=(8,10), sharex=True)
        self.fig1.autofmt_xdate()
        self.fig1.subplots_adjust(left=0.1, bottom=0.05, right=0.95, top=0.95)
        
        for vi, varsGroup in enumerate(self.Groups):
            self.ax1[vi].set_ylabel(self.Groups_Lab[vi][0])
            self.ax1[vi].grid(True)
            #self.ax1[-1].set_xlabel("UT Time[Hours]")      
            #self.ax1[vi].xaxis.set_major_formatter(DateFormatter("%d/%m\n%H:%M"))
            self.ax1[vi].xaxis.set_major_formatter(DateFormatter("%H:%M"))
            self.ax1[vi].xaxis.set_minor_locator(AutoMinorLocator())

    def addInputBox(self):
        #-------------------------
        # 
        #-------------------------
        delay = tk.Label(self, text="Delay [seconds]")
        delay.grid(row=1,column=0)
        self.valdelay   = tk.Entry(self, width=10)
        self.valdelay.insert(0, "30")
        self.valdelay.grid(row=2,column=0)
        
        #-------------------------
        # 
        #-------------------------
        timeframe = tk.Label(self, text="Time Frame [hours]")
        timeframe.grid(row=1,column=1)
        self.valtimeframe   = tk.Entry(self, width=10)
        self.valtimeframe.insert(0, "1")
        self.valtimeframe.grid(row=2,column=1)  
            
    def addButtons(self):

        StartButton =  ttk.Button(self,text="Plot",command=self.StartHK)
        StartButton.grid(row=4,column=0)

        quitButton = ttk.Button(self,text="Quit",command=self.quitGUI)
        quitButton.grid(row=4,column=1)
    
   
    def quitGUI(self):

        exit()
        self.parent.destroy()
 
    def StartHK(self):

        delay    = int(self.valdelay.get())
        
        #now = dt.datetime.now()
        now = dt.datetime(2020, 3,1)
        self.iyear = "{0:04d}".format(now.year)
        self.iday  = "{0:02d}".format(now.day)
        self.imnth = "{0:02d}".format(now.month)

        self.readHK(iyear=self.iyear, iday=self.iday, imnth=self.imnth)
        self.plt_HK()
        self.fig1.canvas.draw()
        self.ini+=1

        self.parent.after(delay*1000,self.StartHK)  

    def plt_HK(self):
   
        try:
            frametimeh    = float(self.valtimeframe.get())
            fdate = dt.datetime(int(self.iyear), int(self.imnth), int(self.iday), int(self.obsTime[-1].hour), int(self.obsTime[-1].minute), int(self.obsTime[-1].second)  )
            idate = fdate - dt.timedelta(hours=frametimeh)
       
            for vi, varsGroup in enumerate(self.Groups):
                
                self.ax1[vi].cla()
                
                if len(varsGroup) == 1:
                
                    for i, v in enumerate(varsGroup):

                        for j, k in enumerate(v):
                                  
                            pltVal  = np.asarray(self.vars[k][0])
                            
                            if pltVal.dtype is np.dtype(np.float64):

                                self.ax1[vi].plot(self.obsTime,pltVal,"." ,markersize=4, label = k, color=self.clr1[j])
                                
                                if vi == 3: 
                                    inds = np.where((self.obsTime >= idate) & (self.obsTime <= fdate))[0]

                                    if k == 'OTEMP': ymin = np.min(pltVal[inds])
                                    if k == 'ELMOT': ymax = np.max(pltVal[inds])
                             
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

                                self.ax1[vi].plot(self.obsTime,pltVal2,"." ,markersize=1, label= k, color=self.clr1[j]) 
                                
                    self.ax1[vi].text(0.05,0.8,'0 = OFF/CLOSE', transform=self.ax1[vi].transAxes, )
                    self.ax1[vi].text(0.05,0.7,'1 = ON/OPEN', transform=self.ax1[vi].transAxes)
                    self.ax1[vi].text(0.05,0.6,'-1 = UNKN/OTHER', transform=self.ax1[vi].transAxes)
                    self.ax1[-1].set_ylim(-0.05, 1.05)                              
                    self.ax1[vi].legend(prop={'size':10}, loc='center', bbox_to_anchor=(0.5,1.1), ncol=5)
                    self.ax1[vi].set_xlim(idate, fdate)
                    self.ax1[vi].set_ylabel(self.Groups_Lab[vi][0])
                    self.ax1[vi].grid(True)
                    self.ax1[vi].xaxis.set_major_formatter(DateFormatter("%H:%M"))
                    self.ax1[vi].xaxis.set_minor_locator(AutoMinorLocator())
                    if vi ==3: self.ax1[3].set_ylim(ymin-ymin*0.15, ymax+np.abs(ymax*0.15))  
                    self.fig1.autofmt_xdate()
                    self.fig1.subplots_adjust(left=0.11, bottom=0.075, right=0.95, top=0.95)
                
                    self.fig1.show()
            
        #except: pass
        except Exception as errmsg:
            print 'Error reading house.log: ', errmsg  

    #----------------------------
    # READ HK
    #----------------------------
    def readHK(self, iyear='',iday='', imnth=''):

        self.date       = str(iyear) + str(imnth) + str(iday) 
        
        self.iyear      = iyear
        self.imnth      = imnth
        self.iday       = iday
           
        self.vars   = {}

        ckDir(self.dir, exit=False)

        self.hkFlg  = False

        #-----------------------------------------------
        # 
        #-----------------------------------------------
        self.fname = self.dir + self.date + '/house.log'
     
        
        try:


            #-------------------
            # Open and read file
            #-------------------
            with open(self.fname,"r") as fopen: lines = fopen.readlines()
        
            #---------------
            # Read in Header
            #---------------
            for line in lines:
                if line.strip().startswith("#$ date"):
                                #if line.strip().startswith("# date"):
                    hdrs = [ val for val in line.strip().split()[3:]]
                    pass
         
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
            self.obsTime = np.array([dt.datetime(int(line[0:4]),int(line[4:6]),int(line[6:8]),
                                        int(line[9:11]),int(line[12:14]),int(line[15:17])) for line in lines[:-2] if (not line.startswith("#"))])

            for i, v in enumerate(idVal):
                try:
                    self.vars.setdefault(v,[]).append(np.array([float(line.strip().split()[i+2]) for line in lines[:-2] if not line.startswith("#")]))
                except ValueError:
                                      
                    self.vars.setdefault(v,[]).append(np.array([line.strip().split()[i+2] for line in lines[:-2] if not line.startswith("#")]))
            
            self.hkFlg  = True
        
            fopen.close()
         
        #except Exception as errmsg:
        #    print 'Error reading house.log: ', errmsg   
        except:  pass 


def main():
    
    #-----------------------
    # Initialize root window
    #-----------------------
    root = tk.Tk()
    
    #---------------
    # Initialize GUI
    #---------------
    app  = appGUI(root)
    root.mainloop() 
    
if __name__ == "__main__":
    main()
