#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import *
import os,pickle,h5py,matplotlib
try: #check if display is set...
 os.environ['DISPLAY']
except:
  matplotlib.use('PDF') #this ensures no display is needed for plot creation, output is set to pdf, vectorial is better
import pylab
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FormatStrFormatter
from matplotlib.backends.backend_pdf import PdfPages #to save multiple pages in 1 pdf...
from scipy.interpolate import interp1d
import datetime
import logging
logformat='%(asctime)s %(name)s %(levelname)-8s %(message)s'
logtfmt='%y-%m-%d %H:%M:%S'
logging.basicConfig(level=logging.INFO,format=logformat,datefmt=logtfmt)
rootlogger=logging.getLogger(__name__)


#labels as they appear in kb files
Kb_labels_orig = ['TEMPERAT','SolLnShft','SolLnStrn','SPhsErr','IWNumShft','DWNumShft','SZA','LineInt','LineTAir','LinePAir','BckGrdSlp','BckGrdCur','EmpApdFcn','EmpPhsFnc','FOV','OPD','ZeroLev']
#labels as they appear in sb file
Kb_labels = ['temperature', 'solshft','solstrnth','phase','wshift','dwshift','sza','lineInt','lineTAir','linePAir','slope','curvature','apod_fcn','phase_fcn','omega','max_opd','zshift'] 
# Sb labels that are calculated per microwindow
Sb_labels_permw=['SPhsErr','FOV','OPD','BckGrdSlp','BckGrdCur']
#maps Kb labels to Sb labels 
Sb_paramMap=lambda paramName: Kb_labels[Kb_labels_orig.index(paramName)];
autopressureticks=[0.001,0.01,.1,1.,5.,10.,20.,50.,100.,200.,500.,1000.,2000.,5000.,1e4]
colorcycle=['r', 'b', 'g', 'm', 'y', 'k'];lc=len(colorcycle)
titlepad=1.02 #distance between title and frame of plot



def create_sfit4_retrievalplot(ctl,retdata={},fontsize=8,title='Spectrum name',plots=['sa','avk','gkb','std'],pdf='',logger=rootlogger):
  """Computes the error budget for a given ctlsb instance and a dict with retrieval data (e.g. as it is stored in the HDF file)

  Input argument: ctl, retdata (a dict or a group in a retrieval hdf file)

  Optional key arguments::
    fontsize: 8
    title: 'Spectrum name'
    plots='sa','avk','gkb','std' (list of plots to make, default is all, plots of retrieval species are always made)
    pdf: '' file in which the pdf plots should be saved, if empty show the plots;;"""
  #color definition
  obsspeccolor='k';synspeccolor='r';apcolor='k';retcolor='r'
  #init
  logger=logging.getLogger(logger.name+'.create_sfit4_retrievalplot')
  figidx=[];pdfmarks=[]
  if isinstance(retdata,h5py.Group): retdata=hdf5todict(retdata,logger=logger)
  requiredkeys=['shat','k','seinv','s/grid','sa','pbp/dims','summary/FITRMS','APRprofs','attr']+['s/%s'%mol for mol in ctl['gas.profile.list']+ctl['gas.column.list']]
  if any([k not in retdata for k in requiredkeys]): logger.error('Not all required keys available in retrieval data');return; 
  grid=retdata['s/grid']*1e-3
  if 'g' not in retdata: retdata['g']=retdata['shat'].dot(retdata['k'].T).dot(diag(retdata['seinv']))
  #Profile and MW plot
  for mol in ctl['gas.profile.list']:
    logger.info('Creating plots for %s'%mol)
    try: zmax=ctl['option.plot.%s.upperlimit'%mol]
    except KeyError: 
      try: zmax=retdata[mol]['zmax'] #try defaultsettings
      except KeyError: zmax=max(grid)
    try: zmin=ctl['option.plot.%s.lowerlimit'%mol]
    except KeyError: zmin=min(grid)
    fig=plt.figure();figidx.append(plt.gcf().number);pdfmarks.append('[/Title (%s) /Page %d /OUT pdfmark'%(title,len(figidx)))#we add the number of subpages at the end
    listofaxes=[]
    ax=plt.axes([.73,.05,.25,.9]) #left,bottum,width,heigth
    listofaxes.append(ax) #TODO implement cut flag for plots
    #uncertainties + profile apriori
    appro=retdata['APRprofs'][:,where(retdata['attr']['APRprofs']['columns']==mol)[0]].squeeze()*1e6
    try:
      std=sqrt(diag(retdata['sb/uncertainties/%s/random'%mol]))*1e6
      ax.errorbar(appro,grid+zmax/3e2,fmt=None,xerr=std,ecolor=apcolor,label='_nolegend_')
    except KeyError: pass
    try:
      std=sqrt(diag(retdata['sb/uncertainties/%s/systematic'%mol]))*1e6
      ax.fill_betweenx(grid,appro-std,appro+std,alpha=.5,color=apcolor)
    except KeyError: pass
    #uncertainties + profile retrieved
    try: 
      std=sqrt(diag(retdata['s/uncertainties/%s/random'%mol]))*1e6
      ax.errorbar(retdata['s/%s'%mol]*1e6,grid,fmt=None,xerr=std,ecolor=retcolor,label='_nolegend_')
    except KeyError: pass
    try:
      std=sqrt(diag(retdata['s/uncertainties/%s/systematic'%mol]))*1e6
      ax.fill_betweenx(grid,retdata['s/%s'%mol]*1e6-std,retdata['s/%s'%mol]*1e6+std,alpha=.2,color=retcolor)
    except KeyError: pass
    ax.plot(retdata['s/%s'%mol]*1e6,grid,label='retrieved %s'%mol,color=retcolor)
    ax.plot(appro,grid,label='apriori %s'%mol,color=apcolor)
    ax.set_ylim(zmin,zmax)
    ax.set_xlabel('VMR [ppmv]');ax.set_ylabel('Height [km]')
    ax.xaxis.set_major_locator(MaxNLocator(nbins = 6))
    try: spec=[line for line in ctl['option.hbin.input'].split('\n') if line.find(mol)>-1][0]
    except (KeyError,IndexError): spec=''
    #spec=spec.replace('_','\_') #if text is formatted with latex
    ax.legend(loc='best',prop={'size':fontsize})
    w=.6/float(retdata['pbp/dims'][0]);l=.06
    for i,j in enumerate(ctl['band']):
      if i==0: 
	ax=plt.axes([l+i*w,.05,w-.01,.72])
	ax.set_ylabel('Transmission');ax.set_xlabel('Wavenumber [$cm^{-1}$]')
      else: ax=plt.axes([l+i*w,.05,w-.01,.72],sharey=listofaxes[1])
      if mol in ctl['band.%s.gasb'%j]: [q.set_linewidth(1.5) for q in ax.spines.itervalues()]
      listofaxes.append(ax)
      ax.locator_params(tight=True)
      ax.plot(retdata['pbp/mw/%d/wavenumber'%i],retdata['pbp/mw/%d/observed'%i],label='obs',color=obsspeccolor,linewidth=.5)
      ax.plot(retdata['pbp/mw/%d/wavenumber'%i],retdata['pbp/mw/%d/fitted'%i],label='calc',color=synspeccolor,linewidth=.5)
      ax.set_title(' '.join(ctl['band.%s.gasb'%j]),fontsize=fontsize-2)
      if len(ctl['band'])>1: ax.xaxis.set_major_locator(MaxNLocator(nbins = 3, prune = 'both') )#ax.xaxis.set_ticks(ax.get_xticks()[array([0,-1])]); #plt.setp(ax.get_xticklabels(),rotation=30,ha='right')
      if i==0: 
	ax.legend(loc='best',prop={'size':fontsize})
	ax=plt.axes([l+i*w,.8,w-.01,.15],sharex=listofaxes[-1])
      else: ax=plt.axes([l+i*w,.8,w-.01,.15],sharex=listofaxes[-1],sharey=listofaxes[2]);
      listofaxes.append(ax)
      ax.plot(retdata['pbp/mw/%d/wavenumber'%i],retdata['pbp/mw/%d/difference'%i],'k');
      ax.xaxis.set_visible(False) #ax.xaxis.set_ticks_position('top')
    for i,ax in enumerate(listofaxes):
      if i>2: plt.setp(ax.get_yticklabels(), visible=False)
      plt.setp(ax.get_xticklabels(),fontsize=fontsize-2)
      plt.setp(ax.get_yticklabels(),fontsize=fontsize-2)
      plt.setp(ax.xaxis.label,fontsize=fontsize);plt.setp(ax.yaxis.label,fontsize=fontsize)
      ax.xaxis.labelpad = 1; ax.yaxis.labelpad = 1
      ax.xaxis.set_major_formatter(FormatStrFormatter('%G'))
    ax=plt.axes([l,.96,.8,.05])
    ax.axis('off')
    ax.text(0,0,title+' %s $\quad$ rTC: %6.4emolec/$cm^2$($\pm$%4.1f%%$\pm$%4.1f%%) $\quad$ RMS:%6.5f $\quad$ Conv: \
%s $\quad$\n %s %s'%(mol,retdata['summary/%s/ret_column'%mol],retdata['TCerror/%s/systematic'%mol],retdata['TCerror/%s/random'%mol],\
	retdata['summary/FITRMS'],retdata['summary/CONVERGED'],spec,retdata['summary/header']),fontsize=fontsize-1,horizontalalignment='left')
    molcols=where(retdata['attr']['k']['columns']==mol)
    avk=retdata['g'].dot(retdata['k'])[molcols[0],:][:,molcols[0]]
    #AVK plot
    if 'avk' in plots:
      fig,ax=plt.subplots();figidx.append(plt.gcf().number);pdfmarks.append('[/Title (AVK %s) /Page %d /OUT pdfmark'%(mol,len(figidx))) 
      plotz=array([i for i in grid if i<=zmax and i>=zmin])
      iM=where(grid==min(plotz))[0][0]
      im=where(grid==max(plotz))[0][0]
      if iM<len(grid)-1: iM+=1
      plotz=grid[im:iM+1]
      plotavk=avk[im:iM+1,im:iM+1]
      plot_avk(ax,plotz,plotavk,ylabelstring='Height [km]',
	  titlestring=[title + ' %s AVK [VMR/VMR rel. to apriori] \n DOF=%4.3f'%(mol,trace(avk)),fontsize])
      sc=10.; #scale factor...
      sensitivity=sum(avk,1)/sc
      ax.plot(sensitivity[im:iM+1],plotz,'--',label='Sensitivity (sum of AVK rows, scaled with 1/%3.1f)'%(sc))
      ax.legend(prop={'size':8},loc='best');
    if 'sa' in plots:
      fig,ax=plt.subplots();figidx.append(plt.gcf().number);pdfmarks.append('[/Title (Sa matrix %s) /Page %d /OUT pdfmark'%(mol,len(figidx)))
      molcols=where(retdata['attr']['sa']['columns']==mol)[0]
      samatrix=retdata['sa'][molcols,:][:,molcols][im:iM+1,im:iM+1]
      plot_matrix(ax,matrix=samatrix,grid=plotz,slabelstring='Height [km]',tlabelstring='Height [km]',
	cnorm='symmetric',colormap='seismic',titlestring=['%s %s Regularization matrix'%(title,mol),fontsize])
  #Column retrieval plots
  fig=plt.figure();figidx.append(plt.gcf().number);pdfmarks.append('[/Title (Column retrievals) /Page %d /OUT pdfmark'%len(figidx))
  listofaxes=[];l=0.06;
  if (len(ctl['gas.column.list'])+1)/4>0: w=(1.-l)/4
  else: w=0
  j=0
  for mol in ctl['gas.column.list']+['airmass']:
    if j>0 and j%4==0: fig=plt.figure();figidx.append(plt.gcf().number);j=0 #no pdf mark in this case
    logger.info('Creating plots for %s'%mol)
    if mol!='airmass':
      try: zmax=ctl['option.plot.%s.upperlimit'%mol]
      except KeyError: 
	try: zmax=retdata[mol]['zmax'] #try defaultsettings
	except KeyError: zmax=max(grid)
      try: zmin=ctl['option.plot.%s.lowerlimit'%mol]
      except KeyError: zmin=min(grid)
      ax=plt.axes([l+j*w,0.1,w-l,.78]) #left,bottum,width,heigth
      listofaxes.append(ax) # TODO implement cut flag for plots
      ax.plot(retdata['s/%s'%mol]*1e6,grid,label='retrieved %s'%mol,color=retcolor)
      ax.plot(retdata['APRprofs'][:,where(retdata['attr']['APRprofs']['columns']==mol)[0]]*1e6,grid,label='apriori %s'%mol,color=apcolor)
      ax.set_ylim(zmin,zmax)
      ax.set_xlabel('VMR [ppmv]');ax.set_ylabel('Height [km]')
      ax.xaxis.set_major_locator(MaxNLocator(nbins = 6))
      try: spec=[line for line in ctl['option.hbin.input'].split('\n') if line.find(mol)>-1][0]
      except (KeyError,IndexError): spec=''
      spec=spec.replace('_','\_')#if text is formatted with latex
      axt=plt.axes([j*w+w,.89,0,.5]);axt.axis('off');axt.text(0,0,'%s rTC: %6.4emolec/$cm^2$\n($\pm$%3.1f%%$\pm$%3.1f%%)\naTC: %6.4emolec/$cm^2$\n%s'%(mol,\
	retdata['summary/%s/ret_column'%mol],retdata['TCerror/%s/systematic'%mol],retdata['TCerror/%s/random'%mol],retdata['summary/%s/apr_column'%mol],spec),
	fontsize=fontsize-2,verticalalignment='bottom',horizontalalignment='right')
      ax.legend(loc='best',prop={'size':fontsize-2})
    else: 
      ax=plt.axes([l+j*w,0.1,w-l,.78]) #left,bottum,width,heigth
      listofaxes.append(ax);
      ax.plot(retdata['s/airmass']*1e-24*1e-4,grid,color='k');ax.set_xlabel('Ymolec/$cm^2$ (Y=$10^{24}$)');ax.set_ylabel('Height [km]')
      ax.xaxis.set_major_locator(MaxNLocator(nbins = 6));ax.set_ylim(0,20)
      axt=plt.axes([j*w+w,.89,0,.5]);axt.axis('off');axt.text(0,0,'%s TC: %6emolec/$m^2$\n%s'%(mol,retdata['s/airmass'].sum(),spec),
	fontsize=fontsize-2,verticalalignment='bottom',horizontalalignment='right')
    if j==0:
      ax=plt.axes([l,.97,.85,.05])
      ax.axis('off')
      ax.text(0,0,title+' column retrievals for %s'%(' '.join(ctl['gas.column.list'])),fontsize=fontsize-1,horizontalalignment='left')  
    j+=1
  for i,ax in enumerate(listofaxes):
    plt.setp(ax.get_xticklabels(),fontsize=fontsize-2)
    plt.setp(ax.get_yticklabels(),fontsize=fontsize-2)
    plt.setp(ax.xaxis.label,fontsize=fontsize);plt.setp(ax.yaxis.label,fontsize=fontsize)
    ax.xaxis.labelpad = 1; ax.yaxis.labelpad = 1
    ax.xaxis.set_major_formatter(FormatStrFormatter('%G'))
  listofaxes=[]
  #Error contribution plot
  if ctl['kb'] and 'GKb' in retdata and 'gkb' in plots:
    for mol in ctl['gas.profile.list']:
      logger.info('Creating error contribution plots for %s'%mol)
      proidx=where(retdata['attr']['k']['columns']==mol)[0] #get profile idx out of the full state vector
      gkb=retdata['GKb']
      tcols=where(prod([retdata['attr']['GKb']['columns']!=sp for sp in ['TEMPERAT']+ctl['kb.profile.gas']],0))[0]
      fig,ax=plt.subplots();figidx.append(plt.gcf().number);pdfmarks.append('[/Title (Scalar errors) /Page %d /OUT pdfmark'%len(figidx))
      listofaxes.append(ax)
      plot_matrix(ax,gkb[proidx,:][:,tcols],gridt=grid,colormap='seismic',
	  shading='flat',cnorm='symmetric',sticks=retdata['attr']['GKb']['columns'][tcols],
	  titlestring=[title+' Scalar error contributions for profile retrieved %s'%(mol),fontsize],tlabelstring='Height [km]')
      for sp in ['TEMPERAT']+ctl['kb.profile.gas']:
	tcols=where(retdata['attr']['GKb']['columns']==sp)[0]
	if len(tcols):
	  fig,ax=plt.subplots();figidx.append(plt.gcf().number);pdfmarks.append('[/Title (%s error) /Page %d /OUT pdfmark'%(sp,len(figidx)))
	  listofaxes.append(ax)
	  plot_matrix(ax,gkb[proidx,:][:,tcols],grid=grid,colormap='seismic',
	  shading='flat',cnorm='symmetric',titlestring=[title+' %s profile error contribution for %s'%(sp,mol),fontsize],
	  tlabelstring='Height [km]',slabelstring='Height [km]')
  if 'std' in plots:
    for mol in ctl['gas.profile.list']:
      logger.info('Creating STD error contribution plots for %s'%mol)
      if 'STDerror' in retdata:
	fig,axtuple=plt.subplots(1,2,sharex=True,sharey=True);figidx.append(plt.gcf().number);pdfmarks.append('[/Title (%s error) /Page %d /OUT pdfmark'%('STD overview',len(figidx)))
	for i,ErrType in enumerate(['random','systematic']):
	  ax=axtuple[i]; listofaxes.append(ax)
	  for ErrLabel in [k for k in retdata['STDerror'] if k.find(ErrType)>-1 and k.find(mol)>-1]:
	    if ErrLabel.split('/')[1]!=ErrLabel.split('/')[1].lower(): ls='--'
	    else: ls='-'
	    ax.plot(retdata['STDerror'][ErrLabel]*100,retdata['s/grid']*1e-3,ls=ls,label='/'.join(ErrLabel.split('/')[1:]))
	    if i==0: ax.set_ylabel('Height [km]')
	    ax.set_xlabel('STD in [$\%$]');ax.set_xscale('log')
	    ax.set_title('%s: Overview of %s contributions'%(mol,ErrType),fontsize=fontsize)
	    ax.legend(loc='best',fontsize=fontsize-2,handlelength=4)
  for i,ax in enumerate(listofaxes):
    plt.setp(ax.xaxis.label,fontsize=fontsize);plt.setp(ax.yaxis.label,fontsize=fontsize)
    ax.xaxis.labelpad = 1; ax.yaxis.labelpad = 1
  logger.info('Saving/showing plots')
  pdfmarks[0]=pdfmarks[0].replace('[','[/Count -%s '%(len(pdfmarks)-1)) #add the chapter/subsection marks...
  norsplotsetup(usetex=False)
  with open(os.path.join(os.path.dirname(pdf),'pdfmarks'),'w') as bm: bm.write('\n'.join(pdfmarks))
  if pdf!='': finalizefig(figidx=figidx,pdf=pdf)
  else: finalizefig(figidx=figidx)
  return;

def expand_dict(d,meta='attr'):
  """Expands a dict as a 1-depth dict (i.e. values are not dicts) with concatenated keys '/'. The meta='attr' keywords filters out subdicts with key meta, and constructs 1 flattened dict"""
  dd=dict(d);attr={}
  if meta in dd: attr=d[meta];del dd[meta]
  while any(array(map(type,dd.values()))==dict):
    for k,v in dict(dd).items():
      if type(v)==dict:
	try: localattr=v[meta]; del v[meta];
	except KeyError: localattr={}
	if k in attr: attr[k].update(localattr)
	else: attr[k]=localattr
	for kk,vv in v.items():
	  dd.update({'/'.join([str(k),str(kk)]):vv});
	  if kk in attr[k]: attr.update({'/'.join([str(k),str(kk)]):attr[k][kk]})
	del dd[k];del attr[k] 
  return dd,attr;

def create_sfit4_retrievalsummary(ctl='sfit4.ctl',logger=rootlogger):
  """Creates plots/hdf for an individual retrieval. The function assumes all requiered files exist (retrieve4 guaranties this).

  Input argument: ctl"""
  if not logger: logger=rootlogger #for multiprocessing
  logger=logging.getLogger(logger.name+'.create_sfit4_retrievalsummary')
  cwd=os.getcwd()
  retdata={'attr':{}}
  if type(ctl)==str: os.chdir(os.path.dirname(ctl));ctl=read_dictfile(ctl,sfit4=True)
  octl,rctl=extract_dict(ctl,'option')
  retdata['sfit4.ctl']=array(print_dictfile(rctl).split('\n'))
  ctl=trim_dict(rctl);octl=trim_dict(octl) #remove the line numbers from the ctl dict...
  filesrequired=['ak_matrix','pbpfile','statevec','summary','shat_matrix','seinv_vector','k_matrix']
  if ctl['kb']: filesrequired.append('kb_matrix')
  for f in filesrequired:
    if not ctl.has_key('file.out.'+f): logger.error('Not all file.out.xxx determined'); return {}
    if not os.path.isfile(ctl['file.out.'+f]): logger.error('File %s does not exist'%ctl['file.out.'+f]); return {}
  #Read and save the summary file
  retdata['summary']=read_summary(ctl['file.out.summary'])
  s=read_statevec(ctl['file.out.statevec'])
  ak=read_output(ctl['file.out.ak_matrix'])
  pbp=read_pbpfile(ctl['file.out.pbpfile'])
  retdata['pbp']=pbp
  if s=={} or ak=={} or pbp=={}: logger.error('empty statevec,ak_matrix or ppbfile'); return {}
  target=ak['attr']['target']
  retdata['AVKtarget']=ak['data'];retdata['attr']['AVKtarget']=ak['attr'];retdata['attr']['AVKtarget'].update({'unit':'relative to the apriori profile'})
  vmrtable=read_output(ctl['file.out.aprprofiles'])
  #change the z(boundaries) and zbar(midpoints) with the data in the station.layers file -> higher precision
  grid=read_stationlayers(ctl['file.in.stalayers'])
  cl=vmrtable['attr']['columns'];idx=where((cl!='AIRMASS')*(cl!='Z'))[0]
  vmrtable['data'][:,where(cl=='ZBAR')[0]]=grid[:-1,-1:]
  am=vmrtable['data'][:,where(cl=='AIRMASS')[0]].squeeze()
  retdata['APRprofs']=vmrtable['data'][:,idx];retdata['attr']['APRprofs']={'columns':vmrtable['attr']['columns'][idx],'unit':' Z[km], T[K], P[hPa],VMR[ppv]'}
  retdata['params']=s['params'];retdata['attr']['params']={'columns':s['paramnames']}
  for mol in ctl['gas.profile.list']+ctl['gas.column.list']:
    retdata['s/%s'%(mol)]=s[mol]['ret']['pro'];retdata['attr']['s/%s'%(mol)]={'unit':'ppv'}
  #copy the grid,boundaries and airmass in s variables ...
  retdata['s/grid']=grid[:-1,-1]*1e3;retdata['attr']['s/grid']={'unit':'m','note':'Retrieval grid: layer midpoints'}
  retdata['s/gridboundaries']=upboundary(grid[::-1,1])*1e3;retdata['attr']['s/gridboundaries']={'unit':'m','note':'Retrieval grid: layer boundaries'}
  retdata['s/airmass']=am*1e4;retdata['attr']['s/airmass']={'unit':'molec/m**2'}
  if os.path.isfile('sfit4.dtl'):
    with open('sfit4.dtl','r') as fid: dtl=fid.readlines()
    retdata['sfit4.dtl']=array([l.strip('\n') for l in dtl]);
  if 'option.isotope.intput' in octl: retdata['isotope.intput']=array(print_isodat(octl['option.isotope.input']).split('\n'))
  if 'option.barcos' in octl: retdata['barcos']=octl['option.barcos']
  if 'option.mtime' in octl: retdata['mtime']=octl['option.mtime']
  if 'option.sb' in octl: retdata['sb']=dict(octl['option.sb']) #contains the Sb covariances...
  sh=read_output(ctl['file.out.shat_matrix'])
  retdata['shat']=sh['data'];retdata['attr']['shat']=sh['attr'];retdata['attr']['shat'].update({'unit':'in VMR relative to the apriori'})
  seinv=read_output(ctl['file.out.seinv_vector'])
  retdata['seinv']=seinv['data'].squeeze();retdata['attr']['seinv']={'unit':'Normalized to ... TODO '}
  k=read_output(ctl['file.out.k_matrix'])
  retdata['k']=k['data'];retdata['attr']['k']=k['attr'];retdata['attr']['k'].update({'unit':'in sfit2 units: source is VMR rel. to\
 apriori, source is normalized to ymeasmax'})
  if any([m=={} for m in [k,sh,seinv]]): logger.error('Could not compute the G matrix for this retrieval %s %s %s'%(sh,seinv,k)) 
  retdata['g']=retdata['shat'].dot(retdata['k'].T).dot(diag(retdata['seinv']))
  sa=read_output(ctl['file.out.sa_matrix'])
  retdata['sa']=sa['data'];retdata['attr']['sa']=sa['attr']
  if ctl['kb']:
    kb=read_output(ctl['file.out.kb_matrix'])
    gkb=retdata['g'].dot(kb['data'])
    #attach the molecule to the column headers
    if len(ctl['kb.line.gas']):
      logger.debug('Found spec database gases %s'%ctl['kb.line.gas'])
      for soort in ['Int','TAir','PAir']:
	dumidx=where(kb['attr']['columns']=='Line%s'%soort)[0];
	for i in range(len(dumidx)): kb['attr']['columns'][dumidx[i]]='Line%s.%s'%(soort,ctl['kb.line.gas'][i])
    #attach the mw to the column numbers
    for kbkey in ['ZeroLev']+Sb_labels_permw:
      mws = []
      if kbkey=='ZeroLev': [mws.append(int(k)) for k in ctl['band'] if not ctl['band.%d.%s'%(k,Sb_paramMap(kbkey))]]        # only include bands where zshift is NOT retrieved
      else: mws=ctl['band']
      dumidx=where(kb['attr']['columns']==kbkey)[0];
      for i,j in enumerate(dumidx): kb['attr']['columns'][j]='%s.%s'%(kbkey,mws[i])
    retdata['GKb']=gkb;retdata['attr']['GKb']={'unit':'TODO','columns':kb['attr']['columns'],'rows':'sfit state vector'}
  retdata,attr=expand_dict(retdata)
  retdata['attr']=attr
  os.chdir(cwd)
  return retdata;

def str2number(di):
  """Converts a string, list of strings or the string values of a dict to int,float or boolean"""
  if type(di)==dict:
    for k in di:
      try: di[k]=int(di[k])
      except ValueError:
	try: di[k]=float(di[k])
	except ValueError: pass
      if di[k]=='T' or di[k]=='True': di[k]=True
      if di[k]=='F' or di[k]=='False': di[k]=False
  elif type(di)==str:
    try: di=int(di)
    except ValueError:
      try: di=float(di)
      except ValueError: pass
    if di=='T' or di=='True': di=True
    if di=='F' or di=='False': di=False
  elif type(di)==list:
    for k,o in enumerate(di):
      try: di[k]=int(di[k])
      except ValueError:
	try: di[k]=float(di[k])
	except ValueError: pass
      if di[k]=='T' or di[k]=='True': di[k]=True
      if di[k]=='F' or di[k]=='False': di[k]=False
  return di;

def hdf5todict(grobj,rootkey='',logger=rootlogger):
  """Loads the contents of a h5py group object into a dict. Attributes are stored under key attr, and has the same keys as the data


  Optional key argument: rootkey='', inserts a string before the keys: rootkey/key"""
  logger=logging.getLogger(logger.name+'.hdf5todict')
  if not isinstance(grobj,h5py.Group):logger.error('Provide a h5py group instance');return {};
  fn=grobj.file.filename+grobj.name;fn=fn.rstrip('/');logger.debug('Group name: %s'%fn)
  out={};attr={}
  datlist=[]

def trim_dict(ctl,root=''):
  """Removes the line number information from a configuartion dict

  Input argument: a dict with values tuples (data,linenumber)

  Optional key arguments: root='' remove this string from the keys (from the beginning)"""
  nctl={}
  for key in ctl: nctl[key.replace(root,'')]=ctl[key][0]
  return nctl;

def read_pbpfile(f,quiet=True):
  """Reads the pbpfile from an sfit4 output

  Outputs a dict with keys::
    mw: contains the data for each microwindow::
      observed: measured spectrum (normalized to max fitted spectrum)
      fitted: synthetic spectrum
      difference: difference observed-fitted
      wavenumber: wavenumbers
      attr: mw specific information;;
    dims: list of nmw and ?
    header: the header of the sfit spectrum file;; """
  out={}
  try: fid=open(f,'r')
  except IOError: print 'Could not open file %s in read_pbpfile'%os.path.basename(f);return out
  line=fid.readline();
  line=fid.readline();
  try: out['dims']=array(map(int,line.strip('\n').split()))
  except: print 'Could not interpret the second line of file %s in readoutput'%os.path.basename(kbfile);return out
  out['mw']={}
  spectra=['observed','fitted','difference']
  #line=fid.readline();out['header']=line.strip('\n')
  fline=lambda x: map(float,x.strip('\n').split())
  for i in range(out['dims'][0]):
    line=fid.readline();out['mw'][i]={'header':line.strip('\n')}
    line=fid.readline();out['mw'][i].update({'attr':line.strip('\n')})
    j=int(ceil(int(out['mw'][i]['attr'].split()[2])/12.))
    step=float(out['mw'][i]['attr'].split()[1])
    data=dict(zip(spectra,[[],[],[]])+[['wavenumber',[]]])
    for l in range(j):
      for q,label in enumerate(spectra):
	line=fline(fid.readline())
	if label=='observed': data['wavenumber'].append(line[0]);line=line[1:]
	elif label=='fitted': data['wavenumber']+=[data['wavenumber'][-1]+p*step for p in range(1,len(line))]
	data[label]+=line
    out['mw'][i].update(data);del data
  return out;

def create_sfit4_sb(ctl,sbctl,logger=rootlogger):
  """Create an sb matrix out of the data found in the ctl"""
  sbdict={'attr':{}} #contains the different sb matrices for the sb keys
  logger=logging.getLogger(logger.name+'.create_sfit4_sb')
  # Determine which microwindows retrieve zshift
  zerolev_band_b = []
  [zerolev_band_b.append(int(k)) for k in ctl['band'] if not ctl['band.'+str(int(k))+'.zshift']]# only include bands where zshift is NOT retrieved
  logger.debug('Non-retrieved zshift in bands %s'%' '.join(map(str,zerolev_band_b)))
  processedkeys=[] #contains the list of all processed sbctl keys
  for ErrType in ['random','systematic']:
    #zshift
    Sb = zeros(len(zerolev_band_b))
    for i in range(len(zerolev_band_b)):
      ctlsbkey='sb.band.%d.zshift.%s'%(zerolev_band_b[i],ErrType)
      processedkeys.append(ctlsbkey)
      try: Sb[i]=sbctl[ctlsbkey]**2 
      except KeyError: logger.warning('Could not find the STD for zshift in microwindow %d'%i);
    if len(zerolev_band_b) and all(Sb!=0):
      sbkey='%s/%s'%('zshift',ErrType)
      sbdict[sbkey]=diag(Sb)
      sbdict['attr'][sbkey]={'origin': 'from ctl','columns': 'microwindows %s'%', '.join(map(str,zerolev_band_b))}
      logger.debug('zshift/%s covariance=%s'%(ErrType,Sb))
    #errors by mw
    for sbkey in map(Sb_paramMap,Sb_labels_permw): #FOV, OPD ,curvature, slope,...
      ctlsbkey='sb.%s.%s'%(sbkey,ErrType)
      processedkeys.append(ctlsbkey)
      try: Sb=(sbctl[ctlsbkey]**2)*ones(len(ctl['band']))
      except KeyError: logger.warning('Could not find the Sb value for %s.%s'%(sbkey,ErrType));continue
      sbkey='%s/%s'%(sbkey,ErrType)
      sbdict[sbkey]=diag(Sb)
      sbdict['attr'][sbkey]={'origin': 'from ctl','columns': 'all microwindows'}
      logger.debug('%s/%s covariance=%s'%(sbkey,ErrType,Sb))
  for k,v in sbctl.items():
    if processedkeys.count(k)>0: continue
    sbkey='/'.join(k.split('.')[1:]) # go to hdf5 groups
    if type(v)==str:
      if os.path.isfile(v): 
	sbdict[sbkey]=read_matrixfile(v) # TODO not tested yet 
	sbdict['attr'][sbkey]={'origin':'from file %s'%v}
	logger.info('Loaded covariance for %s from file %s (shape=%s)'%(sbkey,v,sbdict[sbkey].shape))
    else:
      if type(v).__name__.find('float')>-1 or type(v)==int: Sb=diag(array([v])**2)
      elif type(v)==list: Sb=diag(array(v)**2)
      elif type(v)==ndarray and v.shape==(): Sb=diag(ctl[k].reshape((1,))**2)
      elif type(v)==ndarray and len(v.shape)==1: Sb=diag(v**2)
      else: logger.error('Could not interprete the sb key %s: %s'%(k,v,v.shape));terror=True;continue
      sbdict[sbkey]=Sb
      sbdict['attr'][sbkey]={'origin':'from ctl'}
  Sb_spectypes=['TAir','PAir','Int']
  for ErrType in ['random','systematic']: #rearrange intensity line errors; by molecule (if it is set in the kb.line.gas list or a single value ... 
    kbtest=['line%s/%s/%s'%(ty,m,ErrType) in sbdict for m in ctl['kb.line.gas'] for ty in Sb_spectypes]
    logger.info('%s Kbtest for spectroscopic database: %s'%(ErrType,kbtest))
    if any(kbtest): #is there a specification per molecules in kb.line.gas?
      for ty in Sb_spectypes:
	Sb=zeros(len(ctl['kb.line.gas']))
	for i,m in enumerate(ctl['kb.line.gas']): 
	  sbkey='line%s/%s/%s'%(ty,m,ErrType)
	  try: Sb[i]=sbdict[sbkey];del sbdict[sbkey]
	  except KeyError: 
	    try: Sb[i]=sbdict['line%s/%s'%(ty,ErrType)]
	    except KeyError: logger.warning('Could not find an Sb value for %s'%sbkey)
	if all(Sb!=0): sbdict['line%s/%s'%(ty,ErrType)]=diag(Sb);sbdict['attr']['line%s/%s'%(ty,ErrType)]={'origin':'from ctl','columns': ', '.join(ctl['kb.line.gas'])}
  for key in sbdict.keys(): #clean up key of type line* for specific molecules... 
    if key[:4]=='line' and len(key.split('/'))>2: del sbdict[key] 
  if ctl['kb']:
    logger.info('Loaded the Sb matrices for\n'+'\n'.join(['%s: %s'%(k,v.shape) for k,v in sbdict.items() if k!='attr']))
  return sbdict;

def read_statevec(sfile,quiet=True):
  """Reads the statevec file of sfit4

  Ouputs a dictionary with keys::
    attr; dims=3-list (gridpoints, iterations, maxiterations and flags=3-list,nmol=number of molecules,nparams=number of fitted parameters
    molnames: names of molecules
    z,p,t: profiles
    <molname>: dict with apriori and retrieved, both are dict with a pro and tc entry
    params: 2xnparams array with 1e is apriori, 2th is retrieved value
    paramnames: name of the retrieved params;;"""
  out={};
  try: fid=open(sfile)
  except IOError: return out
  fid.readline();line=fid.readline();
  line=line.strip('\n').split()
  try: out['attr']={'dims': map(int,line[:3]),'flags':[i=='T' for i in line[3:]]}
  except: print 'Could not interpret the second line of file %s in readoutput'%os.path.basename(kbfile);return out
  if not quiet: print out
  line=fid.readline();line=line.strip('\n').split()
  if not quiet: print line
  for i in range(3):
    key=line[0]
    if not quiet: print key
    out[key]=array([]);
    while 1: 
      line=fid.readline();line=line.strip('\n').split()
      if line==[]: break
      try: out[key]=append(out[key],array(map(float,line)))
      except ValueError: break
    if len(out[key])!=out['attr']['dims'][0]: print 'Dimensions are wrong for %s in readstatevec'%key,out[key];return out;
  out['attr']['nmol']=int(fid.readline().strip('\n'));out['molnames']=[];fid.readline()
  for i in range(out['attr']['nmol']):
    for j in range(2):
      if j==0: aprt='apr'
      else: aprt='ret'
      mol=fid.readline().strip('\n').strip();
      if not out.has_key(mol): out[mol]={aprt:{}}
      else: out[mol][aprt]={}
      if not quiet: print mol,aprt
      if out['molnames'].count(mol)==0: out['molnames'].append(mol)
      dum=array([])
      while 1: 
	line=fid.readline();line=line.strip('\n').split()
	if line==[]: break
	try: dum=append(dum,map(float,line))
	except ValueError: break
      out[mol][aprt]['tc']=dum[0];out[mol][aprt]['pro']=dum[1:]
      if out[mol][aprt]['pro'].shape!=(out['attr']['dims'][0],): print 'Dimensions are wrong for %s in readstatevec'%(mol+' '+aprt),out[mol][aprt];return out;
  out['attr']['nparams']=int(fid.readline().strip('\n'));fullline=[]
  for line in fid: fullline+=line.strip('\n').split()
  if not quiet: fullline
  out['params']=map(float,fullline[out['attr']['nparams']:]);
  out['params']=array(out['params']).reshape((2,out['attr']['nparams']));
  out['paramnames']=fullline[:out['attr']['nparams']]
  fid.close()
  return out;

def extract_dict(ctl,section='option'):
  """Extracts a section from a config dict and returns the extracted and remaining part"""
  odict={};rdict={}
  for k in ctl:
    if k[:len(section)]==section: odict[k]=ctl[k]
    else: rdict[k]=ctl[k]
  return odict,rdict

def update_dict(ctl,key,value):
  """Updates a dict and preserves the ordering"""
  if ctl.has_key(key):
    ctl[key]=(value,ctl[key][1])
  else: 
    section=key.split('.')[0]
    try: n=max([ctl[k][1] for k in ctl.keys() if k.split('.')[0]==section])
    except ValueError: n=max([v[1] for v in ctl.values()])+1
    ctl[key]=(value,n)
  return

def read_output(kbfile,quiet=True):
  """Reads the kb.output, k.output, shat.complete, sa.complete,seinv, ak.target, r(a)prfs.table ...  file of sfit4
  
  Ouput is a dict with keys attr and data. Meta contains 'dims', and (optional) 'columns' if a line is printed the labels of the columns.
  
  In the case of r(a)rprfs.table, attr also contains 'molidx': maps SFIT indices to molecule names and 'other': the list of retrieved molecules
  """
  out={'attr':'','data':array([])};columnflag=True;rprfsflag=False
  try: fid=open(kbfile,'r')
  except IOError: print 'Could not open file %s in readoutput'%os.path.basename(kbfile);return out
  line=fid.readline();
  out['attr']={'dims':[]}
  if line.find('SEINV')>-1 or line.find('MEASUREMENT ERROR')>-1 or\
      line.find('AVERAGING KERNELS NLEV X NLEV MATRIX FOR TARGET ONLY')>-1: columnflag=False;out['attr']['target']=line.split(':')[-1].strip()
  if line.find('Z, P, T, AIRMASS & PROFILES')>-1: rprfsflag=True
  line=fid.readline();
  try: 
    dum=line.strip('\n').split()
    for i,h in enumerate(dum): 
      try: dum[i]=int(h)
      except ValueError: pass
    out['attr']['dims']=[h for h in dum if type(h)==int]
    out['attr']['other']=[h for h in dum if type(h)==str]
  except: print 'Could not interpret the second line of file %s in readoutput'%os.path.basename(kbfile);return out
  if columnflag:
    line=fid.readline();
    if rprfsflag: firstline=line;line=fid.readline()
    try: out['attr']['columns']=array(line.strip('\n').split(),dtype='|S15')
    except: print 'Could not interpret the third line of file %s in readoutput'%os.path.basename(kbfile);return out
    if rprfsflag: out['attr']['molidx']=dict(zip(map(int,firstline.strip('\n').split()),out['attr']['columns']))
  if not quiet: print 'Header: ',out['attr']
  out['data']=read_matrixfile(fid)
  if not quiet: print 'Read %d floats'%(out['data'].shape),'\nFirst float: %s\nLast float: %s'%(out['data'][0],out['data'][-1])
  fid.close()
  if not columnflag and len(out['attr']['dims'])>1:
    try: out['data']=out['data'].reshape(out['attr']['dims'][0],out['attr']['dims'][1]);
    except ValueError: print 'Could not reshape to %s in read_output for %s'%((out['attr']['dims'][0],out['attr']['dims'][1]),kbfile)
  elif columnflag and len(out['attr']['columns'])>1:
    if rprfsflag: rowidx=1
    else: rowidx=0
    try: out['data']=out['data'].reshape(out['attr']['dims'][rowidx],len(out['attr']['columns']));
    except ValueError: print 'Could not reshape to %s in read_output for %s'%((out['attr']['dims'][0],len(out['attr']['columns'])),kbfile)
  return out;

def print_dictfile(ctl,keysep='=',quiet=True):
  """Write a dict to a file (like ctl, ini..)"""
  if type(ctl)!=dict: print 'Wrong input in write_dictfile ctl=',type(ctl),str(ctl)
  out='#printed with print_dictfile'
  for k,v in sorted(ctl.items(),key=lambda x: x[1][1]):
    out+='\n%-45s%s'%(k,keysep)
    if type(v[0])==float: out+='%8.4f'%v[0]
    elif type(v[0])==ndarray: 
      out+='\n'
      out+=''.join(map(lambda x: '%8.4f' %x, v[0]))
#      out+=print_mix(v[0],fmt='8.4f') print_mix does not exist in my setup. I believe the line above is doing the same
    elif type(v[0])==int: out+='%d'%v[0]
    elif type(v[0])==list: out+=' '.join([str(i) for i in v[0]])
    elif type(v[0])==bool: out+=str(v[0])[0]
    else: out+=str(v[0])
  return out;

def hdf_store(hdfid,arrayname='',value=array([]),dtype='f',**kargs):
  """Store a string,bool,np.array,list,datetime (as tuple),dict to a HDF5 datafile hdfid, with name arrayname

  When Saving a dict instance, the keys are transformed to (sub)groups. If the dict has an 'attr' key then attr are set according to this attribute dict (must have the same keys...)

  Input arguments::
    hdfid: h5py openend file
    arrayname='', where to store the data in the file
    value=data to save;;
  Optional key arguments::
    dtype='f', or 's', 'ref' (a hdf reference) or 'vars' (variable length string),...
    kargs are stored in the attrs of the dataset (for a dict instance, all values will get these attr...);;"""
  if hdfid==None: return
  extraat={}
  #elif hdfid==str: hdfid=h5Py.File(hdfid,'w')
  if dtype=='vars': dtype=h5py.special_dtype(vlen=str)
  elif dtype=='ref': dtype=h5py.special_dtype(ref=h5py.RegionReference)
  if type(value)==dict:
    value,attr=expand_dict(value,meta='attr')
    for k,v in value.items():
      extraat={};dtype='f'
      if any(type(v)==array([int,bool])): v=array(int(v));dtype='i'
      elif type(v)==float: v=array(v);dtype='f'
      elif type(v)==datetime.datetime or type(v)==datetime.date: 
	v=array(list(v.timetuple()[:7]));dtype='i';extraat.update({'units':'Year,Month,Day,hour,minutes,seconds,microseconds'})
      elif type(v)==str: dtype=h5py.special_dtype(vlen=str);v=array(v)
      elif type(v)==list: 
	if any([type(i)!=float for i in v]): dtype=h5py.special_dtype(vlen=str);v=array(map(str,v));
	else: dtype='f';v=array(v)
      elif type(v)==ndarray: 
	dtype=v.dtype.name[0];
	if dtype=='s':dtype=h5py.special_dtype(vlen=str) #try this...
	elif dtype=='f' and v.dtype!=float64: v=v.astype(float64)
#      elif type(v)==float128: v=(v.astype(float64)) Does not exist in my python
      elif type(v)==float96: v=(v.astype(float64))
      elif v==None: continue
      d=hdfid.create_dataset(arrayname+'/'+k,v.shape,dtype=dtype)
      try: d[...]=v
      except TypeError: rootlogger.error('%s: dtype=%s, trying to save with dtype %s'%(k,type(v),dtype));raise
      except ValueError: rootlogger.error('%s: dtype=%s, trying to save with dtype %s, shape=%s'%(k,type(v),dtype,v.shape));raise
      for kk,vv in kargs.items()+extraat.items(): d.attrs[kk]=vv
      if k in attr:
	for kk,vv in attr[k].items(): d.attrs[kk]=vv
    return;
  elif any(type(value)==array([list,int,str,bool,float,h5py.h5r.RegionReference])): value=array(value)
  elif type(value)==datetime.datetime or type(value)==datetime.date: 
      value=array(list(value.timetuple()[:7]));dtype='i';extraat.update({'units':'Year,Month,Day,hour,minutes,seconds,microseconds'})
  d=hdfid.create_dataset(arrayname,value.shape,dtype=dtype)
  d[...]=value
  for k,v in kargs.items()+extraat.items():
    d.attrs[k]=v
  return;

def read_summary(f,quiet=True,logger=rootlogger):
  """Reads a summary file

  Ouputs a dictionary with keys::
    FITRMS: rms of yobs-ycalc (normalized to max(yobs)) 
    CHI_2_Y, DOFS_ALL, DOFS_TRG, DOFS_TPR, ITER, MAX_ITER, CONVERGED, DIVWARN
    header: spectrum header
    ngases: number of fitted gases (scale or profile)
    <gas>: dict apr_column, ret_column
    nmw: number of mw
    <mw(i)>: dict with keys IBAND, NUSTART, NUSTOP, SPACE, NPTSB, PMAX, FOVDIA, MEAN_SNR, NSCAN, JSCAN, INIT_SNR, CALC_SNR ;;"""
  out={}
  logger=logging.getLogger(logger.name+'.read_summary');#logger.setLevel(logging.DEBUG)
  try: fid=open(f,'r')
  except IOError: logger.error('Could not open file %s in read_summary'%os.path.basename(f));return out
  dum=fid.readlines();fid.close()
  dum=[l.strip('\n') for l in dum]
  out['nmw']=int(dum[2])
  ii=4+out['nmw']
  out['header']=dum[3]
  out['ngases']=int(dum[ii])
  logger.debug('ngases=%s'%out['ngases'])
  lidx=ii+2;
  gastable=[l.split() for l in dum[lidx:lidx+out['ngases']]]
  lidx+=out['ngases']
  out['gases']=[r[1] for r in gastable]
  for r in gastable: 
    out[r[1]]={'apr_column': float(r[3]),'ret_column': float(r[4])}
  out['nmw']=int(dum[lidx+1])
  headers=[h.strip() for h in dum[lidx+2].split()]
  logger.debug('Headers:%s'%headers)
  lidx+=2
  for c in range(out['nmw']): out['mw%d'%(c+1)]=str2number(dict(zip(headers,dum[lidx+1].split())));lidx+=1
  lidx+=2
  headers=[h.strip() for h in dum[lidx].split()]
  out.update(str2number(dict(zip(headers,dum[lidx+1].split()))))
  return out;

def read_stationlayers(f='station.layers',quiet=True):
  """Reads a station.layers file of Jim starting from an array of boundaries"""
  g=None
  try: 
    with open(f,'r') as fid:
      for i in range(3): fid.readline()
      g=read_matrixfile(fid)
      g=g.reshape((g.shape[0]/5,5))
  except: pass
  return g;

def read_dictfile(f,comments=['#',';','%'],keysep='=',preserve=['option.pspec.input','option.hbin.input','option.isotope.input'],sfit4=False,quiet=True,logger=rootlogger):
  """Reads a ctl or ini file

  Input argument: filestring
  
  Optional key arguments::
    comments= string or list of charachters, defaults= #,;,%
    sfit4 = changes the band and gas.(column,profile).list into lists if only 1 item is given
    keysep='=' seperates key,values (if the file only contains values, they become keys);;
  Output is a dictionary whose values are 2 tuples: the key value + line number"""
  out={}
  logger=logging.getLogger(logger.name+'.read_dictfile')
  if not quiet: logger.setLevel(logging.DEBUG)
  else: logger.setLevel(logging.INFO)
  if type(comments)==str: comments=[comments]
  if type(f)==str and os.path.isfile(f):
    with open(f,'r') as fid: contents=fid.readlines()
    fid=contents
  elif type(f)==str: 
    fid=[l+'\n' for l in f.split('\n')]
  elif type(f)==list or type(f)==ndarray: fid=[l+'\n' for l in f]
  else:logger.error('Unknown input format %s'%type(f));return out;
  n=0
  for line in fid:
    n+=1 
    for i,c in enumerate(comments): 
      if i==0: line=line[:line.find(c)] #last charachter of a line is \n, which is removed by this
      elif line.find(c)>-1: line=line[:line.find(c)]  
    logger.debug(line)
    line=line.strip()
    if not line: continue
    kv=[i.strip() for i in line.split(keysep)]
    logger.debug('%s'%kv)
    if len(kv)==2: k,v=kv;out[k]=(v,n)
    elif len(kv)==1: 
      try: out[k]=(out[k][0]+'\n'+kv[0],out[k][1]) #for arrays 
      except UnboundLocalError: out[kv[0]]=('',n) #if there is no key,value system in the file
    else: logger.warning('Line %s contains to many values in read_dictfile %s: %s'%(line,f,kv))
  for k in out: 
    if not quiet: print k,out[k]
    if preserve.count(k): continue
    n=out[k][1]
    dum=out[k][0].split();
    try: dum=map(int,[i for i in dum])
    except ValueError: 
      try: dum=array(map(float,[i for i in dum]))
      except ValueError: pass
    if len(dum)>1: out[k]=(dum,n)
    elif len(dum)==1: out[k]=(dum[0],n)
    if out[k][0]=='T': out[k]=(True,n)
    if out[k][0]=='F': out[k]=(False,n)
  if sfit4:
    if type(out['band'][0])==int: update_dict(out,'band',[out['band'][0]])
    for i in out['band'][0]:
      dum='band.%d.gasb'%i
      if type(out[dum][0])==str: update_dict(out,dum,[out[dum][0]])
    for field in ['gas.profile.list','gas.column.list','kb.line.gas','kb.profile.gas']:
      if not out.has_key(field) or out[field][0]=='': update_dict(out,field,[]);continue
      if type(out[field][0])==str: update_dict(out,field,[out[field][0]])
  return out;

def directsum(A,B,logger=rootlogger,column=True,row=True):
  """Returns the direct sum of two matrices (if column is false, only the row dimension is augmented)"""
  logger=logging.getLogger(logger.name+'.directsum')
  if not (column or row): logger.error('Allow one dimension to be augmented (not both row and column are off)');return A;
  if len(A.shape)!=2: logger.error('The first argument is no 2D matrix: %s'%A.shape);return A
  if len(B.shape)!=2: logger.error('The first argument is no 2D matrix: %s'%B.shape);return A
  if not column:
    if not all(A.shape[1]==B.shape[1]): logger.error('The column dimension should be the same')
    out=zeros((A.shape[0]+B.shape[0],A.shape[1]),dtype=A.dtype)
    out[0:A.shape[0],:]=A
    out[A.shape[0]:,:]=B
  elif not row:
    if not all(A.shape[0]==B.shape[0]): logger.error('The row dimension should be the same')
    out=zeros((A.shape[0],A.shape[1]+B.shape[1]),dtype=A.dtype)
    out[:,:A.shape[1]]=A
    out[:,A.shape[1]:]=B
  else: 
    out=zeros(add(A.shape,B.shape),dtype=A.dtype)
    out[:A.shape[0],:A.shape[1]]=A
    out[A.shape[0]:,A.shape[1]:]=B
  logger.debug('Output matrix=%s dtype=%s'%(out.shape,out.dtype))
  return out;

def create_sfit4_errorbudget(ctl,retdata={},logger=rootlogger):
  """Computes the error budget for a given ctlsb instance and a dict with retrieval data (e.g. as it is stored in the HDF file"""
  logger=logging.getLogger(logger.name+'.create_sfit4_errorbudget')
  sbprokey='sb' #retdata key that contains all sb matrices ... 
  pickle.dump(ctl,open('ctl.p','w'))
  if isinstance(retdata,h5py.Group): retdata=hdf5todict(retdata,logger=logger)
  for var in ['k','sa','summary/FITRMS','APRprofs']:
    if not var in retdata: logger.error('The %s variable is required in retdata');return {}
  if not 'g' in retdata:
    if not 'seinv' in retdata: logger.error('The seinv matrix must be provided');return {}
    if not 'shat' in retdata: logger.error('The shat matrix must be provided'); return {}
    retdata['g']=retdata['shat'].dot(retdata['k'].T).dot(diag(retdata['seinv'])) 
    logger.info('Calculated the contribution matrix G')
  #------------------------------------------------------
  # Determine number of microwindows and retrieved gasses
  #------------------------------------------------------
  n_window  = len( ctl['band'] )
  n_profile = len( ctl['gas.profile.list'] )
  n_column  = len( ctl['gas.column.list'] )
  se=retdata['seinv']**-1    
  K=retdata['k']
  D=retdata['g']
  K_rows=retdata['attr']['shat']['columns']
  retrievedmols=ctl['gas.profile.list']+ctl['gas.column.list']
  Tpro=retdata['APRprofs'][:,where(retdata['attr']['APRprofs']['columns']=='TEMPERATURE')].squeeze() #for Sb scaling
  logger.debug('Retrieved molecules=%s'%(' '.join(retrievedmols)))
  #-----------------------------------------------------
  # Primary retrieved gas is assumed to be the first gas 
  # in the profile gas list. If no gases are retrieved 
  # as a profile, the primary gas is assumed to be the 
  # first gas in the column gas list.
  #-----------------------------------------------------
  if (n_profile > 0): primgas = ctl['gas.profile.list'][0]
  else:               primgas = ctl['gas.column.list'][0]
  logger.debug('Target gas is %s'%primgas)
  pro_idx_start=where(K_rows==primgas)[0][0]
  logger.debug('Found gas data in state vector starting at index %s'%(pro_idx_start))
  AK = D.dot(K)
  #----------------------------------------------
  # Errors from parameters not retrieved by sfit4
  #----------------------------------------------
  Kb = {} #dict with param's for which errors were calculated 
  if 'GKb' in retdata:
    #--------------------------------
    # Loop through parameter list
    #--------------------------------
    Kb_param = retdata['attr']['GKb']['columns']
    Kb_unsrt = retdata['GKb']  
    #----------------------------------
    # Create a dictionary of Kb columns
    # A list of numpy arrays is created
    # for repeated keys
    #----------------------------------
    for k in set(Kb_param):
      k=k.split('.')[0]
      if k not in retrievedmols: Kb[Sb_paramMap(k)]=Kb_unsrt[:,where([l.find(k)>-1 for l in Kb_param])[0]]
      else: Kb[k]=Kb_unsrt[:,where(Kb_param==k)[0]]
    logger.debug('Error GKb components for:\n\t%s'%'\n\t'.join(['%s: %s'%(k,v.shape) for k,v in Kb.items()]))
  #---------------------------------------------
  # Determine which column retrieved molecules
  # have a Kb profile component: as an intersection
  #---------------------------------------------
  pro_interfmols= list(set(Kb.keys())&set(ctl['gas.column.list']))
  logger.debug('Column retrieved molecules with a profile error budget: %s'%' '.join(pro_interfmols))
  #---------------------------------------------
  #try to construct an error covariance from the data in sb for the different molecules
  #---------------------------------------------
  Sstate= {'random': longdouble(retdata['sa'][:pro_idx_start,:pro_idx_start].copy()), 'systematic': longdouble(zeros((pro_idx_start,)*2))}
  Sstateorigin={'random':{},'systematic':{}} #will contain per species the source of the sa update
  #update the sa components for the profile retrieved specs
  for mol in ctl['gas.profile.list']:
    APpro=retdata['APRprofs'][:,where(retdata['attr']['APRprofs']['columns']==mol)[0]].squeeze()
    gasidx=where(K_rows==mol)[0]
    for ErrType in ['random','systematic']:
      speckey='%s/uncertainties/%s/%s'%(sbprokey,mol,ErrType)
      if speckey in retdata: 
	Sstate[ErrType]=directsum(Sstate[ErrType],diag(APpro**-1).dot(longdouble(retdata[speckey])).dot(diag(APpro**-1)))
	Sstateorigin[ErrType][mol]=retdata['attr'][speckey]['origin']
	logger.debug('Updated %s state vector uncertainty with values from %s (shape=%s)'%(ErrType,speckey,Sstate[ErrType].shape))	
      else: Sstate[ErrType]=directsum(Sstate[ErrType],longdouble(retdata['sa'][gasidx,:][:,gasidx]));Sstateorigin[ErrType][mol]='from sa'
  #update the sa components for the column retrieved specs
  for mol in ctl['gas.column.list']:
    colidx=where(retdata['attr']['APRprofs']['columns']==mol)[0][0]
    PCap=retdata['APRprofs'][:,colidx].squeeze()*retdata['s/airmass']
    # I believe this is wanted in line 916 (column in sa matrix)
    colidx=where(retdata['attr']['sa']['columns']==mol)[0][0]
    for ErrType in ['random','systematic']:
      speckey='%s/uncertainties/%s/%s'%(sbprokey,mol,ErrType)
      if speckey in retdata:
	covcolumn=retdata['s/airmass'].dot(longdouble(retdata[speckey])).dot(retdata['s/airmass'])
	Sstate[ErrType]=directsum(Sstate[ErrType],longdouble(covcolumn/(PCap.sum()**2).reshape(1,1)))
	Sstateorigin[ErrType][mol]=('%s'%(retdata['attr'][speckey]['origin']))
	logger.debug('Updated %s state vector %s uncertainty with values from %s: Sstate[%d,%d]=%s [rel. to TCap]'%(mol,ErrType,sbprokey,colidx,colidx,Sstate[ErrType][colidx,colidx]))	
      else: Sstate[ErrType]=directsum(Sstate[ErrType],longdouble(retdata['sa'][colidx,colidx].reshape(1,1)));Sstateorigin[ErrType][mol]=('from sa')
  #---------------------------------------------
  #Loop over the profile retrieved specs to propagate the uncertainties
  #---------------------------------------------
  retdata['STDerror']={}
  for mol in ctl['gas.profile.list']+ctl['gas.column.list']:
    mollogger=logging.getLogger(logger.name+'.%s'%mol)
    S={'random':{},'systematic':{}} #will contain all covariances for the different uncertainties
    origin={'random':{'Interfering_Specs':[], 'Smoothing':[]},'systematic':{'Interfering_Specs':[], 'Smoothing':[]}} #for attributes of Sb
    APpro=retdata['APRprofs'][:,where(retdata['attr']['APRprofs']['columns']==mol)[0]].squeeze()
    PCap=APpro*retdata['s/airmass']
    PCre=retdata['s/%s'%mol]*retdata['s/airmass']
    mollogger.debug('Apriori total column=%s [molec/cm**2]'%PCap.sum())
    if mol in ctl['gas.column.list']: PCap=PCap.sum().reshape(1,);PCre=PCre.sum().reshape(1,)
    #determine the state vector mol component indices
    gasidx=where(K_rows==mol)[0]
    #determine the state vector interfering mol component indices (but only those that do not have a Kb profile componenent...
    boolrow=ones(K_rows[pro_idx_start:].shape,dtype=bool)
    for m in [mol]+pro_interfmols: boolrow*=(K_rows[pro_idx_start:]!=m)
    interfidx=pro_idx_start+where(boolrow)[0]
    interfspecs=list(set(K_rows[interfidx].squeeze().tolist()))
    mollogger.debug('%s indices in state vector %s:%s'%(mol,gasidx[0],gasidx[-1]+1))
    mollogger.debug('Interfering molecules %s (no profile in Kb) indices in state vector %s'%(' '.join(interfspecs),interfidx))
    #Matrix slicing
    Dx=D[gasidx,:]
    AI=AK[gasidx,:][:,gasidx] - identity( gasidx.shape[0] )
    AK_int1=AK[gasidx,0:pro_idx_start]  #for retrieval params
    AK_int2=AK[gasidx,:][:,interfidx ] #for interfering
    #compute the covariances on mol components
    for ErrType in ['random','systematic']:
      #---------------------------------
      # Calculate Smoothing error on target
      #                               T
      #      Ss = (A-I) * Sa * (A-I)
      #---------------------------------
      ErrLabel='Smoothing'
      S[ErrType][ErrLabel] = AI.dot(Sstate[ErrType][gasidx,:][:,gasidx]).dot(AI.T)
      mollogger.info('Uncertainty for %s/%s: %s%% (relative to retrieved column)'%(ErrLabel,ErrType,sqrt(PCap.dot(S[ErrType][ErrLabel]).dot(PCap))/PCre.sum()*100))
      origin[ErrType][ErrLabel]=Sstateorigin[ErrType][mol]
      #----------------------------------
      # Calculate Measurement error using 
      # SNR calculated from the spectrum
      #                    T
      #  Sm = Dx * Se * Dx
      #----------------------------------
      ErrLabel='Measurement'
      if ErrType=='random': 
	S[ErrType][ErrLabel] = Dx.dot(diag(longdouble(se))).dot(Dx.T)
	origin[ErrType][ErrLabel]='measurement noise from se'
	mollogger.info('Uncertainty for %s/%s: %s%% (relative to retrieved column)'%(ErrLabel,ErrType,sqrt(PCap.dot(S[ErrType][ErrLabel]).dot(PCap))/PCre.sum()*100))
      #---------------------
      # Interference Errors:
      #---------------------
      ErrLabel='Retrieval_Params'
      if ErrType=='random': 
	Sa_int1=Sstate[ErrType][0:pro_idx_start,0:pro_idx_start]
	S[ErrType][ErrLabel] = AK_int1.dot(longdouble(Sa_int1)).dot(AK_int1.T)
	origin[ErrType][ErrLabel]='from sa'
	mollogger.info('Uncertainty for %s/%s: %s%% (relative to retrieved column)'%(ErrLabel,ErrType,sqrt(PCap.dot(S[ErrType][ErrLabel]).dot(PCap))/PCre.sum()*100))
      ErrLabel='Interfering_Specs'
      Sa_int2=Sstate[ErrType][interfidx,:][:,interfidx]
      S[ErrType][ErrLabel] = AK_int2.dot(longdouble(Sa_int2)).dot(AK_int2.T)
      origin[ErrType][ErrLabel]=';'.join(['%s: %s'%(sp,v) for sp,v in Sstateorigin[ErrType].items() if sp in interfspecs])
      mollogger.info('Uncertainty for %s/%s: %s%% (relative to retrieved column)'%(ErrLabel,ErrType,sqrt(PCap.dot(S[ErrType][ErrLabel]).dot(PCap))/PCre.sum()*100))
      #Stop if no error computation
      if 'GKb' in retdata: 
	for ErrLabel in Kb_labels+pro_interfmols:
	  if ErrLabel in Kb:
	    if ErrLabel in pro_interfmols + ['temperature']:
	      if ErrLabel=='temperature': species='T'
	      else: species=ErrLabel
	      sbkey='%s/uncertainties/%s/%s'%(sbprokey,species,ErrType)
	      try: Sb =retdata[sbkey];origin[ErrType][ErrLabel]=retdata['attr'][sbkey]['origin']
	      except KeyError: mollogger.warning('Sb is not set for %s/%s in retdata'%(ErrLabel,ErrType));continue	    
	      if species!='T':
		#the column retrieved molecules are excluded from the Interfering_Specs smoothing error if Kb is calculated
		Aprospecies=retdata['APRprofs'][:,where(retdata['attr']['APRprofs']['columns']==species)[0]].squeeze()
		Sb= diag(Aprospecies**-1).dot(Sb).dot(diag(Aprospecies**-1))
		n=Sb.shape[0]
		Cn=identity(n)-1/n*ones((n,n))
		DK=tensordot(AK[gasidx,where(retdata['attr']['k']['columns']==ErrLabel)[0][0]],1/n*ones(n),0) + Kb[ErrLabel][gasidx,:].dot(Cn)
	      else: 
		DK=Kb[ErrLabel][gasidx,:]
		# Convert degrees to relative units ?????
		Sb= diag(Tpro**-1).dot(Sb).dot(diag(Tpro**-1))
	    else:
	      sbkey='sb/%s/%s'%(ErrLabel,ErrType)
	      try: Sb =retdata[sbkey];origin[ErrType][ErrLabel]=retdata['attr'][sbkey]['origin']
	      except KeyError: mollogger.warning('Sb is not set for %s/%s in retdata'%(ErrLabel,ErrType));continue	    
	      DK = Kb[ErrLabel][gasidx,:] #Here Kb is already GKb (store GKb for memory reasons)
	    try: S[ErrType][ErrLabel] = DK.dot(longdouble(Sb)).dot(DK.T)
	    except: mollogger.error('Unable to propagate error %s: Sb.shape=%s, Gkb.shape=%s'%(sbkey,Sb.shape,DK.shape));continue
	    mollogger.info('Uncertainty for %s/%s: %s%% (relative to retrieved column)'%(ErrLabel,ErrType,sqrt(PCap.dot(S[ErrType][ErrLabel]).dot(PCap))/PCre.sum()*100))
      terr=sqrt(PCap.dot(sum([Se for Se in S[ErrType].values()],0)).dot(PCap))/PCre.sum()*100
      retdata['TCerror/%s/%s'%(mol,ErrType)]=terr
      retdata['attr']['TCerror/%s/%s'%(mol,ErrType)]={'unit':'in percentage, relative to retrieved total column',\
	'contributions': ';'.join([ErrLabel for ErrLabel,Se in S[ErrType].items() if any(Se!=0.)]),\
	'origin': ';'.join(['%s:%s'%(ErrLabel,origin[ErrType][ErrLabel]) for ErrLabel,Se in S[ErrType].items() if any(Se!=0.)])}
      mollogger.info('Total %s for %s: %s%% (relative to retrieved column)'%(ErrType,mol,terr))
      if mol in ctl['gas.column.list']:continue
      #store the total error data in the retdata dict
      ek='s/uncertainties/%s/%s'%(mol,ErrType)
      retdata[ek]=sum([(Se) for ErrLabel,Se in S[ErrType].items() if ErrLabel!='Smoothing' and any(Se!=0.)],0)
      logger.debug('%s'%retdata[ek].dtype)
      try: retdata[ek]=diag(APpro).dot(retdata[ek]).dot(diag(APpro))
      except ValueError: logger.error('Shape of matrices involved: APpro=%s,retdata[%s]=%s'%(APpro.shape,ek,retdata[ek].shape));raise
      retdata['attr'][ek]={'unit': 'ppv**2',\
'contributions': ';'.join([ErrLabel for ErrLabel,Se in S[ErrType].items() if ErrLabel!='Smoothing' and any(Se!=0.)]),\
'origin': ';'.join(['%s:%s'%(ErrLabel,origin[ErrType][ErrLabel]) for ErrLabel,Se in S[ErrType].items() if ErrLabel!='Smoothing' and any(Se!=0.)])}
      for ErrLabel in S[ErrType]: retdata['STDerror']['%s/%s/%s'%(mol,ErrLabel,ErrType)]=sqrt(diag(S[ErrType][ErrLabel]))
  return;

def read_matrixfile(filestr,size=0):
  """Read a matrix from a txt file: concatenates all floats in a file, and then tries to reshape to a square matrix

  Input argument: string to a filename or a file identifier

  Optional input argument: size=0, should be a tuple if set, allows to provide the shape of the output matrix (0=try a square)"""
  if size!=0 and type(size)!=tuple:
	print "size should be a tuple... abort"
	return array([])
  out=[]
  if type(filestr)==str: 
    try: fid=open(filestr)
    except:
      print 'Unable to open the file %s, abort'%(filestr)
      return [];
  else: fid=filestr
  for line in fid:
    line=line.strip('\n').split()
    for item in line:
      try: out.append(float(item))
      except ValueError: continue
  fid.close()
  dum=sqrt(len(out))
  if size==0 and int(dum)==dum: size=(int(dum),int(dum))
  if size!=0:
    return array(out).reshape(size)
  else:
    return array(out);

def plot_matrix(ax,matrix=zeros((10,10)),grids=arange(10),gridt=arange(10),grid=arange(10),\
      titlestring='',slabelstring='',tlabelstring='',cbarstring='',zmaxt=nan,\
      zmint=nan,zmins=nan,zmaxs=nan,zmin=nan,zmax=nan,cnorm=[],shading='gouraud',colormap='jet',\
      logflag=False,sticks=[],quiet=True):
  """Create a plot of a matrix
  
  Input arguments:
    ax=axes to plot on
  Optional key arugments::
    matrix=numpy array to plot
    grids,gridt=the source,target axes (column,row axes)
    grid=range(10) used for square matrices (is copied to grids,gridt)
    titlestring='' string of title (or list [titlestring,fontsize])
    slabelstring='', label for source (column,x) grid variables
    tlabelstring='', label for target (row, y) grid variables
    cbarstring=''
    shading='gouraud' (or 'flat' or 'faceted')
    colormap='jet'
    cnorm=[], or a list of 2 floats, or can be a string 'symmetric'
    logflag=grid should be plotted on a logaritmic scale (only square matrices)
    sticks=list of string labels to attach to the source variables
    zmax(s,t)=0, maximal height of the xy axis (0=max(grid))
    zmin(s,t)=0, minimal height of the xy axis (0=min(grid));;"""
  square=False
  if type(matrix)!=ndarray or type(grid)!=ndarray: print 'Wrong type of input for matrix, grid';return
  if len(matrix.shape)!=2: print 'Matrix should be 2D',matrix.shape; return
  if matrix.shape[0]==matrix.shape[1]: square=True;  ax.set_aspect('equal')
  if type(titlestring)==str: titlestring=[titlestring,10]
  ds=1;dt=1;
  if not all(grids==arange(10)): ds=0;
  if not all(gridt==arange(10)): dt=0; 
  if not all(grid==arange(10)) and square: ds=0;dt=0
  newmatrix=nan*zeros((matrix.shape[0]+dt,matrix.shape[1]+ds))
  maskmatrix=ones(newmatrix.shape,dtype=bool)
  newmatrix[dt:,ds:]=matrix[::-1,::-1];newmatrix=newmatrix[::-1,::-1];maskmatrix=isnan(newmatrix)
  #else: newmatrix=matrix;maskmatrix=isnan(matrix)+bdboolmatrix
  if all(gridt==arange(10)): gridt=arange(newmatrix.shape[0])+0.5;
  if all(grids==arange(10)): grids=arange(newmatrix.shape[1])+0.5;
  if any(grid!=arange(10)) and square: grids=grid;gridt=grid
  if all(grids==arange(newmatrix.shape[1])+0.5): ax.set_xticks(arange(1,newmatrix.shape[1]))
  if all(gridt==arange(newmatrix.shape[0])+0.5): ax.set_yticks(arange(1,newmatrix.shape[0]))
  if newmatrix.shape!=gridt.shape+grids.shape: print 'Shape mismatch for matrix,grid: ',newmatrix.shape,gridt.shape,grids.shape
  from matplotlib import cm
  from matplotlib.patches import Patch
  if not quiet: print 'source grid',grids,'target grid',gridt,'Squarematrix?',square
  if isnan(zmins): zmins=min(grids)
  if isnan(zmint): zmint=min(gridt)
  if isnan(zmaxs): zmaxs=max(grids)
  if isnan(zmaxt): zmaxt=max(gridt)
  if all(grids==gridt):
    if not isnan(zmax): zmaxt=zmax;zmaxs=zmax
    if not isnan(zmin): zmint=zmin;zmins=zmin
  zmaxls=min([i for i in grids if i>=zmaxs]+[zmaxs]);zminls=max([i for i in grids if i<=zmins]+[zmins])
  zmaxlt=min([i for i in gridt if i>=zmaxt]+[zmaxt]);zminlt=max([i for i in gridt if i<=zmint]+[zmint])
  #for i,hs in enumerate(grids):
    #for j,ht in enumerate(gridt):
      #if hs<=zmaxls and hs>=zminls and ht<=zmaxlt and ht>=zminlt: maskmatrix[j,i]=False
  if not quiet: print 'Source limits:',zmins,zmaxs,'Target limits:',zmint,zmaxt
  ax.set_xlim(zmins,zmaxs);ax.set_ylim(zmint,zmaxt)
  if square:
    if slabelstring=='': slabelstring=tlabelstring
    if logflag: 
      ax.set_yscale('log');ax.set_xscale('log')
      ax.set_ylim(ax.get_ylim()[::-1]);ax.set_xlim(plt.xlim()[::-1])
  X,Y =meshgrid(grids, gridt)
  if cnorm=='symmetric':
    vmax=matrix.max()
    if not quiet: print vmax
    plt.pcolormesh(X,Y,ma.masked_array(newmatrix,maskmatrix),shading=shading,cmap=colormap,vmin=-vmax,vmax=vmax)
  elif type(cnorm)==list and len(cnorm)==2:
    plt.pcolormesh(X,Y,ma.masked_array(newmatrix,maskmatrix),shading=shading,cmap=colormap,vmin=cnorm[0],vmax=cnorm[1])
  else:
    plt.pcolormesh(X,Y,ma.masked_array(newmatrix,maskmatrix),shading=shading,cmap=colormap);rint 
  t=ax.set_title(titlestring[0],fontsize=titlestring[1])
  t.set_y(titlepad) 
  cbar=plt.colorbar(pad=.05,fraction=0.05)
  cbar.set_label(cbarstring)
  ax.set_xlabel(slabelstring);ax.set_ylabel(tlabelstring)
  if sticks!=[]: plt.xticks(ax.get_xticks(),sticks,rotation=-45,fontsize=8)
  return;

def merge_hdf(listoffiles,target='./full.hdf',logger=rootlogger,**kargs):
  """Merges the contents of HDF files (input is a list, target=target file)

  Will create or append data to the target. If the source is in the target, it will be updated.
  The source files are mapped to groups whose name is found in the source under 'barcos/specid'
  It it is not there, the target groups are the filenames
  
  Input arguments: listoffiles=list of the source hdf files
  
  Optional arguments::
    target=./full.hdf 
    logger=rootlogger (if None, no logging (for multiprocessing))
    kargs= dict with attributes for the target"""
  if logger: logger=logging.getLogger(logger.name+'.merge_hdf')
  if os.path.isfile(target): mode='r+'
  else: mode='w'
  if logger: logger.debug('File %s opened in %s mode'%(target,mode))
  if logger: logger.debug('Merging files:%s'%listoffiles)
  with h5py.File(target,mode) as master:
    processedfiles=[]
    for i,f in enumerate(listoffiles):
      if logger: logger.debug('Copying contents of file %s'%f)
      with h5py.File(f,'r') as source: 
	if 'barcos' in source: label=str(source['barcos/specid'][...])
	else: label=f
	if label in master: 
	  if logger: logger.debug('The group %s already exists in the target file, updating it'%label); 
	  del master[label]
	master.copy(source,label);processedfiles.append(f)
    #set the attributes for the target
    for k,v in kargs.items(): 
      if any([type(v)==t for t in [str,float,int,bool]]): pass
      else: v=str(v)
      master.attrs[k]=v
  for f in processedfiles: os.remove(f)
  return

def norsplotsetup(**kargs):
  """Settings valid for all plots"""
  texflag=True;fsize=10
  for key in kargs:
    if key=='usetex': texflag=kargs[key]
    elif key=='fontsize': fsize=kargs[key]
    else: print "Key %s is unknown and ignored in norsplotsetup"%key
  matplotlib.rcParams['text.usetex']=texflag
  matplotlib.rcParams['font.family']='sans-serif'
  matplotlib.rcParams['font.size']=fsize
  if texflag: matplotlib.rcParams['font.serif']='times'
  matplotlib.rcParams['axes.titlesize']='medium'
  matplotlib.rcParams['xtick.labelsize']='small'
  matplotlib.rcParams['ytick.labelsize']='small'
  matplotlib.rcParams['axes.color_cycle']=colorcycle #colorcycle is defined in the beginning
  matplotlib.rcParams['legend.numpoints']=4
  matplotlib.rcParams['legend.handlelength']=2.5
  matplotlib.rcParams['lines.markersize']=5
  matplotlib.rcParams['savefig.dpi']=300

#>Determine time unit setup from list of dates

def finalizefig(**kargs):
  """Saves, plots figure windows if possible (also for SAGE)
  
  Optional key arguments::
    pdf=string to pdf filename (multiple pages)
    png,jpg,eps=string to png,jpg,eps file (all figures go in seperate files: name+number)
    figidx=list of figure windows to save/show (default is all figs)
    pdftitle=title of pdf document
    compress=False (compress the output pdf file using ghostscript)
    returnfigflag=does not close the figure windows
    transparentflag=False: saves png files with a transparent background;;"""
  returnfigflag=False;plotstohandle=[1];pdftitle='';logger=rootlogger;compress=False
  plottypes={'pdf':{},'jpg':{},'png':{},'eps':{}};transparentflag=False
  for key in plottypes.keys(): plottypes[key]={'flag':False,'f':''}
  quiet=1
  if not quiet: print plottypes
  try: plotstohandle=plt.get_fignums()
  except: pass
  for key in kargs:
    if plottypes.keys().count(key)>0: plottypes[key]['flag']=True;plottypes[key]['f']=kargs[key]
    elif key=='returnfigflag': returnfigflag=kargs[key]
    elif key=='figidx': plotstohandle=map(int,kargs[key])
    elif key=='pdftitle': pdftitle=kargs[key]
    elif key=='transparentflag': transparentflag=kargs[key]
    elif key=='quiet': quiet=kargs[key]
    elif key=='compress': compress=kargs[key]
    elif key=='logger': logger=kargs[keys]
    else: print 'Unknown key in finalizefig',key
  logger=logging.getLogger(logger.name+'.finalizefig')
  if not quiet: logger.setLevel(logging.DEBUG)
  logger.debug('%s'%plottypes)
  for key in [k for k in plottypes if plottypes[k]['flag']]:
    if not os.path.isdir(os.path.dirname(plottypes[key]['f'])): logger.error('The target directory for %s does not exist'%key);return
  if type(plotstohandle)!=list or (any([type(i)!=int for i in plotstohandle]) and not sageflag): logger.error('Indices wrongly formatted');return
  if matplotlib.get_backend()=='pdf' and (plottypes['png']['flag']==True or plottypes['jpg']['flag']==True):
    logger.warning('Skipping the eps, png and jpg plots, backend is set to pdf');
    plottypes['png']['flag']=False;plottypes['jpg']['flag']=False;plottypes['eps']['flag']=False
  if not any([t['flag'] for t in plottypes.values()]) and not returnfigflag:
    try:
      os.environ["DISPLAY"]
      if sageflag: 
	for i in plotstohandle: pylab.figure(i);pylab.savefig('dum%d'%i,dpi=100)
    except: 
      logger.error("No display available to show plots, use pdf key argument")
    else: pylab.show()
  if plottypes['pdf']['flag']==True:
    import getpass
    allpicturesfile = PdfPages(plottypes['pdf']['f']) 
    for i in plotstohandle:
      plt.figure(i)
      pylab.savefig(allpicturesfile,format='pdf')
    d = allpicturesfile.infodict()
    d['Title'] = pdftitle
    d['Author'] = getpass.getuser()
    d['Subject'] = ''
    d['Keywords'] = ''
    d['ModDate'] = datetime.datetime.today()
    allpicturesfile.close()
    #compress the result with gs
    if compress: 
      o,e=subProcRun(('gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dNOPAUSE -dQUIET -dPDFSETTINGS=/ebook -dBATCH\
 -sOutputFile=%s %s'%('.dummy.pdf',plottypes['pdf']['f'])).split(' '),quiet=False)
      if e: logger.error('using gs compress: %s'%e)
      else: shutil.move('.dummy.pdf',plottypes['pdf']['f'])
  for pt in plottypes:
     if pt=='pdf' or plottypes[pt]['flag']==False: continue
     for i in plotstohandle: pylab.figure(i);pylab.savefig('%s_%d.%s'%(os.path.splitext(plottypes[pt]['f'])[0],i,pt),format=pt,transparent=transparentflag)
  if not returnfigflag: 
    for i in plotstohandle: pylab.close(i)
  return;

def plot_avk(ax,z,avk,**kargs):
  """Create mosaic plot of rows of a AVK matrix  (Algorithm~\ref{alg:plotvmravk})
  
  Input arguments::
    ax=axes to plot on
    z=height grid corresponding to the grid of the AVK
    avk=avk matrix (dimension corresponds to z);;
  Optional key arguments::
    cbar,cgrid=flags for color bar and color grid (horizontal colored lines)
    maxh,minh= boundary values for cbar values and ylim 
    ylabelstring=string or list of strings (if list, first=ylabel,second is pressure label)
    titlestring=string or list of string,size
    zscale=1,unit scaling for height scale
    pressure=values for additional pressure grid
    pticks=autopressureticks, determines ticks on the pressurescale
    colormap=string for colormap see \url{http://www.loria.fr/~rougier/teaching/matplotlib/\#colormaps};;"""
  quiet=1
  titlestring='';ylabelstring='';zscale=1;pticks=autopressureticks
  minh=min(z);maxh=max(z); cbarflag=1;cgridflag=0;colormap='jet';pressure=[]
  try: 
    if (z.shape[0],z.shape[0])!=avk.shape: print "Shape mismacht height is %d, avk is"%z.shape,avk.shape; return
  except: 
    print "Wrong type of input for heigth coordinate and/or avk";return
  for key in kargs:
    if key=='cbar': cbarflag=kargs[key]
    elif key=='cgrid': cgridflag=kargs[key]
    elif key=='maxh': maxh=kargs[key] #optional argument to stretch heigth colorbar
    elif key=='minh':minh=kargs[key]
    elif key=='quiet':quiet=kargs[key]
    elif key=='ylabelstring': ylabelstring=kargs[key]
    elif key=='titlestring': titlestring=kargs[key]
    elif key=='zscale': zscale=kargs[key]
    elif key=='pressure': pressure=kargs[key]
    elif key=='pticks': pticks=kargs[key]
    elif key=='colormap': colormap=kargs[key]
    else: print "Key %s is unknown and ignored"%key     
  minh*=zscale;maxh*=zscale #units 
  norsplotsetup();
  if type(titlestring)==list:
    try: t=ax.set_title(titlestring[0],fontsize=titlestring[1])
    except: pass
  elif type(titlestring)==str:
    t=ax.set_title(titlestring)
  t.set_y(titlepad)
  import matplotlib.colors as colors
  import matplotlib.cm as cmx
  try: jet = cm = plt.get_cmap(colormap) 
  except: print 'Colormap %s unknown. Abort...'%colormap
  cNorm  = colors.Normalize(vmin=minh, vmax=maxh)
  scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
  colordata = array([])
  zplot=z*zscale
  if not quiet: print zplot
  for j,h in enumerate(zplot):
    colorVal = scalarMap.to_rgba(zplot[j])
    if not quiet: print colorVal
    ax.plot(avk[j,:],zplot,color=colorVal)
    if cgridflag==1: ax.axhline(y=zplot[j],color=colorVal)
    colordata=append(colordata,zplot[j])
    #lines.append(retLine)
  scalarMap.set_array(colordata)
  if cbarflag==1: cbar = plt.colorbar(scalarMap,pad=.1,fraction=0.05)
  pressurestring=''
  if type(ylabelstring)==str:
    if cbarflag==1: cbar.set_label(ylabelstring)
    ax.set_ylabel(ylabelstring)
  elif type(ylabelstring)==list and len(ylabelstring)>1:
    if cbarflag==1: cbar.set_label(ylabelstring[0])
    ax.set_ylabel(ylabelstring[0])
    pressurestring=ylabelstring[1]
  ax.set_ylim(minh,maxh)
  if len(pressure)!=0:
    axp=ax.twinx() #2 y scales
    axp.set_yscale('log') #set logaritmic scale
    axp.set_ylim(max(pressure),min(pressure)) #invert the pressure scale
    axp.yaxis.set_major_formatter(FormatStrFormatter('%3G'))
    axp.yaxis.set_ticks([p for p in pticks if p<=max(pressure) and p>=min(pressure)]) 
    axp.set_ylabel(pressurestring);
  return;

#>Create pc avk plot of rows of AVK (Algorithm~\ref{alg:plotcolavk})

def upboundary(zb,logger=rootlogger):
  """creates decreasing shape (2,...) boundary out an increasing list of boundaries"""
  logger=logging.getLogger(logger.name+'.upboundary') 
  if len(zb.shape)!=1: logger.error('This function accepts only 1D boundary arrays')
  if any(zb[:]!=sort(zb[:])):  logger.error('The input boundaries must be sorted')
  return array([zb[:-1][::-1],zb[1:][::-1]]);

#>Construction of the MACC pressure grid (Algorithm~\ref{algo:prgrid})

