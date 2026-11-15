# A0.3 — implemented fixes and remaining release gates

**A0.3 contains real schematic, footprint and routed-copper changes.** It remains
an unmanufactured bench-development design. Do not order it or connect it to a
person based on a passing software check.

This follows the [independent A0.2 review](INDEPENDENT_REVIEW_A0_2.md). The A0.2
report and its evidence remain historical; they have not been rewritten to claim
that the new work existed earlier. See the current
[validation status](../hardware/validation/STATUS.md) for actual checks.

| Finding | A0.3 action | Remaining evidence |
| --- | --- | --- |
| IR-01, local analog layout | Repositioned reference/VCAP/supply capacitors; local top-layer bypass connections; separate AVDD1 supply branch; nearby GND vias | Independent geometry review completed; measured startup/noise/return behavior still pending |
| IR-02, socket tolerances | 2.10 mm signal hole; 4.20 × 2.10 mm isolated plated dummy slots; enlarged copper pads | Real cable/socket mating, coupon/solder fit, finished-hole and position tolerance acceptance |
| IR-03, effective capacitance | C29 changed to a 1210 KEMET part; C42 fitted in parallel; recorded typical-curve estimate; C21 increased to 4.7 µF | Guaranteed operating-value evidence or measurement, VREF/VCAP/LDO startup and stability |
| IR-04, weak default pulls | R30–R35 changed from 100 kΩ to 10 kΩ | Verify default logic states on hardware |
| IR-05, direct GPIO backfeed | Two TXU0304PWR buffers, default-disabled OE, separate supply ports, eight 33 Ω output resistors; documented harness candidate | Power-order/brownout tests and final harness parts; analog-clamp injection remains unresolved |
| IR-06, reference/filter imbalance | Expanded the sensitivity model and specified a bench comparison | Measured CMRR with unequal source impedances and real cable loading; no performance closure claimed |
| IR-07, clamps/bias/body faults | Preserve disabled bias/lead-off for initial tests; explicit bench and body-use gates | Bias stability, fault/rail injection, leakage and qualified system review |
| IR-08, acquisition firmware | Updated the implementation contract for the revised hardware | Firmware/receiver implementation, build and physical acquisition tests remain pending |
| IR-09, workflow hazards | Export manifest, source/DSN/session checks, candidate-copy DRC, backup before accepted import; tool/test hashes | Focused failure-path regression tests and normal CAD checks |

## Interface change

U4 and U5 are TI TXU0304PWR in hand-assemblable TSSOP-14 packages. Their A ports
use Nano HOST_3V3, B ports use AFE DVDD_3V3. Six signals go toward the ADC and
MISO/DRDY return to the Nano. R49 holds OE low until GPIO6 enables it. These are
power-off tolerant logic buffers, **not galvanic isolation**. The board still has
common ground and analog input-clamp paths into AVDD.

**Rewire J11:** pin 11 = Nano 3V3; pin 12 = GPIO6/D3 enable. Pin 12 was GND in A0.2.
The full pinout and power sequence are in [POWER_HARNESS_A0_3.md](POWER_HARNESS_A0_3.md).

For the default control inputs, 10 kΩ × 1.01 × 12 µA = **0.1212 V**, below the
0.6468 V LOW ceiling at DVDD = 3.234 V. The 12 µA budget combines ADC input and
buffer tri-state leakage. Six HIGH pulls consume up to about **2.04 mA** at
3.366 V with −1% resistance; this belongs in the 10 mA digital budget. Transient
logic levels and unpowered states still need measurement.

## Reference capacitor estimate

C29 and C42 are both **KEMET C1210C226K3RACTU**, 22 µF / 25 V / ±10% / X7R / 1210.
Both are fitted, giving 44 µF nominal; C30 remains the local 100 nF bypass.
The exact KEMET sheet's typical DC-bias graph was inspected at the 4.5 V operating
point. The following deliberately conservative allowances give an **estimate**:

`44 µF × 0.75 bias × 0.90 tolerance × 0.85 temperature × 0.90 aging × 0.90 AC = 20.44845 µF`

The curve is typical, and the aging/AC factors are engineering assumptions.
This is **not a manufacturer-guaranteed 20.45 µF minimum**. It provides margin
against the 10 µF reference requirement, while leaving effective-capacitance,
settling and startup qualification open. The aging allowance exceeds the
3%/decade-hour sheet rate through approximately ten years from the 48-hour
reference point; actual thermal history and the extra AC allowance need review.
Do not infer Class II capacitance from voltage rating alone.

C21 is now 4.7 µF. Direct analog-rail capacitance is 20.8 µF nominal, with a
26.312 µF positive tolerance/temperature estimate. Digital-rail capacitance is
7.0 µF nominal. Reference and VCAP capacitors are not counted as direct LDO load
capacitors. Effective minimum capacitance and regulator stability remain physical
checks. C24's 100 µF tantalum polarity and VCAP1 settling requirement are unchanged.

## Socket tolerance worksheet

These are conditional engineering calculations from P1 drawing 36619-50 rev H,
not measured production dimensions. The two dummy legs stay electrically
isolated. Socket pitch remains 8.20 mm.

| Quantity | A0.3 value / assumption |
| --- | --- |
| Signal pad / finished hole | 3.10 mm copper / 2.10 mm hole |
| Dummy pad / finished slot | 5.00 × 2.90 mm copper / 4.20 × 2.10 mm slot, long axis X |
| Assumed minimum finished slot | 4.10 × 2.00 mm (−0.10 mm size allowance) |
| Assumed relative hole position error | 0.15 mm per axis, equivalent to two independent ±0.075 mm positions |
| Drawing leg position allowance | ±0.254 mm per axis |
| Maximum rectangular dummy section | 1.2954 × 0.762 mm |
| Worst corner relative to slot centre | (1.0517, 0.7850) mm |
| Slot capsule end-centre / radius | 1.05 mm / 1.00 mm |
| Required corner radius | sqrt(0.0017² + 0.785²) = 0.785002 mm < 1.00 mm |
| Minimum signal radial clearance | (2.00 − 1.778)/2 = 0.111 mm |

The 4.20/2.10 nominal aspect ratio also meets JLCPCB's published 2:1 plated-slot
length guidance. This does not establish its finished-slot/position tolerances
or acceptance of the whole board. Obtain actual fabrication acceptance and test
a socket/coupon before ordering the main PCB. Check solder fill/mechanical
strength in the elongated slots and support the socket edge during insertion.
An electrode plug fitting the jack does not prove the jack's PCB legs fit.

See the [separate follow-up review](INDEPENDENT_REVIEW_A0_3.md) for measured route
lengths and remaining layout criticism, including buffer resistor placement.

## Scope of this checkpoint

No fabricated PCB, electrical measurement, firmware build, noise/EMC test or
human safety approval is represented here. The CAD/BOM are reviewable and the
readiness flags stay false. A0.3 adds two small interface ICs and passives; an
updated delivered BOM/board quote is still needed. The ADS1299 remains one
8-channel device, and the owned Nano remains the controller.

## Primary references

- [TI ADS1299](https://www.ti.com/lit/ds/symlink/ads1299.pdf).
- [TI TXU0304](https://www.ti.com/lit/ds/symlink/txu0304.pdf), Table 6-1 and power-off electrical conditions.
- [TI TPS7A24](https://www.ti.com/lit/ds/symlink/tps7a24.pdf).
- [Exact KEMET reference-capacitor sheet](https://search.kemet.com/component-documentation/download/specsheet/C1210C226K3RACTU).
- [P1 socket drawing](https://catalog.p1tec.com/dash50/36619_dash50.pdf).
- [JLCPCB ordering/slot guidance](https://jlcpcb.com/help/article/instructions-for-ordering).
