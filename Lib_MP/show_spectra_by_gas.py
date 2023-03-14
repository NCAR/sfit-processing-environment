import sys
#sys.path.append('/data/sfit-processing-environment/Lib_MP/')
import read_gas_files as rspec
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker  as tkr
import read_detfile as df
import read_gas_files as rspec
import read_result_sfit4 as sfit4
import glob, pdb
import argparse

def spectra_by_gas(direc,ax=-1,nr_iter = -1, nr_band=1,gases='All',keep=False):

    files = glob.glob(direc + '/spc*')
    sp = sfit4.pbp(direc+'/pbpfile')
    spec = [];
    for ff in files:
        spec.append(rspec.read_gasfiles(ff))

    try:
        nr_iter
    except NameError:
        nr_iter = -1
            
    try:
        nr_band
    except NameError:
        nr_band = 1
            
    try:
        ax
        if not keep:
            ax.clear()
    except:
        fig = plt.figure(5)
        fig.clf()
        ax = fig.gca()

    ax1 = ax #fig.add_subplot(111)
    gas_sum = [];
    for s in spec:
        max_s = np.max(s['clc'])
        max_s = 1.0
        if gases == 'All':
            if int(s['iteration']) == nr_iter and int(s['band']) == nr_band:
                ax1.plot(s['nu'], s['clc'],label=s['gas'])
                try:
                    gas_sum = gas_sum -np.log(s['clc'])
                except:
                    gas_sum = -np.log(s['clc'])
                    nu = s['nu']
#                    gas_sum = np.exp(-gas_sum)
#                    ax1.plot(nu, gas_sum,label='SUM')
                    
        else:
            #                pdb.set_trace()
            if int(s['iteration']) == nr_iter and int(s['band']) == nr_band and gases.count(s['gas'])>0:
                ax1.plot(s['nu'], s['clc']/max_s,label='{}{}'.format(s['gas'],nr_iter))

#    ax1.plot(nu_all, gas_all*np.max(gas_sum),label='ALL')
    
    plt.rcParams['font.size'] = 14
    ax1.xaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
    ax1.yaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
    ax1.set_autoscaley_on(True)
    ax1.autoscale_view(True)
    ax1.xaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
    ax1.set_autoscale_on(True)
    
#         ax2 = fig.add_subplot(212)
#         ax2.xaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
#         ax2.yaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
#         ax2.set_autoscalex_on(True)
#         ax2.autoscale_view(True)
#         ax2.plot(sp.nu[nr_band-1], sp.dif[nr_band-1])
# #        plt.title('Iteration nr: ' + str(nr_iter) + ' Band Nr: ' + str(nr_band))
    plt.legend(loc=2, bbox_to_anchor = (1.0, 1.0))
    plt.draw()

    return (spec)
    


#            self.winmw.clf()
#            ax1 = self.winmw.add_subplot(211)
#            ax1.xaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
#            ax1.yaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
#            ax1.set_autoscaley_on(True)
#            ax1.autoscale_view(True)
#            ax1.plot(self.sp.nu[nr], self.sp.obs[nr],label='obs')
#            ax1.plot(self.sp.nu[nr], self.sp.clc[nr],label='clc')
#            plt.legend()
#            ax2 = self.winmw.add_subplot(212)
#            ax2.xaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
#            ax2.yaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
#            ax2.set_autoscaley_on(True)
#            ax2.set_autoscalex_on(True)
#            ax2.autoscale_view(True)
#            ax2.plot(self.sp.nu[nr], self.sp.dif[nr])
##            pdb.set_trace()
##            ax2.set_xlabel(r'Frequency [cm$^{-1}$]')
#            self.winmw.show()


if __name__== '__main__':

    import os,sys
    sys.path.append(os.path.join(os.path.dirname(sys.argv[0])))
    
    direc = '.'
    gas = 'All'
    for arg in sys.argv[1:]:
        key,val = arg.split('=')
        if key=='--dir':
            direc = val
        if key=='--gas':
            dir = val
    spectra_by_gas(direc,gases=gas)
    input()
