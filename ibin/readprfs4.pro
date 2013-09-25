function readprfs4, prfs, file, rev=rev, quiet=quiet

; read in either apriori or retrieved profiles from sfit4 --------------------------------------------------------------------

; rev & quiet are not implemented


   print, 'readprfs4 input file : ', file

	openr, lun, file, /get_lun, error=ioerr
	if( ioerr ne 0 ) then begin
		printf, -2, !err_string
		free_lun, lun
		return, 1
	endif

   buf = ''
   dum = 0
	readf, lun, buf
	subs = strsplit( buf, /extract, count=count )
	ver = subs(0)
	tag = subs(1)
   ttl = subs(2:count-1)

   buf = ''
	readf, lun, buf
	subs = strsplit( buf, /extract, count=count )
	ngas = 0
	reads, subs[0], ngas, format='(i)'
	nlev = 0
	reads, subs[1], nlev, format='(i)'
	nret = 0
	reads, subs[2], nret, format='(i)'

	print, ngas, nlev, nret

   prfs = {								      $
      ver   : ver,                     $
      tag   : tag,                     $
      ttl   : ttl,                     $
      ngas	: ngas,						   $
      nlev	: nlev,						   $
      nret	: nret,						   $
      rnam  : strarr( nret ),          $
      name	: strarr( ngas ), 			$
      z     : dblarr( nlev ),          $
      zbar	: dblarr( nlev ),			   $
      p		: dblarr( nlev ),			   $
      t		: dblarr( nlev ),			   $
      a   	: dblarr( nlev ),			   $
      vmr	: dblarr( nlev, ngas )		$
   }

   for i=3, count-1 do prfs.rnam[i-3] = strtrim( subs[i], 2 )
   readf, lun, buf
   buf = ''
   readf, lun, buf

   subs = strsplit( buf, /extract, count=count )
   if( count ne ngas + 5 )then begin
      print, 'error in number of columns'
      free_lun, lun
      stop
   endif

   for i=0, ngas-1 do prfs.name[i] = strtrim( subs[i+5], 2 )

   for i= 0, nlev-1 do begin

      buf = dblarr( ngas + 5 )
      readf, lun, buf
      prfs.z[i]            = buf[0]
      prfs.zbar[i]         = buf[1]
      prfs.t[i]            = buf[2]
      prfs.p[i]            = buf[3]
      prfs.a[i]            = buf[4]
      prfs.vmr[i,0:ngas-1] = buf[5:5+ngas-1]

   endfor


   print, 'Readprfs4 : ', file, ' file done'

	free_lun, lun
	return, 0

end


