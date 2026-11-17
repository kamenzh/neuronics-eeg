#!/usr/bin/env python3
"""Engineering arithmetic from fresh CAD values; not SPICE or measurements."""
import math,json,xml.etree.ElementTree as E
from pathlib import Path
base=Path(__file__).parent;r=E.parse(base/'fresh.net.xml').getroot()
values={c.get('ref'):c.findtext('value') for c in r.findall('components/comp')}
def value(s):
 token=s.split()[0]
 for suffix,m in [('uF',1e-6),('nF',1e-9),('k',1e3),('M',1e6),('R',1)]:
  if token.endswith(suffix):return float(token[:-len(suffix)])*m
 return float(token)
R=value(values['R1'])+value(values['R2']);C=value(values['C1']);Rb=value(values['R21'])+value(values['R22']);Rf=value(values['R20']);Cf=value(values['C10'])
def h(f,r,c):return 1/(1+2j*math.pi*f*r*c)
def mismatch(rp,cp,rn,cn):
 out={}
 for f in [50,60]:
  eps=abs(h(f,rp,cp)-h(f,rn,cn));out[str(f)]={'rejection_db':-20*math.log10(eps),'differential_uV_per_100mV_common_mode':eps*.1*1e6}
 return out
cases={
 'capacitor_resistor_tolerance_only':mismatch(R*.99,C*.95,R*1.01,C*1.05),
 'typical_input_capacitance_only_20pF_each':mismatch(R,C+20e-12,R,C+8*20e-12),
 'tolerances_plus_shared_typical_capacitance':mismatch(R*.99,C*.95+20e-12,R*1.01,C*1.05+8*20e-12),
 '5k_reference_source_imbalance_plus_shared_C':mismatch(R,C+20e-12,R+5000,C+8*20e-12),
 '50k_reference_source_imbalance_plus_shared_C':mismatch(R,C+20e-12,R+50000,C+8*20e-12)}
result={'scope':__doc__,'cad_values':{'R_series_ohm':R,'C_shunt_F':C,'bias_series_ohm':Rb,'bias_feedback_ohm':Rf,'bias_feedback_F':Cf},
 'RC_pole_Hz':1/(2*math.pi*R*C),'RC_50Hz_dB':20*math.log10(abs(h(50,R,C))),
 'resistor_noise_uVrms':{str(bw):{'one_leg':math.sqrt(4*1.380649e-23*300*R*bw)*1e6,'P_minus_REF':math.sqrt(4*1.380649e-23*300*2*R*bw)*1e6} for bw in [39.5,70,100]},
 'CMRR_sensitivities_not_predictions':cases,
 'input_bias_300pA_sensitivity':{'positive_drop_uV':300e-12*R*1e6,'reference_8_inputs_drop_uV':8*300e-12*R*1e6,'same_sign_differential_uV':7*300e-12*R*1e6},
 'single_diode_5nA_leakage_sensitivity_uV':5e-9*R*1e6,
 'gain_headroom':{str(g):{'reference_full_scale_V':4.5/g,'max_diff_at_fixed_pair_CM_2_5V':min(4.5/g,4.6/g),'max_one_electrode_offset_with_REF_2_5V':min(4.5/g,4.6/(g+1)),'max_one_electrode_offset_with_REF_2_45V_AVDD_4_9V':min(4.5/g,4.5/(g+1))} for g in [1,2,4,6,8,12,24]},
 'gain12_CM_limits_at_abs_diff':{str(v):[.2+12*v/2,4.8-12*v/2] for v in [.1,.3,.35,.375]},
 'bias_feedback_pole_Hz':1/(2*math.pi*Rf*Cf),
 'bias_series_capacitive_load_poles_Hz':{str(nf):1/(2*math.pi*Rb*nf*1e-9) for nf in [.5,1,5]},
 'bias_gain_source_discrepancy_sensitivity':{str(n):{'220k_diagram':Rf*n/220000,'330k_text':Rf*n/330000} for n in [2,8,16]},
 'VCAP1_illustrative_first_order':{'R1_ohm_Fig25':9800,'bandgap_V_Fig25':1.2,'nominal_time_constant_s':9800*value(values['C24']),'time_to_1_1V_s_ignoring_leakage':-9800*value(values['C24'])*math.log(1-1.1/1.2),'max_6_3uA_leakage_times_9_8k_V':6.3e-6*9800,'qualification':'6.3uA is capacitor rated-voltage leakage, not measured or guaranteed leakage at 1.2V; simplified source model, no guaranteed startup time.'},
 'power':{'ldo_input_low_V_assumed':7.2-.04*15-.5-.1,'AVDD_conservative_V':[4.9,5.1],'DVDD_conservative_V':[3.234,3.366],'analog_dissipation_W_upper':(10.2-4.9)*.03,'digital_dissipation_W_upper':(10.2-3.234)*.01,'analog_temp_rise_C_JEDEC_only':(10.2-4.9)*.03*167.8,'digital_temp_rise_C_JEDEC_only':(10.2-3.234)*.01*167.8,'Nano_VIN_low_conditional':7.2-.6-.3},
 'fault_path_bounds_not_body_acceptance':{'5_1V_single_input_20k_uA':5.1/(R*.99)*1e6,'5_1V_nine_parallel_input_paths_uA':9*5.1/(R*.99)*1e6,'10_2V_input_20k_mA':10.2/(R*.99)*1e3,'10_2V_one_10k_remaining_mA':10.2/(R*.99/2)*1e3,'10_2V_nine_input_paths_mA':9*10.2/(R*.99)*1e3,'5_1V_bias_998k_uA':5.1/(Rb*.99)*1e6,'5_1V_bias_one_499k_uA':5.1/(Rb*.99/2)*1e6,'5V_clamp_short_return_via_2_5V_bias_uA':(5-2.5)/(R+Rb)*1e6,'qualification':'Parallel bounds require a common source and real return on all indicated paths; a single shorted clamp does not automatically create nine such paths.'},
 'SPI':{'frame_bytes':27,'frame_at_1MHz_us':27*8,'period_at_250SPS_us':4000,'raw_bytes_per_second':27*250,'command_decode_4tclk_us':4/2.048e6*1e6,'POR_2pow18_nominal_s':2**18/2.048e6,'internal_test_amplitude_V_default':4.5/2400,'internal_test_frequency_Hz_default':2.048e6/2**21,'test_magnitude_code_gain12_register_formula_ideal':(4.5/2400)/(4.5/12)*(2**23-1)},
 'socket':{'signal_max_diameter_mm':(.06+.01)*25.4,'signal_min_finished_hole_assumed_mm':2.0,'signal_min_radial_clearance_mm':(2.0-(.06+.01)*25.4)/2,'dummy_max_section_mm':[(.046+.005)*25.4,(.02+.01)*25.4],'dummy_worst_corner_distance_mm':math.hypot(1.2954/2+.254+.15-(4.1-2)/2,.762/2+.254+.15),'slot_radius_at_assumed_min_mm':1.0}}
# Direct rail capacitors are identified from the fresh netlist, not design.json.
connections={}
for net in r.findall('nets/net'):
 for n in net.findall('node'):
  connections.setdefault(n.get('ref'),set()).add(net.get('name'))
rail_caps={}
for rail in ['AVDD_5V','DVDD_3V3']:
 refs=[ref for ref,ns in connections.items() if ref.startswith('C') and ns=={rail,'GND'}]
 rail_caps[rail]={'references':sorted(refs),'nominal_uF':sum(value(values[ref]) for ref in refs)*1e6}
ref_nominal=value(values['C29'])+value(values['C42'])
result['capacitance_budget']={'direct_rail_caps':rail_caps,'AVDD_high_uF_tolerance_temperature_only':rail_caps['AVDD_5V']['nominal_uF']*1.1*1.15,'reference_nominal_uF':ref_nominal*1e6,'reference_engineering_factors':[.75,.9,.85,.9,.9],'reference_engineering_estimate_uF':ref_nominal*math.prod([.75,.9,.85,.9,.9])*1e6,'qualification':'Factors are engineering assumptions for DC bias, tolerance, temperature, aging and reserve; not guaranteed manufacturer bounds or measured capacitance.'}
(base/'independent-calculations.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
