;Main Program Version: idlcr8hdf.pro v4.0b16, 20131023
;  Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;Sub-versions (refer to idlcr8hdf-v4.0_Readme.pdf for full history)

PRO idlcr8hdf_common
;Procedure to define the COMMON blocks for this program
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;History:
;  20050909: Introduced to IDLCR8HDF - Version 1.1
;  20061012: Variable 'ncsa' added to METADATA; 'iarr', 'larr', 'rarr', 'darr' holding Arrays
;            removed from DATA and replaced with Structure 'ds'; Variable 'vfv' added to DATA;
;            WIDGET_WIN added for common variables associated with the Graphical User Interface
;            - Version 2.0
;  20080302: tab_type integer added to TABLEDATA - Version 3.0
;  20100205: rerr string added to WIDGET_WIN - Version 3.09
;  20110401: vnchange added to DATA; mv_lng and mv_dbl added to METADATA; vserror added to DATA;
;            vfv removed from DATA; ncsa removed from METADATA - Version 4.0b1
;
;Input: Nil
;
;Output: Nil
;
;Called by: N/A
;
;Subroutines Called: None

COMMON TABLEDATA, tab_arr,tab_ver,tab_type
COMMON METADATA, meta_arr,attr_arr_glob,attr_arr_data,free_attr,mv_lng,mv_dbl
COMMON DATA, ds,ndm,nvn,vn,vu,vnchange,vserror
COMMON WIDGET_WIN, wtxt,b1,lineno,base,o3,dux,rerr

END ;Procedure idlcr8hdf_common



PRO intro_event, ev
;Procedure to define how Events from the Start-up Introduction Window are handled
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;History:
;  20061012: Introduced to IDLCR8HDF - Version 2.0
;
;Input: ev - Selected widget event structure
;
;Output: o3 - Common string array defining the various options for program output
;
;Called by: XMANAGER in INTRO
;
;Subroutines Called: None

COMMON WIDGET_WIN

;The uservalue is retrieved from a widget when an event occurs
WIDGET_CONTROL,ev.id,GET_UVALUE=uv
;Assign/Remove AVK button event to/from a variable name
IF uv EQ 'AVK' THEN IF o3[1] EQ uv THEN o3[1]='0' ELSE o3[1]=uv $
;Assign/Remove Log Output button event to/from a variable name
ELSE IF uv EQ 'idlcr8hdf.log' THEN IF o3[2] EQ uv THEN o3[2]='0' ELSE o3[2]=uv $
;Assign/Remove Pop-up window for Log Output button event to/from a variable name
ELSE IF uv EQ 'Pop' THEN IF o3[3] EQ uv THEN o3[3]='0' ELSE o3[3]=uv $
;Assign button event to a variable name
ELSE IF (uv EQ 'H4') OR (uv EQ 'H5') OR (uv EQ 'NC') THEN o3[0]=uv $
ELSE o3[0]='0' ;Cancel button chosen
IF (uv NE 'AVK') AND (uv NE 'idlcr8hdf.log') AND (uv NE 'Pop') THEN WIDGET_CONTROL,ev.top,/DESTROY

END ;Intro_Event



PRO intro, intype
;Procedure which creates an Introduction Window at start-up when IDLCR8HDF is called without parameters,
;or invalid parameters, or is called by IDL Virtual Machine. The user has a choice of continuing with
;the program after selecting input options, or stopping the program.
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;History:
;  20061012: Introduced to IDLCR8HDF - Version 2.0
;  20080302: Swapped the order of the option windows, so that the options indicated by the check
;            boxes appear above the option boxes that close the Introduction Window and continue
;            with the program - Version 3.0
;  20100205: Include text regarding the RETERR argument which can be accepted as an input
;            parameter when using the full version of idlcr8hdf - Version 3.09
;  20110401: Add vertxt string array to hold text which changes between versions of the code;
;            Change text to reference GEOMS compliant files instead of AVDC/EVDC/NDACC; Change
;            text regarding the format of the structure required for input - Version 4.0b1
;  20111220: Change text and options to include netCDF; change contact details - Version 4.0b7
;  20130114: Make insensitive /LOG and /NC options if the program is called in IDL DEMO mode
;            -Version 4.0b14
;
;Input: intype - Integer set to -1 or -2: -1 indicates normal state; -2 indicates that input
;                parameters at the IDLCR8HDF call were invalid.
;
;Output: Nil
;
;Called by: IDLCR8HDF
;
;Subroutines Called: INTRO_EVENT (via XMANAGER)

nhdr=43 & errtxt=STRARR(nhdr)
vertxt=['idlcr8hdf-v4.0_Readme.pdf','v4.0b16 October 2013']
errtxt[1]='Welcome to IDLcr8HDF.  This program creates GEOMS compliant HDF4, HDF5 and netCDF files'
errtxt[2]='(also refer to '+vertxt[0]+').'
errtxt[4]='Inputs to the program (IDL Virtual Machine (VM) and IDL Licensed (LIC) Versions):'
errtxt[5]='  METADATA TEMPLATE FILE - Containing the Global and Variable Attribute information for the site.'
errtxt[6]='  DATA FILE(s) - Multiple selection permitted. The file(s) must show the datasets in the single column'
errtxt[7]='    format described in the documentation.'
errtxt[8]='  TAV FILE - the current non-encrypted Table Attribute Values file.'
errtxt[9]='  OUTPUT DIRECTORY - Directory for any HDF, netCDF and log files created. Shortcut values of ''M'' or ''D'''
errtxt[10]='   will output files to the Metadata or Data file directories respectively.'
errtxt[12]='Alternative Input Option for IDL LIC Versions:'
errtxt[13]='  GLOBAL ATTRIBUTES ARRAY (GA) - a string array containing the Global Attributes in the form'
errtxt[14]='    ''label=value''.'
errtxt[15]='  DATA STRUCTURE (DS) - a heap structure using pointers containing the Variable Attribute Labels'
errtxt[16]='    (DS.VA_L), the Variable Attribute Values (DS.VA_V), and the Data (DS.Data), for a single output file.'
errtxt[17]='  TAV FILE - the current non-encrypted Table Attribute Values file.'
errtxt[18]='  OUTPUT DIRECTORY - Directory for any HDF, netCDF and log files created.'
errtxt[19]='  RETERR - String variable to which any error(s) are written.'
errtxt[21]='For IDL VM, input is by ''DIALOG_BOXES''. For IDL LIC, input can be by ''DIALOG_BOXES'' or passed'
errtxt[22]='by calling the program with one of the following command line options:'
errtxt[23]='  1. idlcr8hdf  (Opens this box, and allows the user the option to continue with file inputs).'
errtxt[24]='  2. idlcr8hdf,METAFILE,DATAFILE(s),TAVFILE,OUTDIR[,RETERR][,/H5][,/NC][,/AVK][,/Log][,/Popup]  or'
errtxt[25]='    idlcr8hdf,'''','''','''',''''[,/H5][,/NC][,/AVK][,/Log][,/Popup]  (For null string, DIALOG_BOXES will prompt for input).'
errtxt[26]='  3. idlcr8hdf,GA,DS,TAVFILE,OUTDIR[,RETERR][,/H5][,/NC][,/AVK][,/Log][,/Popup] or
errtxt[27]='    idlcr8hdf,GA,DS[,/H5][,/NC][,/AVK][,/Log][,/Popup]  (Inputs are from session memory, DIALOG_BOX(s) will'
errtxt[28]='    prompt for input if TAVFILE or OUTDIR are not included).'
errtxt[29]='    /H5, /NC, /AVK, /Log and /Popup keywords are used in place of the options given below (HDF4 is default).'
errtxt[31]='Contacts -'
errtxt[32]='  Ian Boyd (iboyd@astro.umass.edu)'
errtxt[33]='  Department of Astronomy, 619 Lederle GRC, University of Massachusetts'
errtxt[34]='  710 North Pleasant St, Amherst, MA 01002, USA'
errtxt[36]='  Ghassan Taha, AVDC Project Manager (ghassan.taha@nasa.gov)'
errtxt[37]='  NASA Goddard Space Flight Center, Code 613.3'
errtxt[38]='  Greenbelt, MD 20771, USA'
errtxt[40]='AVDC Website: Tools and documentation available from http://avdc.gsfc.nasa.gov/Overview/index.html'
errtxt[42]='To continue, please choose from the options below (Note: HDF5 only available on IDL6.2 or greater).'
errtxt='      '+errtxt

;Set-up text display widget
IF intype EQ -2 THEN xtxt=' - Command Line Input Error' ELSE xtxt=''
IF intype EQ -3 THEN optsens=0 ELSE optsens=1
base=WIDGET_BASE(Title='idlcr8hdf '+vertxt[1]+xtxt,Tlb_Frame_Attr=1,/Column) ;,Tab_Mode=1)
wtxt=WIDGET_TEXT(base,xsize=90,ysize=25,/Scroll)
base3=WIDGET_BASE(base,/Nonexclusive)
logtext='Append log output to the file ''idlcr8hdf.log'' '
IF intype EQ -3 THEN logtext=logtext+'(No log or netCDF file output permitted in IDL DEMO Mode)' $
ELSE logtext=logtext+'(will create the file IF it doesn''t exist)' 
poptext='Open a Pop-Up Window to display log output'
avktext='If Avg. Kernel data are present, append sentence to VAR_NOTES giving first three values for '
avktext=avktext+'lowest altitude level'
avktip='Sentence reads ''First three AVK values for the lowest altitude level are: x.xx x.xx x.xx'''
b4=WIDGET_BUTTON(base3,value=logtext,uvalue='idlcr8hdf.log',frame=3,SENSITIVE=optsens)
b5=WIDGET_BUTTON(base3,value=poptext,uvalue='Pop',frame=3)
b6=WIDGET_BUTTON(base3,value=avktext,uvalue='AVK',frame=3) ;,Tooltip=AVKTip)
base2=WIDGET_BASE(base,/Row)
tip='Left Mouse Click or Tab to entry and hit <Spacebar>'
b1=WIDGET_BUTTON(base2,value='HDF4',uvalue='H4',frame=3) ;,Tooltip=Tip)
IF FLOAT(!Version.Release) GE 6.2 THEN $
  b2=WIDGET_BUTTON(base2,value='HDF5',uvalue='H5',frame=3) $;,Tooltip=Tip) $
ELSE b2=WIDGET_BUTTON(base2,value='HDF5',Sensitive=0,frame=3)
b7=WIDGET_BUTTON(base2,value='netCDF',uvalue='NC',frame=3,SENSITIVE=optsens)
b3=WIDGET_BUTTON(base2,value='Stop',uvalue='CANCEL',frame=3) ;,ToolTip=Tip)
WIDGET_CONTROL,base,/Realize
WIDGET_CONTROL,b4,/Input_Focus
FOR i=0,N_ELEMENTS(errtxt)-1 DO $
  WIDGET_CONTROL,wtxt,set_value=errtxt[i],/Append
XMANAGER,'intro',base

END ;Intro



PRO idlcr8hdf_event, ev
;Procedure to close the pop-up logging window after user selects 'Finish'.
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;History:
;  20061012: Introduced to IDLCR8HDF - Version 2.0
;
;Input: Selected widget event structure
;
;Output: Nil
;
;Called by: XMANAGER in IDLCR8HDF and STOP_WITH_ERROR
;
;Subroutines Called: None

WIDGET_CONTROL,ev.top,/DESTROY
RETALL & HEAP_GC

END ;IDLcr8HDF_Event



PRO stop_with_error, txt1, txt2, lu, ds
;Procedure called when an error in the program inputs is detected. An error message is displayed
;and the program stopped and reset. If necessary, open files are closed, and memory associated
;with a structure is freed. The error message is displayed in one or more of the following:
;a Pop-up dialog window; the Pop-up logging window; the Output Logging window in the IDLDE;
;a log file (idlcr8hdf.log)
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;History:
;  20050802: Original IDLCR8HDF Routine - Version 1.0
;  20061012: Set-up so that the error output is displayed in the output window(s) dependent on
;            the options chosen by the user, the point in the program that the error is detected,
;            and the method that IDLCR8HDF is called. If txt1 is preceeded by 'D_' or is null,
;            the error output is to a Pop-up Dialog window. Other error output options are
;            determined by the values in the (Common) dux array - Version 2.0
;  20100205: Allow routine to return to the calling routine, rather than stop the application, if
;            a 'reterr' argument is included in the call to idlcr8hdf - Version 3.09
;  20110401: Change end text dependent on whether the program is creating a GEOMS file or doing QA
;            on a GEOMS file - Version 4.0b1
;  20111220: Change text referring to HDF to GEOMS - Version 4.0b7
;
;Inputs: txt1 - the initial text line of the error message. Generally contains the name of the routine
;               where the error was detected.
;        txt2 - the second text line which generally describes the error state.
;        lu - Where applicable, the file unit that needs to be closed at the termination of the program,
;             otherwise set to -1.
;        ds - Where applicable, the name of the data structure set-up by the program (dependent on
;             the point in the program that the error is detected), so that memory associated with the
;             structure can be freed.
;        dux - an integer array used to determine the output options for the error message.
;
;Output: Error message displayed/output dependent on the requested output options.
;
;Called by: The routine in which the error was detected. The following routines call STOP_WITH_ERROR:
;           READ_TABLEFILE; TEST_FILE_INPUT; READ_METADATA; EXTRACT_AND_TEST; CHECK_METADATA;
;           SET_UP_STRUCTURE; CHECK_MIN_MAX_FILL; EXTRACT_DATA; FIND_HDF_FILENAME; IDLCR8HDF.
;
;Subroutines Called: IDLCR8HDF_EVENT (via XMANAGER)

COMMON WIDGET_WIN

IF lu NE -1L THEN FREE_LUN,lu

IF txt1 EQ '' THEN BEGIN ;<cancel> chosen on Intro box
  res=DIALOG_MESSAGE('IDLcr8HDF Stopped!',/Information,Title='AVDC IDLcr8HDF')
ENDIF ELSE BEGIN
  ;If necessary free up memory by destroying the heap variables pointed at by its pointer arguments
  IF N_ELEMENTS(ds) NE 0 THEN PTR_FREE,ds.data
  ;Write error to file and/or IDL output window
  IF STRMID(txt1,0,2) EQ 'D_' THEN txtx=STRMID(txt1,2) ELSE txtx=txt1
  FOR i=dux[0],dux[1],dux[2] DO BEGIN
    IF i EQ -1 THEN BEGIN
      PRINT,'  ERROR in '+txtx & PRINT,'    '+txt2
      PRINT,'' & PRINT,'IDLcr8HDF stopped - Program Ended on '+SYSTIME(0)
    ENDIF ELSE BEGIN 
      PRINTF,i,'  ERROR in '+txtx & PRINTF,i,'    '+txt2
      IF (i EQ dux[0]) OR ((i EQ dux[1]) AND (STRPOS(o3[2],'idlcr8hdf.log') NE -1)) THEN BEGIN
        PRINTF,i,'' & PRINTF,i,'IDLcr8HDF stopped - Program Ended on '+SYSTIME(0)
      ENDIF
    ENDELSE
  ENDFOR
  IF dux[1] NE dux[0] THEN FREE_LUN,dux[1]
  IF (STRMID(txt1,0,2) EQ 'D_') AND (rerr[0] EQ 'NA') THEN BEGIN
    ;write error to DIALOG Box instead of Popup window
    errtxt2=STRARR(4)
    errtxt2[0]=STRMID(txt1,2) & errtxt2[1]=txt2 & errtxt2[3]='IDLcr8HDF Stopped!'
    res=DIALOG_MESSAGE(errtxt2,/Error,Title='AVDC IDLcr8HDF Error')
  ENDIF ELSE IF rerr[0] EQ 'NA' THEN BEGIN ;write error to Popup window
    IF o3[4] EQ '0' THEN endtxt='GEOMS file creation ' $
    ELSE endtxt='GEOMS file testing '
    lineno=lineno+4L
    WIDGET_CONTROL,wtxt,set_value='  ERROR in '+txt1,/Append
    WIDGET_CONTROL,wtxt,set_value='    '+txt2,/Append
    WIDGET_CONTROL,wtxt,set_value='',/Append,Set_text_top_line=lineno
    WIDGET_CONTROL,wtxt,set_value=endtxt+'stopped - hit <Finish> to close program',/Append
    WIDGET_CONTROL,b1,Sensitive=1,/Input_Focus
    XMANAGER,'stop_with_error',base,Event_Handler='idlcr8hdf_event'
  ENDIF
ENDELSE
HEAP_GC
IF rerr[0] EQ 'NA' THEN RETALL $
ELSE BEGIN
  IF o3[4] EQ '0' THEN endtxt='create GEOMS file' $
  ELSE endtxt='complete GEOMS file test'
  rerr[0]='Unable to '+endtxt+' - '+txtx+txt2
ENDELSE

END ;Procedure Stop_With_Error



PRO infotxt_output, infotxt
;Procedure called when the program makes a change to the input meta data or reports information
;relevant to the creation of the HDF/netCDF file. This information can be reported to a Pop-up logging
;window, IDLDE output log window, and/or the log file. Code for this output was originally
;written directly in the affected procedures
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;History:
;  20090311: Introduced to IDLCR8HDF - Version 3.06
;  20110401: infotxt INFORMATION header changed to a number, to allow changes to the comment
;            header depending on how idlcr8hdf has been called, as follows: 0 = INFORMATION;
;            1 = NON-STANDARD COMPLIANCE NOTIFICATION (QA) o/w INFORMATION; 2 = ERROR (QA)
;            o/w INFORMATION; 3 = ERROR; 4 = DEBUG - Version 4.01
;
;Inputs: infotxt - the text line(s) of the information message. Can be either a scalar string
;                  or string array
;
;Output: Message displayed/output dependent on the requested output options
;
;Called by: The routine in which the reported change was made. The following routines call
;           INFOTXT_OUTPUT: READ_TABLEFILE; GEOMS_RULE_CHANGES; PRE_DEFINED_ATT_CHECKS;
;           READ_METADATA; EXTRACT_AND_TEST; CHECK_METADATA; EXTRACT_DATA; SET_UP_STRUCTURE;
;           CHECK_STRING_DATATYPE; CHECK_MIN_MAX_FILL; READ_DATA; FIND_HDF_FILENAME;
;           AVDC_HDF_WRITE; IDLCR8HDF
;
;Subroutines Called: None

COMMON WIDGET_WIN

dm=SIZE(infotxt,/N_ELEMENTS)
qaval=FIX(STRMID(infotxt[0],0,1))
write_rerr=0 ;Boolean to generate a return error message

IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN BEGIN ;program called in QA mode
  ;Add correct message title
  CASE 1 OF
    qaval EQ 0: infotxt[0]='  INFORMATION:'+STRMID(infotxt[0],1)
    qaval EQ 1: infotxt[0]='  NON-STANDARD COMPLIANCE NOTIFICATION:'+STRMID(infotxt[0],1)
    qaval EQ 4: infotxt[0]='  DEBUG:'+STRMID(infotxt[0],1)
    ELSE: infotxt[0]='  ERROR:'+STRMID(infotxt[0],1)
  ENDCASE
  ;truncate message from the '|'
  bs_found=0
  FOR n=0,dm-1 DO BEGIN
    IF bs_found EQ 1 THEN infotxt[n]='' $
    ELSE BEGIN
      bspos=STRPOS(infotxt[n],'|')
      IF bspos NE -1 THEN BEGIN
        infotxt[n]=STRMID(infotxt[n],0,bspos)
        bs_found=1
      ENDIF
    ENDELSE
  ENDFOR
  ;recalculate number of good infotxt values
  gi=WHERE(infotxt NE '',dm)
ENDIF ELSE BEGIN ;program called in HDF file create mode
  CASE 1 OF
    qaval EQ 3: BEGIN
                  infotxt[0]='  ERROR:'+STRMID(infotxt[0],1)
                  IF rerr[1] NE 'NA' THEN BEGIN ;generate return error message
                    IF rerr[1] EQ '' THEN BEGIN
                      IF o3[4] EQ '0' THEN endtxt='create GEOMS file' $
                      ELSE endtxt='complete GEOMS file test'
                    ENDIF
                    write_rerr=1
                  ENDIF
                  o3[4]='NOHDF' ;Error in Input so do not create HDF file
                END
    qaval EQ 4: infotxt[0]='  DEBUG:'+STRMID(infotxt[0],1)
    ELSE: infotxt[0]='  INFORMATION:'+STRMID(infotxt[0],1)
  ENDCASE
  ;remove '|' from the message
  FOR n=0,dm-1 DO BEGIN
    bspos=STRPOS(infotxt[n],'|')
    IF bspos NE -1 THEN BEGIN
      infotxt[n]=STRMID(infotxt[n],0,bspos)+STRMID(infotxt[n],bspos+1)
    ENDIF
  ENDFOR
ENDELSE

lineno=lineno+dm
FOR n=0,dm-1 DO BEGIN
  IF o3[3] EQ '' THEN WIDGET_CONTROL,wtxt,set_value=infotxt[n],/Append,Set_text_top_line=lineno
  FOR m=dux[0],dux[1],dux[2] DO BEGIN
    IF m EQ -1 THEN PRINT,infotxt[n] ELSE PRINTF,m,infotxt[n] ;write out to log
  ENDFOR
ENDFOR

IF write_rerr EQ 1 THEN BEGIN
  IF rerr[1] EQ '' THEN rerr[1]='Unable to '+endtxt+' -'+STRMID(infotxt[0],8) $
  ELSE rerr[1]=rerr[1]+';'+STRMID(infotxt[0],8)
  IF dm GT 1 THEN FOR n=1,dm-1 DO rerr[1]=rerr[1]+STRMID(infotxt[n],3)
ENDIF

END ;Procedure InfoTxt_Output



FUNCTION jdf_2_datetime, jdf, MJD2000=mjd2000, SHORTISO8601=iso, LONGISO8601=isoms
;Computes the UT date/time from JDF/MJD2000.
; ----------
;   Bojan R. Bojkov
;   bojan.r.bojkov@nasa.gov
;   03/04/2004
;   03/11/2004 bug fix
;   05/27/2005 add ShortISO8601 and LongISO8601 switches,
;              and change seconds value to decimal seconds (Ian Boyd)
;
; References ----------
;   Explan. Supp. Astron. Almanac, p.604 (1992); through E. Celarier
;
; Caveats ----------
;   Valid for all YYYY >= -4712 (i.e. for all JD .ge. 0)
;   The true Gregorian calendar was only adopted on 15 October 1582,
;   so any dates before this are "virtual" Gregorian dates.
;
; Input ----------
;   jdf     : double precision value
;   mjd2000 : flag if input is MJD2000
;   iso     : flag if output is in ISO8601 (YYYYMMDDThhmmssZ)
;   isoms   : flag if output is in ISO8601ms (YYYYMMDDThhmmss.sssZ)
;
; Output ---------
;   floating point array [YYYY, MM, DD, hh, mn, ss.sss],
;   or ISO8601 string format
; External subroutines ---------
;   NONE

jdf=DOUBLE(jdf)

j0=2451544.5D
IF KEYWORD_SET(mjd2000) THEN jdhold=jdf+j0 ELSE jdhold=jdf
jdi=LONG(jdhold)
df=jdhold-jdi

;Determine hh, mm, ss, ms
hh=(df+0.5)*24.D
q=WHERE(hh GE 24.D)
IF q[0] NE -1 THEN BEGIN
  hh[q]=hh[q]-24.D
  jdi[q]=jdi[q]+1
ENDIF
t1=hh
hh=LONG(t1)
t2=(t1-hh)*60.D
mn=LONG(t2)
t3=(t2-mn)*60.D
ss=t3
;ss=LONG(t3)
;ms=LONG((t3-ss)*1.d3)

;Determine YYYY, MM, DD
t1=jdi+68569L
t2=(4*t1)/146097L
t1=t1-(146097L*t2+3L)/4L
t3=(4000L*(t1+1L))/1461001L
t1=t1-(1461L*t3)/4L + 31L
t4=(80L*t1)/2447L

dd=t1-(2447L*t4)/80L
t1=t4/11L
mm=t4+2L-12L*t1
yyyy=100L*(t2-49L)+t3+t1

dt=TRANSPOSE([[yyyy],[mm],[dd],[hh],[mn],[ss]])
IF (KEYWORD_SET(iso)) OR (KEYWORD_SET(isoms)) THEN BEGIN
  dts=STRARR(6)
  IF (KEYWORD_SET(iso)) AND (ss-FIX(ss) GE 0.5) THEN BEGIN
    ;recalculate to get correct seconds value
    jdhold=jdf+0.000008D ;add ~0.7 secs
    IF KEYWORD_SET(mjd2000) THEN jdhold=jdhold+j0
    CALDAT,jdhold,mm,dd,yyyy,hh,mn,ss
    dt=TRANSPOSE([[yyyy],[mm],[dd],[hh],[mn],[ss]])
  ENDIF
  dt=LONG(dt)
  FOR i=1,5 DO $
    IF dt[i] LT 10L THEN dts[i]='0'+STRTRIM(dt[i],2) ELSE dts[i]=STRTRIM(dt[i],2)
  IF KEYWORD_SET(isoms) THEN BEGIN
    ssd=STRING(format='(f6.3)',ss)
    IF FLOAT(ssd) LT 10.0 THEN dts[5]='0'+STRTRIM(ssd,2) ELSE dts[5]=STRTRIM(ssd,2)
  ENDIF
  RETURN,STRTRIM(dt[0],2)+dts[1]+dts[2]+'T'+dts[3]+dts[4]+dts[5]+'Z'
ENDIF ELSE RETURN, dt

END ;Function jdf_2_datetime



FUNCTION julian_date, date_ut, ISO8601=iso, MJD2000=mjd2000
;Computes the Julian date (jd) or date in MJD2000 format in double precision.
; ----------
;   Bojan R. Bojkov
;   bojan.r.bojkov@nasa.gov
;   06/03/2001
;   09/24/2001: Code cleanup                        - Function Version 1.0
;   10/16/2001: Mode corrections                    - Function Version 1.01
;   03/07/2002: Comment cleanup and variable change - Function Version 2.0
;   10/08/2002: Added jdf option                    - Function Version 2.1
;   07/21/2003: Converted to a function             - Function Version 3.0
;   05/25/2005: Added ISO8601 and MJD2000 keywords.
;               Input can either be a string or a numeric array
;               (see below for input details). Returns -99999.d
;               if the Input is invalid - Ian Boyd
;
; References ----------
;   Hughes, D.W., Yallop, B.D. and Hohenkerk, C.Y., "The Equation of Time",
;     Mon. Not. R. astr. Soc., 238, pp 1529-1535. 1989.
;
;   Results verified using:
;     Meeus, J, "Astronomical Algorithms", William-Bell, Inc., Richmond VA,
;     p62, 1991.
;
; Caveats ----------
;   NONE
;
; Input ----------
;   date_ut: Numeric array (UT: YYYY, MM, DD, [hh, mm, ss]), or if ISO8601
;            keyword set, a string containing datetime as YYYYMMDDThhmmssZ
;
; Output ---------
;   jd:      julian day, or if MJD2000 keyword set,
;            a double precision day in MJD2000 format
;
; External subroutines ---------
;   NONE

ON_IOERROR,TypeConversionError
valid=0 ;Type conversion check
inputerror=0 ;Check that input is as expected
;Check input format
IF KEYWORD_SET(iso) THEN BEGIN ;input is YYYYMMDDThhmmssZ
  IF STRLEN(date_ut) EQ 16 THEN BEGIN
    ;test for numeric values (will return type conversion error value if not a number)
    FOR i=0,7 DO check=FIX(STRMID(date_ut,i,1))
    FOR i=9,14 DO check=FIX(STRMID(date_ut,i,1))
    dt=INTARR(6)
    dt[0]=FIX(STRMID(date_ut,0,4)) & dt[1]=FIX(STRMID(date_ut,4,2))
    dt[2]=FIX(STRMID(date_ut,6,2)) & dt[3]=FIX(STRMID(date_ut,9,2))
    dt[4]=FIX(STRMID(date_ut,11,2)) & dt[5]=FIX(STRMID(date_ut,13,2))
    date_ut=dt & achk=[0,6] ;to add hhmmss component
  ENDIF ELSE inputerror=1
ENDIF ELSE BEGIN
  ;check that input contains at least YMD (and at most YMDhms) information and is either
  ;an integer, long, float or double array
  achk=SIZE(date_ut)
  IF (achk[1] LT 3) OR (achk[1] GT 6) OR (achk[2] LT 2) OR (achk[2] GT 5) THEN inputerror=1
ENDELSE

IF inputerror EQ 0 THEN BEGIN ;can perform JD calculation
  IF date_ut[1] GT 2 THEN BEGIN
    y=DOUBLE(date_ut[0])
    m=DOUBLE(date_ut[1]-3)
    d=DOUBLE(date_ut[2])
  ENDIF ELSE BEGIN
    y=DOUBLE(date_ut[0]-1)
    m=DOUBLE(date_ut[1]+9)
    d=DOUBLE(date_ut[2])
  ENDELSE

  ;Compute Julian date:
  j=LONG(365.25D0*(y+4712.D0))+LONG(30.6D0*m+0.5D0)+59.D0+d-0.5D0

  ;Check for Julian or Gregorian calendar:
  IF j LT 2299159.5D0 THEN jd=j $ ;If Julian calendar.
  ELSE BEGIN ;If Gregorian calendar.
    gn=38.D0-LONG(3.D0*LONG(49.D0+y/100.D0)/4.D0)
    jd=j+gn
  ENDELSE

  ;add hhmmss values if present
  CASE 1 OF
    achk[1] EQ 4: jd=jd+DOUBLE(date_ut[3])/24.D ;hh only
    achk[1] EQ 5: jd=jd+(DOUBLE(date_ut[3])*3600.D + DOUBLE(date_ut[4])*60.D)/86400.D ;hhmm only
    achk[1] EQ 6: jd=jd+(DOUBLE(date_ut[3])*3600.D + DOUBLE(date_ut[4])*60.D + $
                         DOUBLE(date_ut[5]))/86400.D ;hhmmss
    ELSE:
  ENDCASE

  valid=1 ;Type conversion OK

  ;Set to MJD2000 if required
  IF KEYWORD_SET(mjd2000) THEN jd=jd-2451544.5D
ENDIF

TypeConversionError:
IF valid EQ 0 THEN RETURN,-99999.D ELSE RETURN, jd

END ;Function Julian_Date



PRO var_units_test, vuvalue, rd, tab_type, var_si_conv, errstate
;Procedure to perform checks on the VAR_UNITS value in the metadata and, based on the VAR_UNITS input,
;calculate and return the VAR_SI_CONVERSION value.
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20061012: Introduced to IDLCR8HDF - Version 2.0
;              (Previously these checks were performed in the Extract_and_Test routine)
;    20080302: var_unit_arr and unit_pre_arr added which hold, respectively, the valid VAR_UNITS and
;              corresponding VAR_SI_CONVERSION values, and the set of UNIT_PREFIXs (previously
;              values from the AVDC TAV file have been used). This has been done so that the
;              routine can be stand-alone (i.e. not dependent on also having to read in a TAV file),
;              and also because the original Envisat table.dat file does not contain the
;              VAR_SI_CONVERSION values. The input parameters have been changed to reflect this: bu
;              and up arrays (previously containing the VAR_UNIT and UNIT_PREFIX values from the TAV
;              file), and nbu and nup (the number of elements in the bu and up arrays) are no longer
;              used. The integer flag tab_type has been added to account for the different handling of
;              some of the VAR_UNIT and VAR_SI_CONVERSION values between AVDC and original Envisat.
;              The STOP_WITH_ERROR routine is no longer called in the event of an error, but an Error
;              State string is returned instead. Bug fixed when testing for a UNIT_PREFIX - previously
;              only the first character of the VAR_UNIT value was checked for a possible UNIT_PREFIX,
;              thus 'deka' (da) was excluded. Bug Fixed when the calculated Power Value of the last
;              base SI unit shown in VAR_SI_CONVERSION is '1', this is now set so that the power value
;              does not appear - Version 3.0
;    20090611: Galileo added to var_unit_arr (AVDC); Last VAR_SI_CONVERSION value for ppmv, ppbv,
;              pptv, and ppv changed to DIMENSIONLESS (was ppv) in var_unit_arr (AVDC);
;              VAR_SI_CONVERSION values for molec changed to 0;1.66054E-24;mol (was 0;1;molec) in
;              var_unit_arr (AVDC); VAR_SI_CONVERSION values for DU changed to 0;4.4615E-4;mol m-2
;              (was 0;2.6867E20;molec m-2) in var_unit_arr; Stop power units being added to
;              DIMENSIONLESS (e.g. for VAR_UNITS=ppmv2); Change EVDC VAR_SI_CONVERSION values in
;              var_unit_arr to match Envisat Metadata Guidelines values - Version 3.01
;    20091117: EVDC VAR_SI_CONVERSION values set to the same as AVDC (only one var_unit_arr set);
;              Fix bug which, in some cases, does not account for repeated units in VAR_UNITS when
;              determining the VAR_SI_CONVERSION (e.g. VAR_UNITS=W m-2 sr-1 m-1); Put VAR_SI_CONVERSION
;              units in power value order; Correctly scale multiple units by the power
;              e.g. W2 = (m2 kg s-3)^2 (previously assumed only a single unit was being scaled);
;              Generate error if third VAR_SI_CONVERSION value is 'DIMENSIONLESS' or 'NONE' but also
;              includes extra values - Version 4.0b1
;    20101001: Set up for GEOMS compliance e.g. DIMENSIONLESS changed to 1; MJD2000 changed to MJD2K;
;              NONE removed - Version 4.0b2
;    20101221: Bug fix - need to correctly account for when units cancel each other out. Was still
;              assigned the value DIMENSIONLESS - Version 4.0b3
;    20110303: Bug fix - when a dimensionless unit includes a power value (e.g. ppmv2), the base unit
;              in VAR_SI_CONVERSION stays as '1'; Add 'dB' to var_unit_arr - Version 4.0b4
;    20110719: Add 'pH' - Version 4.0b5
;
;  Inputs: vuvalue - a string containing the Metadata VAR_UNITS value to be checked (everything
;                    after the '=')
;          rd - integer flag to indicate if VAR_DATA_TYPE is real/double (-1) or not (1). Used to
;               make VAR_SI_CONVERSION values of the same type
;          tab_type - integer flag differentiating between AVDC (0) and original Envisat (1) styles
;
;  Output: var_si_conv - a string containing the VAR_SI_CONVERSION value determined by the program
;                        (returns '' if an error is encountered)
;          errstate - string describing an error state encountered during testing (o/w set to '')
;
;  Called by: CHECK_METADATA
;
;  External Subroutines Called: None

var_unit_arr=['%;0;0.01;1','A;0;1;A','C;0;1;s A','cd;0;1;cd','d;0;86400;s','deg;0;1.74533E-2;rad',$
              'degC;273.15;1;K','1;0;1;1','h;0;3600;s','Hz;0;1;s-1','J;0;1;m2 kg s-2','K;0;1;K',$
              'l;0;1E-3;m3','lm;0;1;cd sr','lx;0;1;cd sr m-2','m;0;1;m','min;0;60;s',$
              'MJD2K;0;86400;s','mol;0;1;mol','molec;0;1.66054E-24;mol','Np;0;1;1',$
              'N;0;1E3;m kg s-2','Pa;0;1;m-1 kg s-2','pH;0;1E-12;m2 kg s-2 A-2','photons;0;1;photons',$
              'ppbv;0;1E-9;1','ppmv;0;1E-6;1','pptv;0;1E-12;1','ppv;0;1;1','psu;0;1;psu',$
              'rad;0;1;rad','s;0;1;s','sr;0;1;sr','V;0;1;m2 kg s-3 A-1','W;0;1;m2 kg s-3','kg;0;1;kg',$
              'DU;0;4.4614E-4;mol m-2','Gal;0;1E-2;m s-2','dB;0;1;1']

unit_pre_arr=['Y;yotta;1E24','Z;zetta;1E21','E;exa;1E18','P;peta;1E15','T;tera;1E12','G;giga;1E9',$
              'M;mega;1E6','k;kilo;1E3','h;hecto;1E2','da;deka;1E1','d;deci;1E-1','c;centi;1E-2',$
              'm;milli;1E-3','u;micro;1E-6','n;nano;1E-9','p;pico;1E-12','f;femto;1E-15',$
              'a;atto;1E-18','z;zepto;1E-21','y;yocto;1E-24']

;Set up text in case an error is found in the input VAR_UNITS value
errtxt=STRARR(2)
IF tab_type EQ 1 THEN errtxt[0]='No match with Table.Dat BASE_UNIT/UNIT_PREFIX values.' $
ELSE errtxt[0]='No match with Table Attribute Values file VAR_UNITS/UNIT_PREFIX values.'
errtxt[1]='Not valid.
errtxt='VAR_UNITS='+vuvalue+': '+errtxt
var_si_conv='' & errstate='' ;initialize outputs

nta=N_ELEMENTS(var_unit_arr)
;extract var_unit_arr/unit_pre_arr sub-values into vu/up arrays
vuhold=STRSPLIT(var_unit_arr[0],';',/Extract) ;test for number of sub-values
nvu=N_ELEMENTS(vuhold) & vu=STRARR(nvu,nta)
FOR j=0,nta-1 DO BEGIN
  vuhold=STRSPLIT(var_unit_arr[j],';',/Extract)
  vu[*,j]=vuhold
ENDFOR
nta=N_ELEMENTS(unit_pre_arr)
vuhold=STRSPLIT(unit_pre_arr[0],';',/Extract) ;test for number of sub-values
nup=N_ELEMENTS(vuhold) & up=STRARR(nup,nta)
FOR j=0,nta-1 DO BEGIN
  vuhold=STRSPLIT(unit_pre_arr[j],';',/Extract)
  up[*,j]=vuhold
ENDFOR

;separate out metadata sub-values into component parts, and set-up holding arrays
vp=STRSPLIT(STRTRIM(vuvalue,2),' ',/Extract) & vpn=N_ELEMENTS(vp)
vpx=STRARR(2,vpn) ;0 holds VAR_UNIT value, 1 holds POWER component
bpx=STRARR(vpn) ;holding string array for base unit
ex=INTARR(vpn)+1 ;holding integer array for power value (defaults to 1)
tm=DBLARR(vpn) ;holding array for scale factor
j=0
WHILE (j LE vpn-1) AND (errstate EQ '') DO BEGIN
  ;test to see if the sub-value is a base unit in the TAV file
  ti=WHERE(vp[j] EQ vu[0,*],tcnt)
  IF tcnt NE 0 THEN vpx[0,j]=vp[j] $ it is a base unit
  ELSE BEGIN ;separate out into unit and power values as required
    vpx[0,j]=STRMID(vp[j],0,1) ;save first character of vp(j)
    stopchk=0
    IF (STRLEN(vp[j]) GE 2) THEN BEGIN
      FOR k=1,STRLEN(vp[j])-1 DO BEGIN
        ah=STRMID(vp[j],k,1)
        test1=(BYTE(ah) GE 65) AND (BYTE(ah) LE 90) ;A-Z
        test2=(BYTE(ah) GE 97) AND (BYTE(ah) LE 122) ;a-z
        IF (test1[0]) OR (test2[0]) THEN BEGIN
          IF stopchk EQ 0 THEN vpx[0,j]=vpx[0,j]+ah ELSE stopchk=2
          ;if stopchk EQ 2 THEN this means that VAR_UNITS is not legal
        ENDIF ELSE IF stopchk EQ 0 THEN BEGIN
          stopchk=1 ;first non-alpha character so check for numeric or '-' character
          test1=(BYTE(ah) EQ 45) OR ((BYTE(ah) GE 49) AND (BYTE(ah) LE 57)) ;- or 1-9
          IF NOT test1[0] THEN stopchk=2 ELSE vpx[1,j]=ah
        ENDIF ELSE IF stopchk EQ 1 THEN BEGIN
          ;need to check for a numeric character only
          test1=(BYTE(ah) GE 48) AND (BYTE(ah) LE 57) ;0-9
          IF NOT test1[0] THEN stopchk=2 ELSE vpx[1,j]=vpx[1,j]+ah
        ENDIF
      ENDFOR
      IF vpx[1,j] NE '' THEN ex[j]=FIX(vpx[1,j])
    ENDIF
    IF stopchk EQ 2 THEN vpx[0,j]=vp[j] ;in the event that the value is not valid, so will create error
    ;Do TAV check on the VAR_UNIT value
    ti=WHERE(vpx[0,j] EQ vu[0,*],tcnt)
  ENDELSE

  IF tcnt NE 0 THEN BEGIN ;VAR_UNIT is a BASE_VALUE
    bemult=(DOUBLE(vu[nvu-2,ti[0]]))^ex[j] & tm[j]=bemult
    bpx[j]=vu[nvu-3,ti[0]]+';'+STRTRIM(STRING(format='(E8.1)',bemult),2)+';'+vu[nvu-1,ti[0]]
  ENDIF ELSE IF vpx[0,j] EQ 'g' THEN BEGIN ;check for VAR_UNIT EQ g (gram) for AVDC style TAV file
    bemult=0.001d^ex[j] & tm[j]=bemult
    bpx[j]='0;'+STRTRIM(STRING(format='(E8.1)',bemult),2)+';kg'
  ENDIF ELSE BEGIN ;separate out vpx value into prefix and base-value and test
    ;check for valid prefix - first check for 'deka' (da)
    pref=STRMID(vpx[0,j],0,2) & bas=STRMID(vpx[0,j],2)
    pi=WHERE(pref EQ up[0,*],pcnt)
    IF pcnt EQ 0 THEN BEGIN ;test for the remaining prefixes
      pref=STRMID(vpx[0,j],0,1) & bas=STRMID(vpx[0,j],1)
      pi=WHERE(pref EQ up[0,*],pcnt)
    ENDIF
    IF pcnt NE 0 THEN BEGIN
      pmult=DOUBLE(up[nup-1,pi[0]])
      ;check for valid base
      ti=WHERE(bas EQ vu[0,*],tcnt)
      IF tcnt NE 0 THEN BEGIN
        bpmult=(DOUBLE(vu[nvu-2,ti[0]])*pmult)^ex[j] & tm[j]=bpmult
        bpx[j]=vu[nvu-3,ti[0]]+';'+STRTRIM(STRING(format='(E8.1)',bpmult),2)+';'+vu[nvu-1,ti[0]]
      ENDIF ELSE IF bas EQ 'g' THEN BEGIN ;check for VAR_UNIT EQ g (gram) for AVDC style TAV file
        bpmult=(pmult*0.001D)^ex[j] & tm[j]=bpmult
        bpx[j]='0;'+STRTRIM(STRING(format='(E8.1)',bpmult),2)+';kg'
      ENDIF ELSE errstate=errtxt[0]
    ENDIF ELSE errstate=errtxt[0]
  ENDELSE
  j=j+1
ENDWHILE

IF errstate EQ '' THEN BEGIN ;No errors detected so continue
  ;Create VAR_SI_CONVERSION value
  tmult=1.0D
  FOR j=0,vpn-1 DO tmult=tmult*tm[j]

  ;reformat the multiplier e.g. 1.000E+003 becomes 1E3
  ;convert to Exponential form if necessary
  IF (tmult EQ 273.15D) OR (tmult MOD 60.D EQ 0.D) OR ((tmult GE 0.01D) AND (tmult LT 1.D2) $
    AND (tmult*1.D4 MOD 1.D2 EQ 0.D)) THEN tmults=STRTRIM(STRUPCASE(tmult),2) $ ;keep the same format
  ELSE tmults=STRTRIM(STRING(format='(E14.6)',tmult),2)

  epos=STRPOS(tmults,'E') & ppos=STRPOS(tmults,'.')
  IF epos NE -1 THEN BEGIN ;remove unnecessary characters after 'E'
    ep=FIX(STRMID(tmults,epos+1)) & epx=STRTRIM(ep,2)
    tmults=STRMID(tmults,0,epos+1)+epx
  ENDIF
  IF ppos NE -1 THEN BEGIN ;remove any trailing zeroes after the decimal place
    IF epos NE -1 THEN ep=STRMID(tmults,ppos+1,epos-(ppos+1)) ELSE ep=STRMID(tmults,ppos+1)
    WHILE STRMID(ep,STRLEN(ep)-1,1) EQ '0' DO ep=STRMID(ep,0,STRLEN(ep)-1)
    IF ep NE '' THEN tmults=STRMID(tmults,0,ppos+1)+ep ELSE tmults=STRMID(tmults,0,ppos)
    IF epos NE -1 THEN tmults=tmults+'E'+epx
  ENDIF

  ;Scale the units by the power e.g. W2 = (m2 kg s-3)^2
  FOR j=0,vpn-1 DO BEGIN
    vsc=STRSPLIT(bpx[j],';',/EXTRACT)
    vspl=STRSPLIT(vsc[2],' ',/EXTRACT,COUNT=vscnt)
    sichk=STRARR(vscnt) & pwchk=sichk
    IF (vpx[1,j] NE '') AND (vpx[1,j] NE '1') AND (vsc[2] NE '1') THEN BEGIN
      bpx[j]=vsc[0]+';'+vsc[1]+';'
      FOR k=0,vscnt-1 DO BEGIN
        ;separate out SI units and power values
        sires=STRSPLIT(vspl[k],'-0123456789',/Extract)
        sichk[k]=sires[0] ;SI Unit
        IF STRLEN(sichk[k]) NE STRLEN(vspl[k]) THEN $
          pwchk[k]=STRMID(vspl[k],STRLEN(sichk[k])) $
        ELSE pwchk[k]='1' ;Power value
        pwm=FIX(pwchk[k])*FIX(vpx[1,j])
        IF k EQ 0 THEN sp='' ELSE sp=' '
        bpx[j]=bpx[j]+sp+sichk[k]+STRTRIM(pwm,2)
      ENDFOR
    ENDIF
  ENDFOR

  ;Put together VAR_SI_CONVERSION
  vsc=STRSPLIT(bpx[0],';',/EXTRACT)
  ;IF vsc[2] EQ '1' THEN vpx[1,0]=''
  var_si_conv=vsc[0]+';'+tmults+';'+vsc[2]
  ;add remaining base units to VAR_SI_CONVERSION
  IF vpn GT 1 THEN $
    FOR j=1,vpn-1 DO BEGIN
      vsc=STRSPLIT(bpx[j],';',/Extract)
      var_si_conv=var_si_conv+' '+vsc[2]
    ENDFOR

  ;check VAR_SI_CONVERSION for repeated SI units e.g. m m-3 becomes m-2
  schk=STRSPLIT(var_si_conv,' ;',/Extract) & scnt=N_ELEMENTS(schk)
  IF scnt GT 3 THEN BEGIN ;more than one SI unit in VAR_SI_CONVERSION
    sichk=STRARR(scnt-2) & pwchk=sichk
    FOR j=0,scnt-3 DO BEGIN ;separate out SI units and power values
      sires=STRSPLIT(schk[j+2],'-0123456789',/Extract)
      sichk[j]=sires[0] ;SI Unit
      IF STRLEN(sichk[j]) NE STRLEN(schk[j+2]) THEN $
        pwchk[j]=STRMID(schk[j+2],STRLEN(sichk[j])) $
      ELSE pwchk[j]='1' ;Power value
    ENDFOR
    j=0 & pwval=0
    WHILE j LT scnt-3 DO BEGIN
      si=WHERE((sichk[j] NE '') AND (sichk[j] EQ sichk[j+1:scnt-3]),sicnt)
      IF sicnt NE 0 THEN BEGIN
        FOR k=0,sicnt-1 DO BEGIN
          si[k]=si[k]+j+1
          pwval=FIX(pwchk[j])+FIX(pwchk[si[k]])
          IF (pwval[0] EQ 0) AND (k EQ sicnt-1) THEN BEGIN
            sichk[j]='' & pwchk[j]=''
          ENDIF ELSE IF (pwval[0] EQ 1) and (k EQ sicnt-1) THEN pwchk[j]='' $
          ELSE pwchk[j]=STRTRIM(pwval[0],2)
          ;make null all the other SI values
          sichk[si[k]]='' & pwchk[si[k]]=''
        ENDFOR
      ENDIF ELSE IF pwchk[j] EQ '1' THEN pwchk[j]=''
      j=j+1
    ENDWHILE
    ;Also do check on the power value of the last SI Unit
    IF pwchk[scnt-3] EQ '1' THEN pwchk[scnt-3]=''

    ;Put units in power value order
    pwhold=pwchk
    oi=WHERE(pwhold EQ '',ocnt)
    IF ocnt NE 0 THEN pwhold[oi]='1'
    pws=SORT(FIX(pwhold))
    sichk=sichk[REVERSE(pws)] & pwchk=pwchk[REVERSE(pws)]

    var_si_conv=schk[0]+';'+schk[1]+';'+sichk[0]+pwchk[0]
    si=WHERE(sichk NE '',sicnt)
    IF sicnt EQ 0 THEN var_si_conv=var_si_conv+'1' $ ;i.e. values cancelled out
    ELSE BEGIN
      FOR j=1,scnt-3 DO BEGIN
        si=WHERE(sichk[0:j-1] NE '',sicnt)
        IF (sichk[j] EQ '') OR (sicnt EQ 0) THEN var_si_conv=var_si_conv+sichk[j]+pwchk[j] $
        ELSE var_si_conv=var_si_conv+' '+sichk[j]+pwchk[j]
      ENDFOR
    ENDELSE

  ENDIF

  IF rd LT 0 THEN BEGIN
    ;VAR_DATA_TYPE is Real or Double so make VAR_SI_CONVERSION values floating point
    tchkh=STRSPLIT(var_si_conv,';',/Extract) & tup=STRUPCASE(tchkh)
    FOR j=0,1 DO BEGIN
      IF STRPOS(tup[j],'.') EQ -1 THEN BEGIN
        IF STRPOS(tup[j],'E') EQ -1 THEN tchkh[j]=tchkh[j]+'.0' $
        ELSE tchkh[j]=STRMID(tup[j],0,STRPOS(tup[j],'E'))+'.0'+STRMID(tup[j],STRPOS(tup[j],'E'))
      ENDIF
    ENDFOR
    var_si_conv=tchkh[0]+';'+tchkh[1]+';'+tchkh[2]
  ENDIF

  ;Check for invalid VAR_UNITS - third VAR_SI_CONVERSION is 1 plus extra values
  vsc=STRSPLIT(var_si_conv,';',/EXTRACT)
  vsc[2]=STRTRIM(vsc[2],2)
  IF (errstate EQ '') AND (STRMID(vsc[2],0,1) EQ '1') AND (STRLEN(vsc[2]) GT 1) THEN BEGIN
      errstate=errtxt[1] & var_si_conv=''
  ENDIF
ENDIF

END ;procedure Var_Units_Test



PRO read_tablefile, tablefile
;Procedure to identify the version number of the TAV file, read the contents of the
;LABELS/FIELDS (tab_arr), and determine the FILE_META_VERSION in the global attributes (tab_ver).
;This routine also creates a flag (tab_type) to determine whether the input file is an original
;table.dat file used by Envisat or the GEOMS TAV file, with the HDF/netCDF file generated
;accordingly.
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;History:
;  20050802: Original IDLCR8HDF Routine - Version 1.0
;  20061012: Bug-fix to separate semi-colons with a space when one immediately follows the other,
;            so that the number of subvalues is correctly determined by the program. Common
;            variable definition WIDGET_WIN added - Version 2.0
;  20080302: Added code to differentiate between the AVDC TAV file and original Envisat table.dat.
;            The tab_type flag is used to differentiate between the two formats. Note that some of the
;            table.dat labels are renamed to match the equivalent TAV file labels for compatibility
;            when testing Metadata entries - refer to EnviName/AVDCName arrays; Ensure that the TAV
;            Version value is correctly formatted and is version 03 or greater - Version 3.0
;  20100205: Add RETURN command after all STOP_WITH_ERROR calls, which allows program to return to the
;            calling program if the reterr argument is included in the idlcr8hdf call - Version 3.09
;  20110401: Change AVDC references to GEOMS; Test AVDC TAV file version is version 04 or greater;
;            Remove check on format of TAV file version; Conform to new INFOTXT_OUTPUT reporting
;            - Version 4.0b1
;
;Input: Tablefile - Name of the file containing the Table Attributes.
;
;Outputs: tab_ver - String containing FILE_META_VERSION value.
;         tab_arr - 2-D string array of size nf*mcnt+2, where nf=Number of Fields, and mcnt=maximum
;                   number of values detected in any one field. tab_arr(*,0) is the name of each field,
;                   and tab_arr(*,1) is the number of values in each field.
;         tab_type - 0/1 where 0 identifies an AVDC format TAV file and 1 identifies an original
;                    Envisat format table.dat file.
;
;Called by: IDLCR8HDF
;
;Subroutines Called: STOP_WITH_ERROR (if error state detected); INFOTXT_OUTPUT
;  Possible Conditions for STOP_WITH_ERROR call (plus [line number] where called):
;    1. Table Attribute Values file version not identified
;    2. Envisat table.dat ASC2HDF program version not found
;    3. First Envisat table.dat field value not found
;    4. Table Attribute Values file version is not in a valid format
;
;  Information Conditions (when the program reports issues and continues):
;    1. [Original EVDC]/[GEOMS] Reporting Guidelines Apply (depending on type of Table Attribute
;       Values file read in)
;    2. Old version of the TAV file in use. Update from http://avdc.gsfc.nasa.gov/Tools

COMMON TABLEDATA
COMMON WIDGET_WIN

;Possible error messages for this procedure
proname='Read_TableFile procedure: '
errtxt=STRARR(4)
errtxt[0]='Table Attribute Values file version not identified'
errtxt[1]='Envisat table.dat ASC2HDF program version not found'
errtxt[2]='First Envisat table.dat field value not found'
errtxt[3]='Table Attribute Values file version is invalid (should be ddRddd or ddRdddd): '
FOR i=0,2 do errtxt[i]=errtxt[i]+' with the search criteria used by this program'

;Array of Envisat Field names to be changed to equivalent AVDC Field names
enviname=['_NAME','_AFFILIATION','DATA_VARIABLES_00_00','BASE_UNIT']
avdcname=['ORIGINATOR','AFFILIATION','DATA_VAR_ALL_00_00','VAR_UNITS']

ON_IOERROR,TypeConversionError
dum='' & tab_ver=''
min_fmv=4 ;TAV Version must be GE this value e.g. 04R001, 06R002 but not 03R004
OPENR,lu,tablefile,/GET_LUN
;determine TAV file version
REPEAT BEGIN
  READF,lu,dum
  dumup=STRUPCASE(dum)
  envitest=STRPOS(STRCOMPRESS(dumup,/Remove_all),'!TABLE.DATVERSION') NE -1
  avdctest=STRPOS(STRCOMPRESS(dumup,/Remove_all),'!VERSION') NE -1
ENDREP UNTIL (envitest) OR (avdctest) OR (EOF(lu))
IF EOF(lu) THEN BEGIN
  STOP_WITH_ERROR,o3[3]+proname,errtxt[0],lu & RETURN
ENDIF
res=STRSPLIT(dumup,' ',/Extract) & vi=WHERE(res EQ 'VERSION')
IF N_ELEMENTS(res) LE vi[0]+1 THEN BEGIN
  STOP_WITH_ERROR,o3[3]+proname,errtxt[0]+': '+dum,lu & RETURN
ENDIF
IF envitest THEN BEGIN
  tab_type=1 & infotxt='0 EVDC original style table.dat'
  n_title=4
ENDIF ELSE BEGIN
  tab_type=0 & infotxt='0 GEOMS compliant Table Attribute Values'
  n_title=5
ENDELSE
infotxt=infotxt+' file input. '+STRMID(infotxt,2,n_title)+' Reporting Guidelines apply'
INFOTXT_OUTPUT,infotxt

;Ensure Meta Version has a valid format
;i. Check third character is an 'R'
;ii. Check number of characters is 6 or 7
;iii. Check dd and ddd(d) are numeric
;iv. Check that version number is 03 or greater for AVDC file type
;v. Issue warning and convert to ddRddd if format is ddRdddd
fmv=res[vi[0]+1] ;File_Meta_Version
valid=0 ;set to test for valid string to number conversion
FOR i=0,STRLEN(fmv)-1 DO IF i NE 2 THEN fmvtest=FIX(STRMID(fmv,i,1))
fmvtest=FIX(STRMID(fmv,0,2)) ;To test for TAV version 'min_fmv' or greater
valid=1 ;FILE_META_VERSION characters are numeric (except for the 'R') if program gets to here
TypeConversionError:
IF (STRMID(fmv,2,1) NE 'R') OR (STRLEN(fmv) lt 6) OR (STRLEN(fmv) gt 7) OR $
   (valid EQ 0) THEN BEGIN
  STOP_WITH_ERROR,o3[3]+proname,errtxt[3]+fmv,lu & RETURN
ENDIF

IF (tab_type EQ 0) AND (fmvtest LT min_fmv) THEN BEGIN
  infotxt=STRARR(2)
  infotxt[0]='3 Old version of the Table Attribute Values file used as input: '
  infotxt[0]=infotxt[0]+' TAV Version '+fmv
  infotxt[1]='    Please update from http://avdc.gsfc.nasa.gov/Tools'
  INFOTXT_OUTPUT,infotxt
ENDIF

IF envitest THEN BEGIN ;identify asc2hdf version in table.dat and read past the CHECK_ATTRIBUTE line
  WHILE (STRPOS(STRUPCASE(dum),'ASC2HDF') EQ -1) AND (NOT EOF(lu)) DO READF,lu,dum
  IF EOF(lu) THEN BEGIN
    STOP_WITH_ERROR,o3[3]+proname,errtxt[1],lu & RETURN
  ENDIF
  cr8_hdf_ver=';IDLCR8HDF'
  dum=STRTRIM(dum,2)
  WHILE ((STRMID(dum,0,1) EQ '!') OR (STRMID(dum,0,1) EQ '#') OR (dum EQ '')) AND $
        (NOT EOF(lu)) DO BEGIN
    READF,lu,dum & dum=STRTRIM(dum,2)
  ENDWHILE
  IF EOF(lu) THEN BEGIN
    STOP_WITH_ERROR,o3[3]+proname,errtxt[2],lu & RETURN
  ENDIF
  READF,lu,dum ;to get to the line after 'CHECK_ATTRIBUTE'
ENDIF ELSE cr8_hdf_ver=';IDLCR8HDF'
tab_ver=fmv+cr8_hdf_ver ;= the FILE_META_VERSION input value in the global attributes

;determine no. of FIELDS/LABELS as well as the maximum number of elements
nf=0 & mcnt=0 & firstfield=''
dum=STRTRIM(dum,2)
WHILE NOT EOF(lu) DO BEGIN
  ncnt=-1
  IF (STRMID(dum,0,1) NE '!') AND (STRMID(dum,0,1) NE '#') AND $
     (STRMID(dum,0,1) NE '=') AND (dum NE '') THEN BEGIN

    FOR i=0,N_ELEMENTS(enviname)-1 DO BEGIN
      epos=STRPOS(STRUPCASE(dum),enviname[i])
      IF (epos NE -1) AND (epos LE 3) THEN ncnt=i
    ENDFOR
    IF (ncnt EQ 0) OR (ncnt EQ 1) THEN BEGIN
      IF STRMID(STRUPCASE(dum),0,3) NE 'PI_' THEN nf=nf-1 ELSE ecnt=0
      ;This puts all PI_,DO_, and DS_NAME or AFFILIATION values into either the ORIGINATOR or AFFILIATION fields
    ENDIF ELSE ecnt=0

    nf=nf+1
    IF firstfield EQ '' THEN firstfield=dum
    IF ncnt NE -1 THEN dum=avdcname[ncnt] ;change the name of the Envisat field to AVDC equivalent
    REPEAT BEGIN
      READF,lu,dum & dum=STRTRIM(dum,2)
      IF STRMID(dum,0,1) EQ '=' THEN ecnt=ecnt+1
    ENDREP UNTIL (STRMID(dum,0,1) NE '=') OR (EOF(lu))
    IF ecnt GT mcnt THEN mcnt=ecnt
  ENDIF ELSE IF NOT EOF(lu) THEN BEGIN
    READF,lu,dum & dum=STRTRIM(dum,2)
  ENDIF
ENDWHILE
FREE_LUN,lu

;read in the contents of the file
tab_arr=STRARR(nf,mcnt+2) ;note tab_arr(*,0) EQ FIELD/LABEL name and
;tab_arr(*,1) EQ N_ELEMENTS under each FIELD/LABEL
tab_hold=STRARR(mcnt)

OPENR,lu,tablefile,/GET_LUN
READF,lu,dum & dum=STRTRIM(dum,2)
WHILE dum NE firstfield DO BEGIN
  READF,lu,dum & dum=STRTRIM(dum,2)
ENDWHILE

i=0
WHILE i LE nf-1 DO BEGIN
  ncnt=-1
  FOR j=0,N_ELEMENTS(enviname)-1 DO BEGIN
    epos=STRPOS(STRUPCASE(dum),enviname[j])
    IF (epos NE -1) AND (epos LE 3) THEN ncnt=j
  ENDFOR
  IF (ncnt EQ 0) OR (ncnt EQ 1) THEN BEGIN
    IF STRMID(STRUPCASE(dum),0,3) NE 'PI_' THEN i=i-1 ELSE ecnt=0
  ENDIF ELSE ecnt=0
  IF ncnt NE -1 THEN dum=avdcname[ncnt] ;change the name of the Envisat field to AVDC equivalent
  tab_arr[i,0]=dum
  REPEAT BEGIN
    READF,lu,dum & dum=STRTRIM(dum,2)
    IF STRMID(dum,0,1) EQ '=' THEN BEGIN
      tab_hold[ecnt]=STRMID(dum,1) ;strip the '=' sign
      ;add space between adjacent semi-colons so StrSplit finds correct number of sub-values
      REPEAT BEGIN
        cpos=STRPOS(tab_hold[ecnt],';;')
        IF cpos NE -1 THEN tab_hold[ecnt]=STRMID(tab_hold[ecnt],0,cpos+1)+ $
          ' '+STRMID(tab_hold[ecnt],cpos+1)
      ENDREP UNTIL cpos EQ -1
      ecnt=ecnt+1
    ENDIF
  ENDREP UNTIL (STRMID(dum,0,1) NE '=') OR (EOF(lu))
  tab_arr[i,1]=STRTRIM(ecnt,2)
  tab_arr[i,2:ecnt+1]=tab_hold[0:ecnt-1]
  IF i NE nf-1 THEN BEGIN
    WHILE (STRMID(dum,0,1) EQ '!') OR (STRMID(dum,0,1) EQ '#') OR (dum EQ '') DO BEGIN
      READF,lu,dum & dum=STRTRIM(dum,2)
    ENDWHILE
  ENDIF
  i=i+1
ENDWHILE
FREE_LUN,lu

END ;Procedure Read_TableFile



PRO test_file_input,aname,fentry
;Procedure to test that a file name given as an entry to a free text attribute is valid, based on Envisat
;Metadata Guidelines (not currently used by AVDC). Note: No longer permitted under GEOMS guidelines.
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20050802: Original IDLCR8HDF Routine - Version 1.0
;    20061012: Common variable definition WIDGET_WIN added - Version 2.0
;    20100205: Add RETURN command after all STOP_WITH_ERROR calls, which allows program to return to the
;              calling program if the reterr argument is included in the idlcr8hdf call - Version 3.09
;
;  Inputs: aname - Global or Variable Attribute Label
;          fentry - Filename entry used as the Global or Variable Attribute value
;
;  Outputs: None
;
;  Called by: READ_METADATA
;
;  Subroutines Called: STOP_WITH_ERROR (if error state detected)
;    Possible Conditions for STOP_WITH_ERROR call (plus [line number] where called):
;      1. Syntax of Filename entry incorrect
;      2. Filename entry not found or not usable
;      3. File size is too large

COMMON WIDGET_WIN

sfile=4096 ;maximum permitted file size

;possible error message for this procedure
proname='Test_File_Input procedure: '
errtxt2=STRARR(3) & lu=-1
errtxt2[0]='Syntax of Filename entry incorrect: '
errtxt2[1]='Filename entry not found or not usable: '
errtxt2[2]='File size is too large (maximum permitted: '+STRTRIM(sfile,2)+' bytes)'

si=STRPOS(fentry,'"')+1 & ei=STRPOS(fentry,'"',/Reverse_Search)-si
IF ei EQ si THEN BEGIN
  STOP_WITH_ERROR,o3[3]+proname+aname+': ',errtxt2[0]+fentry,lu & RETURN
ENDIF
faname=STRMID(fentry,si,ei)
ftest=FILE_TEST(faname,/Read,/Regular)
IF ftest EQ 0 THEN BEGIN
  STOP_WITH_ERROR,o3[3]+proname+aname+': ',errtxt2[1]+faname,lu & RETURN
ENDIF
OPENR,fu,faname,/GET_LUN
ftest=FSTAT(fu) & FREE_LUN,fu
IF ftest.size GT sfile THEN BEGIN
  STOP_WITH_ERROR,o3[3]+proname+AName+'='+fentry+': ',errtxt2[2],lu & RETURN
ENDIF

END ;procedure Test_File_Input



PRO geoms_rule_changes, code, in1, in2, in3, in4
;Procedure to check Metadata for old/redundant rules, labels and/or values and update/report
;as required
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20110401: Introduced. Incorporates GEOMS rules changes from v3.0 to v4.0 - Version 4.01
;    20111220: Add ISO646-US ASCII character set check - Version 4.0b7
;    20120313: Add UVVIS.DOAS plus additional gases to Code 6 checks - Version 4.0b8
;    20120703: Bug Fix when checking for non-ASCII characters (rule 10) - Version 4.0b11
;    20131023: Add GEOMS rule change for MIXING.RATIO[.VOLUME][.MASS], and UNCERTAINTY (rule 5);
;              Fixed bug that caused incorrect rep_list_2 values to be written to file (rule 5);
;              Stopped checks for illegal characters if ORIGINATOR values are present in the 
;              TAV file (rule 10) - Version 4.0b16
;
;  Inputs: code - Integer value identifying type of check to carry out
;          in1 - First set of inputs required for checks (optional, dependent on code value)
;          in2 - Second set of inputs required for checks (optional, dependent on code value)
;          in3 - Third set of inputs required for checks (optional, dependent on code value)
;          in4 - Fourth set of inputs required for checks (optional, dependent on code value)
;
;  Outputs: Any or all of the inputs can be changed dependent on the code value
;
;  Called by: READ_METADATA; CHECK_METADATA; SET_UP_STRUCTURE; FIND_HDF_FILENAME
;
;  Subroutines Called: INFOTXT_OUTPUT
;    Information Conditions (when the program is able to make changes):
;      1. Attribute entry is not GEOMS compliant, and removed from the metadata saved to the output file
;      2. Dataset name renamed according to new DATETIME reporting conventions
;      3. Double underscore replaced with a single underscore in the variable name
;      4. VAR_DEPEND value made self-referencing for axis variable
;      5. Axis variable cannot be dependent on another variable
;      6. VAR_UNITS=MJD2000 not GEOMS compliant, changed to VAR_UNITS=MJD2K
;      7. DATA_FILE_VERSION must be in the form 'nnn'
;      8. Obsolete Dataset name renamed
;      9. Obsolete DATA_SOURCE value renamed
;     10. Obsolete FILE_ACCESS values renamed
;     11. Rename obsolete VAR_UNITS=DIMENSIONLESS/NONE values
;     12. DATA_TEMPLATE field is not present in the TAV file
;     13. DATA_TEMPLATE value renamed based on DATA_SOURCE value
;     14. Entry must only include valid characters from the ISO646-US ASCII character set
;
;  Code 0: Check for Attributes that have become redundant between v3.0 and v4.0.
;          Inputs: in1=mh, in2=mhgood
;  Code 1: Check for redundant _START/STOP/INTEGRATION.TIME variable names and replace with
;          DATETIME.START/STOP/INTEGRATION.TIME (for single occurences only). Also check
;          for double underscores in the variable names and replace with single underscore
;          Inputs: in1=vncnt, in2=dv
;  Code 2: Check for Axis Variables and, if found, make VAR_DEPEND=INDEPENDENT self-referencing
;          Inputs: in1=vardeptest, in2=vn[vc], in3=resvd[1], in4=holdvd
;  Code 3: Change VAR_UNIT value MJD2000 to MJD2K
;          Inputs: in1=meta_arr[i], in2=res[1], in3=writeonce
;  Code 4: Do DATA_FILE_VERSION checks
;          Inputs: in1=dfvv (DATA_FILE_VERSION value)
;  Code 5: Look for obsolete DATA_VARIABLES (based on list) and, if possible, modify values to
;          GEOMS compliance
;          Inputs: in1=vncnt, in2=dv, in3=vuv, in4=data_source
;  Code 6: Look for obsolete DATA_SOURCE (based on list) and, if possible, modify values to
;          GEOMS compliance
;          Inputs: in1=vncnt, in2=dv, in3=data_source
;  Code 7: Looks for and replaces obsolete CALVAL and NDSC FILE_ACCESS values
;          Inputs: in1=facnt, in2=fav
;  Code 8: Looks for VAR_UNITS=DIMENSIONLESS or NONE and replace with '' or '1'
;          Inputs: in1=vucnt, in2=vuv, in3=vdv
;  Code 9: Do DATA_TEMPLATE/DATA_QUALITY checks
;          Inputs: in1=m_v0, in2=m_v1, in3=ga_chk
;  Code 10: Do checks on ISO646-US ASCII character set
;           Inputs: in1=meta_arr or dtest, in2=vn[vc] (Variable Name for datasets only)

COMMON TABLEDATA
COMMON METADATA
COMMON DATA
COMMON WIDGET_WIN

CASE 1 OF
  code EQ 0: BEGIN
      ;Check for redundant attributes
      redundant=['DATA_TYPE','DATA_LEVEL','VAR_MONOTONE','VAR_DIMENSION',$
                 'VAR_AVG_TYPE','VIS_LABEL','VIS_FORMAT','VIS_PLOT_TYPE',$
                 'VIS_SCALE_TYPE','VIS_SCALE_MIN','VIS_SCALE_MAX']
      nrd=N_ELEMENTS(redundant)

      FOR i=0,nrd-1 DO BEGIN
        rdl=STRLEN(redundant[i])
        fai=WHERE(STRMID(STRUPCASE(in1),0,rdl) EQ redundant[i],facnt)
        IF facnt NE 0 THEN BEGIN
          in2[fai]=0 ;Metadata lines not wanted
          test1=(STRMID(redundant[i],0,3) EQ 'VAR') OR (STRMID(redundant[i],0,3) EQ 'VIS')
          IF test1 THEN att_type='Variable' ELSE att_type='Global'
          infotxt='1 '+redundant[i]+' not a GEOMS '+att_type+' attribute|.'
          infotxt=infotxt+' Removed from the metadata saved to the output file'
          INFOTXT_OUTPUT, infotxt
        ENDIF
      ENDFOR
    END ;Case 0

  code EQ 1: BEGIN
      ;Check for redundant _START/STOP sub-values and replace with
      ;DATETIME.START/STOP/INTEGRATION.TIME (for single occurences only)
      time_attr=['START','STOP','INTEGRATION','RESOLUTION']
      n_tim=N_ELEMENTS(time_attr)
      iscnt=0 ;Used for RESOLUTION/INTEGRATION.TIME checks
      FOR i=0,n_tim-1 DO BEGIN
        si=WHERE(STRPOS(in2,'_'+time_attr[i]+'.TIME') NE -1,scnt)
        IF (scnt EQ 1) AND (iscnt EQ 0) THEN BEGIN ;change name and also relevant VAR_NAME if present
          IF i EQ 2 THEN iscnt=1 ;used in the event both INTEGRATION and REOLUTION.TIME are present
          vnchange[si[0]]=in2[si[0]]
          IF i GE 2 THEN in2[si[0]]=time_attr[2]+'.TIME' $
          ELSE in2[si[0]]='DATETIME.'+time_attr[i]
          IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN itxt=' expected to be ' $
          ELSE itxt=' renamed '
          infotxt='2 Dataset name '+vnchange[si[0]]+itxt+in2[si[0]]
          INFOTXT_OUTPUT,infotxt
        ENDIF
      ENDFOR
      ;Check for double underscore and replace with single underscore
      FOR i=0,in1-1 DO BEGIN
        IF STRPOS(in2[i],'__') NE -1 THEN BEGIN
          vnchange[i]=in2[i]
          infotxt=STRARR(2)
          infotxt[0]='2 Double underscore present in Variable Name '+in2[i]+'|'
          infotxt[1]='    replaced with a single underscore'
          INFOTXT_OUTPUT, infotxt
          vns=STRSPLIT(in2[i],'_',/Extract,COUNT=n_vns)
          FOR j=0,n_vns-1 DO IF j EQ 0 THEN in2[i]=vns[j] ELSE in2[i]=in2[i]+'_'+vns[j]
        ENDIF
      ENDFOR
    END ;Case 1

  code EQ 2: BEGIN ;Check for and Apply GEOMS rule changes for INDEPENDENT and axis variables
      ;RULE: Any variable that is mentioned in a VAR_DEPENDS is by definition an axis variable
      vdtest=STRUPCASE(in1) & vnv=STRUPCASE(in2) & vdv=STRUPCASE(in3) ;vdtest is an array of VAR_DEPEND variables
      avi=WHERE(vnv EQ vdtest,avcnt) ;i.e. is the VAR_NAME an axis variable
      IF avcnt NE 0 THEN BEGIN ;possible axis variable so do axis variable checks
        test1=(vdv EQ 'INDEPENDENT') OR (vdv EQ vnv) ;value is independent or self-referencing
        test2=(vdv NE 'INDEPENDENT') AND (vdv NE vnv) AND (vdv NE 'CONSTANT') ;neither independent, self-referencing, nor constant
        test6=(vdv EQ 'CONSTANT') AND (vnv EQ 'DATETIME') ;i.e. VAR_NAME=DATETIME and VAR_DEPEND=CONSTANT
        IF (test1) OR (test6) THEN BEGIN
          IF vdv NE vnv THEN BEGIN
            infotxt='2 '+in4+' should be self-referencing for axis variable VAR_NAME='+vnv+'|.'
            infotxt=infotxt+' VAR_DEPEND value changed in metadata'
            INFOTXT_OUTPUT,infotxt
            in3=vnv ;self-referencing VAR_DEPEND value
          ENDIF
        ENDIF ELSE IF test2 THEN BEGIN
          in4[0]='E1' ;i.e. axis variable cannot be dependent on another variable so return error
        ENDIF
      ENDIF ELSE BEGIN ;not an axis variable so ensure VAR_DEPEND value is not self-referencing
        IF vdv EQ vnv THEN in4[0]='E3' ;i.e. VAR_DEPEND value cannot be self-referencing
      ENDELSE
    END ;Case 2

  code EQ 3: BEGIN ;Change MJD2000 to MJD2K
      in1='VAR_UNITS=MJD2K' & in2='MJD2K'
      IF in3 EQ 0 THEN BEGIN ;First instance of MJD2000 so include comment
        infotxt='2 VAR_UNITS=MJD2000 not GEOMS compliant|. Changed to VAR_UNITS=MJD2K'
        INFOTXT_OUTPUT,infotxt
      ENDIF
    END

  code EQ 4: BEGIN ;checks on DATA_FILE_VERSION
      in1=STRTRIM(in1,2)
      vp=0 & errval=0 & in1h=in1
      ON_IOERROR,TypeConversionError
      IF STRMID(STRUPCASE(in1),0,1) EQ 'V' THEN BEGIN
        vp=1 & in1=STRMID(in1,1)
      ENDIF
      dpos=STRPOS(in1,'.')
      valid=0 ;to check for conversion error
      IF  dpos NE -1 THEN BEGIN
        IF LONG(STRMID(in1,dpos+1)) EQ 0L THEN atxt='' ELSE atxt=STRMID(in1,dpos+1)
        in1=STRMID(in1,0,dpos)+atxt
        IF FIX(in1) GE 100 THEN in1=STRMID(in1,0,dpos) ;just use version up to the decimal point
      ENDIF
      IF (FIX(in1) GT 999) OR (FIX(in1) LT 1) THEN errval=1
      valid=1 ;OK if got to here

      TypeConversionError: ;Check for invalid DATA_FILE_VERSION value
      IF (valid EQ 0) OR (errval EQ 1) THEN BEGIN
        infotxt='3 DATA_FILE_VERSION='+in1h+' must be in the form ''nnn'''
        INFOTXT_OUTPUT, infotxt
        in1=in1h
      ENDIF ELSE BEGIN ;format value correctly (nnn)
        IF FIX(in1) LT 10 THEN in1='00'+STRTRIM(FIX(in1),2) $
        ELSE IF FIX(in1) LT 100 THEN in1='0'+STRTRIM(FIX(in1),2) $
        ELSE in1=STRTRIM(in1,2)
        IF (vp EQ 1) OR (in1h NE in1) THEN BEGIN
          infotxt='2 DATA_FILE_VERSION must be in the form ''nnn''|. Renamed from '
          infotxt=infotxt+in1h+' to '+in1
          INFOTXT_OUTPUT, infotxt
        ENDIF
      ENDELSE
    END

  code EQ 5: BEGIN ;Look for obsolete DATA_VARIABLES
      ;Notes = what to do about ALTITUDE.LAYER.INDEX, CHL.A.CONCENTRATION,
      ;        PRESSURE.LEVEL.INDEX (still in 04R001), TSM.CONCENTRATION
      ;List of obsolete DATA_VARIABLE_01 values
      obs_list_1=['AIR.TEMPERATURE','TEMPERATURE.AIR','COLUMN.VERTICAL','H2O.RELATIVE.HUMIDITY',$
                  'PRESSURE.SURFACE','TEMPERATURE.SURFACE','TEMPERATURE.INTERNAL.BOX',$
                  'TEMPERATURE.INTERNAL.INSTRUMENT','TEMPERATURE.SEA.SURFACE','AIR.NUMBER.DENSITY',$
                  'SEA.SURFACE.TEMPERATURE','OPACITY.ATMOSPHERIC.VERTICAL']
      ;Corresponding list of replacement DATA_VARIABLE_1 values (direct replacement)
      rep_list_1=['TEMPERATURE','TEMPERATURE','COLUMN','HUMIDITY.RELATIVE',$
                  'SURFACE.PRESSURE','SURFACE.TEMPERATURE','INTERNAL.BOX.TEMPERATURE',$
                  'INTERNAL.INSTRUMENT.TEMPERATURE','SEA.SURFACE.TEMPERATURE','NUMBER.DENSITY',$
                  'SEA.SURFACE.TEMPERATURE.SKIN','OPACITY.ATMOSPHERIC']
      ;Obsolete DATA_VARIABLE_01 which need special handling
      obs_list_spec_1=['.AMF','.AVK','.CONCENTRATION','.MIXING.RATIO']
      ;Obsolete DATA_VARIABLE_02 values
      obs_list_2=['SOLAR','VERTICAL.SOLAR',$
                  'EMISSION.VERTICAL','VERTICAL.EMISSION',$
                  'VERTICAL','SLANT','SOLAR.OCCULTATION','VERTICAL.ZENITH','VERTICAL.NADIR',$
                  'VERTICAL.LUNAR','VERTICAL.SOLAR.FOCUS']
      ;[0,1] for FTIR/UVVIS (except Brewer and Dobson) only, [2,3] for MWR only
      ;Corresponding list of replacement DATA_VARIABLE_2 values (direct replacement)
      rep_list_2=['ABSORPTION.SOLAR|SCATTER.SOLAR','ABSORPTION.SOLAR|SCATTER.SOLAR',$
                  'EMISSION','EMISSION',$
                  '','','OCCULTATION.SOLAR','ZENITH','NADIR',$
                  'ABSORPTION.LUNAR','ABSORPTION.SOLAR.FOCUS']
      ;Replacements for .CONCENTRATION - dependent on VAR_UNITS
      rep_list_conc=['.MIXING.RATIO.VOLUME','.MIXING.RATIO.MASS','.NUMBER.DENSITY','.PARTIAL.PRESSURE']
      ;Conditional Miscellaneous changes
      misc_list_1=['TEMPERATURE_SKIN','AIR.MASS.FACTOR']
      ;Corresponding change to miscellaneous variables
      misc_list_2=['SEA.SURFACE.TEMPERATURE.SKIN','O3.COLUMN_AMF']
      ;Obsolete DATA_VARIABLE_03 descriptors (may or may not be able to fix these)
      obs_list_3=['UNCERTAINTY.STDEV','UNCERTAINTY.TOTAL','UNCERTAINTY.RANDOM','UNCERTAINTY.SYSTEMATIC']
      ;Corresponding list of replacement DATA_VARIABLE_03 descriptors
      rep_list_3=['UNCERTAINTY.COMBINED.STANDARD','UNCERTAINTY.COMBINED.STANDARD',$
                  'UNCERTAINTY.RANDOM.STANDARD','UNCERTAINTY.SYSTEMATIC.STANDARD']
      vn_v=STRARR(in1,3) & vn_new=STRARR(in1)
      ;Separate out Variable Name/[Mode or Descriptor]/[Descriptor]
      FOR i=0,in1-1 DO BEGIN
        res=STRSPLIT(in2[i],'_',/EXTRACT,COUNT=nres)
        IF nres LE 3 THEN FOR j=0,nres-1 DO vn_v[i,j]=res[j]
      ENDFOR
      ;Test for values in obs_list_1
      FOR i=0,N_ELEMENTS(obs_list_1)-1 DO BEGIN
        ri=WHERE(STRPOS(STRUPCASE(vn_v[*,0]),obs_list_1[i]) NE -1,rcnt)
        IF rcnt NE 0 THEN BEGIN ;obsolete values found so replace
          vlen=STRLEN(obs_list_1[i])
          FOR j=0,rcnt-1 DO BEGIN
            change_val=1
            ;Special case for SEA.SURFACE.TEMPERATURE (only change if mode is _SKIN)
            IF obs_list_1[i] EQ 'SEA.SURFACE.TEMPERATURE' THEN BEGIN
              IF STRUPCASE(vn_v[ri[j],1]) EQ 'SKIN' THEN vn_v[ri[j],1]='' ELSE change_val=0
            ENDIF
            IF change_val EQ 1 THEN BEGIN
              vpos=STRPOS(STRUPCASE(vn_v[ri[j],0]),obs_list_1[i])
              vn_v[ri[j],0]=STRMID(vn_v[ri[j],0],0,vpos)+rep_list_1[i]+STRMID(vn_v[ri[j],0],vpos+vlen)
            ENDIF
          ENDFOR
        ENDIF
      ENDFOR
      ;Special cases for DATA_VARIABLE_01 values .AMF, .AVK, .CONCENTRATION, and .MIXING.RATIO
      nols1=N_ELEMENTS(obs_list_spec_1)
      FOR i=0,nols1-1 DO BEGIN
        ri=WHERE(STRPOS(STRUPCASE(vn_v[*,0]),obs_list_spec_1[i]) NE -1,rcnt)
        IF (i EQ nols1-1) AND (rcnt NE 0) THEN BEGIN 
          ;do check for .MIXING.RATIO. in which case no correction required
          rxi=WHERE(STRPOS(STRUPCASE(vn_v[ri,0]),'.MIXING.RATIO.') EQ -1,rxcnt)
          IF rxcnt NE 0 THEN BEGIN ;some values are just .MIXING.RATIO so correct these only
            rcnt=rxcnt & ri=ri[rxi]
          ENDIF ELSE rcnt=0
        ENDIF
        IF rcnt NE 0 THEN BEGIN ;obsolete values found
          vlen=STRLEN(obs_list_spec_1[i])
          IF i LE 1 THEN BEGIN ;move .AMF and .AVK to DESCRIPTOR section (2 or 3)
            FOR j=0,rcnt-1 DO BEGIN
              vpos=STRPOS(STRUPCASE(vn_v[ri[j],0]),obs_list_spec_1[i])
              ai=WHERE(vn_v[ri[j],*] EQ '',acnt)
              IF acnt NE 0 THEN BEGIN
                ;the DESCRIPTOR field is empty, so can convert value OK (otherwise no change made)
                vn_v[ri[j],0]=STRMID(vn_v[ri[j],0],0,vpos)
                vn_v[ri[j],ai[0]]=STRMID(obs_list_spec_1[i],1) ;write to first empty field
              ENDIF
            ENDFOR
          ENDIF ELSE BEGIN
            ;.CONCENTRATION or .MIXING.RATIO so attempt to identify actual type of measurement 
            ;(mixing ratio etc) by looking at corresponding VAR_UNIT values
            mrvi=WHERE(STRPOS(STRLOWCASE(in3[ri]),'pp') NE -1,mrvcnt) ;testing for volume mixing ratio
            mrmi=WHERE(STRPOS(STRLOWCASE(in3[ri]),' g ') NE -1,mrmcnt) ;test for mass mixing ratio
            ndi=WHERE(STRPOS(STRLOWCASE(in3[ri]),'mol') NE -1,ndcnt) ;test for number density
            ppi=WHERE(STRPOS(STRLOWCASE(in3[ri]),'pa') NE -1,ppcnt) ;test for partial pressure
            IF i EQ nols1-1 THEN cnti=[mrvcnt,mrmcnt,0,0] ELSE cnti=[mrvcnt,mrmcnt,ndcnt,ppcnt]
            ci=WHERE(cnti GT 0,ccnt)
            IF ccnt EQ 1 THEN BEGIN ;type of measurement successfully found
              ;Note: not set up to handle if more than one type of measurement found in the file
              vlen=STRLEN(obs_list_spec_1[i])
              FOR j=0,rcnt-1 DO BEGIN
                IF (STRUPCASE(vn_v[ri[j],0]) EQ 'AIR.CONCENTRATION') AND (ci[0] EQ 2) THEN $
                  ;Do special case check for AIR.CONCENTRATION - can only change to NUMBER.DENSITY
                  vn[ri[j],0]='NUMBER.DENSITY' $
                ELSE BEGIN
                  vpos=STRPOS(STRUPCASE(vn_v[ri[j],0]),obs_list_spec_1[i])
                  vn_v[ri[j],0]=STRMID(vn_v[ri[j],0],0,vpos)+rep_list_conc[ci[0]]+STRMID(vn_v[ri[j],0],vpos+vlen)
                ENDELSE
              ENDFOR
            ENDIF
          ENDELSE
        ENDIF
      ENDFOR
      FOR i=0,N_ELEMENTS(obs_list_2)-1 DO BEGIN ;Check for obsolete mode values
        ri=WHERE(STRUPCASE(vn_v[*,1]) EQ obs_list_2[i],rcnt)
        IF rcnt NE 0 THEN BEGIN
          test1=(i LE 1) AND (STRPOS(STRUPCASE(in4),'FTIR') NE -1)
          test2=(i LE 1) AND (STRPOS(STRUPCASE(in4),'UVVIS') NE -1) AND $
                (STRPOS(STRUPCASE(in4),'DOBSON') EQ -1) AND (STRPOS(STRUPCASE(in4),'BREWER') EQ -1)
          test3=((i EQ 2) OR (i EQ 3)) AND ((STRPOS(STRUPCASE(in4),'MWR') NE -1) OR $
                 (STRPOS(STRUPCASE(in4),'MICROWAVE') NE -1))
          IF i LE 1 THEN mi=STRSPLIT(rep_list_2[i],'|',/EXTRACT)
          ;test1, test2, and test3 are special case obsolete values
          IF test1 THEN vn_v[ri,1]=mi[0] $
          ELSE IF test2 THEN vn_v[ri,1]=mi[1] $
          ELSE IF test3 THEN vn_v[ri,1]=rep_list_2[i] $ ;direct replacement
          ELSE BEGIN ;all other obsolete mode values
            IF i LE 1 THEN vn_v[ri,1]=mi[0] ELSE vn_v[ri,1]=rep_list_2[i] ;direct replacement
            IF i EQ 5 THEN BEGIN ;SLANT (if column measurement then add to main variable name)
              FOR j=0,rcnt-1 DO BEGIN
                IF STRLEN(vn_v[ri[j],0])-STRPOS(vn_v[ri[j],0],'COLUMN') EQ 6 THEN $
                vn_v[ri[j],0]=vn_v[ri[j],0]+'.'+obs_list_2[i]
              ENDFOR
            ENDIF
          ENDELSE
        ENDIF
      ENDFOR
      ;Check conditional miscellaneous changes
      FOR i=0,N_ELEMENTS(misc_list_1)-1 DO BEGIN
        IF i EQ 0 THEN ri=WHERE(STRPOS(STRUPCASE(in2),misc_list_1[i]) NE -1,rcnt) $
        ELSE ri=WHERE(STRUPCASE(in2) EQ misc_list_1[i],rcnt)
        IF rcnt NE 0 THEN BEGIN
          IF i EQ 0 THEN BEGIN ;ensure DATA_SOURCE is BUOY before changing
            IF STRPOS(STRUPCASE(in4),'BUOY') NE -1 THEN BEGIN
              FOR j=0,rcnt-1 DO BEGIN
                vn_v[ri[j],0]=misc_list_2[i] & vn_v[ri[j],1]=''
              ENDFOR
            ENDIF
          ENDIF ELSE BEGIN ;ensure O3.COLUMN is also present as a DATA_VARIABLE before changing
            mi=WHERE(STRUPCASE(vn_v[*,0]) EQ 'O3.COLUMN',mcnt)
            IF mcnt NE 0 THEN BEGIN
              vn_v[ri[0],0]='O3.COLUMN' & vn_v[ri[0],1]='AMF'
            ENDIF
          ENDELSE
        ENDIF
      ENDFOR
      
      FOR i=0,N_ELEMENTS(obs_list_3)-1 DO BEGIN ;Check for obsolete descriptor values (UNCERTAINTY)
        vuok=['ppv','ppmv','ppbv','pptv'] ;acceptable units for identifying correct replacement name (MWR only)
        test1=(STRPOS(STRUPCASE(in4),'MWR') NE -1) OR (STRPOS(STRUPCASE(in4),'MICROWAVE') NE -1) 
        vnvi=1 ;determines the location index of the descriptor variable
        ri=WHERE(STRUPCASE(vn_v[*,1]) EQ obs_list_3[i],rcnt)
        IF rcnt EQ 0 THEN BEGIN
          vnvi=2 & ri=WHERE(STRUPCASE(vn_v[*,2]) EQ obs_list_3[i],rcnt)
        ENDIF
        IF rcnt NE 0 THEN BEGIN
          IF i EQ 0 THEN vn_v[ri,vnvi]=rep_list_3[i] $ ;direct replacement
          ELSE BEGIN ;need to identify whether the UNITS are % or fit vuok criteria
            FOR j=0,rcnt-1 DO BEGIN
              IF STRTRIM(in3[ri[j]],2) EQ '%' THEN vn_v[ri[j],vnvi]=rep_list_3[i]+'.RELATIVE' $
              ELSE BEGIN
                vi=WHERE(STRTRIM(STRLOWCASE(in3[ri[j]]),2) EQ vuok,vcnt)
                IF (test1) AND (vcnt NE 0) THEN $ can assume that the given error values are Standard Deviation
                  vn_v[ri[j],vnvi]=rep_list_3[i]
              ENDELSE
            ENDFOR
          ENDELSE
        ENDIF
      ENDFOR
      
      ;create any comments for INFOTXT_OUTPUT
      FOR i=0,in1-1 DO BEGIN
        ;put full DATA_VARIABLE names back together
        vn_new[i]=vn_v[i,0]
        FOR j=1,2 DO IF vn_v[i,j] NE '' THEN vn_new[i]=vn_new[i]+'_'+vn_v[i,j]
        ;Check to see if it is different to the original DATA_VARIABLE
        IF vn_new[i] NE in2[i] THEN BEGIN
          vnchange[i]=in2[i] & in2[i]=vn_new[i]
          IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN itxt=' expected to be ' $
          ELSE itxt=' renamed '
          infotxt='2 Dataset name '+vnchange[i]+itxt+in2[i]
          INFOTXT_OUTPUT,infotxt
        ENDIF
      ENDFOR
    END

  code EQ 6: BEGIN ;Look for obsolete DATA_SOURCE
      ;List of obsolete DATA_SOURCE_01 values
      obs_list=['FTIR_','UVVIS.DOAS_','MICROWAVE.RADIOMETER','LIDAR.BACKSCATTER','LIDAR.DIAL','LIDAR.OLEX',$
                'LIDAR.RIEGL','LIDAR.RMR']
      ;Corresponding replacement list
      rep_list=['FTIR.','UVVIS.DOAS.','MWR.','LIDAR.']
      ;Possible list of species for the above instruments (note: gases will take precedence
      ;over Aerosol and Temperature, o/w the first species found will be considered the
      ;primary species measured)
      spc_list=['BrO.','C2H2.','C2H6.','CCl2F2.','CCl3F.','CH4.','CHF2Cl.','CHOCHO.','ClO.','ClONO2.','CO.',$
                'CO2.','COF2.','H2CO.','H2O.','HCFC22.','HCl.','HCN.','HCOOH.','HF.','HNO3.','HONO.','IO.',$
                'N2O.','NO.','NO2.','O3.','OClO.','OCS.','SF6.','SO2.','AEROSOL','TEMPERATURE']

      oli=-1 ;will change to obs_list index value if obsolete DATA_SOURCE_01 found
      FOR i=0,N_ELEMENTS(obs_list)-1 DO IF STRPOS(STRUPCASE(in3),obs_list[i]) NE -1 THEN oli=i
      IF oli NE -1 THEN BEGIN ;obsolete DATA_SOURCE value found
        IF oli GE 3 THEN oli=3 ;to correspond with rep_list index for lidar
        n_sl=N_ELEMENTS(spc_list)
        ;Look through VAR_NAME values to try and identify new DATA_SOURCE from species list
        spc_found=INTARR(in1)-1 ;identifies index of found species names in the Datasets
        FOR i=0,n_sl-1 DO BEGIN
          fi=WHERE(STRPOS(STRMID(in2,0,STRLEN(spc_list[i])),spc_list[i]) NE -1,fcnt)
          IF fcnt NE 0 THEN spc_found[fi]=i
        ENDFOR
        ;Check list of found species - don't include Aerosol and Temperature
        pri=-1 ;will change if species found
        fi=WHERE((spc_found NE -1) AND (spc_found LT n_sl-2),fcnt)
        IF fcnt NE 0 THEN pri=spc_found[fi[0]] $ ;primary species index determined
        ELSE IF (oli EQ 1) OR (oli EQ 3) THEN BEGIN ;Test for Temperature (Lidar Only) and Aerosol
          fi=WHERE(spc_found NE -1,fcnt)
          IF fcnt NE 0 THEN BEGIN
            pri=MIN(spc_found[fi]) ;i.e. Aerosol takes precedence over Temperature
            IF (oli EQ 1) AND (pri EQ n_sl-1) THEN pri=-1 ;UVVIS.DOAS can't be Temperature
          ENDIF
        ENDIF
        IF pri NE -1 THEN BEGIN ;update DATA_SOURCE
          old_ds=in3 & in3=spc_list[pri]
          IF STRPOS(in3,'.') NE -1 THEN in3=STRMID(in3,0,STRLEN(in3)-1)
          in3=rep_list[oli]+in3+STRMID(old_ds,STRPOS(old_ds,'_'))
          IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN itxt=' expected to be ' $
          ELSE itxt=' renamed '
          infotxt='2 DATA_SOURCE value '+old_ds+itxt+in3
          INFOTXT_OUTPUT,infotxt
        ENDIF
      ENDIF
    END

  code EQ 7: BEGIN ;Look for obsolete CALVAL and NDSC FILE_ACCESS values
      obs_list=['CALVAL','NDSC']
      rep_list=['EVDC','NDACC']

      FOR i=0,in1-1 DO BEGIN
        oi=WHERE(in2[i] EQ obs_list,ocnt)
        IF ocnt NE 0 THEN BEGIN
          IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN itxt=' expected to be ' $
          ELSE itxt=' renamed '
          infotxt='2 FILE_ACCESS value '+in2[i]+itxt+rep_list[oi[0]]
          INFOTXT_OUTPUT,infotxt
          in2[i]=rep_list[oi[0]]
        ENDIF
      ENDFOR
    END

  code EQ 8: BEGIN ;Look for VAR_UNITS=DIMENSIONLESS or NONE and replace with '' or '1'
      vuv=STRUPCASE(in2)
      FOR i=0,in1-1 DO BEGIN
        IF (vuv[i] EQ 'DIMENSIONLESS') OR (vuv[i] EQ 'NONE') THEN BEGIN
          IF in3[i] EQ 'STRING' THEN newv='' ELSE newv='1'
          IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN itxt=' expected to be ' $
          ELSE itxt=' renamed '
          infotxt='2 VAR_UNITS='+vuv[i]+itxt+'VAR_UNITS='+newv+' based on VAR_DATA_TYPE='+in3[i]
          INFOTXT_OUTPUT,infotxt
          in2[i]=newv
        ENDIF
      ENDFOR
    END

  code EQ 9: BEGIN ;DATA_QUALITY/DATA_TEMPLATE checks
      attr_arr_glob_prov=['DATA_TEMPLATE','DATA_QUALITY']
      geoms_te='' & meta_te='' & std_txt=' Required Metadata Template: '
      ;Check if DATA_TEMPLATE field is present in the TAV file
      dti=WHERE(tab_arr[*,0] EQ attr_arr_glob_prov[0],dtcnt)
      ;Check if DATA_TEMPLATE label is present in the Metadata
      gi=WHERE(in1 EQ attr_arr_glob_prov[0],gcnt)
      IF gcnt EQ 1 THEN IF in2[gi[0]] NE '' THEN meta_te=STRUPCASE(in2[gi[0]])
      IF dtcnt EQ 0 THEN BEGIN
        infotxt='3'+std_txt+'DATA_TEMPLATE field is not present in the TAV file. Checks cannot be performed'
        INFOTXT_OUTPUT,infotxt
        std_txt=''
      ENDIF ELSE BEGIN
        tab_arr_sub=tab_arr[dti[0],2:FIX(tab_arr[dti[0],1]+1)] ;Valid Template values from TAV file
        ;Determine DATA_TEMPLATE value based on DATA_SOURCE value (if applicable)
        di=WHERE(in1 EQ 'DATA_SOURCE',dcnt)
        IF dcnt EQ 1 THEN BEGIN ;DATA_SOURCE found
          ;Extract DATA_SOURCE value
          IF in2[di[0]] NE '' THEN BEGIN
            res=STRSPLIT(in2[di[0]],'_',/EXTRACT)
            ;First check - First part of DATA_SOURCE matches text in TAV entry
            res1=STRUPCASE(STRSPLIT(res[0],'.',/EXTRACT,COUNT=res1cnt))
            ci=WHERE(STRPOS(STRUPCASE(tab_arr_sub),res1[0]) NE -1,ccnt)
            IF ccnt EQ 1 THEN geoms_te=tab_arr_sub[ci[0]] $ ;Template found
            ELSE IF (ccnt GT 1) AND (N_ELEMENTS(res1) GT 1) THEN BEGIN
              ;Second Check - More than one option so match second part of DATA_SOURCE with text in TAV entry
              tab_arr_sub=tab_arr_sub[ci]
              ci=WHERE(STRPOS(STRUPCASE(tab_arr_sub),res1[1]) NE -1,ccnt)
              IF ccnt NE 1 THEN BEGIN ;Try alternatives for H2O and O3, or test for third part
                CASE 1 OF
                  res1[1] EQ 'H2O': res1='WATERVAPOR'
                  res1[1] EQ 'O3': res1='OZONE'
                  (res1[0] EQ 'UVVIS') AND (res1[1] EQ 'DOAS'): BEGIN
                      IF res1cnt GE 3 THEN BEGIN
                        IF res1[2] EQ 'AEROSOL' THEN res1='AEROSOL' ELSE res1='GAS'
                      ENDIF ELSE res1=res1[1]
                    END
                  ELSE: res1=res1[1]
                ENDCASE
                ci=WHERE(STRPOS(STRUPCASE(tab_arr_sub),res1) NE -1,ccnt)
              ENDIF
              IF ccnt EQ 1 THEN geoms_te=tab_arr_sub[ci[0]] ;Template found
            ENDIF
            IF geoms_te NE '' THEN BEGIN ;DATA_TEMPLATE value expected based on DATA_SOURCE
              IF gcnt EQ 1 THEN BEGIN ;DATA_TEMPLATE label is present
                IF meta_te NE STRUPCASE(geoms_te) THEN BEGIN
                  in2[gi[0]]=geoms_te ;Add value to DATA_TEMPLATE label
                  IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN itxt=' expected to be ' $
                  ELSE itxt=' renamed '
                  infotxt='2 DATA_TEMPLATE value'+itxt+geoms_te+' based on DATA_SOURCE value'
                  INFOTXT_OUTPUT,infotxt
                ENDIF
              ENDIF ELSE IF gcnt EQ 0 THEN in3[0]=geoms_te ;Need to add new Global Attribute Information
              infotxt='0'+std_txt+geoms_te ;default log output
              INFOTXT_OUTPUT,infotxt
              std_txt=''
            ENDIF
          ENDIF
        ENDIF
        IF (geoms_te EQ '') AND (meta_te NE '') THEN BEGIN
          ;cannot verify value from DATA_SOURCE so check value already present in the Metadata
          ci=WHERE(STRUPCASE(tab_arr_sub) EQ meta_te,ccnt)
          IF ccnt NE 0 THEN BEGIN
            geoms_te=tab_arr_sub[ci[0]] & in2[gi[0]]=geoms_te
            infotxt='0'+std_txt+geoms_te
          ENDIF ELSE BEGIN ;Template file given in the Metadata is invalid
            infotxt='3'+std_txt+'DATA_TEMPLATE filename does not correspond with any TAV entries'
          ENDELSE
          INFOTXT_OUTPUT,infotxt
          std_txt=''
        ENDIF
      ENDELSE
      IF geoms_te NE '' THEN BEGIN ;Check if DATA_QUALITY label is present
        gi=WHERE(in1 EQ attr_arr_glob_prov[1],gcnt)
        IF gcnt EQ 0 THEN in3[1]='DATA_QUALITY' ;Need to add new Global Attribute Information
      ENDIF
      IF std_txt NE '' THEN BEGIN ;No template file required based on selection criteria
        infotxt='0'+std_txt+'DATA_TEMPLATE value not required based on selection criteria'
        INFOTXT_OUTPUT,infotxt
      ENDIF
    END

  code EQ 10: BEGIN ;check printable characters in Metadata and Datasets (of type String)
      ;Note: Also allowed are Control Characters Null Character (0B), Horizontal Tab (9B),
      ;Line Feed (10B), and Carriage Return (13B) - Note: 10B and 13B for Metadata only
      exempt=['PI_NAME','DO_NAME','DS_NAME','PI_AFFILIATION','DO_AFFILIATION','DS_AFFILIATION',$
              'PI_ADDRESS','DO_ADDRESS','DS_ADDRESS','PI_EMAIL','DO_EMAIL','DS_EMAIL']
      mentry=0 &  ;Default assumes String Dataset Entry
      IF N_PARAMS() EQ 3 THEN in2='Dataset '+STRTRIM(in2,2) $ ;Dataset Entry
      ELSE mentry=1 ;Metadata entry
      FOR i=0L,N_ELEMENTS(in1)-1L DO BEGIN
        exempt_att=0 ;default assumes attribute is not exempt from checks
        testb=BYTE(in1[i])
        IF mentry THEN BEGIN
          res=STRSPLIT(in1[i],'=',/EXTRACT)
          ochk=STRPOS(tab_arr(*,0),'ORIGINATOR') NE -1
          oi=WHERE(ochk NE 0,ocnt)
          IF ocnt NE 0 THEN BEGIN
            ;Do not need to check 'exempt' attributes if using the full version of the TAV file
            ei=WHERE(STRUPCASE(res[0]) EQ exempt,ecnt)
            IF ecnt NE 0 THEN exempt_att=1 ;invalid entries can be corrected by the code
          ENDIF
          in2='Metadata Attribute Entry '+res[0]
          test=(testb NE 0B) AND (testb NE 9B) AND (testb NE 10B) AND (testb NE 13B)
        ENDIF ELSE test=(testb NE 0B) AND (testb NE 9B) ;Check for Dataset Control Characters
        IF exempt_att EQ 0 THEN BEGIN
          bi=WHERE(((testb LT 32B) OR (testb GT 126B)) AND (test),bcnt)
          IF bcnt NE 0 THEN BEGIN ;Illegal character present
            IF bcnt GT 1L THEN BEGIN ;check for repeat illegal characters and only display once
              bix=[bi[0]]
              FOR j=1L,bcnt-1L DO BEGIN
                ri=WHERE(testb[bi[j]] EQ testb[bi[0L:j-1L]],rcnt)
                IF rcnt EQ 0 THEN bix=[bix,bi[j]]
              ENDFOR
              bi=bix & bcnt=N_ELEMENTS(bi)
            ENDIF
            infotxt=STRARR(2)
            infotxt[0]='3 Entry must only include valid characters from the ISO646-US ASCII character set.'
            infotxt[1]='    Illegal character(s) in '+in2+' (may not display correctly): '
            FOR j=0L,bcnt-1L DO BEGIN
              cval=STRTRIM(testb[bi[j]],2)
              IF (cval EQ STRTRIM(8B,2)) OR (cval EQ '') THEN BEGIN
                ;Illegal non-printable character so print in Decimal Byte form
                cval=STRING(format='(I4)',testb[bi[j]]) & cval=STRTRIM(cval,2)+'B'
              ENDIF
              IF j NE bcnt-1L THEN itxt=', ' ELSE itxt=''
              infotxt[1]=infotxt[1]+cval+itxt
            ENDFOR
            INFOTXT_OUTPUT,infotxt
          ENDIF
        ENDIF
      ENDFOR
    END

ENDCASE

END ;Procedure GEOMS_Rule_Changes



PRO pre_defined_att_checks, ct, nav, vav, vnx, vdtv,verror
;Procedure to perform checks on the HDF4 pre-defined attributes, as well as check that
;the numeric variable attribute values are of the same data type as that given by the
;corresponding VAR_DATA_TYPE value (if input is via session memory)
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20101120: Introduced - Version 4.0
;
;  Inputs: ct - Identifies the type of check to be performed on the inputs
;          nav - The HDF pre-defined attribute to check
;          vav - The Variable Attribute corresponding to the pre-defined attribute
;          vnx - The Dataset from which the attributes are derived
;          vdtv - The Data Type of the Dataset
;          verror - Boolean to indicate whether the Variable Attribute data type error has
;                   already been written
;
;  Outputs: None - Any Pre-defined attributes written to an HDF file are recreated by the program
;
;  Called by: IDLCR8HDF, READ_METADATA
;
;  Subroutines Called: INFOTXT_OUTPUT
;    Information Conditions (when the program is able to make changes):
;      1. VAR_VALID_MIN/MAX or VAR_FILL_VALUE data types do not match VAR_DATA_TYPE
;      2. HDF4 pre-defined attribute data type does not match VAR_DATA_TYPE
;      3. HDF4 pre-defined attribute units value does not match VAR_UNITS
;      4. HDF4 pre-defined attribute value does not equal equivalent variable
;         attribute value (valid_range, _FillValue)
;      5. HDF4 pre-defined attribute [long_name/format/coordsys] present in the HDF file
;      6. Datasets that have been scaled or had an offset applied are not permitted

COMMON WIDGET_WIN

IF ct NE -1 THEN BEGIN ;check units, _FillValue, and valid_range attributes only
  ncsa=['units','_Fillvalue','valid_range','valid_range']
  var_atts=['VAR_UNITS','VAR_FILL_VALUE','VAR_VALID_MIN','VAR_VALID_MAX']

  ;Change VAR_DATA_TYPE value to IDL Type code
  CASE 1 OF
    vdtv EQ 'BYTE': idltc=1
    vdtv EQ 'SHORT': idltc=2
    (vdtv EQ 'INTEGER') OR (vdtv EQ 'LONG'): idltc=3
    (vdtv EQ 'REAL') OR (vdtv EQ 'FLOAT'): idltc=4
    vdtv EQ 'DOUBLE': idltc=5
    vdtv EQ 'STRING': idltc=7
    ELSE: idltc=0
  ENDCASE
  test1=(SIZE(vav,/TYPE) EQ 7) AND (STRTRIM(vav,2) NE '')
  test2=SIZE(vav,/TYPE) NE 7
  test3=(SIZE(nav,/TYPE) EQ 7) AND (STRTRIM(nav,2) NE '')
  test4=SIZE(nav,/TYPE) NE 7
  IF ((test1) OR (test2)) AND (ct NE 0) THEN BEGIN
    IF (SIZE(vav,/TYPE) NE idltc) AND (idltc NE 0) AND (verror EQ 0) THEN BEGIN
      ;Check data type of Variable Attribute
      infotxt=STRARR(2)
      itxt='VAR_VALID_MIN, VAR_VALID_MAX or VAR_FILL_VALUE'
      infotxt[0]='2 '+itxt+' data types do not match VAR_DATA_TYPE='+vdtv
      IF vnx NE '' THEN infotxt[1]='    for Dataset '+vnx+'|.' $
      ELSE BEGIN
        infotxt[0]=infotxt[0]+'|.' & infotxt[1]='   '
      ENDELSE
      infotxt[1]=infotxt[1]+' Data type will be changed to match VAR_DATA_TYPE value in HDF file'
      INFOTXT_OUTPUT,infotxt
      verror=1
    ENDIF
  ENDIF
  IF ((test3) OR (test4)) AND (ct NE 0) THEN BEGIN
    IF (SIZE(nav,/TYPE) NE idltc) AND (idltc NE 0) AND (o3[0] EQ 'H4') THEN BEGIN
      ;Check data type of pre-defined attribute
      infotxt=STRARR(2)
      infotxt[0]='2 HDF4 pre-defined attribute '+ncsa[ct]+' data type does not match VAR_DATA_TYPE='+vdtv
      IF vnx NE '' THEN infotxt[0]=infotxt[0]+' for Dataset '+vnx+'|.' $
      ELSE infotxt[0]=infotxt[0]+'|.'
      infotxt[1]='    Data type will be changed to match VAR_DATA_TYPE value in HDF file'
      INFOTXT_OUTPUT,infotxt
    ENDIF
  ENDIF
  IF ((test1) OR (test2)) AND ((test3) OR (test4)) THEN BEGIN
    ;Compare Variable Attributes against pre-defined attributes
    IF ct EQ 0 THEN BEGIN ;units check
      IF (STRTRIM(nav,2) NE STRTRIM(vav,2)) AND (o3[0] EQ 'H4') THEN BEGIN
        infotxt=STRARR(2)
        infotxt[0]='2 HDF4 pre-defined attribute units='+nav+' does not match VAR_UNITS='+vav
        IF vnx NE '' THEN infotxt[0]=infotxt[0]+' for Dataset '+vnx+'|.' $
        ELSE infotxt[0]=infotxt[0]+'|.'
        infotxt[1]='    HDF4 units will be changed to match VAR_UNITS value in HDF file'
        INFOTXT_OUTPUT,infotxt
      ENDIF
    ENDIF ELSE BEGIN
      IF (nav NE vav) AND (idltc NE 7) AND (idltc NE 0) AND (o3[0] EQ 'H4') THEN BEGIN
        infotxt=STRARR(2)
        infotxt[0]='2 HDF4 pre-defined attribute '+ncsa[ct]+' value does not equal '+var_atts[ct]+' value'
        IF vnx NE '' THEN infotxt[0]=infotxt[0]+' for Dataset '+vnx+'|.' $
        ELSE infotxt[0]=infotxt[0]+'|.'
        infotxt[1]='    HDF4 '+ncsa[ct]+' will be changed to match '+var_atts[ct]+' value in HDF file'
        INFOTXT_OUTPUT,infotxt
      ENDIF
    ENDELSE
  ENDIF
ENDIF ELSE BEGIN ;Do checks on remaining pre-defined attributes
  ncsa_str=['long_name','format','coordsys']
  ncsa_cal=['scale_factor','scale_factor_err','add_offset','add_offset_err','calibrated_nt']
  FOR i=0,N_ELEMENTS(ncsa_str)-1 DO BEGIN
    ni=WHERE(STRLOWCASE(nav) EQ ncsa_str[i],ncnt)
    IF ncnt NE 0 THEN BEGIN
      IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN itxt=' present in' ELSE itxt=' will not be written to'
      infotxt='0 HDF4 pre-defined attribute '+ncsa_str[i]+itxt+' the HDF file'
      INFOTXT_OUTPUT,infotxt
    ENDIF
  ENDFOR
  calfound=0
  FOR i=0,N_ELEMENTS(ncsa_cal)-1 DO BEGIN
    ni=WHERE((STRLOWCASE(nav) EQ ncsa_cal[i]) AND (calfound EQ 0),ncnt)
    IF ncnt NE 0 THEN BEGIN
      calfound=1
      infotxt='3 Datasets that have been scaled or had an offset applied are not permitted'
      INFOTXT_OUTPUT,infotxt
    ENDIF
  ENDFOR
ENDELSE

END ;Procedure Pre_Defined_Att_Checks



PRO read_metadata, metafile, inf
;Procedure to check Metadata contents and return as meta_arr - also:
;1. Ensures uniform input (making ATTRIBUTE_NAME uppercase, deleting unwanted spaces etc).
;2. Checks that attribute length falls within allowable limits
;3. Checks for repeated, missing, new, obsolete attributes
;4. Update FILE_META_VERSION with TAV and software version (tab_ver)

;Please also note the following:
;1. Any extra valid Global Attributes will be included (and added to the attr_arr_glob array).
;2. If redundant attributes are detected they will be omitted from the Metadata written
;   to the HDF file.
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20050802: Original IDLCR8HDF Routine - Version 1.0
;    20061012: Error messages modified; Allow VAR_MONOTONE as a Variable Attribute if it is present in the
;              Metadata; If DATA_TYPE is present in the Metadata then change it to DATA_LEVEL; Allow
;              additional Global Attributes; Puts Variable Attribute names in the same order as
;              attr_arr_data; Common variable definition WIDGET_WIN added - Version 2.0
;    20080302: VAR_MONOTONE not included in the output Metadata if it is present in the input Metadata
;              and an AVDC style TAV file is read in; if DATA_TYPE is present in the Metadata it is changed
;              to DATA_LEVEL if an AVDC style TAV file is read in, and vice versa if an original style
;              Envisat table.dat file read in; Warnings added if VAR_MONOTONE attribute is omitted, when
;              changing DATA_TYPE to DATA_LEVEL (or vice versa), and if extra Global Attributes are
;              included in the Metadata; Checks for missing or repeated Global Attributes; Global
;              Attributes can now be listed in any order in the Metadata (will be written to the HDF file
;              in a standard order) - Version 3.0
;    20091203: Stop using DATA_TYPE for EVDC style input (if found change to DATA_LEVEL); If VAR_MONOTONE
;              is present in the Metadata it is removed - Version 3.08
;    20100205: Add RETURN command after all STOP_WITH_ERROR calls, which allows program to return to the
;              calling program if the reterr argument is included in the idlcr8hdf call - Version 3.09
;    20101120: Add DATA_STOP_DATE and remove DATA_LEVEL from Global Attributes; Remove VAR_AVG_TYPE,
;              VAR_DIMENSION, and VIS attributes from Variable Attributes; Add call to GEOMS_RULE_CHANGES
;              to account for changes in Metadata setup between v3.0 and v4.0; Remove option to have a
;              filename as a value for free text attributes; Increase checks between DATA_VARIABLES and
;              VAR_NAME values - Version 4.0b0
;    20111220: Call additional GEOMS_RULE_CHANGES; Perform checks on HDF4 pre-defined attributes
;              - Version 4.0b7
;
;  Inputs: metafile - Either, the filename of the input file containing the Metadata or, if program
;                     input is via string array and Structure, a string array containing the Global
;                     and Variable Attributes.
;          inf - flag, where 0=Metafile is an array; 1=Metafile is a file.
;
;  Output: meta_arr - a string array containing the Global and Variable Attributes, which have been
;                     checked and uniformally formatted.
;
;  Called by: IDLCR8HDF
;
;  Subroutines Called: STOP_WITH_ERROR (if error state detected);
;                      INFOTXT_OUTPUT, GEOMS_RULE_CHANGES
;    Possible Conditions for STOP_WITH_ERROR call (plus [line number] where called):
;      1. Metadata value contains too many characters
;      2. No or invalid DATA_VARIABLES and VAR_NAME attributes present in the metadata
;      3. DATA_VARIABLES or VAR_NAME value appears more than once
;      4. No valid Metadata in command line parameter file or arrays
;      5. VAR_NAME does not match corresponding DATA_VARIABLES value
;      6. Number of DATA_VARIABLES values does not match the number of VAR_NAME occurrences
;      7. A required Global Attribute Label is not present in the Metadata
;      8. A required Global Attribute Label is repeated in the Metadata
;      9. Number of Attribute occurrences does not match the number of datasets
;     10. DATA_QUALITY is not present but is a mandatory attribute when DATA_TEMPLATE is reported
;
;    Information Conditions (when the program is able to make changes):
;      1. Invalid Attribute Label ignored
;      2. Missing Global Attribute added
;      3. DATA_VARIABLES attribute added to metadata based on VAR_NAME values
;      4. Values for DATA_VARIABLES appended to the metadata based on VAR_NAME values
;      5. VAR_NAME value appended to label based on DATA_VARIABLES value
;      6. New Global Attribute added

COMMON TABLEDATA
COMMON METADATA
COMMON DATA
COMMON WIDGET_WIN

attr_arr_glob=['PI_NAME','PI_AFFILIATION','PI_ADDRESS','PI_EMAIL',$
               'DO_NAME','DO_AFFILIATION','DO_ADDRESS','DO_EMAIL',$
               'DS_NAME','DS_AFFILIATION','DS_ADDRESS','DS_EMAIL',$
               'DATA_DESCRIPTION','DATA_DISCIPLINE','DATA_GROUP','DATA_LOCATION',$
               'DATA_SOURCE','DATA_VARIABLES','DATA_START_DATE','DATA_STOP_DATE',$
               'DATA_FILE_VERSION','DATA_MODIFICATIONS','DATA_CAVEATS','DATA_RULES_OF_USE',$
               'DATA_ACKNOWLEDGEMENT','DATA_QUALITY','DATA_TEMPLATE','DATA_PROCESSOR',$
               'FILE_NAME','FILE_GENERATION_DATE','FILE_ACCESS','FILE_PROJECT_ID','FILE_DOI', $
               'FILE_ASSOCIATION','FILE_META_VERSION']

attr_arr_glob_opt=['DATA_DESCRIPTION','DATA_MODIFICATIONS','DATA_CAVEATS','DATA_RULES_OF_USE',$
                   'DATA_ACKNOWLEDGEMENT','DATA_QUALITY','DATA_TEMPLATE','DATA_PROCESSOR',$
                   'FILE_PROJECT_ID','FILE_ASSOCIATION']

attr_arr_glob_ins=['DATA_START_DATE','DATA_STOP_DATE','FILE_GENERATION_DATE', $
                   'FILE_DOI','FILE_META_VERSION']

attr_arr_glob_prov=['DATA_TEMPLATE','DATA_QUALITY']

attr_arr_data=['VAR_NAME','VAR_DESCRIPTION','VAR_NOTES','VAR_SIZE','VAR_DEPEND',$
               'VAR_DATA_TYPE','VAR_UNITS','VAR_SI_CONVERSION','VAR_VALID_MIN',$
               'VAR_VALID_MAX','VAR_FILL_VALUE']

attr_arr_data_opt=['VAR_NOTES']

;To check for pre-defined attributes
ncsa=['long_name','units','format','coordsys','valid_range','_fillvalue','scale_factor', $
      'scale_factor_err','add_offset','add_offset_err','calibrated_nt']

nchar=65535 ;limit on number of characters

;possible error messages for this procedure
errtxt=STRARR(9)
proname='Read_Metadata procedure: '
errtxt[0]=' value contains too many characters (maximum permitted: '+STRTRIM(nchar,2)+')'
errtxt[1]='No or invalid DATA_VARIABLES and VAR_NAME attributes present in the metadata'
errtxt[2]=' value appears more than once: '
errtxt[3]='No valid Metadata in input'
errtxt[4]='VAR_NAME does not match corresponding DATA_VARIABLES value: '
errtxt[5]='Number of DATA_VARIABLES values does not match the number of VAR_NAME occurrences '
errtxt[6]='Global Attribute Label not present in the Metadata: ' ;now INFOTXT
errtxt[7]='Global Attribute Label repeated in the Metadata: '
errtxt[8]=' occurrences does not match the number of datasets (should be '

dum='' & nrline=0 & dvfound=-1L
nd=N_ELEMENTS(attr_arr_data)
ng=N_ELEMENTS(attr_arr_glob)
nna=N_ELEMENTS(num_atts)-1
dsei=WHERE(attr_arr_glob EQ 'DS_EMAIL') ;any new global attributes should be after this attribute
vni=WHERE(attr_arr_data EQ 'VAR_NAME') ;used in VAR_NAME checks
ndv=0 ;will reset to the number of datasets

IF inf EQ 1 THEN BEGIN ;count number of lines in the file
  OPENR,lu,metafile,/GET_LUN
  WHILE NOT EOF(lu) DO BEGIN
    READF,lu,dum & nrline=nrline+1
  ENDWHILE
  FREE_LUN,lu
  mh=STRARR(nrline) & mv_lng=LON64ARR(nrline) & mv_dbl=DBLARR(nrline)
  OPENR,lu,metafile,/GET_LUN
  READF,lu,mh
  FREE_LUN,lu
ENDIF ELSE mh=metafile ;metadata is already in an array
mh=STRTRIM(mh,2)
mhgood=INTARR(N_ELEMENTS(mh))+1 ;will be assigned zero for unwanted metadata lines

;Check for Redundant Attribute Labels
GEOMS_RULE_CHANGES,0,mh,mhgood

;test1 - check first character is A-Z or a-z; test2 - check for '=' and not a redundant label
test1=(((BYTE(STRMID(mh,0,1)) GE 65) AND (BYTE(STRMID(mh,0,1)) LE 90)) OR $
      ((BYTE(STRMID(mh,0,1)) GE 97) AND (BYTE(STRMID(mh,0,1)) LE 122)))
test2=(STRPOS(mh,'=') GE 1) AND (mhgood EQ 1)

nri=WHERE((test1) AND (test2),nrline)
IF nrline EQ 0 THEN BEGIN
  STOP_WITH_ERROR,o3[3]+proname,errtxt[3],lu & RETURN
ENDIF

;Set holding arrays for metadata
mh=mh[nri] & mv_lng=mv_lng[nri] & mv_dbl=mv_dbl[nri]
lu=-1
m_v0=STRARR(nrline) & m_v1=m_v0 ;to hold metadata labels and values
m_v2=INTARR(nrline) ;global/variable attribute switch

;Separate out Meta entries, put in uniform format and put label into upper case
FOR i=0L,nrline-1L DO BEGIN
  ;separate out the Meta entry into two components
  eqpos=STRPOS(mh[i],'=')
  ;Delete unwanted spaces from metadata label
  m_v0[i]=STRMID(mh[i],0,eqpos) & m_v0[i]=STRTRIM(m_v0[i],2)
  IF eqpos EQ STRLEN(mh[i])-1 THEN m_v1[i]='' $ ;ie. the last character is the '='
  ELSE BEGIN
    m_v1[i]=STRMID(mh[i],eqpos+1) & m_v1[i]=STRTRIM(m_v1[i],2)
    ;check for string length of attribute value
    IF STRLEN(m_v1[i]) GT nchar THEN BEGIN
      STOP_WITH_ERROR,o3[3]+proname,m_v0[i]+errtxt[0],lu & RETURN
    ENDIF
  ENDELSE
ENDFOR

;Check for any attribute label that is not uppercase and not an HDF pre-defined label
ui=WHERE(m_v0 NE STRUPCASE(m_v0),ucnt)
IF ucnt NE 0L THEN BEGIN ;some attribute labels are not fully uppercase
  writeonce=0 ;write out information text once only
  FOR i=0L,ucnt-1L DO BEGIN
    ;check for HDF predefined labels which should be lowercase
    pi=WHERE(m_v0[ui[i]] EQ ncsa,pcnt)
    IF pcnt EQ 0 THEN BEGIN ;label expected to be in uppercase
      m_v0[ui[i]]=STRUPCASE(m_v0[ui[i]])
      IF writeonce EQ 0 THEN BEGIN ;write INFORMATION text to log
        writeonce=1
        IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN itxt='must be' ELSE itxt='made'
        infotxt='2 Metadata Attribute Labels '+itxt+' UPPERCASE'
        INFOTXT_OUTPUT,infotxt
      ENDIF
    ENDIF
  ENDFOR
ENDIF

FOR i=0L,nrline-1L DO BEGIN
  ;Do check for DATA_VARIABLES and separate out the values
  IF m_v0[i] EQ 'DATA_VARIABLES' THEN BEGIN
    dv=STRSPLIT(m_v1[i],' ;',/Extract,COUNT=ndv) & dvfound=i
  ENDIF

  ;Check for FILE_META_VERSION and add value derived from READ_TABLEFILE if not doing QA
  IF m_v0[i] EQ 'FILE_META_VERSION' THEN BEGIN
    IF (STRPOS(o3[2],'idlcr8qa.log') EQ -1) AND (m_v1[i] NE tab_ver) THEN BEGIN
      m_v1[i]=tab_ver
      infotxt='0 FILE_META_VERSION updated with corrected tool name and TAV file information'
      INFOTXT_OUTPUT,infotxt
    ENDIF ELSE IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN BEGIN
      ;Check Revision number is less than or equal to the TAV revision number
    ENDIF
  ENDIF

  ;Check whether a Global Attribute (1), GEOMS Variable Attribute (2), or pre-defined Variable Attribute (3)
  gi=WHERE(m_v0[i] EQ attr_arr_glob,gcnt)
  vi=WHERE(m_v0[i] EQ attr_arr_data,vcnt)
  pi=WHERE(STRLOWCASE(m_v0[i]) EQ ncsa,pcnt)
  IF gcnt NE 0 THEN m_v2[i]=1 $
  ELSE IF vcnt NE 0 THEN m_v2[i]=2 $
  ELSE IF pcnt NE 0 THEN m_v2[i]=3 $
  ELSE BEGIN ;check for new Global Attribute
    IF i GT 0 THEN test1=m_v2[i-1] EQ 1 ELSE test1=1 ;i.e. the previous attribute was also a global attribute
    test2=(STRMID(m_v0[i],0,3) NE 'VAR') AND (STRMID(m_v0[i],0,3) NE 'VIS') ;does not start with 'VAR' or 'VIS'
    test3=STRPOS(m_v0[i],' ') EQ -1 ;No spaces in the label
    ;Check for possible mispellings of an actual attribute by removing '_' and comparing
    gv_chk=STRUPCASE(STRJOIN(STRSPLIT(m_v0[i],' _',/EXTRACT),/SINGLE))
    test4=1
    FOR j=0,ng-1 DO BEGIN
      ga_j=STRUPCASE(STRJOIN(STRSPLIT(attr_arr_glob[j],' _',/EXTRACT),/SINGLE))
      IF gv_chk EQ ga_j THEN test4=0 ;Match with actual Global Attribute so do not keep
    ENDFOR
    IF (test1) AND (test2) AND (test3) AND (test4) THEN m_v2[i]=1 ;it is considered a new global attribute
  ENDELSE
ENDFOR

;Check for any invalid attribute labels and remove
bi=WHERE(m_v2 EQ 0,bcnt)
IF bcnt NE 0 THEN BEGIN
  FOR i=0,bcnt-1 DO BEGIN
    infotxt='2 Unknown Attribute Label '+m_v0[bi[i]]+'| ignored'
    INFOTXT_OUTPUT, infotxt
  ENDFOR
ENDIF
;resize arrays, or stop the program if no valid data
gi=WHERE(m_v2 NE 0,nrline)
IF nrline NE 0 THEN BEGIN
  m_v0=m_v0[gi] & m_v1=m_v1[gi] & m_v2=m_v2[gi]
  mv_lng=mv_lng[gi] & mv_dbl=mv_dbl[gi]
ENDIF ELSE BEGIN
  STOP_WITH_ERROR,o3[3]+proname,errtxt[3],lu & RETURN
ENDELSE

;Check to see that Global and Variable Attributes are present
gi=WHERE(m_v2 EQ 1,gcnt)
vi=WHERE(m_v2 EQ 2,vcnt)
pi=WHERE(m_v2 EQ 3,pcnt) ;to do pre-defined attribute checks if necessary
IF (gcnt EQ 0) OR (vcnt EQ 0) THEN BEGIN
  STOP_WITH_ERROR,o3[3]+proname,errtxt[3],lu & RETURN
ENDIF

;Do QA on pre-defined attributes
IF pcnt NE 0 THEN PRE_DEFINED_ATT_CHECKS,-1,m_v0[pi]

;Do DATA_VARIABLES checks
IF ndv EQ 0 THEN BEGIN
  ;If no DATA_VARIABLES values found then try to determine values from VAR_NAME values
  dvi=WHERE((m_v0 EQ 'VAR_NAME') AND (m_v1 NE ''),ndv)
  IF ndv NE 0 THEN BEGIN
    dv=m_v1[dvi]
    ;Create or append to DATA_VARIABLES attribute
    IF dvfound EQ -1L THEN BEGIN ;increase array sizes by 1 to accommodate DATA_VARIABLES
      dvfound=nrline & nrline=nrline+1L
      m_v0=[m_v0,'DATA_VARIABLES'] & m_v1=[m_v1,''] & m_v2=[m_v2,1]
      mv_lng=[mv_lng,0LL] & mv_dbl=[mv_dbl,0.D]
      infotxt='2 Missing DATA_VARIABLES Global Attribute| added to metadata based on VAR_NAME values'
    ENDIF ELSE BEGIN
      infotxt='2 Missing DATA_VARIABLES attribute values| appended to the metadata based on VAR_NAME values'
    ENDELSE
    INFOTXT_OUTPUT, infotxt
  ENDIF ELSE BEGIN
    STOP_WITH_ERROR,o3[3]+proname,errtxt[1],lu & RETURN
    ;No or invalid DATA_VARIABLES and VAR_NAME attributes present in the metadata so cannot proceed
  ENDELSE
ENDIF
;Check for repeated DATA_VARIABLES
FOR i=0,ndv-1 DO BEGIN
  ri=WHERE(STRUPCASE(dv[i]) EQ STRUPCASE(dv),rcnt)
  IF (rcnt GT 1) AND (dv[i] NE '') THEN BEGIN
    STOP_WITH_ERROR,o3[3]+proname,'DATA_VARIABLES'+errtxt[2]+dv[i],lu & RETURN
  ENDIF
ENDFOR

;Do VAR_NAME checks
vi=WHERE(m_v0 EQ attr_arr_data[vni[0]],vcnt) ;identify VAR_NAME indices
IF vcnt NE 0 THEN BEGIN
  ;Check if VAR_NAME values are present, if not add value from DATA_VARIABLES (if number of DATA_VARIABLES values match vcnt)
  IF ndv EQ vcnt THEN BEGIN
    FOR i=0,vcnt-1 DO BEGIN
      IF (m_v1[vi[i]] NE '') AND (m_v1[vi[i]] NE dv[i]) THEN BEGIN
        STOP_WITH_ERROR,o3[3]+proname,errtxt[4]+'('+m_v1[vi[i]]+'/'+dv[i]+')',lu & RETURN
      ENDIF ELSE IF m_v1[vi[i]] EQ '' THEN BEGIN
        m_v1[vi[i]]=dv[i]
        infotxt='2 Missing VAR_NAME value for '+m_v0[vi[i]]+'|. '+dv[i]+'| appended to label based on DATA_VARIABLES value
        INFOTXT_OUTPUT,infotxt
      ENDIF
    ENDFOR
  ENDIF ELSE BEGIN ;number of DATA_VARIABLES values does not match the number of VAR_NAME occurrences
    STOP_WITH_ERROR,o3[3]+proname,errtxt[5]+'('+STRTRIM(ndv,2)+'/'+STRTRIM(vcnt,2)+')',lu & RETURN
  ENDELSE
  ;Check for repeated VAR_NAMES
  FOR i=0,vcnt-1 DO BEGIN
    ri=WHERE(STRUPCASE(m_v1[vi[i]]) EQ STRUPCASE(m_v1[vi]),rcnt)
    IF (rcnt GT 1) AND (m_v1[vi[i]] NE '') THEN BEGIN
      STOP_WITH_ERROR,o3[3]+proname,'VAR_NAME'+errtxt[2]+m_v1[vi[i]],lu & RETURN
    ENDIF
  ENDFOR
ENDIF ELSE BEGIN ;No VAR_NAME labels so create from DATA_VARIABLES
  FOR i=0,ndv-1 DO BEGIN
    m_v0=[m_v0,'VAR_NAME'] & m_v1=[m_v1,dv[i]] & m_v2=[m_v2,2]
    mv_lng=[mv_lng,0LL] & mv_dbl=[mv_dbl,0.D]
    IF i EQ 0 THEN vi=[nrline] ELSE vi=[vi,nrline+1L]
  ENDFOR
  infotxt='1 Missing VAR_NAME attribute labels and values| added to metadata based on DATA_VARIABLES values'
  INFOTXT_OUTPUT,infotxt
ENDELSE

;Check for obsolete FTIR, UVVIS.DOAS, LIDAR, and MWR DATA_SOURCE_01 values and modify of possible
dsi=WHERE(m_v0 EQ 'DATA_SOURCE',dsicnt)
vni=WHERE(m_v0 EQ 'VAR_NAME',vncnt)
;extract VAR_NAME values
dv=STRARR(vncnt) & data_source=''
FOR i=0,vncnt-1 DO dv[i]=m_v1[vni[i]]
IF dsicnt EQ 1 THEN BEGIN
  IF m_v1[dsi[0]] NE '' THEN BEGIN
    data_source=m_v1[dsi[0]] & dschange=data_source
    GEOMS_RULE_CHANGES,6,vncnt,dv,data_source
    IF data_source NE dschange THEN m_v1[dsi[0]]=data_source
  ENDIF
ENDIF

;Check for missing Global Attributes which have values which can be calculated by the program
FOR i=0,N_ELEMENTS(attr_arr_glob_ins)-1 DO BEGIN
  gaii=WHERE(m_v0 EQ attr_arr_glob_ins[i],gaicnt)
  IF gaicnt EQ 0 THEN BEGIN ;missing mandatory global attribute so add to the array
    IF attr_arr_glob_ins[i] EQ 'FILE_META_VERSION' THEN itxt=tab_ver ELSE itxt=''
    nrline=nrline+1L
    m_v0=[m_v0,attr_arr_glob_ins[i]] & m_v1=[m_v1,itxt] & m_v2=[m_v2,1]
    mv_lng=[mv_lng,0LL] & mv_dbl=[mv_dbl,0.D]
    infotxt='2 Missing mandatory Global Attribute '+attr_arr_glob_ins[i]+'| added'
    INFOTXT_OUTPUT, infotxt
  ENDIF
ENDFOR
;Do DATA_TEMPLATE/DATA_QUALITY checks
ngp=N_ELEMENTS(attr_arr_glob_prov)
ga_chk=STRARR(ngp) ;initialize DATA_TEMPLATE/QUALITY values
GEOMS_RULE_CHANGES,9,m_v0,m_v1,ga_chk
;Check to see if Global Attributes have to be added
FOR i=0,ngp-1 DO BEGIN
  IF ga_chk[i] NE '' THEN BEGIN
    m_v0=[m_v0,attr_arr_glob_prov[i]]
    IF i EQ 0 THEN m_v1=[m_v1,ga_chk[i]] ELSE m_v1=[m_v1,'']
    m_v2=[m_v2,1] & nrline=nrline+1L
    mv_lng=[mv_lng,0LL] & mv_dbl=[mv_dbl,0.D]
    IF i EQ 0 THEN itxt='='+ga_chk[i] ELSE itxt=''
    infotxt='2 Missing Global Attribute '+attr_arr_glob_prov[i]+itxt+'| added'
    INFOTXT_OUTPUT, infotxt
  ENDIF
ENDFOR

;Calculate expected size of meta_arr array
gi=WHERE(m_v2 EQ 1,gcnt)
IF gcnt GT ng THEN ngv=gcnt ELSE ngv=ng
n_arr=ngv+(nd*ndv)
meta_arr=STRARR(n_arr) & mlh=LON64ARR(n_arr) & mdh=DBLARR(n_arr)
;mlh and mdh are holding arrays to hold numeric values in the metadata (will be renamed mv_lng and mv_dbl)

;Check for missing or repeated standard Global Attributes
i=0
WHILE i LE ng-1 DO BEGIN
  gai=WHERE(m_v0[gi] EQ attr_arr_glob[i],gacnt)
  IF gacnt EQ 0 THEN BEGIN ;Check to see if Global Attribute Optional or Mandatory
    gaoi=WHERE(attr_arr_glob[i] EQ attr_arr_glob_opt, gaocnt)
    IF gaocnt EQ 0 THEN BEGIN ;it is mandatory, therefore missing
      infotxt='3 Global Attribute Label not present in the Metadata: '+attr_arr_glob[i]
      INFOTXT_OUTPUT,infotxt
    ENDIF
  ENDIF ELSE IF gacnt GT 1 THEN BEGIN ;Global Attribute Repeated
    STOP_WITH_ERROR,o3[3]+proname,errtxt[7]+attr_arr_glob[i],lu & RETURN
  ENDIF
  IF gacnt EQ 0 THEN BEGIN ;remove attribute from the attr_arr_glob array
    attr_arr_glob=[attr_arr_glob[0:i-1],attr_arr_glob[i+1:ng-1]]
    ng=ng-1
  ENDIF ELSE i=i+1
ENDWHILE

;Check for all Standard Global Attributes, add any new ones, and put in expected order
xg=0
FOR i=0,gcnt-1 DO BEGIN
  gai=WHERE(m_v0[gi[i]] EQ attr_arr_glob,gacnt)
  CASE 1 OF
    gacnt EQ 0: BEGIN ;New Global Attribute
        IF (i GE ng-(1+xg)) OR (i LE dsei) THEN BEGIN
          attr_arr_glob=[attr_arr_glob,m_v0[gi[i]]] & mi=ng
          IF i LE dsei THEN xg=xg+1
        ENDIF ELSE BEGIN
          attr_arr_glob=[attr_arr_glob[0:mi],m_v0[gi[i]],attr_arr_glob[mi+1:ng-1]]
          mi=mi+1
        ENDELSE
        ng=ng+1
        infotxt='1 Non-standard Global Attribute '+m_v0[gi[i]]+'| added'
        INFOTXT_OUTPUT, infotxt
      END
    ELSE: mi=gai[0]
  ENDCASE
  meta_arr[mi]=m_v0[gi[i]]+'='+m_v1[gi[i]]
ENDFOR

;Check for repeated new Global Attributes
FOR i=0,ng-1 DO BEGIN
  gai=WHERE(m_v0[gi] EQ attr_arr_glob[i],gacnt)
  IF gacnt GT 1 THEN BEGIN ;Global Attribute Repeated
    STOP_WITH_ERROR,o3[3]+proname,errtxt[7]+attr_arr_glob[i],lu & RETURN
  ENDIF
ENDFOR

;Do checks for all the variable attributes and put in expected order
vni=-1
FOR i=0,nd-1 DO BEGIN
  si=ng+i ;start index of meta_arr for variable attributes
  di=WHERE(m_v0 EQ attr_arr_data[i],dcnt)
  IF attr_arr_data[i] EQ 'VAR_NAME' THEN vni=di ;to enable checks on optional variable attributes
  IF dcnt EQ ndv THEN BEGIN ;i.e. correct number of attribute labels found so add to meta_arr in correct order
    FOR j=0,ndv-1 DO BEGIN
      meta_arr[si+(nd*j)]=m_v0[di[j]]+'='+m_v1[di[j]]
      mlh[si+(nd*j)]=mv_lng[di[j]] & mdh[si+(nd*j)]=mv_dbl[di[j]]
    ENDFOR
  ENDIF ELSE IF dcnt EQ 0 THEN BEGIN ;attribute not present - so add with no label
    oi=WHERE(attr_arr_data[i] EQ attr_arr_data_opt,ocnt) ;check whether missing attribute is optional
    IF ocnt EQ 0 THEN FOR j=0,ndv-1 DO meta_arr[si+(nd*j)]=attr_arr_data[i]+'='
  ENDIF ELSE BEGIN ;incorrect number of attributes - report with error unless attribute is optional
    oi=WHERE(attr_arr_data[i] EQ attr_arr_data_opt,ocnt)
    IF (ocnt NE 0) AND (vni[0] GE 0) AND (di[0]-vni[0] GT 0) THEN BEGIN ;match attributes to the corresponding VAR_NAME index value
      FOR j=0,dcnt-1 DO BEGIN
        vnih=di[j]-vni[0] & jh=0
        FOR k=0,N_ELEMENTS(vni)-1 DO BEGIN
          dvn=di[j]-vni[k]
          IF (dvn LT vnih) AND (dvn GT 0) THEN BEGIN
            vnih=di[j]-vni[k] & jh=k
          ENDIF
        ENDFOR
        meta_arr[si+(nd*jh)]=m_v0[di[j]]+'='+m_v1[di[j]]
        mlh[si+(nd*jh)]=mv_lng[di[j]] & mdh[si+(nd*jh)]=mv_dbl[di[j]]
      ENDFOR
    ENDIF ELSE BEGIN ;Not optional or too much out of order, therefore report as an error
      STOP_WITH_ERROR,o3[3]+proname,'Number of '+attr_arr_data[i]+errtxt[8]+STRTRIM(ndv,2)+')',lu & RETURN
    ENDELSE
  ENDELSE
ENDFOR

;remove any empty meta_arr cells (can happen due to optional attributes)
;and save numeric metadata values in correct order
gi=WHERE(STRTRIM(meta_arr,2) NE '')
meta_arr=meta_arr[gi] & mv_lng=mlh[gi] & mv_dbl=mdh[gi]

;Call GEOMS_RULE_CHANGES to check for obsolete Dataset names and update if possible
;Identify VAR_NAME and VAR_UNITS indices
vni=WHERE(STRMID(meta_arr,0,8) EQ 'VAR_NAME',vncnt)
vui=WHERE(STRMID(meta_arr,0,9) EQ 'VAR_UNITS',vucnt)
vnchange=STRARR(vncnt) ;array to hold original VAR_NAME values if they have been changed
;extract VAR_NAME values
dv=STRARR(vncnt)
FOR i=0,vncnt-1 DO BEGIN
  res=STRSPLIT(meta_arr[vni[i]],' =',/EXTRACT,COUNT=nres)
  IF nres EQ 2 THEN dv[i]=res[1]
ENDFOR
;Check for obsolete _START/STOP/INTEGRATION sub-values and replace with DATETIME.START/STOP
;or INTEGRATION.TIME (for single occurences only). Also check for double underscores and
;replace with single underscores in the Variable Names
GEOMS_RULE_CHANGES,1,vncnt,dv

;Check for other obsolete variable names
IF vncnt EQ vucnt THEN BEGIN
  vuv=STRARR(vucnt)
  FOR i=0,vucnt-1 DO BEGIN
    res=STRSPLIT(meta_arr[vui[i]],'=',/EXTRACT,COUNT=nres)
    IF nres EQ 2 THEN vuv[i]=STRTRIM(res[1],2)
  ENDFOR
  GEOMS_RULE_CHANGES,5,vncnt,dv,vuv,data_source
ENDIF
;Update meta_arr in the case of modified Dataset name values
vci=WHERE(vnchange NE '',vcres)
IF vcres NE 0 THEN BEGIN ;need to update VAR_NAME and DATA_VARIABLES attribute values
  dvi=WHERE(STRMID(meta_arr,0,14) EQ 'DATA_VARIABLES')
  meta_arr[dvi[0]]='DATA_VARIABLES='
  FOR i=0,vncnt-1 DO BEGIN
    ;Check for new VAR_NAME value and update
    IF vnchange[i] NE '' THEN meta_arr[vni[i]]='VAR_NAME='+dv[i]
    ;Append to new DATA_VARIABLES list
    IF i EQ 0 THEN itxt='' ELSE itxt=';'
    meta_arr[dvi[0]]=meta_arr[dvi[0]]+itxt+dv[i]
  ENDFOR
ENDIF

;Check for obsolete CALVAL and EVDC FILE_ACCESS values and replace
fai=WHERE(STRMID(meta_arr,0,11) EQ 'FILE_ACCESS')
res=STRSPLIT(meta_arr[fai[0]],' =;',/EXTRACT,COUNT=facnt)
IF facnt GE 2 THEN BEGIN
  fav=STRUPCASE(res[1:facnt-1]) & fachange=fav
  GEOMS_RULE_CHANGES,7,facnt-1,fav
  IF ARRAY_EQUAL(fav,fachange) EQ 0 THEN BEGIN ;FILE_ACCESS values changed so update meta_arr
    meta_arr[fai[0]]='FILE_ACCESS='
    FOR i=0,facnt-2 DO BEGIN
      IF i EQ 0 THEN itxt='' ELSE itxt=';'
      meta_arr[fai[0]]=meta_arr[fai[0]]+itxt+fav[i]
    ENDFOR
  ENDIF
ENDIF

;Check for VAR_UNITS=DIMENSIONLESS or NONE and fix if possible.
;Need to check VAR_DATA_TYPE. If string then VAR_UNITS value should be blank, o/w replace with '1'
vdi=WHERE(STRMID(meta_arr,0,13) EQ 'VAR_DATA_TYPE',vdcnt)
IF (vdcnt NE 0) AND (vdcnt EQ vucnt) THEN BEGIN
  vdv=STRARR(vdcnt)
  FOR i=0,vdcnt-1 DO BEGIN
    res=STRSPLIT(meta_arr[vdi[i]],'=',/EXTRACT,COUNT=nres)
    IF nres EQ 2 THEN vdv[i]=STRUPCASE(STRTRIM(res[1],2))
  ENDFOR
  vuchange=vuv
  GEOMS_RULE_CHANGES,8,vucnt,vuv,vdv
  FOR i=0,vucnt-1 DO BEGIN ;Check for changes and update meta_arr
    IF STRUPCASE(vuchange[i]) NE vuv[i] THEN meta_arr[vui[i]]='VAR_UNITS='+vuv[i]
  ENDFOR
ENDIF

;Check for non-permitted characters (must be ISO646-US character set)
GEOMS_RULE_CHANGES,10,meta_arr

END ;Procedure Read_Metadata



PRO extract_and_test, dentry, cpos, nel, ta1, ta2, taname, aname, ti
;Procedure called by Check_Metadata to extract the relevant parts of tab_arr and test against
;a corresponding Metadata value.
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20050802: Original IDLCR8HDF Routine - Version 1.0
;    20050909: Make VAR_SI_CONVERSION values match the VAR_DATA_TYPE, and add fix for VAR_SI_CONVERSION
;              calculation rules e.g. if VAR_UNITS=cm m-3 then VAR_SI_CONVERSION=0;0.01;m-2 - Version 1.1
;    20061012: Procedure simplified, with all portions of the code related to the VAR_UNITS and
;              VAR_SI_CONVERSION calculations moved to the Var_Units_Test routine; Common variable
;              definition WIDGET_WIN added - Version 2.0
;    20100205: Add RETURN command after all STOP_WITH_ERROR calls, which allows program to return to the
;              calling program if the reterr argument is included in the idlcr8hdf call - Version 3.09
;    20120313: Add option to check for Metadata Entries that are only different to the TAV entry
;              because of case sensitivity and/or use of incorrect apostrophe ("`" instead of "'")
;              - Version 4.0b8
;
;  Inputs: dentry - the Metadata entry to be checked (everything after the '=')
;          cpos - a pattern used by StrSplit on DEntry to split it into its component parts e.g. ';' or '_'
;          nel - the number of sub-values in the set of tab_arr entries being checked (ta1 only)
;          ta1 - the set of tab_arr values used to check against the Metadata contents
;          ta2 - a second set of tab_arr values used for DATA_SOURCE checks, o/w set to ['']
;          taname - a combination of the Metadata Attribute name and Table Field/Label used for the
;                   error messages
;          aname - the Metadata attribute name to be used for the error message
;          ti - the index value of the ta2 values to be checked. Used for DATA_SOURCE checks only
;
;  Output: ti - the index value(s) of tab_arr which match the Metadata value (used in Check_Metadata
;               to do further checks on the ORIGINATOR values)
;
;  Called by: CHECK_METADATA
;
;  Subroutines Called: STOP_WITH_ERROR (if error state detected)
;    Possible Conditions for STOP_WITH_ERROR call (plus [line number] where called):
;      1. Incorrect number of (sub-)values for a particular Metadata attribute
;      2. Metadata value does not match any values in the Table Attribute Values file

COMMON TABLEDATA
COMMON WIDGET_WIN

proname='Check_Metadata/Extract_And_Test procedures: ' & lu=-1L
errtxt2=STRARR(2)
errtxt2[0]='Number of (sub-)values for this attribute should be '
errtxt2[1]='Doesn''t match any Table Attribute Values under FIELD: '

;Check number of Metadata entry components is as expected
achk=STRSPLIT(dentry,cpos,/Extract)
IF N_ELEMENTS(achk) NE nel THEN BEGIN
  STOP_WITH_ERROR,o3[3]+proname+taname+'='+dentry+': ',errtxt2[0]+STRTRIM(nel,2)+'.',lu
  RETURN
ENDIF

;check Metadata entry with relevant TAV entry or entries
IF cpos EQ '_' THEN BEGIN ;DATA_SOURCE entry so need to treat components separately
  achk=STRCOMPRESS(achk,/Remove_All) & nel=1
  ;strip the last three characters (instrument ID) off achk(1)
  achk[1]=STRMID(achk[1],0,STRLEN(achk[1])-3)
ENDIF ELSE achk=STRCOMPRESS(dentry,/Remove_All)
FOR j=0,N_ELEMENTS(ta1)-1 DO BEGIN
  ;extract valid portion of the entries (depending on ATTRIBUTE name)
  tchk=STRSPLIT(ta1[j],';',/Extract)
  ta1[j]=STRCOMPRESS(tchk[0],/Remove_All)
  IF nel GT 1 THEN $
    FOR k=1,nel-1 DO ta1[j]=ta1[j]+';'+STRCOMPRESS(tchk[k],/Remove_All)
ENDFOR
IF ta2[0] NE '' THEN BEGIN
  FOR j=0,N_ELEMENTS(ta2)-1 DO BEGIN
    ;extract valid portion of the entries (depending on ATTRIBUTE name)
    tchk=STRSPLIT(ta2[j],';',/Extract)
    ta2[j]=STRCOMPRESS(tchk[ti],/Remove_All)
  ENDFOR
ENDIF
IF cpos EQ '_' THEN BEGIN
  gi=WHERE(ta1 EQ achk[0],gcnt)
  IF gcnt NE 0 THEN gi=WHERE(ta2 EQ achk[1],gcnt)
ENDIF ELSE BEGIN ;Check for Case Sensitive or incorrect apostrophe problem
  gi=WHERE(ta1 EQ achk,gcnt)
  IF gcnt EQ 0 THEN BEGIN
    ;Check for Case Sensitivity and/or incorrect apostrophe usage - will be fixed in CHECK_METADATA
    gi=WHERE(STRLOWCASE(ta1) EQ STRLOWCASE(achk),gcnt)
    IF gcnt NE 0 THEN dentry=ta1[gi[0]] ELSE BEGIN
      ;Check for "`" instead of "'" in metadata entry
      IF STRPOS(achk,'`') NE -1 THEN BEGIN
        achkh=achk
        WHILE STRPOS(achkh,'`') NE -1 DO STRPUT,achkh,'''',STRPOS(achkh,'`')
        gi=WHERE(STRLOWCASE(ta1) EQ STRLOWCASE(achkh),gcnt)
        IF gcnt NE 0 THEN dentry=ta1[gi[0]]
      ENDIF
    ENDELSE
  ENDIF
ENDELSE

IF gcnt EQ 0 THEN BEGIN
  IF STRPOS(taname,'ORIGINATOR') NE -1 THEN BEGIN ;Log message only rather than STOP_WITH_ERROR
    gi=-3 & ti=-3 ;error code returned to CHECK_METADATA procedure
    infotxt='3 '+STRMID(taname,STRPOS(taname,'/')+1)+'='+aname+' doesn''t match any '
    infotxt=infotxt+'Table Attribute Values under ORIGINATOR field'
    INFOTXT_OUTPUT,infotxt
  ENDIF ELSE STOP_WITH_ERROR,o3[3]+proname+aname+': ',errtxt2[1]+taname,lu & RETURN
ENDIF
ti=gi ;ti returned to the Check_MetaData procedure to check AFFILIATION, ADDRESS and EMAIL values

END ;procedure Extract_and_Test



PRO check_metadata
;Procedure to check the validity of Metadata values by checking them against the corresponding
;entries in the Table Attribute Values File
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20050802: Original IDLCR8HDF Routine - Version 1.0
;    20050909: 'rd' flag included to convert VAR_SI_CONVERSION values to floating point if the
;              corresponding VAR_DATA_TYPE is real or double; Section included to check for
;              repeated SI units in the calculated VAR_SI_CONVERSION - Version 1.1
;    20061012: Section added to do simple checks on Metadata ORIGINATOR values if the information
;              is not otherwise available in the TAV file; Warning messages written to output
;              windows and/or log file depending on the options chosen by the user; Section relating
;              to checks on VAR_UNITS and VAR_SI_CONVERSION moved to the VAR_UNITS_TEST routine;
;              Common variable definition WIDGET_WIN added - Version 2.0
;    20080302: Sections included to handle checks when an Envisat table.dat file is used, including;
;              ensuring metadata labels DATA_TYPE and VAR_DATA_TYPE are not both found when using the
;              Strpos procedure; Handling different table.dat format of ORIGINATOR attributes; using
;              DATA_SOURCE_02 instead of AFFILIATION for the DATA_SOURCE checks. Section which puts
;              TAV file VAR_UNITS and UNIT_PREFIX values into arrays for the VAR_UNITS_TEST call is
;              no longer needed and is removed; Change made so that Free Attribute Metadata values
;              which include semi-colons do not have white space removed (i.e. the semi-colons are
;              not defined as separating sub-values) - Version 3.0
;    20091203: Account for the situation when a VAR_NAME does not include a Variable Mode, but still
;              includes a Variable Descriptor ('__' will be present in the name) - Version 3.08
;    20100205: Add RETURN command after all STOP_WITH_ERROR calls, which allows program to return to the
;              calling program if the reterr argument is included in the idlcr8hdf call - Version 3.09
;    20101120: Do check for MJD2000 VAR_UNIT, and change to MJD2K; Check for LONG datatype (now refers to
;              LONG64) and change to INTEGER (now means LONG32) for TAV checks - Version 4.0b0
;    20121015: Change VAR_SI_CONVERSION information/error message so will also report if the
;              VAR_SI_CONVERSION label does not have an accompanying value - Version 4.0b13
;
;  Inputs: meta_arr - a string array containing the Global and Variable Attributes
;          tab_arr - a string array containing the TAV or table.dat file attributes

;  Output: meta_arr - some meta_arr values may be corrected or calculated in this routine. White space
;                     between metadata sub-values is also removed.
;
;  Called by: IDLCR8HDF
;
;  Subroutines Called: EXTRACT_AND_TEST
;                      VAR_UNITS_TEST
;                      GEOMS_RULE_CHANGES
;                      STOP_WITH_ERROR (if error state detected); INFOTXT_OUTPUT
;    Possible Conditions for STOP_WITH_ERROR call (plus [line number] where called):
;      1. An attribute value is expected but is absent or invalid
;      2. Incorrect number of (sub-)values for a particular Metadata attribute
;      3. NAME and AFFILIATION values don't match (only applies if reading in the full AVDC
;         TAV file)
;      4. AFFILIATION (AVDC) or DATA_SOURCE_02 (Envisat) field not found in the TAV file
;      5. There is no match between a given VAR_UNIT, and the list of valid units and prefixes
;         present in the TAV file
;      6. VAR_UNITS value is not valid
;
;    Information Conditions (when the program is able to make changes):
;      1. ORIGINATOR values for ADDRESS or EMAIL replaced with those from the TAV file
;      2. VAR_SI_CONVERSION values replaced with those calculated by the program

COMMON TABLEDATA
COMMON METADATA
COMMON WIDGET_WIN

;Possible error messages for this procedure
proname='Check_Metadata procedure: ' & lu=-1L
errtxt=STRARR(4)
errtxt[0]='No or Invalid value for this Attribute: '
errtxt[1]='Number of (sub-)values for this Attribute should be '
errtxt[2]='AFFILIATION value doesn''t match NAME value: '
errtxt[3]=' field not found in the input Table Attribute Values file'

;Variable Attributes which have user defined values
free_attr=['DATA_DESCRIPTION','DATA_MODIFICATIONS','DATA_CAVEATS',$
           'DATA_RULES_OF_USE','DATA_ACKNOWLEDGEMENT',$
           'VAR_DESCRIPTION','VAR_NOTES']

;originator values that need to be checked - ADDRESS and EMAIL derived automatically
orig_attr=['PI_','DO_','DS_','NAME','AFFILIATION']
;initialize variables for VAR_UNITS/VAR_SI_CONVERSION checks
firstvu=0 & tchk='' & rd=1 & writeonce=0
xval=[2,2,3,1] ;expected number of sub-values for the four originator attributes
new_name=[''] ;Entry which will contain any ORIGINATOR name values not present in the TAV file

FOR i=0,N_ELEMENTS(meta_arr)-1 DO BEGIN
  res=STRSPLIT(meta_arr[i],'=',/Extract,COUNT=nres)
  IF res[0] EQ 'VAR_NAME' THEN vnval=meta_arr[i]
  FOR j=0,2 DO FOR k=3,4 DO $
    ;need to change ORIGINATOR NAME ATTRIBUTE names to match TAV File
    IF res[0] EQ orig_attr[j]+orig_attr[k] THEN BEGIN
      IF k EQ 3 THEN res[0]='ORIGINATOR' ELSE res[0]='AFFILIATION'
      jh=j & kh=k
    ENDIF
  ;Test whether metadata label is also a TAV field
  ;First test checks for exact match between metadata label and TAV field
  ;(This avoids possible problem using STRPOS (e.g. DATA_TYPE won't also pick up VAR_DATA_TYPE))
  mi=WHERE(tab_arr[*,0] EQ res[0],mcnt)
  ;Back-up test in the event that label has more than one TAV field (e.g. DATA_VARIABLES)
  IF mcnt EQ 0 THEN mi=WHERE(STRPOS(tab_arr[*,0],res[0]) EQ 0,mcnt) ;was NE -1

  IF res[0] EQ 'AFFILIATION' THEN BEGIN
    ;If tab_type EQ 0 (AVDC) then perform AFFILIATION checks below only if the ORIGINATOR field in the
    ;TAV file is missing. If tab_type EQ 1 (original Envisat) then perform AFFILIATION checks below.
    IF tab_type EQ 0 THEN BEGIN ;AVDC type TAV file
      ai=WHERE(STRPOS(tab_arr[*,0],'ORIGINATOR') NE -1,acnt)
      IF acnt NE 0 THEN BEGIN
        ;ORIGINATOR field present in the TAV file so no need to do separate checks
        ;using the AFFILIATION field as all the information is in the ORIGINATOR field.
        res[0]=orig_attr[jh]+orig_attr[kh]
        mi=WHERE(STRPOS(tab_arr[*,0],res[0]) NE -1,mcnt)
      ENDIF
    ENDIF
  ENDIF

  IF (res[0] EQ 'ORIGINATOR') AND ((mcnt EQ 0) OR (tab_type EQ 1)) THEN BEGIN
    ;Do simple checks on _NAME, _AFFILIATION, _ADDRESS, and _EMAIL sub-values
    FOR k=0,3 DO BEGIN
      resx=STRSPLIT(meta_arr[i+k],'=;')
      nel=N_ELEMENTS(resx)-1
      IF (nel NE xval[k]) OR (STRMID(meta_arr[i+k],STRLEN(meta_arr[i+k])-1,1) EQ ';') THEN BEGIN
        STOP_WITH_ERROR,o3[3]+proname+meta_arr[i+k]+': ',errtxt[1]+STRTRIM(xval[k],2)+'.',lu
        RETURN
      ENDIF
    ENDFOR
  ENDIF

  IF mcnt NE 0 THEN BEGIN ;check Metadata value(s) against TAV file entries
    IF (nres NE 2) AND (rd NE 0) AND (res[0] NE 'ORIGINATOR') THEN BEGIN
      STOP_WITH_ERROR,o3[3]+proname,errtxt[0]+meta_arr[i],lu & RETURN
    ENDIF ELSE IF res[0] EQ 'ORIGINATOR' THEN BEGIN
      ;perform checks on the ORIGINATOR attributes
      IF nres LT 2 THEN BEGIN ;invalid originator value so add dummy value
        aname='[MISSING]' & res=[res[0],'[MISSING;MISSING]']
      ENDIF ELSE aname=res[1]
      res[0]=orig_attr[jh]+orig_attr[3]
      ti=-1
      ta1=tab_arr[mi[0],2:tab_arr[mi[0],1]+1] ;subset of relevant FIELD ENTRIES
      taname=tab_arr[mi[0],0]+'/'+res[0] ;name combination for error message
      dentry=res[1]
      EXTRACT_AND_TEST,dentry,';',xval[0],ta1,[''],taname,aname,ti
      IF STRLEN(rerr[0]) GT 2 THEN RETURN
      IF ti[0] EQ -3 THEN BEGIN ;no match with ORIGINATOR name value so report DEBUG message
        ;Check if name already tested
        IF new_name[0] EQ '' THEN new_name[0]=res[1] $ ;add new name to array
        ELSE new_name=[new_name,res[1]] ;append new name to the array
        nfd=WHERE(res[1] EQ new_name,ncnt)
        IF ncnt EQ 1 THEN BEGIN ;first time this name has been found so include message
          new_entry=res[1] ;given ORIGINATOR name value or [EMPTY;EMPTY]
          FOR j=1,3 DO BEGIN
            ;extract attribute value(s) from Metadata file
            res=STRSPLIT(meta_arr[i+j],'=',/Extract,COUNT=nori)
            IF nori GE 2 THEN BEGIN ;assume valid originator value
              ;remove leading and trailing blanks from each sub-value of res[1]
              achk2=STRSPLIT(res[1],';',/Extract)
              nel=N_ELEMENTS(achk2)
              res[1]=STRTRIM(achk2[0],2)
              IF nel GT 1 THEN FOR m=1,nel-1 DO res[1]=res[1]+';'+STRTRIM(achk2[m],2)
              new_entry=new_entry+';'+res[1]
            ENDIF ELSE BEGIN ;add [EMPTY;..] text
              FOR m=0,xval[j]-1 DO BEGIN
                IF xval[j] EQ 1 THEN new_entry=new_entry+';[MISSING]' $
                ELSE IF m EQ 0 THEN new_entry=new_entry+';[MISSING;' $
                ELSE IF m EQ xval[j]-1 THEN new_entry=new_entry+'MISSING]' $
                ELSE new_entry=new_entry+'MISSING;'
              ENDFOR
            ENDELSE
          ENDFOR
          new_entry=new_entry+';1'
          infotxt=STRARR(3)
          infotxt[0]='4 Provisional make-up of entry required in the TAV file in the ORIGINATOR field,'
          infotxt[0]=infotxt[0]+' based on the'
          infotxt[1]='    GEOMS file values. Note that values may be missing or invalid, or may not'
          infotxt[1]=infotxt[1]+' conform to GEOMS Standard:'
          infotxt[2]='    ='+new_entry
          INFOTXT_OUTPUT,infotxt
        ENDIF
      ENDIF ELSE IF dentry NE res[1] THEN BEGIN
        ;Case and/or apostrophe differences between Metadata entry and TAV entry
        achk2=STRSPLIT(tab_arr[mi[0],ti[0]+2],';',/Extract)
        achk=STRTRIM(achk2[0],2)
        FOR m=1,xval[0]-1 DO achk=achk+';'+STRTRIM(achk2[m],2)
        IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN itxt=' should be ' ELSE itxt=' replaced with '
        infotxt='2 '+meta_arr[i]+itxt+res[0]+'='+achk+' based on the TAV entry'
        INFOTXT_OUTPUT,infotxt
        meta_arr[i]=res[0]+'='+achk
      ENDIF
      IF (tab_type EQ 0) AND (ti[0] NE -3) THEN BEGIN
        ;check/update AFFILIATION, ADDRESS and EMAIL values according to returned tab_arr index(es) (ti)
        n_ti=N_ELEMENTS(ti)
        FOR j=1,3 DO BEGIN
          ;extract attribute value(s) from Metadata file
          res=STRSPLIT(meta_arr[i+j],'=',/Extract,COUNT=nori)
          IF nori EQ 2 THEN BEGIN
            ;remove leading and trailing blanks from each sub-value
            achk2=STRSPLIT(res[1],';',/Extract)
            nel=N_ELEMENTS(achk2)
            res[1]=STRTRIM(achk2[0],2)
            IF nel GT 1 THEN FOR k=1,nel-1 DO res[1]=res[1]+';'+STRTRIM(achk2[k],2)
          ENDIF
          ;check against the TAV(s) returned for the NAME attribute
          IF j EQ 1 THEN BEGIN ;AFFILIATION
            IF (nori NE 2) AND (n_ti NE 1) THEN BEGIN
              ;No Affiliation and cannot determine from TAV
              STOP_WITH_ERROR,o3[3]+proname,errtxt[0]+meta_arr[i],lu & RETURN
            ENDIF
            si=2 & kh=-1
          ENDIF ELSE IF j EQ 2 THEN si=4 $;ADDRESS
          ELSE si=7 ;EMAIL
          ;make up correct set of values from the table attribute file
          FOR k=0,n_ti-1 DO BEGIN ;in the event that the NAME is listed twice
            IF (kh EQ k) OR (j EQ 1) THEN BEGIN ;Extract values from the selected TAV input(s)
              achk2=STRSPLIT(tab_arr[mi[0],ti[k]+2],';',/Extract)
              achk=STRTRIM(achk2[si],2)
              IF xval[j] GT 1 THEN FOR m=si+1,si+xval[j]-1 DO achk=achk+';'+STRTRIM(achk2[m],2)
              IF (j EQ 1) AND (n_ti NE 1) THEN BEGIN
                ;More than one instance of the NAME in the TAV file so check against AFFILIATION
                IF STRUPCASE(achk) EQ STRUPCASE(res[1]) THEN BEGIN
                  kh=k & meta_arr[i+j]=res[0]+'='+achk
                ENDIF
              ENDIF ELSE IF (j GE 2) OR ((j EQ 1) AND (n_ti EQ 1)) THEN BEGIN
                ;Check that metadata AFFILIATION, ADDRESS and EMAIL values are valid, if present
                IF nori NE 2 THEN BEGIN
                  IF nori LT 2 THEN res=[res[0],'[MISSING]'] $
                  ELSE FOR m=2,nori-1 DO res[1]=res[1]+'='+res[m] ;recreate full value
                ENDIF
                IF res[1] NE achk THEN BEGIN
                  infotxt=STRARR(2)
                  infotxt[0]='2 '+res[0]+' values do not match those in the Table Attribute Values file|, '
                  infotxt[0]=infotxt[0]+'and replaced:'
                  infotxt[1]='    '+res[1]+' -> '+achk
                  INFOTXT_OUTPUT, infotxt
                ENDIF
                IF j EQ 1 THEN kh=k
                meta_arr[i+j]=res[0]+'='+achk
              ENDIF
            ENDIF
          ENDFOR
          IF kh EQ -1 THEN BEGIN ;metadata AFFILIATION not valid
            STOP_WITH_ERROR,o3[3]+proname+res[1]+': ',errtxt[2]+meta_arr[i],lu & RETURN
          ENDIF
        ENDFOR
      ENDIF
    ENDIF ELSE IF res[0] EQ 'AFFILIATION' THEN BEGIN
      res[0]=orig_attr[jh]+orig_attr[4]
      IF N_ELEMENTS(res) NE 2 THEN BEGIN
        STOP_WITH_ERROR,o3[3]+proname,errtxt[0]+meta_arr[i],lu & RETURN
      ENDIF
      ta1=tab_arr[mi[0],2:tab_arr[mi[0],1]+1] ;subset of relevant FIELD ENTRIES
      taname=tab_arr[mi[0],0]+'/'+res[0] ;name combination for error message
      dentry=res[1] & ti=-1
      EXTRACT_AND_TEST,dentry,';',xval[1],ta1,[''],taname,res[1],ti
      IF STRLEN(rerr[0]) GT 2 THEN RETURN
      IF dentry NE res[1] THEN BEGIN
        ;Case and/or apostrophe differences between Metadata entry and TAV entry
        achk2=STRSPLIT(tab_arr[mi[0],ti[0]+2],';',/Extract)
        achk=STRTRIM(achk2[0],2)
        FOR m=1,xval[1]-1 DO achk=achk+';'+STRTRIM(achk2[m],2)
        IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN itxt=' should be ' ELSE itxt=' replaced with '
        infotxt='2 '+meta_arr[i]+itxt+res[0]+'='+achk+' based on the TAV entry'
        INFOTXT_OUTPUT,infotxt
        meta_arr[i]=res[0]+'='+achk
      ENDIF
    ENDIF ELSE IF res[0] EQ 'DATA_SOURCE' THEN BEGIN
      ;need to test against 'DATA_SOURCE' and 'AFFILIATION' (AVDC) or 'DATA_SOURCE_02'
      ;(original Envisat) entries
      ta1=tab_arr[mi[0],2:tab_arr[mi[0],1]+1] ;DATA_SOURCE ENTRIES
      IF tab_type EQ 0 THEN BEGIN
        atxt='AFFILIATION' & atx='' & ti=1
      ENDIF ELSE BEGIN
        atxt='DATA_SOURCE_02' & atx='_01' & ti=0
      ENDELSE
      ai=WHERE(STRPOS(tab_arr[*,0],atxt) NE -1,acnt)
      IF acnt EQ 0 THEN BEGIN
        STOP_WITH_ERROR,o3[3]+proname,atxt+errtxt[3],lu & RETURN
      ENDIF
      ta2=tab_arr[ai[0],2:tab_arr[ai[0],1]+1] ;AFFILIATION/DATA_SOURCE_02 ENTRIES
      taname=res[0]+atx+'/'+tab_arr[ai[0],0] ;name combination for error message
      EXTRACT_AND_TEST,res[1],'_',2,ta1,ta2,taname,res[1],ti
      IF STRLEN(rerr[0]) GT 2 THEN RETURN
    ENDIF ELSE IF res[0] EQ 'DATA_VARIABLES' THEN BEGIN
      ;make into 2-D array and separate out the components of the VAR_NAMES
      achk=STRSPLIT(res[1],';',/Extract)
      nel=N_ELEMENTS(achk)
      achk2=STRARR(mcnt,nel)
      FOR j=0,nel-1 DO BEGIN
        dv=STRSPLIT(achk[j],'_',/Extract,Count=n_dv)
        IF n_dv GT mcnt THEN BEGIN ;invalid VAR_NAME composition
          STOP_WITH_ERROR,o3[3]+proname,errtxt[0]+res[0]+'='+achk[j],lu & RETURN
        ENDIF
        achk2[0:N_ELEMENTS(dv)-1,j]=dv
      ENDFOR
      FOR j=0,nel-1 DO BEGIN
        dv=WHERE(achk2[*,j] NE '',dvcnt)
        FOR k=0,mcnt-1 DO BEGIN
          IF achk2[k,j] NE '' THEN BEGIN
            taname=tab_arr[mi[k],0]
            ta1=REFORM(tab_arr[mi[k],2:tab_arr[mi[k],1]+1]) ;subset of TAV DATA_VARIABLES entries
            IF (k NE 0) AND (dvcnt EQ 2) THEN BEGIN
              ;need to check both variable mode and descriptor options
              FOR m=k+1,mcnt-1 DO BEGIN
                taname=taname+'/'+tab_arr[mi[m],0]
                ta1=[ta1,REFORM(tab_arr[mi[m],2:tab_arr[mi[m],1]+1])]
              ENDFOR
            ENDIF
            EXTRACT_AND_TEST,achk2[k,j],';',1,ta1,[''],taname,achk[j],0
            IF STRLEN(rerr[0]) GT 2 THEN RETURN
          ENDIF
        ENDFOR
      ENDFOR
    ENDIF ELSE IF res[0] EQ 'FILE_ACCESS' THEN BEGIN
      ;need to check each Metadata entry individually
      achk=STRSPLIT(res[1],';',/Extract)
      nel=N_ELEMENTS(achk)
      ta1=tab_arr[mi[0],2:tab_arr[mi[0],1]+1] ;FILE_ACCESS entries
      FOR j=0,nel-1 DO BEGIN
        EXTRACT_AND_TEST,achk[j],';',1,ta1,[''],res[0],achk[j],0
        IF STRLEN(rerr[0]) GT 2 THEN RETURN
      ENDFOR
    ENDIF ELSE IF res[0] EQ 'FILE_META_VERSION' THEN BEGIN
      ;only need to look at the second value
      achk=STRSPLIT(res[1],';',/Extract)
      IF N_ELEMENTS(achk) NE 2 THEN BEGIN
        STOP_WITH_ERROR,o3[3]+proname+meta_arr[i]+': ',errtxt[1]+'2.',lu & RETURN
      ENDIF
      achk=[STRTRIM(achk[1],2)]
      ta1=tab_arr[mi[0],2:tab_arr[mi[0],1]+1] ;FILE_META_VERSION entries
      EXTRACT_AND_TEST,achk[0],';',1,ta1,[''],res[0],achk[0],0
      IF STRLEN(rerr[0]) GT 2 THEN RETURN
    ENDIF ELSE IF res[0] EQ 'VAR_UNITS' THEN BEGIN
      ;VAR_UNITS and VAR_SI_CONVERSION entries (not needed for STRING data type)
      IF rd NE 0 THEN BEGIN
        IF STRUPCASE(res[1]) EQ 'MJD2000' THEN BEGIN ;change to MJD2K
          in1=meta_arr[i] & in2=res[1]
          GEOMS_RULE_CHANGES,3,in1,in2,writeonce
          meta_arr[i]=in1 & res[1]=in2
          writeonce=1
        ENDIF
        errstate=''
        VAR_UNITS_TEST,res[1],rd,tab_type,tchk,errstate
        IF errstate NE '' THEN BEGIN ;VAR_UNIT value not valid
          STOP_WITH_ERROR,o3[3]+proname+STRMID(errstate,0,STRPOS(errstate,':')+2), $
                          STRMID(errstate,STRPOS(errstate,':')+2),lu
          RETURN
        ENDIF
        ;Find VAR_SI_CONVERSION meta attribute
        k=1
        WHILE STRMID(meta_arr[i+k],0,17) NE 'VAR_SI_CONVERSION' DO k++
        achk=STRSPLIT(meta_arr[i+k],'=',/Extract) ;VAR_SI_CONVERSION values
        IF N_ELEMENTS(achk) EQ 1 THEN achk=[achk,' ']
        ;check calculated VAR_SI_CONVERSION value against existing value in the metadata
        IF achk[1] NE tchk THEN BEGIN
          IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN itxt=' should be ' ELSE itxt=' replaced with '
          infotxt='2 '+meta_arr[i+k]+itxt+'VAR_SI_CONVERSION='+tchk+' for '+vnval
          INFOTXT_OUTPUT, infotxt
        ENDIF
        meta_arr[i+k]=achk[0]+'='+tchk
      ENDIF
    ENDIF ELSE BEGIN ;perform checks on the remaining ATTRIBUTE_NAMES
      achk=STRSPLIT(res[1],';',/Extract)
      achk=STRTRIM(achk,2)
      nel=N_ELEMENTS(achk) & ta2=['']
      IF res[0] EQ 'VAR_DATA_TYPE' THEN BEGIN
        ;to convert VAR_SI_CONVERSION values to floating point if necessary
        CASE 1 OF
          (STRUPCASE(res[1]) EQ 'REAL') OR (STRUPCASE(res[1]) EQ 'DOUBLE'): rd=-1
          STRUPCASE(res[1]) EQ 'STRING': rd=0
          ELSE: rd=1
        ENDCASE
        IF STRUPCASE(achk[0]) EQ 'LONG' THEN achk[0]='INTEGER'
        ;Changed to INTEGER for EXTRACT_AND_TEST only - actual change occurs in SET_UP_STRUCTURE
      ENDIF
      IF (nel NE mcnt) OR (STRMID(meta_arr[i],STRLEN(meta_arr[i])-1,1) EQ ';') THEN BEGIN
        STOP_WITH_ERROR,o3[3]+proname+meta_arr[i]+': ',errtxt[1]+STRTRIM(mcnt,2)+'.',lu
        RETURN
      ENDIF
      nel=1
      FOR j=0,mcnt-1 DO BEGIN
        ta1=tab_arr[mi[j],2:tab_arr[mi[j],1]+1] ;subset of relevant ENTRIES
        dentry=achk[j] & ti=mi[j]
        EXTRACT_AND_TEST,dentry,';',nel,ta1,ta2,tab_arr[mi[j],0],achk[j],ti
        IF STRLEN(rerr[0]) GT 2 THEN RETURN
        IF (mcnt EQ 1) AND (dentry NE achk[j]) THEN BEGIN
          ;Case and/or apostrophe differences between Metadata entry and TAV entry
          achk2=STRSPLIT(tab_arr[mi[j],ti[0]+2],';',/Extract)
          achk=STRTRIM(achk2[0],2)
          IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN itxt=' should be ' ELSE itxt=' replaced with '
          infotxt='2 '+meta_arr[i]+itxt+res[0]+'='+achk+' based on the TAV entry'
          INFOTXT_OUTPUT,infotxt
          meta_arr[i]=res[0]+'='+achk
        ENDIF
        IF j EQ 0 THEN ta2[0]=''
      ENDFOR
    ENDELSE
  ENDIF
  ;Check for and remove white spaces between sub-values (except for the Free_Attributes)
  eqpos=STRPOS(meta_arr[i],'=')
  lab=STRMID(meta_arr[i],0,eqpos)
  IF eqpos NE STRLEN(meta_arr[i])-1 THEN BEGIN
    val=STRMID(meta_arr[i],eqpos+1) & val=STRTRIM(val,2)
    fi=WHERE(lab EQ free_attr,fcnt)
    IF fcnt EQ 0 THEN BEGIN ;ie. is not a Free Attribute
      res=STRSPLIT(val,';',/Extract)
      res=STRTRIM(res,2)
      meta_arr[i]=lab+'='+res[0]
      IF N_ELEMENTS(res) GT 1 THEN FOR j=1,N_ELEMENTS(res)-1 DO meta_arr[i]=meta_arr[i]+';'+res[j]
    ENDIF ELSE meta_arr[i]=lab+'='+val
  ENDIF
ENDFOR

END ;Procedure Check_Metadata



PRO extract_data, sds, inf, vc, dtest, ndl
;Procedure to extract the set of data corresponding to a particular Variable Attribute
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20050802: Introduced to IDLCR8HDF, originally part of the READ_DATA procedure - Version 1.0
;    20050909: After reading in a data segment according to the VAR_SIZE values, check the next line to
;              ensure it is not a further data point (i.e. there are more data points than specified by
;              VAR_SIZE); If sds is a structure, and there is only one data point then return dtest as
;              an array rather than a scalar - Version 1.1
;    20061012: The portion of READ_DATA dealing with extracting a specific data segment renamed
;              EXTRACT_DATA - Version 2.0
;    20080302: The sets of data values in a file can now be in any order, rather than the same order as
;              that given by the DATA_VARIABLES attribute; dtest used as an input flag to indicate
;              whether the procedure call is from SET_UP_STRUCTURE [-1] or READ_DATA [1]. If from
;              SET_UP_STRUCTURE then only the number of data lines (ndl) is determined by the routine;
;              an error is generated in the case where the same VAR_NAME is repeated in the data file;
;              Error messages clarified when an incorrect number of data values are found in the
;              input data file - Version 3.0
;    20100205: Add RETURN command after all STOP_WITH_ERROR calls, which allows program to return to the
;              calling program if the reterr argument is included in the idlcr8hdf call - Version 3.09
;    20130116: Account for empty string data values in a dataset - previously '' values ignored in an
;              input data file - Version 4.0b15  
;
;  Inputs: sds - Either a structure containing the Variable Attributes and Data, or the input
;                data file
;          inf - flag identifying sds type where, 0=structure; 1=data file
;          vc - the index value of the vn array holding the VAR_NAME being searched for in the data
;               file, or the index value of the sds structure which holds the data
;          dtest - a single string array to show which procedure called this routine, either
;                  SET_UP_STRUCTURE [-1], or READ_DATA [1]
;
;  Outputs: dtest - a string array of size ndl, which holds the data values
;           ndl - The total number of data lines i.e. the product of the VAR_SIZE values
;
;  Called by: SET_UP_STRUCTURE; READ_DATA
;
;  Subroutines Called: STOP_WITH_ERROR (if error state detected)
;    Possible Conditions for STOP_WITH_ERROR call (plus [line number] where called):
;      1. EOF encountered when trying to find the VAR_NAME or while attempting to read in data
;         [2146,2220,2221]
;      2. Invalid data point found in the dataset [2193]
;      3. Two instances of the same VAR_NAME found in the input data file [2204]
;      4. Too many data values present in the dataset or the next line in the file is invalid [2211]
;      5. Number of data values does not match product of VAR_SIZE [2237]
;      6. ISO8601 datetime format not valid [2253]

COMMON DATA
COMMON WIDGET_WIN

;possible error messages for this procedure
errtxt=STRARR(10)
errtxt[0]='EOF encountered but not expected'
errtxt[1]=' when trying to find VAR_NAME in '
errtxt[2]=' when trying to determine VAR_SIZE for VAR_NAME='
errtxt[3]=' - Number of data lines should be '
errtxt[4]='Invalid data point found in the dataset at line '
errtxt[5]='Two instances of this VAR_NAME present in the Data File'
errtxt[6]='Too many data values present in the dataset or invalid data line entry following the dataset'
errtxt[7]='Number of data values does not match product of VAR_SIZE: '
errtxt[8]='ISO8601 format not valid: '
errtxt[9]='Unable to determine correct number of data values due to VAR_SIZE calculation error'
proname='Extract_Data procedure: '

ndl=1L ;initialize data line count
vsi=WHERE(vserror EQ vn[vc],vcnt) ;check whether there is a VAR_SIZE calculation error for this dataset
sdata=ndm(vc,8) EQ 6 ;Check for String data type

IF inf EQ 1 THEN BEGIN ;Find the first data value for the requested VAR_NAME
  ON_IOERROR,TypeConversionError
  dum='' & vntest=vn[vc]
  ;Add check in case VAR_NAME has been changed from original input
  IF vnchange[vc] NE '' THEN vntest=vnchange[vc]
  OPENR,lu,sds,/GET_LUN
  IF NOT EOF(lu) THEN BEGIN ;read through data file until the correct Variable Name is found
    REPEAT READF,lu,dum UNTIL (EOF(lu)) OR (STRTRIM(STRUPCASE(dum),2) EQ STRUPCASE(vntest)) OR $
                              (STRTRIM(STRUPCASE(dum),2) EQ STRUPCASE(vn[vc]))
  ENDIF
  IF STRTRIM(STRUPCASE(dum),2) EQ STRUPCASE(vn[vc]) THEN vntest=vn[vc]
  IF EOF(lu) THEN BEGIN
    STOP_WITH_ERROR,o3[3]+proname+vn[vc],errtxt[0]+errtxt[1]+sds,lu,ds & RETURN
  ENDIF

  ;Find first data point
  dum='!'
  valid=-1 ;set to test for successful line read
  WHILE (STRMID(dum,0,1) EQ '!') OR (STRMID(dum,0,1) EQ '#') OR ((~sdata) AND (dum EQ '')) DO BEGIN
    READF,lu,dum & dum=STRTRIM(dum,2)
  ENDWHILE
  valid=1 ;i.e. got to here without prematurely reaching the eof so first data point found OK

  IF dtest[0] EQ '-1' THEN BEGIN ;need to determine the total number of data lines only (ndl)
    IF NOT EOF(lu) THEN BEGIN
      ;read through until eof or comment line or another VAR_NAME is reached
      REPEAT BEGIN
        READF,lu,dum
        dum=STRTRIM(STRUPCASE(dum),2)
        bi=WHERE(dum EQ STRUPCASE(vn))
        IF (STRMID(dum,0,1) NE '!') AND (STRMID(dum,0,1) NE '#') AND $
           ((dum NE '') OR ((sdata) AND (dum EQ ''))) AND (bi[0] EQ -1) THEN incnt=1L $
        ELSE incnt=0L
        ndl=ndl+incnt ;presume it is a valid data line so add to total
      ENDREP UNTIL (incnt EQ 0L) OR (EOF(lu))
    ENDIF
  ENDIF ELSE BEGIN ;return dtest and ndl
    di=WHERE(ndm[vc,0:7] NE 0L,ndim)
    ;multiply together the array dimensions to determine expected total number of datalines
    FOR i=0,ndim-1 DO ndl=ndl*ndm[vc,di[i]]
    ;attempt to read any remaining data values
    IF ndl GT 1L THEN BEGIN
      valid=0 ;set to test for successful block read
      dtest=STRARR(ndl-1) & READF,lu,dtest
      valid=1 ;i.e. got to here without prematurely reaching the EOF so block read was OK
      dtest=[dum,dtest] ;add first value to dtest
    ENDIF ELSE dtest=[dum]
    dtest=STRTRIM(dtest,2) & dtestup=STRUPCASE(dtest)
    ;Test to see if any of the 'data' read in is a VAR_NAME - if so bcnt will NE 0 (and will generate error message)
    bcnt=0 & i=0
    WHILE (bcnt EQ 0) AND (i LE nvn-1) DO BEGIN
      bi=WHERE(dtestup EQ STRUPCASE(vn[i]),bcnt)
      IF bcnt EQ 0 THEN i=i+1
    ENDWHILE
    ;Test to see if any of the 'data' read in is not a valid data point - if so bcnt will NE 0
    IF bcnt EQ 0 THEN $
      bi=WHERE((STRMID(dtest,0,1) EQ '!') OR (STRMID(dtest,0,1) EQ '#') OR $
               ((dtest EQ '') AND (~sdata)) OR (dtestup EQ STRUPCASE(vntest)),bcnt)

    IF bcnt NE 0 THEN BEGIN ;Non-valid data point found in the dataset
      STOP_WITH_ERROR,o3[3]+proname+vn[vc]+': ',errtxt[4]+STRTRIM(bi[0]+1,2)+errtxt[3]+ $
                      STRTRIM(ndl,2),lu,ds
      RETURN
    ENDIF

    ;Read next line if not EOF to test for the correct number of data lines
    IF NOT EOF(lu) THEN READF,lu,dum ELSE dum='!'
    dum=STRTRIM(STRUPCASE(dum),2)
    ;Test to see if the next line read in is another VAR_NAME - if not then bi[0] will equal -1
    bi=WHERE(dum EQ STRUPCASE(vn))
    IF bi[0] EQ vc THEN BEGIN ;Same VAR_NAME found twice in the data file
      STOP_WITH_ERROR,o3[3]+proname+vn[vc]+': ',errtxt[5],lu,ds & RETURN
    ENDIF
    IF (bi[0] EQ -1) AND (dum NE '!') THEN bi=WHERE(dum EQ STRUPCASE(vnchange))
    ;Test to check if the next line read in is another data point - if so bcnt will be set to 1
    IF (STRMID(dum,0,1) NE '!') AND (STRMID(dum,0,1) NE '#') AND $
       ((dum NE '') OR ((sdata) AND (dum EQ ''))) AND (bi[0] EQ -1) THEN $
      bcnt=1
    IF bcnt NE 0 THEN BEGIN ;not enough data lines read in or next line in the file is invalid
      IF vcnt NE 0 THEN STOP_WITH_ERROR,o3[3]+proname+'VAR_NAME='+vn[vc]+': ',errtxt[9],lu,ds $
      ELSE $
        STOP_WITH_ERROR,o3[3]+proname+'VAR_NAME='+vn[vc]+': ',errtxt[6]+errtxt[3]+STRTRIM(ndl,2),lu,ds
      RETURN
    ENDIF
  ENDELSE
  FREE_LUN,lu

  TypeConversionError:
  IF valid LE 0 THEN BEGIN ;EOF encountered but not expected
    IF (dtest[0] EQ '-1') AND (valid EQ -1) THEN $
      STOP_WITH_ERROR,o3[3]+proname,errtxt[0]+errtxt[2]+vn[vc],lu,ds $
    ELSE BEGIN
      ;Check to see if it is due to a VAR_SIZE calculation error or not
      IF vcnt NE 0 THEN STOP_WITH_ERROR,o3[3]+proname+'VAR_NAME='+vn[vc]+': ',errtxt[9],lu,ds $
      ELSE $
        STOP_WITH_ERROR,o3[3]+proname+'VAR_NAME='+vn[vc]+': ',errtxt[0]+errtxt[3]+STRTRIM(ndl,2),lu,ds
    ENDELSE
    RETURN
  ENDIF
ENDIF ELSE BEGIN ;sds is a structure
  IF dtest[0] EQ '-1' THEN BEGIN ;determine the total number of data lines only
    dtest=*sds[vc].data
    ndl=LONG(N_ELEMENTS(dtest))
    dtest=['-1']
  ENDIF ELSE BEGIN ;return dtest and ndl
    lu=-1
    di=WHERE(ndm[vc,0:7] NE 0L,ndim)
    ;multiply together the array dimensions to determine expected total number of datalines
    FOR i=0,ndim-1 DO ndl=ndl*ndm[vc,di[i]]
    dtest=*sds[vc].data
    ;check structure contains the correct number of elements
    IF N_ELEMENTS(dtest) NE ndl THEN BEGIN
      STOP_WITH_ERROR,o3[3]+proname+vn[vc]+': ',errtxt[7]+STRTRIM(N_ELEMENTS(dtest),2)+'/'+STRTRIM(ndl,2),lu,ds
      RETURN
    ENDIF
    stest=SIZE(dtest) ;test to see if dtest is an array or scalar
    IF stest[0] EQ 0 THEN dtest=[dtest] ELSE dtest=REFORM(dtest,ndl,/Overwrite) ;convert to a 1-D array if necessary
  ENDELSE
ENDELSE

;Note: this conditional will only be satisfied if the routine is called by READ_DATA
;(vu still not assigned VAR_UNITS value if called by SET_UP_STRUCTURE)
IF STRUPCASE(vu[vc]) EQ 'MJD2K' THEN BEGIN
  ;Convert time from ISO8601 to MJD2000 format if necessary
  FOR i=0L,ndl-1L DO BEGIN
    IF STRPOS(STRUPCASE(dtest[i]),'Z') NE -1 THEN BEGIN
      mjd2000=JULIAN_DATE(dtest[i],/I,/M) ;return time in MJD2000 format
      IF mjd2000 EQ -99999.d THEN BEGIN ;conversion error
        STOP_WITH_ERROR,o3[3]+proname+vn[vc]+': ',errtxt[8]+dtest[i],lu,ds & RETURN
      ENDIF
      dtest[i]=STRING(format='(d18.9)',mjd2000)
      IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN itxt='cannot be in ISO8601 format' $
      ELSE itxt='changed from ISO8601 to MJD2K format'
      infotxt='2 Dataset values '+itxt+' for VAR_NAME='+vn[vc]
      INFOTXT_OUTPUT,infotxt
    ENDIF
  ENDFOR
ENDIF

END ;Procedure Extract_Data



PRO set_up_structure, sds, inf
;Procedure to do additional checks on VAR_NAME, VAR_DEPEND, VAR_DATA_TYPE, VAR_UNITS, and
;VAR_FILL_VALUE metadata attributes and set up a structure which will be used to hold the
;data values.
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20050802: Introduced to IDLCR8HDF, as Determine_Arr_Sizes. Data originally stored in 4
;              arrays according to the data type of the variable attributes - Version 1.0
;    20050909: Additional checks performed on the metadata attributes as follows: that the
;              VAR_DEPEND variable name(s), themselves, have a VAR_DEPEND value of CONSTANT or
;              INDEPENDENT, and matching VAR_SIZE values; that VAR_DATA_TYPE is DOUBLE for
;              attributes with VAR_UNITS=MJD2000; that VAR_UNITS=MJD2000 when VAR_NAME=DATETIME
;              - Version 1.1
;    20061012: Procedure renamed Set_Up_Structure. A structure using pointers used to store the
;              data instead of arrays. VAR_FILL_VALUE value saved in common array and, if
;              VAR_UNITS=MJD2000, VAR_FILL_VALUE converted to its MJD2000 form if it is in
;              ISO8601 format. Common variable definition WIDGET_WIN added - Version 2.0
;    20080302: Can calculate the VAR_SIZE value(s) from the input data or from the VAR_SIZE
;              value(s) of the VAR_DEPEND variable name(s), if they are not present in the
;              metadata. Section added to account for the new variables, ALTITUDE/ALTITUDE.GPH/
;              PRESSURE.BOUNDARIES; Additional checks added for VIS_PLOT_TYPE, VIS_SCALE_TYPE,
;              VIS_SCALE_MIN, and VIS_SCALE_MAX values - Version 3.0
;    20100205: Add RETURN command after all STOP_WITH_ERROR calls, which allows program to return to the
;              calling program if the reterr argument is included in the idlcr8hdf call - Version 3.09
;    20101120: Account for GEOMS changes between v3.0 and v4.0; Remove checks on VAR_DIMENSION, and the
;              VIS attributes; Add new VAR_DATA_TYPEs (Byte and Short); Check for self-referencing
;              VAR_DEPEND values (which replace INDEPENDENT in that context); Remove requirement for
;              DATETIME to be of datatype DOUBLE - Version 4.0
;
;  Inputs: sds - Either a structure containing the Variable Attributes and Data, or the input
;                data file
;          inf - flag identifying SDS type where, 0=structure; 1=data file
;          meta_arr - a string array containing the Global and Variable Attributes
;
;  Outputs: meta_arr - some meta_arr values may be corrected or calculated in this routine, including:
;                      VAR_DIMENSION, VAR_SIZE, and VAR_FILL_VALUE
;           nvn - an integer giving the number of Variable Attributes present in the input
;           vn - a string array of size nvn containing the VAR_NAME values
;           vu - a string array of size nvn containing the VAR_UNIT values
;           ndm - a (nvn,9) long array, where ndm(*,0:7) describes the dimensions of each dataset
;                 (maximum of 8 dimensions allowed), and ndm(*,8) describes the VAR_DATA_TYPE
;           ds - the structure that will hold the data
;
;  Called by: IDLCR8HDF
;
;  Subroutines Called: EXTRACT_DATA (if it is necessary to determine VAR_SIZE from the input data)
;                      STOP_WITH_ERROR (if error state detected); INFOTXT_OUTOUT
;    Possible Conditions for STOP_WITH_ERROR call (plus [line number] where called):
;      1. Program expects to find the VAR_NAME in the metadata in the same order as that listed under
;         DATA_VARIABLES [2389]
;      2. The VAR_DIMENSION value is greater than 8 [2428]
;      3. Number of VAR_SIZE and VAR_DEPEND attribute values is different [2425]
;      4. The VAR_DEPEND value is not 'CONSTANT', 'INDEPENDENT' or self-referencing, and doesn't
;         match a previous VAR_NAME [2478]
;      5. The VAR_DEPEND variable name must, itself, have a VAR_DEPEND value of 'CONSTANT' or
;         'INDEPENDENT' or be self-referencing [2490]
;      6. The VAR_DEPEND variable name must have a VAR_SIZE value matching the current VAR_NAME [2500]
;      7. VAR_DATA_TYPE not BYTE, SHORT, INTEGER, LONG, REAL, DOUBLE, or STRING [2402]
;      8. Unexpected number of ATTRIBUTE values extracted [2555]
;      9. VAR_DATA_TYPE should be DOUBLE for VAR_UNITS=MJD2K - No longer a requirement
;     10. VAR_UNITS should be MJD2K for VAR_NAME=DATETIME [2541]
;     11. VAR_FILL_VALUE not a valid value - occurs on an unsuccessful call to JULIAN_DATE [2562]
;     12. VAR_DEPEND values not valid - occurs when INDEPENDENT or CONSTANT is a VAR_DEPEND value
;         when it should not be [2443,2472]
;     13. Second VAR_SIZE value is not '2' when VAR_NAME=ALTITUDE/ALTITUDE.GPH/PRESSURE.BOUNDARIES [2510]
;     14. Axis variable cannot be dependent on another variable [2461]
;     15. Axis variable in the vertical dimension already found [2462]
;     16. Attribute which is not an axis variable has a self-referencing VAR_DEPEND value [2463]
;     17. Type conversion error. Called when trying to convert a string, which is expected to be
;         numeric, to a number [2591]
;
;    Information Conditions (when the program is able to make changes):
;      1. 64-bit LONG Data Type is not currently supported in GEOMS. Will attempt to write data in 32-bit
;         Integer type instead [2410]

COMMON METADATA
COMMON DATA
COMMON WIDGET_WIN

;possible error messages for this procedure
errtxt=STRARR(17) & lu=-1L
errtxt[0]='Does not match the equivalent VAR_NAME in DATA_VARIABLES: '
errtxt[1]='Number of dimensions too high to make HDF file (max. allowed 8)'
errtxt[2]='VAR_DEPEND attribute value missing or does not match the number of VAR_SIZE values'
errtxt[3]='VAR_DEPEND value not CONSTANT,INDEPENDENT nor self-referencing, and doesn''t match a previous VAR_NAME: '
errtxt[4]='VAR_DEPEND variable name(s) must have VAR_DEPEND value of CONSTANT or be self_referencing: '
errtxt[5]='VAR_DEPEND variable name must have matching VAR_SIZE value (= '
errtxt[6]='Data type not BYTE, SHORT, INTEGER, REAL, DOUBLE, or STRING: '
errtxt[7]='Unexpected number of ATTRIBUTE values extracted: '
errtxt[8]='VAR_DATA_TYPE must be DOUBLE for VAR_UNITS=MJD2K: '
errtxt[9]='VAR_UNITS must be MJD2K for '
errtxt[10]='VAR_FILL_VALUE not a valid value: '
errtxt[11]=' not valid'
errtxt[12]='Second VAR_SIZE value should be ''2'' for this VAR_NAME'
errtxt[13]='Axis variable cannot be dependent on another variable: '
errtxt[14]=' is already the axis variable in the vertical dimension'
errtxt[15]='is not an axis variable so VAR_DEPEND value cannot be self-referencing'
errtxt[16]='Type conversion error.  Entry is not a valid number: '
proname='Set_Up_Structure procedure: '

lc=0 & vc=0 & writeonce=0 & bounderror=0
allowable_data_types=['BYTE','SHORT','INTEGER','LONG','REAL','DOUBLE','STRING']
num_atts=['VAR_VALID_MIN','VAR_VALID_MAX','VAR_FILL_VALUE']

ON_IOERROR,TypeConversionError

;Determine a set of possible Axis Variables to be tested (i.e. all VAR_DEPEND values that aren't CONSTANT or INDEPENDENT)
vdi=WHERE(STRMID(meta_arr,0,10) EQ 'VAR_DEPEND',vdcnt)
vardeptest=['']
IF vdcnt NE 0 THEN BEGIN
  FOR i=0,vdcnt-1 DO BEGIN
    res=STRSPLIT(meta_arr[vdi[i]],' =;',/Extract,COUNT=rescnt)
    IF rescnt GT 1 THEN BEGIN ;VAR_DEPEND values found
      FOR j=1,rescnt-1 DO BEGIN
        resuc=STRUPCASE(res[j])
        ni=WHERE(resuc EQ STRUPCASE(vardeptest),ncnt)
        IF (ncnt EQ 0) AND (resuc NE 'INDEPENDENT') AND (resuc NE 'CONSTANT') THEN $
          vardeptest=[vardeptest,res[j]] ;Add VAR_DEPEND value to list of axis-variables to be checked
      ENDFOR
    ENDIF
  ENDFOR
ENDIF
;Remove '' from vardeptest
gi=WHERE(vardeptest NE '',gcnt)
IF gcnt NE 0 THEN vardeptest=vardeptest[gi]

WHILE lc LT N_ELEMENTS(meta_arr) DO BEGIN
  valid=0 ;set to test for successful string conversion to a number
  IF STRMID(meta_arr[lc],0,14) EQ 'DATA_VARIABLES' THEN BEGIN ;determine number of variables reported
    lcdv=lc
    vn=STRSPLIT(meta_arr[lc],' =;',/Extract) ;string containing reported variables
    nvn=N_ELEMENTS(vn)-1 ;total number of variables reported
    vn=vn[1:nvn] ;remove the DATA_VARIABLES label
    vu=STRARR(nvn)
    vfvd=DBLARR(N_ELEMENTS(num_atts),nvn) ;holding array for floating point num_atts array values
    vfvl=LON64ARR(N_ELEMENTS(num_atts),nvn) ;holding array for integer num_atts array values
    ndm=LONARR(nvn,9) ;to contain the dimensions and data type for each dataset
    vserror=STRARR(nvn) ;to hold variable names for datasets where the VAR_SIZE values cannot be determined
  ENDIF
  IF STRMID(meta_arr[lc],0,8) EQ 'VAR_NAME' THEN BEGIN
    vname=meta_arr[lc] ;used in case of error
    lcz=lc ;VAR_NAME index value
    res=STRSPLIT(meta_arr[lc],' =',/Extract)
    IF N_ELEMENTS(res) NE 2 THEN res=[res[0],'-1']
    IF res[1] NE vn[vc] THEN BEGIN
      STOP_WITH_ERROR,o3[3]+proname+vname+': ',errtxt[0]+vn[vc],lu & RETURN
      ;Does not match the equivalent VAR_NAME in DATA_VARIABLES
    ENDIF

    REPEAT lc=lc+1 UNTIL STRMID(meta_arr[lc],0,8) EQ 'VAR_SIZE'
    holdvs=meta_arr[lc] & lcx=lc ;do checks after determining VAR_DATA_TYPE
    REPEAT lc=lc+1 UNTIL STRMID(meta_arr[lc],0,10) EQ 'VAR_DEPEND'
    holdvd=meta_arr[lc] & lcy=lc ;do checks after determining VAR_DATA_TYPE
    REPEAT lc=lc+1 UNTIL STRMID(meta_arr[lc],0,13) EQ 'VAR_DATA_TYPE'
    res=STRSPLIT(STRUPCASE(meta_arr[lc]),' =;',/Extract)
    IF N_ELEMENTS(res) EQ 2 THEN gi=WHERE(res[1] EQ allowable_data_types,gcnt) $ ;Check VAR_DATA_TYPE is valid
    ELSE gcnt=0
    IF gcnt NE 1 THEN BEGIN
      STOP_WITH_ERROR,o3[3]+proname+vname+': ',errtxt[6]+meta_arr[lc],lu & RETURN
      ;Data type not BYTE, SHORT, INTEGER, LONG, REAL, DOUBLE, or STRING
    ENDIF
    IF gi[0] EQ 3 THEN BEGIN
      IF writeonce EQ 0 THEN BEGIN
        writeonce=1
        infotxt='2 64-bit LONG Data Type is not currently supported|. '
        infotxt=infotxt+'Will attempt to write data in 32-bit INTEGER Data Type'
        INFOTXT_OUTPUT,infotxt
      ENDIF
      gi[0]=2 & meta_arr[lc]='VAR_DATA_TYPE=INTEGER'
    ENDIF
    ndm[vc,8]=gi[0] ;index number representing the data type

    ;Do VAR_SIZE and VAR_DEPEND checks
    resvs=STRSPLIT(holdvs,' =;',/Extract,COUNT=nvs) ;VAR_SIZE entries
    resvd=STRSPLIT(holdvd,' =;',/Extract,COUNT=nd) ;VAR_DEPEND entries
    nvs=nvs-1 & nd=nd-1 ;Number of Dimensions based on number of VAR_SIZE/VAR_DEPEND values

    IF nvs EQ 0 THEN ndmok=0 ELSE ndmok=1
    ;If there are no VAR_SIZE value entries, need to determine from Data file or structure or
    ;from the VAR_SIZE values of the VAR_DEPEND dependencies
    IF ((nvs NE nd) AND (ndmok EQ 1)) OR (nd EQ 0) THEN BEGIN
      STOP_WITH_ERROR,o3[3]+proname+vname+': ',errtxt[2],lu & RETURN
      ;VAR_DEPEND attribute value missing or does not match the number of VAR_SIZE values
    ENDIF ELSE IF nd GT 8 THEN BEGIN
      STOP_WITH_ERROR,o3[3]+proname+vname+': ',errtxt[1],lu & RETURN
      ;Number of dimensions too high to make HDF file (max. allowed 8)
    ENDIF ELSE IF ndmok EQ 1 THEN ndm[vc,0:nd-1]=LONG(resvs[1:nvs]) ;save VAR_SIZE values in ndm array

    vshold=LONARR(nd) ;to hold VAR_SIZE of the dependencies

    ;Do checks on VAR_DEPEND values
    ci=WHERE((STRUPCASE(resvd) EQ 'INDEPENDENT') OR (STRUPCASE(resvd) EQ 'CONSTANT'),ccnt)
    IF ccnt NE 0 THEN resvd[ci]=STRUPCASE(resvd[ci])
    ;Rules for .BOUNDARY VAR_NAME
    IF STRPOS(vn[vc],'.BOUNDARIES') NE -1 THEN BEGIN
      test1=0 & test3=0
      IF (nd EQ 2) OR (nd EQ 3) THEN BEGIN
        test1=resvd[2] NE 'INDEPENDENT' & test3=resvd[1] EQ 'INDEPENDENT'
      ENDIF ELSE IF (nd LE 1) OR (nd GE 4) THEN test1=1 ;incorrect number of VAR_DEPEND values
      IF nd EQ 3 THEN IF STRUPCASE(resvd[3]) NE 'DATETIME' THEN test1=1
      ;Third VAR_DEPEND value must be DATETIME in this case
      firstvdsplt=STRSPLIT(resvd[1],'.',/Extract)
      test2=STRPOS(vn[vc],firstvdsplt[0]) EQ -1
      IF (test1) OR (test2) THEN BEGIN
        IF test3 EQ 1 THEN itxt=' in IDL/Fortran Dimension Ordering' ELSE itxt=''
        infotxt='3 '+holdvd+' not valid for '+vname+itxt
        INFOTXT_OUTPUT,infotxt
        bounderror=1
        ;STOP_WITH_ERROR,o3[3]+proname+vname+': ',holdvd+errtxt[11]+' for the given VAR_NAME'+itxt,lu
        ;VAR_DEPEND value(s) not valid for the given VAR_NAME
        ;RETURN
      ENDIF
    ENDIF

    FOR i=1,nd DO BEGIN
      test1=(resvd[i] EQ 'CONSTANT') OR (resvd[i] EQ 'INDEPENDENT') OR (resvd[i] EQ vn[vc])
      test2=(resvd[i] NE 'CONSTANT') AND (resvd[i] NE 'INDEPENDENT') AND (resvd[i] NE vn[vc])
      test3=(resvd[i] EQ 'CONSTANT') OR (resvd[i] EQ vn[vc]) AND ((i GT 1) OR (nd GT 2))
      test4=(resvd[i] EQ 'INDEPENDENT') AND (i GT 2)
      test5=(resvd[i] EQ 'INDEPENDENT') AND (i EQ 2) AND (STRPOS(vn[vc],'.BOUNDARIES') EQ -1)
      test6=(STRPOS(vn[vc],'.BOUNDARIES') NE -1) AND (bounderror EQ 1) ;i.e. .BOUNDARIES error already reported
      IF i EQ 1 THEN BEGIN
        ;Check for and Apply GEOMS rule changes for INDEPENDENT and axis variables
        vdval=resvd[i] & vnval=vn[vc]
        GEOMS_RULE_CHANGES,2,vardeptest,vnval,vdval,holdvd
        IF vdval NE resvd[i] THEN BEGIN ;First VAR_DEPEND value has been changed
          ;Rebuild VAR_DEPEND entry
          holdvd='VAR_DEPEND='+vdval
          IF nd GT 1 THEN FOR j=2,nd DO holdvd=holdvd+';'+resvd[j]
        ENDIF
        IF STRMID(holdvd,0,1) EQ 'E' THEN BEGIN ;error found while attempting to identify axis variables
          CASE 1 OF
            holdvd EQ 'E1': STOP_WITH_ERROR,o3[3]+proname+vname+': ',errtxt[13]+holdvd,lu
            holdvd EQ 'E3': STOP_WITH_ERROR,o3[3]+proname+vname+' ',errtxt[15],lu
          ENDCASE
          RETURN
        ENDIF
        resvd[i]=vdval
        meta_arr[lcy]=holdvd
      ENDIF
      ;Check for CONSTANT,INDEPENDENT or self-referencing and more than one VAR_DEPEND value
      IF ((test1) AND (i EQ 1) AND (nd GT 2) AND (test6 EQ 0)) OR (test3) OR (test4) OR (test5) THEN BEGIN
        STOP_WITH_ERROR,o3[3]+proname+vname+': ',holdvd+errtxt[11],lu & RETURN
        ;VAR_DEPEND value(s) not valid
      ENDIF
      ;Check for valid dependencies, and hold VAR_SIZE values of the dependencies if required
      IF vc GE 1 THEN gi=WHERE(resvd[i] EQ vn[0:vc-1],gcnt) ELSE gcnt=0
      IF (gcnt EQ 0) AND (test2) THEN BEGIN
        STOP_WITH_ERROR,o3[3]+proname+vname+': ',errtxt[3]+resvd[i],lu & RETURN
        ;VAR_DEPEND value not CONSTANT,INDEPENDENT nor Self-referencing, and doesn't match a previous VAR_NAME
      ENDIF
      IF gcnt NE 0 THEN BEGIN ;do remaining checks on VAR_DEPEND values
        errfound=0
        gi=WHERE(meta_arr EQ 'VAR_NAME='+resvd[i])
        ;check VAR_DEPEND value of the VAR_DEPEND variable name
        vi=WHERE(STRPOS(meta_arr[gi[0]:N_ELEMENTS(meta_arr)-1],'VAR_DEPEND') NE -1)
        vex=STRSPLIT(STRUPCASE(meta_arr[gi[0]+vi[0]]),' =;',/Extract,COUNT=nvex)
        IF nvex NE 2 THEN vex=[vex,''] ;missing VAR_DEPEND value so add dummy value
        IF (vex[1] NE 'CONSTANT') AND (vex[1] NE 'INDEPENDENT') AND (vex[1] NE resvd[i]) THEN BEGIN
          vert_var=['ALTITUDE','ALTITUDE.GPH','PRESSURE','DEPTH']
          res=WHERE(resvd[i] EQ vert_var,vcnt) ;does VAR_DEPEND variable name reference a vertical axis
          res=WHERE(vex[1] EQ vert_var,xcnt) ;does VAR_DEPEND of the VAR_DEPEND variable name reference a vertical axis
          IF (vcnt NE 0) AND (xcnt EQ 0) THEN BEGIN ;Vertical axis so should be self-referencing
            infotxt='2 '+meta_arr[gi[0]+vi[0]]+' should be self-referencing for axis variable'
            infotxt=infotxt+' VAR_NAME='+resvd[i]+'|. VAR_DEPEND value changed in metadata'
            INFOTXT_OUTPUT,infotxt
            meta_arr[gi[0]+vi[0]]='VAR_DEPEND='+resvd[i]
            IF nvex GT 2 THEN FOR j=2,nvex-1 DO meta_arr[gi[0]+vi[0]]=meta_arr[gi[0]+vi[0]]+';'+vex[j]
          ENDIF ELSE BEGIN
            ;VAR_DEPEND value of the VAR_DEPEND variable name must be CONSTANT or an axis variable
            infotxt=STRARR(2)
            infotxt[0]='3 '+meta_arr[lcy]+' variable name(s) for '+vname+' must have VAR_DEPEND'
            infotxt[1]='    value of CONSTANT or be self-referencing'
            INFOTXT_OUTPUT,infotxt
          ENDELSE
        ENDIF
        IF errfound EQ 1 THEN BEGIN ;redundant from v4.0
          STOP_WITH_ERROR,o3[3]+proname+vname+': '+meta_arr[lcy]+': ',errtxt[4]+meta_arr[gi[0]+vi[0]],lu
          ;VAR_DEPEND variable name must have VAR_DEPEND value of CONSTANT, INDEPENDENT or be self_referencing
          RETURN
        ENDIF
        ;check VAR_SIZE value of the VAR_DEPEND variable name
        vi=WHERE(STRPOS(meta_arr[gi[0]:N_ELEMENTS(meta_arr)-1],'VAR_SIZE') NE -1)
        vex=STRSPLIT(meta_arr[gi[0]+vi[0]],' =;',/Extract,COUNT=nvex)
        IF (nvex LT 2) OR (nvex GT 3) THEN errfound=1 $
        ELSE IF (ndmok EQ 1) AND (LONG(vex[1]) NE ndm[vc,i-1]) THEN errfound=1
        IF errfound EQ 1 THEN BEGIN
          STOP_WITH_ERROR,o3[3]+proname+vname+': '+'VAR_DEPEND='+resvd[i]+': ', $
                          errtxt[5]+STRTRIM(ndm[vc,i-1],2)+'): '+meta_arr[gi[0]+vi[0]],lu
          ;VAR_DEPEND variable name must have matching VAR_SIZE value
          RETURN
        ENDIF ELSE vshold[i-1]=LONG(vex[1])
      ENDIF
      ;If i eq 2 and value is INDEPENDENT then check that the corresponding VAR_SIZE value is 2
      ;(if present), o/w generate errors
      IF (i EQ 2) AND (STRUPCASE(resvd[i]) EQ 'INDEPENDENT') THEN BEGIN
        IF (ndmok EQ 1) AND (ndm[vc,i-1] NE 2L) THEN BEGIN
          STOP_WITH_ERROR,o3[3]+proname+vname+': '+': '+holdvs+': ',errtxt[12],lu & RETURN
          ;Second VAR_SIZE value should be '2' for this VAR_NAME
        ENDIF
        vshold[i-1]=2L ;set VAR_SIZE value in the event that it is not part of the Metadata
      ENDIF
    ENDFOR

    IF ndmok EQ 0 THEN BEGIN ;no VAR_SIZE value so need to determine from the data or the vshold array
      IF vshold[0] EQ 0L THEN BEGIN
        ;VAR_DEPEND is Self-Referencing or CONSTANT so determine VAR_SIZE from the Data file or structure
        dtest=['-1'] ;-1 identifies to the EXTRACT_DATA routine that ndl is all that is required
        EXTRACT_DATA,SDS,inf,vc,dtest,ndl
        IF STRLEN(rerr[0]) GT 2 THEN RETURN
        ;Check if any other VAR_SIZE values have already been determined
        ;This could happen in the case VAR_DEPEND=ALTITUDE;DATETIME for VAR_NAME=ALTITUDE for e.g.
        gi=WHERE(vshold NE 0L,gcnt)
        ndltot=' ('+STRTRIM(ndl,2)+')'
        IF gcnt NE 0 THEN BEGIN
          FOR i=0,gcnt-1 DO ndl=ndl/FLOAT(vshold[gi[i]])
        ENDIF
        ;Make up VAR_SIZE string based on available values
        IF vshold[0] EQ 0L THEN vsstr=' (VAR_SIZE=x' ELSE vsstr='VAR_SIZE='+STRTRIM(vshold[0],2)
        IF nd GT 1 THEN FOR i=1,nd-1 DO $
          IF vshold[i] EQ 0L THEN vsstr=vsstr+';x' ELSE vsstr=vsstr+';'+STRTRIM(vshold[i],2)
        vsstr=vsstr+') '
        vshold[0]=LONG(ndl)
        bi=WHERE(vshold EQ 0,bcnt) ;Expected VAR_SIZE values are missing if bcnt not equal to 0
        IF (ndl NE vshold[0]) OR (bcnt NE 0) THEN BEGIN
          infotxt=STRARR(2)
          infotxt[0]='3 Unable to determine missing VAR_SIZE value(s) for '+vname+' based on'
          infotxt[1]='    '+holdvd+vsstr+'and the total number of dataset values'+ndltot
          INFOTXT_OUTPUT,infotxt
          vserror[vc]=vn[vc]
        ENDIF
        meta_arr[lcx]='VAR_SIZE='+STRTRIM(vshold[0],2)
        ndm[vc,0:nd-1]=vshold
        IF nd GT 1 THEN FOR i=1,nd-1 DO meta_arr[lcx]=meta_arr[lcx]+';'+STRTRIM(vshold[i],2)
      ENDIF ELSE BEGIN ;can determine VAR_SIZE from the vshold array
        meta_arr[lcx]='VAR_SIZE='
        FOR i=0,nd-1 DO BEGIN
          IF i EQ 0 THEN meta_arr[lcx]=meta_arr[lcx]+STRTRIM(vshold[i],2) $
          ELSE meta_arr[lcx]=meta_arr[lcx]+';'+STRTRIM(vshold[i],2)
          ndm[vc,i]=vshold[i] ;EQ array dimensions from VAR_SIZE of the dependencies
        ENDFOR
      ENDELSE
      ;Check to see if VAR_SIZE calculation is valid or not based on contents of vserror
      vsok=1
      FOR i=0,nd-1 DO BEGIN
        ei=WHERE(resvd[i] EQ vserror,ecnt)
        IF ecnt NE 0 THEN vsok=0
      ENDFOR
      IF vsok EQ 1 THEN BEGIN
        IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN qtxt=' not recorded. Calculated as '+meta_arr[lcx] $
        ELSE qtxt=' added: '+meta_arr[lcx]
        infotxt='2 VAR_SIZE value(s) for '+vname+qtxt
        INFOTXT_OUTPUT,infotxt
      ENDIF
    ENDIF

    IF (resvd[0] EQ 'CONSTANT') AND (TOTAL(ndm[vc,0:7]) GT 1.) THEN BEGIN
      infotxt='3 Dataset must only have a single value for VAR_DEPEND=CONSTANT: '+meta_arr[lcx]
      INFOTXT_OUTPUT,infotxt
    ENDIF

    ;Do DATETIME/MJD2000 checks
    REPEAT lc=lc+1 UNTIL STRMID(meta_arr[lc],0,9) EQ 'VAR_UNITS'
    resv=STRSPLIT(meta_arr[lc],' =',/Extract,Count=rcnt)
    IF rcnt EQ 1 THEN resv=[resv,'[MISSING]'] ;add filler for checks
    test1=(vn[vc] EQ 'DATETIME') OR (vn[vc] EQ 'DATETIME.START') OR (vn[vc] EQ 'DATETIME.STOP')
    IF (test1) AND (STRUPCASE(resv[1]) NE 'MJD2K') THEN BEGIN
      IF (resv[1] EQ '[MISSING]') OR (resv[1] EQ '1') THEN BEGIN
        infotxt='2 '+meta_arr[lc]+' must be MJD2K for '+vname+'|. Value changed in Metadata'
        INFOTXT_OUTPUT,infotxt
        meta_arr[lc]='VAR_UNITS=MJD2K'
        resv[1]='MJD2K'
        ;Change VAR_SI_CONVERSION value also
        REPEAT lc=lc+1 UNTIL STRMID(meta_arr[lc],0,17) EQ 'VAR_SI_CONVERSION'
        CASE 1 OF
          ndm[vc,8] LE 3: meta_arr[lc]='VAR_SI_CONVERSION=0;86400;s
          ndm[vc,8] LE 5: meta_arr[lc]='VAR_SI_CONVERSION=0.0;86400.0;s'
          ELSE: meta_arr[lc]='VAR_SI_CONVERSION='
        ENDCASE
      ENDIF ELSE BEGIN
        STOP_WITH_ERROR,o3[3]+proname,errtxt[9]+vname+': '+meta_arr[lc],lu & RETURN
        ;VAR_UNITS must be MJD2K for VAR_NAME=DATETIME/.START/.STOP
      ENDELSE
    ENDIF
    vu[vc]=resv[1] ;used to check for MJD2K units when reading in data as well as NCSA units value
    IF N_ELEMENTS(resv) GT 2 THEN $
      FOR i=2,N_ELEMENTS(resv)-1 DO vu[vc]=vu[vc]+' '+resv[i]

    ;Do checks on the numeric attributes
    FOR i=0,N_ELEMENTS(num_atts)-1 DO BEGIN
      REPEAT lc=lc+1 UNTIL STRMID(meta_arr[lc],0,STRLEN(num_atts[i])) EQ num_atts[i]
      resv=STRSPLIT(meta_arr[lc],' =;',/Extract)
      test1=(STRUPCASE(vu[vc]) NE 'MJD2K') OR (num_atts[i] EQ 'VAR_FILL_VALUE')
      test2=(N_ELEMENTS(resv) NE 2) AND (ndm[vc,8] NE 6)
      IF (test1) AND (test2) THEN BEGIN
        STOP_WITH_ERROR,o3[3]+proname+vname+': ',errtxt[7]+meta_arr[lc],lu & RETURN
        ;Unexpected number of ATTRIBUTE values extracted
      ENDIF ELSE IF (ndm[vc,8] NE 6) AND (N_ELEMENTS(resv) EQ 2) THEN BEGIN
        ;If VAR_UNITS=MJD2000 then check for ISO8601 format and change to MJD2000 if necessary
        IF (STRUPCASE(vu[vc]) EQ 'MJD2K') AND (STRPOS(STRUPCASE(resv[1]),'Z') NE -1) THEN BEGIN
          mjd2000=JULIAN_DATE(resv[1],/I,/M) ;return time in MJD2000 format
          IF mjd2000 EQ -99999.d THEN BEGIN
            STOP_WITH_ERROR,o3[3]+proname+vn[vc]+': ',errtxt[10]+meta_arr[lc],lu & RETURN
          ENDIF
          vfvd[i,vc]=mjd2000
          meta_arr[lc]=resv[0]+'='+STRTRIM(STRING(format='(d18.9)',mjd2000),2)
          IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN qtxt='    should be in MJD2K format|' $
          ELSE qtxt='    replaced with MJD2K formatted value '
          infotxt[0]='2 '+resv[0]+'='+resv[1]+' for VAR_NAME='+vn[vc]
          infotxt[1]=qtxt+meta_arr[lc]
          INFOTXT_OUTPUT,infotxt
        ENDIF ELSE BEGIN
          ;Check that the VAR_VALID_MIN/MAX or VAR_FILL_VALUE is numeric and save to vfvl or vfvd arrays
          lcx=lc
          IF ndm[vc,8] LE 3 THEN BEGIN ;value is integer type
            IF mv_lng[lc] NE 0LL THEN vfvl[i,vc]=mv_lng[lc] ELSE vfvl[i,vc]=LONG64(DOUBLE(resv[1]))
          ENDIF ELSE BEGIN ;value is floating point type
            IF mv_dbl[lc] NE 0.D THEN vfvd[i,vc]=mv_dbl[lc] ELSE vfvd[i,vc]=DOUBLE(resv[1])
          ENDELSE
        ENDELSE
      ENDIF
    ENDFOR
    vc=vc+1
  ENDIF
  lc=lc+1 & valid=1
ENDWHILE

;Save numeric metadata values to common arrays
mv_lng=vfvl & mv_dbl=vfvd

;Define the HDF storage structure
ds_set={data: PTR_NEW()} ;SDS data array
ds=REPLICATE(ds_set,nvn) ;Dimension the structure to the size of the SDS datasets

TypeConversionError:
IF valid EQ 0 THEN BEGIN
  STOP_WITH_ERROR,o3[3]+proname+vname+': ',errtxt[16]+meta_arr[lcx],lu & RETURN
ENDIF
END ;Procedure Set_Up_Structure



PRO check_string_datatype, vc, dtest, ndl
;Procedure to check that the data, and Variable Attributes are correctly configured when the
;VAR_DATA_TYPE=STRING, including VAR_UNITS, VAR_VALID_MIN/MAX, and VAR_FILL_VALUE. The data
;values are returned in the string datatype.
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20091203: Introduced to IDLCR8HDF routine - Version 3.08
;    20101120: Account for GEOMS rule changes from v3.0 to v4.0 - Version 4.0b0
;    20111220: Check dataset entries for non-ISO646-US ASCII Characters - Version 4.0b7
;    20130116: Allow for a string dataset with maximum string length of 0, i.e. a set
;              of empty values - Version 4.0b15
;
;  Inputs: meta_arr - a string array containing the Global and Variable Attributes
;          vc - the index value of the vn array holding the VARIABLE_NAME being searched for in the data
;               file, or the index value of the sds structure which holds the data
;          dtest - the set of data values to be tested
;          ndl - The total number of data values i.e. the product of the VAR_SIZE values
;
;  Outputs: meta_arr - in the event that the values being tested are changed, the array will be updated
;           dtest - correctly formatted dataset
;
;  Called by: READ_DATA
;
;  Subroutines Called: INFOTXT_OUTPUT
;    Information Conditions (when the program is able to make changes):
;      1. The Metadata value is not valid for VAR_DATA_TYPE=STRING [2645]

COMMON METADATA
COMMON DATA
COMMON WIDGET_WIN

vi=WHERE(meta_arr EQ 'VAR_NAME='+vn[vc])
dtest=STRTRIM(dtest,2)

;Check for non ISO646-US ASCII Characters
GEOMS_RULE_CHANGES,10,dtest,vn[vc]

label=['VAR_UNITS','VAR_SI_CONVERSION','VAR_VALID_MIN','VAR_VALID_MAX','VAR_FILL_VALUE']
n_lab=N_ELEMENTS(label)
mxlablen=MAX(STRLEN(label)) ;determine max label string length
metahold=STRMID(meta_arr,0,mxlablen) ;subset of the meta_arr strings, containing first portion of the Metadata

;Perform checks on the Attributes
FOR i=0,n_lab-1 DO BEGIN
  li=WHERE(STRPOS(metahold[vi[0]:N_ELEMENTS(metahold)-1],label[i]) NE -1)
  lvi=li[0]+vi[0]
  res=STRSPLIT(meta_arr[lvi],'=',/Extract)
  IF N_ELEMENTS(res) EQ 2 THEN BEGIN ;check value is as expected, o/w write to log
    IF STRTRIM(res[1],2) NE '' THEN BEGIN
      infotxt=STRARR(2)
      infotxt[0]='2 Attribute '+meta_arr[lvi]+' in Dataset '+vn[vc]
      infotxt[1]='    not valid for VAR_DATA_TYPE=STRING|. Has been corrected to '+res[0]+'='
      INFOTXT_OUTPUT, infotxt
    ENDIF
  ENDIF
  meta_arr[lvi]=res[0]+'='
  IF res[0] EQ 'VAR_UNITS' THEN vu[vc]=' '
ENDFOR

;Determine maximum string length of the dataset
mxdatalen=0 ;default value of string length
testdatalen=MAX(STRLEN(STRTRIM(dtest,2)))
IF testdatalen GT mxdatalen THEN mxdatalen=testdatalen

;Format the data values to the string with the maximum length
IF mxdatalen NE 0 THEN BEGIN
  vfsx='(A'+STRTRIM(mxdatalen,2)+')'
  dtest=STRING(format=vfsx,dtest)
ENDIF

END ;procedure Check_String_Datatype



PRO check_min_max_fill, vc, dtest, ndl
;Procedure to check that the data, VAR_VALID_MIN/MAX, and VAR_FILL_VALUE fit within the given data
;type. That the VAR_FILL_VALUE falls within the GEOMS definition and that the data values are within
;the valid minimum and maximum values (or the fill value). The data values are returned in the data
;type given by VAR_DATA_TYPE.
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20050802: Original IDLCR8HDF routine - Version 1.0
;    20050909: If VAR_NAME=DATETIME then checks that the first data value is not a fill value, and is
;              the lowest value; Change the methods for determining if a given data value falls within
;              the range allowed by integer or long data types; Add fix for the case where a dataset
;              consists of only fill values - Version 1.1
;    20051107: Include VIS_SCALE_MIN/MAX values in the checks; Add fix to remove unwanted precision (to
;              prevent rounding errors), by converting values to formatted strings then back to numeric
;              values - Version 1.11
;    20061012: Check that all DATETIME values are in chronological order (if more than one value), and
;              contain no fill values; ISO8601 DATETIME conversions to MJD2000 format (if necessary) moved
;              to the READ_DATA routine; Add additional checks when extracting the VIS_FORMAT values for
;              testing; Common variable definition WIDGET_WIN added - Version 2.0
;    20080302: Fix bug so that unwanted precision from all data and relevant metadata values is removed
;              before doing QA checks, to avoid unnecessary error calls - Version 3.0
;    20100205: Add RETURN command after all STOP_WITH_ERROR calls, which allows program to return to the
;              calling program if the reterr argument is included in the idlcr8hdf call - Version 3.09
;    20101120: Account for GEOMS rule changes v3.0 to v4.0; Remove checks involving VIS_FORMAT; Modify
;              method for checking data type limitations - Version 4.0
;    20120420: Fix CHECK_MATH check so that combined floating point errors are ignored for long integer
;              values being tested (error 160) - Version 4.0b9
;    20120620: Remove CHECK_MATH checks, and just apply Type conversion checks, as it was not possible for
;              CHECK_MATH to accurately indicate the problem numeric value - Version 4.0b10
;    20120829: Fix call to ROUND when the value being rounded is a string (ROUND can only be applied to
;              numeric datatypes) - Version v4.0b12
;
;  Inputs: meta_arr - a string array containing the Global and Variable Attributes
;          vc - the index value of the vn array holding the VARIABLE_NAME being searched for in the data
;               file, or the index value of the sds structure which holds the data
;          dtest - the set of data values to be tested
;          ndl - The total number of data values i.e. the product of the VAR_SIZE values
;
;  Outputs: meta_arr - in the event that the VIS_FORMAT value string or the precision of the attribute
;                      values being tested are changed, the array will be updated
;           dtest - dataset returned in correct data type (VAR_FILL_VALUE/VAR_VALID_MIN/VAR_VALID_MAX
;                   also appended to the start of the array)
;
;  Called by: READ_DATA
;
;  Subroutines Called: STOP_WITH_ERROR (if error state detected)
;                      INFOTXT_OUTPUT
;    Possible Conditions for STOP_WITH_ERROR call (plus [line number] where called):
;      1. Value is not valid, or does not match VAR_DATA_TYPE [2826]
;      2. A data value falls outside the range given by VAR_VALID_MIN or VAR_VALID_MAX [2846, 2851]
;      3. The VAR_FILL_VALUE is not outside the valid minimum or maximum values - No longer a requirement
;      4. The metadata or data value being tested is outside the data type range. For example,
;         if a data value is 40000, but VAR_DATA_TYPE=INTEGER (maximum allowable value of 32767)
;         [2786,2793,2800,2807,2813,2819]
;      5. The DATETIME value cannot be a VAR_FILL_VALUE. Because DATETIME is an axis variable
;         it should not contain Fill Values [2862]
;      6. The DATETIME values are not in chronological order [2868]
;      7. Type conversion error. The program cannot convert a data value to a valid number [2874]
;
;    Information Conditions (when the program is able to make changes):
;      1. Fill value falls within the data range and is defined as a Default value [2836]

COMMON METADATA
COMMON DATA
COMMON WIDGET_WIN

;Error messages for this procedure
ON_IOERROR,TypeConversionError
proname='Check_Min_Max_Fill procedure: '
errtxt2=STRARR(7) & lu=-1
errtxt2[0]=' not valid, or does not match VAR_DATA_TYPE'
errtxt2[1]=' data value outside VAR_VALID_'
errtxt2[2]='Fill data value not outside VAR_VALID_MIN or VAR_VALID_MAX: '
errtxt2[3]=' outside the data type range: '
errtxt2[4]='DATETIME value cannot be a VAR_FILL_VALUE. '
errtxt2[5]='DATETIME values not in chronological order'
errtxt2[6]='Type conversion error.  Entry is not a valid value'

vi=WHERE(meta_arr EQ 'VAR_NAME='+vn[vc])

;Determine Var_Fill_Value, Var_Valid_Min, Var_Valid_Max, and data values,
;and check that they fall within the range allowed by VAR_DATA_TYPE
label=['VAR_VALID_MIN','VAR_VALID_MAX','VAR_FILL_VALUE','Data value']
n_lab=N_ELEMENTS(label)
mxlablen=MAX(STRLEN(label[0:n_lab-2])) ;determine max label string length
metahold=STRMID(meta_arr,0,mxlablen) ;subset of the meta_arr strings, containing first portion of the Metadata
lvi=LONARR(n_lab-1) ;to hold index values of the VAR_FILL_VALUE/VALID_MIN/VALID_MAX attributes

CASE ndm[vc,8] OF
  0: vhold=BYTARR(ndl+(n_lab-1L))
  1: vhold=INTARR(ndl+(n_lab-1L))
  2: vhold=LONARR(ndl+(n_lab-1L))
  3: vhold=LON64ARR(ndl+(n_lab-1L))
  4: vhold=FLTARR(ndl+(n_lab-1L))
  5: vhold=DBLARR(ndl+(n_lab-1L))
ENDCASE

IF SIZE(dtest,/TYPE) EQ 7 THEN convertstr=1 ELSE convertstr=0 ;dtest is in ASCII string format
IF ndm[vc,8] LE 3 then convtolng=1 else convtolng=0

FOR i=0L,ndl+(n_lab-2L) DO BEGIN
  valid=0 ;set-up for possible Type Conversion Error
  IF i LE n_lab-2L THEN BEGIN
    lin=i ;label index
    li=WHERE(STRPOS(metahold[vi[0]:N_ELEMENTS(metahold)-1],label[lin]) NE -1)
    lvi[i]=li[0]+vi[0]
    res=STRSPLIT(meta_arr[lvi[i]],'=',/Extract)
    IF convtolng THEN lv=mv_lng[i,vc] ELSE lv=mv_dbl[i,vc]
    tcerr=': '+meta_arr[lvi[i]] ;used for type conversion error
  ENDIF ELSE BEGIN ;check individual data values
    res=['',''] & lin=n_lab-1L ;label index
    tcerr=' in the Data File: '+STRTRIM(dtest[i-lin],2) ;used for type conversion error
    IF convertstr THEN BEGIN
      IF convtolng THEN lv=ROUND(DOUBLE(dtest[i-lin]),/L64) ELSE lv=DOUBLE(dtest[i-lin]) ;LONG64(DOUBLE(dtest[i-lin])) ELSE lv=DOUBLE(dtest[i-lin])
    ENDIF ELSE lv=dtest[i-lin]
  ENDELSE
  IF N_ELEMENTS(res) EQ 2 THEN mok=0 ELSE mok=-1

  IF mok EQ 0 THEN BEGIN
    CASE ndm[vc,8] OF
      0:BEGIN ;BYTE unsigned 8-bit integer (0 to 255)
          ;do difference test to account for possible rounding errors
          IF lv NE BYTE(lv) THEN BEGIN
            STOP_WITH_ERROR,o3[3]+proname+vn[vc]+' (BYTE): ',label[lin]+errtxt2[3]+STRTRIM(lv,2),lu,ds
            RETURN
          ENDIF ELSE vhold[i]=BYTE(lv)
        END
      1:BEGIN ;SHORT signed 16-bit integer (-32,768 to 32,767)
          ;do difference test to account for possible rounding errors
          IF lv NE FIX(DOUBLE(lv)) THEN BEGIN
            STOP_WITH_ERROR,o3[3]+proname+vn[vc]+' (SHORT): ',label[lin]+errtxt2[3]+STRTRIM(lv,2),lu,ds
            RETURN
          ENDIF ELSE vhold[i]=FIX(DOUBLE(lv))
        END
      2:BEGIN ;INTEGER signed 32-bit integer (-2.147e+9 to 2.147e+9)
          ;do difference test to account for possible rounding errors
          IF lv NE LONG(DOUBLE(lv)) THEN BEGIN
            STOP_WITH_ERROR,o3[3]+proname+vn[vc]+' (INTEGER): ',label[lin]+errtxt2[3]+STRTRIM(lv,2),lu,ds
            RETURN
          ENDIF ELSE vhold[i]=LONG(DOUBLE(lv))
        END
      3:BEGIN ;INTEGER signed 64-bit integer (-9.223e+18 to 9.223e+18)
          ;do difference test to account for possible rounding errors
          IF ABS(DOUBLE(lv)-DOUBLE(lv)) GE 1. THEN BEGIN
            STOP_WITH_ERROR,o3[3]+proname+vn[vc]+' (LONG): ',label[lin]+errtxt2[3]+STRTRIM(lv,2),lu,ds
            RETURN
          ENDIF ELSE vhold[i]=LONG64(DOUBLE(lv))
        END
      4:BEGIN
          IF NOT FINITE(FLOAT(lv)) THEN BEGIN
            STOP_WITH_ERROR,o3[3]+proname+vn[vc]+' (REAL): ',label[lin]+errtxt2[3]+STRTRIM(lv,2),lu,ds
            RETURN
          ENDIF ELSE vhold[i]=FLOAT(lv)
        END
      5:BEGIN
          IF NOT FINITE(DOUBLE(lv)) THEN BEGIN
            STOP_WITH_ERROR,o3[3]+proname+vn[vc]+' (DOUBLE): ',label[lin]+errtxt2[3]+STRTRIM(lv,2),lu,ds
            RETURN
          ENDIF ELSE vhold[i]=DOUBLE(lv)
        END
    ENDCASE
  ENDIF ELSE BEGIN
    STOP_WITH_ERROR,o3[3]+proname+vn[vc],label[lin]+errtxt2[0]+tcerr,lu,ds & RETURN
  ENDELSE
  valid=1 ;type conversion OK if got to here
ENDFOR

;Check if VAR_FILL_VALUE falls within VAR_VALID_MIN/MAX - if so it is defined
;as a default, rather than missing/error value
mnv=vhold[0] & mxv=vhold[1] & fv=vhold[2]
IF (fv GE mnv) AND (fv LE mxv) THEN BEGIN
  infotxt='0 Fill value for '+meta_arr[vi[0]]+' falls within the data'
  infotxt=infotxt+' range and is defined as a ''Default'' value'
  INFOTXT_OUTPUT,infotxt
ENDIF

dtest=vhold[n_lab-1L:ndl+(n_lab-2L)]

;determine whether minimum and maximum data values are within VAR_VALID_MIN/MAX
nfvi=WHERE(dtest NE fv,nfvcnt)
IF nfvcnt NE 0 THEN BEGIN ;i.e. there are non-fill values in the data
  minv=MIN(dtest(nfvi),minvi,MAX=maxv,SUBSCRIPT_MAX=maxvi)
  IF minv LT mnv THEN BEGIN ;Minimum data value is less than VAR_VALID_MIN
     IF ndm[vc,8] EQ 0 THEN itxt=STRTRIM(FIX(dtest[nfvi[minvi]]),2) $
     ELSE itxt=STRTRIM(dtest[nfvi[minvi]],2)
     infotxt='3 Minimum data value of '+itxt+' is outside '+meta_arr[lvi[0]]
     infotxt=infotxt+' for dataset '+vn[vc]
     INFOTXT_OUTPUT,infotxt
     ;STOP_WITH_ERROR,o3[3]+proname+vn[vc]+': ','Minimum'+errtxt2[1]+ $
     ;                'MIN: '+STRTRIM(dtest[nfvi[minvi]],2)+' ('+meta_arr[lvi[0]]+').',lu,ds
     ;RETURN
   ENDIF
   IF maxv GT mxv THEN BEGIN ;Maximum data value is greater than VAR_VALID_MAX
     IF ndm[vc,8] EQ 0 THEN itxt=STRTRIM(FIX(dtest[nfvi[maxvi]]),2) $
     ELSE itxt=STRTRIM(dtest[nfvi[maxvi]],2)
     infotxt='3 Maximum data value of '+itxt+' is outside '+meta_arr[lvi[1]]
     infotxt=infotxt+' for dataset '+vn[vc]
     INFOTXT_OUTPUT,infotxt
     ;STOP_WITH_ERROR,o3[3]+proname+vn[vc]+': ','Maximum'+errtxt2[1]+ $
     ;                'MAX: '+STRTRIM(dtest[nfvi[maxvi]],2)+' ('+meta_arr[lvi[1]]+').',lu,ds
     ;RETURN
   ENDIF
ENDIF

;Do Checks with DATETIME attribute
IF vn[vc] EQ 'DATETIME' THEN BEGIN
  ;Does DATETIME contain any fill values?
  di=WHERE(dtest EQ fv,dcnt)
  IF dcnt NE 0 THEN BEGIN
    ;'DTFVOK' = DATETIME fill value is OK
    IF (o3[5] EQ 'DTFVOK') AND (dcnt NE ndl) THEN itxt='1 ' ELSE itxt='3 '
    infotxt=itxt+'DATETIME contains fill value(s)'
    INFOTXT_OUTPUT,infotxt
    ;STOP_WITH_ERROR,o3[3]+proname,errtxt2[4]+STRTRIM(dtest[di[0]],2),lu,ds & RETURN
  ENDIF
  di=WHERE(dtest NE fv,dcnt)
  IF dcnt GT 1 THEN BEGIN
    ;Are DATETIME values in chronological order?
    dsort=SORT(dtest[di])
    IF ARRAY_EQUAL(dtest[di],dtest[di[dsort]]) EQ 0 THEN BEGIN
      IF o3[5] EQ 'DTFVOK' THEN itxt='1 ' ELSE itxt='3 '
      infotxt=itxt+'DATETIME values are not in chronological order'
      INFOTXT_OUTPUT,infotxt
      ;STOP_WITH_ERROR,o3[3]+proname,errtxt2[5],lu,ds & RETURN
    ENDIF
  ENDIF
ENDIF

TypeConversionError:
IF valid EQ 0 THEN STOP_WITH_ERROR,o3[3]+proname+'VAR_NAME='+vn[vc]+': ',errtxt2[6]+tcerr,lu,ds

END ;procedure Check_Min_Max_Fill



PRO read_data, sds, inf
;Procedure to perform checks on the data file or structure. It looks for missing or invalid
;VAR_VALID_MIN/MAX attribute values for datasets which have VAR_UNITS=MJD2K (including
;start and stop times), and determines these values according to values in the data.  It
;also adds a comment to VAR_NOTES if averaging kernel data is present, to indicate the
;proper array order (if this option is chosen on program start-up).
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20050802: Original IDLCR8HDF routine - Version 1.0
;    20050909: Check that the input data file is not empty; test for the correct number of
;              datalines in the dataset being searched (e.g. there is not an additional data
;              line in the input file); Bug fix to save dtest as an array when there is only
;              one data value, and the input data is in a structure - Version 1.1
;    20061012: Portion of routine originally extracting a dataset from the file or structure
;              moved to the EXTRACT_DATA routine; Code added to determine missing or invalid
;              minimum or maximum metadata values for DATETIME, or START/STOP.TIME attributes;
;              Code added to append a comment to VAR_NOTES if averaging kernel data is present,
;              to indicate proper array order (if /AVK option selected); Checked data written
;              to the ds structure instead of a series of arrays set-up according to data type;
;              Common variable definition WIDGET_WIN added - Version 2.0
;    20080302: dtest initialized for the EXTRACT_DATA call - Version 3.0
;    20100205: Add test to allow for RETURN to the calling program after STOP_WITH_ERROR calls
;              made by the external routines used by this this procedure - Version 3.09
;    20101120: Account for new GEOMS rules regarding DATETIME.START/STOP and MJD2K; Do check for
;              averaging kernel vector instead of matrix, in which case do not add AVK comment,
;              if /AVK option chosen - Version 4.0
;
;  Inputs: sds - Either a structure containing the Variable Attributes and Data, or the input
;                data file
;          inf - flag identifying SDS type where, 0=structure; 1=data file
;          meta_arr - a string array containing the Global and Variable Attributes
;
;  Outputs: meta_arr - completes missing or invalid metadata values for attributes with
;                      VAR_UNITS=MJD2K, as required, and also adds comments to VAR_NOTES
;                      for averaging kernel data to indicate proper array order, if this
;                      option is chosen
;           ds - checked datasets are written to the ds structure with correct dimensions and
;                data type
;
;  Called by: IDLCR8HDF
;
;  Subroutines Called: EXTRACT_DATA
;                      CHECK_MIN_MAX_FILL

COMMON METADATA
COMMON DATA
COMMON WIDGET_WIN

;Go through variable names and check for DATETIME, DATETIME.START, or DATETIME.STOP
;values and determine representative minimum and maximum datetime values
mint=90000.D & maxt=-90000.D ;initialize min and max datetimes
valfound=0 ;count variable that increments when DATETIME and related datasets are found
errorfound=1 ;variable to indicate error in DATETIME checks
vchk=['VAR_VALID_MIN','VAR_VALID_MAX']
nvchk=N_ELEMENTS(vchk) & mmi=INTARR(nvchk)
FOR i=0,nvchk-1 DO BEGIN
  mi=WHERE(attr_arr_data EQ vchk[i]) & mmi[i]=mi[0]
ENDFOR
vavk=INTARR(nvn) ;holding array for AVK attribute (used below)

;Determine number of DATETIME values, and set arrays for DATETIME checks
dtfv=DBLARR(3)-mint
dti=WHERE(vn EQ 'DATETIME',dtcnt)
IF dtcnt NE 0 THEN BEGIN
  dtest=['0'] ;initializing dtest array for EXTRACT_DATA call
  EXTRACT_DATA,sds,inf,dti[0],dtest ;return the dataset
  IF STRLEN(rerr[0]) GT 2 THEN RETURN
  dtchk=N_ELEMENTS(dtest)
  dtvals=DBLARR(3,dtchk)-mint
  errorfound=0
ENDIF ELSE BEGIN
  dti=WHERE(vn EQ 'DATETIME.START',dtcnt)
  dtsi=WHERE(vn EQ 'DATETIME.STOP',dtscnt)
  IF (dtcnt NE 0) AND (dtscnt NE 0) THEN BEGIN
    dtest=['0'] ;initializing dtest array for EXTRACT_DATA call
    EXTRACT_DATA,sds,inf,dti[0],dtest ;return the dataset
    IF STRLEN(rerr[0]) GT 2 THEN RETURN
    dtchk=N_ELEMENTS(dtest)
    dtest=['0'] ;initializing dtest array for EXTRACT_DATA call
    EXTRACT_DATA,sds,inf,dtsi[0],dtest ;return the dataset
    IF STRLEN(rerr[0]) GT 2 THEN RETURN
    IF dtchk EQ N_ELEMENTS(dtest) THEN BEGIN
      dtvals=DBLARR(3,dtchk)-mint
      errorfound=0
    ENDIF
  ENDIF
ENDELSE

FOR vc=0,nvn-1 DO BEGIN
  vnspl=STRSPLIT(vn[vc],'_',/Extract)
  vnspl=[vnspl,'x','x'] ;ensures vnspl has a minimum of 3 values
  IF (vnspl[1] EQ 'AVK') OR (vnspl[2] EQ 'AVK') THEN vavk[vc]=1 ;identifies a dataset containing AVK data
  IF ((vn[vc] EQ 'DATETIME') OR (vn[vc] EQ 'DATETIME.START') OR $
     (vn[vc] EQ 'DATETIME.STOP')) THEN BEGIN
    dtest=['0'] ;initializing dtest array for EXTRACT_DATA call
    EXTRACT_DATA,sds,inf,vc,dtest ;return the dataset
    IF STRLEN(rerr[0]) GT 2 THEN RETURN
    IF errorfound EQ 0 THEN BEGIN
      dtnel=N_ELEMENTS(dtest)
      CASE 1 OF
        vn[vc] EQ 'DATETIME.START': BEGIN
            IF dtnel EQ dtchk THEN dtvals[0,*]=DOUBLE(dtest) $
            ELSE IF dtnel EQ 1 THEN dtvals[0,0]=DOUBLE(dtest) $
            ELSE errorfound=1
            dtfv[0]=mv_dbl[2,vc]
          END
        vn[vc] EQ 'DATETIME': BEGIN
            dtvals[1,*]=DOUBLE(dtest) & dtfv[1]=mv_dbl[2,vc]
          END
        ELSE: BEGIN
            IF dtnel EQ dtchk THEN dtvals[2,*]=DOUBLE(dtest) $
            ELSE IF dtnel EQ 1 THEN dtvals[2,dtchk-1]=DOUBLE(dtest) $
            ELSE errorfound=1
            dtfv[2]=mv_dbl[2,vc]
          END
      ENDCASE
    ENDIF
    gi=WHERE(DOUBLE(dtest) NE mv_dbl[2,vc],gcnt) ;edit out fill values
    IF gcnt NE 0 THEN BEGIN
      minth=MIN(DOUBLE(dtest[gi]),MAX=maxth)
      IF minth LT mint THEN mint=minth
      IF maxth GT maxt THEN maxt=maxth
      ;IF vn[vc] EQ 'DATETIME.START' THEN mint=minth $
      ;ELSE IF vn[vc] EQ 'DATETIME.STOP' THEN maxt=maxth
    ENDIF
    valfound=valfound+1
  ENDIF
ENDFOR

IF (errorfound EQ 0) AND (valfound GT 1) THEN BEGIN
  ;Make all missing values equal to fill values
  FOR i=0,2 DO BEGIN
    mi=WHERE(dtvals[i,*] EQ -90000.D,mcnt)
    IF mcnt NE 0 THEN dtvals[i,mi]=dtfv[i]
  ENDFOR
  ;Check that DATETIME.START LE DATETIME LE DATETIME.STOP
  i=0L
  WHILE (errorfound EQ 0) AND (i LE dtchk-1L) DO BEGIN
    test1=(dtvals[0,i] NE dtfv[0]) AND (dtvals[1,i] NE dtfv[1])
    test2=(dtvals[1,i] NE dtfv[1]) AND (dtvals[2,i] NE dtfv[2])
    test3=(dtvals[0,i] NE dtfv[0]) AND (dtvals[2,i] NE dtfv[2])
    IF (test1) AND (dtvals[0,i] GT dtvals[1,i]) THEN errorfound=1
    IF (test2) AND (dtvals[1,i] GT dtvals[2,i]) THEN errorfound=2
    IF (test3) AND (dtvals[0,i] GT dtvals[2,i]) THEN errorfound=3
    i=i+1L
  ENDWHILE
  IF errorfound NE 0 THEN BEGIN
    v0=STRTRIM(STRING(format='(d18.9)',dtvals[0,i-1L]),2)
    v1=STRTRIM(STRING(format='(d18.9)',dtvals[1,i-1L]),2)
    v2=STRTRIM(STRING(format='(d18.9)',dtvals[2,i-1L]),2)
    CASE 1 OF
      errorfound EQ 1: itxt=['DATETIME.START='+v0,'DATETIME='+v1]
      errorfound EQ 2: itxt=['DATETIME='+v1,'DATETIME.STOP='+v2]
      ELSE: itxt=['DATETIME.START='+v0,'DATETIME.STOP='+v2]
    ENDCASE
    infotxt='3 '+itxt[0]+' is greater than '+itxt[1]
    INFOTXT_OUTPUT,infotxt
  ENDIF
ENDIF

valfound=0 ;Boolean to indicate whether missing VAR_VALID_MIN/MAX values have been added
;Add minimum and maximum values to Metadata as required
di=WHERE(STRUPCASE(vu) EQ 'MJD2K',dcnt)
IF dcnt NE 0 THEN BEGIN
  FOR vc=0,dcnt-1 DO BEGIN
    mi=WHERE(meta_arr EQ 'VAR_NAME='+vn[di[vc]])
    FOR i=0,nvchk-1 DO BEGIN
      res=STRSPLIT(meta_arr[mi[0]+mmi[i]],'=',/Extract,COUNT=nres)
      IF nres EQ 1 THEN BEGIN ;no value so add Min or Max value to this attribute
        IF i MOD 2 EQ 0 THEN BEGIN
          IF mint NE 90000.d THEN BEGIN
            meta_arr[mi[0]+mmi[i]]=vchk[i]+'='+STRTRIM(STRING(format='(d18.9)',mint),2)
            valfound=1
          ENDIF
          mv_dbl[i,di[vc]]=mint
        ENDIF ELSE BEGIN
          IF maxt NE -90000.d THEN BEGIN
            meta_arr[mi[0]+mmi[i]]=vchk[i]+'='+STRTRIM(STRING(format='(d18.9)',maxt),2)
            valfound=1
          ENDIF
          mv_dbl[i,di[vc]]=maxt
        ENDELSE
        IF valfound EQ 1 THEN BEGIN
          infotxt=STRARR(2)
          infotxt[0]='2 Missing '+vchk[i]+' value for '+meta_arr[mi[0]]+'| added based on available'
          infotxt[1]='    DATETIME[.START][.STOP] values: '+meta_arr[mi[0]+mmi[i]]
          INFOTXT_OUTPUT,infotxt
        ENDIF
      ENDIF
    ENDFOR
  ENDFOR
ENDIF

IF o3[1] EQ 'AVK' THEN BEGIN ;append sentence to VAR_NOTES in the AVK attribute
  di=WHERE(vavk EQ 1,dcnt)
  vnc=STRARR(nvn) ;holding array for comment
  IF dcnt NE 0 THEN BEGIN
    FOR vc=0,dcnt-1 DO BEGIN
      mi=WHERE(meta_arr EQ 'VAR_NAME='+vn[di[vc]])
      ;check to see if AVK is a matrix or vector (no need for comment if it us a vector)
      add_comm=0 ;default is for no comment
      xi=WHERE(attr_arr_data EQ 'VAR_DEPEND')
      res=STRSPLIT(meta_arr[mi[0]+xi[0]],'=; ',/EXTRACT,COUNT=nres)
      res=STRUPCASE(res)
      IF nres GE 3 THEN BEGIN
        FOR i=1,nres-1 DO BEGIN
          ri=WHERE(res[i] EQ res,rcnt) ;i.e. repeated dependencies indicate an AVK matrix
          IF rcnt GE 2 THEN add_comm=1
        ENDFOR
      ENDIF
      IF add_comm THEN BEGIN
        ;find relevant VAR_NOTES attribute label
        xi=WHERE(attr_arr_data EQ 'VAR_NOTES')
        eqpos=STRPOS(meta_arr[mi[0]+xi[0]],'=')
        vnc[di[vc]]=STRTRIM(STRMID(meta_arr[mi[0]+xi[0]],eqpos+1),2) ;existing VAR_NOTES comment, if any
        ;if comment exists, check to see if it ends with a period, if not add one
        IF vnc[di[vc]] NE '' THEN BEGIN
          IF STRMID(vnc[di[vc]],STRLEN(vnc[di[vc]])-1,1) NE '.' THEN $
            vnc[di[vc]]=vnc[di[vc]]+'. ' ELSE vnc[di[vc]]=vnc[di[vc]]+' '
        ENDIF
        ;determine the number of dimensions
        ni=WHERE(ndm[di[vc],0:7] NE 0,ndim)
        IF ndim GT 2 THEN vncx='for the first measurement are:' ELSE vncx='are:'
        ;append comment
        vnc[di[vc]]=vnc[di[vc]]+'First three AVK values for the lowest altitude level '+vncx
        ;append meta_arr index to comment
        vnc[di[vc]]=STRTRIM(mi[0]+xi[0],2)+'_'+vnc[di[vc]]
      ENDIF
    ENDFOR
  ENDIF
ENDIF

FOR vc=0,nvn-1 DO BEGIN
  dtest=['0'] ;initializing dtest array for EXTRACT_DATA call
  ;Extract the dataset
  EXTRACT_DATA,sds,inf,vc,dtest,ndl
  IF STRLEN(rerr[0]) GT 2 THEN RETURN
  ;perform checks on the attribute and data values
  IF ndm[vc,8] EQ 6 THEN CHECK_STRING_DATATYPE,vc,dtest $ ;Test for String Datatype
  ELSE BEGIN
    CHECK_MIN_MAX_FILL,vc,dtest,ndl ;Test for Numeric Datatype
    IF STRLEN(rerr[0]) GT 2 THEN RETURN
  ENDELSE

  ;if AVK dataset extracted then add comment to VAR_NOTES if required
  IF o3[1] EQ 'AVK' THEN BEGIN
    IF (vnc[vc] NE '') AND (ndm[vc,0] GE 3) THEN BEGIN
      res=STRSPLIT(vnc[vc],'_',/Extract) & mi=FIX(res[0])
      meta_arr[mi]='VAR_NOTES='+res[1]
      FOR i=0,2 DO meta_arr[mi]=meta_arr[mi]+' '+STRTRIM(dtest[i],2)
    ENDIF
  ENDIF

  ;Copy data to the data structure with correct dimensions and data type
  arrchk=SIZE(dtest) ;put it into array form if it is a scalar
  IF arrchk[0] EQ 0 THEN dtest=[dtest]
  gi=WHERE(ndm[vc,0:7] NE 0)
  vs=TRANSPOSE(ndm[vc,gi])
  dtest=REFORM(dtest,vs,/Overwrite)
  ds[vc].data=PTR_NEW(dtest)
ENDFOR

END ;Procedure Read_Data



PRO find_hdf_filename, hdffilename
;Procedure to do the following:
;1. Compare the DATA_START_DATE and DATA_STOP_DATE with the first and last entries under
;   DATETIME. If necessary create/change DATA_START_DATE and DATA_STOP_DATE to match the
;   DATETIME entries, and put in ISO8601 format.
;2. Compare filename created by the program from the DATASET_ATTRIBUTES with that under the
;   FILE_NAME entry (if present). If necessary create/change the FILE_NAME entry to match the
;   created filename
;3. Create/change the FILE_GENERATION_DATE and ensure it is in ISO8601 format.
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20050802: Original IDLCR8HDF routine - Version 1.0
;    20050909: Remove requirement for a 'v' to be at the start of the DATA_FILE_VERSION
;              (e.g. v1.0 or 1.0 acceptable); Change the format that DATA_START_DATE and
;              FILE_GENERATION_DATE values are saved in the HDF file from MJD2000 to
;              ISO8601 - Version 1.1
;    20051107: Move VIS_SCALE_MIN/MAX checks, for correct format of DATETIME values, to the
;              CHECK_MIN_MAX_FILL routine - Version 1.11
;    20061012: Move the FILE_GENERATION_DATE checks to the main loop which determines the file
;              name to facilitate the future option of including the file generation date in the
;              file name (this option is not currently implemented by the AVDC); Common variable
;              definition WIDGET_WIN added - Version 2.0
;    20080302: Do search for either DATA_LEVEL or DATA_TYPE, depending on whether an AVDC style
;              TAV file or original Envisat table.dat file has been read in; Common variable
;              definition TABLEDATA added (tab_type used to differentiate between the databases)
;              - Version 3.0
;    20090610: Allow for the Global Variable DATA_STOP_DATE and calculate the value if required
;              - Version 3.07
;    20100205: Add RETURN command after all STOP_WITH_ERROR calls, which allows program to return to the
;              calling program if the reterr argument is included in the idlcr8hdf call - Version 3.09
;    20101120: Account for new GEOMS changes to filename composition - Version 4.0
;
;  Inputs: meta_arr - a string array containing the Global and Variable Attributes
;          hfdfilename - a string holding the extension of the eventual HDF filename, either
;                        '.hdf' for HDF4 or '.h5' for HDF5
;
;  Outputs: meta_arr - DATA_START_DATE, FILE_GENERATION_DATE and FILE_NAME values will be
;                      (re)written to the array based on values computed by the routine
;           hdffilename - a string holding the full HDF file name determined by the routine
;
;  Called by: IDLCR8HDF
;
;  Subroutines Called: STOP_WITH_ERROR (if error state detected); INFOTXT_OUTPUT
;    Possible Conditions for STOP_WITH_ERROR call (plus [line number] where called):
;      1. An incorrect number of sub-values found in meta_arr for DATA_DISCIPLINE,
;         DATA_SOURCE, DATA_LOCATION, or DATA_FILE_VERSION [3129]
;      2. Error encountered when converting ISO8601 datetime values to MJD2000 format [3138,3179]
;      3. Type conversion error encountered when a datetime value is expected to be in
;         MJD2000 format, but is not numeric [3216]
;
;    Information Conditions (when the program is able to make changes):
;      1. DATA_START_DATE or DATA_STOP_DATE changed to match relevant DATETIME entries [3167]
;      2. Filename determined from DATASETS attributes [3208]

COMMON TABLEDATA
COMMON METADATA
COMMON DATA
COMMON WIDGET_WIN

;Possible error messages for this procedure
ON_IOERROR,TypeConversionError
errtxt=STRARR(4) & lu=-1L
proname='Find_HDF_Filename procedure: '
errtxt[0]='Incorrect number of sub-values under DATA_'
errtxt[1]=' (Should be '
errtxt[2]=' ISO8601 format not valid: '
errtxt[3]='Type conversion error.  MJD2K entry is not valid: '

fhold='' & iso='' & mjd2000=0.d
dtmjd=0.d & dtiso='' & itxt=' '
dt=['DISCIPLINE','SOURCE','LOCATION','START_DATE','STOP_DATE','FILE_GENERATION_DATE','FILE_VERSION']
valid=0 ;test for Type conversion errors
FOR i=0,N_ELEMENTS(dt)-1 DO BEGIN
  IF i EQ 0 THEN BEGIN
    nei=4 & nes='3)'
  ENDIF ELSE BEGIN
    nei=2 & nes='1)'
  ENDELSE
  IF i EQ 5 THEN ai=WHERE(attr_arr_glob EQ dt[i]) $
  ELSE ai=WHERE(attr_arr_glob EQ 'DATA_'+dt[i])

  res=STRSPLIT(meta_arr[ai[0]],' =;',/Extract)
  IF (N_ELEMENTS(res) NE nei) AND ((i LE 2) OR (i GE 6)) THEN BEGIN
    STOP_WITH_ERROR,o3[3]+proname+meta_arr[ai[0]]+': ',errtxt[0]+dt[i]+errtxt[1]+nes,lu,ds
    RETURN
  ENDIF
  
  IF i EQ 6 THEN BEGIN ;Do DATA_FILE_VERSION checks
    dfvv=res[1]
    GEOMS_RULE_CHANGES,4,dfvv
    res[1]=dfvv & meta_arr[ai[0]]='DATA_FILE_VERSION='+dfvv
  ENDIF
  
  IF (i EQ 3) OR (i EQ 4) THEN BEGIN ;calculate the ISO or MJD2000 value as required
    ;Find lowest or highest DATETIME values from Variable Attributes
    IF i EQ 3 THEN BEGIN
      di=WHERE(vn EQ 'DATETIME.START',dcnt)
      itxt= ' first ' & etxt='DATETIME.START '
    ENDIF ELSE BEGIN
      di=WHERE(vn EQ 'DATETIME.STOP',dcnt)
      itxt= ' last ' & etxt='DATETIME.STOP '
    ENDELSE
    IF dcnt NE 0 THEN BEGIN
      darr=*ds[di[0]].data ;extract the DATETIME values
      ;remove any fill values
      fi=WHERE(darr NE mv_dbl[2,di[0]],dcnt)
    ENDIF
    IF dcnt EQ 0 THEN BEGIN
      di=WHERE(vn EQ 'DATETIME',dcnt) & etxt='DATETIME '
      IF dcnt NE 0 THEN BEGIN
        darr=*ds[di[0]].data ;extract the DATETIME values
        ;remove any fill values
        fi=WHERE(darr NE mv_dbl[2,di[0]],dcnt)
      ENDIF
    ENDIF
    IF dcnt NE 0 THEN BEGIN
      darr=darr[fi]
      IF N_ELEMENTS(darr) EQ 1 THEN itxt=' '
      IF i EQ 3 THEN dtmjd=MIN(darr) ELSE dtmjd=MAX(darr)
      dtiso=JDF_2_DATETIME(dtmjd,/M,/S) ;returns datetime in ISO8601 format
      ;Extract DATA_START/STOP_DATE from the Global Attributes, if present
      IF N_ELEMENTS(res) EQ nei THEN BEGIN ;a date/time value is present
        IF STRPOS(STRUPCASE(res[1]),'Z') NE -1 THEN BEGIN
          res[1]=STRUPCASE(res[1])
          mjd2000=JULIAN_DATE(res[1],/I,/M) ;return ISO8601 time in MJD2000 format
          IF mjd2000 EQ -99999.d THEN BEGIN ;conversion error
            STOP_WITH_ERROR,o3[3]+proname,res[0]+errtxt[2]+res[1],lu,ds & RETURN
          ENDIF
        ENDIF ELSE BEGIN
          mjd2000=DOUBLE(res[1])
          iso=JDF_2_DATETIME(mjd2000,/M,/S) ;return MJD2000 time in ISO8601 format
          res[1]=iso
          IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN qtxt=' is not in ' $
          ELSE qtxt= ' converted to '
          infotxt='2 '+meta_arr[ai[0]]+qtxt+'ISO8601 format'
          INFOTXT_OUTPUT,infotxt
        ENDELSE
      ENDIF ELSE mjd2000=-99999.0D
      ;Check that DATA_START_DATE matches the first value under DATETIME.START or DATETIME
      ;and DATA_STOP_DATE matches the last value under DATETIME.STOP or DATETIME (if present)
      IF ABS(mjd2000-dtmjd) GE 1./86400. THEN BEGIN
        IF N_ELEMENTS(res) EQ nei THEN BEGIN
          infotxt=STRARR(3)
          infotxt[0]='2 Date in DATA_'+dt[i]+' does not match'+itxt+etxt+'entry'
          infotxt[1]='    '+res[1]+' -> '+dtiso+'|'
          infotxt[2]='    DATA_'+dt[i]+' changed to match'+itxt+etxt+'entry'
        ENDIF ELSE BEGIN
          IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN qtxt='should be '+dtiso $
          ELSE qtxt=dtiso+' added'
          infotxt='2 Missing DATA_'+dt[i]+' value '+qtxt+' based on'+itxt+etxt+'entry'
        ENDELSE
        INFOTXT_OUTPUT, infotxt
        res=[res[0],dtiso] ;new ISO time for filename
      ENDIF
      meta_arr[ai[0]]=res[0]+'='+res[1] ;rewrite (correct) value in meta_arr in ISO8601 format
    ENDIF ELSE IF N_ELEMENTS(res) EQ 1 THEN res=[res,'[MISSING]']
  ENDIF
  IF i EQ 5 THEN BEGIN
    ;check format of FILE_GENERATION_DATE value and create/change if necessary
    IF N_ELEMENTS(res) EQ 1 THEN res=[res,'-1']
    IF STRPOS(STRUPCASE(res[1]),'Z') NE -1 THEN BEGIN
      mjd2000=JULIAN_DATE(res[1],/I,/M) ;return time in MJD2000 format
      IF mjd2000 EQ -99999.d THEN res=[res[0],'-2'] $ ;conversion error
      ELSE meta_arr[ai[0]]=res[0]+'='+STRTRIM(STRUPCASE(res[1]),2) ;rewrite date in ISO8601 format
    ENDIF
    IF STRPOS(STRUPCASE(res[1]),'Z') EQ -1 THEN BEGIN
      ;FILE_GENERATION_DATE not present or not in ISO8601 format so recalculate
      mjd2000=SYSTIME(/Julian,/UTC)-2451544.5D
      mjds=JDF_2_DATETIME(mjd2000,/M,/S) ;returns datetime in ISO8601 format
      meta_arr[ai[0]]=res[0]+'='+mjds ;write date in ISO8601 format
      IF res[1] EQ '-1' THEN itxt='not present' ELSE itxt='not in ISO8601 format'
      infotxt='2 '+res[0]+' value '+itxt+'|. Recalculated using the system time'
      INFOTXT_OUTPUT,infotxt
      res[1]=mjds
    ENDIF
    ;Test to see if DATA_STOP_DATE is greater than FILE_GENERATION_DATE
    IF dtmjd GT mjd2000 THEN BEGIN
      infotxt='3 Calculated DATA_STOP_DATE='+dtiso+' is later than '+meta_arr[ai[0]]
      INFOTXT_OUTPUT,infotxt
    ENDIF
  ENDIF
  IF i NE 5 THEN BEGIN
    ;i.e. don't include file generation date in the filename
    IF fhold EQ '' THEN fhold=fhold+STRLOWCASE(res[nei-1]) $
    ELSE fhold=fhold+'_'+STRLOWCASE(res[nei-1])
  ENDIF
ENDFOR
hdffilename=fhold+hdffilename
;check to see if the resulting filename is the same as that under FILE_NAME
ai=WHERE(attr_arr_glob EQ 'FILE_NAME')
res=STRSPLIT(meta_arr[ai[0]],' =',/Extract)
IF N_ELEMENTS(res) EQ 1 THEN res=[res,'-1']
IF hdffilename NE res[1] THEN BEGIN
  IF res[1] NE '-1' THEN BEGIN
    infotxt=STRARR(3)
    infotxt[0]='2 FILE_NAME entry under File Attributes does not match the filename'
    infotxt[0]=infotxt[0]+' determined from the Global Attributes'
    infotxt[1]='    '+res[1]+' -> '+hdffilename+'|'
    infotxt[2]='    Filename determined from Global Attributes used'
  ENDIF ELSE BEGIN
    IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN qtxt='should be '+hdffilename $
    ELSE qtxt=hdffilename+' added'
    infotxt=STRARR(2)
    infotxt[0]='2 Missing FILE_NAME value '+qtxt
    infotxt[1]='    based on Global Attribute values'
  ENDELSE
  INFOTXT_OUTPUT, infotxt
  meta_arr[ai[0]]=res[0]+'='+hdffilename ;change FILE_NAME entry
ENDIF
valid=1 ;Type conversions performed OK

TypeConversionError:
IF valid EQ 0 THEN BEGIN
  STOP_WITH_ERROR,o3[3]+proname+res[0]+': ',errtxt[3]+res[1],lu,ds & RETURN
ENDIF

END ;Procedure Find_HDF_Filename



PRO makean, hdf_fn, obj_id, obj_type, label, value
;Procedure to read the contents of a file given as an attribute value and write
;it directly to the HDF Scientific Dataset or to the annotation file description
;section (depending on its size). Currently set up to always write the contents
;of the file to HDF_SD as the text file size limit is also 4096 bytes.
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20050802: Original IDLCR8HDF routine - Version 1.0
;
;  Inputs: hdf_fn - The file handle identifier for the HDF file
;          obj_id - The Scientific Dataset (SD) identifier of the HDF file or a newly
;                   created dataset
;          obj_type - a string identifying the type of annotation (set to 'FILE')
;          label - a string containing the Attribute label from the metadata
;          value - a string containing the Attribute value from the metadata
;
;  Output: Nil
;
;  Called by: AVDC_HDF_WRITE
;
;  Subroutines Called: None

nchar=4096 ;strlen maximum for writing directly to SD (instead of AN)

;Extract name of file
pos1=STRPOS(value,'"')
pos2=STRPOS(value,'"',/REVERSE_SEARCH)
data_notes_file=STRMID(value,pos1+1,pos2-pos1-1)
OPENR,lu,data_notes_file,/GET_LUN

;read each line and count number of characters in file
dum='' & text_in_file=''
i=0
WHILE NOT EOF(lu) DO BEGIN
  READF,lu,dum
  text_in_file=text_in_file+dum+STRING(10B)  ;+STRING(13B)
  i=i+1
ENDWHILE
FREE_LUN,lu
n1=STRLEN(text_in_file)

;The text-buffer contains n1 characters which will be written either
;to the annotation file description section or directly to the HDF file as
;the value of the current attribute
IF n1 LE nchar THEN HDF_SD_ATTRSET,obj_id,label,text_in_file,n1,/DFNT_CHAR $
ELSE BEGIN
  ;open the HDF output file for AN write operations
  ;Initialize the HDF AN interface for the specified file
  an_id=HDF_AN_START(hdf_fn)

  IF obj_type EQ 'FILE' THEN BEGIN
    ;Get id for the file label annotation
    an_labl_id=HDF_AN_CREATEF(an_id,2)
    ;Get id for the file description annotation
    an_desc_id=HDF_AN_CREATEF(an_id,3)
  ENDIF ELSE BEGIN
    ;Get id for the data object label annotation
    an_labl_id=HDF_AN_CREATE(an_id,DFTAG_NDG,HDF_SD_IDTOREF(obj_id),0)
    ;Get id for the data object description annoatation
    an_desc_id=HDF_AN_CREATE(an_id,DFTAG_NDG,HDF_SD_IDTOREF(obj_id),1)
  ENDELSE

  ;Write the label annotation
  status=HDF_AN_WRITEANN(an_labl_id,label)
  ;Terminate access to the label annotation
  HDF_AN_ENDACCESS,an_labl_id

  ;Write the description annotation
  status=HDF_AN_WRITEANN(an_desc_id,text_in_file)
  ;Terminate access to the description annotation
  HDF_AN_ENDACCESS,an_desc_id

  ;Terminate access to the AN interface
  HDF_AN_END,an_id
ENDELSE

END ;Procedure MakeAN



PRO avdc_hdf5_write, hdffilename, natts, av
;IDL subroutine to write AVDC-type global attributes and datasets to the Root
;Group in an HDF5 file.
;##########################################################################
;Note: In versions of IDL earlier than 6.2, this procedure may not compile
;and the HDF5 write option will not be available.
;##########################################################################
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20061012: Introduced to IDLCR8HDF - Version 2.0
;    20080302: Removed portion of the code which created the DIMENSIONLIST attribute
;              containing the object reference pointers to the variables referred to
;              in the VAR_DEPEND values - Version 3.0
;
;  Inputs: hdffilename - a string holding the name of the HDF file being created
;                        and written to
;          natts - an integer giving the number of Variable Attributes in each
;                  dataset (i.e. the number of elements in attr_arr_data)
;          av - a string array of size (nvn,natts+7) containing the attribute and
;               NCSA values for each dataset
;          ds - structure containing the data
;          meta_arr - a string array containing the Global and Variable Attributes
;          vn - a string array containing the VAR_NAME values
;          ndm - a long array describing the dimensions of each dataset and the
;                VAR_DATA_TYPE
;
;  Outputs: An HDF5 file with the name hdffilename
;
;  Called by: AVDC_HDF_WRITE
;
;  Subroutines Called: None

COMMON METADATA
COMMON DATA

;Create an HDF5 file
hdf_file_id=H5F_CREATE(hdffilename)
H5F_CLOSE, hdf_file_id

;open the HDF5 file for writing.
hdf_file_id=H5F_OPEN(hdffilename,/WRITE)
;The H5G_OPEN function opens an existing group within an HDF5 file
sd_id=H5G_OPEN(hdf_file_id,'/')

;Write the Global Attributes to file
;Section 4.1 (Bojkov et al., 2002): Originator attributes
;Section 4.2 (Bojkov et al., 2002): Dataset attributes
;Section 4.3 (Bojkov et al., 2002): File attributes
FOR i=0,N_ELEMENTS(attr_arr_glob)-1 DO BEGIN
  ;separate out the Meta Attribute entry
  eqpos=STRPOS(meta_arr[i],'=')
  IF eqpos EQ STRLEN(meta_arr[i])-1 THEN attribute_value=' ' $
  ELSE attribute_value=STRMID(meta_arr[i],eqpos+1)
  ;get attribute type and space, needed to create the attribute
  atype_id=H5T_IDL_CREATE(attribute_value)
  aspace_id=H5S_CREATE_SCALAR()
  ;create attribute in the output file
  aset_id=H5A_CREATE(sd_id,attr_arr_glob[i],atype_id,aspace_id)
  ;write attribute to dataset
  H5A_WRITE,aset_id,attribute_value
  ;close all open identifiers
  H5A_CLOSE,aset_id
  H5S_CLOSE,aspace_id
  H5T_CLOSE,atype_id
ENDFOR

;Write the Datasets (SDS) to file
;Section 5.1 (Bojkov et al, 2002): Variable description attributes.
al=STRARR(natts)
al[0:natts-1]=attr_arr_data
FOR i=0,nvn-1 DO BEGIN
  CASE ndm[i,8] OF ;identifies the VAR_DATA_TYPE
    0:BEGIN
        valid_range=[BYTE(mv_lng[0,i]),BYTE(mv_lng[1,i])]
        fill_value=BYTE(mv_lng[2,i])
      END
    1:BEGIN
        valid_range=[FIX(mv_lng[0,i]),FIX(mv_lng[1,i])]
        fill_value=FIX(mv_lng[2,i])
      END
    2:BEGIN
        valid_range=[LONG(mv_lng[0,i]),LONG(mv_lng[1,i])]
        fill_value=LONG(mv_lng[2,i])
      END
    3:BEGIN
        valid_range=[mv_lng[0,i],mv_lng[1,i]]
        fill_value=mv_lng[2,i]
      END
    4:BEGIN
        valid_range=[FLOAT(mv_dbl[0,i]),FLOAT(mv_dbl[1,i])]
        fill_value=FLOAT(mv_dbl[2,i])
      END
    5:BEGIN
        valid_range=[mv_dbl[0,i],mv_dbl[1,i]]
        fill_value=mv_dbl[2,i]
      END
    6:BEGIN
        valid_range=[' ',' ']
        fill_value=' '
      END
  ENDCASE

  ;Make up data array for writing to HDF5 file
  data=*ds[i].data
  ;may have lost array VAR_SIZE information if the last value is '1' e.g. 41,1
  gi=WHERE(ndm[i,0:7] NE 0L) & vs=TRANSPOSE(ndm[i,gi]) ;transpose to get array values in a vector
  ;get dataset type and space, needed to create the dataset
  dtype_id=H5T_IDL_CREATE(data)
  dspace_id=H5S_CREATE_SIMPLE(vs)
  ;create dataset in the output file
  dset_id=H5D_CREATE(sd_id,vn[i],dtype_id,dspace_id)
  ;write data to dataset
  H5D_WRITE,dset_id,data

  ;write out variable attributes
  ninc=0 & j=0
  mi=WHERE(meta_arr EQ attr_arr_data[0]+'='+vn[i])
  WHILE j LE natts-1 DO BEGIN
    ma=mi[0]+ninc
    ;Extract Attribute Label
    eqpos=STRPOS(meta_arr[ma],'=')
    res=STRMID(meta_arr[ma],0,eqpos)
    WHILE res[0] NE al[j] DO j=j+1 ;in case of missing optional variable attributes
    CASE 1 OF
      ;attr_arr_data[j] EQ 'VAR_SIZE': athold=vs
      attr_arr_data[j] EQ 'VAR_VALID_MIN': athold=valid_range[0]
      attr_arr_data[j] EQ 'VAR_VALID_MAX': athold=valid_range[1]
      attr_arr_data[j] EQ 'VAR_FILL_VALUE': athold=fill_value
      ELSE: athold=av[i,j]
    ENDCASE
    ;get attribute type and space, needed to create the attribute
    atype_id=H5T_IDL_CREATE(athold)
    IF N_ELEMENTS(athold) EQ 1 THEN aspace_id=H5S_CREATE_SCALAR() $
    ELSE aspace_id=H5S_CREATE_SIMPLE(N_ELEMENTS(athold))
    ;create attribute in the output file
    aset_id=H5A_CREATE(dset_id,al[j],atype_id,aspace_id)
    ;write attribute to dataset
    H5A_WRITE,aset_id,athold
    ;close all open attribute identifiers
    H5A_CLOSE,aset_id
    H5S_CLOSE,aspace_id
    H5T_CLOSE,atype_id
    ninc=ninc+1 & j=j+1
  ENDWHILE
  ;close all open dataset identifiers
  H5D_CLOSE,dset_id
  H5S_CLOSE,dspace_id
  H5T_CLOSE,dtype_id
ENDFOR

;The H5G_CLOSE procedure closes the specified group and releases resources used by it.
H5G_CLOSE,sd_id
;The H5F_CLOSE procedure closes the HDF file associated with the given file handle.
H5F_CLOSE,hdf_file_id

END ;Procedure AVDC_HDF5_Write



PRO avdc_nc_write, hdffilename, natts, av, var_depend, var_size
;IDL subroutine to write AVDC-type global attributes and datasets to a netCDF file.
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20111120: Introduced to IDLCR8DF - Version 4.0
;    20130116: Account for string datasets which contain only empty string values (make
;              string length = 1) - Version 4.0b15
;
;  Inputs: hdffilename - a string holding the name of the netCDF file being created
;                        and written to
;          natts - an integer giving the number of Variable Attributes in each
;                  dataset (i.e. the number of elements in attr_arr_data)
;          av - a string array of size (nvn,natts+7) containing the attribute and
;               NCSA values for each dataset
;          var_depend - a string array of size (nvn) holding the VAR_DEPEND attribute
;                       values, used to assign DIM information
;          var_size - a string array of size (nvn) holding the VAR_SIZE attribute
;                     values, used to assign DIM information
;          ds - structure containing the data
;          meta_arr - a string array containing the Global and Variable Attributes
;          vn - a string array containing the VAR_NAME values
;          ndm - a long array describing the dimensions of each dataset and the
;                VAR_DATA_TYPE
;
;  Outputs: A netCDF file with the name hdffilename
;
;  Called by: AVDC_HDF_WRITE
;
;  Subroutines Called: None

COMMON METADATA
COMMON DATA

;Create a netCDF file
df_file_id=NCDF_CREATE(hdffilename,/CLOBBER)

;Write the Global Attributes to file
;Section 4.1 (Bojkov et al., 2002): Originator attributes
;Section 4.2 (Bojkov et al., 2002): Dataset attributes
;Section 4.3 (Bojkov et al., 2002): File attributes
FOR i=0,N_ELEMENTS(attr_arr_glob)-1 DO BEGIN
  ;separate out the Meta Attribute entry
  eqpos=STRPOS(meta_arr[i],'=')
  IF eqpos EQ STRLEN(meta_arr[i])-1 THEN attribute_value=' ' $
  ELSE attribute_value=STRMID(meta_arr[i],eqpos+1)
  ;get attribute type and space, needed to create the attribute
  NCDF_ATTPUT,df_file_id,/GLOBAL,attr_arr_glob[i],attribute_value
ENDFOR

;Write the Datasets (SDS) to file
;Section 5.1 (Bojkov et al, 2002): Variable description attributes.
al=STRARR(natts)
al[0:natts-1]=attr_arr_data
vdh=['CONSTANT','INDEPENDENT']
dim_id_list=LONARR(2)-999L
FOR i=0,nvn-1 DO BEGIN

  ;Make up data array for writing to netCDF file
  data=*ds[i].data
  ;may have lost array VAR_SIZE information if the last value is '1' e.g. 41,1
  gi=WHERE(ndm[i,0:7] NE 0L) & vs=TRANSPOSE(ndm[i,gi]) ;transpose to get array values in a vector

  ;Determine Dimension IDs for the Variable
  vdl=STRSPLIT(var_depend[i],' ;',/EXTRACT,COUNT=vdcount)
  vsl=STRSPLIT(var_size[i],' ;',/EXTRACT) & vsl=LONG(vsl)
  IF ndm[i,8] EQ 6 THEN BEGIN ;need to include string length dimension variable
    vdcount++
    IF MAX(STRLEN(data)) EQ 0 THEN mxstrlen=1 ELSE mxstrlen=MAX(STRLEN(data))
    vdl=['STRLEN',vdl] & vsl=[mxstrlen,vsl]
  ENDIF

  dims=LONARR(vdcount)-999L & const=0
  FOR j=0,vdcount-1 DO BEGIN
    ndi=WHERE(STRUPCASE(vdl[j]) EQ vdh,ndc)
    IF vdl[j] EQ 'STRLEN' THEN BEGIN
      ;dataset is of type string so add string length dimension variable to vdh array
      dim_id=NCDF_DIMDEF(df_file_id,vn[i]+'_STRLEN',vsl[j])
      vdh=[vdh,STRUPCASE(vn[i])+'_STRLEN'] ;add dimension variable to vdh array
      dim_id_list=[dim_id_list,dim_id]
      dims[j]=dim_id
    ENDIF ELSE IF ndc EQ 0 THEN BEGIN ;new dimension found for file
      vdh=[vdh,STRUPCASE(vdl[j])] ;add dimension variable to vdh array
      dim_id=NCDF_DIMDEF(df_file_id,vdl[j],vsl[j])
      dim_id_list=[dim_id_list,dim_id]
      dims[j]=dim_id
    ENDIF ELSE BEGIN ;dimension already has ID or is CONSTANT or INDEPENDENT
      IF ndi[0] EQ 0 THEN BEGIN
        ;CONSTANT so no dimension is assigned
        const=1
      ENDIF ELSE IF ndi[0] EQ 1 THEN BEGIN
        ;INDEPENDENT or BOUNDARIES so assign INDEPENDENT/BOUNDARIES_%vs as dimension name
        IF (j EQ 1) AND (STRPOS(vn[i],'.BOUNDARIES') NE -1) THEN itxt='BOUNDARIES_' $
        ELSE itxt='INDEPENDENT_'
        dim_id=NCDF_DIMDEF(df_file_id,itxt+STRTRIM(vsl[j],2),vsl[j])
        vdh=[vdh,itxt+STRTRIM(vsl[j],2)] ;add dimension variable to vdh array
        dim_id_list=[dim_id_list,dim_id]
        dims[j]=dim_id
      ENDIF ELSE dims[j]=dim_id_list[ndi[0]]
    ENDELSE
  ENDFOR

  ;If multi-dimensional reverse dimension IDs as the dataset is automatically transposed
  IF N_ELEMENTS(vs) GT 1 THEN dims=REVERSE(dims)

  CASE ndm[i,8] OF ;identifies the VAR_DATA_TYPE
    0:BEGIN
        valid_range=[BYTE(mv_lng[0,i]),BYTE(mv_lng[1,i])]
        fill_value=BYTE(mv_lng[2,i])
        IF const THEN var_id=NCDF_VARDEF(df_file_id,vn[i],/BYTE) $
        ELSE var_id=NCDF_VARDEF(df_file_id,vn[i],dims,/BYTE)
      END
    1:BEGIN
        valid_range=[FIX(mv_lng[0,i]),FIX(mv_lng[1,i])]
        fill_value=FIX(mv_lng[2,i])
        IF const THEN var_id=NCDF_VARDEF(df_file_id,vn[i],/SHORT) $
        ELSE var_id=NCDF_VARDEF(df_file_id,vn[i],dims,/SHORT)
      END
    2:BEGIN
        valid_range=[LONG(mv_lng[0,i]),LONG(mv_lng[1,i])]
        fill_value=LONG(mv_lng[2,i])
        IF const THEN var_id=NCDF_VARDEF(df_file_id,vn[i],/LONG) $
        ELSE var_id=NCDF_VARDEF(df_file_id,vn[i],dims,/LONG)
      END
    3:BEGIN
        valid_range=[mv_lng[0,i],mv_lng[1,i]]
        fill_value=mv_lng[2,i]
        IF const THEN var_id=NCDF_VARDEF(df_file_id,vn[i],/LONG) $
        ELSE var_id=NCDF_VARDEF(df_file_id,vn[i],dims,/LONG)
      END
    4:BEGIN
        valid_range=[FLOAT(mv_dbl[0,i]),FLOAT(mv_dbl[1,i])]
        fill_value=FLOAT(mv_dbl[2,i])
        IF const THEN var_id=NCDF_VARDEF(df_file_id,vn[i],/FLOAT) $
        ELSE var_id=NCDF_VARDEF(df_file_id,vn[i],dims,/FLOAT)
      END
    5:BEGIN
        valid_range=[mv_dbl[0,i],mv_dbl[1,i]]
        fill_value=mv_dbl[2,i]
        IF const THEN var_id=NCDF_VARDEF(df_file_id,vn[i],/DOUBLE) $
        ELSE var_id=NCDF_VARDEF(df_file_id,vn[i],dims,/DOUBLE)
      END
    6:BEGIN
        valid_range=[' ',' ']
        fill_value=' '
        IF const THEN var_id=NCDF_VARDEF(df_file_id,vn[i],/CHAR) $
        ELSE var_id=NCDF_VARDEF(df_file_id,vn[i],dims,/CHAR)
      END
  ENDCASE

  ;write out variable attributes
  ninc=0 & j=0
  mi=WHERE(meta_arr EQ attr_arr_data[0]+'='+vn[i])
  WHILE j LE natts-1 DO BEGIN
    ma=mi[0]+ninc
    ;Extract Attribute Label
    eqpos=STRPOS(meta_arr[ma],'=')
    res=STRMID(meta_arr[ma],0,eqpos)
    WHILE res[0] NE al[j] DO j=j+1 ;in case of missing optional variable attributes
    CASE 1 OF
      attr_arr_data[j] EQ 'VAR_VALID_MIN': athold=valid_range[0]
      attr_arr_data[j] EQ 'VAR_VALID_MAX': athold=valid_range[1]
      attr_arr_data[j] EQ 'VAR_FILL_VALUE': athold=fill_value
      ELSE: athold=av[i,j]
    ENDCASE
    NCDF_ATTPUT,df_file_id,var_id,attr_arr_data[j],athold
    ninc=ninc+1 & j=j+1
  ENDWHILE

  IF ndm[i,8] NE 6 THEN BEGIN
    NCDF_ATTPUT,df_file_id,var_id,'units',vu[i]
    NCDF_ATTPUT,df_file_id,var_id,'valid_range',valid_range
    NCDF_ATTPUT,df_file_id,var_id,'_Fillvalue',fill_value
  ENDIF

  NCDF_CONTROL,df_file_id,/ENDEF ;Enter Data Mode
  NCDF_VARPUT,df_file_id,var_id,data ;Write Data to file
  NCDF_CONTROL,df_file_id,/REDEF ;Enter Define Mode
ENDFOR

NCDF_CLOSE,df_file_id

END ;Procedure AVDC_NC_Write



PRO avdc_hdf_write, hdffilename
;IDL subroutine to write AVDC-type global attributes and datasets to a Scientific
;Dataset (SDS) in HDF4 (Bojkov et al.,2004) or HDF5. This routine creates the HDF4
;file if requested, and calls the AVDC_HDF5_WRITE routine to create the HDF5 file if
;that option is chosen.
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20050802: Originally split into two routines to separately write the Global
;              attributes (AVDC_HDF_GLOBAL_ATTRIBUTES) and the Variable attributes
;              and data (AVDC_HDF_SDS_VARIABLES) to an HDF4 file - Version 1.0
;    20061012: Two routines combined into the AVDC_HDF_WRITE routine; Call to the
;              AVDC_HDF5_WRITE routine if HDF5 file option is chosen; HDF4 file not
;              closed between writing the global and variable attributes to file;
;              Data now written to file from the ds structure instead of from arrays
;              made according to VAR_DATA_TYPE; the av array made to hold attribute
;              values to write to the HDF file, instead of writing the values to
;              file directly from the meta_arr array (to avoid duplication of code
;              in AVDC_HDF5_WRITE) - Version 2.0
;    20130116: Account for string datasets which contain only empty string values (make
;              string length = 1) - Version 4.0b15
;
;  Inputs: hdffilename - a string holding the name of the HDF file being created
;                        and written to
;          ds - structure containing the data
;          meta_arr - a string array containing the Global and Variable Attributes
;          vn - a string array containing the VAR_NAME values
;          ndm - a long array describing the dimensions of each dataset and the
;                VAR_DATA_TYPE
;
;  Outputs: An HDF4 file with the name hdffilename
;
;  Called by: IDLCR8HDF
;
;  Subroutines Called: MAKEAN
;                      AVDC_HDF5_WRITE (if HDF5 option is chosen)
;                      INFOTXT_OUTPUT
;    Information Conditions (when the program is able to make changes):
;      1. HDF4.2R1 or earlier library and SDS name has greater than 63-characters
;         - in which case the SDS name will be truncated [3573]

COMMON METADATA
COMMON DATA

nodimset=1 ;added from version 3.06 to stop dimension information being written to the HDF4 file
           ;while still retaining original code

;Determine HDF format (ftype is either 'hdf' or 'h5')
ftype=STRMID(hdffilename,STRPOS(hdffilename,'.',/Reverse_Search)+1)

;List of dim. attributes to be assigned to the SDS dimensions.
da_list=['VAR_NAME','VAR_UNITS']
da_att=INDGEN(N_ELEMENTS(da_list),/String) & natts=N_ELEMENTS(attr_arr_data)
av=STRARR(nvn,natts) ;array containing attribute and NCSA values for each dataset
var_depend=STRARR(nvn) ;holding array for the VAR_DEPEND attributes, used to assign DIM information
var_size=STRARR(nvn) ;holding array for the VAR_SIZE attributes, used to assign netCDF DIM information

;Write all Dataset Attribute values to an array
FOR i=0,nvn-1 DO BEGIN ;nvn EQ number of variable names
  mi=WHERE(meta_arr EQ attr_arr_data[0]+'='+vn[i])
  ninc=0 & j=0
  WHILE j LE natts-1 DO BEGIN
    ma=mi[0]+ninc
    ;separate out the Meta entry into two components
    eqpos=STRPOS(meta_arr[ma],'=')
    res=STRMID(meta_arr[ma],0,eqpos)
    WHILE res NE attr_arr_data[j] DO j=j+1 ;in case optional variable attributes are not included
    IF eqpos EQ STRLEN(meta_arr[ma])-1 THEN av[i,j]=' ' $
    ELSE av[i,j]=STRMID(meta_arr[ma],eqpos+1)
    ;Reverse Values for VAR_DEPEND and VAR_SIZE to match order values will be saved in HDF
    IF (res EQ 'VAR_DEPEND') OR (res EQ 'VAR_SIZE') THEN BEGIN
      atval=STRSPLIT(av[i,j],' ;',/EXTRACT,COUNT=avcnt)
      IF avcnt GT 1 THEN BEGIN
        atval=REVERSE(atval)
        FOR k=0,avcnt-1 DO IF k EQ 0 THEN ahold=atval[k] ELSE ahold=ahold+';'+atval[k]
        av[i,j]=ahold
      ENDIF
      IF res EQ 'VAR_DEPEND' THEN var_depend[i]=av[i,j] ELSE var_size[i]=av[i,j]
    ENDIF
    ninc=ninc+1 & j=j+1
  ENDWHILE
ENDFOR

IF ftype EQ 'hdf' THEN BEGIN

  ;Determine HDF library used by this program
  HDF_LIB_INFO,MAJOR=mj,MINOR=mn,RELEASE=rl
  hdf4lib=(mj*100)+(mn*10)+rl
  hdf4txt='HDF'+STRTRIM(mj,2)+'.'+STRTRIM(mn,2)+'R'+STRTRIM(rl,2)

  ;Create and open the HDF4 file for writing
  hdf_file_id=HDF_OPEN(hdffilename,/ALL)
  ;The HDF_SD_START function opens or creates an HDF4 file and initializes the SD interface.
  sd_id=HDF_SD_START(hdffilename,/RDWR)

  ;Write the Global Attributes to file
  ;Section 4.1 (Bojkov et al., 2002): Originator attributes
  ;Section 4.2 (Bojkov et al., 2002): Dataset attributes
  ;Section 4.3 (Bojkov et al., 2002): File attributes
  FOR i=0,N_ELEMENTS(attr_arr_glob)-1 DO BEGIN
    ;separate out the Meta Attribute entry
    eqpos=STRPOS(meta_arr[i],'=')
    IF eqpos EQ STRLEN(meta_arr[i])-1 THEN attribute_value=' ' $
    ELSE attribute_value=STRMID(meta_arr[i],eqpos+1)
    ;check for Free text attribute, and filename entry
    res=STRMID(meta_arr[i],0,eqpos)
    fai=WHERE(res EQ free_attr,facnt)
    IF (facnt NE 0) AND (STRMID(STRUPCASE(attribute_value),0,6) EQ 'FILE("') THEN $
      MAKEAN,hdf_file_id,sd_id,'FILE',res,attribute_value $
    ELSE HDF_SD_ATTRSET,sd_id,attr_arr_glob[i],attribute_value
  ENDFOR

  ;Write the Datasets (SDS) to file
  ;Section 5.1 (Bojkov et al, 2002): Variable description attributes.
  FOR i=0,nvn-1 DO BEGIN ;nvn EQ number of variable names

    ;If hdf4 library version is less than 4.2R2 then check length of VAR_NAME
    IF hdf4lib LT 422 THEN BEGIN
      IF STRLEN(vn[i]) GT 63 THEN BEGIN
        infotxt=STRARR(4)
        infotxt[0]='2 '+hdf4txt+' truncates the dataset name if its'
        infotxt[0]=infotxt[0]+' length is greater than 63-characters.'
        infotxt[1]='    If possible update the HDF4 library to HDF4.2R2 or newer| '
        infotxt[1]=infotxt[1]+'(refer to program documentation for procedure to do this).
        infotxt[2]='    The Archive Data Center may also be set up to update the file'
        infotxt[2]=infotxt[2]+' on submission.'
        infotxt[3]='    VAR_NAME='+vn[i]
        INFOTXT_OUTPUT, infotxt
      ENDIF
    ENDIF

    ;create data array from structure and create and define dataset for an HDF4 file
    data=*ds[i].data
    ;may have lost array VAR_SIZE information if the last value is '1' e.g. 41,1
    gi=WHERE(ndm[i,0:7] NE 0L) & vs=TRANSPOSE(ndm[i,gi])
    type=HDF_IDL2HDFTYPE(SIZE(data,/Type))
    IF ndm[i,8] EQ 6 THEN BEGIN
      mxstrlen=MAX(STRLEN(data)) ;determine maximum stength length
      IF mxstrlen EQ 0 THEN mxstrlen=1
      sds_id_1=HDF_SD_CREATE(sd_id,vn[i],[mxstrlen,vs],HDF_TYPE=type)
    ENDIF ELSE sds_id_1=HDF_SD_CREATE(sd_id,vn[i],vs,HDF_TYPE=type)

    mi=WHERE(meta_arr EQ attr_arr_data[0]+'='+vn[i])
    CASE ndm[i,8] OF ;identifies the VAR_DATA_TYPE
      0:BEGIN
          valid_range=[BYTE(mv_lng[0,i]),BYTE(mv_lng[1,i])]
          fill_value=BYTE(mv_lng[2,i])
        END
      1:BEGIN
          valid_range=[FIX(mv_lng[0,i]),FIX(mv_lng[1,i])]
          fill_value=FIX(mv_lng[2,i])
        END
      2:BEGIN
          valid_range=[LONG(mv_lng[0,i]),LONG(mv_lng[1,i])]
          fill_value=LONG(mv_lng[2,i])
        END
      3:BEGIN
          valid_range=[mv_lng[0,i],mv_lng[1,i]]
          fill_value=mv_lng[2,i]
        END
      4:BEGIN
          valid_range=[FLOAT(mv_dbl[0,i]),FLOAT(mv_dbl[1,i])]
          fill_value=FLOAT(mv_dbl[2,i])
        END
      5:BEGIN
          valid_range=[mv_dbl[0,i],mv_dbl[1,i]]
          fill_value=mv_dbl[2,i]
        END
      6:BEGIN
          valid_range=[' ',' ']
          fill_value=' '
        END
    ENDCASE
    ninc=0 & j=0
    WHILE j LE natts-1 DO BEGIN
      ma=mi[0]+ninc
      ;Extract Attribute Label
      eqpos=STRPOS(meta_arr[ma],'=')
      res=STRMID(meta_arr[ma],0,eqpos)
      WHILE res[0] NE attr_arr_data[j] DO j=j+1
      CASE 1 OF
        ;attr_arr_data[j] EQ 'VAR_SIZE': HDF_SD_ATTRSET,sds_id_1,attr_arr_data[j],vs
        attr_arr_data[j] EQ 'VAR_VALID_MIN': HDF_SD_ATTRSET,sds_id_1,attr_arr_data[j],valid_range[0]
        attr_arr_data[j] EQ 'VAR_VALID_MAX': HDF_SD_ATTRSET,sds_id_1,attr_arr_data[j],valid_range[1]
        attr_arr_data[j] EQ 'VAR_FILL_VALUE': HDF_SD_ATTRSET,sds_id_1,attr_arr_data[j],fill_value
        ELSE: HDF_SD_ATTRSET,sds_id_1,attr_arr_data[j],av[i,j]
      ENDCASE
      ninc=ninc+1 & j=j+1
    ENDWHILE
    ;Set information about the dataset (note no pre-defined attributes for String Datatype)
    IF ndm[i,8] NE 6 THEN $
      HDF_SD_SETINFO,sds_id_1,UNIT=vu[i],RANGE=valid_range,FILL=fill_value

    IF nodimset EQ 0 THEN BEGIN
      ;Assign the VAR_DEPEND dimension(s) attribute information
      vd_out=STRSPLIT(var_depend[i],' ;',/Extract) ;Read the variable dependencies
      vdim=N_ELEMENTS(vd_out)
      vd_out=STRTRIM(vd_out,2)
      ;Start search of information
      FOR j=0,vdim-1 DO BEGIN
        IF (STRUPCASE(vd_out[j]) NE 'CONSTANT') AND (STRUPCASE(vd_out[j]) NE 'INDEPENDENT') THEN BEGIN
          ;Return the index of the var_depend array SDS dataset
          index=HDF_SD_NAMETOINDEX(sd_id,vd_out[j])
          ;Access the dataset
          sds_id_tmp=HDF_SD_SELECT(sd_id,index)
          FOR k=0,N_ELEMENTS(da_list)-1 DO BEGIN
            ;Find the dataset attribute in da_list
            dindex=HDF_SD_ATTRFIND(sds_id_tmp,da_list[k])
            ;Read attribute info and assign to da_att
            HDF_SD_ATTRINFO,sds_id_tmp,dindex,DATA=att_data
            da_att[k]=att_data
          ENDFOR
          ;End access of SDS search
          HDF_SD_ENDACCESS,sds_id_tmp

          ;Assign dimension to the current SDS
          dim_id=HDF_SD_DIMGETID(sds_id_1,j)
          HDF_SD_DIMSET,dim_id,/BW_INCOMP,NAME=da_att[0],UNIT=da_att[1]
        ENDIF
      ENDFOR
    ENDIF

    ;Write data to HDF4 file
    HDF_SD_ADDDATA,sds_id_1,data
    HDF_SD_ENDACCESS,sds_id_1
  ENDFOR

  ;The HDF_SD_END function closes the SD interface to an HDF4 file.
  HDF_SD_END,sd_id
  ;The HDF_CLOSE procedure closes the HDF4 file associated with the given file handle.
  HDF_CLOSE,hdf_file_id
ENDIF ELSE IF ftype EQ 'h5' THEN AVDC_HDF5_WRITE,hdffilename,natts,av $
ELSE AVDC_NC_WRITE,hdffilename,natts,av,var_depend,var_size

END ;Procedure AVDC_HDF_Write



PRO idlcr8hdf, ga, sds, tav, odir, reterr, H5=o1, AVK=o2, LOG=o4, POPUP=o5, QA=o6, NOHDF=o7, NC=o8, DATETIME=o9
;Main IDL program to create HDF4 or HDF5 format files for submission to the AVDC, NDACC, or
;NILU (ESA Envisat) databases.
;
;Program documentation, idlcr8hdf-v4.0_Readme.pdf, available from http://avdc.gsfc.nasa.gov.
;
;Program sub-version 4.0b16 (20131023)
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20050802: Original Release - Version 1.0
;    20050909: No change to routine - Version 1.1
;    20051107: No change to routine - Version 1.11
;    20061012: Make the code suitable for running on a licensed version of IDL (using the .pro
;              and .sav versions of the code) and on IDL Virtual Machine (using the .sav version
;              of the code); Change command line keyword options, remove the /Help (window now
;              opened if there are no command line parameters) and /File options (now automatically
;              identifies whether input is from session memory or files), and add the /H5 (write
;              HDF5), /AVK (for Averaging Kernel Datasets add sentence to VAR_NOTES indicating
;              averaging kernel order), /Log (append input/output information to a log file), and
;              /Popup options (append input/output, error and warning information to a pop-up
;              display window); If input is from files, the program can now handle multiple data
;              files (either as a string array or as a file spec), together with a Metadata template
;              file and the TAV file; Input/output information as well as errors and warnings
;              included in the IDL DE output log window and/or to a log file; The user has the
;              option of continuing to run the program with file inputs from the 'Introduction'
;              window; Common variable definition WIDGET_WIN added - Version 2.0
;    20080302: Remove HELP,/TRACEBACK call, which identified how the program was called. This was used
;              to stop output to the IDLDE output window in the event that IDL VM was used, but it is
;              not required as IDL VM ignores these print calls; Add DIALOG_BOX to show completion
;              of the program if program inputs are via the INTRO box, and logging window option
;              isn't requested - Version 3.0
;    20100205: Add optional reterr parameter which allows program to return to a calling program with
;              an error message, rather than stop - Version 3.09
;    20101120: Adopt GEOMS metadata standard; New structure format required when input is by session
;              memory; New arrays created to hold numeric metadata values (mv_lng and mv_dbl) in
;              either LONG64 or DOUBLE format (changed to their actual format before writing to file);
;              Add QA keyword, to perform QA function on HDF file read into session memory (does not
;              create an HDF file) - Version 4.0
;    20130114: Add check for IDL being run in DEMO mode by using LMGR command. Replace PRINTF,-1 
;              statements (i.e. when dux[0] eq -1) with PRINT (o/w causes DEMO mode to stop. Also disable
;              /LOG and /NC keywords in DEMO mode - Version 4.0b14
;
;  Inputs: DIALOG PROMPTS WITH IDL VIRTUAL MACHINE (File input only)
;            Metadata template file - The program will fill in missing spaces based on data file and
;                                     TAV inputs
;            Data file(s) - the user has the option of picking multiple data files
;            tav - the current Table Attribute Values (TAV) file
;            outdir - the directory which will hold the HDF file
;
;          COMMAND LINE PARAMETER OPTION AVAILABLE WITH FULL IDL VERSION
;            ga - either a string array containing the Global Attributes, or a Metadata template file
;                 (as above)
;            sds - either a heap structure using pointers containing the Data (DS.Data) and the Variable
;                  Attributes (DS.VA_L and DS.VA_V) for a single file, or a string array or file spec of
;                  file(s) containing the data (as above)
;            tav - the current Table Attribute Values (TAV) file
;            outdir - the directory to which any HDF and log files will be written
;            reterr - optional string input that, if included, returns an error message to the calling
;                     program rather than stop the program. Note that the Pop-up option will be
;                     deselected if present together with this argument.
;
;          OPTIONS
;            H5 - output will be as an HDF5 file instead of the standard HDF4
;            NC - output will be as a netCDF file instead of the standard HDF4
;            AVK - to add a sentence to VAR_NOTES indicating array order for Averaging Kernel
;                  datasets
;            Log - to append input/output information as well as warnings and errors to a log file
;                  named idlcr8hdf.log, or idlcr8qa.log if QA option chosen
;            Popup - to append input/output information as well as warnings and errors to a pop-up
;                    display window
;            QA - to perform QA function on an HDF file passed to the program using the session
;                 memory option. The logfile is automatically generated and will be called
;                 idlcr8qa.log instead of idlcr8hdf.log
;            NoHDF - an HDF file will not be created, but the logfile idlcr8hdf.log will automatically
;                    be generated
;
;  Output: An HDF file formatted to GEOMS standards. Keyword options can also result
;          in an output log file (idlcr8hdf.log), or a pop-up box showing log output. If the
;          reterr string input parameter is included then reterr will return an error message to the
;          calling program, if encountered.
;
;  Called by: Main Routine
;
;  Subroutines Called: INTRO (if program called without command line parameters)
;                      READ_TABLEFILE
;                      READ_METADATA
;                      CHECK_METADATA
;                      SET_UP_STRUCTURE
;                      READ_DATA
;                      FIND_HDF_FILENAME
;                      AVDC_HDF_WRITE
;                      STOP_WITH_ERROR (if error state detected)
;                      INFOTXT_OUTPUT (if information conditions detected)
;    Possible Conditions for STOP_WITH_ERROR call:
;      1. If Metadata, Data, or Table Attribute Values file(s), or Output Directory
;         selection is not valid
;      2. If input is via session memory and the array holding the global attributes
;         is not of type string, or is not one dimensional
;      3. If input is via session memory and the input heap structure is not valid
;      4. If input is via session memory and the array sizes of the heap structures
;         do not match
;      5. If the H5 option is chosen and the IDL version does not support HDF5 write
;         routines (less than v6.2)
;      6. If the NC option is chosen and IDL was called in IDL DEMO mode
;
;    Information Conditions (when the program is able to make changes):
;      1. /POPUP keyword cannot be used together with the 'reterr' argument
;      2. Argument 'reterr' must be a scalar variable of type string
;      3. /LOG keyword cannot be used in IDL DEMO mode

COMMON TABLEDATA
COMMON METADATA
COMMON DATA
COMMON WIDGET_WIN

;Possible error message for this procedure
proname='IDLcr8HDF procedure: ' & lu=-1L
errtxt=STRARR(6)
errtxt[0]=' selection not valid'
errtxt[1]='Global Attributes Array is not of type string, or is not one dimensional'
errtxt[2]='structure is not valid ('
errtxt[3]='Array sizes of the heap structure do not match: '
errtxt[4]=' does not support HDF5 Write Routines'
errtxt[5]='IDLcr8HDF requires session memory input to perform the QA function'

demomode=LMGR(/DEMO) ;Boolean to check for IDL being run in demo mode (disable /LOG option)
IF N_PARAMS() GE 2 THEN intype=SIZE(sds,/TYPE) $ ;Is SDS a structure (8) or a string (7)?
ELSE IF demomode THEN intype=-3 $
ELSE intype=-1
IF (intype NE 7) AND (intype NE 8) AND (intype NE -1) AND (intype NE -3) THEN intype=-2
;Command line parameter neither string nor structure
dux=[-1,-1,1] ;initialize flags for output log to IDLDE Output Window and/or to file
;dux[0] default allows output to the IDLDE output window (ignored by IDL VM)
;dux[1] is the program assigned file unit for sending log output to file
;dux[2] is the step between dux[0] and dux[1]
lineno=0L ;count variable to put curser at end of text pop-up window
rerr=['NA','NA'] ;initialize return error string

IF intype LT 0 THEN BEGIN ;either no input parameters or invalid second parameter
  o3=['0','0','0','0','0','0']
  INTRO,intype ;Open Intro Box and determine HDF output format (HDF4 or HDF5)
  IF o3[0] EQ '0' THEN BEGIN
    STOP_WITH_ERROR,'','',lu & RETURN
  ENDIF
  IF o3[3] EQ 'Pop' THEN o3[3]='' ELSE o3[3]='D_'
ENDIF ELSE BEGIN ;Set options (HDF4, HDF5, netCDF, AVK, LOGFILE, POP-UP, QA, NOHDF)
  IF KEYWORD_SET(o1) THEN o3=['H5','0','0','D_','0','0'] $
  ELSE IF KEYWORD_SET(o8) THEN o3=['NC','0','0','D_','0','0'] $
  ELSE o3=['H4','0','0','D_','0','0']
  IF KEYWORD_SET(o2) THEN o3[1]='AVK'           ;AVK option
  IF KEYWORD_SET(o4) THEN o3[2]='idlcr8hdf.log' ;Log option
  IF KEYWORD_SET(o5) THEN o3[3]=''              ;POP-UP option
  IF KEYWORD_SET(o6) THEN o3[2]='idlcr8qa.log'  ;QA option
  IF KEYWORD_SET(o7) THEN o3[4]='NOHDF'         ;NoHDF option
  IF KEYWORD_SET(o9) THEN o3[5]='DTFVOK'        ;DATETIME Fill Value OK
ENDELSE
IF o3[0] EQ 'NC' THEN dftxt='netCDF' ELSE dftxt='HDF'

;If reterr included allows error output to return to a calling program
infotxt=STRARR(2,4)
IF N_PARAMS() GE 5 THEN BEGIN
  ;IF (ARG_PRESENT(reterr)) AND (SIZE(reterr,/Type) EQ 7) THEN BEGIN
  IF SIZE(reterr,/Type) EQ 7 THEN BEGIN
    rerr=['','']
    IF o3[3] EQ '' THEN BEGIN
      ;Deselect POPUP option and write INFORMATION message
      o3[3]='D_'
      infotxt[0,0]='0 /POPUP keyword cannot be used together with the ''reterr'' argument.'
      infotxt[1,0]='    The request for a POPUP window has been ignored.'
    ENDIF
  ENDIF ELSE BEGIN
    ;reterr input included but is of the incorrect type, or parameter cannot be returned
    ;to the calling program
    infotxt[0,1]='0 Argument ''reterr'' must be of type string.' ;a returnable variable of type string.'
    infotxt[1,1]='    idlcr8hdf will stop normally if an error is encountered.'
  ENDELSE
ENDIF

;Do check for /LOG and /NC keywords in IDL DEMO Mode and if necessary disable or stop the program
IF demomode THEN BEGIN
  IF o3[2] EQ 'idlcr8hdf.log' THEN BEGIN
    o3[2]='0'
    infotxt[0,2]='0 /LOG keyword cannot be used in IDL DEMO mode and has been ignored.'
  ENDIF
  IF o3[0] EQ 'NC' THEN BEGIN
    o3[4]='NOHDF'
    infotxt[0,3]='3 NetCDF file create feature is disabled in IDL DEMO mode. '
    infotxt[1,3]='    To generate files please use the free IDL Virtual Machine or a licenced version of IDL.' 
  ENDIF
ENDIF

IF (KEYWORD_SET(o1)) AND (FLOAT(!Version.Release) LT 6.2) THEN BEGIN ;No HDF5 library for IDL6.1 or less
  STOP_WITH_ERROR,'D_'+proname,'IDL Version '+!Version.Release+errtxt[4],lu
  IF STRLEN(rerr[0]) GT 2 THEN reterr=rerr[0] & RETURN
ENDIF

;Check TAV file and Output Directory inputs
tablefile='' & outdir=''
CD,CURRENT=path ;identify current working directory
IF N_PARAMS() GE 3 THEN BEGIN ;check TAV file
  IF (SIZE(tav,/N_ELEMENTS) EQ 1) AND (SIZE(tav,/TYPE) EQ 7) THEN BEGIN
    file_exist=FILE_TEST(tav,/READ)
    IF (file_exist EQ 1) AND (tav NE '') THEN tablefile=tav
  ENDIF
ENDIF
IF N_PARAMS() GE 4 THEN BEGIN ;check output directory
  IF (SIZE(odir,/N_ELEMENTS) EQ 1) AND (SIZE(odir,/TYPE) EQ 7) THEN BEGIN
    file_exist=FILE_TEST(odir,/DIRECTORY)
    IF (file_exist EQ 1) AND (odir NE '') THEN BEGIN
      outdir=FILE_SEARCH(odir,/FULLY_QUALIFY_PATH,/MARK_DIRECTORY)
      path=outdir
    ENDIF ELSE IF intype NE 8 THEN outdir=STRUPCASE(STRTRIM(odir,2))
  ENDIF
ENDIF

IF (intype LT 0) OR (intype EQ 7) THEN BEGIN ;Input via files
  IF KEYWORD_SET(o6) THEN BEGIN
    ;session memory inputs required for QA option
    STOP_WITH_ERROR,'D_'+proname,errtxt[5],lu
    IF STRLEN(rerr[0]) GT 2 THEN reterr=rerr[0] & RETURN
  ENDIF
  metafile='' & inf=1
  IF N_PARAMS() GE 2 THEN BEGIN
    ;Check that input files exist. If not then user will be prompted for new inputs
    IF SIZE(ga,/N_ELEMENTS) EQ 1 THEN BEGIN
      file_exist=FILE_TEST(ga,/READ)
      IF (file_exist EQ 1) AND (ga NE '') THEN $
        metafile=FILE_DIRNAME(ga,/MARK_DIRECTORY)+FILE_BASENAME(ga)
    ENDIF
    arorfs=SIZE(sds,/DIMENSIONS) ;Is datafile input Filespec or String Array?
    IF arorfs[0] EQ 0 THEN BEGIN ;input is filespec (scalar)
      IF sds NE '' THEN sds=FINDFILE(sds)
      isize=SIZE(sds,/DIMENSIONS)
      IF isize[0] EQ 0 THEN sds=[''] ;no files found matching filespec
    ENDIF
    IF N_ELEMENTS(arorfs) GT 1 THEN sds=REFORM(sds,N_ELEMENTS(sds),/OVERWRITE) ;Convert to 1-D array
    file_exist=FILE_TEST(sds,/READ)
    gi=WHERE(file_exist EQ 1,nfile)
    IF nfile NE 0 THEN BEGIN
      sds=sds[gi] & sds=FILE_DIRNAME(sds,/MARK_DIRECTORY)+FILE_BASENAME(sds)
    ENDIF ELSE sds=[''] ;contains all valid datafiles
  ENDIF ELSE sds=['']
  IF metafile EQ '' THEN BEGIN
    metafile=DIALOG_PICKFILE(Filter=['*.meta','meta*.txt','*.txt'], PATH=path, $
             /MUST_EXIST,Title='Select Metadata Template File')
    IF metafile EQ '' THEN BEGIN
      STOP_WITH_ERROR,'D_'+proname,'Metadata file'+errtxt[0],lu
      IF STRLEN(rerr[0]) GT 2 THEN reterr=rerr[0] & RETURN
    ENDIF
    path=FILE_DIRNAME(metafile,/MARK_DIRECTORY)
  END
  IF sds[0] EQ '' THEN BEGIN
    datafile=DIALOG_PICKFILE(Filter=['*.data','*.dat','*.txt'], PATH=path, $
             /MUST_EXIST,/Multiple_Files,Title='Select Data File(s)')
    gi=WHERE(datafile NE '',nfile)
    IF nfile EQ 0 THEN BEGIN
      STOP_WITH_ERROR,'D_'+proname,'Data file(s)'+errtxt[0],lu
      IF STRLEN(rerr[0]) GT 2 THEN reterr=rerr[0] & RETURN
    ENDIF ELSE BEGIN
      datafile=datafile[gi] & dsort=SORT(datafile) & sds=datafile[dsort]
      path=FILE_DIRNAME(sds[0],/MARK_DIRECTORY)
    ENDELSE
  ENDIF
  IF outdir EQ 'M' THEN outdir=FILE_DIRNAME(metafile,/MARK_DIRECTORY) $
  ELSE IF outdir EQ 'D' THEN outdir=FILE_DIRNAME(sds[0],/MARK_DIRECTORY)
ENDIF ELSE BEGIN ;SDS is a data structure, so do initial checks on parameters
  ;check GA array
  inf=0 & nfile=1
  as=SIZE(ga) & n_ga=N_ELEMENTS(ga)
  IF (as[0] NE 1) OR (as[2] NE 7) THEN BEGIN
    STOP_WITH_ERROR,'D_'+proname,errtxt[1],lu
    IF STRLEN(rerr[0]) GT 2 THEN reterr=rerr[0] & RETURN
  ENDIF
  ;check pointer array (heap structure)
  IF N_TAGS(sds) EQ 0 THEN BEGIN
    STOP_WITH_ERROR,'D_'+proname,'Input heap '+errtxt[2]+'expecting VA_L, VA_V, and DATA tags).',lu
    IF STRLEN(rerr[0]) GT 2 THEN reterr=rerr[0] & RETURN
  ENDIF
  tagnames=STRUPCASE(TAG_NAMES(sds))
  si=WHERE((tagnames EQ 'VA_L') OR (tagnames EQ 'VA_V') OR (tagnames EQ 'DATA'),scnt)
  IF scnt NE 3 THEN BEGIN
    STOP_WITH_ERROR,'D_'+proname,'Input heap '+errtxt[2]+'missing VA_L, VA_V, and/or DATA tags).',lu
    IF STRLEN(rerr[0]) GT 2 THEN reterr=rerr[0] & RETURN
  ENDIF
  ;Check for number and size of dimensions, and invalid pointer arguments for the data
  FOR i=0,2 DO BEGIN
    CASE 1 OF
      i EQ 0: BEGIN
                pchk=PTR_VALID(sds.data) & sdstxt='SDS.DATA '
              END
      i EQ 1: BEGIN
                pchk=PTR_VALID(sds.va_v) & sdstxt='SDS.VA_V '
                pchkv=pchk
              END
      ELSE: BEGIN
              pchk=PTR_VALID(sds.va_l) & sdstxt='SDS.VA_L '
            END
    ENDCASE
    ;Check that the SDS structure has two dimensions
    s_ndim=SIZE(pchk,/N_DIMENSIONS) & s_dim=SIZE(pchk,/DIMENSIONS)
    IF s_ndim NE 2 THEN BEGIN
      STOP_WITH_ERROR,'D_'+proname,sdstxt+errtxt[2]+'two dimensions expected).',lu
      IF STRLEN(rerr[0]) GT 2 THEN reterr=rerr[0] & RETURN
    ENDIF ELSE IF i EQ 0 THEN BEGIN
      pi=WHERE(pchk[*,0] NE 1,pcnt)
      IF pcnt NE 0 THEN BEGIN
        STOP_WITH_ERROR,'D_'+proname,sdstxt+errtxt[2]+'null pointer arguments).',lu
        IF STRLEN(rerr[0]) GT 2 THEN reterr=rerr[0] & RETURN
      ENDIF
    ENDIF ELSE BEGIN
      IF i EQ 2 THEN test=s_dim[1] NE s_dim0[1] ELSE test=0
      IF (s_dim[0] NE s_dim0[0]) OR (test) THEN BEGIN
        dimv='['+STRTRIM(s_dim0[0],2)+','+STRTRIM(sdim0[1],2)+']/['+ $
                 STRTRIM(s_dim[0],2)+','+STRTRIM(sdim[1],2)+'].'
        STOP_WITH_ERROR,'D_'+proname,errtxt[3]+dimv,lu
        IF STRLEN(rerr[0]) GT 2 THEN reterr=rerr[0] & RETURN
      ENDIF
    ENDELSE
    s_dim0=s_dim
  ENDFOR

  ;create Metafile by combining global and variable attributes, also make
  ;accompanying arrays to hold any numeric metadata values
  vi=WHERE(pchk EQ 1,vatot) ;total number of Variable Attribute labels
  metafile=STRARR(n_ga+vatot) & mv_lng=LON64ARR(n_ga+vatot) & mv_dbl=DBLARR(n_ga+vatot)
  pcnt=LONG(n_ga)
  metafile[0:pcnt-1L]=ga
  FOR i=0,s_dim[0]-1 DO BEGIN ;s_dim[0] is the number of datasets
    FOR j=0,s_dim[1]-1 DO BEGIN ;s_dim[1] is the number of attributes
      IF pchk[i,j] EQ 1 THEN BEGIN
        IF pchkv[i,j] EQ 0 THEN metafile[pcnt]=*sds[i,j].va_l+'=' $
        ELSE BEGIN
          vav=*sds[i,j].va_v
          vavt=SIZE(vav,/TYPE)
          IF vavt EQ 1 THEN metafile[pcnt]=*sds[i,j].va_l+'='+STRTRIM(FIX(vav),2) $
          ELSE metafile[pcnt]=*sds[i,j].va_l+'='+STRTRIM(vav,2) ;save all values as a string representation
          IF vavt NE 7 THEN BEGIN ;i.e. if the metadata value is not of STRING datatype
            n_vav=N_ELEMENTS(vav)
            IF n_vav EQ 1 THEN BEGIN ;save numeric values to the appropriate numeric array (LONG64 or DOUBLE)
              CASE 1 OF
                ((vavt GE 1) AND (vavt LE 3)) OR ((vavt GE 12) AND (vavt LE 14)): mv_lng[pcnt]=vav
                (vavt GE 4) AND (vavt LE 5): mv_dbl[pcnt]=vav
                ELSE:
              ENDCASE
            ENDIF ELSE BEGIN ;need to save it in string form (could be the case for VAR_SIZE values)
              FOR k=0,N_ELEMENTS(vav)-1 DO BEGIN
                IF k EQ 0 THEN metafile[pcnt]=*sds[i,j].va_l+'='+STRTRIM(vav[k],2) $
                ELSE metafile[pcnt]=metafile[pcnt]+';'+STRTRIM(vav[k],2)
              ENDFOR
            ENDELSE
          ENDIF
        ENDELSE
        pcnt=pcnt+1L
      ENDIF
    ENDFOR
  ENDFOR
ENDELSE

;If necessary open DIALOG_BOXES for the TAV File and Output Directory Inputs
IF tablefile EQ '' THEN BEGIN
  tablefile=DIALOG_PICKFILE(Filter=['table*.dat','*.dat'], PATH=path, $
            /MUST_EXIST,Title='Select Table Attribute Values File')
  IF tablefile EQ '' THEN BEGIN
    STOP_WITH_ERROR,'D_'+proname,'Table Attribute Values file'+errtxt[0],lu
    IF STRLEN(rerr[0]) GT 2 THEN reterr=rerr[0] & RETURN
  ENDIF
  path=FILE_DIRNAME(tablefile,/MARK_DIRECTORY)
ENDIF
IF outdir EQ '' THEN BEGIN
  outdir=DIALOG_PICKFILE(/DIRECTORY,Title='Select Directory for Output '+dftxt+' file(s)', PATH=path)
  IF outdir EQ '' THEN BEGIN
    STOP_WITH_ERROR,'D_'+proname,dftxt+' file(s) output directory'+errtxt[0],lu
    IF STRLEN(rerr[0]) GT 2 THEN reterr=rerr[0] & RETURN
  ENDIF
ENDIF

;Set dux values according to output options
IF o3[2] NE '0' THEN BEGIN ;open idlcr8hdf/idlcr8qa.log
  o3[2]=outdir+o3[2]
  res=FILE_TEST(o3[2],/WRITE)
  IF res EQ 0 THEN OPENW,du,o3[2],/GET_LUN $
  ELSE BEGIN
    OPENW,du,o3[2],/Append,/GET_LUN & FOR i=0,1 DO PRINTF,du,''
  ENDELSE
  dux[1]=du & dux[2]=dux[1]-dux[0]
ENDIF
FOR i=dux[0],dux[1],dux[2] DO BEGIN
  IF i EQ -1 THEN BEGIN
    PRINT,dftxt+' File Input/Output Log - Program Started on '+SYSTIME(0) & PRINT,''
  ENDIF ELSE IF (i EQ dux[0]) OR ((i EQ dux[1]) AND (STRPOS(o3[2],'idlcr8hdf.log') NE -1)) THEN BEGIN
    PRINTF,i,dftxt+' File Input/Output Log - Program Started on '+SYSTIME(0)
    PRINTF,i,''
  ENDIF
ENDFOR

IF o3[3] EQ '' THEN BEGIN
  ;Set-up output file display widget and log file
  base=WIDGET_BASE(Title=dftxt+' File Input/Output Log',Units=2,yoffset=3,xoffset=3,Tlb_Frame_Attr=1,/COLUMN) ;,Tab_Mode=1)
  wtxt=WIDGET_TEXT(base,/Scroll,xsize=100,ysize=12)
  base2=WIDGET_BASE(base)
  b1=WIDGET_BUTTON(base2,value='Finish',uvalue='DONE',frame=3,Sensitive=0) ;Accelerator='Return')
  WIDGET_CONTROL,wtxt,/REALIZE
  WIDGET_CONTROL,base,/REALIZE
  WIDGET_CONTROL,wtxt,set_value='',/APPEND
  WIDGET_CONTROL,wtxt,set_value='Input TAV File: '+tablefile,/APPEND
ENDIF

;Call the procedure to read the TAV file (returns tab_arr)
FOR i=dux[0],dux[1],dux[2] DO $
  IF i EQ -1 THEN PRINT,'Input TAV File: '+tablefile ELSE PRINTF,i,'Input TAV File: '+tablefile
READ_TABLEFILE,Tablefile
IF STRLEN(rerr[0]) GT 2 THEN BEGIN
  reterr=rerr[0] & RETURN
ENDIF

;Check (and write out) any earlier infotxt statements
FOR i=0,3 DO BEGIN
  IF infotxt[0,i] NE '' THEN BEGIN
    IF i EQ 2 THEN INFOTXT_OUTPUT,infotxt[0,i] ELSE INFOTXT_OUTPUT,infotxt[*,i]
  ENDIF
ENDFOR

FOR ndf=0,nfile-1 DO BEGIN
  IF o3[3] EQ '' THEN BEGIN
    lineno=lineno+3L
    WIDGET_CONTROL,wtxt,set_value='',/Append
  ENDIF
  FOR i=dux[0],dux[1],dux[2] DO IF i EQ -1 THEN PRINT,'' ELSE PRINTF,i,''
  IF inf EQ 1 THEN BEGIN
    IF o3[3] EQ '' THEN BEGIN
      lineno=lineno+2L
      WIDGET_CONTROL,wtxt,set_value='Input Metadata File: '+metafile,/Append
      WIDGET_CONTROL,wtxt,set_value='Input Data File: '+sds[ndf],/Append
    ENDIF
    FOR i=dux[0],dux[1],dux[2] DO BEGIN
      IF i EQ -1 THEN BEGIN
        PRINT,'Input Metadata File: '+metafile & PRINT,'Input Data File: '+sds[ndf]      
      ENDIF ELSE BEGIN
        PRINTF,i,'Input Metadata File: '+metafile
        PRINTF,i,'Input Data File: '+sds[ndf]
      ENDELSE
    ENDFOR
  ENDIF ELSE BEGIN
    IF o3[3] EQ '' THEN $
      WIDGET_CONTROL,wtxt,set_value='Reading input Global Attribute array and Data Structure',/Append
    FOR i=dux[0],dux[1],dux[2] DO BEGIN
      IF i EQ -1 THEN PRINT,'Reading input Global Attribute array and Data Structure' $
      ELSE IF (i EQ dux[0]) OR ((i EQ dux[1]) AND (STRPOS(o3[2],'idlcr8hdf.log') NE -1)) THEN $
        PRINTF,i,'Reading input Global Attribute array and Data Structure'
    ENDFOR

    ;Do stage 1 of HDF Pre-Defined attributes check (checking units,valid_range,_FillValue only)
    ncsa=['x','x','units','_fillvalue','valid_range','valid_range']
    var_atts=['VAR_NAME','VAR_DATA_TYPE','VAR_UNITS','VAR_FILL_VALUE','VAR_VALID_MIN','VAR_VALID_MAX']
    FOR i=0,s_dim[0]-1 DO BEGIN ;s_dim[0] is the number of datasets
      vdtv='' & vnx='' & verror=0
      FOR k=0,N_ELEMENTS(var_atts)-1 DO BEGIN
        vav='' & nav=''
        FOR j=0,s_dim[1]-1 DO BEGIN ;s_dim[1] is the number of attributes
          IF (pchk[i,j] EQ 1) AND (pchkv[i,j] EQ 1) THEN BEGIN
            CASE 1 OF
              STRUPCASE(STRTRIM(*sds[i,j].va_l,2)) EQ var_atts[k]: vav=*sds[i,j].va_v
              STRLOWCASE(STRTRIM(*sds[i,j].va_l,2)) EQ ncsa[k]: nav=*sds[i,j].va_v
              ELSE:
            ENDCASE
          ENDIF
        ENDFOR
        IF k EQ 0 THEN vnx=STRTRIM(vav[0],2) $ ;VAR_NAME
        ELSE IF k EQ 1 THEN vdtv=STRUPCASE(STRTRIM(vav[0],2)) $ ;VAR_DATA_TYPE
        ELSE IF k GE 4 THEN BEGIN ;separate out min and max valid_range values
          IF ((SIZE(nav[0],/TYPE) EQ 7) AND (STRTRIM(nav[0],2) NE '')) OR (SIZE(nav[0],/TYPE) NE 7) THEN BEGIN
            IF k EQ 4 THEN nav=nav[0] $
            ELSE IF N_ELEMENTS(nav) GT 1 THEN nav=nav[1]
          ENDIF
        ENDIF ELSE BEGIN
          vav=vav[0] & nav=nav[0]
        ENDELSE
        IF k GE 2 THEN PRE_DEFINED_ATT_CHECKS,k-2,nav,vav,vnx,vdtv,verror
      ENDFOR
    ENDFOR
  ENDELSE

  ;Call the procedure to read the metadata (returns meta_arr)
  READ_METADATA,metafile,inf
  IF STRLEN(rerr[0]) GT 2 THEN BEGIN
    reterr=rerr[0] & RETURN
  ENDIF
  ;Call Procedure to check inputs in meta_arr with those from the TAV file
  CHECK_METADATA
  IF STRLEN(rerr[0]) GT 2 THEN BEGIN
    reterr=rerr[0] & RETURN
  ENDIF
  ;Call the procedure to set up the data structure and assign arrays for VAR_NAME and VAR_UNITS
  IF inf EQ 0 THEN SET_UP_STRUCTURE,sds,inf ELSE SET_UP_STRUCTURE,sds[ndf],inf
  IF STRLEN(rerr[0]) GT 2 THEN BEGIN
    reterr=rerr[0] & RETURN
  ENDIF  ;Call the procedure to read the data
  IF inf EQ 0 THEN READ_DATA,sds,inf ELSE READ_DATA,sds[ndf],inf
  IF STRLEN(rerr[0]) GT 2 THEN BEGIN
    reterr=rerr[0] & RETURN
  ENDIF
  ;Call the Procedure to construct the HDF output filename based on input metadata.
  IF o3[0] EQ 'H5' THEN hdffilename='.h5' $
  ELSE IF o3[0] EQ 'NC' THEN hdffilename='.nc' $
  ELSE hdffilename='.hdf'
  FIND_HDF_FILENAME,hdffilename
  IF STRLEN(rerr[0]) GT 2 THEN BEGIN
    reterr=rerr[0] & RETURN
  ENDIF

  ;Create HDF file if the program is not performing QA and NOHDF keyword not selected
  IF (STRPOS(o3[2],'idlcr8qa.log') EQ -1) AND (o3[4] EQ '0') THEN BEGIN
    ;Check to see if file exists - if so delete (o/w will append to existing file)
    IF FILE_TEST(hdffilename) EQ 1 THEN FILE_DELETE,hdffilename

    ;Call the procedure to write the Global Attributes, Variable Attributes and Data
    ;to an HDF4 or HDF5 file
    AVDC_HDF_WRITE,hdffilename
    FILE_MOVE, hdffilename, outdir+hdffilename,/Allow_Same,/Overwrite
    hdffilename=outdir+hdffilename

    IF o3[3] EQ '' THEN $
      WIDGET_CONTROL,wtxt,set_value=hdffilename+' successfully created!',/Append,Set_text_top_line=lineno
    FOR i=dux[0],dux[1],dux[2] DO BEGIN
      IF i EQ -1 THEN PRINT,hdffilename+' successfully created!' $
      ELSE PRINTF,i,hdffilename+' successfully created!'
    ENDFOR
  ENDIF
  ;Free up memory by destroying the heap variables pointed at by its pointer arguments
  PTR_FREE,ds.data
ENDFOR

IF STRPOS(o3[2],'idlcr8qa.log') NE -1 THEN endtxt=dftxt+' QA function ' $
ELSE IF o3[4] EQ '0' THEN endtxt=dftxt+' file creation ' $
ELSE endtxt='GEOMS file testing '

FOR i=dux[0],dux[1],dux[2] DO BEGIN
  IF i EQ -1 THEN BEGIN
    PRINT,'' & PRINT,endtxt+'completed - Program Ended on '+SYSTIME(0)
  ENDIF ELSE IF (i EQ dux[0]) OR ((i EQ dux[1]) AND (STRPOS(o3[2],'idlcr8hdf.log') NE -1)) THEN BEGIN
    PRINTF,i,'' & PRINTF,i,endtxt+'completed - Program Ended on '+SYSTIME(0)
  ENDIF
ENDFOR
IF dux[1] NE dux[0] THEN FREE_LUN,dux[1]

ri=WHERE(rerr EQ '',rcnt)
IF (rcnt EQ N_ELEMENTS(rerr)) AND (STRPOS(o3[2],'idlcr8qa.log') EQ -1) AND (o3[4] EQ '0') THEN BEGIN
  IF nfile EQ 1 THEN reterr=hdffilename+' successfully created' $
  ELSE reterr=dftxt+' files successfully created'
ENDIF ELSE IF (rerr[1] NE 'NA') AND (rerr[1] NE '') THEN reterr=rerr[1]

IF o3[3] EQ '' THEN BEGIN
  WIDGET_CONTROL,b1,Sensitive=1,/Input_Focus
  WIDGET_CONTROL,wtxt,set_value='',/Append,Set_text_top_line=lineno+2L
  WIDGET_CONTROL,wtxt,set_value=endtxt+'completed - hit <Finish> to close program',/Append
  XMANAGER,'idlcr8hdf',base
ENDIF ELSE IF intype LT 0 THEN BEGIN ;Create Finish Dialog Box
  res=DIALOG_MESSAGE(endtxt+'completed successfully!',/Information,Title='AVDC IDLcr8HDF')
ENDIF

END ;Procedure IDLcr8HDF
