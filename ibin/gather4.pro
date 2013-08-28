pro gather, site=site, mol=mol, co2isotope=co2isotope, plt=plt, lstFile=lstFile, specDBfile=specDBfile, ctlfile=ctlfile

close,/all
;******************************************************************************************************************
;
; Purpose: This program is designed to collect information from multiple sfit4 fits for storing in IDL save file and
;          eventualy HDF file for submission. The *.lst file dictates which sfit4 fits to process
;
;
;
; Keywords:
;   site       --  Three letter identifier of site
;   mol        --  Molecular species of interest
;   plt        --  Command to do intermediate plots
;   lstFile    --  Path and name of list file to read
;   specDBfile --  Path and name of spectral database file to read
;
;
; Notes:
;  From list file we get the following parameters:
;     1) Directory of output
;     2) Date
;     3) Time
;     
;  From spectral database file we get the following parameters:
;     1) Date
;     2) Time
;     3) Opus filename
;     4) SNR -- singal to noise ratio
;     5) Latitude [North]
;     6) Longitude [West]
;     7) Altitude [m]
;     8) Solar azmith angle
;     9) Solar zenith angle
;     10) Scan duration
;     
;  From the statvec fiel we get the following parameters
;     
;
;
;
;******************************************************************************************************************

;-------------------------------------------------
; Initialize subroutines/functions used in program
;-------------------------------------------------
forward_function gomkstrct

funcs = [ 'usesite4', 'usemol', 'lfileread', 'mkjday', 'readstat', 'readnxn', 'readlayr' ]
resolve_routine, funcs, /either

;---------------------------------
; Check user input in program call
;---------------------------------
if( ~keyword_set( site ) || ~keyword_set( mol ) || ~keyword_set(lstFile) || ~keyword_set(specDBfile) ) then begin
   print, ' example usage : gatherd, site="tab", mol="co2", lstFile="/home/usr/mlo_1_1_13.lst", specDBfile="/home/usr/specDB_mlo_2013.dat"'
   stop
endif

; based on the site, set a few more variables
lcmol = STRLOWCASE(mol)
ucmol = STRUPCASE(mol)
ucsite= STRUPCASE(site)

;-----------------------------------------------------------
; Gather information on the station location and primary gas
;-----------------------------------------------------------
usemol, ucsite, ucmol, Ag     ; Returns Ag
usesite, ucsite, As, Ag       ; Returns As

;-------------------------
; Open and read *.lst file
;-------------------------
; Determine number of lines in file
nlines = file_lines(lstFile)
  
; Open file
openr, fid_lstFile, lstFile, /get_lun, error=ioerr
if( ioerr ne 0 ) then begin
  printf, -2, !err_string
  stop
endif
  
; Initialize values
buf     = ''
i       = 0
  
; Read header and count lines
while( not strcmp(buf, 'Date', 9 ) ) do begin
  readf, fid_lstFile, buf
  i ++
endwhile
  
; Determine remaining lines
nsize = nlines-i
lDates   =  strarr(nsize)                  ; Create array for reading in Dates
lTstamps =  strarr(nsize)                  ; Create array for reading in timestamps
lDirs    =  strarr(nsize)                  ; Create array for reading in directories
  
; Read relavent data
for j = 0, nsize-1 do begin
  readf, fid_lstFile, buf
  subs = strsplit( buf,' ',/extract, count=nitms)
  lDates[j]   = subs[0]
  lTstamps[j] = subs[1]
  lDirs[j]    = subs[2]
endfor

; Close file
free_lun, fid_lstFile

;------------------------------------------
; Search for duplicate entries in list file
; and remove 
;------------------------------------------
newDate    = lDates*1000000 + lTstamps
unq_ind    = uniq(newDate,sort(newDate))

if nsize ne size(unq_ind,/n_elements) do begin    ; Found duplicate entries
  lDates   = lDates[unq_ind]
  lTstamps = lTstamps[unq_ind]
  lDirs    = lDirs[unq_ind]  
  nsize    = size(lDates,/n_elements)
endif

;-------------------------------------
; Open and read spectral database file
;-------------------------------------
; Determine number of lines in file
nlines = file_lines(specDBfile)
; Headers for data to extract from spectral DB file
getHdrs = ['Filename','TStamp','Date','SNR','N_Lat','W_Lon','Alt','SAzm','SZen','Dur']
;Hdr ind      0         1        2      3     4       5       6     7      8      9
nhdrs    = intarr(size(getHdrs,/n_elements))
Filename = strarr(nsize)
Tstamp   = strarr(nsize)
Date     = strarr(nsize)
snr      = fltarr(nsize)
n_lat    = fltarr(nsize)
w_lon    = fltarr(nsize)
alt      = fltarr(nsize)
SAzm     = fltarr(nsize)
SZen     = fltarr(nsize)
Dur      = fltarr(nsize)
Dir      = strarr(nsize)

; Open file
openr, fid_specDBfile, specDBfile, /get_lun, error=ioerr
if( ioerr ne 0 ) then begin
  printf, -2, !err_string
  stop
  
endif

buf = ''
; First line of spectral DB is the header
readf, fid_specDBfile, buf
header = strsplit(buf,' ', /extract, count=nheaders)

; Find the indices for each header to extract
for i = 0, (size(getHdrs,/n_elements)-1) do begin
  nhdrs[i] = where(header eq getHdrs[i])
  
endfor

buf = ''
; Read data in spectral database
for i = 0, (nlines-2) do begin
  readf, fid_specDBfile, buf
  subs = strsplit( buf, ' ', /extract, count=nitms )
  
  tempDate   = subs[nhdrs[2]]
  tempTstamp = subs[nhdrs[1]]
  
  ; If date and timestamp from DB match an entry in list file grab data
  testMatch = strmatch(lDates, tempDate) + strmatch(lTstamps, tempTstamp)
  indMatch  = where(testMatch eq 2)
  
  if size(indMatch,/n_elements) gt 1) then begin
    print, 'Duplicate Entries in list file found'
    exit
    
  endif
  
  if indMatch gt 0 then begin
    Filename[i] = subs[nhdrs[0]]
    Tstamp[i]   = subs[nhdrs[1]] 
    Date[i]     = subs[nhdrs[2]] 
    snr[i]      = subs[nhdrs[3]] + 0.0
    n_lat[i]    = subs[nhdrs[4]] + 0.0
    w_lon[i]    = subs[nhdrs[5]] + 0.0
    alt[i]      = subs[nhdrs[6]] + 0.0
    SAzm[i]     = subs[nhdrs[7]] + 0.0
    SZen[i]     = subs[nhdrs[8]] + 0.0
    Dur[i]      = subs[nhdrs[9]] + 0.0
    Dir[i]      = lDirs[indMatch]
    
  endif

endfor

;------------------------------------------------
; Manipulate Date and Tstamps to get YYYY, MM, DD
; DOY, etc and convert Date and Tstamp to int
;------------------------------------------------
YYYY     = intarr(nsize)
MM       = intarr(nsize)
DD       = intarr(nsize)
HH       = intarr(nsize)
MM       = intarr(nsize)
SS       = intarr(nsize)
DOY      = intarr(nsize)
timefrac = fltarr(nsize)
jd2000   = julday(1,1,2000, 00, 00, 00)

for i = 0, nsize-1 do begin
  YYYY[i]     = strmid(Date[i],0,4)   + 0
  MM[i]       = strmid(Date[i],4,2)   + 0
  DD[i]       = strmid(Date[i],6,2)   + 0
  HH[i]       = strmid(Tstamp[i],0,2) + 0
  MM[i]       = strmid(Tstamp[i],2,2) + 0
  SS[i]       = strmid(Tstamp[i],4,2) + 0
  
  ; Date conversions
  DOY[i]      = JULDAY( MM[i], DD[i], YYYY[i], HH[i], MM[i], SS[i] )  - JULDAY( 1, 1, YYYY[i], 0, 0, 0 ) +1
  timefrac[i] = double(HH[i]) + (double(MM[i]) + double(SS[i]) /60.0d) /60.0d
  daysinyear  = JULDAY( 12, 31, YYYY[i], 0, 0, 0 )  - JULDAY( 1, 1, YYYY[i], 0, 0, 0 ) +1
  daytfrac[i] = YYYY[i] + (DOY[i] + timefrac[i]/24.D)/daysinyear
  mjd2k[i]    = JULDAY( MM[i], DD[i], YYYY[i], HH[i], MM[i], SS[i] ) - jd2000
endfor

;-------------------------------------------
; Get layering info from station.layers file
;-------------------------------------------
print, ' Opening file : ', As.infodir + '/local/station.layers'
klay = readlayr( grd, As.infodir + '/local/station.layers' )
nlayers = klay-1

                ;--------------------------------------------------;
                ; Loop through observations to collect output data ;
                ;--------------------------------------------------;
for i = 0, nsize-1 do begin
  
  ;----------------------------------------
  ; Read control file from output directory
  ;----------------------------------------  
  ctlFname = Dir[i] + 'sfit4.ctl'
  readsctl4, ctlData, ctlFname
  
  ;----------------------------------------
  ; Read statvec file from output directory
  ; From statvec we get:
  ;    -- pressure, temperature, apriori vmr
  ;       retrieved vmr, 
  ;----------------------------------------  
  statvecFname = Dir[i] + 'statevec'
  readstat4, statvecData, statvecFname
  
  
  
  
  
  
  
  
endfor




;structure initialization
gomkstrct, nlat, nlayers, datastructure, co2isotope=co2isotope

;loop over retrievals & store pertinent data from file into data structure
for i=0, nlat-1 do begin

   datastructure(i).directory      = lines[i].directory
   datastructure(i).spectraname    = lines[i].opusfile
   datastructure(i).year           = lines[i].yyyy
   datastructure(i).month          = lines[i].mm
   datastructure(i).day            = lines[i].dd
   datastructure(i).hrs            = lines[i].tstamp
   datastructure(i).doy            = lines[i].doy
   datastructure(i).tyr            = lines[i].dstamp
   datastructure(i).int_time       = lines[i].dur
   datastructure(i).sza            = lines[i].sza
   datastructure(i).azi            = lines[i].sazm
   datastructure(i).iterations     = lines[i].itr             ;*
   datastructure(i).zcorrect       = lines[i].zerof           ;*
   datastructure(i).rms            = lines[i].rms             ;*
   datastructure(i).dofs           = lines[i].dofs            ;*
   datastructure(i).snr            = lines[i].snr           
   datastructure(i).rettc          = lines[i].col             ;*
   datastructure(i).alt_index      = indgen(nlayers, /long)+1
   datastructure(i).latitude       = As.lat                   
   datastructure(i).longitude      = As.lon
   datastructure(i).alt_instrument = As.alt
   datastructure(i).datetime       = lines[i].mjd2k

   if( keyword_set( co2isotope ))then getiso, datastructure[i], nlayers

   ;collect z, p, t, apriori and retrieved of mol of interest from statevector file

   statevecfile = datastructure[i].directory + '/statevec'
   rc = readstat( sts, statevecfile, statevector )

   datastructure(i).altitude  = grd.midp[0:nlayers-1]
   datastructure(i).p         = sts.p[0:nlayers-1]
   datastructure(i).t         = sts.t[0:nlayers-1]
   datastructure(i).aprtc     = sts.col[0,0]
   datastructure(i).aprvmr    = sts.vmr[0,0,0:nlayers-1]
   datastructure(i).retvmr    = sts.vmr[1,0,0:nlayers-1]

   print, datastructure(i).directory, datastructure(i).datetime, datastructure[i].tyr, datastructure(i).hrs, sts.col[1,0]

   blah=where((sts.pnam[0:sts.nprm-1] eq 'BckGrdSlp'), nb)
   if( nb ge 1 )then datastructure(i).bslope = mean(sts.prm[1,0:blah])

   blah=where(((sts.pnam[0:sts.nprm-1] eq 'SWNumShft' ) or ( sts.pnam[0:sts.nprm-1] eq 'IWNumShft')), nb)
   if( nb ge 1 )then datastructure(i).wshift = mean(sts.prm[1,0:blah])

   blah=where((sts.pnam[0:sts.nprm-1] eq 'ZeroLev'), nb)
   if( nb ge 1 )then datastructure(i).zerolev = mean(sts.prm[1,0:blah])

   blah=where((sts.pnam[0:sts.nprm-1] eq 'SPhsErr'), nb)
   if( nb ge 1 )then datastructure(i).phase = mean(sts.prm[1,0:blah])

   datastructure(i).alt_boundaries[0,*] = grd.alts[1:nlayers]
   datastructure(i).alt_boundaries[1,*] = grd.alts[0:nlayers-1]

   ;get the surface pressure and temperature

   datastructure(i).surface_pressure    = -9.0000E+004
   datastructure(i).surface_temperature = -9.0000E+004

   point_lun, surflun, 0
   while( ~ EOF(surflun) )do begin
      junk = ''
      readf, surflun, junk
      temp = strsplit(junk,/extract)
      if( temp(0) eq lines[i].date )then begin
         datastructure(i).surface_pressure    = double(temp(1))
         datastructure(i).surface_temperature = double(temp(2))+273.15
      endif
   endwhile

   if( datastructure(i).surface_pressure eq '-999.9' )then datastructure(i).surface_pressure    = -9.0000E+004
   if( datastructure(i).surface_temperature lt 0.0 )then   datastructure(i).surface_temperature = -9.0000E+004

   ;collect the AK
   avk      = fltarr(nlayers,nlayers)
   avk_norm = fltarr(nlayers,nlayers)
   AKfile   = datastructure[i].directory + '/AK.out'
   rc       = readnxn( avk, AKfile )
   if( avk.n NE nlayers )then stop,'nlayers and ak.n not equal'

   ;normalize the ak so relative to a priori
   for ii=0,nlayers-1  do begin
      for jj=0, nlayers-1 do begin
         avk_norm(ii,jj)=avk.mat(ii,jj)*(datastructure(i).aprvmr(ii)/datastructure(i).aprvmr(jj))
      endfor
   endfor

   ; get the airmass for the total column averaging kernel,
   msfile  = datastructure[i].directory + '/fasc.ms'
   temparr = fltarr(nlayers)
   msarr   = fltarr(nlayers)
   openr,1,msfile
   readf,1,junk
   readf,1,temparr
   readf,1,junk
   readf,1,temparr
   readf,1,junk
   readf,1,msarr
   close,1

   ; Calculate the total column averaging kernel
   sum  = fltarr(nlayers)
   atc  = fltarr(nlayers)
   atc2 = fltarr(nlayers)
   atc3 = fltarr(nlayers)
   for jj=0, nlayers-1 do begin
      for ii=0, nlayers-1 do begin
         sum(ii)= msarr(ii)*avk_norm(ii,jj)
      endfor
      atc(jj)  = (total(sum))/msarr(jj)
      atc3(jj) = total(avk_norm(*,jj)) ;this one is just a sum of each layer. No airmass weighting = sensitivity.
   endfor

   if( keyword_set( plt ))then begin
      tek_color
      set_plot,'x'
      device,decompose=0
      window,2
      !p.multi=[0,2,2]
      plot, avk_norm(0,*), datastructure(i).altitude, xrange=[-2,2]
      for ii=0, nlayers-1 do oplot, avk_norm(ii,*), datastructure(i).altitude, color=ii+2
      oplot, atc3, datastructure(i).altitude
      plot, datastructure(i).aprvmr, datastructure(i).altitude
      oplot, datastructure(i).retvmr, datastructure(i).altitude, color=2
      plot, atc, datastructure(i).altitude
      ;device,/close
   endif

   datastructure(i).ak   = avk_norm ;reverse(reverse(avk_norm,1),2)
   datastructure(i).aktc = atc ;reverse(atc)
   datastructure(i).sens = atc3 ;reverse(atc3)

   ;a priori water vapour
   h2oprof=fltarr(nlayers)

   fascmixfile = datastructure[i].directory + '/fasc.mix'
   openr,1, fascmixfile
   readf,1, junk
   readf,1, h2oprof
   close,1

   ;calculate the column
   h2ocol=total(h2oprof*msarr)

   ;calculate the retrieved columns here too
   retlaycol = fltarr(nlayers)
   retlaycol = datastructure(i).retvmr*msarr ;reverse(msarr)
   aprlaycol = fltarr(nlayers)
   aprlaycol = datastructure(i).aprvmr*msarr ;reverse(msarr)

   ;and put in the structure
   datastructure(i).aprh2ovmr = h2oprof ;reverse(h2oprof)
   datastructure(i).aprh2otc  = h2ocol
   datastructure(i).ms        = msarr ;reverse(msarr)
   datastructure(i).retlaycol = retlaycol
   datastructure(i).aprlaycol = aprlaycol

   ;a sanity check
   ;print, 'retlaycol=', retlaycol
   ;print, 'total from retlaycol=',  total(retlaycol)
   ;print, 'total column from l=', datastructure(i).rettc

   external_solar_sensor = 0.0
   detector_intern_temp_switch = 0.0
   guider_quad_sensor_sum = 0.0
   outside_relative_humidity = 0.0


   datastructure[i].external_solar_sensor = external_solar_sensor
   datastructure[i].detector_intern_temp_switch = detector_intern_temp_switch
   datastructure[i].guider_quad_sensor_sum = guider_quad_sensor_sum
   datastructure[i].outside_relative_humidity = outside_relative_humidity

endfor ; next entry



;****************************************************************************************************


print, 'ready to save'


;*******************************
;Save the output by year and for all

if extension eq '' then output_filename=mol+'new_all.sav'
if extension ne '' then output_filename=mol+extension+'new_all.sav'

;reorder first by datetime so that we ensure chronological order
sorting = sort(datastructure.datetime)
data    = datastructure(sorting)

;data=datastructure
save, data, filename=output_filename
print,'Data structure for all retrievals saved as ', output_filename

;for i=1995, 2050 do begin
; il=where(datastructure.year eq i, nil)
; if nil ne 0 then begin
;  if extension eq '' then output_filename=mol+'_'+strtrim(string(i),2)+'.sav'
;  if extension ne '' then output_filename=mol+extension+'_'+strtrim(string(i),2)+'.sav'
;  data=datastructure(il)
;  save, data, filename=output_filename
;  print,'Data structure for ', strtrim(string(i),2), ' saved as ', output_filename
; endif
;endfor


end


; make the data structure
pro gomkstrct, nlat, nlayers, datastructure, co2isotope=co2isotope

if( keyword_set( co2isotope ))then begin

   datastructure = REPLICATE({h224, $
   spectraname :'',$ ;x
   directory:'',$ ;x
   snr:0.0,$ ;x
   p:fltarr(nlayers),$ ;x
   t:fltarr(nlayers),$ ;x
   ms:fltarr(nlayers),$
   rms:0.0,$ ;x
   dofs:0.0,$ ;x
   sza:0.D,$ ;x
   azi:0.D,$ ;x
   iterations:0,$
   zcorrect:0.D,$
   wshift:0.D,$
   zerolev:0.D,$
   bslope:0.D,$
   phase:0.D,$
   aprvmr:fltarr(nlayers),$ ;x
   aprlaycol:fltarr(nlayers),$
   retvmr:fltarr(nlayers),$ ;x
   retlaycol:fltarr(nlayers),$

   retvmr13:fltarr(nlayers),$ ;x
   retlaycol13:fltarr(nlayers),$

   retvmr18:fltarr(nlayers),$ ;x
   retlaycol18:fltarr(nlayers),$

   aprtc:0.D,$ ;x
   rettc:0.D,$ ;x
   aprh2ovmr:fltarr(nlayers),$;x
   aprh2otc:0.D,$;x
   year:0,$ ;x
   month:0,$ ;x
   day:0,$ ;x
   hrs:0.D,$ ;x
   doy:0.D,$ ;x
   tyr:0.D,$ ;x
   datetime:0.D,$ ;x
   latitude:0.0,$ ;x
   longitude:0.0,$ ;x
   alt_instrument:0.0,$; x
   surface_pressure:0.D,$; x
   surface_temperature:0.D,$; x
   alt_index:lonarr(nlayers),$ ;x
   alt_boundaries:fltarr(2,nlayers),$ ;x
   altitude:fltarr(nlayers),$ ;x
   ak:fltarr(nlayers,nlayers),$ ;x ;check directions and normalize....
   aktc:fltarr(nlayers),$ ; x plot and check we have the direction right!
   sens:fltarr(nlayers),$
   external_solar_sensor:0.D,$
   detector_intern_temp_switch:0.D,$
   guider_quad_sensor_sum:0.D,$
   outside_relative_humidity:0.D,$
   int_time:0.D},nlat)

endif else begin

   datastructure = REPLICATE({h224, $
   spectraname                : '',$
   directory                  : '',$
   snr                        : 0.0,$
   p                          : fltarr(nlayers),$
   t                          : fltarr(nlayers),$
   ms                         : fltarr(nlayers),$
   rms                        : 0.0,$
   dofs                       : 0.0,$
   sza                        : 0.D,$
   azi:0.D,$ ;x
   iterations:0,$
   zcorrect:0.D,$
   wshift:0.D,$
   zerolev:0.D,$
   bslope:0.D,$
   phase:0.D,$
   aprvmr:fltarr(nlayers),$ ;x
   aprlaycol:fltarr(nlayers),$
   retvmr:fltarr(nlayers),$ ;x
   retlaycol:fltarr(nlayers),$
   aprtc:0.D,$ ;x
   rettc:0.D,$ ;x
   aprh2ovmr:fltarr(nlayers),$;x
   aprh2otc:0.D,$;x
   year                       :0,$ ;x
   month                      :0,$ ;x
   day                        :0,$ ;x
   hrs                        :0.D,$ ;x
   doy                        :0.D,$ ;x
   tyr                        :0.D,$ ;x
   datetime                   :0.D,$ ;x
   latitude:0.0,$ ;x
   longitude:0.0,$ ;x
   alt_instrument:0.0,$; x
   surface_pressure:0.D,$; x
   surface_temperature:0.D,$; x
   alt_index:lonarr(nlayers),$ ;x
   alt_boundaries:fltarr(2,nlayers),$ ;x
   altitude:fltarr(nlayers),$ ;x
   ak:fltarr(nlayers,nlayers),$ ;x ;check directions and normalize....
   aktc:fltarr(nlayers),$ ; x plot and check we have the direction right!
   sens:fltarr(nlayers),$
   external_solar_sensor:0.D,$
   detector_intern_temp_switch:0.D,$
   guider_quad_sensor_sum:0.D,$
   outside_relative_humidity:0.D,$
   int_time:0.D},nlat)

endelse




return
end




