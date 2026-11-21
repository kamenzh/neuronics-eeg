"""Linear DC envelope, conditional on the listed sources/returns and actual netlist."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/validation'

def analyze(netlist):
    tree = ET.parse(netlist)
    nets = {(n.get('ref'), n.get('pin')): net.get('name')
            for net in tree.findall('.//nets/net') for n in net.findall('node')}
    comps = {c.get('ref'): c.findtext('value') for c in tree.findall('.//components/comp')}
    def resistor(ref, value, pins):
        actual = [nets[ref, str(i)] for i in (1, 2)]
        if actual != pins or comps[ref] != value:
            raise ValueError(f'{ref}: expected {value} {pins}, found {comps[ref]} {actual}')
        return float(value[:-1]) * {'R':1, 'k':1000}[value[-1]]
    paths = []
    for i in range(1,10):
        raw = nets[f'J{i}', '1']
        mid = nets[f'R{2*i-1}', '2']
        out = f'EEG{i}' if i < 9 else 'REF_FILTERED'
        assert mid == f'INPUT_RMID_{i}' and raw == 'CONTACT_'+(str(i) if i<9 else 'REF')
        paths.append((resistor(f'R{2*i-1}', '100k', [raw,mid]),
                      resistor(f'R{2*i}', '100k', [mid,out])))
    paths.append((resistor('R21','499k',['BIASOUT','BIAS_LIMIT_MID']),
                  resistor('R22','499k',['BIAS_LIMIT_MID',nets['J10','1']])))
    bleeds = [resistor(ref,'499R',['AVDD_5V','GND']) for ref in ('R50','R52')]
    cases = {'intact': (None, None)}
    for i in range(len(paths)):
        for j in (0,1):
            cases[f'contact_{i+1}_series_{j+1}_short'] = ((i,j),None)
    for i in range(len(bleeds)):
        cases[f'bleed_{i+1}_open'] = (None,i)
    results = []
    for name,(short,opened) in cases.items():
        resistances = [sum(r*.98 for j,r in enumerate(pair) if (i,j)!=short)
                       for i,pair in enumerate(paths)]
        sink = sum(1/(r*1.02) for i,r in enumerate(bleeds) if i!=opened)
        for n in [1,9,10]:
            for source in [5.1,10.2]:
                drive = sum(1/r for r in resistances[:n])
                v = source*drive/(drive+sink)
                results.append(dict(fault=name, driven_contacts=n, source_v=source,
                                    avdd_v=v, peak_branch_current_ua=(source-v)/min(resistances[:n])*1e6))
    worst = max(results,key=lambda row:row['avdd_v'])
    if worst['avdd_v'] >= .3: raise ValueError(f'DC envelope crosses the LDO stress limit: {worst}')
    return dict(description='Steady positive DC driving contacts relative to PCB GND, VIN held at 0 V. Ideal zero-drop clamps feed AVDD, including a conservative path from BIASOUT. Other rail loads omitted. Independent ±2% resistor engineering envelope, one listed resistor fault at a time. Limits concern the LDO only.',worst=worst,
                exclusions=['Stored charge and fast transients','open common copper/ground','loss of both bleeds','fault ahead of series resistors','negative injection, ESD and external mains','USB or instrument ground leakage','person safety'],
                cases=results)

if __name__ == '__main__':
    result=analyze(OUT/'neuronic.net.xml')
    (OUT/'contact-faults.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f"{len(result['cases'])} DC cases. Worst AVDD {result['worst']['avdd_v']:.4f} V.")
