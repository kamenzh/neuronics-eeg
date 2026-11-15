# Routing evidence and current workflow

**Current board: A0.3.** See [A0.3 routing provenance](a0_3/README.md).
The files at this directory's root are historical A0.2 intermediates. Neither
those nor the A0.3 partial pass reconstruct the final saved PCB.

`tools/route_hardware.py export` creates a DSN and source-hash manifest for the
current board. `import` requires that manifest, the matching session base name
and an explicit session SHA-256. It imports/refills in a disposable project copy,
requires full schematic-parity DRC and a reserved In1 plane, then preserves a
pre-import backup before writing the working board. Stale or failing candidates
leave the board unchanged. `fill` refills saved KiCad zones.

```bash
/usr/bin/python3 tools/route_hardware.py export --output-dir /tmp/neuronic-routing-job
# After routing/review, compute the session digest and use the produced manifest:
/usr/bin/python3 tools/route_hardware.py import --manifest /path/job.json --session /path/job.ses --session-sha256 ACTUAL_SHA256
```

The former `seed` action was removed: its old fixed coordinates no longer fit
the revised placement. Modify the authoritative board deliberately in KiCad.
No routing workflow establishes noise performance, fabrication or body approval.

---

# A0.2 routing evidence

The authoritative, manually reviewed copper is `../kicad/neuronic.kicad_pcb`.
The DSN and SES here record an intermediate local routing pass, **not a replacement
for the final PCB**. Re-importing this SES loses later layer and power-return fixes.
Do not rebuild a manufacturing board by blindly re-running generation or routing.

The layout is 88 x 90 mm, four copper layers:

| Layer | Use |
| --- | --- |
| F.Cu | Components, input chains, local power/bypass connections and digital tracks |
| In1.Cu | Dedicated ground plane, no signal tracks |
| In2.Cu | Crossovers and ground fill; not a continuous reference plane |
| B.Cu | Shared reference bus and other signal routes |

Ground pours start at x=69 mm, behind the raw electrode connector terminals.
Digital host routing remains to the right of x=103 mm, within/right of the ADC's
digital side. Channel pads are on its left at x=94.3375 mm. The Nano is offboard
and should be kept away from the electrode/analog region. These geometric checks
are useful constraints, not an EMI or low-noise performance guarantee.

Seeded copper includes the input series links, clamp-to-capacitor links, the
shared negative-input bus, ADC ground fanout and a local DVDD bypass link.
A local Freerouting pass filled remaining paths. Subsequent KiCad edits moved
all routes off In1, resolved the U2 ground connection, rerouted its AVDD feed,
removed sub-0.01 mm router rounding stubs and cleaned connector silkscreen.
Filled zones and full schematic-parity DRC were then checked on the saved PCB.
No exclusions were added. Most small component references are on F.Fab to keep
the silkscreen clear; `pcb-assembly.svg/png` and the CAD identify them for review.

## Router provenance

- [Freerouting v2.1.0](https://github.com/freerouting/freerouting/releases/tag/v2.1.0),
  Java 21; processing was local.
- Upstream JAR SHA-256:
  `2c07d58f75dac03782664081e7a58b41c25400d871a9fcf166a2ea6fe60d5def`.
- Headless run with `--gui.enabled=false -da`, 2 GB Java heap.
- This release did not honor the requested CLI pass limit for the imported job.
  A local compilation of upstream `RouterSettings.java` changed only
  `private transient int stop_pass_no = 999;` to `... = 20;` for the archived pass.
  The JAR itself was unchanged; the patched class preceded it on the classpath.
  No upstream source or executable is redistributed in this repository.
- Source for that one-line change:
  https://github.com/freerouting/freerouting/blob/v2.1.0/src/main/java/app/freerouting/settings/RouterSettings.java
- Router layer hints are not a validation result. Intermediate attempts that
  altered layer activation were discarded. Final layer use is checked against
  actual saved KiCad copper by `tools/check_routing.py`.

The A0.2 workflow used a seed command and an unguarded SES import. Both are
superseded by the version-bound A0.3 workflow described above.

## Still to review physically

Choose a fabricator's actual stack-up and copper weight; confirm socket drills,
enclosure and cable fit, capacitor effective values, local bypass loops and
analog/bias geometry. Measure supply noise, acquisition noise, cable/bias-loop
stability and radio coupling on a bench assembly. The final body-current and
power-off protection review remains open. No Gerber/order release is included.
