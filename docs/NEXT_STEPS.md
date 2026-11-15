# From A0.2 to an assembled prototype

A0.2 selects the touchproof sockets, revises the regulators, documents bounded
protection/power calculations, and adds copper routing. The owned Waveshare
ESP32-S3-Nano and Sino-k ten-lead set remain the system choices.

| Next step | Completion evidence |
| --- | --- |
| Verify socket and capacitor assumptions | Actual cable mates with P1 36619 sample; hole-fit/enclosure check; effective capacitor data |
| Review routed layout and external power harness | Pin-by-pin analog/return review, manufacturer stack-up, battery/controller branch protection, power-off behavior |
| Prepare a bench-only fabrication release | Independent Gerber/drill inspection, exact BOM, assembly drawings and delivered bare-board quote |
| Order bare boards and solder components | Optical inspection, continuity/polarity checks, no shorts; no person connected |
| Bring up power and firmware | Rails/current/temperature/startup, SPI register readback, internal test, loss-counted streaming |
| Measure acquisition | Shorted-input noise, calibrated microvolt source, bias-loop response, radio interference and fault tests |
| Resolve body-connected protection | Qualified review of assembled electronics, cable/enclosure, aggregate leakage, faults and USB/charging paths |
| Record EEG and evaluate control | Repeatable data first; artifact checks and held-out-session classification before robotic-arm commands |

See `hardware/validation/STATUS.md` for actual CAD results and
`PROTECTION_POWER_REVIEW_A0_2.md` for the review's conclusions and limits.
Firmware may proceed alongside physical verification using `hardware/interface.json`.
No physical board, acquisition firmware or trained mind-control classifier is
claimed by this checkpoint.

`.kicad_sch` defines the circuit; `.kicad_pcb` now contains real copper.
`design.json` is an audit record, not a fabrication file. The routed KiCad board
is authoritative for placement and routing. The generator refuses to overwrite
tracks/vias/zones; preserve and edit that board. Re-run validation after changes.
