function ckop, kswap=kswap

;original ckop (saved as ckop.pro.safe) adapted to write out the deleted files into a file called
;  "deleted-nnn"

;Also added a bit that if we hit an opusreader problem (error reading AQPAQ, INSTR, EMIS etc blocks)
;  it will delete them and add to the deleted file, then continue

;some beginning housekeeping

FORWARD_FUNCTION rev_search, opusplot, deleteit


ndel=0 ;initializing the variable that will make up the filename

swap=0
IF KEYWORD_SET( kswap ) THEN BEGIN
   PRINT, 'Setting swap keyword'
   swap=1
ENDIF

;start by establishing whether files have previously been deleted, and if so, update ndel to reflect where we were already up to
thefile=file_search('deleted-*', count=delcount)
if delcount ne 0 then begin
 ndel=fix(strmid(thefile,8,3))
endif

rs=''
rst1=''
rst2=''
rst3=''
rst4=''
rst5=''
;rst6=''

rst1 = file_search( './[Ss][0-9aabb]*', count=count1, /fully_qualify_path )
;rst6 = file_search( './s[0-8]*', count=count6, /fully_qualify_path)
rst2 = file_search( './h[0-9]*.[0-9]', count=count2,/fully_qualify_path)
rst3 = file_search( './ha*.[0-9]', count=count3,/fully_qualify_path)
rst4 = file_search( './h[0-9]*.[0-9][0-9]', count=count4,/fully_qualify_path)
rst5 = file_search( './ha*.[0-9][0-9]', count=count5,/fully_qualify_path)

if (count4 ne 0 or count5 ne 0) then begin
  print, 'there are more than 10 h files from one filter in here'
  print, 'ckop breaks down. fix it or miss files!!!'
  stop
endif

count=count1+count2+count3
if (count1 ne 0 and count2 ne 0 and count3 ne 0) then rs=[rst1,rst2,rst3]
if (count1 ne 0 and count2 ne 0 and count3 eq 0) then rs=[rst1,rst2]
if (count1 ne 0 and count2 eq 0 and count3 ne 0) then rs=[rst1,rst3]
if (count1 eq 0 and count2 ne 0 and count3 ne 0) then rs=[rst2,rst3]
if (count1 eq 0 and count2 ne 0 and count3 eq 0) then rs=[rst2]
if (count1 eq 0 and count2 eq 0 and count3 ne 0) then rs=[rst3]
if (count1 ne 0 and count2 eq 0 and count3 eq 0) then rs=[rst1]
print, ' # files found : ', count
print, rs

re0=''
read, re0, prompt=' enter index to start from (rtn=0) : '
if (re0 eq 'q') then return, 1
if (re0 eq '') then strtdex = 0 else strtdex = fix(re0)

if(( count ne 0 ) and (strtdex lt count ))then begin

   print, rs[strtdex:*]
   for i = strtdex, count -1 do begin
      print, ''
      print, ' check opus file # ', i, '/',count-1,' : ', rs[i], format='(a,i3,a1,i3,a,a)'
      print, ''

      rc = opusplot( rs[i], ndel, swap )
         case rc of
            0 : break
            1 : goto, nextfile
            else: stop, 'unknown opusplot return code : ', rc
      endcase

   endfor

   nextfile:

endif

print, ' Check Opus Done...'
return, 0
end


function opusplot, file1, ndel, swap

	file2 = ''
	aa = bytarr(108)
	title = ''

	if( file1 eq '' )then stop, ' Empty Filename Variable!'

	opusmin=0.0
	opusmax=99999

	opusreaderpath = GETENV('OPUSREADERPATH')
	IF( STRLEN(opusreaderpath) GT 0 )THEN BEGIN
		IF( rev_search(opusreaderpath,"/") NE STRLEN(opusreaderpath) )THEN BEGIN
			opusreaderpath = opusreaderpath + "/"
		ENDIF
	ENDIF

	SPAWN, opusreaderpath + 'opusreader', UNIT=opusunit, /NOSHELL

   PRINTF, opusunit, swap
   ; Select to get bnr back
	PRINTF, opusunit, 1
	; give OPUS filename
	PRINTF, opusunit, file1

	result = -999L
	if( not eof( opusunit ))then begin
	   ; read result code from pipe
	   READU, opusunit, result
	endif else begin
	   print, '   ...eof on opusunit ', opusunit

      ; all these today were 1kb files (on otmlo as well...)
      ; if thats the case delete and move on
      afs = file_info( file1 )
      print, '   File size : ', file1, afs.size
      if( afs.size / 1.0e6 LT 1. )then begin
         rc = deleteit( file1, ndel )
         return, 0
      endif else begin
         cmd = 'ckopus -C ' + file1
         spawn, cmd
         goto, jump4
      endelse
  endelse

	READU, opusunit, aa		; read bnr header from pipe
;	print,string(aa(0))
;	print,string(aa(1))
	FOR i=0,79 DO BEGIN
		title = title + STRING(aa(i))
	ENDFOR

	PRINT, '   Title : ', title

	wave1 = DOUBLE(aa,80)
	PRINT, '   Starting wavenumber = ',wave1
	wave2 = DOUBLE(aa,88)
	PRINT, '   Ending wavenumber   = ',wave2
	wave3 = DOUBLE(aa,96)
	PRINT,'   Spacing             = ',wave3
	npoint = LONG(aa,104)
	spectral = FLTARR(npoint)
	wave = FLTARR(npoint)
	PRINT, '   Number of points    = ',npoint
	i = LONG(-1)
	bb = BYTARR(4)
;print, ' got header'
	WHILE( i LT npoint-1 ) DO BEGIN
		i = i +1
		READU, opusunit, bb
		value = FLOAT(bb,0)
		spectral(i) = value
		wave(i) = (i*wave3) + wave1
		;print,2,wave(i),spectral(i)
	END
;print, ' got spectra'
	FREE_LUN, opusunit

	spect  = FLTARR(i+1)
	spwave = FLTARR(i+1)

   tek_color
   set_plot, 'x'
   device, decomposed=0
   !p.charsize=1.4
   pos=[0.1, 0.1, 0.9, 0.85]

	ii=LONG(0)
jump:
	IF (ii le i) THEN BEGIN
		spect(ii) = spectral(ii)
		spwave(ii) = wave(ii)
		ii = ii +1
		GOTO, jump
	ENDIF

	xmin = MIN(spwave)
	xmax = MAX(spwave)
	ymin = MIN(spect)
	ymax = MAX(spect)

jump1:
	PLOT, spwave, spect, $
	XTITLE = 'WAVENUMBER', $
	YTITLE = 'INTENSITY', $
	TITLE  = file1 +'!C'+ strtrim(title,2), $
	XRANGE = [xmin,xmax], /xstyle, $
	YRANGE = [ymin,ymax], position=pos

   dex = where( spect lt 0.0, cnt )
   if( cnt gt 0 ) then begin
      oplot, spwave[dex], spect[dex], color=3, psym=3
      print, ymin, ymin/ymax, cnt
   endif

jump4:
	re0=' '
	READ, re0, PROMPT='   Would you like to change the x range (p,d,n,f,q,y) : '

    CASE re0 OF
   	'd' : BEGIN
   	   rc = deleteit( file1, ndel )
        	RETURN, 0
        	END
		'n' : RETURN, 0
		'f' : RETURN, 1
		'q' : STOP, 'Quitting...'
		'y' : BEGIN
				READ, xmin, PROMPT = ' X minimum : '
				READ, xmax, PROMPT = ' X maximum : '
				PLOT, spwave, spect, $
				XTITLE = 'WAVENUMBER', $
				YTITLE = title, $
				TITLE  = file1, $
				XRANGE = [xmin,xmax], /XSTYLE, $
				YRANGE = [ymin,ymax]
				;oplot,spwave,spect,psym=4
			END
		'p' : BEGIN
            for i=0, npoint-1 do print, spwave[i], spect[i]
		   END

		ELSE : BEGIN
			PRINT, '  Enter somnething?'
			GOTO, jump4
			END
	ENDCASE

	re0 = ' '
	READ, re0, PROMPT= '   Would you like to change the y range (y,n): '

	IF( re0 EQ 'y')THEN BEGIN
		READ, ymin, PROMPT= ' Y minimum : '
		READ, ymax, PROMPT= ' Y maximum : '

		PLOT, spwave, spect, $
		XTITLE = 'WAVENUMBER', $
		YTITLE = title, $
		TITLE  = file1, $
		XRANGE = [xmin,xmax],/xstyle, $
		YRANGE = [ymin,ymax]
		;oplot,spwave,spect,psym=4
	ENDIF

	re0 = ' '
	READ, re0, PROMPT= '   Would you like to get the hard copy of this figure (y,n): '
	IF ((re0 EQ 'y') OR (re0 EQ 'Y')) THEN BEGIN
		SET_PLOT,'PS'
		plotfilename = file1+'.ps'
		DEVICE, /landscape, filename = plotfilename
		PLOT, spwave, spect, $
		XTITLE = 'WAVENUMBER', $
		YTITLE = title, $
		TITLE  = file1, $
		XRANGE = [xmin,xmax], /XSTYLE, $
		YRANGE = [ymin,ymax]

		SET_PLOT, 'x'
		PLOT, spwave, spect, $
		XTITLE = 'WAVENUMBER', $
		YTITLE = title, $
		TITLE  = file1, $
		XRANGE = [xmin,xmax], /XSTYLE, $
		YRANGE = [ymin,ymax]

	ENDIF

	re0= ' '
	READ, re0, PROMPT = '   Replot or go to next (y,n) : '

	IF((re0 EQ 'y' ) OR (re0 EQ 'Y')) THEN GOTO, jump1

RETURN, 0
END

function deleteit, file1, ndel

   ndelstr=string(format='(I03)', ndel)        ;make the number of deleted files into a string
   delfilename='deleted-'+ndelstr              ; make the filename of the existing file (or a new one if zero)
   openw,1,delfilename,/append                 ;open the file and add to it
      printf,1,file1                           ;print in the name of the deleted file
      ndel=ndel+1                              ;update the count
      newdelfilename='deleted-'+string(format='(I03)',ndel) ;make a new file name with the updated count
   close,1                                     ;close the file
   command='mv '+delfilename+' '+newdelfilename ; command to move the file with the old count in the name, to the new count-named file
   spawn,command
   ;now to move the deleted file into a sub-directory
   command='mkdir deleted'
   spawn,command
   spawn, 'chmod 777 deleted'
   temp=strsplit(file1,'/',count=tempcount,/extract)
   file1short=temp(tempcount-1)
   command='cp '+file1+' deleted/'+file1short
   spawn,command
   spawn,'chmod 666 deleted/*'
   print, ''
   file_delete, file1, /verbose

return, 0
end

function rev_search, str, target
	return,strpos( str, target, /reverse_search )
end
