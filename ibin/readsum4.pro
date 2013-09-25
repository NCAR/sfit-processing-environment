function readsum4, sumf, file

   print, 'readsum4 input file : ', file

	openr, lun, file, /get_lun, error=ioerr
	if( ioerr ne 0 ) then begin
		printf, -2, !err_string
		return, 1
	endif

   buf = ''
   dum = 0
	readf, lun, buf
	subs = strsplit( buf, /extract, count=count )
	ver = subs(0)
	tag = subs(1)
   ttl = subs(2:count-1)

; read headers for all spectra (fits)
   buf = ''
   readf, lun, buf
   readf, lun, nfit
   spechead = strarr(nfit)
   for i=0, nfit-1 do begin
      buf = ''
      readf, lun, buf
      spechead[i] = buf
   endfor

; read data for all retrieved gases
   buf = ''
   readf, lun, buf
   readf, lun, nret
   readf, lun, buf
   sret = strarr(nret)
   for i=0, nret-1 do begin
      buf = ''
      readf, lun, buf
      sret[i] = buf
   endfor

; read data by band
   buf = ''
   readf, lun, buf
   readf, lun, nband
   readf, lun, buf
   ;print, buf
   sband = strarr(nband)
   sjscn = strarr(nband, 10)
   nscnb = intarr(nband)
   npts = intarr(nband)
   wstrt = fltarr(nband)
   wstop = fltarr(nband)
   nspac = fltarr(nband)
   for i=0, nband-1 do begin
      buf = ''
      readf, lun, buf
      sband[i] = buf
      ;print, sband[i]
      subs = strsplit( sband[i], /extract, count=count )
      nscnb[i] = subs[count-1] + 0
      ;print, count
      ;print, subs
      npts[i]     = subs[4] + 0
      wstrt[i]    = subs[1] + 0.0D0
      wstop[i]    = subs[2] + 0.0D0
      nspac[i]     = subs[3] + 0.0D0
      for j=0, nscnb[i]-1 do begin
         readf, lun, buf
         sjscn(i,j) = buf
      endfor
   endfor

; read retparm list
   readf, lun, buf
   readf, lun, buf
   parms = ''
   readf, lun, parms
   subs = strsplit( parms, /extract, count=count )
   fitrms  = subs[0] + 0.0D0
   chi_2_y = subs[1] + 0.0D0
   dofstrg = subs[3] + 0.0D0
   itr     = subs[5] + 0
   convTF  = subs[7] 
   divwarn = subs[8]


; store data
   sumf = {                $
      ver  : ver,          $
      tag  : tag,          $
      ttl  : ttl,          $
      nfit : nfit,         $
      nret : nret,         $
      nbnd : nband,        $
      nscn : nscnb,        $
      npts : npts,         $
      wstr : wstrt,        $
      wstp : wstop,        $
     nspac : nspac,        $
     shead : spechead,		 $
		  sret : sret,			   $
		  sbnd : sband,		     $
		 sjscn : sjscn,			   $
		fitrms : fitrms,	     $
	 chi_2_y : chi_2_y,      $
	 dofstrg : dofstrg,      $
		   itr : itr,          $
		convTF : convTF,       $
	 divwarn : divwarn       $
		}

help, sumf

   free_lun, lun
   return, 0

stop
end