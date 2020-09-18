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

def plot_hist_mdates(axes, mdate, granu='month'):
    month = dates.MonthLocator()
    axes.xaxis.set_major_locator(month) 
    monthFmt = dates.DateFormatter('%m')
    axes.xaxis.set_major_formatter(monthFmt)

    if granu != 'month':
        print('granularity %s not yet implemented'%granu)
        return()
    
    dnums = [dates.date2num(x.replace(day=15)) for x in np.unique(mdate)]
    axes.hist(dnums,np.linspace(dates.date2num(mdate[0].replace(month=1,day=1)),
                                dates.date2num(mdate[0].replace(month=12,day=1)),
                                num=12,endpoint=True))
    axes.set_xlim((mdate[0].replace(day=1,month=1),mdate[0].replace(day=31,month=12)))


if __name__ == '__main__':

    num_gops = len(sys.argv)-1
    f = plt.figure('Meas_Days')
    f.clf()
    f2 = plt.figure('No of Meas')
    f2.clf()

    num = 1
    for ff in sys.argv[1:]:
        mdate = read_meas_from_gopfile(ff)
        ax = f.add_subplot(num_gops,1,num)
        ax2 = f2.add_subplot(num_gops,1,num)
        plot_mdates(ax, mdate)
        plot_hist_mdates(ax2, mdate)
        ax.set_yticks([])
        ax2.set_ylabel('Meas days per \n month of Year %s'%mdate[0].year)
        # set month ticks only in the last subplot
        if num < num_gops:
            ax.set_xticks([])
            ax2.set_xticks([])
        if num == num_gops:
            ax.set_xlabel('Month of year')
            ax2.set_xlabel('Month of year')
        num += 1
    f.tight_layout()
    f2.tight_layout()
    f.show()
    f2.show()


        
    input()
