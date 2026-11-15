#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
TODAY="$(date +%F)"
INBOX="$ROOT/var/inbox/$TODAY.json"
REPORT="$ROOT/reports/$TODAY.md"
CODEX_BIN="${CODEX_BIN:-$(command -v codex || true)}"
if [[ -z "$CODEX_BIN" ]]; then echo 'codex CLI not found; set CODEX_BIN' >&2; exit 127; fi
mkdir -p "$ROOT/var/inbox" "$ROOT/reports" "$ROOT/logs"
python3 "$ROOT/scripts/collect_sources.py" --config "$ROOT/config/sources.json" --output "$INBOX" --state "$ROOT/var/state/seen.json"
PROMPT="Read skills/signal-radar/SKILL.md, config/profile.json, and $INBOX. Use only the collected source items and any explicitly available read-only sources. Apply the Skill's evidence labels, hard gates, relevance scoring, and low-noise policy. Write today's complete Chinese Markdown digest as your final response. Cite item URLs inline. Do not invent corroboration or claim a test ran. If no item clears the bar, output exactly NO_SEND with no other text. This is a read-only scheduled run; do not publish, install software, send messages, or change external systems."
"$CODEX_BIN" exec --cd "$ROOT" --sandbox read-only --output-last-message "$REPORT" "$PROMPT"
if [[ "$(tr -d '\r\n' < "$REPORT")" == "NO_SEND" ]]; then
  python3 "$ROOT/scripts/mark_seen.py" --inbox "$INBOX" --state "$ROOT/var/state/seen.json"
  echo '{"ok":true,"sent":false,"reason":"quiet day"}'
  exit 0
fi
python3 "$ROOT/scripts/push_to_feishu.py" "$REPORT" --identity "${LARK_IDENTITY:-user}"
python3 "$ROOT/scripts/mark_seen.py" --inbox "$INBOX" --state "$ROOT/var/state/seen.json"
