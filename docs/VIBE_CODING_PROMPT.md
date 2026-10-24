# Prompt for the next hardware iteration

Use this from the repository root with an AI coding agent:

> Work on Neuronic, an eight-channel ADS1299 EEG acquisition project. Read
> README.md, docs/START_HERE.md, docs/DESIGN_DECISIONS.md,
> docs/REVIEW_BLOCKERS.md and hardware/validation/STATUS.md first.
>
> Complete ONE named design blocker at a time. Cite primary datasheets with
> revision, page/section and physical pin numbers for circuit decisions. Do not
> invent a component, footprint, simulation model or measured result. The design
> is bench-only until protection, power and body-connected fault paths are
> reviewed. Do not imply ERC/DRC proves safety or EEG quality.
>
> Before editing, inspect the current schematic, exported netlist and PCB. Make
> a checkpoint. If modifying generated circuit structure, update
> tools/generate_hardware.py and regenerate the schematic/BOM. Never regenerate
> the PCB over hand routing without preserving it. Retain deterministic symbol
> IDs and show a pin/net change summary.
>
> Validate the actual KiCad export with tools/check_design.py; update independent
> pin-contract checks only when the underlying requirement intentionally changes.
> Run ERC, schematic-parity DRC and the relevant electrical calculations. Save
> complete reports, include unconnected items, and list unresolved findings.
> Check the rendered sheets and PCB before finishing. Do not export an
> order-ready fabrication package while blockers remain. Preserve third-party
> licenses and attribution. Return a concise change summary, evidence and the
> next open blocker.

Suggested first task: HW-02/HW-03, review the candidate input/clamp/fault-current
network and propose a documented replacement if needed, before optimizing cost
or routing the whole board.
