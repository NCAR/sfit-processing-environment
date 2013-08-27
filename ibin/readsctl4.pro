; read in sfit4.ctl file --------------------------------------------------------------------

function readsctl4, ctl, file

   print, 'readsctl4 input file : ', file

	openr, lun, file, /get_lun, error=ioerr
	if( ioerr ne 0 ) then begin
		printf, -2, !err_string
		return, 1
	endif

      ctl = {									               $
         stalayers      : 'file.in.stalayers',        $
         refprofile     : 'file.in.refprofile',       $
         spectrum       : 'file.in.spectrum',         $
         modulation_fcn : 'file.in.modulation_fcn',   $
         phase_fcn      : 'file.in.phase_fcn',        $
         isa_matrix     : 'file.in.sa_matrix',        $
         isotope        : 'file.in.isotope',          $
         solarlines     : 'file.in.solarlines',       $
         linelist       : 'file.in.linelist',         $
         pbpfile        : 'file.out.pbpfile',         $
         statevec       : 'file.out.statevec',        $
         k_matrix       : 'file.out.k_matrix',        $
         kb_matrix      : 'file.out.kb_matrix',       $
         osa_matrix     : 'file.out.sa_matrix',       $
         retprofiles    : 'file.out.retprofiles',     $
         aprprofiles    : 'file.out.aprprofiles',     $
         ab_matrix      : 'file.out.ab_matrix',       $
         summary        : 'file.out.summary',         $
         parm_vectors   : 'file.out.parm_vectors ',   $
         seinv_vector   : 'file.out.seinv_vector',    $
         sainv_matrix   : 'file.out.sainv_matrix',    $
         smeas_matrix   : 'file.out.smeas_matrix',    $
         shat_matrix    : 'file.out.shat_matrix',     $
         ssmooth_matrix : 'file.out.ssmooth_matrix',  $
         ak_matrix      : 'file.out.ak_matrix',       $
         solarspectrum  : 'file.out.solarspectrum',   $
         n              : 26                          $ ; parameters in sfit4.ctl that we are getting
         }

   for i=0, ctl.n-1 do begin

      point_lun, lun, 0
      ;print, i, '  ', ctl.(i)
      while( not eof(lun) )do begin
         buf = ''
         readf, lun, buf
         ;print, buf
         if( strmid( strtrim( buf, 2 ), 0, strlen(ctl.(i))) EQ ctl.(i) )then begin
            ;print, ctl.(i)
            ;print, buf
            subs = strsplit( buf, /extract, count=count )
            ctl.(i) = subs[count-1]
            ;print, ctl.(i)
         endif

       endwhile

   endfor

   print, 'Readsctl4 : ', file, ' file done'
	free_lun, lun
   return, 0

stop
end
