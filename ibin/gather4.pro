pro gather4, site=site, mol=mol, plt=plt, lstFile=lstFile, specDBfile=specDBfile, outfile=outfile

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
forward_function bldstrct

funcs = [ 'usesite', 'usemol', 'readrfmd4', 'readnxn4', 'readprfs4', 'readlayr4']
resolve_routine, funcs, /either

;---------------------------------
; Check user input in program call
;---------------------------------
if( ~keyword_set( site ) || ~keyword_set( mol ) || ~keyword_set(lstFile) || ~keyword_set(specDBfile) || ~keyword_set(outfile) ) then begin
   print, ' example usage : gatherd, site="tab", mol="co2", lstFile="/home/usr/mlo_1_1_13.lst", specDBfile="/home/usr/specDB_mlo_2013.dat", outfile="/home/usr/MLO_2013.sav" '
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
  
; Read header and count lines
buf = ''
i   = 0
while ~strcmp(buf, 'Date', 4, /fold_case )  do begin
  readf, fid_lstFile, buf
  i++
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
newDate    = (lDates + 0D)*1000000 + (lTstamps + 0D)
unq_ind    = uniq(newDate,sort(newDate))

if ( nsize ne size(unq_ind,/n_elements) ) then begin    ; Found duplicate entries
  lDates   = lDates[unq_ind]
  lTstamps = lTstamps[unq_ind]
  lDirs    = lDirs[unq_ind]  
  nsize    = size(lDates,/n_elements)
endif

;-------------------------------------------
; Get layering info from station.layers file
;-------------------------------------------
print, ' Opening file : ', As.infodir + 'local/station.layers'
klay = readlayr4( grd, '/Users/ebaumer/Data/TestBed/mlo/station.layers' )
;klay = readlayr( grd, As.infodir + 'local/station.layers' )
nlayers = klay-1

;--------------------------------------------------
; Now that we have the number of spectra and number
; of layers for the spectra we can initialize the 
; datastructure to read data to
;--------------------------------------------------
ds = bldstrct( nsize, nlayers )

;-------------------------------------
; Open and read spectral database file
;-------------------------------------
; Determine number of lines in file
nlines = file_lines(specDBfile)
; Headers for data to extract from spectral DB file
getHdrs = ['Filename','TStamp','Date','SNR','N_Lat','W_Lon','Alt','SAzm','SZen','Dur','HouseRH','ExtStatRH','Ext_Solar_Sens','Quad_Sens','Det_Intern_T_Swtch']
;Hdr ind      0         1        2      3     4       5       6     7      8      9      10         11           12             13               14
nhdrs    = intarr(size(getHdrs,/n_elements))

; Open file
openr, fid_specDBfile, specDBfile, /get_lun, error=ioerr
if( ioerr ne 0 ) then begin
  printf, -2, !err_string
  stop
  
endif

; First line of spectral DB is the header
buf = ''
readf, fid_specDBfile, buf
header = strsplit(buf,' ', /extract, count=nheaders)

; Find the indices for each header to extract
for i = 0, (size(getHdrs,/n_elements)-1) do begin
  nhdrs[i] = where(header eq getHdrs[i])
  
endfor

; Read data in spectral database
buf = ''
j = 0
for i = 0, (nlines-2) do begin
  readf, fid_specDBfile, buf
  subs = strsplit( buf, ' ', /extract, count=nitms )
  
  tempDate   = subs[nhdrs[2]]
  tempTstamp = subs[nhdrs[1]]
  
  ; If date and timestamp from DB match an entry in list file grab data
  testMatch = strmatch(lDates, tempDate) + strmatch(lTstamps, tempTstamp)
  indMatch  = where(testMatch eq 2)
  
  if ( size(indMatch,/n_elements) gt 1 ) then begin
    print, 'Duplicate Entries in list file found'
    exit
    
  endif
  
  if indMatch ge 0 then begin   
    ds[j].spectraname    = subs[nhdrs[0]]
    ds[j].hhmmss         = subs[nhdrs[1]] 
    ds[j].yyyymmdd       = subs[nhdrs[2]] 
    ds[j].snr            = subs[nhdrs[3]]  + 0.0D0
    ds[j].latitude       = subs[nhdrs[4]]  + 0.0D0
    ds[j].longitude      = subs[nhdrs[5]]  + 0.0D0
    ds[j].alt_instrument = subs[nhdrs[6]]  + 0.0D0
    ds[j].azi            = subs[nhdrs[7]]  + 0.0D0
    ds[j].sza            = subs[nhdrs[8]]  + 0.0D0
    ds[j].int_time       = subs[nhdrs[9]]  + 0.0D0
    ds[j].external_solar_sensor       = subs[nhdrs[12]] + 0.0D0
    ds[j].guider_quad_sensor_sum      = subs[nhdrs[13]] + 0.0D0
    ds[j].detector_intern_temp_switch = subs[nhdrs[14]] + 0.0D0
    ds[j].directory      = lDirs[indMatch]
    
    ; Inputs related to station.layers file
    ds[j].alt_index = indgen(nlayers, /long) + 1
    ds[j].altitude  = grd.midp[0:nlayers-1]    
    
    ;----------------------------------------
    ; Determine Outside RH. First choice is 
    ; external station RH. If this is missing
    ; default to house log RH
    ;----------------------------------------
    HouseRH  = subs[nhdrs[10]] + 0.0D0
    ExtStaRH = subs[nhdrs[11]] + 0.0D0
    
    if ( ExtStaRH ge 0 ) then begin
      ds[j].outside_relative_humidity = ExtStaRH
    endif else begin         
      ds[j].outside_relative_humidity = HouseRH  
    endelse
    j++
  endif

endfor

;------------------------------------------------
; Manipulate Date and Tstamps to get YYYY, MM, DD
; DOY, etc and convert Date and Tstamp to int
;------------------------------------------------
jd2000   = julday(1,1,2000, 00, 00, 00)

for i = 0, nsize-1 do begin
  ds[i].year  = strmid(ds[i].yyyymmdd,0,4) + 0
  ds[i].month = strmid(ds[i].yyyymmdd,4,2) + 0
  ds[i].day   = strmid(ds[i].yyyymmdd,6,2) + 0
  HH          = strmid(ds[i].hhmmss,0,2)   + 0
  MM          = strmid(ds[i].hhmmss,2,2)   + 0
  SS          = strmid(ds[i].hhmmss,4,2)   + 0
  
  ; Date conversions
  ds[i].doy      = JULDAY( ds[i].month, ds[i].day, ds[i].year, HH, MM, SS )  - JULDAY( 1, 1, ds[i].year, 0, 0, 0 ) +1
  ds[i].hrs      = double(HH) + (double(MM) + double(SS) /60.0d) /60.0d
  daysinyear     = JULDAY( 12, 31, ds[i].year, 0, 0, 0 )  - JULDAY( 1, 1, ds[i].year, 0, 0, 0 ) +1
  ds[i].tyr      = ds[i].year + (ds[i].doy + ds[i].hrs/24.D)/daysinyear
  ds[i].datetime = JULDAY( ds[i].month, ds[i].day, ds[i].year, HH, MM, SS ) - jd2000
endfor

;--------------------------------------------
; Create Dummy variables. These are variables
; that are to be stored in the save files;
; however, are not currently read in. Set
; to missing value -999
;--------------------------------------------
ds.zcorrect = make_array(nsize,/float, value=-999)

                ;--------------------------------------------------;
                ; Loop through observations to collect output data ;
                ;--------------------------------------------------;
for i = 0, nsize-1 do begin
  
  ;----------------------------------------
  ; Read control file from output directory
  ;----------------------------------------  
;  ctlFname = ds[i].directory + 'sfit4.ctl'
;  readsctl4, ctlData, ctlFname
  
   ;----------------------------------------
   ; Read summary file from output directory
   ;----------------------------------------
   dum = readsum4( sumf, ds[i].directory + 'summary' ) 
   
   ds[i].iterations = sumf.itr
   ds[i].rms        = sumf.fitrms
   ds[i].dofs       = sumf.dofstrg
   ;ds[i].rettc      = ?????
  
  ;----------------------------------------
  ; Read statvec file from output directory
  ;----------------------------------------  
  statvecFname = ds[i].directory + 'statevec'
  dum = readstat4( statvecData, statvecFname )
  
  ds[i].p      = statvecData.p[0:nlayers-1]
  ds[i].t      = statvecData.t[0:nlayers-1]
  ds[i].aprtc  = statvecData.col[0,0]
  ds[i].aprvmr = statvecData.vmr[0,0,0:nlayers-1]
  ds[i].retvmr = statvecData.vmr[1,0,0:nlayers-1] 
   
  dum = where((statvecData.pnam[0:statvecData.nprm-1] eq 'BckGrdSlp'), count)
  if ( count ge 1 ) then ds[i].bslope = mean(statvecData.prm[1,dum])
  
  dum = where(((statvecData.pnam[0:statvecData.nprm-1] eq 'SWNumShft' ) or ( statvecData.pnam[0:statvecData.nprm-1] eq 'IWNumShft')), count)
  if ( count ge 1 ) then ds[i].wshift = mean(statvecData.prm[1,dum])
  
  dum = where((statvecData.pnam[0:statvecData.nprm-1] eq 'ZeroLev'), count)
  if ( count ge 1 ) then ds[i].zerolev = mean(statvecData.prm[1,dum])
  
  dum = where((statvecData.pnam[0:statvecData.nprm-1] eq 'SPhsErr'), count)
  if ( count ge 1 ) then ds[i].phase = mean(statvecData.prm[1,dum])
  
  ds[i].alt_boundaries[0,*] = grd.alts[1:nlayers]
  ds[i].alt_boundaries[1,*] = grd.alts[0:nlayers-1]
  
  ;--------------------------------------------------------------
  ; Read surface pressure and temperature from reference.prf file
  ;--------------------------------------------------------------
  dum = readrfmd4( refm, ds[i].directory + 'reference.prf', /zpt )
  
  ; Determine if alt decreasing: updn=1 or alt increasing: updn=0
  if ( refm.updn eq 1 ) then begin
    ds[i].surface_pressure    = refm.prfs[1,-1]
    ds[i].surface_temperature = refm.prfs[2,-1]
  endif else if ( ref.updn eq 2 ) then begin
    ds[i].surface_pressure    = refm.prfs[1,0]
    ds[i].surface_temperature = refm.prfs[2,0]
  endif
  
  ;-------------------------------------
  ; Read Averaging Kernal data AK.target
  ;-------------------------------------
  dum = readnxn4( akData, ds[i].directory + 'ak.target' )
  if (akData.n ne nlayers ) then stop, 'akData.n and nlayers NOT equal'
  
  ; Normalize Averaging Kernal relative to a priori
  for ii = 0, nlayers-1  do begin
    for jj = 0, nlayers-1 do begin
      ds[i].ak[ii,jj] = akData.mat[ii,jj] * ( ds[i].aprvmr[ii] / ds[i].aprvmr[jj] )
    endfor
  endfor  
  
  ;-----------------------------------------------
  ; Calculate the total column averaging kernel.
  ; Need to get retrieved airmass for total column 
  ; averaging kernel from rprs.table
  ;-----------------------------------------------
  dum = readprfs4( rprfs, ds[i].directory + 'rprfs.table' )
  tmpsum   = fltarr(nlayers)
  ds[i].ms = rprfs.a                                    ; Air-mass profile (same in a prior prf table or retreived prf table)
  
  for jj = 0, nlayers-1 do begin
    for ii = 0, nlayers-1 do begin
      tmpsum[ii] = rprfs.a[ii] * ds[i].ak[ii,jj]
    endfor
    ds[i].aktc[jj] = ( total(tmpsum) ) / rprfs.a[jj]
    ds[i].sens[jj] = total( ds[i].ak[*,jj] )            ; This is suming all layers without airmass weighting => sensitivity.
  endfor
  
  ;----------------------
  ; Intermediate plotting
  ;----------------------
  if( keyword_set( plt ) ) then begin
    tek_color
    set_plot, 'x'
    device, decompose=0
    window, 2
    !p.multi=[0,2,2]
    plot,  ds[i].ak[0,*], ds[i].altitude, xrange=[-2,2]
    for ii = 0, nlayers-1 do oplot, ds[i].ak[ii,*], ds[i].altitude, color=ii+2    
    oplot, ds[i].sens,    ds[i].altitude
    plot,  ds[i].aprvmr,  ds[i].altitude
    oplot, ds[i].retvmr,  ds[i].altitude, color=2
    plot,  ds[i].aktc,    ds[i].altitude
    ;device,/close
  endif 
  
  ;-----------------
  ; Get water vapour
  ;-----------------
  dum = readprfs4( aprfs, ds[i].directory + 'aprfs.table' )
  
  ; A priori
  ds[i].aprh2ovmr = aprfs.vmr[*,0]                       ; H2O profile
  ds[i].aprh2otc  = total( aprfs.vmr[*,0] * rprfs.a )    ; Total column H2O
  ds[i].aprlaycol = ds[i].aprvmr * rprfs.a               ;
  
  ; Retrieved
  ds[i].retlaycol = ds[i].retvmr * rprfs.a               ;

endfor ; next entry

;---------------------------
; Save data to IDL save file
;---------------------------
print, 'ready to save'

;reorder first by datetime so that we ensure chronological order
ds = ds( sort( ds.datetime ) )

save, ds, filename=outfile
print,'Data structure for all retrievals saved as ', outfile

end


;___________________________________________________________________________
;                            SUBROUTINES
;___________________________________________________________________________
                            
function bldstrct, npnts, nlayers
;--------------------------------------------
; Subroutine to initialize data structure for 
; save file
;--------------------------------------------
return, datastructure = REPLICATE({h224, $                ; What is h224 ??????
        spectraname                :'',$                  ; OPUS file name
        directory                  :'',$                  ; Output directory location
        hhmmss                     :'',$                  ; Time stamp of observation HHMMSS     [String!!!]
        yyyymmdd                   :'',$                  ; Date stamp of observation YYYYMMDD   [String!!!]
        snr                        :0.0,$                 ; Signal to noise ratio as given by OPUS file
        p                          :fltarr(nlayers),$     ; Pressure levels [mbar]
        t                          :fltarr(nlayers),$     ;
        ms                         :fltarr(nlayers),$     ;
        rms                        :0.0,$                 ;
        dofs                       :0.0,$                 ;
        sza                        :0.D0,$                ;
        azi                        :0.D0,$                ;
        iterations                 :0,$                   ;
        zcorrect                   :0.D0,$                ;
        wshift                     :0.D0,$                ;
        zerolev                    :0.D0,$                ;
        bslope                     :0.D0,$                ;
        phase                      :0.D0,$                ;
        aprvmr                     :fltarr(nlayers),$     ;
        aprlaycol                  :fltarr(nlayers),$     ;
        retvmr                     :fltarr(nlayers),$     ;
        retlaycol                  :fltarr(nlayers),$     ;
        aprtc                      :0.D0,$                ;
        rettc                      :0.D0,$                ; Gas total column ????????????
        aprh2ovmr                  :fltarr(nlayers),$     ;
        aprh2otc                   :0.D0,$                ;
        year                       :0,$                   ; Year [YYYY]
        month                      :0,$                   ; Month [MM]
        day                        :0,$                   ; Day [DD]
        hrs                        :0.D0,$                ; Hours plus fractional hours  hh.fffffff
        doy                        :0.D0,$                ; Day of the year
        tyr                        :0.D0,$                ; Days plus fractional days    ddd.ffffff
        datetime                   :0.D0,$                ; mjd2k date
        latitude                   :0.00,$                ; Latitude of instrument []
        longitude                  :0.00,$                ; Longitude of insturment []
        alt_instrument             :0.00,$                ; Altitude of insturment [m]
        surface_pressure           :0.D0,$                ; Surface Pressure [mbar]
        surface_temperature        :0.D0,$                ; Surface temperature [C]
        alt_index                  :lonarr(nlayers),$     ;
        alt_boundaries             :fltarr(2,nlayers),$   ;
        altitude                   :fltarr(nlayers),$     ;
        ak                         :fltarr(nlayers,nlayers),$ ;check directions and normalize....
        aktc                       :fltarr(nlayers),$     ; x plot and check we have the direction right!
        sens                       :fltarr(nlayers),$     ;
        external_solar_sensor      :0.D0,$                ; External solar sensor (for MLO either E_radiance or W_radiance) [volts]
        detector_intern_temp_switch:0.D0,$                ; Detector Internal Temperature Switch []
        guider_quad_sensor_sum     :0.D0,$                ; Quad solar sensor from house log data [volts]
        outside_relative_humidity  :0.D0,$                ; Outside relative humidity. From either house log or external station data [%]
        int_time                   :0.D0      },npnts)

end




