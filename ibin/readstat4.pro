function readstat4, sts, file, rev=rev, quiet=quiet

; read in statevec file --------------------------------------------------------------------

   print, 'Readstat4 input file : ', file

	openr, lun, file, /get_lun, error=ioerr
	if( ioerr ne 0 ) then begin
		printf, -2, !err_string
		return, 1
	endif

   buf = ''
   dum = 0
	readf, lun, buf
	tag = buf
   buf = ''
   dum = 0
	readf, lun, buf
	subs = strsplit( buf, /extract, count=count )
	if( count ne 6 )then begin
	   print, count
	   print, subs
	   stop
	endif
	reads, subs[0], dum
	nlev = dum
	reads, subs[1], dum
	iter = dum
	reads, subs[2], dum
	itrx = dum
	if( subs[3] eq 'T' )then iftemp=1 else iftemp=0
	if( subs[4] eq 'T' )then converge=1 else converge=0
	if( subs[5] eq 'T' )then divwarn=1 else divwarn=0

   ;print , iftemp, converge, divwarn

	z = fltarr(nlev) & p = z & t = z & vmr = z & tr = z

   dum = ''
	readf, lun, dum & readf, lun, z
	readf, lun, dum & readf, lun, p
	readf, lun, dum & readf, lun, t
   if( iftemp )then begin
      readf, lun, dum & readf, lun, tr
   endif

	readf, lun, dum & readf, lun, ngas

   if( ngas EQ 0 )then begin
      sts = {									      $
         tag   : '',                         $
         nlev	: 0,						         $
         ngas	: 0, 						         $
         nprm  : 0,                          $
         iter  : 0,                          $
         itrx  : 0,                          $
         iftm  : 0,                          $
         cvrg  : 0,                          $
         dvrn  : 0,                          $
         prm   : dblarr( 2, 32 ),            $
         pnam  : STRARR( 32 ),               $
         z		: fltarr( nlev ),			      $
         p		: fltarr( nlev ),			      $
         t		: fltarr( nlev ),			      $
         tr		: fltarr( nlev )			      $
         }
   endif else begin
      sts = {									      $
         tag   : '',                         $
         nlev	: 0,						         $
         ngas	: 0, 						         $
         nprm  : 0,                          $
         iter  : 0,                          $
         itrx  : 0,                          $
         iftm  : 0,                          $
         cvrg  : 0,                          $
         dvrn  : 0,                          $
         prm   : dblarr( 2, 32 ),            $
         pnam  : STRARR( 32 ),               $
         z		: fltarr( nlev ),			      $
         p		: fltarr( nlev ),			      $
         t		: fltarr( nlev ),			      $
         tr		: fltarr( nlev ),			      $
         col	: fltarr( 2, ngas ),		      $
         vmr	: fltarr( 2, ngas, nlev ),	   $
         gas	: strarr( 2, ngas )			   $
         }
   endelse
   sts.tag  = tag
   sts.iftm = iftemp
   sts.itrx = itrx
   sts.iter = iter
   sts.cvrg = converge
   sts.dvrn = divwarn
   sts.nlev = nlev
   sts.ngas = ngas

   if( keyword_set(rev) )then begin
    if( ~keyword_set(quiet) )then print, 'Readstat: Reversing z,p,t,vmrs'
      sts.z[0:nlev-1] = REVERSE( z )
      sts.p[0:nlev-1] = REVERSE( p )
      sts.t[0:nlev-1] = REVERSE( t )
      sts.tr[0:nlev-1] = REVERSE( tr )
   endif else begin
      sts.z[0:nlev-1] = z
      sts.p[0:nlev-1] = p
      sts.t[0:nlev-1] = t
      sts.tr[0:nlev-1] = tr
   endelse

;	sts.z  = reverse( z )
;	sts.p  = reverse( p )
;	sts.t  = reverse( t )
;	sts.tr = reverse( tr )
;	sts.z  = z
;	sts.p  = p
;	sts.t  = t
;	sts.tr = tr

	col = 0.0
	name = ''

	for i = 0, ngas-1 do begin
		for j = 0, 1 do begin

			readf, lun, dum & readf, lun, name & readf, lun, col
			readf, lun, vmr

			sts.gas[j, i] = strtrim( name, 2 )
			sts.col[j, i] = col
         if( keyword_set(rev) )then sts.vmr[j, i, 0:nlev-1] = REVERSE( vmr ) $
         else sts.vmr[j, i, 0:nlev-1] = vmr

;			sts.vmr[j, i, *] = reverse( vmr )
			sts.vmr[j, i, *] = vmr

		endfor
	endfor

    READF, lun, dum & READF, lun, nprm
    sts.nprm = nprm

    if( nprm eq 0 ) then return, 0

    aprm     = dblarr(nprm)

    buf = ''
    n = floor(nprm/5)
    nleft = nprm mod 5
    if( nleft gt 0 )then n++

    j = 0
    for i=0, n-1 do begin
       readf, lun, buf
       subs = strsplit( buf, count=count, /extract)
       for k=0, count-1 do begin
          sts.pnam[j] = subs[k]
          ;print, j, sts.pnam[j]
          j++
          if( j gt nprm )then stop, 'too many parm names?!'
       endfor ; k
    endfor ; i

    ;print, j

    READF, lun, aprm
    sts.prm[0,0:nprm-1] = aprm

    READF, lun, aprm
    sts.prm[1,0:nprm-1] = aprm

   print, 'Read statevec file done'
	free_lun, lun
	return, 0

end


