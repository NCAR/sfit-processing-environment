import re, string
import pdb

def read_det_sfit4(filename):
    # reads a detfile written by sfit4 v 003.81

    det = {}
    gas = []
    all_gases = [];
    col = []
    dcol = []
    snr_theo = []
    rms = -1
    band = []
    ff = open(filename, 'r')
    detlines = ff.readlines()

    retrieval = True
    
    nr_iter = 0
    for line in detlines:
        if 'GAS' in line[1:4] and not '*' in line:
            tmp = re.match(" *GAS: *([A-Z0-9]*) *COLUMN: *([0-9eEdD\-\+\.]*) *\+/\- *([0-9eEdD\-\+\.]*) *([0-9eEdD\-\+\.\*]*)", line)
            gas.append(tmp.group(1))
            col.append(float(tmp.group(2)))
            tmp.group(3)
            dcol.append(float(tmp.group(3)))
        elif 'MAXIMUM NUMBER OF ITERATIONS' in line:
            tmp = re.match(' MAX[A-Z ]*: *([0-9]*)', line)
            max_nr = int(tmp.group(1))
        elif 'ITER= 0' in line[1:8]:
            retrieval = False
        elif 'ITER=' in line[1:6]:
#            pdb.set_trace()
            tmp = re.match(" *ITER= *([\-0-9]*) *AVGSNR= *([0-9E\-\+\.]*) *RMS\(\%\)= *([0-9\.]*) *NVAR= *([0-9]*) *NFIT= *([0-9]*)", line)
            if tmp == None:
                continue
#            if int(tmp.group(1)) == -1:
            rms = float(tmp.group(3))
#            else:
            nr_iter = int(tmp.group(1))
            nvar = int(tmp.group(4))
            nfit = int(tmp.group(5))
#        elif 'BAND' in line[1:5]:
#            tmp = re.match(" *BAND *= *([0-9]*)", line)
#            nr_band = int(tmp.group(1))
        elif 'SNR ' in line[1:5]: 
            tmp = re.match(" *SNR *= *([\.\-0-9]*)", line)
            snr_theo.append(float(tmp.group(1)))
        elif 'NUMBER OF RETRIEVAL GASES' in line[1:27]: 
            tmp = re.match(".*: *([0-9]*)", line)
        elif 'RETRIEVAL GAS #' in line[1:16]: 
            tmp = re.match(" *RETRIEVAL GAS # *([0-9])* *: *([0-9A-Z]*)", line)
            all_gases.insert(int(tmp.group(1)), tmp.group(2))
        elif 'BANDPASS' in line[1:9] and not '#' in line and not "LOWER" in line: 
            tmp = re.match(" *BANDPASS *: *([0-9]*)", line)
            nr_band = int(tmp.group(1))
        elif 'RETRIEVAL GAS' in line[1:14] and not '#' in line:
            tmp = re.match(" *RETRIEVAL GAS *: *([0-9A-Z ]*)", line)
            band.insert(nr_band, str.split(tmp.group(1)))

#    pdb.set_trace()
    if (rms == -1 or rms == 0) and retrieval:
        det = -1
        ff.close()
        return(det)

    det['gas'] = gas
    det['col'] = col
    det['dcol'] = dcol
    det['max_nr'] = max_nr
    det['nr_iter'] = nr_iter
    det['snr'] = 100/rms
    det['snr_theo'] = snr_theo
    det['all_gases'] = all_gases
    det['band'] = band
    det['nvar'] = nvar
    det['nfit'] = nfit

    ff.close()
    return(det)
