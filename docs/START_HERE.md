# Neuronic: your first PCB, step by step

**Start with `hardware/kicad/neuronic.kicad_pro`.** This package contains a real,
editable KiCad project and a reproducible generator. Revision A0 is a **bench-only,
placed but unrouted review checkpoint**. It is not ready to order or wear.

## 1. What a custom PCB actually involves

| Step | What it means | File or output |
| --- | --- | --- |
| Requirements | Decide channel count, supplies, controller interface and tests | `docs/DESIGN_DECISIONS.md` |
| Schematic | Define which numbered component pins connect | `.kicad_sch` |
| Component selection | Select exact purchasable parts and physical packages | BOM and datasheets |
| Footprint assignment | Map symbol pin numbers to real solder-pad numbers | `.kicad_mod`, `.pretty/` |
| Placement | Put the packages in sensible physical locations | `.kicad_pcb` |
| Routing | Draw copper tracks and vias, then add/fill copper planes | `.kicad_pcb` |
| Verification | Check connections, geometry, footprints and electrical behavior | ERC, DRC, review and bench reports |
| Manufacturing | Export a reviewed, frozen revision | Gerbers, drill, BOM, placement and drawings |

A symbol is a drawing used in the schematic. A footprint is the physical solder
pad pattern. A net is a named electrical connection. A ratsnest line shows a
connection that still needs copper; it is not an existing track.

## 2. Open this checkpoint on Windows

1. Extract the whole archive into a normal directory, such as `Documents/Neuronic`.
   Keep the `.pretty` folder, symbol file and library tables beside the project.
2. In KiCad, select **File -> Open Existing Project** and open
   `hardware/kicad/neuronic.kicad_pro`.
3. Open `neuronic.kicad_sch`. The main sheet contains the ADS1299 and controller
   connector. Enter the `Input filters` and `Power` child sheets to inspect those
   circuits. The page navigator can also select a sheet.
4. Open `neuronic.kicad_pcb`. You should see the ADS1299 in the middle, inputs on
   the left, regulators and SPI connector on the right, and thin ratsnest lines.
5. Use the mouse wheel to zoom, `M` to move, `R` to rotate and `E` to edit.
   Press `Esc` to exit a tool. Use **View -> 3D Viewer** or `Alt+3` for 3D.

The files were loaded and exported using KiCad 7.0.11. Newer versions can upgrade
them when saving; keep the upgraded project in Git together. Do not expect an
older KiCad version to reopen files saved by a newer version.

The bundled footprints make the project portable. 3D models are not bundled, so
some packages may have pads but no 3D body until the normal KiCad 3D library is
installed. That does not establish whether the footprint is physically correct.

## 3. What this circuit does

The eight channel contacts pass through two 10 kohm resistors, an RF capacitor
and candidate low-leakage clamps. The ADS1299 measures them relative to the ninth
contact through SRB1. A tenth contact is the current-limited bias output.

The ADS1299 contains eight programmable amplifiers and eight simultaneous 24-bit
converters. The ESP32 receives **digital samples**, not an analog EEG voltage.
At 250 samples/s, a frame has 3 status bytes and 8 x 3 channel bytes: 27 bytes,
or 6,750 raw bytes/s before packet headers. Keep counters and acquisition timing.

This revision uses unipolar 5 V analog power and 3.3 V ADC digital power, with a
7-9 V battery input. The internal bias reference is approximately 2.5 V. This
matters: a signal can be within the voltage rails yet violate the amplifier's
common-mode or differential range. A unipolar design is a deliberate departure
from references using +/-2.5 V; their connections cannot be copied blindly.

`J11` is a generic 12-pin connector, not a footprint for any particular ESP32
development board. Pin 11 is the ADC's logic reference; **it must not power an
ESP32 radio**. A specific ESP32 board, its GPIO assignments and battery supply
remain to be selected. Use short wiring for SPI and position the radio away
from the electrode inputs. Do not connect EEG to the ESP32's internal ADC.

## 4. How to vibe-code hardware properly

Use AI to propose small, reviewable changes with evidence:

1. State one requirement, such as "check all ADS1299 supply pins and bypasses".
2. Require the exact datasheet revision, pin numbers, package and rationale.
3. Change one functional block and inspect the schematic before layout changes.
4. Export the actual KiCad netlist and check what KiCad understood.
5. Update the PCB from the schematic with **Tools -> Update PCB from Schematic**
   (`F8`). Review the proposed changes; do not delete unmatched footprints blindly.
6. Run ERC and DRC. Read every warning rather than hiding categories until a
   report looks clean. Commit a checkpoint with the known limitations.

An example prompt is in `docs/VIBE_CODING_PROMPT.md`. The generator is
`tools/generate_hardware.py`; it uses deterministic IDs so component identity is
stable across runs. It writes the schematic, custom symbols, footprint bundle,
BOM and, with `--board`, the PCB placement. **Regeneration overwrites GUI edits.**
After hand routing, keep the PCB as the source of truth or explicitly teach the
generator to preserve it. Do not regenerate over your only routed board.

Running the existing project does not require Python. Regenerating schematic
files needs Python and installed KiCad symbol/footprint libraries. Generating
the PCB also needs KiCad's `pcbnew` Python module; on Linux this is commonly
available to the distribution's `/usr/bin/python3`. A normal Windows Python
installation may not find `pcbnew`. Use the KiCad GUI for layout if needed.

## 5. Finish the design before routing everything

Resolve `docs/REVIEW_BLOCKERS.md` first. In particular:

- Check the gold-cup lead plug dimensions and choose real touchproof connectors.
  The ten pin headers are bench placeholders, not the final electrode interface.
- Review clamp behavior, current paths, aggregate leakage and bias stability.
- Verify regulator parts, capacitance under DC bias, thermal limits and shutdown
  behavior. The power circuit is not yet measured to be quiet enough for EEG.
- Select the controller board and solve programming/charging access physically.
- Rework placement around actual pin locations: decoupling capacitors must have
  short loops, and AVDD1/AVSS1 return paths need particular care.

For routing, use a four-layer board as a starting constraint: signal/components,
continuous ground, power/low-speed routing, and secondary signals. Keep the
ground plane continuous under sensitive signals and route return currents away
from the analog input region. Do not split ground simply because nets are
called "analog" and "digital". Plan where radio/switching return currents flow.

In PCB Editor, use `X` for the interactive router and `V` to insert a via while
routing. Use **Board Setup** to confirm the manufacturer's stack-up, clearance,
trace, drill and annular-ring rules. The initial 0.20 mm clearance, 0.15 mm
minimum trace and 0.60/0.30 mm via are draft project constraints, not a checked
fabrication quote. Route sensitive inputs first, keep them short and clean,
then reference/bias, decoupling/power and finally digital signals.

## 6. Check it in KiCad

**Schematic Editor -> Inspect -> Electrical Rules Checker -> Run ERC.**
Check pin types, unpowered rails, output conflicts, missing connections and
library mismatches. ERC cannot decide whether a filter value, amplifier bias or
protection design is right.

**PCB Editor -> Inspect -> Design Rules Checker -> Run DRC.** Include schematic
parity and unconnected items. Check clearance, shorts, courtyards, copper near
edges and missing connections. Press `B` to refill zones after editing copper.
For an order candidate, require zero unrouted connections and no unexplained
errors; justify any remaining warnings individually.

For KiCad 8 or newer, the supplied runner can collect CLI checks:

```powershell
# Replace 9.0 with the version actually installed on your computer.
py tools/validate_kicad.py --kicad-cli "C:\Program Files\KiCad\9.0\bin\kicad-cli.exe"
```

The script deliberately exits with failure if ERC/DRC finds violations or the
required checks are unavailable. This A0 board is expected to fail DRC because
it has no tracks. `hardware/validation/STATUS.md` records the actual results.

For deeper checks, compare every IC pin and physical package against its
datasheet, inspect the 3D model and connector orientations, and review the
analog layout with an experienced electronics teacher/engineer. A clean ERC
and DRC do not prove circuit function or body safety.

## 7. Test after manufacture

Use `docs/BENCH_TEST_PLAN.md`. The sequence is inspection -> rails -> digital
communication -> internal test waveform -> shorted-input noise -> external
microvolt test signals -> sample timing/wireless -> electrical safety review
before considering body connection. Put measured results in
`hardware/validation/measurements/` with the hardware revision and conditions.

Only after the review and routing are complete should we make a fabrication
package. This checkpoint intentionally has no order-ready Gerbers.
