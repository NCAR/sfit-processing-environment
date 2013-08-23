FUNCTION jdf_2_datetime, jdf, MJD2000=mjd2000, SHORTISO8601=iso, LONGISO8601=isoms
;Computes the UT date/time from JDF/MJD2000.
; ----------
;   Bojan R. Bojkov
;   bojan.r.bojkov@nasa.gov
;   03/04/2004
;   03/11/2004 bug fix
;   05/27/2005 add ShortISO8601 and LongISO8601 switches,
;              and change seconds value to decimal seconds (Ian Boyd)
;
; References ----------
;   Explan. Supp. Astron. Almanac, p.604 (1992); through E. Celarier
;
; Caveats ----------
;   Valid for all YYYY >= -4712 (i.e. for all JD .ge. 0)
;   The true Gregorian calendar was only adopted on 15 October 1582,
;   so any dates before this are "virtual" Gregorian dates.
;
; Input ----------
;   jdf     : double precision value
;   mjd2000 : flag if input is MJD2000
;   iso     : flag if output is in ISO8601 (YYYYMMDDThhmmssZ)
;   isoms   : flag if output is in ISO8601ms (YYYYMMDDThhmmss.sssZ)
;
; Output ---------
;   floating point array [YYYY, MM, DD, hh, mn, ss.sss],
;   or ISO8601 string format
; External subroutines ---------
;   NONE

jdf=DOUBLE(jdf)

j0=2451544.5D
IF KEYWORD_SET(mjd2000) THEN jdhold=jdf+j0 ELSE jdhold=jdf
jdi=LONG(jdhold)
df=jdhold-jdi

;Determine hh, mm, ss, ms
hh=(df+0.5)*24.D
q=WHERE(hh GE 24.D)
IF q[0] NE -1 THEN BEGIN
  hh[q]=hh[q]-24.D
  jdi[q]=jdi[q]+1
ENDIF
t1=hh
hh=LONG(t1)
t2=(t1-hh)*60.D
mn=LONG(t2)
t3=(t2-mn)*60.D
ss=t3
;ss=LONG(t3)
;ms=LONG((t3-ss)*1.d3)

;Determine YYYY, MM, DD
t1=jdi+68569L
t2=(4*t1)/146097L
t1=t1-(146097L*t2+3L)/4L
t3=(4000L*(t1+1L))/1461001L
t1=t1-(1461L*t3)/4L + 31L
t4=(80L*t1)/2447L

dd=t1-(2447L*t4)/80L
t1=t4/11L
mm=t4+2L-12L*t1
yyyy=100L*(t2-49L)+t3+t1

dt=TRANSPOSE([[yyyy],[mm],[dd],[hh],[mn],[ss]])
IF (KEYWORD_SET(iso)) OR (KEYWORD_SET(isoms)) THEN BEGIN
  dts=STRARR(6)
  IF (KEYWORD_SET(iso)) AND (ss-FIX(ss) GE 0.5) THEN BEGIN
    ;recalculate to get correct seconds value
    jdhold=jdf+0.000008D ;add ~0.7 secs
    IF KEYWORD_SET(mjd2000) THEN jdhold=jdhold+j0
    CALDAT,jdhold,mm,dd,yyyy,hh,mn,ss
    dt=TRANSPOSE([[yyyy],[mm],[dd],[hh],[mn],[ss]])
  ENDIF
  dt=LONG(dt)
  FOR i=1,5 DO $
    IF dt[i] LT 10L THEN dts[i]='0'+STRTRIM(dt[i],2) ELSE dts[i]=STRTRIM(dt[i],2)
  IF KEYWORD_SET(isoms) THEN BEGIN
    ssd=STRING(format='(f6.3)',ss)
    IF FLOAT(ssd) LT 10.0 THEN dts[5]='0'+STRTRIM(ssd,2) ELSE dts[5]=STRTRIM(ssd,2)
  ENDIF
  RETURN,STRTRIM(dt[0],2)+dts[1]+dts[2]+'T'+dts[3]+dts[4]+dts[5]+'Z'
ENDIF ELSE RETURN, dt

END ;Function jdf_2_datetime
