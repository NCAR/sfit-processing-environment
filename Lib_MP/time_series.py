import numpy as np
import pdb

def daily_mean(ds, cols, ecols, ts='daily'):

    cols = np.array(cols)
    ds = np.array(ds)
    
    if ecols.ndim == 1:
        ecolsnum = 1
    else:
        ecolsnum = ecols.shape[1]

    if ts == 'daily':
        dd_mean = list(set(ds.round()))
        col_mean = np.zeros(0)
        ecol_mean = np.zeros(0)
#        col_mean = np.zeros((cols.shape[0],0))
#        col_mean = []
        for ndd in dd_mean:
            inds = np.int16(np.nonzero(abs(ndd - ds)<1))
            print col_mean.size, np.mean(cols[inds], axis=1).size
            col_mean = np.hstack((col_mean, np.mean(cols[inds], axis=1)))
            # if ecolsnum > 1:
            #     for cols in range(0,ecolsnum):
            #         ecol_mean[cols] = np.hstack((ecol_mean[cols], np.linalg.norm(ecols[cols,inds])/inds.size))
            # else:
            #     ecol_mean = np.hstack((ecol_mean, np.linalg.norm(ecols[inds])/in
 #                                      ds.size))
        dd = np.array(dd_mean).copy()

    return(dd, col_mean, ecol_mean)




def match_dates(dd1, dd2, dist=1):
    nr = 0
    ddc = []
    ind1 = []
    ind2 = []
    for ndd in dd2:
        inds = np.argmin(abs(dd1 - ndd))
        if abs(dd1[inds]-ndd) < dist:
#            print abs(dd1[inds]-ndd), dd1[inds], ndd, dist, inds, nr
            ddc.append(dd1[inds])
            ind2.append(nr)
            ind1.append(inds)
        nr = nr + 1

    return(ddc, ind1, ind2)
