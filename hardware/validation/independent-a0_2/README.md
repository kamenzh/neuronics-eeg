# Independent review evidence

Reviewed SHA: `558886fb6f877d274462cd4d457188c72b215d7d`.

Read [the review report](../../../docs/INDEPENDENT_REVIEW_A0_2.md). This directory contains fresh KiCad reports, independently extracted geometry/pin mapping, original bounded calculations and command logs. No vendor PDF, page image or copied article is included. Manufacturer references are linked in the report.

- `test-runs.json`: exact commands, cwd, timestamps, stdout/stderr and exit codes.
- `review-integrity.json` / `input-sha256.json`: reviewed-source and unchanged-CAD evidence.
- `ads1299-64-pin-contract.csv`: all 64 manufacturer pin names, fresh netlist/PCB parity and coordinates.
- `inspect_actual_board.py` / `independent-geometry.json`: read-only copper paths, nearest same-net bypasses and ground-return geometry. The geometric graph is not an impedance or electromagnetic model.
- `independent_calculations.py` / `independent-calculations.json`: tolerance, RC sensitivity, bias-pole, logic-margin and bounded power/current calculations.
- `erc.txt` / `drc.txt`: fresh KiCad ERC/full schematic-parity DRC. Other copied JSONs are fresh outputs of the repository's existing checkers, whose scope is audited in the report.
- `refill-check.json` / `refilled-drc.txt`: an additional zone refill and full parity DRC in a disposable project copy, including the unchanged board hash.

Independent scripts require `/usr/bin/python3` with KiCad pcbnew for geometry, and are run from the repository root. The other script is Python standard library only.

No hardware or body-use test was performed. Passing these tools does not establish fabrication readiness, analog performance or body safety.
