#!/usr/bin/python

import sys
sys.path.append('/home/mathias/sfit-processing-environment/ModLib')

import sfitClasses as sc
import os,shutil
from multiprocessing import Pool
from functools import partial
import random, time
import gc

pyversion = sys.version_info


def run_sfit4(direc,sfit4):
    old_dir = os.path.realpath(os.path.curdir)
    os.chdir(direc)
    try:
        os.system(sfit4)
    except:
        pass
    os.chdir(old_dir)
    

def run_sfit4_in_direcs(**kwargs):
    
    start_date = '19900101'
    end_date = '20301231'
    nr_procs = 4

    if 'dir' not in kwargs:
        print ('Please provide the path to the results (dir=...)')
        return()
    if 'start_date' in kwargs:
        start_date=kwargs['start_date']
    if 'end_date' in kwargs:
        end_date=kwargs['end_date']
    if 'sfit4' in kwargs:
        sfit4=kwargs['sfit4']
    if 'nr_procs' in kwargs:
        nr_procs = kwargs['nr_procs']

    
    dd = list(filter(lambda x: os.path.isfile(kwargs['dir'] + '/' + x+'/sfit4.ctl')
                     and x[0:8] >= start_date[0:8] 
                     and x[0:8] <= end_date[0:8], os.listdir(kwargs['dir'])))

    dd.sort()
    print (start_date, end_date)
    direcs = []
    for direc in dd:
        direcs.append(kwargs['dir']+'/'+direc)

    p = Pool(processes=int(nr_procs))
    p.map(partial(run_sfit4, sfit4=sfit4), direcs)

if __name__ == '__main__':
    import os,sys, getopt
    sys.path.append(os.path.dirname(sys.argv[0]))
    
    try:
        opts,arg = getopt.getopt(sys.argv[1:], [], ["dir=","sfit4=","start_date=","end_date=","nr_procs="])
    except:
        print ('error in arguments')
        exit()
    
    args= 'run_sfit4_in_direcs('
    for opt,arg in opts:
        if opt == '--dir':
            args = args + 'dir="' + arg + '",'
        if opt == '--start_date':
            args = args + 'start_date="' + arg + '",'
        if opt == '--end_date':
            args = args + 'end_date="' + arg + '",'
        if opt == '--sfit4':
            args = args + 'sfit4="' + arg + '",'
        if opt == '--nr_procs':
            args = args + 'nr_procs="' + arg + '",'
    args=args+')'
    eval(args)
