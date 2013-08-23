pro pltfits4, ps=ps, thicklines=thicklines, oldgas=oldgas, mol=mol, big=big

; feb 2012
; from oex...plot only pbpfile

; idl script to plot sfit2 output
; originally scripted in matlab now converted to idl
;adapted 18/3/2010 to add in total column amount from retrieval rb


   forward_function plotiter, plotpbp, readgasf, readpbp, setfilenames, exponent

   funcs = [ 'readstat4' ]
   resolve_routine, funcs, /either

	print, ' usage : pltfits, /ps, /thick, /final'

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

	if( not keyword_set( oldgas )) then begin
		print, '  main : keyword oldgas not set.'
		print, '  main : setting default oldgas=0 -> read new gas files.'
		oldgas = 0
	endif

	if( not keyword_set( mol )) then begin
		print, '  main : keyword mol not set.'
		print, '  main : setting default final -> plot each final iteration for all gases.'
		final = 1
	endif else final = 0

   ppos = intarr(3)
   psiz = intarr(2)
	if( keyword_set( big )) then begin
      ppos = [ 10, 660, 0 ]		; dual display
      psiz = [ 1000, 750 ]       ; dual display
	endif else begin
      ppos = [ 10, 390, 0 ]		; mbp - retina
      psiz = [ 760, 500 ]			; mbp - retina
   endelse

	encap   = 0
	plottop = 120

; set up file names
	setfilenames, pbpfile, stfile

; read in pbpfile
	rc = 0
	rc = readpbp( pbp, pbpfile )

	if( rc ne 0 ) then begin
		printf, -2,'could not read pbp file: ', pbpfile
		return
		stop
	endif

; read in statevector file
	rc = 0
	rc = readstat4( stat, stfile )
	;rc = readstat( stat, stfile )

	if( rc ne 0 ) then begin
		printf, -2,'could not read st file: ', stfile
		stop
	endif

   print, ''
   if( stat.ngas NE 0 )then print, stat.ngas, transpose(stat.gas[0,0:stat.ngas-1])

	; 0 = x, 1 = ps
	for tops = 0 , ps do begin

		thick = 1.0
		if tops then begin ;1
			set_plot, 'ps'
			psfile = 'pltfits.ps'
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

		; plot spectra
		if( final )then begin
         suffix = 'final'
         ;suffix = 'FINAL'
         rc = plotpbp( pbp, tops, ppos, psiz, tek, lthick, summary, nsum, stat, oldgas, suffix, mol )
      endif else begin
         mol = strlowcase( mol )
         rc = plotiter( pbp, tops, ppos, psiz, tek, lthick, summary, nsum, stat, mol )
      endelse

		; plot  profiles
		;c = plotprfs( stat, tops, ppos, psiz, a.vmrscl, a.vmrunits, $
		;		tek, lthick, plottop, vmrng )

		; plot bnr file
		;rc = plotbnr( pbp, tops, ppos, psiz, stickthick, plottop, ftype )

		if( tops ) then device, /close_file

	endfor ; tops

	print, ' pltfits4 .done.', format='(/,a,/)'

end



; plot bnr --------------------------------------------------------------------------


function plotiter, pbp, tops, ppos, psiz, tek, lthick, summary, nsum, stat, mol

	!p.multi = 0

	dfpos = fltarr(4)
	sppos = fltarr(4)
	ftpos = fltarr(5); changed from 3 rb

	nfit = pbp[0].nfit
   smol = mol
   iter = stat.iter

   ;maxnpt = max(pbp[*].npt, mxk)
   ;print, maxnpt, mxk

	tek_color
	for kk = 0, nfit-1 do begin

		; set up windows
		if tops then begin

         right = 0.90
         dsbrk = 0.77
         difmd = 0.86
			dfpos = [0.12, dsbrk+0.01, right, 0.97]	; ps
			sppos = [0.12, 0.20, right, dsbrk ]
         lcsz = 1.0
			ftpos = [0.00, .02, .04, .06, 0.08]
			hdpos = .90
			if( kk ne 0 ) then erase

		endif else begin

         right = 0.90
         difmd = 0.86
         dsbrk = 0.77
			dfpos[*] = [0.08, dsbrk+0.01, right, 0.95 ]	; x
			sppos[*] = [0.08, 0.08, right, dsbrk ]
         lcsz = 1.4
			ftpos[*] = [ .00, .02, 0.04, 0.06, 0.08]
			hdpos    = 0.95
			ppos     = ppos + [ 20, -20, 1 ]

			window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1], 	$
				title = string( 'plot ', ppos[2], $
				format = '(a,i02)') + ' : spectral fit : ' + string( kk+1, nfit, format='(i02,"/",i02)' ), $
				xpos = ppos[0], ypos = ppos[1]

		endelse

		npt1 = pbp[kk].npt -1

      mn = 0.
      mx = 1.
      omx      = mx
      yoff     = 0.05*(mx-mn)
      mx       = mx + (iter+1)*yoff +0.005
		!y.range = [mn,mx]

      gasfile = 'spc.' + mol + '.'+string(kk+1,format='(i02)') + '.01.01'
      if( ~file_test( gasfile, /regular ))then stop

      rc = readgasf( gasfile, title, w1, w2, spac, npt, ary )
      nu = fltarr(npt)
      nu(0:npt-1) = findgen(npt) * spac + w1

		; plot spectra
      tickv = fltarr(5)
      tickv = [ 0.0, 0.25, 0.5, 0.75, 1.0]
		plot, nu, ary, position = sppos,						$
			/nodata, ytitle='arbitrary', charsize = 1.4, xticklen = 0.06, ystyle = 1, yminor = ymn,			$
			xtitle = 'wavenumber [cm!e-1!n]', xstyle=1, yticks = 4, ytickv=tickv

		if( !y.crange[0] lt 0.0 ) then oplot, !x.crange, [0.0,0.0], color = tek
		;if( !y.crange[1] gt 1.0 ) then oplot, !x.crange, [1.0,1.0], color = tek


      ; gasfile : gas.h2o.1.1.final  iband, jscan, iteration
      for j=1, iter do begin

         suffix = string( j, format='(i02)')
         gasfile = 'spc.' + mol + '.'+string(kk+1,format='(i02)') + '.01.' + suffix
         if( file_test( gasfile, /regular ))then begin

            rc = readgasf( gasfile, title, w1, w2, spac, npt, ary )

            ;print, stat.gas[0,j]

            clr = j+4
            if(clr GE 7 )then clr++
            oplot, nu, ary/(max(ary)) + yoff*(j+1), color = clr, thick = lthick, /noclip

            res = convert_coord( 0., omx+yoff*(j+1), /to_normal )
            res[1] = res[1]
            xyouts, right+0.01, res[1]-0.01, suffix, /normal, color = clr, charsize=lcsz
         endif
      endfor

      ; plot the obs & syn spectra
		oplot, pbp[kk].wnu[0:npt1], pbp[kk].obsspc[0:npt1], color = 3, thick = lthick, /noclip
		oplot, pbp[kk].wnu[0:npt1], pbp[kk].synspc[0:npt1], color = 2, thick = lthick, /noclip

		xyouts, right+0.01, dsbrk-0.03*iter-0.05, 'OBSERVED',   /normal, color = 3, charsize=lcsz
		xyouts, right+0.01, dsbrk-0.03*iter-0.08, 'CALCULATED', /normal, color = 2, charsize=lcsz

	endfor

	return, 0

end

; plot spectra --------------------------------------------------------------------

function plotpbp, pbp, tops, ppos, psiz, tek, lthick, summary, nsum, stat, oldgas, suffix, mol

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

         right = 0.90
         dsbrk = 0.77
         difmd = 0.86
			dfpos = [0.12, dsbrk+0.01, right, 0.97]	; ps
			sppos = [0.12, 0.20, right, dsbrk ]
         lcsz = 1.0
			ftpos = [0.00, .02, .04, .06, 0.08]
			hdpos = .90
			if( kk ne 0 ) then erase

		endif else begin

         right = 0.90
         difmd = 0.86
         dsbrk = 0.77
			dfpos[*] = [0.08, dsbrk+0.01, right, 0.95 ]	; x
			sppos[*] = [0.08, 0.08, right, dsbrk ]
         lcsz = 1.4
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

		; plot difference on top
		plot, pbp[kk].wnu[0:npt1], difs, position = dfpos, yticks = 4, title = titl,   $
			/nodata, ytitle='% difference', charsize = 1.4, xtickname = replicate(' ',30), xticklen = 0.08, $
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
			/nodata, ytitle='arbitrary', charsize = 1.4, xticklen = 0.06, $
			ystyle = 1, yminor = ymn,		$
			xtitle = 'wavenumber [cm!e-1!n]', xstyle=1 ;, yticks = 4, ytickv=tickv

		if( !y.crange[0] lt 0.0 ) then oplot, !x.crange, [0.0,0.0], color = tek
		if( !y.crange[1] gt 1.0 ) then oplot, !x.crange, [1.0,1.0], color = tek


      ; put solar at top
      gasfile = 'spc.sol.' + string(iband,jscan,format='(i02,".",i02,".")') + suffix

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

; read in pbpfile --------------------------------------------------------------------

function readgasf, filename, title, w1, w2, spac, npt, ary

   ; read simul gas file no struct

   print, 'gasfile : ', filename

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
	print, '   ', title
	readf, gflun, w1, w2, spac, npt

	ary = fltarr(npt)
	readf, gflun, ary

free_lun,gflun
return,1
end


; read in pbpfile --------------------------------------------------------------------

function readpbp, pbp, file

	maxpts = 262144l

	openr, lun, file, /get_lun, error=ioerr
	if( ioerr ne 0 ) then begin
	printf, -2, !err_string
	return, 1
	endif

	pbpstruct = { 				  	   $
      tag     : '',              $
		title   : '',              $
		nfit    : 0,				   $
		nband   : 0,				   $
		idex   : intarr(3),        $   ; band, scan id
		zang    : 0,				   $
		dnu     : 0.0d,				$
		npt     : 0l,				   $
		nulo    : 0.0d,				$
		nuhi    : 0.0d,				$
		gndalt  : 0.0,				   $
		wnu     : dblarr(maxpts),	$
		obsspc  : fltarr(maxpts),	$
		synspc  : fltarr(maxpts),	$
		difspc  : fltarr(maxpts) 	$
	}

	vec  = fltarr( 12 )
	lvec = fltarr( 13 )
	string1  = ''
	zang     = 0
	npt      = 0l
	dnu      = 0.0d
	nulo     = 0.0d
	nuhi     = 0.0d
	gndalt   = 0.0d
	nfits    = 0

   buf=''
   readf,lun, buf
   print, buf

	readf, lun, nfits, nband
	pbp = replicate( pbpstruct, nfits )
	pbp[0].nfit  = nfits
	pbp[0].nband = nband
   pbp[0].tag   = buf

	waverange= fltarr(2)
	npt=0l

	for kk = 0, nfits-1 do begin

      buf=''
      readf,lun, buf
      print, kk, ' ', buf
      pbp[kk].title   = buf

		readf, lun, zang, dnu, npt, nulo, nuhi, gndalt, i, j, k
		if( npt gt maxpts ) then begin
			print, 'spectral points in pbpfile: ', npt, ' is greater than size allocated: ', maxpts
			stop
		endif

		;print, npt

      pbp[kk].idex   = [i,j,k]
		pbp[kk].zang   = zang
		pbp[kk].dnu    = dnu
		pbp[kk].npt    = npt
		pbp[kk].nulo   = nulo
		pbp[kk].nuhi   = nuhi
		pbp[kk].gndalt = gndalt

		;help, pbp[kk].npt
		;help, npt
		nu  = fltarr( npt )
		obs = fltarr( npt )
		clc = fltarr( npt )
		dif = fltarr( npt )
		;help, obs

		rpt = fix( npt/12 )
		rem = npt - rpt * 12
		nu( 0:npt-1 ) = findgen( npt ) * dnu + nulo

		i = 0l
		j = 0l
		for i=0, rpt-1 do begin
			readf, lun, lvec
			for j=0,11 do obs(i*12+j) = lvec(j+1)
			readf, lun, vec
			for j=0,11 do clc(i*12+j) = vec(j)
			readf, lun, vec
			for j=0,11 do dif(i*12+j) = vec(j)
		endfor

		if( rem gt 0 ) then begin
			lrvec = fltarr( rem+1 )
			rvec = fltarr( rem )
			readf, lun, lrvec
			for j=0,rem-1 do obs((rpt)*12+j) = lrvec(j+1)
			readf, lun, rvec
			for j=0,rem-1 do clc((rpt)*12+j) = rvec(j)
			readf, lun, rvec
			for j=0,rem-1 do dif((rpt)*12+j) = rvec(j)
		endif

		pbp[kk].wnu[0:npt-1]    = nu
		pbp[kk].obsspc[0:npt-1] = obs
		pbp[kk].synspc[0:npt-1] = clc
		pbp[kk].difspc[0:npt-1] = dif ;* 100

	endfor

	free_lun, lun
	return, 0

end


; set file names  --------------------------------------------------------------------

pro setfilenames, pbfile, stfile

; spectra, fit & difference 	: pbpfile
pbfile = 'pbpfile';

; profile & apriori				: statevec
stfile = 'statevec';

end


function exponent, axis, index, number

	; a special case.
	if number eq 0 then return, '0'

	; assuming multiples of 10 with format.
	ex = string(number, format='(e8.0)')
	pt = strpos(ex, '.')

	first = strmid(ex, 0, pt)
	sign = strmid(ex, pt+2, 1)
	thisexponent = strmid(ex, pt+3)

	;print, number, ex, first
	;help, first, sign

	; shave off leading zero in exponent
	while strmid(thisexponent, 0, 1) eq '0' do thisexponent = strmid(thisexponent, 1)

	; fix for sign and missing zero problem.
	if (long(thisexponent) eq 0) then begin
		sign = ''
		thisexponent = '0'
	endif

	; make the exponent a superscript.
	if sign eq '-' then begin

	if( strtrim(first,2) eq '1' ) then begin
		return, '10!u' + sign + thisexponent + '!n'
	endif else begin
		return, first + 'x10!u' + sign + thisexponent + '!n'
	endelse

	endif else begin
	if strtrim(first,2) eq '1' then begin
		if strtrim(thisexponent,2) eq '0' then return, '1'
		if strtrim(thisexponent,2) eq '1' then return, '10'
		return, '10!u' + thisexponent + '!n'
		endif else begin
			return, first + 'x10!u' + thisexponent + '!n'
		endelse
	endelse


	end