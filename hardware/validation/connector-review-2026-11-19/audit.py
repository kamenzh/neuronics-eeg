#!/usr/bin/env python3
"""Read saved CAD/BOM; print evidence. Never modify or regenerate the board.

Run from any directory using KiCad's Python:
  /usr/bin/python3 hardware/validation/connector-review-2026-11-19/audit.py
This checks recorded geometry, not connector mating or physical tolerances.
"""
import csv
import hashlib
import json
from pathlib import Path

import pcbnew

ROOT = Path(__file__).resolve().parents[3]
BOARD = ROOT / 'hardware/kicad/neuronic.kicad_pcb'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def xy(vector):
    return [round(pcbnew.ToMM(vector.x), 6), round(pcbnew.ToMM(vector.y), 6)]


board_hash = sha(BOARD)
board = pcbnew.LoadBoard(str(BOARD))
footprints = {f.GetReference(): f for f in board.GetFootprints()}
refs = [f'J{i}' for i in range(1, 13)] + ['SW1']
connectors = {}
for ref in refs:
    fp = footprints[ref]
    connectors[ref] = {
        'footprint': str(fp.GetFPID().GetLibItemName()),
        'position_mm': xy(fp.GetPosition()),
        'rotation_degrees': fp.GetOrientationDegrees(),
        'pads': sorted([
            {'number': p.GetNumber(), 'net': p.GetNetname(),
             'position_mm': xy(p.GetPosition()), 'copper_mm': xy(p.GetSize()),
             'drill_mm': xy(p.GetDrillSize())}
            for p in fp.Pads()
        ], key=lambda p: (p['number'], p['position_mm'])),
    }
for ref in refs[:10]:
    pads = connectors[ref]['pads']
    assert len(pads) == 3, ref
    assert [p['drill_mm'] for p in pads] == [[4.2, 2.1], [4.2, 2.1], [2.1, 2.1]], ref
    assert all(p['net'] == '' for p in pads if p['number'] == ''), ref
    assert [p['number'] for p in pads] == ['', '', '1'], ref
socket_y = sorted(connectors[r]['position_mm'][1] for r in refs[:10])
pitch = [round(b - a, 6) for a, b in zip(socket_y, socket_y[1:])]
assert pitch == [8.2] * 9
for ref, count in [('J11', 12), ('J12', 2), ('SW1', 2)]:
    pads = connectors[ref]['pads']
    assert len(pads) == count
    assert all(p['drill_mm'] == [1.0, 1.0] for p in pads)

with (ROOT / 'hardware/bom/bom-review.csv').open() as f:
    components = list(csv.DictReader(f))
with (ROOT / 'hardware/bom/bom-candidates.csv').open() as f:
    groups = list(csv.DictReader(f))
mpns = {g['Candidate_MPN'] for g in groups}
assert len(components) == sum(int(g['Quantity']) for g in groups) == 107
assert len(groups) == 25 and len(mpns) == 23
by_ref = {c['Reference']: c for c in components}
assert len(by_ref) == 107
assert set(by_ref) == {r for r in footprints if not r.startswith('H')}
expected = {**{r: '8R003661901F' for r in refs[:10]},
            'J11': '61301221121', 'J12': 'B2B-XH-A(LF)(SN)', 'SW1': '61300211121'}
for ref, mpn in expected.items():
    assert by_ref[ref]['Proposed_MPN'] == mpn, ref
    connectors[ref]['candidate_mpn'] = mpn

checks = json.loads((ROOT / 'hardware/validation/cli-checks.json').read_text())
hashes = {p: sha(ROOT / p) for p in checks['input_sha256']}
assert hashes == checks['input_sha256'], 'Previous validation inputs changed'
assert sha(BOARD) == board_hash, 'Board changed during read-only audit'
print(json.dumps({
    'scope': 'Saved-CAD geometry and BOM audit; physical fit NOT tested',
    'review_date': '2026-11-19',
    'cad_checkpoint': '577aad8a8dee0c60e3b7e949f6b8f7cf200fe180',
    'pcb_sha256': board_hash,
    'previous_validation_input_hashes_match': True,
    'previous_validation_input_count': len(hashes),
    'bom': {'components': len(components), 'groups': len(groups), 'unique_mpns': len(mpns)},
    'socket_pitch_mm': pitch,
    'connectors': connectors,
}, indent=2))
