# Next steps toward a working EEG board

The goal is a usable eight-channel EEG system with the owned Waveshare
ESP32-S3-Nano and self-assembly. A0.3 has real schematics, component placement and
copper routing; it has not been manufactured or demonstrated to work.

Kamen's current scope is review integration and connector verification.
Fabrication files, manufacturer choice and parts ordering wait until design
confirmation. No new purchase is needed to review the evidence already available.

| Step | Work and owner | Status / completion evidence |
| --- | --- | --- |
| 1 | Incorporate the independent report and correct documentation — Codex | Complete in this follow-up: original report/evidence retained, BOM counts and socket description corrected, findings mapped into the blocker register |
| 2 | Verify connectors — Codex for drawings/CAD, Kamen for actual parts | Desk audit complete. Exact Sino-k plug identity/mating, physical seating and enclosure support remain open; J11/SW1 hole decision and J12 finished minimum need resolution |
| 3 | Close design-stage decisions for the intended working system — Codex plus qualified electronics/safety reviewer | Whole-system protection and external connections must be reviewed before design confirmation; resolve any necessary circuit/mechanical changes and define measurable acceptance limits |
| 4 | Implement acquisition and recorder — Codex, as a separate work item | Missing. Build/register/protocol checks first; prove all eight channels and raw recording on assembled hardware later |
| 5 | Confirm the proposed design — Kamen with documented engineering review | Record exact revision, intended use, remaining post-assembly tests and any limitations; this is not physical validation |
| 6 | Prepare manufacturing files, select process and price parts — later | Deferred by Kamen. Inspect exports, confirm tolerances, freeze BOM/harness and quote before an order |
| 7 | Assemble and verify without a person — Kamen with suitable assistance/equipment | Inspect, check power/startup, test acquisition, noise/CMRR/bias, radio and fault behavior; correct failures and revise if necessary |
| 8 | Qualify the complete system for body connection — qualified reviewer | Physical safety evidence and final assembly/harness/enclosure review required before EEG on a person |
| 9 | Record repeatable EEG, then evaluate control models — Kamen + Codex | Requires a working, accepted instrument; robotic-arm control is a later project stage |

The immediate missing evidence from Kamen is a clear front/side photo of the
actual electrode plug, with scale, plus its model/package marking. If an exact
P1 jack sample is already available, record disconnected mating/contact evidence.
If none is available, leave that check pending; do not substitute a nominal
“1.5 mm” description for proof. Photos can identify a connector but cannot alone
close the physical-fit test. See the [connector worksheet](CONNECTOR_VERIFICATION_A0_3.md).

The [working-system acceptance plan](SYSTEM_ACCEPTANCE_PLAN.md) separates
pre-fabrication design review from tests that require assembled hardware.
The [blocker register](REVIEW_BLOCKERS.md) maps every November 17 finding to
closure evidence. The [original report](reviews/independent-577aad8-2026-11-17/REPORT.md)
remains intact, including the measurements it says were not performed.

`.kicad_sch` defines the circuit; `.kicad_pcb` contains placement and copper.
`design.json` is generated component/net/starting-placement data, not a fabrication
file. Preserve the routed CAD: generation refuses a board with copper; router
import requires a matching export and clean candidate DRC. Automated passes do
not establish signal quality or safety.
