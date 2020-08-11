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
        self.mxSclFctZVal                 = 1E-21
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

        self.nullascii                    = b'\x00'.decode('ascii')

    def getFillValue(self):
        return -90000.0

    def getDatetimeName(self):
        return 'DATETIME'

    def getLatitudeInstrumentName(self):
        return 'LATITUDE.INSTRUMENT'

    def getLatitudeLOSName(self):
        return 'LATITUDE_LOS'

    def getLongitudeLOSName(self):
        return 'LONGITUDE_LOS'

    def getLongitudeInstrumentName(self):
        return 'LONGITUDE.INSTRUMENT'

    def getAltitudeInstrumentName(self):
        return 'ALTITUDE.INSTRUMENT'

    def getSurfacePressureIndependentName(self):
        return 'SURFACE.PRESSURE_INDEPENDENT'

    def getSurfacePressureIndependentSourceName(self):
        return 'SURFACE.PRESSURE_INDEPENDENT_SOURCE'

    def getSurfaceTemperatureIndependentName(self):
        return 'SURFACE.TEMPERATURE_INDEPENDENT'

    def getSurfaceTemperatureIndependentSourceName(self):
        return 'SURFACE.TEMPERATURE_INDEPENDENT_SOURCE'

    def getAltitudeName(self):
        return 'ALTITUDE'

    def getAltitudeBoundariesName(self):
        return 'ALTITUDE.BOUNDARIES'

    def getPressureIndependentName(self):
        return 'PRESSURE_INDEPENDENT'

    def getPressureIndependentSourceName(self):
        return 'PRESSURE_INDEPENDENT_SOURCE'

    def getTemperatureIndependentName(self):
        return 'TEMPERATURE_INDEPENDENT'

    def getTemperatureIndependentSourceName(self):
        return 'TEMPERATURE_INDEPENDENT_SOURCE'

    def getMixingRatioAbsorptionSolarDryName(self):
        return 'MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR'

    def getMixingRatioAbsorptionSolarName(self):
        return 'MIXING.RATIO.VOLUME_ABSORPTION.SOLAR'

    def getMixingRatioAbsorptionSolarAprioriName(self):
        return 'MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_APRIORI'

    def getMixingRatioAprioriDryName(self):
        return 'MIXING.RATIO.VOLUME.DRY_APRIORI'

    def getMixingRatioAprioriDrySourceName(self):
        return 'MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE'


    def getMixingRatioAbsorptionSolarAvkName(self):
        return 'MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_AVK'

    def getMixingRatioAbsorptionSolarAvkDryName(self):
        return 'MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_AVK'

    def getIntegrationTimeName(self):
        return 'INTEGRATION.TIME'

    def getMixingRatioAbsorptionSolarUncertaintyRandomName(self):
        return 'MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.COVARIANCE'

    def getMixingRatioAbsorptionSolarUncertaintyRandomDryName(self):
        return 'MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.COVARIANCE'

    def getMixingRatioAbsorptionSolarUncertaintySystematicName(self):
        return 'MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_UNCERTAINTY.SYSTEMATIC.COVARIANCE'

    def getMixingRatioAbsorptionSolarUncertaintySystematicDryName(self):
        return 'MIXING.RATIO.VOLUME.DRY_ABSORPTION.SOLAR_UNCERTAINTY.SYSTEMATIC.COVARIANCE'

    def getColumnPartialAbsorptionSolarName(self):
        return 'COLUMN.PARTIAL_ABSORPTION.SOLAR'

    def getColumnPartialAbsorptionSolarAprioriName(self):
        return 'COLUMN.PARTIAL_ABSORPTION.SOLAR_APRIORI'

    def getColumnPartialAprioriName(self):
        return 'COLUMN.PARTIAL_APRIORI'

    def getColumnAbsorptionSolarName(self):
        return 'COLUMN_ABSORPTION.SOLAR'

    def getColumnAbsorptionSolarAprioriName(self):
        return 'COLUMN_ABSORPTION.SOLAR_APRIORI'

    def getColumnAprioriName(self):
        return 'COLUMN_APRIORI'

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

    def getH2oColumnAprioriName(self):
        return 'H2O.COLUMN_APRIORI'

    def getDryAirColumnPartialName(self):
        return 'DRY.AIR.COLUMN.PARTIAL_INDEPENDENT'

    def getDryAirColumnPartialSourceName(self):
        return 'DRY.AIR.COLUMN.PARTIAL_INDEPENDENT_SOURCE'

    def getH2oMixingRatioVolumeDryAprioriName(self):
        return 'H2O.MIXING.RATIO.VOLUME.DRY_APRIORI'

    def getH2oMixingRatioVolumeDryAprioriSourceName(self):
        return 'H2O.MIXING.RATIO.VOLUME.DRY_APRIORI.SOURCE'

    def getHumidityName(self):
        return 'HUMIDITY.RELATIVE.SURFACE_INDEPENDENT'

    def getHumiditySourceName(self):
        return 'HUMIDITY.RELATIVE.SURFACE_INDEPENDENT_SOURCE'

    def getwinddirectionName(self):
        return 'WIND.DIRECTION.SURFACE_INDEPENDENT'

    def getwinddirectionSourceName(self):
        return 'WIND.DIRECTION.SURFACE_INDEPENDENT_SOURCE'

    def getwindspeedName(self):
        return 'WIND.SPEED.SURFACE_INDEPENDENT'

    def getwindspeedSourceName(self):
        return 'WIND.SPEED.SURFACE_INDEPENDENT_SOURCE'

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

    @abc.abstractmethod
    def DryAirAttrbs(self,nsize,datatype):
        ''' Return a dictionary of Dry air for the hdf file,  like dataStr = { 'VAR_NAME': self.getH2oColumnAprioriName() }  '''
        pass

    def createHDF(self,hdfFile, geomsTmpl=False):
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

        #-----------------------------------
        # Create Altitude dataset (variable)
        #-----------------------------------
        hdfFile.createDataSet(self.getAltitudeName(),np.size(self.altitudes),self.altitudes, \
                                self.AltAttrbs(np.size(self.altitudes), float(self.altitudes.min()), float(self.altitudes.max())))

        #----------------------------------------------
        # Create Altitude Boundaries dataset (variable)
        #----------------------------------------------
        if int(geomsTmpl) >= int(3): 
            hdfFile.createDataSet(self.getAltitudeBoundariesName(), \
                                   (self.altitudeBoundaries.shape[0],self.altitudeBoundaries.shape[1]),self.altitudeBoundaries, \
                                   self.AltBnds2Attrbs(self.altitudeBoundaries.shape[0]))
        else:
            hdfFile.createDataSet(self.getAltitudeBoundariesName(), \
                                    (self.altitudeBoundaries.shape[0],self.altitudeBoundaries.shape[1]),self.altitudeBoundaries, \
                                    self.AltBndsAttrbs(self.altitudeBoundaries.shape[1]))

        #----------------------------------------------
        # Create Instrument Altitude dataset (variable)
        #----------------------------------------------
        if int(geomsTmpl) >= int(3):
            hdfFile.createDataSet(self.getAltitudeInstrumentName(),np.size(self.instAltitudes),self.instAltitudes, \
                                    self.instAlt2Attrbs(np.size(self.instAltitudes)))
        else:
            hdfFile.createDataSet(self.getAltitudeInstrumentName(),np.size(self.instAltitudes),self.instAltitudes, \
                                    self.instAltAttrbs(np.size(self.instAltitudes)))


        #-----------------------------------------------------------------------------
        # Create solar azimuth angle dataset (variable)
        #-----------------------------------------------------------------------------
        hdfFile.createDataSet(self.getAngleSolarAzimuthName(),np.size(self.angleSolAz),self.angleSolAz, \
                                self.saaAttrbs(np.size(self.angleSolAz)))


        #-----------------------------------------------------------------------------
        # Create solar zenith angle dataset (variable)
        #-----------------------------------------------------------------------------
        hdfFile.createDataSet(self.getAngleSolarZenithAstronomicalName(),np.size(self.angleZastr), self.angleZastr, \
                                self.szaAttrbs(np.size(self.angleZastr)))

        #------------------------------------
        # Create Datetime dataset (variable)
        # Should always be a float64 (double)
        #------------------------------------
        hdfFile.createDataSet(self.getDatetimeName(),np.size(self.datesJD2K),self.datesJD2K, \
                                self.datetimeAttrbs(np.size(self.datesJD2K)),typeOvrd='float64')

        #-----------------------------------------------------------------------------
        # Create Dry Air column independent
        #-----------------------------------------------------------------------------
        if int(geomsTmpl) >= int(3):

            hdfFile.createDataSet(self.getDryAirColumnPartialName(),(self.airMass.shape[0],self.airMass.shape[1]), \
                                    self.airMass, \
                                    self.DryAirAttrbs(self.airMass.shape[1],self.airMass.shape[0], \
                                                       float(self.airMass.min()), \
                                                       float(self.airMass.max())))



            datatowrite=str('\x10Test')
            varvalidmin=varvalidmax=unit=siconversion=fill=self.nullascii
            hdfFile.createDataSet(self.getDryAirColumnPartialSourceName(),(10), \
                                    datatowrite, \
                                    self.DryAirSourceAttrbs(varvalidmin, varvalidmax, unit,siconversion, fill), typeOvrd='string' )




        if self.gasNameUpper != 'H2O':

            #-----------------------------------------------------------------------------
            # H2O Column apriori - Total vertical column of H2O adopted in the target gas retrieval
            #-----------------------------------------------------------------------------

            if int(geomsTmpl) >= int(3):

                hdfFile.createDataSet(self.getH2oColumnAprioriName(),np.size(self.h2oColApr), self.h2oColApr, \
                                        self.H2OtcAprAttrbs(np.size(self.h2oColApr), \
                                                           float(self.h2oMxRatAbsSolar.min()), \
                                                           float(self.h2oMxRatAbsSolar.max())))
            else:
                #-----------------------------------------------------------------------------
                # Create total column of interfering H2O solar absorption dataset (variable)
                #-----------------------------------------------------------------------------
                hdfFile.createDataSet(self.getH2oColumnAbsorptionSolarName(),np.size(self.h2oColAbsSol), self.h2oColAbsSol, \
                                        self.H2OtcAttrbs(np.size(self.h2oColAbsSol)))



            #-----------------------------------------------------------------------------
            # Create interfering H2O from solar absorption profile dataset (variable)
            #-----------------------------------------------------------------------------
            if int(geomsTmpl) >= int(3):

                hdfFile.createDataSet(self.getH2oMixingRatioVolumeDryAprioriName(), \
                                        (self.h2oMxRatAbsSolar.shape[0],self.h2oMxRatAbsSolar.shape[1]), self.h2oMxRatAbsSolar, \
                                        self.H2OVolDryAprAttrbs(self.h2oMxRatAbsSolar.shape[1],self.h2oMxRatAbsSolar.shape[0], \
                                                           float(self.h2oMxRatAbsSolar.min()), \
                                                           float(self.h2oMxRatAbsSolar.max())))

                datatowrite=str('\x10Test')
                varvalidmin=varvalidmax=unit=siconversion=fill=self.nullascii
                hdfFile.createDataSet(self.getH2oMixingRatioVolumeDryAprioriSourceName(),(10), \
                                        datatowrite, \
                                        self.H2OVolDryAprSourceAttrbs(varvalidmin, varvalidmax, unit,siconversion, fill), typeOvrd='string' )

            else:
                hdfFile.createDataSet(self.getH2oMixingRatioAbsorptionSolarName(), \
                                        (self.h2oMxRatAbsSolar.shape[0],self.h2oMxRatAbsSolar.shape[1]), self.h2oMxRatAbsSolar, \
                                        self.H2OrprfAttrbs(self.h2oMxRatAbsSolar.shape[1],self.h2oMxRatAbsSolar.shape[0], \
                                                           float(self.h2oMxRatAbsSolar.min()), \
                                                           float(self.h2oMxRatAbsSolar.max())))

        #-----------------------------------------------------------------------------
        # Create Humidity - Relative humidity at the station
        #-----------------------------------------------------------------------------
        if int(geomsTmpl) >= int(3):

            hdfFile.createDataSet(self.getHumidityName(),np.size(self.rh), self.rh, \
                                self.humidityAttrbs(np.size(self.rh)))

            datatowrite=str('\x10Test')
            varvalidmin=varvalidmax=unit=siconversion=fill=self.nullascii
            hdfFile.createDataSet(self.getHumiditySourceName(),(10), \
                                    datatowrite, \
                                    self.humiditySourceAttrbs(varvalidmin, varvalidmax, unit,siconversion, fill), typeOvrd='string' )

        
        #----------------------------------------------
        # Create Integration time dataset (variable)
        #----------------------------------------------
        hdfFile.createDataSet(self.getIntegrationTimeName(),np.size(self.integrationTimes),self.integrationTimes, \
                                self.intTAttrbs(np.size(self.integrationTimes)))


        #-----------------------------------
        # Create Latitude dataset (variable)
        #-----------------------------------
        hdfFile.createDataSet(self.getLatitudeInstrumentName(),np.size(self.latitude),self.latitude, \
                                self.latAttrbs(np.size(self.latitude)))


        
        #----------------------------------------------
        # Create Create Latitude LOS dataset (variable)
        #----------------------------------------------
        if int(geomsTmpl) >= int(3):
            hdfFile.createDataSet(self.getLatitudeLOSName(),(self.latLOS.shape[0],self.latLOS.shape[1]), \
                                    self.latLOS, \
                                    self.latLOSAttrbs(self.latLOS.shape[1],self.latLOS.shape[0]))


        #-----------------------------------
        # Create Longitude dataset (variable)
        #-----------------------------------
        hdfFile.createDataSet(self.getLongitudeInstrumentName(),np.size(self.longitude),self.longitude, \
                                self.lonAttrbs(np.size(self.longitude)))


        #----------------------------------------------
        # Create Create Longitude LOS dataset (variable)
        #----------------------------------------------
        if int(geomsTmpl) >= int(3):
            hdfFile.createDataSet(self.getLongitudeLOSName(),(self.lonLOS.shape[0],self.lonLOS.shape[1]), \
                                    self.lonLOS, \
                                    self.lonLOSAttrbs(self.lonLOS.shape[1],self.lonLOS.shape[0]))


        #----------------------------------------------
        # Create pressure Boundaries dataset (variable)
        #----------------------------------------------
        hdfFile.createDataSet(self.getPressureIndependentName(),(self.pressures.shape[0],self.pressures.shape[1]), \
                                self.pressures, \
                                self.pressAttrbs(self.pressures.shape[1],self.pressures.shape[0]))
        
        if int(geomsTmpl) >= int(3):
            datatowrite=str('\x10Test')
            varvalidmin=varvalidmax=unit=siconversion=fill=self.nullascii
            hdfFile.createDataSet(self.getPressureIndependentSourceName(),(10), \
                                    datatowrite, \
                                    self.pressSourceAttrbs(varvalidmin, varvalidmax, unit,siconversion, fill), typeOvrd='string' )


        #-------------------------------------------
        # Create surface pressure dataset (variable)
        #-------------------------------------------
        hdfFile.createDataSet(self.getSurfacePressureIndependentName(),np.size(self.surfPressures),self.surfPressures, \
                                self.surfpAttrbs(np.size(self.surfPressures)))

        if int(geomsTmpl) >= int(3):
            datatowrite=str('\x10Test')
            varvalidmin=varvalidmax=unit=siconversion=fill=self.nullascii
            hdfFile.createDataSet(self.getSurfacePressureIndependentSourceName(),(10), \
                                    datatowrite, \
                                    self.surfpSourceAttrbs(varvalidmin, varvalidmax, unit,siconversion, fill), typeOvrd='string' )

        #----------------------------------------------
        # Create surface temperature dataset (variable)
        #----------------------------------------------
        hdfFile.createDataSet(self.getSurfaceTemperatureIndependentName(),np.size(self.surfTemperatures),self.surfTemperatures, \
                                self.surftAttrbs(np.size(self.surfTemperatures)))

        if int(geomsTmpl) >= int(3):
            datatowrite=str('\x10Test')
            varvalidmin=varvalidmax=unit=siconversion=fill=self.nullascii
            hdfFile.createDataSet(self.getSurfaceTemperatureIndependentSourceName(),(10), \
                                    datatowrite, \
                                    self.surftSourceAttrbs(varvalidmin, varvalidmax, unit,siconversion, fill), typeOvrd='string' )

        
        #-------------------------------------------------
        # Create temperature Boundaries dataset (variable)
        #-------------------------------------------------
        hdfFile.createDataSet(self.getTemperatureIndependentName(), \
                                (self.temperatures.shape[0],self.temperatures.shape[1]),self.temperatures, \
                                self.tempAttrbs(self.temperatures.shape[1],self.temperatures.shape[0],float(self.temperatures.max())))

        if int(geomsTmpl) >= int(3):
            datatowrite=str('\x10Test')
            varvalidmin=varvalidmax=unit=siconversion=fill=self.nullascii
            hdfFile.createDataSet(self.getTemperatureIndependentSourceName(),(10), \
                                    datatowrite, \
                                    self.tempSourceAttrbs(varvalidmin, varvalidmax, unit,siconversion, fill), typeOvrd='string' )



        #-------------------------------------------
        # Create wind direction/speed dataset (variable)
        #-------------------------------------------
        if int(geomsTmpl) >= int(3):
            hdfFile.createDataSet(self.getwinddirectionName(),np.size(self.wd),self.wd, \
                                    self.winddirectionAttrbs(np.size(self.wd)))

            datatowrite=str('\x10Test')
            varvalidmin=varvalidmax=unit=siconversion=fill=self.nullascii
            hdfFile.createDataSet(self.getwinddirectionSourceName(),(10), \
                                    datatowrite, \
                                    self.winddirectionSourceAttrbs(varvalidmin, varvalidmax, unit,siconversion, fill), typeOvrd='string' )



            hdfFile.createDataSet(self.getwindspeedName(),np.size(self.ws),self.ws, \
                                    self.windspeedAttrbs(np.size(self.ws)))

            datatowrite=str('\x10Test')
            varvalidmin=varvalidmax=unit=siconversion=fill=self.nullascii
            hdfFile.createDataSet(self.getwindspeedSourceName(),(10), \
                                    datatowrite, \
                                    self.windspeedSourceAttrbs(varvalidmin, varvalidmax, unit,siconversion, fill), typeOvrd='string' )




        #-------------------------------------------------------------
        # Create gasname retrieved vertical profile dataset (variable)
        #-------------------------------------------------------------
        if int(geomsTmpl) >= int(3): 
            hdfFile.createDataSet(self.gasNameUpper+"."+self.getMixingRatioAbsorptionSolarDryName(), \
                                        (self.gasMxRatAbsSolar.shape[0],self.gasMxRatAbsSolar.shape[1]),self.gasMxRatAbsSolar, \
                                        self.rprfDryAttrbs(self.gasMxRatAbsSolar.shape[1],self.gasMxRatAbsSolar.shape[0], \
                                                        float(self.gasMxRatAbsSolar.max())))

        else:                         
            hdfFile.createDataSet(self.gasNameUpper+"."+self.getMixingRatioAbsorptionSolarName(), \
                                        (self.gasMxRatAbsSolar.shape[0],self.gasMxRatAbsSolar.shape[1]),self.gasMxRatAbsSolar, \
                                        self.rprfAttrbs(self.gasMxRatAbsSolar.shape[1],self.gasMxRatAbsSolar.shape[0], \
                                                        float(self.gasMxRatAbsSolar.max())))
        

        #------------------------------------------------------------
        # Create gasname a priori vertical profile dataset (variable)
        #------------------------------------------------------------
        if int(geomsTmpl) >= int(3):
            hdfFile.createDataSet(self.gasNameUpper+"."+self.getMixingRatioAprioriDryName(), \
                                    (self.gasMxRatAbsSolarApriori.shape[0],self.gasMxRatAbsSolarApriori.shape[1]),self.gasMxRatAbsSolarApriori, \
                                    self.aprfDryAttrbs(self.gasMxRatAbsSolarApriori.shape[1],self.gasMxRatAbsSolarApriori.shape[0], 
                                                    float(self.gasMxRatAbsSolarApriori.max())))
        else:                        

            hdfFile.createDataSet(self.gasNameUpper+"."+self.getMixingRatioAbsorptionSolarAprioriName(), \
                                    (self.gasMxRatAbsSolarApriori.shape[0],self.gasMxRatAbsSolarApriori.shape[1]),self.gasMxRatAbsSolarApriori, \
                                    self.aprfAttrbs(self.gasMxRatAbsSolarApriori.shape[1],self.gasMxRatAbsSolarApriori.shape[0], 
                                                    float(self.gasMxRatAbsSolarApriori.max())))

        if int(geomsTmpl) >= int(3):

            datatowrite=str('\x10Test')
            varvalidmin=varvalidmax=unit=siconversion=fill=self.nullascii
            hdfFile.createDataSet(self.gasNameUpper+"."+self.getMixingRatioAprioriDrySourceName(),(10), \
                                    datatowrite, \
                                    self.aprfSourceAttrbs(varvalidmin, varvalidmax, unit,siconversion, fill), typeOvrd='string' )


        #--------------------------------------------------------------------------------------
        # Create gasname averaging Kernel maxtrix retrieved vertical profile dataset (variable)
        #--------------------------------------------------------------------------------------
        if int(geomsTmpl) >= int(3):
            hdfFile.createDataSet(self.gasNameUpper+"."+self.getMixingRatioAbsorptionSolarAvkDryName(), \
                                    (self.gasMxRatAbsSolarAVK.shape[0],self.gasMxRatAbsSolarAVK.shape[1],self.gasMxRatAbsSolarAVK.shape[2]),  \
                                    self.gasMxRatAbsSolarAVK, \
                                    self.avkDryAttrbs(self.gasMxRatAbsSolarAVK.shape[1],self.gasMxRatAbsSolarAVK.shape[0]))
        else:                      

            hdfFile.createDataSet(self.gasNameUpper+"."+self.getMixingRatioAbsorptionSolarAvkName(), \
                                    (self.gasMxRatAbsSolarAVK.shape[0],self.gasMxRatAbsSolarAVK.shape[1],self.gasMxRatAbsSolarAVK.shape[2]),  \
                                    self.gasMxRatAbsSolarAVK, \
                                    self.avkAttrbs(self.gasMxRatAbsSolarAVK.shape[1],self.gasMxRatAbsSolarAVK.shape[0]))

        

        #-------------------------------------------------------------------------------
        # Create gasname total random error covariance matrix profile dataset (variable) nlyrs,nsize,datatype,units,sclfctr,maxval
        #-------------------------------------------------------------------------------
        if int(geomsTmpl) >= int(3):
            hdfFile.createDataSet(self.gasNameUpper+"."+self.getMixingRatioAbsorptionSolarUncertaintyRandomDryName(), \
                                    (self.gasMxRatAbsSolarUncRand.shape[0],self.gasMxRatAbsSolarUncRand.shape[1],self.gasMxRatAbsSolarUncRand.shape[2]), \
                                    self.gasMxRatAbsSolarUncRand, self.mRandDryAttrbs(self.gasMxRatAbsSolarUncRand.shape[1],self.gasMxRatAbsSolarUncRand.shape[0], float(self.gasMxRatAbsSolarUncRand.min()), float(self.gasMxRatAbsSolarUncRand.max() )))
        else:
            hdfFile.createDataSet(self.gasNameUpper+"."+self.getMixingRatioAbsorptionSolarUncertaintyRandomName(), \
                                    (self.gasMxRatAbsSolarUncRand.shape[0],self.gasMxRatAbsSolarUncRand.shape[1],self.gasMxRatAbsSolarUncRand.shape[2]), \
                                    self.gasMxRatAbsSolarUncRand, self.mRandAttrbs(self.gasMxRatAbsSolarUncRand.shape[1],self.gasMxRatAbsSolarUncRand.shape[0], float(self.gasMxRatAbsSolarUncRand.min()), float(self.gasMxRatAbsSolarUncRand.max() )))



        #-----------------------------------------------------------------------------
        # Create gasname systematic error covariance matrix profile dataset (variable)
        #-----------------------------------------------------------------------------
        if int(geomsTmpl) >= int(3):
            hdfFile.createDataSet(self.gasNameUpper+"."+self.getMixingRatioAbsorptionSolarUncertaintySystematicDryName(), \
                                (self.gasMxRatAbsSolarUncSys.shape[0],self.gasMxRatAbsSolarUncSys.shape[1],self.gasMxRatAbsSolarUncSys.shape[2]), \
                                self.gasMxRatAbsSolarUncSys, self.mSysDryAttrbs(self.gasMxRatAbsSolarUncSys.shape[1],self.gasMxRatAbsSolarUncSys.shape[0], float(self.gasMxRatAbsSolarUncSys.min()), float(self.gasMxRatAbsSolarUncSys.max() )))
        else:
            hdfFile.createDataSet(self.gasNameUpper+"."+self.getMixingRatioAbsorptionSolarUncertaintySystematicName(), \
                                (self.gasMxRatAbsSolarUncSys.shape[0],self.gasMxRatAbsSolarUncSys.shape[1],self.gasMxRatAbsSolarUncSys.shape[2]), \
                                self.gasMxRatAbsSolarUncSys, self.mSysAttrbs(self.gasMxRatAbsSolarUncSys.shape[1],self.gasMxRatAbsSolarUncSys.shape[0], float(self.gasMxRatAbsSolarUncSys.min()), float(self.gasMxRatAbsSolarUncSys.max() )))


        #-----------------------------------------------------------------------------
        # Create gasname retrieved partial column profile dataset (variable)
        #-----------------------------------------------------------------------------
        hdfFile.createDataSet(self.gasNameUpper+'.'+self.getColumnPartialAbsorptionSolarName(), \
                                (self.gasColPartAbsSolar.shape[0],self.gasColPartAbsSolar.shape[1]), self.gasColPartAbsSolar, \
                                self.pcRtrprfAttrbs(self.gasColPartAbsSolar.shape[1],self.gasColPartAbsSolar.shape[0], float(self.gasColPartAbsSolar.max()) ))

        #-----------------------------------------------------------------------------
        # Create gasname a priori partial column profile dataset (variable)
        #-----------------------------------------------------------------------------
        if int(geomsTmpl) >= int(3):
            hdfFile.createDataSet(self.gasNameUpper+'.'+self.getColumnPartialAprioriName(), 
                                    (self.gasColPartAbsApriori.shape[0],self.gasColPartAbsApriori.shape[1]), self.gasColPartAbsApriori, \
                                    self.pcaAprf2Attrbs(self.gasColPartAbsApriori.shape[1],self.gasColPartAbsApriori.shape[0], float(self.gasColPartAbsApriori.max()) ))
        else:
            hdfFile.createDataSet(self.gasNameUpper+'.'+self.getColumnPartialAbsorptionSolarAprioriName(), 
                                    (self.gasColPartAbsApriori.shape[0],self.gasColPartAbsApriori.shape[1]), self.gasColPartAbsApriori, \
                                    self.pcaAprfAttrbs(self.gasColPartAbsApriori.shape[1],self.gasColPartAbsApriori.shape[0], float(self.gasColPartAbsApriori.max()) ))

        #-----------------------------------------------------------------------------
        # Create gasname total column profile dataset (variable)
        #-----------------------------------------------------------------------------
        hdfFile.createDataSet(self.gasNameUpper+"."+self.getColumnAbsorptionSolarName(),np.size(self.gasColAbsSolar), \
                                self.gasColAbsSolar, self.tcRprfAttrbs(np.size(self.gasColAbsSolar), float(self.gasColAbsSolar.max()) ))

        #-----------------------------------------------------------------------------
        # Create gasname apriori total column profile dataset (variable)
        #-----------------------------------------------------------------------------
        if int(geomsTmpl) >= int(3):
            hdfFile.createDataSet(self.gasNameUpper+'.'+self.getColumnAprioriName(), \
                                    np.size(self.gasColAbsSolarApriori), self.gasColAbsSolarApriori, 
                                    self.tcAprf2Attrbs(np.size(self.gasColAbsSolarApriori), float(self.gasColAbsSolarApriori.max()) ))

        else:
            hdfFile.createDataSet(self.gasNameUpper+'.'+self.getColumnAbsorptionSolarAprioriName(), \
                                    np.size(self.gasColAbsSolarApriori), self.gasColAbsSolarApriori, 
                                    self.tcAprfAttrbs(np.size(self.gasColAbsSolarApriori), float(self.gasColAbsSolarApriori.max()) ))



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
                                self.tcRandAttrbs(np.size(self.gasColAbsSolarUncRand), float(self.gasColAbsSolarUncRand.max()) ))

        #-----------------------------------------------------------------------------
        # Create gasname total column systematic uncertainty dataset (variable)
        #-----------------------------------------------------------------------------
        hdfFile.createDataSet(self.gasNameUpper+'.'+self.getColumnAbsorptionSolarUncertaintySystematicName(), \
                                np.size(self.gasColAbsSolarUncSys),  self.gasColAbsSolarUncSys, \
                                self.tcSysAttrbs(np.size(self.gasColAbsSolarUncSys), float(self.gasColAbsSolarUncSys.max()) ))

        

        

        
        #---------------
        # Close HDF file
        #---------------
        hdfFile.closeFile


    def createHDF4(self, geomsTmpl=False):
        ''' create an HDF 4 file in outDdir specified from the pltOutputClass outputDatat passed in'''
                
        #----------------
        # Create instance
        #----------------        
        hdfFile = hdfCrtFile.HDF4File(self.dType)

        #--------------------------------------
        # Open hdf file, write data, close file
        #--------------------------------------        
        self.createHDF(hdfFile, geomsTmpl=geomsTmpl)
        

    def createHDF5(self, geomsTmpl=False):
        ''' create an HDF 5 file in outDdir specified from the pltOutputClass outputDatat passed in'''
                 
        #----------------
        # Create instance
        #----------------            
        hdfFile = hdfCrtFile.HDF5File(self.dType)
        
        #--------------------------------------
        # Open hdf file, write data, close file
        #--------------------------------------                
        self.createHDF(hdfFile, geomsTmpl=geomsTmpl)