import sys
sys.path.append('/data/sfit-processing-environment/Lib_MP/')
import read_result_sfit4 as sfit4
from sfit4_ctl import *
from Tkinter import *
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import matplotlib.dates as dates
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2TkAgg
import numpy as np
import os, pdb, string
from load_tmp_h5 import load_tmph5

class show_tmph5:

    def __init__(self,tmph5file='tmp.h5'):


        self.res = load_tmph5(tmph5file)
        self.valid_ind = range(0,len(self.res.dnum))

        
        # out.level = 1
        plt.rcParams['font.size'] = 18
#        plt.rc('text', usetex=True)

        # Find a free figure for profile
        self.columns = plt.figure(figsize=(7,3))#figsize=(24,12))
        self.aux = plt.figure(figsize=(7,3))
        self.vmr = plt.figure(figsize=(7,3))

        self.tkroot = Tk()
        self.tkroot.wm_title('tmph5 result viewer')

        main_frame_1 = Frame(self.tkroot)
        main_frame_2 = Frame(self.tkroot)
        main_frame_1.grid(row=0,column=0)
        main_frame_2.grid(row=0,column=1)

        
        button_quit = Button(main_frame_1, text = 'Quit',
                             command = self.quit)
        button_quit.grid(row=0, column=0, sticky=E+W)

        options = list(set(('CHI_Y_2', 'DOFS', 'CO2', 'E_TOT', 'SNR')))
        frame_show = Frame(main_frame_1)
        frame_show.grid(row=1,column=0)    

        if len(options) > 0:
            self.aux_val = StringVar(frame_show)
            self.aux_val.set(options[0])

            self.menu1 = OptionMenu(frame_show,self.aux_val, 
                                    *options)
            self.menu1.grid(row=0,column=2,stick=E+W)


        button_save = Button(frame_show, 
                             text = 'Save columns', 
                             command = lambda:self.save_values())
        button_save.grid(row=0, column=0, sticky=E+W)

        button_show = Button(frame_show, 
                             text = 'Auxiliary quantity', 
                             command = lambda:self.plot_aux_val())
        button_show.grid(row=0, column=1, sticky=E+W)
        if len(options) == 0:
            button_show.config(state=DISABLED)
#        self.button_spec_by_gas = button_spec

        frame_filter = Frame(main_frame_2)
        frame_filter.grid(row=0,column=0)

        self.min_dofs = Entry(frame_filter)
        self.min_dofs.insert(0,np.min(self.res.dofs))
        self.min_dofs.grid(row=0,column=0,sticky=W)
        filter_dofs = Button(frame_filter, 
                             text = 'DOFS', 
                             command = lambda:self.filter())
        filter_dofs.grid(row=0, column=1, sticky=E+W)
        self.max_dofs = Entry(frame_filter)
        self.max_dofs.insert(10,np.max(self.res.dofs))
        self.max_dofs.grid(row=0,column=2,sticky=E)


        self.min_c2y = Entry(frame_filter)
        self.min_c2y.insert(10,np.min(self.res.c2y))
        self.min_c2y.grid(row=1,column=0,sticky=W)
        filter_c2y = Button(frame_filter, 
                             text = 'CHI_Y 2 ', 
                             command = lambda:self.filter())
        filter_c2y.grid(row=1, column=1, sticky=E+W)
        self.max_c2y = Entry(frame_filter)
        self.max_c2y.insert(10,np.max(self.res.c2y))
        self.max_c2y.grid(row=1,column=2,sticky=E)

        self.min_co2 = Entry(frame_filter)
        self.min_co2.insert(10,np.min(self.res.col_co2))
        self.min_co2.grid(row=2,column=0,sticky=W)
        filter_co2 = Button(frame_filter, 
                             text = 'COL CO2', 
                             command = lambda:self.filter())
        filter_co2.grid(row=2, column=1, sticky=E+W)
        self.max_co2 = Entry(frame_filter)
        self.max_co2.insert(10,np.max(self.res.col_co2))
        self.max_co2.grid(row=2,column=2,sticky=E)

        self.min_vmr = Entry(frame_filter)
        self.min_vmr.insert(10,np.min(self.res.vmr_rt))
        self.min_vmr.grid(row=3,column=0,sticky=W)
        filter_vmr = Button(frame_filter, 
                             text = 'VMR', 
                             command = lambda:self.filter())
        filter_vmr.grid(row=3, column=1, sticky=E+W)
        self.max_vmr = Entry(frame_filter)
        self.max_vmr.insert(10,np.max(self.res.vmr_rt))
        self.max_vmr.grid(row=3,column=2,sticky=E)

        filter_errcol = Button(frame_filter, 
                             text = 'Err Col Tot', 
                             command = lambda:self.filter())
        filter_errcol.grid(row=4, column=1, sticky=E+W)
        self.err_col = Entry(frame_filter)
        self.err_col.insert(10,np.max(self.res.err_tot))
        self.err_col.grid(row=4,column=2,sticky=E)

        frame_check = Frame(main_frame_2)
        frame_check.grid(row=9,column=0)
        filter_errcol = Button(frame_check, 
                               text = 'Error Covariances', 
                               command = lambda:self.filter())
        filter_errcol.grid(row=0, column=0, sticky=W)

        # Bad hack, dont know why it does not work as intended with
        # self.v1 = IntVar()
        # Checkbutton(...,variable=self.v1,...)
        self.v1 = False
        def setv1():
            self.v1 = not self.v1

        rb_pos1 = Checkbutton(frame_check,text="VALID?", command=setv1)
        rb_pos1.grid(row=0,column=1,stick=W)
        
        
        frame2 = Frame(main_frame_1)
        frame2.grid(row=2,column=0)


        
        self.canvas = FigureCanvasTkAgg(self.columns, master=frame2)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        toolbar = NavigationToolbar2TkAgg( self.canvas, frame2 )
        toolbar.update()
        self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=0)
        self.plot_values()
        
        frame3 = Frame(main_frame_1)
        frame3.grid(row=3,column=0)
        self.canvas2 = FigureCanvasTkAgg(self.aux, master=frame3)
        self.canvas2.show()
        self.canvas2.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        toolbar = NavigationToolbar2TkAgg( self.canvas2, frame3 )
        toolbar.update()
        self.canvas2._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        self.plot_aux_val()
        
        frame4 = Frame(main_frame_2)
        frame4.grid(row=10,column=0)
        self.canvas3 = FigureCanvasTkAgg(self.vmr, master=frame4)
        self.canvas3.show()
        self.canvas3.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        toolbar = NavigationToolbar2TkAgg( self.canvas3, frame4 )
        toolbar.update()
        self.canvas3._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        self.plot_vmr()

        self.tkroot.mainloop()

    def printv(self):
        print self.v1.get()
        
    def plot_values(self):
        self.columns.clf()
        self.columns.gca().plot_date(self.res.dnum[self.valid_ind],
                                     self.res.col_rt[self.valid_ind])
        self.columns.gca().errorbar(self.res.dnum[self.valid_ind],
                                    self.res.col_rt[self.valid_ind],
                                    self.res.err_tot[self.valid_ind],
                                    color = 'b', fmt='none')        
        self.canvas.show()

    def save_values(self):
        fid = open('columns_show_and_filter.dat', 'write')
        fid.write('date dnum retr apr ran, sys\n')
        for d,r,a,rr,ss in zip(self.res.dnum[self.valid_ind],
                               self.res.col_rt[self.valid_ind],
                               self.res.col_ap[self.valid_ind],
                               self.res.err_ran[self.valid_ind],
                               self.res.err_sys[self.valid_ind]):
            dstring = dates.num2date(d).strftime('%Y%m%d%H%M%S')
            fid.write('%s %d %g %g %g %g\n'%(dstring, d, r, a, rr, ss))
        fid.close()
            

        
    def plot_vmr(self):
        self.vmr.clf()
        self.vmr.gca().plot(self.res.vmr_rt[:,self.valid_ind], self.res.Z)
        self.canvas3.show()

    def plot_aux_val(self):
        aux = self.aux_val.get()
        self.aux.clf()
        if aux == 'CHI_Y_2':
            self.aux.gca().plot_date(self.res.dnum[self.valid_ind], self.res.c2y[self.valid_ind])
        elif aux == 'DOFS':
            self.aux.gca().plot_date(self.res.dnum[self.valid_ind], self.res.dofs[self.valid_ind])
        elif aux == 'CO2':
            self.aux.gca().plot_date(self.res.dnum[self.valid_ind], self.res.col_co2[self.valid_ind])
        elif aux == 'E_TOT':
            self.aux.gca().plot_date(self.res.dnum[self.valid_ind], self.res.err_tot[self.valid_ind])
        elif aux == 'SNR':
            self.aux.gca().plot_date(self.res.dnum[self.valid_ind], self.res.snr_clc[self.valid_ind], label='SNR CLC')
            self.aux.gca().plot_date(self.res.dnum[self.valid_ind], self.res.snr_the[self.valid_ind], label='SNR THE')
        self.canvas2.show()

    def filter(self):

        # for dofs
        mindofs = self.min_dofs.get()
        maxdofs = self.max_dofs.get()
        try:
            mindofs = string.atof(mindofs)
        except:
            mindofs = 0.0
        try:
            maxdofs = string.atof(maxdofs)
        except:
            maxdofs = 100.0
        
        minc2y = self.min_c2y.get()
        maxc2y = self.max_c2y.get()
        try:
            minc2y = string.atof(minc2y)
        except:
            minc2y = -1000.0
        try:
            maxc2y = string.atof(maxc2y)
        except:
            maxc2y = 1000.0

        minco2 = self.min_co2.get()
        maxco2 = self.max_co2.get()
        try:
            minco2 = string.atof(minco2)
        except:
            minco2 = -1000.0
        try:
            maxco2 = string.atof(maxco2)
        except:
            maxco2 = 1000.0

        minvmr = self.min_vmr.get()
        maxvmr = self.max_vmr.get()
        try:
            minvmr = string.atof(minvmr)
        except:
            minvmr = -1.0
        try:
            maxvmr = string.atof(maxvmr)
        except:
            maxvmr = 1.0

        errcol = self.err_col.get()
        try:
            errcol = string.atof(errcol)
        except:
            errcol = 1.0e99

        self.valid_ind = filter(lambda x: self.res.dofs[x] > mindofs
                                and self.res.dofs[x] < maxdofs
                                and self.res.c2y[x] > minc2y
                                and self.res.c2y[x] < maxc2y
                                and np.min(self.res.vmr_rt[:,x]) > minvmr
                                and np.max(self.res.vmr_rt[:,x]) < maxvmr
                                and self.res.err_tot[x] < errcol
                                and self.res.col_co2[x] > minco2
                                and self.res.col_co2[x] < maxco2, range(0,len(self.res.dnum)))
#        self.valid_ind = np.array(self.valid_ind)


        if self.v1:
            inds = []
            print self.v1
            for v in self.valid_ind:
                try:
                    np.linalg.cholesky(self.res.vmr_ran[:,:,v])
                    np.linalg.cholesky(self.res.vmr_sys[:,:,v])
                    inds.extend(v)
                except:
                    pass

            print 'Error Cov not valid:%d'%(len(self.valid_ind)-len(inds))
            
        self.plot_values()
        self.plot_aux_val()
        self.plot_vmr()

        self.min_dofs.delete(0,END)
        self.min_dofs.insert(0,np.min(self.res.dofs[self.valid_ind]))
        self.max_dofs.delete(0,END)
        self.max_dofs.insert(0,np.max(self.res.dofs[self.valid_ind]))
        self.min_c2y.delete(0,END)
        self.min_c2y.insert(0,np.min(self.res.c2y[self.valid_ind]))
        self.max_c2y.delete(0,END)
        self.max_c2y.insert(0,np.max(self.res.c2y[self.valid_ind]))
        self.min_co2.delete(0,END)
        self.min_co2.insert(0,np.min(self.res.col_co2[self.valid_ind]))
        self.max_co2.delete(0,END)
        self.max_co2.insert(0,np.max(self.res.col_co2[self.valid_ind]))
        self.min_vmr.delete(0,END)
        self.min_vmr.insert(0,np.min(self.res.vmr_rt[:,self.valid_ind]))
        self.max_vmr.delete(0,END)
        self.max_vmr.insert(0,np.max(self.res.vmr_rt[:,self.valid_ind]))
        self.err_col.delete(0,END)
        self.err_col.insert(0,np.max(self.res.err_tot[self.valid_ind]))        


        
    def quit(self):
        self.tkroot.destroy()
        sys.exit()

        
if __name__ == '__main__':

    direc = sys.argv[1]
    show_tmph5(direc)

    
