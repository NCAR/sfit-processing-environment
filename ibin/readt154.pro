function readt154, t15, file

   print, 'Readt154 input file : ', file

	openr, lun, file, /get_lun, error=ioerr
	if( ioerr ne 0 ) then begin
		printf, -2, !err_string
		return, 1
	endif

; find the number of blocks

   n = 0
   mxpts = 0L
   buf1 = ''

   while( ~ eof( lun ) )do begin

      readf, lun, buf1
      readf, lun, buf1
      readf, lun, buf1
      readf, lun, buf1
      sb = strsplit( buf1, /extract, count=count )
      npts = sb(count-1) +0L
      amps = dblarr( npts )
      mxpts = max( [mxpts, npts] )
      readf, lun, amps
      n++

   endwhile

   print, ' Found : ', n, ' blocks in file : ', file

   t15 = { $
      sbuf  : strarr(n, 4),     $
      tstmp : long(n),          $
      npts  : long(n),          $
      amps  : dblarr(n, mxpts)  $
      }

   point_lun, lun, 0

   for i=0, n-1 do begin
      buf = ''
      for j = 0, 3 do begin
         readf, lun, buf
         t15.sbuf[i,j] = buf
      endfor

      sb = strsplit( t15.sbuf[i,1], /extract, count=count )
      t15.tstmp[i] = long(sb[3])*10000L + long(sb[4])*100L + long(sb[5]) + 0L

      sb = strsplit( t15.sbuf[i,3], /extract, count=count )
      t15.npts[i] = sb(count-1) +0L
      amps = dblarr( t15.npts[i] )
      readf, lun, amps
      t15.amps[i,0:t15.npts[i]-1] = amps

   endfor

   free_lun, lun

   print, 'Read t15asc file Done.'

return, 0
end
