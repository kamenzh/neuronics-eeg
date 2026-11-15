# A0.3 routing provenance

The authoritative result is `hardware/kicad/neuronic.kicad_pcb`. These files are
an **incomplete intermediate pass**, not a replacement for that board. Replaying
them would lose later corrections; the current import tool rejects them without
a matching version-bound export manifest.

Critical reference, VCAP, AVDD-star, local DVDD and ground-return copper was
seeded deliberately. Freerouting 2.1.0 supplied a partial local pass. Its input
excludes In1 from routing geometry and excludes plane pours; KiCad retains the
four-layer stack and refills the actual GND planes afterward. This avoids treating
the reserved plane as a signal-routing layer. The pass limit was constrained to
20 in a local RouterSettings class, with Java 21 and a 1 GB heap; the unchanged
upstream JAR hash is recorded in `provenance.json`. Analytics were disabled.

Remaining connections were completed with local geometric path searches and
manual corrections. Redundant router ground traces were removed in favour of
the preserved local vias and continuous In1 plane; dangling and duplicate items
were corrected. Full saved-board schematic-parity DRC, rather than the router's
completion count, establishes the current connection/clearance result.

No third-party router executable is distributed. The CAD remains authoritative;
this is provenance, not a claim that one command regenerates the final layout.
The [independent follow-up](../../../docs/INDEPENDENT_REVIEW_A0_3.md) documents the
changed analog paths and remaining layout limitations.
