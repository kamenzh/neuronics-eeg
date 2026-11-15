#!/usr/bin/env python3
"""Export a version-bound routing job, validate an SES in a copy, or refill zones.

An import requires the original board/dependencies, DSN, session digest and
matching base_design. Failed validation leaves the working PCB untouched.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
import pcbnew as k
ROOT=Path(__file__).resolve().parents[1]
PCB=ROOT/'hardware/kicad/neuronic.kicad_pcb'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dependencies(root):
    return sorted(p for p in (root/'hardware/kicad').rglob('*') if p.is_file() and
                  (p.suffix in {'.kicad_sch','.kicad_pro','.kicad_sym','.kicad_mod'} or
                   p.name in {'fp-lib-table','sym-lib-table'}))

def verify_import_inputs(root,board,session,manifest,session_sha256):
    data=json.loads(manifest.read_text())
    if data.get('schema')!=1:raise ValueError('Unknown routing manifest schema')
    if digest(board)!=data['board_sha256']:raise ValueError('Source board changed since export; refusing stale import')
    actual={str(p.relative_to(root)):digest(p) for p in dependencies(root)}
    if actual!=data['dependency_sha256']:raise ValueError('Schematic, libraries or rules changed since export')
    dsn=manifest.parent/data['dsn_file']
    if digest(dsn)!=data['dsn_sha256']:raise ValueError('DSN changed since export')
    if digest(session)!=session_sha256:raise ValueError('Session SHA-256 does not match reviewed file')
    match=re.search(r'\(base_design\s+(?:"([^"]+)"|([^\s)]+))\)',session.read_text())
    if not match or (match[1] or match[2])!=data['design_id']:
        raise ValueError('Session belongs to a different routing export')
    return data

def import_checked(root,board,session,manifest,session_sha256,cli='kicad-cli'):
    verify_import_inputs(root,board,session,manifest,session_sha256)
    original=board.read_bytes()
    with tempfile.TemporaryDirectory(prefix='neuronic-route-') as tmp:
        project=Path(tmp)/'kicad';shutil.copytree(board.parent,project)
        candidate=project/board.name
        b=k.LoadBoard(str(candidate))
        if not k.ImportSpecctraSES(b,str(session.resolve())):raise RuntimeError('SES import failed')
        b.BuildConnectivity();k.ZONE_FILLER(b).Fill(b.Zones());k.SaveBoard(str(candidate),b)
        report=Path(tmp)/'drc.json'
        result=subprocess.run([cli,'pcb','drc','--schematic-parity','--exit-code-violations',
                               '--format','json','-o',str(report),str(candidate)],capture_output=True,text=True)
        if result.returncode!=0:
            raise RuntimeError('Candidate failed full DRC; original PCB preserved.\n'+result.stdout+result.stderr)
        checks=json.loads(report.read_text())
        if any(checks.get(key,[]) for key in ['violations','unconnected_items','schematic_parity']):
            raise RuntimeError('Candidate has DRC findings; original PCB preserved')
        if any(t.GetLayer()==k.In1_Cu for t in b.GetTracks() if type(t)!=k.PCB_VIA):
            raise RuntimeError('Candidate routes on reserved In1 ground layer; original PCB preserved')
        # Detect a simultaneous edit before the only write to the working board.
        if board.read_bytes()!=original:raise RuntimeError('Working board changed during validation')
        backup=board.with_name(board.name+'.pre-import-'+hashlib.sha256(original).hexdigest()[:12]+'.bak')
        if not backup.exists():backup.write_bytes(original)
        board.write_bytes(candidate.read_bytes())
        print(f'Imported after clean parity DRC; backup: {backup}')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action',choices=['export','import','fill'])
    ap.add_argument('--output-dir',type=Path,default=ROOT/'hardware/routing/jobs')
    ap.add_argument('--session',type=Path);ap.add_argument('--manifest',type=Path)
    ap.add_argument('--session-sha256');args=ap.parse_args()
    if args.action=='import':
        if not all([args.session,args.manifest,args.session_sha256]):
            ap.error('import requires --session, --manifest and --session-sha256')
        import_checked(ROOT,PCB,args.session,args.manifest,args.session_sha256)
        return
    b=k.LoadBoard(str(PCB))
    if args.action=='fill':
        b.BuildConnectivity();k.ZONE_FILLER(b).Fill(b.Zones());k.SaveBoard(str(PCB),b)
        return
    args.output_dir.mkdir(parents=True,exist_ok=True)
    board_hash=digest(PCB);design_id='neuronic_'+board_hash[:16]
    dsn=args.output_dir/(design_id+'.dsn');manifest=dsn.with_suffix('.json')
    if dsn.exists() or manifest.exists():raise FileExistsError('Routing job already exists; choose a fresh output directory')
    if not k.ExportSpecctraDSN(b,str(dsn)):raise RuntimeError('DSN export failed')
    data={'schema':1,'design_id':design_id,'board_sha256':board_hash,
          'dependency_sha256':{str(p.relative_to(ROOT)):digest(p) for p in dependencies(ROOT)},
          'dsn_file':dsn.name,'dsn_sha256':digest(dsn),
          'note':'Keep this job unchanged. Review session SHA-256 before import. No manufacture approval.'}
    manifest.write_text(json.dumps(data,indent=2)+'\n');print(manifest)

if __name__=='__main__':main()
