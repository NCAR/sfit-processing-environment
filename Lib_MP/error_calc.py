#!/usr/bin/python

import sys
sys.path.append('/home/mathias/sfit-processing-environment/ModLib')

from Layer1Mods import errAnalysis
import sfitClasses as sc
import os,shutil



def error_calc(**kwargs):
    
    start_date = '19900101'
    end_date = '20301231'

    if not kwargs.has_key('dir'):
        print 'Please provide the path to the results (dir=...)'
        return()

    if not kwargs.has_key('sbctl'):
        print 'Please provide the path to the sb.ctl (sbctl=...'
        return()

    if kwargs.has_key('start_date'):
        start_date=kwargs['start_date']
    if kwargs.has_key('end_date'):
        end_date=kwargs['end_date']

    
    dd = filter(lambda x: os.path.isfile(kwargs['dir'] + '/' + x+'/sfit4.ctl')
                and x[0:8] >= start_date[0:8] 
                and x[0:8] <= end_date[0:8], os.listdir(kwargs['dir']))
    
    print start_date, end_date
    for direc in dd:
        ctl = sc.CtlInputFile(kwargs['dir']+'/'+direc+'/sfit4.ctl')
        ctl.getInputs()
        Sbctl = sc.CtlInputFile(kwargs['sbctl'])
        Sbctl.getInputs()
        try:    
            errAnalysis(ctl,Sbctl,kwargs['dir']+'/'+direc+'/', False)
            print 'errorcalculation in path: '+direc
        except:
            print 'failed in path: '+direc
            pass
#        import ipdb
#        ipdb.set_trace()
        shutil.copy(kwargs['dir']+'/'+direc+'/sfit4.ctl',kwargs['dir'])
        shutil.copy(kwargs['dir']+'/'+direc+'/'+ctl.inputs['file.in.stalayers'][0],
                    kwargs['dir']+'/'+'station.layers')
        
if __name__ == '__main__':
    import os,sys, getopt
    sys.path.append(os.path.dirname(sys.argv[0]))

    try:
        opts,arg = getopt.getopt(sys.argv[1:], [], ["dir=","sbctl=","start_date=","end_date="])
    except:
        print 'error in arguments'
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
    args=args+')'
    eval(args)
