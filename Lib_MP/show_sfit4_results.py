import sys
sys.path.append('/data/sfit-processing-environment/Lib_MP/')
import read_result_sfit4 as sfit4
from sfit4_ctl import *
from Tkinter import *
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import matplotlib.gridspec as gridspec
import numpy as np
import os, pdb


class show_results:

    def __init__(self,direc='.', ctlfile='sfit4.ctl'):

        self.direc = direc
        self.ctlfile = ctlfile


        # out.level = 1
        plt.rcParams['font.size'] = 18
#        plt.rc('text', usetex=True)


        self.load_result()

        # Find a free figure for profile
        self.winprf = plt.figure()#figsize=(24,12))
        # Find a free figure for microwindow
        self.winmw = plt.figure()#figsize=(24,12))
        # Find a free figure for AVK
        self.winavk = plt.figure()#figsize=(24,12))

    

        self.tkroot = Tk()
        self.tkroot.wm_title('sfit4 result viewer')

        self.entry = Entry(self.tkroot)
        self.entry.grid(row=0, column=1, sticky=E+W)
        self.entry.delete(0, END)
        self.entry.insert(0, os.path.abspath(self.direc))
#        self.update_dirlist()

        button_update = Button(self.tkroot, text = 'Reload', command = self.load_result)
        button_update.grid(row=0, column=0, sticky=E+W)
        button_update.config(state=DISABLED)
#        button_update.pack()

        options = []
        for n in range(0,self.sp.nr_mw):
            options.append(int('%i'%(n+1)))


        def spectrum_show():
            nr = int(self.spec_nr.get())
            self.show_spectra(nr)

        frame1 = Frame(self.tkroot)
        frame1.grid(row=1,column=1)
        self.spec_nr = IntVar(self.tkroot)
        self.spec_nr.set(options[0])
        for n in options:
            m=Radiobutton(frame1,
                          text=str(n),
                          variable=self.spec_nr,
                          value=int(n),
                          indicatoron=1)
            m.grid(row=0,column=n-1,stick=E+W)


            button_spec = Button(self.tkroot, text = 'Spectrum', 
                                 command = lambda: spectrum_show())
        button_spec.grid(row=1, column=0, sticky=E+W)

        def spectrum_by_gas_show():
            nr = int(self.spec_nr.get())
            gas = self.spec_gas.get()
            self.show_spectra_by_gas(1,-1,nr,gas=gas) 

        
        options = list(set(self.gas.gas[:]))

        if len(options) > 0:
            self.spec_gas = StringVar(self.tkroot)
            self.spec_gas.set(options[0])

            self.menu1 = OptionMenu(self.tkroot,self.spec_gas, 
                                    *options)
            self.menu1.grid(row=2,column=1,stick=E+W)


        button_spec = Button(self.tkroot, 
                             text = 'Spectrum by gas', 
                             command = lambda: spectrum_by_gas_show())
        button_spec.grid(row=2, column=0, sticky=E+W)
        if len(options) == 0:
            button_spec.config(state=DISABLED)


        options =  ('Profile', 'AVK')
        self.show_var = StringVar(self.tkroot)
        self.show_var.set(options[0])
        frame2 = Frame(self.tkroot)
        frame2.grid(row=3,column=1)
        num = 0
        for n in options:
            m=Radiobutton(frame2,
                          text=str(n),
                          variable=self.show_var,
                          value=n,
                          indicatoron=0)
            m.grid(row=0,column=num,stick=E+W)
            num = num+1
#        self.menu1 = OptionMenu(self.tkroot,self.show_var, *options)
#        self.menu1.grid(row=3,column=1,stick=E+W)

        def profile_show():
            if self.show_var.get() == 'Profile':
                self.show()
            if self.show_var.get() == 'AVK':
                self.show(type='avk')

        button_profile = Button(self.tkroot, text = 'Profile', command = lambda: profile_show())
        button_profile.grid(row=3, column=0, sticky=E+W)

        button_summary = Button(self.tkroot, text = 'Summary')
        button_summary.grid(row=4, column=0, sticky=E+W)

        button_quit = Button(self.tkroot, text = 'Quit', command = self.tkroot.quit)
        button_quit.grid(row=5, column=0, sticky=E+W)

# #        self.SummaryText()
# #        self.mkOptionMenu1()

        self.tkroot.mainloop()

    def quit(self):
        self.tkroot.destroy()


    def SummaryText(self):
        tt1 = Text(self.tkroot)
        nr_mw = self.sp.nr_mw
        tt1.insert('end', 'Nr. of microwindows %i'%nr_mw)
        tt1.pack()

    def mkOptionMenu1(self):
        nr_mw = self.sp.nr_mw
        opt = []
        for n in range(0,nr_mw):
            opt.append('Spectrum MW %i'%(n+1))
        opt.append('Profile')
        opt.append('AVK')
        opt.append('Summary')

        try:
            self.menu1.destroy
        except:
            pass
        var = StringVar()
        var.set(opt[0])
        self.menu1 = OptionMenu(self.tkroot,var, *opt,command=self.menu1)
        self.menu1.pack()

        

    def load_result(self):
        direc = self.direc
        ctlfile = self.ctlfile
        ctl = sfit4_ctl()
        ctl.read_ctl_file(ctlfile)
        ak_m = ctl.get_value('file.out.ak_matrix')
        if ak_m == -1:
            ak_m = 'ak.out' # Default name of ak_matrix
        self.retprf = sfit4.read_table(direc+'/rprfs.table')
        self.aprprf = sfit4.read_table(direc+'/aprfs.table')
        self.gases = self.aprprf.get_retrieval_gasnames()
        self.sp = sfit4.pbp(direc+'/pbpfile')
        if os.path.exists(direc+'/'+ak_m):
            self.avk = sfit4.avk(direc+'/'+ak_m, direc+'/aprfs.table')
        elif os.path.exists(direc+'/ak.target'):
            self.avk = sfit4.avk(direc+'/ak.target', direc+'/aprfs.table')
        else:
            self.avk = -1
#        self.error = sfit4.error(direc+'/smeas.target',direc+'/aprfs.table')
        try:
            self.error = sfit4.error(direc+'/smeas.target',direc+'/aprfs.table')
        except:
            pass

        self.gas = sfit4.gasspectra(direc)




    def __del__(self):
        plt.close(self.winprf)
        plt.close(self.winmw)
        plt.close(self.winavk)

    def show(self, type='vmr', nr = 0):
        if (type == 'vmr' or type=='target'):
            try:
                self.winprf.clf()
                self.winprf.show()
            except:
                self.winprf=plt.figure()
            if (type == 'vmr'):
                ax = self.winprf.add_subplot(121)
            else:
                ax = self.winprf.add_subplot(111)
            vmr,z = self.retprf.get_gas_vmr(self.gases[0])
            apr,z = self.aprprf.get_gas_vmr(self.gases[0])
            l = ax.plot(vmr,z,'-',label=self.gases[0])
#            ax.plot(vmr+self.error.error_meas(),z,'.', color=l[0].get_color())
#            ax.plot(vmr-self.error.error_meas(),z,'.', color=l[0].get_color())
            ax.plot(apr,z,'--', color=l[0].get_color())
            ax.legend()
            if (type == 'vmr'):
                ax = self.winprf.add_subplot(122)
                for n in range(0,len(self.gases)):
                    vmr,z = self.retprf.get_gas_vmr(self.gases[n])
                    l = ax.plot(vmr,z,'-',label=self.gases[n])
                    apr,z = self.aprprf.get_gas_vmr(self.gases[n])
                    ax.plot(apr,z,'--', color=l[0].get_color())
                    ax.legend()

            self.winprf.show()
            
                
        if(type=='mw'):
            self.show_spectra(nr)

        if (type=='avk'):
            self.winavk.clf()
            ax = self.winavk.add_subplot(141)
            vmr,z = self.retprf.get_gas_vmr(self.gases[0])
            ax.plot(self.avk.avk('frac').T, z)
            ax = self.winavk.add_subplot(142)
            ax.plot(self.avk.avk('vmr').T, z)
            ax = self.winavk.add_subplot(143)
            ax.plot(self.avk.avk('col').T, z)
            ax = self.winavk.add_subplot(144)
            ax.plot(np.sum(self.avk.avk('col'),0), z)
            self.winavk.show()


    def show_spectra(self,band_nr = 1,gas=None):


            self.winmw.clf()
            gs = gridspec.GridSpec(2, 1, height_ratios=[2,1])


            ax1 = self.winmw.add_subplot(gs[0])
            ax2 = self.winmw.add_subplot(gs[1])

            self.f = True
            def oncall1(ax):
                if not self.f:
                    self.f = True
                    ax2.set_xlim(ax.get_xlim())
                self.f = False

            def oncall2(ax):
                if not self.f:
                    self.f = True
                    ax1.set_xlim(ax.get_xlim())
                self.f = False


            ax1.xaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
            ax1.yaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
            ax1.set_autoscaley_on(True)
            ax1.autoscale_view(True)
            ax1.plot(self.sp.nu[band_nr-1], self.sp.obs[band_nr-1],label='obs')
            ax1.plot(self.sp.nu[band_nr-1], self.sp.clc[band_nr-1],label='clc')
            ax1.legend(bbox_to_anchor=(0.5,1.0), loc=8, ncol=2)
            ax2.xaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
            ax2.yaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
            ax2.set_autoscaley_on(True)
            ax2.set_autoscalex_on(True)
            ax2.autoscale_view(True)
            ax2.plot(self.sp.nu[band_nr-1], self.sp.dif[band_nr-1])
#            pdb.set_trace()
#            ax2.set_xlabel(r'Frequency [cm$^{-1}$]')
            self.winmw.show()
            ax1.callbacks.connect('xlim_changed', oncall1)
            ax2.callbacks.connect('xlim_changed', oncall2)
            self.f = False

#            if gas <> None and len(self.gasspectra)>0 :
#                spec.s
                
    def show_spectra_by_gas(self, scan_nr = 1, itera = -1, band_nr = 1, gas = 'ALL'):
            self.winmw.clf()
            gs = gridspec.GridSpec(2, 1, height_ratios=[2,1])
            ax1 = self.winmw.add_subplot(gs[0])
            ax2 = self.winmw.add_subplot(gs[1])

            self.f = True
            def oncall1(ax):
                if not self.f:
                    self.f = True
                    ax2.set_xlim(ax.get_xlim())
                self.f = False

            def oncall2(ax):
                if not self.f:
                    self.f = True
                    ax1.set_xlim(ax.get_xlim())
                self.f = False


            inds = filter(lambda x: self.gas.band[x]==band_nr \
                   and self.gas.scan[x]==scan_nr\
                   and (self.gas.gas[x]==gas or gas == 'ALL')\
                   and self.gas.iteration[x] == itera,\
                   range(0,len(self.gas.band)))
            
            for ind in inds:
                ax1.plot(self.gas.nu[ind],self.gas.clc[ind],label=self.gas.gas[ind])

            ax1.xaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
            ax1.yaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
            ax1.set_autoscaley_on(True)
            ax1.autoscale_view(True)                      
            ax1.legend(bbox_to_anchor=(1.005, 1), loc=2, borderaxespad=0.)

            ax2.xaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
            ax2.yaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
            ax2.set_autoscaley_on(True)
            ax2.set_autoscalex_on(True)
            ax2.autoscale_view(True)
            ax2.plot(self.sp.nu[band_nr-1], self.sp.dif[band_nr-1])
            ax1.callbacks.connect('xlim_changed', oncall1)
            ax2.callbacks.connect('xlim_changed', oncall2)
            self.f = False

#            pdb.set_trace()
#            ax2.set_xlabel(r'Frequency [cm$^{-1}$]')
            self.winmw.show()
#            self.winmw.savefig('/home/christof_p/res_win_'+str(band_nr)+'.png')
												

if __name__ == '__main__':
    show_results()
