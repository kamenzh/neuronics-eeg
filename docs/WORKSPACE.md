# Workspace and upstream

Upstream: https://github.com/kamenzh/neuronics-eeg

A0.3 implements the main circuit/layout changes proposed in the independent
review of A0.2 hardware commit `558886f`. The A0.2 review checkpoint was
`0d6456d`; historical reports remain in the repo. The new work is on
`hardware/a0.3-review-fixes`, with explicit remaining release gates.

Open `hardware/kicad/neuronic.kicad_pro` in KiCad 9 with its bundled libraries.
The saved PCB is authoritative. Preserve and edit that routed board; the source
generator refuses to replace copper. Use the revised J11 cable contract.

No manufacturing package or body-use approval is implied. Read
`hardware/validation/STATUS.md` and `docs/NEXT_STEPS.md`.
