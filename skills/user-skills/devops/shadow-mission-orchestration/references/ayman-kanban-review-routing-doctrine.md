# Ayman Kanban Review + Model Routing Doctrine

Session-derived doctrine for future Kanban raids.

## Review scope

GPT-5.5 reviewer must review only what the worker produced, not redo the whole task.

Review inputs should be compact:
- task result / handoff
- changed files and diff summary
- tests/commands run
- screenshots or output artifacts when relevant
- acceptance criteria
- risks and rollback notes

## Iteration rule

If review fails:
1. Reviewer marks `BLOCKED` and gives exact failures.
2. General creates a fix/iteration card.
3. Route the fix card back to the same worker model/profile that produced the failed work.
4. Same worker fixes its own output.
5. GPT-5.5 reviews again.
6. Escalate model only after repeated failed iterations or Ayman's explicit approval.

## Review-required handoff routing

A worker may finish useful uncommitted work by blocking itself with a `review-required` summary. Treat that as a handoff state, not as a failed implementation and not as approval.

Safe routing pattern:
1. Inspect the worker task summary/comment and confirm it is a handoff, not a crash or true blocker.
2. Add a Kanban comment saying the parent is being completed only to unlock review, and that completion is not code approval.
3. Mark the worker card complete with a summary like `Worker handoff complete; review required before commit/push.`
4. Dispatch the dependent GPT-5.5 review card.
5. Do not commit or push until review returns PASS and final gates pass from the verified repo root.

Pitfall: a child review card with a blocked parent will remain parked. `dispatch` cannot spawn it until the parent is complete.

## Fix-card routing after blocked review

When GPT-5.5 review returns `BLOCKED`, create a focused fix card with the exact review failures and assign it to the original implementation worker/profile.

Do not attach the fix card as a child of the blocked review card unless you intend it to wait forever. A blocked parent keeps the child in `todo`. Either:
- create the fix card with no parent and include `Parent review: <id>` in the body, or
- if you accidentally parent it to the blocked review, immediately `unlink <blocked-review-id> <fix-card-id>` and dispatch.

The fix card must preserve scope: fix only review blockers, keep existing constraints, rerun gates, and return a review-required handoff. Then create or reuse a fresh GPT-5.5 review card for the fix output before final commit/push.

## When GPT-5.5 review is required

Require GPT-5.5 review for:
- code edits
- config edits
- deployments
- cron / Raid Timers
- services / gateways / systemd
- auth, security, billing, payments, POS/customer/inventory logic
- memory, skills, routing docs, or other durable future-behavior changes
- high-stakes business or system decisions

Do not automatically require GPT-5.5 review for simple research/scraping that only gathers public information. For research-only work, report source links, confidence, and official vs anecdotal distinction directly. If research edits a skill/routing doc or becomes a durable rule, review is required.

## Model routing defaults

- Coding / bug fixes: OpenCode Go `deepseek-v4-flash` by default.
- Coding fallback/escalation: `qwen3.6-plus`; use `deepseek-v4-pro` only for explicit heavy cases, repeated review failures, or Ayman approval.
- UI/product/frontend visual tasks: always `kimi-k2.6` unless Ayman explicitly overrides.
- Research / long docs / browser-use planning: `kimi-k2.6`.
- Memory curation / preference extraction / judgment triage: `glm-5.1`.
- Writing / report polish: `minimax-m2.7`.
- Final code/config/system review: `gpt-5.5`.

## Kanban commander behavior

The General monitors and routes. Do not burn GPT-5.5 doing routine worker labor. Keep the main chat free, report card IDs/status, and stop for Ayman's approval before side effects such as restarts, cron activation, deploys, service changes, or live config activation.
