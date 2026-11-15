# Independent EEG PCB review — A0.2

Reviewed commit: **`558886fb6f877d274462cd4d457188c72b215d7d`** (`kamenzh/neuronics-eeg`). Review date: **2026-11-15**. This is a **separate AI design review**, not a review or certification by a qualified human engineer. It used a detached worktree, fresh KiCad exports and read-only inspection of the saved PCB; a disposable project copy was used for zone refill. No reviewed schematic, footprint, placement or copper was changed. **No hardware testing or safety certification was performed.**

## Recommendation

The [reproducible evidence](../hardware/validation/independent-a0_2/) accompanies this report. See [the action roadmap](NEXT_STEPS.md) for the implementation sequence and [the review handoff](REVIEW_HANDOFF_A0_2.md) to request another review of the same hardware revision.

**Do not order the current board yet.** Its logical connectivity is substantially sound, and fresh ERC/full schematic-parity DRC pass. I found no ADS1299 physical pin-map error. However, there are avoidable layout weaknesses, a socket tolerance stack that is not closed, and capacitor operating-value evidence still missing. These can be addressed before spending money on a board that may need rework.

The minimum pre-order work is:

1. **Reroute the ADS1299 supply/reference/bypass area** as described in IR-01. Keep the useful continuous ground plane, but shorten the local loops and give AVDD1 an intentional supply/return connection.
2. **Verify actual electrode/socket mating and close the three-hole socket fit**, using the manufacturer's tolerances, the chosen PCB fabricator's finished-hole tolerances and a coupon/sample. Change the footprint if necessary; do not simply assume a nominal fit (IR-02).
3. **Select capacitors using effective capacitance at the actual operating conditions**, especially C29. A larger/parallel reference-capacitor option may change placement and routing (IR-03).
4. **Replace the six 100 kΩ control pull-downs with values that guarantee LOW**, including receiver and controller leakage. This is a BOM/value change, not a footprint change (IR-04).
5. Define the complete battery/controller harness and power sequencing. For a reusable prototype that can be switched independently or debugged over USB, add hardware handling for unpowered interfaces before layout release (IR-05). A tightly controlled, electrode-disconnected bench setup can instead accept this limitation explicitly.

After these changes, a **bench fabrication candidate** can be prepared with a named fabricator/stack-up, fresh checks and an intentional assembly/test package. It will still **not be safe for body use merely because it passes bench tests**. Body-current protection, fault handling, enclosure, cable loading and system-level leakage remain a separate, unresolved design task.

Severity meanings below: **High** means resolve before an intentional fabrication release, or explicitly constrain the bench setup where stated. **Medium** means a material functional/measurement risk to resolve during prototype development. **Low** means a workflow or usability improvement. A finding marked “uncertainty” is not an observed failure.

## IR-01 — High: local ADC supply/reference layout needs revision

**Type/confidence:** confirmed geometry and departure from manufacturer guidance; high confidence. Its effect on measured noise or startup is **not measured**. **Rerouting required for the recommended correction.**

**Location:** `hardware/kicad/neuronic.kicad_pcb`, U1 at approximately (100, 92) mm; AVDD_5V, DVDD_3V3, VREFP, VCAP1–4; C24–C41. Coordinates below are PCB coordinates in millimetres.

The 0.20 mm AVDD feed enters the local area through C36, reaches **U1.54 AVDD1 at (101.25, 86.3375)**, then continues through the supply connections around U1.56 and U1.59 toward the bottom analog-supply pins. U1.59 also feeds a roughly 9.2 mm under-package segment toward the lower pins. This is a shared daisy-chain path, not an intentional AVDD1 branch returning to a supply star point. C36's GND connection reaches a via at **(104.29, 79.6375)**; U1.53 AVSS1 reaches GND at **(101.75, 88)**. These vias are 8.74 mm apart. C26/C27 share the former ground-via connection. A continuous plane is beneficial, but it does not make these local charging-current loops disappear.

Independent centerline measurements of the saved copper:

| Connection | Route length | Layer transitions | Interpretation |
|---|---:|---:|---|
| U1.54 AVDD1 → C36.1 | 4.65 mm | 0 | Nearest AVDD bypass to this pin; return vias are 8.74 mm apart |
| U1.59 AVDD → C34.1 | 3.70 mm | 0 | C34 return via is 8.71 mm from the U1.58 return via |
| U1.24 VREFP → C30.1, 100 nF | 7.79 mm | 2 | Reference bypass changes to In2.Cu and back |
| U1.24 VREFP → C29.1, 22 µF | 14.40 mm | 2 | C29 at (94.5, 108); return-via separation from U1.25 is 14.22 mm |
| U1.55 VCAP3 → C26.1 / C27.1 | 8.88 / 11.38 mm | 0 / 0 | Both capacitors are north of the package; C27's GND trace to its first via is another 4.45 mm |
| U1.28 VCAP1 → C24.1 | 9.75 mm | 0 | Reference-related node routed to (105, 105.46) |
| U1.30 VCAP2 → C25.1 | 7.71 mm | 0 | A local bypass can be placed much closer |
| U1.26 VCAP4 → C28.1 | 8.52 mm | 0 | Meanders around lower supply connections |
| U1.50 DVDD → nearest C39.1 | 8.68 mm | 0 | C40 is 13.38 mm away by copper, despite its intended proximity |

These are copper centerline approximations, including short distances within pads, excluding via barrel height. Plane-via separation is a geometric observation, **not** a calculated ground impedance or field simulation.

I checked alternate same-net bypass paths: **U1.22 reaches C31 in 3.66 mm and C32 in 4.71 mm**. Therefore its 15.77 mm route to C33 is inefficient/redundant, not evidence that pin 22 has no closer bypass. U1.48 reaches C39 in 3.39 mm. These distinctions matter when evaluating the layout.

**Source and consequence:** [TI ADS1299 SBAS499C](https://www.ti.com/lit/ds/symlink/ads1299.pdf), section 11, page 70, specifically recommends star connection of AVDD1/AVSS1 because of charge-pump transients. The note to Figure 77, page 71, calls for supply, reference and VCAP capacitors close to the package. Section 6 identifies the required supply-pin bypass connections. The present geometry adds shared supply impedance and loop area in nodes where microvolt performance is the objective. A zero-error DRC does not evaluate this.

**Fix:** move C29/C30 and C24–C28 into the immediate pin escape area; connect the VREF pair locally to U1.24/U1.25; connect the AVDD1 bypass directly between the pin pair with a short local return; branch AVDD1 deliberately into the common supply rather than feeding other analog pins through that branch. Give pin 59/pin 58 their own compact loop. Bring pin 50's bypass closer. Reorganize nearby passives before routing; avoid making a new split in the ground plane just to imitate a schematic star symbol.

**Verify:** repeat the read-only path inventory and visual review after routing, fresh parity DRC and zone refill. On the assembled board, measure supply/reference startup and ripple at U1, then input-short noise/PSD with radio off/on and with the real harness. There is no demonstrated noise-failure threshold at a particular trace length; this is a preventative layout correction supported by TI's guidance.

## IR-02 — High: socket nominal geometry matches, but guaranteed fit is not established

**Type/confidence:** unresolved mechanical release condition with a concrete tolerance conflict under stated assumptions. High confidence in nominal dimensions and arithmetic; **not an observed assembly failure**. A footprint/drill change may be needed.

**Location:** J1–J10; `hardware/footprints/P1_36619_Touchproof_RA.kicad_mod` and bundled `hardware/kicad/Neuronic.pretty/P1_36619_Touchproof_RA.kicad_mod`. Signal pads lie at x = 67.026 mm; dummy legs at x = 56.866 mm. Adjacent socket centres are 8.20 mm apart.

The [P1 36619-50 revision H drawing](https://catalog.p1tec.com/dash50/36619_dash50.pdf) and [manufacturer catalogue](https://catalog.p1tec.com/?FILTER_CLEAR=&FILTER_FCOMPONENT=36619) support the selected right-angle 1.5 mm family. The actual pad pattern uses the primary inch dimensions correctly: a 10.16 mm longitudinal offset and ±2.54 mm transverse offsets. Pad 1 is the signal; the two plated dummy holes have no net and are isolated. The socket faces the left board edge. This is not a pin-polarity or mirrored-footprint error.

The drawing's general tolerances are ±0.01 inch for two-place dimensions and ±0.005 inch for three-place dimensions. Applying these to rigid, unbent legs gives:

| Quantity | Calculation | Result |
|---|---|---:|
| Largest round signal leg | (0.060 + 0.010) × 25.4 | 1.778 mm |
| Signal radial float in a nominal 1.90 mm finished hole | (1.90 − 1.778) / 2 | 0.061 mm |
| Largest rectangular dummy section | (0.046 + 0.005) × 25.4 by (0.020 + 0.010) × 25.4 | 1.2954 × 0.762 mm |
| Dummy diagonal, centred | sqrt(1.2954² + 0.762²) | 1.503 mm |
| Each dummy's transverse location allowance | 0.010 × 25.4 | 0.254 mm |
| Hole diameter containing that rectangle at a 0.254 mm transverse offset | 2 × sqrt((1.2954/2)² + (0.762/2 + 0.254)²) | **1.8141 mm** |

Thus the **1.80 mm nominal dummy holes do not cover that full combined corner even before PCB hole tolerance**. If both dummy legs are displaced outward, translating the socket cannot cure their increased separation. Along the longitudinal axis, the nominal holes permit about **0.1677 mm dummy float + 0.0610 mm signal float = 0.2287 mm**, below the drawing's 0.254 mm span allowance under the same maximum-section assumptions. These are deliberately conservative simultaneous extremes; supplier knowledge about correlated tolerances or actual leg compliance could change the accepted stack.

The project gives no fabricator's guaranteed finished-hole range. An illustrative −0.10 mm hole allowance would reduce signal float to 0.011 mm and make the dummy case worse; **this is not an assertion that a selected fabricator has that tolerance**. Hole position, plating, solder clearance and leg forming are additional considerations. Do not enlarge holes blindly: preserve adequate annular ring and mechanical solder-joint strength.

The maximum 6.604 mm housing width still leaves about 1.596 mm between housings at the 8.20 mm pitch. The 8.10 mm courtyard leaves only 0.10 mm between courtyards, but that is not itself a collision. The nominal 0.50 mm nose overhang varies by roughly ±0.508 mm from the two controlling length tolerances alone; enclosure access needs its own dimensions. The plug shell and cable bend clearance are not established by this PCB footprint.

**Fix/verify:** obtain a socket sample and physically mate the owned Sino-k cable; inspect/measure all three legs; confirm the exact black ordering MPN through the P1 catalogue's ordering link; obtain a recommended hole pattern or an approved tolerance interpretation. Make a three-hole coupon with the chosen fabricator's actual drill/plating specification. Check fit without forcing/bending, solder wetting and repeated insertion/extraction with the board supported. The drawing discourages wave soldering; use the stated hand-assembly route. The manufacturer's touchproof description is not finished-system safety qualification.

## IR-03 — High release uncertainty: operating capacitor values remain unproved

**Location:** `hardware/parts.json`, C29 = GRM31CR61E226KE15L, C24 = T491B107M006AT, C21/C25/C26/C28/C31–C36/C39/C40 = C0805C105K3RACTU; actual nodes are in `power.kicad_sch` and U1 bypass nets. Confidence: high that required evidence is absent; **no claim that the selected capacitors have been measured below specification**.

C29 is nominally 22 µF, ±10%, X5R. TI requires at least 10 µF at VREFP. Before DC-bias, small-signal AC-level and aging effects, a conservative tolerance/temperature corner gives **22 × 0.90 × 0.85 = 16.83 µF**. The remaining combined retention must exceed **59.4%** to stay at 10 µF. A 25 V voltage rating does not establish that retention at 4.5 V. The [Murata part-specific reference sheet](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM31CR61E226KE15-01A.pdf) and [SimSurfing model](https://ds.murata.com/simsurfing/mlcc.html?partnumbers=%5B%22GRM31CR61E226KE15%22%5D) must be checked for the exact part. I could retrieve indexed specifications but not a usable numeric operating-point curve/export in this review; the direct model page returned HTTP 403. This remains an evidence gap, not a passed capacitance check.

C24's polarity is correct: positive pad 1 to VCAP1, pad 2 to GND. Its [KEMET part-specific sheet](https://search.kemet.com/component-documentation/download/specsheet/T491B107M006AT) identifies a 100 µF ±20% tantalum, with 2 Ω ESR at 100 kHz and 6.3 µA leakage at its specified test condition. Tantalum is an expressly permitted nonferroelectric choice in TI section 11; I do not reject it merely for being tantalum or for its tolerance. However, capacitance, leakage and settling still influence the reference-related node; the rated-voltage leakage number is not a measurement at the actual VCAP voltage.

The [1 µF KEMET sheet](https://search.kemet.com/component-documentation/download/specsheet/C0805C105K3RACTU) identifies Class II X7R, ±10%, ±15% temperature characteristic and aging. These nominal 1 µF bypasses are not automatically guaranteed to remain 1 µF in use. Also distinguish TI's nominal bypass recommendation from its explicit minimum reference-capacitance requirement: do not call every ±10% bypass a demonstrated defect.

The direct LDO output totals from actual connectivity are **17.1 µF AVDD** and **6.8 µF DVDD**; VCAP and reference capacitors are not direct LDO output capacitors. Even the conservative AVDD positive tolerance/temperature estimate, 21.63 µF, is below the TPS7A24 recommended 50 µF effective upper bound. I found no excessive-output-capacitance defect. Effective minimum output/input capacitance and stability remain to be established at voltage and temperature.

**Fix/verify:** record operating-point capacitance calculations and exact replacement MPNs before order release. Give C29 adequate documented margin, using a suitable part or parallel option; allow room now if that changes its footprint. Validate VREF, VCAP1 startup/settling and the other bypass voltages on the assembled board, including cold/aged conditions appropriate to the intended prototype range. This may require BOM-only changes, or placement/routing if more area is needed.

## IR-04 — Medium actual margin defect: 100 kΩ control pull-downs do not guarantee LOW

**Location:** `neuronic.kicad_sch`, R30–R35, U1 pins 39, 36, 35, 38, 40 and 34; nets ADS_CS_N, ADS_RESET_N, ADS_PWDN_N, ADS_START, SPI_SCLK and SPI_MOSI. High confidence. **No reroute required** if only the resistor values change.

[TI ADS1299 section 7.5, page 10](https://www.ti.com/lit/ds/symlink/ads1299.pdf) specifies digital input current up to ±10 µA and LOW input voltage no higher than **0.2 × DVDD**. At the conservative 3.234 V rail minimum, the LOW ceiling is **0.6468 V**. A 100 kΩ +1% resistor permits **1.01 V** from +10 µA leakage alone. Thus a floating/high-impedance controller does not have a guaranteed LOW state over these stated limits. Typical devices may work; that is different from a closed margin.

**Fix:** use at most approximately 64 kΩ nominal before adding resistor tolerance and controller/harness leakage; **47 kΩ or less** is a practical starting choice. Include both receivers' leakage and any controller boot pulls in the final bound. **Verify:** check logic levels at supply corners with the controller detached, reset and unpowered; verify startup/reset behavior. This change does not solve active GPIO backfeeding in IR-05.

## IR-05 — High for a robust reusable bench prototype: independent power domains can backfeed

**Type/confidence:** confirmed unprotected paths; high confidence. Actual injected current, rail rise and damage are unmeasured. **Hardware correction can require schematic changes and rerouting.** A restricted, electrode-disconnected bench protocol can defer it, but this is a real operating limitation.

**Location:** J11 directly connects SPI/control GPIOs to U1 without series impedance or a fail-safe buffer. R30–R35 are shunts, not series current limiters. SW1 switches only the AFE's VBAT path; the Nano has a separate power branch. U2/U3 pins 5 are directly connected to the AFE rails. D1–D9 connect input clamp currents into AVDD_5V/GND.

Turning the AFE off while the Nano remains powered, including during USB debugging, leaves GPIOs able to drive an unpowered ADS1299. Conversely, an operating AFE can drive DOUT/DRDY into an unpowered host. Positive analog input excursions can also feed AVDD. A 100 mA PTC is not a microamp/milliamp rail-clamp or interface sequencer. D10's input-polarity isolation is useful but is not a general guarantee that both LDO outputs satisfy their reverse-voltage condition.

**Sources:** [TI ADS1299](https://www.ti.com/lit/ds/symlink/ads1299.pdf), sections 7.1, 7.3 and 11.1; [TPS7A24](https://www.ti.com/lit/ds/symlink/tps7a24.pdf), sections 6.1 and 8.1.4; [Waveshare Nano schematic](https://files.waveshare.com/wiki/ESP32-S3-Nano/ESP32-S3-Nano-Schematic.pdf). The LDO's VOUT ≤ VIN + 0.3 V condition matters, and reverse current is not internally limited. Its active overshoot pull-down feature is not a specified substitute for an arbitrary externally injected current sink.

**Fix:** decide the interface's powered/unpowered contract. For ordinary independent switching, use appropriate power-off tolerant isolation/buffering with output enable controlled by valid rails, or another verified interlock/sequence. Series resistors can bound some injection and aid edge damping, but do not by themselves eliminate phantom powering; size and verify them against the actual receiver limits and cable capacitance. Define the Nano battery branch fuse/switch and shared return, connector polarity and startup/shutdown order. Do not take Nano radio current from U2/U3.

**Verify:** with no electrodes/person connected, current-limited sources and a defined fixture, test each power-order case and input clamp case; record both rails, reverse/input currents, reset state and recovery. Inspect the host pins too. Before this is corrected, drive no external analog signals while the AFE is off, and de-energize both ends before rewiring; firmware alone cannot enforce a condition when the relevant controller is unpowered.

### Power checks that did not reveal an immediate sizing defect

U2/U3's fixed-version pinout is correct: 1 IN, 2 GND, 3 EN = IN, 4 NC grounded, 5 OUT; their SOT-23-5 pads agree. The conservative additive accuracy allowance (1.25% + 0.25% + 0.5%) gives 4.90–5.10 V and 3.234–3.366 V, inside ADS1299 operating rails under the stated regulation conditions. With a 7.2 V pack, 40 mA budget, 15 Ω fuse, 0.5 V diode and 0.1 V harness allowances, LDO input is 6.0 V. This provides 0.5 V beyond the 5.5 V line-regulation test boundary. At 10.2 V and 30/10 mA, losses are about 159/69.7 mW, corresponding to about 26.7/11.7 °C rise using the datasheet board's thermal resistance, **not a validated temperature for this PCB/enclosure**.

The ADS1299's normal bias-off typical currents are only about 7.14 mA analog and 1 mA digital at its stated conditions, so the 30/10 mA budget is generous; it is not a measured consumption value. LDO no-load/power-down behavior, inrush, battery-endpoint behavior and PTC temperature derating still need checking. The LDO's 300 µV RMS noise figure is for its stated 1.24 V/10 Hz–100 kHz condition; it must not be combined with a single-frequency ADC PSRR number to claim an EEG noise floor. Startup, dropout recovery overshoot and radio-coupled noise need measurement.

## IR-06 — Medium: shared-reference/RF-filter imbalance is absent from the existing model

**Location:** R1–R18 and C1–C9 in `inputs.kicad_sch`; REF_FILTERED directly ties U1 pins 1/3/5/7/9/11/13/15; C9 at (89, 113). **Type:** quantified sensitivity, not measured system CMRR. A topology change could require rerouting; tighter/matched values may not.

The direct reference bus is valid with SRB1/SRB2 disabled; it is not a wiring mistake. But eight negative inputs and their parasitics load one filtered reference, while each positive input has its own RC. The reference net has **71.78 mm total tracked copper and eight vias**; point-to-point paths from C9 to U1 negative pins range approximately 24.38–33.42 mm. Positive-filter capacitor to U1 routes range approximately 7.25–14.82 mm. These distances do not establish capacitance by themselves.

`tools/simulate_input.py` only models one ideal 20 kΩ/1 nF branch. My separate calculation uses H = 1/(1+jωRC): with only the stated resistor/capacitor tolerance extremes, R+ = 19.8 kΩ, C+ = 0.95 nF and Rref = 20.2 kΩ, Cref = 1.05 nF, the differential conversion of common mode is **−62.45 dB at 50 Hz** and **−60.87 dB at 60 Hz**. For example, 100 mV of common-mode interference becomes about 75/90 µV differential in this simplified corner case, before ADC conversion. A notch filter cannot recover headroom already lost to saturation.

As a separate sensitivity example, treating the datasheet's typical 20 pF input capacitance as a shunt at every input makes nominal positive/reference effective values 1.02/1.16 nF; this gives about 61.1 dB at 50 Hz. **That is not a guaranteed model of the ADC's common-mode capacitance.** Electrode impedance, cable capacitance, leakage and bias feedback are omitted. The specified ADC CMRR therefore cannot be presented as the completed PCB's CMRR.

The two 20 kΩ paths contribute roughly **0.162 µV RMS over 0.5–40 Hz** at 300 K before ADC/electrode noise. Shared-reference resistor noise is correlated between channels. These values are design tradeoffs, not automatic rejection of 20 kΩ protection resistance.

**Fix/verify:** establish a noise/CMRR target; evaluate matched filtering or a revised input/reference arrangement while preserving protection. Use an electrode simulator with controlled common-mode signal, source-impedance imbalance and cable capacitance, recording raw data at 50/60 Hz and across the acquisition band. This is a useful bench-performance gate, not by itself proof the first prototype cannot collect data.

## IR-07 — Medium functional uncertainty, body-use blocker: clamps and bias need system tests

**Location:** D1–D9 BAV199, R1–R18, U1.61/.63, R20/C10, R21/R22 and J10. High confidence in connectivity; stability, surge and body-current qualification remain unmeasured.

The [Nexperia BAV199 pinning](https://assets.nexperia.com/documents/data-sheet/BAV199.pdf) agrees with the actual board: pin 1 anode to GND, pin 2 cathode to AVDD, pin 3 midpoint to signal. The two 10 kΩ resistors precede each clamp. I found no reversed clamp. However, its specified forward drop can be 0.9 V at 1 mA; it does not guarantee clamping within the ADC's rail ±0.3 V absolute-voltage window. ADC internal clamps can conduct first. The relevant protection is the bounded source current plus rail behavior, not the diode's mere presence.

For a deliberately bounded 10.2 V low-energy DC source, the −1% resistors give 0.515 mA per two-resistor input path, or 1.030 mA with one resistor shorted. Nine such simultaneous source paths give a conservative **4.636 mA sum**, but actual current depends on the rail/clamp voltage and state. An internal 5.1 V-to-contact fault through a 19.8 kΩ path permits about **258 µA**. These are circuit bounds, **not acceptable body-current limits**. Common faults, rail injection, reference-contact current, input source energy, contaminated-board leakage and fault combinations require a system model. No mains/defibrillation qualification follows from these resistors.

R20 = 1 MΩ and C10 = 1.5 nF are correctly in parallel from BIASOUT to BIASINV and match TI's example values. Their feedback corner is about **106 Hz**. R21 + R22 add **998 kΩ** outside that local feedback connection; with illustrative cable/electrode capacitances of 0.5/1/5 nF, the associated output pole is approximately **319/159/31.9 Hz**. This is enough to require a real loop analysis; the feedback corner alone is not a phase-margin result. The selected bias-sense channels also affect loop gain, and the shared reference must not be unintentionally counted eight times. The large output resistance trades drive authority and bandwidth for current limiting. Bounds at 5.1 V are 5.16 µA with both resistors and 10.32 µA with one shorted, without establishing an allowed body current.

**Fix/verify:** keep bias and lead-off disabled for initial internal tests, then test bias with an explicit cable/electrode/body simulator, selected-channel register dump, load steps, disconnect/reconnect and saturation recovery. Establish loop gain/phase margin with a defensible model or measurement. Test leakage/clamping and power-off cases with a current-limited fixture. The existing 0805 feedback parts can be retuned without a respin; a new protection architecture may require one. A body-connected final design requires a separate qualified system review.

## IR-08 — Medium completion gap: acquisition firmware and startup proof do not exist yet

**Location:** `firmware/README.md`, `hardware/interface.json`, J11. High confidence. No firmware build or acquisition test was runnable because this commit contains no implementation.

The GPIO mapping matches the Waveshare schematic; remapping SCLK to GPIO5 avoids the GPIO48 SCK LED. The selected SPI mode 1 and 27-byte frame are appropriate. At 1 MHz, the ideal frame transfer is 216 µs within a 4 ms, 250 SPS period, leaving room for implementation overhead. That is a throughput calculation, not proof of lossless acquisition.

The direct reference bus requires MISC1.SRB1 = 0 and every CHnSET.SRB2 = 0. The internal voltage reference must be enabled explicitly in CONFIG3; reset defaults do not enable it. Since BIASREF is physically floating, enabling bias later also requires the intended internal BIASREF selection. Startup must wait for both TI's power-on interval and VCAP1 >1.1 V; 2^18 clocks at nominal 2.048 MHz is 128 ms, **not a universal sufficient delay for the 100 µF VCAP1 node**. Then reset, stop continuous-read mode before register writes, and verify the written settings by readback.

**Fix/verify:** implement register dump/readback, internal-test and input-short acquisition, signed 24-bit conversion, channel ordering, timestamps/counters and explicit overruns. Test radio-off and radio-on buffering. External bench inputs need a valid common-mode bias; directly grounding both inputs on this unipolar design is not the external low-noise test fixture. Firmware is not a reason to abandon a bench board, but it is required before claiming a useful working EEG prototype.

## IR-09 — Low workflow risk: passing tools have a narrow and partly shared basis

**Location:** `tools/check_design.py`, `check_board.py`, `check_routing.py`, `validate_kicad.py`, `route_hardware.py`, `generate_hardware.py`, `tests/test_workflow_guards.py`.

The fresh KiCad exporter, ERC and full schematic-parity DRC are meaningful checks. The existing pin-contract assertions supplement the generator and are useful. Most of the 462 connectivity assertions nevertheless compare the export to `design.json`, which was produced by the same generator; agreement cannot establish the original engineering intent. PCB pad checks establish net membership, not local return quality. The routing checker counts filled GND zones and keeps digital routing east of x = 103 mm; it does not compute return-path impedance or RF coupling. The nine electrical “passes” are conditional scalar bounds. The RC script is neither an ADS1299 simulation nor a nonlinear protection model.

The five workflow guards passed, including track/via/zone preservation and fresh-export failure handling. The committed `cli-checks.json` input hashes matched the reviewed CAD/configuration; **I found no stale-source success in this commit**. However, those hashes omit the checker/test source files. The SES import action accepts a supplied session and saves the board without a source-board/session hash match, backup or automatic subsequent validation. Its existing tests do not cover importing an obsolete session after manual routing changes. An explicit import can therefore replace routing without proving that it belongs to the current design.

**Fix/verify:** include tool/test versions or hashes in release evidence; restrict SES import to a matching source snapshot, preserve the pre-import board, and make refill plus full parity DRC mandatory after import. Do not regenerate a manually edited routed design just to update reports. Add focused stale-import/round-trip tests when changing that workflow. No hazardous import or regeneration was run against the reviewed board during this review.

## What was independently verified

- **All 64 ADS1299 physical names** were manually transcribed from TI's pin table and compared with the fresh schematic export; all 64 also matched PCB pad nets. The complete mapping, including coordinates, is in `ads1299-64-pin-contract.csv`. U1's TQFP numbering/orientation agrees with the top-view package convention. Pins 27/29/64 are open, RESV1 is GND, DAISY_IN is GND, unused GPIOs have 10 kΩ pull-downs, and CLKSEL has a 10 kΩ pull-up. Internal-clock and unused-bias pin handling are consistent with the intended configuration.
- **Power and clamp pinouts** agree with their manufacturer sources. All eight positive channels, shared negative reference and bias connector roles reach the expected physical pads. Capacitor and diode polarities were checked against the actual exported netlist and PCB.
- The saved board has **95 footprints**: 91 schematic components and four mechanical holes. It contains **537 track segments, 87 vias and two filled GND zones**. In1.Cu has no signal tracks; both saved fills have a single outline in the extracted representation. Fresh DRC reports no disconnected ground items. This supports continuity, not a complete return-current/EMI analysis.
- Digital tracks stay on the right side of U1; representative actual paths are 34.64 mm SCLK, 51.09 mm MOSI, 26.51 mm MISO and 34.85 mm DRDY. SCLK/MISO change layers and DRDY uses In2.Cu. The continuous In1 plane is a sound starting point, while In2 signal crossovers and the external Nano/harness still need measured coupling assessment.
- Standard 0805 passives, 0.5 mm-pitch TQFP and the through-hole connectors are feasible for careful hand assembly with magnification and appropriate tools. Clear bench-only silk and four mounting holes are useful. Add labelled GND/AVDD/DVDD/VREF/VCAP1 probe points and J11 pin/function/polarity markings before ordering if space permits; most small-component references are only on the assembly drawing. Support the long socket edge against insertion force and verify enclosure/fastener clearance. These are practical improvements, not observed solderability failures.

## Test record and limits

All commands below ran in `/workspace/scratch/3a280c114457/neuronic-review-a02`. Full commands, stdout/stderr, UTC timestamps and return codes are retained under `hardware/validation/independent-a0_2/`. KiCad CLI was **9.0.2**, pcbnew **9.0.2+dfsg-1**, and `/usr/bin/python3` **3.13.5**.

| Command | Exit | Result |
|---|---:|---|
| `/usr/bin/python3 tools/validate_kicad.py` | 0 | Fresh XML export; 462/462 connectivity; 370 PCB checks, 0 issues; ERC 0 errors/0 warnings; full schematic-parity DRC 0 violations/0 unconnected pads/0 footprint errors |
| `/usr/bin/python3 tools/check_routing.py` | 0 | 4/4 coarse checks; 537 tracks, 87 vias, 2 zones |
| `/usr/bin/python3 tools/review_electrical.py` | 0 | 9/9 conditional scalar checks; no manufacture/body approval |
| `/usr/bin/python3 tools/simulate_input.py` | 0 | Ideal RC pole 7957.75 Hz; approximately −0.000171 dB at 50 Hz |
| `/usr/bin/python3 -m unittest discover -s tests -v` | 0 | 5/5 workflow guards. The printed exit-2 netlist/ERC/DRC lines are intentional mocked failures in the stale-export regression test |
| `/usr/bin/python3 hardware/validation/independent-a0_2/inspect_actual_board.py` | 0 | 64 pin names and PCB parity, zero failures; route/return geometry and nearest bypasses extracted independently of generator metadata |
| `/usr/bin/python3 hardware/validation/independent-a0_2/independent_calculations.py` | 0 | Original socket stack, CMRR sensitivities, bias poles, power/current/noise and logic-margin calculations; not a physical simulation |
| `pcbnew.ZONE_FILLER(...).Fill(...)`, then `kicad-cli pcb drc --schematic-parity --exit-code-violations ...` in a disposable full project copy | 0 / 0 | Fresh refill of both zones; full parity DRC again reports 0 violations, 0 unconnected pads and 0 footprint errors. Exact command, output and pre/post hashes: `refill-check.json`; report: `refilled-drc.txt` |

The fresh ERC/DRC were invoked with `--exit-code-violations`; PCB DRC also used `--schematic-parity`. No DRC exclusions are configured. Some noncritical rule categories are ignored and board-wide minimum track width is zero while netclass routing uses 0.20 mm, with intentional 0.15 mm escapes. Select the fabricator's actual constraints and rerun DRC against them; today's pass does not certify a fabrication process.

No hardware, probes, measured electrodes, connector sample, fabricated coupon or working firmware was available. There was no ADC/bias-loop/nonlinear clamp SPICE test, no thermal/EMC measurement and no compliance test. The PCB tool checks and independent arithmetic must not be reported as those tests.

Evidence entry points: `test-runs.json`, `input-sha256.json`, `ads1299-64-pin-contract.csv`, `independent-geometry.json`, `independent-calculations.json`, the two independent Python scripts, and fresh `erc.txt`/`drc.txt`. Vendor documents are linked above rather than included in the deliverable evidence. Only the new report and new evidence directory should be collected from this worktree; existing generated validation files changed their timestamps/paths during reruns and are not proposed repository changes.

## Prioritized next actions

1. Correct the AVDD1/local reference/VCAP layout; change the control pull-down values.
2. Close the socket sample/coupon fit and exact-part effective-capacitance checks before finalizing placement.
3. Complete the battery/controller harness and decide whether to add power-off interface protection before ordering.
4. Freeze a bench-only fabrication package with fabricator constraints and freshly refilled, checked copper; implement acquisition firmware.
5. Carry out and record the physical measurements in [BENCH_TEST_PLAN.md](BENCH_TEST_PLAN.md), including the specific power-order, CMRR and bias-load cases above. Keep body use excluded until a separate qualified system review closes its requirements.
