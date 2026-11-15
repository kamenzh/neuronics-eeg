# Validation status — A0.1, 2026-11-15

**Not ready for fabrication or body connection.** These are fresh results for
this revision, generated with KiCad 9.0.2. No assembled board was tested.

| Check | Result | Scope |
| --- | --- | --- |
| Schematic load/export | Pass, three sheets | Editable KiCad files and refreshed SVG/PNG previews |
| Actual exported netlist | 436/436 pass | Parts/footprints, independent ADS1299 pin contract, direct shared reference, J11 and Nano GPIO mapping |
| Saved PCB pad/net comparison | 348 checks, zero issues | 91 electrical footprints plus four board-only mounting holes; includes exact NC names |
| ERC | 0 errors, 0 warnings | No exclusions added |
| DRC geometry/rules | 0 violations | Preliminary placement only; does not establish analog layout quality |
| DRC schematic parity | 0 footprint errors | Full KiCad schematic-parity option enabled |
| DRC missing connections | **193 — FAIL** | No copper routing yet; retained in report, not suppressed |
| Saved copper inventory | 0 tracks, 0 vias, 0 zones | 88 x 80 mm, four-layer placement checkpoint |
| Conditional electrical calculations | 5/5 pass | Assumption-based budgets; not a circuit simulation or measurement |
| Workflow regression tests | 5/5 pass | Prevent stale netlist success and overwriting tracks/vias/zones or unconfirmed schematic edits |
| Ideal input RC model | Pass | One linear RC path only; not electrode, clamp or bias-loop behavior |
| Candidate PCB BOM | 91 components / 22 groups | Exact candidate MPNs, no purchase approval or live price/stock claim |
| Physical performance and body-use review | **Not performed** | Power/noise, bias stability, fault paths and assembled interconnects remain open |

`cli-checks.json` records return codes and SHA-256 hashes of CAD/catalog/interface
inputs. `validate_kicad.py` exits 1 because the DRC process returns 5 for missing
connections. This failure is expected at this milestone and blocks release.
A future all-pass CAD report still would not establish electrical or body safety.

`workflow-tests.txt` includes deliberately failed mocked CLI calls inside the
stale-export regression test; those are test fixtures, not the actual KiCad run.
Actual CAD results are in `erc.txt`, `drc.txt` and `cli-checks.json`.

## Reproduce (Linux, KiCad 9 installed)

```bash
# Generate only if intentionally replacing the unrouted checkpoint; commit edits first.
/usr/bin/python3 tools/generate_hardware.py --board --overwrite
/usr/bin/python3 tools/validate_kicad.py
python3 tools/prepare_bom.py
python3 tools/review_electrical.py
python3 tools/simulate_input.py
/usr/bin/python3 -m unittest discover -s tests -v
python3 tools/render_previews.py
```

Rendering requires Inkscape. On Windows use KiCad's compatible Python for pcbnew
checks, or run full ERC/DRC in KiCad and record any unavailable script checks
honestly. Do not treat unavailable checks as passes.

Read `docs/SCHEMATIC_REVIEW_A0_1.md` for changes and `docs/NEXT_STEPS.md` for the
remaining manufacturing roadmap. The electrode connector remains unresolved
because the supplied product listing does not specify the mating dimensions.
