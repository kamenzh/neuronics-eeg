#!/usr/bin/python3
"""Original bounded calculations; no circuit simulation or safety acceptance.

Inputs are manually selected source/drawing values and explicit scenarios.
Does not use design.json, review_electrical.py, or simulate_input.py.
"""
import cmath
import json
import math
from pathlib import Path
OUT=Path(__file__).resolve().parent
inch=25.4
signal_max=(.06+.01)*inch
dummy_w=(.046+.005)*inch
dummy_t=(.02+.01)*inch
position_error=.01*inch
mechanical={
 'units':'mm',
 'source':'https://catalog.p1tec.com/dash50/36619_dash50.pdf; revision H; inch dimensions control',
 'assumptions':'Rigid unbent legs; independent full drawing tolerances can coincide. Finished hole tolerances not specified in project; -0.10 mm is illustrative only.',
 'signal_max_diameter':signal_max,
 'dummy_max_width':dummy_w,'dummy_max_thickness':dummy_t,
 'dummy_max_diagonal':math.hypot(dummy_w,dummy_t),
 'signal_radial_float_nominal_1_9_hole':(1.9-signal_max)/2,
 'signal_radial_float_1_8_min_hole':(1.8-signal_max)/2,
 'dummy_transverse_location_error':position_error,
 'dummy_required_hole_for_outward_y_tolerance':2*math.hypot(dummy_w/2,dummy_t/2+position_error),
 'dummy_x_float_at_nominal_hole':math.sqrt((1.8/2)**2-(dummy_t/2)**2)-dummy_w/2,
 'socket_signal_to_dummy_span_tolerance':position_error,
 'maximum_housing_width':(.25+.01)*inch,
 'nominal_socket_pitch':8.2,
 'housing_gap_at_max_width':8.2-(.25+.01)*inch,
 'nominal_nose_overhang':.5,'nose_overhang_dimension_only_range':[.5-.02*inch,.5+.02*inch],
}
mechanical['combined_signal_and_dummy_x_float_nominal_holes']=mechanical['signal_radial_float_nominal_1_9_hole']+mechanical['dummy_x_float_at_nominal_hole']

def h(freq,res,cap):return 1/(1+2j*math.pi*freq*res*cap)
cases=[]
for freq in [50,60]:
 for name,rp,cp,rn,cn in [
  ('nominal discrete RC only',20000,1e-9,20000,1e-9),
  ('R and C opposite tolerance corners; no ADC capacitance',19800,.95e-9,20200,1.05e-9),
  ('illustrative 20 pF each ADC input; eight inputs on REF',20000,1.02e-9,20000,1.16e-9),
  ('tolerance corners plus illustrative ADC input capacitance',19800,.97e-9,20200,1.21e-9),
 ]:
  error=abs(h(freq,rp,cp)-h(freq,rn,cn))
  cases.append({'case':name,'frequency_hz':freq,'differential_per_common_mode':error,
                'cmrr_db':-20*math.log10(error) if error else None,
                'uV_differential_from_100mV_common_mode':error*.1*1e6})
electrical={
 'assumptions':'Ideal linear RC, identical ideal common-mode drive, no electrode impedance, no bias feedback. ADC input C=20pF is a sensitivity model, not a guaranteed common-mode capacitance model or system CMRR.',
 'cmrr_sensitivity':cases,
 'bias_feedback_pole_hz':1/(2*math.pi*1e6*1.5e-9),
 'bias_998k_output_pole_hz':{str(c):1/(2*math.pi*998000*c) for c in [100e-12,500e-12,1e-9,5e-9]},
 'resistor_pair_differential_noise_uV_0_5_to_40Hz_300K':math.sqrt(4*1.380649e-23*300*40000*39.5)*1e6,
 'resistor_pair_differential_noise_uV_100Hz_300K':math.sqrt(4*1.380649e-23*300*40000*100)*1e6,
 'dc_fault_10_2V_one_19_8k_path_mA':10.2/19800*1000,
 'dc_fault_10_2V_one_9_9k_path_mA':10.2/9900*1000,
 'nine_19_8k_paths_10_2V_upper_sum_mA':9*10.2/19800*1000,
 'rail_5_1V_to_contact_19_8k_uA':5.1/19800*1e6,
 'bias_5_1V_988_02k_uA':5.1/(998000*.99)*1e6,
 'bias_5_1V_494_01k_uA':5.1/(499000*.99)*1e6,
 'C29_required_bias_ac_aging_retention_after_tolerance_temperature':10/(22*.9*.85),
 'C29_uF_before_bias_ac_aging_at_negative_tolerance_temperature':22*.9*.85,
 'ldo_additive_accuracy_rails':{'5V':[4.9,5.1],'3V3':[3.234,3.366]},
 'ldo_input_at_pack7_2V_load40mA_fuse15ohm_diode0_5V_harness0_1V':7.2-.04*15-.5-.1,
 'ldo_dissipation_W_input10_2V_and_30_10mA':[ (10.2-4.9)*.03,(10.2-3.234)*.01],
 'pulldown100k_1pct_voltage_at_positive10uA_input_leak':101000*10e-6,
 'digital_VIL_limit_at_min_3V3_rail':.2*3.234,
 'ADS_tPOR_at_2_048MHz_seconds':2**18/2.048e6,
 'frame_27bytes_read_us_at_1MHz':27*8,
 'sample_period_us_250sps':1e6/250,
}
result={'mechanical':mechanical,'electrical':electrical}
(OUT/'independent-calculations.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
