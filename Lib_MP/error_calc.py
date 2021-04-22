#!/usr/bin/python

import sys
sys.path.append('/home/mathias/sfit-processing-environment/ModLib')

from Layer1Mods_v2 import errAnalysis
import sfitClasses as sc
import os,shutil
from multiprocessing import Pool
from functools import partial
import random, time
import gc

def calc_now(direc,sbctl,sbDefaults,rootdir):
    ctl = sc.CtlInputFile(direc+'/sfit4.ctl')
    ctl.getInputs()
    Sbctl = sc.CtlInputFile(sbctl)
    Sbctl.getInputs()
    SbctlDefaults = sc.CtlInputFile(sbDefaults)
    SbctlDefaults.getInputs()
    errAnalysis(ctl,Sbctl,SbctlDefaults,direc, False)
    try:    
        print ('errorcalculation in path: '+direc)
    except:
        print ('failed in path: '+direc)
        pass

    del ctl, Sbctl
    gc.collect()
    #        import ipdb
    #        ipdb.set_trace()
    # shutil.copy(direc+'/sfit4.ctl',rootdir)
    # shutil.copy(direc+'/'+ctl.inputs['file.in.stalayers'][0],
    #                 rootdir+'/'+'station.layers')
        


def error_calc(**kwargs):
    
    start_date = '19900101'
    end_date = '20301231'

    if not 'dir' in kwargs:
        print ('Please provide the path to the results (dir=...)')
        return()

    if not 'sbctl' in kwargs:
        print ('Please provide the path to the sb.ctl (sbctl=...')
        return()

    sbdefaults= kwargs['sbDefaults']        


    if 'start_date' in kwargs:
        start_date=kwargs['start_date']
    if 'end_date' in kwargs:
        end_date=kwargs['end_date']

    
    dd = list(filter(lambda x: os.path.isfile(kwargs['dir'] + '/' + x+'/sfit4.ctl')
                and x[0:8] >= start_date[0:8] 
                and x[0:8] <= end_date[0:8], os.listdir(kwargs['dir'])))

    dd.sort()
    print (start_date, end_date)
    direcs = []
    sbctl= kwargs['sbctl']
    for direc in dd:
        direcs.append(kwargs['dir']+'/'+direc)
#        calc_now(kwargs['dir']+'/'+direc,sbctl=sbctl,sbDefaults=sbdefaults,rootdir=kwargs['dir'])
    p = Pool(processes=4)

    p.map(partial(calc_now, sbctl=sbctl,sbDefaults=sbdefaults,rootdir=kwargs['dir']), direcs)

    
if __name__ == '__main__':
    import os,sys, getopt
    sys.path.append(os.path.dirname(sys.argv[0]))
    
    try:
        opts,arg = getopt.getopt(sys.argv[1:], [], ["dir=","sbctl=","start_date=","end_date=","sbdefaults="])
    except:
        print ('error in arguments')
        exit()
    
    args= 'error_calc('
    for opt,arg in opts:
        if opt == '--dir':
            args = args + 'dir="' + arg + '",'
        if opt == '--sbctl':
            args = args + 'sbctl="' + arg + '",'
        if opt == '--start_date':
            args = args + 'start_date="' + arg + '",'
        if opt == '--end_date':
            args = args + 'end_date="' + arg + '",'
        if opt == '--sbdefaults':
            print(arg)
            args = args + 'sbDefaults="' + arg + '",'
    args=args+')'
    eval(args)
