#! /usr/bin/python2.7
#----------------------------------------------------------------------------------------
# Name:
#        WACCMptwMonthly.py
#
# Purpose:
#       
#
#
# External Subprocess Calls:
#	
#
# Notes:
#       1)
#			
#
#
# Version History:
#       Created, December, 2013  Eric Nussbaumer (ebaumer@ucar.edu)
#
#
# References:
#
#----------------------------------------------------------------------------------------

                                #-------------------------#
                                # Import Standard modules #
                                #-------------------------#



import datetime as dt
import numpy as np
import sys
import os
import matplotlib.pyplot as plt

#-------------------------#
# Define helper functions #
#-------------------------#

def ckFile(fName,logFlg=False,exit=False):
    '''Check if a file exists'''
    if not os.path.isfile(fName):
        print 'File %s does not exist' % (fName)
        if logFlg: logFlg.error('Unable to find file: %s' % fName)
        if exit: sys.exit()
        return False
    else: return True

def segmnt(seq,n):
    '''Yeilds successive n-sized segments from seq'''
    try:
        xrange
    except NameError:
        xrange = range
        
    for i in xrange(0,len(seq),n):
        yield seq[i:i+n] 
      



                            #----------------------------#
                            #                            #
                            #        --- Main---         #
                            #                            #
                            #----------------------------#    
                            
                            
def main():
    station    = 'Thule'
    inputDir   = '/data/Campaign/TAB/waccm/Thule.V6/'
    outputFile = '/data/Campaign/TAB/waccm/WACCM_pTW-meanV6-TEST.TAB'
    allFiles   = ['T.refprfs','P.refprfs','H2O.refprfs', 'CO.refprfs']
    typeList   = ['Temperature','Pressure','Water', 'CO']


    #-----------------
    # Open output file 
    #-----------------
    with open(outputFile,'w+') as fout:
        for indF,snglFile in enumerate(allFiles):
                       
            #-------------------------------------------
            # Open and read Temperature File (T.refprfs)
            #-------------------------------------------
            ckFile(inputDir+snglFile,exit=True)
            with open(inputDir+snglFile,'r') as fopen:
                lines = fopen.readlines()
                
            #-------------------------------------------
            # Get altitudes. These are reversed compared
            # to output so we must flip
            #-------------------------------------------
            alt    = np.array([float(x) for x in lines[1].strip().split()])
            alt[:] = np.flipud(alt) 
            
            #-------------------
            # Get list of months
            #-------------------
            months = np.array([int(line.strip().split()[0].split('/')[1]) for line in lines[2:]] )
            
            #-------------
            # Read in data
            #-------------
            data    = np.array( [ [ float(x) for x in row.strip().split()[1:]] for row in lines[2:]] )
            data[:] = np.fliplr(data)
            
            #----------------------
            # Find monthly averages
            #----------------------
            data_mean = np.zeros((12,len(alt)))
            for mnth in range(1,13):
                inds                = np.where(months == mnth)[0]
                data_mean[mnth-1,:] = np.mean(data[inds,:],axis=0)  # [month, altitude]
            
            data_mean = data_mean.T    # Transpose so that [altitude,month]
    
            #------------------------------------------------------
            # If this is the first loop write header to output file
            #------------------------------------------------------
            if indF == 0: fout.write('{:<5d}\n'.format(len(alt)))
            
            #------------------------------
            # Write out data to output file
            #------------------------------
            fout.write('Monthly mean '+typeList[indF]+' from WACCM V6 1980-2020 for '+station+'\n')
            strformat = [' {'+str(i)+':>10s}' for i in range(0,13)]
            strformat = ''.join(strformat).lstrip() + '\n'            
            fout.write(strformat.format('Altitude','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'))
            if indF == 0:   strformat = [' {'+str(i)+':>10.3f}' for i in range(0,13)]
            elif indF == 2: strformat = ['{0:10.3f}']+[' {'+str(i)+':>10.4E}' for i in range(1,13)]
            else:           strformat = ['{0:10.3f}']+[' {'+str(i)+':>10.3E}' for i in range(1,13)]
            strformat = ''.join(strformat).lstrip() + '\n'  
            for indW in range(0,len(alt)):
                fout.write(strformat.format(alt[indW],*data_mean[indW,:]))


            fig, ax = plt.subplots()

            with open('/data/Campaign/TAB/waccm/'+typeList[indF]+'_MonthlyMean.TAB','w') as Dout:

                for mnth in range(1,13):
                    Dout.write('Month '+ str(mnth)+' '+ typeList[indF]+' WACCM V4 CESM REFC1.3 1980-2020 CCMVal/CCMI, 2012\n')
                    d2p = data_mean[:, mnth-1]
                    d2p[:] = np.flipud(d2p) 

            
                    for row in segmnt(d2p, 5):
                        strformat = ','.join('{:>12.3E}' for i in row) + ', \n'
                        Dout.write(strformat.format(*row))


                    ax.plot(d2p, np.flipud(alt), marker ='o', markersize=6, label=str(mnth))

            ax.xaxis.set_tick_params(which='major',labelsize=12)
            ax.set_ylabel('Altitude [km]', fontsize=16)
            ax.set_xlabel('Mixing Ratio ' + typeList[indF], fontsize=16, color='b')
            ax.tick_params(axis='both', which='major', labelsize=14)
            ax.grid(True)
            ax.set_xscale('log')
            ax.legend(prop={'size':12})
            

            #-----------------------------------------------
            #plots
            #-----------------------------------------------
            
            
            fig.subplots_adjust(left = 0.12, bottom=0.1, top=0.9, right = 0.95)
          
            plt.show(block= False)
            user_input = raw_input('Press any key to exit >>> ')
            #sys.exit()   
             

    
if __name__ == "__main__":
    main()