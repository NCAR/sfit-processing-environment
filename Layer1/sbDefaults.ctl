#-----------------------------------------------------------------
# Name:
#      sbDefaults.ctl
#
# Purpose:
#      This is the Default ctl file for the error analysis module located 
#      in Layer1Mods.py
#
# Notes:
#       1) Comments are denoted by '#'
#       2) Sb are specified in either native or fractional units. See below
#        
#
# Units:
#    -- Sb for Temperature, SZA, and FOV can either be specified in native 
#       or fractional units. This is controlled by the units flag.
#    -- Following list shows units for various Sb's:
#
#     Parameter Name          Description                           Units
#     ---------------         --------------------------            ----------------------------------
#     temperature             Temperature                           Native [Kelvin] or fractional                      
#     solshft                 Solar line shift                      Native [cm^-1]
#     solstrnth               Solar line strength                   Fractional       
#     phase                   Phase                                 Native [Radians]
#     wshift                  Wavelength shift                      Fractional 
#     dwshift                 Differential Wavelength shift         ******Currently NOT implemented***** 
#     sza                     Solar zenith angle                    Native [degrees] or fractional
#     lineInt                 Line intensity                        Fractional
#     lineTAir                Line temperature broadening           Fractional
#     linePAir                Line pressure broadening              Fractional
#     slope                   Background slope                      Native [cm^-1]
#     curvature               Background curvature                  Native [cm^-2]
#     apod_fcn                Empirical apodization Function        Fractional
#     phase_fcn               Empirical phase function              Fractional
#     omega                   Field of view                         Native [milliradians] or fractional
#     max_opd                 Optical path difference               Fractional
#     zshift                  Zero level                            Native [0-1]
#     profile.gas             VMR of retrieval gas                  Fractional
#
# Notes:
#  1) phase and phase_fcn are different ways to describe the same parameter. 
#     It is not recommended to calculate an error on both simultaneously. 
#  2) dwshift is currently not functional. Do NOT use.
#     
#-----------------------------------------------------------------
#
Kb_info =        temperature                TEMPERAT                fractional               retrievable
                   solshft                 SolLnShft                      cm-1                      True
                 solstrnth                 SolLnStrn                fractional                      True
                     phase                   SPhsErr                   radians                      True
                    wshift                 SWNumShft                fractional                      True
                    wshift                 IWNumShft                fractional                      True
                   dwshift                 DWNumShft units_of_point_calc_space                      True
                       sza                       SZA                fractional                     False
                   lineInt                   LineInt                fractional                     False
                  lineTAir                  LineTAir                fractional                     False
                  linePAir                  LinePAir                fractional                     False
                     slope                 BckGrdSlp                    1/cm-1                      True
                 curvature                 BckGrdCur                    1/cm-2                      True
                  apod_fcn                 EmpApdFcn                fractional                      True
                 phase_fcn                 EmpPhsFnc                fractional                      True
                     omega                       FOV                fractional                     False
                   max_opd                       OPD                fractional                     False
                    zshift                   ZeroLev                       0-1                      True
                   beamamp                  PEAK_AMP                         ?                      True
                beamperiod                  CHAN_SEP                         ?                      True
                 beamphase               ZERO_PH_REF                         ?                      True
                 beamslope            DELTA_PEAK_AMP                         ?                      True

                        #-------#
                        # Flags #
                        #-------#

#-------------
# Output flags
#-------------

VMRoutFlg                             = T              
MolsoutFlg                            = T              
out.total                             = T              
out.srandom                           = T              
out.ssystematic                       = T              

SeinputFlg                            = T                             

sb.sza.random.scaled                  = F
sb.sza.systematic.scaled              = F

sb.omega.random.scaled                = T
sb.omega.systematic.scaled            = T

file.out.total                        = Stotal.output
file.out.total.vmr                    = Stotal.vmr.output
file.out.srandom                      = Srandom.output   
file.out.srandom.vmr                  = Srandom.vmr.output
file.out.ssystematic                  = Ssystematic.output
file.out.ssystematic.vmr              = Ssystematic.vmr.output
file.out.error.summary                = Errorsummary.output   
file.out.avk                          = avk.output  

sb.temperature.random.scaled          = F #in Kelvin
sb.temperature.systematic.scaled      = F #in Kelvin

#sb.temperature.grid                   = -0.020    4     6    10   13     25     40    120
#sb.temperature.correlation.width      =  2
#sb.temperature.random                 =  2       2     4     4    2      3      6      1 
#sb.temperature.systematic             =  1       1     1     2    2      2      4      5

#-------
# Constructed based on values from Boulder and MLO assesments
#--------
sb.temperature.grid                   = -0.020    4       6       10     13       25       40     120
sb.temperature.correlation.width      =  2
sb.temperature.random                 =  1.0      1.0     1.0     0.5    0.5      0.5      1.0     1.0 
sb.temperature.systematic             =  1.0      2.0     1.0     2.0    1.5      2.0      2.0     5.0

#---------
sb.profile.H2O.grid                   = -0.020   1     6    10    13    25    40    120
sb.profile.H2O.correlation.width      = 4
sb.profile.H2O.random                 = 0.10 0.30  0.60  0.50  0.30  0.10  0.10   0.10  #relative units
sb.profile.H2O.systematic             = 0.10  0.4  0.20  0.20  0.20  0.20  0.20   0.20 

sb.profile.HDO.grid                   = -0.020   1     6    10    13    25    40    120
sb.profile.HDO.correlation.width      = 4
sb.profile.HDO.random                 = 0.10 0.30  0.60  0.50  0.30  0.10  0.10   0.10  #relative units
sb.profile.HDO.systematic             = 0.10  0.4  0.20  0.20  0.20  0.20  0.20   0.20 

sb.profile.H2CO.grid                  =-0.020    4     6    10   13     25     40    120 #coarse grid in km
sb.profile.H2CO.correlation.width     =4 #in km, see sfit4 correlation def
sb.profile.H2CO.random                = 0.10   0.30  0.60  0.50 0.30 0.10 0.10 0.10  #relative units
sb.profile.H2CO.systematic            = -0.50 -0.50 -0.20 -0.10 0.10 0.08 0.05 0.05

sb.profile.C2H4.grid                  =-0.020    4     6    10   13     25     40    120 #coarse grid in km
sb.profile.C2H4.correlation.width     =4 #in km, see sfit4 correlation def
sb.profile.C2H4.random                = 0.10   0.30  0.60  0.50 0.30 0.10 0.10 0.10  #relative units
sb.profile.C2H4.systematic            = -0.50 -0.50 -0.20 -0.10 0.10 0.08 0.05 0.05

sb.profile.NO2.grid                   = -0.02 120
sb.profile.NO2.correlation.width      = 4
sb.profile.NO2.random                 = .10 .10 #relative units
sb.profile.NO2.systematic             = .10 .10 #relative units, profile shape is not changed! Will vanish for Tikhonov retrievals

sb.profile.N2O.grid                   =-0.020    4     6    10   13     25     40    120 #coarse grid in km
sb.profile.N2O.correlation.width      =4 #in km, see sfit4 correlation def
sb.profile.N2O.random                 = 0.025 0.025 0.025 0.025 0.025 0.035 0.20 0.65 #relative units
sb.profile.N2O.systematic             = 0.02   0.02  0.02  0.02 0.02 0.03 0.03 0.05  #relative units

sb.profile.CO2.grid                   =-0.020    4     6    10   13     25     40    120 #coarse grid in km
sb.profile.CO2.correlation.width      = 4 #in km, see sfit4 correlation def
sb.profile.CO2.random                 = 0.01 0.01 0.01 0.01 0.01 0.01 0.01 0.01 #relative units
sb.profile.CO2.systematic             = 0.01   0.01  0.01  0.01 0.01 0.01 0.01 0.01  #relative units

sb.profile.O13CO.grid                   =-0.020    4     6    10   13     25     40    120 #coarse grid in km
sb.profile.O13CO.correlation.width      = 4 #in km, see sfit4 correlation def
sb.profile.O13CO.random                 = 0.01 0.01 0.01 0.01 0.01 0.01 0.01 0.01 #relative units
sb.profile.O13CO.systematic             = 0.01   0.01  0.01  0.01 0.01 0.01 0.01 0.01  #relative units

sb.profile.CO18O.grid                   =-0.020    4     6    10   13     25     40    120 #coarse grid in km
sb.profile.CO18O.correlation.width      = 4 #in km, see sfit4 correlation def
sb.profile.CO18O.random                 = 0.01 0.01 0.01 0.01 0.01 0.01 0.01 0.01 #relative units
sb.profile.CO18O.systematic             = 0.01   0.01  0.01  0.01 0.01 0.01 0.01 0.01  #relative units

sb.profile.CH4.grid                   =-0.020    4     6    10   13     25     40    120 #coarse grid in km
sb.profile.CH4.correlation.width      = 4 #in km, see sfit4 correlation def
sb.profile.CH4.random                 = 0.01 0.01 0.01 0.01 0.01 0.01 0.01 0.01 #relative units
sb.profile.CH4.systematic             = 0.01   0.01  0.01  0.01 0.01 0.01 0.01 0.01  #relative units

sb.profile.C2H6.grid                  =-0.020    4     6    10   13     25     40    120 #coarse grid in km
sb.profile.C2H6.correlation.width     =4 #in km, see sfit4 correlation def
sb.profile.C2H6.random                = 0.10   0.30  0.60  0.50 0.30 0.10 0.10 0.10  #relative units
sb.profile.C2H6.systematic            = -0.50 -0.50 -0.20 -0.10 0.10 0.08 0.05 0.05

sb.profile.CO.grid                  =-0.020    4     6    10   13     25     40    120 #coarse grid in km
sb.profile.CO.correlation.width     =4 #in km, see sfit4 correlation def
sb.profile.CO.random                = 0.10   0.30  0.60  0.50 0.30 0.10 0.10 0.10  #relative units
sb.profile.CO.systematic            = -0.50 -0.50 -0.20 -0.10 0.10 0.08 0.05 0.05

sb.profile.CHF2CL.grid                  =-0.020    4     6    10   13     25     40    120 #coarse grid in km
sb.profile.CHF2CL.correlation.width     =4 #in km, see sfit4 correlation def
sb.profile.CHF2CL.random                = 0.10   0.30  0.60  0.50 0.30 0.10 0.10 0.10  #relative units
sb.profile.CHF2CL.systematic            = -0.50 -0.50 -0.20 -0.10 0.10 0.08 0.05 0.05

sb.profile.PAN.grid                    =-0.02 3.00 6.00 9.00 12.0 15.0 25.0 40.0 120.0 # In km, will be interpolated to retrievql grid
sb.profile.PAN.correlation.width       = 3.0
sb.profile.PAN.random                  = 0.55 0.45 0.37 0.45 0.45 0.50 0.80 0.20 0.10 # rbased on comparison btw modeled vertical profiles (WACCM v6, GEOS-Chem v9-02)
sb.profile.PAN.systematic              = 0.80 0.70 0.50 0.35 0.25 0.10 0.10 0.10 0.10 # relative units


sb.profile.O3.grid                     = -0.02 120
sb.profile.O3.correlation.width        = 4
sb.profile.O3.random                   = .05 .05 
sb.profile.O3.systematic               = .05 .05 


sb.profile.*.grid                     = -0.02 120
sb.profile.*.correlation.width        = 4
sb.profile.*.random                   = .10 .10 #relative units
sb.profile.*.systematic               = .10 .10 #relative units, profile shape is not changed! Will vanish for Tikhonov retrievals

sb.omega.*                            = 0.001

sb.sza.random                         = 0.03
sb.sza.systematic                     = 0.03


sb.phase.*                            = 0.001
sb.wshift.*                           = 0.001
sb.slope.*                            = 0.001
sb.curvature.*                        = 0.001
sb.max_opd.*                          = 0.0
sb.band.*.zshift.*                    = 0.0015                                   
sb.solshft.random                     = 0.0000008
sb.solshft.systematic                 = 0.0000002
sb.solstrnth.*                        = 0.01                                       
sb.apod_fcn.*                         = 0.05
sb.phase_fcn.*                        = 0.05

#-------------------------
# Line Intensity Uncertainty
#-------------------------
sb.line*_*.random                     = 0.
sb.lineInt_CH4.systematic             = 0.03     
sb.lineInt_CO.systematic              = 0.02
sb.lineInt_NO2.systematic             = 0.05     
sb.lineInt_HNO3.systematic            = 0.1     
sb.lineInt_O3.systematic              = 0.03 
sb.lineInt_N2O.systematic             = 0.02   # HIT20    
sb.lineInt_HCl.systematic             = 0.05
sb.lineInt_HF.systematic              = 0.05     
sb.lineInt_OCS.systematic             = 0.02
sb.lineInt_NO.systematic              = 0.05     
sb.lineInt_C2H6.systematic            = 0.05
sb.lineInt_HCN.systematic             = 0.1     
sb.lineInt_ClONO2.systematic          = 0.1     
sb.lineInt_H2O.systematic             = 0.15
sb.lineInt_HDO.systematic             = 0.15
sb.lineInt_H2CO.systematic            = 0.10
sb.lineInt_CO2.systematic             = 0.02
sb.lineInt_C2H4.systematic            = 0.05 # Vander Auwera et al. (2014) quote an uncertainty range of 2 to 5%. 
sb.lineInt_C2H4.systematic            = 0.07 


sb.lineInt_PAN.systematic             = 0.08 # From Eureka - Consistent with Tereszchuk (Table 2) # Conversion to sudo could add 1% max (see Geoff's scaling factors on mkIVsun): neglig.!

sb.lineInt_CCL4.systematic            = 0.04 # Consistent with Rinsland et al 2011

sb.lineInt_CHF2Cl.systematic          = 0.07 
#-------------------------
# Line Temp Uncertainty
#-------------------------
sb.lineTAir_*.systematic              = 0.05 
sb.lineTAir_CH4.systematic            = 0.10 
sb.lineTAir_C2H4.systematic           = 0.10 # No indication here. Not included.
sb.lineTAir_CHF2Cl.systematic         = 0.01
sb.lineTAir_H2CO.systematic           = 0.10
sb.lineTAir_PAN.systematic            = 0.03 # From Eureka - X-sect were measured at 295, 273 and 250K
sb.lineTAir_CCL4.systematic           = 0.02 # Raw estimate
sb.lineTAir_N2O.systematic            = 0.1 # HIT20
#-------------------------
# Line Pressure Uncertainty
#-------------------------
sb.linePAir_*.systematic              = 0.05 
sb.linePAir_CH4.systematic            = 0.05
sb.linePAir_C2H4.systematic           = 0.10 # Vander Auwera et al. (2014) quote an uncertainty range of 5 to 10%. 
sb.linePAir_H2CO.systematic           = 0.10 
sb.linePAir_CHF2Cl.systematic         = 0.05 
sb.linePAir_PAN.systematic            = 0.02 #From Eureka - N2 broadening does not seem critical (see concl. of Allen, low temp PAN, 2005)
sb.linePAir_CCL4.systematic           = 0.02 # Raw estimate
sb.linePAir_N2O.systematic            = 0.05 # HIT20
#-------------------------
# include everything in the error budget, except smoothing!!
#-------------------------
sb.total.smoothing                    = F
sb.total.*                            = T