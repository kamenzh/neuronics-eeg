#!/usr/bin/env python3
"""Linear RC check, not a simulation of the ADS1299, clamps or human safety."""
import json
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
interface=json.loads((ROOT/'hardware/interface.json').read_text())
gain=interface['acquisition']['initial_gain']
R=20000.0
C=1e-9
fc=1/(2*math.pi*R*C)
def complex_h(f,r,c):return 1/(1+2j*math.pi*f*r*c)
def rejection_db(f,rp,cp,rn,cn):return -20*math.log10(abs(complex_h(f,rp,cp)-complex_h(f,rn,cn)))
def h(f):return 1/math.sqrt(1+(2*math.pi*f*R*C)**2)
result={
 'model':'Ideal 20 kohm series, 1 nF shunt, high impedance ADC input; one input path',
 'limitations':['No ADS1299 SPICE model','No electrode impedance','No diode leakage or clamping model',
               'No bias-loop stability model','No parasitic coupling, power noise or patient safety model'],
 'rf_pole_hz':fc,
 'response_db':{str(f):20*math.log10(h(f)) for f in [0.5,10,40,50,60,125,8000,1e6]},
 'series_resistor_thermal_noise_0_5_to_40_hz_uV_rms_300K':math.sqrt(4*1.380649e-23*300*R*39.5)*1e6,
 'initial_gain':gain,'ideal_input_range_V_at_VREF_4_5':[-4.5/gain,4.5/gain],
 'ideal_code_step_nV_at_VREF_4_5':4.5/gain/(2**23-1)*1e9,
 'two_input_resistor_noise_0_5_to_40_hz_uV_rms_300K':math.sqrt(4*1.380649e-23*300*2*R*39.5)*1e6,
 'tolerance_only_common_mode_rejection_db':{str(f):rejection_db(f,19800,.95e-9,20200,1.05e-9) for f in [10,40,50,60,125]},
 'illustrative_shared_input_capacitance_rejection_db':{str(f):rejection_db(f,R,1.02e-9,R,1.16e-9) for f in [50,60]},
 'shared_capacitance_qualification':'Sensitivity example only: 20pF per input modeled as a shunt, not a guaranteed ADC common-mode capacitance model; electrode/cable loading and bias omitted.',
 'bias_output_rc_pole_hz_illustrative':{str(c):1/(2*math.pi*998000*c*1e-9) for c in [.5,1,5]},
 'bias_pole_qualification':'Output RC only, not bias-loop phase margin or stability proof.',
 'interpretation':'The RF filter barely attenuates 50/60 Hz. Use suitable digital processing after conversion; do not expect this RC to remove mains interference.'}
assert 7900<fc<8000
assert h(40)>0.999
assert result['response_db']['1000000.0'] < -40
path=ROOT/'hardware/validation/input-model.json';path.write_text(json.dumps(result,indent=2)+'\n')
print(f'RC pole: {fc:.2f} Hz; 50 Hz attenuation: {result["response_db"]["50"]:.6f} dB')
