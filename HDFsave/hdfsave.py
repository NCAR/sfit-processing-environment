#----------------------------------------------------------------------------------------
# Name:
#        metaRetDat.py
#
# Purpose:
#       Real class of HDFbaseRetDat, defining the attribute values
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
#    Note!!!! You can not have empty strings. HDF will fail to write if there are 
#             empty strings. Must at least contain a space character (i.e. ' ')
#
#----------------------------------------------------------------------------------------
import hdfBaseRetDat
import numpy as np
import math
import collections as cl
import hdfInitData

class HDFsave(hdfBaseRetDat.HDFbaseRetDat,hdfInitData.HDFinitData):

   def __init__(self,gasNameStr,outputDir,processingSfitVer,location,instrument,attr_file,granu,mtype,source,dType):
      super(HDFsave, self).__init__(gasNameStr,type=source)
      self.dType               = dType
      if   dType.lower() == 'float32': self.dTypeStr = 'REAL'
      elif dType.lower() == 'float64': self.dTypeStr = 'DOUBLE'       
      self.outDir              = outputDir
      self.gasName             = gasNameStr
      self.gasNameUpper        = gasNameStr.upper()
      self.sfitVer             = processingSfitVer
      self.loc                 = location
      self.mxSclFctName        = 'ppmv'               
      self.mxSclFctVal         = 1E-6                   
      self.mxSclFct2Name       = 'ppmv2'
      self.mxSclFct2Val        = 1E-12
      self.attribute_file      = attr_file
      self.locID               = instrument
      self.granularity         = granu
      self.mtype               = mtype
      

   def glblAttrbs(self,fDOI,idate,fdate):
      ''' Meta-data for hdf file (Global Attributes) '''

      idateStr = "{0:04d}{1:02d}{2:02d}T{3:02d}{4:02d}{5:02d}Z".format(idate.year,idate.month,idate.day,idate.hour,idate.minute,idate.second)
      fdateStr = "{0:04d}{1:02d}{2:02d}T{3:02d}{4:02d}{5:02d}Z".format(fdate.year,fdate.month,fdate.day,fdate.hour,fdate.minute,fdate.second)

      dataStr = cl.OrderedDict()
      dataStr2 = cl.OrderedDict()


      dataStr['DATA_FILE_VERSION']       = '004'
      dataStr['DATA_TEMPLATE']           = 'GEOMS-TE-FTIR-002'
      if False and self.granularity == 'yearly':
         file_idateStr = "{0:04d}{1:02d}{2:02d}T{3:02d}{4:02d}{5:02d}Z".format(idate.year,1,1,0,0,0)
         file_fdateStr = "{0:04d}{1:02d}{2:02d}T{3:02d}{4:02d}{5:02d}Z".format(fdate.year,12,31,23,59,59)
      else:
         file_idateStr = idateStr
         file_fdateStr = fdateStr
      dataStr['DATA_START_DATE']         = file_idateStr
      dataStr['DATA_STOP_DATE']          = file_fdateStr
      file_idateStr = file_idateStr.lower()
      file_fdateStr = file_fdateStr.lower()

         

      dataStr['FILE_GENERATION_DATE']    = "{0:04d}{1:02d}{2:02d}T{3:02d}{4:02d}{5:02d}Z".format(fDOI.year,fDOI.month,fDOI.day,fDOI.hour,fDOI.minute,fDOI.second)
      
      dataStr['PI_NAME']                 = '!!!CHANGE!!!'
      dataStr['PI_AFFILIATION']          = '!!!CHANGE!!!'
      dataStr['PI_ADDRESS']              = '!!!CHANGE!!!'
      dataStr['PI_EMAIL']                = '!!!CHANGE!!!'
      dataStr['DO_NAME']                 = '!!!CHANGE!!!'
      dataStr['DO_AFFILIATION']          = '!!!CHANGE!!!'
      dataStr['DO_ADDRESS']              = '!!!CHANGE!!!'
      dataStr['DO_EMAIL']                = '!!!CHANGE!!!'
      dataStr['DS_NAME']                 = '!!!CHANGE!!!'
      dataStr['DS_AFFILIATION']          = '!!!CHANGE!!!'
      dataStr['DS_ADDRESS']              = '!!!CHANGE!!!'
      dataStr['DS_EMAIL']                = '!!!CHANGE!!!'
      dataStr['DATA_DESCRIPTION']        = '!!!CHANGE!!!'
      dataStr['DATA_DISCIPLINE']         = '!!!CHANGE!!!'
      dataStr['DATA_GROUP']              = '!!!CHANGE!!!'
      dataStr['DATA_LOCATION']           = '!!!CHANGE!!!'
      dataStr['DATA_MODIFICATIONS']      = '!!!CHANGE!!!' 
      dataStr['DATA_TEMPLATE']           = '!!!CHANGE!!!' 
      dataStr['DATA_QUALITY']            = '!!!CHANGE!!!' 
      dataStr['DATA_CAVEATS']            = '!!!CHANGE!!!'
      dataStr['DATA_RULES_OF_USE']       = '!!!CHANGE!!!'
      dataStr['DATA_ACKNOWLEDGEMENT']    = '!!!CHANGE!!!'
      dataStr['FILE_DOI']                = '!!!CHANGE!!!'
      dataStr['FILE_ACCESS']             = '!!!CHANGE!!!'
      dataStr['FILE_PROJECT_ID']         = '!!!CHANGE!!!'
      dataStr['FILE_ASSOCIATION']        = '!!!CHANGE!!!'
      dataStr['FILE_META_VERSION']       = '!!!CHANGE!!!'
                                           
      dataStr['DATA_SOURCE']             = 'FTIR.'+self.gasName+'_'+self.locID.upper()      
      dataStr['DATA_VARIABLES']          = self.getDatetimeName()+';'+self.getLatitudeInstrumentName()+';'\
                                           +self.getLongitudeInstrumentName()+';'+self.getAltitudeInstrumentName()+';'+ \
                                           self.getSurfacePressureIndependentName()+';'+  \
                                           self.getSurfaceTemperatureIndependentName()+';'+\
                                           self.getAltitudeName()+';'+self.getAltitudeBoundariesName()+';'\
                                           +self.getPressureIndependentName()+';'+                 \
                                           self.getTemperatureIndependentName()+';'+\
                                           self.getIntegrationTimeName()+';'+\
                                           self.gasName+'.'+self.getMixingRatioAbsorptionSolarName()+';'+\
                                           self.gasName+'.'+self.getMixingRatioAbsorptionSolarAprioriName()+';'+      \
                                           self.gasName+'.'+self.getMixingRatioAbsorptionSolarAvkName()+';'+\
                                           self.gasName+'.'+self.getMixingRatioAbsorptionSolarUncertaintyRandomName()+';'+\
                                           self.gasName+'.'+self.getMixingRatioAbsorptionSolarUncertaintySystematicName()+';'+\
                                           self.gasName+'.'+self.getColumnPartialAbsorptionSolarName()+';'+           \
                                           self.gasName+'.'+self.getColumnPartialAbsorptionSolarAprioriName()+';'+\
                                           self.gasName+'.'+self.getColumnAbsorptionSolarName()+';'+\
                                           self.gasName+'.'+self.getColumnAbsorptionSolarAprioriName()+';'+      \
                                           self.gasName+'.'+self.getColumnAbsorptionSolarAvkName()+';'+\
                                           self.gasName+'.'+self.getColumnAbsorptionSolarUncertaintyRandomName()+';'+\
                                           self.gasName+'.'+self.getColumnAbsorptionSolarUncertaintySystematicName()+';'+\
                                           self.getAngleSolarZenithAstronomicalName()+';'+self.getAngleSolarAzimuthName()

      if self.gasName.upper() != 'H2O':
         dataStr['DATA_VARIABLES'] = dataStr['DATA_VARIABLES'] +';'+\
                                     self.getH2oMixingRatioAbsorptionSolarName()+';'+self.getH2oColumnAbsorptionSolarName()

      

      fid = open(self.attribute_file)
      for line in fid.readlines():
         val = line.split('=')
         dataStr[val[0].strip()] = str(val[1].strip())
      fid.close()

      dataStr['FILE_NAME']               = 'groundbased_ftir.'+self.gasName.lower()+'_'+self.locID.lower()+'_'+self.loc.lower()+'_'+file_idateStr+'_'+file_fdateStr+'_'+dataStr['DATA_FILE_VERSION']+'.hdf'
      print (dataStr['FILE_NAME'])

      
      return dataStr

   def datetimeAttrbs(self,nsize):
      ''' Attributes for retrieval date and time variable.'''
      
      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.getDatetimeName()
      dataStr['VAR_DESCRIPTION']      = 'Griddatetime (UT) defined relative to reference datetime of Jan. 1 2000 at 0]00]00 UT which is equal to 0.00'
      dataStr['VAR_NOTES']            = 'None'
      dataStr['VAR_SIZE']             = str(nsize)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()
      dataStr['VAR_DATA_TYPE']        = 'DOUBLE'
      dataStr['VAR_UNITS']            = 'MJD2K'
      dataStr['VAR_SI_CONVERSION']    = '0.0;86400.0;s'
      dataStr['VAR_VALID_MIN']        = -9000.0
      dataStr['VAR_VALID_MAX']        =  100000.0
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (-9000.0,100000.0)
      dataStr['units']                = 'MJD2K'
      dataStr['_FillValue']           = self.getFillValue()

      
      return dataStr

   def latAttrbs(self,nsize):
      ''' Attributes for instrument latitude variable '''

      dataStr = cl.OrderedDict()
      
      dataStr['VAR_NAME']             = self.getLatitudeInstrumentName()
      dataStr['VAR_DESCRIPTION']      = 'Latitude of the instrument location, positive North'
      dataStr['VAR_NOTES']            = 'None'
      dataStr['VAR_SIZE']             = str(nsize)
      if self.mtype.lower() == 'stationary':
         dataStr['VAR_DEPEND']           = 'CONSTANT'
      elif self.mtype.lower() == 'mobile':
         dataStr['VAR_DEPEND']           = self.getDatetimeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'deg'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.74533E-2;rad'
      dataStr['VAR_VALID_MIN']        = -90.0
      dataStr['VAR_VALID_MAX']        =  90.0
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (-90.0,90.0)
      dataStr['units']                = 'deg'
      dataStr['_FillValue']           = self.getFillValue()

      return dataStr

   def lonAttrbs(self,nsize):
      ''' Attributes for instrument longitude variable '''

      dataStr = cl.OrderedDict()
      
      dataStr['VAR_NAME']             = self.getLongitudeInstrumentName()
      dataStr['VAR_DESCRIPTION']      = 'Longitude of the instrument location, positive East'
      dataStr['VAR_NOTES']            = 'None'
      dataStr['VAR_SIZE']             = str(nsize)
      if self.mtype.lower() == 'stationary':
         dataStr['VAR_DEPEND']           = 'CONSTANT'
      elif self.mtype.lower() == 'mobile':
         dataStr['VAR_DEPEND']           = self.getDatetimeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'deg'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.74533E-2;rad'
      dataStr['VAR_VALID_MIN']        = -180.0
      dataStr['VAR_VALID_MAX']        =  180.0
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (-180.0,180.0)
      dataStr['units']                = 'deg'
      dataStr['_FillValue']           = self.getFillValue()

      return dataStr

   def instAltAttrbs(self,nsize):
      ''' Attributes for instrument altitude variable '''

      dataStr = cl.OrderedDict()
      
      dataStr['VAR_NAME']             = self.getAltitudeInstrumentName()
      dataStr['VAR_DESCRIPTION']      = 'altitude of the location of the instrument'
      dataStr['VAR_NOTES']            = 'None'
      dataStr['VAR_SIZE']             = str(nsize)
      if self.mtype.lower() == 'stationary':
         dataStr['VAR_DEPEND']           = 'CONSTANT'
      elif self.mtype.lower() == 'mobile':
         dataStr['VAR_DEPEND']           = self.getDatetimeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'km'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.0E3;m'
      dataStr['VAR_VALID_MIN']        = -0.05
      dataStr['VAR_VALID_MAX']        =  10.0
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (-0.05,10.0)
      dataStr['units']                = 'km'    
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def surfpAttrbs(self,nsize):
      ''' Attributes for instrument surface pressure variable '''

      dataStr = cl.OrderedDict()
      
      dataStr['VAR_NAME']             = self.getSurfacePressureIndependentName()
      dataStr['VAR_DESCRIPTION']      = 'Daily average surface pressure measured at the observation site'
      dataStr['VAR_NOTES']            = 'Values are operational data recorded by weather station near instrument. If not available, ' +\
                                        'NCEP daily pressure interpolated to instrument alitude used.'
      dataStr['VAR_SIZE']             = str(nsize)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'hPa'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.0E2;kg m-1 s-2'
      dataStr['VAR_VALID_MIN']        = 0.0
      dataStr['VAR_VALID_MAX']        = 1100.0
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (0.0,1100.0)
      dataStr['units']                = 'hPa'
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def surftAttrbs(self,nsize):
      ''' Attributes for instrument surface temperature variable '''

      dataStr = cl.OrderedDict()
      
      dataStr['VAR_NAME']             = self.getSurfaceTemperatureIndependentName()
      dataStr['VAR_DESCRIPTION']      = 'Daily average temperature at ground level measured at the observation site'
      dataStr['VAR_NOTES']            = 'Values are operational data recorded by weather station near instrument. If not available, ' +\
                                        'NCEP daily temperature interpolated to instrument alitude used.'
      dataStr['VAR_SIZE']             = str(nsize)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'K'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.0;K'
      dataStr['VAR_VALID_MIN']        = 0.0
      dataStr['VAR_VALID_MAX']        = 500.0
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (0.0,500.0)
      dataStr['units']                = 'K'
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def AltAttrbs(self,nlyrs,minval,maxval):
      ''' Attributes for altitude variable '''

      dataStr = cl.OrderedDict()
      
      dataStr['VAR_NAME']             = self.getAltitudeName()
      dataStr['VAR_DESCRIPTION']      = 'Grid of altitude levels upon which the retrieved target vmr profile as well as pressure and temperature profiles are reported'
      dataStr['VAR_NOTES']            = 'These altitudes are the centers of the retrieval altitude layers (geometric mean between the 2 layer boundaries); the reported vmr, P and T are effective layer values'
      dataStr['VAR_SIZE']             = str(nlyrs)
      dataStr['VAR_DEPEND']           = 'ALTITUDE'
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'km'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.0E3;m'
      dataStr['VAR_VALID_MIN']        = minval
      dataStr['VAR_VALID_MAX']        = maxval
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (minval,maxval)
      dataStr['units']                = 'km'
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def AltBndsAttrbs(self,nlyrs):
      ''' Attributes for altitude boundaries variable '''

      dataStr = cl.OrderedDict()
      
      dataStr['VAR_NAME']             = self.getAltitudeBoundariesName()
      dataStr['VAR_DESCRIPTION']      = '2D matrix providing the layer boundaries used for vertical profile retrieval'
      dataStr['VAR_NOTES']            = 'The retrieved partial columns are given between the boundaries provided in this vector. The lowermost boundary is equal to ALTITUDE.INSTRUMENT'
      dataStr['VAR_SIZE']             = str(2)+';'+str(nlyrs)
      dataStr['VAR_DEPEND']           = 'INDEPENDENT;'+self.getAltitudeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'km'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.0E3;m'
      dataStr['VAR_VALID_MIN']        = 0.0
      dataStr['VAR_VALID_MAX']        = 150.0
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (0.0,150.0)
      dataStr['units']                = 'km'
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def pressAttrbs(self,nlyrs,nsize):
      ''' Attributes for pressure profile variable '''

      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.getPressureIndependentName()
      dataStr['VAR_DESCRIPTION']      = 'Effective air pressures in retrieval grid layers'
      dataStr['VAR_NOTES']            = 'A priori pressure and temperature profiles are taken from NCEP; the pressure values represent the effective pressure in each layer and are reported at the center altitude of each layer. Above NCEP (~32 km) WACCM monthly mean pressure is used'
      dataStr['VAR_SIZE']             = str(nsize)+";"+str(nlyrs)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()+';'+self.getAltitudeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'hPa'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.0E2;kg m-1 s-2'
      dataStr['VAR_VALID_MIN']        = 0.0
      dataStr['VAR_VALID_MAX']        = 1100.0
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (0.0,1100.0)
      dataStr['units']                = 'hPa'
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def tempAttrbs(self,nlyrs,nsize,maxval):
      ''' Attributes for temperature profile variable '''

      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.getTemperatureIndependentName()
      dataStr['VAR_DESCRIPTION']      = 'Effective air temperatures in retrieval grid layers'
      dataStr['VAR_NOTES']            = 'A priori pressure and temperature profiles are taken from NCEP; the pressure values represent the effective pressure in each layer and are reported at the center altitude of each layer. Above NCEP (~32 km) WACCM monthly mean pressure is used'
      dataStr['VAR_SIZE']             = str(nsize)+";"+str(nlyrs)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()+';'+self.getAltitudeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'K'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.0;K'
      dataStr['VAR_VALID_MIN']        = 0.0
      dataStr['VAR_VALID_MAX']        = 500.0
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (0.0,500.0)
      dataStr['units']                = 'K'
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr


   def airmassAttrbs(self,nlyrs,nsize,maxval):
      ''' Attributes for airmass profile variable '''

      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.getAirmassName()
      dataStr['VAR_DESCRIPTION']      = 'Airmass on retrieval grid layers'
      dataStr['VAR_NOTES']            = 'The airmass is calculated on layers and represent the mass of air of the layer.'
      dataStr['VAR_SIZE']             = str(nsize)+";"+str(nlyrs)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()+';'+self.getAltitudeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'TBD'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.0;TBD'
      dataStr['VAR_VALID_MIN']        = 0.0
      dataStr['VAR_VALID_MAX']        = 1E25
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (0.0,1E25)
      dataStr['units']                = 'TBD'
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def rprfAttrbs(self,nlyrs,nsize,maxval):
      ''' Attributes for retrieved vertical profile from solar absorption measurements in VMR units '''

      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.gasName+'.'+self.getMixingRatioAbsorptionSolarName()
      dataStr['VAR_DESCRIPTION']      = 'Retrieved mixing ratio profile of {} '.format(self.gasName)
      dataStr['VAR_NOTES']            = 'Retrieval algorithm sfit4 version: ' + self.sfitVer + ' NDACC IRWG retrieval strategy. HITRAN2008 spectroscopy'
      dataStr['VAR_SIZE']             = str(nsize)+";"+str(nlyrs)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()+';'+self.getAltitudeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = self.mxSclFctName
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.0E{};1'.format(int(math.log10(self.mxSclFctVal)))
      dataStr['VAR_VALID_MIN']        = -maxval/10.0
      dataStr['VAR_VALID_MAX']        = maxval
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (-maxval/10.0,maxval)
      dataStr['units']                = self.mxSclFctName
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def aprfAttrbs(self,nlyrs,nsize,maxval):
      ''' Attributes for a priori vertical profile from solar absorption measurements in VMR units '''

      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.gasName+'.'+self.getMixingRatioAbsorptionSolarAprioriName()
      dataStr['VAR_DESCRIPTION']      = 'A priori mixing raito profile of {}'.format(self.gasName)
      dataStr['VAR_NOTES']            = 'The same a priori vertical profile is used for all days in the present datafile and is based on WACCM 1980-2020 output'
      dataStr['VAR_SIZE']             = str(nsize)+";"+str(nlyrs)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()+';'+self.getAltitudeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = self.mxSclFctName
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.0E{};1'.format(int(math.log10(self.mxSclFctVal)))
      dataStr['VAR_VALID_MIN']        = 0.0
      dataStr['VAR_VALID_MAX']        = maxval
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (0.0,maxval)
      dataStr['units']                = self.mxSclFctName
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def avkAttrbs(self,nlyrs,nsize):
      ''' Attributes for averaging kernel matrix (AVK) of the retrieved vertical profile in VMR/VMR units '''

      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.gasName+'.'+self.getMixingRatioAbsorptionSolarAvkName()
      dataStr['VAR_DESCRIPTION']      = 'Averaging kernel matrix (AVK) of the retrieved vertical profile of {} in VMR/VMR units'.format(self.gasName)
      dataStr['VAR_NOTES']            = 'Columns of AVK are the fastest running index (see https://wiki.ucar.edu/display/sfit4/Post-Processing)'
      dataStr['VAR_SIZE']             = str(nsize)+";"+str(nlyrs)+";"+str(nlyrs)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()+';'+self.getAltitudeName()+';'+self.getAltitudeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = '1'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.0;1'
      dataStr['VAR_VALID_MIN']        = -1000.0
      dataStr['VAR_VALID_MAX']        = 1000.0
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (-1000.0,1000.0)
      dataStr['units']                = '1'
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def intTAttrbs(self,nsize):
      ''' Attributes for duration of the measurement of the interferogram (and thus spectrum) from which the profile has been retrieved '''

      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.getIntegrationTimeName()
      dataStr['VAR_DESCRIPTION']      = 'Duration of the measurement of the interferogram (and thus spectrum) from which the profile has been retrieved'
      dataStr['VAR_NOTES']            = 'The duration of the measurement may include 1 or more scans (inteferograms) coadded together'
      dataStr['VAR_SIZE']             = str(nsize)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 's'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.0;s'
      dataStr['VAR_VALID_MIN']        = 0.0
      dataStr['VAR_VALID_MAX']        = 21600.0
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (0.0,21600.0)
      dataStr['units']                = 's'
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def mRandAttrbs(self,nlyrs,nsize):
      ''' Attributes for total random error covariance matrix associated with the retrieved vertical profiles in VMR units '''

      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.gasName+'.'+self.getMixingRatioAbsorptionSolarUncertaintyRandomName()
      dataStr['VAR_DESCRIPTION']      = 'Total random error covariance matrix associated with the retrieved vertical profiles of {} in VMR units'.format(self.gasName)
      dataStr['VAR_NOTES']            = 'Random errors include: Temperature, SZA, and Measurement noise. Temperature errors are determined by comparing ' +\
                                        'radiosonde data with NCEP temperature profiles. SZA error is set at 0.10 degs. Measurement noise is calculated ' +\
                                        'using the SNR.'
      dataStr['VAR_SIZE']             = str(nsize)+";"+str(nlyrs)+";"+str(nlyrs)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()+';'+self.getAltitudeName()+';'+self.getAltitudeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = self.mxSclFct2Name
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.0E{};1'.format(int(math.log10(self.mxSclFct2Val)))
      dataStr['VAR_VALID_MIN']        = -1000.0
      dataStr['VAR_VALID_MAX']        = 1000.0
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (-1000.0,1000.0)
      dataStr['units']                = self.mxSclFct2Name
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def mSysAttrbs(self,nlyrs,nsize):
      ''' Attributes for total systematic error covariance matrix associated with the retrieved vertical profiles in VMR units '''

      dataStr = cl.OrderedDict()
      
      dataStr['VAR_NAME']             = self.gasName+'.'+self.getMixingRatioAbsorptionSolarUncertaintySystematicName()
      dataStr['VAR_DESCRIPTION']      = 'Total systematic error covariance matrix associated with the retrieved vertical profiles of {} in VMR units'.format(self.gasName)
      dataStr['VAR_NOTES']            = 'Systematic error includes: Temperature, and Line Parameters. Temperature errors are determined by comparing ' +\
                                        'radiosonde data with NCEP temperature profiles. Line parameter errors are set at 4% as given ' + \
                                        'in Harrison et al., 2010 (JQRST). Smoothing error is not included.'
      dataStr['VAR_SIZE']             = str(nsize)+";"+str(nlyrs)+";"+str(nlyrs)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()+';'+self.getAltitudeName()+';'+self.getAltitudeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = self.mxSclFct2Name
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.0E{};1'.format(int(math.log10(self.mxSclFct2Val)))
      dataStr['VAR_VALID_MIN']        = -1000.0
      dataStr['VAR_VALID_MAX']        = 1000.0
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (-1000.0,1000.0)
      dataStr['units']                = self.mxSclFct2Name
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def pcRtrprfAttrbs(self,nlyrs,nsize):
      ''' Attributes for retrieved partial columns in the retrieval layers '''

      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.gasName+'.'+self.getColumnPartialAbsorptionSolarName()
      dataStr['VAR_DESCRIPTION']      = 'Retrieved {} (vertical) partial columns in the retrieval layers'.format(self.gasName)
      dataStr['VAR_NOTES']            = 'Values depend on VMR and vertical airmass'
      dataStr['VAR_SIZE']             = str(nsize)+";"+str(nlyrs)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()+';'+self.getAltitudeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'molec cm-2'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.66054E-20;mol m-2'
      if self.gasName.upper() == 'H2O':
         dataStr['VAR_VALID_MIN']        = -1.0E17
         dataStr['VAR_VALID_MAX']        = 1.0E25
         dataStr['VALID_RANGE']          = (-1.0E17,1.0E25)
      else:
         dataStr['VAR_VALID_MIN']        = -1.0E17
         dataStr['VAR_VALID_MAX']        = 1.0E20
         dataStr['VALID_RANGE']          = (-1.0E17,1.0E20)
      dataStr['units']                = 'molec cm-2'
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()*dataStr['VAR_VALID_MAX']
      dataStr['_FillValue']           = self.getFillValue()*dataStr['VAR_VALID_MAX']
      
      return dataStr

   def pcaAprfAttrbs(self,nlyrs,nsize):
      ''' Attributes for a priori partial columns in the retrieval layers '''
      
      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.gasName+'.'+self.getColumnPartialAbsorptionSolarAprioriName()
      dataStr['VAR_DESCRIPTION']      = 'A priori {} (vertical) partial columns in the retrieval layers'.format(self.gasName)
      dataStr['VAR_NOTES']            = 'Partial column evaluations use a priori pressure and temperature values from NCEP'
      dataStr['VAR_SIZE']             = str(nsize)+";"+str(nlyrs)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()+';'+self.getAltitudeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'molec cm-2'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.66054E-20;mol m-2'
      dataStr['VAR_VALID_MIN']        = 0.0
      dataStr['VAR_VALID_MAX']        = 1.0E20
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (0.0,1.0E20)
      dataStr['units']                = 'molec cm-2'
      dataStr['_FillValue']          = self.getFillValue()
      
      return dataStr

   def tcRprfAttrbs(self,nsize):
      ''' Attributes for total column from retrieved profile '''

      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.gasName+'.'+self.getColumnAbsorptionSolarName()
      dataStr['VAR_DESCRIPTION']      = 'Retrieved total vertical column for {} corresponding to retrieved vmr profiles'.format(self.gasName)
      dataStr['VAR_NOTES']            = 'None'
      dataStr['VAR_SIZE']             = str(nsize)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'molec cm-2'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.66054E-20;mol m-2'
      dataStr['VAR_VALID_MIN']        = 0.0
      dataStr['VAR_VALID_MAX']        = 1.0E20
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (0.0,1.0E20)
      dataStr['units']                = 'molec cm-2'
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def tcAprfAttrbs(self,nsize):
      ''' Attributes for total column from a priori profile '''

      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.gasName+'.'+self.getColumnAbsorptionSolarAprioriName()
      dataStr['VAR_DESCRIPTION']      = 'A priori total vertical column for {} corresponding to a priori vmr profiles'.format(self.gasName)
      dataStr['VAR_NOTES']            = 'None'
      dataStr['VAR_SIZE']             = str(nsize)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'molec cm-2'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.66054E-20;mol m-2'
      dataStr['VAR_VALID_MIN']        = 0.0
      dataStr['VAR_VALID_MAX']        = 1.0E20
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (0.0,1.0E20)
      dataStr['units']                = 'molec cm-2'
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def tcAvkAttrbs(self,nlyrs,nsize):
      ''' Attributes for total column averaging kernel '''

      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.gasName+'.'+self.getColumnAbsorptionSolarAvkName()
      dataStr['VAR_DESCRIPTION']      = 'Total vertical column averaging kernel for {} derived from retrieved mixing ratio averaging kernel'.format(self.gasName)
      dataStr['VAR_NOTES']            = 'This averaging kernel multiplies the partial column vector in order to get smoothed total column'
      dataStr['VAR_SIZE']             = str(nsize)+";"+str(nlyrs)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()+';'+self.getAltitudeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = '1'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.0;1'
      dataStr['VAR_VALID_MIN']        = -10.0
      dataStr['VAR_VALID_MAX']        =  10.0
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (-10.0,10.0)
      dataStr['units']                = '1'
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def tcRandAttrbs(self,nsize):
      ''' Attributes for total column random uncertainty'''

      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.gasName+'.'+self.getColumnAbsorptionSolarUncertaintyRandomName()
      dataStr['VAR_DESCRIPTION']      = 'Estimated total random uncertainty on the retrieved total vertical columns of {}'.format(self.gasName)
      dataStr['VAR_NOTES']            = 'See notes for total random error covariance matrix'
      dataStr['VAR_SIZE']             = str(nsize)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'molec cm-2'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.66054E-20;mol m-2'
      dataStr['VAR_VALID_MIN']        = 0.0
      dataStr['VAR_VALID_MAX']        = 1.0E20
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (0.0,1.0E20)
      dataStr['units']                = 'molec cm-2'
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def tcSysAttrbs(self,nsize):
      ''' Attributes for total column systematic uncertainty'''

      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.gasName+'.'+self.getColumnAbsorptionSolarUncertaintySystematicName()
      dataStr['VAR_DESCRIPTION']      = 'Estimated total systematic uncertainty on the retrieved total vertical columns of {}'.format(self.gasName)
      dataStr['VAR_NOTES']            = 'See notes for total systematic error covariance matrix'
      dataStr['VAR_SIZE']             = str(nsize)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'molec cm-2'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.66054E-20;mol m-2'
      dataStr['VAR_VALID_MIN']        = 0.0
      dataStr['VAR_VALID_MAX']        = 1.0E20
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (0.0,1.0E20)
      dataStr['units']                = 'molec cm-2'
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def szaAttrbs(self,nsize):
      ''' Attributes for solar zenith angle'''

      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.getAngleSolarZenithAstronomicalName()
      dataStr['VAR_DESCRIPTION']      = 'Astronomical zenith angle of the sun at the time of the measurement'
      dataStr['VAR_NOTES']            = 'In solar absorption mode, the sun defines the line of sight'
      dataStr['VAR_SIZE']             = str(nsize)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'deg'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.74533E-2;rad'
      dataStr['VAR_VALID_MIN']        = 0.0
      dataStr['VAR_VALID_MAX']        = 90.0
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (0.0,90.0)
      dataStr['units']                = 'deg'
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def saaAttrbs(self,nsize):
      ''' Attributes for solar azimuth angle'''

      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.getAngleSolarAzimuthName()
      dataStr['VAR_DESCRIPTION']      = 'Astronomical azimuth angle of the sun (zero at South neg. to East pos. to West)'
      dataStr['VAR_NOTES']            = 'Due North is defined as 0 degrees. Values increase CLOCKWISE (e.g. Due East is 90 deg)'
      dataStr['VAR_SIZE']             = str(nsize)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'deg'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.74533E-2;rad'
      dataStr['VAR_VALID_MIN']        =  0.0
      dataStr['VAR_VALID_MAX']        =  360.0
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (0.0,360.0)

      dataStr['units']                = 'deg'
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def H2OrprfAttrbs(self,nlyrs,nsize,minval,maxval):
      ''' Attributes for retrieved vertical profile of interfering H2O from solar absorption measurements in VMR units '''

      dataStr = cl.OrderedDict()
      
      dataStr['VAR_NAME']             = self.getH2oMixingRatioAbsorptionSolarName()
      dataStr['VAR_DESCRIPTION']      = 'Final vertical profile of H2O in VMR units'
      dataStr['VAR_NOTES']            = 'Daily averages derived from daily NCEP re-analysis data'
      dataStr['VAR_SIZE']             = str(nsize)+";"+str(nlyrs)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()+';'+self.getAltitudeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = self.mxSclFctName
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.0E{};1'.format(int(math.log10(self.mxSclFctVal)))
      dataStr['VAR_VALID_MIN']        = minval
      dataStr['VAR_VALID_MAX']        = maxval
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()
      dataStr['VALID_RANGE']          = (minval,maxval)
      dataStr['units']                = self.mxSclFctName
      dataStr['_FillValue']           = self.getFillValue()
      
      return dataStr

   def H2OtcAttrbs(self,nsize):
      ''' Attributes for retrieved total column of interfering H2O from solar absorption measurements in VMR units '''

      dataStr = cl.OrderedDict()

      dataStr['VAR_NAME']             = self.getH2oColumnAbsorptionSolarName()
      dataStr['VAR_DESCRIPTION']      = 'Total vertical column of final H2O'
      dataStr['VAR_NOTES']            = 'Daily averages derived from daily NCEP re-analysis data'
      dataStr['VAR_SIZE']             = str(nsize)
      dataStr['VAR_DEPEND']           = self.getDatetimeName()
      dataStr['VAR_DATA_TYPE']        = self.dTypeStr
      dataStr['VAR_UNITS']            = 'molec cm-2'
      dataStr['VAR_SI_CONVERSION']    = '0.0;1.66054E-20;mol m-2'
      dataStr['VAR_VALID_MIN']        = -1.0E24
      dataStr['VAR_VALID_MAX']        = 1.0E25
      dataStr['VAR_FILL_VALUE']       = self.getFillValue()*dataStr['VAR_VALID_MAX']
      dataStr['VALID_RANGE']          = (-1.0E24,1.0E25)
      dataStr['units']                = 'molec cm-2'
      dataStr['_FillValue']           = self.getFillValue()*dataStr['VAR_VALID_MAX']
      
      return dataStr
