#!/usr/bin/env python3
"""Compare the saved PCB's pads against KiCad's actual exported netlist.

Uses pcbnew (run with KiCad's compatible Python environment). This checks
logical pad/net parity, not trace continuity or layout suitability.
"""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import pcbnew as k
ROOT=Path(__file__).resolve().parents[1]
tree=ET.parse(ROOT/'hardware/validation/neuronic.net.xml').getroot()
comps={x.attrib['ref']:x for x in tree.findall('components/comp')}
expected={}
for net in tree.findall('nets/net'):
    for node in net.findall('node'):
        expected[(node.attrib['ref'],node.attrib['pin'])]=net.attrib['name']
b=k.LoadBoard(str(ROOT/'hardware/kicad/neuronic.kicad_pcb'))
fps={fp.GetReference():fp for fp in b.GetFootprints()}
issues=[]
check_count=0
for ref,c in comps.items():
    fp=fps.get(ref)
    check_count+=1
    if fp is None:issues.append(f'Missing footprint {ref}');continue
    libid=fp.GetFPID()
    foundid=str(libid.GetLibNickname())+':'+str(libid.GetLibItemName())
    if foundid!=c.findtext('footprint'):issues.append(f'{ref} footprint {foundid} != {c.findtext("footprint")}')
    for pad in fp.Pads():
        pin=pad.GetNumber();want=expected.get((ref,pin),'');got=pad.GetNetname()
        check_count+=1
        if want.startswith('unconnected-'):want=''
        if got!=want:issues.append(f'{ref}.{pin}: PCB={got!r}, netlist={want!r}')
actual_ids=set(fps)-set(comps)
if actual_ids!={'H1','H2','H3','H4'}:issues.append(f'Unexpected extra footprints: {sorted(actual_ids)}')
result={'checks':check_count,'issues':issues,'passed':not issues,'pcb_footprints':len(fps),
 'mechanical_only':['H1','H2','H3','H4'],'scope':'Saved physical pad/footprint net parity, not routing continuity or KiCad full schematic parity DRC.'}
(ROOT/'hardware/validation/board-net-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(f'PCB pad/net parity: {check_count} checks, {len(issues)} issues')
for issue in issues:print(issue)
sys.exit(bool(issues))
