#!/usr/bin/env python3
"""Small-signal sensitivity model for the passive inputs. No human load model."""
import itertools
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parts = {p['ref']:p['value'] for p in json.loads((ROOT/'hardware/design.json').read_text())['parts']}
def capacitance(ref):
    return float(parts[ref].split('pF')[0])*1e-12
rp = sum(float(parts[r].removesuffix('k'))*1000 for r in ('R1','R2'))
rn = sum(float(parts[r].removesuffix('k'))*1000 for r in ('R17','R18'))
cp, cn = capacitance('C1'), capacitance('C9')
def transfer(f,r,c):
    return 1/(1+2j*math.pi*f*r*c)
def rejection(f,cin,rtol,ctol,extra):
    errors = []
    for a,b,d,e in itertools.product((-1,1),repeat=4):
        hp=transfer(f,rp*(1+a*rtol)+extra,cp*(1+b*ctol)+cin)
        hn=transfer(f,rn*(1+d*rtol),cn*(1+e*ctol)+8*cin)
        errors.append(abs(hp-hn))
    error=max(errors)
    return round(-20*math.log10(error),2) if error>1e-12 else None
result={'model':'Independent shunt capacitance per ADS input is a sensitivity assumption; PCB/cable parasitics, leakage, finite ADC input resistance, bias loop, noise from active devices and electrode noise are excluded.',
        'external_RC_poles_hz':{'record':1/(2*math.pi*rp*cp),'reference':1/(2*math.pi*rn*cn)},
        'two_input_resistor_noise_0_5_to_40_hz_uV_rms_300K':math.sqrt(4*1.380649e-23*300*(rp+rn)*39.5)*1e6,
        'gain_db_at_40hz_nominal_record_with_20pF':20*math.log10(abs(transfer(40,rp,cp+20e-12))),
        'worst_corner_cmrr_db':[{'hz':f,'assumed_input_pf':c,'record_extra_source_ohms':z,
          'db':rejection(f,c*1e-12,.001,.01,z)} for f in (50,60) for c in (0,10,20,30,40) for z in (0,5000,50000)],
        'corner_scope':'±0.1% series R and ±1% external C (initial tolerance). Both electrode source impedances zero except indicated recording mismatch. No notch.'}
(ROOT/'hardware/validation/input-model.json').write_text(json.dumps(result,indent=2)+'\n')
print('Passive resistor-pair noise:',result['two_input_resistor_noise_0_5_to_40_hz_uV_rms_300K'],'uV RMS')
