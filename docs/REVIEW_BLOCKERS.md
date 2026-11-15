# Remaining hardware work — A0.1

These are engineering tasks, not requests for permission. No manufacturing release.

| ID | State / item | Evidence required |
| --- | --- | --- |
| HW-01 | Electrode identified: Sino-k SGE117DN; mating socket OPEN | Actual plug dimensions, compatible touchproof part/drawing, verified footprint and enclosure fit |
| HW-02 | Clamp network OPEN | Worst-case voltage/injection/leakage/noise, transient and unpowered behavior; BAV199 is not yet proven suitable |
| HW-03 | Body-current protection OPEN | All channel/reference/bias/power/USB faults and aggregate current; resistor-only analysis is insufficient |
| HW-04 | Bias loop OPEN | Realistic electrode/cable model and bench settling/stability measurements |
| HW-05 | Candidate power parts chosen; validation OPEN | Effective capacitance, startup, dropout, temperature, rail noise, external battery harness/branch protection |
| HW-06 | Nano and GPIO map SET; integration OPEN | Physical wiring, VIN under radio bursts, GPIO backfeeding and programming/recording access arrangement |
| HW-07 | Placement PRELIMINARY | Short bypass loops, internal-rail returns, reference/bias/input geometry and radio/return-current review |
| HW-08 | PCB UNROUTED | Tracks, vias, filled reviewed planes; zero unconnected items and clean parity |
| HW-09 | Automated CAD checks EXECUTED | KiCad 9.0.2 ERC clean; geometry/parity clean; routing DRC still fails as recorded in validation/STATUS.md |
| HW-10 | Candidate BOM COMPLETE; procurement OPEN | Verify parts/footprints/stock, replacement electrode sockets, all off-board items and delivered quote |
| HW-11 | Physical tests NOT STARTED | Measured bench results with hardware/firmware revision and instrument conditions |
| HW-12 | Body-use review NOT STARTED | Qualified review of final assembled topology and physical interconnects before any person is connected |

The ten input/bias pin headers are for bench wiring only. USB and the shared
returns are not galvanically isolated. Separate regulators do not create isolation.
