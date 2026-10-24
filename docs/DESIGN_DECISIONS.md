# Design decisions — A0, 2026-10-24

| Decision | Current choice | Reason and limitation |
| --- | --- | --- |
| Project name | Neuronic | Repository slug can stay `neuronics-eeg` |
| Analog front end | ADS1299IPAG, eight channels | Integrated low-noise PGA and simultaneous ADCs; exact 64-pin contract documented |
| Contacts | 8 recording + REF + BIAS | Ten total contacts, eight measured channels |
| Reference | SRB1 shared reference | Enable MISC1 bit 5; unused external N inputs tied to AVDD per unused-input guidance |
| Initial rate | 250 SPS/channel | 27 bytes/frame before host metadata; 500 SPS is a later configurable option |
| Analog power | Unipolar 5 V | Avoid negative supply generation on the first bench board; common-mode must be around mid-supply |
| Digital power | Separate 3.3 V LDO for AFE only | ESP32 must use its own correctly sized supply |
| Battery | External 7-9 V pack, no onboard charger | Exact pack, switch, connector and fuse require selection; no runtime claim |
| Controller | Generic 3.3 V SPI connector | Allows ESP32-S3 initially and Pi/other controllers on the bench |
| Layout | 88 x 80 mm, four copper layers | Initial placement only; stack-up, plane and routing review still required |
| Input filters | 2 x 10 kohm + 1 nF per input/reference | RF pole about 7.96 kHz; does not implement 0.5-40 Hz EEG filtering |
| Clamps | BAV199 candidate rail clamps | Low leakage helps, but forward clamp voltage and fault paths are unresolved |
| Bias | Internal midpoint, 1 M feedback parallel 1.5 nF, 2 x 499 kohm output | Candidate values; stability with electrodes/cables is not validated |
| Training | PC | Acquisition firmware keeps raw samples; models are a later milestone |

## Source discipline

The circuit was drafted from the TI ADS1299 datasheet and standard circuit
functions. No Low-Cost-EEG, OpenBCI or HackEEG source files are included or
represented as KiCad-native conversions. Their different supply topologies
must be accounted for before borrowing any circuitry. Source reuse must carry
the relevant license and attribution; the main repo's existing MIT license
does not relicense third-party design files.

KiCad 7.0.11 library symbols are embedded in the sheets and a small set of
unmodified standard footprints is bundled. Their notices and design-use
exception are in `hardware/licenses/`. The custom ADS1299 and BAV199 symbols
are explicit pin maps to support inspection, not vendor-validated libraries.

## Sources

- TI ADS1299 datasheet SBAS499C: https://www.ti.com/lit/ds/symlink/ads1299.pdf
  — sections 6, 9, 10.1.1, 10.2, 11 and 12. Pin table includes 100 uF on VCAP1,
  1 uF on VCAP2/4 and 1 uF + 100 nF on VCAP3. Reference bypass is >=10 uF.
- TI EVM guide SLAU443B: https://www.ti.com/lit/ug/slau443b/slau443b.pdf
  — an evaluation reference, explicitly not a patient interface.
- Nexperia BAV199: https://assets.nexperia.com/documents/data-sheet/BAV199.pdf
  — pin 1 A1, pin 2 K2, pin 3 K1/A2; review worst-case leakage and clamp voltage.
- Microchip MCP1703A product and datasheet:
  https://www.microchip.com/en-us/product/MCP1703A
  — final regulator choice, footprint and capacitor/thermal requirements must
  be independently confirmed before release.
- KiCad getting started: https://docs.kicad.org/9.0/en/getting_started_in_kicad/getting_started_in_kicad.html
- KiCad CLI: https://docs.kicad.org/9.0/en/cli/cli.html
