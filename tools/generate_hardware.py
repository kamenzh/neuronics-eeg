#!/usr/bin/env python3
"""Generate Neuronic's review checkpoint. Not a manufacturing release.

Python stdlib only for schematic/BOM. --board also requires KiCad pcbnew.
Set KICAD_DATA to the KiCad share directory, e.g. /usr/share/kicad.
Generated files are overwritten; commit GUI edits before regenerating.
"""
import argparse
import csv
import json
import math
import os
import re
import shutil
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'hardware/kicad'
DATA = Path(os.environ.get('KICAD_DATA', '/usr/share/kicad'))
NS = uuid.UUID('b314a604-c394-4051-a09e-9626c22cb806')
def uid(key): return str(uuid.uuid5(NS, key))
def q(s): return json.dumps(str(s))
def n(x): return f'{x:.4f}'.rstrip('0').rstrip('.') if x else '0'

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
    token = f'(symbol "{name}" '
    start = text.find(token)
    if start < 0: raise ValueError(f'Missing {lib}:{name}')
    s = block(text, start)
    if '(extends ' in s: raise ValueError('Use the base library symbol explicitly')
    return s.replace(f'(symbol "{name}" ', f'(symbol "{lib}:{name}" ', 1)

LIB = {}
PARTS = []
SHEETS = {}

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
    for lib, name in [('Device','R'), ('Device','C'), ('Device','D_Schottky'),
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
    LIB['Neuronic:BAV199'] = custom_symbol('BAV199', [
        ('1','A1','passive',-7.62,2.54,0), ('2','K2','passive',7.62,2.54,180),
        ('3','K1_A2','passive',0,-7.62,90)],5.08,5.08,
        'Series low leakage diodes: pin1 anode to GND, pin2 cathode to AVDD, pin3 input')

def symbol_pins(s):
    out=[]
    for m in re.finditer(r'\(pin (?:input|output|bidirectional|tri_state|passive|free|unspecified|power_in|power_out|open_collector|open_emitter|no_connect) ',s):
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
        if a==b:return
        self.items.append(f'(wire (pts (xy {n(a[0])} {n(a[1])}) (xy {n(b[0])} {n(b[1])})) (stroke (width 0) (type default)) (uuid {self.ident()}))')
    def label(self,t,x,y,angle=0):
        self.items.append(f'(global_label {q(t)} (shape bidirectional) (at {n(x)} {n(y)} {angle}) (effects (font (size 1.016 1.016)) (justify {"left" if angle in [0,90] else "right"})) (uuid {self.ident()}) (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {n(x)} {n(y)} {angle}) (effects (font (size 1.016 1.016)) hide)))')
    def part(self,ref,lib,value,x,y,nets,fp='',angle=0,xy=None,rot=0,note='',mpn='',labels=True):
        self.used.add(lib)
        symid=uid(ref)
        self.items.append(f'(symbol (lib_id {q(lib)}) (at {n(x)} {n(y)} {angle}) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {symid})\n'
            f'(property "Reference" {q(ref)} (at {n(x+3)} {n(y-5)} 0) (effects (font (size 1.016 1.016))))\n'
            f'(property "Value" {q(value)} (at {n(x+3)} {n(y-2.5)} 0) (effects (font (size 1.016 1.016))))\n'
            f'(property "Footprint" {q(fp)} (at {n(x)} {n(y)} 0) (effects (font (size 1.016 1.016)) hide))\n'
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
        txt=f'(kicad_sch (version 20230121) (generator eeschema) (uuid {self.id}) (paper "A3")\n(title_block (title {q(self.title)}) (date "2026-10-24") (rev "A0-review") (company "Neuronic") (comment 1 "BENCH DEVELOPMENT ONLY - NOT FOR BODY CONNECTION OR FABRICATION"))\n(lib_symbols\n{lib}\n)\n'+'\n'.join(self.items)
        if root: txt+='\n(sheet_instances (path "/" (page "1")))'
        txt+='\n)\n'
        (OUT/f'{self.name}.kicad_sch').write_text(txt)

    def local_label(self,t,x,y):
        self.label(t,x,y,0)

RFP='Neuronic:R_0805_2012Metric'
CFP='Neuronic:C_0805_2012Metric'

def add_rc(sh,ref,value,net1,net2,x,y,xy,kind='R',rot=0,note=''):
    return sh.part(ref,f'Device:{kind}',value,x,y,{'1':net1,'2':net2},RFP if kind=='R' else ('Neuronic:C_1210_3225Metric' if ref=='C24' else CFP),xy=xy,rot=rot,note=note)

def make_design():
    root=Sheet('neuronic','01 - ADS1299 core and SPI interface',1)
    inp=Sheet('inputs','02 - Eight channels and shared reference',2)
    power=Sheet('power','03 - Battery regulators, decoupling and bias',3)
    root.text('NEURONIC / A0 REVIEW CHECKPOINT',20,18,2)
    root.text('8 synchronous channels, 10 contacts. One ADS1299 contains both PGAs and ADCs.',20,25)
    root.text('Global labels connect sheets. Negative inputs tie to AVDD; enable SRB1 in MISC1 before normal acquisition.',20,32)
    nets={}
    for i in range(8):nets[str(16-2*i)]=f'EEG{i+1}';nets[str(15-2*i)]='AVDD_5V'
    nets.update({'17':'REF_FILTERED','18':None,'19':'AVDD_5V','20':'GND','21':'AVDD_5V','22':'AVDD_5V','23':'GND',
        '24':'VREFP','25':'GND','26':'VCAP4','27':None,'28':'VCAP1','29':None,'30':'VCAP2','31':'GND','32':'GND',
        '33':'GND','34':'SPI_MOSI','35':'ADS_PWDN_N','36':'ADS_RESET_N','37':None,'38':'ADS_START','39':'ADS_CS_N',
        '40':'SPI_SCLK','41':'GND','42':'GPIO1_PD','43':'SPI_MISO','44':'GPIO2_PD','45':'GPIO3_PD','46':'GPIO4_PD',
        '47':'ADS_DRDY_N','48':'DVDD_3V3','49':'GND','50':'DVDD_3V3','51':'GND','52':'CLKSEL_PU',
        '53':'GND','54':'AVDD_5V','55':'VCAP3','56':'AVDD_5V','57':'GND','58':'GND','59':'AVDD_5V',
        '60':None,'61':'BIASINV','62':'GND','63':'BIASOUT','64':None})
    root.part('U1','Neuronic:ADS1299IPAG','ADS1299IPAG',155,105,nets,'Neuronic:TQFP-64_10x10mm_P0.5mm',xy=(95,90),note='TI SBAS499C pin functions, unipolar 5 V, internal clock/reference',mpn='ADS1299IPAG')
    root.part('J11','Connector_Generic:Conn_02x06_Odd_Even','MCU_3V3_IO_ONLY',312,65,
        {'1':'GND','2':'GND','3':'SPI_SCLK','4':'SPI_MOSI','5':'SPI_MISO','6':'ADS_CS_N',
         '7':'ADS_DRDY_N','8':'ADS_RESET_N','9':'ADS_START','10':'ADS_PWDN_N','11':'DVDD_3V3','12':'GND'},
        'Neuronic:PinHeader_2x06_P2.54mm_Vertical',xy=(130,86),note='Pin 11 is AFE logic reference only. Do not power the ESP32 from this LDO.')
    root.text('J11: board-neutral connector; not an ESP32 dev-board footprint.',258,93)
    root.text('3.3 V logic only. Pi GPIO uses the same voltage.',258,100)
    root.text('External controller power/USB can join GND. No body-connected tests.',258,107)
    rnum=30
    for i,(net,rail) in enumerate([('ADS_CS_N','GND'),('ADS_RESET_N','GND'),('ADS_PWDN_N','GND'),('ADS_START','GND'),('SPI_SCLK','GND'),('SPI_MOSI','GND'),('CLKSEL_PU','DVDD_3V3'),('GPIO1_PD','GND'),('GPIO2_PD','GND'),('GPIO3_PD','GND'),('GPIO4_PD','GND')]):
        x=35+(i%6)*58;y=181+(i//6)*40
        add_rc(root,f'R{rnum+i}','100k' if i<6 else '10k',net,rail,x,y,(116+(i%4)*5,103+(i//4)*7))
    root.text('Default pulldowns keep host inputs low at startup. MCU must release PWDN/RESET and drive CS high after rails settle.',20,250)
    root.text('CONFIG1=0x96 (250 SPS, internal clock output disabled); MISC1=0x20 (SRB1); BIASREF_INT enabled in normal mode.',20,257)
    for name,title,x in [('inputs','Input filters / CH1-8 / REF',25),('power','Power / bypass / bias drive',215)]:
        root.items.append(f'(sheet (at {x} 39.37) (size 170.18 12.7) (fields_autoplaced) (stroke (width 0.1524) (type default)) (fill (color 0 0 0 0)) (uuid {uid("sheet-"+name)}) (property "Sheetname" {q(title)} (at {x} 38 0) (effects (font (size 1.27 1.27)) (justify left bottom))) (property "Sheetfile" "{name}.kicad_sch" (at {x} 53 0) (effects (font (size 1.27 1.27)) (justify left top))) (instances (project "neuronic" (path "/{root.id}" (page "{SHEETS[name].page}")))))')

    inp.text('INPUT NETWORKS: prototype pin headers, not the final touchproof electrode connectors',18,16,1.8)
    inp.text('20k series + 1nF shunt: nominal RF pole 7.96 kHz. This is not the EEG bandpass. ADS1299 digital filter is still required.',18,24)
    inp.text('BAV199 clamps are a bench starting point. Clamp voltage / input injection / leakage and fault protection remain UNREVIEWED.',18,31)
    for i in range(9):
        y=47+i*24
        out=f'EEG{i+1}' if i<8 else 'REF_FILTERED'
        raw=f'CONTACT_{i+1}' if i<8 else 'CONTACT_REF'
        mid=f'INPUT_RMID_{i+1}'
        inp.text(f'CH{i+1}' if i<8 else 'REFERENCE',18,y-5)
        inp.part(f'J{i+1}','Connector_Generic:Conn_01x01',f'CH{i+1}_BENCH' if i<8 else 'REF_BENCH',45,y,{'1':raw},'Neuronic:PinHeader_1x01_P2.54mm_Vertical',angle=180,xy=(57,65+i*7),note='Bench header; replace with verified electrode connector before wearable revision',labels=False)
        inp.part(f'R{i*2+1}','Device:R','10k',95,y,{'1':raw,'2':mid},RFP,angle=90,xy=(64,65+i*7),rot=90,note='Input series resistor, 1%',labels=False)
        inp.part(f'R{i*2+2}','Device:R','10k',160,y,{'1':mid,'2':out},RFP,angle=90,xy=(69,65+i*7),rot=90,note='Input series resistor, 1%',labels=False)
        inp.part(f'C{i+1}','Device:C','1nF C0G',225,y+6.35,{'1':out,'2':'GND'},CFP,xy=(78,65+i*7),note='Matched C0G RF filter capacitor',labels=False)
        inp.wire((50.08,y),(91.19,y));inp.local_label(raw,56,y)
        inp.wire((98.81,y),(156.19,y));inp.local_label(mid,112,y)
        inp.wire((163.81,y),(225,y));inp.wire((225,y),(245,y));inp.label(out,245,y,0)
        inp.wire((225,y),(225,y+2.54))
        inp.items.append(f'(junction (at 225 {n(y)}) (diameter 0) (color 0 0 0 0) (uuid {inp.ident()}))')
        inp.wire((225,y+10.16),(225,y+13.97));inp.wire((225,y+13.97),(235.16,y+13.97));inp.label('GND',235.16,y+13.97,0)
        inp.part(f'D{i+1}','Neuronic:BAV199','BAV199',335,y,{'1':'GND','2':'AVDD_5V','3':out},'Neuronic:SOT-23',xy=(73.5,65+i*7),note='Clamp candidate only; not certified input protection',mpn='BAV199,215')
    inp.text('All 9 paths use the same nominal RC values; routing and parasitics still need review for common-mode rejection.',18,272)

    power.text('BENCH POWER: 7-9 V battery pack -> independent 5 V analog and 3.3 V ADC logic LDOs',18,17,1.8)
    power.text('ESP32 has its own supply. No onboard charging. Regulators must not supply ESP32 radio current.',18,25)
    power.part('J12','Connector_Generic:Conn_01x02','BATTERY_7_TO_9V',40,48,{'1':'VBAT_RAW','2':'GND'},'Neuronic:PinHeader_1x02_P2.54mm_Vertical',xy=(130,61))
    power.part('F1','Device:Polyfuse','100mA_HOLD_CANDIDATE',100,48,{'1':'VBAT_RAW','2':'VBAT_FUSED'},RFP,xy=(124,60),note='Choose exact voltage/current/thermal rating before release')
    power.part('D10','Device:D_Schottky','SS14',162,48,{'2':'VBAT_FUSED','1':'VBAT_DIODE'},'Neuronic:D_SMA',xy=(117,60),note='Reverse polarity protection; verify thermal behavior',mpn='SS14')
    power.part('SW1','Switch:SW_SPST','POWER',220,48,{'1':'VBAT_DIODE','2':'VBAT'},'Neuronic:PinHeader_1x02_P2.54mm_Vertical',xy=(109,60),note='Header for an offboard SPST switch')
    for i,(value,rail) in enumerate([('MCP1703AT-5002E/DB','AVDD_5V'),('MCP1703AT-3302E/DB','DVDD_3V3')]):
        power.part(f'U{i+2}','Regulator_Linear:MCP1703Ax-330xxDB',value,95+155*i,86,{'1':'VBAT','2':'GND','3':rail},'Neuronic:SOT-223-3_TabPin2',xy=(109+i*14,72),note='Fixed output variant; matching footprint pin1 VIN pin2 GND pin3 VOUT',mpn=value)
    power.part('FLG1','power:PWR_FLAG','PWR_FLAG',330,48,{'1':'VBAT'})
    power.part('FLG2','power:PWR_FLAG','PWR_FLAG',365,48,{'1':'GND'})
    bypass=[('C20','4.7uF 16V','VBAT','GND',(109,66)),('C21','4.7uF 10V','AVDD_5V','GND',(109,78)),
        ('C22','4.7uF 16V','VBAT','GND',(123,66)),('C23','4.7uF 10V','DVDD_3V3','GND',(123,78)),
        ('C24','100uF 6.3V','VCAP1','GND',(91,103)),('C25','1uF','VCAP2','GND',(96,103)),
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
    power.part('J10','Connector_Generic:Conn_01x01','BIAS_BENCH',345,225,{'1':'CONTACT_BIAS'},'Neuronic:PinHeader_1x01_P2.54mm_Vertical',xy=(57,128),note='Bias output. Not protective earth. Bench connector only.')
    power.text('Do not infer patient safety from the two bias resistors. Input faults, aggregate leakage, clamps and USB paths remain open review items.',18,279)
    for s in SHEETS.values():s.save(s is root)
    return PARTS

def bundle_libraries():
    used=sorted({p['fp'].split(':')[1] for p in PARTS} | {'MountingHole_2.7mm_M2.5'})
    pretty=OUT/'Neuronic.pretty';pretty.mkdir(exist_ok=True)
    origins={}
    for p in DATA.glob('footprints/*.pretty/*.kicad_mod'):
        if p.stem in used:origins[p.stem]=p
    for name in used:
        if name not in origins:raise FileNotFoundError(name)
        shutil.copyfile(origins[name],pretty/f'{name}.kicad_mod')
    syms='\n'.join(v.replace('(symbol "Neuronic:', '(symbol "',1) for k,v in LIB.items() if k.startswith('Neuronic:'))
    (OUT/'Neuronic.kicad_sym').write_text(f'(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor)\n{syms}\n)\n')
    (OUT/'sym-lib-table').write_text('(sym_lib_table (lib (name "Neuronic")(type "KiCad")(uri "${KIPRJMOD}/Neuronic.kicad_sym")(options "")(descr "Local symbols")))\n')
    (OUT/'fp-lib-table').write_text('(fp_lib_table (lib (name "Neuronic")(type "KiCad")(uri "${KIPRJMOD}/Neuronic.pretty")(options "")(descr "Bundled KiCad 7 footprints")))\n')
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
      'text_variables':{'REVISION':'A0 - UNROUTED REVIEW'}}
    (OUT/'neuronic.kicad_pro').write_text(json.dumps(pro,indent=2)+'\n')

def save_bom():
    d=ROOT/'hardware/bom';d.mkdir(exist_ok=True)
    with (d/'bom-review.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['Reference','Value','Footprint','Proposed_MPN','Review_notes'])
        for p in PARTS:w.writerow([p['ref'],p['value'],p['fp'],p['mpn'] or 'TBD - do not order',p['note']])
    (ROOT/'hardware/design.json').write_text(json.dumps({'revision':'A0-review','state':'placed-unrouted-bench-only','parts':PARTS,'ads_pin_names':PIN_NAMES},indent=2)+'\n')

def board():
    import pcbnew as k
    b=k.BOARD();b.SetCopperLayerCount(4)
    netnames=sorted({v for p in PARTS for v in p['nets'].values() if v})
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
            net=p['nets'].get(pad.GetNumber())
            if net:pad.SetNet(nets[net])
        b.Add(fp)
        fp.Reference().SetTextSize(k.VECTOR2I(k.FromMM(0.8),k.FromMM(0.8)))
        fp.Reference().SetTextThickness(k.FromMM(0.12))
        fp.Value().SetVisible(False)
        if p['ref']=='C20':fp.Reference().SetVisible(False)
    # Board is deliberately a placement checkpoint: no inferred tracks or planes.
    for a,c in [((50,55),(138,55)),((138,55),(138,135)),((138,135),(50,135)),((50,135),(50,55))]:
        s=k.PCB_SHAPE();s.SetShape(k.SHAPE_T_SEGMENT);s.SetLayer(k.Edge_Cuts);s.SetWidth(k.FromMM(0.05));s.SetStart(k.VECTOR2I(k.FromMM(a[0]),k.FromMM(a[1])));s.SetEnd(k.VECTOR2I(k.FromMM(c[0]),k.FromMM(c[1])));b.Add(s)
    for text,xy,size in [('NEURONIC A0 / UNROUTED', (93,58),1),('BENCH ONLY / NO BODY CONNECTION',(93,132),0.9),('CH1-8 / REF',(63,59),0.8),('MCU 3V3 IO',(128,112),0.8)]:
        t=k.PCB_TEXT(b);t.SetText(text);t.SetPosition(k.VECTOR2I(k.FromMM(xy[0]),k.FromMM(xy[1])));t.SetTextSize(k.VECTOR2I(k.FromMM(size),k.FromMM(size)));t.SetTextThickness(k.FromMM(0.12));t.SetLayer(k.F_SilkS);b.Add(t)
    for num,xy in enumerate([(53,58),(135,58),(135,132),(53,132)]):
        fp=k.FootprintLoad(str(OUT/'Neuronic.pretty'),'MountingHole_2.7mm_M2.5');fp.SetReference(f'H{num+1}');fp.SetValue('M2.5');fp.SetFPID(k.LIB_ID('Neuronic','MountingHole_2.7mm_M2.5'));fp.SetPosition(k.VECTOR2I(k.FromMM(xy[0]),k.FromMM(xy[1])));fp.Reference().SetVisible(False);fp.Value().SetVisible(False);b.Add(fp)
    b.BuildConnectivity()
    k.SaveBoard(str(OUT/'neuronic.kicad_pcb'),b)
    reports=ROOT/'hardware/validation';reports.mkdir(exist_ok=True)
    loaded=k.LoadBoard(str(OUT/'neuronic.kicad_pcb'))
    ok=k.WriteDRCReport(loaded,str(reports/'drc-placement.txt'),k.EDA_UNITS_MILLIMETRES,True)
    print(f'PCB loaded by KiCad {k.GetBuildVersion()}, DRC report written: {ok}')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--board',action='store_true');args=parser.parse_args()
    initialize();make_design();bundle_libraries();save_project();save_bom()
    if args.board:board()
    print(f'Generated {len(PARTS)} components, 3 schematic sheets and BOM at {OUT}')

if __name__=='__main__':main()
