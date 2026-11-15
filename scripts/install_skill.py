#!/usr/bin/env python3
"""Install Signal Radar into the selected agent's user-level Skills directory."""
import argparse, shutil
from pathlib import Path

TARGETS={"codex":".agents/skills","claude-code":".claude/skills","workbuddy":".codebuddy/skills"}
def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("platform",choices=TARGETS); ap.add_argument("--base-dir",type=Path,default=Path.home(),help="Install base: home for user-scoped agents; project root for WorkBuddy"); ap.add_argument("--force",action="store_true",help="Replace an existing signal-radar skill folder"); a=ap.parse_args()
    root=Path(__file__).resolve().parents[1]; src=root/"skills"/"signal-radar"; dest=a.base_dir/TARGETS[a.platform]/"signal-radar"
    if not src.is_dir() or not (src/"SKILL.md").is_file(): ap.error(f"Skill package incomplete: {src}")
    if dest.exists() and not a.force: ap.error(f"destination exists: {dest}; inspect it or rerun with --force")
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists(): shutil.rmtree(dest)
    shutil.copytree(src,dest)
    print(f"Installed {a.platform} skill: {dest}")
    return 0
if __name__=="__main__": raise SystemExit(main())
