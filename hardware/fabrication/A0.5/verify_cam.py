"""Inspect an extracted Neuronic A0.5 CAM package using Gerbonara 1.6.3."""
from collections import Counter
from pathlib import Path
import sys

from gerbonara import GerberFile, ExcellonFile
from gerbonara.graphic_objects import Flash, Line

directory = Path(sys.argv[1])
layers = {p.stem.removeprefix('neuronic-'): GerberFile.open(p) for p in directory.glob('*.gbr')}
expected = {'F_Cu': 'Copper,L1,Top', 'In1_Cu': 'Copper,L2,Inr', 'In2_Cu': 'Copper,L3,Inr',
            'B_Cu': 'Copper,L4,Bot', 'F_Mask': 'Soldermask,Top', 'B_Mask': 'Soldermask,Bot',
            'F_Silkscreen': 'Legend,Top', 'B_Silkscreen': 'Legend,Bot', 'Edge_Cuts': 'Profile,NP'}
assert set(layers) == set(expected)
for name, plot in layers.items():
    assert ','.join(plot.file_attrs['.FileFunction']) == expected[name]
    assert plot.file_attrs['.ProjectId'][-1] == 'A0.5'
    assert plot.file_attrs['.SameCoordinates'] == ('Original',)
    if name.endswith('_Cu'):
        assert any(obj.polarity_dark for obj in plot.objects)
edges = layers['Edge_Cuts'].objects
assert len(edges) == 4 and all(isinstance(e, Line) for e in edges)
corners = {(50,-55),(138,-55),(50,-145),(138,-145)}
assert Counter(p for e in edges for p in [(e.x1,e.y1),(e.x2,e.y2)]) == {p:2 for p in corners}
assert all((e.x1 == e.x2) != (e.y1 == e.y2) for e in edges)
assert len({frozenset(((e.x1,e.y1),(e.x2,e.y2))) for e in edges}) == 4

def drills(plating):
    path = directory / f'neuronic-{plating}.drl'
    assert f',1,4,{plating}' in path.read_text()
    return ExcellonFile.open(path).objects

plated = drills('PTH')
circles = [obj for obj in plated if isinstance(obj, Flash)]
slots = [obj for obj in plated if isinstance(obj, Line)]
assert len(circles)+len(slots) == len(plated)
assert Counter(p.aperture.diameter for p in circles) == {0.3:124, 1.0:2, 1.1:14, 2.1:10}
def at(x, y):
    return (round(x,4), round(y,4))
signals = {at(p.x,p.y) for p in circles if p.aperture.diameter == 2.1}
assert signals == {at(67.026,-61-i*8.2) for i in range(10)}
assert len(slots) == 20
assert {at((s.x1+s.x2)/2,s.y1) for s in slots} == {at(x-10.16,y+dy) for x,y in signals for dy in (-2.54,2.54)}
for s in slots:
    assert s.y1 == s.y2 and s.aperture.diameter == 2.1 and round(abs(s.x1-s.x2)+2.1,4) == 4.2
mounts = drills('NPTH')
assert len(mounts) == 4 and all(isinstance(p,Flash) and p.aperture.diameter == 2.7 for p in mounts)
assert {at(p.x,p.y) for p in mounts} == {(87,-58),(135,-58),(135,-142),(73,-142)}
pads = {p.attrs['.P'][:2]:p for p in layers['F_Cu'].objects if isinstance(p,Flash) and '.P' in p.attrs}
assert {at(p.x,p.y) for p in circles if p.aperture.diameter == 1.1} == {at(p.x,p.y) for (r,n),p in pads.items() if r in ('SW1','J11')}
assert {at(p.x,p.y) for p in circles if p.aperture.diameter == 1} == {at(p.x,p.y) for (r,n),p in pads.items() if r == 'J12'}
mask = {at(p.x,p.y):p for p in layers['F_Mask'].objects if isinstance(p,Flash) and p.polarity_dark}
for pin in range(1,65):
    p = pads[('U1',str(pin))]
    m = mask[at(p.x,p.y)]
    assert m.bounding_box() == p.bounding_box()
for ref,rail in [('R50','AVDD_5V'),('R51','DVDD_3V3'),('R52','AVDD_5V')]:
    assert pads[(ref,'1')].attrs['.N'] == (rail,) and pads[(ref,'2')].attrs['.N'] == ('GND',)
assert pads[('J11','2')].attrs['.N'][0].startswith('unconnected-')
print('Verified 9 X2 plots, layer order L1–L4, closed 88 × 90 mm outline, 150 plated round holes, 20 plated slots, 4 nonplated holes, connector locations, 64 ADC mask openings and R50/R51/R52 and J11 key pad nets.')
