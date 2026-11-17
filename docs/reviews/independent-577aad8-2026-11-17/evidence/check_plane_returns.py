#!/usr/bin/python3
"""Sample actual filled copper; point coverage is not HF return impedance."""
import sys,json,math
from pathlib import Path
import pcbnew as k
base=Path(__file__).parent;b=k.LoadBoard(sys.argv[1]);data=json.loads((base/'saved-board.json').read_text());m=json.loads((base/'geometry-measurements.json').read_text())
zones={b.GetLayerName(z.GetLayer()):z for z in b.Zones()}
def filled(l,xy):return zones[l].HitTestFilledArea(b.GetLayerID(l),k.VECTOR2I(k.FromMM(xy[0]),k.FromMM(xy[1])))
returns={r['from']:r['path'][-1][:2] for r in m['returns'] if 'path' in r}
result={'method':__doc__,'return_via_pairs':[],'back_digital_over_In2':[]}
for cap,pin in [('C24','32'),('C25','32'),('C26','57'),('C27','57'),('C28','25'),('C29','25'),('C30','25'),('C36','53'),('C39','49'),('C40','51')]:
 a=returns[cap+'.2'];c=returns['U1.'+pin];length=math.dist(a,c);points=[[a[j]+(c[j]-a[j])*i/200 for j in [0,1]] for i in range(201)]
 result['return_via_pairs'].append({'capacitor':cap,'adc_ground_pin':pin,'from_via':a,'to_via':c,'separation_mm':length,'In1_filled_samples':sum(filled('In1.Cu',p) for p in points),'samples':len(points)})
digital=lambda n: ('SPI' in n or 'ADS_' in n or n=='IF_EN')
vias=[t['start'] for t in data['tracks'] if t['type']=='PCB_VIA']
for t in data['tracks']:
 if t['layer']!='B.Cu' or t['type']=='PCB_VIA' or not digital(t['net']):continue
 length=math.dist(t['start'],t['end']);ns=max(2,math.ceil(length/.1));bad=[]
 for i in range(ns):
  p=[t['start'][j]+(t['end'][j]-t['start'][j])*(i+.5)/ns for j in [0,1]]
  if not filled('In2.Cu',p):bad.append({'xy':p,'In1_filled':filled('In1.Cu',p),'distance_to_any_via_mm':min(math.dist(p,v) for v in vias)})
 if bad:result['back_digital_over_In2'].append({'net':t['net'],'start':t['start'],'end':t['end'],'segment_length_mm':length,'uncovered_length_estimate_mm':length*len(bad)/ns,'samples_in_gap':bad})
(base/'plane-return-samples.json').write_text(json.dumps(result,indent=2)+'\n')
for r in result['return_via_pairs']:print(r)
for r in result['back_digital_over_In2']:
 far=[p for p in r['samples_in_gap'] if p['distance_to_any_via_mm']>.8]
 if far:print('B.Cu crossing',r['net'],r['start'],r['end'],'In2 uncovered ~',round(r['uncovered_length_estimate_mm'],3),'example',far[len(far)//2])
