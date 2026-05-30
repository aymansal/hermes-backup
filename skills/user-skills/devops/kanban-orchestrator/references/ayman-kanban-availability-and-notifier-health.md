# Ayman Kanban availability and notifier health

Use this reference when orchestrating Ayman's Kanban raids from chat.

## Core lesson

For Ayman, Kanban exists so the main chat stays available. If the General has to sit in long polling loops or manually babysit worker completion, the workflow has failed even if the card eventually succeeds.

## Required behavior

When a worker/reviewer phase changes:
1. Report the phase change promptly.
2. If a worker blocks with `review-required`, inspect the handoff, complete it explicitly as `review-required, not PASS`, dispatch the dependent reviewer, and report the reviewer card id/status.
3. Do not sit in long inline polling loops. Use short status checks only when Ayman asks, or when a phase transition is expected imminently and the check will not occupy the chat for long.
4. If notifications are unreliable, treat that as a System Alert to fix, not as a reason to babysit manually forever.

## Notifier health check

If phase changes are not arriving automatically or the General is forced into manual polling, verify notification health:

```bash
hermes kanban --board <board> notify-list
```

If this throws `sqlite3.DatabaseError: database disk image is malformed`, the Kanban SQLite DB/notifier path is corrupted. The board may still partially work while notifications fail.

## Safe recovery pattern

Use the main `kanban-db-corruption-recovery.md` reference for exact recovery commands. The high-level order is:

1. Ask Ayman for approval before touching the Kanban Core Crystal or restarting Hermes gateway.
2. Back up the Kanban DB.
3. Run `PRAGMA integrity_check`.
4. Attempt SQLite `.recover` into a new DB.
5. Verify recovered DB with `PRAGMA integrity_check`.
6. Restart the Hermes gateway only after recovery succeeds and with approval.
7. After any gateway shutdown/restart interrupts the chat, immediately verify the gateway is active, run `notify-list`, check recent gateway logs for `malformed`/`notifier tick failed`, and report what completed before moving back to product work.

## Reporting wording

Use clear labels:
- `worker done as review-required, not PASS`
- `review running`
- `review PASS`
- `review BLOCKED`
- `committed/pushed`

Never imply that a review-required worker handoff is accepted work.
