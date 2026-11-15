# From A0.3 to an assembled prototype

A0.3 has a revised circuit and real copper routing. The main A0.2 review fixes
are implemented; a manufactured, working EEG device does not exist yet.
Use the owned Waveshare ESP32-S3-Nano and the full eight-channel ADS1299.

The next work has two tracks: physical connector/manufacturing checks, and
acquisition firmware. Neither requires buying an assembled PCB.

| Order | Work | Who can do it | Evidence needed |
| --- | --- | --- | --- |
| 1 | Verify the actual Sino-k lead fits a P1 36619 / 8R003661901F socket | Kamen with a real sample | Comfortable insertion/retention, correct contact, photos/measurements; no forcing |
| 2 | Verify the revised three-hole footprint and enclosure clearance | Kamen + chosen fabricator | Approved slot/hole tolerances; socket coupon/sample solder fit and mechanical support |
| 3 | Finish manufacturing review | CAD reviewer + fabricator | Confirm 4-layer stack-up, process rules, BOM availability, hand-assembly access and remaining analog concerns |
| 4 | Implement bench acquisition firmware and PC recorder | Codex can do this in the repo | Pinned successful build, register readback, test/short modes, timestamps, loss accounting and protocol tests |
| 5 | Export and inspect a bench fabrication package | Codex + independent reviewer | Gerber/drill inspection, plated slots, exact BOM, assembly drawing, test map and recorded source hashes |
| 6 | Choose a delivered bare-board quote | Kamen | Board-only price + shipping + tax; confirm affordable total before ordering |
| 7 | Assemble one board | Kamen, preferably with an experienced soldering helper | Magnified solder inspection, continuity/polarity tests, no rail short |
| 8 | Power and acquire on the bench | Kamen with the documented fixture | Rails, startup, reference, temperature, internal test, noise, calibrated input and radio/loss measurements |
| 9 | Resolve any measured hardware weaknesses | Codex + electronics reviewer | CMRR/reference matching, bias-loop/cable behavior, rail injection and fault analysis; revise if needed |
| 10 | Complete a separate body-connected safety review | Qualified electronics/safety reviewer | Assembled system, cable/enclosure, aggregate leakage, faults and external power paths covered |
| 11 | Record EEG, then evaluate a control model | Kamen + Codex | Repeatable signal first; held-out-session classification and artifact checks before robotic control |

**The practical next item for Kamen is one real socket sample, not a PCB order.**
The plug family is still an assumption. A nominal drawing match cannot replace
that inexpensive physical check. Codex can develop firmware while the sample
and fabricator checks are pending.

The [review-fix record](REVIEW_FIXES_A0_3.md),
[harness/pinout](POWER_HARNESS_A0_3.md) and
[current validation status](../hardware/validation/STATUS.md) distinguish completed
software checks from physical measurements. Historical A0.2 findings remain in
[the independent review](INDEPENDENT_REVIEW_A0_2.md).

`.kicad_sch` defines the circuit; `.kicad_pcb` contains placement and copper.
`design.json` records the generated component/net/starting placement data; it is
not a manufacturing file. Preserve the routed CAD. Generation refuses a board
with copper; a router import now requires a matching export and clean candidate
DRC. Passing either tool is not a body-use approval.
