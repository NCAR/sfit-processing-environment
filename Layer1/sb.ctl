#-----------------------------------------------------------------
#
# Sb values for error analysis calculations
#
#
#
#
#
#
#
#
#
#-----------------------------------------------------------------

                        #-------#
                        # Flags #
                        #-------#
#-------------
# Output flags
#-------------
VMRoutFlg  = T                # T = output error covariance matrices in VMR
MolsoutFlg = T                # T = output error covariance matrices in molecules cm^-2


#----------------------------------------------
# Units flag indicate whether the Sb is given in
# native units or scaled
#     F = Native Units, T = Scaled by a priori
#----------------------------------------------
sb.temperature.random.scaled                = F    
sb.temperature.systematic.scaled            = T     
sb.sza.random.scaled                        =
sb.sza.systematic.scaled                    =


                    #-------------------#
                    #     Sb values     #
                    #-------------------#
#-----------------------------------------------
# Sb for temperature:
# -- Specify diagonals of Sb matrix, i.e.
#    one value for each layer (Descending, first
#    value is top layer)     
#-----------------------------------------------
sb.temperature.random       =   
9  9  9  9  9  9  9  7  7  7  7  6  6  5  5  2  2  2  2  2  2  2  2  2
2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2

sb.temperature.systematic   =
9  9  9  9  9  9  9  7  7  7  7  6  6  5  5  2  2  2  2  2  2  2  2 2
2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2

#----------------------------------------------------------------------------
# Sb for SZA:
#  --- Number of entries corresponds to the number of bands
#      *** The order of the entries in sb.sza must correspond to the order of
#          bands specified in "band = " in the sfit4.ctl file ***
#----------------------------------------------------------------------------
sb.sza.random     = 0.001 0.002 0.001
sb.sza.systematic = 0.001 0.002 0.001


#----------------------------------------------------------------------------
# Sb for Omega (FOV):
#  --- Number of entries corresponds to the number of bands
#      *** The order of the entries in sb.omega must correspond to the order of
#          bands specified in "band = " in the sfit4.ctl file ***
#----------------------------------------------------------------------------
sb.omega.random.scaled       =
sb.omega.systematic.scaled   =

sb.omega.random     = 0.001 0.002 0.001
sb.omega.systematic = 0.001 0.002 0.001



# natural units here but should be relative, converted in error_cal.py
# sb.slope.random                     = 0.1
# sb.curvature.random                 = 0.1
# sb.solshft.random                   = 0.5
# sb.solstrnth.random                 = 0.1
 
# sb.phase.random                     = 0.0005 # natural units

# sb.wshift.random                    = 0.1

# sb.apod_fcn.random                  = 0.2
# sb.apod_fcn.systematic              = 0.2
# sb.phase_fcn.random                 = 0.2
# sb.phase_fcn.systematic             = 0.2

# sb.band.1.zshift.random             = 0.01
# sb.band.2.zshift.random             = 0.01
# sb.band.3.zshift.random       	     = 0.01
# sb.band.4.zshift.random       	     = 0.01
# sb.band.1.zshift.systematic         = 0.01
# sb.band.2.zshift.systematic   	     = 0.01
# sb.band.3.zshift.systematic   	     = 0.01
# sb.band.4.zshift.systematic   	     = 0.01

 sb.sza.random                       = 0.0056#0.125 absolute
# sb.sza.systematic                   = 0.001
# sb.omega.random                     = 0.001
# sb.omega.systematic                 = 0.001
# sb.max_opd.random                   = 0.005
# sb.max_opd.systematic               = 0.005
sb.lineInt.systematic               = 0.1 # relative
sb.lineTAir.systematic              = 0.1 # relative
sb.linePAir.systematic              = 0.1 # relative

sb.lineInt.HCN.systematic               = 0.1 # relative
sb.lineTAir.HCN.systematic              = 0.1 # relative
sb.linePAir.HCN.systematic              = 0.1 # relative

sb.lineInt.H2O.systematic               = 0.1 # relative
sb.lineTAir.H2O.systematic              = 0.1 # relative
sb.linePAir.H2O.systematic              = 0.1 # relative
sb.profile.H2O.random                   = 
 9  9  9  9  9  9  9  7  7  7  7  6  6  5  5  2  2  2  2  2  2  2  2  2
 2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2

# Output
 out.total                             = T
 out.srandom                           = T
 out.ssystematic.interferer            = T      
 out.ssystematic                       = T


# file names
 file.out.total                        = Stotal.output
 file.out.total.vmr                    = Stotal.vmr.output
 file.out.srandom                      = Srandom.output
 file.out.srandom.vmr                  = Srandom.vmr.output
 file.out.ssystematic                  = Ssystematic.output
 file.out.ssystematic.vmr              = Ssystematic.vmr.output
 file.out.error.summary                = Errorsummary.output
