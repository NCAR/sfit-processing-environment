#!/usr/bin/python

import os, string, pdb, sys
import tables as hdf5
import numpy as np
import matplotlib.dates as mdt
import datetime as dt
import read_result_sfit4 as sfit4
from read_result_sfit4 import sfit4_ctl
import read_misc

def create_hdf5(**kwargs):
        


        if not 'sbctl' in kwargs:
                print ('Please provide the path to the sb.ctl (sbctl=...')
                exit()

        if 'start_date' in kwargs:
                start_date=dt.datetime.strptime(kwargs['start_date'],'%Y%m%d')
                
        else:
                start_date = dt.datetime.strptime('19900101', '%Y%m%d')
        if 'end_date' in kwargs:
                end_date=dt.datetime.strptime(kwargs['end_date'],'%Y%m%d')
        else:
                end_date=dt.datetime.today()

                
        try:        
                direc = kwargs['dir']
        except:
                print ('Pleasen provide path to the results dir=')
                exit()
        sb_ctl = kwargs['sbctl']

        filename = direc+'/'+'tmp.h5'
#       filename = direc+'/'+site+'_'+target+'_'+str(end_date)+'_tmp.h5'

        if not os.path.isfile(sb_ctl):
            print ('SB %s control file not found'%sb_ctl)
            return
        dirs = os.listdir(direc)
        dirs = list(filter(lambda x: os.path.isdir(direc+'/'+x) and end_date > dt.datetime(int(x[0:4]),int(x[4:6]),int(x[6:8])) > start_date, dirs))
        if dirs == []:
                print ('no matching results found in '+direc)
                return
        dirs.sort()
        
        ctlfile = ''.join((direc, '/', 'sfit4.ctl'))
        if not os.path.isfile(ctlfile):
                print ('no sfit4.ctl file')
                return

        ctl = sfit4_ctl()
        ctl.read(ctlfile)
        sbctl = sfit4_ctl()
        sbctl.read(sb_ctl)
        h5file = hdf5.open_file(filename, mode = "w", title = "sfit4 results")
        
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
            print (dd)
            # Essential quantities fist
            sumfile =  ''.join((direc, '/', dd, '/', 'summary'))
            if not os.path.isfile(sumfile):
                print ('No summary file')
                continue
            rprfsfile =  ''.join((direc, '/', dd, '/', 'rprfs.table'))
            if not os.path.isfile(rprfsfile):
                print ('rprfs.table')
                continue            
            aprfsfile =  ''.join((direc, '/', dd, '/', 'aprfs.table'))
            if not os.path.isfile(aprfsfile):
                print ('aprfs.table')
                continue
            statefile =  ''.join((direc, '/', dd, '/', 'statevec'))
            if not os.path.isfile(statefile):
                print ('statevecfile')
                continue
            miscfile =  ''.join((direc, '/', dd, '/', 'misc.out'))
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
                summary = sfit4.summary(sumfile)
            try:
                summary = sfit4.summary(sumfile)
            except:
                print ('summary file not readable')
                continue

            if (ctl.get_value('rt.temperature') == 'T'):
                    flag_tret = True
            else:
                    flag_tret = False
            
        
            flag_h2o = False
            try:
                rprf = sfit4.read_table(rprfsfile)
            except:
                print ('rprf file not readable')
                continue
            try:
                aprf = sfit4.read_table(aprfsfile)
            except:
                print ('aprf file not readable')
                continue
            gasnames = rprf.get_retrieval_gasnames()
            rvmr,z = rprf.get_gas_vmr(gasnames[0])
            avmr,z = aprf.get_gas_vmr(gasnames[0])
            rcol = rprf.get_gas_col(gasnames[0])
            acol = aprf.get_gas_col(gasnames[0])
            len_vmr = len(z)
            
            try:
                stv = sfit4.statevec(statefile)
            except:
                print ('statevec file not readable')
                continue
                    
            auxnames =  stv.aux
            aux_apriori = stv.ap_aux
            aux_retrieved = stv.rt_aux
            nr_aux = len(aux_apriori)

            if flag_tret:
                t_apriori = stv.T
		t_ret = stv.Tret
                    
            nr_gas = len(gasnames)
            i_rvmr=np.zeros((len_vmr,0))
            i_avmr=np.zeros((len_vmr,0))
            i_col = []
            for gas in gasnames[1:]:
                vmr,z = rprf.get_gas_vmr(gas)
                i_rvmr = np.hstack((i_rvmr, np.reshape(vmr, (len_vmr,1))))
                vmr,z = aprf.get_gas_vmr(gas)
                i_avmr = np.hstack((i_avmr, np.reshape(vmr, (len_vmr,1))))
                col,z = rprf.get_gas_col(gas)
                i_col.append(sum(col))
            i_col = np.array(i_col)


            z,zb,p,t,ac = rprf.get_atmosphere()
            err = sfit4.error(sbctl=sb_ctl,dir=direc+'/'+dd)
            srvmr, ssvmr = err.read_total_vmr()
            srpcol, sspcol = err.read_total_pcol()
            srcol, sscol = err.read_total_col()

            err_flag = err.flag
            if not err.flag:
                 print ('No Error matrices')
                 continue

            if err_flag:
                    cov_srvmr = err.S_vmr_ran;
                    cov_ssvmr = err.S_vmr_sys;
            else:
                    cov_srvmr = np.ones((len_vmr, len_vmr))*-1
                    cov_ssvmr = np.ones((len_vmr, len_vmr))*-1
                    srpcol = np.ones((len_vmr))*-1
                    sspcol = np.ones((len_vmr))*-1

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
                if flag_tret:
                        T_apriori = np.zeros((len_vmr, nr_entries)) *np.nan
			Tret = np.zeros((len_vmr, nr_entries)) *np.nan
                airmass = np.zeros((len_vmr, nr_entries)) *np.nan
                vmr_h2o_ap = np.zeros((len_vmr, nr_entries)) *np.nan

                h5file.create_array("/", 'Z', np.array(z), "Altitude levels (mid points)")1
                h5file.create_array("/", 'Zb', np.array(zb), "Altitude levels (boundaries)")
                vmr_rt = h5file.create_earray("/", 'vmr_rt', hdf5.Float32Atom(), 
                                             (len_vmr,0), title="Retrieved VMR", expectedrows=nr_entries)
                ivmr_rt = h5file.create_earray("/", 'ivmr_rt', hdf5.Float32Atom(),
                                             (len_vmr,nr_gas-1,0), title="Retrieved VMR of interfering gases", 
                                              expectedrows=nr_entries)
                ivmr_ap = h5file.create_earray("/", 'ivmr_ap', hdf5.Float32Atom(), 
                                             (len_vmr,nr_gas-1,0), title="A priori VMR of interfering gases", 
                                              expectedrows=nr_entries)
                icol_rt = h5file.create_earray("/", 'icol_rt', hdf5.Float32Atom(), 
                                             (nr_gas-1,0), title="Retrieved total column of interfering gases", 
                                              expectedrows=nr_entries)
                if nr_aux > 0:
                        aux_ap = h5file.create_earray("/", 'aux_ap', hdf5.Float32Atom(), 
                                                     (nr_aux,0), title="Apriori of auxilliary entries in state vector", 
                                                     expectedrows=nr_entries)
                        aux_rt = h5file.create_earray("/", 'aux_rt', hdf5.Float32Atom(), 
                                                     (nr_aux,0), title="Retrievals of auxilliary entries in state vector", expectedrows=nr_entries)
                vmr_ap = h5file.create_earray("/", 'vmr_ap', hdf5.Float32Atom(), 
                                             (len_vmr,0), title="Apriori VMR", expectedrows=nr_entries)
                vmr_ran = h5file.create_earray("/", 'cov_vmr_ran', hdf5.Float32Atom(), 
                                             (len_vmr,len_vmr,0), title="Total error random VMR", expectedrows=nr_entries)
                vmr_sys = h5file.create_earray("/", 'cov_vmr_sys', hdf5.Float32Atom(), 
                                             (len_vmr,len_vmr,0), title="Total error systematic VMR", expectedrows=nr_entries)
                pcol_rt = h5file.create_earray("/", 'pcol_rt', hdf5.Float32Atom(), 
                                             (len_vmr,0), title="Retrieved Partial Columns", expectedrows=nr_entries)
                pcol_ap = h5file.create_earray("/", 'pcol_ap', hdf5.Float32Atom(), 
                                             (len_vmr,0), title="Apriori Partial Columns", expectedrows=nr_entries)
                pcol_ran = h5file.create_earray("/", 'pcol_ran', hdf5.Float32Atom(), 
                                             (len_vmr,0), title="Total error random partial column", expectedrows=nr_entries)
                pcol_sys = h5file.create_earray("/", 'pcol_sys', hdf5.Float32Atom(), 
                                             (len_vmr,0), title="Total error systematic partial column", expectedrows=nr_entries)
                h2o_setup = h5file.create_earray("/", 'h2o_vmr_setup', hdf5.Float32Atom(), 
                                             (len_vmr,0), title="H2O VMR profile of setup", expectedrows=nr_entries)
                
                P = h5file.create_earray("/", 'P', hdf5.Float32Atom(), 
                                        (len_vmr,0), title="Pressure", expectedrows=nr_entries)
                T = h5file.create_earray("/", 'T', hdf5.Float32Atom(), 
                                        (len_vmr,0), title="Temperature", expectedrows=nr_entries)
                if (flag_tret):
                     T_apriori = h5file.create_earray("/", 'Tapriori', hdf5.Float32Atom(), 
                                        (len_vmr,0), title="Temperature apriori", expectedrows=nr_entries)
		     Tret = h5file.create_earray("/", 'Tret', hdf5.Float32Atom(), 
                                         (len_vmr,0), title="Temperature", expectedrows=nr_entries)
                air_mass = h5file.create_earray("/", 'air_mass', hdf5.Float32Atom(), 
                                             (len_vmr,0), title="AIRMASS", expectedrows=nr_entries)
        
            akt_entry = akt_entry + 1
            if (~np.isfinite(summary.retriev[0])) :
                print ('not finite')
                continue
        
            akfile =  ''.join((direc, '/', dd, '/', 'ak.out'))
            avk = True
            if not os.path.isfile(akfile):
                print ('no sfit4 avk')
                ak_flag = False
                avk = np.zeros((len_vmr,len_vmr))
                avk_vmr = avk
                avk_col = avk
            else:
                print ('read sfit4 avk')
                ak_flag = True
                ak = sfit4.avk(akfile,aprfsfile)
                avk = ak.avk()
                avk_col = ak.avk(type='column')
                avk_vmr = ak.avk(type='vmr')

            akfile =  ''.join((direc, '/', dd, '/', sbctl.get_value('file.out.avk')))
            if not os.path.isfile(akfile):
                print ('no error avk')
            else:
                print ('read error avk')
                ak_flag = True
                ak = sfit4.avk(akfile,aprfsfile)    
                avk = ak.avk()
                avk_col = ak.avk(type='column')
                avk_vmr = ak.avk(type='vmr')
            try:
                chi_2_y[nr_res] = summary.chi_y_2
            except:
                print ('no chi_2_y')
                continue

            if not ak_flag:
                print ('no avk found')
                continue    

            print ('akzepted')
            col_rt[:,nr_res] = summary.retriev
            col_ap[:,nr_res] = summary.apriori
            airmass[:,nr_res] = ac
            air_col[nr_res] = np.sum(ac)
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
            # fisrt argument is test of existence of PTH from misc.out
            if pth.size > 0 and np.double(pth[0]) > 500.0:
                    p_surface.append(pth[0])
            else:
                    p_surface.append(-90000)

            if  pth.size == 0 or pth[1] > 90:
                    t_surface.append(-90000)
            else:
                    t_surface.append(pth[1] + 273.15) 

            if  pth.size > 0 and np.double(pth[2]) > 0.0:
                    h_surface.append(pth[2])
            else:
                    h_surface.append(np.double(-90000))
        
            vmr_rt.append(np.reshape(rvmr,(len_vmr,-1)))
            vmr_ap.append(np.reshape(avmr,(len_vmr,-1)))
            ivmr_rt.append(np.reshape(i_rvmr, (len_vmr, nr_gas-1, 1)))
            ivmr_ap.append(np.reshape(i_avmr, (len_vmr, nr_gas-1, 1)))  
            icol_rt.append(np.reshape(i_col, (nr_gas-1, 1)))
            if nr_aux > 0:
                    aux_ap.append(np.reshape(aux_apriori, (nr_aux, 1)))
                    aux_rt.append(np.reshape(aux_retrieved, (nr_aux, 1)))
            if np.isfinite(srvmr).all() and np.isfinite(srpcol).all():
                vmr_ran.append(np.reshape(cov_srvmr,(len_vmr, len_vmr, 1)))
                vmr_sys.append(np.reshape(cov_ssvmr,(len_vmr, len_vmr, 1)))
                pcol_ran.append(np.reshape(srpcol,(len_vmr, -1)))
                pcol_sys.append(np.reshape(sspcol,(len_vmr, -1)))
                col_ran[nr_res] = srcol
                col_sys[nr_res] = sscol
            pcol_rt.append(np.reshape(rcol[0],(len_vmr, -1)))
            pcol_ap.append(np.reshape(acol[0],(len_vmr, -1)))
            P.append(np.reshape(p,(len_vmr, -1)))
            T.append(np.reshape(t,(len_vmr, -1)))
            if flag_tret:
                    T_apriori.append(np.reshape(t_apriori,(len_vmr, -1)))
		    Tret.append(np.reshape(t,(len_vmr, -1)))
            air_mass.append(np.reshape(ac,(len_vmr, -1)))

            h2o, z = aprf.get_gas_vmr('H2O')
            h2o_setup.append(np.reshape(h2o,(len_vmr, -1)))
            h2o, z = aprf.get_gas_col('H2O')
            col_h2o_ap.append(np.sum(h2o))
        
            nr_res = nr_res + 1
            if nr_res == 1:
                len_ak = avk.shape[0]
                AK = h5file.create_earray("/", 'avk', hdf5.Float32Atom(), 
                                         (len_ak,len_ak,0), title="AVK (normalised)", 
                                         expectedrows=nr_entries)
                AKc = h5file.create_earray("/", 'avk_col', hdf5.Float32Atom(), 
                                         (len_ak,len_ak,0), title="AVK (column)", 
                                         expectedrows=nr_entries)
                AKv = h5file.create_earray("/", 'avk_vmr', hdf5.Float32Atom(), 
                                         (len_ak,len_ak,0), title="AVK (vmr)", 
                                         expectedrows=nr_entries)
                if flag_tret:                                                  
                        AKt = h5file.create_earray("/", 'avk_temperature', hdf5.Float32Atom(), 
                                                   (len_ak,len_ak,0), title="AVK temperature (normalised)", 
                                                   expectedrows=nr_entries)
            AK.append(np.reshape(avk,(len_ak,len_ak,1)))
            AKc.append(np.reshape(avk_col,(len_ak,len_ak,1)))
            AKv.append(np.reshape(avk_vmr,(len_ak,len_ak,1)))
                if flag_tret:
                        AKt.append(np.reshape(avk_temp,(len_ak,len_ak,1)))
        
        
        col_rt = col_rt[0,0:nr_res]
        col_ap = col_ap[0,0:nr_res]
        col_ran = col_ran[0:nr_res]
        col_sys = col_sys[0:nr_res]
        air_col = air_col[0:nr_res]
        chi_2_y = chi_2_y[0:nr_res]
        dofs = dofs[0:nr_res]

        
        h5file.create_array("/", 'directories', dir, "Directories")
        h5file.create_array("/", 'spectra', spectra, "Filename of Spectrum")
        h5file.create_array("/", 'mdate', np.array(mdate), "Measurement date and time")
        h5file.create_array("/", 'sza', np.array(sza), "Solar zenith angle")
        h5file.create_array("/", 'azimuth', np.array(azi), "Solar azimuth angle")
        h5file.create_array("/", 'lat', np.array(lat), "Latitude")
        h5file.create_array("/", 'lon', np.array(lon), "Longitude")
        h5file.create_array("/", 'alt', np.array(alt), "Altitude of Instrument")
        h5file.create_array("/", 'dur', np.array(dur), "Duration of measurement")
        h5file.create_array("/", 'P_s', np.array(p_surface), "Surface Pressure")
        h5file.create_array("/", 'T_s', np.array(t_surface), "Surface temperature")
        h5file.create_array("/", 'H_s', np.array(h_surface), "Surface Humidity")
        h5file.create_array("/", 'snr_clc', np.array(snr_clc), "Calculated SNR")
        h5file.create_array("/", 'snr_the', np.array(snr_the), "Theoretically possible SNR")
        h5file.create_array("/", 'chi_2_y', np.array(chi_2_y), "CHI_2_Y")
        h5file.create_array("/", 'dofs', np.array(dofs), "DOFS (theo)")
        h5file.create_array("/", 'iter', np.array(iter), "Iteration")
        h5file.create_array("/", 'itmx', np.array(itmx), "Maximum nr of Iteration")
        h5file.create_array("/", 'col_rt', col_rt, "Retrieved columns")
        h5file.create_array("/", 'col_ap', col_ap, "A prior columns")
        h5file.create_array("/", 'col_ran', col_ran, "Column error random")
        h5file.create_array("/", 'col_sys', col_sys, "Column error systematic")
        h5file.create_array("/", 'air_col', air_col, "Retrieved AIRMASS")
        h5file.create_array("/", 'gasnames', gasnames, "Names of retrieved gases")
        h5file.create_array("/", 'auxnames', auxnames, "Names of auxilliary state entries")
        h5file.create_array("/", 'h2o_col_setup', col_h2o_ap, "Columns of H2O in setup")

        h5file.close()

        # Create spectral database
        fid = open(direc+'/spectral_database.dat', 'w')
        fid.write('FileName Date Time Dur SZA SAzm N_Lat E_Lon Alt S_PRES S_TEMP\n')
        for nr in range(0,len(mdate)):
                ddate = mdt.num2date(mdate[nr])
                # Azimuth angle in hdf: 0 is south, clockwise increase, i.e. west is positive.
                fid.write('%s %s %s %f %f %f %f %f %f %f %f\n'%(spectra[nr], ddate.strftime('%Y%m%d'),
                       ddate.strftime('%H:%M:%S'), dur[nr], sza[nr],
                       np.mod(180.0+azi[nr],360), lat[nr], lon[nr], alt[nr],
                       p_surface[nr], t_surface[nr]))
        fid.close()


if __name__ == '__main__':

        import os,sys, getopt
        sys.path.append(os.path.dirname(sys.argv[0]))
        print (sys.argv[0])
        
        print ('Arguments: --sbctl= : path to sb.ctl-file (mandatory), --dir= : directory containing results, --start_date=yyyymmdd, --end_date=yyyymmdd')

        
        try:
                opts,arg = getopt.getopt(sys.argv[1:], [], ["dir=","sbctl=","start_date=","end_date="])
        except:
                print ('error in arguments')
                exit()

        args= 'create_hdf5('
        for opt,arg in opts:
                if opt == '--dir':
                        args = args + 'dir="' + arg + '",'
                if opt == '--sbctl':
                        args = args + 'sbctl="' + arg + '",'
                if opt == '--start_date':
                        args = args + 'start_date="' + arg + '",'
                if opt == '--end_date':
                        args = args + 'end_date="' + arg + '",'
        args=args+')'
        eval(args)


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

    
