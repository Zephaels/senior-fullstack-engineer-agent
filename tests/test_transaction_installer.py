import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SCRIPT=ROOT/'scripts/sfse_installer.py'; PLUGIN=ROOT/'plugins/senior-fullstack-engineer-agent'
def run(*args,env=None):
 cp=subprocess.run([sys.executable,str(SCRIPT),*map(str,args)],text=True,capture_output=True,env=env); return cp,json.loads(cp.stdout)
class InstallerTests(unittest.TestCase):
 def test_install_verify_uninstall(self):
  with tempfile.TemporaryDirectory() as td:
   cp,r=run('install','--source',PLUGIN,'--home',td); self.assertEqual(cp.returncode,0,r); self.assertTrue(r['ok'])
   cp,r=run('verify','--home',td); self.assertEqual(cp.returncode,0,r)
   cp,r=run('uninstall','--home',td); self.assertEqual(cp.returncode,0,r); self.assertFalse((Path(td)/'plugins/senior-fullstack-engineer-agent').exists())
 def test_upgrade_rollback(self):
  with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as sd:
   cp,r=run('install','--source',PLUGIN,'--home',td); self.assertEqual(cp.returncode,0,r)
   alt=Path(sd)/PLUGIN.name; import shutil; shutil.copytree(PLUGIN,alt); m=json.loads((alt/'.codex-plugin/plugin.json').read_text()); m['version']='9.9.9'; (alt/'.codex-plugin/plugin.json').write_text(json.dumps(m)); (alt/'marker.txt').write_text('new')
   cp,r=run('upgrade','--source',alt,'--home',td); self.assertEqual(cp.returncode,0,r); self.assertTrue((Path(td)/'plugins/senior-fullstack-engineer-agent/marker.txt').exists())
   cp,r=run('rollback','--home',td); self.assertEqual(cp.returncode,0,r); self.assertFalse((Path(td)/'plugins/senior-fullstack-engineer-agent/marker.txt').exists())
 def test_failure_rolls_back(self):
  with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as sd:
   cp,r=run('install','--source',PLUGIN,'--home',td); self.assertEqual(cp.returncode,0,r); before=run('verify','--home',td)[1]['hash']
   alt=Path(sd)/PLUGIN.name; import shutil; shutil.copytree(PLUGIN,alt); (alt/'marker.txt').write_text('new')
   env=os.environ.copy(); env['SFSE_INSTALLER_FAIL_AT']='after-switch'; cp,r=run('upgrade','--source',alt,'--home',td,env=env); self.assertNotEqual(cp.returncode,0)
   after=run('verify','--home',td)[1]['hash']; self.assertEqual(before,after)
if __name__=='__main__': unittest.main()
