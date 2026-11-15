# Independent review handoff — Neuronic A0.2

Use this brief in a fresh AI conversation or give it to an electronics reviewer.
The goal is to find and document defects before spending money on fabrication.
A separate AI review is useful, but does not replace measurements or a qualified
review of the final body-connected hardware.

## Exact design to review

Repository: https://github.com/kamenzh/neuronics-eeg

Review commit: **558886fb6f877d274462cd4d457188c72b215d7d**

Pinned files: https://github.com/kamenzh/neuronics-eeg/tree/558886fb6f877d274462cd4d457188c72b215d7d

Project constraints:

- Eight simultaneous EEG channels, one ADS1299, shared reference and bias: ten physical contacts.
- Affordable bare PCB, assembled by the owner. Avoid a preventable second fabrication order.
- Use the owned Waveshare ESP32-S3-Nano, connected through J11; no radio power from the AFE regulators.
- Owned Sino-k SGE117DN gold-cup leads. The user thinks the plugs are 1.5 mm DIN 42802 touchproof; physical compatibility is not confirmed.
- The saved design uses P1 36619 / 8R003661901F jacks and TPS7A2450DBVR / TPS7A2433DBVR regulators.
- The 88 x 90 mm four-layer board is routed and explicitly marked bench only. No body-use or manufacturing release has been issued.

## Request to the reviewer

Act as a critical reviewer of a low-noise analog PCB. Independently inspect the
actual KiCad schematic, board, footprints and BOM. Do not assume the existing
documentation or a clean ERC/DRC proves the circuit is correct. Do not rewrite
the design to make tests pass, suppress findings, or claim physical testing.

Work on an isolated copy of the pinned commit. Preserve the original circuit
and copper. Do not run the hardware generator or import the intermediate
routing session over the final board. No design changes, commits or pushes
are requested as part of this review.

Start with:

- `hardware/kicad/neuronic.kicad_pro`, all three schematic sheets and the PCB.
- `hardware/parts.json`, `hardware/interface.json` and `hardware/bom/`.
- `hardware/footprints/` and bundled `Neuronic.pretty/` footprints.
- `docs/PROTECTION_POWER_REVIEW_A0_2.md`, `docs/REVIEW_BLOCKERS.md` and `docs/BENCH_TEST_PLAN.md`.
- `hardware/validation/STATUS.md` and the scripts/tests that produce its claims.
- `hardware/routing/README.md`: the router session is intermediate, not the final board.

Check the following against manufacturer primary sources, identifying the
actual device variant, datasheet revision and relevant section or drawing:

1. ADS1299 pin assignments, supplies, charge-pump returns, VCAP/reference capacitors, reference topology and firmware assumptions.
2. Regulator pinouts, full error budget, effective capacitance, startup, dropout, dissipation, noise and reverse/unpowered current paths.
3. Input resistor/clamp polarity, realistic fault-current paths, aggregate contact currents, reference matching/CMRR, bias feedback and cable stability.
4. Socket mating gender, signal versus dummy pins, drill and pad dimensions, positional tolerance stack, courtyard, board edge and enclosure fit.
5. Actual routed local bypass loops, return paths, vias, reference/bias routing, digital coupling, mounting and hand-solder practicality.
6. Battery/controller branches, protection, switches, GPIO power sequencing and USB/charging paths.
7. Test quality: fresh results versus stale artifacts, assertions that merely repeat the generator, missing negative tests, regeneration/import hazards.
8. Missing information needed for a useful bench build and, separately, for body-connected operation.

## Checks that can run before hardware exists

Run from an isolated checkout using KiCad-compatible Python. These commands
write generated files, so do not run them over the owner's working checkout:

```bash
kicad-cli version
/usr/bin/python3 tools/validate_kicad.py
/usr/bin/python3 tools/check_routing.py
python3 tools/review_electrical.py
python3 tools/simulate_input.py
/usr/bin/python3 -m unittest discover -s tests -v
```

Independently rerun schematic ERC and full schematic-parity DRC after refilling
zones in a disposable PCB copy. Inspect the assertions, not just exit codes.
Record tool versions, exact commands, output, limits and any unavailable checks.
Use additional calculations or simulations only when the model supports the
conclusion. An ideal RC calculation is not a clamp, electrode or bias-loop test.

## Required review report

Write `docs/INDEPENDENT_REVIEW_A0_2.md` and keep reproducible evidence in
`hardware/validation/independent-a0_2/`.

Begin with a decision: what blocks ordering, what requires redesign/rerouting,
and what must wait for physical measurements. Identify the reviewed commit.
Use this finding format:

| Field | Required content |
| --- | --- |
| ID and severity | Critical, high, medium or low, with a concrete reason |
| Location | File plus reference/pin/net or PCB coordinates |
| Evidence | Observed circuit/geometry, calculation or test, source URL and section |
| Consequence | What can fail and under which actual condition |
| Confidence | Confirmed defect, supported concern, or unresolved assumption |
| Fix | Specific suggested change, including whether routing/BOM changes are needed |
| Verification | How the fix can be checked, and whether hardware is required |

Separate actual errors from unverified assumptions and optional improvements.
List verified strengths as well as problems. Finish with the smallest prioritized
set of fixes needed before an order, followed by a physical bench-test plan.
Never present automated checks as body-safety certification.

## What comes after the review

1. Triage the report and resolve design/fault-protection issues that could force a respin.
2. Verify the actual cable/socket fit and critical capacitor data; finalize the battery/controller harness and fabricator stack-up.
3. Apply accepted fixes and rerun ERC, DRC, connectivity and targeted regression checks.
4. Inspect a manufacturing package independently: Gerbers, drills, BOM and assembly drawings; compare delivered bare-board costs.
5. Order and assemble the prototype; test power, SPI, internal signals, noise, bias response and wireless timing without a person connected.
6. Complete the final assembled body-interface review before any scalp recording.

Basic acquisition firmware can be developed alongside the hardware review.
A circuit or simulation review cannot physically test a board that has not
been manufactured.
