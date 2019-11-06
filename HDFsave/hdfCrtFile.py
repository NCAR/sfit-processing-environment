#----------------------------------------------------------------------------------------
# Name:
#        hdfCrtFile.py
#
# Purpose:
#       Class to provide generic create HDF interface to hdf4/5 files
#
# License:
#    Copyright (c) 2013-2014 NDACC/IRWG
#    This file is part of sfit4.
#
#    sfit4 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    sfit4 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with sfit4.  If not, see <http://www.gnu.org/licenses/>
#
#----------------------------------------------------------------------------------------
import h5py
import itertools as it
import numpy as np
from pyhdf.SD import *
import sys


class HDF5File(object):
   ''' Interface for creating writing HDF5 files '''
   
   def __init__(self,dType):
      self.fopen = None
      self.dType = dType

   def createFile(self,filename, attrDict):
      ''' create hdf file and set global attributes'''
      
      #-------------------------------------------
      # Open file and write file global attributes
      #-------------------------------------------      
      self.fopen=h5py.File(filename,'w')
      
      for k,val in attrDict.iteritems():
         self.fopen.attrs[k] = val

   def createDataSet(self,dataSetName, dimSpec, data, attrDict, typeOvrd=''):
      ''' create dataset in hdf file and set its attributes'''
      
      tmpType = self.dType
      if typeOvrd: tmpType = typeOvrd      
      
      #-------------------------------
      # create data set and store data
      # as 32 or 64 precision
      #-------------------------------
      dtSet = self.fopen.create_dataset(dataSetName,data=data,dtype=tmpType)

      #-----------------
      # store attributes
      #-----------------
      for k,val in attrDict.iteritems():
         dtSet.attrs[k] = val

   def closeFile(self):
      #---------------
      # Close HDF file
      #---------------      
      self.fopen.close()
      
if __name__ == "__main__":
   print('Testing class')
   assert HDF5File()
   
   
class HDF4File(object):
   ''' Interface for creating writing HDF4 files '''
   
   def __init__(self,dType):
      self.fopen = None
      self.dType = dType

   def createFile(self,filename, attrDict):
      ''' create hdf file and set global attributes'''
      
      #-----------------
      # Create HDF4 file
      #-----------------    

      self.fopen = SD(filename,SDC.TRUNC | SDC.WRITE | SDC.CREATE) 

      
      #--------------------------------
      # Write global attributes to file
      #--------------------------------
      #for k,val in attrDict.iteritems():   # Syntax compatible with python 2x
      for k,val in attrDict.items():        # Syntax compatible with python 3
         setattr(self.fopen,k,val)

   
   def createDataSet(self,dataSetName, dimSpec, data, attrDict, typeOvrd=''):
      ''' create dataset in hdf file and set its attributes'''

      tmpType = self.dType
      if typeOvrd: tmpType = typeOvrd

      #---------------------------------------
      # Create HDF4 file. Write data as single
      # or double precision
      #---------------------------------------        
      if tmpType.lower() == 'float32': 
         dtSet = self.fopen.create(dataSetName,SDC.FLOAT32,dimSpec)
         data  = data.astype(np.float32) 
         
      elif tmpType.lower() == 'float64': 
         dtSet = self.fopen.create(dataSetName,SDC.FLOAT64,dimSpec)

      #-------------------
      # Store data in file
      #------------------- 
      if not np.size(data):
         print ('Variable: {} is empty. Unable to write empty variable. Terminating program'.format(dataSetName))
         sys.exit()      
      else: 
         dtSet[:] = data
      
      #---------------------------------------------------------------
      # Store attributes in file. Rules state that numerical meta-data
      # must have same data-type as data set.
      #---------------------------------------------------------------
      #for k,val in attrDict.iteritems():     # Syntax compatible with python 2x
      for k,val in attrDict.items():          # Syntax compatible with python 3
         
         #-------------------------------------------
         # Determine if attribute is string or number
         #-------------------------------------------
         if not isinstance(val,str):
            att = dtSet.attr(k)
            if   tmpType.lower() == 'float32': att.set(SDC.FLOAT32,val)
            elif tmpType.lower() == 'float64': att.set(SDC.FLOAT64,val)
            
         else: setattr(dtSet,k,val)

      #---------------------
      # Finish write to file
      #---------------------
      dtSet.endaccess()
     
   def closeFile(self):
      
      #---------------
      # Close HDF file
      #---------------      
      self.fopen.end()

