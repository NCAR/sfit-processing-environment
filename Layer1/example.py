#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tools_bavo
import os,h5py
os.chdir('.')
ctl=tools_bavo.read_dictfile('sfit4.ctl',sfit4=True)
sbctl=tools_bavo.trim_dict(tools_bavo.read_dictfile('sb.ctl')) #trim is to get rid of the line numbers...
tools_bavo.update_dict(ctl,'option.sb',sbctl) #glue sb in ctl with a separate key 
retdata=tools_bavo.create_sfit4_retrievalsummary(ctl)
ctl=tools_bavo.trim_dict(ctl)
tools_bavo.create_sfit4_errorbudget(ctl,retdata)
tools_bavo.create_sfit4_retrievalplot(ctl,retdata,pdf='./test.pdf')

datafile='data.hdf'
del retdata['g'] #remove the contribution matrix, this is indirectly stored in the HDF file
with h5py.File(datafile,'w') as hdfid: tools_bavo.hdf_store(hdfid,'',retdata)
