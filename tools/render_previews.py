#!/usr/bin/env python3
"""Export current KiCad SVGs and PNG previews using KiCad 9 and Inkscape."""
import subprocess
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/validation'
with tempfile.TemporaryDirectory() as temp:
    subprocess.run(['kicad-cli','sch','export','svg','-o',temp,str(ROOT/'hardware/kicad/neuronic.kicad_sch')],check=True)
    paths=sorted(Path(temp).glob('*.svg'))
    if len(paths)!=3:raise ValueError(f'Expected 3 sheets, got {paths}')
    for path in paths:
        dest='core' if path.stem=='neuronic' else 'inputs' if 'Input' in path.stem else 'power' if 'Power' in path.stem else None
        if dest is None:raise ValueError(path.name)
        svg=OUT/f'schematics/{dest}.svg';svg.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
        subprocess.run(['inkscape',str(svg),'--export-type=png','--export-width=2400','--export-filename='+str(svg.with_suffix('.png'))],check=True)
for name,layers in [('pcb-routed','F.Cu,F.Silkscreen,Edge.Cuts'),('pcb-back','B.Cu,Edge.Cuts'),('pcb-inner2','In2.Cu,Edge.Cuts'),('pcb-assembly','F.Fab,Edge.Cuts')]:
    svg=OUT/(name+'.svg')
    subprocess.run(['kicad-cli','pcb','export','svg','--mode-single','--layers',layers,'--fit-page-to-board','--exclude-drawing-sheet','-o',str(svg),str(ROOT/'hardware/kicad/neuronic.kicad_pcb')],check=True)
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    subprocess.run(['inkscape',str(svg),'--export-type=png','--export-width=1600','--export-background=#182334','--export-background-opacity=1','--export-filename='+str(svg.with_suffix('.png'))],check=True)
print('Rendered 3 schematic sheets, routed copper and assembly previews')
