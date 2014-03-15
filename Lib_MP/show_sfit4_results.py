import sys
sys.path.append('/data/sfit-processing-environment/Lib_MP/')
import read_result_sfit4 as sfit4
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import matplotlib.gridspec as gridspec
import os, pdb

class show_results:

    def __init__(self,direc='.'):

        # out.level = 1
        plt.rcParams['font.size'] = 24
#        plt.rc('text', usetex=True)
        self.retprf = sfit4.read_table(direc+'/rprfs.table')
        self.aprprf = sfit4.read_table(direc+'/aprfs.table')
        self.gases = self.aprprf.get_retrieval_gasnames()
        self.sp = sfit4.pbp(direc+'/pbpfile')
        if os.path.exists(direc+'/ak.out'):
            self.avk = sfit4.avk(direc+'/ak.out')
        else:
            self.avk = -1
#        self.error = sfit4.error(direc+'/smeas.target',direc+'/aprfs.table')
        try:
            self.error = sfit4.error(direc+'/smeas.target',direc+'/aprfs.table')
        except:
            pass

        self.gas = sfit4.gasspectra(direc)


        # Find a free figure for profile
        self.winprf = plt.figure()#figsize=(24,12))
        # Find a free figure for microwindow
        self.winmw = plt.figure()#figsize=(24,12))
        # Find a free figure for AVK
        self.winavk = plt.figure()#figsize=(24,12))

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
            ax = self.winavk.add_subplot(111)
            vmr,z = self.retprf.get_gas_vmr(self.gases[0])
            ax.plot(self.avk.avk('frac').T, z)
            self.winavk.show()


    def show_spectra(self,band_nr = 1,gas=None):
            self.winmw.clf()
            gs = gridspec.GridSpec(2, 1, height_ratios=[2,1])
            ax1 = self.winmw.add_subplot(gs[0])
            ax1.xaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
            ax1.yaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
            ax1.set_autoscaley_on(True)
            ax1.autoscale_view(True)
            ax1.plot(self.sp.nu[band_nr-1], self.sp.obs[band_nr-1],label='obs')
            ax1.plot(self.sp.nu[band_nr-1], self.sp.clc[band_nr-1],label='clc')
            ax1.legend(bbox_to_anchor=(1.005, 1), loc=2, borderaxespad=0.)
            ax2 = self.winmw.add_subplot(gs[1])
            ax2.xaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
            ax2.yaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
            ax2.set_autoscaley_on(True)
            ax2.set_autoscalex_on(True)
            ax2.autoscale_view(True)
            ax2.plot(self.sp.nu[band_nr-1], self.sp.dif[band_nr-1])
#            pdb.set_trace()
#            ax2.set_xlabel(r'Frequency [cm$^{-1}$]')
            self.winmw.show()

#            if gas <> None and len(self.gasspectra)>0 :
#                spec.s
                
    def show_spectra_by_gas(self, scan_nr = 1, iter = 'final', band_nr = 1, gas = 'all'):
            self.winmw.clf()
            gs = gridspec.GridSpec(2, 1, height_ratios=[2,1])
            ax1 = self.winmw.add_subplot(gs[0])

            for gas_sp in self.gas.spec[scan_nr][iter][band_nr]:
                try:
                    ax1.plot(self.gas.spec[scan_nr][iter][band_nr][gas_sp][0][0], self.gas.spec[scan_nr][iter][band_nr][gas_sp][1][0], label=gas_sp)
                except:
                    continue
            ax1.xaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
            ax1.yaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
            ax1.set_autoscaley_on(True)
            ax1.autoscale_view(True)                      
            ax1.legend(bbox_to_anchor=(1.005, 1), loc=2, borderaxespad=0.)
            ax2 = self.winmw.add_subplot(gs[1])
            ax2.xaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
            ax2.yaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
            ax2.set_autoscaley_on(True)
            ax2.set_autoscalex_on(True)
            ax2.autoscale_view(True)
            ax2.plot(self.sp.nu[band_nr-1], self.sp.dif[band_nr-1])

#            pdb.set_trace()
#            ax2.set_xlabel(r'Frequency [cm$^{-1}$]')
            self.winmw.show()
#            self.winmw.savefig('/home/christof_p/res_win_'+str(band_nr)+'.png')
												
