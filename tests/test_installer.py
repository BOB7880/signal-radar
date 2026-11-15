import subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class InstallerTests(unittest.TestCase):
    def test_installs_to_each_platform_directory(self):
        expected={'codex':'.agents/skills','claude-code':'.claude/skills','workbuddy':'.codebuddy/skills'}
        for platform,subdir in expected.items():
            with self.subTest(platform=platform), tempfile.TemporaryDirectory() as td:
                subprocess.run([sys.executable,str(ROOT/'scripts/install_skill.py'),platform,'--base-dir',td],check=True,capture_output=True,text=True)
                target=Path(td)/subdir/'signal-radar'
                self.assertTrue((target/'SKILL.md').is_file())
                self.assertTrue((target/'references/feishu-delivery.md').is_file())
    def test_does_not_overwrite_existing_install_by_default(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/'.agents/skills/signal-radar'; target.mkdir(parents=True); marker=target/'keep'; marker.write_text('x')
            result=subprocess.run([sys.executable,str(ROOT/'scripts/install_skill.py'),'codex','--base-dir',td],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0); self.assertTrue(marker.exists())
if __name__=='__main__': unittest.main()
