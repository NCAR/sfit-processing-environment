pro pltprfs4, afile=afile, rfile=rfile, reffile=reffile, dir=dir, big=big, ps=ps

   funcs = ['readprfs4', 'readrfmd4' ]
   resolve_routine, funcs, /either

   close, /all

	if( not keyword_set( ps )) then begin
		print, '  main : setting default ps=0 -> do not create ps output.'
		ps = 0
	endif

   if( not keyword_set( afile )) then begin
      afile = 'aprfs.table'
      print, '  main : apriori profile file not given using : ', afile
   endif

   if( not keyword_set( rfile )) then begin
      rfile = 'rprfs.table'
      print, '  main : retrieved profile file not given using : ', rfile
   endif

   if( not keyword_set( reffile )) then begin
      reffile = 'reference.prf'
      print, '  main : retrieved profile file not given using : ', reffile
   endif

; read in profiles file
	rc = 0
	if( keyword_set( dir ) )then afile = dir + afile
	rc = readprfs4( aprf, afile )
	if( rc ne 0 ) then begin
		printf, -2,'could not read profile file: ', afile
		stop
	endif

; read in profiles file
	rc = 0
	if( keyword_set( dir ) )then rfile = dir + rfile
	rc = readprfs4( rprf, rfile )
	if( rc ne 0 ) then begin
		printf, -2,'could not read profile file: ', rfile
		stop
	endif

; read in profiles file
	rc = 0
	if( keyword_set( dir ) )then reffile = dir + reffile
	rc = readrfmd4( refm, reffile, /zpt )
	if( rc ne 0 ) then begin
		printf, -2,'could not read profile file: ', reffile
		stop
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

   plottop = 120.

   print, aprf.ver
   print, aprf.tag
   print, aprf.ttl

   des = ''
   read, des, prompt=' plot what ? , t, p, a, g : '
   if( des eq 'g' )then begin
      ng = 0
      read, ng, prompt=' enter id of gas to plot '
   endif else begin
      if( des eq 't' )then begin
         ng = 101
      endif
      if( des eq 'a' )then begin
         ng = 102
      endif
      if( des eq 'p' )then begin
         ng = 103
      endif
   endelse

	for toPS = 0, ps do begin

		thick = 1.0
		if toPS then begin ;1
			set_plot, 'ps'
			psfile = 'pltprfs.ps'
			if( keyword_set( dir ) )then psfile = dir + psfile
			print, 'saving ps file to : ', psfile
			device, /color, /landscape, filename = psfile, encapsulated = encap, bits=8
			tek = 0 ; black

		endif else begin
			set_plot,'x'
			device, decompose = 0 ; allow for terminals with > 256 color
			tek = 1 ; white

		endelse

         rc = plotprfs( aprf, rprf, refm, ng, tops, ppos, psiz, tek, lthick, plottop )

		if( toPS ) then device, /close_file

	endfor ; tops

	print, ' pltprfs .done.', format='(/,a,/)'

stop
end

; plot vmr profiles --------------------------------------------------------------------

function plotprfs, aprf, rprf, refm, n, tops, ppos, psiz, tek, lthick, plottop

	; set up windows
	!p.multi = [ 0, 2, 1 ]
	tek_color
	if tops then begin
		erase
		!p.charsize = 1.6
		chrsz = 1.5
	endif else begin
		ppos = ppos +  [ 20,  -20, 1 ]
		window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1], 	$
			title= string( 'plot ', ppos[2], format='(a,i02)') + ' : apriori and retrieved vmrs',  $
			xpos = ppos[0], ypos = ppos[1]
		!p.charsize = 1.6
		chrsz = 1.5
	endelse

   z    = aprf.zbar
   zf   = refm.prfs[0,*]
	dex  = where(z  LE plottop, cnt)
	fdex = where(zf LE plottop, cnt)

   case n of
      101 : begin
         avmr  = aprf.t
         rvmr  = rprf.t
         fvmr  = refm.prfs[2,*]
         xtitl = 'Temperature [K] '
         end
      102 : begin
         avmr  = aprf.a
         rvmr  = rprf.a
         xtitl = 'Airmass [molec/cm^2] '
         fvmr  = fltarr(refm.nlay)
         end
      103 : begin
         avmr  = aprf.p
         rvmr  = rprf.p
         fvmr  = refm.prfs[1,*]
         xtitl = 'Pressure [mb] '
         end
      else : begin
         avmr  = aprf.vmr[*,n-1]
         rvmr  = rprf.vmr[*,n-1]
         fvmr  = refm.prfs[2+n,*]
         xtitl = aprf.name[n-1]
         end
   endcase

	; calculate ymin and ymax for profiles plot
	omx = max( rvmr, min=omn )
	cmx = max( avmr, min=cmn )
	if (omx gt cmx) then begin
		mx = omx
	endif else begin
		mx = cmx
	endelse
	if (omn lt cmn) then begin
		mn = omn
	endif else begin
		mn = cmn
	endelse

   scl = 1.
   while( mx lt 1. ) do begin
      scl = scl * 10.
      mx  = mx * 10.
      mn  = mn * 10.
   endwhile
   scl = 1
   mn  = 0.0
   mx  = 0.0
   ex  = alog10(scl)

	; plot vmrs log
	plot, avmr*scl, z[dex], /xlog, /nodata, yrange=[0.0, plottop], xrange=[mn,mx], $
		ytitle = 'altitude [km]', yticklen = 0.06, xticklen = 0.03, 	$
		xtitle = xtitl, ystyle = 8, $
		title = 'Profile', charsize=chrsz, xtickformat = 'exponent'

	oplot, avmr*scl, z[dex], color = 2, thick = lthick
	oplot, rvmr*scl, z[dex], color = 3,psym=2
	oplot, fvmr*scl, zf[fdex], color = 4, thick = lthick


	; plot vmrs linear
	plot, avmr*scl, z[dex], /nodata, yrange=[0.0, plottop], xrange=[mn,mx], $
		ytitle = 'altitude [km]', yticklen = 0.06, xticklen = 0.03, 	$
		xtitle = xtitl, ystyle = 8, $
		title = 'Profile', charsize=chrsz

	oplot, avmr*scl, z[dex], color = 2, thick = lthick
	oplot, rvmr*scl, z[dex], color = 3, psym=2
	oplot, fvmr*scl, zf[fdex], color = 4, thick = lthick

	fx = !x.crange[1]
	;print, fx, !x.crange, scl
	for i=0, aprf.nlev-1 do begin
	   rng = [fx - .02*fx, fx + 0.02*fx]
	   print, rng, scl*rng, [z[i], z[i]], format='(6f20.5)'
	   oplot, rng*scl, [z[i], z[i]], color = 5
   	xyouts, rng[0]*0.98*scl, z[i], string( dex[aprf.nlev-1-i]+1,format='(i2)' ), color = 2, charsize=1.5
	endfor

	xyouts, 0.50, 0.80, 'a priori',  /normal, color = 2, charsize=1.5
	xyouts, 0.50, 0.85, 'retrieved', /normal, color = 3, charsize=1.5
	xyouts, 0.50, 0.90, 'reference', /normal, color = 4, charsize=1.5

   for i=0, aprf.nlev-1 do print, i+1, z[i], avmr[i], rvmr[i]
   for i=0, refm.nlay-1 do print, i+1, zf[i], fvmr[i]

	return, 0
stop
end
