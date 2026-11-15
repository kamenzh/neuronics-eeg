#!/usr/bin/python3
"""Independent read-only geometry audit of the saved PCB and fresh KiCad XML.

Does not import design.json or any generator/checker. Copper distances are
centerline approximations, including distances within pads, excluding via barrel
height. Plane path distance is not treated as an electrical/field simulation.
"""
import collections
import csv
import hashlib
import heapq
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import pcbnew as k

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BOARD = ROOT / 'hardware/kicad/neuronic.kicad_pcb'
b = k.LoadBoard(str(BOARD))
fps = {f.GetReference(): f for f in b.GetFootprints()}
COPPER = [k.F_Cu, k.In1_Cu, k.In2_Cu, k.B_Cu]

def xy(p):
    return (round(k.ToMM(p.x), 6), round(k.ToMM(p.y), 6))

def pad(ref, pin):
    return next(p for p in fps[ref].Pads() if p.GetNumber() == str(pin))

def node(layer, p):
    return (layer, round(p[0], 4), round(p[1], 4))

def dist(a, c):
    return math.hypot(a[0] - c[0], a[1] - c[1])

graphs = {}
def graph(net):
    if net in graphs:
        return graphs[net]
    g = collections.defaultdict(list)
    def add(a, c, weight, kind):
        g[a].append((c, weight, kind)); g[c].append((a, weight, kind))
    tracks = [t for t in b.GetTracks() if t.GetNetname() == net and not isinstance(t, k.PCB_VIA)]
    vias = [t for t in b.GetTracks() if t.GetNetname() == net and isinstance(t, k.PCB_VIA)]
    nodes = set()
    for t in tracks:
        nodes.add(node(t.GetLayer(), xy(t.GetStart())))
        nodes.add(node(t.GetLayer(), xy(t.GetEnd())))
    for t in vias:
        for layer in COPPER:
            nodes.add(node(layer, xy(t.GetPosition())))
    # Include junctions that lie in the middle of a straight trace.
    for t in tracks:
        a, c = xy(t.GetStart()), xy(t.GetEnd())
        dx, dy = c[0]-a[0], c[1]-a[1]
        ll = dx*dx + dy*dy
        candidates = []
        for n in nodes:
            if n[0] != t.GetLayer():
                continue
            u = ((n[1]-a[0])*dx + (n[2]-a[1])*dy)/ll
            if -.0001 <= u <= 1.0001:
                p = (a[0]+u*dx, a[1]+u*dy)
                # One imported REF junction is 0.0015 mm off centerline but
                # physically overlaps 0.15/0.20 mm copper; allow 0.002 mm.
                if dist(n[1:], p) < .002:
                    candidates.append((u, n))
        candidates.sort()
        for (_, n1), (_, n2) in zip(candidates, candidates[1:]):
            add(n1, n2, dist(n1[1:], n2[1:]), 'track')
    for t in vias:
        vnodes = [node(layer, xy(t.GetPosition())) for layer in COPPER]
        for n in vnodes[1:]:
            add(vnodes[0], n, 0, 'via')
    # KiCad route endpoints need not coincide with pad center.
    for f in fps.values():
        for p in f.Pads():
            if p.GetNetname() != net:
                continue
            anchor = ('pad', f.GetReference(), p.GetNumber())
            center = xy(p.GetPosition())
            for n in nodes:
                if p.IsOnLayer(n[0]) and p.HitTest(k.VECTOR2I(k.FromMM(n[1]), k.FromMM(n[2]))):
                    add(anchor, n, dist(center, n[1:]), 'pad')
    graphs[net] = g
    return g

def route(ref1, pin1, ref2, pin2):
    p1, p2 = pad(ref1, pin1), pad(ref2, pin2)
    assert p1.GetNetname() == p2.GetNetname()
    g = graph(p1.GetNetname())
    start, end = ('pad', ref1, str(pin1)), ('pad', ref2, str(pin2))
    counter = 0
    q, seen, prev = [(0, counter, start)], {start: 0}, {}
    while q:
        length, _, n = heapq.heappop(q)
        if length > seen[n]:
            continue
        if n == end:
            break
        for c, weight, kind in g[n]:
            score = length + weight
            if score + 1e-9 < seen.get(c, math.inf):
                seen[c], prev[c] = score, (n, kind)
                counter += 1
                heapq.heappush(q, (score, counter, c))
    if end not in seen:
        return {'from': f'{ref1}.{pin1}', 'to': f'{ref2}.{pin2}', 'error': 'No track-only path; may be plane-connected'}
    path, kinds = [end], []
    n = end
    while n != start:
        n, kind = prev[n]; path.append(n); kinds.append(kind)
    path.reverse(); kinds.reverse()
    return {'from': f'{ref1}.{pin1}', 'to': f'{ref2}.{pin2}', 'net': p1.GetNetname(),
            'length_mm': round(seen[end], 4), 'layer_transitions': kinds.count('via'),
            'pad_center_distance_mm': round(dist(xy(p1.GetPosition()), xy(p2.GetPosition())),4),
            'path': path}

targets = [(19,'C31'),(21,'C32'),(22,'C33'),(59,'C34'),(56,'C35'),(54,'C36'),
           (48,'C39'),(50,'C40'),(24,'C29'),(24,'C30'),(28,'C24'),(30,'C25'),
           (55,'C26'),(55,'C27'),(26,'C28')]
paths = [route('U1', pin, ref, 1) for pin, ref in targets]
paths += [route('U1', pin, 'U2', 5) for pin in [54,56,59,22,21,19]]
paths += [route('U1', pin, 'U3', 5) for pin in [48,50]]
paths += [route('U1', pin, 'J11', hp) for pin,hp in [(40,3),(34,4),(43,5),(39,6),(47,7),(36,8),(38,9),(35,10)]]
paths += [route('U1', pin, 'C9', 1) for pin in range(1,16,2)]
paths += [route('U1', pin, f'C{i}', 1) for i,pin in enumerate([16,14,12,10,8,6,4,2],1)]
for r in paths:
    fields = [r['from'], r['to'], r.get('length_mm'), r.get('layer_transitions')]
    if r.get('error'):
        fields.append(r['error'])
    print(*fields)

# Return traces to first directly reached GND via (no assumed plane shortcut).
g = graph('GND')
gndvias = {node(k.F_Cu, xy(v.GetPosition())) for v in b.GetTracks()
           if isinstance(v,k.PCB_VIA) and v.GetNetname() == 'GND'}
returns = []
refs = [('U1', str(i)) for i in [20,23,25,31,32,33,49,51,53,57,58]] + [(f'C{i}','2') for i in range(20,42)]
for ref,pin in refs:
    start=('pad',ref,pin);q=[(0,0,start)];seen={start:0};counter=0
    while q:
        length,_,n=heapq.heappop(q)
        if length>seen[n]:continue
        if n in gndvias:
            returns.append({'pad':f'{ref}.{pin}','pad_xy':xy(pad(ref,pin).GetPosition()),
                            'first_via_xy':n[1:],'track_length_mm':round(length,4)})
            break
        for c,w,kind in g[n]:
            score=length+w
            if score+1e-9<seen.get(c,math.inf):
                seen[c]=score;counter+=1;heapq.heappush(q,(score,counter,c))

# A manually transcribed manufacturer pin map, not generator metadata.
names={1:'IN8N',2:'IN8P',3:'IN7N',4:'IN7P',5:'IN6N',6:'IN6P',7:'IN5N',8:'IN5P',
       9:'IN4N',10:'IN4P',11:'IN3N',12:'IN3P',13:'IN2N',14:'IN2P',15:'IN1N',16:'IN1P',
       17:'SRB1',18:'SRB2',19:'AVDD',20:'AVSS',21:'AVDD',22:'AVDD',23:'AVSS',24:'VREFP',25:'VREFN',
       26:'VCAP4',27:'NC',28:'VCAP1',29:'NC',30:'VCAP2',31:'RESV1',32:'AVSS',33:'DGND',34:'DIN',
       35:'PWDN',36:'RESET',37:'CLK',38:'START',39:'CS',40:'SCLK',41:'DAISY_IN',42:'GPIO1',43:'DOUT',
       44:'GPIO2',45:'GPIO3',46:'GPIO4',47:'DRDY',48:'DVDD',49:'DGND',50:'DVDD',51:'DGND',52:'CLKSEL',
       53:'AVSS1',54:'AVDD1',55:'VCAP3',56:'AVDD',57:'AVSS',58:'AVSS',59:'AVDD',60:'BIASREF',
       61:'BIASINV',62:'BIASIN',63:'BIASOUT',64:'Reserved'}
xml=ET.parse(OUT/'neuronic.net.xml').getroot()
nets={(n.attrib['ref'],n.attrib['pin']):net.attrib['name'] for net in xml.findall('nets/net') for n in net.findall('node')}
lib=next(l for l in xml.findall('libparts/libpart') if l.attrib['part']=='ADS1299IPAG')
sch_names={p.attrib['num']:p.attrib['name'] for p in lib.findall('pins/pin')}
rows=[]
for i in range(1,65):
    p=pad('U1',i);sn=sch_names[str(i)].replace('~{','').replace('}','').lower()
    rows.append({'pin':i,'ti_name':names[i],'schematic_name':sch_names[str(i)],'name_matches_ti':sn==names[i].lower(),
                 'net_schematic':nets[('U1',str(i))],'net_pcb':p.GetNetname(),'parity':nets[('U1',str(i))]==p.GetNetname(),
                 'x_mm':xy(p.GetPosition())[0],'y_mm':xy(p.GetPosition())[1]})
with (OUT/'ads1299-64-pin-contract.csv').open('w') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)

inventory=collections.defaultdict(lambda:{'length_mm':0,'vias':0,'layers':set()})
for t in b.GetTracks():
    item=inventory[t.GetNetname()]
    if isinstance(t,k.PCB_VIA):item['vias']+=1
    else:item['length_mm']+=k.ToMM(t.GetLength());item['layers'].add(b.GetLayerName(t.GetLayer()))
for v in inventory.values():v['length_mm']=round(v['length_mm'],4);v['layers']=sorted(v['layers'])
result={'board_sha256':hashlib.sha256(BOARD.read_bytes()).hexdigest(),
        'method':__doc__,'pin_count':len(rows),'pin_name_failures':[r for r in rows if not r['name_matches_ti']],
        'pcb_parity_failures':[r for r in rows if not r['parity']],
        'point_to_point_routes':paths,'ground_return_traces':returns,'net_inventory':dict(inventory)}
nearest=[]
for pin in [19,21,22,54,56,59,48,50]:
    net=pad('U1',pin).GetNetname()
    choices=[]
    for ref in fps:
        if ref.startswith('C') and pad(ref,1).GetNetname()==net and pad(ref,2).GetNetname()=='GND':
            r=route('U1',pin,ref,1)
            if 'length_mm' in r:choices.append(r)
    choices.sort(key=lambda r:r['length_mm'])
    nearest.append({'pin':pin,'nearest_three':choices[:3]})
    print('Nearest bypasses U1.'+str(pin),[(r['to'],r['length_mm']) for r in choices[:3]])
result['nearest_same_net_bypasses']=nearest
(OUT/'independent-geometry.json').write_text(json.dumps(result,indent=2)+'\n')
print('64-pin names/PCB parity failures:',len(result['pin_name_failures']),len(result['pcb_parity_failures']))
