import numpy as np

def sza(year, day, lat, lon):
    #
    # Calculates Solar Zenith Angles SZA for day of year, lat and lon
    # Eastward longitudes positive. Day of year is 1 for Jan 1st
    #
    # Time is given in UT
    # Ulf Klein, 22.05.00; BMSinnhuber, 14.10.97
    # using routines from Gerhard Schwaab
    # converted to python by Mathias Palm 25.2.2015


    JD_UT=juldat(day,year)

    # Berechne einige benoetigte Zeiten:
    # from http://stjarnhimlen.se/comp/time.html#deltat72p (TT - UT1)
    # Mathias

    deltat72p = {1990: 56.86,
                 1991: 57.57,
                 1992: 58.31,
                 1993: 59.12,
                 1994: 59.98,
                 1995: 60.78,
                 1996: 61.63,
                 1997: 62.29,
                 1998: 62.97,
                 1999: 63.47,
                 2000: 63.82,
                 2001: 63.98,
                 2002: 65.30,
                 2003: 64.47,
                 2004: 64.57,
                 2005: 64.68,
                 2006: 64.84,
                 2007: 65.25,
                 2008: 65.54,
                 2009: 65.86,
                 2010: 66.15,
                 2011: 66.39,
                 2012: 66.9,
                 2013: 67,
                 2014: 67.3,
                 2015: 67.7}

    try:
        ET_UT = deltat72p[year]
    except:
        print 'epheremide time %4d not yet known'%(year)


        
    # Berechne UT aus localtime und timezone
    JD_ET=JD_UT+ET_UT/86400

    # Berechne mittlere lokale Sternzeit (always UT !!!)
    # therefor longitude is set to 0
    lmst=lmsidtim1(JD_UT,-lon,0)

    # Berechne Rektaszension und Deklination der Sonne:
    akoord=sunpos1(JD_ET)


    # Berechnung von SZA in Grad fuer einen Standort bekannter geographischer
    # Breite aus den Groessen akoord = [Rektaszension (in Stunden) Deklination (in Grad)]
    # und der dazugehoerigen Sternzeit lmst (in Stunden)

    rad1=np.pi/180
    # Stundenwinkel in Grad
    Stundenwinkel=(lmst-akoord[0])*15*rad1
    deklination=akoord[1]*rad1
    breite=lat*rad1

    phi=90-np.arcsin(np.sin(breite)*np.sin(deklination)+np.cos(breite)*np.cos(deklination)*np.cos(Stundenwinkel))/rad1

    return(phi)


def juldat(day,year):
    # Berechnet julianisches Datum aus day of year und year
    #
    # BMSinnhuber, 14.10.97 nach juldat.m von Gerhard Schwaab

    A=np.fix((year-1)/100)
    B=0
    if((10000*(year-1)+100*13+day) > 15821004):
        B=2-A+np.fix(A/4)
        
    JD=np.fix(365.25*((year-1)+4716))+np.fix(30.6001*(13+1))+day+B-1524.5

    return(JD)

def lmsidtim1(localtime,longitude,timezone):

    # Berechnung der lokalen Sternzeit aus dem julianischen Datum localtime,
    # der geographischen Laenge und der Zeitzone (MEZ = -1)

    # Berechnung des julianischen Datums fuer Greenwich
    greenwich=localtime+timezone/24


    # Julianisches Datum fuer Greenwich um 0:00 UT
    greenwich0=np.floor(greenwich-0.5)+0.5

    # UT in Stunden
    UT = (greenwich-greenwich0)*24

    #Zeitdifferenz zur Epoche 1.1.2000,12:00
    timediff=greenwich0-2451545
    centuries=timediff/36525

    result =  6.697374558 + 1.0027379093 * UT + (8.640184812866e6 + (9.3104e-2 - 6.2e-6 * centuries)*centuries)*centuries/3.6e3

    result=(result-longitude/15.0)

    result=np.fmod(result,24)
    if result < 0:
        result=result+24

    return(result)
            
def sunpos1(DT):
    # Berechnet Rektaszension und Deklination der Sonne bei gegebener Dynamischer Zeit 

    rad1=np.pi/180.0
    # Berechne Zeitdifferenz zum 1.1.2000,12:00 in Jahrhunderten
    T= (DT-2451545)/36525.0

    # geometrische mittlere Laenge der Sonne in Grad:
    Lnull=280.46645+(36000.76983+0.0003032*T)*T

    # Mittlere Anomalie der Sonne in Grad
    M=357.52910+(35999.05030-(0.0001559+0.00000048*T)*T)*T

    # Exzentrizitaet der Erdbahn
    e=0.016708617-(0.000042037+0.0000001236*T)*T

    # Mittelspunktgleichung
    C=(1.914600-(0.004817+0.000014*T)*T)*np.sin(M*rad1) + (0.019993-0.000101*T)*np.sin(2*M*rad1) + 0.000290*np.sin(3*M*rad1)

    # Wahre Laenge der Sonne
    L=Lnull+C

    # aufsteigender Knoten in Grad:
    Omega=125.04 -1934.136*T

    # scheinbare Laenge der Sonne in Grad
    lamb=L-0.00569-0.00478*np.sin(Omega*rad1)

    # Schiefe der Ekliptik in Grad:
    deltaeps= -(46.8150+(0.00059-0.001813*T)*T)*T;
    epsilon=hr1([23.0, 26.0, 21.448])+deltaeps/3600.0+0.00256*np.cos(Omega*rad1)

    position = np.array([0.0,0.0])
    position[0]=np.arctan2(np.cos(epsilon*rad1)*np.sin(lamb*rad1),np.cos(lamb*rad1))*12.0/np.pi
    if position[0]<0:
        position[0]=position[0]+24.0
    position[1]=np.arcsin(np.sin(epsilon*rad1)*np.sin(lamb*rad1))/rad1;

    return(position)

def hr1(time):
    # Verwandelt time=[Stunde Minute Sekunde] in dezimale Stunde

    sign=1
    if time[0] < 0:
        sign = -1
    dechour=time[0]+sign*np.abs(time[1])/60.0+sign*np.abs(time[2])/3600.0
    return(dechour)
