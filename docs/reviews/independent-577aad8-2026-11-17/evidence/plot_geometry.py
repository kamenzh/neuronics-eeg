#!/usr/bin/env python3
"""Plots extracted saved copper, not a generator model. Axes are PCB millimetres."""
import json,sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle,Circle
from matplotlib.transforms import Affine2D
base=Path(__file__).parent
d=json.loads((base/'saved-board.json').read_text())
colors={'GND':'#9cacbc','AVDD_5V':'#dd541e','DVDD_3V3':'#7c35a3','VREFP':'#1b9b6c','REF_FILTERED':'#d12581','VCAP1':'#1984ad','VCAP2':'#1984ad','VCAP3':'#1984ad','VCAP4':'#1984ad','SPI_SCLK':'#d49400','BUF_SPI_SCLK':'#d49400'}
def draw(ax,layer,limits=None,labels=False,highlight=None):
    for z in d['zones']:
        if z['layer']==layer:
            for p in z['polygons']:ax.add_patch(Polygon(p['outline'],facecolor='#d8e3ed',edgecolor='none',lw=0))
    for t in d['tracks']:
        col=colors.get(t['net'],'#555b63');alpha=1 if highlight is None or t['net'] in highlight else .13
        if t['type']=='PCB_VIA':
            if layer in t['layers']:
                ax.add_patch(Circle(t['start'],t['width']/2,fc=col,ec='none',alpha=alpha));ax.add_patch(Circle(t['start'],t['drill']/2,fc='white',ec='none'))
        elif t['layer']==layer:ax.plot([t['start'][0],t['end'][0]],[t['start'][1],t['end'][1]],color=col,lw=t['width']*3,alpha=alpha,solid_capstyle='round')
    for f in d['footprints']:
        for p in f['pads']:
            if layer not in p['layers']:continue
            x,y=p['xy'];w,h=p['size'];col=colors.get(p['net'],'#555b63')
            patch=Rectangle((x-w/2,y-h/2),w,h,fc=col,ec='none',alpha=.8)
            patch.set_transform(Affine2D().rotate_deg_around(x,y,-p['angle'])+ax.transData);ax.add_patch(patch)
            if p['drill'][0]:ax.add_patch(Circle((x,y),p['drill'][0]/2,fc='white',ec='none'))
        if labels:
            ax.text(f['xy'][0],f['xy'][1]-1,f['ref'],fontsize=5,ha='center',color='#101725',clip_on=True)
    for e in d['outline']:
        a,b=e['start'],e['end'];ax.plot([a[0],b[0]],[a[1],b[1]],color='black',lw=.7)
    if limits:ax.set_xlim(limits[0:2]);ax.set_ylim(limits[3],limits[2])
    else:ax.set_xlim(48,142);ax.set_ylim(147,53)
    ax.set_aspect('equal');ax.set_title(layer);ax.set_xlabel('x (mm)');ax.set_ylabel('y (mm)');ax.grid(alpha=.12)
fig,axs=plt.subplots(2,2,figsize=(15,15))
for ax,l in zip(axs.flat,['F.Cu','In1.Cu','In2.Cu','B.Cu']):draw(ax,l,labels=l=='F.Cu')
fig.suptitle('A0.3 saved CAD: all four copper layers; inner pours shown as saved',fontsize=16)
fig.tight_layout();fig.savefig(base/'four-layers.png',dpi=180);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(15,8))
for ax,l in zip(axs,['F.Cu','B.Cu']):draw(ax,l,(90,112,77,111),True,{'AVDD_5V','VREFP','VCAP1','VCAP2','VCAP3','VCAP4','REF_FILTERED','GND'})
axs[0].annotate('U1.54 AVDD1',xy=(101.25,86.338),xytext=(104,79),fontsize=8,arrowprops={'arrowstyle':'->'})
axs[0].annotate('U1.24 VREFP',xy=(99.75,97.662),xytext=(106,109),fontsize=8,arrowprops={'arrowstyle':'->'})
fig.suptitle('ADC local supply/reference routing — inspect with corresponding ground planes')
fig.tight_layout();fig.savefig(base/'adc-detail.png',dpi=200);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(15,7))
for ax,l in zip(axs,['In2.Cu','B.Cu']):draw(ax,l,(102,138,82,110),True,{'SPI_SCLK','BUF_SPI_SCLK','SPI_MOSI','SPI_MISO','GND'})
fig.suptitle('Digital routing and adjacent inner-plane copper; gaps are visible in In2.Cu')
fig.tight_layout();fig.savefig(base/'digital-return-detail.png',dpi=200)
print('Created four-layers.png, adc-detail.png, digital-return-detail.png')
