# A0.3 connector verification — 2026-11-19

**A0.4 update.** See the [current circuit decisions, dimensions, budgets and checks](A0_4_DESIGN_REVIEW.md). The A0.3 figures below describe the earlier hardware. The Sino-k leads have not been ordered.

**Desk review complete; actual mating and solder fit remain untested.** This is
the step-two follow-up to the [independent November 17 review](reviews/independent-577aad8-2026-11-17/REPORT.md),
IR-06. The saved CAD remains the reviewed `577aad8` board. No footprints, holes,
copper, component selections or fabrication files were changed by this audit.

There are three separate questions: does the electrode plug mate to the jack;
do the jack/header pins fit the finished PCB holes; and can the enclosure and
harness withstand use without transmitting removal loads into solder joints?
A nominal 1.5 mm label answers none of these completely.

## Drawing against saved CAD

All dimensions below are millimetres. CAD drill dimensions are nominal; no
fabricator's finished-hole capability has been accepted. Evidence was extracted
from the actual saved board, rather than inferred from footprint names.

| Item | Selected part and primary drawing | Saved CAD | Conclusion / open evidence |
| --- | --- | --- | --- |
| J1–J10 | P1 `8R003661901F`, family 36619; [36619-50 rev H](https://catalog.p1tec.com/dash50/36619_dash50.pdf), sheet 1; [family catalog](https://catalog.p1tec.com/?FILTER_FCOMPONENT=36619) | One 2.10 round signal hole; two isolated plated 4.20 × 2.10 slots; slot centres 10.16 behind signal pin and ±2.54 across body | Nominal layout agrees with drawing. Existing conditional tolerance calculation is plausible; exact mating lead, finished tolerances and sample fit remain open. |
| J11 | Würth `61301221121`; [drawing](https://www.we-online.com/components/products/datasheet/61301221121.pdf), rev 002.000, page 1 | 2 × 6, 2.54 pitch, twelve 1.00 holes | Drawing recommends 1.10 ±0.15 holes. Current nominal is inside that interval but only 0.05 above its lower bound. Resolve finished-hole minimum / sample fit or revise the footprint before design freeze. |
| SW1 | Würth `61300211121`; [drawing](https://www.we-online.com/components/products/datasheet/61300211121.pdf), rev 003.000, page 1 | 1 × 2, 2.54 pitch, two 1.00 holes | Same 1.10 ±0.15 hole recommendation and open tolerance issue. This is an off-board switch header, not a supplied switch. |
| J12 | JST `B2B-XH-A(LF)(SN)`; [XH drawing](https://www.jst-mfg.com/product/pdf/eng/eXH.pdf), page 2, two-circuit top-entry pattern | 1 × 2, 2.50 pitch, two 1.00 holes | Reference pattern says **1.00 +0.05/−0**, not ±0.05. An undersized finished hole is outside that pattern. JST also qualifies hole advice by PCB material/process. Final fit/process still needs confirmation. |

**Review erratum:** the November 17 report describes J12 as 1.00 ±0.05.
Visual inspection of the manufacturer drawing shows the unilateral tolerance
above. The original report is retained unchanged as historical evidence; this
follow-up corrects the interpretation. No incompatible physical sample has been
observed, so none of these concerns is a demonstrated fit failure.

For J11/SW1, simply noting that 1.00 lies within 0.95–1.25 is insufficient:
a negative fabrication tolerance greater than 0.05 would leave that range.
Preferred design action is to align a reviewed custom footprint with the
manufacturer's 1.10 nominal, unless a documented tolerance/sample assessment
supports keeping 1.00. Any change must include annular-ring, clearance, library
and saved-board consistency checks and fresh DRC; it is not made silently in
this documentation follow-up. Do not apply this recommendation indiscriminately
to J12, which has a different manufacturer's pattern.

## P1 details and limits of the evidence

The P1 family catalog identifies a right-angle 1.5 mm touchproof male contact,
DIN 42802 Type BU. The receiving plastic jack and contact gender are different
descriptions: the lead must have the corresponding mating contact and shroud.
The [Sino-k product listing](https://www.sinokmed.com/products/eeg-cable-10-leadwires-golden-plated-cup-electrodes)
identifies SGE117DN, but does not provide enough connector dimensions to prove
this exact pair mates. Another Sino-k model's “DIN 1.5 mm” description is not
evidence for the supplied lead. Confirm the actual package/model as well.

P1's inch dimensions control its drawing. The signal tail is 0.06 ±0.01 inch
(maximum 1.778 mm). Dummy tails are 0.046 ±0.005 by 0.02 ±0.01 inch
(maximum 1.2954 × 0.762 mm). The existing slot model assumes finished minima
4.10 × 2.00 and bounded relative position error; those are assumptions, not
fabricator commitments. Signal-pin radial clearance at a 2.00 finished minimum
would be only 0.111 mm at the maximum tail diameter, before position error.
See the original review's engineering calculation for the complete conditional
slot model. Physical seating of all three tails together still needs checking.

The board has 8.20 jack pitch, nominal 0.10 between neighbouring courtyards,
and about 0.50 jack-nose overhang beyond the left board edge. Actual lead shrouds,
fingers, enclosure wall and insertion depth must fit that arrangement. P1 lists
2–7 lb extraction force under its test conditions, so mechanical support is
required; this is not an instruction to load-test the bare PCB by pulling it.
P1 says this version is not recommended for wave soldering. Hand assembly still
needs an appropriate heating process and inspection for housing/contact damage.

## Evidence needed from the actual hardware

No purchasing is requested at this stage. When leads become available,
use a socket/header sample only if available. If none is available, record that
physical verification remains pending rather than calling it passed.

| Check | Record | Current status |
| --- | --- | --- |
| Identify supplied lead | Package/model marking; clear front and side photos of plug with a ruler for scale; identify any connector marking | Awaiting Kamen's evidence |
| Identify exact jack | Part marking/package traceability to `8R003661901F` and drawing revision | No sample evidence |
| Disconnected mating | Plug seats normally without forcing, bending pins or bottoming on wrong shroud; stable retention; side photo of seated pair | Not performed |
| Passive contact | With everything unpowered and disconnected from people, meter continuity from cup to the jack signal tail; record lead resistance and whether gentle cable movement interrupts it | Not performed |
| PCB seating | Exact part tails enter the reviewed hole/slot pattern together without bending; body seats as drawn; contact remains sound after suitable soldering | Not performed; requires sample/coupon or board later |
| Enclosure clearance | All ten plugs can be inserted/removed without collision; support/strain relief keeps removal force off solder joints | Not designed/verified |
| J11/SW1 header fit | Exact samples, finished-hole limits, orientation and eventual mating cable dimensions | Open design decision |
| J12 battery harness | XHP-2 mating housing with contacts chosen for the actual wire; pin 1 battery positive, pin 2 GND; continuity and polarity checked before power | Not built/verified |

A ruler photo helps identification; it does not prove submillimetre mating
tolerances. Do not put oversize probes into the recessed contact or force a plug
to fit. Sample checks are disconnected mechanical/electrical checks, not EEG tests.

For J11 use the [A0.3 harness](POWER_HARNESS_A0_3.md): pin 11 is host 3V3 and
pin 12 is GPIO6 interface enable. Pin 12 must not be wired as the old ground pin.
SW1 needs an external switch. Header pitch alone does not establish cable pinout.

## Optional supplier inquiry — prepared, not sent

> Please confirm the connector on Sino-k EEG cup lead set SGE117DN (original
> product variant 42757052924081). Is the supplied lead contact the mating female
> 1.5 mm DIN 42802 contact for a P1 Technologies 36619 / 8R003661901F PCB jack?
> Please provide its connector drawing, shroud diameter/clearance, insertion
> depth and any known mating-part specification. We need confirmation for this
> exact lead model, not another cable family.

Manufacturer selection, process negotiation and a connector coupon order are
deferred until the agreed design stage allows them. Record the required hole/
slot limits now; verify that a later fabrication process actually meets them
before releasing files. No supplier has been contacted and no fit is certified.

## Reproduce the desk audit

Run `/usr/bin/python3 hardware/validation/connector-review-2026-11-19/audit.py`
from the repository. The script reads CAD/BOM, checks all 13 connector footprints,
confirms 107 components / 25 groups / 23 unique MPNs, and verifies the previous
validation input hashes. It never writes the board. The captured output is
[saved-cad.json](../hardware/validation/connector-review-2026-11-19/saved-cad.json).
Manufacturer download URLs and SHA-256 values are in
[sources.json](../hardware/validation/connector-review-2026-11-19/sources.json).
These reproducible geometry checks cannot establish actual connector fit.
