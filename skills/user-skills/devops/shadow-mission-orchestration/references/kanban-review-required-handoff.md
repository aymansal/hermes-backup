# Kanban review-required handoff and stuck completion recovery

## When to use
Use this reference during Shadow Mission Orchestration when a Kanban worker has produced useful uncommitted work but is blocked, stuck, or unable to transition cleanly to review.

## Safe workflow
1. Inspect card status, run summary, log tail, and git diff/status.
2. If stuck at completion, verify evidence: stale log mtime, no heartbeat, sleeping/idle process, unchanged diff, and last line like `preparing kanban_complete`.
3. Preserve worker-written files unless Ayman explicitly asks to revert.
4. Complete/mark the worker card with a clear summary beginning: `Review-required handoff, not PASS:`.
5. Start or create the dependent GPT-5.5 review card.
6. Reviewer returns PASS/BLOCKED.
7. General verifies routes/gates/diff directly before commit.
8. If BLOCKED, create a same-worker fix card with exact reviewer failures.

## Summary template
```text
Review-required handoff, not PASS: <what worker changed>. Preserved uncommitted changes for GPT-5.5 review. No commit performed.
```

## Pitfalls
- A living PID is not proof of progress.
- A blocked `review-required` card is not a failed implementation; it is usually a review handoff.
- Do not commit from a worker self-report; require review and General verification first.
- Do not kill/reclaim worker processes without Ayman approval unless he has explicitly authorized that recovery.
