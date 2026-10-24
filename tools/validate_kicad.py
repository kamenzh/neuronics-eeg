#!/usr/bin/env python3
"""Run KiCad validation on Windows/Linux. KiCad CLI >=8 required for ERC/DRC.

Always writes every available check; fails when a release check is unavailable
or when KiCad reports an error. Never suppresses unconnected items.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument('--kicad-cli',default=shutil.which('kicad-cli'))
args=ap.parse_args()
if not args.kicad_cli:
    raise SystemExit('Pass --kicad-cli with the full path to kicad-cli.exe (KiCad 8 or newer).')
cli=args.kicad_cli
out=ROOT/'hardware/validation';out.mkdir(exist_ok=True)
project=ROOT/'hardware/kicad/neuronic'
version=subprocess.check_output([cli,'version'],text=True).strip()
records=[]
def run(name,command):
    p=subprocess.run([cli,*command],text=True,capture_output=True)
    records.append({'check':name,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    print(f'{name}: exit {p.returncode}')
    return p.returncode
run('netlist',['sch','export','netlist','--format','kicadxml','-o',str(out/'neuronic.net.xml'),str(project.with_suffix('.kicad_sch'))])
netcheck=subprocess.run([sys.executable,str(ROOT/'tools/check_design.py')])
major=int(version.split('.')[0])
if major>=8:
    run('ERC',['sch','erc','--exit-code-violations','-o',str(out/'erc.txt'),str(project.with_suffix('.kicad_sch'))])
    run('DRC',['pcb','drc','--schematic-parity','--exit-code-violations','-o',str(out/'drc.txt'),str(project.with_suffix('.kicad_pcb'))])
else:
    records.append({'check':'ERC/DRC CLI','returncode':1,'stderr':'KiCad >=8 required. Use GUI ERC; pcbnew DRC exists separately for KiCad 7.'})
status={'kicad_version':version,'results':records,'release_passed':not netcheck.returncode and all(x['returncode']==0 for x in records)}
(out/'cli-checks.json').write_text(json.dumps(status,indent=2)+'\n')
sys.exit(0 if status['release_passed'] else 1)
