#!/usr/bin/python

# Script to print results in a hdf created by create_hdf5.py

import tables as h5
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker  as tkr
import matplotlib.dates as dates
import sys

plt.rc('text', usetex=True)

if __name__ == '__main__':
    h5_file = sys.argv[1]


h5f = h5.File(h5_file)
dnum = h5f.root.mdate[:]
col = h5f.root.col_rt[0,:]
apc = h5f.root.col_ap[0,:]
gases = h5f.root.gasnames[:]
h2oc = -1
try:
    ind = gases.index('H2O')
    h2oc =  h5f.root.col_rt[ind,:]
except:
    pass

ecol_sys = h5f.root.col_sys[:]
ecol_ran = h5f.root.col_ran[:]
vmr = h5f.root.vmr_rt[:]
spectra = h5f.root.spectra[:]
dirs = h5f.root.directories[:]
sza = np.double(h5f.root.sza[:])
snrt = h5f.root.snr_the[:]
snr = h5f.root.snr_clc[:]
avk = h5f.root.avk[:]
c2y = h5f.root.chi_2_y[:]
nr_iter = h5f.root.iter[:]
max_iter = h5f.root.itmx[:]
h5f.close()
dofs = np.trace(avk)

s_date = dates.date2num(dates.datetime.date(1990,1,1))
ind = range(0,len(snr))
ind = filter (lambda x: nr_iter[x] < max_iter[x] and c2y[x] > 0 and c2y[x]<3.0, range(0,len(snr)))
#ind = filter (lambda x: c2y[x] > 0 and c2y[x]<3.0 and snr[x] > 50.0, range(0,len(snr)))

f1 = plt.figure(1)
f1.clf()
ax = plt.subplot(221)
plt.plot_date(dnum[ind], apc[ind], 'rx')
plt.plot_date(dnum[ind], col[ind], 'o')
plt.errorbar(dnum[ind], col[ind], ecol_ran[ind], fmt=None)
ax.yaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
plt.title('Total Columns');
ax = plt.subplot(223)
plt.plot_date(dnum[ind], h2oc[ind], 'o')
plt.errorbar(dnum[ind], col[ind], ecol_ran[ind], fmt=None)
ax.yaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
plt.title('Total Columns H2O');
ax = plt.subplot(222)
plt.plot_date(dnum[ind], snr[ind], 'o')
ax.yaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
plt.title('SNR');
ax2 = ax.twinx()
plt.plot_date(dnum[ind], c2y[ind], 'rx')
ax = plt.subplot(224)
plt.plot_date(dnum[ind], dofs[ind], 'o')
ax.yaxis.set_major_formatter(tkr.ScalarFormatter(useOffset=False))
plt.title('DOFs');
f1.show()

raw_input()

