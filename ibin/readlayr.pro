function readlayr, mygrd, filename, rev=rev, quiet=quiet

; see mklev.pro to create the layers this code reads

; Jan 2010
; read a 'station.layers' file for the retrieval alt grids
;filename = 'station.layers'

buf = ''
openr, lun, filename, /get_lun
readf, lun, buf
readf, lun, klay
readf, lun, buf
;print, buf
mygrd = {k          : klay,		      $
	      alts       : dblarr(klay),    $
	      thik       : dblarr(klay),    $
	      grth       : dblarr(klay),    $
	      midp       : dblarr(klay)     }

dat = dblarr(5,klay)
readf, lun, dat
free_lun, lun

if( keyword_set(rev) )then begin
   if( ~keyword_set(quite) )then print,'Readlayr: reversing alts...'
   mygrd.alts = reverse(dat[1,*],2)
   mygrd.thik = reverse(dat[2,*],2)
   mygrd.grth = reverse(dat[3,*],2)
   mygrd.midp = reverse(dat[4,*],2)
endif else begin
   mygrd.alts = dat[1,*]
   mygrd.thik = dat[2,*]
   mygrd.grth = dat[3,*]
   mygrd.midp = dat[4,*]
endelse

;print, mygrd.midp

return, fix(klay) ; midpoints
end
