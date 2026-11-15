# Candidate parts — not an order release

`bom-review.csv` lists each of the 91 PCB components. `bom-candidates.csv` groups
them into 22 exact candidate MPNs with quantities, packages and manufacturer
sources. `hardware/parts.json` is the editable catalog; the generator applies it
to the schematic and BOM. Candidate selection is not stock or price verification.

The owned Nano and Sino-k electrode set cost nothing additional to reuse and
are off-board, so neither is included in the PCB component count. Do not buy
another controller or a second ADS1299. ADS1299IPAG and ADS1299IPAGR use the same
PAG package; the R suffix is reel packaging. Buy one genuine eight-channel device
from a traceable supplier when the design/order list is frozen.

J1–J10 are bench headers and DO NOT mate to the electrode plugs. Their replacement
sockets remain unresolved. SW1's BOM item is a header for an external switch, not
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
