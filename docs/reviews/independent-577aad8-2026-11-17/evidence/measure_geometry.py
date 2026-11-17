#!/usr/bin/env python3
"""Independent centerline graph; geometric evidence, not impedance extraction.
Pads connect at their centres; trace endpoint positions must touch the pad.
Zero-length via transitions exclude barrel length. Zones excluded from graph.
"""
import json,math,heapq,collections
from pathlib import Path
base=Path(__file__).parent;d=json.loads((base/'saved-board.json').read_text())
pads={(f['ref'],p['number']):p for f in d['footprints'] for p in f['pads'] if p['number']}
cu=['F.Cu','In1.Cu','In2.Cu','B.Cu']
def node(xy,l):return (round(xy[0],5),round(xy[1],5),l)
def distance(a,b):return math.hypot(a[0]-b[0],a[1]-b[1])
def inpad(p,xy):
 a=math.radians(p['angle']);x=xy[0]-p['xy'][0];y=xy[1]-p['xy'][1]
 return abs(x*math.cos(a)-y*math.sin(a))<=p['size'][0]/2+1e-5 and abs(x*math.sin(a)+y*math.cos(a))<=p['size'][1]/2+1e-5
cache={}
def graph(net):
 if net in cache:return cache[net]
 g=collections.defaultdict(dict);vias=[]
 def edge(a,b,w):g[a][b]=min(w,g[a].get(b,1e20));g[b][a]=g[a][b]
 tracks=[t for t in d['tracks'] if t['net']==net]
 for t in tracks:
  if t['type']=='PCB_VIA':
   ns=[node(t['start'],l) for l in t['layers'] if l in cu];vias.append(t)
   for a,b in zip(ns,ns[1:]):edge(a,b,0)
  else:edge(node(t['start'],t['layer']),node(t['end'],t['layer']),distance(t['start'],t['end']))
 points=list(g)
 for t in tracks:
  if t['type']=='PCB_VIA':continue
  a=node(t['start'],t['layer']);b=node(t['end'],t['layer']);length=distance(a,b)
  if length==0:continue
  for c in points:
   if c[2]==t['layer'] and abs(distance(a,c)+distance(c,b)-length)<1e-5:edge(a,c,distance(a,c));edge(c,b,distance(c,b))
 for p in pads.values():
  if p['net']!=net:continue
  ns=[node(p['xy'],l) for l in p['layers'] if l in cu]
  for a,b in zip(ns,ns[1:]):edge(a,b,0)
  for n in ns:
   for c in points:
    if c[2]==n[2] and inpad(p,c):edge(c,n,distance(c,n))
 cache[net]=(g,vias);return g,vias
def walk(source,target=None,first_via=False):
 p=pads[source];g,vias=graph(p['net']);s=node(p['xy'],'F.Cu');goals=set()
 if first_via:
  goals={node(v['start'],l) for v in vias for l in cu}
 else:
  q=pads[target];assert p['net']==q['net'];goals={node(q['xy'],l) for l in q['layers'] if l in cu}
 heap=[(0,s)];best={s:0};prev={}
 while heap:
  length,n=heapq.heappop(heap)
  if length>best[n]+1e-8:continue
  if n in goals:
   path=[n]
   while path[-1]!=s:path.append(prev[path[-1]])
   path.reverse()
   return {'from':'.'.join(source),'to':'first via' if first_via else '.'.join(target),'net':p['net'],'length_mm':round(length,6),'transitions':sum(a[2]!=b[2] for a,b in zip(path,path[1:])),'path':path}
  for c,w in g.get(n,{}).items():
   v=length+w
   if v<best.get(c,1e20):best[c]=v;prev[c]=n;heapq.heappush(heap,(v,c))
 return {'from':'.'.join(source),'to':str(target),'NOT_FOUND':True}
pairs=[(('U1',pin),(c,'1')) for pin,c in [('24','C29'),('24','C30'),('24','C42'),('28','C24'),('30','C25'),('55','C26'),('55','C27'),('26','C28'),('54','C36'),('59','C34'),('50','C40'),('48','C39')]]
pairs+=[(('C37','1'),('C36','1')),(('C9','1'),('U1','1')),(('C9','1'),('U1','15'))]
pairs+=[((u,p),(r,'1')) for u,p,r in [('U4','13','R41'),('U4','12','R42'),('U4','11','R43'),('U5','13','R44'),('U5','12','R45'),('U5','11','R46'),('U4','5','R47'),('U5','5','R48')]]
routes=[walk(a,b) for a,b in pairs]
returns=[walk((r,'2'),first_via=True) for r in ['C24','C25','C26','C27','C28','C29','C30','C31','C32','C33','C34','C35','C36','C39','C40','C43','C44','C45','C46']]
returns+=[walk(('U1',p),first_via=True) for p in ['20','23','25','32','33','49','51','53','57','58']]
result={'method':__doc__,'routes':routes,'returns':returns,'board_size_mm':[88,90],
 'track_counts_by_layer':dict(collections.Counter(t['layer'] for t in d['tracks'] if t['type']!='PCB_VIA')),
 'trace_width_counts_mm':dict(collections.Counter(t['width'] for t in d['tracks'] if t['type']!='PCB_VIA'))}
(base/'geometry-measurements.json').write_text(json.dumps(result,indent=2)+'\n')
for r in routes:print(r['from'],'->',r['to'],r.get('length_mm'),r.get('transitions'))
print('Ground stubs:')
for r in returns:print(r['from'],r.get('length_mm'),r.get('path',[[]])[-1])
