FUNCTION Exponent, axis, index, number

	; A special case.
	IF number EQ 0 THEN RETURN, '0'

	; Assuming multiples of 10 with format.
	ex = String(number, Format='(e8.0)')
	pt = StrPos(ex, '.')

	first = StrMid(ex, 0, pt)
	sign = StrMid(ex, pt+2, 1)
	thisExponent = StrMid(ex, pt+3)

	;print, number, ex, first
	;help, first, sign

	; Shave off leading zero in exponent
	WHILE StrMid(thisExponent, 0, 1) EQ '0' DO thisExponent = StrMid(thisExponent, 1)

	; Fix for sign and missing zero problem.
	IF (Long(thisExponent) EQ 0) THEN BEGIN
		sign = ''
		thisExponent = '0'
	ENDIF

	; Make the exponent a superscript.
	IF sign EQ '-' THEN BEGIN

	IF( STRTRIM(first,2) EQ '1' ) THEN BEGIN
		RETURN, '10!U' + sign + thisExponent + '!N'
	ENDIF ELSE BEGIN
		RETURN, first + 'x10!U' + sign + thisExponent + '!N'
	ENDELSE

	ENDIF ELSE BEGIN
	IF STRTRIM(first,2) EQ '1' THEN BEGIN
		IF STRTRIM(thisExponent,2) EQ '0' THEN RETURN, '1'
		IF STRTRIM(thisExponent,2) EQ '1' THEN RETURN, '10'
		RETURN, '10!U' + thisExponent + '!N'
		ENDIF ELSE BEGIN
			RETURN, first + 'x10!U' + thisExponent + '!N'
		ENDELSE
	ENDELSE


	END
