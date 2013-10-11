#----------------------------------------------------------------------------------------
# Name:
#        Layer1Mods.py
#
# Purpose:
#       This file contains various modules used by sfit layer 1 processing. These modules 
#       are intended to be user specific. They have been seperated from the main code such
#       that they can easily be tailored to the user. Currently there are two modules:
#       1) reMkrNCAR  -- This is a simple module to build a reference profile.
#       2) t15ascPrep -- This module creates a pspec.input file and runs pspec to create
#                        t15asc files from bnr file type.
#
#
# External Subprocess Calls:
#	1) Call to sfitClasses to run subProcRun. This handles stdout and stderr of a sub-process call		
#
#
# Notes:
#       1)
#			
#
#
# Version History:
#       Created, June, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
#
#
# References:
#
#----------------------------------------------------------------------------------------

                                #-------------------------#
                                # Import Standard modules #
                                #-------------------------#
                                
import os                                
import sys
import fileinput
import re
import glob
import logging
import shutil
import re
import sfitClasses as sc
import numpy as np
import itertools as it

                                #--------------------------#
                                #                          #
                                #  -- Helper functions --  #
                                #                          #
                                #--------------------------#
def tryopen(fname,lines,rtnFlg,logFile=False):
    try:
        with open(fname, 'r' ) as fopen:
            lines = fopen.readlines()
            rtnFlg = True
    except IOError as errmsg:
        print errmsg
        if logFile: logFile.error(errmsg)
        rtnFlg = False         
    

                                #-------------------------#
                                #                         #
                                #   -- NCAR Refmaker --   #
                                #                         #
                                #-------------------------#


def refMkrNCAR(zptwPath, WACCMfile, outPath, lvl, wVer, specDB, spcDBind, logFile=False):
    ''' Reference maker for NCAR. Insert your own version here. '''
    #----------------------------------------------
    # refMkrNCAR level options for creating 
    # reference.prf
    #
    # Level 0 option:
    #   Use pre-existing zpt file. Concatonate with
    #   water and WACCM profiles. 
    # Level 1 option:
    #   Use pre-existing zpt file. Concatonate with
    #   water and WACCM profiles. Replace surface
    #   pressure and temperature with values in
    #   database file. If those values are not 
    #   present, then default to origianl zpt file
    #----------------------------------------------  
    
    #--------------------------
    # Determine if paths exists
    #--------------------------    
    try:
        os.path.isdir(zptwPath)     # Path for zpt and water profile
        os.path.isfile(WACCMfile)    # Path for WACCM profile
        os.path.isdir(outPath)      # Outpath for reference.prf
    except OSError as errmsg:
        print errmsg
        if logFile: logFile.error(errmsg)
        sys.exit()
        
    #--------------
    # Find ZPT file
    #--------------
    zptFiles = glob.glob(zptwPath + 'ZPT.nmc*')
    
    # If more than one zpt file found trigger warning and use first one 
    if len(zptFiles) > 1:                 
        print 'Found more than one ZPT file. Using file: ' + zptFiles[0]
        if logFile: logFile.info('Using ZPTW file: ' + zptFiles[0])
        zptFile = zptFiles[0]
        
    # If no zpt files found trigger error    
    elif len(zptFiles) == 0:              
        print 'No zpt files found in: ' + zptwPath
        if logFile: logFile.error('No zpt files found in: ' + zptwPath)
        sys.exit()
        
    else:
        zptFile = zptFiles[0]
        
    #------------------------
    # Find water profile file
    #------------------------
    waterFiles = glob.glob(zptwPath + 'w-120*')

    # If no water files found trigger error
    if len(waterFiles) == 0:
        print 'No water files found in: ' + zptwPath
        if logFile: logFile.error('No water files found in: ' + zptwPath)
        sys.exit()            

    #---------------------------
    # Grab correct water version
    # based on user input
    #---------------------------
    # Create a list of version number for water files
    r = re.compile(r"([0-9]+)")
    waterVer = [int(r.search(os.path.splitext(wfile)[1]).group(1)) for wfile in waterFiles]
    
    # For wVer < 0 get latest water version file
    if wVer < 0:
        waterInd  = waterVer.index(max(waterVer))
       
    # For wVer >= 0 get user specified water version file   
    else:
        try:
            waterInd = waterVer.index(wVer)
        except ValueError:
            print 'Water version %d not found, using latest version' % wVer
            if logFile: logFile.error('Water version %d not found, using latest version'% wVer)
            waterInd = waterVer.index(max(waterVer))
            
    waterFile = waterFiles[waterInd] 
       
        
    #----------------------------------
    # Concate ZPT, water, and WACCM  
    # profiles to produce reference.prf
    #----------------------------------
    refFile = outPath + 'reference.prf'
    
    with open( refFile, 'w') as fout:
        for line in fileinput.input([zptFile,waterFile,WACCMfile]):
            if line.strip():
                fout.write(line)
              
    #--------------------------------------------
    # Now that reference.prf is created, go back to
    # make necessary changes. This includes adding 
    # the number 99 to first line of file and 
    # inserting database values of temperature and
    # pressure if specified by level option.
    #----------------------------------------------
               
    #------------------------------
    # Add number 99 to first line
    # of file indicating 99 species
    # included in list
    #------------------------------                 
    with open( refFile, 'r+' ) as fout:
        lines    = fout.readlines()
        lines[0] = lines[0].rstrip() + "{0:5d}".format(99) + '\n'
        # Number of atmospheric layers
        nlyrs    = int(lines[0].split()[1])         
        
        # For level 1 options
        if lvl == 1:
            # Determine the number of lines in each profile = ceil(nlyrs/5)
            nlines = int(nlyrs//5)
            
            #---------------------------------------------------------
            # Determine if database values of Temperature and Pressure
            # are valid to use. First choice is external station data.
            # If this is not available default to house log data. If 
            # this is not available default to NCEP data.
            #---------------------------------------------------------
            # Temperature
            NCEPtempFlg = False
            
            if specDB['ExtStatTemp'][spcDBind] == -9999:
                if specDB['HouseTemp'][spcDBind] == -9999:
                    NCEPtempFlg = True
                    
                else:
                    newTemp = specDB['HouseTemp'][spcDBind]
                    newTemp += 273.15                        # Convert [C] => [K]           
                    newTemp = "{0:.4f}".format(newTemp)
                    
            else:
                newTemp = specDB['ExtStatTemp'][spcDBind]
                newTemp += 273.15                            # Convert [C] => [K]
                newTemp = "{0:.4f}".format(newTemp)
                
            # Pressure
            NCEPpresFlg = False
            
            if specDB['ExtStatPres'][spcDBind] == -9999:
                if specDB['HousePres'][spcDBind] == -9999:
                    NCEPpresFlg = True
                    
                else:
                    newPres = specDB['HousePres'][spcDBind]
                    newPres = "{0:.4e}".format(newPres)
            else:
                newPres = specDB['ExtStatPres'][spcDBind]
                newPres = "{0:.4e}".format(newPres)
                       
            #-----------------------------------------
            # Replace surface temperature and pressure
            # in reference.prf with external station 
            # or house log data if applicable
            #-----------------------------------------
            for linenum,line in enumerate(lines):
                if NCEPpresFlg == False:
                    if 'pressure' in line.lower():
                        nlnum        = linenum + nlines
                        oldPres      = lines[nlnum].split()[-1].rstrip(',')
                        
                        #----------------------------------------------------
                        # Compare NCEP pressure with new updated pressure
                        #  1) If updated surface pressure is less than NCEP
                        #     one level above surface throw error
                        #  2) If the absolute value of the difference between
                        #     NCEP and external station surface pressure is
                        #     greater than 15 hPa warning is thrown
                        #----------------------------------------------------
                        if (float(lines[nlnum].split()[-2].rstrip(',')) > float(oldPres)):
                            if logFile:
                                logFile.error('Surface pressure error for reference profile: ' + refFile)
                                logFile.error('External surface pressure < NCEP pressure one level above surface => Non-hydrostatic equilibrium!!')
                            print 'Surface pressure error for reference profile: ' + refFile
                            print 'External surface pressure < NCEP pressure one level above surface => Non-hydrostatic equilibrium!!'
                        elif ( abs(float(oldPres) - float(newPres)) > 15):
                            if logFile:
                                logFile.warning('Surface pressure warning for reference profile: ' + refFile)
                                logFile.warning('Difference between NCEP and external station surface pressure > 15 hPa')
                            print 'Surface pressure warning for reference profile: ' + refFile
                            print 'Difference between NCEP and external station surface pressure > 15 hPa'
                                                 
                        lines[nlnum] = lines[nlnum].replace(oldPres,newPres)
            
                if NCEPtempFlg == False:
                    if 'temper' in line.lower():
                        nlnum        = linenum + nlines
                        oldTemp      = lines[nlnum].split()[-1].rstrip(',')
                        
                        #------------------------------------------------------
                        # Compare NCEP temperature with new updated temperature
                        #  1) If updated surface temperature is less than NCEP
                        #     one level above surface throw error
                        #  2) If the absolute value of the difference between
                        #     NCEP and external station surface temperature is
                        #     greater than 10 DegC warning is thrown
                        #------------------------------------------------------
                        if (float(lines[nlnum].split()[-2].rstrip(',')) > float(oldTemp)):
                            if logFile:
                                logFile.error('Surface Temperature error for reference profile: ' + refFile)
                                logFile.error('External surface Temperature < NCEP Temperature one level above surface => Non-hydrostatic equilibrium!!')
                            print 'Surface Temperature error for reference profile: ' + refFile
                            print 'External surface temperature < NCEP temperature one level above surface => Non-hydrostatic equilibrium!!'
                        elif ( abs(float(oldTemp) - float(newTemp)) > 10):
                            if logFile:
                                logFile.warning('Surface temperature warning for reference profile: ' + refFile)
                                logFile.warning('Difference between NCEP and external station surface temperature > 10 DegC')
                            print 'Surface temperature warning for reference profile: ' + refFile
                            print 'Difference between NCEP and external station surface temperature > 10 DegC'                        
  
                        lines[nlnum] = lines[nlnum].replace(oldTemp,newTemp)                    
                              
            
    with open( refFile, 'w' ) as fout:
        for line in lines:
            fout.write(line)
      
    return True    

 
                        #-------------------------#
                        #                         #
                        #    -- t15ascPrep --     #
                        #                         #
                        #-------------------------#    
    
# Copy bnr file to output folder
def t15ascPrep(dbFltData_2, wrkInputDir2, wrkOutputDir5, mainInF, spcDBind, ctl_ind, logFile):
    
    bnrFname = "{0:06}".format(int(dbFltData_2['TStamp'][spcDBind])) + '.bnr'
    
    if not os.path.isfile(wrkOutputDir5+bnrFname):
        try:
            shutil.copy( wrkInputDir2 + bnrFname, wrkOutputDir5 )
        except IOError as errmsg:
            print errmsg
            if logFile: logFile.error(errmsg)
            sys.exit()                    
    
    #--------------------------------------
    # Create pspec.input file for pspec.f90
    #--------------------------------------    
    with open(wrkOutputDir5 + 'pspec.input', 'w') as fname:
        
        # Write header information
        fname.write('# Input file for pspec.f90\n')
        fname.write('# Latitude of Observation [+N, 90 - -90]\n')
        fname.write( str(dbFltData_2['N_Lat'][spcDBind]) + '\n' )
        fname.write('# Longitude of Observation[+E, 0 - 360]\n')
        fname.write( str(dbFltData_2['W_Lon'][spcDBind]) + '\n')
        fname.write('# Altitude of Observation [masl]\n')
        fname.write( str(dbFltData_2['Alt'][spcDBind]) + '\n')
        fname.write('# filter bands and regions for calculating SNR\n')
        fname.write( mainInF.inputs['fltrBndInputs'] )
        fname.write('# number of data blocks in the output ascii file\n')
        fname.write( str(mainInF.inputs['numDataBlks']) + '\n')
        fname.write('# Specify data block (Each block contains at least 2 lines):\n')
        fname.write('# bnr file name\n')
        fname.write('# Radius of Earth (ROE), zero fill factor (nterp), ratioflg (rflag), file open flag (fflag)\n')
        fname.write('# roe - radius of earth [km]\n')
        fname.write('# nterp -  zero fill factor\n')
        fname.write('#     nterp =  0 - skip resample & resolution degradation\n')
        fname.write('#     nterp =  1 - minimally sample at opdmax\n')
        fname.write('#     nterp >  1 - interpolate nterp-1 points upon minimal sampled spacing\n')
        fname.write('#     note: OPDMAX is taken from sfit4.ctl file\n')
        fname.write('# rflag - ratio flag, to ratio the spectra with another low resolution spectral file (eg spectral envelope)\n')
        fname.write('# fflag -  file open flag\n')
        fname.write('#     fflag = 0 for fortran unformatted file\n')
        fname.write('#     fflag = 1 for open as steam or binary or c-type file (gfortran uses stream)\n')
        fname.write('# ratio file name in bnr format\n')
        fname.write('#     if rflag eq 1 this file has to exist\n')
        fname.write('#     skip if rflag eq 0 \n')
        fname.write( bnrFname + '\n') 
        fname.write( str(dbFltData_2['ROE'][spcDBind])          + '   '   +           # ROE
                     str(mainInF.inputs['ctlList'][ctl_ind][1]) + '     ' +           # Zero Fill factor
                     str(mainInF.inputs['ctlList'][ctl_ind][2]) + '     ' +           # Ratio flag
                     str(mainInF.inputs['ctlList'][ctl_ind][3]) +'\n' )               # File open flag
        if mainInF.inputs['ctlList'][ctl_ind][2]:
            fname.write( mainInF.inputs['ctlList'][ctl_ind][4] + '\n' )
        else:
            fname.write('#\n')
    
    #------------------------------
    # Change working directory to 
    # output directory to run pspec
    #------------------------------
    try:
        os.chdir(wrkOutputDir5)
    except OSError as errmsg:
        if logFile: logFile.error(errmsg)
        sys.exit()

        
    #--------------
    # Call to pspec
    #--------------
    print 'Running pspec for ctl file: ' + mainInF.inputs['ctlList'][ctl_ind][0] 
    sc.subProcRun( [mainInF.inputs['binDir'] + 'pspec'] )           # Subprocess call to run pspec

    #if ( stderr is None or not stderr ):
            #if log_flg:
                    #logFile.info( stdout )
                    #logFile.info('Finished running pspec\n' + stdout)
    #else:
            #print 'Error running pspec!!!'
            #if log_flg:
                    #logFile.error('Error running pspec \n' + stdout)
            #sys.exit()                                
        
        
    return True


                            #-------------------------#
                            #                         #
                            #  -- Error Analysis --   #
                            #                         #
                            #-------------------------#    
def errAnalysis(ctlFileVars, wrkingDir, logFile=False):
    """
    Calculates systematic and random uncertainty covariance matrix 
    using output from sfit4 and sb values from ctl file
    
    Outputs:
    error_analysis.log: summary of calculated erros in %
    error_analysis.summary: summary of calculated erros in molec / cm^2
    outputs for covariance matrices are controlled by sfit4.ctl file
    options:
      total systematic uncertainty covariance matrix
      total random uncertainty covariance matrix
      all systematic uncertainty covariance matrices
      all random uncertainty covariance matrices
    
    Updates 09/07/2013
    
    1) Made changes to reconcile changes to version 2 of file read
      a) n_profile and n_column are now calculated in file_read
    2) Added vmr covariance matrix outpur
    3) Changed error summary to error log
    4) Added error summary of uncertainties in mol cm^-2
    5) Fixed size of AK_int2 and Se_int2 for case of interfering species retrieved as profile
    6) Improved outputs, allows choice of untis of covariance matrix between vmr and molec /cm 2
    
    Created Stephanie Conway (sconway@atmosp.physics.utoronto.ca)
    
    """

    #import file_read_v4 as rout
    #import read_prfs as prfs
    #import sfit4_ctl_simple as sfit4   
    #ctl = sfit4.sfit4_ctl()
    #ctl.read_ctl_file('sfit4.ctl')
    #b = sfit4.sfit4_ctl()
    #b.read_ctl_file('sb.ctl')
    
    
    #------------------------------------------------------
    # Determine number of microwindows and retrieved gasses
    #------------------------------------------------------
    n_window  = len( ctlFileVars.inputs['band'] )
    n_profile = len( ctlFileVars.inputs['gas.profile.list'] )
    n_column  = len( ctlFileVars.inputs['gas.column.list'] )
    
    #------------------------------
    # Read values from sfit4 output
    #------------------------------
    #------------------------------------------------------------------------------
    # Read in output files from sfit4 run
    #  -- k.output to calculate averaging kernel
    #  -- d.complete to calculate averaging kernel and measurement error
    #  -- sa.complete to calculate smoothing error
    #  -- summary file for the SNR to calculate the measurement error
    #  -- kb.output for non-retrieved parameter error calculation
    #  -- rprfs.table and aprfs.table for the airmass, apriori and retrieved profiles 
    #------------------------------------------------------------------------------    
    # Read in Sa matrix
    #------------------
    tryopen(wrkingDir+ctlFileVarsinputs['file.out.sa_matrix'], lines, rtnFlg, logFile)
    if not rtnFlg: sys.exit()    # Critical file, if missing terminate program    
    
    sa = np.array( [ [ float(x) for x in row.split()] for row in lines[3:] ] )
    
    #-----------------------
    # Read in SNR values
    #-----------------------    
    tryopen(wrkingDir+ctlFileVarsinputs['file.out.summary'], lines, rtnFlg, logFile) 
    if not rtnFlg: sys.exit()    # Critical file, if missing terminate program

    lstart   = [ind for ind,line in enumerate(lines) if 'IBAND' in line][0]  
    indNPTSB = lines[lstart].index('NPTSB')
    indSNR   = lines[lstart].index('CALC_SNR')
    lend     = [ind for ind,line in enumerate(lines) if 'FITRMS' in line][0] - 1
    
    calc_SNR   = []
    nptsb      = []
    
    for lnum in range(lstart+1,lend):
        nptsb.append(    float( lines[lnum].strip().split(indNPTSB) ) )
        calc_SNR.append( float( lines[lnum].strip().split(indSNR)   ) )
    
    snr        = np.zeros((sum(nptsb),sum(nptsb)), float)
    snrList    = list(itertools.chain(*[[snrVal]*npnts for snrVal,npnts in itertools.izip(calc_SNR,nptsb)]))
    snrList[:] = [val**-2 for val in snrList]
    np.fill_diagonal(snr,snrList)    
      
    #-----------------
    # Read in K matrix
    #-----------------
    tryopen(wrkingDir+ctlFileVarsinputs['file.out.k_matrix'], lines, rtnFlg, logFile) 
    if not rtnFlg: sys.exit()      # Critical file, if missing terminate program
    
    n_wav   = int( lines[1].strip().split()[0] )
    x_start = int( lines[1].strip().split()[2] )
    n_layer = int( lines[1].strip().split()[3] )
    x_stop  = x_start + n_layer
    K       = np.array([[float(x) for x in row.split()] for row in lines[3:]])

    #--------------------
    # Read in Gain matrix
    #--------------------
    tryopen(wrkingDir+ctlFileVarsinputs['file.out.gain_matrix'], lines, rtnFlg, logFile)
    if not rtnFlg: sys.exit()      # Critical file, if missing terminate program
    
    D = np.array([[float(x) for x in row.split()] for row in lines[3:]])

    #------------------
    # Read in Kb matrix
    #------------------    
    tryopen(wrkingDir+ctlFileVarsinputs['file.out.kb_matrix'], lines, rtnFlg, logFile)
    if not rtnFlg: sys.exit()      # Critical file, if missing terminate program
     
    Kb_param = lines[2].strip().split()
    Kb_unsrt = np.array([[float(x) for x in row.split()] for row in lines[3:]])
    
    #----------------------------------
    # Create a dictionary of Kb columns
    # A list of numpy arrays is created
    # for repeated keys
    #----------------------------------
    Kb = {}
    for kind,k in enumerate(Kb_param):
        Kb.setdefault(k,[]).append(Kb_unsrt[:,kind])
         
    #----------------------------------
    # Column stack multiple arrays if
    # they exist
    #----------------------------------          
    for k in Kb:
        if len(Kb[k]) == 1: Kb[k] = Kb[k][0]
        else:               Kb[k] = np.column_stack(Kb[k])
           
    #-----------------------------------------------------
    # Primary retrieved gas is assumed to be the first gas 
    # in the profile gas list. If no gases are retrieved 
    # as a profile, the primary gas is assumed to be the 
    # first gas in the column gas list.
    #-----------------------------------------------------
    if (n_profile > 0): primgas = ctlFileVarsinputs['gas.profile.list'][0]
    else:               primgas = ctlFileVarsinputs['gas.column.list'][0]
    
    #------------------------------------
    # Read in profile data of primary gas
    #------------------------------------
    pGasPrf = GasPrfs.GasPrfs( wrkingDir + ctlFileVarsinputs['file.out.retprofiles'], 
                               wrkingDir + ctlFileVarsinputs['file.out.aprprofiles'], primgas, npFlg=True, logFile=logFile)
        
    #-------------------------------------
    # Get gain matrix for the retrieved 
    # profile of the gas in questions only
    #-------------------------------------
    Dx = D[x_start:x_stop,:]
    
    #-----------------------------------------
    # Calculate the unscaled Averaging Kernel: 
    #    AK = D*K
    #-----------------------------------------
    try: AK = np.dot(D,K)
    except ValueError:
	print 'Unable to multiple Gain and K matrix '
	print 'Gain matrix shape: %s, K matrix shape: %s' %(str(D.shape),str(K.shape))
	if logFile: logFile.error('Unable to multiple Gain and K matrix; Gain matrix shape: %s, K matrix shape: %s' %(str(D.shape),str(K.shape)) ) 

    #-----------------------------------------------
    # Get unscaled Averaging Kernel for the 
    # retrieved profile of the gas in questions only
    #-----------------------------------------------
    AKx = AK[x_start:x_stop,x_start:x_stop]
    
    #------------------------------------------------------------
    # Calculate the scaled Averaging Kernel:
    # 
    #------------------------------------------------------------
    AKvmr = np.dot( np.dot( np.diag( 1.0 / pGasPrf.Aprf), AKx ), np.diag(pGasPrf.Aprf) )
    
    #----------------------------------
    # Calculate retrieved total column:
    #
    #----------------------------------
    retdenscol = np.dot( pGasPrf.Rprf, pGasPrf.Airmass )  
    
    #------------------------------------
    # Calculate A priori density profile:
    #
    #------------------------------------
    aprdensprf = pGasPrf.Aprf * pGasPrf.Airmass
    
    #---------------------------
    # Determine DOFS for column:
    #
    #---------------------------
    col_dofs = np.trace(AKx)
    
    #-----------------------
    # List of all parameters 
    #-----------------------
    Kb_labels = ['temperature','solshft','solstrnth','phase','wshift','dwshift','sza','lineInt','lineTAir','linePAir','slope','curvature','apod_fcn','phase_fcn','omega','max_opd','zshift']
    
    #------------------------------------------------------------
    # Initialize dictionary of all calculated random error data,
    # including: convariance matrices, percent errors, and labels
    #------------------------------------------------------------
    S_ran = {}
    
    #---------------------------------------------------------------
    # Initialize dictionary of all calculated systematic error data,
    # including: convariance matrices, percent errors, and labels
    #---------------------------------------------------------------
    S_sys = {}
       
    #---------------------------------
    # Calculate Smoothing error
    #                               T
    #      Serr = (A-I) * Sa * (A-I)
    #---------------------------------
    #S_sys, S_ran are lists of 4tuples: cov in sfit units, cov in pc units, tot col std, error name
    S_tmp     = np.dot( np.dot( ( AKvmr - np.identity(AKvmr.shape[0]) ), sa[x_start:x_stop,x_start:x_stop] ),(AKvmr - np.identity(AKvmr.shape[0]) ).T )
    S_err_tmp = np.sqrt( np.dot( np.dot( aprdensprf, S_tmp ),aprdensprf.T ) )
    S_tmp2    = np.dot( np.dot( np.diag(aprdensprf), S_tmp ), np.diag(aprdensprf) )
    S_ran['smoothing'] = (S_tmp, S_err_tmp, S_tmp2)
	
	
    # Otherwise calculate from Rogers: Ss=(A-I)*Sa*(A-I)T
    S_tmp = np.dot(np.dot((AKvmr - np.identity(AKvmr.shape[0])),a.sa[a.x_start:a.x_stop,a.x_start:a.x_stop]),(AKvmr - np.identity(AKvmr.shape[0])).T)
    S_err_tmp = np.sqrt(np.dot(np.dot(aprdensprf,S_tmp),aprdensprf.T))
    S_tmp = np.dot(np.dot(np.diag(r.aprf),S_tmp),np.diag(r.aprf))
    S_tmp2 = np.dot(np.dot(np.diag(r.airmass),S_tmp),np.diag(r.airmass))
    
    S_sys.append((S_tmp,S_tmp2,S_err_tmp,'smoothing'))
    
    # Calculate Measurement error using SNR calculated from the spectrum
    
    # Calculate from Rogers: Sm = Dx * Sm * Dx.T
    S_tmp = np.dot(np.dot(Dx,a.se),Dx.T)
    S_err_tmp = np.sqrt(np.dot(np.dot(aprdensprf,S_tmp),aprdensprf.T))
    S_tmp = np.dot(np.dot(np.diag(r.aprf),S_tmp),np.diag(r.aprf))
    S_tmp2 = np.dot(np.dot(np.diag(r.airmass),S_tmp),np.diag(r.airmass))
    
    S_ran.append((S_tmp,S_tmp2,S_err_tmp,'measurement'))
    logger.info('%s     %.4E\n'%('Column amount = ', retdenscol))
    logger.info('%s     %f\n'%('DOFS (total column) = ', col_dofs))
    logger.info('%s     %f\n'%('Sm (%) = ', (S_ran[0][2]/retdenscol)*100))
    logger.info('%s     %f\n'%('Ss (%) = ', (S_sys[0][2]/retdenscol)*100))
    
    # Interference error 1 - retrieval parameters
    AK_int1 = AK[a.x_start:a.x_stop,0:a.x_start]  # Per Bavo
    Se_int1 =  a.sa[0:a.x_start,0:a.x_start]
      
    S_tmp = np.dot(np.dot(AK_int1,Se_int1),AK_int1.T)
    S_err_tmp = np.sqrt(np.dot(np.dot(aprdensprf,S_tmp),aprdensprf.T)) 
    S_tmp = np.dot(np.dot(np.diag(r.aprf),S_tmp),np.diag(r.aprf))
    S_tmp2 = np.dot(np.dot(np.diag(r.airmass),S_tmp),np.diag(r.airmass))
    
    logger.info('%s     %f\n'%('Sint1_random (retrieval params) (%) = ', S_err_tmp/retdenscol*100))
    
    S_ran.append((S_tmp,S_tmp2,S_err_tmp,'retrieval parameters'))    
    
    # Interference error 2 - interfering species
    
    n_int2 = a.n_profile + a.n_column - 1
    n_int2_column = (a.n_profile-1)*a.n_layer + a.n_column
    
    AK_int2 = AK[a.x_start:a.x_stop,a.x_stop:a.x_stop+n_int2_column] # Per Bavo
    
    Se_int2 = a.sa[a.x_stop:a.x_stop+n_int2_column,a.x_stop:a.x_stop+n_int2_column]
    
    S_tmp = np.dot(np.dot(AK_int2,Se_int2),AK_int2.T)
    S_err_tmp = np.sqrt(np.dot(np.dot(aprdensprf,S_tmp),aprdensprf.T))
    S_tmp = np.dot(np.dot(np.diag(r.aprf),S_tmp),np.diag(r.aprf))
    S_tmp2 = np.dot(np.dot(np.diag(r.airmass),S_tmp),np.diag(r.airmass))
    
    S_ran.append((S_tmp,S_tmp2,S_err_tmp,'interfering species'))
    
    logger.info('%s     %f\n'%('Sint2_random (intf. spec.) (%) = ', (S_err_tmp/retdenscol)*100))
    
    # Errors from parameters not retrieved by Sfit4
    
    zerolev_band_b = [];
    for k in ctl.value['band'].strip().split():
      if (ctl.value['band.'+k+'.zshift'].strip() == 'F'):  # only include bands where zshift is retrieved
	zerolev_band_b.append(k)
    
    for s in Kb_labels:
      Kb_exists = True
      try:
	DK = np.dot(Dx,a.Kb[s])
      except KeyError, e:
	Kb_exists = False
      
      if (Kb_exists):
	for k in ['random', 'systematic']:
    #      print s
	  try:
	    if (s == 'zshift'):    
	      Sb = np.zeros((len(zerolev_band_b),len(zerolev_band_b)))
	      for i in range(0,len(zerolev_band_b)):
		Sb[i,i] = float( b.value['sb.band.'+zerolev_band_b[i]+'.zshift.'+k])**2
	    elif (DK.shape[1] == 1):
	      Sb = np.zeros((1,1))
	      Sb[0,0] = float(b.value['sb.'+s+'.'+k])**2
	    elif (DK.shape[1] == a.n_window):
	      Sb = np.dot(float(b.value['sb.'+s+'.'+k])**2,np.identity(a.n_window))
	    elif (DK.shape[1] == a.n_layer):  # Only the temperature error fits this requirement
	      temp_sb = b.value['sb.temperature.'+k].strip().split()
	      Sb = np.zeros((a.n_layer,a.n_layer))
	      for j in range(0, len(temp_sb)):
		Sb[j,j] = (float(temp_sb[j])/r.T[j])**2  # convert degrees to relative units
	      del temp_sb
	    else:
	       Sb = 0
	  except KeyError, e:
	    Sb = 0
	  if np.sum(Sb) == 0:
	    if (s == 'zshift'):
	      logger.info('%s\n'%('sb.band.x.'+s+'.'+k+' for all bands where zshift is not retrieved is 0 or is not specified, error covariance matrix not calculated'))
	    else:
	      logger.info('%s\n'%('sb.'+s+'.'+k+' for '+s+' is 0 or is not specified, error covariance matrix not calculated'))
	  else:
	    S_tmp = np.dot(np.dot(DK,Sb),DK.T)
	    S_err_tmp = np.sqrt(np.dot(np.dot(aprdensprf,S_tmp),aprdensprf.T))
	    S_tmp = np.dot(np.dot(np.diag(r.aprf),S_tmp),np.diag(r.aprf))
	    S_tmp2 = np.dot(np.dot(np.diag(r.airmass),S_tmp),np.diag(r.airmass))
	    logger.info('%s     %f\n'%('S.'+s+'.'+k+' (%) =', (S_err_tmp/retdenscol)*100))
    
	    if (k == 'random'):
	      S_ran.append((S_tmp,S_tmp2,S_err_tmp,s))
    
	    if (k == 'systematic'):
	      S_sys.append((S_tmp,S_tmp2,S_err_tmp,s))
    
    S_random_err = 0
    S_random = np.zeros((a.n_layer,a.n_layer))
    S_random_vmr = np.zeros((a.n_layer,a.n_layer))
    
    for k in range(0,len(S_ran)):
      S_random_err += S_ran[k][2]**2
      S_random_vmr += S_ran[k][0]
      S_random += S_ran[k][1]
    S_random_err = np.sqrt(S_random_err)
    
    logger.info('%s     %f\n'%('Total random error (%) = ', (S_random_err/retdenscol)*100))
    
    S_systematic_err = 0
    S_systematic =  np.zeros((a.n_layer,a.n_layer))
    S_systematic_vmr =  np.zeros((a.n_layer,a.n_layer))
    
    for k in range(1,len(S_sys)):
      S_systematic_err += S_sys[k][2]**2
      S_systematic_vmr += S_sys[k][0]
      S_systematic += S_sys[k][1]
    S_systematic_err = np.sqrt(S_systematic_err)
    logger.info('%s     %f\n'%('Total systematic error (%) = ', (S_systematic_err/retdenscol)*100))
    
    logger.info('%s     %f\n'%('Total error exclusive of smoothing error (%) = ',np.sqrt(S_systematic_err**2 + S_random_err**2)/retdenscol*100))
    
    try:
      filename = b.value['file.out.error.summary']
    except KeyError, e:
      filename = 'error_analysis.summary'
    
    with open(filename, 'w') as fout:
      fout.write(a.header + 'ERROR SUMMARY\n\n')
      fout.write('  %s  %.4e\n'%('Total random uncertainty in mol cm^-2 :', S_random_err))
      fout.write('  %s  %.4e\n'%('Total systematic uncertainty in mol cm^-2 :', S_systematic_err))
      for k in range(0, len(S_ran)):
	fout.write('  %s%s %s  %.4e\n'%(S_ran[k][3][0].upper(),S_ran[k][3][1:],'random uncertainty in mol cm^-2 :', S_ran[k][2]))
      for k in range(0, len(S_sys)):
	fout.write('  %s%s %s  %.4e\n'%(S_sys[k][3][0].upper(),S_sys[k][3][1:],'systematic uncertainty in mol cm^-2 :', S_sys[k][2]))
    
    # Output Covariance matrices in mol/cm^2
    
    try:
      output = b.value['out.ssystematic'].strip()
    except KeyError, e:
      output = False
    
    if (output == 'T'):
      try:
	filename = b.value['file.out.ssystematic']
      except KeyError, e:
	filename = 'ssystematic.output'
    
      with open(filename, 'w') as fout:
	fout.write(a.header + 'SYSTEMATIC ERROR COVARIANCE MATRIX IN MOL CM^-2\n')
	fout.write('          ' + str(S_systematic.shape[0]) + '          ' + str(S_systematic.shape[1]) +'\n')
	for row in  S_systematic:
	  fout.write(' %s \n' % '  '.join('% .18E' % i for i in row))
    
    try:
      output = b.value['out.srandom'].strip()
    except KeyError, e:
      output = False
    if (output == 'T'):
    
      try:
	filename = b.value['file.out.srandom']
      except KeyError, e:
	filename = 'srandom.output'
    
      with open(filename, 'w') as fout: 
	fout.write(a.header + 'RANDOM ERROR COVARIANCE MATRIX IN MOL CM^-2\n')
	fout.write('          ' + str(S_random.shape[0]) + '          ' + str(S_random.shape[1])+'\n')
	for row in S_random:
	  fout.write(' %s \n' % '  '.join('% .18E' % i for i in row))
    
    try:
      output = b.value['out.srandom.all'].strip()
    except KeyError, e:
      output = False
    
    if (output == 'T'):
    
      try:
	filename = b.value['file.out.srandom.all']
      except KeyError, e:
	filename = 'srandom.all.output'
    
      with open(filename, 'w') as fout:
	fout.write(a.header + 'RANDOM ERROR COVARIANCE MATRICES IN MOL CM^-2\n')
	fout.write('          ' + str(S_ran[0][1].shape[0]) + '          ' + str(S_ran[0][1].shape[1])+'\n')
	fout.write('\n')
	for k in range(0, len(S_ran)):
	  fout.write('  '+S_ran[k][3].upper()+' ERROR COVARIANCE MATRIX IN MOL CM^-2\n')
	  for row in  S_ran[k][1]:
	    fout.write(' %s \n' % '  '.join('% .18E' % i for i in row))
	  fout.write('\n')
	  fout.write('\n')
    
    try:
      output = b.value['out.ssystematic.all'].strip()
    except KeyError, e:
      output = False
    
    if (output == 'T'): 
      try:
	filename = b.value['file.out.ssytematic.all'].strip()
      except KeyError, e:
	filename = 'ssystematic.all.output'
    
      with open(filename, 'w') as fout:
	fout.write(a.header + 'SYSTEMATIC ERROR COVARIANCE MATRICES IN MOL CM^-2\n')
	fout.write('          ' + str(S_sys[0][1].shape[0]) + '          ' + str(S_sys[0][1].shape[1])+'\n')
	fout.write('\n')
	for k in range(0, len(S_sys)):
	  fout.write('  '+S_sys[k][3].upper()+' ERROR COVARIANCE MATRIX IN MOL CM^-2\n')
	  for row in  S_sys[k][1]:
	    fout.write(' %s \n' % '  '.join('% .18E' % i for i in row))
	  fout.write('\n')
	  fout.write('\n')
    
    # Output Covariance matrices in vmr
    
    try:
      output = b.value['out.ssystematic.vmr'].strip()
    except KeyError, e:
      output = False
    
    if (output == 'T'):
      try:
	filename = b.value['file.out.ssystematic.vmr']
      except KeyError, e:
	filename = 'ssystematic.vmr.output'
    
      with open(filename, 'w') as fout:
	fout.write(a.header + 'SYSTEMATIC ERROR COVARIANCE MATRIX IN VMR UNITS\n')
	fout.write('          ' + str(S_systematic_vmr.shape[0]) + '          ' + str(S_systematic_vmr.shape[1]) +'\n')
	for row in  S_systematic_vmr:
	  fout.write(' %s \n' % '  '.join('% .18E' % i for i in row))
    
    try:
      output = b.value['out.srandom.vmr'].strip()
    except KeyError, e:
      output = False
    if (output == 'T'):
    
      try:
	filename = b.value['file.out.srandom.vmr']
      except KeyError, e:
	filename = 'srandom.vmr.output'
    
      with open(filename, 'w') as fout: 
	fout.write(a.header + 'RANDOM ERROR COVARIANCE MATRIX IN VMR UNITS \n')
	fout.write('          ' + str(S_random_vmr.shape[0]) + '          ' + str(S_random_vmr.shape[1])+'\n')
	for row in S_random_vmr:
	  fout.write(' %s \n' % '  '.join('% .18E' % i for i in row))
    
    try:
      output = b.value['out.srandom.vmr.all'].strip()
    except KeyError, e:
      output = False
    if (output == 'T'):
    
      try:
	filename = b.value['file.out.srandom.vmr.all']
      except KeyError, e:
	filename = 'srandom.vmr.all.output'
      with open(filename, 'w') as fout:
	fout.write(a.header + 'RANDOM ERROR COVARIANCE MATRICES IN VMR UNITS \n')
	fout.write('          ' + str(S_ran[0][0].shape[0]) + '          ' + str(S_ran[0][0].shape[1])+'\n')
	fout.write('\n')
	for k in range(0, len(S_ran)):
	  fout.write('  '+S_ran[k][3].upper()+' ERROR COVARIANCE MATRIX IN VMR UNITS \n')
	  for row in S_ran[k][0]:
	    fout.write(' %s \n' % '  '.join('% .18E' % i for i in row))
	  fout.write('\n')
	  fout.write('\n')
    
    try:
      output = b.value['out.ssystematic.vmr.all'].strip()
    except KeyError, e:
      output = False
    
    if (output == 'T'): 
      try:
	filename = b.value['file.out.ssytematic.vmr.all'].strip()
      except KeyError, e:
	filename = 'ssystematic.vmr.all.output'
    
      with open(filename, 'w') as fout:
	fout.write(a.header + 'SYSTEMATIC ERROR COVARIANCE MATRICES IN VMR UNITS \n')
	fout.write('          ' + str(S_sys[0][0].shape[0]) + '          ' + str(S_sys[0][0].shape[1])+'\n')
	fout.write('\n')
	for k in range(0, len(S_sys_vmr)):
	  fout.write('  '+S_sys[k][3].upper()+' ERROR COVARIANCE MATRIX IN VMR UNITS \n')
	  for row in  S_sys[k][0]:
	    fout.write(' %s \n' % '  '.join('% .18E' % i for i in row))
	  fout.write('\n')
	  fout.write('\n')
