#!/usr/bin/env python3
"""Audit the actual KiCad-exported netlist against the source and pin contract.

Not a replacement for ERC, DRC, analog review or physical measurements.
"""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
src=json.loads((ROOT/'hardware/design.json').read_text())
tree=ET.parse(ROOT/'hardware/validation/neuronic.net.xml').getroot()
comps={x.attrib['ref']:x for x in tree.findall('components/comp')}
actual={}
for net in tree.findall('nets/net'):
    for node in net.findall('node'):
        actual[(node.attrib['ref'],node.attrib['pin'])]=net.attrib['name']
checks=[]
def check(name,condition):
    checks.append({'name':name,'passed':bool(condition)})
    if not condition: print('FAIL:',name)

parts={p['ref']:p for p in src['parts']}
check('All 91 physical components exported by KiCad',set(parts)==set(comps) and len(parts)==91)
for p in parts.values():
    check(f"{p['ref']} footprint matches schematic",comps[p['ref']].findtext('footprint')==p['fp'])
    for pin,net in p['nets'].items():
        found=actual.get((p['ref'],pin),'')
        check(f"{p['ref']}.{pin} -> {net or 'NC'}",found==net if net else found.startswith('unconnected-') or not found)

# This physical pin contract is deliberately independent of the generator's map.
pin_contract={
    '16':'EEG1','14':'EEG2','12':'EEG3','10':'EEG4','8':'EEG5','6':'EEG6','4':'EEG7','2':'EEG8',
    '1':'REF_FILTERED','3':'REF_FILTERED','5':'REF_FILTERED','7':'REF_FILTERED',
    '9':'REF_FILTERED','11':'REF_FILTERED','13':'REF_FILTERED','15':'REF_FILTERED',
    '24':'VREFP','25':'GND','26':'VCAP4','28':'VCAP1','30':'VCAP2',
    '31':'GND','33':'GND','34':'SPI_MOSI','35':'ADS_PWDN_N','36':'ADS_RESET_N',
    '38':'ADS_START','39':'ADS_CS_N','40':'SPI_SCLK','41':'GND','43':'SPI_MISO',
    '47':'ADS_DRDY_N','48':'DVDD_3V3','49':'GND','50':'DVDD_3V3','51':'GND',
    '52':'CLKSEL_PU','53':'GND','54':'AVDD_5V','55':'VCAP3','61':'BIASINV','62':'GND','63':'BIASOUT'}
for pin,net in pin_contract.items():check(f'TI pin contract U1.{pin}',actual.get(('U1',pin))==net)
for pin in ['19','21','22','56','59']:check(f'Analog rail U1.{pin}',actual.get(('U1',pin))=='AVDD_5V')
for pin in ['20','23','32','57','58']:check(f'Analog return U1.{pin}',actual.get(('U1',pin))=='GND')
for i in range(1,10):
    check(f'Clamp D{i}: A1=GND / K2=5V / midpoint=signal',
      actual.get((f'D{i}','1'))=='GND' and actual.get((f'D{i}','2'))=='AVDD_5V' and
      actual.get((f'D{i}','3'))==(f'EEG{i}' if i<9 else 'REF_FILTERED'))
check('J11 pin 11 carries no power',actual.get(('J11','11'),'').startswith('unconnected-'))
for pin in ['17','18']:
    check(f'Unused SRB pin {pin} is NC',actual.get(('U1',pin),'').startswith('unconnected-'))
interface=json.loads((ROOT/'hardware/interface.json').read_text())
for entry in interface['j11']:
    if entry['net']:
        check(f"Controller header J11.{entry['pin']}",actual.get(('J11',str(entry['pin'])))==entry['net'])
gpios=[p['gpio'] for p in interface['j11'] if p['gpio'] is not None]
check('Eight distinct controller signals',len(gpios)==len(set(gpios))==8)
check('No reserved GPIO used',not(set(gpios)&set(interface['controller']['reserved_gpio'])))
native_contract={3:(5,'D2'),4:(38,'D11'),5:(47,'D12'),6:(21,'D10'),7:(18,'D9'),8:(17,'D8'),9:(10,'D7'),10:(9,'D6')}
for entry in interface['j11']:
    if entry['pin'] in native_contract:
        check(f"Verified Nano label/GPIO J11.{entry['pin']}",(entry['gpio'],entry['board_label'])==native_contract[entry['pin']])
check('Direct shared reference firmware contract',interface['acquisition']['misc1']==0 and not interface['acquisition']['srb2_enabled'])
check('VCAP1 polarized capacitor orientation',actual.get(('C24','1'))=='VCAP1' and actual.get(('C24','2'))=='GND')
check('Bias feedback resistor and capacitor are in parallel',
      actual[('R20','1')]==actual[('C10','1')]=='BIASOUT' and actual[('R20','2')]==actual[('C10','2')]=='BIASINV')
result={'passed':sum(x['passed'] for x in checks),'total':len(checks),'checks':checks,
  'scope':'KiCad-exported connectivity and footprint audit. Does not prove electrical behavior or safety.'}
(ROOT/'hardware/validation/connectivity-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(f"Connectivity checks: {result['passed']}/{result['total']}")
sys.exit(0 if result['passed']==result['total'] else 1)
