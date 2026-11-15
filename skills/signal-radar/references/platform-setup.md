# Platform setup: Codex, Claude Code, WorkBuddy

The Skill folder is portable. Platform-specific directories and scheduler behavior vary by version; verify the current product UI/docs before enabling automation.

## Codex

- Global install: copy `skills/signal-radar/` to `~/.agents/skills/signal-radar/` (or the Skills directory shown by the installed Codex version).
- Repository install: `.agents/skills/signal-radar/`.
- Run interactively: ask Codex to use `$signal-radar` and inspect the configured inbox.
- For unattended runs, use `codex exec` under a user-owned scheduler with least privilege; see `docs/飞书CLI设置与日报推送教程.md`. Collect public sources first, then run Codex read-only over the collected JSON and save the final Markdown. Do not use approval bypass flags.

## Claude Code

- Global install: `~/.claude/skills/signal-radar/SKILL.md` plus its sibling `references/`.
- Project install: `.claude/skills/signal-radar/`.
- Invoke with `/signal-radar` or describe the relevant task. For scheduled runs, use a separately configured Routines/automation runtime; verify that it can access the required local source files and delivery command.

## Tencent WorkBuddy

- User-level install: project-level `.codebuddy/skills/signal-radar/` (WorkBuddy Enterprise Skills format).
- Project-level install: `.agents/skills/signal-radar/` or the project Skills directory exposed by the current WorkBuddy version.
- Restart/reload Skills if required by the installed version, then run one manual test with a sample inbox.
- WorkBuddy supports local and cloud task modes. A cloud task cannot be assumed to see a local `lark-cli` binary or local files. For Feishu CLI delivery, use a local task/runtime where `lark-cli` is installed, or schedule the local pipeline with macOS LaunchAgent/Windows Task Scheduler. WorkBuddy's own scheduled notification channel may be WeCom; that is separate from sending via Feishu CLI.

## Cross-platform contract

All platforms should produce the same dated Markdown report and pass it to `scripts/push_to_feishu.py`. The sender uses the locally installed `lark-cli` and its own stored authorization. Never put app secrets or access tokens in this repository, profile, launchd plist, or report.
