import sys
sys.path.append('/home/mathias/sfit-processing-environment/Lib_MP/')
import read_result_sfit4 as sfit4
from sfit4_ctl import *
from Tkinter import *
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import matplotlib.gridspec as gridspec
import numpy as np
import os, pdb


class show_results:

    def __init__(self,direc='.', sb_ctl = 'sb.ctl', ctlfile='sfit4.ctl'):

        self.direc = direc
        self.ctlfile = ctlfile


        # out.level = 1
        plt.rcParams['font.size'] = 18
#        plt.rc('text', usetex=True)

        self.sb_ctl = sb_ctl
        self.load_result(sb_ctl)
        
        # Find a free figure for profile
        self.winprf = plt.figure('Profile')#figsize=(24,12))
        # Find a free figure for microwindow
        self.winmw = plt.figure('Spectrum')#figsize=(24,12))
        # Find a free figure for AVK
        self.winavk = plt.figure('AVK')#figsize=(24,12))
        # Find a free figure for ERROR
        self.winerr = plt.figure('Error')#figsize=(24,12))

        self.winpcol = plt.figure('Partial column')#figsize=(24,12))

        self.winfft = plt.figure('FFT')#figsize=(24,12))

    

        self.tkroot = Tk()
        self.tkroot.wm_title('sfit4 result viewer')


        
        self.entry = Entry(self.tkroot)
        self.entry.grid(row=0, column=1, sticky=E+W)
        self.entry.delete(0, END)
        self.entry.insert(0, os.path.abspath(self.direc))
#        self.update_dirlist()

        button_update = Button(self.tkroot, text = 'Reload', command = self.update_result)
        button_update.grid(row=0, column=0, sticky=E+W)
#        button_update.config(state=DISABLED)
#        button_update.pack()

        options = []
        for n in range(0,self.sp.nr_mw):
            options.append(int('%i'%(n+1)))


        def spectrum_show():
            nr = int(self.spec_nr.get())
            self.show_spectra(nr)

        def fft_show():
            nr = int(self.spec_nr.get())
            self.show_fft(nr)

        def pcol_show():
            self.show_pcol()

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
        self.button_spec_by_gas = button_spec

        if self.error.flag:
            options =  ('TARGET', 'INTERF', 'ERR')
        else:
            options =  ('TARGET', 'INTERF')
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

        def avk_show():
            self.winavk.clf()
            vmr,z = self.retprf.get_gas_vmr(self.gases[0])
            if self.avk_type.get() == 'FRAC':
                self.winavk.gca().plot(self.avk.avk('frac').T, z)
            elif self.avk_type.get() == 'VMR':
                self.winavk.gca().plot(self.avk.avk('vmr').T, z)
            elif self.avk_type.get() == 'COL':
                self.winavk.gca().plot(np.sum(self.avk.avk('col')[:,:],0), z)
            elif self.avk_type.get() == 'PCOL ALL':
                self.winavk.gca().plot(self.avk.avk('col').T, z)
            elif self.avk_type.get() == 'PCOL':
                for i in range(0,self.nr_pcols):
                    min_alt = float(self.min_pcv[i].get())
                    max_alt = float(self.max_pcv[i].get())
                    min_ind = np.max(np.where(np.array(z)>=min_alt))
                    max_ind = np.min(np.where(np.array(z)<max_alt))
                    self.winavk.gca().plot(np.sum(self.avk.avk('col')[:,max_ind:min_ind],1), z, label='PCOL from %.2f to %.2f km'%(min_alt,max_alt))
            self.winavk.gca().set_ylabel('Altitude [km]')
            self.winavk.gca().set_xlabel('Fraction of AVK [a.u.]')
            self.winavk.gca().legend(fontsize=16)
            self.winavk.show()


        def profile_show():
            if self.show_var.get() == 'TARGET':
                self.show(type='target')
            if self.show_var.get() == 'INTERF':
                self.show(type='vmr')
            if self.show_var.get() == 'ERR':
                self.show(type='err')

        button_profile = Button(self.tkroot, text = 'Profile', command = lambda: profile_show())
        button_profile.grid(row=3, column=0, sticky=E+W)

        button_avk = Button(self.tkroot, 
                            text = 'AVK', 
                            command = lambda: avk_show())
        button_avk.grid(row=4, column=0, sticky=E+W)
        avk_options=['FRAC', 'VMR', 'COL', 'PCOL ALL', 'PCOL']
        self.avk_type = StringVar(self.tkroot)
        self.avk_type.set(avk_options[0])
        self.menu2 = OptionMenu(self.tkroot,self.avk_type, 
                                *avk_options)
        self.menu2.grid(row=4,column=1,stick=E+W)


        frame3 = Frame(self.tkroot)
        frame3.grid(row=5,column=0)
                
        button_summary = Button(frame3, text = 'FFT',
                                command = lambda: fft_show())
        button_summary.grid(row=2, column=0, sticky=E+W)

        button_pcol = Button(frame3, text = 'PCOL',
                             command = lambda: pcol_show())
        button_pcol.grid(row=3,column=0)

        button_quit = Button(self.tkroot, text = 'Quit',
                             command = self.tkroot.quit)
        button_quit.grid(row=6, column=0, sticky=E+W)

        frame4 = Frame(self.tkroot)
        frame4.grid(row=5,column=1)
        self.nr_pcols = 3
        pc,z = self.retprf.get_gas_col(self.gases[0])
#        ap = np.linalg.inv(np.diag(pc))
        if self.error.flag:
            self.label_repc,repc = self.error.read_matrix_random_pcol()
            self.label_sepc,sepc = self.error.read_matrix_system_pcol()
            # Error matrices must be normalized in order to take correlation into account
            #        self.repc = np.dot(ap,np.dot(np.sum(repc,0),ap))
            #        self.sepc = np.dot(ap,np.dot(np.sum(sepc,0),ap))
            self.repc = np.sum(repc,0)
            self.sepc = np.sum(sepc,0)
        self.min_pcv = []
        self.max_pcv = []
        self.pcol1 = []
        self.epcol1 = []

        def modify_pc(event, nr):
            try:
                min_alt = float(self.min_pcv[nr].get())
                max_alt = float(self.max_pcv[nr].get())
                min_ind = np.max(np.where(np.array(z)>=min_alt))
                max_ind = np.min(np.where(np.array(z)<=max_alt))
                ap = np.zeros(pc.size)
                ap[max_ind:min_ind+1] = 1.0
                pcol = pc[max_ind:min_ind+1]
                self.pcol1[nr].set('%g'%np.sum(pcol))
                if self.error.flag:
                    col_ran = self.repc + self.sepc
                    self.epcol1[nr].set('%g'%np.sqrt(np.dot(np.dot(ap.T,col_ran),ap)))
#                self.epcol1[nr].set('%g'%np.sqrt(np.sum(col_ran)))
            except:
                print 'fail'
                pass
            
        default = [[0.0, 10.0],
                   [10.0, 120.0],
                   [0.0, 120.0]]

        for i in range(0,self.nr_pcols):
            self.min_pcv.append(StringVar(frame4))
            min_pc = Entry(frame4, width=5,textvariable=self.min_pcv[-1])
            self.min_pcv[-1].set(default[i][0])
            min_pc.grid(row = i, column=0)

            self.max_pcv.append(StringVar(frame4))
            max_pc = Entry(frame4, width=5,textvariable=self.max_pcv[-1])
            self.max_pcv[-1].set(default[i][1])
            max_pc.grid(row = i, column=1)

            
            self.pcol1.append(StringVar(frame4))
            self.epcol1.append(StringVar(frame4))
            val_pc = Label(frame4, textvariable=self.pcol1[-1])
            val_pc.grid(row = i, column=2)
            err_pc = Label(frame4, textvariable=self.epcol1[-1])
            err_pc.grid(row = i, column=3)
            modify_pc(0,i)
            

            min_pc.bind('<Return>', lambda ev, x=i: modify_pc(ev,x))
            max_pc.bind('<Return>', lambda ev, x=i : modify_pc(ev,x))



        
        

#        self.SummaryText()
# #        self.mkOptionMenu1()

        
        self.tkroot.mainloop()

    def quit(self):
        self.tkroot.destroy()


    def SummaryText(self):
        tt1 = Text(self.tkroot)
        nr_mw = self.sp.nr_mw
        tt1.insert('end', 'Nr. of microwindows %i'%nr_mw)
        tt1.grid(row=4,column=1)

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


    def update_result(self):
        self.load_result(self.sb_ctl)
        options = list(set(self.gas.gas[:]))
        if len(options) == 0:
            self.button_spec_by_gas.config(state=DISABLED)
        else:
            self.button_spec_by_gas.config(state=NORMAL)
        if len(options) > 0:
            self.spec_gas = StringVar(self.tkroot)
            self.spec_gas.set(options[0])

            self.menu1 = OptionMenu(self.tkroot,self.spec_gas, 
                                    *options)
            self.menu1.grid(row=2,column=1,stick=E+W)
        

    def load_result(self, sb_ctl = 'sb.ctl'):
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
        pbp_m = ctl.get_value('file.out.pbpfile')
        if pbp_m == -1:
            self.sp = sfit4.pbp(direc+'/pbpfile')
        else:
            self.sp = sfit4.pbp(direc+'/'+pbp_m)
        if os.path.exists(direc+'/'+ak_m):
            self.avk = sfit4.avk(direc+'/'+ak_m, direc+'/aprfs.table')
        elif os.path.exists(direc+'/ak.target'):
            self.avk = sfit4.avk(direc+'/ak.target', direc+'/aprfs.table')
        elif os.path.exists(direc+'/avk.output'):
            self.avk = sfit4.avk(direc+'/avk.output', direc+'/aprfs.table')
        else:
            self.avk = -1

        self.error = sfit4.error('.', sbctl=sb_ctl,rprfs=direc+'/rprfs.table')

        self.gas = sfit4.gasspectra(direc)



    def __del__(self):
        plt.close(self.winprf)
        plt.close(self.winmw)
        plt.close(self.winavk)
        plt.close(self.winfft)

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
            l = ax.plot(vmr,z,'-',lw=3,label=self.gases[0])
            e_ran, e_sys = self.error.read_total_vmr()
            e_tot = np.sqrt(e_ran**2 + e_sys**2)
            ax.plot(vmr+e_tot,z,'--', color=l[0].get_color())
            ax.plot(vmr-e_tot,z,'--', color=l[0].get_color())

            ax.plot(apr,z,'-', lw=1, label='a priori', color=l[0].get_color())
            ax.legend()
            if (type == 'vmr'):
                ax = self.winprf.add_subplot(122)
                for n in range(0,len(self.gases)):
                    vmr,z = self.retprf.get_gas_vmr(self.gases[n])
                    l = ax.plot(vmr,z,lw=2,label=self.gases[n])
                    apr,z = self.aprprf.get_gas_vmr(self.gases[n])
                    ax.plot(apr,z,'--',lw=1, color=l[0].get_color())
                    ax.legend()
            ax.set_ylabel('altitude [km]')
            ax.set_xlabel('VMR [ppt]')
            ax.set_xticklabels(ax.get_xticks()/1.0e-9)
            self.winprf.show()

                
        if(type=='mw'):
            self.show_spectra(nr)


        if (type=='err'):
            vmr,z = self.retprf.get_gas_vmr(self.gases[0])
            self.winerr.clf()

            ax = self.winerr.add_subplot(221)
            label,matrix = self.error.read_matrix_random_vmr()
            for l,m in zip(label,range(0,len(label))):
                err = np.sqrt(np.diag(matrix[m,:,:]))
                ax.plot(err,z,label=l)
            ax.set_title('random')
            ax.legend(fontsize=8)
            ax.ticklabel_format(style='sci', scilimits=(0,0))

            ax = self.winerr.add_subplot(222)
            label,matrix = self.error.read_matrix_random_pcol()
            for l,m in zip(label,range(0,len(label))):
                err = np.sqrt(np.diag(matrix[m,:,:]))
                ax.plot(err,z,label=l)
            ax.set_title('random')
            ax.legend(fontsize=8)
            ax.ticklabel_format(style='sci', scilimits=(0,0))

            ax = self.winerr.add_subplot(223)
            ax.set_title('systematic')
            label,matrix = self.error.read_matrix_system_vmr()
            for l,m in zip(label,range(0,len(label))):
                if l=='smoothing':
                    continue
                err = np.sqrt(np.diag(matrix[m,:,:]))
                ax.plot(err,z,label=l)
            ax.legend(fontsize=8)
            ax.ticklabel_format(style='sci', scilimits=(0,0))

            ax = self.winerr.add_subplot(224)
            ax.set_title('systematic')
            label,matrix = self.error.read_matrix_system_pcol()
            for l,m in zip(label,range(0,len(label))):
                if l=='smoothing':
                    continue
                err = np.sqrt(np.diag(matrix[m,:,:]))
                ax.plot(err,z,label=l)
            ax.legend(fontsize=8)
            ax.ticklabel_format(style='sci', scilimits=(0,0))

            self.winerr.show()
            
    def show_pcol(self):
        self.winpcol.clf()
        ax = self.winpcol.add_subplot(111)
        vmr,z = self.retprf.get_gas_vmr(self.gases[0])
        pcol = [[-1,22],
                [-23,0]]
        ind = [[-20,len(z)], 
               [0,-21]]
        ax.plot(np.sum(self.avk.avk('col')[ind[0][0]:ind[0][1],:],0), z,
                label='%0.2f-%0.2f'%(z[ind[0][1]-1],z[ind[0][0]]))
        ax.plot(np.sum(self.avk.avk('col')[ind[1][0]:ind[1][1],:],0), z, 
                label='%0.2f-%0.2f'%(z[ind[1][1]-1],z[ind[1][0]]))
        ax.legend(fontsize=8)
        self.winpcol.show()
        

        
    def show_fft(self,band_nr = 1,gas=None):
        def oncall1(event):
            dnum = event.artist.get_xdata()
            mdnum = event.mouseevent.xdata
            ind = np.argmin(np.abs(dnum-mdnum))
            print (self.sp.mw_stop[band_nr-1] - self.sp.mw_start[band_nr-1])/(ind/10.0)
        self.winfft.clf()
        fsp = np.fft.fft(self.sp.dif[band_nr-1],
                         10*self.sp.dif[band_nr-1].size)
        spacing = self.sp.mw_res[band_nr-1]
        xax = np.fft.fftfreq(fsp.size, spacing)
        self.winfft.gca().plot(np.abs(fsp[xax>0]),picker=5)
        self.winfft.canvas.mpl_connect('pick_event', oncall1)
        self.winfft.show()

            
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
            ax1.set_xticks([])
            ax1.set_ylabel('Transmission [a.u.]')
            ax1.set_autoscaley_on(True)
            ax1.autoscale_view(True)                      
            ax1.legend(bbox_to_anchor=(1.005, 1), loc=2, borderaxespad=0.)

            ax2.xaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
            ax2.yaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
            ax2.set_autoscaley_on(True)
            ax2.set_autoscalex_on(True)
            ax2.autoscale_view(True)
            ax2.plot(self.sp.nu[band_nr-1], self.sp.dif[band_nr-1])
            ax2.set_xlabel('Wavelength [1/cm]')
            ax1.callbacks.connect('xlim_changed', oncall1)
            ax2.callbacks.connect('xlim_changed', oncall2)
            self.f = False

#            pdb.set_trace()
#            ax2.set_xlabel(r'Frequency [cm$^{-1}$]')
            self.winmw.show()
#            self.winmw.savefig('/home/christof_p/res_win_'+str(band_nr)+'.png')
												

if __name__ == '__main__':
    import sys
    print len(sys.argv)
    if len(sys.argv) == 2:
        show_results(sb_ctl=sys.argv[1])
    else:
        show_results()
