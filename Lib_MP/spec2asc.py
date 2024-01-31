#!/usr/bin/python3
from ftsreader import ftsreader
import numpy as np

class spectrum:

    def __init__(self,opusfile):
        self.s = ftsreader(opusfile,getspc=True)

    def write_sfit4_file(self,freqs):
        f_s = self.s.spcwvn[0]
        f_e = self.s.spcwvn[-1]
        if f_s > f_e:
            flag_inv = True
            f_s = self.s.spcwvn[-1]
            f_e = self.s.spcwvn[0]
        else:
            flag_inv = False

        nr_e = self.s.spcwvn.size
        res = np.abs((f_s-f_e)/nr_e)
        fid = open('output','w')
        for nr in range(0,freqs.shape[0]):
            inds = np.argwhere((self.s.spcwvn > freqs[nr,0]) & (self.s.spcwvn < freqs[nr,1]))
            fid.write('Spectrum {}\n'.format(nr))
            fid.write('{} '.format(freqs[nr,0]))
            fid.write('{} '.format(freqs[nr,1]))
            fid.write('{} '.format(res))
            fid.write('{}\n'.format(inds.size))
            if flag_inv:
                inds = np.flip(inds)
            for ind in inds:
                fid.write('{}\n'.format(self.s.spc[ind[0]]))
        fid.close()
        

if __name__ == '__main__':
    spctype=input('filetype?')
    insttype = input('instrument?')
    specfile = input('spectrum')
    regions = input('ranges')
    freqs = np.zeros((int(regions),2))
    for nr in range (1,int(regions)+1):
        st=input('start {}'.format(nr))
        en=input('end {}'.format(nr))
        freqs[nr-1,0]=st
        freqs[nr-1,1]=en

    s = spectrum(specfile)
    s.write_sfit4_file(freqs)
