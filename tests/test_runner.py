import json, os, shutil, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class RunnerIntegrationTests(unittest.TestCase):
    def run_case(self, report_text):
        td=tempfile.TemporaryDirectory(); root=Path(td.name)/'repo'
        shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.git'))
        (root/'config/sources.json').write_text('{"rss_feeds":[],"github_repositories":[]}')
        codex=Path(td.name)/'fake-codex'
        codex.write_text('#!/usr/bin/env python3\nimport os,sys\nfrom pathlib import Path\np=Path(sys.argv[sys.argv.index("--output-last-message")+1]); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(os.environ["MOCK_REPORT"])\n')
        codex.chmod(0o755)
        lark_log=Path(td.name)/'lark-args.json'; lark=Path(td.name)/'fake-lark'
        lark.write_text('#!/usr/bin/env python3\nimport json,os,sys\nopen(os.environ["MOCK_LARK_LOG"],"w").write(json.dumps(sys.argv[1:]))\nprint(json.dumps({"ok":True}))\n')
        lark.chmod(0o755)
        env=os.environ.copy(); env.update({'CODEX_BIN':str(codex),'LARK_CLI_BIN':str(lark),'FEISHU_CHAT_ID':'oc_test123','LARK_IDENTITY':'user','MOCK_REPORT':report_text,'MOCK_LARK_LOG':str(lark_log)})
        result=subprocess.run([str(root/'scripts/run_codex_daily.sh')],cwd=root,env=env,text=True,capture_output=True,timeout=60)
        return td,root,lark_log,result

    def test_mocked_daily_run_delivers_through_cli_adapter(self):
        td,root,log,result=self.run_case('# Test digest\n')
        try:
            self.assertEqual(result.returncode,0,result.stderr)
            args=json.loads(log.read_text())
            self.assertIn('im',args); self.assertIn('+messages-send',args)
            self.assertIn('oc_test123',args); self.assertIn('--markdown',args)
            self.assertTrue(list((root/'var/state').glob('seen.json')))
        finally: td.cleanup()

    def test_quiet_day_skips_delivery(self):
        td,root,log,result=self.run_case('NO_SEND')
        try:
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertFalse(log.exists())
            self.assertIn('quiet day',result.stdout)
        finally: td.cleanup()

if __name__=='__main__': unittest.main()
