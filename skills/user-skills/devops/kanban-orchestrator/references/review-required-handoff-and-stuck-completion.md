# Kanban review-required handoff and stuck completion recovery

## When to use
Use this reference when a Hermes Kanban worker has produced useful uncommitted work but is blocked, stuck, or unable to transition cleanly to review.

## Pattern observed
A worker may:
- write valid changes,
- run some gates,
- leave a `review-required` comment/summary,
- block because it wants human/GPT-5.5 review,
- or freeze at `preparing kanban_complete` while files are already changed.

Do not treat this as PASS. Do not discard the diff automatically.

## Safe recovery workflow
1. Inspect the card status, run summary, log tail, and git diff/status.
2. If the worker is stuck at completion, verify evidence such as stale log mtime, no heartbeat, process sleeping, and unchanged repo diff.
3. Preserve worker-written files unless Ayman explicitly asks to revert.
4. Complete/mark the worker card with a clear summary beginning with `Review-required handoff, not PASS:`.
5. Start or create the dependent GPT-5.5 review card.
6. Reviewer returns PASS/BLOCKED.
7. If PASS, the General verifies routes/gates/diff directly before commit.
8. If BLOCKED, create a same-worker fix card with exact reviewer failures.

## Summary wording template
```text
Review-required handoff, not PASS: <what worker changed>. Preserved uncommitted changes for GPT-5.5 review. No commit performed.
```

## Stuck-worker evidence checklist
A worker is likely stuck, not just running, when several hold:
- card remains `running` far longer than expected,
- events only show `claim_extended` with `reason: pid_alive`,
- `last_heartbeat_at` is `None` or stale,
- log tail is stuck on a tool-preparation line such as `preparing kanban_complete`,
- log mtime has not changed,
- process is sleeping/idle with low CPU,
- repo has uncommitted changes from the worker.

## Pitfalls
- A living PID is not proof of progress.
- A blocked `review-required` card is not a failed implementation; it is usually a review handoff.
- Do not commit from a worker self-report; require review and General verification first.
- Do not kill/reclaim worker processes without Ayman approval unless an explicit prior command authorized that recovery.
