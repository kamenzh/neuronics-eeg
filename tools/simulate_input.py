#!/usr/bin/env python3
"""Linear RC check, not a simulation of the ADS1299, clamps or human safety."""
import json
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=20000.0
C=1e-9
fc=1/(2*math.pi*R*C)
def h(f):return 1/math.sqrt(1+(2*math.pi*f*R*C)**2)
result={
 'model':'Ideal 20 kohm series, 1 nF shunt, high impedance ADC input; one input path',
 'limitations':['No ADS1299 SPICE model','No electrode impedance','No diode leakage or clamping model',
               'No bias-loop stability model','No parasitic coupling, power noise or patient safety model'],
 'rf_pole_hz':fc,
 'response_db':{str(f):20*math.log10(h(f)) for f in [0.5,10,40,50,60,125,8000,1e6]},
 'series_resistor_thermal_noise_0_5_to_40_hz_uV_rms_300K':math.sqrt(4*1.380649e-23*300*R*39.5)*1e6,
 'ideal_ads1299_input_range_V_at_gain_24_VREF_4_5':[-4.5/24,4.5/24],
 'ideal_code_step_nV_at_gain_24_VREF_4_5':4.5/24/(2**23-1)*1e9,
 'interpretation':'The RF filter barely attenuates 50/60 Hz. Use suitable digital processing after conversion; do not expect this RC to remove mains interference.'}
assert 7900<fc<8000
assert h(40)>0.999
assert result['response_db']['1000000.0'] < -40
path=ROOT/'hardware/validation/input-model.json';path.write_text(json.dumps(result,indent=2)+'\n')
print(f'RC pole: {fc:.2f} Hz; 50 Hz attenuation: {result["response_db"]["50"]:.6f} dB')
