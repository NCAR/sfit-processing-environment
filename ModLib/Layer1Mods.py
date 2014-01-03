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
import printStatmnts as ps

                                #--------------------------#
                                #                          #
                                #  -- Helper functions --  #
                                #                          #
                                #--------------------------#
def tryopen(fname,logFile=False):
    try:
        with open(fname, 'r' ) as fopen:
            return fopen.readlines()
    except IOError as errmsg:
        print errmsg
        if logFile: logFile.error(errmsg)
        return False
	
    

                                #-------------------------#
                                #                         #
                                #   -- NCAR Refmaker --   #
                                #                         #
                                #-------------------------#


def refMkrNCAR(zptwPath, WACCMfile, outPath, lvl, wVer, zptFlg, specDB, spcDBind, logFile=False):
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
    if zptFlg: zptFiles = glob.glob(zptwPath + 'ZPT.nmc*')
    else     : zptFiles = glob.glob(zptwPath + 'zpt-120')
    
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
    
    if mainInF.inputs['coaddFlg']: bnrExt = '.bnrc'
    else:                          bnrExt = '.bnr'
    
    bnrFname = "{0:06}".format(int(dbFltData_2['TStamp'][spcDBind])) + bnrExt
    
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
	pWrtStr = ps.pspecInputStr()
	
	fname.writelines(pWrtStr[0:7])
        fname.write( str(dbFltData_2['N_Lat'][spcDBind]) + '\n' )
        fname.writelines(pWrtStr[7:8])
        fname.write( str(dbFltData_2['W_Lon'][spcDBind]) + '\n')
        fname.writelines(pWrtStr[8:9])
	fname.write( str(dbFltData_2['Alt'][spcDBind]) + '\n')
	fname.writelines(pWrtStr[9:19])
	fname.write('{:<5d}{:<5d}\n'.format(mainInF.inputs['outFlg'],mainInF.inputs['verbFlg']))
	fname.writelines(pWrtStr[19:24])
        fname.write( mainInF.inputs['fltrBndInputs'] )
	fname.writelines(pWrtStr[24:26])
        fname.write( str(mainInF.inputs['nBNRfiles']) + '\n')
	fname.writelines(pWrtStr[26:])
        fname.write( bnrFname + '\n') 
        fname.write( '{0:<10.1f}{1:<5d}{2:<5d}{3:<5d}{4:<5d}'.format(dbFltData_2['ROE'][spcDBind] ,          # ROE
	                                                             mainInF.inputs['nterpFlg']   ,          # nterp
	                                                             mainInF.inputs['ratioFlg']   ,          # rflag
	                                                             mainInF.inputs['fileFlg']    ,          # fflag
	                                                             mainInF.inputs['zFlg'] )        )       # zflag
	    
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
def errAnalysis(ctlFileVars, SbctlFileVars, wrkingDir, spDBdataOne, logFile=False):
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
    
    To Do List: (These are things we hope to implement in the future)
    1) Calculate errors on interfering gasses (retrieved as profile or total column)
    2) Investigate necessity of long double (128-bit) for calcCoVar
    
    
    Created Stephanie Conway (sconway@atmosp.physics.utoronto.ca)
    
    """
    
    def calcCoVar(coVar,A,aprDensPrf,retPrfVMR,VMRoutFlg, MolsoutFlg, airMass):
	''' Calculate covariance matricies in various units'''
	
	Sm   = np.dot(  np.dot( A, coVar ), A.T )                                                      # Uncertainty covariance matrix [Fractional]
	Sm_1 = np.sqrt( np.dot( np.dot( aprDensPrf, Sm ), aprDensPrf.T )     )                         # Whole column uncertainty [molecules cm^-2]
	
	if VMRoutFlg[0].upper()== 'T': Sm_2 = np.dot(  np.dot( np.diag(retPrfVMR), Sm ), np.diag(retPrfVMR) )     # Uncertainty covariance matrix [VMR]
	else:               Sm_2 = 0
	
	if MolsoutFlg[0].upper() == 'T': Sm_3 = np.dot(  np.dot( np.diag(airMass), Sm_2 ), np.diag(airMass)   )   # Uncertainty covariance matrix [molecules cm^-2]
	else:                 Sm_3 = 0
	
	return (Sm_2, Sm_3, Sm_1)
	
    def writeCoVar(fname,header,var,ind):
	''' Write covariance matricies to files'''
	with open(fname, 'w') as fout:
	    fout.write('# ' + header + '\n'                                       )
	    fout.write('# nmatr  = {}\n'.format(len(var)                         ))
	    fout.write('# nrows  = {}\n'.format(var[var.keys()[0]][0].shape[0]   ))
	    fout.write('# ncols  = {}\n\n'.format(var[var.keys()[0]][0].shape[1] )) 
	    for k in var:
		fout.write('{}\n'.format(k))
		
		for row in var[k][ind]:
		    strformat = ' '.join('{:>12.4E}' for i in row) + ' \n'
		    fout.write( strformat.format(*row) )
		
		fout.write('\n\n')    
		
		
    def paramMap(paramName,Kb_labels):
	'''There is discontinuity between the variable names used in sfit ctl file
	   and what is output in kb.output. This function helps map the kb.output
	   file variable names to what is used in ctl file. Kb_labels are the 
	   parameter names as they appear in the ctl file'''
	
	#----------------------------------
	# Split parameter name if necessary
	#----------------------------------
	if len(paramName.split('_')) == 2: paramName,gas = paramName.split('_')
	
	#--------------------------------------------------------
	# List of parameters as they appear in the Kb.output file 
	#--------------------------------------------------------
	Kb_labels_orig = ['TEMPERAT','SolLnShft','SolLnStrn','SPhsErr','IWNumShft','DWNumShft','SZA','LineInt','LineTAir','LinePAir','BckGrdSlp','BckGrdCur','EmpApdFcn','EmpPhsFnc','FOV','OPD','ZeroLev']
	
	#------------------------------------------------------
	# Find index of input paramName. If this is not matched
	# then program returns original paramName. This is for
	# kb.profile.gases
	#------------------------------------------------------
	try:               ind = Kb_labels_orig.index(paramName)
	except ValueError: return paramName
	
	if 'gas' in locals(): rtrnVal = Kb_labels[ind] + '_' + gas
	else:                 rtrnVal = Kb_labels[ind]
	
	return rtrnVal
			

    #----------------------------------------------
    # List of parameters as they appear in ctl file 
    #----------------------------------------------   
    Kb_labels = ['temperature', 'solshft','solstrnth','phase','wshift','dwshift','sza','lineInt','lineTAir','linePAir','slope','curvature','apod_fcn','phase_fcn','omega','max_opd','zshift'] 
   
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
    lines = tryopen(wrkingDir+ctlFileVars.inputs['file.out.sa_matrix'][0], logFile)
    if not lines: 
	print 'file.out.sa_matrix missing for observation, Date: ' + str(int(spDBdataOne['Date'])) + ' Time: ' + spDBdataOne['Time']
	if logFile: logFile.error('file.out.sa_matrix missing for observation, Date: ' + str(int(spDBdataOne['Date'])) + ' Time: ' + spDBdataOne['Time'])
	return False    # Critical file, if missing terminate program    
    
    sa = np.array( [ [ float(x) for x in row.split()] for row in lines[3:] ] )
    
    #---------------------------------------------------------------
    # Create Se matrix (Two ways to do this depending on input flg):
    # 1) Read SNR from summary file for each band and each scan.
    #    This value is the SNR from the T15asc file. With this option 
    #    if the user manipulates the snr values it will not be carried
    #    through to the error calculation.
    # 2) Read seinv.output matrix. With this option, if the user 
    #    manipulates snr values for the fit, these changed values 
    #    will be carried through (via seinv.output) to the error
    #    calculations.
    #---------------------------------------------------------------
    lines = tryopen(wrkingDir+ctlFileVars.inputs['file.out.summary'][0], logFile) 
    if not lines: 
	print 'file.out.summary missing for observation, Date: ' + str(int(spDBdataOne['Date'])) + ' Time: ' + spDBdataOne['Time']
	if logFile: logFile.error('file.out.summary missing for observation, Date: ' + str(int(spDBdataOne['Date'])) + ' Time: ' + spDBdataOne['Time'])
	return False    # Critical file, if missing terminate program   	

    #-----------------------------------------------------------
    # Currently set up to read SNR from summary file where the
    # summary file format has INIT_SNR on the same line as IBAND 
    #-----------------------------------------------------------
    lstart   = [ind for ind,line in enumerate(lines) if 'IBAND' in line][0]  
    indNPTSB = lines[lstart].strip().split().index('NPTSB')
    indSNR   = lines[lstart].strip().split().index('INIT_SNR') 
    lend     = [ind for ind,line in enumerate(lines) if 'FITRMS' in line][0] - 1
        
    SNR   = []
    nptsb = []
    
    for lnum in range(lstart+1,lend):
        nptsb.append( float( lines[lnum].strip().split()[indNPTSB] ) )
        SNR.append(   float( lines[lnum].strip().split()[indSNR]   ) )       
    
    se         = np.zeros((sum(nptsb),sum(nptsb)), float)

    if SbctlFileVars.inputs['SeInputFlg'][0].upper() == 'F':
	snrList    = list(it.chain(*[[snrVal]*int(npnts) for snrVal,npnts in it.izip(SNR,nptsb)]))
	snrList[:] = [val**-2 for val in snrList]
    else:
	lines      = tryopen(wrkingDir+ctlFileVars.inputs['file.out.seinv_vector'][0], logFile)
	snrList    = float( lines[2].strip().split() ) 
	snrList[:] = [1.0/val for val in snrList]
    
    np.fill_diagonal(se,snrList)    
      
    #-----------------
    # Read in K matrix
    #-----------------
    lines = tryopen(wrkingDir+ctlFileVars.inputs['file.out.k_matrix'][0], logFile) 
    if not lines: 
	print 'file.out.k_matrix missing for observation, Date: ' + str(int(spDBdataOne['Date'])) + ' Time: ' + spDBdataOne['Time']
	if logFile: logFile.error('file.out.k_matrix missing for observation, Date: ' + str(int(spDBdataOne['Date'])) + ' Time: ' + spDBdataOne['Time'])
	return False    # Critical file, if missing terminate program   
    
    n_wav   = int( lines[1].strip().split()[0] )
    x_start = int( lines[1].strip().split()[2] )
    n_layer = int( lines[1].strip().split()[3] )
    x_stop  = x_start + n_layer
    K       = np.array([[float(x) for x in row.split()] for row in lines[3:]])

    #--------------------
    # Read in Gain matrix
    #--------------------
    lines = tryopen(wrkingDir+ctlFileVars.inputs['file.out.g_matrix'][0], logFile)
    if not lines: 
	print 'file.out.g_matrix missing for observation, Date: ' + str(int(spDBdataOne['Date'])) + ' Time: ' + spDBdataOne['Time']
	if logFile: logFile.error('file.out.g_matrix missing for observation, Date: ' + str(int(spDBdataOne['Date'])) + ' Time: ' + spDBdataOne['Time'])
	return False    # Critical file, if missing terminate program   
    
    D = np.array([[float(x) for x in row.split()] for row in lines[3:]])

    #------------------
    # Read in Kb matrix
    #------------------    
    lines = tryopen(wrkingDir+ctlFileVars.inputs['file.out.kb_matrix'][0], logFile)
    if not lines: 
	print 'file.out.kb_matrix missing for observation, Date: ' + str(int(spDBdataOne['Date'])) + ' Time: ' + spDBdataOne['Time']
	if logFile: logFile.error('file.out.kb_matrix missing for observation, Date: ' + str(int(spDBdataOne['Date'])) + ' Time: ' + spDBdataOne['Time'])
	return False    # Critical file, if missing terminate program   
    
    Kb_param = lines[2].strip().split()
    #---------------------------------------------------------------
    # Some parameter names in the Kb file are appended by either 
    # micro-window or gas name. If they are appended by micro-window
    # strip this and just keep parameter name so that we may group
    # the micro-windows under one key
    #---------------------------------------------------------------
    for ind,val in enumerate(Kb_param):
	if len(val.split('_')) == 2:
	    pname,appnd = val.split('_')
	    try:               int(appnd); val = pname
	    except ValueError: pass
	Kb_param[ind] = val
				
    Kb_unsrt = np.array([[float(x) for x in row.split()] for row in lines[3:]])
    
    #----------------------------------
    # Create a dictionary of Kb columns
    # A list of numpy arrays is created
    # for repeated keys
    #----------------------------------
    Kb = {}
    for k in set(Kb_param):
	inds = [i for i, val in enumerate(Kb_param) if val == k]
        Kb.setdefault(paramMap(k,Kb_labels),[]).append(Kb_unsrt[:,inds])
         
    #--------------------------------------
    # Un-nest numpy arrays in Kb dictionary
    #--------------------------------------
    for k in Kb: Kb[k] = Kb[k][0]   # Check this

    #-----------------------------------------------------
    # Primary retrieved gas is assumed to be the first gas 
    # in the profile gas list. If no gases are retrieved 
    # as a profile, the primary gas is assumed to be the 
    # first gas in the column gas list.
    #-----------------------------------------------------
    if (n_profile > 0): primgas = ctlFileVars.inputs['gas.profile.list'][0]
    else:               primgas = ctlFileVars.inputs['gas.column.list'][0]
    
    #------------------------------------
    # Read in profile data of primary gas
    #------------------------------------
    pGasPrf = sc.GasPrfs( wrkingDir + ctlFileVars.inputs['file.out.retprofiles'][0], 
                          wrkingDir + ctlFileVars.inputs['file.out.aprprofiles'][0], primgas, npFlg=True, logFile=logFile)
        
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
    
    #----------------------------------
    # Calculate retrieved total column:
    # molec/cm**2
    #----------------------------------
    retdenscol = np.dot( pGasPrf.Rprf, pGasPrf.Airmass )  
    
    #------------------------------------
    # Calculate A priori density profile:
    # molec/cm**2
    #------------------------------------
    aprdensprf = pGasPrf.Aprf * pGasPrf.Airmass
    
    #---------------------------
    # Determine DOFS for column:
    #
    #---------------------------
    col_dofs = np.trace(AKx)
    
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
    #      Ss = (A-I) * Sa * (A-I)
    #---------------------------------
    mat1               = sa[x_start:x_stop,x_start:x_stop]
    mat2               = AKx - np.identity( AKx.shape[0] )
    S_sys['Smoothing'] = calcCoVar(mat1,mat2,aprdensprf,pGasPrf.Aprf,SbctlFileVars.inputs['VMRoutFlg'],SbctlFileVars.inputs['MolsoutFlg'],pGasPrf.Airmass)
    
    #----------------------------------
    # Calculate Measurement error using 
    # SNR calculated from the spectrum
    #                    T
    #  Sm = Dx * Se * Dx
    #----------------------------------
    S_ran['Measurement'] = calcCoVar(se,Dx,aprdensprf,pGasPrf.Aprf,SbctlFileVars.inputs['VMRoutFlg'],SbctlFileVars.inputs['MolsoutFlg'],pGasPrf.Airmass)
 
    #---------------------
    # Interference Errors:
    #---------------------
    #------------------------
    # 1) Retrieval parameters
    #------------------------
    AK_int1                   = AK[x_start:x_stop,0:x_start]  
    Sa_int1                   = sa[0:x_start,0:x_start]
    S_ran['Retrieval_Params'] = calcCoVar(Sa_int1,AK_int1,aprdensprf,pGasPrf.Aprf,SbctlFileVars.inputs['VMRoutFlg'],SbctlFileVars.inputs['MolsoutFlg'],pGasPrf.Airmass)
    
    #-----------------------
    # 2) Interfering species
    #-----------------------
    n_int2                     = n_profile + n_column - 1
    n_int2_column              = ( n_profile - 1 ) * n_layer + n_column
    AK_int2                    = AK[x_start:x_stop, x_stop:x_stop + n_int2_column] 
    Sa_int2                    = sa[x_stop:x_stop + n_int2_column, x_stop:x_stop + n_int2_column]
    S_ran['Interfering_Specs'] = calcCoVar(Sa_int2,AK_int2,aprdensprf,pGasPrf.Aprf,SbctlFileVars.inputs['VMRoutFlg'],SbctlFileVars.inputs['MolsoutFlg'],pGasPrf.Airmass)
      
    #----------------------------------------------
    # Errors from parameters not retrieved by sfit4
    #----------------------------------------------
    #-------------------------------------------------
    # Determine which microwindows retrieve for zshift
    #-------------------------------------------------
    bands = {}
    for k in ctlFileVars.inputs['band']:
	if (ctlFileVars.inputs['band.'+str(int(k))+'.zshift'][0].upper() == 'F'): bands.setdefault('zshift',[]).append(int(k))        # only include bands where zshift is NOT retrieved
    
    #--------------------------------------------------------------------
    # Set band ordering for micro-window dependent Sb's other than zshift
    #--------------------------------------------------------------------
	bands.setdefault('other',[]).append(int(k))
	
    #-------------------------------------------------------------------
    # Get kb.profile.gas(es) list from sfit4.ctl file. These are used 
    # to calculate errors on profile of gases not retrieved as profiles.
    #-------------------------------------------------------------------
    try:             kb_profile_gas = ctlFileVars.inputs['kb.profile.gas']
    except KeyError: kb_profile_gas = []
    
    #--------------------------------
    # Loop through parameter list and
    # determine errors
    #--------------------------------
    for Kbl in Kb:
	DK = np.dot(Dx,Kb[Kbl])
	for ErrType in ['random','systematic']:

	    #-------------------------------------------
	    # Pre-allocate Sb matrix based on size of Kb
	    #-------------------------------------------
	    Sb = np.zeros((DK.shape[1],DK.shape[1]))
	    
	    try:
		#-------------------------------------------------------------------------------------
		# Get diagonal elements for Sb matricies. Some special cases require seperate handling
		#-------------------------------------------------------------------------------------
		#-------
		# Zshift
		#-------
		if Kbl.lower() == 'zshift':	
		    diagFill = np.array( [ SbctlFileVars.inputs['sb.band.'+str(x)+'.zshift.'+ErrType][0]  for x in bands['zshift'] ])
		
		#---------------------------------
		# Temperature (in case of scaling)
		#---------------------------------
		elif (Kbl.lower() == 'temperature') and (SbctlFileVars.inputs['sb.temperature.'+ErrType+'.scaled'][0].upper() == 'F'):
		    diagFill = np.array(SbctlFileVars.inputs['sb.temperature.'+ErrType])
		    if len(diagFill) != len(pGasPrf.T): raise Exception('Number of Sb for temperature does not match atmospheric layers!!')
		    diagFill = diagFill / pGasPrf.T
		    
		#------------
		# Profile Gas
		#------------
		elif Kbl.upper() in [x.upper() for x in kb_profile_gas]:
		    diagFill = np.array(SbctlFileVars.inputs['sb.profile.'+Kbl+'.'+ErrType])
		    
		#-------------------------
		# SZA (in case of scaling)
		#-------------------------
		elif (Kbl.lower() == 'sza') and (SbctlFileVars.inputs['sb.sza.'+ErrType+'.scaled'][0].upper() == 'F'):
		    diagFill = np.array(SbctlFileVars.inputs['sb.sza.'+ErrType]) / spDBdataOne['SZen']
		    
		#---------------------------------
		# Omega (FOV) (in case of scaling)
		#---------------------------------
		elif (Kbl.lower() == 'omega') and (SbctlFileVars.inputs['sb.omega.'+ErrType+'.scaled'][0].upper() == 'F'):
		    diagFill = np.array(SbctlFileVars.inputs['sb.omega.'+ErrType]) / spDBdataOne['FOV']
	    
		#----------------
		# All other cases
		#----------------
		else: 
		    #--------------------------------------------------------------------
		    # Catch errors where number of specified Sb does not match Kb columns
		    #--------------------------------------------------------------------
		    if len(SbctlFileVars.inputs['sb.'+Kbl+'.'+ErrType]) != DK.shape[1]: raise Exception('Number of specified Sb does not match number of Kb columns!! Check Sb.ctl file.')
		    diagFill = np.array(SbctlFileVars.inputs['sb.'+Kbl+'.'+ErrType]) 
		    
		#--------------------------------------
		# Fill Sb matrix with diagonal elements
		#--------------------------------------
		np.fill_diagonal(Sb,diagFill**2)
	
	    except: 
		errmsg = sys.exc_info()[1]
		print 'Problem calculating error covariance matrix for '+Kbl+': Error type -- ' + ErrType 
		print errmsg
		if logFile: logFile.error('Problem calculating error covariance matrix for '+Kbl+': Error type -- ' + ErrTypeerrmsg+'\n'+errmsg)	
		

	    #----------------------------------------------------------------------
	    # Check if Error covariance matrix has not been filled from sb.ctl file
	    #----------------------------------------------------------------------
	    if np.sum(Sb) == 0:
		if Kbl.lower() == 'zshift': 
		    print 'sb.band.x.zshift.'+ErrType+' for all bands where zshift is not retrieved is 0 or not specifed => error covariance matrix not calculated'
		    if logFile: logFile.info('sb.band.x.zshift.'+ErrType+' for all bands where zshift is not retrieved is 0 or not specifed => error covariance matrix not calculated')
		elif Kbl.upper() in [x.upper() for x in kb_profile_gas]:
		    print 'sb.profile.'+Kbl+'.'+ErrType+' is 0 or not specified => error covariance matrix not calculated'
		    if logFile: logFile.info('sb.profile.'+Kbl+'.'+ErrType+' is 0 or not specified => error covariance matrix not calculated')		    
		else:               
		    print 'sb.'+Kbl+'.'+ErrType+' is 0 or not specified => error covariance matrix not calculated'
		    if logFile: logFile.info('sb.'+Kbl+'.'+ErrType+' is 0 or not specified => error covariance matrix not calculated')
	    
	    #----------------------------
	    # Calculate
	    #----------------------------
	    else:
		if ErrType == 'random': S_ran[Kbl] = calcCoVar(Sb,DK,aprdensprf,pGasPrf.Aprf,SbctlFileVars.inputs['VMRoutFlg'],SbctlFileVars.inputs['MolsoutFlg'],pGasPrf.Airmass)
		else:                   S_sys[Kbl] = calcCoVar(Sb,DK,aprdensprf,pGasPrf.Aprf,SbctlFileVars.inputs['VMRoutFlg'],SbctlFileVars.inputs['MolsoutFlg'],pGasPrf.Airmass)
	    
    #---------------------------------------------
    # Calculate total systematic and random errors
    #---------------------------------------------
    # Initialize total random and systematic
    S_tot                = {}
    S_tot_rndm_err       = 0
    S_tot_systematic_err = 0
    
    if  SbctlFileVars.inputs['VMRoutFlg'][0].upper() == 'T': 
	S_tot_ran_vmr   = np.zeros((n_layer,n_layer))
	S_tot_sys_vmr   = np.zeros((n_layer,n_layer))
	
    if  SbctlFileVars.inputs['MolsoutFlg'][0].upper() =='T': 
	S_tot_ran_molcs = np.zeros((n_layer,n_layer))
	S_tot_sys_molcs = np.zeros((n_layer,n_layer))
    
    # Random
    for k in S_ran:
	S_tot_rndm_err  += S_ran[k][2]**2
	if  SbctlFileVars.inputs['VMRoutFlg'][0].upper()  =='T': S_tot_ran_vmr   += S_ran[k][0]
	else:						           S_tot_ran_vmr    = 0
	if  SbctlFileVars.inputs['MolsoutFlg'][0].upper() =='T': S_tot_ran_molcs += S_ran[k][1]
	else:                                                    S_tot_ran_molcs  = 0
	
    S_tot_rndm_err  = np.sqrt(S_tot_rndm_err)
    
    # Systematic
    for k in S_sys:
	S_tot_systematic_err += S_sys[k][2]**2
	if  SbctlFileVars.inputs['VMRoutFlg'][0].upper()  =='T': S_tot_sys_vmr   += S_sys[k][0]
	else:						           S_tot_sys_vmr    = 0
	if  SbctlFileVars.inputs['MolsoutFlg'][0].upper() =='T': S_tot_sys_molcs += S_sys[k][1]
	else:						           S_tot_sys_molcs  = 0 
	
    S_tot_systematic_err = np.sqrt(S_tot_systematic_err)
    S_tot['Random']      = (S_tot_ran_vmr,S_tot_ran_molcs,S_tot_rndm_err)
    S_tot['Systematic']  = (S_tot_sys_vmr,S_tot_sys_molcs,S_tot_systematic_err)
       
					#---------------#
					# Write outputs #
					#---------------#

    #--------------------------
    # Error summary information
    #--------------------------      
    with open(wrkingDir+SbctlFileVars.inputs['file.out.error.summary'][0], 'w') as fout:
	fout.write('sfit4 ERROR SUMMARY\n\n')
	fout.write('Primary gas                                   = {:>15s}\n'.format(primgas.upper())                                  )
	fout.write('Total column amount                           = {:15.5E} [molecules cm^-2]\n'.format(retdenscol)                    )
	fout.write('DOFs (total column)                           = {:15.3f}\n'.format(col_dofs)                                        )
	fout.write('Smoothing error (Ss)                          = {:15.3f} [%]\n'.format(S_sys['Smoothing'][2]        /retdenscol*100))
	fout.write('Measurement error (Sm)                        = {:15.3f} [%]\n'.format(S_ran['Measurement'][2]      /retdenscol*100))
	fout.write('Interference error (retrieved params)         = {:15.3f} [%]\n'.format(S_ran['Retrieval_Params'][2] /retdenscol*100))
	fout.write('Interference error (interfering spcs)         = {:15.3f} [%]\n'.format(S_ran['Interfering_Specs'][2]/retdenscol*100))
	fout.write('Total random error                            = {:15.3f} [%]\n'.format(S_tot['Random'][2]           /retdenscol*100))
	fout.write('Total systematic error                        = {:15.3f} [%]\n'.format(S_tot['Systematic'][2]       /retdenscol*100))
	fout.write('Total random uncertainty                      = {:15.3E} [molecules cm^-2]\n'.format(S_tot['Random'][2])            )
	fout.write('Total systematic uncertainty                  = {:15.3E} [molecules cm^-2]\n'.format(S_tot['Systematic'][2])        )
	for k in S_ran:
	    fout.write('Total random uncertainty {:<20s} = {:15.3E} [molecules cm^-2]\n'.format(k,S_ran[k][2]))
	for k in S_sys:
	    fout.write('Total systematic uncertainty {:<16s} = {:15.3E} [molecules cm^-2]\n'.format(k,S_sys[k][2])) 
        
    #-----------------------------------
    # Write to file covariance matricies
    #-----------------------------------
    if SbctlFileVars.inputs['out.total'][0].upper() == 'T':
	if SbctlFileVars.inputs['MolsoutFlg'][0].upper() == 'T':
	    # molecules cm^-2
	    fname  = wrkingDir+SbctlFileVars.inputs['file.out.total'][0]
	    header = 'TOTAL RANDOM ERROR COVARIANCE MATRIX IN MOL CM^-2'
	    writeCoVar(fname,header,S_tot,1) 
	
	if SbctlFileVars.inputs['VMRoutFlg'][0].upper() == 'T':
	    # vmr
	    fname  = wrkingDir+SbctlFileVars.inputs['file.out.total.vmr'][0]
	    header = 'TOTAL RANDOM ERROR COVARIANCE MATRICES IN VMR UNITS'
	    writeCoVar(fname,header,S_tot,0) 	

    if SbctlFileVars.inputs['out.srandom'][0].upper() == 'T':
	if SbctlFileVars.inputs['MolsoutFlg'][0].upper() == 'T':
	    # molecules cm^-2
	    fname  = wrkingDir+SbctlFileVars.inputs['file.out.srandom'][0]
	    header = 'RANDOM ERROR COVARIANCE MATRIX IN MOL CM^-2'
	    writeCoVar(fname,header,S_ran,1)
	
	if SbctlFileVars.inputs['VMRoutFlg'][0].upper() == 'T':
	    # vmr
	    fname  = wrkingDir+SbctlFileVars.inputs['file.out.srandom.vmr'][0]
	    header = 'RANDOM ERROR COVARIANCE MATRICES IN VMR UNITS'
	    writeCoVar(fname,header,S_ran,0)	
		
    if SbctlFileVars.inputs['out.ssystematic'][0].upper() == 'T':
	
	if SbctlFileVars.inputs['MolsoutFlg'][0].upper() == 'T':
	    # molecules cm^-2
	    fname  = wrkingDir+SbctlFileVars.inputs['file.out.ssystematic'][0]
	    header = 'SYSTEMATIC ERROR COVARIANCE MATRIX IN MOL CM^-2'
	    writeCoVar(fname,header,S_sys,1)
	
	if SbctlFileVars.inputs['VMRoutFlg'][0].upper() == 'T':
	    # vmr
	    fname  = wrkingDir+SbctlFileVars.inputs['file.out.ssystematic.vmr'][0]
	    header = 'SYSTEMATIC ERROR COVARIANCE MATRICES IN VMR UNITS'
	    writeCoVar(fname,header,S_sys,0)	

    #-----------------------
    # Write Averaging Kernel
    #-----------------------
    fname      = wrkingDir+SbctlFileVars.inputs['file.out.avk'][0]    
    header     = 'Averaging Kernel for '+ primgas.upper()
    AVK        = {}
    AVK['AVK'] = (AKx,[],[])
    writeCoVar(fname,header,AVK,0)
    
    
    return True

