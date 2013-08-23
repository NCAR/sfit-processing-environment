PRO usesite, site, asite, Ag

  asite = { as,          $
         name     : '',  $
         cbtitle	: '',  $
         dbtitle	: '',  $
         prtitle	: '',  $
         sztitle	: '',  $
         rmtitle	: '',  $
         y1       : 0,   $
         y2       : 0,   $
         infodir  : '',  $
         strtmnth : 0,   $
         npage    : 0,   $
         lat      : 0.0, $
         lon      : 0.0, $
         alt      : 0.0, $
         troprng  : dblarr(2), $
         pcaltrng : dblarr(2,3) }

   site          = STRUPCASE( site )
   asite.name    = site
	asite.infodir = '/data/Campaign/' + strupcase(site) + '/'

   CASE( site ) OF

      'TAB' : BEGIN
			PRINT, '  Usesite : Setting time plot range to 1999 to 2012'
			asite.y1 = 1999
			asite.y2 = 2013
			asite.troprng = [ 0.0d0, 8.0d0 ]
			asite.cbtitle = 'NDACC / NCAR Thule, GR, FTS Total Column & Profile Retrieval Trends for ' + Ag.smol + Ag.vmrunits
			asite.dbtitle = 'NDACC / NCAR Thule, GR, FTS Total Column Retrieval for ' + Ag.smol + Ag.vmrunits
			asite.prtitle = 'NDACC / NCAR Thule, GR, FTS Profiles by DOY for ' + Ag.smol + Ag.vmrunits
			asite.sztitle = 'NDACC / NCAR Thule, GR, FTS Profiles by SZA for ' + Ag.smol + Ag.vmrunits
			asite.rmtitle = 'NDACC / NCAR Thule, GR, FTS Profiles by RMS for ' + Ag.smol + Ag.vmrunits
			asite.pcaltrng = [[ 0.0,  8.0 ], [  8.0, 20.0 ], [ 20.0, 40.0 ]]
			asite.strtmnth = 2
			asite.npage    = 1
			asite.lat      = 76.53
         asite.lon      = -68.74
         asite.alt      = 0.225
      END

      'MLO' : BEGIN
			PRINT, '  Usesite : Setting time plot range to 1995 to 2012'
			asite.y1 = 1995
			asite.y2 = 2012
			asite.troprng = [ 0.0d0, 17.0d0 ]
			asite.cbtitle = 'NDACC / NCAR MLO, FTS Total Column & Profile Retrieval Trends for ' + Ag.smol + Ag.vmrunits
			asite.dbtitle = 'NDACC / NCAR MLO, FTS Total Column Retrieval for ' + Ag.smol + Ag.vmrunits
			asite.prtitle = 'NDACC / NCAR MLO, FTS Profiles by DOY for ' + Ag.smol + Ag.vmrunits
			asite.sztitle = 'NDACC / NCAR MLO, FTS Profiles by SZA for ' + Ag.smol + Ag.vmrunits
			asite.rmtitle = 'NDACC / NCAR MLO, FTS Profiles by RMS for ' + Ag.smol + Ag.vmrunits
			asite.pcaltrng = [[ 0.0,  17.0 ], [  17.0, 26.0 ], [ 26.0, 40.0 ]]
			asite.strtmnth = 0
			asite.npage    = 2
			asite.lat      = 19.54
         asite.lon      = -155.57
         asite.alt      = 3.396

      END

      'ACF' : BEGIN
			PRINT, '  Usesite : Setting time plot range to 1975 to 2006'
			asite.y1 = 1975
			asite.y2 = 2006
			asite.infodir = '~/Programs/OTA/Analysis/results'
			asite.troprng = [ 0.0d0, 13.5d0 ]
			asite.cbtitle = 'NCAR Airborne FTS Total Column & Profile Retrieval Trends for ' + Ag.smol + Ag.vmrunits
			asite.dbtitle = 'NCAR Airborne FTS Total Column Retrieval for ' + Ag.smol + Ag.vmrunits
			asite.prtitle = 'NCAR Airborne FTS Profiles by DOY for ' + Ag.smol + Ag.vmrunits
			asite.sztitle = 'NCAR Airborne FTS Profiles by SZA for ' + Ag.smol + Ag.vmrunits
			asite.rmtitle = 'NCAR Airborne FTS Profiles by RMS for ' + Ag.smol + Ag.vmrunits
	 	   asite.pcaltrng = [[ 2.0, 16.0 ], [ 16.0, 24.0 ], [ 24.0, 40.0 ]]
			asite.strtmnth = 0
			asite.npage    = 2

 		END

      'FL0' : BEGIN
			PRINT, '  Usesite : Setting time plot range to 2008 to 2012'
			asite.y1 = 2008
			asite.y2 = 2012
			asite.troprng = [ 0.0d0, 12.0d0 ]
			asite.cbtitle = 'NCAR FL0, FTS Total Column & Profile Retrieval Trends for ' + Ag.smol + Ag.vmrunits
			asite.dbtitle = 'NCAR FL0, FTS Total Column Retrieval for ' + Ag.smol + Ag.vmrunits
			asite.prtitle = 'NCAR FL0, FTS Profiles by DOY for ' + Ag.smol + Ag.vmrunits
			asite.sztitle = 'NCAR FL0, FTS Profiles by SZA for ' + Ag.smol + Ag.vmrunits
			asite.rmtitle = 'NCAR FL0, FTS Profiles by RMS for ' + Ag.smol + Ag.vmrunits
			asite.pcaltrng = [[ 0.0,  12.0 ], [  12.0, 24.0 ], [ 24.0, 40.0 ]]
			asite.strtmnth = 0
			asite.npage    = 2
         asite.lat      = 40.038
         asite.lon      = -105.243
         asite.alt      = 1.612

      END
      ELSE : BEGIN
         PRINT, ' USESITE.PRO : Site not setup yet : ', site
         STOP
      END

   ENDCASE

RETURN

END
