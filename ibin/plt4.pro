pro plt4, file=file, last=last, site=site, big=big

; August 2013
; reads a list file of completed retrievals from sfit4Layer1.py and calls oex4

   if( not keyword_set( file )) then begin
      print, '  main : enter a layer1 list file'
      stop
   endif
   if( not keyword_set( file )) then begin
      print, '  main : enter a site eg site="mlo"'
      stop
   endif
   if( not keyword_set( big )) then begin
      print, '  main : setting big=0'
      big = 0
   endif

   funcs = [ 'oex4' ]
   resolve_routine, funcs, /either

   openr, lun, file, /get_lun, error=ioerr
   if( ioerr ne 0 ) then begin
      printf, -2, !err_string
      stop
   endif

   buf = 'zz'
   while( not eof(lun) and not strcmp(buf, 'TimeStamp', 9 ) ) do begin
      readf, lun, buf
      ;print, buf
   endwhile
   ;print, buf

   if( eof(lun) )then begin
      print, 'Reached end of list file : ', file
      print, 'Stopping...'
      stop
   endif

   if( keyword_set( last ) )then begin
      while( not eof(lun) )do begin
         readf, lun, buf
         ;print, buf
      endwhile
      subs = strsplit( buf, /extract, count=count )
      print, subs(count-1)
      oex4, site=site, big=big, /ps, dir=subs(1)
   endif else begin

      while( not eof(lun) )do begin
         readf, lun, buf
         ;print, buf
         subs = strsplit( buf, /extract, count=count )
         print, 'Plotting from directory : ', subs(1)
         oex4, site=site, big=big, /ps, dir=subs(1)
         des = 'z'
         read, des, prompt='enter c to continue, q to quit : '
         if( des eq 'q' )then stop
     endwhile

   endelse





stop
end