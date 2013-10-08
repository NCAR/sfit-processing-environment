pro plt4, file=file, last=last, site=site, big=big, dir=dir

; August 2013
; reads a list file of completed retrievals from sfit4Layer1.py and calls oex4

   close, /all

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
   while( not eof(lun) and not strcmp(buf, 'Date', 4 ) ) do begin
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
      print, subs(2)
      oex4, site=site, big=big, /ps, dir=subs(2)

   endif else begin

      n=0
      while( not eof(lun) )do begin
         readf, lun, buf
         n++
      endwhile
      print, 'Found : ', n, ' retrievals in list file : ', file
      retrievalist = strarr( n )
      point_lun, lun, 0
      while( not eof(lun) and not strcmp(buf, 'Date', 4 ) ) do readf, lun, buf
      for i=0, n-1 do begin
         readf, lun, buf
         retrievalist(i) = buf
      endfor
      free_lun, lun

      des = 0
      for i=0, n-1 do begin
         print, 'Retrieval : ', i+1, '  ', retrievalist(i)
         subs = strsplit( retrievalist(i), /extract, count=count )
         print, 'Plotting from directory : ', subs(2)
         if( keyword_set( dir) )then begin
            oex4, site=site, big=big, /ps, dir=subs(2)
         endif else begin
            oex4, site=site, big=big, dir=subs(2)
         endelse
         print, '  Retrieval : ', i+1, '  ', retrievalist(i)
         print, ' Done with # ', i+1, ' of : ', n
         read, des, prompt='enter 0=quit, 1=next, n=skip to nth retrieval : '
         print, des
         if( des EQ 0 )then stop
         if( des GT 1 )then begin
            i = des-2
            if( i GT n-1 )then begin
               print, 'Asked for more fits thane we have : ,', n, des
               print, ' plotting last one.'
               i = n-2
            endif
         endif
     endfor

   endelse

   print, 'PLT4 .done.'
stop
end