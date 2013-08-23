;Main Program Version: idlcr8ascii.pro v4.0, 20101122
;  Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;  
;Note: This program still requires checks on some of the predefined HDF4 attributes (e.g check for caldata
;      structure in HDF_SD_GETINFO call - save to session memory in appropriate format).
;      
;Sub-versions:
;  v3.01, 20081020 - If the HDF4 file is created using the HDF4.2r3 library, then extra information
;                    regarding the dimensions of the VAR_DEPEND values may be included in the file
;                    (which show up as extra datasets in the HDF_SD_FILEINFO call). A check for
;                    this is carried out and, if found, the information is excluded from the output.
;  v3.02, 20090311 - Improve HDF4.2r3 library checks by comparing the number of datasets recorded
;                    under DATA_VARIABLES, with the number returned by the HDF_SD_FILEINFO call;
;                    Change 'WARNING' to 'INFORMATION; Add procedure to handle 'INFORMATION' text
;                    output; Add 'INFORMATION' text if anything irregular found with the datasets;
;                    Change 'Data dimensions exceed 8' and 'Data type not allowable' ERROR messages
;                    to 'INFORMATION' messages. Make log file output to the same directory as the
;                    first HDF file to be read.
;  v3.03, 20091208 - Incorporate HDF_SD_ISCOORDVAR to differentiate between datasets and dimension
;                    variable names. Add check for allowable VAR_DATA_TYPE=STRING. Add all
;                    INFORMATION text messages to INFOTXT_OUTPUT_A procedure to avoid duplication
;                    of code that creates the messages; Add INFORMATION messages when reading HDF5
;                    files; Rename AVDC Button to FORMAT and replace keyword option /AVDC with 
;                    /FORMAT. Improve checks on parameter and keyword inputs; Improve checks for 
;                    non-standard (i.e. non-groundbased) HDF files.
;  v4.0, 20101122  - Adopt GEOMS metadata standard; Because FORMAT attribute(s) have been dropped 
;                    can no longer use defined formatting values when outputing data to files;
;                    Default ASCII formatting adopted - scientific notation for REAL and DOUBLE, 
;                    except for DATETIME and related values, which have formatting dependent on 
;                    the data type; Numeric metadata values remain in their original data type
;                    when writing to session memory, meaning: variable attribute labels and values 
;                    now written to separate structure variables sds.va_l and sds.va_v (previously 
;                    sds.va), and structure has 2 dimensions (n_sds, n_atts) instead of 1 
;                    (previously n_sds); The dataset is written to the initial n_atts index (i.e.
;                    sds[n_sds,0].data); Rename saved SDS datatype according to GEOMS rules 
;                    (affects INT, LONG, and FLOAT); Add JDF_2_DATETIME and JULIAN_DATE routines
;                    to the program; Include coordinate variables if they and the non-coordinate
;                    variables add up to the number of saved DATA_VARIABLES. Add return error code
;                    option so that program returns to the calling program if an error is
;                    generated.                    

PRO idlcr8ascii_common
;Procedure to define the data COMMON block WIDGET_WIN_A, containing common variables
;associated with the Graphical User Interface
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20061004: Introduced to IDLCR8ASCII - Version 2.0
;    20080302: 'cwidg' variable removed, and 'dux' array added to identify requested
;              output options - Version 3.0
;    2010xxxx: Add rerr - Version 4.0          
;
;
;  Input: Nil
;
;  Output: Nil
;
;  Called by: N/A
;
;  Subroutines Called: None

COMMON WIDGET_WIN_A,wtxt,lineno,base,o3,b3,dux,rerr

END ; Procedure idlcr8ascii_common



PRO intro_a_event, ev
;Procedure to define how Events from the Start-up Introduction Window are handled
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20061004: Introduced to IDLCR8ASCII - Version 2.0
;    20080302: Code added to define the Pop-up Window and Log Output events added to
;              the Introduction Window - Version 3.0
;
;  Input: ev - Selected widget event structure
;
;  Output: o3 - Common string array defining the various options for program output
;
;  Called by: XMANAGER in INTRO_A
;
;  Subroutines Called: None

COMMON WIDGET_WIN_A

;The uservalue is retrieved from a widget when an event occurs
WIDGET_CONTROL,ev.id,GET_UVALUE=uv
IF (uv EQ 'C') OR (uv EQ 'P') OR (uv EQ 'idlcr8ascii.log') THEN BEGIN
  CASE 1 OF
    uv EQ 'C': uvi=1
    uv EQ 'P': uvi=3
    ELSE: uvi=4
  ENDCASE
  IF o3[uvi] EQ uv THEN o3[uvi]='0' ELSE o3[uvi]=uv
  IF uv EQ 'C' THEN BEGIN
    IF o3[1] EQ '0' THEN WIDGET_CONTROL,ev.id+6,Sensitive=0 $
    ELSE IF o3[1] EQ 'C' THEN BEGIN
      WIDGET_CONTROL,ev.id+6,Sensitive=1
      WIDGET_CONTROL,ev.id+1,/Set_Button
      o3[3]='P'
    ENDIF
  ENDIF
ENDIF ELSE IF (uv EQ 'F') OR (uv EQ 'D') THEN o3[0]=uv $ ;Assign button event to a variable name
ELSE IF uv EQ 'Cont' THEN o3[0]='0' ;changes o3[0] from -1 to 0
IF (uv NE 'C') AND (uv NE 'P') AND (uv NE 'idlcr8ascii.log') THEN WIDGET_CONTROL,ev.top,/DESTROY

END ;Intro_Event handler



PRO intro_a, intype
;Procedure which creates an Introduction Window at start-up when IDLCR8ASCII is called without parameters,
;or invalid parameters, or is called by IDL Virtual Machine. The user has a choice of continuing with
;the program after selecting input options, or stopping the program.
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20061004: Introduced to IDLCR8ASCII - Version 2.0
;    20080302: Swapped the order of the option windows, so that the options indicated by the check
;              boxes appear above the option boxes that close the Introduction Window and continue
;              with the program; Added options to allow the user to send input/output log information
;              to a Pop-Up Window and/or a Log File - Version 3.0
;    20091208: Change AVDC button to FORMAT and keyword option from /AVDC to /FORMAT - Version 3.03
;    20101122: Add vertxt array. Modify Introduction text to indicate that program accepts 'GEOMS
;              Compliant' files, and also to show the new structure format.
;
;  Input: intype - Integer set to -2 or -3: -2 indicates normal state; -3 indicates that input
;                  parameters or keywords at the IDLCR8ASCII call are invalid.
;
;  Output: Nil
;
;  Called by: IDLCR8ASCII
;
;  Subroutines Called: INTRO_A_EVENT (via XMANAGER)

COMMON WIDGET_WIN_A

;procedure which provides an introduction message before starting the program.
nhdr=43 & errtxt=STRARR(nhdr)
vertxt=['idlcr8ascii-v4.0_Readme.pdf','v4.0 November 2010']
errtxt[1]='Welcome to IDLcr8ASCII.  This program reads GEOMS compliant HDF4 and HDF5 files and'
errtxt[2]='saves contents to either session memory, an output window (summary only) or to files'
errtxt[3]='(also refer to '+vertxt[0]+').'
errtxt[5]='Inputs to the program:'
errtxt[6]='  HDF FILE(s) - GEOMS compliant HDF4 or compatible HDF5 files.  Input can be by DIALOG_BOX'
errtxt[7]='    (IDL VM or full version of IDL), or by command line (full version of IDL only).'
errtxt[9]='Choice of output is made by selecting options in this DIALOG_BOX (IDL VM or full version'
errtxt[10]='  of IDL), or by ''Keywords'' at the command line input (full version only), as follows:'
errtxt[11]='  /F or /FORMAT - generates two output files (with .META and .DATA extensions).  The resulting'
errtxt[12]='    files can be used as inputs to GEOMS compliant HDF write programs (IDLcr8HDF etc), OR'
errtxt[13]='  /D or /DUMP - generates two output files (with .META and .DATA extensions).  Data values'
errtxt[14]='    will be shown as indicated in the array format defined by VAR_SIZE, AND/OR'
errtxt[15]='  /C or /CATALOG - sends variable index, variable name, data format, and dimension size'
errtxt[16]='    information to an output window and/or log file, AND/OR'
errtxt[17]='  /P or /POPUP - sends log input/output information to a Pop-up Dialog Box, AND/OR'
errtxt[18]='  /L or /LOG - sends log input/output information to a file named idlcr8ascii.log
errtxt[20]='Example of command line input:  idlcr8ascii,HDFSpec[,/F][,/D][,/C][,/P][,/L], where ''HDFSpec'''
errtxt[21]='  can either be a string array containing filenames or a scalar string containing a file spec or'
errtxt[22]='  single file name.'
errtxt[23]='If running the full version of IDL, and input is a single HDF file, output can also be saved'
errtxt[24]='  to session memory.  This can be done by calling idlcr8ascii with the following command line:'
errtxt[25]='  idlcr8ascii,HDFFile,GA,SDS[,/F][,/D][,/C][,/P][,/L].'
errtxt[26]='HDFFile can either be the name of an HDF file or '''' (in which case a DIALOG_BOX will open'
errtxt[27]='  and prompt for the input filename).  ''GA'' is a returned string array containing the Global'
errtxt[28]='  Attributes, and ''SDS'' is a returned structure using pointers containing the Variable'
errtxt[29]='  Attribute Labels (sds.va_l), Variable Attribute Values (sds.va_v), and the Data (sds.data).
errtxt[31]='Contacts -'
errtxt[32]='  Ian Boyd, NIWA-ERI (i.boyd@niwa.com)'
errtxt[33]='  Department of Astronomy, 619 Lederle GRC, University of Massachusetts'
errtxt[34]='  710 North Pleasant St, Amherst, MA 01002, USA'
errtxt[36]='  Christian Retscher, AVDC Project Coordinator (Christian.Retscher@nasa.gov)'
errtxt[37]='  NASA Goddard Space Flight Center, Code 613.3'
errtxt[38]='  Greenbelt, MD 20771, USA'
errtxt[40]='AVDC Website: Tools and documentation available from http://avdc.gsfc.nasa.gov/Overview/index.html'
errtxt[42]='To continue, please choose from the options below.'
errtxt='        '+errtxt

;Set-up text display widget
IF intype EQ -3 THEN xtxt=' - Command Line Input Error' ELSE xtxt=''
base=WIDGET_BASE(Title='idlcr8ascii '+vertxt[1]+xtxt,Tlb_Frame_Attr=1,/Column) ;,Tab_Mode=1)
wtxt=WIDGET_TEXT(base,xsize=88,ysize=17,/Scroll)

tip='Left Mouse Click or Tab to entry and hit <Spacebar>'
base2=WIDGET_BASE(base,/Nonexclusive)
cattxt='Catalog - Generate a summary of the contents of the HDF file and send to an output window or file'
poptext='Open a Pop-Up Window to display log input/output (default if ''Catalog'' option is chosen)'
logtext='Append log input/output to the file ''idlcr8ascii.log'' (will create the file IF it doesn''t exist)'
b1=WIDGET_BUTTON(base2,value=cattxt,uvalue='C',frame=3) ;,ToolTip=Tip)
b2=WIDGET_BUTTON(base2,value=poptext,uvalue='P',frame=3)
b3=WIDGET_BUTTON(base2,value=logtext,uvalue='idlcr8ascii.log',frame=3)

base3=WIDGET_BASE(base,/Row)
b4=WIDGET_BUTTON(base3,value='FORMAT',uvalue='F',frame=3) ;,Tooltip=Tip)
b5=WIDGET_BUTTON(base3,value='DUMP',uvalue='D',frame=3) ;,Tooltip=Tip)
b6=WIDGET_BUTTON(base3,value='Continue',uvalue='Cont',frame=3,Sensitive=0) ;,Tooltip=Tip)
b7=WIDGET_BUTTON(base3,value='Stop',uvalue='S',frame=3) ;,ToolTip=Tip)
WIDGET_CONTROL,base,/Realize
WIDGET_CONTROL,b1,/Input_Focus
FOR i=0,N_ELEMENTS(errtxt)-1 do $
  WIDGET_CONTROL,wtxt,set_value=errtxt[i],/Append
XMANAGER,'intro_a',base

END ;Intro_A



PRO idlcr8ascii_event, ev
;Procedure to close the pop-up logging window after user selects 'Finish'.
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20061004: Introduced to IDLCR8ASCII - Version 2.0
;
;  Input: Selected widget event structure
;
;  Output: Nil
;
;  Called by: XMANAGER in IDLCR8ASCII and STOP_WITH_ERROR_A
;
;  Subroutines Called: None

WIDGET_CONTROL,ev.top,/DESTROY
RETALL & HEAP_GC

END ;Proc IDLcr8ASCII_Event



PRO stop_with_error_a, txt1, txt2, lu
;Procedure called when an error in the program is detected. An error message is displayed
;and the program stopped and reset. If necessary, open files are closed. The error message
;is displayed in one or more of the following: a Pop-up dialog window; the Pop-up logging
;window; the Output Logging window in the IDLDE.
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20050729: Original IDLCR8ASCII Routine - Version 1.0
;    20061004: Set-up so that the error output is displayed in the output window dependent on the
;              method that IDLCR8ASCII is called. If txt1 is preceeded by 'D_' or is null, the
;              error output is to a Pop-up Dialog window. Otherwise output will be to a logging
;              window. Renamed from STOP_WITH_ERROR to STOP_WITH_ERROR_A to avoid a name conflict
;              with the equivalent procedure in IDLCR8HDF. Common variable definition WIDGET_WIN_A
;              added - Version 2.0
;    20080302: Added code which sends the error message to the IDLDE output window and/or an external
;              file (as determined by the dux array values) - Version 3.0
;    2010xxxx: Allow routine to return to the calling program, rather than stop the application, if
;              a 'reterr' argument is included in the call to idlcr8ascii - Version 3.09 

;
;  Inputs: txt1 - the initial text line of the error message. Generally contains the name of the routine
;                 where the error was detected.
;          txt2 - the second text line which generally describes the error state.
;          lu - Where applicable, the file unit that needs to be closed at the termination of the program,
;               otherwise set to -1.
;
;  Output: Nil
;
;  Called by: The routine in which the error was detected. The following routines call STOP_WITH_ERROR:
;             READ_HDF_SDS; IDLCR8ASCII
;
;  Subroutines Called: IDLCR8ASCII_EVENT (via XMANAGER)

COMMON WIDGET_WIN_A

IF lu NE -1L THEN FREE_LUN,lu

IF txt1 EQ '' THEN BEGIN ;<cancel> chosen on Intro box
  res=DIALOG_MESSAGE('IDLcr8ASCII Stopped!',/Information,Title='AVDC IDLcr8ASCII')
ENDIF ELSE BEGIN
  IF STRMID(txt1,0,2) EQ 'D_' THEN txtx=STRMID(txt1,2) ELSE txtx=txt1
  FOR i=dux[0],dux[1],dux[2] DO BEGIN
    PRINTF,i,'  ERROR in '+txtx & PRINTF,i,'  '+txt2
    PRINTF,i,'' & PRINTF,i,'IDLcr8ASCII stopped - Program Ended on '+SYSTIME(0)
  ENDFOR
  IF dux[1] GT -1 THEN FREE_LUN,dux[1]
  IF (STRMID(txt1,0,2) EQ 'D_') AND (rerr EQ 'NA') THEN BEGIN 
    ;write error to DIALOG Box instead of Popup window
    errtxt2=STRARR(4)
    errtxt2[0]=STRMID(txt1,2) & errtxt2[1]=txt2 & errtxt2[3]='IDLcr8ASCII Stopped!'
    res=DIALOG_MESSAGE(errtxt2,/Error,Title='AVDC IDLcr8ASCII Error')
  ENDIF ELSE IF rerr EQ 'NA' THEN BEGIN ;write error to Popup window
    lineno=lineno+4L
    WIDGET_CONTROL,wtxt,set_value='    ERROR in '+txt1,/Append
    WIDGET_CONTROL,wtxt,set_value='    '+txt2,/Append
    WIDGET_CONTROL,wtxt,set_value='',/Append,Set_text_top_line=lineno
    WIDGET_CONTROL,wtxt,set_value='HDF file read stopped - hit <Finish> to close program',/Append
    WIDGET_CONTROL,b3,Sensitive=1,/Input_Focus
    XMANAGER,'stop_with_error_a',base,Event_Handler='idlcr8ascii_event'
  ENDIF
ENDELSE
HEAP_GC
IF rerr EQ 'NA' THEN RETALL ELSE rerr='Unable to read HDF file - '+txtx+txt2

END ;Procedure Stop_With_Error_A



PRO infotxt_output_a, in0, in1
;Procedure called to report information relevant to the reading of the HDF file.
;This information can be reported to a Pop-up logging window, IDLDE output log window, and/or
;the log file. Code for this output was originally written directly in the affected procedures
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20090311: Introduced to IDLCR8ASCII - Version 3.02
;    20091208: Added all the INFORMATION text messages to the routine, to avoid duplication
;              in the HDF4 and HDF5 read sections of READ_HDF_SDS - Version 3.03
;
;  Inputs: in0 - Integer array containing input used to make correct text output
;          in1 - String array containing input used to make correct text output
;
;  Output: Nil
;
;  Called by: The routine in which the request for INFORMATION text was made.
;             The following routines call INFOTXT_OUTPUT_A: READ_HDF_SDS; IDLCR8ASCII
;
;  Subroutines Called: None

COMMON WIDGET_WIN_A

CASE 1 OF
  in0[0] EQ 0: BEGIN
                 infotxt=STRARR(3)
                 IF LONG(in1[0]) EQ 0L THEN BEGIN
                   infotxt[0]='  INFORMATION: Global Attribute DATA_VARIABLES not found or has no values.'
                   infotxt[1]='    Dataset listing order matches the order that the dataset is read in the HDF file.'
                 ENDIF ELSE BEGIN
                   infotxt[0]='  INFORMATION: Number of Global Attribute DATA_VARIABLES values ('+in1[0]+')'
                   infotxt[1]='    does not match the number of datasets saved to the HDF file ('+in1[1]+')'
                 ENDELSE
                 infotxt[2]='    Number of datasets determined from '+in1[2]+' call'
               END
  in0[0] EQ 1: infotxt='  INFORMATION: '+in1[0]+' has '+in1[1]+' data dimensions'
  in0[0] EQ 2: infotxt='  INFORMATION: '+in1[0]+' dataset is not one of the allowable Data Types - '+in1[1]
  in0[0] EQ 3: BEGIN
                 infotxt=STRARR(4)
                 IF (STRPOS(STRUPCASE(in1[1]),STRUPCASE(in1[0])) NE -1) AND (in0[1] EQ 4) AND (in0[2] EQ 0) THEN $
                   infotxt[0]='  INFORMATION: Dataset Name is truncated (File created with HDF4.2r1 library or earlier).' $
                 ELSE infotxt[0]='  INFORMATION: Dataset Name does not match VAR_NAME value.'
                 IF in0[2] EQ 0 THEN infotxt[1]='    Output uses VAR_NAME from Metadata' $
                 ELSE infotxt[1]='    Output uses Dataset Name from the HDF file.'
                 infotxt[2]='    SDS_NAME: '+in1[0]
                 infotxt[3]='    VAR_NAME: '+in1[1]
               END
  in0[0] EQ 4: BEGIN
                 infotxt=STRARR(2)
                 IF in0[1] EQ 0 THEN BEGIN
                   infotxt[0]='  INFORMATION: Metadata label VAR_NAME not found for dataset:'
                   infotxt[1]='    SDS_NAME: '+in1[0]
                 ENDIF ELSE IF (in0[2] EQ 0) AND (in0[3] NE 0L) THEN BEGIN
                   infotxt[0]='  INFORMATION: VAR_NAME value does not match any DATA_VARIABLES values:'
                   infotxt[1]='    VAR_NAME: '+in1[1]
                 ENDIF
               END
  in0[0] EQ 5: BEGIN
                 infotxt=STRARR(2)
                 infotxt[0]='  INFORMATION: No Variable Attributes returned after call to '+in1[1]
                 infotxt[1]='    SDS_NAME: '+in1[0]
               END
  in0[0] EQ 6: BEGIN
                 infotxt=STRARR(2)
                 infotxt[0]='  INFORMATION: Metadata Dataset listing order may not match the order of'
                 infotxt[1]='    the Global Attribute DATA_VARIABLES Values'
               END
  in0[0] EQ 7: BEGIN
                 infotxt=STRARR(2)
                 infotxt[0]='  INFORMATION: Can read one HDF file into session memory.'
                 infotxt[1]='    Only first file in the array will be read'
               END
  in0[0] EQ 8: BEGIN
                 infotxt='  INFORMATION: '+in1[0]+' is a coordinate variable'
               END
  in0[0] EQ 9: BEGIN
                 infotxt=STRARR(3)
                 infotxt[0]='  INFORMATION: Calibrated data in dataset '+in1[0]
                 infotxt[1]='    has been converted back to its original form using the formula:'
                 infotxt[2]='    Orig_Data = Scale_Factor * (Cal_Data - Offset)' 
               END
  in0[0] EQ 10: BEGIN
                  infotxt=STRARR(2)
                  infotxt[0]='  INFORMATION: VAR_DATA_TYPE='+in1[1]+' for Calibrated data in dataset '+in1[0]
                  infotxt[1]='    has been changed to the original datatype of '+in1[2] 
                END
ENDCASE

dm=SIZE(infotxt,/N_Elements)
IF o3[3] EQ '' THEN lineno=lineno+dm

FOR n=0,dm-1 DO BEGIN
  IF o3[3] EQ '' THEN BEGIN
    IF n EQ dm THEN WIDGET_CONTROL,wtxt,set_value='',/Append $
    ELSE WIDGET_CONTROL,wtxt,set_value=infotxt[n],/Append,Set_text_top_line=lineno
  ENDIF
  FOR m=dux[0],dux[1],dux[2] DO PRINTF,m,infotxt[n] ;write out to log(s)
ENDFOR

END ;Procedure InfoTxt_Output_A



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



PRO read_hdf_sds, ifile, ga, sds, catinfo
;Procedure to read the contents of a GEOMS standard HDF4 or HDF5 compatible file
;into session memory
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20050729: Original IDLCR8ASCII Routine - Version 1.0
;    20050912: Removed Common variable definition CATALOGINFO and made the variable a parameter passed
;              to the procedure; Checks that the attribute variable names read by HDF_SD_GETINFO, match
;              those recorded in DATA_VARIABLES in the Global Attributes. If not use the variable name
;              listed in DATA_VARIABLES - Version 1.1
;    20061004: Common variable definition WIDGET_WIN_A added for Error calls; Add option to read HDF5
;              files (needs IDL5.6 or newer); Add check that the HDF4 file has valid information on the
;              number of global and variable attributes; Checks added in the event that the HDF4 or
;              HDF5 file has been created by the NCSA utility programs H5toH4 or H4toH5 from an original
;              AVDC/Envisat/NDACC HDF4 or HDF5 file; Ensures variable attributes and data are listed in
;              the same order as that given under DATA_VARIABLES - Version 2.0
;    20081020 - If the HDF4 file is created using the HDF4.2r3 library, then extra information
;               regarding the dimensions of the VAR_DEPEND values may be included in the file (which
;               show up as extra datasets in the HDF_SD_FILEINFO call). A check for this is carried out
;               and, if found, the information is excluded from the output - Version 3.01
;    20090311: Improve HDF4.2r3 library checks by comparing the number of datasets recorded under
;              DATA_VARIABLES, with the number returned by the HDF_SD_FILEINFO call; Change 'WARNING' to
;              'INFORMATION and make calls to procedure INFOTXT_OUTPUT_A to avoid duplication. Add
;              'INFORMATION' text if anything irregular found with the datasets; Change 'Data dimensions
;               exceed 8' and 'Data type not allowable' ERROR messages to 'INFORMATION' messages
;               - Version 3.02
;    20091208: Incorporate HDF_SD_ISCOORDVAR to differentiate between datasets and dimension variable
;              names. Add check for allowable VAR_DATA_TYPE=STRING. Add all INFORMATION text messages to
;              INFOTXT_OUTPUT_A procedure to avoid duplication of code that creates the messages; 
;              Add INFORMATION messages when reading HDF5 files; Improve checks for non-standard (i.e. 
;              non-groundbased) HDF input file - Version 3.03
;    20101122: Numeric metadata values remain in their original data type when transferring to session 
;              memory, meaning: variable attribute labels and values now written to separate structure 
;              variables sds.va_l and sds.va_v (previously sds.va), and structure has 2 dimensions 
;              (n_sds, n_atts) instead of 1 (previously n_sds); The dataset is written to the initial 
;              n_atts index (i.e. sds[n_sds,0].data); Rename saved SDS datatype according to GEOMS rules 
;              (affects INT, LONG, and FLOAT); Compare HDF dimensions with VAR_SIZE values and transpose
;              VAR_SIZE and VAR_DEPEND values if required - Version 4.0       
;
;  Inputs: ifile - a string containing the name of the HDF file to be read in.
;          catinfo - a string array identifying the type of HDF file ('H4' or 'H5')
;
;  Outputs: ga - a string array containing the global attribute labels and values extracted from the HDF
;                file.
;           sds - a structure using pointers, of size [n_sds,n_atts], containing the variable attribute 
;                 labels and values (sds[n,m].va_l and sds[n,m].va_v) and the data (sds[n,0].data) 
;                 extracted from the HDF file.
;           catinfo - a string array of size [n_sds,4] (where n_sds is the number of datasets in the HDF
;                     file), containing information on the variable name, data type, data dimension, and
;                     number of attributes.
;
;  Called by: IDLCR8ASCII
;
;  Subroutines Called: STOP_WITH_ERROR_A (if error state detected)
;                      INFOTXT_OUTPUT_A (if program can make a change)
;    Possible Conditions for STOP_WITH_ERROR call (plus [line number] where called):
;      1. No global attributes or datasets present in the root group of an HDF5 file [946,1027]
;      2. The number of global attributes or datasets is zero or not able to be determined
;         in an HDF4 file [697,734]
;
;    Information Conditions (when the program is able to make changes):
;      1 (0). DATA_VARIABLES global attribute not found or has no values [737,950]
;      2 (0). Number of datasets given under DATA_VARIABLES is not equal to the number saved to the 
;         file [737,950]
;      3 (1). The number of dimensions in a dataset exceeds 8 [763]
;      4 (2). The data type of a dataset is not BYTE, SHORT, INTEGER, LONG, REAL, DOUBLE, or STRING [775,995]
;      5 (3). Dataset name is truncated or does not match VAR_NAME value [794,985]
;      6 (4). Metadata label VAR_NAME not found for the dataset [818,1020]
;      7 (4). VAR_NAME does not match any DATA_VARIABLES values [818,1020]
;      8 (5). No Variable Attributes returned after HDF call [807,1009]
;      9 (6). Metadata Dataset listing order may not match the order of the Global Attribute 
;         DATA_VARIABLES Values [1071]
;     10 (8). Variable is written to the HDF file as a coordinate variable [759]

COMMON WIDGET_WIN_A

;Note any calibrated (scaled) HDF4 dataset is corrected using the formula specified in 
;UG_print42r3.pdf pg. 3-107: orig = cal * (cal_val - offset)

;Possible error messages for this procedure
proname='Read_HDF_SDS procedure: '
errtxt=STRARR(2)
errtxt[0]=' found in the Root Group of the HDF5 File.'
errtxt[1]=' is zero or not able to be determined (check for corrupted file).'
lu=-1

;Allowable VAR_DATA_TYPEs
avdt=['BYTE','SHORT','INTEGER','LONG','REAL','DOUBLE','STRING']
transpose_vals=1 ;default is to transpose VAR_SIZE and VAR_DEPEND values on reading

;If necessary, free up memory by destroying the heap variables pointed at by its pointer arguments
;from previous calls to this program
IF N_ELEMENTS(sds) NE 0 THEN PTR_FREE,sds.va_l,sds.va_v,sds.data

;Define the HDF SDS storage structure
sds_set={va_l: PTR_NEW(), $ ;Variable Attribute Labels
         va_v: PTR_NEW(), $ ;Variable Attribute Values
         data: PTR_NEW()}   ;SD data array

IF catinfo[0,0] EQ 'H4' THEN BEGIN

  ;The HDF_SD_START function opens an HDF file and initializes the SD interface.
  sd_id=HDF_SD_START(ifile,/READ)

  ;Determine the number of SDS (n_sds) and global attributes (n_ga) found
  ;in the current file.
  HDF_SD_FILEINFO,sd_id,n_sds,n_ga
  IF n_sds EQ 0L THEN ntxt='Number of SDS datasets' $
  ELSE IF n_ga EQ 0L THEN ntxt='Number of Global Attributes' $
  ELSE ntxt=''
  IF ntxt NE '' THEN BEGIN
    STOP_WITH_ERROR_A,o3[3]+proname,ntxt+errtxt[1],lu & RETURN
  ENDIF
  ga=STRARR(n_ga) ;set the Global Attribute dimensions
  vn=[''] ;initialize vn array (to hold Dataset names)
  n_sds_hold=n_sds & n_vn=0L & do_coordvar=0

  ;Read the file's Global Attributes and determine number of DATA_VARIABLES
  FOR i=0L,n_ga-1L DO BEGIN
    ;The HDF_SD_ATTRINFO procedure reads or retrieves info about an SD attribute.
    HDF_SD_ATTRINFO,sd_id,i,NAME=ga_name,DATA=ga_data
    ga_name=STRTRIM(ga_name,2) & ga_data=STRTRIM(ga_data,2)
    ;Assign global attributes to ga
    ga[i]=ga_name+'='+ga_data
    ;read list of DATA_VARIABLES into array
    IF STRUPCASE(ga_name) EQ 'DATA_VARIABLES' THEN vn=STRSPLIT(ga_data,' ;',/Extract,COUNT=n_vn)
  ENDFOR
  
  IF n_sds_hold NE n_vn THEN BEGIN 
    ;Do check for sds being a Dimension attribute
    do_coordvar=1
    FOR i=0L,n_sds-1L DO BEGIN
      ;The HDF_SD_SELECT function returns an SD dataset ID given the current
      ;SD interface ID, and the zero-based SD dataset index.
      sds_id=HDF_SD_SELECT(sd_id,i)
      IF HDF_SD_ISCOORDVAR(sds_id) THEN n_sds_hold=n_sds_hold-1L
      ;Closes the SDS interface.
      HDF_SD_ENDACCESS,sds_id
    ENDFOR
    IF n_sds_hold EQ 0L THEN BEGIN
      STOP_WITH_ERROR_A,o3[3]+proname,'Number of SDS datasets'+errtxt[1],lu
      RETURN
    ENDIF

    IF n_sds_hold NE n_vn THEN $
      INFOTXT_OUTPUT_A,[0],[STRTRIM(n_vn,2),STRTRIM(n_sds_hold,2),'HDF_SD_FILEINFO']
      ;DATA_VARIABLES values not read successfully, or number of datasets given under DATA_VARIABLES
      ;is not equal to the number saved to the file
  ENDIF
  
  ;Determine maximum number of attributes, and match the dataset order to DATA_VARIABLES list if possible
  max_atts=0L & oi=LONARR(n_sds_hold)
  dv_order=1 & c_sds=0L
  catinfo=STRARR(n_sds_hold,4) ;output info for catalog output
  FOR i=0L,n_sds-1L DO BEGIN
    ;The HDF_SD_SELECT function returns an SD dataset ID given the current
    ;SD interface ID, and the zero-based SD dataset index.
    sds_id=HDF_SD_SELECT(sd_id,i)

    IF (do_coordvar EQ 0) OR (NOT HDF_SD_ISCOORDVAR(sds_id)) THEN BEGIN
      ;The HDF_SD_GETINFO procedure retrieves information about an SD dataset.
      HDF_SD_GETINFO,sds_id,NATTS=sds_natts, $ ;no. attributes
                            TYPE=sds_type, $   ;data type
                            DIMS=sds_dim, $    ;dimension information
                            NAME=sds_name      ;dataset name

      ;Check for coordinate variable
      IF HDF_SD_ISCOORDVAR(sds_id) THEN INFOTXT_OUTPUT_A,[8],[sds_name] 

      ;Check number of dimensions
      n_sds_dim=N_ELEMENTS(sds_dim)
      IF n_sds_dim gt 8 THEN INFOTXT_OUTPUT_A,[1],[sds_name,STRTRIM(n_sds_dim,2)]

      ;Check that a dataset name has been successfully read
      sds_name=STRTRIM(sds_name,2)
      IF sds_name EQ '' THEN sds_name='N/A'

      ;Rename format to be compatible with the Metadata guidelines
      sds_type=STRTRIM(STRUPCASE(sds_type),2)
      IF sds_type EQ 'INT' THEN sds_type='SHORT' $
      ELSE IF sds_type EQ 'LONG' THEN sds_type='INTEGER' $
      ELSE IF sds_type EQ 'FLOAT' THEN sds_type='REAL'
      vi=WHERE(sds_type EQ avdt,vcnt)
      IF vcnt EQ 0 THEN INFOTXT_OUTPUT_A,[2],[sds_name,sds_type]

      IF sds_natts NE 0L THEN BEGIN
        IF sds_natts GT max_atts THEN max_atts=sds_natts
        vnf=0 & lcnt=0 & vnv='' & vcnt=sds_natts
        ;Extract the variable attributes
        FOR j=0L,sds_natts-1L DO BEGIN
          ;The HDF_SD_ATTRINFO procedure reads or retrieves information about an SD attribute.
          HDF_SD_ATTRINFO,sds_id,j,NAME=va_name,DATA=va_value,TYPE=va_type
          va_name=STRTRIM(va_name,2)
          IF va_type EQ 'STRING' THEN va_value=STRTRIM(va_value,2)
          ;Check returned dataset attributes (sds_) with saved attributes (va_) 
          IF (STRUPCASE(va_name) EQ 'VAR_NAME') AND (vnf EQ 0) THEN BEGIN
            ;check that the dataset name matches the VAR_NAME
            vnf=1
            IF STRUPCASE(va_value) NE STRUPCASE(sds_name) THEN BEGIN
              ;Try and determine which is wrong - Dataset name or VAR_NAME - default is Dataset name
              li=WHERE((STRUPCASE(sds_name) EQ STRUPCASE(vn)) AND (vn[0] NE ''),lcnt)
              ;If lcnt NE 0 then Dataset name matches DATA_VARIABLES value so assume that VAR_NAME is wrong
              IF lcnt NE 0 THEN usesds=1 ELSE usesds=0
              INFOTXT_OUTPUT_A,[3,4,usesds],[sds_name,va_value]
              IF usesds EQ 0 THEN sds_name=va_value ELSE va_value=sds_name
            ENDIF
            vnv=va_value
            ;match the order of the dataset to the DATA_VARIABLES list
            li=WHERE(STRUPCASE(va_value) EQ STRUPCASE(vn),lcnt)
          ENDIF
          IF STRUPCASE(va_name) EQ 'VAR_DATA_TYPE' THEN BEGIN
            va_value=STRUPCASE(va_value) 
            IF va_value NE sds_type THEN BEGIN
              ;Dataset is not saved in the same data type as that described by VAR_DATA_TYPE
              IF (sds_type EQ 'INTEGER') AND (va_value EQ 'LONG') THEN $
                itxt=['32-bit INTEGER','64-bit LONG'] $
              ELSE IF (sds_type EQ 'SHORT') AND (va_value EQ 'INTEGER') THEN $
                itxt=['16-bit SHORT','32-bit INTEGER'] $
              ELSE itxt=[sds_type,va_value]
               
            ENDIF
          ENDIF
          IF STRUPCASE(va_name) EQ 'VAR_SIZE' THEN BEGIN
          
          ENDIF
        ENDFOR
      ENDIF ELSE BEGIN ;No Variable Attributes found
        vcnt=3
        ;Can the SDS_NAME be matched with a DATA_VARIABLES value?
        li=WHERE(STRUPCASE(sds_name) EQ STRUPCASE(vn),lcnt)
        IF lcnt NE 0 THEN vnf=1 ELSE vnf=0
        INFOTXT_OUTPUT_A,[5],[sds_name,'HDF_SD_GETINFO']
      ENDELSE

      ;Check for possible problems with determining array index
      IF (lcnt NE 0) AND (li[0] LT n_sds_hold) THEN BEGIN
        IF catinfo[li[0],0] NE '' THEN dv_order=0 ;This array has already been written to
      ENDIF ELSE IF (lcnt EQ 0) OR (vnf EQ 0) OR (li[0] GE n_sds_hold) THEN dv_order=0
      ;Write out information text if sds_name cannot be matched and determine array index
      IF dv_order EQ 0 THEN BEGIN
        li=WHERE(catinfo[*,0] EQ '') ;determine lowest available array index to write info to
        in0=[4,vnf,lcnt,n_vn]
        IF (vnf EQ 0) OR ((lcnt EQ 0) AND (n_vn NE 0L)) THEN INFOTXT_OUTPUT_A,in0,[sds_name,vnv]
      ENDIF
      
      oi[c_sds]=li[0] ;Attribute order index
      c_sds=c_sds+1L

      catinfo[li[0],0]=sds_name & catinfo[li[0],1]=sds_type
      catinfo[li[0],2]=STRTRIM(sds_dim[0],2) & catinfo[li[0],3]=vcnt
      IF N_ELEMENTS(sds_dim) GT 1 THEN $
        FOR j=1,N_ELEMENTS(sds_dim)-1 DO catinfo[li[0],2]=catinfo[li[0],2]+';'+STRTRIM(sds_dim[j],2)
    ENDIF

    ;Closes the SDS interface.
    HDF_SD_ENDACCESS,sds_id
  ENDFOR

  IF max_atts EQ 0L THEN max_atts=3 ;Use information from HDF_SD_GETINFO call only
  
  ;Dimension the structure to the number of datasets x number of attributes
  sds=REPLICATE(sds_set, n_sds_hold, max_atts)
  
  ;Write attributes to structure
  c_sds=0L
  !QUIET=1 ;suppress system error and information messages  
  FOR i=0L,n_sds-1L DO BEGIN
    ;The HDF_SD_SELECT function returns an SD dataset ID given the current
    ;SD interface ID, and the zero-based SD dataset index.
    sds_id=HDF_SD_SELECT(sd_id,i)
    nocal=1 ;Boolean to identify dataset which has been calibrated
    IF (do_coordvar EQ 0) OR (NOT HDF_SD_ISCOORDVAR(sds_id)) THEN BEGIN
      ;The HDF_SD_GETINFO procedure retrieves information about an SD dataset.
      ;Note - any saved pre-defined attributes will be called with HDF_SD_ATTRINFO call
      HDF_SD_GETINFO,sds_id,NATTS=sds_natts, $ ;no. attributes
                            TYPE=sds_type, $   ;data type
                            DIMS=sds_dim, $    ;dimension information
                            NAME=sds_name, $   ;dataset name
                            CALDATA=sds_cal    ;pre-defined calibration info
      
      ;Check to see whether data has had scale factor and offset applied
      IF (sds_cal.Cal NE 0.D) OR (sds_cal.Offset NE 0.D) THEN BEGIN
        nocal=0 ;Dataset has been calibrated
        ;identify datatype of the original dataset
        CASE 1 OF
          sds_cal.Num_Type EQ 21L: vdt_val='BYTE'
          sds_cal.Num_Type EQ 22L: vdt_val='SHORT'
          sds_cal.Num_Type EQ 24L: vdt_val='INTEGER'
          sds_cal.Num_Type EQ 5L: vdt_val='REAL'
          sds_cal.Num_Type EQ 6L: vdt_val='DOUBLE'
          ELSE: vdt_val='' ;invalid or cannot determine original datatype
        ENDCASE
      ENDIF
      
      IF sds_natts NE 0L THEN BEGIN
        ;Extract the variable attributes
        FOR j=0L,sds_natts-1L DO BEGIN
          ;The HDF_SD_ATTRINFO procedure reads or retrieves information about an SD attribute.
          HDF_SD_ATTRINFO,sds_id,j,NAME=va_name,DATA=va_value,TYPE=va_type
          va_name=STRTRIM(va_name,2)
          IF va_type EQ 'STRING' THEN va_value=STRTRIM(va_value,2)
          IF (nocal EQ 0) AND (STRUPCASE(va_name) EQ 'VAR_DATA_TYPE') THEN BEGIN 
            ;If required prepare INFORMATION text (written after DATA has been corrected)
            IF (vdt_val NE STRUPCASE(va_value)) AND (vdt_val NE '') THEN BEGIN
              io_arr=[STRTRIM(sds_name,2),va_value,vdt_val]
              va_value=vdt_val
            ENDIF ELSE BEGIN
              io_arr=[''] & vdt_val=va_value
            ENDELSE
          ENDIF 
          sds[oi[c_sds],j].va_l=PTR_NEW(va_name)
          sds[oi[c_sds],j].va_v=PTR_NEW(va_value)
        ENDFOR
      ENDIF ELSE BEGIN ;No Variable Attributes found
        va_lab=['VAR_NAME','VAR_SIZE','VAR_DATA_TYPE']
        FOR j=0,2 DO sds[oi[c_sds],j].va_l=PTR_NEW(va_lab)
        sds[oi[c_sds],0].va_v=PTR_NEW(sds_name)
        sds[oi[c_sds],1].va_v=PTR_NEW(sds_dim)
        ;Rename format to be compatible with the Metadata guidelines
        IF sds_type EQ 'INT' THEN sds_type='SHORT' $
        ELSE IF sds_type EQ 'LONG' THEN sds_type='INTEGER' $
        ELSE IF sds_type EQ 'FLOAT' THEN sds_type='REAL'
        sds[oi[c_sds],2].va_v=PTR_NEW(sds_type)
      ENDELSE
      ;Extract the data
      HDF_SD_GETDATA,sds_id,datasize
      
      IF nocal EQ 0 THEN BEGIN 
        ;apply scale factor and offset corrections to data and write text to log file
        CASE 1 OF 
          vdt_val EQ 'BYTE': datasize=BYTE(sds_cal.Cal*(datasize-sds_cal.Offset))
          vdt_val EQ 'SHORT': datasize=FIX(sds_cal.Cal*(datasize-sds_cal.Offset))
          vdt_val EQ 'INTEGER': datasize=LONG(sds_cal.Cal*(datasize-sds_cal.Offset))
          vdt_val EQ 'REAL': datasize=FLOAT(sds_cal.Cal*(datasize-sds_cal.Offset))
          ELSE: datasize=DOUBLE(sds_cal.Cal*(datasize-sds_cal.Offset))
        ENDCASE
        INFOTXT_OUTPUT_A,[9],[STRTRIM(sds_name,2)]
        IF io_arr[0] NE '' THEN INFOTXT_OUTPUT_A,[10],io_arr
      ENDIF
      sds[oi[c_sds],0].data=PTR_NEW(datasize)
      c_sds=c_sds+1L
    ENDIF

    ;Closes the SDS interface.
    HDF_SD_ENDACCESS,sds_id
  ENDFOR
  !QUIET=0 ;Allow system error and information messages
  ;The HDF_SD_END function closes the SD interface to an HDF file.
  HDF_SD_END,sd_id
ENDIF ELSE BEGIN ;HDF5 format file
  stdfm=1 ;Boolean indicating standard AVDC/EVDC/NDACC H5 format or not
  dv_order=1 ;Boolean indicating whether Metadata Variable listing order matches DATA_VARIABLES values
  n_vn=0L ;Initialize the number of Variable Names in the standard format h5 file
  hdf_file_id=H5F_OPEN(ifile)
  sd_id=H5G_OPEN(hdf_file_id,'/')

  ;Get number of attributes within the root group (these should be the Global Attributes)
  n_ga=H5A_GET_NUM_ATTRS(sd_id)
  ;Get the number of objects within the root group (including datasets, groups etc)
  n_obj=H5G_GET_NMEMBERS(sd_id,'/')

  IF n_obj NE 0L THEN BEGIN
    d_obj=INTARR(n_obj) & g_obj=INTARR(n_obj)
    ;Determine number of datasets.  Note: if H5 file created using H4toH5 then an extra
    ;group will have been created which will not be used.  Also datasets may be listed
    ;alphabetically. This section also determines whether the H5 file is a standard
    ;AVDC/EVDC/NDACC groundbased file or otherwise.
    FOR i=0L,n_obj-1L DO BEGIN
      sds_name=H5G_GET_MEMBER_NAME(sd_id,'/',i)
      h5fstat=H5G_GET_OBJINFO(sd_id,sds_name)
      IF h5fstat.type EQ 'DATASET' THEN d_obj[i]=1 $
      ELSE IF h5fstat.type EQ 'GROUP' THEN g_obj[i]=1
    ENDFOR
    di=WHERE(d_obj EQ 1,n_sds)
    gi=WHERE(g_obj EQ 1,n_grp)
    IF (n_ga EQ 0) AND (n_sds EQ 0) AND (n_grp NE 0) THEN stdfm=0
  ENDIF ELSE n_sds=0L

  IF stdfm EQ 0 THEN catinfo[0,0]='HE5' ;non-standard dataset so need to call READ_NONSTD_H5

  IF n_ga NE 0 THEN BEGIN
    ga=STRARR(n_ga) ;set the Global Attribute dimensions
    vn=[''] ;initialize vn array (to hold Dataset names)
    ;Read in the Global Attribute labels and values
    FOR i=0L,n_ga-1L DO BEGIN
      ga_id=H5A_OPEN_IDX(sd_id,i)
      ga_name=H5A_GET_NAME(ga_id) & ga_name=STRTRIM(ga_name,2)
      ga_data=H5A_READ(ga_id) & ga_data=STRTRIM(ga_data,2)
      ;Check for _GLOSDS suffix and strip (added for compatibility with H4toH5 utility)
      IF STRMID(STRUPCASE(ga_name),STRLEN(ga_name)-7) EQ '_GLOSDS' THEN $
        ga_name=STRMID(ga_name,0,STRPOS(ga_name,'_',/Reverse_Search))
      WHILE STRMID(ga_name,STRLEN(ga_name)-1) EQ '_' DO ga_name=STRMID(ga_name,0,STRLEN(ga_name)-1)
      ga[i]=ga_name+'='+ga_data
      H5A_CLOSE,ga_id
      ;Extract the list of the DATA_VARIABLES
      IF STRUPCASE(ga_name) EQ 'DATA_VARIABLES' THEN vn=STRSPLIT(ga_data,' ;',/Extract,COUNT=n_vn)
    ENDFOR
  ENDIF ELSE IF stdfm EQ 1 THEN BEGIN
    STOP_WITH_ERROR_A,o3[3]+proname,'No Global Attributes'+errtxt[0],lu
    RETURN
  ENDIF

  IF n_sds NE 0L THEN BEGIN
    IF n_vn NE n_sds THEN $
      INFOTXT_OUTPUT_A,[0],[STRTRIM(n_vn,2),STRTRIM(n_sds,2),'H5G_GET_NMEMBERS']
      ;DATA_VARIABLES values not read successfully, or number of datasets given under DATA_VARIABLES
      ;is not equal to the number saved to the file

    ;Determine maximum number of Attributes and correct dataset order
    max_atts=0L & oi=LONARR(n_sds)
    dv_order=1 & c_sds=0L
    catinfo=STRARR(n_sds,4) ;output info for catalog output
    FOR i=0,n_sds-1 DO BEGIN
      sds_name=H5G_GET_MEMBER_NAME(sd_id,'/',di[i])
      ds_id=H5D_OPEN(sd_id,sds_name)
      IF sds_name EQ '' THEN sds_name='N/A'
      datasize=H5D_READ(ds_id)
      ;Determine the number of attributes associated with the dataset
      sds_natts=H5A_GET_NUM_ATTRS(ds_id)
      IF sds_natts GT max_atts THEN max_atts=sds_natts

      IF sds_natts NE 0L THEN BEGIN
        vnf=0 & lcnt=0 & vnv=''
        ci=STRARR(4) ;array containing catalog attributes
        ;Read in Dataset Attributes
        FOR j=0L,sds_natts-1L DO BEGIN
          da_id=H5A_OPEN_IDX(ds_id,j)
          da_name=H5A_GET_NAME(da_id) & da_name=STRTRIM(da_name,2)
          va_value=H5A_READ(da_id)
          IF SIZE(va_value,/TYPE) EQ 7 THEN va_value=STRTRIM(va_value,2)
          CASE 1 OF
            (STRUPCASE(da_name) EQ 'VAR_NAME') AND (vnf EQ 0):BEGIN
                vnf=1
                ;check that the dataset name matches the VAR_NAME
                IF STRUPCASE(va_value) NE STRUPCASE(sds_name) THEN BEGIN
                  ;Try and determine which is wrong - Dataset name or VAR_NAME - default is Dataset name
                  li=WHERE((STRUPCASE(sds_name) EQ STRUPCASE(vn)) AND (vn[0] NE ''),lcnt)
                  ;If lcnt NE 0 then Dataset name matches DATA_VARIABLES value so assume that VAR_NAME is wrong
                  IF lcnt NE 0 THEN usesds=1 ELSE usesds=0
                  INFOTXT_OUTPUT_A,[3,5,usesds],[sds_name,va_value]
                  IF usesds EQ 0 THEN sds_name=va_value ELSE va_value=sds_name
                ENDIF
                ;Determine actual list order from DATA_VARIABLE listing (H5 lists datasets alphabetically)
                li=WHERE(STRUPCASE(va_value[0]) EQ STRUPCASE(vn),lcnt)
                ci[0]=va_value & vnv=va_value
              END
            STRUPCASE(da_name) EQ 'VAR_DATA_TYPE': BEGIN
                ci[1]=va_value
                vi=WHERE(STRUPCASE(va_value[0]) EQ avdt,vcnt)
                if vcnt EQ 0 THEN INFOTXT_OUTPUT_A,[2],[sds_name,va_value]
              END
            STRUPCASE(da_name) EQ 'VAR_SIZE': FOR k=0,N_ELEMENTS(va_value)-1 DO $  
                IF k EQ 0 THEN ci[2]=STRTRIM(va_value[k],2) ELSE ci[2]=ci[2]+';'+STRTRIM(va_value[k],2)
            ELSE:
          ENDCASE
          H5A_CLOSE,da_id
        ENDFOR
        ci[3]=STRTRIM(sds_natts,2)
      ENDIF ELSE BEGIN ;No Attributes, so can only write dataset name to Metadata
        ci=[STRUPCASE(sds_name),'','','1'] & vnv=sds_name
        ;Can the SDS_NAME be matched with a DATA_VARIABLES value?
        li=WHERE(STRUPCASE(sds_name) EQ STRUPCASE(vn),lcnt)
        IF lcnt NE 0 THEN vnf=1 ELSE vnf=0
        INFOTXT_OUTPUT_A,[5],[sds_name,'H5A_GET_NUM_ATTRS']
      ENDELSE

      ;Check for possible problems with determining array index
      IF lcnt NE 0 THEN BEGIN
        IF catinfo[li[0],0] NE '' THEN dv_order=0 ;This array has already been written to
      ENDIF ELSE IF (lcnt EQ 0) OR (vnf EQ 0) THEN dv_order=0
      ;Write out information text if sds_name cannot be matched and determine array index
      IF dv_order EQ 0 THEN BEGIN
        li=WHERE(catinfo[*,0] EQ '') ;determine lowest available array index to write info to
        in0=[4,vnf,lcnt,n_vn]
        IF (vnf EQ 0) OR ((lcnt EQ 0) AND (n_vn NE 0L)) THEN INFOTXT_OUTPUT_A,in0,[sds_name,vnv]
      ENDIF
      
      H5D_CLOSE,ds_id
      oi[i]=li[0] ;to put datasets in the correct order
      catinfo[li[0],*]=ci[*]
    ENDFOR
  ENDIF ELSE IF stdfm EQ 1 THEN BEGIN
    STOP_WITH_ERROR_A,o3[3]+proname,'No Datasets'+errtxt[0],lu & RETURN
  ENDIF
 
  ;Dimension the structure to the size of the SDS datasets (with dimension n_sds) 
  sds=REPLICATE(sds_set, n_sds, max_atts)
  ;Put datasets and attributes into sds structure
  FOR i=0,n_sds-1 DO BEGIN
    sds_name=H5G_GET_MEMBER_NAME(sd_id,'/',di[i])
    ds_id=H5D_OPEN(sd_id,sds_name)
    IF sds_name EQ '' THEN sds_name='N/A'
    datasize=H5D_READ(ds_id)
    ;Determine the number of attributes associated with the dataset
    sds_natts=H5A_GET_NUM_ATTRS(ds_id)

    IF sds_natts NE 0L THEN BEGIN
      ;Read in Dataset Attributes
      FOR j=0L,sds_natts-1L DO BEGIN
        da_id=H5A_OPEN_IDX(ds_id,j)
        da_name=H5A_GET_NAME(da_id) & da_name=STRTRIM(da_name,2)
        va_value=H5A_READ(da_id)
        IF SIZE(va_value,/TYPE) EQ 7 THEN va_value=STRTRIM(va_value,2)
        H5A_CLOSE,da_id
        sds[oi[i],j].va_l=PTR_NEW(da_name)
        sds[oi[i],j].va_v=PTR_NEW(va_value)
      ENDFOR
    ENDIF ELSE BEGIN ;No Attributes, so can only write dataset name to structure
      val='VAR_NAME'
      sds[oi[i],0].va_l=PTR_NEW(val)
      sds[oi[i],0].va_v=PTR_NEW(sds_name)
    ENDELSE

    H5D_CLOSE,ds_id
    sds[oi[i],0].data=PTR_NEW(datasize)
  ENDFOR

  H5G_CLOSE,sd_id
  H5F_CLOSE,hdf_file_id
ENDELSE

IF (dv_order EQ 0) AND (n_vn NE 0L) THEN INFOTXT_OUTPUT_A,[6]

END ;Procedure Read_HDF_SDS



PRO output_hdf_data, ifile, ga, sds, catinfo
;Procedure to output the contents of an HDF file in ASCII form, either in a format compatible for
;conversion back to HDF, or in Row and Column format, or as a summary list
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20050729: Original IDLCR8ASCII Routine - Version 1.0
;    20050912: Removed Common variable definition CATALOGINFO and made the variable a parameter passed
;              to the procedure; Make output filenames lower case; If data type is double and the
;              accompanying VIS_FORMAT value starts with an 'F' (e.g. F9.4), then, change the 'F' to a
;              'D' when specifying the format for output - Version 1.1
;    20061004: Common variable definition WIDGET_WIN_A added for Error calls; Display input/output
;              information in a pop-up display window if the program is opened using IDL VM - Version 2.0
;    20080302: Added code which sends the Catalog and log output to the IDLDE output window and/or an
;              external file (as determined by the dux array values); Ensure all data values are
;              separated by a space when the Dump output option is chosen - Version 3.0
;    20101122: Adopt GEOMS metadata standard; Because FORMAT attribute(s) have been dropped can no longer 
;              use defined formatting values when outputing data to files; Default ASCII formatting 
;              adopted - scientific notation for REAL and DOUBLE, except for DATETIME and related values, 
;              which have formatting dependent on the data type - Version 4.0
;
;  Inputs: ifile - a string containing the name of the HDF file to be read in.
;          ga - a string array containing the global attribute labels and values extracted from the HDF
;               file.
;          sds - a structure using pointers, of size [n_sds,n_atts], containing the variable attribute 
;                labels and values (sds[n,m].va_l and sds[n,m].va_v) and the data (sds[n,0].data) 
;                extracted from the HDF file.
;          catinfo - a string array of size [n_sds,4] (where n_sds is the number of datasets in the HDF
;                    file), containing information on the variable name, data type, data dimension, and
;                    number of attributes
;
;  Outputs: Nil
;
;  Called by: IDLCR8ASCII
;
;  Subroutines Called: None

COMMON WIDGET_WIN_A

;determine number of datasets and attributes (from sds.va)
as=SIZE(catinfo)
n_sds=as[1]

IF o3[1] EQ 'C' THEN BEGIN
  IF o3[3] EQ '' THEN BEGIN
    lineno=lineno+n_sds+1
    wintxt='Listing of Var_Name Index; Var_Name; Var_Data_Type; Var_Size'
    WIDGET_CONTROL,wtxt,set_value=wintxt,/Append,Set_text_top_line=lineno
  ENDIF
  FOR i=dux[0],dux[1],dux[2] DO PRINTF,i,'Listing of Var_Name Index; Var_Name; Var_Data_Type; Var_Size'
  FOR j=0,n_sds-1 DO BEGIN
    IF o3[3] EQ '' THEN BEGIN
      wintxt=STRTRIM(j,2)+'; '+catinfo[j,0]+'; '+catinfo[j,1]+'; '+catinfo[j,2]
      WIDGET_CONTROL,wtxt,set_value=wintxt,/Append
    ENDIF
    FOR i=dux[0],dux[1],dux[2] DO $
      PRINTF,i,STRTRIM(j,2),'; ',catinfo[j,0],'; ',catinfo[j,1],'; ',catinfo[j,2]
  ENDFOR
ENDIF
IF o3[0] NE '0' THEN BEGIN
  ;create output filenames
  outf1=STRMID(ifile,0,STRPOS(ifile,'.',/Reverse_Search))+'.meta'
  outf2=STRMID(ifile,0,STRPOS(ifile,'.',/Reverse_Search))+'.data'
  OPENW,lu1,outf1,/GET_LUN
  OPENW,lu2,outf2,/GET_LUN

  ;HDF4 and NETCDF pre-defined attributes
  ncsa=['long_name','units','format','coordsys','valid_range','_FillValue','scale_factor', $
        'scale_factor_err','add_offset','add_offset_err','calibrated_nt']

  PRINTF,lu1,'! Output from IDLcr8ASCII application v4.0'
  PRINTF,lu1,'! '+ifile & PRINTF,lu1,'!'
  PRINTF,lu1,'! Global Attributes'
  FOR i=0,N_ELEMENTS(ga)-1 DO PRINTF,lu1,ga[i]

  FOR j=0,n_sds-1 DO BEGIN
    n_atts=FIX(catinfo[j,3])
    PRINTF,lu1,'!' & PRINTF,lu1,'! Variable Attributes'
    PRINTF,lu2,catinfo[j,0]
    FOR i=0,n_atts DO BEGIN ;number of attributes. Last loop is for Data
      IF i EQ n_atts THEN vav=*sds[j,0].data ELSE vav=*sds[j,i].va_v
      vavt=SIZE(vav,/TYPE)
      IF (STRPOS(STRUPCASE(catinfo[j,0]),'DATETIME') NE -1) AND ((vavt EQ 4) OR (vavt EQ 5)) THEN BEGIN
        ns=MAX(STRLEN(STRTRIM(LONG(vav),2)))
        IF vavt EQ 4 THEN dp=6 ELSE dp=9 ;indicates the number of decimal places to use in the output
        fmt='(D'+STRTRIM(ns+dp+1,2)+'.'+STRTRIM(dp,2)+')'
      ENDIF ELSE IF (vavt EQ 4) OR (vavt EQ 5) THEN fmt='(E0)' $
      ELSE IF vavt EQ 7 THEN fmt='(A)' $
      ELSE fmt='(I0)'
      IF i NE n_atts THEN BEGIN ;write out metadata in form LABEL=VALUE
        vat=*sds[j,i].va_l
        ni=WHERE(STRLOWCASE(vat) EQ STRLOWCASE(ncsa),ncnt) ;check for pre-defined attributes and exclude
        IF ncnt EQ 0 THEN BEGIN
          FOR k=0,N_ELEMENTS(vav)-1 DO BEGIN
            IF k EQ 0 THEN vat=vat+'='+STRTRIM(STRING(FORMAT=fmt,vav[k]),2) $
            ELSE vat=vat+';'+STRTRIM(STRING(FORMAT=fmt,vav[k]),2)
          ENDFOR
          PRINTF,lu1,vat
        ENDIF
      ENDIF
    ENDFOR
         
    ;Write out data
    IF o3[0] EQ 'F' THEN BEGIN
      PRINTF,lu2,format=fmt,vav
    ENDIF ELSE IF o3[0] EQ 'D' THEN BEGIN
      ;Ensure there is a single character between all values
      sdssize=SIZE(vav,/Dimension)
      sdshold=STRTRIM(STRING(FORMAT=fmt,vav),2)
      maxstr=MAX(STRLEN(sdshold)) 
      ;use default IDL formatting rules
      sdshold=STRING(format='(A'+STRTRIM(maxstr,2)+')',sdshold)
      ;Uncomment line below if format described by VIS_FORMAT is required
      ;sdshold=STRING(format=p_f,*sds[j].data)
      sdshold=REFORM(sdshold,sdssize)
      PRINTF,lu2,sdshold
    ENDIF
  ENDFOR
  PRINTF,lu1,'!' & PRINTF,lu1,'! End of output file created by IDLcr8ASCII'
  FREE_LUN,lu1 & FREE_LUN,lu2
  IF o3[3] EQ '' THEN BEGIN
    lineno=lineno+2L
    WIDGET_CONTROL,wtxt,set_value=outf1+' created!',/Append,Set_text_top_line=lineno
    WIDGET_CONTROL,wtxt,set_value=outf2+' created!',/Append,Set_text_top_line=lineno
  ENDIF
  FOR i=dux[0],dux[1],dux[2] DO BEGIN
    PRINTF,i,'  '+outf1+' created!' & PRINTF,i,'  '+outf2+' created!'
  ENDFOR
ENDIF
END ;Procedure Output_HDF_Data



PRO idlcr8ascii, ifile, ga, sds, reterr, FORMAT=o1, DUMP=o2, CATALOG=o4, POPUP=o5, LOG=o6, AVDC=o7
;Main IDL procedure to read GEOMS compliant HDF4 and HDF5 files.
;
;Program documentation, idlcr8ascii-v4.0_Readme.pdf, available on http://avdc.gsfc.nasa.gov.
;
;Program sub-version 4.0 (2010xxxx)
; ----------
;Written by Ian Boyd, NIWA-ERI for the AVDC - i.boyd@niwa.com
;
;  History:
;    20050729: Original Release - Version 1.0
;    20050912: Removed Common variable definition CATALOGINFO; If the format of the
;              DATA_START_DATE and FILE_GENERATION_DATE values is MJD2000, then change to ISO8601,
;              unless the output option is /Dump - Version 1.1
;    20061004: Common variable definition WIDGET_WIN_A added for Error calls; Make the code suitable
;              for running on a licensed version of IDL (using the .pro and .sav versions of the code)
;              and on IDL Virtual Machine (using the .sav version of the code); Change the command
;              line keyword options. Remove the /Help option (window now opened if there are no command
;              line parameters), and /Catalog can now be called together with /AVDC or /Dump; The
;              program can now handle multiple HDF files as input (either as a string array or as a
;              file spec); Display input/output information as well as errors and warnings in a pop-up
;              display window if the program is called using IDL VM; Help window becomes an
;              Introduction window, and the user has the option of continuing to run the program with
;              file inputs; Include option to read HDF5 versions of the ground-based files
;              - Version 2.0
;    20080302: Remove HELP,/TRACEBACK call, which identified how the program was called. This was used
;              to stop output to the IDLDE output window in the event that IDL VM was used, but it is
;              not required as IDL VM ignores these print calls; Add options to send Catalog and logged
;              input/output information to a Pop-up Box (/Popup) and/or to an external file (/Log). Add
;              DIALOG_BOX to show completion of the program if program inputs are via the INTRO box, and
;              logging window option isn't requested - Version 3.0
;    20091208: Add INFORMATION text message to INFOTXT_OUTPUT_A procedure; Replace /AVDC keyword with 
;              /FORMAT (note /AVDC also retained for backward compatibility purposes); Improve checks 
;              on parameter and keyword inputs - Version 3.03
;    20101122: Changes made to account for new GEOMS conventions, including changing the format of the
;              structure so that numeric metadata values can be saved in their actual datatype, rather
;              than string; Add return error code option so that program returns to the calling program 
;              if an error is generated - Version 4.0
;
;  Inputs: ifile - a string array or filespec containing the name of the HDF file(s) to be read in 
;
;          OPTIONS
;            FORMAT - Program generates two output files per input file (with .meta and .data 
;                     extensions). The resulting files are compatible with programs that can write HDF 
;                     files using these two files as input.
;            DUMP - Program generates two output files per input file (with .meta and .data extensions).
;                   Data values will be shown as indicated by the array format defined by VAR_SIZE.
;            CATALOG - Program sends the variable index, variable name, format, and dimension(s)
;                      information to a pop-up window or the IDL DE output log window.
;            POPUP - to append input/output information as well as warnings and errors to a pop-up
;                    display window
;            LOG - to append input/output/catalog information as well as errors to a log file named
;                  idlcr8ascii.log
;
;  Outputs: ga - If included as a parameter in the command line, a string array containing the global
;                attribute labels and values extracted from a single HDF file.
;           sds - If included as a parameter in the command line, a structure using pointers, of size
;                 [n_sds,n_atts], containing the variable attribute labels and values (sds[n,m].va_l
;                 and sds[n.m].va_v) and the data (sds[n,0].data) extracted from a single HDF file. 
;                 The data is saved in the form defined by the variable attributes
;           reterr - optional string input that, if included, returns an error message to the calling
;                    program rather than stop the program. Note that the Pop-up option will be
;                    deselected if present together with this argument.
;           Two ASCII files per input file containing the attributes and datasets extracted from the HDF
;           file(s), if the FORMAT or DUMP options are chosen. Summary metadata information if the
;           CATALOG option is chosen.
;
;  Called by: Main Routine
;
;  Subroutines Called: INTRO_A (if program called without command line parameters)
;                      READ_HDF_SDS
;                      JDF_2_DATETIME
;                      OUTPUT_HDF_DATA (if output is not just to session memory only)
;                      STOP_WITH_ERROR_A (if error state detected)
;                      INFOTXT_OUTPUT_A (if program can make a change)
;    Possible Conditions for STOP_WITH_ERROR call (plus [line number] where called):
;      1. No valid HDF4 or HDF5 file selected [1354,1405,1406,1407,1412]
;
;    Information Conditions (when the program is able to make changes):
;      1. If Session Memory option is chosen can only read in one HDF file [1385]
;      2. /POPUP keyword cannot be used together with the 'reterr' argument [4043]
;      3. Argument 'reterr' must be a scalar variable of type string [4044]

COMMON WIDGET_WIN_A

;Possible error messages for this procedure
proname='IDLCR8ASCII procedure: '
IF FLOAT(!Version.Release) GE 5.6 THEN errtxt='No valid HDF4 or HDF5 file selected.' $
ELSE BEGIN
  errtxt='No valid HDF4 file selected '
  errtxt=errtxt+'(Note: Input file can only be HDF4 for IDL'+!Version.Release+').'
ENDELSE
lu=-1

ON_IOERROR,TypeConversionError ;used when checking Datetime format

IF N_PARAMS() EQ 1 THEN BEGIN ;File input only
  ;check to see what output keyword options are set - if none then intype=-3 (i.e. invalid)
  IF (NOT KEYWORD_SET(o1)) AND (NOT KEYWORD_SET(o2)) AND (NOT KEYWORD_SET(o4)) AND $
     (NOT KEYWORD_SET(o7)) THEN intype=-3 ELSE intype=SIZE(ifile,/Type)
ENDIF ELSE IF N_PARAMS() GE 1 THEN intype=SIZE(ifile,/Type) $ ;Check that infile is a string
ELSE IF (KEYWORD_SET(o1)) OR (KEYWORD_SET(o2)) OR (KEYWORD_SET(o4)) OR $
        (KEYWORD_SET(o7)) THEN intype=-1 $ ;only need to open dialog box for input file
ELSE IF (KEYWORD_SET(o5)) OR (KEYWORD_SET(o6)) THEN intype=-3 $ ;cannot have these keyword options only        
ELSE intype=-2 ;no parameter or keyword inputs in idlcr8ascii call
IF (intype NE 7) AND (intype GE 0) THEN intype=-3 ;first command line parameter not a string type
dux=[-1,-1,1] ;initialize flags for output log to IDLDE Output Window and/or to file
;dux[0] default allows output to the IDLDE output window (ignored by IDL VM)
;dux[1] is the program assigned file unit for sending log output to file
;dux[2] is the step between dux[0] and dux[1]
rerr='NA' ;initialize return error string

o3=['-1','0','0','0','0']
IF intype LT -1 THEN BEGIN ;either no or invalid input parameters and/or keywords
  INTRO_A,intype ;Open Intro Box and determine output options (FORMAT/DUMP, Catalog, Session Memory)
  IF o3[0] EQ '-1' THEN BEGIN
    STOP_WITH_ERROR_A,'','',lu & RETURN
  ENDIF
  IF o3[3] EQ 'P' THEN o3[3]='' ELSE o3[3]='D_'
ENDIF ELSE BEGIN ;Set options (FORMAT/DUMP, Catalog, Session Memory, Popup Window, Log Output)
  IF (KEYWORD_SET(o1)) OR (KEYWORD_SET(o7)) THEN o3=['F','0','0','D_','0'] $
  ELSE IF KEYWORD_SET(o2) THEN o3=['D','0','0','D_','0'] ELSE o3=['0','0','0','D_','0']
  IF N_PARAMS() EQ 3 THEN o3[2]='M'
  IF KEYWORD_SET(o4) THEN o3[1]='C'
  IF KEYWORD_SET(o5) THEN o3[3]=''
  IF KEYWORD_SET(o6) THEN o3[4]='idlcr8ascii.log'
ENDELSE

;Check for reterr parameter
infotxt1=STRARR(3) & infotxt2=infotxt1
IF (N_PARAMS() EQ 2) OR (N_PARAMS() GE 4) THEN BEGIN
  ;If reterr included allows error output to return to a calling program
  IF N_PARAMS() EQ 2 THEN reterr=ga ;session memory option not wanted
  ;IF (ARG_PRESENT(reterr)) AND (SIZE(reterr,/Type) EQ 7) THEN BEGIN
  IF SIZE(reterr,/Type) EQ 7 THEN BEGIN
    rerr=''
    IF o3[3] EQ '' THEN BEGIN
      ;Deselect POPUP option and write INFORMATION message
      o3[3]='D_'
      infotxt1[1]='  INFORMATION: /POPUP keyword cannot be used together with the ''reterr'' argument.'
      infotxt1[2]='  The request for a POPUP window has been ignored.'
    ENDIF
  ENDIF ELSE BEGIN
    ;reterr input included but is of the incorrect type, or parameter cannot be returned
    ;to the calling program
    infotxt2[1]='  INFORMATION: Argument ''reterr'' must be of type string.' ;a returnable variable of type string.'
    infotxt2[2]='  idlcr8ascii will stop normally if an error is encountered.'
  ENDELSE
ENDIF

IF N_PARAMS() GE 1 THEN BEGIN
  ;Check that input HDF files exist. If not then prompt the user for the missing files
  arorfs=SIZE(ifile,/Dimensions) ;Is HDF file input Filespec or String Array?
  IF (arorfs[0] EQ 0) THEN BEGIN ;input is filespec
    IF ifile NE '' THEN ifile=FINDFILE(ifile)
    isize=SIZE(ifile,/Dimensions)
    IF isize[0] EQ 0 THEN ifile=[''] ;no files found matching filespec
  ENDIF
  IF N_ELEMENTS(arorfs) GT 1 THEN ifile=REFORM(ifile,N_ELEMENTS(ifile),/Overwrite) ;Convert to 1-D array
  file_exist=FILE_TEST(ifile,/Read)
  gi=WHERE(file_exist EQ 1,gcnt)
  IF gcnt NE 0 THEN ifile=ifile[gi] ;contains all valid filenames
ENDIF ELSE ifile=['']
gi=WHERE(ifile NE '',nfile)
IF nfile EQ 0 THEN BEGIN
  IF o3[2] EQ 'M' THEN $ ;pick one file only
    ifile=DIALOG_PICKFILE(Filter=['*.hdf','*.h5'],/Must_Exist, $
          Title='Select HDFv4 or HDFv5 AVDC/EVDC/NDACC Format File') $
  ELSE $ ;multiple selection permissable
    ifile=DIALOG_PICKFILE(Filter=['*.hdf','*.h5'],/Must_Exist, $
          /Multiple_Files,Title='Select HDFv4 or HDFv5 AVDC/EVDC/NDACC Format File(s)')
ENDIF
;now check to see that files were actually selected, if not STOP!
gi=WHERE(ifile NE '',nfile)
IF nfile EQ 0 THEN BEGIN
  STOP_WITH_ERROR_A,'D_'+proname,errtxt,lu
  IF STRLEN(rerr) GT 2 THEN BEGIN
    IF N_PARAMS() EQ 2 THEN ga=rerr ELSE reterr=rerr
  ENDIF
  RETURN
ENDIF ELSE BEGIN
  ifile=ifile[gi] & dsort=SORT(ifile) & ifile=ifile[dsort]
  ifile=FILE_DIRNAME(ifile,/Mark_Directory)+FILE_BASENAME(ifile)
ENDELSE

;Set dux values according to output options
IF o3[4] NE '0' THEN BEGIN ;open idlcr8ascii.log
  o3[4]=FILE_DIRNAME(ifile[0],/Mark_Directory)+o3[4]
  res=FILE_TEST(o3[4],/Write)
  IF res EQ 0 THEN openw,du,o3[4],/GET_LUN $
  ELSE BEGIN
    OPENW,du,o3[4],/Append,/GET_LUN & FOR i=0,1 DO PRINTF,du,''
  ENDELSE
  dux[1]=du & dux[2]=dux[1]-dux[0]
ENDIF
FOR i=dux[0],dux[1],dux[2] DO PRINTF,i,'HDF File Input/Output Log - Program Started on '+SYSTIME(0)

IF o3[3] EQ '' THEN BEGIN
  ;Set-up output window display widget
  base=WIDGET_BASE(Title='HDF File Input/Output Log',Units=2,yoffset=3,xoffset=3,Tlb_Frame_Attr=1,/Column) ;,Tab_Mode=1)
  wtxt=WIDGET_TEXT(base,/Scroll,xsize=100,ysize=12)
  base2=WIDGET_BASE(base)
  b3=WIDGET_BUTTON(base2,value='Finish',uvalue='DONE',frame=3,Sensitive=0) ;,Accelerator='Return')
  WIDGET_CONTROL,wtxt,/Realize
  WIDGET_CONTROL,base,/Realize
  lineno=0L
ENDIF

IF (o3[2] EQ 'M') AND (N_ELEMENTS(ifile) GT 1) THEN BEGIN
  ifile=[ifile[0]] & nfile=1
  INFOTXT_OUTPUT_A,[7]
ENDIF

FOR ndf=0,nfile-1 DO BEGIN
  catinfo=STRARR(1,4) ;initialize catinfo array
  ifile[ndf]=FILE_SEARCH(ifile[ndf],/Fully_Qualify_Path)
  IF o3[3] EQ '' THEN BEGIN
    lineno=lineno+2L
    IF ndf NE 0 THEN WIDGET_CONTROL,wtxt,set_value='',/Append
    WIDGET_CONTROL,wtxt,set_value='Reading '+ifile[ndf],/Append,Set_text_top_line=lineno
  ENDIF
  FOR i=dux[0],dux[1],dux[2] DO BEGIN
    IF ndf NE 0 THEN PRINTF,i,''
    PRINTF,i,'Reading '+ifile[ndf]
    PRINTF,i,''
  ENDFOR

  IF FILE_TEST(ifile[ndf]) EQ 1 THEN BEGIN
    IF HDF_ISHDF(ifile[ndf]) EQ 1 THEN catinfo[0,0]='H4' $
    ELSE IF FLOAT(!Version.Release) GE 5.6 THEN BEGIN
      IF H5F_IS_HDF5(ifile[ndf]) EQ 1 THEN catinfo[0,0]='H5' $
      ELSE BEGIN
        STOP_WITH_ERROR_A,o3[3]+proname,errtxt,lu
        IF STRLEN(rerr) GT 2 THEN BEGIN
          IF N_PARAMS() EQ 2 THEN ga=rerr ELSE reterr=rerr
        ENDIF
        RETURN
      ENDELSE
    ENDIF ELSE BEGIN
      STOP_WITH_ERROR_A,o3[3]+proname,errtxt,lu
      IF STRLEN(rerr) GT 2 THEN BEGIN
        IF N_PARAMS() EQ 2 THEN ga=rerr ELSE reterr=rerr
      ENDIF
      RETURN
    ENDELSE
  ENDIF ELSE BEGIN
    STOP_WITH_ERROR_A,o3[3]+proname,errtxt,lu
    IF STRLEN(rerr) GT 2 THEN BEGIN
      IF N_PARAMS() EQ 2 THEN ga=rerr ELSE reterr=rerr
    ENDIF
    RETURN 
  ENDELSE

  ;Open and read the file
  READ_HDF_SDS,ifile[ndf],ga,sds,catinfo
  IF STRLEN(rerr) GT 2 THEN BEGIN
    reterr=rerr & RETURN
  ENDIF

  IF catinfo[0,0] EQ 'HE5' THEN BEGIN
    STOP_WITH_ERROR_A,o3[3]+proname,errtxt,lu
    IF STRLEN(rerr) GT 2 THEN BEGIN
      IF N_PARAMS() EQ 2 THEN ga=rerr ELSE reterr=rerr
    ENDIF
    RETURN
  ENDIF ELSE BEGIN ;Do checks and output standard format file
    ;Convert format of DATA_START_DATE and FILE_GENERATION_DATE if required
    ;Note: for /Dump option output will still be original format
    gaiso=STRARR(2)
    gi=WHERE((STRPOS(STRUPCASE(ga),'DATA_START_DATE') NE -1) OR $
             (STRPOS(STRUPCASE(ga),'FILE_GENERATION_DATE') NE -1),gcnt)
    IF gcnt NE 0 THEN BEGIN
      FOR i=0,gcnt-1 DO BEGIN
        res=STRSPLIT(ga[gi[i]],' =',/Extract)
        IF N_ELEMENTS(res) EQ 2 THEN BEGIN
          IF STRPOS(STRUPCASE(res[1]),'Z') EQ -1 THEN BEGIN ;i.e. not ISO8601
            valid=0 ;used for Type Conversion Check
            mjd=DOUBLE(res[1]) ;will jump to TypeConversionError if Res[1] is not a number
            valid=1 ;got to here so valid conversion (presumably it is MJD2000)
            TypeConversionError:
            IF valid EQ 1 THEN BEGIN
              iso='' & iso=JDF_2_DATETIME(mjd,/MJD2000,/S)
              gaiso[i]=res[0]+'='+iso
              IF o3[0] EQ 'F' THEN ga[gi[i]]=gaiso[i]
            ENDIF
          ENDIF
        ENDIF
      ENDFOR
    ENDIF

    IF (o3[0] NE '0') OR (o3[1] NE '0') THEN OUTPUT_HDF_DATA,ifile[ndf],ga,sds,catinfo
    FOR i=0,1 DO IF gaiso[i] NE '' THEN ga[gi[i]]=gaiso[i]
    IF o3[2] EQ 'M' THEN BEGIN
      IF o3[3] EQ '' THEN BEGIN
        lineno=lineno+1L
        WIDGET_CONTROL,wtxt,set_value=ifile+' array and heap structure created!',/Append,Set_text_top_line=lineno
      ENDIF
      FOR i=dux[0],dux[1],dux[2] DO PRINTF,i,'  '+ifile[ndf]+' array and heap structure created!'
    ENDIF
  ENDELSE
ENDFOR

IF rerr EQ '' THEN $
  IF nfile EQ 1 THEN reterr=ifile[0]+' successfully read' $
  ELSE reterr='HDF files successfully read'
IF N_PARAMS() EQ 2 THEN ga=reterr

FOR i=dux[0],dux[1],dux[2] DO BEGIN
  PRINTF,i,'' & PRINTF,i,'HDF file read completed - Program Ended on '+SYSTIME(0)
ENDFOR
IF dux[1] GT -1 THEN FREE_LUN,dux[1]
IF o3[3] EQ '' THEN BEGIN
  WIDGET_CONTROL,b3,Sensitive=1,/Input_Focus
  WIDGET_CONTROL,wtxt,set_value='',/Append,Set_text_top_line=lineno+2L
  WIDGET_CONTROL,wtxt,set_value='HDF file read completed - hit <Finish> to close program',/Append
  XMANAGER,'idlcr8ascii',base
ENDIF ELSE IF intype LT 0 THEN BEGIN ;Create Finish Dialog Box
  res=DIALOG_MESSAGE('HDF file read completed!',/Information,Title='AVDC IDLcr8ASCII')
ENDIF

END ;procedure IDLcr8ASCII
