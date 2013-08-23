FUNCTION julian_date, date_ut, ISO8601=iso, MJD2000=mjd2000
;Computes the Julian date (jd) or date in MJD2000 format in double precision.
; ----------
;   Bojan R. Bojkov
;   bojan.r.bojkov@nasa.gov
;   06/03/2001
;   09/24/2001: Code cleanup                        - Function Version 1.0
;   10/16/2001: Mode corrections                    - Function Version 1.01
;   03/07/2002: Comment cleanup and variable change - Function Version 2.0
;   10/08/2002: Added jdf option                    - Function Version 2.1
;   07/21/2003: Converted to a function             - Function Version 3.0
;   05/25/2005: Added ISO8601 and MJD2000 keywords.
;               Input can either be a string or a numeric array
;               (see below for input details). Returns -99999.d
;               if the Input is invalid - Ian Boyd
;
; References ----------
;   Hughes, D.W., Yallop, B.D. and Hohenkerk, C.Y., "The Equation of Time",
;     Mon. Not. R. astr. Soc., 238, pp 1529-1535. 1989.
;
;   Results verified using:
;     Meeus, J, "Astronomical Algorithms", William-Bell, Inc., Richmond VA,
;     p62, 1991.
;
; Caveats ----------
;   NONE
;
; Input ----------
;   date_ut: Numeric array (UT: YYYY, MM, DD, [hh, mm, ss]), or if ISO8601
;            keyword set, a string containing datetime as YYYYMMDDThhmmssZ
;
; Output ---------
;   jd:      julian day, or if MJD2000 keyword set,
;            a double precision day in MJD2000 format
;
; External subroutines ---------
;   NONE

ON_IOERROR,TypeConversionError
valid=0 ;Type conversion check
inputerror=0 ;Check that input is as expected
;Check input format
IF KEYWORD_SET(iso) THEN BEGIN ;input is YYYYMMDDThhmmssZ
  IF STRLEN(date_ut) EQ 16 THEN BEGIN
    ;test for numeric values (will return type conversion error value if not a number)
    FOR i=0,7 DO check=FIX(STRMID(date_ut,i,1))
    FOR i=9,14 DO check=FIX(STRMID(date_ut,i,1))
    dt=INTARR(6)
    dt[0]=FIX(STRMID(date_ut,0,4)) & dt[1]=FIX(STRMID(date_ut,4,2))
    dt[2]=FIX(STRMID(date_ut,6,2)) & dt[3]=FIX(STRMID(date_ut,9,2))
    dt[4]=FIX(STRMID(date_ut,11,2)) & dt[5]=FIX(STRMID(date_ut,13,2))
    date_ut=dt & achk=[0,6] ;to add hhmmss component
  ENDIF ELSE inputerror=1
ENDIF ELSE BEGIN
  ;check that input contains at least YMD (and at most YMDhms) information and is either
  ;an integer, long, float or double array
  achk=SIZE(date_ut)
  IF (achk[1] LT 3) OR (achk[1] GT 6) OR (achk[2] LT 2) OR (achk[2] GT 5) THEN inputerror=1
ENDELSE

IF inputerror EQ 0 THEN BEGIN ;can perform JD calculation
  IF date_ut[1] GT 2 THEN BEGIN
    y=DOUBLE(date_ut[0])
    m=DOUBLE(date_ut[1]-3)
    d=DOUBLE(date_ut[2])
  ENDIF ELSE BEGIN
    y=DOUBLE(date_ut[0]-1)
    m=DOUBLE(date_ut[1]+9)
    d=DOUBLE(date_ut[2])
  ENDELSE

  ;Compute Julian date:
  j=LONG(365.25D0*(y+4712.D0))+LONG(30.6D0*m+0.5D0)+59.D0+d-0.5D0

  ;Check for Julian or Gregorian calendar:
  IF j LT 2299159.5D0 THEN jd=j $ ;If Julian calendar.
  ELSE BEGIN ;If Gregorian calendar.
    gn=38.D0-LONG(3.D0*LONG(49.D0+y/100.D0)/4.D0)
    jd=j+gn
  ENDELSE

  ;add hhmmss values if present
  CASE 1 OF
    achk[1] EQ 4: jd=jd+DOUBLE(date_ut[3])/24.D ;hh only
    achk[1] EQ 5: jd=jd+(DOUBLE(date_ut[3])*3600.D + DOUBLE(date_ut[4])*60.D)/86400.D ;hhmm only
    achk[1] EQ 6: jd=jd+(DOUBLE(date_ut[3])*3600.D + DOUBLE(date_ut[4])*60.D + $
                         DOUBLE(date_ut[5]))/86400.D ;hhmmss
    ELSE:
  ENDCASE

  valid=1 ;Type conversion OK

  ;Set to MJD2000 if required
  IF KEYWORD_SET(mjd2000) THEN jd=jd-2451544.5D
ENDIF

TypeConversionError:
IF valid EQ 0 THEN RETURN,-99999.D ELSE RETURN, jd

END ;Function Julian_Date
