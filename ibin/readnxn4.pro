function readnxn4, nxn, file, rev=rev, quiet=quiet

; Read in n by n file --------------------------------------------------------------------
;  such as SM.out an SS.out


	openr, lun, file, /get_lun, error=ioerr
	if( ioerr ne 0 ) then begin
		printf, -2, !err_string
		return, 1
	endif

   buf = ''
	readf, lun, buf
	subs = strsplit( buf, /extract, count=count )
	ver = subs(0)
	tag = subs(1)
   ttl = subs(2:count-1)

	n = 0
	readf, lun, n, n1
	if( n ne n1 )then begin
	   print, 'readnxn4 : matrix should be square : ', n, n1
	   stop
	endif
	;print, ' readnxn, n : ', n

	nxn = {		               $
	   ver   : ver,            $
      tag   : tag,            $
      ttl   : ttl,            $
		n	   : n,		  			$
		mat	: dblarr( n, n )	$
	}

	mat = dblarr( n, n )
	readf, lun, mat

   if( keyword_set(rev) )then begin
      if( ~keyword_set(quiet) )then print, 'Readnxn4: Reversing each dimension'
      mat = reverse( mat, 1 )
      mat = reverse( mat, 2 )
   endif

	; transpose so get mak(k,*) is a 'row' (kernel)
	;mat = transpose( mat )

	nxn.mat = mat
	mat = 0

   print, 'Readnxn4 : ', file, ' file done'
	free_lun, lun
	return, 0

end


