from pyhdf import SD
import tables as h5
import sys, re, os
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import numpy as np

class load_h5:
    def __init__(self, h5_file):
        self.h5 = h5.File(h5_file)
        self.h5file = h5_file
        self.dates = dates.num2date(self.h5.root.mdate[:])

    def get_columns(self,gas):
        rt = self.h5.root.col_rt[:]
        er=es=ap = []
        try:
            ap = self.h5.root.col_ap[:]
        except:
            pass
        try:
            er = self.h5.root.col_ran[:]
            es = self.h5.root.col_sys[:]
        except:
            pass
        return(rt,ap,er,es)


class load_H4:
    def __init__(self, h4file):
        self.h4 = SD.SD(h4file)
        self.keys = self.h4.datasets().keys()
        self.h4file = file
        # in hdf file datenum since 2000-1-1-0-0-0
        self.dates = dates.num2date(self.h4.select('DATETIME').get()+730120.0)
        self.data_template = self.h4.attributes()['DATA_TEMPLATE']
#        import pdb
#        pdb.set_trace()

    def __del__(self):
        self.h4.end()

    def get_ind_from_date(self, dnum):
        dd = dates.date2num(self.dates)
        if (dd==dnum).any():
            ind = (dd==dnum).nonzero()[0][0]
        else:
            ind = -1
        return(ind)

    def get_partial_columns(self,gas):
        rt = self.h4.select(gas+'.COLUMN.PARTIAL_ABSORPTION.SOLAR').get()
        z = self.h4.select('ALTITUDE').get()
        return(rt,z)

    def get_diff_partial_columns(self,gas):
        # for old sfit4 data which have been saved wrongly

        rt = self.h4.select(gas+'.COLUMN.PARTIAL_ABSORPTION.SOLAR').get()
        rt = np.diff(rt)
        rt = np.insert(rt,0,rt[:,0],axis=1)
        z = self.h4.select('ALTITUDE').get()
        return(rt,z)

    def get_columns(self,gas):
        rt = self.h4.select(gas+'.COLUMN_ABSORPTION.SOLAR').get()
        er=es=ap = []
        try:
            ap = self.h4.select(gas+'.COLUMN_ABSORPTION.SOLAR_APRIORI').get()
        except:
            pass
        try:
            if self.data_template == 'GEOMS-TE-FTIR-001':
                er = self.h4.select(gas+'.COLUMN_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM').get()
                es = self.h4.select(gas+'.COLUMN_ABSORPTION.SOLAR_UNCERTAINTY.SYSTEMATIC').get()
            else:
                er = self.h4.select(gas+'.COLUMN_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.STANDARD').get()
                es = self.h4.select(gas+'.COLUMN_ABSORPTION.SOLAR_UNCERTAINTY.SYSTEMATIC.STANDARD').get()
        except:
            pass
        return(rt,ap,er,es)

    def get_profile(self,gas):
        if self.data_template == 'GEOMS-TE-FTIR-001':
            vmrt = self.h4.select(gas+'.MIXING.RATIO_ABSORPTION.SOLAR').get()
            vmap = self.h4.select(gas+'.MIXING.RATIO_ABSORPTION.SOLAR_APRIORI').get()
        else:
            vmrt = self.h4.select(gas+'.MIXING.RATIO.VOLUME_ABSORPTION.SOLAR').get()
            vmap = self.h4.select(gas+'.MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_APRIORI').get()
        z = self.h4.select('ALTITUDE').get()
        return(vmrt,vmap,z)

    def get_avk_column(self, gas):
        avk_col = self.h4.select(gas+'.COLUMN_ABSORPTION.SOLAR_AVK').get()
        z = self.h4.select('ALTITUDE').get()
        return(avk_col,z)

    def get_avk_vmr(self, gas):
        if self.data_template == 'GEOMS-TE-FTIR-001':
            avk_vmr = self.h4.select(gas+'.MIXING.RATIO_ABSORPTION.SOLAR_AVK').get()
        else:
            avk_vmr = self.h4.select(gas+'.MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_AVK').get()
        z = self.h4.select('ALTITUDE').get()
        return(avk_vmr,z)

    def get_sys_vmr(self, gas):
        if self.data_template == 'GEOMS-TE-FTIR-001':
            sys_vmr = self.h4.select(gas+'.MIXING.RATIO_ABSORPTION.SOLAR_UNCERTAINTY.SYSTEMATIC.COVARIANCE').get()
        else:
            sys_vmr = self.h4.select(gas+'.MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_UNCERTAINTY.SYSTEMATIC.COVARIANCE').get()
        z = self.h4.select('ALTITUDE').get()
        return(sys_vmr,z)

    def get_ran_vmr(self, gas):
        if self.data_template == 'GEOMS-TE-FTIR-001':
            ran_vmr = self.h4.select(gas+'.MIXING.RATIO_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.COVARIANCE').get()
        else:
            ran_vmr = self.h4.select(gas+'.MIXING.RATIO.VOLUME_ABSORPTION.SOLAR_UNCERTAINTY.RANDOM.COVARIANCE').get()
        z = self.h4.select('ALTITUDE').get()
        return(ran_vmr,z)

    def get_zpt(self):
        P = self.h4.select('PRESSURE_INDEPENDENT').get()
        T = self.h4.select('TEMPERATURE_INDEPENDENT').get()
        Z = self.h4.select('ALTITUDE').get()
        Zb = self.h4.select('ALTITUDE.BOUNDARIES').get()
        return(Z,Zb,P,T)

        
    def get_misc(self):
        p_s = self.h4.select('SURFACE.PRESSURE_INDEPENDENT').get()
        t_s = self.h4.select('SURFACE.TEMPERATURE_INDEPENDENT').get()
        dnum = self.h4.select('INTEGRATION.TIME').get()
        asza = self.h4.select('ANGLE.SOLAR_ZENITH.ASTRONOMICAL').get()
        return(p_s, t_s, dnum, asza)


class load_hdf:

    def __init__(self):
        self.f1 = plt.figure(1)
        self.f1.clf()
        self.f2 = plt.figure(2)
        self.f2.clf()

    def load_tmph5(self,tmph5):
        self.h5 = [load_h5(tmph5)]
        

    def load_AllGeoms(self,direc,site,gas):
        m = re.compile(".*\.hdf",re.I)
        s = re.compile(site,re.I)
        g = re.compile(gas+'_',re.I)
        hdffiles = filter(m.search,os.listdir(direc))
        hdffiles = filter(s.search,hdffiles)
        hdffiles = filter(g.search,hdffiles)

        self.h4 = []
        for hf in hdffiles:
            print hf
            self.h4.append(load_H4(direc+'/'+hf))
            

    def __del__(self):
        pass 

    def get_vmr(self, gas, src='GEOMS'):
        if src=='TMPH5':
            src_hdf = self.h5
        else:
            src_hdf = self.h4
        dd = np.array([])
        for hf in src_hdf:
            dd = np.hstack((dd,dates.date2num(hf.dates)))
            rt,ap,z = hf.get_profile(gas)
            try:
                rvmr
            except:
                rvmr = np.ndarray((0,rt.shape[1]))
            rvmr = np.vstack((rvmr,rt))

            try:
                avmr
            except:
                avmr = np.ndarray((0,ap.shape[1]))
            avmr = np.vstack((avmr,ap))

        return(rvmr,avmr,dd)
        

    def get_zpts(self, src='GEOMS'):
        if src=='TMPH5':
            src_hdf = self.h5
        else:
            src_hdf = self.h4
        dd = np.array([])
        for hf in src_hdf:
            dd = np.hstack((dd,dates.date2num(hf.dates)))
            z,zb,p,t = hf.get_zpt()
            try:
                Z
            except:
                import ipdb
                ipdb.set_trace()
                Z = np.ndarray((0,z.size))
                Zb = np.ndarray((0,zb.size))
                T = np.ndarray((0,t.shape[1]))
                P = np.ndarray((0,p.shape[1]))
            Z= np.vstack((Z,z))
            Zb= np.vstack((Zb,zb))
            T= np.vstack((T,t))
            P= np.vstack((P,p))
            
        return(z,zb,p,t,dd)
        
    
    def get_avk_vmr(self, gas,src='GEOMS'):
        if src=='TMPH5':
            src_hdf = self.h5
        else:
            src_hdf = self.h4
        dd = np.array([])
        for hf in src_hdf:
            dd = np.hstack((dd,dates.date2num(hf.dates)))
            ak,z = hf.get_avk_vmr(gas)
            try:
                avk
            except:
                avk = np.ndarray((0,ak.shape[1],ak.shape[2]))
            avk = np.vstack((avk,ak))
            
        return(avk,dd)

            
    def get_columns(self,gas,src='GEOMS'):
        if src=='TMPH5':
            src_hdf = self.h5
        else:
            src_hdf = self.h4
        dd = np.array([])
        colrt = np.array([])
        coler = np.array([])
        coles = np.array([])
        for hf in src_hdf:
            dd = np.hstack((dd,dates.date2num(hf.dates)))
            rt,ap,er,es = hf.get_columns(gas)
            colrt = np.hstack((colrt,rt))
            coler = np.hstack((coler,er))
            coles = np.hstack((coles,es))
            
        return(dd, colrt, coler, coles)

    def get_partial_columns(self,gas,zrange, src='GEOMS', diff=False):
        if src=='TMPH5':
            src_hdf = self.h5
        else:
            src_hdf = self.h4
        dd = np.array([])
        colrt = np.array([])
        for hf in src_hdf:
            dd = np.hstack((dd,dates.date2num(hf.dates)))
            if diff:
                rt,z = hf.get_diff_partial_columns(gas)
            else:
                rt,z = hf.get_partial_columns(gas)
            ind1 = np.where(np.all((z > zrange[0],z < zrange[1]),axis=0))[0]
            # if diff:
            #     min_ind = np.max(ind1)
            #     max_ind = np.min(ind1)
            #     print min_ind, max_ind
            #     colrt = np.hstack((colrt,(rt[:,min_ind]-rt[:,max_ind])))
            # else:
            colrt = np.hstack((colrt,np.sum(rt[:,ind1],axis=1)))

        return(dd, colrt)

    
    def plot_columns(self, gas, ax, src='GEOMS'):

        if src=='TMPH5':
            src_hdf = self.h5
        else:
            src_hdf = self.h4

        def oncall(event):
            f3 = plt.figure(3)
            f3.clf()
            a1 = f3.add_subplot(321)
            a1.set_title('VMR')
            a3 = f3.add_subplot(323)
            a3.set_title('AVK [VMR]')
            a4 = f3.add_subplot(324)
            a4.set_title('AVK [total column]')
            a5 = f3.add_subplot(325)
            a5.set_title('COV Systematic')
            a6 = f3.add_subplot(326)
            a6.set_title('COV Random')
            dnum = event.artist.get_xdata()
            mdnum = event.mouseevent.xdata
            ind = np.argmin(np.abs(dnum-mdnum))
            pt = False
            print mdnum, dnum[ind]
            dnum = dnum[ind]

            for hf in src_hdf:
                ind = hf.get_ind_from_date(dnum)
                if ind > -1:
                    rvmr,avmr,z = hf.get_profile(gas)
                    a1.plot(rvmr[ind,:],z,'b')
                    a1.plot(avmr[ind,:],z,'r')
                    avk_vmr,z = hf.get_avk_vmr(gas)
                    a3.plot(avk_vmr[ind,:,:].T, z)
                    avk_col,z = hf.get_avk_column(gas)
                    a4.plot(avk_col[ind,:], z)
                    sys_vmr,z = hf.get_sys_vmr(gas)
                    h = a5.pcolor(z,z,sys_vmr[ind,:,:])
                    f3.colorbar(h, ax=a5, orientation='horizontal')
                    ran_vmr,z = hf.get_ran_vmr(gas)
                    h = a6.pcolor(z,z,ran_vmr[ind,:,:])
                    f3.colorbar(h, ax=a6, orientation='horizontal')
                    pt = True
                    f3.suptitle('Date %s'%(dates.num2date(dnum).strftime('%Y%m%d %H:%M:%S')))
            if not pt:
                f3.clf()
            f3.show()

        dd_min = 9e99
        dd_max = 0
#        ax2 = ax.twinx()
        for hf in src_hdf:
            dd = dates.date2num(hf.dates)
            rt2,ap,er,es = hf.get_columns('H2O')
 #           ax2.plot(dd, rt2,'go',)
            rt,ap,er,es = hf.get_columns(gas)
            ax.plot(dd, rt,'bx',picker=5)
            dd_min = np.min(np.hstack((dd_min, dd)))
            dd_max = np.max(np.hstack((dd_max, dd)))
            if len(er) == len(rt):
                ax.errorbar(dd,rt,er,ecolor='b', fmt=None)
            if len(ap) == len(rt):
                ax.plot(dd, ap,'ro')
  #      plt.sca(ax)
        ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))
        ax.set_xlim((dd_min,dd_max))
        ax.get_figure().canvas.mpl_connect('pick_event', oncall)


    def save_all_columns(self, gas, src='GEOMS'):
    
        if src=='TMPH5':
            src_hdf = self.h5
        else:
            src_hdf = self.h4

        dd = []
        rtt = []
        app = []
        err = []
        ess = []
        for hf in src_hdf:
            dd.extend(dates.date2num(hf.dates))
            rt,ap,er,es = hf.get_columns(gas)
            rtt.extend(rt)
            app.extend(ap)
            err.extend(er)
            ess.extend(es)

#        import ipdb
#        ipdb.set_trace()    
        ind = np.argsort(dd)
        dd = np.array(dd)[ind]
        rt = np.array(rtt)[ind]
        ap = np.array(app)[ind]
        er = np.array(err)[ind]
        es = np.array(ess)[ind]

        fid = open('columns.dat', 'write')
        fid.write('date dnum retr apr ran, sys\n')
        for d,r,a,rr,ss in zip(dd,rt,ap,er,es):
            dstring = dates.num2date(d).strftime('%Y%m%d%H%M%S')
            fid.write('%s %d %g %g %g %g\n'%(dstring, d, r, a, rr, ss))
        fid.close()


    
    def plot_profiles(self,gas,ax):
        dd_min = 9e99
        dd_max = 0
        for hf in self.h4:
            print hf
            rt,ap,z = hf.get_profile(gas)
            dd = dates.date2num(hf.dates)
            dd_min = np.min(np.hstack((dd_min, dd)))
            dd_max = np.max(np.hstack((dd_max, dd)))
            h = ax.pcolor(dd,z,rt.T)

        ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))
        ax.set_xlim((dd_min,dd_max))
        ax.get_figure().colorbar(h, orientation='horizontal')

    def plot_avk_column(self,gas,ax):
        dd_min = 9e99
        dd_max = 0
        for hf in self.h4:
            avk, z = hf.get_avk_column(gas)
            dd = dates.date2num(hf.dates)
            dd_min = np.min(np.hstack((dd_min, dd)))
            dd_max = np.max(np.hstack((dd_max, dd)))
            h = ax.pcolor(dd,z,avk.T)

        ax.set_xlim((dd_min,dd_max))
        ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))
        ax.get_figure().colorbar(h, orientation='horizontal')

    def plot_avk_vmr(self,gas,ax):
        dd_min = 9e99
        dd_max = 0
        for hf in self.h4:
            avk, z = hf.get_avk_vmr(gas)
            dd = dates.date2num(hf.dates)
            dd_min = np.min(np.hstack((dd_min, dd)))
            dd_max = np.max(np.hstack((dd_max, dd)))
            h = ax.pcolor(dd,z,avk.T)

        ax.set_xlim((dd_min,dd_max))
        ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))
        ax.get_figure().colorbar(h, orientation='horizontal')

    def get_auxilliary(self):
        ps = []
        ts = []
        im = []
        dd = []
        asza = []
        for hf in self.h4:
            p_s, t_s, ms, sz = hf.get_misc()
            dd.extend(dates.date2num(hf.dates))
            ps.extend(p_s) # Surface pressure
            ts.extend(t_s) # Surface temperature
            im.extend(ms)  # integration time
            asza.extend(sz) # solar zenith angle

        
            
        return(np.array(dd),np.array(ps),np.array(ts),
               np.array(im),np.array(asza))
            
        
    def plot_auxilliary(self,ax11,ax21):
        ps = []
        ts = []
        im = []
        dd = []
        asza = []
        for hf in self.h4:
            p_s, t_s, ms, sz = hf.get_misc()
            dd.extend(dates.date2num(hf.dates))
            ps.extend(p_s) # Surface pressure
            ts.extend(t_s) # Surface temperature
            im.extend(ms)  # integration time
            asza.extend(sz) # solar zenith angle
            
        ax12 = ax11.twinx()
        ax11.plot_date(dd,ps,'bx')
        ax11.set_ylabel('Surface pressure (blue)')
        ax12.plot_date(dd,ts,'rx')
        ax12.set_ylabel('Surface temperature (red)')

        ax22 = ax21.twinx()
        ax21.plot_date(dd,im,'bx')
        ax21.set_ylabel('integration time (blue)')
        ax22.plot_date(dd,asza,'rx')
        ax22.set_ylabel('SZA (red)')



    def plot_results(self,gas,src='GEOMS'):
        self.f1.clf()
        self.f2.clf()
        ax1 = self.f1.add_subplot(311)
        self.plot_columns(gas, ax1, src)
        ax2 = self.f1.add_subplot(312)
        self.plot_profiles(gas, ax2)
        ax3 = self.f1.add_subplot(313)
        self.plot_avk_column(gas, ax3)

        ax11 = self.f2.add_subplot(211)
        ax21 = self.f2.add_subplot(212)
        self.plot_auxilliary(ax11,ax21)
        self.f1.show()
        self.f2.show()

if __name__ == '__main__':
#    load_H4GEOMS(sys.argv[1])
    import sys, os
    sys.path.append(os.path.dirname(sys.argv[0]))
    h4 = load_hdf()
    h4.load_AllGeoms (sys.argv[1])
    h4.plot_results('NH3')
