function readt154, t15, file

   print, 'readt154 input file : ', file

	openr, lun, file, /get_lun, error=ioerr
	if( ioerr ne 0 ) then begin
		printf, -2, !err_string
		return, 1
	endif

; find the number of blocks

   n = 0
   mxpts = 0L
   buf1 = ''
   readf, lun, buf1
   while( ~ eof( lun ) )do begin

      n++
      readf, lun, buf1
      readf, lun, buf1
      readf, lun, buf1
      sb = strsplit( buf1, /extract, cnt )
      npts = sb(cnt-1) +0L
      amps = dblarr( npts )
      mxnpts = max( [mxnpts, npts] )
      readf, lun, amps
      readf, lun, buf1

   endwhile

   print, ' Found : ', n ' blocks in file : ' file

   t15 = {
      sbuf  : strarr(n, 4),   $
      tstmp : long(n),     $
      npts  : long(n),     $
      amps  : dblarr(n, mxnpts) $
      }

   point_lun, lun, 0

   for i=0, n-1 do begin
      buf = ''
      for j = 0, 3 do begin
         readf, lun, buf
         t15.sbuf[i,j] = buf
      endfor

      sb = strsplit( t15.sbuf[i,2], /extract, cnt )
      t15.npts[j] = sb[3]*10000L + sb[4]*100L + sb[5]

      sb = strsplit( t15.sbuf[i,3], /extract, cnt )
      t15.npts[j] = sb(cnt-1) +0L
      amps = dblarr( t15.npts[j] )
      readf, lun, amps
      t15.amps[i,0:t15.npts[j]-1] = amps

   endfor

   free_lun, lun

   print, 'Read t15asc file Done.'

return, 0
end
