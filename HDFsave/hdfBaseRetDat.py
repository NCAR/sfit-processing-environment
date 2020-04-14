#----------------------------------------------------------------------------------------
# Name:
#        HDFbaseRetDat.py
#
# Purpose:
#       Abstract Base Class to build HDF5 file from retrieval data
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
import os, sys
sys.path.append((os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "HDFsave")))
import datetime as dt
import numpy as np
import abc
import hdfCrtFile


class HDFbaseRetDat(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self,gasNameStr):
        self.gasName                      = gasNameStr
        self.gasNameUpper                 = gasNameStr.upper()
        self.mxSclFctName                 = 'ppmv'               # default Max Scale Factor Name 
        self.mxSclFctVal                  = 1E-6                   # default Max Scale Factor Value use in SI Conversion 
        self.mxSclFct2Name                = 'ppmv2'
        self.mxSclFct2Val                 = 1E-12
        self.dates                        = []
        self.latitude                     = 0
        self.longitude                    = 0
        self.instAltitudes                = []
        self.surfPressures                = []  
        self.surfTempuratures             = []
        self.altitudes                    = []      
        self.altitudeBoundaries           = []  
        self.pressures                    = []  
        self.temperatures                 = []
        self.gasMxRatAbsSolar             = []
        self.gasMxRatAbsSolarAprior       = [] 
        self.gasMxRatAbsSolarAVK          = []  
        self.integrationTimes             = []  
        self.gasMxRatAbsSolarUncRand      = []  
        self.gasMxRatAbsSolarUncSys       = []  
        self.gasColPartAbsSolar           = []
        self.gasColPartAbsApriori         = []
        self.gasColAbsSolar               = []  
        self.gasColAbsSolarApriori        = []  
        self.gasColAbsSolarAVK            = []  
        self.gasColAbsSolarUncRand        = []  
        self.gasColAbsSolarUncSys         = []   
        self.angleZastr                   = []
        self.angleSolAz                   = []  
        self.h2oMxRatAbsSolar             = []  
        self.h2oColAbsSol                 = []  
        self.datesJD2K                    = []

    def getFillValue(self):
        return -90000.0

    def getDatetimeName(self):
        return 'DATETIME'

    def getLatitudeInstrumentName(self):
        return 'LATITUDE.INSTRUMENT'

    def getLongitudeInstrumentName(self):
        return 'LONGITUDE.INSTRUMENT'

    def getAltitudeInstrumentName(self):
        return 'ALTITUDE.INSTRUMENT'

    def getSurfacePressureIndependentName(self):
        return 'SURFACE.PRESSURE_INDEPENDENT'

    def getSurfaceTemperatureIndependentName(self):
        return 'SURFACE.TEMPERATURE_INDEPENDENT'

    def getAltitudeName(self):
        return 'ALTITUDE'

    def getAltitudeBoundariesName(self):
        return 'ALTITUDE.BOUNDARIES'

    def getPressureIndependentName(self):
        return 'PRESSURE_INDEPENDENT'

    def getTemperatureIndependentName(self):
        return 'TEMPERATURE_INDEPENDENT'

    def getMixingRatioAbsorptionSolarName(self):
        return 'MIXING.RATIO.VOLUME_ABSORPTION.SOLAR'

    def getMixingRatioAbsorptionSolarAprioriName(self):
        return 'MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_APRIORI'

    def getMixingRatioAbsorptionSolarAvkName(self):
        return 'MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_AVK'

    def getIntegrationTimeName(self):
        return 'INTEGRATION.TIME'

    def getMixingRatioAbsorptionSolarUncertaintyRandomName(self):
        return 'MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.COVARIANCE'

    def getMixingRatioAbsorptionSolarUncertaintySystematicName(self):
        return 'MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_UNCERTAINTY.SYSTEMATIC.COVARIANCE'

    def getColumnPartialAbsorptionSolarName(self):
        return 'COLUMN.PARTIAL_ABSORPTION.SOLAR'

    def getColumnPartialAbsorptionSolarAprioriName(self):
        return 'COLUMN.PARTIAL_ABSORPTION.SOLAR_APRIORI'

    def getColumnAbsorptionSolarName(self):
        return 'COLUMN_ABSORPTION.SOLAR'

    def getColumnAbsorptionSolarAprioriName(self):
        return 'COLUMN_ABSORPTION.SOLAR_APRIORI'

    def getColumnAbsorptionSolarAvkName(self):
        return 'COLUMN_ABSORPTION.SOLAR_AVK'

    def getColumnAbsorptionSolarUncertaintyRandomName(self):
        return 'COLUMN_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD'

    def getColumnAbsorptionSolarUncertaintySystematicName(self):
        return 'COLUMN_ABSORPTION.SOLAR_UNCERTAINTY.SYSTEMATIC.STANDARD'

    def getAngleSolarZenithAstronomicalName(self):
        return 'ANGLE.SOLAR_ZENITH.ASTRONOMICAL'

    def getAngleSolarAzimuthName(self):
        return 'ANGLE.SOLAR_AZIMUTH'

    def getH2oMixingRatioAbsorptionSolarName(self):
        return 'H2O.MIXING.RATIO.VOLUME_ABSORPTION.SOLAR'

    def getH2oColumnAbsorptionSolarName(self):
        return 'H2O.COLUMN_ABSORPTION.SOLAR'

    @abc.abstractmethod
    def glblAttrbs(self,fDOI,idate,fdate):
        ''' Return a dictionary of global attributes for the hdf file, like dataStr = { 'PI_NAME': 'Doe; John' } '''
        pass

    @abc.abstractmethod
    def datetimeAttrbs(self):
        ''' Return a dictionary of datetime attributes for the hdf file, like dataStr = { 'VAR_NAME': self.getDatetimeName() } '''
        pass

    @abc.abstractmethod
    def latAttrbs(self,nsize,datatype):
        ''' Return a dictionary of instrument latitude attributes for the hdf file, like dataStr = { 'VAR_NAME': self.getLatitudeInstrumentName() } '''
        pass

    @abc.abstractmethod
    def lonAttrbs(self,nsize,datatype):
        ''' Return a dictionary of instrument longitude attributes for the hdf file,  like dataStr = { 'VAR_NAME': self.getLongitudeInstrumentName() } '''
        pass

    @abc.abstractmethod
    def instAltAttrbs(self,nsize,datatype):
        ''' Return a dictionary of instrument altitude attributes for the hdf file, like dataStr = { 'VAR_NAME': self.getAltitudeInstrumentName() } '''
        pass

    @abc.abstractmethod
    def surfpAttrbs(self,nsize,datatype):
        ''' Return a dictionary of surface pressure_independent attributes for the hdf file,  like dataStr = { 'VAR_NAME': self.getSurfacePressureIndependentName() } '''
        pass

    @abc.abstractmethod
    def surftAttrbs(self,nsize,datatype):
        ''' Return a dictionary of surface temperature_independent attributes for the hdf file, like dataStr = { 'VAR_NAME': self.getSurfaceTemperatureIndependentName() } '''
        pass

    @abc.abstractmethod
    def AltAttrbs(self,nlyrs,datatype,minval,maxval):
        ''' Return a dictionary of altitude attributes for the hdf file,  like dataStr = { 'VAR_NAME': self.getAltitudeName() } '''
        pass

    @abc.abstractmethod
    def AltBndsAttrbs(self,nlyrs,datatype):
        ''' Return a dictionary of altitude boundaries attributes for the hdf file, like dataStr = { 'VAR_NAME': self.getAltitudeBoundariesName() } '''
        pass

    @abc.abstractmethod
    def pressAttrbs(self,nlyrs,nsize,datatype):
        ''' Return a dictionary of pressure independent attributes for the hdf file,  like dataStr = { 'VAR_NAME': self.getPressureIndependentName() }  '''
        pass

    @abc.abstractmethod
    def tempAttrbs(self,nlyrs,nsize,datatype):
        ''' Return a dictionary of temperature independent attributes for the hdf file,  like dataStr = { 'VAR_NAME': self.getTemperatureIndependentName() } '''
        pass

    @abc.abstractmethod
    def rprfAttrbs(self,nlyrs,nsize,datatype,units,sclfctr,maxval):
        ''' Return a dictionary of gasname mixing ratio absorption solar attributes for the hdf file,  like dataStr = { 'VAR_NAME': 'gasName.upper()+'.'+self.getMixingRatioAbsorptionSolarName() } '''
        pass

    @abc.abstractmethod
    def aprfAttrbs(self,nlyrs,nsize,datatype,units,sclfctr,maxval):
        ''' Return a dictionary of gasname mixing ratio absorption solar apriori attributes for the hdf file,  like dataStr = { 'VAR_NAME': 'gasName.upper()+'.'+self.getMixingRatioAbsorptionSolarAprioriName() } '''
        pass

    @abc.abstractmethod
    def avkAttrbs(self,nlyrs,nsize,datatype,units,sclfctr):
        ''' Return a dictionary of gasname mixing ratio absorption solar avk attributes for the hdf file,  like dataStr = { 'VAR_NAME': 'gasName.upper()+'.'+self.getMixingRatioAbsorptionSolarAvkName() }  '''
        pass

    @abc.abstractmethod
    def intTAttrbs(self,nsize,datatype):
        ''' Return a dictionary of inteeration time attributes for the hdf file,  like dataStr = { 'VAR_NAME': self.etIntegrationTimeName() } '''
        pass

    @abc.abstractmethod
    def mRandAttrbs(self,nlyrs,nsize,datatype):
        ''' Return a dictionary of total random error covariance attributes for the hdf file,  like dataStr = { 'VAR_NAME': gasName.upper()+'.'+self.getMixingRatioAbsorptionSolarUncertaintyRandomName() }  '''
        pass

    @abc.abstractmethod
    def mSysAttrbs(self,nlyrs,nsize,datatype):
        ''' Return a dictionary of total systematic error covariance attributes for the hdf file,  like dataStr = { 'VAR_NAME': gasName.upper()+'.'+self.getMixingRatioAbsorptionSolarUncertaintySystematicName() }  '''
        pass

    @abc.abstractmethod
    def pcRtrprfAttrbs(self,nlyrs,nsize,datatype):
        ''' Return a dictionary of retrieved partial column attributes for the hdf file,  like dataStr = { 'VAR_NAME': gasName.upper()+'.'+self.getColumnPartialAbsorptionSolarName() }  '''
        pass

    @abc.abstractmethod
    def pcaAprfAttrbs(self,nlyrs,nsize,datatype):
        ''' Return a dictionary of a priori partial column attributes for the hdf file,  like dataStr = { 'VAR_NAME': gasName.upper()+'.'+self.getColumnPartialAbsorptionSolarAprioriName() } '''
        pass

    @abc.abstractmethod
    def tcRprfAttrbs(self,nsize,datatype):
        ''' Return a dictionary of total column from retrieved profile attributes for the hdf file,  like dataStr = { 'VAR_NAME': gasName.upper()+'.'+self.getColumnAbsorptionSolarName() } '''
        pass

    @abc.abstractmethod
    def tcAprfAttrbs(self,nsize,datatype):
        ''' Return a dictionary of total column from a priori profile attributes for the hdf file,  like dataStr = { 'VAR_NAME': gasName.upper()+'.'+self.getColumnAbsoprtionSolarAprioriName() }  '''
        pass

    @abc.abstractmethod
    def tcAvkAttrbs(self,nlyrs,nsize,datatype):
        ''' Return a dictionary of total column from averaging kernel attributes for the hdf file,  like dataStr = { 'VAR_NAME': gasName.upper()+'.'+self.getColumnAbsorptionSolarAvkName() }  '''
        pass

    @abc.abstractmethod
    def tcRandAttrbs(self,nsize,datatype):
        ''' Return a dictionary of total column random uncertainty attributes for the hdf file,  like dataStr = { 'VAR_NAME': gasName.upper()+'.'+self.getColumnAbsorptionSolarUncertaintyRandomName() }  '''
        pass

    @abc.abstractmethod
    def tcSysAttrbs(self,nsize,datatype):
        ''' Return a dictionary of total column systematic uncertainty attributes for the hdf file,  like dataStr = { 'VAR_NAME': gasName.upper()+'.'+self.getColumnAbsorptionSolarUncertaintySystematicName() }  '''
        pass

    @abc.abstractmethod
    def szaAttrbs(self,nsize,datatype):
        ''' Return a dictionary of solar zenith angle attributes for the hdf file,  like dataStr = { 'VAR_NAME': self.getAngleSolarZenith.AstronomicalName() }  '''
        pass

    @abc.abstractmethod
    def saaAttrbs(self,nsize,datatype):
        ''' Return a dictionary of angle solar azimuth attributes for the hdf file,  like dataStr = { 'VAR_NAME': self.getAngleSolarAzimuthName() }  '''
        pass

    @abc.abstractmethod
    def H2OrprfAttrbs(self,nlyrs,nsize,datatype,units,sclfctr,minval,maxval):
        ''' Return a dictionary of H2O mixing ratio attributes for the hdf file,  like dataStr = { 'VAR_NAME': self.getH2oMixingRatioAbsorptionSolarName() }  '''
        pass

    @abc.abstractmethod
    def H2OtcAttrbs(self,nsize,datatype):
        ''' Return a dictionary of H2O mixing ratio solar absorption attributes for the hdf file,  like dataStr = { 'VAR_NAME': self.getH2oColumnAbsorptionSolarNAme() }  '''
        pass

    def createHDF(self,hdfFile):
        ''' create an HDF file specified in global attribute FILE_NAME in the directory specified in the outDir attribute'''

        #--------------------------
        # Open hdf file for writing
        #--------------------------
        idate          = np.min(self.dates)
        fdate          = np.max(self.dates)
        fDOI           = dt.datetime.now()
        hdfHdr         = self.glblAttrbs(fDOI,idate,fdate)
        hdfFname       = hdfHdr['FILE_NAME']

        #-----------------------------------
        # Create HDF file
        #-----------------------------------
        hdfFile.createFile(self.outDir+hdfFname.lower(),hdfHdr)

        #------------------------------------
        # Create Datetime dataset (variable)
        # Should always be a float64 (double)
        #------------------------------------
        hdfFile.createDataSet(self.getDatetimeName(),np.size(self.datesJD2K),self.datesJD2K, \
                                self.datetimeAttrbs(np.size(self.datesJD2K)),typeOvrd='float64')

        #-----------------------------------
        # Create Latitude dataset (variable)
        #-----------------------------------
        hdfFile.createDataSet(self.getLatitudeInstrumentName(),np.size(self.latitude),self.latitude, \
                                self.latAttrbs(np.size(self.latitude)))

        #-----------------------------------
        # Create Longitude dataset (variable)
        #-----------------------------------
        hdfFile.createDataSet(self.getLongitudeInstrumentName(),np.size(self.longitude),self.longitude, \
                                self.lonAttrbs(np.size(self.longitude)))

        #----------------------------------------------
        # Create Instrument Altitude dataset (variable)
        #----------------------------------------------
        hdfFile.createDataSet(self.getAltitudeInstrumentName(),np.size(self.instAltitudes),self.instAltitudes, \
                                self.instAltAttrbs(np.size(self.instAltitudes)))

        #-------------------------------------------
        # Create surface pressure dataset (variable)
        #-------------------------------------------
        hdfFile.createDataSet(self.getSurfacePressureIndependentName(),np.size(self.surfPressures),self.surfPressures, \
                                self.surfpAttrbs(np.size(self.surfPressures)))

        #----------------------------------------------
        # Create surface temperature dataset (variable)
        #----------------------------------------------
        hdfFile.createDataSet(self.getSurfaceTemperatureIndependentName(),np.size(self.surfTemperatures),self.surfTemperatures, \
                                self.surftAttrbs(np.size(self.surfTemperatures)))

        #-----------------------------------
        # Create Altitude dataset (variable)
        #-----------------------------------
        hdfFile.createDataSet(self.getAltitudeName(),np.size(self.altitudes),self.altitudes, \
                                self.AltAttrbs(np.size(self.altitudes), float(self.altitudes.min()), float(self.altitudes.max())))

        #----------------------------------------------
        # Create Altitude Boundaries dataset (variable)
        #----------------------------------------------
        hdfFile.createDataSet(self.getAltitudeBoundariesName(), \
                                (self.altitudeBoundaries.shape[0],self.altitudeBoundaries.shape[1]),self.altitudeBoundaries, \
                                self.AltBndsAttrbs(self.altitudeBoundaries.shape[1]))

        #----------------------------------------------
        # Create pressure Boundaries dataset (variable)
        #----------------------------------------------
        hdfFile.createDataSet(self.getPressureIndependentName(),(self.pressures.shape[0],self.pressures.shape[1]), \
                                self.pressures, \
                                self.pressAttrbs(self.pressures.shape[1],self.pressures.shape[0]))

        #-------------------------------------------------
        # Create temperature Boundaries dataset (variable)
        #-------------------------------------------------
        hdfFile.createDataSet(self.getTemperatureIndependentName(), \
                                (self.temperatures.shape[0],self.temperatures.shape[1]),self.temperatures, \
                                self.tempAttrbs(self.temperatures.shape[1],self.temperatures.shape[0],float(self.temperatures.max())))

        #-------------------------------------------------------------
        # Create gasname retrieved vertical profile dataset (variable)
        #-------------------------------------------------------------
        hdfFile.createDataSet(self.gasNameUpper+"."+self.getMixingRatioAbsorptionSolarName(), \
                                (self.gasMxRatAbsSolar.shape[0],self.gasMxRatAbsSolar.shape[1]),self.gasMxRatAbsSolar, \
                                self.rprfAttrbs(self.gasMxRatAbsSolar.shape[1],self.gasMxRatAbsSolar.shape[0], \
                                                float(self.gasMxRatAbsSolar.max())))

        #------------------------------------------------------------
        # Create gasname a priori vertical profile dataset (variable)
        #------------------------------------------------------------
        hdfFile.createDataSet(self.gasNameUpper+"."+self.getMixingRatioAbsorptionSolarAprioriName(), \
                                (self.gasMxRatAbsSolarApriori.shape[0],self.gasMxRatAbsSolarApriori.shape[1]),self.gasMxRatAbsSolarApriori, \
                                self.aprfAttrbs(self.gasMxRatAbsSolarApriori.shape[1],self.gasMxRatAbsSolarApriori.shape[0], 
                                                float(self.gasMxRatAbsSolarApriori.max())))

        #--------------------------------------------------------------------------------------
        # Create gasname averaging Kernel maxtrix retrieved vertical profile dataset (variable)
        #--------------------------------------------------------------------------------------
        hdfFile.createDataSet(self.gasNameUpper+"."+self.getMixingRatioAbsorptionSolarAvkName(), \
                                (self.gasMxRatAbsSolarAVK.shape[0],self.gasMxRatAbsSolarAVK.shape[1],self.gasMxRatAbsSolarAVK.shape[2]),  \
                                self.gasMxRatAbsSolarAVK, \
                                self.avkAttrbs(self.gasMxRatAbsSolarAVK.shape[1],self.gasMxRatAbsSolarAVK.shape[0]))

        #----------------------------------------------
        # Create Interation time dataset (variable)
        #----------------------------------------------
        hdfFile.createDataSet(self.getIntegrationTimeName(),np.size(self.integrationTimes),self.integrationTimes, \
                                self.intTAttrbs(np.size(self.integrationTimes)))

        #-------------------------------------------------------------------------------
        # Create gasname total random error covariance matrix profile dataset (variable) nlyrs,nsize,datatype,units,sclfctr,maxval
        #-------------------------------------------------------------------------------
        hdfFile.createDataSet(self.gasNameUpper+"."+self.getMixingRatioAbsorptionSolarUncertaintyRandomName(), \
                                (self.gasMxRatAbsSolarUncRand.shape[0],self.gasMxRatAbsSolarUncRand.shape[1],self.gasMxRatAbsSolarUncRand.shape[2]), \
                                self.gasMxRatAbsSolarUncRand, self.mRandAttrbs(self.gasMxRatAbsSolarUncRand.shape[1],self.gasMxRatAbsSolarUncRand.shape[0]))




        #-----------------------------------------------------------------------------
        # Create gasname systematic error covariance matrix profile dataset (variable)
        #-----------------------------------------------------------------------------
        hdfFile.createDataSet(self.gasNameUpper+"."+self.getMixingRatioAbsorptionSolarUncertaintySystematicName(), \
                                (self.gasMxRatAbsSolarUncSys.shape[0],self.gasMxRatAbsSolarUncSys.shape[1],self.gasMxRatAbsSolarUncSys.shape[2]), \
                                self.gasMxRatAbsSolarUncSys, self.mSysAttrbs(self.gasMxRatAbsSolarUncSys.shape[1],self.gasMxRatAbsSolarUncSys.shape[0]))


        #-----------------------------------------------------------------------------
        # Create gasname retrieved partial column profile dataset (variable)
        #-----------------------------------------------------------------------------
        hdfFile.createDataSet(self.gasNameUpper+'.'+self.getColumnPartialAbsorptionSolarName(), \
                                (self.gasColPartAbsSolar.shape[0],self.gasColPartAbsSolar.shape[1]), self.gasColPartAbsSolar, \
                                self.pcRtrprfAttrbs(self.gasColPartAbsSolar.shape[1],self.gasColPartAbsSolar.shape[0]))

        #-----------------------------------------------------------------------------
        # Create gasname a priori partial column profile dataset (variable)
        #-----------------------------------------------------------------------------
        hdfFile.createDataSet(self.gasNameUpper+'.'+self.getColumnPartialAbsorptionSolarAprioriName(), 
                                (self.gasColPartAbsApriori.shape[0],self.gasColPartAbsApriori.shape[1]), self.gasColPartAbsApriori, \
                                self.pcaAprfAttrbs(self.gasColPartAbsApriori.shape[1],self.gasColPartAbsApriori.shape[0]))

        #-----------------------------------------------------------------------------
        # Create gasname total column profile dataset (variable)
        #-----------------------------------------------------------------------------
        hdfFile.createDataSet(self.gasNameUpper+"."+self.getColumnAbsorptionSolarName(),np.size(self.gasColAbsSolar), \
                                self.gasColAbsSolar, self.tcRprfAttrbs(np.size(self.gasColAbsSolar)))

        #-----------------------------------------------------------------------------
        # Create gasname apriori total column profile dataset (variable)
        #-----------------------------------------------------------------------------
        hdfFile.createDataSet(self.gasNameUpper+'.'+self.getColumnAbsorptionSolarAprioriName(), \
                                np.size(self.gasColAbsSolarApriori), self.gasColAbsSolarApriori, 
                                self.tcAprfAttrbs(np.size(self.gasColAbsSolarApriori)))



        #-----------------------------------------------------------------------------
        # Create gasname total column averaging kernel profile dataset (variable)
        #-----------------------------------------------------------------------------
        hdfFile.createDataSet(self.gasNameUpper+'.'+self.getColumnAbsorptionSolarAvkName(), 
                                (self.gasColAbsSolarAVK.shape[0],self.gasColAbsSolarAVK.shape[1]), self.gasColAbsSolarAVK, \
                                self.tcAvkAttrbs(self.gasColAbsSolarAVK.shape[1],self.gasColAbsSolarAVK.shape[0]))

        #-----------------------------------------------------------------------------
        # Create gasname total column random uncertainty dataset (variable)
        #-----------------------------------------------------------------------------
        hdfFile.createDataSet(self.gasNameUpper+'.'+self.getColumnAbsorptionSolarUncertaintyRandomName(), \
                                np.size(self.gasColAbsSolarUncRand), self.gasColAbsSolarUncRand, \
                                self.tcRandAttrbs(np.size(self.gasColAbsSolarUncRand)))

        #-----------------------------------------------------------------------------
        # Create gasname total column systematic uncertainty dataset (variable)
        #-----------------------------------------------------------------------------
        hdfFile.createDataSet(self.gasNameUpper+'.'+self.getColumnAbsorptionSolarUncertaintySystematicName(), \
                                np.size(self.gasColAbsSolarUncSys),  self.gasColAbsSolarUncSys, \
                                self.tcSysAttrbs(np.size(self.gasColAbsSolarUncSys)))

        #-----------------------------------------------------------------------------
        # Create solar zenith angle dataset (variable)
        #-----------------------------------------------------------------------------
        hdfFile.createDataSet(self.getAngleSolarZenithAstronomicalName(),np.size(self.angleZastr), self.angleZastr, \
                                self.szaAttrbs(np.size(self.angleZastr)))

        #-----------------------------------------------------------------------------
        # Create solar azimuth angle dataset (variable)
        #-----------------------------------------------------------------------------
        hdfFile.createDataSet(self.getAngleSolarAzimuthName(),np.size(self.angleSolAz),self.angleSolAz, \
                                self.saaAttrbs(np.size(self.angleSolAz)))

        if self.gasNameUpper != 'H2O':

            #-----------------------------------------------------------------------------
            # Create interfering H2O from solar absorption profile dataset (variable)
            #-----------------------------------------------------------------------------
            hdfFile.createDataSet(self.getH2oMixingRatioAbsorptionSolarName(), \
                                    (self.h2oMxRatAbsSolar.shape[0],self.h2oMxRatAbsSolar.shape[1]), self.h2oMxRatAbsSolar, \
                                    self.H2OrprfAttrbs(self.h2oMxRatAbsSolar.shape[1],self.h2oMxRatAbsSolar.shape[0], \
                                                       float(self.h2oMxRatAbsSolar.min()), \
                                                       float(self.h2oMxRatAbsSolar.max())))

            #-----------------------------------------------------------------------------
            # Create total column of interfering H2O solar absorption dataset (variable)
            #-----------------------------------------------------------------------------
            hdfFile.createDataSet(self.getH2oColumnAbsorptionSolarName(),np.size(self.h2oColAbsSol), self.h2oColAbsSol, \
                                    self.H2OtcAttrbs(np.size(self.h2oColAbsSol)))


        
        #---------------
        # Close HDF file
        #---------------
        hdfFile.closeFile


    def createHDF4(self):
        ''' create an HDF 4 file in outDdir specified from the pltOutputClass outputDatat passed in'''
                
        #----------------
        # Create instance
        #----------------        
        hdfFile = hdfCrtFile.HDF4File(self.dType)

        #--------------------------------------
        # Open hdf file, write data, close file
        #--------------------------------------        
        self.createHDF(hdfFile)
        

    def createHDF5(self):
        ''' create an HDF 5 file in outDdir specified from the pltOutputClass outputDatat passed in'''
                 
        #----------------
        # Create instance
        #----------------            
        hdfFile = hdfCrtFile.HDF5File(self.dType)
        
        #--------------------------------------
        # Open hdf file, write data, close file
        #--------------------------------------                
        self.createHDF(hdfFile)