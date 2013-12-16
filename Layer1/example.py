#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tools_bavo
import os,h5py
sbctl=tools_bavo.trim_dict(tools_bavo.read_dictfile('sb.ctl')) #dict files are loaded with line numbers, ... trim removes this
#os.chdir('/dev/shm/bavol/testbavon2o/12223002.Shh/NO2/')
ctl=tools_bavo.read_dictfile('sfit4.ctl',sfit4=True)
tools_bavo.update_dict(ctl,'option.sb',tools_bavo.create_sfit4_sb(ctl,sbctl))


retdata=tools_bavo.create_sfit4_retrievalsummary(ctl)
tools_bavo.create_sfit4_errorbudget(retdata)
tools_bavo.create_sfit4_retrievalplot(retdata,plots=['pro','col'],pdf='./test.pdf')

datafile='data.hdf'
del retdata['g'] #remove the contribution matrix, this is indirectly stored in the HDF file
with h5py.File(datafile,'w') as hdfid: tools_bavo.hdf_store(hdfid,'',retdata)