# Independent A0.3 follow-up — 2026-11-15

A separate AI reviewer rechecked the revised circuit and selected saved-board
geometry, read-only. **No new blocking copper defect was found within that scope.**
This is not a qualified human engineering review, a hardware test or a
manufacturing/body-use approval. The latter remain false.

The reviewed PCB SHA-256 is
`56e3c25c3cbefbf489e86c24db1670b0620a263d7c0c5adaea14d672e3de33b5`.
It contains 1,181 track segments, 123 vias and two filled GND zones. The reviewer
made no repository changes. Point-to-point/return measurements are preserved in
[the A0.3 evidence directory](../hardware/validation/independent-a0_3/).

## Circuit checks

The reviewer compared a fresh 107-component KiCad export with the actual buffer,
header, pull and reference-capacitor pads. TXU0304 PW14 supply pins, six forward
and two return signal directions, OE and NC pins agree with TI's table. Each
buffer supply reaches its 100 nF capacitor in 2.552 mm without transitions.
The static 10 kΩ LOW-level calculation is sound under its leakage assumptions.
The selected parts still require physical power-order/brownout testing.

The KEMET curve supports using 25% bias loss as a conservative typical allowance
near 4.5 V. The C29+C42 arithmetic is 20.44845 µF; it is an **estimate**, with AC,
aging and operating-condition assumptions, not a guaranteed capacitance floor.
The operating-capacitance/startup gate stays open.

All ten socket footprints have the final 4.2 × 2.1 mm isolated dummy slots,
5.0 × 2.9 mm copper pads and 2.1 mm signal holes. The conditional capsule-corner
calculation gives 0.7850 mm against 1.0 mm available, and signal radial clearance
is 0.111 mm at the stated minimum hole. Nominal slot length now meets JLCPCB's
published 2:1 guidance. Physical mating, solder practicality and actual
fabricator tolerances still require verification.

## Measured routing

Lengths below include approximate pad-center distances and exclude via barrels.
They are geometric measurements, not noise or impedance predictions.

| Connection | A0.3 length | Layer transitions |
| --- | --- | --- |
| U1.24 → C29 reference bulk | 2.851 mm | 0 |
| U1.24 → C30 reference bypass | 4.954 mm | 0 |
| U1.24 → C42 additional bulk | 12.112 mm | 0 |
| U1.28 → C24, VCAP1 | 6.951 mm | 0 |
| U1.30 → C25, VCAP2 | 3.566 mm | 0 |
| U1.55 → C26 / C27, VCAP3 | 3.420 / 5.620 mm | 0 / 0 |
| U1.26 → C28, VCAP4 | 5.553 mm | 0 |
| U1.54 → C36, AVDD1 | 3.176 mm | 0 |
| U1.59 → C34 | 3.586 mm | 0 |
| U1.50 → C40, DVDD | 5.282 mm | 0 |

C29's old route was 14.400 mm with two transitions; C30's was 7.786 mm with two.
The revised AVDD1 branch connects to the remaining AVDD copper only inside the
C37.1 star pad. Removing that pad from the connectivity graph leaves only C36.1
and U1.54 downstream; a trace-width overlap check agrees. C37→C36 is 12.214 mm.
No unintended other load was found on that branch.

Capacitor ground stubs reach their first vias in about 0.9–1.2 mm; relevant U1
escapes are 1.66–1.89 mm. Straight-line samples between selected return vias
remained in filled In1.Cu. This supports a continuous plane connection, not
minimum inductance or proven analog performance.

## Remaining criticism

1. **Physical socket and fabrication acceptance still block a board release.**
   A drawing-based tolerance model cannot prove the user's actual lead/socket fit.
2. **Reference and regulator operating values/startup remain unmeasured.** The
   new nominal capacitance and graph estimate reduce uncertainty; they do not
   replace effective-capacitance and startup measurements.
3. **Some loops still deserve bench scrutiny.** C24/C28 return-via separations
   from the selected U1.25 via remain about 11.75/9.86 mm. In1 stays continuous,
   but do not describe every local loop as minimal.
4. **Series resistor placement is not uniformly close to the buffers.** Buffer
   SCLK→R41 is 11.257 mm and START→R45 is 22.035 mm. This is a layout/damping
   optimization and scope-test item, not an established functional failure.
5. **Firmware and system tests are still missing.** Repeat supply sequencing,
   readback, input-short noise, radio, CMRR, bias-load and fault tests before
   claiming a working acquisition system. Body-use protection remains separate.

A stale 3.20 mm slot note and an obsolete resistor source URL were also reported;
the catalog/generator metadata were corrected after review. The copper hash
above identifies the board the reviewer measured.

Primary sources: [TI ADS1299](https://www.ti.com/lit/ds/symlink/ads1299.pdf),
[TI TXU0304](https://www.ti.com/lit/ds/symlink/txu0304.pdf),
[KEMET exact sheet](https://search.kemet.com/component-documentation/download/specsheet/C1210C226K3RACTU),
[P1 drawing](https://catalog.p1tec.com/dash50/36619_dash50.pdf),
[JLCPCB slot guidance](https://jlcpcb.com/help/article/instructions-for-ordering).
