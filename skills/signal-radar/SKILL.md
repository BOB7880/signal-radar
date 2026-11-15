---
name: signal-radar
description: Filter information against a user's business goals, verify important claims against primary sources, rank by relevance and evidence confidence, and produce a concise actionable digest. Use when discovering, reviewing, or scheduling news, GitHub projects, releases, research, or methods for a specific user or business.
---

# Signal Radar · 信息决策雷达

## Purpose

Allocate the user's attention and verification budget. Do not claim to exhaust the web, prove truth, or decide for the user. Separate source claims, observed facts, and inference. Every recommended item needs a traceable source and one bounded next action.

## Runtime boundary

This Skill contains workflow instructions. Network collection, durable state, scheduling, and delivery require scripts or host tools. Use only configured sources and available tools. Never search local files for credentials or put tokens in reports. Sending to Feishu is an external write: require an explicit target configured by the user and use the local `lark-cli` identity they selected. A dry run never counts as successful delivery.

Read `references/feishu-delivery.md` when sending to Feishu. Read `references/platform-setup.md` when installing or scheduling on Codex, Claude Code, or WorkBuddy.

## Workflow

1. **Set decision context.** Read `config/profile.json` if present. Identify the user's goals, time horizon, audience, exclusions, time budget, and risk tolerance. If absent, use the current request as a temporary profile and mark it as such.
2. **Collect.** Prefer configured primary sources and dated artifacts: official docs, GitHub repo/release/commit, papers, raw data, or product notices. Record collection time, source date, canonical URL, source type, and errors. Do not infer that unavailable sources contain no relevant information.
3. **Normalize and deduplicate.** Use `scripts/collect_sources.py` and persistent state when configured. Do not claim cross-run deduplication when state is missing. Group copies of the same underlying announcement.
4. **Build evidence notes.** For every high-impact claim, state: claim; primary evidence; independent corroboration or its absence; version/date/context; limitations. Label evidence T0–T4:
   - T0: unattributed/unverified;
   - T1: attributable source self-report;
   - T2: inspectable artifact such as code, docs, release, data, or runnable demo;
   - T3: independent corroboration;
   - T4: repeated independent reproduction under stated conditions.
   Never convert T1 into an independently verified fact.
5. **Apply hard gates.** Check source identity and date. For code/tools check license, archive/maintenance state, install provenance, permissions, privacy, and reversibility. A high relevance score cannot override an unresolved safety gate. Label unresolved items `审计/沙盒` or exclude them.
6. **Score relevance separately from confidence.** Score each relevance dimension 0–5 and explain briefly:
   - strategic fit 35%; potential impact 25%; novelty 15%; actionability 20%; diversity/exploration 5%.
   - `R = 20 × (0.35S + 0.25I + 0.15N + 0.20A + 0.05D)`, range 0–100.
   - Store evidence confidence separately as ordinal T0–T4; it is not a truth probability and must not be merged into R.
7. **Triage without padding.** Suggested initial policy: R≥75 and T≥T2 → shortlist; R≥75 with T<T2 → `high-potential / needs verification`; R 55–74 → watchlist; R<55 → archive. Safety, legal, security, account, or outage events use a separate urgent lane. A quiet day is valid.
8. **Offer one bounded experiment.** For each shortlisted item, propose a reversible 30–90 minute test: hypothesis, synthetic/redacted input, observable pass/fail criterion, and what result changes the recommendation. Never claim the experiment ran unless it did.
9. **Control volume and diversify.** Honor the configured item cap; do not repeat unchanged stories. Reserve a small exploration share for adjacent topics when allowed. Do not let personalization suppress high-impact safety notices.
10. **Learn only from recorded feedback.** Record read/reject/test/adopt/correction events only if durable state is available. Do not claim to remember across runs without it.
11. **Deliver.** Save the complete Markdown report to the configured reports directory. Send only after the report passes validation and the destination is configured. If no item clears the bar, output exactly `NO_SEND` and skip Feishu delivery.

## Output contract

For each selected item include:

- title and direct source link;
- why now and which user goal it serves;
- claim, primary evidence, corroboration or explicit absence, source date/version;
- R score, T label, and risk gate;
- what remains uncertain;
- one 30–90 minute experiment and pass/fail criterion.

Finish with one reusable method/reference and exactly one recommended next action. Disclose source coverage failures and whether this was manual or scheduled. Avoid hype language and false precision. Link primary sources near the claims they support.
