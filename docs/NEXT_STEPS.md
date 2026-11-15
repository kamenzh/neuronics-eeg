# From this checkpoint to a manufactured PCB

**Current state: A0.1 schematic plus preliminary component placement. Copper
routing has not started.** One eight-channel ADS1299, the owned Waveshare
ESP32-S3-Nano and the owned Sino-k ten-lead cup set are the selected system.

| Step | Work | Completion evidence |
| --- | --- | --- |
| 1 — now | Finalize the electrode plug/socket pair and battery/USB/power harness; review protection, reference, bias and effective capacitors | Dimensioned connector drawings, documented electrical review and closed pre-layout blockers |
| 2 | Refine the 4-layer placement around actual ADS1299 supply/input pins, Nano separation and enclosure access | Reviewed bypass loops, input/reference geometry and return-current plan |
| 3 | Route copper, vias and ground/power zones using the chosen fabricator's stack-up/rules | Filled zones; zero unconnected connections; clean ERC and full schematic-parity DRC |
| 4 | Review footprints/polarity, freeze BOM and compare bare-board delivered quotes | One consistent revision with verified sourcing and final assembly drawing |
| 5 | Export Gerbers and drill files; inspect them in an independent viewer | Manufacturing ZIP with drill/board outline/masks/silkscreen and fabrication notes |
| 6 | Order bare prototype boards and reviewed components; solder and inspect | Assembled board with no shorts/bridges and documented polarity/continuity checks |
| 7 | Bring up power, then SPI/internal test, shorted inputs, microvolt test source, noise and wireless timing | Measured bench log tied to PCB/firmware revisions |
| 8 | Complete final body-connected safety review | Reviewed protection, interconnects/enclosure and battery-only operating arrangement |
| 9 | Record repeatable EEG and then develop command classification | Clean raw data with timestamps, artifact checks and held-out-session evaluation |

Firmware can proceed alongside steps 1–4 using `hardware/interface.json`: first
register readback/internal test, then loss-counted raw streaming. It is not yet
implemented. Robotic-arm control comes after reliable acquisition and measured
classification; the eight-channel hardware alone does not produce arbitrary
mind-controlled motion.

**What the files mean:** `.kicad_sch` defines the electrical connections;
`.kicad_pcb` holds physical placement and eventually copper. `design.json` is a
generated audit record of parts/nets/placements, not a manufacturing file and
not the sole editable circuit source. Circuit generation lives in
`tools/generate_hardware.py`; part candidates in `hardware/parts.json`; the
external controller/electrode contract in `hardware/interface.json`.

The scripts generate or check files; they do not fabricate a board. Keep the
KiCad GUI layout as the source of truth once routing begins. Generator safeguards
prevent replacing a board containing tracks, vias or zones even with --overwrite.
