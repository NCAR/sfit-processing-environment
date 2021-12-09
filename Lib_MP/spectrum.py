import read_from_file as rn
import matplotlib.dates as dt
import string, pdb
import numpy as np
import matplotlib.pyplot as plt

class spectrum:

    def read_spectrum(self, filename, synspec=False):
        self.sza = []
        self.earth_rad = []
        self.latitude = []
        self.longitude = []
        self.snr = []
        self.meas_date = []
        self.comment = []
        self.nu_start = []
        self.nu_stop = []
        self.nu_res = []
        self.nr_nu = []
        self.nu = []
        self.spectrum=[]

        spdf = rn.read_from_file(filename)

        while 1:

            if not synspec:
                tmp = spdf.next(5)
                if spdf.stat() == -1:
                    break
                self.sza.append(tmp[0])
                self.earth_rad.append(tmp[1])
                self.latitude.append(tmp[2])
                self.longitude.append(tmp[3])
                self.snr.append(tmp[4])

                tmp = spdf.next(6)
                year = int(tmp[0])
                month = int(tmp[1])
                day = int(tmp[2])
                hour = int(tmp[3])
                minute = int(tmp[4])
                second = int(tmp[5])

                self.meas_date.append(dt.date2num(dt.datetime.datetime(year,month,day,hour,minute,second)))
            
                spdf.nextline()

#            else:
#                spdf.nextline()

            self.comment.append(spdf.get_line())
            
            tmp = spdf.next(4)
            print(tmp)
            if spdf.stat() == -1:
                break
            self.nu_start.append(tmp[0])
            self.nu_stop.append(tmp[1])
            self.nu_res.append(tmp[2])
            self.nr_nu.append(tmp[3])
            print (tmp)
            nu = []
            spectrum = []
            for n in range(0,self.nr_nu[-1]):
                nu.append(self.nu_start[-1] + n*self.nu_res[-1])

            spectrum = spdf.next(self.nr_nu[-1])


            self.nu.append(np.array(nu))
            self.spectrum.append(np.array(spectrum))

        del spdf

    def one_spectrum(self, nu_start, nu_stop, res):
        # creates a new spectrum using the same header information but 
        # different frequency range and resolution
        
        self.sza[1:] = []
        self.earth_rad[1:] = [] 
        self.latitude[1:] = [] 
        self.longitude[1:] = [] 
        self.snr[1:] = [] 
        self.meas_date[1:] = [] 
        self.comment[1:] = [] 

        self.nu_start = []
        self.nu_stop = []
        self.nu_res = []
        self.nr_nu = []
        self.nu = []
        self.spectrum = []
        self.nu_start.append(nu_start)
        self.nr_nu.append(int(np.ceil((nu_stop - nu_start)/res)))
        self.nu_stop.append((nu_start + self.nr_nu[0] * res))
        self.nu_res.append(res)
        self.nu.append(np.linspace(nu_start, nu_stop, num=self.nr_nu[0], endpoint=True))
        self.spectrum.append(np.ones(self.nr_nu[0]))

    def write_spectrum(self,filename):
        fid = open(filename, 'w')

        for nr in range(0,len(self.sza)):
            tmp = '%.2f %.2f %.2f %.2f %.2f' % (self.sza[nr], self.earth_rad[nr], self.latitude[nr], self.longitude[nr], self.snr[nr])
            fid.write(tmp+'\n')
        
            fid.write(dt.num2date(self.meas_date[nr]).strftime('%Y %m %d %H %M %S')+'\n')
            fid.write(self.comment[nr]+'\n')

            res = np.abs(self.nu[nr][0] - self.nu[nr][-1])/(self.nu[nr].size-1)
            nr_sp = self.nu[nr].size
            print (self.nu[nr][0], self.nu[nr][-1], res, nr_sp)
            fid.write('%.10f %.10f %.20f %d \n'% 
                      (self.nu[nr][0], self.nu[nr][-1], res, nr_sp))

            for n in range(0,nr_sp):
                fid.write('%.6f\n'%self.spectrum[nr][n])

        fid.close()

    def plot_spectrum(self):
        f = plt.figure('Spectrum')
        f.clf()
        plt.plot(self.nu[0], self.spectrum[0])
        f.show()




    
