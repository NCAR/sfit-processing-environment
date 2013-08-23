pro ch4comp, ratio=ratio, mkinput=mkinput, dry=dry, apcnt=apcnt

	if( not keyword_set( ratio ))then begin
		print, '  ch4comp 1 : keyword ratio not set.'
		print, '  ch4comp 2 : setting default ratio = FALSE.'
	   ratio = 0
	endif

	if( not keyword_set( mkinput ))then begin
		print, '  ch4comp 3 : keyword mkinput not set.'
		print, '  ch4comp 4 : setting default mkinput = FALSE.'
	   mkinput = 0
	endif

	if( not keyword_set( dry ))then begin
		print, '  ch4comp 5 : keyword dry not set.'
		print, '  ch4comp 6 : setting default dry = FALSE.'
	   dry = 0
	endif

	if( not keyword_set( apcnt ))then begin
		print, '  ch4comp 5 : keyword apcnt not set.'
		print, '  ch4comp 6 : setting default apcnt = FALSE.'
	   apcnt = 0
	endif

   forward_function plotrat, plotann, plotcnt, plotdrl, sortem, getdata, plotvmr

   rc = getdata( nf, lines, mkinput, fdex, label )

   rc = sortem( nf, lines, fdex )

; Read in layers file station.layers
   lyfile = '/project/ya4/sfit/tab/station.layers'
	rc = 0
	klay = readlayr( grd, lyfile )
	alt  = grd.midp[1:klay-1]

   hdoscl = 1.d22
   ch4scl = 1.d19
   h2ofrc = 0.997318d0
   hdofrc = 3.1069d-4

   if( dry )then begin
      for k=0, nf-1 do begin
         dex = lines[k,0].dex
         a = h2ofrc/hdofrc
         ;print, a
         b = lines[k,dex].ch4/lines[k,dex].air
         ;print, b
         c = lines[k,dex].ch4 - (lines[k,dex].hdo*b)
         ;help, c
         ;for j=0, lines[k,0].cnt-1 do print, lines[k,dex[j]].ch4, c[j], c[j]/lines[k,dex[j]].ch4
         lines[k,dex].ch4 = c
      endfor
   endif

   ppos = INTARR(3)
   ppos = [ 10, 380, 0 ]
   psiz = INTARR(2)
   psiz = [ 600, 465 ]
   tek_color

   for tops =0, 1 do begin

      if tops then begin ;1
         set_plot, 'ps'
         psfile = 'ch4comp.ps'
         print, '  ch4comp 5 :saving ps file to : ', psfile
         encap = 0
         device, /color, /landscape, filename = psfile, encapsulated = encap, bits=8
         !p.charsize = 1
         !p.charthick = 4.0
         tek = 0 ; black

      endif else begin
         set_plot,'x'
         device, decompose = 0 ; allow for terminals with > 256 color
         !p.charsize = 1.7
         !p.charthick = 1
         tek = 1 ; white
      endelse

      rc = plotrat( lines, nlines, nf, ratio, tops, ppos, psiz, hdoscl, ch4scl, fdex, label)

      rc = plotcnt( lines, nlines, nf, tops, ppos, psiz, hdoscl, fdex, label)

      rc = plotann( lines, nlines, nf, ratio, tops, ppos, psiz, hdoscl, ch4scl, 'CH4', fdex, apcnt, label)

      rc = plotann( lines, nlines, nf, ratio, tops, ppos, psiz, hdoscl, ch4scl, 'HDO', fdex, apcnt, label)

      ;rc = plotdrl( lines, nlines, nf, ratio, tops, ppos, psiz, hdoscl, ch4scl, 'CH4', fdex)

      ;rc = plotdrl( lines, nlines, nf, ratio, tops, ppos, psiz, hdoscl, ch4scl, 'HDO', fdex)

      rc = plotvmr( lines, nlines, nf, alt, tops, ppos, psiz, hdoscl, ch4scl, fdex, label)

      if tops then device, /close_file

   endfor ; tops

stop

end


function getdata, nf, lines, mkinput, fdex, label

   naltmax = 47

   allnf = 16
   files = strarr(allnf)
   label = strarr(allnf)

   files[0] = '/project/ya4/sfit/tab1.1/ch4_jun_1a'   ; hit00      135
   files[1] = '/project/ya4/sfit/tab1.1/ch4_jun_1b'   ; hit08      12345
   files[2] = '/project/ya4/sfit/tab1.1/ch4_jun_1c'   ; hit08      1234
   files[3] = '/project/ya4/sfit/tab1.1/ch4_jun_1d'   ; hit08      673
   files[4] = '/project/ya4/sfit/tab1.1/ch4_jun_2d'   ; hit08      673  not_tik
   files[5] = '/project/ya4/sfit/tab1.1/ch4_jun_3d'   ; hit08      673  not_tik wider #7 fit hdo in all 3
   files[6] = '/project/ya4/sfit/tab1.1/ch4_jun_4d'   ; hit08      673  not_tik wider #7 fit hdo in all 3 wider #3
   files[7] = '/project/ya4/sfit/tab1.1/ch4_jun_5d'   ; hit08      673  not_tik wider #7 fit hdo in all 3 wider #3 .1 hdo variance
   files[8] = '/project/ya4/sfit/tab1.1/ch4_jun_2a'   ; hit00      135 curv
   files[9] = '/project/ya4/sfit/tab1.1/ch4_jun_1e'   ; hit08      67 curv (from 5d)
   files[10]= '/project/ya4/sfit/tab1.1/ch4_jun_1f'   ; hit08      87  8 is wide 6
   files[11]= '/project/ya4/sfit/tab1.1/ch4_jun_2f'   ; hit08      87  wider 8 prof fit of hdo
   files[12]= '/project/ya4/sfit/tab1.1/ch4_jun_6a'   ; hit08      897
   files[13]= '/project/ya4/sfit/tab1.1/ch4_jun_1g'   ; hit08 + FH mods not finished
   files[14]= '/project/ya4/sfit/tab1.1/ch4_jun_7a'   ; hit08      8a97
   files[15]= '/project/ya4/sfit/tab1.1/ch4_jun_7b'   ; hit08      8a7

   label[0] = 'HIT00_135 (1a) '
   label[1] = 'HIT08_12345 (1b) '
   label[2] = 'HIT08_1234 (1c) '
   label[3] = 'HIT00_673 (1d) '
   label[4] = 'HIT00_673 (2d) no_tik'
   label[5] = 'HIT00_673 (3d) no_tik wide7'
   label[6] = 'HIT00_673 (4d) no_tik wide wide3'
   label[7] = 'HIT00_673 5d) no_tik wide wide3 curv'
   label[8] = 'HIT00_135 (2a) curv '
   label[9] = 'HIT08_67 (1e) '
   label[10] = 'HIT08_87 (1f) '
   label[11] = 'HIT08_87 (2f) '
   label[12] = 'HIT08_897 (6a) '
   label[13] = 'HIT08_897 (1g) '
   label[14] = 'HIT08_8a97 (7a) '
   label[15] = 'HIT08_8a7 (7b) '

   nf = 4
   ; first 2 are always 0 & 1 for ratios
   fdex = [0,1,2,12] ; index of dataset

   dayzero = JULDAY( 1, 1, 2006, 0, 0, 0 ) -1
   maxline = 166

	A = {data,   line :'',     $
	             jday :0.0D,	$
	             rms  :0.0D,	$
	             dofs :0.0D,  	$
	             hdo  :0.0D,	$
	             ch4  :0.0D,   $
	             doy  :0.0D,   $
	             air  :0.0D,   $
	             vmr  :dblarr(50), $
	             pcl  :dblarr(50), $
	             nln  :0,      $ ; # lines from input file
	             cnt  :0,      $ ; # common lines all files
	             dex  :intarr(maxline) } ; index of common lines

	lines = REPLICATE( {data}, nf, maxline )

   for k=0, nf-1 do begin

      kk = fdex[k]

      lfile = files[kk] + '/Rslt.l'
      print, '  getdata : lfile : ', lfile

      if( mkinput )then rc = getstatparm( lfile=lfile, dir=files[kk] )

      statfile = files[kk] + '/getstates.out'

      ; get vmrs
      qfile = files[kk] + '/Rslt.q'
      pfileread, qfile, qline, naltmax, nq, dates, ndate, maxline

      ; get partial columns
      qcfile = files[kk] + '/Rslt.qc'
      pfileread, qcfile, qcline, naltmax, nqc, dates, ndate, maxline

      openr, lun, statfile, /get_lun

      readf, lun, nlines
      lines[k,0].nln = nlines

      for j=0, nlines-1 do begin
         jd = 0.0d0
         rm = 0.0d0
         df = 0.0d0
         hd = 0.0d0
         ch = 0.0d0
         ar = 0.0d0
         buffer = ''
         readf, lun, buffer

         lines[k,j].line = buffer
         reads, buffer, jd, rm, df, hd, ch, ar

         lines[k,j].jday = jd
         lines[k,j].rms  = rm
         lines[k,j].dofs = df
         lines[k,j].hdo  = hd
         lines[k,j].ch4  = ch
         lines[k,j].air  = ar
         lines[k,j].doy  = jd - dayzero

         lines[k,j].vmr[0:naltmax-1] = qline[j].vmr[0:naltmax-1]

         lines[k,j].pcl[0:naltmax-1] = qcline[j].vmr[0:naltmax-1]

      endfor ; j

      free_lun, lun

   endfor ; k

   help, lines

return, 0
end


function sortem, nf, lines, fdex

   mxlines = max( lines[*,0].nln )
   print, '  sortem 1 : mxlines : ', mxlines

   dex = intarr(mxlines,nf)
   cnt = intarr(nf)

   for k=0, nf-1 do begin

      nlines = lines[k,0].nln

      for i=0, nlines-1 do begin
         if( lines[k,i].hdo gt 0.0 && lines[k,i].ch4 gt 0.0 && lines[k,i].rms lt 0.6 ) $
         then begin
            dex[cnt[k],k] =  i
            cnt[k] = cnt[k] +1
         endif

      endfor ; i

   endfor ; k

   for k=0, nf-1 do begin
      print, k, cnt[k]
   endfor

   mincnt = min( cnt[0:nf-1] )
   d = where( cnt[0:nf-1] eq mincnt )
   dx = d[0]

   print, '  sortem 2 : minimum index and value : ', dx, cnt[dx]

   minjd = lines[dx,dex[0:cnt[dx]-1,dx]].jday

   for k=0, nf-1 do begin

      if( k eq dx )then continue

      newcnt = 0
      newminjd = dblarr(mincnt)

;print, mincnt
;help, newminjd
;print, '  new k, cnt : ', k, cnt[k]

      thisjd = lines[k,dex[0:cnt[k]-1,k]].jday

      for i=0, mincnt-1 do begin
         flag = 0

         for j=0, cnt[k]-1 do begin
            if( thisjd[j] eq minjd[i] )then begin
;print, newcnt
               newminjd[newcnt] = minjd[i]
               newcnt++
               flag = 1
               continue
            endif

         endfor ; j
         if( flag eq 1 )then continue
      endfor ; i

;print, '  post, common newcnt : ', newcnt

      minjd = dblarr(newcnt)
      minjd = newminjd[0:newcnt-1]
      mincnt = newcnt

   endfor ; k

   print, '  sortem 3 : common good daytimes : ', mincnt

   for k=0, nf-1 do begin

      for i=0, mincnt-1 do begin
         flag = 0
         for j=0, nlines-1 do begin
            if( lines[k,j].jday eq minjd[i] )then begin
               lines[k,0].dex[i] = j
               lines[k,0].cnt = lines[k,0].cnt +1
               flag = 1
               continue
            endif
         endfor ; j
         if( flag eq 1 )then continue
      endfor ; i

      ;print, lines[k,0].cnt
      ;print, lines[k,0].dex[0:lines[k,0].cnt-1]
   endfor ; k

   for i=0, lines[0,0].cnt-1 do begin
      j = lines[0,0].dex[i]
      caldat, lines[0,j].jday, mm, dd, yy
      print, i, j, lines[0,j].jday, yy, mm, dd, lines[fdex,j].ch4, format='(2i5,f15.3,i6,i02,i02,10e12.3)'
   endfor

   return, 0

end


function plotvmr, lines, nlines, nf, alt, tops, ppos, psiz, hdoscl, ch4scl, fdex, label

   cnt = lines[0,0].cnt
   dex = lines[0,0].dex[0:cnt-1]

   for k = 0, nf-1 do begin ; nf-1

      kk = fdex[k]

      mol = 'CH4'

      kk = fdex[k]

      lab = label[kk] + mol

      title='pltvmr : ' + lab

      if tops then begin
         erase
         xcharsz = 1.0
         ycharsz = 1.0
         charsz = 1.7
      endif else begin
         ppos = ppos + [ 20, -20, 1 ]
         window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1], xpos = ppos[0], ypos = ppos[1], $
                 title = title
         device, decompose = 0
         xcharsz = 1.8
         ycharsz = 1.8
         charsz = 1.7
         !p.charsize = 1
      endelse

      yrange = [0., 60.]
      xrange = [0., 3.]
      yx = 3.2
      yti = ' column / 1e19'
      yx = 107.
      yxs = 0.005
      yti = '% '+ ' column of mean'
      scl = 1.e-6

      yy = reform(lines[k,dex].vmr)

      plot, yy[0,*]/scl, alt, /nodata, charsize = charsz, $
            yrange = yrange, xrange = xrange, $
            ytitle = 'Altitude [km]', xtitle = ' VMR * 1e6 : '+ lab, title = title

      for i=0, cnt-1 do oplot, yy[*,i]/scl, alt ;, color = i+1

   endfor ;k

return, 0
end


function plotdrl, lines, nlines, nf, ratio, tops, ppos, psiz, hdoscl, ch4scl, mol, fdex, label

   title = 'plotdrl : mean diurnal cycle'

   if tops then begin
      erase
      xcharsz = 1.0
      ycharsz = 1.0
      charsz = 1.7
   endif else begin
      ppos = ppos + [ 20, -20, 1 ]
      window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1], xpos = ppos[0], ypos = ppos[1], $
              title = title
      device, decompose = 0
      xcharsz = 1.8
      ycharsz = 1.8
      charsz = 1.7
      !p.charsize = 1
   endelse

   gas = dblarr(nf,24,3) ; mean, sd, n

   for k = 0, nf-1 do begin ; nf-1

      cnt = lines[0,0].cnt
      dex = lines[0,0].dex[0:cnt-1]

      if( mol eq 'CH4' ) then begin
         gasyy = lines[k,dex].ch4
         yrange = [3.2, 3.7]
         yx = 3.2
         yti = mol + ' column / 1e19'
         yrange = [90., 110.]
         yx = 107.
         yxs = 0.005
         yti = '% ' + mol + ' column of mean'
         scl = ch4scl
      endif
      if( mol eq 'HDO' ) then begin
         gasyy = lines[k,dex].hdo
         yrange = [3.2, 3.7]
         yx = 3.2
         yti = mol + ' column / 1e22'
         yrange = [0., 200.]
         yx = 175.
         yxs = 0.08
         yti = '% ' + mol + ' column of mean'
         scl = hdoscl
      endif

      dayzero = JULDAY( 1, 1, 2006, 0, 0, 0 ) -1

;print, lines[k,dex].jday, format='(3f20.8)'

      jdays = lines[k,dex].jday

      for i=0, cnt-1 do begin

         ftime = jdays[i] - floor(jdays[i],/L64)
         hour = ftime *24.

         ;print, jdays[i], ftime, hour, format='(3f20.8)'

         for j=0, 24-1 do begin
            if( hour ge j && hour lt j+1 )then begin
               gas[k,j,0] = gas[k,j,0] + gasyy[i]
               gas[k,j,2] = gas[k,j,2] + 1
               continue
            endif
         endfor ; j
      endfor ; i

      for j=0, 24-1 do begin
         if( gas[k,j,2] gt .9 )then gas[k,j,0] = gas[k,j,0] / gas[k,j,2]
         ;print, j, gas[k,j,0]
      endfor

   endfor ; k

   hours = findgen(24) +.5 - 3
   hours[2] = 23.5
   hours[1] = 22.5
   hours[0] = 21.5
   ;print, hours
   plot, hours, gas[0,*,0]/scl, /ynozero, /nodata, charsize=charsz, title=title, $
            xtitle = 'hours', ytitle = yti, yrange = yrange, xrange = [0.,25.]

   for k=0, nf-1 do begin

      kk  = fdex[k]
      lab = label[kk] + mol

      dex = where(gas[k,*,0] ne 0.0, cnt )
      mm  = moment(gas[k,dex,0], /double )
      scl = mm[0]/100.

      cc = k+2
      if( cc ge 7)then cc++
      if( cnt gt 0 ) then begin
         oplot, hours[dex], gas[k,dex,0]/scl, psym=k+1, color = cc
         xyouts, 13., yx-k*yxs*yx, lab, color = cc
      endif

   endfor ; k

   return, 0

end




function plotcnt, lines, nlines, nf, tops, ppos, psiz, hdoscl, fdex, label

   for k = 0, nf-1 do begin

      kk = fdex[k]

      xti = label[kk] + 'HDO Column /10^22'
      yti = label[kk] + '% CH4'

      title = 'pltpercent : ' + yti

      if tops then begin
         erase
         xcharsz = 1.0
         ycharsz = 1.0
         charsz = 1.7
      endif else begin
         ppos = ppos + [ 20, -20, 1 ]
         window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1], xpos = ppos[0], ypos = ppos[1], $
                 title = title
         device, decompose = 0
         xcharsz = 1.8
         ycharsz = 1.8
         charsz = 1.7
         !p.charsize = 1
      endelse


      yrange = [90., 115.]
      yx = 105.
      yxs = 0.01

      cnt = lines[0,0].cnt
      dex = lines[0,0].dex[0:cnt-1]

      xx = lines[k,dex].hdo/hdoscl
      yy = lines[k,dex].ch4
      mm = moment( yy, /double )
      yy = yy / mm[0] * 100.

      plot, xx, yy, psym=3, /ynozero, /nodata, charsize=charsz, title = title, $
            xtitle = xti, ytitle = yti, yrange = yrange, xrange = [0.,5.]

      ;qd = where(yy - min(yy) eq 0.0, qc)
      ;if( qc ne 0 )then print, 'qc min ', k, yy[qd[0]]

      ;qd = where(yy - max(yy) eq 0.0, qc)
      ;if( qc ne 0 )then print, 'qc max ', k, yy[qd[0]]

      ;if( min(yy) lt yrange[0] )then print, k, yrange[0], min(yy)
      ;if( max(yy) gt yrange[1] )then print, k, yrange[1], max(yy)

      oplot, xx, yy, psym=2, color=2

      lf = linfit( xx, yy, yfit=yfit,chisqr=chisqr )
      ;print, ' lf : ', lf
      r2 = (correlate( xx, yy, /double ))^2
      ;print, r2
      oplot, xx, yfit, color=4
      xyouts, 4, yx,          'chisqr = '+string(chisqr,format='(f9.4)')
      xyouts, 4, yx-yxs*yx,   'slope  = '+string(lf[1],format='(f9.5)')
      xyouts, 4, yx-2.*yxs*yx, 'r2     = '+string(r2,format='(f9.5)')
      xyouts, 4, yx-3.*yxs*yx, 'n      = '+string(cnt,format='(i8)')

   endfor ; k

   return, 0
end

function plotann, lines, nlines, nf, ratio, tops, ppos, psiz, hdoscl, ch4scl, mol, fdex, apcnt, label

   title = 'plotann : annual cycle'

   if tops then begin
      erase
      xcharsz = 1.0
      ycharsz = 1.0
      charsz = 1.7
   endif else begin
      ppos = ppos + [ 20, -20, 1 ]
      window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1], xpos = ppos[0], ypos = ppos[1], $
                 title = title
      device, decompose = 0
      xcharsz = 1.8
      ycharsz = 1.8
      charsz = 1.7
      !p.charsize = 1
   endelse

   gas = dblarr(nf,12,2)

   for k = 0, nf-1 do begin

      cnt = lines[0,0].cnt
      dex = lines[0,0].dex[0:cnt-1]

      if( mol eq 'CH4' ) then begin
         gasyy = lines[k,dex].ch4
         yrange = [3.4, 3.8]
         yx = 3.7
         yxs = 0.01
         yti = mol + ' column / 1e19'
         if( apcnt )then begin
            yrange = [96., 104.]
            yx = 103.
            yxs = 0.005
            yti = '% ' + mol + ' column of mean'
         endif
         scl = ch4scl
      endif
      if( mol eq 'HDO' ) then begin
         gasyy = lines[k,dex].hdo
         yrange = [0, 3.]
         yx = 2.
         yxs = 0.08
         yti = mol + ' column / 1e22'
         if( apcnt )then begin
            yrange = [0., 200.]
            yx = 175.
            yxs = 0.08
            yti = '% ' + mol + ' column of mean'
         endif
         scl = hdoscl
      endif

      jdays = lines[k,dex].jday

      m=0l
      yy = 2006
      for m=0l, 11 do begin
         maxn = 31l
         if( m eq 2 )then maxn=28l
         if( m eq 9 )then maxn=30l
         if( m eq 4 )then maxn=30l
         if( m eq 6 )then maxn=30l

         dex2 = where( jdays ge julday( m, 1, yy ) and jdays le julday( m, maxn, yy), cnt )

         if( cnt eq 0 ) then begin
            mm = dblarr(5)
         endif else if ( cnt eq 1 ) then begin
            mm[0] = gasyy[dex2]
            mm[1] = 0.
            ncol  = cnt
         endif else begin
            mm = moment( gasyy[dex2], /double )
            ncol = cnt
         endelse

         gas[k,m,0] = mm[0]
         gas[k,m,1] = sqrt(mm[1])

      endfor ; m

   endfor ; k

   if( apcnt )then yti = '% ' + yti

   mnths = findgen(12) + 0.5
   plot, mnths, gas[0,*,0]/scl, /ynozero, /nodata, charsize=charsz, title=title, $
            xtitle = 'Months', ytitle = yti, yrange = yrange, xrange = [0.,13.]

   for k=0, nf-1 do begin

      kk = fdex[k]
      lab = label[kk] + mol

      dex = where(gas[k,*,0] ne 0.0, cnt )

      mm = moment(gas[k,dex,0], /double )
      if( apcnt )then scl = mm[0]/100.

      cc = k+2
      if( cc ge 7 )then cc++
      if( cnt gt 0 )then begin
         oplot, mnths[dex], gas[k,dex,0]/scl, color = cc
         xyouts, 10.5, yx-k*yxs*yx, lab, color = cc
      endif

   endfor ; k

   return, 0

end


function plotrat, lines, nlines, nf, ratio, tops, ppos, psiz, hdoscl, ch4scl, fdex, label

   for k = 0, nf-1 do begin
      ;print, k

      kk  = fdex[k]

      xti = label[kk] + 'HDO Column /10^22'
      yti = label[kk] + 'CH4'

      case kk of
         0: begin
               aa = 0      ; ch4 numerator & HDO
               bb = 4      ; ch4 denomenator
               if( ratio )then yti = 'HIT00_135 (1a) CH4 / HIT08_12345 (1b) CH4'
            end
         1: begin
               aa = 1
               bb = 4
               if( ratio )then yti = 'HIT08_12345 (1b) CH4 / HIT00_135 (1a) CH4'
            end
         else: begin
               aa = k
               bb = 4
               if( ratio )then yti = yti + ' / HIT00_135 (1a) CH4'
            end

      endcase

      title='plotratio : ' + yti

      if tops then begin
         erase
         xcharsz = 1.0
         ycharsz = 1.0
         charsz = 1.7
      endif else begin
         ppos = ppos + [ 20, -20, 1 ]
         window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1], xpos = ppos[0], ypos = ppos[1], $
                 title = title
         device, decompose = 0
         xcharsz = 1.8
         ycharsz = 1.8
         charsz = 1.7
         !p.charsize = 1
      endelse


     if( ratio ) then begin
        yrange = [0.97, 1.04]
        yx = 1.02
        yxs = 0.01
      endif else begin
        yrange = [3., 4.5]
        yx = 3.7
        yxs = 0.01
      endelse

      cnt = lines[0,0].cnt
      dex = lines[0,0].dex[0:cnt-1]

      xx = lines[aa,dex].hdo/hdoscl

      if( ratio ) then begin
         yy = lines[aa,dex].ch4 / lines[bb,dex].ch4
      endif else begin
         yy = lines[aa,dex].ch4 / ch4scl
      endelse

      ;qd = where(yy - min(yy) eq 0.0, qc)
      ;if( qc ne 0 )then print, 'qc min ', k, yy[qd[0]]

      ;qd = where(yy - max(yy) eq 0.0, qc)
      ;if( qc ne 0 )then print, 'qc max ', k, yy[qd[0]]

      ;if( min(yy) lt yrange[0] )then print, k, yrange[0], min(yy)
      ;if( max(yy) gt yrange[1] )then print, k, yrange[1], max(yy)

      plot, xx, yy, psym=3, /ynozero, /nodata, charsize=charsz, title = title, $
            xtitle = xti, ytitle = yti, yrange = yrange, xrange = [0.,5.]

      oplot, xx, yy, psym=2, color=2

      lf = linfit( xx, yy, yfit=yfit,chisqr=chisqr )
      print, ' lf : ', lf
      r2 = (correlate( xx, yy, /double ))^2
      oplot, xx, yfit, color=4
      xyouts, 4, yx,        'chisqr = '+string(chisqr,format='(f9.4)')
      xyouts, 4, yx-yxs*yx, 'slope  = '+string(lf[1],format='(f8.5)')
      xyouts, 4, yx-2.*yxs*yx, 'r2     = '+string(r2,format='(f8.5)')
      xyouts, 4, yx-3.*yxs*yx, 'n      = '+string(cnt,format='(i8)')

   endfor ; k

   return, 0
end