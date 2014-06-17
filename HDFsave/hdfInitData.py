#----------------------------------------------------------------------------------------
# Name:
#        hdfInitData.py
#
# Purpose:
#       Class of initializing data. This is the interface between the data source and
#       the HDF write functions.
#
#
# Notes:
#      1) Create your own interface to get the data from your source to the HDFfile. 
#         Currently there are three interfaces in this file:
#             initIDL -- This interface takes data in from an IDL save file. Note the
#                         IDL save file has a specific structure
#             initPy  -- This interface can take data using python functions. It is 
#                        currently not developed
#             initDummy -- This is a dummy interface which will create dummy (FillValue)
#                          data to go into the HDF file.
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
import datetime as dt
import numpy as np
import tables as h5
import scipy.io as si
from itertools import izip

class HDFinitData(object):
    
    def initIDL(self,fname,iyear,imonth,iday,fyear,fmonth,fday):
        ''' Interface for initializing data with IDL save files'''
        #--------------------------------------------------------------------------------------------------------------------        
        #                             -------- IDL Data Structure Variables --------
        # ['TOTOBS', 'FLTR_NEGVMR', 'FLTR_TC0', 'FLTR_MAXRMS', 'NOBS', 'SPECTRANAME', 'DIRECTORY', 'HHMMSS', 'YYYYMMDD', 
        #  'SNR', 'P', 'T', 'MS', 'RMS', 'DOFS', 'SZA', 'AZI', 'ITERATIONS', 'ZCORRECT', 'WSHIFT', 'ZEROLEV', 'BSLOPE', 
        #  'PHASE', 'APRVMR', 'APRLAYCOL', 'APRTC', 'RETVMR', 'RETLAYCOL', 'RETTC', 'H2O_VMR', 'H2O_TC', 'YEAR', 'MONTH', 
        #  'DAY', 'HRS', 'DOY', 'TYR', 'DATETIME', 'JDAY', 'LATITUDE', 'LONGITUDE', 'ALT_INSTRUMENT', 'SURFACE_PRESSURE', 
        #  'SURFACE_TEMPERATURE', 'ALT_INDEX', 'ALT_BOUNDARIES', 'ALTITUDE', 'AK', 'AKTC', 'SENS', 'EXTERNAL_SOLAR_SENSOR', 
        #  'DETECTOR_INTERN_TEMP_SWITCH', 'GUIDER_QUAD_SENSOR_SUM', 'OUTSIDE_RELATIVE_HUMIDITY', 'INT_TIME', 'TOT_RAND_ERR', 
        #  'TOT_SYS_ERR', 'RAND_COVAR', 'SYS_COVAR']
        #--------------------------------------------------------------------------------------------------------------------
        
        #-------------------------------
        # Read IDL save file into Python 
        # dictionary
        #-------------------------------
        dataStrc = si.readsav(fname)
        
        #------------------------------------------------
        # Get the name of the variables in data structure
        # Assuming that the data structure is named ds
        #------------------------------------------------
        varName = dataStrc['ds'].dtype.names
        
        #----------------------------
        # Find number of observations
        #----------------------------
        nobs = dataStrc['ds']['NOBS'][0]
        
        #------------------------------------
        # Determine number of altitude layers
        #------------------------------------
        nlyrs = len(dataStrc['ds']['ALTITUDE'][0])
                
        #------------------------------------
        # Put dates in python datetime object
        #------------------------------------
        YYYYMMDD   = dataStrc['ds']['YYYYMMDD']
        HHMMSS     = dataStrc['ds']['HHMMSS']        
        self.dates = np.array([dt.datetime(int(ymd[0:4]),int(ymd[4:6]),int(ymd[6:]),int(hms[0:2]),int(hms[2:4]),int(hms[4:])) for (ymd,hms) in izip(YYYYMMDD,HHMMSS)])
        
        
        #---------------------------------------------------
        # Assign IDL data to attributes to be written to HDF
        #---------------------------------------------------
        self.datesJD2K                      = np.asarray(dataStrc['ds']['DATETIME'])
        self.latitude                       = dataStrc['ds']['LATITUDE'][0]
        self.longitude                      = dataStrc['ds']['LONGITUDE'][0]
        self.instAltitudes                  = dataStrc['ds']['ALT_INSTRUMENT'][0] / 1000.0                          # Convert [m] -> [km]
        self.surfPressures                  = np.asarray(dataStrc['ds']['SURFACE_PRESSURE'])
        self.surfTemperatures               = np.asarray(dataStrc['ds']['SURFACE_TEMPERATURE'])
        self.altitudes                      = dataStrc['ds']['ALTITUDE'][0]
        self.altitudeBoundaries             = np.rot90(dataStrc['ds']['ALT_BOUNDARIES'][0])
        self.pressures                      = np.vstack(dataStrc['ds']['P']).reshape(nobs,nlyrs)
        self.temperatures                   = np.vstack(dataStrc['ds']['T']).reshape(nobs,nlyrs)
        self.gasMxRatAbsSolar               = np.vstack(dataStrc['ds']['RETVMR']).reshape(nobs,nlyrs)
        self.gasMxRatAbsSolarApriori        = np.vstack(dataStrc['ds']['APRVMR']).reshape(nobs,nlyrs)
        self.gasMxRatAbsSolarAVK            = np.vstack(dataStrc['ds']['AK']).reshape(nobs,nlyrs,nlyrs) 
        self.integrationTimes               = np.asarray(dataStrc['ds']['INT_TIME'])  
        self.gasMxRatAbsSolarUncRand        = np.vstack(dataStrc['ds']['RAND_COVAR']).reshape(nobs,nlyrs,nlyrs)  
        self.gasMxRatAbsSolarUncSys         = np.vstack(dataStrc['ds']['SYS_COVAR']).reshape(nobs,nlyrs,nlyrs)  
        self.gasColPartAbsSolar             = np.vstack(dataStrc['ds']['RETLAYCOL']).reshape(nobs,nlyrs)
        self.gasColPartAbsApriori           = np.vstack(dataStrc['ds']['APRLAYCOL']).reshape(nobs,nlyrs)
        self.gasColAbsSolar                 = np.asarray(dataStrc['ds']['RETTC']) 
        self.gasColAbsSolarApriori          = np.asarray(dataStrc['ds']['APRTC'])  
        self.gasColAbsSolarAVK              = np.vstack(dataStrc['ds']['AKTC']).reshape(nobs,nlyrs) 
        self.gasColAbsSolarUncRand          = np.asarray(dataStrc['ds']['TOT_RAND_ERR'])  
        self.gasColAbsSolarUncSys           = np.asarray(dataStrc['ds']['TOT_SYS_ERR'])  
        self.angleZastr                     = np.asarray(dataStrc['ds']['SZA']) 
        self.angleSolAz                     = np.asarray(dataStrc['ds']['AZI']) 
        self.h2oMxRatAbsSolar               = np.vstack(dataStrc['ds']['H2O_VMR']).reshape(nobs,nlyrs) 
        self.h2oColAbsSol                   = np.asarray(dataStrc['ds']['H2O_TC'])  


        self.filter_for_date(iyear,imonth,iday,fyear,fmonth,fday)


    def ini_tmphdf5(self,fname,iyear,imonth,iday,fyear,fmonth,fday):
        ''' Interface to read tmp.hd5 created with create_hdf5.py'''


        h5f = h5.File(fname)
        #---------------------------------------------------
        # Assign IDL data to attributes to be written to HDF
        #---------------------------------------------------
        self.datesJD2K                      = np.asarray(h5f.root.mdate[:])
        self.latitude                       = np.asarray(h5f.root.lat[:])
        self.longitude                      = np.asarray(h5f.root.lon[:])
        self.instAltitudes                  = np.asarray(h5f.root.Zb[end]) / 1000.0  # Convert [m] -> [km]
        self.surfPressures                  = np.asarray(h5f.root.P_surface[:])
        self.surfTemperatures               = np.asarray(h5f.root.T_surface[:])
        self.altitudes                      = np.asarray(h5f.root.Z[:])
        self.altitudeBoundaries             = np.rot90(h5f.root.Zb[:]) / 1000.0
        self.pressures                      = np.asarray(h5f.root.P[:])
        self.temperatures                   = np.asarray(h5f.root.T[:])
        self.gasMxRatAbsSolar               = np.asarray(h5f.root.vmr_rt[:])
        self.gasMxRatAbsSolarApriori        = np.asarray(h5f.root.vmr_ap[:])
        self.gasMxRatAbsSolarAVK            = np.asarray(h5f.root.avk_vmr[:])
        self.integrationTimes               = np.asarray(h5f.root.dur[:])
        self.gasMxRatAbsSolarUncRand        = np.asarray(h5f.root.cov_vmr_ran[:])
        self.gasMxRatAbsSolarUncSys         = np.asarray(h5f.root.cov_vmr_sys[:])
        self.gasColPartAbsSolar             = np.asarray(h5f.root.pcol_rt[:])
        self.gasColPartAbsApriori           = np.asarray(h5f.root.pcol_ap[:])
        self.gasColAbsSolar                 = np.asarray(h5f.root.col_rt[:])
        self.gasColAbsSolarApriori          = np.asarray(h5f.root.col_ap[:])
        self.gasColAbsSolarAVK              = np.asarray(h5f.root.avk_col[:])
        self.gasColAbsSolarUncRand          = np.asarray(h5f.root.col_ran[:])
        self.gasColAbsSolarUncSys           = np.asarray(h5f.root.col_sys[:])
        self.angleZastr                     = np.asarray(h5f.root.sza[:])
        self.angleSolAz                     = np.asarray(h5f.root.azi[:])
        self.h2oMxRatAbsSolar               = np.asarray(h5f.root.h2o_vmr_setup[:])
        self.h2oColAbsSol                   = np.asarray(h5f.root.col_h2o_setup[:])

        self.filter_for_date(iyear,imonth,iday,fyear,fmonth,fday)

                     
    def filter_for_date(self,iyear,imonth,iday,fyear,fmonth,fday) 

        #------------------------------------------
        # Find indicies of dates in specified range
        #------------------------------------------
        idate = dt.datetime(iyear,imonth,iday)
        fdate = dt.datetime(fyear,fmonth,fday)
        inds  = np.where((self.dates >= idate) & (self.dates <= fdate))[0]

        self.dates                          = self.dates[inds]
        self.datesJD2K                      = self.datesJD2K[inds]
        self.surfPressures                  = self.surfPressures[inds]
        self.surfTemperatures               = self.surfTemperatures[inds]
        self.pressures                      = self.pressures[inds,:]
        self.temperatures                   = self.temperatures[inds,:]
        self.gasMxRatAbsSolar               = self.gasMxRatAbsSolar[inds,:]
        self.gasMxRatAbsSolarApriori        = self.gasMxRatAbsSolarApriori[inds,:]
        self.gasMxRatAbsSolarAVK            = self.gasMxRatAbsSolarAVK[inds,:,:]
        self.integrationTimes               = self.integrationTimes[inds]
        self.gasMxRatAbsSolarUncRand        = self.gasMxRatAbsSolarUncRand[inds,:,:]
        self.gasMxRatAbsSolarUncSys         = self.gasMxRatAbsSolarUncSys[inds,:,:]
        self.gasColPartAbsSolar             = self.gasColPartAbsSolar[inds,:]
        self.gasColPartAbsApriori           = self.gasColPartAbsApriori[inds,:]
        self.gasColAbsSolar                 = self.gasColAbsSolar[inds]
        self.gasColAbsSolarApriori          = self.gasColAbsSolarApriori[inds]
        self.gasColAbsSolarAVK              = self.gasColAbsSolarAVK[inds,:]
        self.gasColAbsSolarUncRand          = self.gasColAbsSolarUncRand[inds]
        self.gasColAbsSolarUncSys           = self.gasColAbsSolarUncSys[inds]
        self.angleZastr                     = self.angleZastr[inds]
        self.angleSolAz                     = self.angleSolAz[inds]
        self.h2oMxRatAbsSolar               = self.h2oMxRatAbsSolar[inds,:]
        self.h2oColAbsSol                   = self.h2oColAbsSol[inds]
        


    def initPy(self):
        ''' Interface for initializing data with python set of routines'''
        
        #---------------------------------------
        # Convert dates to Julian Day since 2000
        #---------------------------------------        
        self.datesJD2K = np.array([(x - dt.datetime(2000,1,1)).total_seconds()/dt.timedelta(1).total_seconds() for x in self.dates])    
        
        
        
        
    def initDummy(self):
        ''' Interface for initalizing with dummy data. For testing!!!'''
 
        #---------------------------------------
        # Convert dates to Julian Day since 2000
        #---------------------------------------        
        self.dates = np.array([dt.datetime(2008,1,1),dt.datetime(2008,1,2),dt.datetime(2008,1,3),dt.datetime(2008,1,4)])
        self.datesJD2K = np.array([(x - dt.datetime(2000,1,1)).total_seconds()/dt.timedelta(1).total_seconds() for x in self.dates])   
                    
        dummyNlayers                        = 41
        dummyNangles                        = len(self.dates)
        dummySingleArray                    = np.empty(1)
        dummySingleArray.fill(self.getFillValue())
        dummyLayerData                      = np.empty(dummyNlayers)
        dummyLayerData.fill(self.getFillValue())
        dummyAngleData                      = np.empty(dummyNangles)
        dummyAngleData.fill(self.getFillValue())
        dummyNotes                          = 'notes about dummy data'
        dummy2dimLayerData                  = np.empty(2*dummyNlayers).reshape((2, dummyNlayers))
        dummy2dimLayerData.fill(self.getFillValue())
        dummy2dimData                       = np.empty(dummyNlayers*dummyNangles).reshape((dummyNangles, dummyNlayers))
        dummy2dimData.fill(self.getFillValue())
        dummy3dimData                       = np.empty(dummyNangles*dummyNlayers*dummyNlayers).reshape((dummyNangles, dummyNlayers, dummyNlayers))
        dummy3dimData.fill(self.getFillValue())
    
        self.latitude                       = dummySingleArray
        self.longitude                      = dummySingleArray
        self.instAltitudes                  = dummySingleArray
        self.surfPressures                  = dummyAngleData
        self.surfTemperatures               = dummyAngleData
        self.altitudes                      = dummyLayerData
        self.altitudeBoundaries             = dummy2dimLayerData
        self.pressures                      = dummy2dimData
        self.temperatures                   = dummy2dimData
        self.gasMxRatAbsSolar               = dummy2dimData
        self.gasMxRatAbsSolarApriori        = dummy2dimData
        self.gasMxRatAbsSolarAVK            = dummy3dimData
        self.integrationTimes               = dummyAngleData  
        self.gasMxRatAbsSolarUncRand        = dummy3dimData  
        self.gasMxRatAbsSolarUncSys         = dummy3dimData  
        self.gasColPartAbsSolar             = dummy2dimData
        self.gasColPartAbsApriori           = dummy2dimData
        self.gasColAbsSolar                 = dummyAngleData 
        self.gasColAbsSolarApriori          = dummyAngleData 
        self.gasColAbsSolarAVK              = dummy2dimData 
        self.gasColAbsSolarUncRand          = dummyAngleData 
        self.gasColAbsSolarUncSys           = dummyAngleData 
        self.angleZastr                     = dummyAngleData
        self.angleSolAz                     = dummyAngleData
        self.h2oMxRatAbsSolar               = dummy2dimData 
        self.h2oColAbsSol                   = dummyAngleData 
