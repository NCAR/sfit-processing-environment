PRO pltpbp4, PS=PS, ThickLines=ThickLines

; Feb 2012
; from oex...plot only pbpfile

; idl script to plot sfit2 output
; originally scripted in matlab now converted to idl
;adapted 18/3/2010 to add in total column amount from retrieval RB

	PRINT, ' Usage : oex, site="mlo | tab | acf", /ps, /thick, ftype= "B" | "L"'

	IF( NOT KEYWORD_SET( ThickLines )) THEN BEGIN
		PRINT, '  Main : keyword ThickLines  not set.'
		PRINT, '  Main : setting default ThickLines=0 -> use thin lines.'
		ThickLines = 0  		 ;  0 means thin lines, 1 means thick lines
	ENDIF

	IF( NOT KEYWORD_SET( FTYPE )) THEN BEGIN
		PRINT, '  Main : keyword FTYPE not set.'
		PRINT, '  Main : setting default FTYPE=B -> use Big Endian for Mac.'
		FTYPE = 'B'
	ENDIF

	IF( NOT KEYWORD_SET( PS )) THEN BEGIN
		PRINT, '  Main : keyword PS not set.'
		PRINT, '  Main : setting default PS=0 -> do not create ps output.'
		PS = 0
	ENDIF

	; ppos running position & id of last plot on screen
	ppos = INTARR(3)
	ppos = [ 10, 380, 0 ]			; work - double screens

	psiz = INTARR(2)
	psiz = [ 600, 465 ]
	psiz = [ 900, 700 ]

	FORWARD_FUNCTION readpbp, readnxn, readstat, readaevc, readkmf, readprfs
	FORWARD_FUNCTION plotpbp, plotprfs, plotak, plotaegv, blockplot, plotk, covarplot, plotbnr
	FORWARD_FUNCTION Exponent

	encap = 0
	plottop = 120

; Set up file names from LAPACK version sfit2 run
	setfilenames, pbpfile, stfile, akfile, kfile, smfile, ssfile, aefile, ptfile, shfile, prfile

; Read in pbpfile
	rc = 0
	rc = readpbp( pbp, pbpfile )

	IF( rc NE 0 ) THEN BEGIN
		PRINTF, -2,'Could not read pbp file: ', pbpfile
		RETURN
		STOP
	ENDIF

	; 0 = X, 1 = PS
	FOR toPS = 0 , PS DO BEGIN

		thick = 1.0
		IF toPS THEN BEGIN ;1
			SET_PLOT, 'PS'
			psfile = 'pltpbp.ps'
			PRINT, 'Saving ps file to : ', psfile
			DEVICE, /COLOR, /LANDSCAPE, $
			FILENAME = psfile, ENCAPSULATED = encap, BITS=8
			; full page PS

	      IF ThickLines THEN thick=3.5
			!P.CHARSIZE = 1
			!P.CHARTHICK = 4.0
			!X.THICK = thick
			!Y.THICK = thick
			stickthick = 8
			charsize = 2.
			lthick = thick
			fillcolor = 170
			tek = 0 ; black

		ENDIF ELSE BEGIN
			SET_PLOT,'X'
			DEVICE, DECOMPOSE = 0 ; allow for terminals with > 256 color

			IF ThickLines THEN thick=2.0
			!P.CHARSIZE = 1
			!P.CHARTHICK = 1
			!P.THICK = thick
			!X.THICK = thick
			!Y.THICK = thick
			stickthick = 1
			charsize = 1.5
			lthick = thick
			fillcolor = 0
			tek = 1 ; white

		ENDELSE

		; plot spectra
		rc = plotpbp( pbp, toPS, ppos, psiz, tek, lthick, summary, nsum, 'zzz' )

		; plot  profiles
		;c = plotprfs( stat, toPS, ppos, psiz, A.vmrscl, A.vmrunits, $
		;		tek, lthick, plottop, vmrng )

		; plot bnr file
		;rc = plotbnr( pbp, toPS, ppos, psiz, stickthick, plottop, ftype )

		IF( toPS ) THEN DEVICE, /CLOSE_FILE

	ENDFOR ; toPS

	PRINT,''
	PRINT, ' Mean VMR uncertainty  : ', muncert, FORMAT='(a, f7.2, "%" )'

	PRINT,''
	FOR i=0, nsum-1 DO PRINT, i, summary[i], FORMAT='(i2,2x,a)'

	PRINT, ' PLTPBP .DONE.', FORMAT='(/,a,/)'

END



; Plot bnr --------------------------------------------------------------------------


; Plot spectra --------------------------------------------------------------------

FUNCTION plotpbp, pbp, toPS, ppos, psiz, tek, lthick, summary, nsum, smol

	!P.MULTI = 2

	dfpos = FLTARR(4)
	sppos = FLTARR(4)
	ftpos = FLTARR(5); changed from 3 RB

	nfit = pbp[0].nfit

	TEK_COLOR
	FOR kk = 0, nfit-1 DO BEGIN

		; set up windows
		IF toPS THEN BEGIN

			dfpos = [0.12, 0.80, 0.93, 0.97]	; PS
			sppos = [0.12, 0.20, 0.93, 0.74]
;			ftpos = [ .00, .04, 0.08 ];RB
			ftpos = [0.00, .02, .04, .06, 0.08]
			hdpos = .76
			IF( kk NE 0 ) THEN ERASE

		ENDIF ELSE BEGIN

			dfpos[*] = [0.15, 0.78, 0.95, 0.95]	; X
			sppos[*] = [0.15, 0.20, 0.95, 0.72]
			;ftpos[*] = [ .02, .05, 0.08 ]; RB
			ftpos[*] = [ .00, .02, 0.04, 0.06, 0.08]
			hdpos = 0.74
			ppos = ppos + [ 20, -20, 1 ]

			WINDOW, ppos[2], RETAIN=2, XSIZE=psiz[0], YSIZE=psiz[1], 	$
				title = STRING( 'Plot ', ppos[2], $
				FORMAT = '(a,i02)') + ' : Spectral Fit : ' + string( kk+1, nfit, format='(i02,"/",i02)' ), $
				XPOS = ppos[0], YPOS = ppos[1]

		ENDELSE

		npt1 = pbp[kk].npt -1

		; set diff range
		mx = MAX( pbp[kk].difspc[0:npt1], MIN=mn )
		IF( ABS(mn) GT ABS(mx) ) THEN mx = mn
		!y.range = [ -ABS(mx), ABS(mx) ]

		titl = 'NCAR FTS Retrieval : ' + smol
		; plot difference on top
		PLOT, pbp[kk].wnu[0:npt1], pbp[kk].difspc[0:npt1],  	$
			POSITION = dfpos, YTICKS = 4, TITLE = titl,			$
			/NODATA, YTITLE='Difference', CHARSIZE = 1.4, 		$
			XTICKNAME = REPLICATE(' ',30), XTICKLEN = 0.08 ;	$
			;XTITLE = 'Wavenumber [cm!E-1!N]'

		OPLOT, !X.CRANGE, [0.0,0.0], COLOR = tek, THICK = lthick/2
		OPLOT, pbp[kk].wnu[0:npt1], pbp[kk].difspc[0:npt1], COLOR = 4, $
		THICK = lthick

		; calculate ymin and ymax for transmission plot
		omx = MAX( pbp[kk].obsspc[0:npt1], MIN=omn )
		cmx = MAX( pbp[kk].synspc[0:npt1], MIN=cmn )

		IF( omx GT cmx ) THEN BEGIN
			mx = omx
		ENDIF ELSE BEGIN
			mx = cmx
		ENDELSE

		IF( omn LT cmn ) THEN BEGIN
			mn = omn
		ENDIF ELSE BEGIN
			mn = cmn
		ENDELSE

		; set range and ticks on ordinate
		ymn = 5
		IF( mn GT 0.8 ) THEN mn = 0.8
		IF( mn EQ 0.8 ) THEN ymn = 2
		IF( mn LT 0.8 AND mn GE .4) THEN mn = 0.4
		IF( mn EQ 0.4 ) THEN ymn = 3
		;IF( mn LT 0.4 AND mn GE .2) THEN mn = 0.2
		IF( mn EQ 0.2 ) THEN ymn = 4
		IF( mn LT 0.2 ) THEN mn = 0.0
		IF( mn EQ 0.0 ) THEN ymn = 5
		IF( mx GT 1.0 ) THEN mx = 1.0

		!Y.RANGE=[mn,mx]
		;print, !y.range

		; plot spectra
		PLOT, pbp[kk].wnu[0:npt1], pbp[kk].obsspc[0:npt1],    $
			POSITION = sppos, YTICKS = 4,						$
			/NODATA, YTITLE='Transmission', CHARSIZE = 1.4, 	$
			XTICKLEN = 0.06, YSTYLE = 1, YMINOR = ymn,			$
			XTITLE = 'Wavenumber [cm!E-1!N]'

		IF( !Y.CRANGE[0] LT 0.0 ) THEN OPLOT, !X.CRANGE, [0.0,0.0], COLOR = tek

		OPLOT, pbp[kk].wnu[0:npt1], pbp[kk].obsspc[0:npt1], $
			COLOR = 3, THICK = lthick, /NOCLIP

		OPLOT, pbp[kk].wnu[0:npt1], pbp[kk].synspc[0:npt1], $
			COLOR = 2, THICK = lthick, /NOCLIP

		;legend = STRING( 'Observed', 'Fitted', 'Difference', FORMAT='(3a14)' )
		;print, legend
		XYOUTS, 0.12, hdpos, 'Observed', /NORMAL, COLOR = 3, CHARSIZE=1.7
		XYOUTS, 0.30, hdpos, 'Calculated', /NORMAL, COLOR = 2, CHARSIZE=1.7
		XYOUTS, 0.50, hdpos, 'Difference', /NORMAL, COLOR = 4, CHARSIZE=1.7

cz = 1.0
;	   XYOUTS, 0.5, ftpos[0], summary[3], /NORMAL, CHARSIZE=cz, ALIGNMENT = 0.5
;      XYOUTS, 0.5, ftpos[1], summary[2], /NORMAL, CHARSIZE=cz, ALIGNMENT = 0.5
;  	   XYOUTS, 0.5, ftpos[2], summary[4], /NORMAL, CHARSIZE=cz, ALIGNMENT = 0.5
;		XYOUTS, 0.5, ftpos[3], summary[1], /NORMAL, CHARSIZE=cz, ALIGNMENT = 0.5
;		XYOUTS, 0.5, ftpos[4], summary[nsum-1], /NORMAL, CHARSIZE=cz, ALIGNMENT = 0.5
		;XYOUTS, 0.5, ftpos[2], summary[nsum-1], /NORMAL, CHARSIZE=1.2, ALIGNMENT = 0.5

	ENDFOR

	RETURN, 0

END



; Read in pbpfile --------------------------------------------------------------------

FUNCTION readpbp, pbp, file

	maxpts = 262144L

	OPENR, lun, file, /GET_LUN, ERROR=ioerr
	IF( ioerr NE 0 ) THEN BEGIN
	PRINTF, -2, !ERR_STRING
	RETURN, 1
	ENDIF

	pbpstruct = { 					$
		tag     : '',           $
		nfit    : 0,				$
		zang    : 0,				$
		dnu     : 0.0d,				$
		npt     : 0L,				$
		nulo    : 0.0d,				$
		nuhi    : 0.0d,				$
		gndalt  : 0.0,				$
		wnu     : DBLARR(maxpts),	$
		obsspc  : FLTARR(maxpts),	$
		synspc  : FLTARR(maxpts),	$
		difspc  : FLTARR(maxpts) 	$
	}

   waverange = FLTARR(2)
	vec       = FLTARR( 12 )
	lvec      = FLTARR( 13 )
	string1   = ''
	zang      = 0L
	npt       = 0L
	dnu       = 0.0d
	nulo      = 0.0d
	nuhi      = 0.0d
	gndalt    = 0.0d
	nfits     = 0

	READF, lun, tag
	print, tag
	READF, lun, nfits
	pbp = REPLICATE( pbpstruct, nfits )
	pbp[0].nfit = nfits

   buf=''
   ;readf,lun, buf
   ;print, buf

	FOR kk = 0, nfits-1 DO BEGIN

; maybe this is read each block or maybe only at top...
      readf,lun, buf
      print, buf

		READF, lun, zang, dnu, npt, nulo, nuhi, gndalt
      print, zang, dnu, npt, nulo, nuhi, gndalt

		IF( npt GT maxpts ) THEN BEGIN
			PRINT, 'Spectral points in pbpfile: ', npt, ' is greater than size allocated: ', maxpts
			STOP
		ENDIF

		;PRINT, npt
      print, zang, dnu, npt, nulo, nuhi, gndalt
		pbp[kk].zang   = zang
		pbp[kk].dnu    = dnu
		pbp[kk].npt    = npt
		pbp[kk].nulo   = nulo
		pbp[kk].nuhi   = nuhi
		pbp[kk].gndalt = gndalt

		;HELP, pbp[kk].npt
		;HELP, npt
		nu  = FLTARR( npt )
		obs = FLTARR( npt )
		clc = FLTARR( npt )
		dif = FLTARR( npt )
		;HELP, obs

		rpt = FIX( npt/12 )
		rem = npt - rpt * 12
		nu( 0:npt-1 ) = FINDGEN( npt ) * dnu + nulo

		i = 0l
		j = 0l
		FOR i=0, rpt-1 DO BEGIN
			READF, lun, lvec
			FOR j=0,11 DO obs(i*12+j) = lvec(j+1)
			READF, lun, vec
			FOR j=0,11 DO clc(i*12+j) = vec(j)
			READF, lun, vec
			FOR j=0,11 DO dif(i*12+j) = vec(j)
		ENDFOR

		IF( rem gt 0 ) THEN BEGIN
			lrvec = FLTARR( rem+1 )
			rvec = FLTARR( rem )
			READF, lun, lrvec
			FOR j=0,rem-1 DO obs((rpt)*12+j) = lrvec(j+1)
			READF, lun, rvec
			FOR j=0,rem-1 DO clc((rpt)*12+j) = rvec(j)
			READF, lun, rvec
			FOR j=0,rem-1 DO dif((rpt)*12+j) = rvec(j)
		ENDIF

		pbp[kk].wnu[0:npt-1]    = nu
		pbp[kk].obsspc[0:npt-1] = obs
		pbp[kk].synspc[0:npt-1] = clc
		pbp[kk].difspc[0:npt-1] = dif ;* 100

	ENDFOR

	FREE_LUN, lun
	RETURN, 0

END



; Set file names  --------------------------------------------------------------------

PRO setfilenames, pbfile, stfile, akfile, kfile, smfile, ssfile, aefile, ptfile, shfile, prfile

; spectra, fit & difference 	: pbpfile
pbfile = 'pbpfile';

; profile & apriori				: statevec
stfile = 'statevec';

; averaging kernels				: AK.out
akfile = 'AK.out'

; Jacobian						: k.out
kfile  = 'K.out';

; smoothing error				: SS.out
ssfile = 'SS.out';

; measurement error				: SM.out
smfile = 'SM.out';

; eiganvectors					: AEIGEN.out
aefile = 'AEIGEN.out';

; pressure-temperature 			; fasc.pt
ptfile = 'fasc.pt'

; comments						; summary.st
shfile = 'summary.st';

; profiles - nostly need Z boundries						; summary.st
prfile = 'PRFS.out';

;PRINT, pbfile, stfile, akfile, kfile, smfile, ssfile, aefile, ptfile, shfile

msfile = 'fasc.ms'
mxfile = 'fasc.mx'
cifile = 'cinput';
asfile = 'A-S.out';

END




	;STOP
		;	color table 5				TEK_COLOR
		; color on screen,   on ps 		on screen		on PS
		;  	0		black 				0				1
		;	50		blue				4				4
		;  	80		purple				6				6
		;  	100		red					2				2
		;  	150 	yellow
		;	200		orange
		;	230		pale yellow
		;	180		yellow green
		;  	255		white				1				0
		;			green				3				3
		;  			teal				5				5


FUNCTION Exponent, axis, index, number

	; A special case.
	IF number EQ 0 THEN RETURN, '0'

	; Assuming multiples of 10 with format.
	ex = String(number, Format='(e8.0)')
	pt = StrPos(ex, '.')

	first = StrMid(ex, 0, pt)
	sign = StrMid(ex, pt+2, 1)
	thisExponent = StrMid(ex, pt+3)

	;print, number, ex, first
	;help, first, sign

	; Shave off leading zero in exponent
	WHILE StrMid(thisExponent, 0, 1) EQ '0' DO thisExponent = StrMid(thisExponent, 1)

	; Fix for sign and missing zero problem.
	IF (Long(thisExponent) EQ 0) THEN BEGIN
		sign = ''
		thisExponent = '0'
	ENDIF

	; Make the exponent a superscript.
	IF sign EQ '-' THEN BEGIN

	IF( STRTRIM(first,2) EQ '1' ) THEN BEGIN
		RETURN, '10!U' + sign + thisExponent + '!N'
	ENDIF ELSE BEGIN
		RETURN, first + 'x10!U' + sign + thisExponent + '!N'
	ENDELSE

	ENDIF ELSE BEGIN
	IF STRTRIM(first,2) EQ '1' THEN BEGIN
		IF STRTRIM(thisExponent,2) EQ '0' THEN RETURN, '1'
		IF STRTRIM(thisExponent,2) EQ '1' THEN RETURN, '10'
		RETURN, '10!U' + thisExponent + '!N'
		ENDIF ELSE BEGIN
			RETURN, first + 'x10!U' + thisExponent + '!N'
		ENDELSE
	ENDELSE


	END