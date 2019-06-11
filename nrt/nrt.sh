#! /bin/sh
############################################################################
############################################################################
#
# Usage: nrt.sh
#
# - Run nrtPreProc.py.
# - Run nrtLayer1.py for rapid delivery gases
#
# Options:
#
#
# Version History:
#       Created, June, 2019  Ivan Ortega (iortega@ucar.edu)
#
############################################################################
############################################################################

echo "Enter Dates, e.g., 20190101_20190202:"
read dates

echo "Enter site, e.g., mlo:"
read site

############################################################################
############################################################################

#------------------------
# Launch Pre-Processing program
#------------------------
#echo 'Start nrt Pre-Processing...'
#/usr/bin/screen -dmS nrtPre$site python /data/pbin/Dev_Ivan/nrtAnalysis/nrtPreProc.py -s $site -d $dates
#sleep 10
#screen -ls

#------------------------
# Launch nrtLayer1 program for water vapor
#------------------------
echo 'Start nrt Analysis of water vapor...'
/usr/bin/screen -dmS nrtH2O$site python /data/pbin/Dev_Ivan/nrt/nrtLayer1.py -s $site -d $dates -g h2o
sleep 5
screen -ls

#------------------------
# Launch nrtLayer1 program for CO
#------------------------
echo 'Start nrt Analysis of CO'
/usr/bin/screen -dmS nrtCO$site python /data/pbin/Dev_Ivan/nrt/nrtLayer1.py -s $site -d $dates -g co
sleep 5
screen -ls

#------------------------
# Launch nrtLayer1 program for CO
#------------------------
echo 'Start nrt Analysis of O3'
/usr/bin/screen -dmS nrtO3$site python /data/pbin/Dev_Ivan/nrt/nrtLayer1.py -s $site -d $dates -g o3
sleep 5
screen -ls

#------------------------
# Launch nrtLayer1 program for CO
#------------------------
echo 'Start nrt Analysis of CH4'
/usr/bin/screen -dmS nrtCH4$site python /data/pbin/Dev_Ivan/nrt/nrtLayer1.py -s $site -d $dates -g ch4
sleep 5
screen -ls




