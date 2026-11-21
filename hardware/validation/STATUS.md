# Validation status — A0.3, 2026-11-15

**A0.4 update.** See the [current circuit decisions, dimensions, budgets and checks](../../docs/A0_4_DESIGN_REVIEW.md). The A0.3 figures below describe the earlier hardware. The Sino-k leads have not been ordered.

**Routed bench-development checkpoint; not a manufacturing or body-use release.**
No physical board was tested and no acquisition firmware was built. Reports
were generated from the saved KiCad 9.0.2 source, not the partial router output.

| Check | Result | Scope |
| --- | --- | --- |
| Schematic export | Four sheets | Editable core, input, power and interface sources |
| Exported netlist audit | 573/573 pass | ADC, regulators, TXU0304 pin mapping, defaults, sockets, reference and Nano mapping |
| Saved PCB pad/net comparison | 442 checks, zero issues | 107 electrical footprints plus four mounting holes |
| ERC | 0 errors, 0 warnings | No exclusions added |
| Full DRC | 0 violations, 0 unconnected items, 0 schematic parity issues | Filled saved copper; full schematic parity enabled |
| Copper | 1,181 track segments, 123 vias, 2 filled ground zones | 88 × 90 mm; four layers; In1 dedicated GND, In2 crossover/fill |
| Routing boundary checks | 5/5 pass | No In1 tracks, filled zones, all 25 expected digital nets routed, host digital traces right of x=103 mm |
| Conditional electrical calculations | 12/12 pass | Explicit assumptions, including reference-capacitance estimate and socket tolerance model; no physical qualification |
| Workflow regression tests | 9/9 pass | Protect existing copper, reject stale exports/sessions, and preserve the board when candidate DRC fails |
| Input model | Calculated | Ideal RC response, resistor noise, tolerance-only common-mode conversion and illustrative cable capacitance; not full ADC/SPICE or bias-loop stability analysis |
| Candidate PCB BOM | 107 components / 25 groups | Candidate parts; no live stock/price guarantee; off-board harness listed separately |
| Independent A0.3 follow-up | No new blocking defect in the checked copper | Read-only geometry, pin-map and calculation review; see the review's scope and remaining criticisms |
| Connector physical fit | Not verified | Assumed DIN 42802 plug family; sample mating, slot/coupon fit and fabricator tolerances remain open |
| Firmware and hardware tests | Pending | Firmware implementation/build, assembled hardware, noise, startup, fault, thermal and radio measurements required |
| Body-connected safety review | Not passed | Aggregate leakage, faults, analog power-off injection and complete external connections remain open |

Reviewed PCB SHA-256:
`56e3c25c3cbefbf489e86c24db1670b0620a263d7c0c5adaea14d672e3de33b5`

`cli-checks.json` records CAD, catalog, interface, tool and test-source hashes,
plus the KiCad command results. `automated_checks_passed` is true while
`manufacture_ready` remains false. `electrical-review.json` also leaves body
connection unapproved. The mocked failures in `workflow-tests.txt` are regression
fixtures, not actual KiCad failures. The router-import guards have negative
regression tests; a successful new export/import round trip is not claimed.

## Documentation and connector follow-up — 2026-11-19

The [November 17 independent report](../../docs/reviews/independent-577aad8-2026-11-17/REPORT.md)
and all its original evidence are incorporated. It repeated ERC/full DRC and
the nine workflow tests successfully. Its additional strict-category run exposed
13 footprint-filter warnings, with no copper/unconnected errors. The default
zero-violation result above must not be read as zero warnings under every setting.

The November 19 [read-only connector audit](connector-review-2026-11-19/saved-cad.json)
confirms all 13 connector footprints, 107 components / 25 groups / 23 unique
MPNs, and all 46 previous validation input hashes. CAD, BOM CSVs, source tools,
tests and copper were not changed; this follow-up did not rerun ERC/DRC or claim
new physical measurements. The [connector worksheet](../../docs/CONNECTOR_VERIFICATION_A0_3.md)
records manufacturer drawings, remaining fit checks and a J12 tolerance erratum.
Only the stale BOM-prose finding is closed. Firmware, physical performance and
person-use acceptance remain pending under the
[working-system plan](../../docs/SYSTEM_ACCEPTANCE_PLAN.md).

## Recheck the saved board

```bash
/usr/bin/python3 tools/validate_kicad.py
/usr/bin/python3 tools/check_routing.py
python3 tools/prepare_bom.py
python3 tools/review_electrical.py
python3 tools/simulate_input.py
/usr/bin/python3 -m unittest discover -s tests -v
python3 tools/render_previews.py
```

After intentional copper changes, refill zones with KiCad's `B` command or
`/usr/bin/python3 tools/route_hardware.py fill`, then rerun validation. This
changes the board hash and makes the current geometry review historical.

Do not regenerate this PCB: the generator refuses existing copper. The saved
routed board is authoritative. The routing directory contains an incomplete
historical pass, not a substitute for the final board.

See the [independent A0.3 review](../../docs/INDEPENDENT_REVIEW_A0_3.md),
[review-fix record](../../docs/REVIEW_FIXES_A0_3.md),
[power harness and changed J11 pinout](../../docs/POWER_HARNESS_A0_3.md),
[remaining blockers](../../docs/REVIEW_BLOCKERS.md) and
[next steps](../../docs/NEXT_STEPS.md). The A0.2 review and its evidence remain
unchanged for comparison.
