import read_from_file as rn
import time
import calendar

def read_misc(filename):
    
    miscf = open(filename, 'r')
    spectrum = []
    meas_time = []
    dur = []
    sza = []
    zen = []
    lat = []
    alt = []
    lon = []
    pth = []
    p = []
    for f in miscf:
        ss = f.split('=')
        if ss[0].strip() == 'SPECTRUM':
            spectrum.append(ss[1].strip())
        if ss[0].strip() == 'Meastime':
            meas_time.append(map(lambda x:float(x), ss[1].strip()))
        if ss[0].strip() == 'Measurement time':
            meas_time.append(calendar.timegm(time.strptime(ss[1].strip(),'%Y %m %d %H %M %S')))
        if ss[0].strip() == 'Duration':
            dur.append(ss[1].strip())
        if ss[0].strip() == 'SZA':
            sza.append(ss[1].strip())
        if ss[0].strip() == 'AZIMUTH':
            zen.append(ss[1].strip())
        if ss[0].strip() == 'LATITUDE':
            lat.append(ss[1].strip())
        if ss[0].strip() == 'LONGITUDE':
            lon.append(ss[1].strip())
        if ss[0].strip() == 'ALTITUDE':
            alt.append(ss[1].strip())
        if ss[0].strip() == 'T_SURFACE':
            t = ss[1].strip()
        if ss[0].strip() == 'P_SURFACE':
            p = ss[1].strip()
        if ss[0].strip() == 'HUM_SURFACE':
            h = ss[1].strip()
    if len(p) > 0:
        pth.extend([p,t,h])
    return(meas_time, dur, sza, zen, lat, lon, alt, spectrum, pth)
            

