> **A0.3 update:** this decision history is supplemented by
> [the review fixes](REVIEW_FIXES_A0_3.md) and [new harness/pinout](POWER_HARNESS_A0_3.md).
> Where the original A0.2 text differs, those current records govern.

# Design decisions — A0.2, 2026-11-15

See [the socket/protection/power review](PROTECTION_POWER_REVIEW_A0_2.md) for the current calculation limits and physical checks.

| Decision | Current choice | Reason and limitation |
| --- | --- | --- |
| Project name | Neuronic | Repository slug can stay `neuronics-eeg` |
| Analog front end | ADS1299IPAG, eight channels | Integrated low-noise PGA and simultaneous ADCs; exact 64-pin contract documented |
| Contacts | 8 recording + REF + BIAS | Ten total contacts, eight measured channels |
| Reference | Direct shared REF_FILTERED to all INxN | MISC1=0x00, SRB2 off; SRB1/SRB2 NC |
| Initial rate | 250 SPS/channel | 27 bytes/frame before host metadata; 500 SPS is a later configurable option |
| Analog power | Unipolar 5 V | Avoid negative supply generation on the first bench board; common-mode must be around mid-supply |
| Digital power | Separate 3.3 V LDO for AFE only | ESP32 must use its own correctly sized supply |
| Battery | Six-AA alkaline candidate, 7.2–10.2V calculation envelope, no onboard charger | Exact pack, switch, connector and fuse require selection; no runtime claim |
| Controller | Owned Waveshare ESP32-S3-Nano via J11 | GPIO/power contract in hardware/interface.json; J11.11 NC |
| Layout | 88 x 90 mm, four copper layers, routed | In1 dedicated GND; In2 crossovers/ground fill; detailed layout and fabricator stack-up review remain |
| Regulators | TPS7A2450DBVR / TPS7A2433DBVR | Fixed 5 V / 3.3 V; 2% additive output-error budget; noise/thermal/startup tests pending |
| Sockets | P1 36619 / 8R003661901F | User-assumed 1.5 mm DIN 42802; derived footprint and physical mating still need verification |
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

KiCad 9.0.2 library symbols are embedded in the sheets and a small set of
standard footprints plus the original derived P1 socket footprint is bundled. Their notices and design-use
exception are in `hardware/licenses/`. The custom ADS1299, BAV199 and TPS7A24 symbols
are explicit pin maps to support inspection, not vendor-validated libraries.

## Sources

- TI ADS1299 datasheet SBAS499C: https://www.ti.com/lit/ds/symlink/ads1299.pdf
  — sections 6, 9, 10.1.1, 10.2, 11 and 12. Pin table includes 100 uF on VCAP1,
  1 uF on VCAP2/4 and 1 uF + 100 nF on VCAP3. Reference bypass is >=10 uF.
- TI EVM guide SLAU443B: https://www.ti.com/lit/ug/slau443b/slau443b.pdf
  — an evaluation reference, explicitly not a patient interface.
- Nexperia BAV199: https://assets.nexperia.com/documents/data-sheet/BAV199.pdf
  — pin 1 A1, pin 2 K2, pin 3 K1/A2; review worst-case leakage and clamp voltage.
- TI TPS7A24 datasheet: https://www.ti.com/lit/ds/symlink/tps7a24.pdf
  — fixed-version pin contract, accuracy budget, capacitance and thermal checks.
- P1 socket drawing: https://catalog.p1tec.com/dash50/36619_dash50.pdf
  — original derived footprint, not a vendor-approved PCB land pattern.
- KiCad getting started: https://docs.kicad.org/9.0/en/getting_started_in_kicad/getting_started_in_kicad.html
- KiCad CLI: https://docs.kicad.org/9.0/en/cli/cli.html

See [A0.2 review](PROTECTION_POWER_REVIEW_A0_2.md), [controller and electrodes](CONTROLLER_AND_ELECTRODES.md) and `hardware/parts.json` for current component sources.
