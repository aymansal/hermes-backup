# Ayman Hermes Ops Kanban Correction

## Trigger

Use this reference when Ayman asks for Hermes Agent, Shadow Realm, cron/Raid Timer, credential-pool, auth metadata, service restart, dashboard, gateway, or live-repo work that is likely to exceed ~90 seconds or touches durable system state.

## Lesson captured

In a Hermes Codex account-label + quota-warmup repair session, the operator initially used an inline local todo and performed implementation directly. Ayman challenged this because his standing rule is Kanban-first for >90-second/system/code/cron/auth-adjacent work. The correct pattern is to create Kanban cards before continuing, then report card IDs and phase changes.

## Correct raid pattern

1. Load relevant task skills first, then load `kanban-orchestrator` and Ayman's review doctrine reference.
2. Discover actual profiles with `hermes profile list`; do not invent assignees.
3. Split work into cards by operational gate, for example:
   - implementation/code patch card,
   - tests/verification card,
   - credential metadata repair card,
   - service restart/deploy card,
   - GPT-5.5 review card for high-stakes output.
4. For Ayman, code/config/cron/auth/service restart work needs explicit approval at the write/restart gate and GPT-5.5 review for durable changes.
5. Use safe summaries only for credential-adjacent work: labels and short ID prefixes are acceptable; never print tokens, emails, refresh tokens, cookies, raw auth headers, OAuth payloads, JWT claims, or full account identifiers.
6. Before editing auth metadata, create a backup and change only the approved metadata fields. Verify with sanitized output.
7. Before restarting services, identify the exact service/process and restart only the approved service. Verify status and endpoint health afterward. Do not restart unrelated Comms Gates.
8. Complete Kanban cards with concise PASS/BLOCKED summaries and metadata containing safe handles: task IDs, backup path, service name, endpoint status, and sanitized IDs only.
9. Final user report should include card IDs, what changed, verification results, what was intentionally not done, and any approval-required next options.

## Pitfall

A local `todo` list is useful for personal sequencing but does not satisfy Ayman's Kanban raid rule. If the task crosses the threshold, create board cards before doing more inline work.