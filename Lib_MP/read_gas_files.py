import read_from_file as rn
import numpy as np
import pdb
import re

def read_gasfiles(file):
    s = dict([])
    ascf = rn.read_from_file(file)
    headerline = ascf.get_line().split()
    mw_start = ascf.next(1).pop(0)
    mw_stop = ascf.next(1).pop(0)
    mw_res = ascf.next(1).pop(0)
    mw_nr = ascf.next(1).pop(0)
    while int(float(mw_nr)) < 1:
        mw_nr = ascf.next(1).pop(0) 
    clc = np.array(ascf.next(mw_nr))
    nu = np.array(range(0, mw_nr)) * mw_res + mw_start 

    
    s['gas'] = headerline[1]
    s['band'] = headerline[3]
    s['scan'] = headerline[5]
    s['iteration'] = headerline[7]
    s['mw_start'] = mw_start
    s['mw_stop'] = mw_stop
    s['mw_res'] = mw_res
    s['mw_nr'] = mw_nr
    s['clc'] = clc
    s['nu'] = nu

    return(s)
