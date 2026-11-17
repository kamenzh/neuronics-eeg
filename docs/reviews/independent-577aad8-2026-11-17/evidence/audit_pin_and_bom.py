#!/usr/bin/env python3
"""Compare fresh netlist/PCB against a manually transcribed ADS1299 pin contract.
The contract below is transcribed from TI SBAS499C pp5-7, not design.json.
This checks identity/connectivity; physical assembly and IC performance are not tested.
"""
from pathlib import Path
import csv,json,xml.etree.ElementTree as E
base=Path(__file__).parent
repo=base.parents[3]
r=E.parse(base/'fresh.net.xml').getroot()
board=json.loads((base/'saved-board.json').read_text())
comps={c.get('ref'):c for c in r.findall('components/comp')}
nodes={}
for net in r.findall('nets/net'):
 for n in net.findall('node'):nodes[(n.get('ref'),n.get('pin'))]=(net.get('name'),n.get('pinfunction'))
fp={f['ref']:f for f in board['footprints']}
pads={p['number']:p for p in fp['U1']['pads']}
expected={}
for ch in range(1,9):
 n=17-2*ch
 expected[n]=(f'IN{ch}N','REF_FILTERED','Shared reference; MISC1.SRB1 and channel SRB2 off')
 expected[n+1]=(f'IN{ch}P',f'EEG{ch}','Recording input; positive minus shared reference')
expected.update({17:('SRB1','OPEN','Unused internal switch disabled'),18:('SRB2','OPEN','Unused internal switches disabled'),
 19:('AVDD','AVDD_5V','Shared AVDD network, C31-C36 1uF each to GND; see routing evidence'),20:('AVSS','GND','Analog ground'),21:('AVDD','AVDD_5V','Shared AVDD network, C31-C36 1uF each to GND; see routing evidence'),22:('AVDD','AVDD_5V','Shared AVDD network, C31-C36 1uF each to GND; see routing evidence'),23:('AVSS','GND','Analog ground'),24:('VREFP','VREFP','C29/C42 22uF each and C30 100nF to GND; enable internal reference'),25:('VREFN','GND','Internal reference negative to AVSS'),26:('VCAP4','VCAP4','C28 1uF to GND'),27:('NC','OPEN','Datasheet requires open'),28:('VCAP1','VCAP1','C24 100uF positive pad1; negative pad2 GND'),29:('NC','OPEN','Datasheet requires open'),30:('VCAP2','VCAP2','C25 1uF to GND'),31:('RESV1','GND','Direct DGND connection required'),32:('AVSS','GND','Analog ground'),33:('DGND','GND','Digital ground'),34:('DIN','SPI_MOSI','U4 B2Y through R42 33 ohm; R35 10k down'),35:('PWDN','ADS_PWDN_N','U5 B3Y through R46; R32 10k down'),36:('RESET','ADS_RESET_N','U5 B1Y through R44; R31 10k down'),37:('CLK','OPEN','Internal oscillator, CLK_EN=0'),38:('START','ADS_START','U5 B2Y through R45; R33 10k down'),39:('CS','ADS_CS_N','U4 B3Y through R43; R30 10k down'),40:('SCLK','SPI_SCLK','U4 B1Y through R41; R34 10k down'),41:('DAISY_IN','GND','Unused daisy-chain input'),42:('GPIO1','GPIO1_PD','R37 10k to GND; firmware input'),43:('DOUT','SPI_MISO','U4 B4 input'),44:('GPIO2','GPIO2_PD','R38 10k to GND; firmware input'),45:('GPIO3','GPIO3_PD','R39 10k to GND; firmware input'),46:('GPIO4','GPIO4_PD','R40 10k to GND; firmware input'),47:('DRDY','ADS_DRDY_N','U5 B4 input'),48:('DVDD','DVDD_3V3','C39 1uF and C41 100nF'),49:('DGND','GND','Digital ground'),50:('DVDD','DVDD_3V3','C40 1uF; local supply'),51:('DGND','GND','Digital ground'),52:('CLKSEL','CLKSEL_PU','R36 10k to DVDD; internal oscillator'),53:('AVSS1','GND','Analog ground'),54:('AVDD1','AVDD_5V','C36 1uF; distinct branch from C37'),55:('VCAP3','VCAP3','C26 1uF plus C27 100nF to GND'),56:('AVDD','AVDD_5V','C35 1uF to GND'),57:('AVSS','GND','Analog ground'),58:('AVSS','GND','Charge-pump ground'),59:('AVDD','AVDD_5V','C34 1uF to GND; charge-pump supply'),60:('BIASREF','OPEN','Internal midrail reference selected; external pin unused'),61:('BIASINV','BIASINV','R20 1M || C10 1.5nF from BIASOUT'),62:('BIASIN','GND','Unused bias-measurement mux; BIAS_MEAS=0'),63:('BIASOUT','BIASOUT','Feedback plus R21/R22 to bias contact'),64:('Reserved','OPEN','Datasheet requires open')})
rows=[]
for pin,(fn,net,note) in sorted(expected.items()):
 actual,actualfn=nodes[('U1',str(pin))];p=pads[str(pin)]
 ok=(actual.startswith('unconnected-') if net=='OPEN' else actual==net) and actual==p['net']
 rows.append(dict(pin=pin,manufacturer_function=fn,expected_net=net,netlist_function=actualfn,netlist_net=actual,pcb_net=p['net'],x_mm=p['xy'][0],y_mm=p['xy'][1],result='MATCH' if ok else 'MISMATCH',basis='TI SBAS499C pp5-7',notes=note))
with (base/'ADS1299-pin-audit.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');w.writeheader();w.writerows(rows)
# The actual net names on the four GPIO resistor links are deliberately checked,
# rather than permitting any net simply because the generator uses it.
parts=json.loads((repo/'hardware/parts.json').read_text())
cat={ref:g for g in parts['groups'] for ref in g['references']}
bom=list(csv.DictReader((repo/'hardware/bom/bom-review.csv').open()))
bom={b['Reference']:b for b in bom};br=[]
for ref,c in sorted(comps.items()):
 mpn=next((v.text for v in c.findall('fields/field') if v.get('name')=='Candidate_MPN'),None)
 b=bom[ref];g=cat[ref];f=fp[ref]
 ok=mpn==g['mpn']==b['Proposed_MPN'] and c.findtext('value')==f['value']==b['Value'] and c.findtext('footprint')==b['Footprint'] and c.findtext('footprint').split(':')[-1]==f['library']
 br.append(dict(ref=ref,value=c.findtext('value'),mpn=mpn,footprint=c.findtext('footprint'),sheet=c.find('sheetpath').get('names'),result='MATCH' if ok else 'MISMATCH'))
with (base/'BOM-CAD-crosscheck.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=br[0],lineterminator='\n');w.writeheader();w.writerows(br)
print(json.dumps({'ADS_pins':len(rows),'pin_mismatches':[a for a in rows if a['result']!='MATCH'],'electrical_components':len(br),'parts_groups':len(parts['groups']),'unique_MPNs':len({g['mpn'] for g in parts['groups']}),'BOM_mismatches':[a for a in br if a['result']!='MATCH']},indent=2))

if any(a['result']!='MATCH' for a in rows+br):
 raise SystemExit(1)
