#!/usr/bin/env python3
"""Conditional engineering calculations; NOT SPICE, safety or bench validation."""
import json
import re
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
a=interface['acquisition'];p=interface['power']; vmin,vmax=p['review_input_range_v']
# Explicit conservative assumptions, not measured part behavior.
load=(p['afe_analog_budget_ma']+p['afe_digital_budget_ma'])/1000
vin_min=vmin-load*15-.5-.1
result={
 'revision':design['revision'],'manufacture_ready':False,
 'assumptions':{'battery_min_max_v':[vmin,vmax],'afe_current_a':load,'fuse_resistance_upper_ohm':15,'diode_drop_allowance_v':.5,'harness_switch_drop_allowance_v':.1,'ldo_output_tolerance_assumption':.02,'ldo_dropout_allowance_v':.725,'capacitor_positive_tolerance':.1,'capacitor_positive_temperature_allowance':.15},
 'calculations':{'avdd_direct_caps_uF':analog,'avdd_nominal_uF':sum(analog.values()),'avdd_upper_uF_before_bias_aging':sum(analog.values())*1.1*1.15,'dvdd_direct_caps_uF':digital,'dvdd_nominal_uF':sum(digital.values()),'afe_ldo_min_input_v_conditional':vin_min,'analog_headroom_v_at_high_output':vin_min-5*1.02,'analog_ldo_power_w_upper_ignoring_input_drops':(vmax-5)*p['afe_analog_budget_ma']/1000,'digital_ldo_power_w_upper_ignoring_input_drops':(vmax-3.3)*p['afe_digital_budget_ma']/1000,'raw_bytes_s':a['sample_rate_sps']*a['frame_bytes'],'frame_read_us_ideal':a['frame_bytes']*8/a['initial_spi_hz']*1e6,'sample_period_us':1e6/a['sample_rate_sps'],'ideal_differential_full_scale_v':4.5/a['initial_gain']},
 'open_items':['No guaranteed effective lower capacitance bounds or startup stability proof','C29 must retain >=10uF at 4.5V including temperature/tolerance/aging','Battery limits are operating assumptions, not measured discharge limits or an automatic cutoff','Nano separate branch protection/wiring/current budget and radio noise need validation','BAV199 forward voltage is not guaranteed to hold ADS input within AVSS-0.3/AVDD+0.3V','ADC injection-current limit is not a permissible body current','All electrode fault paths, aggregate current, unpowered backfeeding and bias-loop stability remain unresolved']}
checks=[('AVDD upper capacitance inside stated 22uF ceramic range',sum(analog.values())*1.1*1.15<=22),('Conditional analog dropout headroom',vin_min-5*1.02>=.725),('40mA AFE allowance below 100mA fuse hold at 23C',load<.1),('Eight-channel frame size',a['frame_bytes']==3+3*a['channels']),('Ideal SPI frame fits sample period',a['frame_bytes']*8/a['initial_spi_hz']<1/a['sample_rate_sps'])]
result['conditional_checks']=[{'name':n,'passed':bool(ok)} for n,ok in checks]
(ROOT/'hardware/validation/electrical-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(f'Conditional calculations: {sum(ok for _,ok in checks)}/{len(checks)}; manufacturing readiness remains false')
raise SystemExit(0 if all(ok for _,ok in checks) else 1)
