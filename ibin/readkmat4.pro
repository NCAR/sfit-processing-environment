; Read in K matrix file --------------------------------------------------------------------

FUNCTION readkmat4, kmf, file

   print, 'Readkmat4 input file : ', file

; in sfit4 we transposed the k matrix in the k file
; nparam columns x npoints rows

	openr, lun, file, /get_lun, error=ioerr
	if( ioerr ne 0 ) then begin
		printf, -2, !err_string
		return, 1
	endif

	dums = ''
	npts = 0L		; number of spectral points
	npar = 0		; number of parameters
	ismx = 0		; last pt before mixing ratios
	nlev = 0		; same number of levels

   vertagtitle = ''

	READF, lun, vertagtitle
   subs = strsplit( vertagtitle, /extract, count=count )
   ver = subs[0]
   tag = subs[0:1]
   ttl = subs[2:count-1]
   ;print, tag
   ;print, ttl
	READF, lun, npts, npar, ismx, nlev
	;PRINT, npts, npar, ismx, nlev

	kmf = {		 						   $
		npts    : npts,					$
		npar    : npar,					$
		ismx    : ismx,					$
		nlev    : nlev,					$
		tag     : tag,                $
		title   : ttl,                $
		pname   : strarr(npar),       $
		mat    : DBLARR( npar, npts )$
	}

   ; pname
   pname = ''
   readf, lun, pname
   subs = strsplit( pname, /extract, count=count )
   if( count ne npar )then begin
      print, 'error # values in pname not equal to npar : ', count, npar
      stop
   endif
   kmf.pname[0:npar-1] = subs[0:count-1]
   ;print, kmf.pname[0:npar-1]

	; K
	mat = DBLARR( npar, npts )
	READF, lun, mat
	;print, max(mat), min(mat)

	;print, mat[0:2,0]
	kmf.mat = transpose(mat)
	kmf.mat = mat

   print, 'Read k matrix done.'
	FREE_LUN, lun
	RETURN, 0

END
