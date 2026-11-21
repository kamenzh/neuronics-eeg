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
check('All 109 physical components exported by KiCad',set(parts)==set(comps) and len(parts)==109)
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
for ref,rail in [('U2','AVDD_5V'),('U3','DVDD_3V3')]:
    for pin,net in {'1':'VBAT','2':'GND','3':'VBAT','4':'GND','5':rail}.items():
        check(f'TI fixed TPS7A24 DBV contract {ref}.{pin}',actual.get((ref,pin))==net)
    check(f'{ref} uses SOT-23-5 footprint',comps[ref].findtext('footprint')=='Neuronic:SOT-23-5')
for ref, rail in [('R50','AVDD_5V'),('R51','DVDD_3V3')]:
    check(f'{ref} regulator discharge path', comps[ref].findtext('value')=='1k' and actual.get((ref,'1'))==rail and actual.get((ref,'2'))=='GND')
for i in range(1,11):
    check(f'J{i} selected touchproof jack footprint',comps[f'J{i}'].findtext('footprint')=='Neuronic:P1_36619_Touchproof_RA')
for i in range(1,10):
    check(f'Clamp D{i}: A1=GND / K2=5V / midpoint=signal',
      actual.get((f'D{i}','1'))=='GND' and actual.get((f'D{i}','2'))=='AVDD_5V' and
      actual.get((f'D{i}','3'))==(f'EEG{i}' if i<9 else 'REF_FILTERED'))
check('J11 pin 11 powers buffer host ports only',actual.get(('J11','11'))=='HOST_3V3')
check('J11 pin 12 is interface enable',actual.get(('J11','12'))=='IF_EN')
buffer_contract={
 'U4':{'1':'HOST_3V3','2':'HOST_SPI_SCLK','3':'HOST_SPI_MOSI','4':'HOST_ADS_CS_N',
       '5':'BUF_HOST_SPI_MISO','7':'GND','8':'IF_EN','10':'SPI_MISO',
       '11':'BUF_ADS_CS_N','12':'BUF_SPI_MOSI','13':'BUF_SPI_SCLK','14':'DVDD_3V3'},
 'U5':{'1':'HOST_3V3','2':'HOST_ADS_RESET_N','3':'HOST_ADS_START','4':'HOST_ADS_PWDN_N',
       '5':'BUF_HOST_ADS_DRDY_N','7':'GND','8':'IF_EN','10':'ADS_DRDY_N',
       '11':'BUF_ADS_PWDN_N','12':'BUF_ADS_START','13':'BUF_ADS_RESET_N','14':'DVDD_3V3'}}
for ref,contract in buffer_contract.items():
    for pin,net in contract.items():check(f'TI TXU0304 PW contract {ref}.{pin}',actual.get((ref,pin))==net)
    for pin in ['6','9']:check(f'{ref}.{pin} NC',actual.get((ref,pin),'').startswith('unconnected-'))
for ref in ['R30','R31','R32','R33','R34','R35','R49']:
    check(f'{ref} 10k default-low value',comps[ref].findtext('value')=='10k')
check('Two parallel reference bulk capacitors',all(actual.get((r,'1'))=='VREFP' and actual.get((r,'2'))=='GND' for r in ['C29','C42']))
for pin in ['17','18']:
    check(f'Unused SRB pin {pin} is NC',actual.get(('U1',pin),'').startswith('unconnected-'))
interface=json.loads((ROOT/'hardware/interface.json').read_text())
for entry in interface['j11']:
    if entry['net']:
        check(f"Controller header J11.{entry['pin']}",actual.get(('J11',str(entry['pin'])))==entry['net'])
gpios=[p['gpio'] for p in interface['j11'] if p['gpio'] is not None]
check('Nine distinct controller signals including enable',len(gpios)==len(set(gpios))==9)
check('No reserved GPIO used',not(set(gpios)&set(interface['controller']['reserved_gpio'])))
native_contract={3:(5,'D2'),4:(38,'D11'),5:(47,'D12'),6:(21,'D10'),7:(18,'D9'),8:(17,'D8'),9:(10,'D7'),10:(9,'D6'),12:(6,'D3')}
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
