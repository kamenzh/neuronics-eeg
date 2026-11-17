# Independent engineering review — Neuronics EEG A0.3

**Reviewed commit:** `577aad8a8dee0c60e3b7e949f6b8f7cf200fe180`

**Repository:** https://github.com/kamenzh/neuronics-eeg

**Review date:** 2026-11-17

**Scope:** current `main` fetched for this review; it **matches** the supplied A0.3 checkpoint. Documentation-only review branch: `review/independent-577aad8-2026-11-17`. No hardware, firmware, generator or historical report was changed; no merge to `main` is authorized by this review.

## Verdict

**This is a plausible bench-development board, not a completed EEG instrument and not a board approved for connection to a person.** I found no confirmed fatal ADS1299 pin assignment, reversed channel polarity, missing routed connection or copper short in the saved CAD. Fresh native checks and independent pin/net inspection support that limited conclusion. They cannot establish noise performance, connector fit or human safety.

The strongest reasons to pause a full purchase are practical: **prove the actual Sino-k plug mates with the selected socket, confirm the socket's plated slots with the fabricator, and prepare an explicit manufacturing release.** A small electrode-disconnected prototype is a reasonable next engineering step once those inexpensive checks are closed. It is unnecessary to demand measured EEG performance before a prototype exists. It is equally unjustified to treat this review as permission for scalp recordings.

The most consequential open issues are:

- Shared-reference loading and real electrode/cable imbalance may convert common-mode interference into a signal much larger than EEG. The board's intrinsic ADC specification does not determine system CMRR.
- Analog input injection, regulator reverse current and intermediate brownout behavior remain untested. The new digital buffers are useful, but do not cover every analog or supply failure.
- Bias-loop stability and disconnect/recovery behavior have not been established for the actual sense mask and electrode/cable loads.
- Firmware and the recorder are specifications only. The hardware cannot yet produce a verified recording, and an internal test alone would not test the external electrode path.
- There is no demonstrated body-protection architecture. USB, charger and instrument grounds can join the electrode circuit through common ground. The bias resistors do not limit every possible electrode current.

A low-severity **confirmed documentation defect** also remains: `hardware/bom/README.md` describes 91 components, 22 groups and bench-header electrode connectors. The saved design contains **107 electrical components, 25 catalog groups (23 unique MPNs), and ten P1 socket footprints**. Do not use that README as the current shopping/assembly instruction.

## Scope, independence and evidence

The complete repository was cloned into a disposable working area. Source tree: `5f442167e52139c1d277884793f3417da6335e17`. The original PCB SHA-256 is `56e3c25c3cbefbf489e86c24db1670b0620a263d7c0c5adaea14d672e3de33b5`.

I first inspected `neuronic.kicad_pro`, the saved parent and three child schematics (`inputs`, `power`, `interface`), a fresh KiCad netlist, saved PCB pad/track/via/filled-zone geometry, library tables, project symbols/footprints, and the exact TI/P1/Waveshare documents. `parts.json` was used to identify purchase candidates, not as evidence that a connection existed. Its short historical annotations were encountered during identification. The [initial observations](evidence/INITIAL_FINDINGS.md) were written before opening previous review reports. They are preserved as hypotheses, including concerns that the subsequent analysis narrowed or disproved.

Only afterwards did I examine the prior review conclusions, `design.json`, validation/generation/routing scripts, tests, interface and firmware contracts, BOMs, status documents and bench procedures. Source inspection covered the generator's preservation guards and router import checks; **no source-board regeneration or router-session import was performed**.

Primary references, revisions and access limitations are in [SOURCES.md](SOURCES.md). Detailed independent calculations, physical comparisons and supply-state analysis are in [ENGINEERING.md](ENGINEERING.md). All numeric results in this report are either CAD measurements, arithmetic with stated assumptions, or explicitly identified source specifications. **No circuit simulation, manufactured-board measurement or biological recording was performed.**

Native evidence includes the [fresh schematic PDF](evidence/cad-exports/schematic.pdf), [netlist](evidence/fresh.net.xml), [all-component connectivity listing](evidence/schematic-connectivity.txt), [64-pin audit](evidence/ADS1299-pin-audit.csv), [BOM/CAD crosscheck](evidence/BOM-CAD-crosscheck.csv), [saved-board extraction](evidence/saved-board.json), exact KiCad SVG exports and separate plated/nonplated review drill files. The latter are **audit evidence, not a manufacturing package**.

## Checks actually performed

Toolchain: **KiCad CLI / pcbnew 9.0.2**, Debian CLI build identifying `9.0.2+dfsg-1`; system Python **3.13.5**, additional analysis Python **3.12.14**, git **2.52.0**. Commands, exit codes and stdout/stderr are retained in the evidence directory; see [evidence README](evidence/README.md). Original tracked-file hashes are in [source-sha256.json](evidence/source-sha256.json).

| Check | Actual result | What it does and does not establish |
| --- | --- | --- |
| Fetch current `main` and record full SHA | Matches supplied checkpoint | Identifies the reviewed revision; not an assertion about future `main`. |
| Fresh KiCad XML netlist export | Exit 0 | Exported from saved schematics, not `design.json`. |
| Native ERC, `--severity-all --exit-code-violations` | Exit 0; zero reported violations | Schematic rule checks under this project's settings. |
| Native PCB DRC, `--schematic-parity --all-track-errors --severity-all --exit-code-violations` | Exit 0; zero DRC, unconnected or footprint/parity errors under configured categories | Checks saved copper and schematic/PCB correspondence. |
| Native zone refill in a separate copy, followed by the same full DRC | Exit 0; zero violations; PCB SHA-256 unchanged after save | Existing fills reproduce with KiCad 9.0.2. No newer-version conversion was needed. |
| Raise all five ignored DRC categories to warnings in that copy; repeat full DRC | **Exit 5: 13 footprint-filter mismatch warnings**, zero copper/unconnected errors | Generic symbol footprint wildcards do not match custom library names for J1–J12 and F1. These are not 13 electrical faults. See full log. |
| Explicit DRC exclusion inspection | No item exclusions found | Categories were still ignored; they were separately exercised above. |
| Manual manufacturer pin/function comparison, then independent netlist-to-pad audit | 64/64 U1 connections agree | Includes reserved/unused pins, supply and VCAP pins. Does not test silicon or soldering. |
| BOM → fresh netlist → saved PCB identity comparison | 107/107 agree; 25 groups, 23 unique MPNs | Values, candidate MPNs and footprints are consistent; does not prove all parts fit or are in stock. |
| All four copper layers, saved fills, local routes and selected return paths | Examined and measured | Exact routes/coordinates retained. No electromagnetic field extraction or impedance model. |
| Native drill export | Exit 0; **20 plated G85 slots**, four 2.7mm NPTH mounting holes | Slot data is emitted; fabricator interpretation remains unverified. |
| `tools/validate_kicad.py` in copy | Exit 0; 573/573 connectivity contracts, 442 board checks, fresh ERC/DRC pass | Much of the expected topology shares the generator's model; not independent electrical proof. |
| `tools/check_routing.py` | Exit 0; 5/5 coarse checks | Counts/routing-region heuristics are not a return-path or signal-integrity analysis. |
| `tools/review_electrical.py` | Exit 0; 12/12 conditional checks | Arithmetic using assumed currents, capacitance factors and leakage bounds; no physical measurement. |
| `tools/simulate_input.py` | Exit 0 | Ideal RC calculations, **not SPICE** or a validated electrode/ADS model. |
| `tools/prepare_bom.py` in copy | Exit 0 | Fresh 107-component / 25-group candidate export. Original BOM untouched. |
| Workflow unit tests | Exit 0; **9/9 passed** | Preservation/stale-output/failed-import guard tests. Mocked failures in logs are expected test cases. |
| Historical result input hashes | **46/46 recorded hashes match** source | No stale-source mismatch found in the reviewed stored checks. |
| Exact-package drawing comparison | Performed for U1–U5, D1–D10, C24, socket/header/JST families and passive package candidates | Physical samples, actual assembly tolerances and final enclosure are **UNVERIFIED**. |
| Firmware build, stream capture, analog noise/CMRR, bias stability, rail transients, thermal/injection/ESD tests | **NOT RUN** | Firmware/recorder absent; no prototype, instruments or validated circuit model available. |
| Supplier CAM acceptance, complete delivered quote, enclosure fit, body leakage/single-fault assessment | **NOT RUN / UNVERIFIED** | No named fabricator has accepted this job; no body-use approval follows. |

## Prioritized findings

Severity describes the consequence in the stated use, not a prediction that a failure will occur. Confidence describes the strength of the evidence. “Measurement required” is not synonymous with “cannot fabricate a bench prototype.” All locations below refer to the reviewed commit.

| ID | Severity / confidence | Status | Stage affected |
| --- | --- | --- | --- |
| IR-01 | High / high | Supported concern | Blocker before any body connection |
| IR-02 | Medium / high on paths, moderate on behavior | Supported concern | Controlled first power-up; robust acquisition |
| IR-03 | Medium / high on requirements, moderate on actual startup | Measurement required | Reference/startup qualification |
| IR-04 | Medium / high on mechanism, moderate on magnitude | Supported concern | External EEG-quality acquisition |
| IR-05 | Medium / high on missing evidence | Measurement required | Enabling closed-loop bias |
| IR-06 | Medium / high | Supported concern | Before bulk socket/PCB purchase |
| IR-07 | Medium / high | Supported concern | Before fabrication release |
| IR-08 | High for acquisition completion / high | Confirmed defect: missing implementation | Before claiming a working instrument |
| IR-09 | Low / moderate | Optional improvement | Prototype edge/noise qualification; possible later layout revision |
| IR-10 | Low / high | Confirmed defect | Before using documentation to order/assemble |

### IR-01 — Body-current protection is not established across the whole system

**Location:** `inputs.kicad_sch` J1–J9, R1–R18, D1–D9; `power.kicad_sch` J10, R21/R22, U2/U3; J11 GND; external Nano USB/charger/instrument connections.

**Evidence:** Each recording/reference contact has 20kΩ total series resistance; only the bias contact has 998kΩ. The Nano and AFE share GND. TXU0304 supply-disconnect behavior is not galvanic isolation [D3,D6]. A 5.1V source across one minimum-tolerance 19.8kΩ input path permits approximately **258µA**, whereas the bias path alone permits about **5.16µA**. These are conditional circuit bounds, **not permissible human-current limits**. The [fault-path table](ENGINEERING.md#fault-path-analysis) specifies sources and returns, including why multiplying by nine is not always valid.

**Failure scenario/consequence:** A clamp or regulator fault, or a cable to grounded external equipment, can create a return path not limited by the two bias resistors. An onboard fuse reacts to wiring-scale current and cannot be credited as microampere electrode protection. An uninsulated assembly also allows faults outside the intended resistor paths.

**Smallest reasonable correction:** Keep this prototype electrode-disconnected from people. Before body use, define the complete enclosed power/communication arrangement and have a qualified reviewer close normal and single-fault currents through **every** contact, insulation, accessible conductors and external equipment paths. A self-contained battery/wireless arrangement removes some external paths but does not itself close the analysis. Any wired/body-use proposal requires a separately justified isolation/protection design; do not select an expensive isolator without that system analysis.

**Closure evidence:** A reviewed system schematic, physical enclosure/harness, fault matrix and suitably conducted leakage/fault measurements, plus verified removal or qualified isolation of USB/charging/instrument paths. This desktop report cannot supply certification or approval.

### IR-02 — Analog injection and partial-power behavior remain outside the digital buffer guarantee

**Location:** D1–D9 clamp rails; U2/U3 IN/OUT/EN; D10/SW1/VBAT; U4/U5 VCCA/VCCB/OE; J11/J12; `docs/POWER_HARNESS_A0_3.md`.

**Evidence:** BAV199 is correctly oriented, but its forward drop is not a guaranteed ±0.3V clamp. ADS1299 internal clamps may conduct first [D1 p7; D4 p3]. An externally driven contact can energize `AVDD_5V` through D1–D9 or the ADC while the AFE is off. TPS7A24 does not internally limit extended reverse current [D2 §8.1.4]. **D10 already provides useful input-series isolation of an upstream collapse**, corresponding to one TI mitigation; absence of a separate output-to-input diode is not automatically a design defect. Local input faults and external output injection still need testing.

TXU sees HOST_3V3 and DVDD, not AVDD. With AVDD absent but DVDD=3.3V, the ADS supply relationship is outside its recommended range. TXU also does not promise normal operation through every voltage between its supply-off threshold and valid supply range. Low-pack Nano VIN margin is only about 0.3V under the assumed harness drops.

**Failure scenario/consequence:** External stimulus with power off causes phantom powering; battery droop or a host reset causes invalid frames; radio current contaminates the common ground; adverse reverse current damages a regulator. None of these outcomes has been observed on hardware.

**Smallest reasonable correction:** Use the documented current-limited, no-person fixture and controlled sequence for the first prototype. Measure the state matrix in ENGINEERING.md. Add an analog-rail/undervoltage monitor or reverse-current mitigation only if the measured behavior or intended unattended use requires it. Do not “fix” the return problem by casually removing signal ground.

**Closure evidence:** Rail, input-pin and supply-current waveforms for host-only, AFE-only, both orders, reset, disconnected supplies, slow discharge, analog-only dropout, startup and shutdown; current-limited external-input injection with safe device stress; no unintended valid-data indication. Verify actual pack/fuse/wire drops and Nano burst behavior at the low endpoint.

### IR-03 — Effective reference capacitance and VCAP1 startup are plausible, not verified

**Location:** U1.24/.28, C29/C42/C30 and polarized C24; U2/U3 output capacitors C21/C23; `firmware/README.md` startup contract.

**Evidence:** Two 22µF/25V/1210 reference capacitors provide substantial improvement over relying on one nominal value. Their manufacturer curve supports the direction of the change, but is typical simulation data [D8]. A compounded engineering estimate gives approximately 20.45µF combined, not a guaranteed lower limit; D1 specifies at least 10µF on VREFP. VCAP1 correctly has 100µF. Fig25's 9.8kΩ and nominal capacitance give a **0.98s illustrative time constant** and roughly **2.44s to 1.1V** if the final source is 1.2V and leakage is ignored. This is not a guaranteed timing model. The 128ms digital power-on interval alone does not prove VCAP1 ready.

C24's rated-condition leakage is 6.3µA [D10]; multiplying it by 9.8kΩ gives 61.7mV sensitivity. That is **not** the actual leakage at its roughly 1.2V operating point, and is not grounds to declare the tantalum part wrong. LDO total directly connected capacitance is below its 50µF effective upper recommendation [D2]; reference/VCAP capacitances are not simply counted as LDO output capacitors.

**Failure scenario/consequence:** Fixed-delay startup intermittently reads wrong scale or unsettled data; unexpectedly low effective capacitance or contamination adds reference noise.

**Smallest reasonable correction:** Retain the present parts for a controlled prototype, measure startup with a high-impedance probe and qualify exact fitted capacitors. Do not shrink the reference capacitors or hardcode 128ms as complete readiness. Establish a measured, margin-bearing delay/monitoring strategy and discard startup data.

**Closure evidence:** Cold/hot and repeated start/stop traces of VCAP1, VREFP, AVDD/DVDD; VCAP1 above 1.1V before the specified reset/configuration sequence; settled reference and gain; no oscillation; adequate effective capacitance at operating voltage, temperature, tolerance and age.

### IR-04 — Shared-reference loading and impedance mismatch can dominate system CMRR

**Location:** J1–J9, R1–R18, C1–C9, D1–D9; U1.1/.3/.5/.7/.9/.11/.13/.15; `REF_FILTERED` trunk on B.Cu.

**Evidence:** One shared 20kΩ/1nF network drives eight negative inputs; each positive network drives one. At 50Hz, opposing 1% resistor / 5% capacitor tolerances alone give about **62.5dB** common-mode rejection in the simplified two-RC calculation. Adding illustrative 20pF/input loading gives about **55.7dB** in that particular worst-direction case: 100mV common-mode could become approximately **164µV differential**. The ADS input capacitance specification is not a complete common-mode/cable model, so these are sensitivities, not predictions. See [calculation details](ENGINEERING.md#input-quality-and-headroom).

The existing 7.96kHz pole is an RF input filter, not a 50Hz notch or the complete EEG bandwidth filter. There is no evidence that joining the negative inputs is inherently wrong or that eight separate reference contacts are required.

**Failure scenario/consequence:** Balanced bench injection works but real electrode impedance mismatch creates mains pickup or clipping. Digital subtraction/notching may conceal interference without recovering clipped information.

**Smallest reasonable correction:** Measure with the existing circuit first. If needed, select better-matched C0G parts, improve electrode/reference contact impedance and cable symmetry, and tune filtering from measured loading. A new reference buffer adds noise, stability and fault paths and is not the first justified purchase.

**Closure evidence:** Raw 50/60Hz common-mode tests with equal, +5kΩ and +50kΩ source impedances and 0.5/1/5nF added cable loads; bias off/on separately; no notch hiding the result. Aim initially for the repository's **60dB balanced-fixture development goal** and document degradation in unequal cases. Characterize all channels, reference disconnection and clipping.

### IR-05 — Bias compensation cannot be approved from its RC corner alone

**Location:** U1.60–.63, R20=1MΩ, C10=1.5nF, R21/R22=499kΩ, J10; BIAS_SENSP/N firmware settings.

**Evidence:** Feedback polarity is correct and the nominal R20/C10 corner is 106Hz. That is not closed-loop bandwidth or phase margin. The 998kΩ output path plus 0.5/1/5nF load has simple RC corners near 319/159/31.9Hz, illustrating significant load dependence. D1 itself has a **220kΩ diagram versus 330kΩ application-text discrepancy** for the internal bias summing network; this report brackets the calculation rather than asserting a precise loop gain. Selecting both P and N for eight channels can intentionally average channel common mode; repeating a shared N node eight times is not by itself a wiring error.

**Failure scenario/consequence:** A high-capacitance cable or disconnected reference causes oscillation, slow recovery or bias saturation, corrupting every channel.

**Smallest reasonable correction:** Leave bias disabled for initial internal-test and externally biased dummy-input tests. Define the actual sense mask and load network before enabling it. Change compensation only after measured behavior or a credible model supports a change.

**Closure evidence:** For each intended mask, record BIASOUT and input common mode across load extremes, contact disconnect/reconnect, overload and recovery. Demonstrate bounded settling without sustained oscillation or prolonged clipping. If a simulation is used, identify its model and validate it against the prototype. No such simulation was run here.

### IR-06 — Socket mating and physical tolerance qualification remain open

**Location:** `Neuronic.pretty/P1_36619_Touchproof_RA.kicad_mod`, J1–J10; J11/SW1 header footprints, J12 JST header; actual Sino-k leads.

**Evidence:** The actual footprint has a 2.10mm signal hole and two **4.20×2.10mm plated oval slots**. The P1 drawing's inch-primary maximum signal pin diameter is 1.778mm. With an assumed 2.00mm minimum finished hole, radial clearance is about 0.111mm; the dummy-slot tolerance calculation also shows conditional room. This disproves the simple claim that the present holes are necessarily undersized. Physical cable mating is still **UNVERIFIED**: the specific Sino-k listing does not establish it [D5,V1].

Socket noses overhang the board edge by about 0.5mm; row pitch is 8.2mm and nominal courtyards are only 0.1mm apart. Extraction force is specified at 2–7lb (about 9–31N), so the enclosure must support removal loads. J11/SW1 use 1.00mm holes while the exact Würth drawing recommends 1.10±0.15mm; a negative fabrication tolerance can fall below the recommended lower bound. J12 also uses 1.00mm holes against the JST two-circuit reference pattern of 1.00±0.05mm; include it in finished-hole qualification. These are tolerance concerns, not proof that ordinary samples cannot fit.

**Failure scenario/consequence:** Ten costly sockets do not mate, a tolerance-corner header does not insert, or repeated unplugging cracks a joint/board.

**Smallest reasonable correction:** Buy/borrow **one** exact socket and the actual headers, verify mating and fit, then use a coupon or fabricator-confirmed finished holes/slots. Qualify an alternative compatible header or adopt the vendor land pattern in a separately reviewed future source change if required. Provide mechanical support and accessible solder joints.

**Closure evidence:** Identified sample MPNs, measured pins/plug, successful mating/continuity, fit on the chosen fabrication process, photos/dimensions and supported extraction test. Manufacturer confirmation of the exact cable/connector combination can supplement, but not replace, assembly-fit evidence.

### IR-07 — Generic DRC has not become a fabricator-approved release

**Location:** `neuronic.kicad_pro`, PCB stack/layers/outline, plated slots and masks; manufacturing outputs/workflow.

**Evidence:** Saved board is 88×90mm, four copper layers, nominal 1.6mm. Actual minimum track is 0.15mm, vias 0.60/0.30mm, configured clearance 0.20mm. These are not inherently exotic against the named JLCPCB capability comparison [F1]. Native drill output contains all 20 plated slots. But no exact stack-up/copper-weight selection, final CAM acceptance, assembly enclosure approval or manufacturing job exists. Zero global mask expansion and ignored footprint-related categories are settings to review, not evidence of guaranteed solder-mask quality. Strict-category results are disclosed above.

**Failure scenario/consequence:** A shop misinterprets plated slots, modifies a fine-pitch mask web, or delivers a stack/mechanical result incompatible with the intended assembly.

**Smallest reasonable correction:** Prepare a revision-locked release in a subsequent task, with named stack-up, thickness/copper/finish, Gerbers, PTH/NPTH drills and explicit slot/mechanical notes. Obtain the fabricator's interpretation and inspect its preview. Standard economical four-layer fabrication is plausible; impedance-controlled premium fabrication is not automatically necessary for this short, initially 1MHz interface.

**Closure evidence:** Archived release hashes, actual job settings, CAM acceptance and slot/mask/outline confirmation. Confirm final board-to-enclosure dimensions and connector/hole tolerances. This review's drill files are not the release.

### IR-08 — The acquisition/recording implementation is absent

**Location:** `firmware/README.md`, `software/README.md`, `hardware/interface.json` and the external Nano harness.

**Evidence:** These are implementation contracts, not executable acquisition firmware or a recorder. The stated native GPIO mapping and initial register values are consistent with the saved wiring and manufacturer tables; see ENGINEERING.md. At 1MHz, a 27-byte frame takes 216µs against a nominal 4ms sample period, so raw bandwidth is plausible. This does not establish ISR timing, channel order, loss handling or signed-code conversion.

**Failure scenario/consequence:** A program appears to plot data while frames are lost, offset/gain is wrong or stale records survive a brownout. A functioning internal test can coexist with dead external inputs.

**Smallest reasonable correction:** Implement the existing first milestone with pinned tools, explicit wake/configure, register readback, raw frame capture, timestamp/session/loss accounting and a PC recorder. Start with internal test, then internal short, then independently injected external signals. No ML or GUI is needed to close this milestone.

**Closure evidence:** Reproducible build and firmware SHA; validated register dumps and signed boundaries; correct eight-channel internal-test frequency/amplitude; ten-minute loss-accounted raw recording; external path tests on every contact; explicit refusal/flagging of invalid power/clip states. This is a known completion gap, not a newly discovered hidden firmware bug, and does not forbid ordering a bench prototype.

### IR-09 — Residual routing opportunities need measurement, not a speculative wholesale reroute

**Location:** U4.13→R41 (SCLK), U5.12→R45 (START); B.Cu digital routes above In2.Cu gaps; C24/C28 ground returns; reference trunk around x=96.8mm under U1's input side.

**Evidence:** Source-to-series-resistor centerline lengths are **11.26mm for SCLK** and **22.03mm for START**; return-output resistors R47/R48 are 2.925mm from their buffer sources. Selected B.Cu DRDY/MOSI segments cross In2 fill gaps near (108.31,89.50), (110.57,90.67) and (111.22,86.50)mm, while In1 remains filled there. C24/C28 ground-via-to-selected-ADC-ground-via separations are about 11.15/9.86mm. These are real geometric opportunities, not proof of ringing or excessive noise. Native DRC still passes; In1 has no routed signal cuts.

**Failure scenario/consequence:** Fast edges cause overshoot/false clocks, or high-frequency return currents couple into sensitive circuitry despite a low SPI repetition rate.

**Smallest reasonable correction:** Scope receiver and source edges with appropriate probing. If a later board revision is warranted, place damping electrically next to the driver, reduce avoidable local return loops, and preserve adjacent ground under digital paths. Do not spend on a respin just to shorten a line in a screenshot.

**Closure evidence:** Receiver-level timing/overshoot within device limits, stable frame capture and radio-on/off noise comparison. A demonstrably clean prototype can close this concern without any routing change.

### IR-10 — BOM README contradicts the current CAD

**Location:** `hardware/bom/README.md`, opening component-count paragraph and J1–J10 paragraph.

**Evidence:** README says 91/22 and bench headers; fresh CAD/BOM audit finds 107/25 and P1 sockets. The actual candidate tables and saved PCB agree with each other.

**Failure scenario/consequence:** Ordering from the prose omits components or substitutes nonmating headers; the budget omits socket cost.

**Smallest reasonable correction:** In a separate authorized source/documentation change, update counts and connector description, preserve candidate-not-release status, and link physical-fit gates. This review intentionally does not edit the existing file.

**Closure evidence:** Prose agrees with the revision-locked BOM and CAD and distinguishes owned Nano/leads, PCB parts, offboard harness, fabrication and enclosure.

## Reconciliation with previous reviews

Earlier reports were consulted after the initial pass. “Fixed” below means demonstrated in current CAD or tests, not proven in a manufactured instrument.

| Prior concern | Independent disposition at reviewed SHA |
| --- | --- |
| A0.2 IR-01: local VREF/VCAP and AVDD1 routing | **Substantially fixed in saved copper.** Measured VREFP→C29 is 2.851mm; VCAP routes are local; AVDD1 branches separately from C37 into C36/U1.54. Do not repeat the obsolete long-loop description as a current defect. Residual ground-return/edge concerns are IR-09. |
| A0.2 IR-02: socket hole/slot fit | **CAD enlargement is real; qualification remains open.** Present geometry is conditionally compatible with the tolerance calculation. Calling current holes definitively too small would overstate the evidence. IR-06 remains. |
| A0.2 IR-03: capacitance budget | **Real improvement:** two 22µF reference parts and 4.7µF LDO outputs. Typical curves are not guaranteed operating values. IR-03 remains measurement work. |
| A0.2 IR-04: weak control pull-downs | **Fixed:** R30–R35 are 10kΩ. Even a conservative 12µA combined leakage assumption gives about 0.121V, below the ADS low threshold at the considered DVDD minimum. Physical transient behavior still belongs to IR-02. |
| A0.2 IR-05: direct host GPIO / power-order exposure | **Digital path improved materially:** actual TXU0304 devices, distinct supplies, OE pull-down and damping are present. Power-off buffering is not safety isolation and does not solve analog AVDD injection or every brownout. |
| A0.2 IR-06: input/reference loading | **Still open.** Independent RC/noise calculations support investigation, not a guaranteed failure claim. Shared N fanout itself is valid. |
| A0.2 IR-07: clamp/bias/body faults | **Still open for body use.** BAV199 is correctly oriented. A silicon diode's forward drop alone is insufficient to predict ADS destruction; its internal current-limited clamp specification matters. Aggregate body-current bounds must specify actual source and return. |
| A0.2 IR-08: firmware/recorder | **Still absent**, explicitly documented. Contract is more concrete and register intent checks out. |
| A0.2 IR-09: validation/generator/router safety | **Several real fixes:** hashes/manifests, destructive-generation refusal, failed-export cleanup and failed-import source preservation; nine tests pass. Shared-model validation is still not independent circuit verification. Router-success execution, hardware behavior and all test combinations are not covered by those nine tests. |
| A0.3 follow-up routing review | Independently reproduced its important local route measurements; no basis found to overturn its narrow “no new blocking copper defect” conclusion. That conclusion was not equivalent to release/body approval. |
| Additional emphasis from this review | Stale BOM README confirmed; exact header-hole tolerance concern; single-electrode offset headroom differs from the simple ±VREF/gain claim; explicit power-state/fault-path tables and internal bias-resistor source discrepancy. These are refinements, not evidence that every previous conclusion was wrong. |

Current status documents already say manufacturing/body readiness is false and physical tests are pending. I did **not** find a current repository-wide claim that DRC proves human safety. Historical input hashes match; “stale report” is not an appropriate accusation here.

## Ordered correction and verification plan

1. **Before a full purchase:** close IR-06 with one socket/actual lead and header samples; decide mechanical support. Correct the stale BOM prose in a separate change. Keep one ADS1299 and the owned Nano; do not purchase a second ADC/controller merely because there are eight channels.
2. **Before ordering boards:** choose an economical four-layer process and complete IR-07's release/CAM confirmation, especially finished slots/holes and fine-pitch mask. A small prototype or connector coupon can be a deliberate controlled experiment; it is not a production release.
3. **Before first power:** assemble and inspect under magnification; verify IC orientation, D10 cathode, C24 polarity, harness pinout, rail shorts and fuse/diode continuity. Use a current-limited supply with no person connected. Do not reuse the A0.2 J11 cable: pins 11/12 changed.
4. **Power/reference qualification:** execute IR-02/03 and the supply matrix; establish actual operating limits and startup timing. Stop on unexpected current, heat, invalid rails or phantom power.
5. **Firmware milestone:** implement IR-08, prove internal test/short acquisition and raw PC recording; then inject external differential signals at valid common mode on every channel.
6. **Analog qualification:** measure IR-04, offset headroom, leakage/noise and radio sensitivity. Review the bias mask/fixture and then close IR-05. Use IR-09 measurements to decide whether any layout revision has enough benefit to justify cost.
7. **Only afterwards consider body readiness:** close IR-01 with qualified system-level review and physical evidence. A pass in steps 1–6 is not a substitute.

The concrete bench sequence, proposed acceptance targets and record format are in [VERIFICATION_PLAN.md](VERIFICATION_PLAN.md).

## Separate readiness conclusions

| Intended milestone | Conclusion |
| --- | --- |
| **Bench fabrication** | **Conditional candidate.** No confirmed fatal circuit/copper defect identified. Close connector/finished-hole/slot and fabricator-release questions before a bulk order. Prototype-only noise/stability measurements are not prerequisites to making the prototype needed to perform them. |
| **Expected acquisition functionality** | **Plausible but unproven and incomplete.** The ADS supplies/pinout, polarity, internal reference/clock, buffered GPIO mapping and initial register contract are coherent. Firmware/recorder, assembly, power/reference behavior, real CMRR and bias behavior remain unverified. No EEG recording exists. |
| **Body-connected readiness** | **No.** Whole-system fault-current, external-connection, insulation and physical safety evidence is missing. Neither this review nor passing ERC/DRC establishes medical-standard compliance or human safety. |

No component order, hardware modification, manufacture, simulation, bench measurement or body connection was performed during this review.
