#!/usr/bin/python 

import os,sys
sys.path.append('/home/mathias/sfit-processing-environment/Lib_MP/')
sys.path.append('/home/mathias/sfit-processing-environment/Layer0/')

from read_result_sfit4 import summary,statevec
from sfit4Layer0 import sfit4Layer0

import numpy as np

sfit4_dir = '/home/mathias/sfit-core-code_new/'
#testcase_dir = '/home/mathias/sfit-core-code_new/test_cases_NDACC'
testcase_dir = '/home/mathias/test_cases'

#testcases=[
#    ['x.o3'],
#    ['x.clono2'],
#    ['x.co'],
#    ['x.hf'],
#    ['x.hcl'],
#    ['x.ccl4']
#]
testcases=[
    ['c2h6'],
    ['clono2'],
    ['hcl'],
    ['hcn'],
    ['hno3'],
    ['n2o'],
    ['no2'],
    ['o3']
]

orig_testcases = '/home/mathias/sfit4_tentative_testcases'


results = {}
results_orig = {}

for tc in testcases:
    tcpath = os.path.join(testcase_dir,tc[0])
    sf4l0args = ['-i',tcpath,
                 '-b',os.path.join(sfit4_dir,'src'),
                 '-f','hs']
    sfit4Layer0(sf4l0args)

    continue

    # Store values from summary
    sum_orig = summary(os.path.join(orig_testcases,'summary.%s'%(tc[0].split('.')[1])))
    result = {'apriori':sum_orig.apriori[0],
              'retriev':sum_orig.retriev[0],
              'chi_y_2':sum_orig.chi_y_2
              }
    results_orig.update({tc[0].split('.')[1]:result})
    
    sum_new = summary(os.path.join(tcpath,'summary'))
    result = {'apriori':sum_new.apriori[0],
              'retriev':sum_new.retriev[0],
              'chi_y_2':sum_new.chi_y_2
              }
    results.update({tc[0].split('.')[1]:result})
    
    #Store values from statevec
    state_orig = statevec(os.path.join(orig_testcases,'statevec.%s'%(tc[0].split('.')[1])))
    result = {'ret_profile': state_orig.rt_vmr[0]}
    results_orig[tc[0].split('.')[1]].update(result)

    state = statevec(os.path.join(tcpath,'statevec'))
    result = {'ret_profile': state.rt_vmr[0]}
    results[tc[0].split('.')[1]].update(result)

    
for rs in results.keys():
    print 'Testcase for:', rs
    print 'Target Apriori:', results[rs]['apriori'], results_orig[rs]['apriori'], 2*(results[rs]['apriori']-results_orig[rs]['apriori'])/(results[rs]['apriori']+results_orig[rs]['apriori'])
    print 'Target Retrieved:', results[rs]['retriev'], results_orig[rs]['retriev'], 2*(results[rs]['retriev']-results_orig[rs]['retriev'])/(results[rs]['retriev']+results_orig[rs]['retriev'])
    print 'CHI_Y_2:', results[rs]['chi_y_2'], results_orig[rs]['chi_y_2'], 2*(results[rs]['chi_y_2']-results_orig[rs]['chi_y_2'])/(results[rs]['chi_y_2']+results_orig[rs]['chi_y_2'])
    print 'MEAN SQARE Diff. RETRIEVED VMR:', np.sqrt(np.mean((results[rs]['chi_y_2']-results_orig[rs]['chi_y_2'])**2))
    

