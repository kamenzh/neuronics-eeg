# Open design blockers — no manufacturing release

These items are engineering work, not requests for user permission.

| ID | Open item | Evidence required to close |
| --- | --- | --- |
| HW-01 | Final electrode connector unknown | Actual plug measurement, matching touchproof part number, drawing, PCB footprint and enclosure fit |
| HW-02 | Clamp network not validated | Worst-case BAV199 forward voltage, ADS1299 allowed input voltage/injection current, leakage/noise, transient and unpowered behavior |
| HW-03 | Body-current protection incomplete | Review all input/reference/bias/USB/power fault paths, parallel paths and aggregate current; do not claim resistor-only compliance |
| HW-04 | Bias-loop stability untested | Electrode impedance/cable capacitance model, simulation if suitable model is available, then bench phase/settling tests |
| HW-05 | Power design not characterized | Exact LDO/fuse/capacitor parts, thermal/dropout review, startup sequence, rail ripple and noise measurement |
| HW-06 | Controller and access plan incomplete | Selected ESP32 board, pin map, own power budget, programming/charging arrangement and wiring review |
| HW-07 | Placement preliminary | Short bypass loops per supply pin, charge-pump/star connection treatment, reference/bias/input placement and return-current review |
| HW-08 | PCB unrouted | Route, add reviewed planes, refill zones, zero unconnected items and clean schematic parity |
| HW-09 | ERC not executed in supplied runtime | Run KiCad >=8 CLI or GUI ERC; investigate every finding without blanket exclusions |
| HW-10 | BOM not procurement-ready | Real MPN for every part, voltage/tolerance/dielectric, stock and delivered quote to Bulgaria |
| HW-11 | No physical measurements yet | Complete bench test record with instrument conditions and actual values |
| HW-12 | No body-use review | Qualified review of the final assembled topology and physical interconnects before any person is connected |

The current pin headers are expressly for bench wiring. USB/ground paths are
not galvanically isolated. Separate LDOs do not provide electrical isolation.
