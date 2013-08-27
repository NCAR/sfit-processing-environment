function readrfmd4, refm, file, zpt=zpt

   print, 'readrfmd4 input file : ', file

	openr, lun, file, /get_lun, error=ioerr
	if( ioerr ne 0 ) then begin
		printf, -2, !err_string
		return, 1
	endif

   openr, lun, file, /get_lun

   nlines = 10

   buffer = ''
   readf, lun, updn, nlay, nmol
   ;print, lun, updn, nlay, nmol

   refm = {   $
      nlay : nlay,               $
      updn : updn,               $
      nmol : nmol,               $
      id   : intarr(nmol+3),		$
		name : strarr(nmol+3),			$
		titl : strarr(nmol+3),			$
		prfs : dblarr(nmol+3, nlay)	$
		}

   arr = fltarr(nlay)

   if( keyword_set (zpt) ) then begin

         refm.id[0] = 0
         refm.name[0] = 'Altitude'
         readf, lun, buffer
         refm.titl[0] = buffer
         readf, lun, arr
         refm.prfs[0,*] = arr

         refm.id[1] = 0
         refm.name[1] = 'Pressure'
         readf, lun, buffer
         refm.titl[1] = buffer
         readf, lun, arr
         refm.prfs[1,*] = arr

         refm.id[2] = 0
         refm.name[2] = 'Temperature'
         readf, lun, buffer
         refm.titl[2] = buffer
         readf, lun, arr
         refm.prfs[2,*] = arr

    endif else begin
      for i = 0, 2 do begin
         refm.id[i] = 0
         refm.name[i] = ''
         refm.titl[i] = ''
         refm.prfs[i,*] = 0
       endfor
   endelse


   for i = 3, nmol+2 do begin

      readf, lun, buffer
      readf, lun, arr
      ;print, buffer
      strs = strsplit( buffer, count=count, /extract )

      reads, strs[0], id, format='(i)'
         refm.id[i] = id
         refm.name[i] = strs[1]
         buffer = ''
         for j=2,count-1 do begin
            buffer = buffer + ' ' + strs[j]
         end
         refm.titl[i] = buffer
         refm.prfs[i,*] = arr

   endfor

   free_lun, lun
   return, 0

stop
end