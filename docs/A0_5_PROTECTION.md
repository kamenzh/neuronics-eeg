# A0.5 electrical protection and failure review

This revision targets an eight-channel EEG recorder using the existing Nano. It addresses a reproducible low-voltage power-off fault from A0.4. All results below are calculations or checks of saved design files. No board, leads, enclosure or patient-connected system has been tested. The Sino-k mating-dimension inquiry is pending.

## What changed electrically

- Each of the eight recording contacts and REF now enters through two 100 kΩ, 0.1% thin-film resistors in series. C1–C8 are 470 pF and C9 is 330 pF, all 1% C0G. The nine clamp networks and the two 499 kΩ bias-output resistors remain. Sources: [100 kΩ](https://www.yageogroup.com/component-documentation/download/specsheet/RT0805BRD07100KL), [470 pF](https://yageogroup.com/download/specsheet/C0805C471F5GACTU), [330 pF](https://yageogroup.com/download/specsheet/C0805C331F5GACTU).
- R50 and R52 are separate 499 Ω, 1%, 0.125 W paths from AVDD to ground. R52 has a dedicated ground via. R51 remains 1 kΩ on DVDD. Maximum resistor dissipation is about 53.2 mW per analog bleed under the modeled corners. Both AVDD bleeds depend on PCB ground and the local supply copper. [499 Ω part](https://yageogroup.com/component-documentation/download/specsheet/RC0805FR-07499RL).
- F1 is Bourns MF-MSMF014-2 in the existing 1812 land pattern. At 23 °C its hold/trip currents are 140/340 mA, compared with 100/300 mA for A0.4. R1max falls from 15 Ω to 6.5 Ω. The PTC protects the board's battery branch. Its thermal trip characteristics cannot limit electrode currents. [Bourns electrical and derating tables](https://bourns.com/docs/product-datasheets/mf-msmf.pdf).
- J11 pad 2 is now electrically isolated and explicitly NC in KiCad. Pin 1 remains the signal return. Assemble the header with the exposed pin-2 mating post removed and block cavity 2 on the matching socket. The pad and solder tail may remain. Use the labeled pin-1 position and a captive guide to prevent a one-row or one-column offset. The A0.3/A0.4 cable drawing showing a second ground wire is superseded.

## Power-off injection through the contacts

The stress limit of interest for the TPS7A24 is VOUT ≤ VIN + 0.3 V. For this **steady positive DC** case, hold VIN at 0 V and treat each driven contact as a source relative to PCB ground. A zero-drop clamp feeding AVDD and zero credit for other loads maximize AVDD in this model. The BIAS path is included conservatively as an additional path to AVDD. For parallel contact-path conductance G and active bleed conductance B, AVDD = Vsource × G/(G + B). The verifier reads component values and connectivity from KiCad's exported netlist. It uses an engineering allowance of −2% for series resistances and +2% for bleeds; this is not a measured lifetime limit. [TI regulator, §8.1.4](https://www.ti.com/lit/ds/symlink/tps7a24.pdf).

| Ground-referenced DC case | A0.4 | A0.5 |
| --- | ---: | ---: |
| One 5.1 V recording input, one of its two resistors shorted | 0.472 V | 0.0132 V |
| Nine intact recording/reference paths at 10.2 V | about 3.21 V under A0.4's zero-drop model | about 0.118 V |
| All ten paths at 10.2 V, either analog bleed open | Loss of the sole intentional AVDD discharge path | 0.2380 V |

All 138 combinations of 1, 9 or 10 driven paths, 5.1/10.2 V, intact parts, each possible single series-resistor short and either single bleed open are below 0.3 V in this model. Check [case data](../hardware/validation/contact-faults.json) and [the executable calculation](../tools/check_contact_faults.py). A disconnected series resistor reduces that branch's DC contribution. A shorted bleed or clamp can instead collapse a rail or disable a channel and must be treated as a failed instrument.

**Patient fault current is a different quantity.** For a hypothetical 5.1 V internal rail-to-contact fault with a board-ground return, the intact series pair permits up to 26.0 µA. One shorted series resistor gives 52.0 µA. Nine intact parallel paths in a common-source/common-return fault could carry about 234 µA in aggregate. At 10.2 V one surviving 98 kΩ resistor can pass about 104 µA with either polarity. A wire short upstream of these resistors bypasses them. Neither the DC injection calculation nor an individual electrode current establishes system safety.

## USB and harness protection

The Nano and AFE share ground through J11 and through the battery wiring. Opening the battery switch or disconnecting J11 alone may leave a conductive return. For the recording enclosure use the following **mechanical design requirement**, still awaiting implementation and inspection:

1. Mount the Nano in a removable carrier with one captive docking interface for all GPIO, host 3V3, VIN and every ground wire. Keep the galvanically connected ADC, Nano, battery and all wiring inside the battery-powered assembly. Cover all other service/test connections.
2. Orient the Nano USB port against a fixed insulating wall so a USB plug cannot engage until the carrier has fully separated from every docking contact. A USB plug already inserted must mechanically block docking. Use wireless data during acquisition. Provide no external charging or instrument port.
3. Verify both directions of exclusion, including partial insertion, before energizing the assembly. In the USB-accessible position, verify the complete wiring diagram and measure absence of continuity from USB shell, ground and VBUS to all AFE power, ground and contact terminals. A handheld meter checks wiring only. Insulation/leakage qualification requires appropriate equipment and review.

A loose Nano, an ordinary ribbon cable, or a software operating mode cannot implement that exclusion. If simultaneous USB and electrodes must be supported, the power and signal interface requires a separately engineered isolation barrier. The present PCB has none. A qualified reviewer must assess complete-system protection, operating/fault states and applicable test limits before any person connection. [IEC EEG safety and essential performance](https://webstore.iec.ch/en/publication/92074).

## Other ways the board can fail

| Finding | Design decision or measured evidence needed |
| --- | --- |
| Reverse insertion of the original unkeyed J11 placed host 3V3 directly on grounded pad 2 | A0.5 removes this copper connection and specifies the mating key. Reverse and offset insertion can still cross-connect GPIO if the harness is assembled incorrectly. Verify every cable pin end-to-end, check pin 2 unwired and test the guide unpowered. |
| Battery droop and warmed PTC | At the revised 66 mA AFE budget, the old PTC left 5.61 V at the regulator input under the existing low-pack assumptions. The new part gives 6.171 V (7.2 V pack, 6.5 Ω PTC, 0.5 V diode and 0.1 V wiring). R1max is a specified test-condition value. Measure warm resistance, common wiring drop and Nano radio-burst minima. The pack has no automatic undervoltage cutoff. |
| Regulator heating | The revised analog allowance is 52 mA and the digital allowance is 14 mA. At 10.2 V, modeled upper regulator dissipation is 0.276 W and 0.098 W. The datasheet-board thermal estimate for U2 is a 46 °C rise. Measure temperatures in the intended enclosure at maximum input/load and compare to device operating limits. |
| Interference and noise at larger input resistance | The resistor pair on each side contributes a calculated 0.512 µV RMS differential over 0.5–40 Hz, before ADC, electrode and amplifier noise. The lower C9 compensates the *illustrative* extra 7 × 20 pF on the shared reference. At 60 Hz, equal source impedances and that typical capacitance, the worst initial R/C tolerance corner is 63.4 dB. Adding 5 kΩ on the record side gives 55.9 dB. At 10 pF/input even equal sources give 44.5 dB. Measure instead of assuming the capacitance model holds. The preliminary balanced goal remains 60 dB. [TI electrical characteristics](https://www.ti.com/lit/ds/symlink/ads1299.pdf) · [Sensitivity sweep](../hardware/validation/input-model.json). |
| DC offset from unequal bias/leakage currents | 1 nA of *net mismatch* across 200 kΩ produces 200 µV. With eight negative inputs sharing REF, temperature, dirty flux or clamp leakage can shift all channels together. Measure offset at operating temperature on balanced dummy sources and check recovery and headroom at each gain. |
| Power reset, partial supplies, fast transients or negative inputs | The resistive model omits charge already in the capacitors and parasitic paths. Measure AVDD−VIN and DVDD−VIN during collapse/restart, host-only and AFE-only power. Check pin excursions and clamp currents for both polarities in a current-limited dummy fixture. Reject unexpected backfeed, overshoot above device ratings, or invalid recordings. Keep external sources disconnected during rewiring. |
| Bias oscillation or missing common-mode return | Keep bias/lead-off disabled for initial internal tests. External dummy tests need a defined common-mode return. Sweep cable capacitance and impedance before enabling feedback, checking BIASOUT settling, saturation and sustained oscillation. |

The PCB and CAM files are suitable for engineering review. The assembled protective enclosure, fault and leakage measurements, analog qualification, firmware and PC acquisition remain open. The [bench sequence](reviews/independent-577aad8-2026-11-17/VERIFICATION_PLAN.md) and [A0.5 fabrication package](../hardware/fabrication/A0.5/) tie these next checks to this revision.
