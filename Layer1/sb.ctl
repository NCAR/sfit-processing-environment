#-----------------------------------------------------------------
# Name:
#      sb.ctl
#
# Purpose:
#      sb.ctl created as example for the python package distribution
#      This is the ctl file for the error analysis module located 
#      in Layer1Mods.py
#
#      - In this example, defaults are set True, hence path defined in sbDefaults needs to be set
#      - In this example, temperature, and sza are defined here, and will override values in the sb defaults 
#
# Notes:
#       1) Comments are denoted by '#'
#       2) Sb are specified in either native or fractional units. See below
#        
#
# Units: 
#        Check: Layer1/sbDefaults.ctl
#-----------------------------------------------------------------

#-------------
# Default flag (T = true; F = False)
#-------------
sbDefFlg                                = T

#-------------
# Location of default Sb
#-------------
sbDefaults                              = /data/pbin/Dev_Ivan/Layer1/sbDefaults.ctl

                        #-------#
                        # Flags #
                        #-------#


#-----------------------------------------------
# Units flag indicate whether the Sb is given in
# native units or scaled
#     F = Native Units, T = Fractional
#-----------------------------------------------
sb.temperature.random.scaled                = F         # If = T (fractional) -- scaled by a priori
sb.temperature.systematic.scaled            = F         # If = T (fractional) -- scaled by a priori
sb.sza.random.scaled                        = F
sb.sza.systematic.scaled                    = F



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
1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0 .7 .7 .7 .7 .7 .7 .7 .32 0.665 0.907 0.572
0.181 0.168 0.176 0.232 0.277 0.407 0.523 0.368 0.234 0.045 0.571 0.612 0.981 0.143
0.177 0.486 0.127 0.271 0.171 0.7   0.928 0.736 0.728 1.273 1.723 2.201 2.446

sb.temperature.systematic   =
10.0 9.0 8.0 7.0 6.0 5.0 4.0 3.0 2.0 2.0 2.0 2.0 2.0 2.0 2.0 2.0 1.769 1.387 1.639 1.539
1.408 1.374 1.187 1.171 1.065 1.123 1.039 1.148 1.214 1.427 1.544 2.05 2.774 2.967 2.228
1.955 2.171 2.166 2.144 2.218 2.228 2.159 2.423 2.479 2.475 2.306 2.26 


#----------------
# Single value Sb
#----------------
sb.sza.random           = 0.15    # Half Angular diameter of sun 

