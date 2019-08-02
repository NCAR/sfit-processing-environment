# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 09:14:38 2013

@author: wolf
"""
import struct
import numpy as np

def get_param_idx(fff,idx,paramname):
    ##print   'called get_param_idx'
    value='None'
    paramname=paramname[0:3]
    


    global pointernamearr
    global blocktypar
    global blocklenarr
    global blockpntarr
    global blockidarr
    global formatarr
    
    pointernamearr=[]
    blocktyparr=[]
    blocklenarr=[]
    blockpntarr=[]    
    fff.seek(0)
    field1=np.fromfile(fff,dtype='int32',count=1)
    ##print  field1
    field2=np.fromfile(fff,dtype='float64',count=1)
    field3=np.fromfile(fff,dtype='int32',count=1)
    field4=np.fromfile(fff,dtype='int32',count=1)
    field5=np.fromfile(fff,dtype='int32',count=1)
    #print  field2,field3,field4,field5

    magic_opus_number=field1[0]
    opus_version=field2[0]
    ipdb=field3[0] # pointer , byt offset to directory block
    mndb=field4[0] # maximal N byts in directory block b, maximal number of entries
    ndb=field5[0] # N byts in directory block; number of entries
    ##print  ndb
########################################################
    #;;;;;;;;;;;;;;;;;

    #print  'ndb',ndb
    if idx == -1:
        #print  'look for parameter in all blocks and return el primer valor'
        for idx in range(ndb):
            #print  'idx',idx
            value=get_param_idx(fff,idx,paramname)
            #print  'listo'
            #print  value
            if bytes(value) == bytes('None'):
                print  'value todavia -1',value
              
            else:
                print  'value not -1',value
                return value
                #return value
                
    #print   'idx', idx   
             
    for i in range(ndb):
        field6=np.fromfile(fff,dtype='int32',count=1)
        blocktyparr.append(field6[0])
        field7=np.fromfile(fff,dtype='int32',count=1)
        blocklenarr.append(field7[0])
        field8=np.fromfile(fff,dtype='uint32',count=1)
        blockpntarr.append(field8[0])

    #indexparameter=parameterlist.index(paramname)
    #formatflag=formatflagarr[indexparameter]
    ##print  'get_param'
    ipoint=blockpntarr[idx]
    blocklength=blocklenarr[idx]
    ##print  blocklength    
    fff.seek(ipoint)
    for i in range(blocklength-1):
        param=fff.read(4)
        ##print  param
        if param[0:3] == paramname[0:3]:
            endflag=param[3]
            #print  'hola',param 
            param=fff.read(2)
            ##print  param 
            dtype=struct.unpack('h',param)
            dtype=dtype[0]
            ##print  'dtype'
            ##print  dtype
            if dtype == 0:
                param=fff.read(2)
                param=fff.read(4)
                value=struct.unpack('i',param) 
                value=value[0]
                ##print  'value',value
                return value
            if dtype == 1:   
                param=fff.read(2)
                param=fff.read(8)
                value=struct.unpack('d',param)
                value=value[0]                
                ##print  blockid,paramname,dtype,value
                return value
            if dtype == 2:
                param=fff.read(2)
                strlen=struct.unpack('h',param)
                strlen=2*strlen[0]
                param=fff.read(strlen)
                value=str(param) 
                ie=value.find(endflag)
                value=value[0:ie]
                ##print  blockid,paramname,dtype,value
                return value
            if dtype == 3:
                param=fff.read(2)
                nextbyte=struct.unpack('h',param)
                ##print  nextbyte
                param=fff.read(nextbyte[0])
                value=str(param)
                ##print  'value',endflag
                ##print  value
                param=fff.read(2)
                ##print  blockid,paramname,dtype,value
                return value
            if dtype == 4:
                param=fff.read(2)
                strlen=struct.unpack('h',param)
                strlen=strlen[0]*2
                ##print  strlen
                param=fff.read(strlen)
                value=str(param)
                ie=value.find(endflag)
                value=value[0:ie]
                ##print  blockid,paramname,dtype,value
                return value  
            return 'None' 
