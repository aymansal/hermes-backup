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
- `BLOCKED` with exact failure reasons and a fix prompt when it does not.

If blocked, create an iteration/fix card routed back to the same worker model/profile that failed. Escalate models only after repeated failed iterations or explicit user approval.

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
