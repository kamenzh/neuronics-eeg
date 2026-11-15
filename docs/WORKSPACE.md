# Workspace and upstream

Upstream: https://github.com/kamenzh/neuronics-eeg

A0.2 follows the published A0.1 checkpoint `1b0b3a11e555164f0fccab73d3814518bf575570`.
It selects P1 touchproof sockets, revises power to TPS7A24 regulators and adds
routed copper with fresh validation. See Git history for the resulting commit.

Open `hardware/kicad/neuronic.kicad_pro` in KiCad 9 and keep the bundled libraries
with it. The routed PCB is authoritative: preserve it and edit in KiCad. The
source generator refuses to replace existing copper. No manufacturing package
or body-use approval is implied; read `hardware/validation/STATUS.md`.

Old starter material remains in Git history and `docs/archive/`.
