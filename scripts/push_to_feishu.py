#!/usr/bin/env python3
"""Send one Markdown report with the locally authenticated official lark-cli."""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("report",type=Path); ap.add_argument("--chat-id",default=os.getenv("FEISHU_CHAT_ID")); ap.add_argument("--identity",choices=["user","bot"],default=os.getenv("LARK_IDENTITY","user")); ap.add_argument("--lark-cli",default=os.getenv("LARK_CLI_BIN") or shutil.which("lark-cli") or "lark-cli"); ap.add_argument("--dry-run",action="store_true"); args=ap.parse_args()
    path=args.report.expanduser().resolve()
    if not path.is_file(): ap.error(f"report file not found: {path}")
    body=path.read_text(encoding="utf-8").strip()
    if not body: ap.error("report is empty")
    if body=="NO_SEND": print(json.dumps({"ok":True,"sent":False,"reason":"quiet day"})); return 0
    if not args.chat_id: ap.error("set FEISHU_CHAT_ID or pass --chat-id; recipient is required")
    if not re.fullmatch(r"oc_[A-Za-z0-9_-]+",args.chat_id): ap.error("--chat-id must be a Feishu chat_id beginning oc_; use --user-id support only after explicitly configuring a direct recipient")
    binary=shutil.which(args.lark_cli) if "/" not in args.lark_cli else args.lark_cli
    if not binary: ap.error("lark-cli not found; install the official CLI and complete auth login")
    key="radar-"+hashlib.sha256((path.stem+"\0"+body).encode()).hexdigest()[:40]
    cmd=[binary,"im","+messages-send","--chat-id",args.chat_id,"--as",args.identity,"--markdown","@"+path.name,"--idempotency-key",key]
    if args.dry_run: cmd.append("--dry-run")
    try: result=subprocess.run(cmd,cwd=path.parent,text=True,capture_output=True,check=False)
    except OSError as e: print(json.dumps({"ok":False,"error":f"could not start lark-cli: {type(e).__name__}"}),file=sys.stderr); return 2
    if result.returncode:
        # Expose only stable error metadata; never echo arbitrary stderr or request payloads.
        info={"ok":False,"sent":False,"exit_code":result.returncode,"error":"lark-cli failed"}
        try:
            envelope=json.loads(result.stderr or result.stdout); err=envelope.get("error",{})
            for key in ("type","subtype","code","missing_scopes"):
                if key in err: info["error_"+key]=err[key]
        except (json.JSONDecodeError,AttributeError,TypeError): pass
        print(json.dumps(info,ensure_ascii=False),file=sys.stderr); return result.returncode
    if not args.dry_run:
        try:
            envelope=json.loads(result.stdout)
            if envelope.get("ok") is False:
                print(json.dumps({"ok":False,"sent":False,"error":"lark-cli returned ok=false"}),file=sys.stderr); return 2
        except json.JSONDecodeError:
            # CLI versions may use non-JSON output; a zero exit is still their success contract.
            pass
    print(json.dumps({"ok":True,"sent":not args.dry_run,"dry_run":args.dry_run,"identity":args.identity,"destination":"configured Feishu chat","report":path.name},ensure_ascii=False)); return 0
if __name__=="__main__": raise SystemExit(main())
