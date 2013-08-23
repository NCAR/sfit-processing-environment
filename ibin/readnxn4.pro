FUNCTION readnxn, nxn, file, rev=rev, quiet=quiet

; Read in n by n file --------------------------------------------------------------------
;  such as SM.out an SS.out


	OPENR, lun, file, /GET_LUN, ERROR=ioerr
	IF( ioerr NE 0 ) THEN BEGIN
		PRINTF, -2, !ERR_STRING
		RETURN, 1
	ENDIF

	n = 0
	READF, lun, n
	;print, ' readnxn, n : ', n
	mat = DBLARR( n, n )
	READF, lun, mat

   if( keyword_set(rev) )then begin
      if( ~keyword_set(quiet) )then print, 'Readnxn: Reversing each dimension'
      mat = REVERSE( mat, 1 )
      mat = REVERSE( mat, 2 )
   endif

	; transpose so get mak(k,*) is a 'row' (kernel)
	mat = TRANSPOSE( mat )

	nxn = {		               $
		n	   : 0,		  			$
		mat	: DBLARR( n, n )	$
	}
	nxn.n   = n
	nxn.mat = mat

	mat = 0

	FREE_LUN, lun
	RETURN, 0
END


