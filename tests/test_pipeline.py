import json, os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import collect_sources, push_to_feishu

class CollectorTests(unittest.TestCase):
    def test_rss_namespaced_entry_and_dedup_key(self):
        xml=b'''<rss><channel><item><title>Launch</title><link>https://example.com/a</link><pubDate>Sat, 15 Nov 2026 00:00:00 GMT</pubDate><description>Demo</description></item></channel></rss>'''
        items=collect_sources.parse_feed(xml,'test',['ai'],10)
        self.assertEqual(len(items),1)
        self.assertEqual(items[0]['url'],'https://example.com/a')
        self.assertEqual(items[0]['tags'],['ai'])
        self.assertEqual(items[0]['id'],collect_sources.digest('https://example.com/a','Launch'))

class SenderTests(unittest.TestCase):
    def test_quiet_day_needs_no_destination(self):
        with tempfile.TemporaryDirectory() as td:
            report=Path(td)/'quiet.md'; report.write_text('NO_SEND')
            with patch('sys.argv',['push_to_feishu.py',str(report)]):
                self.assertEqual(push_to_feishu.main(),0)

    def test_requires_recipient_before_call(self):
        with tempfile.TemporaryDirectory() as td:
            report=Path(td)/'daily.md'; report.write_text('# Digest')
            with patch('sys.argv',['push_to_feishu.py',str(report)]), patch('subprocess.run') as run:
                with self.assertRaises(SystemExit) as exc: push_to_feishu.main()
                self.assertEqual(exc.exception.code,2)
                run.assert_not_called()

    def test_dry_run_uses_markdown_and_never_reports_sent(self):
        with tempfile.TemporaryDirectory() as td:
            report=Path(td)/'daily.md'; report.write_text('# Digest\n\n- Source: https://example.com')
            fake=Path(td)/'lark-cli'; fake.write_text('#!/bin/sh\nprintf \'{"ok":true,"secret":"never-print"}\\n\'\n'); fake.chmod(0o755)
            with patch('sys.argv',['push_to_feishu.py',str(report),'--chat-id','oc_test123','--lark-cli',str(fake),'--dry-run']):
                self.assertEqual(push_to_feishu.main(),0)


    def test_cli_failure_exposes_only_safe_scope_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            report=Path(td)/'daily.md'; report.write_text('# Digest')
            fake=Path(td)/'lark-cli'; fake.write_text("""#!/usr/bin/env python3
import json,sys
print(json.dumps({"ok":False,"error":{"type":"authorization","subtype":"missing_scope","code":123,"missing_scopes":["im:message"],"message":"contains secret private text"}}),file=sys.stderr)
sys.exit(3)
"""); fake.chmod(0o755)
            from contextlib import redirect_stderr
            from io import StringIO
            captured=StringIO()
            with patch('sys.argv',['push_to_feishu.py',str(report),'--chat-id','oc_test123','--lark-cli',str(fake)]), redirect_stderr(captured):
                self.assertEqual(push_to_feishu.main(),3)
            self.assertIn('im:message',captured.getvalue())
            self.assertNotIn('secret private text',captured.getvalue())

    def test_live_success_uses_configured_identity(self):
        with tempfile.TemporaryDirectory() as td:
            report=Path(td)/'daily.md'; report.write_text('# Digest')
            log=Path(td)/'args.json'; fake=Path(td)/'lark-cli'
            fake.write_text('#!/usr/bin/env python3\nimport json,sys,os\nopen(os.environ["ARGS_LOG"],"w").write(json.dumps(sys.argv[1:]))\nprint(json.dumps({"ok": True}))\n'); fake.chmod(0o755)
            with patch.dict(os.environ,{'ARGS_LOG':str(log)}), patch('sys.argv',['push_to_feishu.py',str(report),'--chat-id','oc_test123','--identity','bot','--lark-cli',str(fake)]):
                self.assertEqual(push_to_feishu.main(),0)
            args=json.loads(log.read_text())
            self.assertIn('--as',args); self.assertEqual(args[args.index('--as')+1],'bot')
            self.assertIn('--markdown',args); self.assertIn('@daily.md',args)

if __name__=='__main__': unittest.main()
