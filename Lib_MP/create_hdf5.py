#!/usr/bin/python

import sys
sys.path.append('/data/sfit-processing-environment/Lib_MP')

import os, string, pdb, sys
import tables as hdf5
import numpy as np
import matplotlib.dates as mdt
import datetime as dt
import read_result_sfit4 as sfit4
import read_misc

def create_hdf5(sb_ctl, direc, start_date, end_date):
	
	filename = direc+'/'+'tmp.h5'
#	filename = direc+'/'+site+'_'+target+'_'+str(end_date)+'_tmp.h5'

	if not os.path.isfile(sb_ctl):
	    print 'SB %s control file not found'%sb_ctl
	    return
	dirs = os.listdir(direc)
	dirs = filter(lambda x: os.path.isdir(direc+'/'+x) and end_date > dt.date(int(x[0:4]),int(x[4:6]),int(x[6:8])) > start_date, dirs)
	if dirs == []:
		print 'no matching results found in '+direc
		return
	dirs.sort()
	
	h5file = hdf5.openFile(filename, mode = "w", title = "sfit4 results")
	
	df = mdt.strpdate2num('%Y%m%d.%H%M%S')
	dnum = []
	sza = []
	azi = []
	lat = []
	lon = []
	alt = []
	dur = []
	spectra = []
	p_surface = []
	t_surface = []
	h_surface = []
	dir = []
	col_h2o_rt = []
	col_h2o_ap = []
	vmr_rt = []
	vmr_ap = []
	snr_clc = []
	snr_the = []
	chi_2_y = []
	dofs = []
	iter = []
	itmx = []
	
	nr_entries = len(dirs)
	akt_entry = 0
	nr_ak = 0
	nr_prf = 0
	nr_res = 0
	
	mdate = []

	for dd in dirs:
	    print dd
	    # Essential quantities fist
	    sumfile =  string.join([direc, '/', dd, '/', 'summary'], '')
	    if not os.path.isfile(sumfile):
	        print 'No summary file'
	        continue
	    rprfsfile =  string.join([direc, '/', dd, '/', 'rprfs.table'], '')
	    if not os.path.isfile(rprfsfile):
	        print 'rprfs.table'
	        continue
	    aprfsfile =  string.join([direc, '/', dd, '/', 'aprfs.table'], '')
	    if not os.path.isfile(aprfsfile):
	        print 'aprfs.table'
	        continue
	    miscfile =  string.join([direc, '/', dd, '/', 'misc.out'], '')
	    if not os.path.isfile(miscfile):
	        sz = -1
	        ze = -1
	        lat = -1
	        lon = -1
	        alt = -1
	        du = -1
	        spectrum = 'NA'
	    else:
	        mt,du,sz,az,lati,long,alti,spectrum,pth = read_misc.read_misc(miscfile)
	        sz = np.double(sz)
	        az = np.double(az)
	        lati = np.double(lati)
	        long = np.double(long)
	        alti = np.double(alti)
	        du = np.double(du)
		pth = np.array(np.double(pth))
	    try:
	        summary = sfit4.summary(sumfile)
	    except:
	        print 'summary file not readable'
	        continue

	    flag_h2o = False
	    rprf = sfit4.read_table(rprfsfile)    
	    aprf = sfit4.read_table(aprfsfile)    
	    gasnames = rprf.get_retrieval_gasnames()
	    rvmr,z = rprf.get_gas_vmr(gasnames[0])
	    avmr = aprf.get_gas_vmr(gasnames[0])
	    rcol = rprf.get_gas_col(gasnames[0])
	    acol = aprf.get_gas_col(gasnames[0])
	    len_vmr = len(z)
	
	    nr_gas = len(gasnames)
	    i_rvmr=np.zeros((len_vmr,0))
	    i_col = []
	    for gas in gasnames[1:]:
	        vmr,z = rprf.get_gas_vmr(gas)
	        i_rvmr = np.hstack((i_rvmr, np.reshape(vmr, (len_vmr,1))))
	        col,z = rprf.get_gas_col(gas)
	        i_col.append(sum(col))
	    i_col = np.array(i_col)

	    z,zb,p,t,ac = rprf.get_atmosphere()
	
	    err = sfit4.error(sb_ctl,direc+'/'+dd)
	    srvmr, ssvmr = err.read_total_vmr()
	    srpcol, sspcol = err.read_total_pcol()

	    err_flag = err.flag
	    if not err.flag:
		 print 'No Error matrices'

	    if err_flag:
		    cov_srvmr = err.S_vmr_ran;
		    cov_ssvmr = err.S_vmr_sys;
	    else:
		    cov_srvmr = ones((len_vmr, len_vmr))*-1
		    cov_ssvmr = ones((len_vmr, len_vmr))*-1
		    srpcol = ones((len_vmr))*-1
		    sspcol = ones((len_vmr))*-1

	    if akt_entry == 0:
	        col_rt = np.zeros((nr_gas, nr_entries)) *np.nan
	        col_ap = np.zeros((nr_gas, nr_entries)) *np.nan
	        col_ran = np.zeros(nr_entries) *np.nan
	        col_sys = np.zeros(nr_entries) *np.nan
	        chi_2_y = np.zeros(nr_entries) *np.nan
	        dofs = np.zeros(nr_entries) *np.nan
	        air_col=np.zeros(nr_entries) * np.nan
	        P = np.zeros((len_vmr, nr_entries)) *np.nan
	        T = np.zeros((len_vmr, nr_entries)) *np.nan
		vmr_h2o_ap = np.zeros((len_vmr, nr_entries)) *np.nan

	        h5file.createArray("/", 'Z', np.array(z), "Altitude levels (mid points)")
	        h5file.createArray("/", 'Zb', np.array(zb), "Altitude levels (boundaries)")
	        vmr_rt = h5file.createEArray("/", 'vmr_rt', hdf5.Float32Atom(), 
	                                     (len_vmr,0), title="Retrieved VMR", expectedrows=nr_entries)
	        ivmr_rt = h5file.createEArray("/", 'ivmr_rt', hdf5.Float32Atom(), 
	                                     (len_vmr,nr_gas-1,0), title="Retrieved VMR of interfering gases", 
	                                      expectedrows=nr_entries)
	        icol_rt = h5file.createEArray("/", 'icol_rt', hdf5.Float32Atom(), 
	                                     (nr_gas-1,0), title="Retrieved total column of interfering gases", 
	                                      expectedrows=nr_entries)
	        vmr_ap = h5file.createEArray("/", 'vmr_ap', hdf5.Float32Atom(), 
	                                     (len_vmr,0), title="Apriori VMR", expectedrows=nr_entries)
	        vmr_ran = h5file.createEArray("/", 'cov_vmr_ran', hdf5.Float32Atom(), 
	                                     (len_vmr,len_vmr,0), title="Total error random VMR", expectedrows=nr_entries)
	        vmr_sys = h5file.createEArray("/", 'cov_vmr_sys', hdf5.Float32Atom(), 
	                                     (len_vmr,len_vmr,0), title="Total error systematic VMR", expectedrows=nr_entries)
	        pcol_rt = h5file.createEArray("/", 'pcol_rt', hdf5.Float32Atom(), 
	                                     (len_vmr,0), title="Retrieved Partial Columns", expectedrows=nr_entries)
	        pcol_ap = h5file.createEArray("/", 'pcol_ap', hdf5.Float32Atom(), 
	                                     (len_vmr,0), title="Apriori Partial Columns", expectedrows=nr_entries)
	        pcol_ran = h5file.createEArray("/", 'pcol_ran', hdf5.Float32Atom(), 
	                                     (len_vmr,0), title="Total error random partial column", expectedrows=nr_entries)
	        pcol_sys = h5file.createEArray("/", 'pcol_sys', hdf5.Float32Atom(), 
	                                     (len_vmr,0), title="Total error systematic partial column", expectedrows=nr_entries)
	        h2o_setup = h5file.createEArray("/", 'h2o_vmr_setup', hdf5.Float32Atom(), 
	                                     (len_vmr,0), title="H2O VMR profile of setup", expectedrows=nr_entries)
	        
	        P = h5file.createEArray("/", 'P', hdf5.Float32Atom(), 
	                                (len_vmr,0), title="Pressure", expectedrows=nr_entries)
	        T = h5file.createEArray("/", 'T', hdf5.Float32Atom(), 
	                                (len_vmr,0), title="Temperature", expectedrows=nr_entries)
	
	    akt_entry = akt_entry + 1
	    if (~np.isfinite(summary.retriev[0])) :
		print 'not finite'
	        continue
	
	    akfile =  string.join([direc, '/', dd, '/', 'ak.out'], '')
	    if not os.path.isfile(akfile):
		print 'no avk'
	        continue
	    ak = sfit4.avk(akfile,aprfsfile)
	    avk = ak.avk()
	    avk_col = ak.avk(type='column')
	    avk_vmr = ak.avk(type='vmr')

	    try:
	        chi_2_y[nr_res] = summary.chi_y_2
	    except:
		print 'no chi_2_y'
	        continue
	
	    print 'akzepted'
	    col_rt[:,nr_res] = summary.retriev
	    col_ap[:,nr_res] = summary.apriori
	    air_col[nr_res] = ac
	    snr_clc.append(np.mean(summary.snr_ret))
	    snr_the.append(np.mean(summary.snr_apr))
	    dofs[nr_res] = summary.dofs
	    iter.append(summary.iter)
	    itmx.append(summary.iter_max)
	    dir.append(dd)
	
	    mdate.append(df(dd))
	    sza = np.hstack((sza,sz))
	    azi = np.hstack((azi,az))
	    lat = np.hstack((lat, lati))
	    lon = np.hstack((lon, long))
	    alt = np.hstack((alt,alti))
	    dur = np.hstack((dur, du))
	    spectra.extend(spectrum)
	    p_surface.append(pth[0])
	    if np.double(pth[0]) > 500.0:
		    p_surface.append(pth[0])
	    else:
		    p_surface.append(-90000)

	    if pth[1] > 90:
		    t_surface.append(-90000)
	    else:
		    t_surface.append(pth[1] + 273.15) 

	    if np.double(pth[2]) > 0.0:
		    h_surface.append(pth[2])
	    else:
		    h_surface.append(np.double(-90000))
	
	    vmr_rt.append(np.reshape(rvmr,(len_vmr,-1)))
	    ivmr_rt.append(np.reshape(i_rvmr, (len_vmr, nr_gas-1, 1)))
	    icol_rt.append(np.reshape(i_col, (nr_gas-1, 1)))
	    vmr_ap.append(np.reshape(avmr[0],(len_vmr, -1)))
	    if np.isfinite(srvmr).all() and np.isfinite(srpcol).all():
	        vmr_ran.append(np.reshape(cov_srvmr,(len_vmr, len_vmr, 1)))
	        vmr_sys.append(np.reshape(cov_ssvmr,(len_vmr, len_vmr, 1)))
	        pcol_ran.append(np.reshape(srpcol,(len_vmr, -1)))
	        pcol_sys.append(np.reshape(sspcol,(len_vmr, -1)))
	        col_ran[nr_res] = np.linalg.norm(srpcol)
	        col_sys[nr_res] = np.linalg.norm(sspcol)
	    pcol_rt.append(np.reshape(rcol[0],(len_vmr, -1)))
	    pcol_ap.append(np.reshape(acol[0],(len_vmr, -1)))
	    P.append(np.reshape(p,(len_vmr, -1)))
	    T.append(np.reshape(t,(len_vmr, -1)))

	    h2o, z = aprf.get_gas_vmr('H2O')
	    h2o_setup.append(np.reshape(h2o,(len_vmr, -1)))
	    h2o, z = aprf.get_gas_col('H2O')
	    col_h2o_ap.append(np.sum(h2o))
	
	    nr_res = nr_res + 1
	    if nr_res == 1:
	        len_ak = avk.shape[0]
	        AK = h5file.createEArray("/", 'avk', hdf5.Float32Atom(), 
	                                 (len_ak,len_ak,0), title="AVK (normalised)", 
	                                 expectedrows=nr_entries)
	        AKc = h5file.createEArray("/", 'avk_col', hdf5.Float32Atom(), 
	                                 (len_ak,len_ak,0), title="AVK (column)", 
	                                 expectedrows=nr_entries)
	        AKv = h5file.createEArray("/", 'avk_vmr', hdf5.Float32Atom(), 
	                                 (len_ak,len_ak,0), title="AVK (vmr)", 
	                                 expectedrows=nr_entries)
	    AK.append(np.reshape(avk,(len_ak,len_ak,1)))
	    AKc.append(np.reshape(avk_col,(len_ak,len_ak,1)))
	    AKv.append(np.reshape(avk_vmr,(len_ak,len_ak,1)))
	
	
	col_rt = col_rt[0,0:nr_res]
	col_ap = col_ap[0,0:nr_res]
	col_ran = col_ran[0:nr_res]
	col_sys = col_sys[0:nr_res]
	air_col = air_col[0:nr_res]
	chi_2_y = chi_2_y[0:nr_res]
	dofs = dofs[0:nr_res]

	
	h5file.createArray("/", 'directories', dir, "Directories")
	h5file.createArray("/", 'spectra', spectra, "Filename of Spectrum")
	h5file.createArray("/", 'mdate', np.array(mdate), "Measurement date and time")
	h5file.createArray("/", 'sza', np.array(sza), "Solar zenith angle")
	h5file.createArray("/", 'azimuth', np.array(azi), "Solar azimuth angle")
	h5file.createArray("/", 'lat', np.array(lat), "Latitude")
	h5file.createArray("/", 'lon', np.array(lon), "Longitude")
	h5file.createArray("/", 'alt', np.array(alt), "Altitude of Instrument")
	h5file.createArray("/", 'dur', np.array(dur), "Duration of measurement")
	h5file.createArray("/", 'P_s', np.array(p_surface), "Surface Pressure")
	h5file.createArray("/", 'T_s', np.array(t_surface), "Surface temperature")
	h5file.createArray("/", 'H_s', np.array(h_surface), "Surface Humidity")
	h5file.createArray("/", 'snr_clc', np.array(snr_clc), "Calculated SNR")
	h5file.createArray("/", 'snr_the', np.array(snr_the), "Theoretically possible SNR")
	h5file.createArray("/", 'chi_2_y', np.array(chi_2_y), "CHI_2_Y")
	h5file.createArray("/", 'dofs', np.array(dofs), "DOFS (theo)")
	h5file.createArray("/", 'iter', np.array(iter), "Iteration")
	h5file.createArray("/", 'itmx', np.array(itmx), "Maximum nr of Iteration")
	h5file.createArray("/", 'col_rt', col_rt, "Retrieved columns")
	h5file.createArray("/", 'col_ap', col_ap, "A prior columns")
	h5file.createArray("/", 'col_ran', col_ran, "Column error random")
	h5file.createArray("/", 'col_sys', col_sys, "Column error systematic")
	h5file.createArray("/", 'air_col', air_col, "Retrieved AIRMASS")
	h5file.createArray("/", 'gasnames', gasnames, "Names of retrieved gases")
	h5file.createArray("/", 'h2o_col_setup', col_h2o_ap, "Columns of H2O in setup")

	h5file.close()


if __name__ == '__main__':
	
	print 'Arguments: path to sb.ctl-file (mandatory), directory containing results, start-date(yyyymmdd), end-date(yyyymmdd)'

	if len(sys.argv)==1:
		print 'path to sb.ctl is missing'
		exit()
	if len(sys.argv)>=2:
		sb_ctl = sys.argv[1]
		if not os.path.isfile(sb_ctl):
			print 'SB %s control file not found'%sb_ctl
			exit()
	if len(sys.argv)>=3:
		direc =  sys.argv[2]
	else:
		direc = '.'
	if len(sys.argv)>=4:
		start_date = dt.date(int(sys.argv[3][0:4]),int(sys.argv[3][4:6]), int(sys.argv[3][6:8]))
	else:
		start_date = dt.date(1970,01,01)
	if len(sys.argv)>=5:
		end_date = dt.date(int(sys.argv[4][0:4]),int(sys.argv[4][4:6]), int(sys.argv[4][6:8]))
	else:
		end_date = dt.date.today ()

	create_hdf5(sb_ctl, direc, start_date, end_date)

##################

# col_rt = col_rt[:,np.isfinite(col_rt[0,:])]
# col_ap = col_ap[:,np.isfinite(col_ap[0,:])]
# P = col_ap[:,np.isfinite(P[0,:])]
# T = col_ap[:,np.isfinite(T[0,:])]
# h5file.createArray("/", 'P', P, "Pressure")
# h5file.createArray("/", 'T', T, "Temperature")






# print 'Load spectra ...' 
# pbp_mw = h5file.createVLArray("/", 'pbp_mw', hdf5.Float32Atom(), "Index of the start of each MW")
# pbp_clc = h5file.createVLArray("/", 'pbp_clc', hdf5.Float32Atom(), "PBP Spectra of the final iteration")
# pbp_obs = h5file.createVLArray("/", 'pbp_obs', hdf5.Float32Atom(), "PBP Spectra of the Observation")
# pbp_nu = h5file.createVLArray("/", 'pbp_nu', hdf5.Float32Atom(), "Frequency grid")
 
# for pbpfile in pbpfile_list:
#     b = read_pbpfile.pbp(pbpfile)
#     nu = np.hstack((b.nu[:]))
#     clc = np.hstack((b.clc[:]))
#     obs = np.hstack((b.obs[:]))
#     mw = [0]
#     for n in range(1,len(b.nu)):
#         mw.append(b.nu[n].shape[0]+mw[n-1])
#     pbp_mw.append(np.array(mw))
#     pbp_nu.append(nu)
#     pbp_clc.append(clc)
#     pbp_obs.append(obs)

    
