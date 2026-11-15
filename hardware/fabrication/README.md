# Manufacturing release gate — A0.3

The current PCB is routed, but **no order-ready release is included**. The new
socket slots and component choices remain conditional on physical fit and the
chosen fabricator. See [the roadmap](../../docs/NEXT_STEPS.md).

The intended purchase is **bare boards for hand assembly**. It is not an assembly
order. The owned Nano and electrode set are separate from the PCB BOM. No order,
payment, fabrication submission or delivered quote has been made here.

Before release:

- Confirm a real electrode/socket sample and coupon/solder fit.
- Select the actual four-layer stack-up and soldermask/copper process. Current
  design rules use 0.15 mm minimum tracks, 0.20 mm clearance, 0.30 mm via drills,
  and 0.50 mm edge clearance; this is not a named fabrication qualification.
- Obtain acceptance of 4.20 × 2.10 mm plated dummy slots and 2.10 mm signal holes,
  including finished size and positional tolerances. Dummy slots have no net.
- Resolve remaining design-review comments and exact BOM/procurement details.
- Freeze the source revision; refill zones; run fresh ERC and full parity DRC.
- Export all four copper layers, both mask layers, required silk, outline,
  Excellon PTH/NPTH drill/slots, exact MPN BOM and assembly drawing. Generate a
  placement file only if the chosen assembly process needs it.
- Inspect those exports independently for missing layers, mirrored numbering,
  omitted slots, drills, annular rings, mask bridges and hand-solder access.
- Compare delivered board-only quotes to Bulgaria, including shipping and tax.

A later bench-only fabrication release must still say **no body connection**.
The repository's current readiness flags deliberately remain false.
