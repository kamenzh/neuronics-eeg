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
        b=k.BOARD();v=k.PCB_VIA(b);v.SetPosition(k.VECTOR2I(0,0));v.SetWidth(600000,k.F_Cu);v.SetDrill(300000);b.Add(v)
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

if __name__=='__main__':unittest.main()
