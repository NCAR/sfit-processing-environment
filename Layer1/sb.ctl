#-----------------------------------------------------------------
# Name:
#      sb.ctl
#
# Purpose:
#      This is the ctl file for the error analysis module located 
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
#     sza                     Solar zenith angle                    Native [degrees] or fractional ??
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
#  2) dwshift is currently not implemented.
#  3) Line parameter errors currently only work for 
#
#-----------------------------------------------------------------

                        #-------#
                        # Flags #
                        #-------#
#-------------
# Output flags
#-------------
VMRoutFlg                  = T      # T = output error covariance matrices in VMR
MolsoutFlg                 = T      # T = output error covariance matrices in molecules cm^-2
out.total                  = T      # T = write out total random error covariance matrix
out.srandom                = T      # T = write out random error covariance matrix
out.ssystematic            = T      # T = write out systematic error covariance matrix 

#------------
# Input Flags
#------------
SeInputFlg = F                # This flag determines where the Se matrix is read in.
                              # If = T, the Se matrix is read in from sfit output file: file.out.seinv_vector
                              # This method takes into account de-weighting of the SNR set in the sfit4.ctl file
                              # If = F, the Se is taken from the summary file. These are the actual SNR values
                              # taken from the t15asc files.

#-----------------------------------------------
# Units flag indicate whether the Sb is given in
# native units or scaled
#     F = Native Units, T = Fractional
#-----------------------------------------------
sb.temperature.random.scaled                = F         # If = T (fractional) -- scaled by a priori
sb.temperature.systematic.scaled            = T         # If = T (fractional) -- scaled by a priori
sb.sza.random.scaled                        = T
sb.sza.systematic.scaled                    = T
sb.fov.random.scaled                        = T
sb.fov.systematic.scaled                    = T


                    #-------------------#
                    # Output file names #
                    #-------------------#
file.out.total                        = Stotal.output
file.out.total.vmr                    = Stotal.vmr.output
file.out.srandom                      = Srandom.output
file.out.srandom.vmr                  = Srandom.vmr.output
file.out.ssystematic                  = Ssystematic.output
file.out.ssystematic.vmr              = Ssystematic.vmr.output
file.out.error.summary                = Errorsummary.output



                    #-------------------#
                    #     Sb values     #
                    #-------------------#
#-----------------------------------------------
# Sb for temperature & profile.gas:
# -- Specify diagonals of Sb matrix, i.e.
#    one value for each layer (Descending, first
#    value is top layer)  
#------------------------------------------------
sb.temperature.random       =   
9  9  9  9  9  9  9  7  7  7  7  6  6  5  5  2  2  2  2  2  2  2  2  2
2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2

sb.temperature.systematic   =
9  9  9  9  9  9  9  7  7  7  7  6  6  5  5  2  2  2  2  2  2  2  2 2
2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2

sb.profile.H2O.random       = 
 9  9  9  9  9  9  9  7  7  7  7  6  6  5  5  2  2  2  2  2  2  2  2  2
 2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2

sb.profile.H2O.systematic   = 
 9  9  9  9  9  9  9  7  7  7  7  6  6  5  5  2  2  2  2  2  2  2  2  2
 2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2

#----------------------------------------------------------------------------
# Micro-window dependent Sb:
# -- Number of entries corresponds to the number of bands
#    *** The order of the entries in sb.sza must correspond to the order of
#        bands specified in "band = " in the sfit4.ctl file ***
#----------------------------------------------------------------------------
sb.sza.random           = 0.001 0.002 0.001
sb.sza.systematic       = 0.001 0.002 0.001

sb.omega.random         = 0.001 0.002 0.001
sb.omega.systematic     = 0.001 0.002 0.001

sb.phase.random         = 0.001 0.002 0.001
sb.phase.systematic     = 0.001 0.002 0.001

sb.wshift.random        = 0.001 0.002 0.001
sb.wshift.systematic    = 0.001 0.002 0.001

sb.slope.random         = 0.001 0.002 0.001
sb.slope.systematic     = 0.001 0.002 0.001

sb.curvature.random     = 0.001 0.002 0.001
sb.curvature.systematic = 0.001 0.002 0.001

sb.max_opd.random       = 0.001 0.002 0.001
sb.max_opd.systematic   = 0.001 0.002 0.001

#----------------
# Single value Sb
#----------------
sb.solshft.random       = 0.5
sb.solstrnth.random     = 0.1
sb.apod_fcn.random      = 0.2
sb.apod_fcn.systematic  = 0.2
sb.phase_fcn.random     = 0.2   ## Micro window 
sb.phase_fcn.systematic = 0.2

#-----------------------------------------------------------
# Sb for zshift is micro window dependent. However, Sb's are 
# only to be specified in microwindows where zshift is not
# retrieved. For example, if you have two microwindows and 
# you retrieve the first (1), then you would specify:
#  sb.band.2.zshift.random and sb.band.2.zshift.systematic
# The number corresponds to the band number in the sfit4.ctl
# file.
#-----------------------------------------------------------
sb.band.1.zshift.random      = 0.01
sb.band.2.zshift.random      = 0.01
sb.band.3.zshift.random      = 0.01
sb.band.4.zshift.random      = 0.01
sb.band.1.zshift.systematic  = 0.01
sb.band.2.zshift.systematic  = 0.01
sb.band.3.zshift.systematic  = 0.01
sb.band.4.zshift.systematic  = 0.01


#----------------------------------------------------------
# Sb's for lineInt, lineTair, and linePair currently only
# work for when kb.line.gas = target in the sfit4.ctl file.
# Does not work with kb.line.gas = retrieval because it is 
# unclear which gas and order of gases in Kb
#----------------------------------------------------------
**sb.lineInt.systematic               = 0.1     
**sb.lineTAir.systematic              = 0.1 
**sb.linePAir.systematic              = 0.1 

**sb.dwshift.H2O.random                
**sb.dwshift.H2O.systematic           










