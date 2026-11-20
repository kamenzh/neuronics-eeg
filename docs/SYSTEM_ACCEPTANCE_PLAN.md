# Target: a working eight-channel EEG system

Updated 2026-11-19 to reflect Kamen's requested outcome. The goal is one useful,
self-assembled EEG instrument using the full ADS1299 and the owned Waveshare
ESP32-S3-Nano, with wireless recording on a PC. Eight recording contacts share
one reference; the tenth contact is bias. This does not require a second ADC.

“Bench development” describes the present evidence status and the initial
verification phase. It does not redefine the final goal as a board that can
never record a person. Conversely, changing that label cannot establish human
safety, signal quality or firmware functionality. There is no assembled/tested
board yet, and a first fabrication may still need a correction or another spin.

## Gate A — confirm the design before fabrication work

Kamen has deferred fabrication files, manufacturer choice and ordering until
this design gate is reviewed. This is approval to build the proposed design,
not a claim that an unbuilt system already works.

| Requirement | Evidence needed before design confirmation | Current state |
| --- | --- | --- |
| Electrode interface | Exact lead identity and mating geometry; sample evidence where available; documented unresolved physical checks | Desk audit complete; actual fit open |
| Mechanical design | Connector hole/slot decision, jack support, enclosure clearance, cable retention and battery access | Open; see connector audit |
| Whole-system body protection | Qualified electronics/safety review of circuit plus Nano, battery, switches, all contacts, cables and enclosure; define normal and fault paths, aggregate current limits and tests | Open; input resistors and digital buffers are not a complete safety case |
| External connections | Explicit operating/service states for battery, USB, charger and instruments; prevent unintended external conductive paths during eventual recording | Candidate battery/wireless arrangement only; common-ground buffers provide no galvanic isolation |
| Power and analog behavior | Review startup/partial-power paths, clamp stress, effective reference capacitance, bias compensation, shared-reference impedance and offset headroom; decide any circuit changes and measurable acceptance criteria | Remaining IR-02 through IR-05 work |
| Acquisition interface | Pin/register/startup specification consistent with CAD; define all eight channels, rate, raw units, timestamps, dropped-sample accounting and safe defaults | Contract exists; implementation missing |
| Independent design review | Review any resulting CAD changes, rerun ERC/DRC and contract checks, classify footprint-filter warnings, record limitations and open physical tests | November 17 review integrated; no new CAD revision in this follow-up |

Do not defer all body-protection engineering until after building: architecture
changes can affect PCB layout, enclosure and the budget. A qualified reviewer
must establish the applicable safety requirements and evidence for the intended
system. Conversely, noise, startup and fault measurements need physical hardware;
those belong after assembly. A paper review alone cannot close them.

The connector audit records a preferred J11/SW1 hole update for evaluation.
The shared-reference concern is a test/design question, not a mandate to add
an unreviewed buffer. Bias RC corner is not a stability proof. Do not reroute the
whole board solely because optional improvements were mentioned.

## Gate B — later build release

Only after design confirmation: agree a suitable fabrication process, check
finished holes/slots and stack-up, generate and independently inspect Gerber/drill
and assembly files, freeze exact BOM and harness parts, and obtain an affordable
quote. Manufacturing exports and orders are deliberately outside this change.
Any material supplier-driven design change returns to Gate A.

## Gate C — demonstrate a working instrument on the bench

Implement and build the firmware and PC recorder, then assemble and test the
complete system without a person attached. Use the detailed
[independent verification plan](reviews/independent-577aad8-2026-11-17/VERIFICATION_PLAN.md)
and [existing bench plan](BENCH_TEST_PLAN.md) as the starting protocols.

Required evidence includes inspected assembly; correct rails/polarity/current;
reference and VCAP startup; power-order and brownout behavior; all eight channels
in internal-test and shorted-input modes; calibrated differential input at valid
common mode; raw sample/timestamp/loss logs; measured noise, bandwidth, gain and
offset headroom; reference/common-mode rejection with realistic impedances;
bias stability and recovery; thermal behavior and radio interference. Record
board/firmware revisions, fixture, instruments, conditions and pass limits.
Acceptance limits must be settled before calling a measurement a pass, not
selected afterwards to fit its result. Unperformed tests stay marked pending.

## Gate D — establish readiness for person-connected EEG

A qualified reviewer must assess the assembled complete system and the physical
normal/fault evidence against the agreed requirements. Include all electrode
paths, aggregate currents, enclosure, battery/harness and every possible external
connection. Passing bench acquisition, having touchproof connectors or using
batteries alone does not close this gate. No human connection is authorized by
this document, the independent AI review, or a clean ERC/DRC result.

Once the complete system has been accepted for that use, demonstrate repeatable
EEG recordings with artifact checks. Robotic-arm control is a subsequent software
and robotics goal; this board does not guarantee reliable thought decoding.

## Progress now

Review documentation is incorporated and the stale BOM prose is corrected.
Connector geometry has fresh read-only evidence, with physical checks explicitly
open. Hardware source/copper is unchanged. Firmware, recorder, assembled-system
measurements and person-use acceptance are still outstanding.
