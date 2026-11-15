#!/usr/bin/env python3
"""Inventory saved copper and basic routing boundaries; KiCad DRC is separate."""
import json,collections,math
from pathlib import Path
import pcbnew as k
ROOT=Path(__file__).resolve().parents[1]
b=k.LoadBoard(str(ROOT/'hardware/kicad/neuronic.kicad_pcb'))
tracks=[t for t in b.GetTracks() if type(t)!=k.PCB_VIA]
vias=[t for t in b.GetTracks() if type(t)==k.PCB_VIA]
by_layer=collections.Counter(b.GetLayerName(t.GetLayer()) for t in tracks)
by_net=collections.defaultdict(lambda:{'track_length_mm':0,'via_count':0,'layers':set(),'x_min_mm':1e9,'x_max_mm':-1e9})
for t in tracks:
 n=by_net[t.GetNetname()];n['track_length_mm']+=k.ToMM(t.GetLength());n['layers'].add(b.GetLayerName(t.GetLayer()))
 n['x_min_mm']=min(n['x_min_mm'],k.ToMM(t.GetStart().x),k.ToMM(t.GetEnd().x));n['x_max_mm']=max(n['x_max_mm'],k.ToMM(t.GetStart().x),k.ToMM(t.GetEnd().x))
for t in vias:by_net[t.GetNetname()]['via_count']+=1
for n in by_net.values():n['layers']=sorted(n['layers']);n['track_length_mm']=round(n['track_length_mm'],3)
zones=[{'net':z.GetNetname(),'layer':b.GetLayerName(z.GetLayer()),'filled':z.IsFilled()} for z in b.Zones()]
digital=['SPI_MOSI','SPI_MISO','SPI_SCLK','ADS_CS_N','ADS_DRDY_N','ADS_RESET_N','ADS_START','ADS_PWDN_N']
digital += ['HOST_'+n for n in digital]+['BUF_'+n for n in ['SPI_MOSI','SPI_SCLK','ADS_CS_N','ADS_RESET_N','ADS_START','ADS_PWDN_N']]+['BUF_HOST_SPI_MISO','BUF_HOST_ADS_DRDY_N','IF_EN']
checks=[('Real tracks and vias exist',len(tracks)>0 and len(vias)>0),('Dedicated In1 ground plane has no tracks',not any(t.GetLayer()==k.In1_Cu for t in tracks)),('Ground plane and crossover-layer ground fill are filled',len(zones)==2 and {z['layer'] for z in zones}=={'In1.Cu','In2.Cu'} and all(z['net']=='GND' and z['filled'] for z in zones)),('All expected digital nets contain copper',all(n in by_net and by_net[n]['track_length_mm']>0 for n in digital)),('Host digital signals stay right of x=103mm, away from left-side inputs',all(n in by_net and by_net[n]['x_min_mm']>=103 for n in digital))]
result={'manufacture_ready':False,'checks':[{'name':n,'passed':bool(ok)} for n,ok in checks],'tracks':len(tracks),'vias':len(vias),'zones':zones,'tracks_by_layer':by_layer,'nets':dict(sorted(by_net.items())),'scope':'Copper inventory and coarse region checks. Not a noise, return-current, fault or impedance validation.'}
(ROOT/'hardware/validation/routing-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(f'{len(tracks)} tracks, {len(vias)} vias, {len(zones)} zones; routing checks {sum(ok for _,ok in checks)}/{len(checks)}')
for n,ok in checks:
 if not ok:print('FAIL:',n)
raise SystemExit(0 if all(ok for _,ok in checks) else 1)
