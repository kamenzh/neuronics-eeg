# A0.5 fabrication candidate

- **Neuronic-A0.5-bare-board-review.zip** contains nine X2 plots, separate plated and nonplated metric Excellon files and shop notes. The four copper layers are identified by L1, L2, L3 and L4 in the X2 headers. The optional KiCad 9.0.2 job summary labeled the inner layers L5/L7, so the delivered archive omits that file. Layer ordering comes from the actual plots.
- **Neuronic-A0.5-hand-assembly.zip** contains the top assembly drawing, component placements, both BOM tables and polarity notes. Placements are in mm as viewed from the top, with Y increasing upward.
- **manifest.json** records the precise board, schematic and archive hashes and individual CAM file hashes. **verify_cam.py** checks the extracted artwork using Gerbonara 1.6.3. Run it with the extracted CAM directory as its only argument. Gerbonara reported a G90 placement warning on the KiCad drill headers. Tool sizes, absolute coordinates, slots and mounting-hole positions parsed correctly.
- **Shop-notes.txt** gives the finished dimensions and open process choices. Gerbonara separately decoded the plots and checked the new resistor nets, via count and J11 pin 2. Supplier CAM acceptance and physical assembly tests remain pending.

[Engineering decisions and limits](../../../docs/A0_5_PROTECTION.md)
