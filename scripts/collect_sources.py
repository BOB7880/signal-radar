#!/usr/bin/env python3
"""Collect configured public RSS feeds and GitHub release/repository metadata."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, ssl, time, urllib.error, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path

UA = "SignalRadar/0.1 (+https://github.com/BOB7880/signal-radar)"

def stamp(): return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
def digest(*parts): return hashlib.sha256("\0".join(parts).encode()).hexdigest()
def local(tag): return tag.rsplit("}", 1)[-1].lower()
def child_text(node, names):
    for child in node.iter():
        if local(child.tag) in names and child.text:
            return child.text.strip()
    return ""
def tls_context():
    # Prefer a maintained CA bundle when certifi is already available; never disable TLS checks.
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()

def fetch(url, timeout):
    req=urllib.request.Request(url, headers={"User-Agent":UA,"Accept":"application/json, application/atom+xml, application/rss+xml, application/xml;q=0.9,*/*;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout, context=tls_context()) as resp: return resp.read()
def parse_feed(data, name, tags, limit):
    root=ET.fromstring(data); out=[]
    for node in root.iter():
        if local(node.tag) not in {"item","entry"}: continue
        title=child_text(node,{"title"}); link=child_text(node,{"link","guid","id"})
        for c in node:
            if local(c.tag)=="link" and c.attrib.get("href"):
                link=c.attrib["href"]; break
        published=child_text(node,{"published","updated","pubdate","date"})
        summary=child_text(node,{"summary","description","encoded","content"})
        if not title or not link: continue
        out.append({"id":digest(link.strip(),title.strip()),"title":title,"url":link.strip(),"published":published,"summary":summary[:3000],"source":name,"source_type":"rss","tags":tags})
        if len(out)>=limit: break
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--config",type=Path,default=Path("config/sources.json")); ap.add_argument("--output",type=Path,default=Path("var/inbox/latest.json")); ap.add_argument("--state",type=Path,default=Path("var/state/seen.json")); args=ap.parse_args()
    cfg=json.loads(args.config.read_text()); timeout=int(cfg.get("request_timeout_seconds",15)); limit=int(cfg.get("max_items_per_feed",30)); args.state.parent.mkdir(parents=True,exist_ok=True)
    seen=set(json.loads(args.state.read_text()).get("ids",[])) if args.state.exists() else set(); items=[]; health=[]
    for feed in cfg.get("rss_feeds",[]):
        try:
            rows=parse_feed(fetch(feed["url"],timeout),feed.get("name",feed["url"]),feed.get("tags",[]),limit)
            for row in rows: row["seen_before"]=row["id"] in seen
            items.extend(rows); health.append({"source":feed.get("name",feed["url"]),"ok":True,"count":len(rows)})
        except Exception as e: health.append({"source":feed.get("name",feed.get("url","unknown")),"ok":False,"error":f"{type(e).__name__}: {e}"})
    for repo in cfg.get("github_repositories",[]):
        api=f"https://api.github.com/repos/{repo}/releases?per_page=5"
        try:
            releases=json.loads(fetch(api,timeout)); count=0
            for rel in releases:
                url=rel.get("html_url",""); title=rel.get("name") or rel.get("tag_name") or "release"
                if not url: continue
                rid=digest(url,title); items.append({"id":rid,"title":f"{repo}: {title}","url":url,"published":rel.get("published_at") or rel.get("created_at",""),"summary":(rel.get("body") or "")[:3000],"source":repo,"source_type":"github_release","tags":["GitHub"],"seen_before":rid in seen}); count+=1
            health.append({"source":repo,"ok":True,"count":count})
        except Exception as e: health.append({"source":repo,"ok":False,"error":f"{type(e).__name__}: {e}"})
        time.sleep(0.15)
    # Deduplicate within the batch while preserving order.
    unique=[]; ids=set()
    for item in items:
        if item["id"] not in ids: unique.append(item); ids.add(item["id"])
    payload={"collected_at":stamp(),"source_health":health,"items":unique,"new_item_count":sum(not x["seen_before"] for x in unique)}
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"ok":True,"items":len(unique),"new_items":payload["new_item_count"],"sources_ok":sum(x["ok"] for x in health),"sources_failed":sum(not x["ok"] for x in health),"output":str(args.output)},ensure_ascii=False))
    return 0 if any(x["ok"] for x in health) or not health else 2
if __name__=="__main__": raise SystemExit(main())
