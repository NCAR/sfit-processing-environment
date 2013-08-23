PRO mkjday, lines, nlat, yy

; lines, nlat   -  input struct & # of lines from pfileread
; includes jday - output julian days
; includes doy
; yy            -  output  - array of years

	dd=INTARR(nlat)
	mm=INTARR(nlat)
	yy=INTARR(nlat)
	hr=INTARR(nlat)
	mn=INTARR(nlat)
	sc=INTARR(nlat)

	;window ,1
	;plot, lines[0].vmr

	FOR i=0, nlat-1 DO BEGIN
	;oplot, lines[i].vmr
	    READS, lines[i].date,format='(i2,1x,i2,1x,i4)', imm, idd, iyy
	    dd[i] = idd
	    mm[i] = imm
	    yy[i] = iyy; +2000
	    READS, lines[i].timestr,format='(i2,1x,i2,1x,i2)', ihr, imn, isc
	    hr[i] = ihr
	    mn[i] = imn
	    sc[i] = isc
	    ;PRINT, imm, idd, iyy
	ENDFOR

   ; julian date
	lines[0:nlat-1].jday = JULDAY( mm, dd, yy, hr, mn, sc )

	; day of year
	lines[0:nlat-1].doy = JULDAY( mm, dd, yy, hr, mn, sc )  - JULDAY( 1, 1, yy, 0, 0, 0 ) +1

   ; # of days this year
   daysthisyear =  JULDAY( 12, 31, yy, 0, 0, 0 )  - JULDAY( 1, 1, yy, 0, 0, 0 ) +1

   ; time stamp fractional hours this day : hh.fffffff
   lines[0:nlat-1].tstamp = double(hr) + (double(mn) + double(sc) /60.0d) /60.0d

   ; date + time stamp fractional days this year : ddd.ffffff
   lines[0:nlat-1].dstamp = yy + (lines[0:nlat-1].doy + lines[0:nlat-1].tstamp/24.D)/daysthisyear

   ; mjd2000 calculation for "datetime"

   ; calculate 1/1/2000 0:00:00UT
   m2000 = julday(1,1,2000, 00, 00, 00)

   ; measurement time in MJD2000
   lines[0:nlat-1].mjd2k = lines[0:nlat-1].jday - m2000


   ;PRINT, '    Date     DOY  Fit RMS   DOFS   SNR      Column      Column Err'
	;FOR i=0, nlat-1 DO BEGIN
	;	PRINT, lines[i].date, lines[i].doy, lines[i].rms, lines[i].dofs, lines[i].snr, $
	;	       lines[i].col, lines[i].cer, FORMAT='(a12, i4, 3(f8.3), 2(e13.4))'
	;ENDFOR

END
