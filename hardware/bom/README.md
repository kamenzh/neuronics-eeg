# Candidate parts — not an order release

`bom-review.csv` lists each of the **110 electrical PCB components** (the four
mounting-hole footprints are not purchased components). `bom-candidates.csv`
contains **29 catalog groups and 27 distinct candidate MPNs**: some groups use
the same MPN for different circuit roles. It records quantities, packages and manufacturer
sources. `hardware/parts.json` is the editable catalog; the generator applies it
to the schematic and BOM. Candidate selection is not stock or price verification.

The Nano is already owned. The planned Sino-k leads have not been ordered. Both are off-board, so neither is included in the PCB component count. Do not buy
another controller or a second ADS1299. ADS1299IPAG and ADS1299IPAGR use the same
PAG package; the R suffix is reel packaging. Buy one genuine eight-channel device
from a traceable supplier when the design/order list is frozen.

J1–J10 are ten selected **P1 36619 / 8R003661901F** right-angle touchproof jacks,
not the superseded bench headers. Mating with Kamen's actual Sino-k leads is
**not yet verified**. See the [connector drawing/fit audit](../../docs/CONNECTOR_VERIFICATION_A0_3.md),
and the [A0.4 dimensions](../../docs/A0_4_DESIGN_REVIEW.md), including finished-hole requirements for J11, SW1 and J12.
SW1's BOM item is a header for an external switch, not
a switch. The battery holder/cells, Nano branch protection, switches, cables,
JST mating housing/contacts, enclosure, paste/gel, soldering consumables and PCB
fabrication/delivery are also outside this PCB BOM and must be budgeted separately.

Self-assembly remains the plan: order bare boards once released, buy the reviewed
components and solder them. The 64-pin ADS1299 has 0.5mm lead pitch; practice on a
cheap fine-pitch board first and use magnification, flux and inspection. Do not
assume a bare-board order includes components or assembly. No order has been placed.

Before ordering: confirm every footprint and polarity against its drawing,
finish effective-capacitance/protection review, check genuine part stock, request
cut tape rather than a whole reel, allow a few spare inexpensive passives, and
compare total delivered cost including tax/shipping. Prices from earlier planning
are not quotes and are not reproduced as current facts here.

Updated 2026-11-19 against both CSVs and saved CAD; this closes the stale prose
finding IR-10 in the [November 17 review](../../docs/reviews/independent-577aad8-2026-11-17/REPORT.md).
It does not close procurement or physical fit. At Kamen's request, fabrication
files, manufacturer selection and parts ordering wait until design confirmation.
