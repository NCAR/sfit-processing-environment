pro ckopdd, ddfile=ddfile

; reads in daydirs and loops over them calling ckop

if( not keyword_set( ddfile )) then begin
   print, ' !!  must set ddfile arg to a "date.nn" file'
   stop
endif

openr, lun, ddfile, /get_lun

   while( NOT eof( lun ) ) do begin

      daydir=''
      readf, lun, daydir

      if( strmid(daydir,0,1) EQ '#' )then begin
         print, daydir
         continue
      endif

      if( strmid(daydir,0,1) EQ '!' )then begin
         print, 'End of input...'
         break
      endif

      testdir = file_test( daydir, /directory )

      if( file_test( daydir, /directory ) )then begin

         cd, daydir
         spawn, 'pwd'
         spawn, 'ls'
         rc = ckop()
         cd, '..'
         if( rc eq 1 ) then stop
      endif else begin
         print, daydir,' is not a directory...skipping'
         continue
      endelse

   endwhile

free_lun, lun

return

end
