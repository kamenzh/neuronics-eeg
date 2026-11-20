# Remaining hardware and system work — A0.3

Updated 2026-11-19. IR numbers below refer specifically to the
[November 17 review of 577aad8](reviews/independent-577aad8-2026-11-17/REPORT.md),
not the older A0.2/A0.3 reports which reuse similar identifiers.

| ID | Review mapping | Current state | Closure evidence / next action |
| --- | --- | --- | --- |
| HW-01 | IR-06 | Exact P1 socket selected; fresh drawing/CAD audit done, physical fit open | Actual Sino-k identity/mating and three-tail seating; resolve J11/SW1 hole decision, J12 unilateral tolerance, enclosure support; later process acceptance |
| HW-02 | IR-02 | Bounded DC clamp calculation; analog behavior not qualified | Powered/unpowered injection and partial-power analysis/tests; transient/leakage and clamp/regulator stress review |
| HW-03 | IR-01 | Whole-system electrode protection unresolved | Qualified design-stage normal/fault current analysis, including aggregate paths and external connections; implement necessary changes, then measure assembled system |
| HW-04 | IR-05 | Bias candidate; initial tests keep it disabled | Cable/electrode model, compensation assessment, stability and recovery measurements before enabling closed loop |
| HW-05 | IR-03 | Reference/VCAP routing and capacitance improved; typical-capacitance estimate only | Effective-capacitance and startup review; measured VCAP1/reference readiness, noise, temperature and supply limits |
| HW-06 | IR-02, IR-01 | Power-off tolerant GPIO buffers and candidate harness | Final battery/switch/harness architecture; brownout/power-order/inrush/fuse/drop measurements; no claim of galvanic isolation |
| HW-07 | IR-04, IR-09 | No confirmed fatal copper defect; shared-reference CMRR concern remains | Review impedance loading and acceptance limits; measure CMRR/noise/radio and digital edges; use evidence to decide optional routing changes |
| HW-08 | IR-07 | Default full DRC passed; strict-category check found 13 footprint-filter warnings | Resolve/classify symbol-to-footprint metadata; later process/stack-up and export inspection. No current order release |
| HW-09 | Review verification scope | Nine workflow tests passed in independent review; prior 46 source hashes still match | Existing checks prove their limited contracts only; rerun relevant checks after source changes; physical behavior is not covered |
| HW-10 | IR-10 | **Documentation defect closed:** 107 components, 25 groups, 23 unique MPNs, ten P1 sockets | Procurement remains separate: stock/source and off-board parts/quote deferred until design confirmation |
| HW-11 | IR-08 | Firmware and PC acquisition/recorder absent | Implement/build, then demonstrate eight-channel acquisition and raw timestamp/loss-accounted recording on real hardware |
| HW-12 | IR-01 plus assembled-system validation | No person-use approval | Qualified review of complete assembled system and physical normal/fault evidence before any body connection |

All ten review findings are accounted for. Only IR-10's stale prose is closed
by this documentation change. IR-06's desk review is partial evidence, not a
physical pass. IR-09 is optional optimization, not a proven need to reroute.

The 13 strict-category warnings concern footprint filters for J1–J10, J11,
J12 and F1. They are not 13 copper shorts or unconnected nets. They remain
visible in the [original strict DRC evidence](reviews/independent-577aad8-2026-11-17/evidence/strict-category-drc.txt);
no rules were weakened or source metadata changed in this follow-up.

The [connector audit](CONNECTOR_VERIFICATION_A0_3.md) corrects the historical
review's J12 tolerance transcription: the drawing says 1.00 +0.05/−0, not ±0.05.
See the [next steps](NEXT_STEPS.md) and [working-system gates](SYSTEM_ACCEPTANCE_PLAN.md)
for the distinction between design confirmation, build release and demonstrated
body-use readiness. A working EEG system remains the goal; the current untested
board must not be connected to a person.
