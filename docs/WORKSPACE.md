# Workspace and upstream

Upstream: https://github.com/kamenzh/neuronics-eeg

A0.1 is based on `b8af12f03bf256dca78ebfd285dcb80679491b1f` (A0 on main).
This revision reconstructs earlier missing review changes and incorporates the
user's owned Waveshare ESP32-S3-Nano and Sino-k SGE117DN electrode selection.
See Git history for the published checkpoint; this document does not embed its
own commit ID.

Open `hardware/kicad/neuronic.kicad_pro` in KiCad 9. Keep bundled libraries with
the project. Commit existing GUI edits before regeneration. The main files are
real editable CAD, but the present PCB is unrouted and no fabrication package
exists. Old starter content remains available in Git history and docs/archive.
