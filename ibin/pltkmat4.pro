pro pltkmat4, ps=ps, thicklines=thicklines, big=big, file=file, wind=wind

; idl script to plot sfit2 output
; originally scripted in matlab now converted to idl
;adapted 18/3/2010 to add in total column amount from retrieval rb

forward_function plotk
funcs = [ 'readpbp4', 'readstat4','readkmat4' ]
resolve_routine, funcs, /either


print, ' usage : pltkmat4, /ps, /thick, /big'

if( not keyword_set( thicklines )) then begin
   print, '  main : keyword thicklines  not set.'
   print, '  main : setting default thicklines=0 -> use thin lines.'
   thicklines = 0  		 ;  0 means thin lines, 1 means thick lines
endif

if( not keyword_set( ps )) then begin
   print, '  main : keyword ps not set.'
   print, '  main : setting default ps=0 -> do not create ps output.'
   ps = 0
endif

if( not keyword_set( file )) then begin
   print, '  main : keyword file not set.'
   kfile = 'k.output'
   print, '  main : setting default file : ', kfile
endif else kfile = file

if( not keyword_set( wind )) then begin
   print, '  main : keyword wind not set.'
   print, '  main : setting default wind=0.'
   wind = 0
endif

ppos = intarr(3)
psiz = intarr(2)
if( keyword_set( big )) then begin
   ppos = [ 10, 920, wind ]		; dual display
   psiz = [ 1000, 750 ]       ; dual display
endif else begin
   ppos = [ 10, 390, wind ]		; mbp - retina
   psiz = [ 760, 500 ]			; mbp - retina
endelse

encap   = 0
plottop = 120

; Read in K matrix file
rc = 0
rc = readkmat4( kmf, kfile )
;HELP, kmf
IF( rc NE 0 ) THEN BEGIN
   PRINTF, -2,'Could not read K file: ', kfile
   STOP
ENDIF

rc = 0
pbpfile = 'pbpfile'
rc = readpbp4( pbp, pbpfile )
;HELP, pbp
IF( rc NE 0 ) THEN BEGIN
   PRINTF, -2,'Could not read pbpfile: ', pbpfile
   STOP
ENDIF

rc = 0
; read in statevector file
rc = 0
stfile = 'statevec'
rc = readstat4( stat, stfile )
IF( rc NE 0 ) THEN BEGIN
   PRINTF, -2,'Could not read statevec: ', statevec
   STOP
ENDIF


	; 0 = X, 1 = PS
	FOR toPS = 0 , PS DO BEGIN

		thick = 1.0
		IF toPS THEN BEGIN ;1
			SET_PLOT, 'PS'
			psfile = 'oex.ps'
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


			; 2d countour of K matrix
		rc = plotk( kmf, stat, pbp, toPS, ppos, psiz, stickthick, plottop )

		IF( toPS ) THEN DEVICE, /CLOSE_FILE

	ENDFOR ; toPS


return
end


; Contour plot K Matrix ------------------------------------------------------------------

FUNCTION plotk, kmf, stat, pbp, toPS, ppos, psiz, stickthick, plottop

	nfit = pbp[0].nfit
	!P.MULTI = [nfit+1,nfit,nfit,0,0]

	cbpos = FLTARR(4)
	ctpos = FLTARR(4)

	; set up windows
	IF toPS THEN BEGIN

		ERASE
		cbpos = [0.20, 0.92, 0.80, 0.97]	; PS
		ctpos = [0.12, 0.10, 0.93, 0.83]
		ftpos = [ .00, .04, 0.08 ]
		xcharsz = 1.3
		ycharsz = 1.8

	ENDIF ELSE BEGIN

		ppos = ppos +  [ 20,  -20, 1 ]
		print, ppos
		WINDOW, ppos[2], RETAIN=2, XSIZE=psiz[0], YSIZE=psiz[1],	$
			title= STRING( 'Plot ', ppos[2], FORMAT='(a,i02)') + ' : K Matrix',	$
			XPOS = ppos[0], YPOS = ppos[1]
		;!P.CHARSIZE = 1.2
		DEVICE, DECOMPOSE = 0  ; allow for terminals with > 256 color
		cbpos = [0.20, 0.87, 0.90, 0.92]	; X
		ctpos = [0.10, 0.10, 0.95, 0.80]
		ftpos = [0.02, 0.05, 0.08 ]
		xcharsz = 1.3
		ycharsz = 1.3

	ENDELSE

	nlev = kmf.nlev
	ismx = kmf.ismx
	npts = kmf.npts

	; kmat is npar x npts
   ;help, kmf.mat
   mat = transpose(kmf.mat)
   ;help, mat

   ; plot low to high altitudes
	mat  = -REVERSE( mat[ 0:npts-1, ismx:ismx+nlev-1 ], 2); *1000.0

	title = ' Jacobian Matrix : ' + STRING( nlev, npts, FORMAT='( i2,"x",i5 )' )

	div = 0
	WHILE( MAX( mat ) GT 10. ) DO BEGIN
		div = div -1
		mat = mat / 10.
	ENDWHILE

	WHILE( MAX( mat ) LT 1. ) DO BEGIN
		div = div +1
		mat = mat * 10.
	ENDWHILE

	z = stat.z

	; set up contours
	ndiv = 7
	nclr = 240
	scal = 1.0
	span = MAX(mat)/scal - MIN(mat) + 0.0*(MAX(mat) - MIN(mat))
	clvs = MIN(mat) - 0.0*span + INDGEN( nclr +1 ) * span/(nclr -1)

	IF( NOT toPS ) THEN PRINT, ' Min, Max of contour levels             : ', MIN( clvs ), MAX( clvs )
	IF( NOT toPS ) THEN PRINT, ' Number of contour divisions in colorbar : ', ndiv
	IF( NOT toPS ) THEN PRINT, ' Number of color levels in contour plot  : ', nclr

	; define contours names for color table ticks
	cbtics = STRARR( ndiv + 1 )
	FOR i = 0, ndiv DO BEGIN
		cbtics[i] = STRING( clvs[i*(nclr/ndiv)], FORMAT = '(f7.3)' )
		;PRINT, i, nclr/ndiv, nclr/ndiv*i, clvs[i*(nclr/ndiv)], cbtics[i]
	END

	; tell max and min out of range
	FOR i=0, nlev-1 do begin
		FOR j=0, nlev-1 do begin
			IF mat[j,i] LT MIN( clvs ) THEN PRINT, 'less : ', j, i, mat[j,i]
			IF mat[j,i] GT MAX( clvs ) THEN PRINT, 'more : ', j, i, mat[j,i]
		END
	END

; CONTOUR - set up the plot window
	; colorbar at top

	LOADCT, 5, NCOLORS = nclr, /SILENT ;, BOTTOM=20
	cbtitle = title + ' [x10!E' + STRING( div, FORMAT='(i+2)' ) + '!N]'
	COLORBAR, NCOLORS = nclr-40, POSITION = cbpos, CHARSIZE=1.5,	$
		DIVISIONS = ndiv, TICKNAMES = cbtics, TITLE = cbtitle

	offset = 0
	pointoff = 0
	pwidth = ctpos[2] - ctpos[0]
	thispos = FLTARR(4)
	thistic = FLTARR(8)

	;Tick step size for major ticks. ie 1 = every wavenumber
	tick_interval = 1
	minor = 10

	FOR kk = 0, nfit-1 DO BEGIN

		thispos = ctpos
		pratio = FLOAT( pbp[kk].npt ) / FLOAT( npts	)

		pw = pratio * pwidth

		thispos[0] = ctpos[0] + offset
		thispos[2] = ctpos[0] + offset + pw
		offset = offset + pw

		IF( kk EQ 0 ) THEN BEGIN
			thispos[2] = thispos[2] - 0.01
		ENDIF ELSE IF( kk EQ nfit -1 ) THEN BEGIN
			thispos[0] = thispos[0] + 0.01
		ENDIF ELSE BEGIN
			thispos[2] = thispos[2] - 0.0005
			thispos[0] = thispos[0] + 0.0005
		ENDELSE

		npt      = pbp[kk].npt
		x        = pbp[kk].wnu[0:npt-1]
		thismat   = mat[ pointoff:pointoff+npt-1, * ]
		pointoff  = pointoff + npt

      nulo = pbp[kk].nulo
      nuhi = pbp[kk].nuhi
      IF( NOT toPS ) THEN PRINT, ' wv # range : ', kk, nulo, nuhi, pw

      leftmost_tick = floor(nulo / tick_interval)*tick_interval + tick_interval
      rightmost_tick = floor(nuhi / tick_interval)*tick_interval

      num_ticks = (rightmost_tick - leftmost_tick) / tick_interval + 1
      if (not toPS) then begin
         print, 'number of major ticks: ',num_ticks
         if (num_ticks eq 1) then begin
            print, 'Warning: only 1 major tick for interval, no minor tick marks will show'
         endif
         if (num_ticks eq 0) then begin
            print, 'Warning: no major ticks for interval, no major or minor tick marks will show'
         endif
      endif

      ;Set character size along y-axis to have characters only for left-most plot
      ys = 0
      IF( kk eq 0 ) THEN BEGIN
      ys = ycharsz
      ENDIF ELSE BEGIN
      ys = 0.0001;Small enough to suppress characters showing up
      ;If set to 0, IDL scales to a small, but visible size
      ENDELSE

      CONTOUR, thismat, x, z, POSITION = thispos, NLEVELS = nclr-40,$
         YRANGE = [0.0, plottop], /FILL,$
         CHARSIZE = charsz, YTICKLEN = -0.02, XTICKLEN = -0.02,$
         YTITLE = 'Altitude [km]', xtitle = '', XCHARSIZE = xcharsz,$
         YCHARSIZE = ys,$
         XRANGE = [nulo,nuhi],$
         XSTYLE = 1,$
         XTICKINTERVAL = tick_interval,$
         XMINOR = minor

	ENDFOR

	xtitl = 'Wavenumber [cm!E-1!N]'
	XYOUTS, 0.5, ftpos[0], xtitl, /NORMAL, CHARSIZE=1.2, ALIGNMENT = 0.5

	RETURN, 0

END

