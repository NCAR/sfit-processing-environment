pro oex4, site=site, ps=ps, nsm=nsm, ftype=ftype, thicklines=thicklines, big=big, dir=dir

; idl script to plot sfit4 output
; originally scripted in matlab now converted to idl
; adapted 18/3/2010 to add in total column amount from retrieval RB

; August 2013
; plots gas files not just pbpfile, vmr including T if its retrieved & k matrix
; reads in sfit 4 output
; still to do error matrix, bnr file

   ;close,/all

	FORWARD_FUNCTION plotak, plotaegv, plotk, covarplot, plotbnr, readgasf, plotprfs
	FORWARD_FUNCTION plotgases

   funcs = [ 'readt154', 'readstat4', 'usemol', 'readnxn4', 'readlayr','readpbp4', 'exponent', 'readsctl4' ]
   resolve_routine, funcs, /either

	PRINT, ' Usage : oex, site="mlo | tab | acf", /ps, /nsm, /thick, ftype= "B" | "L"'

	IF( NOT KEYWORD_SET( site )) THEN BEGIN
		PRINT, '  Main : keyword SITE not set...stop'
      STOP
	ENDIF

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

	IF( NOT KEYWORD_SET( NSM )) THEN BEGIN
		PRINT, '  Main : keyword NSM not set.'
		PRINT, '  Main : setting default NSM=0 -> plot smoothing error figure.'
		NSM = 0
	ENDIF

	IF( NOT KEYWORD_SET( PS )) THEN BEGIN
		PRINT, '  Main : keyword PS not set.'
		PRINT, '  Main : setting default PS=0 -> do not create ps output.'
		PS = 0
	ENDIF

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

; read summary file
   rc = 0
   smmfile = ctl.summary
	if( keyword_set( dir ) )then smmfile = dir + smmfile
   rc = readsum4( smf, smmfile )
   if( rc ne 0 ) then begin
      printf, -2,'could not read summary file: ', smmfile
      stop
   endif

; read in pbpfile - local to sfit4.cfl
	rc = 0
	pbpfile = ctl.pbpfile
	if( keyword_set( dir ) )then pbpfile = dir + pbpfile
	rc = readpbp4( pbp, pbpfile )
	if( rc ne 0 ) then begin
		printf, -2,'could not read pbp file: ', pbpfile
		return
		stop
	endif

; read in statevector file - local to sfit4.ctl
	rc = 0
	stfile = ctl.statevec
	if( keyword_set( dir ) )then stfile = dir + stfile
	rc = readstat4( stat, stfile )
	if( rc ne 0 ) then begin
		printf, -2,'could not read st file: ', stfile
		stop
	endif

; get site and gas info
   ;if( stat.ngas gt 0 )then print, stat.ngas, transpose(stat.gas[0,0:stat.ngas-1])
	ucmol = strupcase( stat.gas[0,0] )
	usite = strupcase( site)
   usemol, usite, ucmol, a

; get grid data
   nlev =  readlayr( stgrd, ctl.stalayers)

; read in k matrix file
	rc = 0
	kfile = ctl.k_matrix
	if( keyword_set( dir ) )then kfile = dir + ctl.k_matrix
	rc = readkmat4( kmf, kfile )
	if( rc ne 0 ) then begin
		printf, -2,'could not read k file: ', kfile
		stop
	endif

; Read in Averaging kernels file
	rc = 0
   akfile = ctl.ak_matrix
	if( keyword_set( dir ) )then akfile = dir + ctl.ak_matrix
	rc = readnxn4( ak, akfile )
	if( rc ne 0 ) then begin
		printf, -2,'could not read ak file: ', akfile
		stop
	endif

; Read in t15asc file
	rc = 0
   t15file = ctl.spectrum
	if( keyword_set( dir ) )then t15file = dir + ctl.spectrum
	rc = readt154( t15, t15file )
	if( rc ne 0 ) then begin
		printf, -2,'could not read ak file: ', t15file
		stop
	endif

	bnrfile = strtrim(string(t15.tstmp[0]),2) + '.bnr'
	if( keyword_set( dir ) )then bnrfile = dir + bnrfile


; Read in Smoothing Error file
;	rc = 0
;	rc = readnxn( sserr, ssfile )
;
;	IF( rc NE 0 ) THEN BEGIN
;		PRINTF, -2,'Could not read ss file: ', ssfile
;		STOP
;	ENDIF

; Read in Measurement Error file
;	rc = 0
;	rc = readnxn( smerr, smfile )
;
;	IF( rc NE 0 ) THEN BEGIN
;		PRINTF, -2,'Could not read sm file: ', smfile
;		STOP
;	ENDIF

	; 0 = X, 1 = PS
	FOR toPS = 0 , PS DO BEGIN

		thick = 1.0
		IF toPS THEN BEGIN ;1
			set_plot, 'ps'
			;!p.font = 0
			psfile = 'oex.ps'
			if( keyword_set( dir ) )then psfile = dir + psfile
			print, 'saving ps file to : ', psfile
			;device, /color, /landscape, /helvetica, filename = psfile, encapsulated = encap, bits=8
			device, /color, /landscape, /helvetica, filename = psfile, encapsulated = encap, bits=8
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
			!p.font = -1
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

      ; plot vmr profiles from statevector
      for ii=0 , stat.ngas-1 do begin
		  rc = plotprfs( ii, stat, stgrd, tops, ppos, psiz, tek, lthick, plottop )
      endfor

      ; if temperature retrieval plot it
      if( stat.iftm )then rc = plott( stat, stgrd, tops, ppos, psiz, tek, lthick, plottop )

		; 2d countour of K matrix
		rc = plotk( kmf, stat, smf, toPS, ppos, psiz, stickthick, plottop )

		; plot Smooth & Measurement error, profiles
		;rc = ploterrs( sserr, smerr, stat, kmf, toPS, ppos, psiz, A.vmrscl, A.vmrunits, $
		;		tek, lthick, plottop, rms, vmrng )

		; plot averaging kernels
		rc = plotak( ak, stat, toPS, ppos, psiz, tek, lthick, plottop, usite, auc )

		; plot averaging kernels
		;rc = plotak( ak, stat, toPS, ppos, psiz, tek, lthick, plottop, usite, auc, /nrm )

		; plot bnr file
		rc = plotbnr( pbp, bnrfile, toPS, ppos, psiz, stickthick, plottop, ftype )

      ; print summary file
      rc = prntsum( smf, toPS, ppos, psiz )

		; plot spectra
      rc = plotgases( pbp, toPS, ppos, psiz, tek, lthick, summary, stat, A.mol, dir )


		IF( toPS ) THEN DEVICE, /CLOSE_FILE

	ENDFOR ; toPS

	PRINT, ' OEX .DONE.', FORMAT='(/,a,/)'

END


; Print out retrieval details to a plot window
function prntsum, smf, toPS, ppos, psiz

	; set up windows
	tek_color
	if tops then begin
		erase
		!p.charsize = 1.
		chrsz = 1.
	endif else begin
		ppos = ppos +  [ 20,  -20, 1 ]
		window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1], 	$
			title= string( 'plot ', ppos[2], format='(a,i02)') + ' : Retrieval Summary',  $
			xpos = ppos[0], ypos = ppos[1]
		!p.charsize = 1.2
		chrsz = 1.
	endelse

    y = 0.9
    x = 0.03
    xyouts, x, y, smf.ver, /normal

    xyouts, x+0.4, y, smf.tag, /normal

    y = y - 0.05
    for j=0, smf.nfit-1 do xyouts, x, y-j*0.03, 'Fit :' + string(j+1,format='(i3,1x)') + smf.shead[j], /normal

    y = y - 0.05
    xyouts, x, y, smf.hret, /normal
    y = y - 0.03
    for j=0, smf.nret-1 do xyouts, x, y-j*0.03, smf.sret[j], /normal

    y = y - (smf.nret-1)*0.03 - 0.05
    pos = strpos( smf.hbnd, 'NSCAN' )
    xyouts, x, y, strmid(smf.hbnd,0,pos+5), /normal
    for j=0, smf.nbnd-1 do begin
      y = y - 0.03
      xyouts, x, y, smf.sbnd[j], /normal
      if( j eq 0 )then begin
         y = y - 0.03
         xyouts, x, y, '        ' + strmid(smf.hbnd,pos+5, strlen( smf.hbnd )), /normal
      endif
      for k = 0, smf.nscn[j]-1 do begin
          y = y - 0.03
         xyouts, x, y, '              ' + strtrim(smf.sjscn[k], 2 ), /normal
       endfor
    endfor

    y = y - 0.05
    xyouts, x, y, strtrim(smf.hprm,2), /normal
    y = y - 0.03
    xyouts, x, y, strtrim(smf.sprm,2), /normal


return, 0
end




; Plot Temperature profile  --------------------------------------------------------------------
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


; Plot VMR profiles --------------------------------------------------------------------

FUNCTION plotprfs, ii, stat, stgrd, tops, ppos, psiz, tek, lthick, plottop

	; set up windows
	tek_color
	IF toPS THEN BEGIN
		ERASE
		!P.CHARSIZE = 1.
		chrsz = 1.2
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


; plot spectra --------------------------------------------------------------------

function plotgases, pbp, tops, ppos, psiz, tek, lthick, summary, stat, mol, dir

   suffix = 'final'

	!p.multi = 2

	dfpos = fltarr(4)
	sppos = fltarr(4)
	ftpos = fltarr(5); changed from 3 rb

	nfit  = pbp[0].nfit
   nband = pbp[0].nband
   ngas = stat.ngas

   if( ngas EQ 0 )then smol = '' else $ smol = stat.gas[0,0]

	tek_color
	print, ' # fits to plot : ', nfit, ' in : ', nband, ' bands'
	for kk = 0, nfit-1 do begin

      iband = pbp[kk].idex[0]
      jscan = pbp[kk].idex[1]
      ngasb = pbp[kk].idex[2]

		; set up windows
		if tops then begin

         erase
         !p.charsize = 1.
         chsize = 1.2
         lcsz = 1.0
         right = 0.90
         dsbrk = 0.77
         difmd = 0.86
			dfpos = [0.12, dsbrk+0.01, right, 0.97]	; ps
			sppos = [0.12, 0.20, right, dsbrk ]
			ftpos = [0.00, .02, .04, .06, 0.08]
			hdpos = .90
			if( kk ne 0 ) then erase

		endif else begin

         !p.charsize = 1.0
         chsize = 1.4
         lcsz = 1.4
         right = 0.90
         difmd = 0.86
         dsbrk = 0.77
			dfpos[*] = [0.08, dsbrk+0.01, right, 0.95 ]	; x
			sppos[*] = [0.08, 0.08, right, dsbrk ]
			ftpos[*] = [ .00, .02, 0.04, 0.06, 0.08]
			hdpos    = 0.95
			ppos     = ppos + [ 20, -20, 1 ]

			window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1], 	$
				title = string( 'plot ', ppos[2], $
				format = '(a,i02)') + ' : spectral fit : ' + string( kk+1, nfit, format='(i02,"/",i02)' ), $
				xpos = ppos[0], ypos = ppos[1]

		endelse

		npt1 = pbp[kk].npt -1

		; set diff range
		difs = 100.* pbp[kk].difspc[0:npt1]
		mx = max( difs, min=mn )
		if( abs(mn) gt abs(mx) ) then mx = mn
		!y.range = [ -abs(mx), abs(mx) ]

		rms = moment( difs )
		if( stat.ngas EQ 0 )then gases = '' else $
		   gases = string( transpose( stat.gas[0,0:stat.ngas-1]), /print )

		titl = 'FTS Retrieval : ' + gases + string( ', %rms=',sqrt(rms[1]),format='(a,f6.3)')

		; plot difference on top from pbpfile
		plot, pbp[kk].wnu[0:npt1], difs, position = dfpos, yticks = 4, title = titl,   $
			/nodata, ytitle='% difference', charsize = chsize, xtickname = replicate(' ',30), xticklen = 0.08, $
			xstyle=1 ;	$
			;xtitle = 'wavenumber [cm!e-1!n]'

		oplot, pbp[kk].wnu[0:npt1], difs, color = 4,	thick = lthick
		xyouts, right+0.01, difmd+0.003, 'OBS-CALC', /normal, color = 4, charsize=lcsz
		oplot, !x.crange, [0.0,0.0], color = tek, thick = lthick/2

		; calculate ymin and ymax for transmission plot
		omx = max( pbp[kk].obsspc[0:npt1], min=omn )
		cmx = max( pbp[kk].synspc[0:npt1], min=cmn )

		if( omx gt cmx ) then begin
			mx = omx
		endif else begin
			mx = cmx
		endelse

		if( omn lt cmn ) then begin
			mn = omn
		endif else begin
			mn = cmn
		endelse

		; set range and ticks on ordinate
		ymn = 5
		if( mn gt 0.8 ) then mn = 0.8
		if( mn eq 0.8 ) then ymn = 2
		if( mn lt 0.8 and mn ge .4) then mn = 0.4
		if( mn eq 0.4 ) then ymn = 3
		;if( mn lt 0.4 and mn ge .2) then mn = 0.2
		if( mn eq 0.2 ) then ymn = 4
		if( mn lt 0.2 ) then mn = 0.0
		if( mn eq 0.0 ) then ymn = 5
		if( mx gt 1.0 ) then mx = 1.0

      omx      = mx
      yoff     = 0.05*(mx-mn)
      yoff     = 0.02*(ngasb+1)*(mx-mn)
      mx       = mx + (ngasb+1)*yoff +0.005
		!y.range = [mn,mx]

		; plot spectra
      tickv = fltarr(5)
      tickv = [ 0.0, 0.25, 0.5, 0.75, 1.0]
		plot, pbp[kk].wnu[0:npt1], pbp[kk].obsspc[0:npt1], position = sppos,						$
			/nodata, ytitle='arbitrary', charsize = chsize, xticklen = 0.06, $
			ystyle = 1, yminor = ymn,		$
			xtitle = 'wavenumber [cm!e-1!n]', xstyle=1 ;, yticks = 4, ytickv=tickv

		if( !y.crange[0] lt 0.0 ) then oplot, !x.crange, [0.0,0.0], color = tek
		if( !y.crange[1] gt 1.0 ) then oplot, !x.crange, [1.0,1.0], color = tek


      ; put solar at top
      gasfile = 'spc.sol.' + string(iband,jscan,format='(i02,".",i02,".")') + suffix
      if( keyword_set( dir ) )then gasfile = dir + gasfile
      if( file_test( gasfile, /regular ))then begin

         rc = readgasf( gasfile, title, w1, w2, spac, npt, ary )

         ; calculate complete wavenumber array for simulated spectra
         nu = fltarr(npt)
         nu(0:npt-1) = findgen(npt) * spac + w1

         clr = ngasb+4
         if(clr GE 7 )then clr++
         oplot, nu, ary + yoff*(ngasb+1), color = clr, thick = lthick, /noclip

         res = convert_coord( 0., omx+yoff*(ngasb+1), /to_normal )
         xyouts, right+0.01, res[1]-0.01, 'SOLAR', /normal, color = clr, charsize=lcsz

      endif

      ; gasfile : gas.h2o.1.1.final  iband, jscan, iteration
      n=0
      for j=0, ngas-1 do begin

         gasfile = 'spc.' + stat.gas[0,j] + '.'+string(iband,jscan,format='(i02,".",i02,".")') + suffix
         if( keyword_set( dir ) )then gasfile = dir + gasfile
         if( file_test( gasfile, /regular ))then begin

            rc = readgasf( gasfile, title, w1, w2, spac, npt, ary )

            ;print, stat.gas[0,j]

            nu = fltarr(npt)
            nu(0:npt-1) = findgen(npt) * spac + w1

            clr = n+4
            if(clr GE 7 )then clr++
            oplot, nu, ary/(max(ary)) + yoff*(n+1), color = clr, thick = lthick, /noclip

            res = convert_coord( 0., omx+yoff*(n+1), /to_normal )
            res[1] = res[1]
            xyouts, right+0.01, res[1]-0.01, stat.gas[0,j], /normal, color = clr, charsize=lcsz
            n++
         endif

      endfor

      ; plot the obs & syn spectra
		oplot, pbp[kk].wnu[0:npt1], pbp[kk].obsspc[0:npt1], color = 3, thick = lthick, /noclip
		oplot, pbp[kk].wnu[0:npt1], pbp[kk].synspc[0:npt1], color = 2, thick = lthick, /noclip

;		xyouts, right+0.01, dsbrk-0.03*ngas-0.05, 'OBSERVED',   /normal, color = 3, charsize=lcsz
;		xyouts, right+0.01, dsbrk-0.03*ngas-0.08, 'CALCULATED', /normal, color = 2, charsize=lcsz

		xyouts, !x.crange[1], 1-(1.-mn)*0.1, 'OBSERVED', color = 3, charsize=lcsz
		xyouts, !x.crange[1], 1.-(1.-mn)*0.2, 'CALCULATED', color = 2, charsize=lcsz


	endfor

	return, 0

end

; read in gas files --------------------------------------------------------------------

function readgasf, filename, title, w1, w2, spac, npt, ary

   ; read simul gas file no struct

   ;print, 'gasfile : ', filename

   openr, gflun, filename, /get_lun, error=ioerr
   if (ioerr ne 0) then begin
      printf, -2, filename, !err_string
      return,0
   endif

   title=''
   w1=0.0d
   w2=0.0d
   spac=0.0d
   npt=0l

	readf, gflun, title
	;print, '   ', title
	readf, gflun, w1, w2, spac, npt

	ary = fltarr(npt)
	readf, gflun, ary

free_lun,gflun
return,1
end


; Plot bnr --------------------------------------------------------------------------

FUNCTION plotbnr, pbp, file, toPS, ppos, psiz, stickthick, plottop, ftype

	if( toPS )then PRINT, '  BNR file &  type : ', file, '  ', ftype

	IF( ftype EQ 'L' ) THEN 			$
		OPENR, sftlun, file, /GET_LUN ,/F77_UNFORMATTED, /SWAP_ENDIAN, ERROR=ioerr	$
	ELSE IF( ftype EQ 'C' ) THEN 		$
		OPENR, sftlun, file, /GET_LUN, ERROR=ioerr 		$
	ELSE					$
		OPENR, sftlun, file, /GET_LUN ,/F77_UNFORMATTED, ERROR=ioerr

	IF( ioerr NE 0 ) THEN BEGIN
		PRINTF, -2, !ERR_STRING
		RETURN, 1
	ENDIF

	header = string(replicate(32b,80))
	READU, sftlun, header
	header = STRTRIM( header, 2 )
	if( toPS )then begin
      PRINT, '  BNR File header:'
      PRINT, '   ', '"', header, '"'
      PRINT, ''
   endif

	wlo=0D & whi=0D & spa=0D & npp=0L

	READU,sftlun,wlo,whi,spa,npp
	;print, wlo, whi, spa, npp

	arr=FLTARR(npp)
	READU, sftlun, arr
	FREE_LUN, sftlun

	xar = FLOAT( wlo + spa*FINDGEN(npp) )

	cbpos = FLTARR(4)
	ctpos = FLTARR(4)

	TEK_COLOR
	; set up windows
	IF toPS THEN BEGIN

		ERASE
		ctpos = [0.12, 0.10, 0.93, 0.83]
		xcharsz = 1.0
		ycharsz = 1.0

	ENDIF ELSE BEGIN

		ppos = ppos + [ 20, -20, 1 ]
		WINDOW, ppos[2], RETAIN=2, XSIZE=psiz[0], YSIZE=psiz[1], 	$
			title= STRING( 'Plot ', ppos[2], FORMAT='(a,i02)') + ' : Spectra Region' ,  $
			XPOS = ppos[0], YPOS = ppos[1]
		;!P.CHARSIZE = 1.2
		DEVICE, DECOMPOSE = 0  ; allow for terminals with > 256 color
		ctpos = [0.10, 0.15, 0.92, 0.80]
		xcharsz = 1.4
		ycharsz = 1.4
		!P.CHARSIZE = 1

	ENDELSE

	minnu = MIN( pbp[*].nulo )
	maxnu = MAX( pbp[*].nuhi )

	buffer = 10
	xr = [ minnu -buffer, maxnu +buffer ]

	ix = LINDGEN(npp)
	yr = [ 0, max(arr(ix))+0.1*max(arr(ix)) ]
	yr = [0,0]

	q1 = MIN( arr )
	q3 = MAX( arr )
	qx = WHERE( arr LT 0.0, qc )
	IF( qc GT 0 ) THEN BEGIN
		q2 = MEAN( arr[qx] )
		xt = STRING( '!C', q3,' to ', q1, ' # neg : ', qc, ' mean : ', q2, -q1/q3*100, '%', $
			FORMAT = '(a, f7.4, a, f8.5, a, i6, a, f8.5, f6.2, a1 )' )
	ENDIF ELSE BEGIN
		xt = STRING( '!Cmax : ', q3,' min : ', q1, $
			FORMAT = '(a, f8.5, a, f8.5)' )
	ENDELSE

	PLOT, xar(ix), arr(ix), LINESTYLE = 0,				$
		XTITLE ='Wavenumber [cm-1]' + xt, 				$
		YTITLE ='Transmission',  						$
		YRANGE = yr, XRANGE = xr, TITLE =header, 		$
		XTICKFORMAT ='(f7.2)', 	YTICKFORMAT ='(f5.2)',	$
		XSTYLE = 1, YSTYLE = 0, POSITION = ctpos, 		$
		XCHARSIZE = xcharsz, YCHARSIZE = ycharsz

	OPLOT, !X.crange, [0,0], COLOR = 2, THICK = 2. ; red

	FOR i=0, pbp[0].nfit-1 DO BEGIN

		OPLOT, [ pbp[i].nulo, pbp[i].nulo ], !Y.CRANGE, COLOR= i +3, THICK = 2.
		OPLOT, [ pbp[i].nuhi, pbp[i].nuhi ], !Y.CRANGE, COLOR= i +3, THICK = 2.

	ENDFOR

	RETURN, 0
END


; Contour plot Sa ------------------------------------------------------------------

FUNCTION covarplot, mat, prfs, toPS, ppos, psiz, stickthick, title, plottop

	!P.MULTI = [2]

	cbpos = FLTARR(4)
	ctpos = FLTARR(4)

	; set up windows
	IF toPS THEN BEGIN

		cbpos = [0.20, 0.91, 0.80, 0.96]	; PS
		ctpos = [0.20, 0.10, 0.80, 0.81]
		ERASE

	ENDIF ELSE BEGIN

		cbpos = [0.20, 0.87, 0.90, 0.92]	; X
		ctpos = [0.25, 0.10, 0.85, 0.80]
		ppos = ppos +  [ 20,  -20, 1 ]
		WINDOW, ppos[2], RETAIN=2, XSIZE=psiz[0], YSIZE=psiz[1], 	$
			title= STRING( 'Plot ', ppos[2], FORMAT='(a,i02)') + ' : ' + title,  $
			XPOS = ppos[0], YPOS = ppos[1]
		!P.CHARSIZE = 1.2
		DEVICE, DECOMPOSE = 0  ; allow for terminals with > 256 color
      chsiz = 1
	ENDELSE

	IF( toPS ) THEN PRINT, ' CovarPlot : ', title

	nlev = prfs.nlev
	z    = prfs.zbar
	bnd  = [ prfs.zbnd, 80.0 ]

	div = 0
	WHILE( MAX( mat ) GT 10. ) DO BEGIN
		div = div -1
		mat = mat / 10.
	ENDWHILE

	WHILE( MAX( mat ) LT 1. ) DO BEGIN
      div = div +1
		mat = mat * 10.
	ENDWHILE

	; set up contours
	ndiv = 7
	nclr = 200
	scal = 1.0
	span = MAX(mat)/scal - MIN(mat) + 0.0*(MAX(mat) - MIN(mat))
	clvs = MIN(mat) - 0.0*span + INDGEN( nclr+1 ) * span/(nclr -1)

	;IF( NOT toPS ) THEN PRINT, ' Min, Max of contour levels              : ', MIN( clvs ), MAX( clvs )
	;IF( not toPS ) THEN PRINT, ' Number of contour divisions in colorbar : ', ndiv
	;IF( not toPS ) THEN PRINT, ' Number of color levels in contour plot  : ', nclr

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

	LOADCT, 5, NCOLORS = nclr+40, /SILENT;, BOTTOM = 10

	cbtitle = title + ' [x10!E' + STRING( div, FORMAT='(i+2)' ) + '!N]'
	COLORBAR, NCOLORS = nclr, POSITION = cbpos, CHARSIZE = chsiz,		$
		DIVISIONS = ndiv, TICKNAMES = cbtics, TITLE = cbtitle, BOTTOM=00

	CONTOUR, mat, z, z, POSITION = ctpos, NLEVELS = nclr,				$
		YRANGE = [0.0, plottop], XRANGE = [0.0, plottop],				$
		;C_COLORS = INDGEN(nclr)+00,									$
		CHARSIZE = chsiz, /FILL, YTICKLEN = -0.02, XTICKLEN = -0.02, 		$
		YTITLE = 'Altitude [km]', XTITLE = 'Altitude [km]'

	;print,''
	;print, mat[indgen(40),indgen(40)]
	RETURN, 0

END

; Contour plot K Matrix ------------------------------------------------------------------

FUNCTION plotk, kmf, stat, smf, toPS, ppos, psiz, stickthick, plottop

	nfit = smf.nfit
	nbnd = smf.nbnd
	print, ' plotk : nfits in nbands : ', nfit, nbnd

	cbpos = FLTARR(4)
	ctpos = FLTARR(4)

	; set up windows
	IF toPS THEN BEGIN

		ERASE
		cbpos = [0.20, 0.92, 0.80, 0.97]	; PS
		ctpos = [0.12, 0.10, 0.93, 0.83]
		ftpos = [ .00, .04, 0.08 ]
      !p.charsize = 1.0
      chsize = 1.2
		xcharsz = 1.2
		ycharsz = 1.2

	ENDIF ELSE BEGIN

		ppos = ppos +  [ 20,  -20, 1 ]
		WINDOW, ppos[2], RETAIN=2, XSIZE=psiz[0], YSIZE=psiz[1],	$
			title= STRING( 'Plot ', ppos[2], FORMAT='(a,i02)') + ' : K Matrix',	$
			XPOS = ppos[0], YPOS = ppos[1]
		DEVICE, DECOMPOSE = 0  ; allow for terminals with > 256 color
		cbpos = [0.20, 0.87, 0.90, 0.92]	; X
		ctpos = [0.10, 0.10, 0.95, 0.80]
		ftpos = [0.02, 0.05, 0.08 ]
		!p.charsize = 1.1
      chsize = 1.3
		xcharsz = 1.4
		ycharsz = 1.4

	ENDELSE

	nlev = kmf.nlev
	ismx = kmf.ismx
	npts = kmf.npts
	z = stat.z

	;help, z
	; kmat is npts x npar in sfit 4 & from readkmat4
   ;print, 'k matrix :'
   ;help, kmf.mat
   mat = kmf.mat[ ismx:ismx+nlev-1, 0:npts-1 ]
   ;help, mat
   mat = transpose( mat )
   ;print, 'k matrix target to plot:'
   ;help, mat

	;mat  = REVERSE( mat[ 0:npts-1, ismx:ismx+nlev-1 ], 2); *1000.0

	title = ' Jacobian Matrix : ' + STRING( nlev, npts, FORMAT='( i2,"x",i5 )' )
;	mat = kmf.kmat *1000.0

	div = 0
	WHILE( MAX( mat ) GT 10. ) DO BEGIN
		div = div -1
		mat = mat / 10.
	ENDWHILE

	WHILE( MAX( mat ) LT 1. ) DO BEGIN
		div = div +1
		mat = mat * 10.
	ENDWHILE

	; set up contours
	ndiv = 7
	nclr = 240
	scal = 1.0
	span = MAX(mat)/scal - MIN(mat) + 0.0*(MAX(mat) - MIN(mat))
	clvs = MIN(mat) - 0.0*span + INDGEN( nclr +1 ) * span/(nclr -1)

	;IF( NOT toPS ) THEN PRINT, ' Min, Max of contour levels             : ', MIN( clvs ), MAX( clvs )
	;IF( NOT toPS ) THEN PRINT, ' Number of contour divisions in colorbar : ', ndiv
	;IF( NOT toPS ) THEN PRINT, ' Number of color levels in contour plot  : ', nclr

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
	COLORBAR, NCOLORS = nclr-40, POSITION = cbpos, CHARSIZE=chsize,	$
		DIVISIONS = ndiv, TICKNAMES = cbtics, TITLE = cbtitle

	offset = 0
	pointoff = 0
	pwidth = ctpos[2] - ctpos[0]
	thispos = FLTARR(4)
	thistic = FLTARR(8)

	;Tick step size for major ticks. ie 1 = every wavenumber
	tick_interval = 1
	minor = 10

	FOR kk = 0, nbnd-1 DO BEGIN

	   jscan = smf.nscn(kk)

      for j = 0, jscan-1 do begin

         print , ' plotting band : ', kk, ' scan : ', j
         thispos = ctpos
         ;print, kk, smf.npts[kk], smf.wstr[kk], smf.wstp[kk], smf.nspac[kk]
         pratio = FLOAT( smf.npts[kk] ) / FLOAT( npts	)
         ;pratio = FLOAT( pbp[kk].npt ) / FLOAT( npts	)

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

         ;npt      = pbp[kk].npt
         ;x        = pbp[kk].wnu[0:npt-1]
         npt       = smf.npts[kk]
         x         = smf.wstr[kk] + indgen(npt)*smf.nspac[kk]
         thismat   = mat[ pointoff:pointoff+npt-1, * ]
         pointoff  = pointoff + npt

         ;nulo = pbp[kk].nulo
         ;nuhi = pbp[kk].nuhi
         nulo = smf.wstr[kk]
         nuhi = smf.wstp[kk]
         ;IF( NOT toPS ) THEN PRINT, ' wv # range : ', kk, nulo, nuhi, pw

         leftmost_tick = floor(nulo / tick_interval)*tick_interval + tick_interval
         rightmost_tick = floor(nuhi / tick_interval)*tick_interval

         num_ticks = (rightmost_tick - leftmost_tick) / tick_interval + 1
         if (not toPS) then begin
            ;print, 'number of major ticks: ',num_ticks
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
            YRANGE = [0.0, plottop], /FILL, /noerase, $
            CHARSIZE = charsz, YTICKLEN = -0.02, XTICKLEN = -0.02,$
            YTITLE = 'Altitude [km]', xtitle = '', XCHARSIZE = xcharsz,$
            YCHARSIZE = ys,$
            XRANGE = [nulo,nuhi],$
            XSTYLE = 1,$
            XTICKINTERVAL = tick_interval,$
            XMINOR = minor


         endfor

	ENDFOR

	xtitl = 'Wavenumber [cm!E-1!N]'
	XYOUTS, 0.5, ftpos[0], xtitl, /NORMAL, CHARSIZE=1.2, ALIGNMENT = 0.5

	RETURN, 0

END




; Plot averaging kernels --------------------------------------------------------------------

FUNCTION plotak, ak, stat, toPS, ppos, psiz, tek, lthick, plottop, site, auc, nrm=nrm

	!P.MULTI = [ 0, 2, 1 ]

	yrng = [0.,plottop]
   nlev = stat.nlev
   v    = stat.vmr[0,0,*]  ; top to bottom
   z    = stat.z

   mat = dblarr(nlev,nlev)
   mat = ak.mat
   ;mat = transpose(ak.mat)
   ;print, v[0], mat[0,0:2]

   XTITL = 'Fractional Value'
   ; scale apriori relative kernel for vmrs
   if( keyword_set( nrm ) )then begin
      XTITL = 'VMR Normalized Value'
      for i=0, nlev-1 do begin
         for j=0, nlev-1 do mat[i,j] = mat[i,j] * v[i] / v[j]
      endfor
   endif

;openw, lun1, 'nak.out', /get_lun
;printf, lun1,mat
;free_lun, lun1

	; set up windows
	IF toPS THEN BEGIN
		ERASE
		!P.CHARSIZE = 1.2
	ENDIF ELSE BEGIN
		ppos = ppos + [ 20, -20, 1 ]
		WINDOW, ppos[2], RETAIN=2, XSIZE=psiz[0], YSIZE=psiz[1], 	$
			title= STRING( 'Plot ', ppos[2], FORMAT='(a,i02)') + ' : Averging Kernels',  $
			XPOS = ppos[0], YPOS = ppos[1]
		!P.CHARSIZE = 1.2
	ENDELSE

	omx = MAX( mat, MIN=omn )
	cmx = MAX( mat, MIN=cmn )
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

	TEK_COLOR
	; plot all averaging kernels on left
	PLOT, mat[0,*], z, /NODATA, $
	   YRANGE = yrng,	$
		YTITLE = 'Altitude [km]', $
		YTICKLEN = 0.06, $
		XTICKLEN = 0.03,		$
		TITLE = 'All Averging Kernels', $
		XTITLE = xtitl,	$
		XTICKS=4, $
		XRANGE=[mn,mx]

   xr = !X.Crange
   yr = !Y.Crange

	cc = 1
	FOR i = 0, nlev-1, 2 DO BEGIN
		cc = cc + 1 mod 32
		; 0,1 are black and white, resp, which we want to skip
		IF( cc eq 0 )THEN cc = 2
		; Switching kernels to rows - second index
		;OPLOT, mat[i,*], z, COLOR = cc, THICK = lthick
		; with ak mat not transposed use first index as rox from ak file
		OPLOT, mat[*,i], z, COLOR = cc, THICK = lthick
	   XYOUTS, xr[0], z[i], STRING(z[i],FORMAT='(i2)'), COLOR=cc, NOCLIP=0
	ENDFOR

	; sum several kernels
	; from ground - IRWG
	IF( site NE 'ACF' ) THEN BEGIN
		bnds  = [ [0, 8], [8, 17], [17, 26], [26, 40], [0, 120], [0,5], [0,8], [0,11] ]
		bname = [ ' 0- 8km', ' 8-17km', '17-26km', '26-40km', ' 0-120km', 'Prior Cont', ' 0-5km', ' 0-8km',' 0-11km' ]
		nband = 8
	ENDIF ELSE BEGIN
	; Aircraft
		PRINT, '!!!! Plotting Aircraft Summed Kernels!!!!'
		bnds  = [ [10, 13], [13, 18], [18, 26], [26, 40], [10, 80] ]
		bname = [ '10-13km', '13-18km', '18-26km', '26-40km', '10-80km', 'Prior Cont' ]
		nband = 5
	ENDELSE
	bpos  = [ [0.84, 0.90], [0.84, 0.86], [0.84, 0.82], [0.84, 0.78], [0.84, 0.74], [0.84, 0.70]];, [0.84, 0.66]];!added [0.84, 0.66] RB 4/8/10

	; plot summed averaging kernels on right
	PLOT, TOTAL( mat, 1 ), z, /NODATA, YRANGE=yrng, XRANGE = [-0.5, 1.5], $
		YTITLE = 'Altitude [km]', YTICKLEN = 0.06, XTICKLEN = 0.03, $
		TITLE = 'Summed Partial Kernels', XTITLE = xtitl

	smaks = DBLARR( nlev, nband )

   FOR i = 0, nband-1 DO BEGIN
      ids        = WHERE(( z GE bnds[0,i] ) AND ( z LE bnds[1,i] ), cnt )
      q          = dblarr(nlev)
      q[ids]     = 1.
      smak       = q#mat
      smaks[*,i] = smak

		IF( i GT 4 )THEN CONTINUE

		OPLOT, smaks[ *, i ], z, COLOR = i+2, THICK = lthick
		XYOUTS, bpos[0,i], bpos[1,i], bname[i], /NORMAL, COLOR = i+2, CHARSIZE=1.

	ENDFOR

	OPLOT, [0.0,0.0], [0.0,80.0], COLOR = tek

	; Compute 'area under curve for AK's as apriori contribution
	auc = DBLARR( nlev )

   FOR i=0, nlev-1 DO auc[i] = total( mat[*,i], /DOUBLE )

	cc = 12	; Purple
	XYOUTS, bpos[0,5], bpos[1,5], bname[5], /NORMAL, COLOR = cc, CHARSIZE=1.

   OPLOT, 1.-auc, z, color=cc, thick=lthick, linestyle=1

	; Printout summed kernels
;	IF( toPS )THEN BEGIN
;		OPENW, lun, 'partkrnl.dat', /GET_LUN
;		PRINTF, lun, 'Alt[km]', bname, FORMAT='(10A13)'
;		FOR i=0, nlev-1 DO PRINTF, lun, z[i], smaks[i, 0:4], 1.-auc[i],smaks[i, 5:7], FORMAT='(F8.2, 10F14.6)'
;		FREE_LUN, lun
;		pre_k = smak[0]
;		FOR i=1, cnt-1 DO BEGIN
;			IF( pre_k GE 0.5 AND i EQ 1 ) THEN PRINT, 'Min alt TCAK GT 0.5 : ', z[ids[0]]
;			IF( pre_k LT 0.5 AND smak[ids[i]] GE 0.5 ) THEN PRINT, 'Min alt TCAK GT 0.5 : ', z[ids[i-1]]
;			IF( pre_k GE 0.5 AND smak[ids[i]] LT 0.5 ) THEN PRINT, 'Max alt TCAK GT 0.5 : ', z[ids[i-1]]
;			pre_k = smak[ids[i]]
;		ENDFOR
;	ENDIF

	RETURN, 0
END


; Plot Smooth & Measurement error, profiles --------------------------------------------------------------------
FUNCTION ploterrs, sserr, smerr, stat, kmf, toPS, ppos, psiz, vmrscl, vmrunits, $
				tek, lthick, plottop, rms, vmrng

	!P.MULTI = [ 0, 3, 1 ]

	nlev  = smerr.n
	z     = stat.z
	sqrsm = DBLARR( nlev )
	sqrss = sqrsm

	diag = INDGEN( nlev )

	layr = DBLARR(nlev)
	FOR i=0, nlev-2 DO layr[i] = ( z[i+1] - z[i] ) ;*1.0e5
	layr[nlev-1] = ( 80. - z[nlev-1] )

	sqrsm = SQRT( smerr.mat[ diag, diag ] )
	sqrss = SQRT( sserr.mat[ diag, diag ] )

	npar = kmf.npar
	npts = kmf.npts
	nlev = kmf.nlev
	ismx = kmf.ismx

	sa   = REVERSE( REVERSE( kmf.sa[ ismx:ismx+nlev-1, ismx:ismx+nlev-1 ], 1), 2)
	shat = REVERSE( REVERSE( kmf.shat[ ismx:ismx+nlev-1, ismx:ismx+nlev-1 ], 1), 2)

	sqrsa = SQRT( sa[ diag, diag ] )
	sqrsh = SQRT( shat[ diag, diag ] )
	;print, sqrsa


	; set up windows
	IF toPS THEN BEGIN

		ERASE
		!P.CHARSIZE = 1.
	ENDIF ELSE BEGIN

		ppos = ppos +  [ 20,  -20, 1 ]
		WINDOW, ppos[2], RETAIN=2, XSIZE=psiz[0], YSIZE=psiz[1], 	$
			title= STRING( 'Plot ', ppos[2], FORMAT='(a,i02)') + ' : Error Diagonals & VMRs',  $
			XPOS = ppos[0], YPOS = ppos[1]
		!P.CHARSIZE = 1.6

	ENDELSE

	dex = WHERE( z LE plottop )
	mx = MAX( [ sqrsm[dex], sqrss[dex], sqrsa[dex]*layr, sqrsh[dex]], MIN=mn )
	;print, mx, mn

	IF( toPS ) THEN BEGIN
		PRINT, '  i   alt     Sm        Ss       Sa       Shat'
		FOR i=0, nlev-1 DO PRINT, i, z[i], sqrsm[i], sqrss[i], sqrsa[i], sqrsh[i], $
								FORMAT='(i4, f6.2, 4f9.5)'
	ENDIF

	rms = SQRT( TOTAL( sqrsm*sqrsm )/nlev)
	PRINT, ' RMS Measurement error : ', rms*100, FORMAT='(a, f7.2, "%" )'

	; plot uncertainty diagonals
	PLOT, sqrsm, z, /NODATA, YRANGE=[0.0, plottop], $
		YTITLE = 'Altitude [km]', YTICKLEN = 0.06, XTICKLEN = 0.03, $
		TITLE = 'Uncertainty Diagonals', XTITLE = 'Fractional Value', $
		XRANGE = [ mn, mx ], XTICKFORMAT = 'exponent', XSTYLE=0,CHARSIZE=1.5 ;/XLOG

	OPLOT, sqrsm, z, COLOR = 2, THICK = lthick
	OPLOT, sqrss, z, COLOR = 3, THICK = lthick
	OPLOT, sqrsa*layr, z, COLOR = 4, THICK = lthick
	OPLOT, sqrsh, z, COLOR = 5, THICK = lthick

	XYOUTS, 0.34, 0.50, 'Measure', /NORMAL, COLOR = 2, CHARSIZE=1.5, $
		ORIENTATION = 90
	XYOUTS, 0.34, 0.30, 'Smooth', /NORMAL, COLOR = 3, CHARSIZE=1.5, $
		ORIENTATION = 90
	XYOUTS, 0.34, 0.10, 'A-priori', /NORMAL, COLOR = 4, CHARSIZE=1.5, $
		ORIENTATION = 90
	XYOUTS, 0.34, 0.70, 'Total', /NORMAL, COLOR = 5, CHARSIZE=1.5, $
		ORIENTATION = 90

	; calculate ymin and ymax for profiles plot

	dex = where(z LE plottop, cnt)
	if( cnt EQ 0 )then stop, 'plotprf & z & plottop'
	avmr = stat.vmr[0,0,dex] * vmrscl
	vmr = stat.vmr[1,0,dex] * vmrscl

	omx = MAX( vmr, MIN=omn )
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

	; plot vmrs log
	PLOT, vmr, z[dex], /XLOG, /NODATA, YRANGE=[0.0, plottop], XRANGE=[mn,mx], $
		YTITLE = 'Altitude [km]', YTICKLEN = 0.06, XTICKLEN = 0.03, 	$
		XTITLE = 'Mixing Ratio for ' + stat.gas[0] + ' ' + vmrunits, $
		TITLE = 'Mixing Ratio', XTICKFORMAT = 'exponent',CHARSIZE=1.5

	OPLOT, vmr, z[dex], COLOR = 2, THICK = lthick
	OPLOT, avmr, z[dex], COLOR = 3, THICK = lthick

	XYOUTS, 0.67, 0.55, 'Retrieved VMR', /NORMAL, COLOR = 2, CHARSIZE=1.5, $
		ORIENTATION = 90
	XYOUTS, 0.67, 0.25, 'A Priori VMR', /NORMAL, COLOR = 3, CHARSIZE=1.5, $
		ORIENTATION = 90

	; plot vmrs linear
	PLOT, vmr, z[dex], /NODATA, YRANGE=[0.0, plottop], XRANGE=[mn,mx], $
		YTITLE = 'Altitude [km]', YTICKLEN = 0.06, XTICKLEN = 0.03, 	$
		XTITLE = 'Mixing Ratio for ' + stat.gas[0] + ' ' + vmrunits, $
		TITLE = 'Mixing Ratio' ;, XTICKFORMAT = 'exponent'

	OPLOT, vmr, z[dex], COLOR = 2, THICK = lthick
	OPLOT, avmr, z[dex], COLOR = 3, THICK = lthick

	;XYOUTS, 0.67, 0.55, 'Retrieved VMR', /NORMAL, COLOR = 2, CHARSIZE=1.7, $
	;	ORIENTATION = 90
	;XYOUTS, 0.67, 0.25, 'A Priori VMR', /NORMAL, COLOR = 3, CHARSIZE=1.7, $
	;	ORIENTATION = 90

	RETURN, 0



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


