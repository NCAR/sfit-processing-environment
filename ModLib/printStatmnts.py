#----------------------------------------------------------------------------------------
# Name:
#        printStatmnts.py
#
# Purpose:
#       Collection of strings used in sfit4Layer1
#
# Notes:
#       1)
#			
#
#
# Version History:
#       Created, December, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
#
#
# References:
#
#----------------------------------------------------------------------------------------


def pspecInputStr():
    ''' String data for writing pspec input file '''
    
    dataStr = [
        '# Input file for pspec.f90\n',                                                                             # 0
        '# version V1.1 for sfit4 v0.9.5 October 1 2013\n',                                                         # 1
        '# \n',                                                                                                     # 2
        '# pspec.f90 loops through this file and creates an ascii file with a spectra block for\n',                 # 3 
        '# each spectrum that will be fit by sfit4 - the t15asc.4 file\n',                                          # 4
        '# the observation lat lon and altitude are required for each spectrum\n',                                  # 5 
        '# Latitude of Observation [+N, 90 - -90]\n',                                                               # 6
        '# Longitude of Observation[+E, 0 - 360]\n',                                                                # 7
        '# Altitude of Observation [masl]\n',                                                                       # 8
        '# \n',                                                                                                     # 9
        '# output & verbosity flags\n',
        '# oflag  - output\n',
        '#     = 1 output t15asc file\n',
        '#     = 2 bnr file\n',
        '#     = 3 both\n',
        '# vflag  - verbosity\n',
        '#     = 0 no output from baseline correct or zero bnr or block output for plotting\n',
        '#     = 1 verbose output from bc and zeroed bnr but no blockout\n',
        '#     = 2 verbose, zeroed bnr and blockout for plotting\n',
        '# \n',
        '# filter bands and regions for calculating SNR (max 100)\n',
        '# noise value is calculate in the region below that is nearest to the fit microwindow\n',
        '#  SNR = (Peak signal in microwindow) / noise\n',
        '# \n',
        '# \n',
        '# number of BNR files\n',
        '# \n',
        '# each block contains at least 2 lines:\n',
        '# bnr spectra file name\n',
        '# roe, nterp, rflag, fflag, zflag\n',
        '# \n',
        '# roe - radius of earth [km]\n',
        '# \n',
        '# nterp -  zero fill factor\n',
        '#     = 0 - skip resample & resolution degradation (regardless of sfit4.ctl:band.n.max_opd value)\n',
        '#     = 1 - minimally sample at opdmax\n',
        '#     > 1 - interpolate nterp-1 points upon minimal sampled spacing\n',
        '#     note: OPD is taken from sfit4.ctl:band.n.max_opd value\n',
        '# \n',
        '# rflag - ratio flag, to ratio the spectra with another low resolution spectral file (eg spectral envelope)\n',
        '#      = 0 - no ratio\n',
        '#      = 1 - ratio, file is a bnr of same type as fflag below, expected to be resolution of ~10cm-1\n',
        '# fflag -  file open flag\n',
        '#     = 0 for fortran unformatted file\n',
        '#     = 1 for open as steam or binary or c-type file (gfortran uses stream)\n',
        '#\n'
        '# zflag - zero offset\n',
        '#     = 0 no zero offset\n',
        '#     = 1 try w/ baselincorrect\n',
        '#     0 < z < 1 use this value\n',
        '#     = 2 use optimized 2nd polynomial fit to fully absorbed regions in 10m region\n',
        '#\n',
        '# roe, nterp, rflag, fflag, zflag\n',
        '#\n'
         ]

    return dataStr


