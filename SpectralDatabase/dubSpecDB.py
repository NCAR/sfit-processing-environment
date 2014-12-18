#! /usr/local/python-2.7/bin/python
# Change the above line to point to the location of your python executable
#----------------------------------------------------------------------------------------
# Name:
#        dubSpecDB.py
#
# Purpose:
#       This program finds duplicate date and time entries in spectral database file
#
#
# Notes:
#
# Usage:
#
# Examples:
#
#
# Version History:
#       Created, May, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
#       Version history stored in git repository
#
#
# License:
#    Copyright (c) 2013-2014 NDACC/IRWG
#    This file is part of sfit4.
#
#    sfit4 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    sfit4 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with sfit4.  If not, see <http://www.gnu.org/licenses/>
#
#----------------------------------------------------------------------------------------


                            #-------------------------#
                            # Import Standard modules #
                            #-------------------------#

import sfitClasses as sc
import datetime    as dt
import itertools   as it
from collections import Counter

fname = '/Volumes/data/Campaign/MLO/Spectral_DB/HRspDB_mlo_1995_2012.dat'

#--------------------------
# Read in Spectral Database
#--------------------------
dbData = sc.DbInputFile(fname)
dbData.getInputs()

dates = [dt.datetime(int(str(int(d))[0:4]),int(str(int(d))[4:6]),int(str(int(d))[6:]),int(t[0:2]),int(t[3:5]),int(t[6:])) for (d,t) in it.izip(dbData.dbInputs['Date'],dbData.dbInputs['Time'])]

dDates = [k for k,v in Counter(dates).items() if v>1]

if not dDates: 
    print 'No duplicates found!!!'

else:
    for val in dDates:
        print 'Duplicate dates = {}'.format(val)

