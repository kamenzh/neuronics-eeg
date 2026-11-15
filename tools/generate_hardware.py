#!/usr/bin/env python3
"""Generate Neuronic's review checkpoint. Not a manufacturing release.

Python stdlib only for schematic/BOM. --board also requires KiCad pcbnew.
Set KICAD_DATA to the KiCad share directory, e.g. /usr/share/kicad.
Existing generated files require --overwrite. Routed boards are never replaced.
"""
import argparse
import csv
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/kicad'
DATA = Path(os.environ.get('KICAD_DATA', '/usr/share/kicad'))
NS = uuid.UUID('b314a604-c394-4051-a09e-9626c22cb806')
REVISION = 'A0.2-routed-bench'
def uid(key): return str(uuid.uuid5(NS, key))
def q(s): return json.dumps(str(s))
def n(x): return f'{x:.4f}'.rstrip('0').rstrip('.') if x else '0'
def grid(x): return round(round(x / 1.27) * 1.27, 4)

def block(text, start):
    level = 0
    quoted = escaped = False
    for i in range(start, len(text)):
        c = text[i]
        if quoted:
            if escaped: escaped = False
            elif c == '\\': escaped = True
            elif c == '"': quoted = False
        elif c == '"': quoted = True
        elif c == '(': level += 1
        elif c == ')':
            level -= 1
            if not level: return text[start:i+1]
    raise ValueError('Unclosed s-expression')

def lib_symbol(lib, name):
    text = (DATA / f'symbols/{lib}.kicad_sym').read_text()
    token = f'(symbol "{name}"'
    start = text.find(token)
    if start < 0: raise ValueError(f'Missing {lib}:{name}')
    s = block(text, start)
    if '(extends ' in s: raise ValueError('Use the base library symbol explicitly')
    return s.replace(token, f'(symbol "{lib}:{name}"', 1)

LIB = {}
PARTS = []
SHEETS = {}
CATALOG = json.loads((ROOT/'hardware/parts.json').read_text())
BY_REF = {ref: p for p in CATALOG['groups'] for ref in p['references']}

def custom_symbol(name, pins, halfwidth=15.24, halfheight=12.7, desc=''):
    p = [f'(symbol "Neuronic:{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)',
         '(property "Reference" "U" (at 0 0 0) (effects (font (size 1.27 1.27))))',
         f'(property "Value" {q(name)} (at 0 0 0) (effects (font (size 1.27 1.27))))',
         f'(property "ki_description" {q(desc)} (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
         f'(symbol "{name}_0_1" (rectangle (start {-halfwidth} {halfheight}) (end {halfwidth} {-halfheight}) (stroke (width 0.254) (type default)) (fill (type background))))',
         f'(symbol "{name}_1_1"']
    for num, pname, typ, x, y, angle in pins:
        p.append(f'(pin {typ} line (at {n(x)} {n(y)} {angle}) (length 2.54) (name {q(pname)} (effects (font (size 1.016 1.016)))) (number {q(num)} (effects (font (size 1.016 1.016)))))')
    p += ['))']
    return '\n'.join(p)

PIN_NAMES = {
    **{str(16-2*i): f'IN{i+1}P' for i in range(8)},
    **{str(15-2*i): f'IN{i+1}N' for i in range(8)},
    '17':'SRB1', '18':'SRB2', '19':'AVDD', '20':'AVSS', '21':'AVDD', '22':'AVDD',
    '23':'AVSS', '24':'VREFP', '25':'VREFN', '26':'VCAP4', '27':'NC', '28':'VCAP1',
    '29':'NC', '30':'VCAP2', '31':'RESV1', '32':'AVSS', '33':'DGND', '34':'DIN',
    '35':'~{PWDN}', '36':'~{RESET}', '37':'CLK', '38':'START', '39':'~{CS}', '40':'SCLK',
    '41':'DAISY_IN', '42':'GPIO1', '43':'DOUT', '44':'GPIO2', '45':'GPIO3', '46':'GPIO4',
    '47':'~{DRDY}', '48':'DVDD', '49':'DGND', '50':'DVDD', '51':'DGND', '52':'CLKSEL',
    '53':'AVSS1', '54':'AVDD1', '55':'VCAP3', '56':'AVDD', '57':'AVSS', '58':'AVSS',
    '59':'AVDD', '60':'BIASREF', '61':'BIASINV', '62':'BIASIN', '63':'BIASOUT', '64':'RESERVED'}

def initialize():
    OUT.mkdir(parents=True, exist_ok=True)
    for lib, name in [('Device','R'), ('Device','C'), ('Device','C_Polarized'), ('Device','D_Schottky'),
                      ('Connector_Generic','Conn_01x01'), ('Connector_Generic','Conn_01x02'),
                      ('Connector_Generic','Conn_02x06_Odd_Even'), ('Device','Polyfuse'),
                      ('Switch','SW_SPST'), ('power','PWR_FLAG'),
                      ('Regulator_Linear','MCP1703Ax-330xxDB')]:
        LIB[f'{lib}:{name}'] = lib_symbol(lib, name)
    pins = []
    for i in range(1,65):
        side = i <= 32
        y = 39.37 - ((i-1) if side else (64-i))*2.54
        name = PIN_NAMES[str(i)]
        typ = 'input'
        if name.startswith(('AVDD','AVSS','DVDD','DGND')): typ='power_in'
        elif name in ['DOUT','~{DRDY}','BIASOUT'] or name.startswith('VCAP'): typ='output'
        elif name.startswith('GPIO') or name in ['SRB1','SRB2','VREFP','BIASINV']: typ='bidirectional'
        elif name in ['NC','RESERVED']: typ='no_connect'
        pins.append((str(i), name, typ, -22.86 if side else 22.86, y, 0 if side else 180))
    LIB['Neuronic:ADS1299IPAG'] = custom_symbol('ADS1299IPAG', pins, 20.32, 43.18,
        'TI ADS1299 eight-channel PAG64; pin numbers checked against SBAS499C table 6')
    LIB['Neuronic:TPS7A24_FIXED'] = custom_symbol('TPS7A24_FIXED', [('1','IN','power_in',-12.7,5.08,0),('2','GND','power_in',0,-10.16,90),('3','EN','input',-12.7,-2.54,0),('4','NC_GND','passive',5.08,-10.16,90),('5','OUT','power_out',12.7,5.08,180)],10.16,7.62,'TI TPS7A24 DBV fixed pin contract, SBVS386E table 5-1')
    LIB['Neuronic:BAV199'] = custom_symbol('BAV199', [
        ('1','A1','passive',-7.62,2.54,0), ('2','K2','passive',7.62,2.54,180),
        ('3','K1_A2','passive',0,-7.62,90)],5.08,5.08,
        'Series low leakage diodes: pin1 anode to GND, pin2 cathode to AVDD, pin3 input')

def symbol_pins(s):
    out=[]
    for m in re.finditer(r'\(pin\s+(?:input|output|bidirectional|tri_state|passive|free|unspecified|power_in|power_out|open_collector|open_emitter|no_connect)\s+',s):
        b=block(s,m.start())
        num=re.search(r'\(number "([^"]+)"',b).group(1)
        a=re.search(r'\(at ([\-\d.]+) ([\-\d.]+) ([\d.]+)\)',b)
        out.append((num,float(a[1]),float(a[2]),float(a[3])))
    return out

class Sheet:
    def __init__(self,name,title,page):
        self.name=name; self.title=title; self.page=page; self.id=uid(name); self.items=[]; self.used=set(); self.serial=0
        SHEETS[name]=self
    def ident(self):
        self.serial+=1; return uid(f'{self.name}-{self.serial}')
    def text(self,t,x,y,size=1.27):
        self.items.append(f'(text {q(t)} (at {n(x)} {n(y)} 0) (effects (font (size {size} {size})) (justify left)) (uuid {self.ident()}))')
    def wire(self,a,b):
        a=tuple(map(grid,a));b=tuple(map(grid,b))
        if a==b:return
        self.items.append(f'(wire (pts (xy {n(a[0])} {n(a[1])}) (xy {n(b[0])} {n(b[1])})) (stroke (width 0) (type default)) (uuid {self.ident()}))')
    def label(self,t,x,y,angle=0):
        x,y=grid(x),grid(y)
        self.items.append(f'(global_label {q(t)} (shape bidirectional) (at {n(x)} {n(y)} {angle}) (effects (font (size 1.016 1.016)) (justify {"left" if angle in [0,90] else "right"})) (uuid {self.ident()}) (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {n(x)} {n(y)} {angle}) (effects (font (size 1.016 1.016)) hide)))')
    def part(self,ref,lib,value,x,y,nets,fp='',angle=0,xy=None,rot=0,note='',mpn='',labels=True):
        x,y=grid(x),grid(y)
        candidate=BY_REF.get(ref)
        if fp:
            if candidate is None: raise ValueError(f'No candidate part for {ref}')
            mpn=candidate['mpn']
            value=candidate.get('value',value)
            fp=candidate.get('footprint',fp)
            note='; '.join(filter(None,[note,candidate.get('review')]))
        self.used.add(lib)
        symid=uid(ref)
        # Keep visible fields outside small symbols; use the symbol's angle so
        # horizontal resistors do not get overlapping vertical ref/value text.
        rx,ry,vx,vy=x+2.54,y-5.08,x+2.54,y-2.54
        justify=' (justify left)'
        if lib in ('Device:R','Device:C','Device:C_Polarized','Device:Polyfuse') and angle==0:
            rx,ry,vx,vy=x+2.54,y-2.54,x+2.54,y
        if angle==90:
            rx,ry,vx,vy=x,y-5.08,x,y-2.54
            justify=''
        if lib in ('Neuronic:BAV199','Connector_Generic:Conn_02x06_Odd_Even'):
            rx,ry,vx,vy=x,y-10.16,x,y-7.62
            justify=''
        if ref=='U1':justify=''
        field_angle=angle % 180
        self.items.append(f'(symbol (lib_id {q(lib)}) (at {n(x)} {n(y)} {angle}) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {symid})\n'
            f'(property "Reference" {q(ref)} (at {n(rx)} {n(ry)} {field_angle}) (effects (font (size 1.016 1.016)){justify}))\n'
            f'(property "Value" {q(value)} (at {n(vx)} {n(vy)} {field_angle}) (effects (font (size 1.016 1.016)){justify}))\n'
            f'(property "Footprint" {q(fp)} (at {n(x)} {n(y)} 0) (effects (font (size 1.016 1.016)) hide))\n'
            f'(property "Candidate_MPN" {q(mpn)} (at {n(x)} {n(y)} 0) (effects (font (size 1.016 1.016)) hide))\n'
            f'(instances (project "neuronic" (path "/{uid("neuronic")}' + ('' if self.name=='neuronic' else f'/{uid("sheet-"+self.name)}') + f'" (reference {q(ref)}) (unit 1)))))')
        theta=math.radians(angle)
        for num,px,py,pa in symbol_pins(LIB[lib]):
            wx=x+px*math.cos(theta)-py*math.sin(theta)
            wy=y-px*math.sin(theta)-py*math.cos(theta)
            net=nets.get(num)
            if net is None:
                self.items.append(f'(no_connect (at {n(wx)} {n(wy)}) (uuid {self.ident()}))')
                continue
            if not labels:continue
            outward=math.radians(pa+angle)
            end=(round(wx-5.08*math.cos(outward),4),round(wy+5.08*math.sin(outward),4))
            self.wire((wx,wy),end)
            if abs(math.cos(outward))<0.5:
                right=math.sin(outward)>0
                bent=(round(end[0]+(5.08 if right else -5.08),4),end[1])
                self.wire(end,bent)
                self.label(net,*bent,0 if right else 180)
            else:
                self.label(net,*end,180 if math.cos(outward)>0 else 0)
        p=dict(ref=ref,lib=lib,value=value,nets=nets,fp=fp,xy=xy,rot=rot,note=note,mpn=mpn,sheet=self.name,uuid=symid)
        if fp: PARTS.append(p)
        return p
    def save(self,root=False):
        lib='\n'.join(LIB[k] for k in sorted(self.used))
        txt=f'(kicad_sch (version 20250114) (generator eeschema) (uuid {self.id}) (paper "A3")\n(title_block (title {q(self.title)}) (date "2026-11-15") (rev "{REVISION}") (company "Neuronic") (comment 1 "BENCH DEVELOPMENT ONLY - NOT FOR BODY CONNECTION OR FABRICATION"))\n(lib_symbols\n{lib}\n)\n'+'\n'.join(self.items)
        if root: txt+='\n(sheet_instances (path "/" (page "1")))'
        txt+='\n)\n'
        (OUT/f'{self.name}.kicad_sch').write_text(txt)

    def local_label(self,t,x,y):
        self.label(t,x,y,0)

RFP='Neuronic:R_0805_2012Metric'
CFP='Neuronic:C_0805_2012Metric'

def add_rc(sh,ref,value,net1,net2,x,y,xy,kind='R',rot=0,note=''):
    if ref=='C24':kind='C_Polarized'
    fp=RFP if kind=='R' else ('Neuronic:CP_EIA-3528-21_Kemet-B' if ref=='C24' else CFP)
    return sh.part(ref,f'Device:{kind}',value,x,y,{'1':net1,'2':net2},fp,xy=xy,rot=rot,note=note)

def make_design():
    root=Sheet('neuronic','01 - ADS1299 core and SPI interface',1)
    inp=Sheet('inputs','02 - Eight channels and shared reference',2)
    power=Sheet('power','03 - Battery regulators, decoupling and bias',3)
    root.text('NEURONIC / A0.2 BENCH REVIEW',20,18,2)
    root.text('8 synchronous channels, 10 contacts. One ADS1299 contains both PGAs and ADCs.',20,25)
    root.text('Shared reference wires directly to all negative inputs. MISC1=0x00; CHnSET.SRB2=0. SRB1/SRB2 are NC.',20,32)
    nets={}
    for i in range(8):nets[str(16-2*i)]=f'EEG{i+1}';nets[str(15-2*i)]='REF_FILTERED'
    nets.update({'17':None,'18':None,'19':'AVDD_5V','20':'GND','21':'AVDD_5V','22':'AVDD_5V','23':'GND',
        '24':'VREFP','25':'GND','26':'VCAP4','27':None,'28':'VCAP1','29':None,'30':'VCAP2','31':'GND','32':'GND',
        '33':'GND','34':'SPI_MOSI','35':'ADS_PWDN_N','36':'ADS_RESET_N','37':None,'38':'ADS_START','39':'ADS_CS_N',
        '40':'SPI_SCLK','41':'GND','42':'GPIO1_PD','43':'SPI_MISO','44':'GPIO2_PD','45':'GPIO3_PD','46':'GPIO4_PD',
        '47':'ADS_DRDY_N','48':'DVDD_3V3','49':'GND','50':'DVDD_3V3','51':'GND','52':'CLKSEL_PU',
        '53':'GND','54':'AVDD_5V','55':'VCAP3','56':'AVDD_5V','57':'GND','58':'GND','59':'AVDD_5V',
        '60':None,'61':'BIASINV','62':'GND','63':'BIASOUT','64':None})
    root.part('U1','Neuronic:ADS1299IPAG','ADS1299IPAG',155,105,nets,'Neuronic:TQFP-64_10x10mm_P0.5mm',xy=(95,90),note='TI SBAS499C pin functions, unipolar 5 V, internal clock/reference',mpn='ADS1299IPAG')
    root.part('J11','Connector_Generic:Conn_02x06_Odd_Even','MCU_3V3_IO_ONLY',312,65,
        {'1':'GND','2':'GND','3':'SPI_SCLK','4':'SPI_MOSI','5':'SPI_MISO','6':'ADS_CS_N',
         '7':'ADS_DRDY_N','8':'ADS_RESET_N','9':'ADS_START','10':'ADS_PWDN_N','11':None,'12':'GND'},
        'Neuronic:PinHeader_2x06_P2.54mm_Vertical',xy=(130,86),note='Pin 11 NC. Signals/GND only; separate controller supply.')
    root.text('J11: board-neutral connector; not an ESP32 dev-board footprint.',258,93)
    root.text('Waveshare ESP32-S3-Nano; see hardware/interface.json.',258,100)
    root.text('External controller power/USB can join GND. No body-connected tests.',258,107)
    rnum=30
    for i,(net,rail) in enumerate([('ADS_CS_N','GND'),('ADS_RESET_N','GND'),('ADS_PWDN_N','GND'),('ADS_START','GND'),('SPI_SCLK','GND'),('SPI_MOSI','GND'),('CLKSEL_PU','DVDD_3V3'),('GPIO1_PD','GND'),('GPIO2_PD','GND'),('GPIO3_PD','GND'),('GPIO4_PD','GND')]):
        x=35+(i%6)*58;y=181+(i//6)*40
        add_rc(root,f'R{rnum+i}','100k' if i<6 else '10k',net,rail,x,y,(116+(i%4)*5,103+(i//4)*7))
    root.text('Default pulldowns keep host inputs low at startup. MCU must release PWDN/RESET and drive CS high after rails settle.',20,250)
    root.text('CONFIG1=0x96 (250 SPS, internal clock output disabled); MISC1=0x00; bias/lead-off disabled for initial bench tests.',20,257)
    for name,title,x in [('inputs','Input filters / CH1-8 / REF',25),('power','Power / bypass / bias drive',215)]:
        root.items.append(f'(sheet (at {x} 39.37) (size 170.18 12.7) (fields_autoplaced) (stroke (width 0.1524) (type default)) (fill (color 0 0 0 0)) (uuid {uid("sheet-"+name)}) (property "Sheetname" {q(title)} (at {x} 38 0) (effects (font (size 1.27 1.27)) (justify left bottom))) (property "Sheetfile" "{name}.kicad_sch" (at {x} 53 0) (effects (font (size 1.27 1.27)) (justify left top))) (instances (project "neuronic" (path "/{root.id}" (page "{SHEETS[name].page}")))))')

    inp.text('INPUT NETWORKS: P1 36619 touchproof jacks; verify physical cable fit before fabrication',18,16,1.8)
    inp.text('20k series + 1nF shunt: nominal RF pole 7.96 kHz. This is not the EEG bandpass. ADS1299 digital filter is still required.',18,24)
    inp.text('BAV199 + 20k: bounded low-energy bench faults only. Power-off backfeeding / body fault currents are not qualified.',18,31)
    for i in range(9):
        y=47+i*24
        out=f'EEG{i+1}' if i<8 else 'REF_FILTERED'
        raw=f'CONTACT_{i+1}' if i<8 else 'CONTACT_REF'
        mid=f'INPUT_RMID_{i+1}'
        inp.text(f'CH{i+1}' if i<8 else 'REFERENCE',18,y-5)
        inp.part(f'J{i+1}','Connector_Generic:Conn_01x01',f'CH{i+1}_TOUCHPROOF' if i<8 else 'REF_TOUCHPROOF',45,y,{'1':raw},'Neuronic:P1_36619_Touchproof_RA',angle=180,xy=(67.026,61+(7-i if i<8 else 8)*8.2),note='P1 36619-50 rev H; pad 1 signal, two unnumbered isolated dummy legs; physical sample fit required',labels=False)
        inp.part(f'R{i*2+1}','Device:R','10k',95,y,{'1':raw,'2':mid},RFP,angle=90,xy=(64,65+i*7),rot=90,note='Input series resistor, 1%',labels=False)
        inp.part(f'R{i*2+2}','Device:R','10k',160,y,{'1':mid,'2':out},RFP,angle=90,xy=(69,65+i*7),rot=90,note='Input series resistor, 1%',labels=False)
        inp.part(f'C{i+1}','Device:C','1nF C0G',225,y+6.35,{'1':out,'2':'GND'},CFP,xy=(78,65+i*7),note='Matched C0G RF filter capacitor',labels=False)
        inp.wire((50.08,y),(91.19,y));inp.local_label(raw,56,y)
        inp.wire((98.81,y),(156.19,y));inp.local_label(mid,112,y)
        inp.wire((163.81,y),(225,y));inp.wire((225,y),(245,y));inp.label(out,245,y,0)
        inp.wire((225,y),(225,y+2.54))
        inp.items.append(f'(junction (at {n(grid(225))} {n(grid(y))}) (diameter 0) (color 0 0 0 0) (uuid {inp.ident()}))')
        inp.wire((225,y+10.16),(225,y+13.97));inp.wire((225,y+13.97),(235.16,y+13.97));inp.label('GND',235.16,y+13.97,0)
        inp.part(f'D{i+1}','Neuronic:BAV199','BAV199',335,y,{'1':'GND','2':'AVDD_5V','3':out},'Neuronic:SOT-23',xy=(73.5,65+i*7),note='Clamp candidate only; not certified input protection',mpn='BAV199,215')
    inp.text('All 9 paths use the same nominal RC values; routing and parasitics still need review for common-mode rejection.',18,272)

    power.text('BENCH POWER: 6 x AA alkaline candidate (7.2-10.2 V review envelope) -> 5 V / 3.3 V LDOs',18,17,1.8)
    power.text('ESP32 has its own supply. No onboard charging. Regulators must not supply ESP32 radio current.',18,25)
    power.part('J12','Connector_Generic:Conn_01x02','BATTERY_6AA',40,48,{'1':'VBAT_RAW','2':'GND'},'Neuronic:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical',xy=(132,66),note='Candidate keyed battery connector; pin 1 positive, pin 2 ground; verify harness polarity')
    power.part('F1','Device:Polyfuse','100mA_HOLD',100,48,{'1':'VBAT_RAW','2':'VBAT_FUSED'},'Neuronic:Fuse_1812_4532Metric',xy=(124,60),note='MF-MSMF010-2: 60V, 100mA hold / 300mA trip at 23C; AFE branch only, not body protection',mpn='MF-MSMF010-2')
    power.part('D10','Device:D_Schottky','SS14',162,48,{'2':'VBAT_FUSED','1':'VBAT_DIODE'},'Neuronic:D_SMA',xy=(117,60),note='Reverse polarity protection; verify thermal behavior',mpn='SS14')
    power.part('SW1','Switch:SW_SPST','POWER',220,48,{'1':'VBAT_DIODE','2':'VBAT'},'Neuronic:PinHeader_1x02_P2.54mm_Vertical',xy=(109,60),note='Header for an offboard SPST switch')
    for i,(value,rail) in enumerate([('TPS7A2450DBVR','AVDD_5V'),('TPS7A2433DBVR','DVDD_3V3')]):
        power.part(f'U{i+2}','Neuronic:TPS7A24_FIXED',value,95+155*i,86,{'1':'VBAT','2':'GND','3':'VBAT','4':'GND','5':rail},'Neuronic:SOT-23-5',xy=(109+i*14,72),note='Fixed DBV: 1 VIN, 2 GND, 3 EN=VIN, 4 NC=GND, 5 VOUT',mpn=value)
    power.part('FLG1','power:PWR_FLAG','PWR_FLAG',330,48,{'1':'VBAT'})
    power.part('FLG2','power:PWR_FLAG','PWR_FLAG',365,48,{'1':'GND'})
    bypass=[('C20','4.7uF 25V','VBAT','GND',(109,66)),('C21','1uF','AVDD_5V','GND',(109,78)),
        ('C22','4.7uF 25V','VBAT','GND',(123,66)),('C23','4.7uF 25V','DVDD_3V3','GND',(123,78)),
        ('C24','100uF 6.3V','VCAP1','GND',(91.5,104)),('C25','1uF','VCAP2','GND',(96,103)),
        ('C26','1uF','VCAP3','GND',(96,78)),('C27','100nF','VCAP3','GND',(100,78)),
        ('C28','1uF','VCAP4','GND',(87,103)),('C29','10uF','VREFP','GND',(83,100)),
        ('C30','100nF','VREFP','GND',(83,104))]
    # Individual bypass capacitors for all supply pins, plus bulk capacitance.
    analogpos=[(83,94),(83,90),(83,86),(87,78),(91,78),(104,86)]
    for j,pos in enumerate(analogpos):bypass.append((f'C{31+j}','1uF','AVDD_5V','GND',pos))
    bypass += [('C37','10uF','AVDD_5V','GND',(105,94)),('C38','100nF','AVDD_5V','GND',(105,90)),
               ('C39','1uF','DVDD_3V3','GND',(104,98)),('C40','1uF','DVDD_3V3','GND',(100,102)),
               ('C41','100nF','DVDD_3V3','GND',(100,106))]
    for j,(ref,value,a,b,pos) in enumerate(bypass):
        x=35+(j%7)*55;y=125+(j//7)*30
        p=add_rc(power,ref,value,a,b,x,y,pos,kind='C',note='Final MPN, voltage bias capacitance and placement require review')
    power.text('Bias amplifier: internal mid-supply reference (2.5 V); start disabled for internal-test/shorted-input tests.',18,240)
    add_rc(power,'R20','1M','BIASOUT','BIASINV',60,259,(100,72),note='Bias feedback, candidate compensation must be checked with cable/electrode model')
    add_rc(power,'C10','1.5nF C0G','BIASOUT','BIASINV',125,259,(95,72),kind='C')
    add_rc(power,'R21','499k','BIASOUT','BIAS_LIMIT_MID',190,259,(86,114),rot=90)
    add_rc(power,'R22','499k','BIAS_LIMIT_MID','CONTACT_BIAS',260,259,(75,128),rot=90)
    power.part('J10','Connector_Generic:Conn_01x01','BIAS_TOUCHPROOF',345,225,{'1':'CONTACT_BIAS'},'Neuronic:P1_36619_Touchproof_RA',xy=(67.026,134.8),note='Bias output, not protective earth. Same P1 jack; fit requires verification.')
    power.text('Do not infer patient safety from the two bias resistors. Input faults, aggregate leakage, clamps and USB paths remain open review items.',18,279)
    apply_placement()
    for s in SHEETS.values():s.save(s is root)
    return PARTS

def apply_placement():
    """A0.2 routing start placement; final routed CAD is the authority."""
    fixed={
      'U1':(100,92,0),'J11':(131,88,0),'J12':(126,65,0),
      'F1':(121,60,0),'D10':(112,60,0),'SW1':(104,60,0),
      'U2':(110,71,0),'U3':(124,71,0),'C20':(106,70,90),'C21':(114,70,90),
      'C22':(120,70,90),'C23':(128,72,90),
      'C24':(105,107,270),'C25':(109,101,270),'C26':(103,78,0),'C27':(103,75.5,0),
      'C28':(100,105,270),'C29':(94.5,108,0),'C30':(94.5,103,270),
      'C31':(97.3,101,270),'C32':(100.1,101,270),'C33':(102.9,101,270),
      'C34':(98,82,90),'C35':(101,82,90),'C36':(104,82,90),
      'C37':(115,78,0),'C38':(115,81,0),'C39':(110,88.25,0),
      'C40':(110,83,90),'C41':(113,84,90),'R20':(93,81,0),'C10':(93,78,0),
      'R21':(82,124,0),'R22':(72,129.2,0),'R36':(107,85,0)}
    for i in range(9):
        row=7-i if i<8 else 8
        sy=61+row*8.2
        fy=77+row*4 if i<8 else 113
        fixed.update({f'R{2*i+1}':(71,sy,0),f'R{2*i+2}':(75,sy,0),
                      f'D{i+1}':(83.5,fy,0),f'C{i+1}':(89,fy,0)})
    for i,ref in enumerate(['R30','R31','R32','R33','R34','R35','R37','R38','R39','R40']):
        fixed[ref]=(114+(i%3)*5,96+(i//3)*4,0)
    for p in PARTS:
        if p['ref'] in fixed:
            x,y,rot=fixed[p['ref']];p['xy']=(x,y);p['rot']=rot

def bundle_libraries():
    used=sorted({p['fp'].split(':')[1] for p in PARTS} | {'MountingHole_2.7mm_M2.5'})
    pretty=OUT/'Neuronic.pretty';pretty.mkdir(exist_ok=True)
    origins={}
    for p in DATA.glob('footprints/*.pretty/*.kicad_mod'):
        if p.stem in used:origins[p.stem]=p
    for p in (ROOT/'hardware/footprints').glob('*.kicad_mod'):
        if p.stem in used:origins[p.stem]=p
    for name in used:
        if name not in origins:raise FileNotFoundError(name)
        shutil.copyfile(origins[name],pretty/f'{name}.kicad_mod')
    libraries=sorted({key.split(':')[0] for key in LIB})
    for library in libraries:
        syms='\n'.join(v.replace(f'(symbol "{library}:', '(symbol "',1) for k,v in LIB.items() if k.startswith(library+':'))
        (OUT/f'{library}.kicad_sym').write_text(f'(kicad_symbol_lib (version 20241209) (generator kicad_symbol_editor)\n{syms}\n)\n')
    (OUT/'sym-lib-table').write_text('(sym_lib_table\n'+''.join(f'(lib (name "{lib}")(type "KiCad")(uri "${{KIPRJMOD}}/{lib}.kicad_sym")(options "")(descr "Project symbol subset"))\n' for lib in libraries)+')\n')
    (OUT/'fp-lib-table').write_text('(fp_lib_table (lib (name "Neuronic")(type "KiCad")(uri "${KIPRJMOD}/Neuronic.pretty")(options "")(descr "Bundled KiCad footprints")))\n')
    lic=ROOT/'hardware/licenses';lic.mkdir(exist_ok=True)
    for kind in ['symbols','footprints']:
        path=DATA.parent/f'doc/kicad-{kind}/copyright'
        if path.exists():shutil.copyfile(path,lic/f'KiCad-{kind}-copyright.txt')

def save_project():
    pro={
      'meta':{'filename':'neuronic.kicad_pro','version':1},
      'board':{'design_settings':{'rules':{'min_clearance':0.2,'min_track_width':0.15,'min_via_diameter':0.6,'min_through_hole_diameter':0.3,'min_copper_edge_clearance':0.5}}},
      'net_settings':{'classes':[{'name':'Default','clearance':0.2,'track_width':0.2,'via_diameter':0.6,'via_drill':0.3,'bus_width':12,'wire_width':6,'pcb_color':'rgba(0, 0, 0, 0.000)','schematic_color':'rgba(0, 0, 0, 0.000)'}],'meta':{'version':3}},
      'schematic':{'meta':{'version':1}},
      'erc':{'erc_exclusions':[]},
      'text_variables':{'REVISION':'A0.2 - BENCH REVIEW'}}
    (OUT/'neuronic.kicad_pro').write_text(json.dumps(pro,indent=2)+'\n')

def save_bom():
    d=ROOT/'hardware/bom';d.mkdir(exist_ok=True)
    with (d/'bom-review.csv').open('w',newline='') as f:
        w=csv.writer(f,lineterminator="\n");w.writerow(['Reference','Value','Footprint','Proposed_MPN','Review_notes'])
        for p in PARTS:w.writerow([p['ref'],p['value'],p['fp'],p['mpn'] or 'TBD - do not order',p['note']])
    (ROOT/'hardware/design.json').write_text(json.dumps({'revision':REVISION,'state':'placed-unrouted-bench-only','parts':PARTS,'ads_pin_names':PIN_NAMES},indent=2)+'\n')

def board():
    import pcbnew as k
    import xml.etree.ElementTree as ET
    # Use KiCad's real NC net names, including pin names, for full parity DRC.
    with tempfile.TemporaryDirectory() as temporary:
        netfile=Path(temporary)/'net.xml'
        subprocess.run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(netfile),str(OUT/'neuronic.kicad_sch')],check=True)
        pin_nets={(node.attrib['ref'],node.attrib['pin']):net.attrib['name']
                  for net in ET.parse(netfile).findall('nets/net') for node in net.findall('node')}
    b=k.BOARD();b.SetCopperLayerCount(4)
    netnames=sorted(set(pin_nets.values()))
    nets={}
    for name in netnames:
        net=k.NETINFO_ITEM(b,name);b.Add(net);nets[name]=net
    for p in PARTS:
        fp=k.FootprintLoad(str(OUT/'Neuronic.pretty'),p['fp'].split(':')[1])
        if fp is None:raise ValueError(p['fp'])
        fp.SetReference(p['ref']);fp.SetValue(p['value'])
        fp.SetFPID(k.LIB_ID('Neuronic',p['fp'].split(':')[1]))
        fp.SetPath(k.KIID_PATH(f'/{uid("neuronic")}/'+ ('' if p['sheet']=='neuronic' else uid('sheet-'+p['sheet'])+'/')+p['uuid']))
        fp.SetPosition(k.VECTOR2I(k.FromMM(p['xy'][0]),k.FromMM(p['xy'][1])))
        fp.SetOrientationDegrees(p['rot'])
        for pad in fp.Pads():
            net=pin_nets.get((p['ref'],pad.GetNumber()))
            if net:pad.SetNet(nets[net])
        b.Add(fp)
        fp.Reference().SetTextSize(k.VECTOR2I(k.FromMM(0.8),k.FromMM(0.8)))
        fp.Reference().SetTextThickness(k.FromMM(0.12))
        fp.Value().SetVisible(False)
        if p['ref']=='C20':fp.Reference().SetVisible(False)
    # Board is deliberately a placement checkpoint: no inferred tracks or planes.
    for a,c in [((50,55),(138,55)),((138,55),(138,145)),((138,145),(50,145)),((50,145),(50,55))]:
        s=k.PCB_SHAPE();s.SetShape(k.SHAPE_T_SEGMENT);s.SetLayer(k.Edge_Cuts);s.SetWidth(k.FromMM(0.05));s.SetStart(k.VECTOR2I(k.FromMM(a[0]),k.FromMM(a[1])));s.SetEnd(k.VECTOR2I(k.FromMM(c[0]),k.FromMM(c[1])));b.Add(s)
    for text,xy,size in [('NEURONIC A0.2 / BENCH', (109,138),1),('BENCH ONLY / NO BODY CONNECTION',(93,141),0.9),('8CH + REF + BIAS',(70,138),0.8),('MCU 3V3 IO',(128,112),0.8)]:
        t=k.PCB_TEXT(b);t.SetText(text);t.SetPosition(k.VECTOR2I(k.FromMM(xy[0]),k.FromMM(xy[1])));t.SetTextSize(k.VECTOR2I(k.FromMM(size),k.FromMM(size)));t.SetTextThickness(k.FromMM(0.12));t.SetLayer(k.F_SilkS);b.Add(t)
    for num,xy in enumerate([(87,58),(135,58),(135,142),(73,142)]):
        fp=k.FootprintLoad(str(OUT/'Neuronic.pretty'),'MountingHole_2.7mm_M2.5');fp.SetReference(f'H{num+1}');fp.SetValue('M2.5');fp.SetFPID(k.LIB_ID('Neuronic','MountingHole_2.7mm_M2.5'));fp.SetPosition(k.VECTOR2I(k.FromMM(xy[0]),k.FromMM(xy[1])));fp.Reference().SetVisible(False);fp.Value().SetVisible(False);fp.SetAttributes(k.FP_BOARD_ONLY | k.FP_EXCLUDE_FROM_BOM | k.FP_EXCLUDE_FROM_POS_FILES);b.Add(fp)
    b.BuildConnectivity()
    k.SaveBoard(str(OUT/'neuronic.kicad_pcb'),b)
    reports=ROOT/'hardware/validation';reports.mkdir(exist_ok=True)
    k.LoadBoard(str(OUT/'neuronic.kicad_pcb'))
    print(f'PCB saved and reloaded by KiCad {k.GetBuildVersion()}; run validate_kicad.py for DRC.')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--board',action='store_true');parser.add_argument('--overwrite',action='store_true');args=parser.parse_args()
    if (OUT/'neuronic.kicad_sch').exists() and not args.overwrite:
        parser.error('Existing design: commit edits first and explicitly pass --overwrite.')
    pcb=OUT/'neuronic.kicad_pcb'
    if args.board and pcb.exists():
        import pcbnew as k
        existing=k.LoadBoard(str(pcb))
        if len(existing.GetTracks()) or existing.GetAreaCount():
            parser.error('Refusing to replace a PCB containing tracks, vias or zones. Preserve and edit that PCB in KiCad.')
    initialize();make_design();bundle_libraries();save_project();save_bom()
    if args.board:board()
    print(f'Generated {len(PARTS)} components, 3 schematic sheets and BOM at {OUT}')

if __name__=='__main__':main()
