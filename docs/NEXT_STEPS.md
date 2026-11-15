# From A0.2 to an assembled prototype

A0.2 selects the touchproof sockets, revises the regulators, documents bounded
protection/power calculations, and adds copper routing. The owned Waveshare
ESP32-S3-Nano and Sino-k ten-lead set remain the system choices.

The [independent A0.2 review](INDEPENDENT_REVIEW_A0_2.md) has now reproduced the
automated checks and identified actionable issues. The reviewed hardware is
still commit `558886f`; the review itself does not apply its proposed fixes.
Do not order the current board yet. Close the likely causes of a second board
order first, especially core power/reference routing and connector fit.

| Next step | Completion evidence |
| --- | --- |
| Correct the ADS1299 supply and bypass layout | Separate charge-pump supply branch; short local reference/VCAP/supply connections; reviewed return paths |
| Correct default digital logic margins | Revised R30-R35 values and a worst-case LOW-level calculation including host leakage |
| Verify socket and capacitor assumptions | Actual cable mates with P1 36619 sample; hole-fit/enclosure check; effective capacitor data |
| Resolve remaining circuit and harness decisions | Input-filter/reference matching, bias-loop test model, protection fault paths, battery/controller branch protection and power-off behavior; resolve choices that affect copper before fabrication |
| Verify the revised design | Fresh ERC, full schematic-parity DRC, connectivity checks and independent review of the changed copper; selected manufacturer stack-up |
| Prepare a bench-only fabrication release | Independent Gerber/drill inspection, exact BOM, assembly drawings and delivered bare-board quote |
| Order bare boards and solder components | Optical inspection, continuity/polarity checks, no shorts; no person connected |
| Bring up power and firmware | Rails/current/temperature/startup, SPI register readback, internal test, loss-counted streaming |
| Measure acquisition | Shorted-input noise, calibrated microvolt source, bias-loop response, radio interference and fault tests |
| Resolve body-connected protection | Qualified review of assembled electronics, cable/enclosure, aggregate leakage, faults and USB/charging paths |
| Record EEG and evaluate control | Repeatable data first; artifact checks and held-out-session classification before robotic-arm commands |

See `hardware/validation/STATUS.md` for the original CAD checkpoint and
`hardware/validation/independent-a0_2/` for fresh review evidence. The earlier
`PROTECTION_POWER_REVIEW_A0_2.md` records the original design decisions; the
independent review adds criticism and does not supersede unperformed physical tests.
Firmware may proceed alongside physical verification using `hardware/interface.json`.
No physical board, acquisition firmware or trained mind-control classifier is
claimed by this checkpoint.

`.kicad_sch` defines the circuit; `.kicad_pcb` now contains real copper.
`design.json` is an audit record, not a fabrication file. The routed KiCad board
is authoritative for placement and routing. The generator refuses to overwrite
tracks/vias/zones; preserve and edit that board. Re-run validation after changes.
