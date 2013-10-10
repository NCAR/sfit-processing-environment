pro pltmvmr4, file=file, mol=mol, site=site, mxrms=mxrms

; edited to handle next version of gather4 (no reverse stuff there - its here now)
; Last edit 7 October 2013 : Current/CO2 at mlo

if( not keyword_set( file )) then begin
   print, '  main : must set file arg.'
   stop
endif

if( not keyword_set( mol )) then begin
   print, '  main : must set mol arg.'
   stop
endif

if( not keyword_set( site )) then begin
   print, '  main : must set site arg.'
   stop
endif

if( not keyword_set( mxrms )) then begin
   mxrms = 1.0
   print, '  main : setting mxrms limit to : ', mxrms
endif

; get molecule - dependent info for plots
ucmol = STRUPCASE( mol )
usite = STRUPCASE( site )
usemol, usite, ucmol, Ag

psiz = INTARR(2)
psiz = [ 800, 465 ]
ppos = INTARR(3)
ppos = [ 200, 400, 0 ]        ; laptop

print, ' Restoring save file : ', file
restore, file
;help, ds, /structure


print, 'Number of retrievals in save file : ',  n_elements(ds)
idx = where( ds.rms LT mxrms, nobs )
data = ds[idx]
print, 'Number of retrievals in max rms criteria : ',  nobs

years = fltarr(2)
years[0] = min( data[*].year )
years[1] = max( data[*].year ) +1

nobs = n_elements(data)
alt  = reform(data[0].altitude)
altr = reverse(alt)
alb  = reform(data[0].alt_boundaries[0,*])
albr = reverse(alb)
nalt = n_elements(alt)
print, 'Number of obs    : ', nobs
print, 'Number of layers : ', nalt

altfmt = string(nalt,format='( "(", i2, "f14.3)")' )
vmrfmt = string(nalt,format='( "(", i2, "e14.6)")' )

top = 7
bot = 0

; calc mean weighted mix ratio near surface

idx = where( alt LE top AND alt GE bot, cnt )
print, ' Altitude ranges included in mean mixing ratio sum '
print, cnt, nobs, alt[idx]
xd = dblarr(nobs)
xh = dblarr(nobs)
dt = dblarr(nobs)
xm = dblarr(nobs,2)
nn = 0


for i=0, nobs-1 do begin

   dt[i] = data[i].tyr

   xm[i,0] = total( data[i].ms[idx] ) ; sum airmass

   xh[i] = total( data[i].retvmr[idx] * data[i].ms[idx]  ) / xm[i,0] * Ag.vmrscl


   xm[i,1] = total( (1. - data[i].h2o_vmr[idx] ) * data[i].ms[idx] ) ; sum airmass

   xd[i] = total( data[i].retvmr[idx] * data[i].ms[idx]  ) / xm[i,1] * Ag.vmrscl

   print, i+1, ds[i].tyr, '  ', ds[i].yyyymmdd, '  ', ds[i].hhmmss, xh[i], xd[i]

endfor

print,''
print, ' Mean difference humid-dry : '
yrm = moment( xh-xd )
print, yrm[0],  ' +- 1 sigma : ', sqrt(yrm[1])
print,''

; calc daily mean of humid and dry
dm = dblarr(366,5)
for i=0, 366 do begin
   idx = where( fix(data[*].doy) EQ i AND data[*].rms LT 3.0, dcnt )
   if( dcnt GT 1 )then begin
       a = moment( xh[idx] )
       dm[i,0] = a[0]
       dm[i,1] = sqrt( a[1] )
       a = moment( xd[idx] )
       dm[i,2] = a[0]
       dm[i,3] = sqrt( a[1] )
       dm[i,4] = fix(data[idx[0]].doy)
    endif
endfor

idx = where( dm[*,4] NE 0, dcnt )
print, ' # daily mean values : ', dcnt
m = moment( dm[idx,0] )
print, ' humid daily mean : ', m[0], sqrt(m[1])
m = moment( dm[idx,1] )
print, ' humid daily sdev : ', m[0], sqrt(m[1])
m = moment( dm[idx,2] )
print, '   dry daily mean : ', m[0], sqrt(m[1])
m = moment( dm[idx,3] )
print, '   dry daily sdev : ', m[0], sqrt(m[1])
print,''

des = 0

for tops = 0, 1 do begin

     if tops then begin ; 1 is true
         set_plot, 'ps'
         locdir = file_basename(file_expand_path('.'))
         pos = strpos( file, '.' )
         psfile =  strmid( file, 0, pos ) + '.ps'
         print,''
         print, '   main : saving ps file to : ', psfile
         device, /color, /landscape, filename = psfile, encapsulated = 0, bits=8
         !p.charsize  = 1.4
         !p.charthick = 4.0
         !p.thick     = 1
         !x.thick     = 4.
         !y.thick     = 4.
         !p.multi      = 0
         stickthick   = 2
         charsize     = 2.
         lthick       = 6
         fillcolor    = 170

      endif else begin
         set_plot,'x'
         device, decompose=0  ; allow for terminals with > 256 color
         tek_color
         !p.charsize  = 1.4
         !p.charthick = 1
         !p.thick     = 1
         !x.thick     = 1
         !y.thick     = 1
         !p.multi      = 0
         stickthick   = 1
         charsize     = 1.5
         lthick       = 2
         fillcolor    = 0

      endelse

   plotsym2, 0, 1, /fill

   title='plt8 COL vz DOY'
   rc = plt8( data, years, title, ppos, psiz, tops )

   title='plt9 mass ratio vs doy'
   rc = plt9( xd, data, xm, years, Ag.trng, title, ppos, psiz, tops )

   title='plt7 mass ratio vs sza'
   rc = plt7( xd, data, xm, Ag.trng, title, ppos, psiz, tops )

   title='plt6 mass correlation'
   rc = plt6( xd, xm, Ag.trng, title, ppos, psiz, tops )

   title='plt1 humid and dry vs DOY - all data'
   rc = plt1( dt, xd, xh, years, Ag.trng, title, ppos, psiz, tops )

   title='plt2 humid vs dry correlation'
   rc = plt2( dt, xh, xd, Ag.trng, title, ppos, psiz, tops )

   title='plt4 mean difference humid-dry vmr'
   rc = plt4( dt, xh, xd, years, Ag.trng, title, ppos, psiz, tops )

   title='plt5 SZA vz DOY'
   rc = plt5( data, xd, years, Ag.trng, title, ppos, psiz, tops )

   rc = plothist( tops, ppos, psiz, data )


   goto, skipdays

   title='plt3 dry and humid daily mean vs DOY'
   ppos = ppos +  [ 20,  -20, 1 ]
   for i=0, 366 do begin
      idx = where( fix(data[*].doy) EQ i, dcnt )
      if( dcnt GT 1 )then begin
         rc = plt3(  data, xd, xh, idx, title, ppos, psiz, tops )
         if( des NE 2 )then begin
            read, des, prompt=' 0=quit, 1=next, 2=finish : '
            if( des EQ 0 )then return
         endif
      endif
   endfor

   skipdays:

   if( tops )then device, /close
endfor

return
end

function plt9, xd, ds, xm, years, trng, title, ppos, psiz, tops

   xtl = 'DOY'
   ytl = 'mass ratio'
   if( tops )then begin
      erase
   endif else begin
      ppos = ppos +  [ 20,  -20, 1 ]
      window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1], title=title, xpos = ppos[0], ypos = ppos[1]
   endelse

   idx = where( xd[*] GT trng[0] AND xd[*] LT trng[1], mmcnt )

   plot,  ds[idx].tyr, xm[idx,0]/xm[idx,1], xrange=years, yrange=[0,0], /ynozero, /nodata, title=title, xtitle=xtl, ytitle=ytl
   oplot, ds[idx].tyr, xm[idx,0]/xm[idx,1], psym=8, color=4
   ;print, xm[idx,0]/xm[idx,1]
   ;read,des, prompt='qq'

return, 0
end


function plt8, ds, years, title, ppos, psiz, tops

   xtl = 'DOY'
   ytl = 'Total Column'
   if( tops )then begin
      erase
   endif else begin
      ppos = ppos +  [ 20,  -20, 1 ]
      window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1], title=title, xpos = ppos[0], ypos = ppos[1]
   endelse

   idx = where( ds[*].rms < 10.7, mmcnt )
   plot,  ds[idx].tyr, ds[idx].prmgas_tc, psym=8, xrange=years,  /nodata, /ynozero,title=title, xtitle=xtl, ytitle=ytl
   oplot, ds[idx].tyr, ds[idx].prmgas_tc, psym=8, color = 4

return, 0
end


function plt7, xd, ds, xm, trng, title, ppos, psiz, tops

   xtl = 'SZA'
   ytl = 'mass ratio'
   if( tops )then begin
      erase
   endif else begin
      ppos = ppos +  [ 20,  -20, 1 ]
      window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1], title=title, xpos = ppos[0], ypos = ppos[1]
   endelse

   idx = where( xd[*] GT trng[0] AND xd[*] LT trng[1], mmcnt )
   plot,  ds[idx].sza, xm[idx,0]/xm[idx,1], xrange=[0,0], yrange=[0,0], /ynozero, /nodata,  title=title, xtitle=xtl, ytitle=ytl
   oplot, ds[idx].sza, xm[idx,0]/xm[idx,1], psym=8, color=4
   ;print, xm[idx,0]/xm[idx,1]
   ;read,des, prompt='qq'

return, 0
end


function plt6, xd, xm, trng, title, ppos, psiz, tops

   xtl = 'humid airmass'
   ytl = 'dry airmass'
   if( tops )then begin
      erase
   endif else begin
      ppos = ppos +  [ 20,  -20, 1 ]
      window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1], title=title, xpos = ppos[0], ypos = ppos[1]
   endelse

   xy = [5.35e24,5.55e24]
   idx = where( xd[*] GT trng[0] AND xd[*] LT trng[1], mmcnt )
   plot, xm[idx,0], xm[idx,1], xrange=xy, yrange=xy,/nodata,  title=title, xtitle=xtl, ytitle=ytl
   plots, xm[idx,0], xm[idx,1], psym=8, color=2
   oplot, xy, xy, color = 4
   ;read,des, prompt='qq'

return, 0
end


function plt5, ds, xd, years, trng, title, ppos, psiz, tops

   xtl = 'DOY'
   ytl = 'sza'
   if( tops )then begin
      erase
   endif else begin
      ppos = ppos +  [ 20,  -20, 1 ]
      window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1], title=title, xpos = ppos[0], ypos = ppos[1]
   endelse

   idx = where( xd[*] GT trng[0] AND xd[*] LT trng[1], mmcnt )
   plot,  ds[idx].tyr, ds[idx].sza, psym=8, xrange=years, /ynozero, /nodata, title=title, xtitle=xtl, ytitle=ytl
   oplot, ds[idx].tyr, ds[idx].sza, psym=8, color=4

return, 0
end


function plt4, dt, xh, xd, years, trng, title, ppos, psiz, tops

   xtl = 'DOY'
   ytl = 'humid-dry mean vmr'
   if( tops )then begin
      erase
   endif else begin
      ppos = ppos +  [ 20,  -20, 1 ]
      title='mean difference humid-dry vmr'
      window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1], title=title, xpos = ppos[0], ypos = ppos[1]
   endelse

   idx = where( xd[*] GT trng[0] AND xd[*] LT trng[1], mmcnt )
   plot, dt[idx], xh[idx]-xd[idx], psym=8, xrange=years, /ynozero, /nodata, xtitle=xtl, ytitle=ytl, title=title
   oplot, dt[idx], xh[idx]-xd[idx], psym=8

return, 0
end


function plt3, ds, xd, xh, idx, title, ppos, psiz, tops

   xtl = 'DOY'
   ytl = 'humid & dry mean vmr'
   if tops then begin
      erase
   endif else begin
      window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1], title=title, xpos = ppos[0], ypos = ppos[1]
   endelse

   x1  = fix( ds[idx[0]].doy )
   y   = xh[idx]
   z   = xd[idx]
   ymx = max( [y, z] )
   ymn = min( [y, z] )

   n = n_elements(idx)
   print, ' doy, #, dif : ', fix(ds[idx[0]].doy), n, y-z

   if( n GT 1 )then begin
      ym = moment( y )
      print, '    mean hmd ', ym[0], sqrt(ym[1])
      zm = moment( z )
      print, '    mean dry ', zm[0], sqrt(zm[1])
   endif

   xr = [x1,x1+1]
   xr = [0,0]
   yr = [ ymn, ymx ]

   xtl = xtl + string( fix(ds[idx[0]].doy) )
   plot,  ds[idx].doy, y, xrange = xr, yrange = yr, /ynozero, /nodata,  xtitle=xtl, ytitle=ytl, xstyle=0, ystyle=0, title=title
   oplot, ds[idx].doy, y, psym=7, color = 4
   oplot, ds[idx].doy, z, psym=5, color = 3

return, 0
end


function plt2, dt, xh, xd, trng, title, ppos, psiz, tops

   xtl = 'humid mean vmr'
   ytl = 'dry mean vmr'
   if( tops )then begin
      erase
   endif else begin
      ppos = ppos +  [ 20,  -20, 1 ]
      window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1], title=title, xpos = ppos[0], ypos = ppos[1]
   endelse

   idx = where( xd[*] GT trng[0] AND xd[*] LT trng[1], mmcnt )
   plot, xh[idx], xd[idx], psym=4, /ynozero, /nodata,   xtitle=xtl, ytitle=ytl, title=TITLE, xrange = trng, yrange = trng
   oplot, trng, trng, color=4
   des = 1
   for i=0, mmcnt-1 do begin
      plots, xh[i], xd[i], psym=8, color=2
      if( des EQ 1 AND tops EQ 0 )then begin
         print, dt[i], xh[i]-xd[i]
         read, des, prompt=' 0,1,2 : '
         if( des eq 0 )then return, 0
      endif
   endfor

return, 0
end

function plt1, dt, xd, xh, years, trng, title, ppos, psiz, tops

   xtl = 'day of year'
   ytl = 'mean vmr, humid & dry air'
   if tops then begin
      erase
   endif else begin
      ppos = ppos +  [ 20,  -20, 1 ]
      window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1], title=title, xpos = ppos[0], ypos = ppos[1]
   endelse

   idx = where( xd[*] gt trng[0] and xd[*] lt trng[1], mmcnt )
   plot,  dt[idx], xd[idx], psym=7, xrange=years, /nodata, /ynozero, xtitle=xtl, ytitle=ytl, title=title
   oplot, dt[idx], xd[idx], psym=8, color=2
   oplot, dt[idx], xh[idx], psym=7, color=4

   xyouts, 0.2, 0.04, 'all airmass', color=4, /normal
   xyouts, 0.2, 0.09, 'dry airmass', color=2, /normal

return, 0
end

; plot parameters in histograms in 4 panels -------------------------------------------------------

function plothist, tops, ppos, psiz, ds

   !p.multi = [0, 2, 2, 0, 0]

   if tops then begin
      erase
      csz = 1.0

   endif else begin
      ppos = ppos +  [ 20,  -20, 1 ]
      window, ppos[2], retain=2, xsize=psiz[0], ysize=psiz[1],          $
              title='ncar fts retrieval histogram distributions',    $
              xpos = ppos[0], ypos = ppos[1]
      csz = 1.0

   endelse

   nobs = n_elements( ds )

   for i=0, 3 do begin

      switch i of

      0: begin
         data = ds[0:nobs-1].sza
         title = 'sza'
         xtitle = 'solar zenith angle [deg]'
         break
         end

      1: begin
         data = ds[0:nobs-1].rms
         title = 'fit rms'
         xtitle = 'fit rms [%]'
         break
         end

      2: begin
         data = ds[0:nobs-1].dofs
         title = 'dofs'
         xtitle = 'degrees of freedom for signal'
         break
         end

      3: begin
         data = ds[0:nobs-1].azi
         title = 'sazm'
         xtitle = 'solar azimuth angle [deg]'
         break
         end

      endswitch

      if( max( data ) gt 0.0 )then begin
			hist = histogram(data, nbins=60, locations=locs)
			bins = findgen(n_elements(hist)) + min(data)
			;print, min(hist)
			;print, bins
			;print, locs
			plot, locs, hist, yrange = [0.0, max(hist)+1], /nodata, $
				  psym = 10, xtitle = xtitle, ytitle = 'density per bin', $
				  title=title
			oplot, locs, hist, psym = 10, color=4
      endif

   endfor

   ;for i=0, nlat-1 do begin
   ;print, lines[i].sza, lines[i].rms, lines[i].dofs, lines[i].sazm
   ;endfor


return, 0

end

