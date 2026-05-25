# Ayman Kanban Review Doctrine

Use this reference when orchestrating Ayman's Kanban raids, especially Hermes/POS/business work.

## Model routing

- Main General stays available in chat and monitors raid state.
- Coding / implementation / bug-fix cards: OpenCode Go `deepseek-v4-flash` by default.
- Escalate coding to `qwen3.6-plus` or `deepseek-v4-pro` only after repeated failure, obvious heavy complexity, or explicit approval.
- UI/product/frontend visual cards: `kimi-k2.6` always.
- Research / long web or docs synthesis: `kimi-k2.6`.
- Curation / memory / judgment: `glm-5.1`.
- Writing/report polish: `minimax-m2.7`.
- Final review of code/config/system/business-impact cards: `gpt-5.5`.

## Review gate scope

GPT-5.5 review is mandatory for:

- code or config changes
- deployments, service restarts, cron/Raid Timers, automations
- auth/security, quota/account switching, backups/restore flows
- memory/skill/routing-doc changes
- POS/business work that can affect money, customers, inventory, reporting, or operations

GPT-5.5 review is not automatically required for simple research/scraping that only summarizes public information and does not persist into rules, skills, memory, or system behavior. For research-only cards, report sources, confidence, and official-vs-anecdotal status directly.

## How GPT-5.5 should review

Every non-trivial worker/task-agent result in Ayman's Kanban raids must pass through a reviewer before the General treats it as accepted. A worker finishing a card is not enough by itself.

The reviewer must review only what the worker produced. It should not redo the task.

Review inputs should be compact:

- task goal and acceptance criteria
- worker handoff summary
- changed files / diff summary
- tests or commands run
- screenshots/output if relevant
- risks and rollback notes

Reviewer verdict format:

- `PASS` when the worker output satisfies the card and risk is acceptable.
- `BLOCKED` when the worker output does not match the request, misses acceptance criteria, has unsafe changes, lacks tests/evidence, or otherwise needs correction.

A `BLOCKED` review must include:

- exact failure reasons
- affected files/lines or artifacts when available
- what was expected versus what was delivered
- concrete redo/fix instructions the coder shadow can execute
- tests or verification required before re-review

If blocked, create an iteration/fix card routed back to the same worker model/profile that failed, carrying the reviewer’s exact findings and redo instructions. Escalate models only after repeated failed iterations or explicit user approval.

When a worker profile cannot resolve a forced `--skill` that exists for the General/default profile, do not keep retrying the same broken card. Reclaim/archive the bad attempt, then recreate the card with the relevant doctrine embedded directly in the task body or verify the skill is installed/visible for that worker profile first. Worker profile skill scope can differ from the General's scope.

For dependency chains, pass parent links at task creation time. If cards were accidentally created/promoted before dependencies were linked, immediately reclaim/block unsafe children and recreate a clean chained graph when practical; do not let implementation/review run before parent handoffs exist.

## Approval / YOLO discipline

Ayman permits YOLO or auto-approval for low-risk inspection commands, but the operator must still stop and ask explicit chat approval before disruptive or meaningful-write actions:

- reboot or shutdown;
- service/dashboard/gateway restarts;
- turning off or disabling services;
- deleting/removing files, jobs, volumes, branches, credentials, or resources;
- production/Core Crystal changes;
- config or code edits;
- installs;
- cron/Raid Timer changes;
- any irreversible or risky action.

If a Telegram approval prompt says `Always`, do not assume it is acceptable for high-warning/security-sensitive commands. Explain the scope and prefer safer/local checks when possible. Treat YOLO as reducing popup friction, not as permission to skip the operator's explicit approval gate for disruptive work.

## Automation minimalism for Ayman

For Raid Timers / cron / automation changes, separate the essential action from convenience refreshes or status checks before implementing. If Ayman can already see the state in the Shadow Realm dashboard, do not add or keep extra refresh-only automation unless he explicitly wants it. Example: Codex quota alignment needs the 09:00 Morocco all-account warmup to start 5h timers; a 14:00 refresh-only job is optional dashboard polish and should be removed if Ayman says he will check manually.

## Reporting expectations

Report phase changes promptly:

- worker started
- worker completed
- review started
- review passed/failed
- blocked needing Ayman's decision
- approval required
- crash/reclaim/retry

Do not wait for Ayman to ask when a review passes or a decision gate opens.

### Active status checks

When Ayman asks `Status?`, treat it as a commander checkpoint, not a passive summary request:

1. Poll every active worker/reviewer card that belongs to the current raid, plus relevant repo/artifact state if it affects the verdict.
2. If a reviewer has returned `BLOCKED` and the fix is mechanical/clear from the review, immediately create the same-worker fix card and dependent GPT-5.5 re-review card before replying. Report both the blocker and the new card IDs/statuses.
3. If the blocker needs Ayman's product/business decision, stop and ask instead of spawning a speculative fix.
4. Distinguish `worker complete`, `review PASS`, `review BLOCKED`, and `committed` explicitly. Never imply a worker handoff is accepted before review PASS.
5. For parallel lanes, group status by lane (`backend`, `prototype`, `review`, etc.) and state the current battle line in one concise final section.
6. If Ayman says a board view looks different from your report, immediately re-check the actual Kanban board and identify stale/unrelated blocked cards before defending the earlier summary.
7. If Ayman asks only for a link (for example, “just give me the Tailscale link”), answer with the link(s) only and skip the battle report.

### Dev-preview cache poison during Kanban raids

Next.js dev servers can be cache-poisoned after workers run `next build`, Convex codegen, or route/component edits while `next dev` is still running. Symptoms seen in ImmoPilot raids include:

- HTML route returns 200 but `/_next/static/css/app/layout.css` returns 404, showing raw unstyled HTML.
- Routes throw HTTP 500 with missing `.next/server` chunks such as `Cannot find module './613.js'` or missing vendor chunks.
- One route works while another route fails immediately after quality gates.

Do not treat this as a code failure until verified after a clean resummon. Recovery pattern:

1. Stop only the project dev server process for the affected port.
2. Remove the project `.next` directory.
3. Restart `pnpm --filter <web-package> dev --hostname 0.0.0.0 --port <port>`.
4. Verify the key routes and CSS asset by HTTP before reporting visual readiness or committing.
5. If quality gates are run again while dev is open, expect to repeat this before sending preview links.

### Safe Kanban card body creation

When creating Kanban cards from shell scripts, never put markdown containing backticks inside an unquoted command substitution directly in the CLI arguments. Bash will execute inline code spans and corrupt the card body. Use single-quoted heredocs written to `/tmp/*.md`, then pass file content carefully; if corruption is detected after creation, add a corrective Kanban comment immediately so the reviewer has the accurate criteria.

#### Stalled worker checks

If a worker has been `running` unusually long or Ayman asks whether it is stuck, do not rely on Kanban status alone. Verify whether the shadow is actually progressing:

- inspect the worker PID from the card/run and check process state, elapsed time, CPU time, and wait channel;
- inspect child processes so an active build/test is not mistaken for a stall;
- check the Kanban log file modify time and tail the log for the last meaningful action;
- compare card events for heartbeat/claim extension details (`last_heartbeat_at` vs merely `pid_alive`);
- preserve repo changes before killing anything.

Treat a worker as corrupted/stalled when the process exists but has no heartbeat, low/no CPU progress, stale logs, and only `pid_alive` claim extensions. Ask for approval before killing the worker or restarting dev services. If the worker completed while being inspected, continue with review/blocker handling instead of forcing a retry.

#### Dev preview cache collisions during Kanban raids

For Next.js/Turborepo dev previews, `pnpm build` or worker route changes can poison `.next` while a dev server is running, causing transient 404/500 errors such as missing CSS or missing server chunks. Do not misclassify this as a code failure until verified. Safe recovery pattern after approval:

1. stop only the dev preview process for that app/port;
2. remove the app's `.next` directory;
3. restart the dev server;
4. verify the affected routes and CSS asset over localhost/Tailscale;
5. keep review verdicts separate from live-preview health.

When Ayman only asks for a link, answer with the link directly and avoid a full raid report unless there is an active safety/blocker condition.

7. For parallel lanes, group status by lane (`backend`, `prototype`, `review`, etc.) and state the current battle line in one concise final section.

6. If Ayman says the Shadow Realm/Kanban board shows a different state than your summary, immediately re-read the exact card(s) plus board-wide blocked/running tasks before defending the prior report. Explain any mismatch by card ID (e.g. current review PASS vs old unrelated blocked prototype review). Do not imply PASS/BLOCKED from memory.
7. For UI cards, distinguish three gates explicitly: `review PASS`, `live preview healthy`, and `committed`. A review PASS is not enough if the Next dev preview is returning 500 or missing assets; verify `/app/...` routes and CSS before recommending commit.
8. If a Next dev preview serves HTML but CSS assets 404, or throws webpack-runtime missing chunk errors after route/component changes, treat it as likely stale `.next` cache. Ask Ayman before resummoning the dev shadow, then stop Next dev, remove `apps/web/.next`, restart, and verify both local/Tailscale route and any temporary tunnel.

### Link-only requests

When Ayman asks only for a preview/link (e.g. “just give me the Tailscale link”), answer with the requested link(s) only plus minimal labels. Do not add raid summaries, status blocks, or extra commentary unless there is a live safety issue.
