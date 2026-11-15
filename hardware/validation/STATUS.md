# Validation status — A0.2, 2026-11-15

**Routed bench-development checkpoint; not a manufacturing or body-use release.**
No physical board was tested. Reports are freshly generated from the saved
KiCad 9.0.2 source, not from the intermediate router output.

| Check | Result | Scope |
| --- | --- | --- |
| Schematic export | Three sheets | Real editable KiCad sources |
| Exported netlist audit | 462/462 pass | ADS1299, TPS7A24 fixed-regulator pins, sockets, reference, Nano mapping |
| Saved PCB pad/net comparison | 370 checks, zero issues | 91 electrical footprints plus four mounting holes; isolated socket dummy pads |
| ERC | 0 errors, 0 warnings | No exclusions added |
| Full DRC | 0 violations, 0 unconnected items, 0 footprint parity errors | Filled saved copper; full schematic parity enabled |
| Copper | 537 track segments, 87 vias, 2 filled ground zones | 88 x 90 mm; In1 dedicated GND, In2 crossover/fill |
| Routing boundary checks | 4/4 pass | No tracks on In1, filled zones, host digital traces right of x=103 mm |
| Conditional electrical calculations | 9/9 pass | Explicit DC assumptions; no patient-current or transient qualification |
| Workflow regression tests | 5/5 pass | Protect copper and reject stale netlist results |
| Ideal input RC calculation | Pass | One linear RC model; not a full electrode/clamp/bias simulation |
| Candidate PCB BOM | 91 components / 22 groups | Exact candidates, no live stock/price guarantee |
| Connector physical fit | Not verified | User-assumed DIN 42802; derived P1 footprint needs sample/coupon check |
| Hardware noise/fault/thermal tests | Not performed | Assembled hardware and firmware required |
| Body-connected safety review | Not passed | Current limiting, aggregate leakage, power-off and external connections remain open |

`cli-checks.json` records CAD/catalog/interface hashes and all tool return codes.
`automated_checks_passed` can now be true, while `manufacture_ready` remains false.
`electrical-review.json` also explicitly leaves body connection unapproved.
The mocked failures in `workflow-tests.txt` are regression fixtures, not actual
KiCad failures.

## Recheck this routed board

```bash
/usr/bin/python3 tools/route_hardware.py fill
/usr/bin/python3 tools/check_routing.py
/usr/bin/python3 tools/validate_kicad.py
python3 tools/prepare_bom.py
python3 tools/review_electrical.py
python3 tools/simulate_input.py
/usr/bin/python3 -m unittest discover -s tests -v
python3 tools/render_previews.py
```

Do not regenerate this PCB: the generator deliberately refuses existing copper.
The routed KiCad board is authoritative. The routing directory contains an
intermediate session, not a substitute for the later manual fixes.

Read `docs/PROTECTION_POWER_REVIEW_A0_2.md` for the socket and electrical review,
`docs/REVIEW_BLOCKERS.md` for unresolved engineering items, and
`docs/NEXT_STEPS.md` for the manufacturing roadmap.
