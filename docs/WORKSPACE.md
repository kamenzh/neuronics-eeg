# Workspace and upstream

Upstream: https://github.com/kamenzh/neuronics-eeg

A0.3 implements the main circuit/layout changes proposed in the independent
review of A0.2 hardware commit `558886f`. The A0.2 review checkpoint was
`0d6456d`; historical reports remain in the repo. The A0.3 routed hardware is
on `main` at checkpoint `577aad8`. The November 17 independent review commit
`1367dec` is incorporated into `main` with its original report/evidence intact.
The November 19 follow-up corrects documentation and records connector desk
checks; hardware source and copper remain unchanged from `577aad8`.

Open `hardware/kicad/neuronic.kicad_pro` in KiCad 9 with its bundled libraries.
The saved PCB is authoritative. Preserve and edit that routed board; the source
generator refuses to replace copper. Use the revised J11 cable contract.

No manufacturing package or body-use approval is implied. Read
`hardware/validation/STATUS.md` and `docs/NEXT_STEPS.md`.
