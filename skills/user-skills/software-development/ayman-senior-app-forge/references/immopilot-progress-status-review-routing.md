# ImmoPilot progress/status and review-routing lessons

## Trigger
Use when Ayman asks short commands like `Update?`, `Go`, asks for a completion percentage, or when a Kanban worker returns `review-required` but dependent review cards are stuck behind a blocked parent.

## Status replies
- `Update?` should be a concise raid status, not a plan: current card, status, blockers, action already taken, next gate.
- If a worker is `blocked` only because it produced a `review-required` handoff, do **not** describe it as a product blocker. Treat it as a routing state.
- Say clearly: `handoff complete` is not approval.
- When moving a parent card to done to unlock a dependent review card, add a comment explaining: this unlocks review only, not code approval.

## Go replies
- `Go` means choose and dispatch the next sensible card/gate from repo + board truth.
- First check clean working tree and recent board state, then create worker + review cards with no forced skills if profile skill resolution is uncertain.
- Keep card bodies self-contained: doctrine paths, scope, safety rules, verification commands, output contract.

## Completion percentage replies
Do not report raw Kanban percentages as product truth.

Report both:
- raw board/card count percent, clearly labeled as inflated if many cards are reviews/fixes
- weighted MVP/product readiness estimate, based on remaining feature classes, wiring, review, final smoke, and risk

Example from the delivery-notes/dashboard phase:
- raw Kanban could show ~94% done
- honest MVP readiness was closer to ~80-82%, with ~18-20% remaining because dashboard/reporting, tenant isolation review, UI review, performance review, final smoke test, and unwired shells still carried weight

## Review doctrine reinforced
- Worker handoff ≠ done.
- Review PASS is required before final gates, commit, and push.
- If review blocks, spawn a focused fix card with exact failures and re-review.
- For UI shells, enabled no-op controls are blockers: controls must be genuinely functional or visibly disabled/non-misleading.
- For backend aggregations/dashboards, reject fake data and unbounded all-tenant scans; unavailable metrics should be honest/deferred.

## Evidence to include
For final PASS summaries, include:
- review card verdict
- gates run
- commit hash
- push target
- final git cleanliness

Do not save stale blocked review-card IDs in memory; those are session state, not durable doctrine.
