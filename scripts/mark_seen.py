#!/usr/bin/env python3
"""Commit collected candidate IDs to the local dedupe ledger after report handling."""
import argparse, datetime as dt, json
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--inbox',type=Path,default=Path('var/inbox/latest.json')); p.add_argument('--state',type=Path,default=Path('var/state/seen.json')); a=p.parse_args()
payload=json.loads(a.inbox.read_text()); old=json.loads(a.state.read_text()).get('ids',[]) if a.state.exists() else []; ids=list(dict.fromkeys(old+[i['id'] for i in payload.get('items',[])])); a.state.parent.mkdir(parents=True,exist_ok=True); a.state.write_text(json.dumps({'updated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'ids':ids[-20000:]},indent=2)+'\n'); print(json.dumps({'ok':True,'tracked':len(payload.get('items',[]))}))
