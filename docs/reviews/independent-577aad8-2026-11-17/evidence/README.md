# Evidence index and reproduction notes

All outputs here belong to the independent review of `577aad8a8dee0c60e3b7e949f6b8f7cf200fe180`. They are separate from historical repository reports. Full vendor documents are linked rather than redistributed; downloaded document hashes identify the versions examined.

| Files | Meaning |
| --- | --- |
| `origin.txt`, `source-sha256.json` | Retrieved commit/tree and SHA-256 for all 149 originally tracked files. |
| `INITIAL_FINDINGS.md` | Frozen hypothesis log before opening earlier review reports. Final dispositions are in REPORT.md; an early hypothesis is not a confirmed defect. |
| `initial-commands.json`, `initial-command-*.log` | Native version, fresh netlist, ERC and full DRC commands/exit codes. Initial working directory was `/workspace/scratch/e0fcc76666ca`. |
| `fresh.net.xml`, `schematic-connectivity.txt`, `fresh-erc.txt`, `fresh-drc.txt` | Fresh saved-CAD connectivity and native rule results. |
| `extract_saved_board.py`, `saved-board.json` | Independent read-only pcbnew extraction of pads, tracks, vias, outline and saved filled polygons. No generator-model substitution. |
| `measure_geometry.py`, `geometry-measurements.json` | Independent centerline graph and complete measured paths; via barrel length/plane impedance excluded. |
| `check_plane_returns.py`, `plane-return-samples.json` | Native filled-area sampling. Point coverage is not an electromagnetic field solution or proof of minimum inductance. |
| `plot_geometry.py`, three PNGs | Annotated views of extracted geometry. Pad corners/holes/line rendering simplified; exact CAD SVGs control dimensions. |
| `audit_pin_and_bom.py`, `ADS1299-pin-audit.csv`, `BOM-CAD-crosscheck.csv` | Manually transcribed manufacturer pin intent compared to fresh netlist and saved pad nets; catalog/BOM/CAD identity audit. Physical-fit limits are stated in the report. |
| `independent_calculations.py`, `independent-calculations.json` | RC/noise, mismatch sensitivities, headroom, power, startup, bias and conditional fault-current arithmetic. **Not circuit simulation.** |
| `export-commands.json`, `export-*.log`, `cad-exports/` | Native schematic PDF and exact per-layer SVGs. Drill files under `drill-audit` are review-only, not an order release. |
| `repository-commands.json`, `repo-check-*.log`, `fresh-repository-results/` | Relevant repository scripts and nine tests executed in a separate `bench-copy`; original outputs were not overwritten. The intentional mocked command failure in the unit-test log is not a failed real netlist export. |
| `historical-hash-audit.json` | 46 historical input-hash comparisons, zero mismatches. |
| `refill-and-strict-check.json`, `refill.log`, `refilled-drc.*`, `strict-category-drc.*`, `drill-export.log` | Native refill in `refill-copy`, unchanged PCB hash; full DRC pass. Five previously ignored categories were elevated to warning only in that copy: strict check exit5 with 13 wildcard footprint-filter warnings. |
| `manufacturer-source-hashes.json` | Hashes of successfully downloaded manufacturer PDFs. Nexperia/Bourns direct downloads were blocked but manufacturer documents were read via the web/PDF service. |
| `analysis-commands.json`, `analysis-*.log` | Final recorded executions of independent extraction/measurement/calculation/audit scripts and tool versions. |
| `publication-preflight.json` | Remote main SHA and unique-branch absence immediately before publication. |
| `final-integrity.json` | Original-file preservation and internal report-link audit at finalization. |
| `SHA256SUMS` | Final review-bundle content hashes, excluding this checksum file itself. |

## Reproduce without overwriting historical outputs

Use a clean disposable checkout of the reviewed SHA, KiCad 9.0.2 with Python pcbnew bindings, and a separate output directory. Copy the review scripts/evidence somewhere writable before rerunning them: these scripts rewrite their own derived evidence, never the source board.

The command JSON files retain the exact original paths, flags and exit codes. Substitute your checkout/output paths. The native checks used:

```sh
kicad-cli sch export netlist --format kicadxml -o fresh.net.xml COPY/hardware/kicad/neuronic.kicad_sch
kicad-cli sch erc --severity-all --exit-code-violations -o fresh-erc.txt COPY/hardware/kicad/neuronic.kicad_sch
kicad-cli pcb drc --schematic-parity --all-track-errors --severity-all --exit-code-violations -o fresh-drc.txt COPY/hardware/kicad/neuronic.kicad_pcb
```

`validate_kicad.py` and BOM preparation write into their checkout, so execute them **only in the disposable copy**. The refill/strict experiment also belongs only in another copy; its exact Python command and category list are in `refill-and-strict-check.json`. No newer-version conversion, routing import or hardware regeneration is required to reproduce this review.

The read-only extraction requires a PCB path and output JSON path. The measurement, plotting, calculation and BOM/pin audit scripts use the evidence beside themselves. The BOM audit expects this directory's repository-relative location. Additional SVG/PDF rasterizations were made only for visual inspection with Inkscape/pdftoppm; native vector exports are retained as authoritative visual evidence.

No bench waveform, simulation trace, recorded EEG, fabrication approval or firmware build log is present, because none was produced. Missing physical evidence must not be inferred from a successful software-check log.

Native KiCad exports are retained byte-for-byte as generated. Their SVG/XML formatting and the copied repository CSV's CRLF endings can trigger git whitespace warnings; these are not CAD or test failures. Authored Markdown/Python and the independent audit CSVs are checked separately.
