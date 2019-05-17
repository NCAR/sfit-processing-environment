import sys,os
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import dates

def read_meas_from_gopfile(filename):

    mdate = []
    with open(filename) as fid:
        for ll in fid:
            try:
                mdate.append(datetime.strptime(ll.strip()[2:10],'%Y%m%d'))
            except:
                pass

    return(mdate)


def plot_mdates(axes, mdate):
    month = dates.MonthLocator()
    axes.xaxis.set_major_locator(month) 
    monthFmt = dates.DateFormatter('%m')
    axes.xaxis.set_major_formatter(monthFmt)
    dnums = np.unique(dates.date2num(mdate))
    axes.plot_date(dnums, np.ones((dnums.shape)))
    axes.set_xlim((mdate[0].replace(day=1,month=1),mdate[0].replace(day=31,month=12)))
    axes.text(0.9,0.05,mdate[0].year,transform=ax.transAxes)
    f.show()

def plot_hist_mdates(axes, mdate, granu='month'):
    month = dates.MonthLocator()
    axes.xaxis.set_major_locator(month) 
    monthFmt = dates.DateFormatter('%m')
    axes.xaxis.set_major_formatter(monthFmt)

    if granu != 'month':
        print('granularity %s not yet implemented'%granu)
        return()
    #    dnums = [x in np.unique(dates.date2num(mdate))
    dnums = [dates.date2num(x.replace(day=1)) for x in mdate]
    axes.hist(dnums,np.unique(dnums))
    axes.set_xlim((mdate[0].replace(day=1,month=1),mdate[0].replace(day=31,month=12)))
    axes.text(0.9,0.05,mdate[0].year,transform=ax.transAxes)
    f.show()


if __name__ == '__main__':

    num_gops = len(sys.argv)-1
    f = plt.figure('Meas_Days')
    f.clf()

    num = 1
    for ff in sys.argv[1:]:
        mdate = read_meas_from_gopfile(ff)
        ax = f.add_subplot(num_gops,1,num)
        plot_hist_mdates(ax, mdate)
        ax.set_yticks([])
        # set month ticks only in the last subplot
        if num < num_gops:
            ax.set_xticks([])
        if num == num_gops:
            ax.set_xlabel('Month of year')
        num += 1
