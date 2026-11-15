#!/usr/bin/env python3
"""Fresh KiCad netlist, ERC and full parity DRC; never reuse a failed export.

Exit 1 for violations/unavailable checks. An unrouted checkpoint is expected to
fail. Successful automated checks alone do not establish manufacturing readiness.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--kicad-cli',default=shutil.which('kicad-cli'))
    args=ap.parse_args()
    if not args.kicad_cli:
        ap.error('Pass --kicad-cli with the full path to KiCad 9 kicad-cli.')
    out=ROOT/'hardware/validation';out.mkdir(exist_ok=True)
    project=ROOT/'hardware/kicad/neuronic'
    records=[]
    def run(name,command):
        try:
            p=subprocess.run(command,text=True,capture_output=True)
            record={'check':name,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
        except OSError as exc:
            record={'check':name,'returncode':1,'stdout':'','stderr':str(exc)}
        records.append(record)
        print(f"{name}: exit {record['returncode']}")
        if name in ('connectivity','board parity'):print(record['stdout'].strip())
        return record['returncode']
    # Delete old downstream results before attempting export, even if CLI fails.
    for name in ['neuronic.net.xml','connectivity-checks.json','board-net-checks.json','erc.txt','drc.txt','cli-checks.json']:
        (out/name).unlink(missing_ok=True)
    cli=args.kicad_cli
    run('version',[cli,'version'])
    version=records[-1]['stdout'].strip()
    exported=run('netlist',[cli,'sch','export','netlist','--format','kicadxml','-o',str(out/'neuronic.net.xml'),str(project.with_suffix('.kicad_sch'))])==0
    if exported and (out/'neuronic.net.xml').is_file():
        run('connectivity',[sys.executable,str(ROOT/'tools/check_design.py')])
        run('board parity',[sys.executable,str(ROOT/'tools/check_board.py')])
    else:
        (out/'neuronic.net.xml').unlink(missing_ok=True)
        for name in ['connectivity','board parity']:
            records.append({'check':name,'returncode':1,'status':'NOT_RUN','reason':'Fresh netlist export failed'})
    run('ERC',[cli,'sch','erc','--exit-code-violations','-o',str(out/'erc.txt'),str(project.with_suffix('.kicad_sch'))])
    run('DRC',[cli,'pcb','drc','--schematic-parity','--exit-code-violations','-o',str(out/'drc.txt'),str(project.with_suffix('.kicad_pcb'))])
    paths=sorted(p for p in (ROOT/'hardware/kicad').rglob('*') if p.is_file() and (p.suffix in {'.kicad_sch','.kicad_pcb','.kicad_pro','.kicad_sym','.kicad_mod'} or p.name in {'fp-lib-table','sym-lib-table'}))+[ROOT/'hardware/design.json',ROOT/'hardware/interface.json',ROOT/'hardware/parts.json']
    paths+=sorted((ROOT/'tools').glob('*.py'))+sorted((ROOT/'tests').glob('*.py'))
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
    passed=all(r['returncode']==0 for r in records)
    (out/'cli-checks.json').write_text(json.dumps({'kicad_version':version,'input_sha256':hashes,'results':records,'automated_checks_passed':passed,'manufacture_ready':False,'scope':'Automated checks only. Analog/body review and physical tests are separate requirements.'},indent=2)+'\n')
    return 0 if passed else 1

if __name__=='__main__':sys.exit(main())
