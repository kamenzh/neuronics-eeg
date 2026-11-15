# A0.1 review checkpoint — 2026-11-15

Reconstructed on GitHub A0 commit `b8af12f03bf256dca78ebfd285dcb80679491b1f`.
Earlier local review work was not in that commit; the results here are from
newly generated and checked files, not copied test claims. KiCad 9.0.2 was used.
This remains an unrouted, bench-only design, not a fabrication release.

| Area | Change and rationale | Remaining evidence |
| --- | --- | --- |
| Shared reference | All IN1N–IN8N connect directly to REF_FILTERED; SRB1/SRB2 NC. Removes the previous AVDD termination of negative inputs and makes the measurement connection explicit | Common-mode range, shared reference impedance/noise and lead-off configuration review |
| Controller | Select owned Waveshare ESP32-S3-Nano; publish all eight GPIO assignments; J11.11 NC | Physical wire check, startup/unpowered backfeeding, streaming firmware |
| Supply | Six-AA alkaline candidate; separate Nano VIN branch; C21 reduced to 1uF | Complete harness and branch protection, DC-bias capacitance, thermal/startup/load-step/noise tests |
| Fuse | MF-MSMF010-2 with actual 1812 footprint instead of an 0805 resistor footprint | Temperature derating, fault interruption and board/harness coordination |
| Battery connector | JST B2B-XH-A with 2.50mm footprint, positive pin 1 | Mating harness and polarity inspection |
| VCAP1 | T491B107M006AT, 100uF polarized tantalum with B-case footprint | Leakage, surge/derating and settling validation |
| VREFP | C29 increased from nominal 10uF to 22uF/25V in 1206 | Must retain >=10uF effective at 4.5V including tolerance, temperature and aging |
| Components | 91 PCB components covered by 22 candidate MPN groups | Procurement/footprint review; ten electrode headers remain placeholders |
| CAD checks | Project symbol subsets bundled; electrical geometry on 1.27mm grid; NC net names match KiCad; holes marked board-only | Physical placement and copper design still incomplete |
| Workflow | Regeneration requires --overwrite and refuses boards containing copper; failed netlist exports cannot reuse stale results | Commit GUI changes before regeneration; future routed PCB edited in KiCad |

## Conditional calculations

`tools/review_electrical.py` derives rail capacitor totals from `design.json`.
The analog rail has 17.1uF nominal direct capacitance. A conservative +10%
tolerance and +15% temperature envelope gives 21.6315uF, below the MCP1703A
stated 22uF ceramic range. This does not establish effective minimum capacitance,
placement-dependent stability, regulator output overshoot or startup behavior.

With the assumed 7.2V minimum pack voltage, 40mA total AFE allowance, 15-ohm fuse
resistance, 0.5V diode and 0.1V wiring/switch drop, the LDO input is 6.0V.
Against 5.1V output (+2% assumption), this leaves 0.9V headroom. An assumed
0.725V dropout allowance fits, conditionally. At 10.2V the upper simple LDO
loss estimates are 0.156W analog and 0.069W digital, before upstream drops.
Junction temperature still depends on copper and enclosure conditions.

The ADC's ideal differential full scale at gain 12 and 4.5V reference is
+/-0.375V. This is not its allowable common-mode range or a noise specification.
The existing ideal RC calculation models one 20k/1nF path, not the whole EEG
circuit; shared-reference resistor noise is correlated across recorded channels.

## Protection and bias findings remain open

BAV199 forward voltage is not guaranteed to clamp within the ADC's rail +/-0.3V
absolute input range. Series resistance, diode leakage, rail sinking/backfeeding,
unpowered operation and transient paths need review together. The ADC's specified
injection-current limit is a silicon limit, not an allowable current through a person.

Two 499k bias resistors do not prove a safe system. Assess every channel/reference/
bias path and aggregate fault current. The 1Mohm/1.5nF feedback and long electrode
leads require a loop model and bench settling/stability tests. The Nano buck and
radio can also couple interference into reference, ground and supplies.

See `REVIEW_BLOCKERS.md` and `hardware/validation/STATUS.md`. No Gerbers are
provided. No human, electrode-noise, bias-loop or assembled-board test was run.
