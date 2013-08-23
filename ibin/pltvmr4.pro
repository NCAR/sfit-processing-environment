pro pltvmr4, ps=ps, thicklines=thicklines, big=big, dir=dir

	;print, ' usage : pltvmr4, /ps, /thick'

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

	; ppos running position & id of last plot on screen
   ppos = intarr(3)
   psiz = intarr(2)
	if( keyword_set( big )) then begin
      ppos = [ 10, 660, 0 ]		; dual display
      psiz = [ 1000, 750 ]       ; dual display
	endif else begin
      ppos = [ 10, 390, 0 ]		; mbp - retina
      psiz = [ 760, 500 ]			; mbp - retina
   endelse

   forward_function setfilenames, exponent, plotprfs

   funcs = [ 'readstat4' ]
   resolve_routine, funcs, /either

	encap = 0
	plottop = 120

; read in sfit4.ctl file
	rc = 0
	ctlfile = 'sfit4.ctl'
	if( keyword_set( dir ) )then ctlfile=dir + ctlfile
	rc = readsctl4( ctl, ctlfile )
	if( rc ne 0 ) then begin
		printf, -2,'could not read sfit4.ctl file: ', ctlfile
		stop
	endif

   ; read in statevector file
   rc = 0
   stfile = ctl.statevec
   rc = readstat4( stat, stfile )
   if( rc ne 0 ) then begin
      printf, -2,'could not read statevec: ', statevec
      stop
   endif

   print, ''
   if( stat.ngas GT 0 )then print, stat.ngas, transpose(stat.gas[0,0:stat.ngas-1])

   stlfile = ctl.stalayers
   nlev =  readlayr( stgrd, stlfile )

	; 0 = x, 1 = ps
	for tops = 0 , ps do begin

		thick = 1.0
		if tops then begin ;1
			set_plot, 'ps'
			psfile = 'pltvmr4.ps'
			print, 'saving ps file to : ', psfile
			device, /color, /landscape, $
			filename = psfile, encapsulated = encap, bits=8
			; full page ps

	      if thicklines then thick=3.5
			!p.charsize = 1
			!p.charthick = 4.0
			!x.thick = thick
			!y.thick = thick
			stickthick = 8
			charsize = 2.
			lthick = thick
			fillcolor = 170
			tek = 0 ; black

		endif else begin
			set_plot,'x'
			device, decompose = 0 ; allow for terminals with > 256 color

			if thicklines then thick=2.0
			!p.charsize = 1
			!p.charthick = 1
			!p.thick = thick
			!x.thick = thick
			!y.thick = thick
			stickthick = 1
			charsize = 1.5
			lthick = thick
			fillcolor = 0
			tek = 1 ; white

		endelse

		; plot  profiles
		for ii=0 , stat.ngas-1 do begin

		  rc = plotprfs( ii, stat, stgrd, tops, ppos, psiz, tek, lthick, plottop )

      endfor

      if( stat.iftm )then rc = plott( stat, stgrd, tops, ppos, psiz, tek, lthick, plottop )

		; plot bnr file
		;rc = plotbnr( pbp, tops, ppos, psiz, stickthick, plottop, ftype )

		if( tops ) then device, /close_file

	endfor ; tops

	print, ' pltvmr4 .done.', format='(/,a,/)'

end


; Plot Smooth & Measurement error, profiles --------------------------------------------------------------------
FUNCTION plott, stat, stgrd, tops, ppos, psiz, tek, lthick, plottop

	; set up windows
	tek_color
	IF toPS THEN BEGIN
		ERASE
		!P.CHARSIZE = 1.6
		chrsz = 1.5
	ENDIF ELSE BEGIN
		ppos = ppos +  [ 20,  -20, 1 ]
		WINDOW, ppos[2], RETAIN=2, XSIZE=psiz[0], YSIZE=psiz[1], 	$
			title= STRING( 'Plot ', ppos[2], FORMAT='(a,i02)') + ' : Temperature Retrieval',  $
			XPOS = ppos[0], YPOS = ppos[1]
		!P.CHARSIZE = 1.6
		chrsz = 1.5
	ENDELSE

   !P.MULTI = [ 0,0,0,0,0 ]

	z     = stat.z
	dex   = where(z LE plottop, cnt)
	if( cnt EQ 0 )then stop, 'plotprf & z & plottop'
	nlev  = stgrd.k

   ; calculate ymin and ymax for transmission plot
   omx = max( stat.t,  min=omn )
   cmx = max( stat.tr, min=cmn )
   mx = cmx
   if( omx gt cmx ) then mx = omx
   mn = cmn
   if( omn lt cmn ) then mn = omn

   PLOT, stat.t, z[dex], /NODATA, YRANGE=[0.0, plottop], XRANGE=[mn,mx], $
      YTITLE = 'Altitude [km]', YTICKLEN = 0.06, XTICKLEN = 0.03,     	 $
      XTITLE = 'Temperature ', $
      TITLE  = 'Temperature', CHARSIZE=chrsz

   OPLOT, stat.tr, z[dex], COLOR = 2, THICK = lthick
   OPLOT, stat.t,  z[dex], COLOR = 3, THICK = lthick

	RETURN, 0

END


; Plot Smooth & Measurement error, profiles --------------------------------------------------------------------
FUNCTION plotprfs, ii, stat, stgrd, tops, ppos, psiz, tek, lthick, plottop

	; set up windows
	tek_color
	IF toPS THEN BEGIN
		ERASE
		!P.CHARSIZE = 1.6
		chrsz = 1.5
	ENDIF ELSE BEGIN
		ppos = ppos +  [ 20,  -20, 1 ]
		WINDOW, ppos[2], RETAIN=2, XSIZE=psiz[0], YSIZE=psiz[1], 	$
			title= STRING( 'Plot ', ppos[2], FORMAT='(a,i02)') + ' : aPriori and Retrieved VMRs',  $
			XPOS = ppos[0], YPOS = ppos[1]
		!P.CHARSIZE = 1.6
		chrsz = 1.5
	ENDELSE

	!P.MULTI = [ 0, 2, 1 ]
	if( stat.iftm )then 	!P.MULTI = [ 0, 3, 1 ]

	z     = stat.z
	dex   = where(z LE plottop, cnt)
	if( cnt EQ 0 )then stop, 'plotprf & z & plottop'

	avmr  = stat.vmr[0,ii,dex] ;* vmrscl
	vmr   = stat.vmr[1,ii,dex] ;* vmrscl
	nlev  = stgrd.k
   ucmol = stat.gas[0,ii]
print, ucmol
	; calculate ymin and ymax for profiles plot
	omx = MAX( vmr,  MIN=omn )
	cmx = MAX( avmr, MIN=cmn )
	IF (omx GT cmx) THEN BEGIN
		mx = omx
	ENDIF ELSE BEGIN
		mx = cmx
	ENDELSE
	IF (omn LT cmn) THEN BEGIN
		mn = omn
	ENDIF ELSE BEGIN
		mn = cmn
	ENDELSE

   scl = 1.
   while( mx LT 1. ) do begin
      scl = scl * 10.
      mx  = mx * 10.
      mn  = mn * 10.
   endwhile
   ex     = alog10(scl)
print, ex, scl

	; plot vmrs log
	PLOT, vmr*scl, z[dex], /XLOG, /NODATA, YRANGE=[0.0, plottop], XRANGE=[mn,mx], $
		YTITLE = 'Altitude [km]', YTICKLEN = 0.06, XTICKLEN = 0.03, 	$
		XTITLE = 'Mixing Ratio for ' + ucmol + ' *10!U ' + string(ex,format='(i02)'), $
		TITLE = 'Mixing Ratio', CHARSIZE=chrsz, XTICKFORMAT = 'exponent'

	OPLOT, vmr*scl,  z[dex], COLOR = 2, THICK = lthick
	OPLOT, avmr*scl, z[dex], COLOR = 3, THICK = lthick

	XYOUTS, 0.67, 0.55, 'Retrieved VMR', /NORMAL, COLOR = 2, CHARSIZE=1.5, ORIENTATION = 90
	XYOUTS, 0.67, 0.25, 'A Priori VMR',  /NORMAL, COLOR = 3, CHARSIZE=1.5, ORIENTATION = 90

	; plot vmrs linear
	PLOT, vmr*scl, z[dex], /NODATA, YRANGE=[0.0, plottop], XRANGE=[mn,mx], $
		YTITLE = 'Altitude [km]', YTICKLEN = 0.06, XTICKLEN = 0.03, 	$
		XTITLE = 'Mixing Ratio for ' + ucmol + ' *10!U ' + string(ex,format='(i02)'), $
		TITLE  = 'Mixing Ratio', CHARSIZE=chrsz ;XTICKFORMAT = 'exponent'

	OPLOT, vmr*scl,  z[dex], COLOR = 2, THICK = lthick
	OPLOT, avmr*scl, z[dex], COLOR = 3, THICK = lthick


;   if( stat.iftm )then begin
;      mn = 0.
;      mx = 0.
;      PLOT, stat.t, z[dex], /NODATA, YRANGE=[0.0, plottop], XRANGE=[mn,mx], $
;         YTITLE = 'Altitude [km]', YTICKLEN = 0.06, XTICKLEN = 0.03, 	$
;         XTITLE = 'Temperature ', $
;         TITLE = 'Temperature', CHARSIZE=chrsz ;XTICKFORMAT = 'exponent'
;
;      OPLOT, stat.tr, z[dex], COLOR = 2, THICK = lthick
;      OPLOT, stat.t,  z[dex], COLOR = 3, THICK = lthick

;   endif

	RETURN, 0

END

