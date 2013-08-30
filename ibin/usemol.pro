PRO usemol, site, mol, A

; updated to use structure Dec 09
; old version is usemol1

A = {gas, mol       : '',           $
	      ctfmt      : '',		      $
		   smol       : '',		      $
         vmrscl     : 0.0,		      $
	      vmrunits   : '',		      $
	      altpltrng  : DBLARR(2),	   $
	      altrng     : DBLARR(2),  	$
	      colscl     : 0.0,		      $
	      colrng     : DBLARR(2),	   $
	      avgcolrng  : DBLARR(2),	   $	; average column range
	      vmrng      : DBLARR(2),  	$
	      avrng      : DBLARR(2),  	$	; average trop vmr range
	      molid      : 0,            $
	      logrng     : DBLARR(2),    $
	      vrngs      : DBLARR(3,2),  $
	      pcrng      : DBLARR(3,2),  $
	      mnthrng    : DBLARR(2),	   $
	      files      : STRARR(10),   $
	      cerr       : 0.0,          $
	      slimid     : 0,            $
	      mls        : 0}

A.mol     = mol
A.mls     = 1
A.pcrng   = [ [0., 0., 0. ], [10.,10.,10.] ]
A.mnthrng = [0.0, 0.0]

; dummy names so we can plot slimcat for mols w/o A.mls profiles

A.files[0] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d063.he5'
A.files[1] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d066.he5'
A.files[2] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d068.he5'
A.files[3] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d071.he5'
A.files[4] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d074.he5'
A.files[1] =	'MLS-Aura_L2GP-O3_v01-51-c03_2005d078.he5'
A.files[6] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d080.he5'
A.files[7] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d081.he5'
A.files[8] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d084.he5'

sitemol = site + mol

CASE sitemol OF


   'ACFHCL' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'HCl'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.vmrng = [0,4]
      A.logrng = [0.001,10.]			; for A.mls log scale
      A.ctfmt = '(f4.1)'
      A.altrng = [ 0., 60. ]		; plot bounds
      A.altpltrng = [3., 55.]		; min max for file read
      A.colscl = 1.e-15
      A.colrng = [ 1.5, 2.5 ]
      A.avgcolrng = [ 1.5, 2.5 ]
      A.slimid = 17

      A.pcrng[0,*] = [ 0., 1. ]		; 0  - 10km
      A.pcrng[1,*] = [ 0., 8.0 ]	; 10 - 19km
      A.pcrng[2,*] = [ 0., 4.0 ]	; 19 - 30km
      END


   'MLOHCL' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'HCl'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.vmrng = [0,4]
      A.logrng = [0.001,10.]			; for A.mls log scale
      A.ctfmt = '(f4.1)'
      A.altrng = [ 0., 60. ]		; plot bounds
      A.altpltrng = [3., 55.]		; min max for file read
      A.colscl = 1.e-15
      A.colrng = [ 1.5, 2.5 ]
      A.avgcolrng = [ 1.5, 2.5 ]
      A.slimid = 17

      A.pcrng[0,*] = [ 0., 1. ]		; 0  - 10km
      A.pcrng[1,*] = [ 0., 8.0 ]	; 10 - 19km
      A.pcrng[2,*] = [ 0., 4.0 ]	; 19 - 30km


      ; !!! check indexes below

      A.files[0] =	'MLS-Aura_L2GP-HCl_v01-51-c01_2005d063.he5'
      A.files[1] =	'MLS-Aura_L2GP-HCl_v01-51-c01_2005d066.he5'
      A.files[2] =	'MLS-Aura_L2GP-HCl_v01-51-c01_2005d068.he5'
      A.files[3] =	'MLS-Aura_L2GP-HCl_v01-51-c01_2005d071.he5'
      A.files[4] =	'MLS-Aura_L2GP-HCl_v01-51-c01_2005d074.he5'
      A.files[1] =	'MLS-Aura_L2GP-HCl_v01-51-c03_2005d078.he5'
      A.files[6] =	'MLS-Aura_L2GP-HCl_v01-51-c01_2005d080.he5'
      A.files[7] =	'MLS-Aura_L2GP-HCl_v01-51-c01_2005d081.he5'
      A.files[8] =	'MLS-Aura_L2GP-HCl_v01-51-c01_2005d084.he5'
      A.molid = 15
      END


   'MLOH2CO' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'H!D2!NCO!N'
      A.vmrscl     = 1.0e9
      A.vmrunits   =  '[ppb]'
      A.logrng     = [ 1.e-4, 10. ]
      A.vmrng      = [ 0.0, 0.4 ]
      A.avrng      = [ 0.0, 0.2 ]
      A.mnthrng    = [ 0.0, 0.2 ]
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 40. ]		; plot bounds
      A.altpltrng  = [ 0., 40.]		   ; min max for file read
      A.colscl     = 1.0e-15
      A.colrng     = [ 0., 4. ]
      A.avgcolrng     = [ 0., 2. ]
      A.slimid     = -1
      A.molid      = 46
      A.pcrng[0,*] = [ 0., 4. ]	      ; low alt panel
      A.pcrng[1,*] = [ 0., .4 ]		   ; mid alt panel
      A.pcrng[2,*] = [ 0., 0.05 ]	   ; high alt panel
      END


   'TABH2CO' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'H!D2!NCO!N'
      A.vmrscl     = 1.0e9
      A.vmrunits   =  '[ppb]'
      A.logrng     = [ 1.e-4, 10. ]
      A.vmrng      = [ 0.0, 0.4 ]
      A.avrng      = [ 0.0, 0.2 ]
      A.mnthrng    = [ 0.0, 0.2 ]
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 40. ]		; plot bounds
      A.altpltrng  = [ 0., 40.]		   ; min max for file read
      A.colscl     = 1.0e-15
      A.colrng     = [ 0., 4. ]
      A.avgcolrng     = [ 0., 2. ]
      A.slimid     = -1
      A.molid      = 46
      A.pcrng[0,*] = [ 0., 4. ]	      ; low alt panel
      A.pcrng[1,*] = [ 0., .4 ]		   ; mid alt panel
      A.pcrng[2,*] = [ 0., 0.05 ]	   ; high alt panel
      END

   'MLOHCOOH' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'HCOOH!N'
      A.vmrscl     = 1.0e9
      A.vmrunits   =  '[ppb]'
      A.logrng     = [ 1.e-7, 10. ]
      A.vmrng      = [ 0.0, 2. ]
      A.mnthrng    = [ 0.0, 0.8 ]
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 40. ]		   ; plot bounds
      A.altpltrng  = [ 0., 40.]		   ; min max for file read
      A.colscl     = 1.0e-15
      A.colrng     = [ 0., 8. ]
      A.avgcolrng     = [ 0., 8. ]
      A.avrng      = [ 0., 0.3 ]
      A.slimid     = -1
      A.molid      = 46
      A.pcrng[0,*] = [ 0., 8.0 ]	   ; low alt panel
      A.pcrng[1,*] = [ 0., 1. ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.05 ]	   ; high alt panel
      END


   'TABHCOOH' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'HCOOH!N'
      A.vmrscl     = 1.0e9
      A.vmrunits   =  '[ppb]'
      A.logrng     = [ 1.e-7, 10. ]
      A.vmrng      = [ 0.0, 2. ]
      A.mnthrng    = [ 0.0, 0.8 ]
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 40. ]		   ; plot bounds
      A.altpltrng  = [ 0., 40.]		   ; min max for file read
      A.colscl     = 1.0e-15
      A.colrng     = [ 0., 8. ]
      A.avgcolrng     = [ 0., 8. ]
      A.avrng      = [ 0., 0.3 ]
      A.slimid     = -1
      A.molid      = 46
      A.pcrng[0,*] = [ 0., 8.0 ]	   ; low alt panel
      A.pcrng[1,*] = [ 0., 1. ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.05 ]	   ; high alt panel
      END

   'MLOC2H2' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'C!D2!NH!D2!N'
      A.vmrscl     = 1.0e9
      A.vmrunits   =  '[ppb]'
      A.logrng     = [ 1.e-7, 10. ]
      A.vmrng      = [ 0.0, 2. ]
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 40. ]		; plot bounds
      A.altpltrng  = [ 0., 40.]		; min max for file read
      A.colscl     = 1.0e-16
      A.colrng     = [ 0., 1. ]
      A.slimid     = -1
      A.molid      = 40
      A.pcrng[0,*] = [ 0., 1.0 ]	   ; low alt panel
      A.pcrng[1,*] = [ 0., 0.2 ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.0001 ]	   ; high alt panel
      END

   'TABC2H2' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'C!D2!NH!D2!N'
      A.vmrscl     = 1.0e9
      A.vmrunits   =  '[ppb]'
      A.logrng     = [ 1.e-7, 10. ]
      A.vmrng      = [ 0.0, 2. ]
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 40. ]		; plot bounds
      A.altpltrng  = [ 0., 40.]		; min max for file read
      A.colscl     = 1.0e-16
      A.colrng     = [ 0., 1. ]
      A.slimid     = -1
      A.molid      = 40
      A.pcrng[0,*] = [ 0., 1.0 ]	   ; low alt panel
      A.pcrng[1,*] = [ 0., 0.2 ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.0001 ]	   ; high alt panel
      END

   'TABC5H8' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'C!D5!NH!D8!N'
      A.vmrscl     = 1.0e9
      A.vmrunits   =  '[ppb]'
      A.logrng     = [ 1.e-7, 10. ]
      A.vmrng      = [ 0.0, 2. ]
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 40. ]		; plot bounds
      A.altpltrng  = [ 0., 40.]		; min max for file read
      A.colscl     = 1.0e-16
      A.colrng     = [ 0., 1. ]
      A.slimid     = -1
      A.molid      = 72
      A.pcrng[0,*] = [ 0., 1.0 ]	   ; low alt panel
      A.pcrng[1,*] = [ 0., 0.2 ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.0001 ]	   ; high alt panel
      END

   'TABCH2O' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'CH!D2!NO!N'
      A.vmrscl     = 1.0e9
      A.vmrunits   =  '[ppb]'
      A.logrng     = [ 1.e-7, 10. ]
      A.vmrng      = [ 0.0, 2. ]
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 40. ]		; plot bounds
      A.altpltrng  = [ 0., 40.]		; min max for file read
      A.colscl     = 1.0e-16
      A.colrng     = [ 0., 1. ]
      A.slimid     = -1
      A.molid      = 20
      A.pcrng[0,*] = [ 0., 1.0 ]	   ; low alt panel
      A.pcrng[1,*] = [ 0., 0.2 ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.0001 ]	   ; high alt panel
      END

   'TABMVK' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'MVK!N'
      A.vmrscl     = 1.0e9
      A.vmrunits   =  '[ppb]'
      A.logrng     = [ 1.e-7, 10. ]
      A.vmrng      = [ 0.0, 2. ]
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 40. ]		; plot bounds
      A.altpltrng  = [ 0., 40.]		; min max for file read
      A.colscl     = 1.0e-16
      A.colrng     = [ 0., 1. ]
      A.slimid     = -1
      A.molid      = 73
      A.pcrng[0,*] = [ 0., 1.0 ]	   ; low alt panel
      A.pcrng[1,*] = [ 0., 0.2 ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.0001 ]	   ; high alt panel
      END

   'TABHBR' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'HBr'
      A.vmrscl     = 1.0e9
      A.vmrunits   =  '[ppb]'
      A.logrng     = [ 1.e-7, 10. ]
      A.vmrng      = [ 0.0, 2. ]
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 40. ]		; plot bounds
      A.altpltrng  = [ 0., 40.]		; min max for file read
      A.colscl     = 1.0e-16
      A.colrng     = [ 0., 1. ]
      A.slimid     = -1
      A.molid      = 39
      A.pcrng[0,*] = [ 0., 1.0 ]	   ; low alt panel
      A.pcrng[1,*] = [ 0., 0.2 ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.0001 ]	   ; high alt panel
      END

   'MLOHBR' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'HBr'
      A.vmrscl     = 1.0e9
      A.vmrunits   =  '[ppb]'
      A.logrng     = [ 1.e-7, 10. ]
      A.vmrng      = [ 0.0, 2. ]
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 40. ]		; plot bounds
      A.altpltrng  = [ 0., 40.]		; min max for file read
      A.colscl     = 1.0e-16
      A.colrng     = [ 0., 1. ]
      A.slimid     = -1
      A.molid      = 39
      A.pcrng[0,*] = [ 0., 1.0 ]	   ; low alt panel
      A.pcrng[1,*] = [ 0., 0.2 ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.0001 ]	   ; high alt panel
      END

   'TABC2H4' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'C!D2!NH!D4!N'
      A.vmrscl     = 1.0e9
      A.vmrunits   =  '[ppb]'
      A.logrng     = [ 1.e-7, 10. ]
      A.vmrng      = [ 0.0, 2. ]
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 40. ]		; plot bounds
      A.altpltrng  = [ 0., 40.]		; min max for file read
      A.colscl     = 1.0e-16
      A.colrng     = [ 0., 1. ]
      A.slimid     = -1
      A.molid      = 39
      A.pcrng[0,*] = [ 0., 1.0 ]	   ; low alt panel
      A.pcrng[1,*] = [ 0., 0.2 ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.0001 ]	   ; high alt panel
      END

   'TABC3H6' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'C!D3!NH!D6!N'
      A.vmrscl     = 1.0e9
      A.vmrunits   =  '[ppb]'
      A.logrng     = [ 1.e-7, 10. ]
      A.vmrng      = [ 0.0, 2. ]
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 40. ]		; plot bounds
      A.altpltrng  = [ 0., 40.]		; min max for file read
      A.colscl     = 1.0e-16
      A.colrng     = [ 0., 1. ]
      A.slimid     = -1
      A.molid      = 75
      A.pcrng[0,*] = [ 0., 1.0 ]	   ; low alt panel
      A.pcrng[1,*] = [ 0., 0.2 ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.0001 ]	   ; high alt panel
      END

   'TABC4H8' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'C!D4!NH!D8!N'
      A.vmrscl     = 1.0e9
      A.vmrunits   =  '[ppb]'
      A.logrng     = [ 1.e-7, 10. ]
      A.vmrng      = [ 0.0, 2. ]
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 40. ]		; plot bounds
      A.altpltrng  = [ 0., 40.]		; min max for file read
      A.colscl     = 1.0e-16
      A.colrng     = [ 0., 1. ]
      A.slimid     = -1
      A.molid      = 76
      A.pcrng[0,*] = [ 0., 1.0 ]	   ; low alt panel
      A.pcrng[1,*] = [ 0., 0.2 ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.0001 ]	   ; high alt panel
      END

   'TABCH3COOH' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'CH!D3!NCOOH!N'
      A.vmrscl     = 1.0e9
      A.vmrunits   =  '[ppb]'
      A.logrng     = [ 1.e-7, 10. ]
      A.vmrng      = [ 0.0, 2. ]
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 40. ]		; plot bounds
      A.altpltrng  = [ 0., 40.]		; min max for file read
      A.colscl     = 1.0e-16
      A.colrng     = [ 0., 1. ]
      A.slimid     = -1
      A.molid      = 71
      A.pcrng[0,*] = [ 0., 1.0 ]	   ; low alt panel
      A.pcrng[1,*] = [ 0., 0.2 ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.0001 ]	   ; high alt panel
      END

   'TABHCOOH' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'HCOOH!N'
      A.vmrscl     = 1.0e9
      A.vmrunits   =  '[ppb]'
      A.logrng     = [ 1.e-7, 10. ]
      A.vmrng      = [ 0.0, 2. ]
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 40. ]		; plot bounds
      A.altpltrng  = [ 0., 40.]		; min max for file read
      A.colscl     = 1.0e-16
      A.colrng     = [ 0., 1. ]
      A.slimid     = -1
      A.molid      = 46
      A.pcrng[0,*] = [ 0., 1.0 ]	   ; low alt panel
      A.pcrng[1,*] = [ 0., 0.2 ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.0001 ]	   ; high alt panel
      END

   'TABC2H6' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'C!D2!NH!D6!N'
      A.vmrscl     = 1.0e9
      A.vmrunits   =  '[ppb]'
      A.logrng     = [ 1.e-7, 10. ]
      A.vmrng      = [ 1.0, 30 ]
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 40. ]		; plot bounds
      A.altpltrng = [ 0., 40.]		; min max for file read
      A.colscl     = 1.0e-16
      A.colrng     = [ 0., 5. ]
      A.slimid     = -1
      A.molid      = 38
      A.pcrng[0,*] = [ 0., 5.0 ]	   ; low alt panel
      A.pcrng[1,*] = [ 0., 1.0 ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.5 ]	   ; high alt panel
      END

   'MLOC2H6' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'C!D2!NH!D6!N'
      A.vmrscl     = 1.0e9
      A.vmrunits   =  '[ppb]'
      A.logrng     = [ 1.e-7, 10. ]
      A.vmrng      = [ 1.0, 30 ]
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 40. ]		; plot bounds
      A.altpltrng = [ 0., 40.]		; min max for file read
      A.colscl     = 1.0e-16
      A.colrng     = [ 0., 5. ]
      A.slimid     = -1
      A.molid      = 38
      A.pcrng[0,*] = [ 0., 5.0 ]	   ; low alt panel
      A.pcrng[1,*] = [ 0., 1.0 ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.5 ]	   ; high alt panel
      END

   'SF6' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'SF!D6!N'
      A.vmrscl = 1.0e12
      A.vmrunits = '[ppt]'
      A.logrng = [ 0.01, 100 ]
      A.vmrng = [ 0.1, 10 ]
      A.ctfmt = '(f4.2)'
      A.altrng = [ 10., 40. ]		; plot bounds
      A.altpltrng = [13., 40.]		; min max for file read
      A.colscl = 1.0e-14
      A.colrng = [ 0.0, 3. ]
      A.slimid = 28
      A.molid = 50
      A.pcrng[0,*] = [ 0., 2.0 ]	; low alt panel
      A.pcrng[1,*] = [ 0., 0.5 ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.1 ]	; high alt panel
      END

   'TABCH3OH' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'CH!D3!NOH'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.logrng = [ 0.01, 100 ]
      A.vmrng = [ 1.0, 30 ]
      A.ctfmt = '(f4.2)'
      A.altrng = [ 10., 40. ]		; plot bounds
      A.altpltrng = [13., 40.]		; min max for file read
      A.colscl = 1.
      A.colrng = [ 0., 0. ]
      A.slimid = -1
      A.molid = 64
      END


   'MLOCH3OH' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'CH!D3!NOH'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.logrng = [ 0.01, 100 ]
      A.vmrng = [ 1.0, 30 ]
      A.ctfmt = '(f4.2)'
      A.altrng = [ 10., 40. ]		; plot bounds
      A.altpltrng = [13., 40.]		; min max for file read
      A.colscl = 1.
      A.colrng = [ 0., 0. ]
      A.slimid = -1
      A.molid = 64
      END

   'FL0CO2' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'CO!D2!N'
      A.vmrscl = 1.0e6
      A.vmrunits = '[ppm]'
      A.vmrng = [1,8]
      A.logrng = [0.1,10.]			; for A.mls log scale
      A.ctfmt = '(f4.0)'
      A.altrng = [ 1., 45. ]		; plot bounds
      ;A.altrng = [ 1., 40. ]		; plot bounds for A.mls
      A.altpltrng = [1., 44.]		; min max for file read
      A.colscl = 1.0e-21
      A.colrng = [ 4., 12. ]
      A.slimid = 0
      A.molid = 2
      END

   'ACFCO2' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'CO!D2!N'
      A.vmrscl = 1.0e6
      A.vmrunits = '[ppm]'
      A.vmrng = [1,8]
      A.logrng = [0.1,10.]			; for A.mls log scale
      A.ctfmt = '(f4.0)'
      A.altrng = [ 1., 45. ]		; plot bounds
      ;A.altrng = [ 1., 40. ]		; plot bounds for A.mls
      A.altpltrng = [1., 44.]		; min max for file read
      A.colscl = 1.0e-21
      A.colrng = [ 4., 12. ]
      A.slimid = 0
      A.molid = 2
      END

   'ACFO13CO' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'CO!D2!N'
      A.vmrscl = 1.0e6
      A.vmrunits = '[ppm]'
      A.vmrng = [1,8]
      A.logrng = [0.1,10.]			; for A.mls log scale
      A.ctfmt = '(f4.0)'
      A.altrng = [ 1., 45. ]		; plot bounds
      ;A.altrng = [ 1., 40. ]		; plot bounds for A.mls
      A.altpltrng = [1., 44.]		; min max for file read
      A.colscl = 1.0e-21
      A.colrng = [ 4., 12. ]
      A.slimid = 0
      A.molid = 2
      END

   'ACFCO18O' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'CO!D2!N'
      A.vmrscl = 1.0e6
      A.vmrunits = '[ppm]'
      A.vmrng = [1,8]
      A.logrng = [0.1,10.]			; for A.mls log scale
      A.ctfmt = '(f4.0)'
      A.altrng = [ 1., 45. ]		; plot bounds
      ;A.altrng = [ 1., 40. ]		; plot bounds for A.mls
      A.altpltrng = [1., 44.]		; min max for file read
      A.colscl = 1.0e-21
      A.colrng = [ 4., 12. ]
      A.slimid = 0
      A.molid = 2
      END

   'TABCO2' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'CO!D2!N'
      A.vmrscl = 1.0e6
      A.vmrunits = '[ppm]'
      A.vmrng = [1,8]
      A.logrng = [0.1,10.]			; for A.mls log scale
      A.ctfmt = '(f4.0)'
      A.altrng = [ 1., 45. ]		; plot bounds
      ;A.altrng = [ 1., 40. ]		; plot bounds for A.mls
      A.altpltrng = [1., 44.]		; min max for file read
      A.colscl = 1.0e-21
      A.colrng = [ 4., 12. ]
      A.slimid = 0
      A.molid = 2
      END

   'MLOCO2' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'CO!D2!N'
      A.vmrscl = 1.0e6
      A.vmrunits = '[ppm]'
      A.vmrng = [1,8]
      A.logrng = [0.1,10.]			; for A.mls log scale
      A.ctfmt = '(f4.0)'
      A.altrng = [ 1., 45. ]		; plot bounds
      ;A.altrng = [ 1., 40. ]		; plot bounds for A.mls
      A.altpltrng = [1., 44.]		; min max for file read
      A.colscl = 1.0e-21
      A.colrng = [ 4., 12. ]
      A.slimid = 0
      A.molid = 2
      END

   'CHF2CL' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'CHF!D2!NCl'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.ctfmt = '(f4.1)'
      A.altrng = [ 0., 40. ]		; plot bounds
      A.altpltrng = [0., 40.]		; min max for file read
      A.colscl = 1.e-15
      A.colrng = [ 1.0, 5. ]
      A.logrng = [0.001, 1.0 ]
      A.slimid = 15
      A.molid = 42
      A.pcrng[0,*] = [ 0., 5. ]
      A.pcrng[1,*] = [ 0., 2. ]
      A.pcrng[2,*] = [ 0., 0.5 ]
      END

   'TABCLONO2' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'ClONO!D2!N'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.logrng = [ 0.01, 100 ]
      A.vmrng = [ 0.0, 10. ]
      A.ctfmt = '(f4.1)'
      A.altrng = [ 5., 40. ]		; plot bounds
      A.altpltrng = [12., 40.]		; min max for file read
      A.colscl = 1.e-15
      A.colrng = [ 0.0, 5.0 ]
      A.slimid = 15
      A.molid = 27
      A.pcrng[0,*] = [ 0., 0.2 ]	; low alt panel
      A.pcrng[1,*] = [ 0., 1. ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 4.0 ]	; high alt panel
      END

   'TABCOF2' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'COF!D2!N'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.ctfmt = '(f4.1)'
      A.logrng = [ 0.0001, 1 ]
      A.vmrng = [ 0.0, 0.5 ]
      A.altrng = [ 5., 40. ]		; plot bounds
      A.altpltrng = [12., 40.]		; min max for file read
      A.colscl = 1.e-14
      A.colrng = [ 0., 20. ]
      A.slimid = 37
      A.molid = 36
      END

   'TABO3' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol      = 'O!D3!N'
      A.vmrscl    = 1.0e6
      A.vmrunits  = '[ppm]'
      A.vmrng     = [0,8]
      A.logrng    = [0.001,10.]			; for A.mls log scale
      A.ctfmt     = '(f4.1)'
      A.altrng    = [ 0., 60. ]		; plot bounds
      ;A.altrng = [ 10., 40. ]		; plot bounds for A.mls
      A.altpltrng = [0., 55.]		; min max for file read
      A.colscl = 1.0e-18
      A.colrng = [ 5., 15. ]
      A.avgcolrng = [ 5., 15. ]
      A.avrng      = [ 0.02, 0.14 ]
      A.slimid = 0
      A.pcrng[0,*] = [ 0., 2. ]
      A.pcrng[1,*] = [ 0., 8. ]
      A.pcrng[2,*] = [ 2., 8. ]
                              ; !!! check indexes below

      A.files[0] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d063.he5'
      A.files[1] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d066.he5'
      A.files[2] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d068.he5'
      A.files[3] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d071.he5'
      A.files[4] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d074.he5'
      A.files[1] =	'MLS-Aura_L2GP-O3_v01-51-c03_2005d078.he5'
      A.files[6] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d080.he5'
      A.files[7] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d081.he5'
      A.files[8] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d084.he5'
      A.molid = 3
      END


'MLOO3' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'O!D3!N'
      A.vmrscl = 1.0e6
      A.vmrunits = '[ppm]'
      A.vmrng = [0,8]
      A.logrng = [0.001,15.]			; for A.mls log scale
      A.ctfmt = '(f4.1)'
      A.altrng = [ 5., 55. ]		; plot bounds
      ;A.altrng = [ 10., 40. ]		; plot bounds for A.mls
      A.altpltrng = [5., 44.]		; min max for file read
      A.colscl = 1.0e-18
      A.colrng = [ 5., 10. ]
      A.avgcolrng = [ 5., 15. ]
      A.avrng      = [ 0.02, 0.14 ]
      A.slimid = 0
      A.pcrng[0,*] = [ 0., 1. ]
      A.pcrng[1,*] = [ 0., 2. ]
      A.pcrng[2,*] = [ 2., 6. ]
                              ; !!! check indexes below

      A.files[0] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d063.he5'
      A.files[1] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d066.he5'
      A.files[2] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d068.he5'
      A.files[3] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d071.he5'
      A.files[4] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d074.he5'
      A.files[1] =	'MLS-Aura_L2GP-O3_v01-51-c03_2005d078.he5'
      A.files[6] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d080.he5'
      A.files[7] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d081.he5'
      A.files[8] =	'MLS-Aura_L2GP-O3_v01-51-c01_2005d084.he5'
      A.molid = 3
      END

   'TABN2O' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'N!D2!NO'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppbv]'
      A.logrng = [ 0.1, 500 ]
      A.vmrng = [ 0.0, 400 ]
      A.ctfmt = '(f4.1)'
      A.altrng = [ 5., 40. ]		; plot bounds
      A.altpltrng = [6., 40.]		; min max for file read
      A.colscl = 1.e-18
      A.colrng = [ 4., 8. ]
      A.avgcolrng = [ 4., 8. ]
      A.avrng  = [ 250., 500. ]
      A.slimid = 30
      A.molid = 4
      A.pcrng[0,*] = [ 0., 10. ]			; low
      A.pcrng[1,*] = [ 0., 4. ]				; mid
      A.pcrng[2,*] = [ 0., 0.5 ]			; high
      END

   'MLON2O' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'N!D2!NO'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppbv]'
      A.logrng = [ 0.1, 500 ]
      A.vmrng = [ 0.0, 400 ]
      A.ctfmt = '(f4.1)'
      A.altrng = [ 5., 40. ]		; plot bounds
      A.altpltrng = [6., 40.]		; min max for file read
      A.colscl = 1.e-18
      A.colrng = [ 4., 8. ]
      A.avgcolrng = [ 4., 8. ]
      A.avrng  = [ 250., 500. ]
      A.slimid = 30
      A.molid = 4
      A.pcrng[0,*] = [ 0., 10. ]			; low
      A.pcrng[1,*] = [ 0., 4. ]				; mid
      A.pcrng[2,*] = [ 0., 0.5 ]			; high
      END

   'ACFHNO3' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'HNO!D3!N'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.vmrng = [0,10]
      A.logrng = [0.0001,100.]			; for A.mls log scale
      A.ctfmt = '(f4.0)'
      A.altrng = [ 5., 40. ]		; plot bounds
      ;A.altrng = [ 10., 40. ]		; plot bounds   for A.mls
      A.altpltrng = [9., 40.]		; min max for file read
      A.colscl = 1.0e-16
      A.colrng = [ 1., 5. ]
      A.slimid = 8
      A.pcrng[0,*] = [ 0., 1. ]
      A.pcrng[1,*] = [ 0., 4. ]
      A.pcrng[2,*] = [ 0., 2. ]
      END

   'TABHNO3' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'HNO!D3!N'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.vmrng = [0,10]
      A.logrng = [0.0001,100.]			; for A.mls log scale
      A.ctfmt = '(f4.0)'
      A.altrng = [ 5., 40. ]		; plot bounds
      ;A.altrng = [ 10., 40. ]		; plot bounds   for A.mls
      A.altpltrng = [9., 40.]		; min max for file read
      A.colscl = 1.0e-16
      A.colrng = [ 1., 5. ]
      A.slimid = 8
      A.pcrng[0,*] = [ 0., 1. ]
      A.pcrng[1,*] = [ 0., 4. ]
      A.pcrng[2,*] = [ 0., 2. ]

                  ; !!! check indexes below

      A.files[0] =	'MLS-Aura_L2GP-HNO3_v01-51-c01_2005d063.he5'
      A.files[1] =	'MLS-Aura_L2GP-HNO3_v01-51-c01_2005d066.he5'
      A.files[2] =	'MLS-Aura_L2GP-HNO3_v01-51-c01_2005d068.he5'
      A.files[3] =	'MLS-Aura_L2GP-HNO3_v01-51-c01_2005d071.he5'
      A.files[4] =	'MLS-Aura_L2GP-HNO3_v01-51-c01_2005d074.he5'
      A.files[1] =	'MLS-Aura_L2GP-HNO3_v01-51-c03_2005d078.he5'
      A.files[6] =	'MLS-Aura_L2GP-HNO3_v01-51-c01_2005d080.he5'
      A.files[7] =	'MLS-Aura_L2GP-HNO3_v01-51-c01_2005d081.he5'
      A.files[8] =	'MLS-Aura_L2GP-HNO3_v01-51-c01_2005d084.he5'
      A.molid = 12
      END

   'MLOHNO3' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'HNO!D3!N'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.vmrng = [0,10]
      A.logrng = [0.0001,100.]			; for A.mls log scale
      A.ctfmt = '(f4.0)'
      A.altrng = [ 5., 40. ]		; plot bounds
      ;A.altrng = [ 10., 40. ]		; plot bounds   for A.mls
      A.altpltrng = [9., 40.]		; min max for file read
      A.colscl = 1.0e-16
      A.colrng = [ 0., 1.5]
      A.slimid = 8
      A.pcrng[0,*] = [ 0., 1. ]
      A.pcrng[1,*] = [ 0., 1. ]
      A.pcrng[2,*] = [ 0., 1. ]

                  ; !!! check indexes below

      A.files[0] =	'MLS-Aura_L2GP-HNO3_v01-51-c01_2005d063.he5'
      A.files[1] =	'MLS-Aura_L2GP-HNO3_v01-51-c01_2005d066.he5'
      A.files[2] =	'MLS-Aura_L2GP-HNO3_v01-51-c01_2005d068.he5'
      A.files[3] =	'MLS-Aura_L2GP-HNO3_v01-51-c01_2005d071.he5'
      A.files[4] =	'MLS-Aura_L2GP-HNO3_v01-51-c01_2005d074.he5'
      A.files[1] =	'MLS-Aura_L2GP-HNO3_v01-51-c03_2005d078.he5'
      A.files[6] =	'MLS-Aura_L2GP-HNO3_v01-51-c01_2005d080.he5'
      A.files[7] =	'MLS-Aura_L2GP-HNO3_v01-51-c01_2005d081.he5'
      A.files[8] =	'MLS-Aura_L2GP-HNO3_v01-51-c01_2005d084.he5'
      A.molid = 12
      END

   'MLOCO' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'CO'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppbv]'
      A.vmrng = [1,500]
      A.logrng = [ 0.1, 1000. ]
      A.ctfmt = '(f4.0)'
      A.altrng = [ 0., 80. ]		; plot bounds
      A.altpltrng = [0., 80.]		; min max for file read
      A.altrng = [ 0., 80. ]		; plot bounds   ground
      A.altpltrng = [0., 80.]		; min max for file read
      A.colscl = 1.0d-18
      A.colrng = [ 0.0, 4. ]
      A.slimid = 31
      A.molid = 5
      A.pcrng[0,*] = [ 0., 3. ]		; 0  - 8km
      A.pcrng[1,*] = [ 0.0, 0.4 ]	; 8  - 16km
      A.pcrng[2,*] = [ 0., 0.1 ]	; 16 - 28km
      END

   'TABCO' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'CO'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppbv]'
      A.vmrng = [1,500]
      A.logrng = [ 1.0, 1000. ]
      A.ctfmt = '(f4.0)'
      A.altrng = [ 10., 80. ]		; plot bounds
      A.altpltrng = [13., 80.]		; min max for file read
      A.altrng = [ 0., 80. ]		; plot bounds   ground
      A.altpltrng = [1., 80.]		; min max for file read
      A.colscl = 1.0d-18
      A.colrng = [ 1.0, 4. ]
      A.avgcolrng = [ 1., 3. ]
      A.slimid = 31
      A.molid = 5
      A.pcrng[0,*] = [ 1., 3. ]		; 0  - 8km
      A.pcrng[1,*] = [ 0.1, 0.4 ]	; 8  - 16km
      A.pcrng[2,*] = [ 0., 0.1 ]	; 16 - 28km
      END

   'TABCCL2F2' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'CCl!D2!NF!D2!N'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.logrng = [ 0.001, 1. ]
      A.vmrng = [ 0.0, 1.0 ]
      A.avrng = [ 0.4, 0.7 ]
      A.avgcolrng = [ 8.0, 12.0 ]
      A.ctfmt = '(f4.2)'
      A.altrng = [ 5., 40. ]		; plot bounds
      A.altpltrng = [7., 40.]		; min max for file read
      A.mnthrng    = [ 0., 0.6 ]			; monthly vmr plot
      A.colscl = 1.e-15
      A.colrng = [ 8., 12. ]
      A.slimid = 35
      A.molid = 32
      A.pcrng[0,*] = [ 5., 10. ]
      A.pcrng[1,*] = [ 1., 4. ]
      A.pcrng[2,*] = [ 0.2, 0.6 ]

      END

   'TABCCL3F' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'CCl!D3!NF!N'
      A.vmrscl = 1.0e12
      A.vmrunits = '[ppt]'
      A.logrng = [ 0.1, 500. ]
      A.vmrng = [ 1.0, 30 ]
      A.ctfmt = '(f5.1)'
      A.altrng = [ 0., 40. ]					; plot bounds
      A.altpltrng = [0., 40.]					; min max for file read
      A.avrng      = [ 150., 350. ]			; average trop range
      A.avgcolrng     = [ 3., 6. ]				; average trop range
      A.mnthrng    = [ 0., 300. ]			; monthly vmr plot
      A.colscl = 1.e-15
      A.colrng = [ 2., 7. ]
      A.slimid = 0
      A.molid = 33
      A.pcrng[0,*] = [ 2., 5. ]
      A.pcrng[1,*] = [ 0., 2. ]
      A.pcrng[2,*] = [ 0., 0.2 ]
      END


   'MLOCCL2F2' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'CCl!D2!NF!D2!N'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.logrng = [ 0.001, 10. ]
      A.vmrng = [ 0.0,1.0 ]
      A.avrng = [ 0.4, 0.8 ]
      A.avgcolrng = [ 8.0, 12.0 ]
      A.ctfmt = '(f4.2)'
      A.altrng = [ 5., 40. ]		; plot bounds
      A.altpltrng = [7., 40.]		; min max for file read
      A.colscl = 1.e-15
      A.colrng = [ 8., 14. ]
      A.slimid = 35
      A.molid = 32
      END

   'MLOCCL3F' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'CCl!D3!NF!N'
      A.vmrscl = 1.0e12
      A.vmrunits = '[ppt]'
      A.logrng = [ 0.1, 500. ]
      A.vmrng = [ 1.0, 30 ]
      A.ctfmt = '(f4.2)'
      A.altrng = [ 0., 40. ]		; plot bounds
      A.altpltrng = [0., 40.]		; min max for file read
      A.colscl = 1.e-15
      A.colrng = [ 1., 6. ]
      A.slimid = 0
      A.molid = 33
      A.pcrng[0,*] = [ 0., 6. ]
      A.pcrng[1,*] = [ 0., 2. ]
      A.pcrng[2,*] = [ 0., 0.5 ]
      END


   '13CH4' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = '!E13!NCH!D4!N'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.vmrng = [0.1, 5]
      A.logrng = [ 0.01, 100 ]
      A.ctfmt = '(f4.1)'
      A.altrng = [ 5., 40. ]		; plot bounds
      A.altpltrng = [7., 40.]		; min max for file read
      A.colscl = 1.0e-17
      A.colrng = [ 2., 5. ]
      A.slimid = 29
      A.molid = 6
      A.pcrng[0,*] = [ 0., 6. ]
      A.pcrng[1,*] = [ 0., 2. ]
      A.pcrng[2,*] = [ 0., 0.5 ]
      END

   'TABCH4' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol        = 'CH!D4!N'
      A.vmrscl      = 1.0e6
      A.vmrunits    = '[ppm]'
      A.vmrng       = [0.1, 3]
      A.logrng      = [ 0.01, 100 ]
      A.ctfmt       = '(f4.1)'
      A.altrng      = [ 5., 40. ]		; plot bounds
      A.altpltrng   = [7., 40.]		; min max for file read
      A.colscl      = 1.0e-19
      A.colrng      = [ 3., 4. ]
      A.mnthrng     = [0.0, 2.5]
      A.avgcolrng      = [ 3.4, 3.8 ]
      A.avrng       = [ 1.7, 2.0 ]
      A.vrngs[0,*]  = [ 1.5, 2.2 ]
      A.vrngs[1,*]  = [ 0.2, 2.0 ]
      A.vrngs[2,*]  = [ 0.1, 2.0 ]
      A.slimid      = 29
      A.molid       = 6
      A.pcrng[0,*]  = [ 2.0, 4.0 ]
      A.pcrng[1,*]  = [ 0.01, 1.0 ]
      A.pcrng[2,*]  = [ 0.01, .5 ]
      END

   'MLOCH4' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'CH!D4!N'
      A.vmrscl = 1.0e6
      A.vmrunits = '[ppm]'
      A.vmrng = [0.1, 5]
      A.logrng = [ 0.01, 100 ]
      A.ctfmt = '(f4.1)'
      A.altrng = [ 5., 40. ]		; plot bounds
      A.altpltrng = [7., 40.]		; min max for file read
      A.colscl = 1.0e-19
      A.colrng = [ 3., 4. ]
      A.mnthrng = [0.0, 2.5]
      A.avgcolrng     = [ 3.4, 3.8 ]
      A.avrng      = [ 1.7, 2.0 ]
      A.vrngs[0,*] = [ 1.5, 2.2 ]
      A.vrngs[1,*] = [ 0.2, 2.0 ]
      A.vrngs[2,*] = [ 0.1, 1.2 ]
      A.slimid = 29
      A.molid = 6
      A.pcrng[0,*] = [ 3.0, 4.0 ]
      A.pcrng[1,*] = [ 0.001, 0.2 ]
      A.pcrng[2,*] = [ 0.001, .03 ]
      END

   'MLOH2O' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'H!D2!NO'
      A.vmrscl = 1.0e6
      A.vmrunits = '[ppm]'
      A.logrng = [ 1.0, 1500 ]
      A.vmrng = [ 1.0, 30 ]
      A.ctfmt = '(f8.2)'
      A.altrng = [ 0., 20. ]		; plot bounds
      A.altpltrng = [0., 20.]		; min max for file read
      A.colscl = 1.
      A.colrng = [ 0., 0. ]
      A.slimid = 28
      A.molid = 1
      END

   'FL0H2O' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'H!D2!NO'
      A.vmrscl = 1.0e6
      A.vmrunits = '[ppm]'
      A.logrng = [ 1.0, 1500 ]
      A.vmrng = [ 1.0, 30 ]
      A.ctfmt = '(f8.2)'
      A.altrng = [ 0., 20. ]		; plot bounds
      A.altpltrng = [0., 20.]		; min max for file read
      A.colscl = 1.
      A.colrng = [ 0., 0. ]
      A.slimid = 28
      A.molid = 1
      END

   'TABH2O' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'H!D2!NO'
      A.vmrscl = 1.0e6
      A.vmrunits = '[ppm]'
      A.logrng = [ 0.01, 100 ]
      A.vmrng = [ 1.0, 30 ]
      A.ctfmt = '(f4.2)'
      A.altrng = [ 10., 40. ]		; plot bounds
      A.altpltrng = [13., 40.]		; min max for file read
      A.colscl = 1.
      A.colrng = [ 0., 0. ]
      A.slimid = 28
      A.molid = 1
      END

   'TABHCL' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'HCl'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.vmrng = [0,4]
      A.logrng = [0.001,10.]			; for A.mls log scale
      A.ctfmt = '(f4.1)'
      A.altrng = [ 0., 50. ]		; plot bounds
      A.altpltrng = [5., 45.]		; min max for file read
      A.colscl = 1.e-15
      A.colrng = [ 1., 10. ]
      A.slimid = 17

      A.pcrng[0,*] = [ 0., 1. ]		; 0  - 10km
      A.pcrng[1,*] = [ 0., 8.0 ]	; 10 - 19km
      A.pcrng[2,*] = [ 0., 4.0 ]	; 19 - 30km


      ; !!! check indexes below

      A.files[0] =	'MLS-Aura_L2GP-HCl_v01-51-c01_2005d063.he5'
      A.files[1] =	'MLS-Aura_L2GP-HCl_v01-51-c01_2005d066.he5'
      A.files[2] =	'MLS-Aura_L2GP-HCl_v01-51-c01_2005d068.he5'
      A.files[3] =	'MLS-Aura_L2GP-HCl_v01-51-c01_2005d071.he5'
      A.files[4] =	'MLS-Aura_L2GP-HCl_v01-51-c01_2005d074.he5'
      A.files[1] =	'MLS-Aura_L2GP-HCl_v01-51-c03_2005d078.he5'
      A.files[6] =	'MLS-Aura_L2GP-HCl_v01-51-c01_2005d080.he5'
      A.files[7] =	'MLS-Aura_L2GP-HCl_v01-51-c01_2005d081.he5'
      A.files[8] =	'MLS-Aura_L2GP-HCl_v01-51-c01_2005d084.he5'
      A.molid = 15
      END

   'MLOHCL' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'HCl'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.vmrng = [0,4]
      A.logrng = [0.001,10.]			; for A.mls log scale
      A.ctfmt = '(f4.1)'
      A.altrng = [ 0., 50. ]		; plot bounds
      A.altpltrng = [5., 45.]		; min max for file read
      A.colscl = 1.e-15
      A.colrng = [ 1., 10. ]
      A.slimid = 17

      A.pcrng[0,*] = [ 0., 1. ]		; 0  - 10km
      A.pcrng[1,*] = [ 0., 8.0 ]	; 10 - 19km
      A.pcrng[2,*] = [ 0., 4.0 ]	; 19 - 30km

      A.molid = 15
      END

   'TABHCN' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'HCN'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.vmrng = [0,4]
      A.logrng = [0.0001,1.]			; for A.mls log scale
      A.ctfmt = '(f4.2)'
      A.altrng = [ 0., 50. ]		; plot bounds
      A.altpltrng = [0., 50.]		; min max for file read
      A.colscl = 1.e-15
      A.colrng = [ 0., 12. ]
      A.slimid = -1
      A.molid = 28
      A.pcrng[0,*] = [ 0., 10.0 ]	   ; low alt panel
      A.pcrng[1,*] = [ 0., 4.0 ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.8 ]	   ; high alt panel
      END

  'MLOHCN' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'HCN'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.vmrng = [0,4]
      A.logrng = [0.0001,1.]			; for A.mls log scale
      A.ctfmt = '(f4.2)'
      A.altrng = [ 0., 50. ]		; plot bounds
      A.altpltrng = [0., 50.]		; min max for file read
      A.colscl = 1.e-15
      A.colrng = [ 0., 12. ]
      A.slimid = -1
      A.molid = 28
      A.pcrng[0,*] = [ 0., 10.0 ]	   ; low alt panel
      A.pcrng[1,*] = [ 0., 4.0 ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.8 ]	   ; high alt panel
      END

   'TABHF' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'HF'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.vmrng = [0.0,3.0]
      A.logrng = [0.0001,10.]			; for A.mls log scale
      A.ctfmt = '(f4.2)'
      A.altrng = [ 0., 60. ]	   	; plot bounds
      A.altpltrng = [0., 60.]		; min max for file read
      A.colscl = 1.e-14
      A.colrng = [ 10., 30. ]
      A.slimid = 39
      A.mls = 0
      A.molid = 14
      A.pcrng[0,*] = [ 0., 0.6 ]	; 0  - 8km
      A.pcrng[1,*] = [ 0., 15. ]	; 8  - 16km
      A.pcrng[2,*] = [ 5., 30. ]	; 16 - 28km

      END

   'MLOHF' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol       = 'HF'
      A.vmrscl     = 1.0e9
      A.vmrunits   = '[ppb]'
      A.vmrng      = [ 0.0, 1.8 ]
      A.logrng     = [ 0.0001,10. ]	; for A.mls log scale
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 0., 60. ]	   ; plot bounds
      A.altpltrng  = [ 0., 60. ]		; min max for file read
      A.colscl     = 1.e-14
      A.colrng     = [ 1., 12. ]
      A.slimid     = 39
      A.mls        = 0
      A.molid      = 14
      A.pcrng[0,*] = [ 0., 0.1 ]		; 0  - 8km
      A.pcrng[1,*] = [ 0., 0.4 ]		; 8  - 16km
      A.pcrng[2,*] = [ 0., 7. ]		; 16 - 28km

      A.vrngs[0,*] = [ 0., 0.002 ]		; low alt panel
      A.vrngs[1,*] = [ 0., 0.01 ]		; mid alt panel
      A.vrngs[2,*] = [ 0., 0.6 ]		; high alt panel

	   A.mnthrng    = [ 0., 1.8 ]
	   A.avgcolrng  = [ 4., 10. ]		; average column range
	   A.avrng      = [ 0., 0.002 ]	; average trop vmr range
      END


   'ACFHF' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'HF'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.vmrng = [0.0,3.0]
      A.logrng = [0.0001,10.]			; for A.mls log scale
      A.ctfmt = '(f4.2)'
      A.altrng = [ 0., 60. ]	   	; plot bounds
      A.altpltrng = [0., 60.]		; min max for file read
      A.colscl = 1.e-14
      A.colrng = [ 10., 30. ]
      A.slimid = 39
      A.mls = 0
      A.molid = 14
      A.pcrng[0,*] = [ 0., 0.6 ]	; 0  - 8km
      A.pcrng[1,*] = [ 0., 15. ]	; 8  - 16km
      A.pcrng[2,*] = [ 5., 30. ]	; 16 - 28km
      END


   'NO' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'NO'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.vmrng = [0,4]
      A.logrng = [0.1,100.]			; for A.mls log scale
      A.ctfmt = '(f4.2)'
      A.altrng = [ 10., 60. ]		; plot bounds
      A.altpltrng = [13., 56.]		; min max for file read
      A.colscl = 1.
      A.colrng = [ 0., 0. ]
      A.slimid = 5
      A.molid = 8
      END

   'ACFNO' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'NO!D2!N'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.vmrng = [0,4]
      A.logrng = [0.1,100.]			; for A.mls log scale
      A.ctfmt = '(f4.2)'
      A.altrng = [ 10., 60. ]		; plot bounds
      A.altpltrng = [13., 56.]		; min max for file read
      A.colscl = 1.
      A.colrng = [ 0., 0. ]
      A.slimid = 6
      A.molid = 10
      END



   'ACFNO2' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'NO!D2!N'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.vmrng = [0,4]
      A.logrng = [0.1,100.]			; for A.mls log scale
      A.ctfmt = '(f4.2)'
      A.altrng = [ 10., 60. ]		; plot bounds
      A.altpltrng = [13., 56.]		; min max for file read
      A.colscl = 1.
      A.colrng = [ 0., 0. ]
      A.slimid = 6
      A.molid = 10
      END


   'NO2' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'NO!D2!N'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.vmrng = [0,4]
      A.logrng = [0.1,100.]			; for A.mls log scale
      A.ctfmt = '(f4.2)'
      A.altrng = [ 10., 60. ]		; plot bounds
      A.altpltrng = [13., 56.]		; min max for file read
      A.colscl = 1.
      A.colrng = [ 0., 0. ]
      A.slimid = 6
      A.molid = 10
      END


   'TABOCS' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'OCS'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.vmrng = [0,4]
      A.logrng = [0.1,100.]			; for A.mls log scale
      A.ctfmt = '(f4.2)'
      A.altrng = [ 3., 40. ]		; plot bounds
      A.altpltrng = [0., 40.]		; min max for file read
      A.colscl = 1.0e-15
      A.colrng = [ 5., 15. ]
      A.slimid = -1
      A.molid = 19
      END

   'MLOOCS' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'OCS'
      A.vmrscl = 1.0e9
      A.vmrunits = '[ppb]'
      A.vmrng = [0,4]
      A.logrng = [0.1,100.]			; for A.mls log scale
      A.mnthrng = [ 0., 0.8]
      A.ctfmt = '(f4.2)'
      A.altrng = [ 3., 40. ]		; plot bounds
      A.altpltrng = [0., 40.]		; min max for file read
      A.colscl = 1.0e-15
      A.colrng = [ 5., 15. ]
      A.slimid = -1
      A.molid = 19
      END

   'ACFOCS' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      PRINT, '  UseMol : Found : ', site
      A.smol       = 'OCS'
      A.vmrscl     = 1.0e9
      A.vmrunits   = '[ppb]'
      A.mnthrng    = [0.,1.]
      A.avgcolrng  = [0., 3.]
      A.vmrng      = [0.,1.]
      A.logrng     = [0.1, 10.]		; for A.mls log scale
      A.ctfmt      = '(f4.2)'
      A.altrng     = [ 3., 40. ]		; plot bounds
      A.altpltrng  = [0., 40.]		; min max for file read
      A.colscl     = 1.0e-15
      A.colrng     = [ .1, 10. ]
      A.slimid     = -1
      A.molid      = 19
      A.pcrng[0,*] = [ 0., 2. ]		; low alt panel
      A.pcrng[1,*] = [ 0., 2. ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.5 ]		; high alt panel
      A.vrngs[0,*] = [ 0., 2. ]		; low alt panel
      A.vrngs[1,*] = [ 0., 1.0 ]		; mid alt panel
      A.vrngs[2,*] = [ 0., 1.0 ]		; high alt panel

      END


  'TABSO2' : BEGIN
      PRINT, '  UseMol : Found : ', mol
      A.smol = 'SO!D2!N'
      A.vmrscl = 1.0e12
      A.vmrunits = '[ppt]'
      A.logrng = [ 0.01, 100 ]
      A.vmrng = [ 0.1, 10 ]
      A.ctfmt = '(f4.2)'
      A.altrng = [ 10., 40. ]		; plot bounds
      A.altpltrng = [13., 40.]		; min max for file read
      A.colscl = 1.0e-14
      A.colrng = [ 0.0, 3. ]
      A.slimid = 28
      A.molid = 50
      A.pcrng[0,*] = [ 0., 0.5 ]	; low alt panel
      A.pcrng[1,*] = [ 0., 0.5 ]		; mid alt panel
      A.pcrng[2,*] = [ 0., 0.1 ]	; high alt panel
      END

   ELSE : BEGIN
      PRINT, 'No match in molecule case : ', sitemol
      STOP
      END

ENDCASE

RETURN
END
