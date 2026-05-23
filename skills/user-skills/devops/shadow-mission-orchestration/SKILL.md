---
name: shadow-mission-orchestration
description: Orchestrate missions as General Igris using Hermes delegate_task, Kanban, cron, browser-use, and Scrapy with verification/re-prompt loops before reporting to Ayman.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [orchestration, delegation, kanban, opencode-go, verification, shadow-system]
    created_by: agent
---

# Shadow Mission Orchestration

## Purpose

Use this Skill Rune when Ayman gives a mission that benefits from multiple workers, review loops, research scouts, code implementers, durable task tracking, browser operation, crawling, or scheduled automation.

Mandatory linked references:

- `references/shadow-agent-model-codex.md` — load/read this before creating Kanban worker profiles or assigning long-running cards. It contains Ayman's universal 90-second Kanban-first rule, OpenCode Go live model roster, task-to-model routing table, and review/iteration doctrine.
- `references/codex-quota-rotation-ops.md` — load/read this for Hermes Codex/ChatGPT multi-account quota rotation, dashboard quota display, weekly-vs-5h quota gates, Morocco warmup timers, and restart/activation safety.
- `references/telegram-topic-command-center.md` — load/read this when Ayman wants a Telegram supergroup with many topics as separate Hermes command lanes, topic-specific Skill Rune bindings, or topic-targeted cron/raid delivery.
- `references/ams-warp-browser-crawler.md` — load/read this for AMS/Austrian job-board browser/crawler missions. It captures the WARP route test, AMS robots/API constraints, and the safe browser-use vs Scrapy split.
- `references/cron-session-memory-curator-coverage.md` — load/read this when creating, reviewing, or debugging a daily session-memory curator Raid Timer. It captures the pitfall that `session_search()` default browse returns only 3 sessions, the need to enumerate `state.db` by timestamp, cluster related sessions, and verify delivery target/output after patching.

The operating model:

- Ayman is the Shadow Monarch.
- The main Hermes assistant is General Igris: commander, planner, verifier, and final reporter.
- Worker agents/subagents are Shadows.
- OpenCode Go models are the preferred Shadow brain pool once mission-type model routing is configured.
- Igris must verify Shadow outputs against the original mission before presenting them as final.

This is practical engineering orchestration with light Solo Leveling flavor. Do not imply magic, mysticism, or occult practice.

## Required Access Keys / Config Values

Depending on the mission type, verify these before acting:

- OpenCode Go access: `OPENCODE_GO_API_KEY` in `~/.hermes/.env` or configured provider route.
- Hermes delegation config: `delegation.*` in `~/.hermes/config.yaml`.
- Browser-use lab path when browser-human operation is needed: `/home/ubuntu/browser-tools-lab`.
- Scrapy lab path when crawling/scraping is needed: `/home/ubuntu/browser-tools-lab`.
- Repo/server/API credentials required by the specific mission.

Never print, repeat, store, or commit secrets.

## Mission Router

Pick the lightest reliable native Hermes system for the mission.

### 1. Igris alone

Use for simple tasks that can be done directly and verified quickly.

Examples:

- Explain an error.
- Inspect one file.
- Run one safe diagnostic.
- Answer a small question from known local context.

### 2. `delegate_task` Shadows

Default for medium missions that can finish inside the current active run.

Use when:

- Research needs independent scouts.
- Coding needs implementer + reviewer.
- The task benefits from fresh context.
- The work is bounded and synchronous.
- Up to 3 parallel Shadows are enough.

Examples:

- Compare tools.
- Review code.
- Implement a small feature.
- Generate options, then have Igris decide.
- Ask one Shadow to inspect evidence and another to challenge the result.

### 3. Kanban raid board

Use for long or durable missions, not every task.

Use when:

- Many tasks or phases exist.
- Progress must survive interruption or context changes.
- Work may take a long time.
- Tasks need states: pending, blocked, complete.
- Worker profiles should operate independently.
- Retries, logs, or durable coordination are required.

Examples:

- Build a Hermes integration.
- Refactor multiple modules safely.
- Audit a full backup/recovery system.
- Run a multi-day research or implementation campaign.

### 4. Cron / Raid Timer

Use for recurring or scheduled missions.

Examples:

- Daily backup verification.
- Quota checks.
- Log monitoring.
- Periodic reports.
- Daily session-memory curation into Holographic/fact_store.

When a Kanban worker designs or creates a Raid Timer, remember that the worker profile may store cron state under its own profile directory. Igris must verify the final timer from the runtime/default profile before reporting success. If the timer must be visible to the live gateway, prefer creating the final cron job from Igris/operator context with the native cronjob tool, then let a reviewer certify the default-profile job id, schedule, provider/model, enabled state, and delivery route.

For session-memory curator Raid Timers, do not certify success from `last_status=ok` alone. A run can store useful facts while failing coverage. Verify the actual target-window session count from `~/.hermes/state.db` and compare it to the sessions the curator claims it inspected. `session_search()` with no arguments only browses the 3 most recent sessions; it is not a full "last 24 hours" scan. See `references/cron-session-memory-curator-coverage.md` before creating or judging this class of cron job.

### 5. Telegram topic command-center missions

Use when Ayman wants one Telegram group with many topics to behave like separate Hermes command lanes.

Before proposing or configuring this pattern:

1. Read `references/telegram-topic-command-center.md`.
2. Explain that Telegram forum topics give separate thread/session lanes, while Holographic memory remains shared.
3. Warn that bot privacy controls whether Hermes sees normal topic messages or only commands/mentions/replies.
4. Collect real `chat_id` and `thread_id` values from live `/status` messages or gateway/session evidence before editing config.
5. Use `telegram:<chat_id>:<thread_id>` targets for topic-specific cron, send_message, and raid reports.
6. Do not claim topics make long inline work non-blocking; the 90-second Kanban-first rule remains the non-blocking mechanism.

Optional topic-specific Skill Rune bindings can route topics like `Kanban Raids`, `System Ops`, `Memory Core`, and `Research` to different auto-loaded skills once IDs are verified.

### 6. Browser / crawling missions

Use Ayman's preferred split:

- Human-like browsing: browser-use with `kimi-k2.6` through OpenCode Go.
- Crawling/scraping: Scrapy.
- Native Hermes browser/crawling tools: fallback only, unless explicitly requested.

## Standard Mission Brief

Before dispatching Shadows, Igris should define:

1. Objective
2. Background/context
3. Constraints
4. Forbidden moves
5. Required tools or allowed toolsets
6. Expected output format
7. Acceptance criteria
8. Verification method
9. Escalation condition

### Ayman's Kanban-first correction

When Ayman asks how a >90-second task should start, answer narrowly and operationally: create Kanban cards first, report card IDs/status quickly, dispatch workers, keep the main chat available, and require approval before side effects. Do not bury this answer under unrelated feature rules or architecture detail.

When Ayman says to establish/build/implement a long Hermes feature, immediately open the raid instead of doing long inline recon. Create a dedicated board or cards, make the first card read-only when appropriate, and block implementation/deployment/cron cards behind explicit Ayman approval. Report the board slug and task IDs in the same turn.

Template:

```text
Mission: <short name>
Objective: <what must be achieved>
Context: <relevant facts, paths, repos, constraints>
Allowed tools: <toolsets / scripts / commands>
Forbidden moves: <do not modify, delete, deploy, expose secrets, etc.>
Output format: <exact shape>
Acceptance criteria:
- <criterion 1>
- <criterion 2>
Verification:
- <how Igris will test/check>
Escalate if:
- <condition requiring user decision>
```

## Shadow Output Contract

Every Shadow should return:

- Summary
- Evidence checked
- Exact commands/files/URLs inspected when applicable
- Findings
- Confidence level
- Gaps or uncertainty
- Recommended next action

For code work, require:

- Files changed
- Tests run and results
- Known risks
- Rollback notes if relevant

## Igris Verification Gate

Never accept Shadow output blindly.

Igris must check:

- Did the Shadow answer the exact mission?
- Did it obey constraints and forbidden moves?
- Is the evidence concrete?
- Are claims supported by files, commands, URLs, logs, or tests?
- Did it skip required output fields?
- Did it introduce scope creep?
- Does it conflict with another Shadow?
- Are there safety, secret, or production risks?

For code/system changes, Igris should verify directly when possible:

- Read the changed files.
- Inspect `git diff`.
- Run relevant tests or diagnostics.
- Check logs/ports/status before claiming success.

## Re-prompt Loop

If a Shadow fails the Verification Gate, Igris re-prompts with specific correction instructions.

Correction prompt template:

```text
Your previous output failed verification.

Original mission:
<brief>

Failures:
- <specific failure 1>
- <specific failure 2>

Redo only the failed part.
Do not change: <protected scope>
Return in this exact format: <format>
```

Default retry limits:

- Normal missions: 2 correction loops.
- Code/system missions: 3 correction loops.
- Production/Core Crystal tasks: stop earlier and ask Ayman if uncertainty remains.

Escalate to Ayman when:

- Required Access Keys are missing.
- Requirements conflict.
- Destructive or irreversible action is needed.
- Two or more Shadows disagree on a critical fact and Igris cannot verify.
- Retry limit is reached.

## Coding Mission Pattern

Use delegate_task first unless the project is large enough for Kanban.

Recommended sequence:

1. Planning Shadow: decomposes requirements.
2. Reviewer Shadow checks the plan/spec before implementation proceeds.
3. Implementer Shadow writes code/tests using a task-appropriate worker model/profile.
4. Reviewer Shadow checks prompt compliance, bugs, security, style, and tests.
5. If review fails, Igris creates an iteration/fix card linked from the review and routes it back to the appropriate worker; repeat until PASS or BLOCKED.
6. Igris Final Gate verifies diffs and tests directly before reporting success.

Do not let an implementer be its own final reviewer.
Do not assign implementation labor to the `default`/GPT-5.5 General profile just because it exists. For Ayman's raids, GPT-5.5 is reserved for review/commander verification unless he explicitly approves using it for labor; create or reuse an OpenCode Go coding profile first.
Every Kanban card must pass a review gate before dependent cards proceed. A worker handoff saying "review-required" should become a reviewer run, not a final completion.

## Research Mission Pattern

For research missions, dispatch independent scouts when useful:

- Shadow Scout A: official docs / primary sources.
- Shadow Scout B: GitHub / code / package metadata.
- Shadow Scout C: forums, Reddit, blogs, community reports.

Igris then cross-checks claims, resolves conflicts, and reports what is verified vs uncertain.

## Browser/Crawler Mission Pattern

Human-like browser operation:

- Use browser-use from `/home/ubuntu/browser-tools-lab`.
- Default working model: `kimi-k2.6` via OpenCode Go.
- Prefer settings proven in lab: `dont_force_structured_output=True`, `add_schema_to_system_prompt=True`.
- Verify extracted output before reporting.

Crawling/scraping:

- Use Scrapy from `/home/ubuntu/browser-tools-lab`.
- Prefer deterministic HTTP crawling over LLM browsing when possible.
- Respect robots/rate limits and avoid credentials unless explicitly authorized.

Network/robots discipline for web missions:

- If a site is reachable in one path but job/API hosts time out from the VPS, test route reachability before rewriting scrapers. A trusted VPN/exit route such as Cloudflare WARP can distinguish network blockage from application blockage.
- After a route change opens a host, re-check `robots.txt` and API authorization before crawling. Network access is not permission to scrape.
- For AMS/Austrian job-board work, read `references/ams-warp-browser-crawler.md` before deciding between browser-use and Scrapy.
- Avoid long combined endpoint probes; use short isolated probes with explicit connect/read timeouts so one sealed Gate does not freeze the mission.

## Safety Rules

- Read-only scan first unless Ayman authorized writes.
- Confirm destructive actions before running them.
- Never expose secrets.
- Do not modify production/Core Crystal without confirmation.
- Do not guess missing Access Keys, ports, config paths, or credentials.
- For GitHub/backups/config changes, inspect diff and verify no secrets before pushing.

## Final Report Format

Igris final response should include:

```text
System report:
<plain summary>

Shadows deployed:
- <Shadow role>: <task + result>

Verification:
- <checks Igris personally performed>

Result:
- PASS / PARTIAL / BLOCKED / FAILED

Risks / unknowns:
- <only if any>

Next move:
<recommended action or request for approval>
```

Keep the flavor tactical but the technical result clear.

## Model Routing Doctrine

Ayman's model routing is now configured through the linked Shadow Agent Model Codex.

Before creating Kanban worker profiles or assigning long-running cards:

1. Load/read `references/shadow-agent-model-codex.md`.
2. Match the mission type to the routing table.
3. Create or reuse a profile with the chosen OpenCode Go model.
4. Verify the profile exists with `hermes profile list` before assigning cards.
5. Prefer local empirical success history over generic model reputation once enough runs exist.

Current defaults from the codex:

- Routine scout/read-only diagnostics: `deepseek-v4-flash`.
- Code implementation / bug fixes: `deepseek-v4-flash` by default because GPT-5.5 reviews worker output.
- Coding escalation only after repeated review failure, clear heavy complexity, or Ayman approval: `qwen3.6-plus` or `deepseek-v4-pro`.
- Large docs/web/session synthesis: `kimi-k2.6`.
- UI/product/frontend visual work: `kimi-k2.6`.
- Memory curation and policy-style judgment: `glm-5.1`.
- Writing/final report shaping: `minimax-m2.7`.
- High-stakes final review: GPT-5.5 shadow or main General verification.

If a worker fails twice on the same task shape, switch model family rather than retrying blindly.

## Common System Alerts

- Shadow gives confident but unsupported claims: reject and request evidence.
- Shadow ignores format: re-prompt with exact schema.
- Shadow changes scope: reject scope creep and narrow the task.
- Shadow cannot access needed credentials: stop and ask Ayman for Access Keys.
- Kanban used for small task: too much overhead; use delegate_task next time.
- delegate_task used for long campaign: promote to Kanban raid board.
