FUNCTION readpbp4, pbp, file

   print, 'readpbp4 input file : ', file

	maxpts = 262144L

	OPENR, lun, file, /GET_LUN, ERROR=ioerr
	IF( ioerr NE 0 ) THEN BEGIN
	PRINTF, -2, !ERR_STRING
	RETURN, 1
	ENDIF

	pbpstruct = { 					$
		tag     : '',           $
		title   : '',              $
		nfit    : 0,				$
		nband   : 0,				   $
		idex   : intarr(3),        $   ; band, scan id
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

   tag = ''
	READF, lun, tag
	print, tag
	READF, lun, nfits, nbands
	pbp = REPLICATE( pbpstruct, nfits )
	pbp[0].nfit  = nfits
	pbp[0].nband = nbands
   pbp[0].tag   = tag

   buf=''
   ;readf,lun, buf
   ;print, buf

	waverange= fltarr(2)
	npt=0l

	FOR kk = 0, nfits-1 DO BEGIN

; maybe this is read each block or maybe only at top...
      readf,lun, buf
      print, buf

		READF, lun, zang, dnu, npt, nulo, nuhi, gndalt, i, j, k
      print, zang, dnu, npt, nulo, nuhi, gndalt

		IF( npt GT maxpts ) THEN BEGIN
			PRINT, 'Spectral points in pbpfile: ', npt, ' is greater than size allocated: ', maxpts
			STOP
		ENDIF

		;PRINT, npt
      print, zang, dnu, npt, nulo, nuhi, gndalt
      pbp[kk].idex   = [i,j,k]
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

   print, 'Read pbpfile done.'

	FREE_LUN, lun
	RETURN, 0

END

