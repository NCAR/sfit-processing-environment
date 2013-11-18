#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tools_bavo
import os,h5py
os.chdir('.')

sbctl=tools_bavo.trim_dict(tools_bavo.read_dictfile('sb.ctl')) #dict files are loaded with line numbers, ... trim removes this
ctl=tools_bavo.read_dictfile('sfit4.ctl',sfit4=True)
sbdict=tools_bavo.create_sfit4_sb(ctl,sbctl)
tools_bavo.update_dict(ctl,'option.sb',sbdict) #glue sb in ctl with a separate key (all keys starting with option are seperated from sfit4.cl)
retdata=tools_bavo.create_sfit4_retrievalsummary(ctl)
tools_bavo.create_sfit4_errorbudget(ctl,retdata)
tools_bavo.create_sfit4_retrievalplot(ctl,retdata,pdf='./test.pdf')

datafile='data.hdf'
del retdata['g'] #remove the contribution matrix, this is indirectly stored in the HDF file
with h5py.File(datafile,'w') as hdfid: tools_bavo.hdf_store(hdfid,'',retdata)
