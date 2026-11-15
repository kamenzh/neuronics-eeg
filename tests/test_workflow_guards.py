"""Regression coverage for destructive generation and stale-success hazards."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pcbnew as k
ROOT=Path(__file__).resolve().parents[1]

class GeneratorGuards(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'tools').mkdir();(self.root/'hardware/kicad').mkdir(parents=True)
        shutil.copyfile(ROOT/'tools/generate_hardware.py',self.root/'tools/generate_hardware.py')
        shutil.copyfile(ROOT/'hardware/parts.json',self.root/'hardware/parts.json')
        self.schematic=self.root/'hardware/kicad/neuronic.kicad_sch'
        self.schematic.write_text('user edits to preserve')
    def run_generator(self,*flags):
        return subprocess.run([sys.executable,str(self.root/'tools/generate_hardware.py'),*flags],capture_output=True,text=True)
    def test_requires_explicit_overwrite(self):
        result=self.run_generator()
        self.assertNotEqual(result.returncode,0)
        self.assertIn('--overwrite',result.stderr)
        self.assertEqual(self.schematic.read_text(),'user edits to preserve')
    def assert_copper_guard(self,board):
        pcb=self.root/'hardware/kicad/neuronic.kicad_pcb'
        k.SaveBoard(str(pcb),board);before=pcb.read_bytes()
        result=self.run_generator('--board','--overwrite')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Refusing to replace',result.stderr)
        self.assertEqual(pcb.read_bytes(),before)
        self.assertEqual(self.schematic.read_text(),'user edits to preserve')
    def test_preserves_tracks(self):
        b=k.BOARD();t=k.PCB_TRACK(b)
        t.SetStart(k.VECTOR2I(0,0));t.SetEnd(k.VECTOR2I(1000000,0));t.SetWidth(200000);b.Add(t)
        self.assert_copper_guard(b)
    def test_preserves_vias(self):
        b=k.BOARD();v=k.PCB_VIA(b);v.SetPosition(k.VECTOR2I(0,0));v.SetWidth(k.F_Cu,600000);v.SetDrill(300000);b.Add(v)
        self.assert_copper_guard(b)
    def test_preserves_zones(self):
        b=k.BOARD();z=k.ZONE(b);z.SetLayer(k.F_Cu)
        poly=z.Outline();poly.NewOutline()
        for x,y in [(0,0),(2000000,0),(2000000,2000000),(0,2000000)]:poly.Append(x,y)
        b.Add(z);self.assert_copper_guard(b)

class FailedExport(unittest.TestCase):
    def test_failed_export_cannot_reuse_stale_passes(self):
        spec=importlib.util.spec_from_file_location('validate',ROOT/'tools/validate_kicad.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temp:
            module.ROOT=Path(temp);out=module.ROOT/'hardware/validation';out.mkdir(parents=True)
            (module.ROOT/'hardware/kicad').mkdir()
            for name in ['design.json','interface.json','parts.json']:
                (module.ROOT/'hardware'/name).write_text('{}')
            for name in ['neuronic.net.xml','connectivity-checks.json','board-net-checks.json','erc.txt','drc.txt']:
                (out/name).write_text('stale success')
            def fail(command,**kwargs):
                if command[-1]=='version':return subprocess.CompletedProcess(command,0,'9.0.2\n','')
                return subprocess.CompletedProcess(command,2,'','forced export/check failure')
            with patch.object(sys,'argv',['validate','--kicad-cli','fake-cli']),patch.object(subprocess,'run',side_effect=fail):
                self.assertEqual(module.main(),1)
            for name in ['neuronic.net.xml','connectivity-checks.json','board-net-checks.json','erc.txt','drc.txt']:
                self.assertFalse((out/name).exists())
            result=json.loads((out/'cli-checks.json').read_text())
            self.assertFalse(result['automated_checks_passed'])
            self.assertFalse(result['manufacture_ready'])
            self.assertEqual([r['status'] for r in result['results'] if r['check'] in ['connectivity','board parity']],['NOT_RUN','NOT_RUN'])


class RoutingImportGuards(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location('route',ROOT/'tools/route_hardware.py')
        self.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.module)
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.project=self.root/'hardware/kicad';self.project.mkdir(parents=True)
        self.board=self.project/'neuronic.kicad_pcb';k.SaveBoard(str(self.board),k.BOARD())
        (self.project/'neuronic.kicad_sch').write_text('fixture schematic')
        self.session=self.root/'test.ses';self.session.write_text('(session test (base_design test))')
        self.dsn=self.root/'test.dsn';self.dsn.write_text('(pcb test)')
        self.manifest=self.root/'test.json'
        self.data={'schema':1,'board_sha256':self.module.digest(self.board),
                   'dependency_sha256':{str(p.relative_to(self.root)):self.module.digest(p) for p in self.module.dependencies(self.root)},
                   'dsn_file':'test.dsn','dsn_sha256':self.module.digest(self.dsn),'design_id':'test'}
        self.manifest.write_text(json.dumps(self.data));self.session_hash=self.module.digest(self.session)
    def verify(self):
        return self.module.verify_import_inputs(self.root,self.board,self.session,self.manifest,self.session_hash)
    def test_stale_board_rejected_without_write(self):
        self.board.write_text(self.board.read_text()+'\n# later manual edit\n')
        before=self.board.read_bytes()
        with self.assertRaisesRegex(ValueError,'Source board changed'):self.verify()
        self.assertEqual(before,self.board.read_bytes())
    def test_old_session_and_changed_digest_rejected(self):
        self.session.write_text('(session old (base_design old))')
        with self.assertRaisesRegex(ValueError,'SHA-256'):self.verify()
        self.session_hash=self.module.digest(self.session)
        with self.assertRaisesRegex(ValueError,'different routing export'):self.verify()
    def test_changed_schematic_and_dsn_rejected(self):
        schematic=self.project/'neuronic.kicad_sch';original=schematic.read_text();schematic.write_text('different circuit')
        with self.assertRaisesRegex(ValueError,'Schematic'):self.verify()
        schematic.write_text(original);self.dsn.write_text('different routing input')
        with self.assertRaisesRegex(ValueError,'DSN changed'):self.verify()
    def test_failed_drc_preserves_original_board(self):
        before=self.board.read_bytes()
        with patch.object(k,'ImportSpecctraSES',return_value=True),patch.object(k,'ZONE_FILLER'),\
             patch.object(subprocess,'run',return_value=subprocess.CompletedProcess([],5,'Found missing connections','')):
            with self.assertRaisesRegex(RuntimeError,'failed full DRC'):
                self.module.import_checked(self.root,self.board,self.session,self.manifest,self.session_hash)
        self.assertEqual(before,self.board.read_bytes())

if __name__=='__main__':unittest.main()
