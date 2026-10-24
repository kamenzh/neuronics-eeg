# Validation status — A0, 2026-10-24

**Release status: BLOCKED. Bench review checkpoint; not for fabrication or body connection.**

| Check | Actual outcome | Practical limit |
| --- | --- | --- |
| KiCad schematic load/export | Passed with KiCad 7.0.11 | Three sheets exported and visually inspected |
| Actual netlist connectivity/footprints | 404/404 passed | Includes independent ADS1299 pin contract; not electrical simulation |
| Saved PCB pad/net parity | 348 checks, zero issues | Does not prove traces exist or replace full KiCad schematic-parity DRC |
| PCB load | Passed with KiCad 7.0.11 | 91 electrical footprints + four mechanical mounting holes |
| DRC geometric violations | 0 in the saved report | Preliminary placement has no copper routes, so this does not prove routability or analog layout quality |
| DRC unconnected items | **195 — FAIL** | Board is entirely unrouted |
| Ideal input RC calculation | Passed | Pole 7,957.75 Hz; excludes ADC, clamps, electrode model and bias loop |
| ERC | **Not run** | Supplied runtime has KiCad 7 CLI, without schematic ERC command; run GUI ERC or KiCad >=8 CLI |
| KiCad full schematic-parity DRC | **Not run** | Use supplied runner with a current KiCad version |
| Physical electrical tests | **Not run** | No manufactured Neuronic board exists |
| Human/body safety review | **Not complete** | See all open design blockers |

## Evidence files

- `neuronic.net.xml`: actual KiCad-exported netlist.
- `connectivity-checks.json`: all connectivity checks, not just a summary.
- `board-net-checks.json`: checks of the actual saved PCB pads against that netlist.
- `drc-placement.txt`: complete report; missing connections remain visible.
- `input-model.json`: ideal RC values, assumptions and explicit limitations.
- `cli-checks.json`: runner result; release fails because ERC/DRC CLI is unavailable in KiCad 7.
- `schematics/`: rendered core/input/power sheets in SVG and PNG.
- `pcb-placement.png`: KiCad plot of physical packages; it does not show copper routing.

No reported result is an EEG performance measurement or safety certification.
Do not interpret the partial geometric pass as a clean board DRC.
