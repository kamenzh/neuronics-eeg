# A0.2 protection and power review

This is a routed **bench-development** revision. The review is a bounded DC
calculation and layout assessment, not certification, transient simulation or a
measured safety result. No person may be connected to this revision.

## Socket selection

Use ten black **P1 Technologies 8R003661901F**, family **36619**, right-angle PCB
1.5 mm touchproof jacks. The manufacturer identifies DIN 42-802 Type BU. The
recessed board contact is male; the mating electrode cable contact is female.
The user's DIN 42802 identification is an assumption until the actual cable
mates with a sample. Do not substitute an ordinary exposed 1.5 mm pin or a
2 mm socket.

Sources: [manufacturer selection](https://catalog.p1tec.com/?FILTER_CLEAR=&FILTER_FCOMPONENT=36619),
[drawing 36619-50 revision H](https://catalog.p1tec.com/dash50/36619_dash50.pdf).
The catalog's BLACK link identifies the ordering MPN. No live price/stock quote
or purchased sample is implied.

The original footprint is in `hardware/footprints/`; its bundled copy is in
`hardware/kicad/Neuronic.pretty/`. It is derived from the drawing's primary inch
dimensions, not a supplied manufacturer land pattern:

| Feature | Footprint decision |
| --- | --- |
| Signal contact | Pad 1 at origin, 1.90 mm finished drill, 2.90 mm copper |
| Two dummy anchoring legs | Unnumbered isolated plated holes; 1.80 mm drill / 2.80 mm copper |
| Leg centers | -10.16 mm along mating axis, +/-2.54 mm across it |
| Mating direction | Left, toward -X; front at -17.526 mm from signal pin |
| Socket pitch | 8.20 mm; 8.10 mm courtyard includes dummy copper pads (about 0.1 mm margin) |
| Board | 88 x 90 mm; socket noses overhang left edge by 0.50 mm |

The drills are nominal assembly candidates, not a manufacturer-approved land pattern. The complete positional tolerance stack still requires manufacturer confirmation and a physical sample/hole-fit coupon. Confirm the signal contact, electrically isolated dummy
legs, insertion clearance, housing dimensions and enclosure restraint. The
drawing advises against wave soldering; use a controlled hand-solder process.
Connector component ratings do not establish the finished device's protection.
Top-to-bottom order is CH8, CH7, ... CH1, REF, BIAS; silk labels identify functions.

## Changes made to power

U2/U3 are now **TPS7A2450DBVR / TPS7A2433DBVR**, fixed 5 V / 3.3 V, SOT-23-5.
The old MCP1703A choice had separate full-temperature, load and line errors that
were not fully represented by the previous 2% calculation. The new schematic
uses an explicit TI pin contract: 1 IN, 2 GND, 3 EN tied to IN, 4 NC tied to GND
as allowed by TI, 5 OUT. This is a footprint and wiring change, not a drop-in
substitution on an A0.1 board.

[TI TPS7A24 datasheet, sections 5, 6 and 8](https://www.ti.com/lit/ds/symlink/tps7a24.pdf)
is the component reference. A conservative additive error budget is 2%:
1.25% initial/temperature, 0.25% line and 0.5% load. This gives 4.90–5.10 V and
3.234–3.366 V, within the ADS1299 recommended rail ranges. The 6-AA pack range
7.2–10.2 V is an operating assumption. At 40 mA, allowing 0.6 V fuse loss,
0.5 V diode loss and 0.1 V harness/switch loss leaves 6.0 V at the regulators,
above the 5.5 V input boundary used for analog regulator accuracy specifications.

Analog/digital budgets are 30/10 mA. Worst input-to-output dissipation before
input drops is approximately 159/70 mW. The TI thermal-board model suggests
27/12 C junction rise; our copper/enclosure must be measured. This PCB must not
power the Nano radio from either regulator. F1 protects the AFE battery branch;
it is not electrode protection or the controller branch fuse.

Direct AVDD capacitance is 17.1 uF nominal, 21.63 uF with the documented positive
tolerance/temperature allowances. This is below the new regulator's 50 uF
recommended effective upper bound. Minimum effective capacitance remains to be
confirmed, particularly C29 at 4.5 V and input ceramics at battery voltage.
Check startup, overshoot, load steps, noise, temperature and rail discharge on
hardware. The new LDO is not a guarantee of microvolt acquisition performance.

## Input and bias protection findings

[TI ADS1299 datasheet, section 7.1 and its clamp-current footnote](https://www.ti.com/lit/ds/symlink/ads1299.pdf)
distinguishes absolute voltage limits from current-limited excursions. The
BAV199 forward drop is not guaranteed below the ADC's internal clamp threshold;
the internal clamps may conduct first. The two 10 kohm resistors provide the
bounded current limit, not proof that BAV199 alone protects the converter.

`tools/review_electrical.py` writes the reproducible calculation and assumptions:

| Hypothetical DC condition | Bound with -1% resistor tolerance |
| --- | --- |
| 10.2 V across a 20 kohm input path | 0.515 mA |
| Same voltage, one 10 kohm resistor shorted | 1.030 mA; remaining resistor 10.51 mW |
| Internal 5.1 V rail-to-contact fault through 20 kohm | 258 uA |
| Same internal fault with one resistor shorted | 515 uA |
| 5.1 V through both 499 kohm bias resistors | 5.16 uA |
| Same bias fault with one resistor shorted | 10.32 uA |

These are circuit-path bounds, **not acceptable patient-current limits**. A
bounded low-energy DC input fault can be below TI's injection limit while the
system is still unsuitable for a person. Open resistors lose signals; a shorted
input resistor removes half the limiting resistance; a shorted clamp can drive
a contact from a rail through the remaining resistance. Common supply failures
and multiple simultaneous contacts need aggregate analysis.

The unpowered case is unresolved: input or GPIO injection can raise an unpowered
rail; neither ordinary regulator operation nor the fuse guarantees that rail
can absorb it. The TPS7A24 output-to-input absolute limit also matters during
backfeeding. Do not drive external signals while the board is off; de-energize
both ends before changing bench wiring. This operational rule is not a hardware
interlock or a final wearable solution. A final revision may need additional
current limiting, isolation/interlocking or a revised supply/protection design.

This review does not qualify mains faults, defibrillation, ESD pulses, leakage
across contaminated surfaces or an assembled enclosure. Keep USB, chargers and
mains-connected instruments out of any future approved body-connected setup.
The bias 1 Mohm || 1.5 nF feedback is still a candidate; cable/electrode load,
phase margin and recovery must be tested with a simulator before body use.

## Release disposition

Routing is allowed for a clearly identified bench-development checkpoint.
Manufacturing release remains false pending connector/sample and capacitor
verification, detailed layout review, a defined fabricator stack-up, the
external power harness and an intentional bench-only fabrication package.
Body use has a separate unresolved protection review and measured test gate.
