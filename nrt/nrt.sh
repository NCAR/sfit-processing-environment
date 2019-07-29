#! /bin/sh
############################################################################
############################################################################
#
# Usage: nrt.sh
#
# - Run nrtPreProc.py      --> Pre=Processing
# - Run nrtLayer1.py       --> rapid delivery Analysis of CH4, CO and O3
# - Run nrtHDFUpload.py    --> rapid delivery gases HDF creation & upload to RD archive (NDACC)
#
# Options:
#
#
# Version History:
#       Created, June, 2019  Ivan Ortega (iortega@ucar.edu)
# pkill screen
#
# Log:
# Last Dates:  
#
# TAB - 20190701_20190710
# MLO - 20190701_20190710
# FL0 - 20190701_20190710
#
############################################################################
############################################################################
echo "Enter site, e.g., mlo:"
read site

echo "Enter Dates, e.g., 20190101_20190202:"
read dates

############################################################################
############################################################################

#------------------------
# Launch Pre-Processing program
#------------------------
echo 'Start nrt Pre-Processing...'
/usr/bin/screen -dmS nrtPre$site python /data/pbin/Dev_Ivan/nrt/nrtPreProc.py -s $site -d $dates
sleep 5
screen -ls

#------------------------
# Launch nrtLayer1 program for water vapor
#------------------------
echo 'Start nrt Analysis of water vapor...'
/usr/bin/screen -dmS nrtH2O$site python /data/pbin/Dev_Ivan/nrt/nrtLayer1.py -s $site -d $dates -g h2o
sleep 5
screen -ls

#------------------------
# Launch nrtLayer1 program for CO & HDF creation/upload
#------------------------
echo 'Start nrt Analysis of CO'
/usr/bin/screen -dmS nrtCO$site python /data/pbin/Dev_Ivan/nrt/nrtLayer1.py -s $site -d $dates -g co
sleep 5
screen -ls

echo 'Start nrt HDF Creation/Upload for CO'
/usr/bin/screen -dmS nrtCOhdf$site python /data/pbin/Dev_Ivan/nrt/nrtHDFUpload.py -s $site  -g co -d $dates -H -U -l
sleep 5
screen -ls

#------------------------
# Launch nrtLayer1 program for O3 & HDF creation/upload
#------------------------
echo 'Start nrt Analysis of O3'
/usr/bin/screen -dmS nrtO3$site python /data/pbin/Dev_Ivan/nrt/nrtLayer1.py -s $site -d $dates -g o3
sleep 5
screen -ls

echo 'Start nrt HDF Creation/Upload for O3'
/usr/bin/screen -dmS nrtO3hdf$site python /data/pbin/Dev_Ivan/nrt/nrtHDFUpload.py -s $site  -g o3 -d $dates -H -U -l
sleep 5
screen -ls

#------------------------
# Launch nrtLayer1 program for CH4
#------------------------
echo 'Start nrt Analysis of CH4'
/usr/bin/screen -dmS nrtCH4$site python /data/pbin/Dev_Ivan/nrt/nrtLayer1.py -s $site -d $dates -g ch4
sleep 5
screen -ls

echo 'Start nrt HDF Creation/Upload for CH4'
/usr/bin/screen -dmS nrtCH4hdf$site python /data/pbin/Dev_Ivan/nrt/nrtHDFUpload.py -s $site  -g ch4 -d $dates -H -U -l
sleep 5
screen -ls
