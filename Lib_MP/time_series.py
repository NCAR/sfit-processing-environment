import numpy as np
import pdb
import matplotlib.dates as dates

def daily_index(ds, ts = 'daily'):

    mean_inds = {}
    
    if ts == 'daily':
        dd_mean = list(set(ds.round()))
        #        col_mean = np.zeros((cols.shape[0],0))
        #        col_mean = []

    if ts == 'monthly':
        mdates = dates.num2date(ds)
        dss = map(lambda x: x.replace(day=1,hour=0,minute=0), mdates)
        dss = dates.date2num(dss)
        dd_mean = list(set(dss))
        year = np.array(map(lambda x: x.year, mdates))
        month = np.array(map(lambda x: x.month, mdates))

    for ndd in dd_mean:
        if ts =='monthly':
            d_this = dates.num2date(ndd)
            inds = np.where(np.all((year==d_this.year,month==d_this.month),axis=0))[0]
        elif ts == 'daily':
            inds = np.int16(np.nonzero(abs(ndd - ds)<1))

        mean_inds[ndd] = inds 

    return(mean_inds)

            
def daily_mean(ds, cols, ecols, ts='daily'):

    cols = np.array(cols)
    ds = np.array(ds)
    
    if ecols.ndim == 1:
        ecolsnum = 1
    else:
        ecolsnum = ecols.shape[1]
        
    col_mean = np.zeros(0)
    ecol_mean = np.zeros(0)
        
    if ts == 'daily':
        dd_mean = list(set(ds.round()))
        #        col_mean = np.zeros((cols.shape[0],0))
        #        col_mean = []

    if ts == 'monthly':
        mdates = dates.num2date(ds)
        dss = map(lambda x: x.replace(day=1,hour=0,minute=0), mdates)
        dss = dates.date2num(dss)
        dd_mean = list(set(dss))
        year = np.array(map(lambda x: x.year, mdates))
        month = np.array(map(lambda x: x.month, mdates))

    for ndd in dd_mean:
        if ts =='monthly':
            d_this = dates.num2date(ndd)
            inds = np.where(np.all((year==d_this.year,month==d_this.month),axis=0))[0]
        elif ts == 'daily':
            inds = np.int16(np.nonzero(abs(ndd - ds)<1))

        if len(inds)>0:
#            print col_mean.size, np.mean(cols[inds]).size
            col_mean = np.hstack((col_mean, np.mean(cols[inds])))
        if ecolsnum > 1:
            for cols in range(0,ecolsnum):
                ecol_mean[cols] = np.hstack((ecol_mean[cols], np.linalg.norm(ecols[cols,inds])/inds.size))
        else:
            ecol_mean = np.hstack((ecol_mean, np.linalg.norm(ecols[inds])/inds.size))
            dd = np.array(dd_mean).copy()
            
    return(dd, col_mean, ecol_mean)




def match_dates(dd1, dd2, dist=1):
    nr = 0
    ddc = []
    ind1 = []
    ind2 = []
    for ndd in dd2:
        inds = np.argmin(abs(dd1 - ndd))
        if abs(dd1[inds]-ndd) <= dist:
#            print abs(dd1[inds]-ndd), dd1[inds], ndd, dist, inds, nr
            ddc.append(dd1[inds])
            ind2.append(nr)
            ind1.append(inds)
        nr = nr + 1

    return(ddc, ind1, ind2)
