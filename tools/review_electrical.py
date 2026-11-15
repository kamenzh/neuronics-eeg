#!/usr/bin/env python3
"""Bounded DC engineering calculations; not SPICE, safety or bench validation."""
import json, re, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
design=json.loads((ROOT/'hardware/design.json').read_text())
parts={p['ref']:p for p in design['parts']}
interface=json.loads((ROOT/'hardware/interface.json').read_text())
def cap_uf(value):
 m=re.match(r'([0-9.]+)([un])F',value)
 if not m:raise ValueError(value)
 return float(m[1])*(1 if m[2]=='u' else .001)
def rail_caps(rail):
 return {r:cap_uf(p['value']) for r,p in parts.items() if r.startswith('C') and set(p['nets'].values())=={rail,'GND'}}
analog=rail_caps('AVDD_5V');digital=rail_caps('DVDD_3V3')
a=interface['acquisition'];p=interface['power'];vmin,vmax=p['review_input_range_v']
load=(p['afe_analog_budget_ma']+p['afe_digital_budget_ma'])/1000
vin_min=vmin-load*15-.5-.1
# TPS7A24 fixed: +/-1.25% over temperature +0.25% line +0.5% load.
error=.0125+.0025+.005
avdd_min,avdd_max=5*(1-error),5*(1+error)
dvdd_min,dvdd_max=3.3*(1-error),3.3*(1+error)
input_min_r=2*10000*.99;bias_min_r=2*499000*.99
fault_v=10.2
cmax=sum(analog.values())*1.1*1.15
calculations={
 'avdd_direct_caps_uF':analog,'avdd_nominal_uF':sum(analog.values()),'avdd_upper_uF_before_bias_aging':cmax,
 'dvdd_direct_caps_uF':digital,'dvdd_nominal_uF':sum(digital.values()),
 'afe_ldo_min_input_v_conditional':vin_min,'analog_output_range_v':[avdd_min,avdd_max],
 'digital_output_range_v':[dvdd_min,dvdd_max],
 'analog_min_input_margin_over_nominal_plus_0_5_v':vin_min-5.5,
 'analog_dropout_margin_v_at_high_output':vin_min-avdd_max-.25,
 'analog_ldo_power_w_upper_ignoring_input_drops':(vmax-avdd_min)*p['afe_analog_budget_ma']/1000,
 'digital_ldo_power_w_upper_ignoring_input_drops':(vmax-dvdd_min)*p['afe_digital_budget_ma']/1000,
 'analog_temp_rise_c_using_datasheet_board':(vmax-avdd_min)*p['afe_analog_budget_ma']/1000*167.8,
 'digital_temp_rise_c_using_datasheet_board':(vmax-dvdd_min)*p['afe_digital_budget_ma']/1000*167.8,
 'raw_bytes_s':a['sample_rate_sps']*a['frame_bytes'],'frame_read_us_ideal':a['frame_bytes']*8/a['initial_spi_hz']*1e6,
 'sample_period_us':1e6/a['sample_rate_sps'],'ideal_differential_full_scale_v':4.5/a['initial_gain'],
 'bounded_10_2v_input_fault_current_ma':fault_v/input_min_r*1000,
 'bounded_10_2v_input_fault_one_resistor_short_ma':fault_v/(input_min_r/2)*1000,
 'bounded_10_2v_remaining_input_resistor_power_w':fault_v**2/(input_min_r/2),
 'internal_5_1v_to_contact_20k_path_ua':avdd_max/input_min_r*1e6,
 'internal_5_1v_to_contact_one_resistor_short_ua':avdd_max/(input_min_r/2)*1e6,
 'bias_5_1v_through_two_resistors_ua':avdd_max/bias_min_r*1e6,
 'bias_5_1v_one_resistor_short_ua':avdd_max/(bias_min_r/2)*1e6,
 'two_20k_paths_resistor_noise_uv_rms_100hz_300k':math.sqrt(4*1.380649e-23*300*40000*100)*1e6}
checks=[
 ('TPS7A24 analog output budget inside ADS1299 recommended 4.75-5.25V',avdd_min>=4.75 and avdd_max<=5.25),
 ('TPS7A24 digital output budget inside ADS1299 recommended 1.8-3.6V',dvdd_min>=1.8 and dvdd_max<=3.6),
 ('Conditional input exceeds nominal+0.5V regulation test boundary',vin_min>=5.5),
 ('AVDD upper direct output capacitance below 50uF effective limit',cmax<=50),
 ('40mA AFE budget below 100mA fuse hold at 23C',load<.1),
 ('Bounded low-energy 10.2V fault with one series resistor short below TI 10mA injection limit',fault_v/(input_min_r/2)<.01),
 ('Bounded DC fault resistor dissipation below nominal 0.125W rating',fault_v**2/(input_min_r/2)<.125),
 ('Eight-channel frame size',a['frame_bytes']==3+3*a['channels']),
 ('Ideal SPI frame fits sample period',a['frame_bytes']*8/a['initial_spi_hz']<1/a['sample_rate_sps'])]
result={'revision':design['revision'],'manufacture_ready':False,'body_connection_approved':False,
 'sources':{'adc':'https://www.ti.com/lit/ds/symlink/ads1299.pdf','ldo':'https://www.ti.com/lit/ds/symlink/tps7a24.pdf'},
 'assumptions':{'battery_min_max_v':[vmin,vmax],'afe_current_a':load,'fuse_resistance_upper_ohm':15,'diode_drop_allowance_v':.5,'harness_switch_drop_allowance_v':.1,'ldo_total_output_error_budget':error,'ldo_dropout_max_at_200ma_v':.25,'capacitor_positive_tolerance':.1,'capacitor_positive_temperature_allowance':.15,'low_energy_dc_fault_voltage_v':fault_v,'resistor_negative_tolerance':.01,'thermal_model':'TI JEDEC board, not this layout; physical thermal measurements required'},
 'calculations':calculations,
 'conditional_checks':[{'name':n,'passed':bool(ok)} for n,ok in checks],
 'open_items':['Effective minimum capacitance, cold/aged startup and stability measurements required','C29 must retain >=10uF at 4.5V including temperature/tolerance/aging','TPS7A24 noise/overshoot and ADC PSRR must be assessed in assembled board','Battery limits are assumptions, not discharge limits or an automatic cutoff','Nano branch protection, VIN radio-burst droop and interference require validation','BAV199 does not guarantee rail +/-0.3V clamping: TI internal clamps may conduct first','Injection-current calculation does not prove rails can sink current or establish acceptable body current','Power-off analog and GPIO injection can back-power rails and violate LDO VOUT <= VIN+0.3V; no live inputs with board off','20k input paths allow hundreds of microamps in a rail-to-contact fault; not a qualified body protection design','Bias resistor fault bounds, aggregate leakage, cable compensation and ESD tests remain open','No mains, defibrillator or IEC patient-protection compliance claim']}
(ROOT/'hardware/validation/electrical-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(f'Conditional calculations: {sum(ok for _,ok in checks)}/{len(checks)}; manufacturing/body readiness remains false')
raise SystemExit(0 if all(ok for _,ok in checks) else 1)
