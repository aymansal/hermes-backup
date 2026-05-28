# Ayman Kanban Update Cadence and BLOCKED Fix Loop

Use this when Ayman asks `Update?` during a Kanban raid, especially repo/code/config work with worker + GPT-5.5 review gates.

## Update? is an operational poll, not a prose request

When Ayman asks `Update?`, immediately inspect the relevant worker/reviewer cards before answering. Do not answer from memory if a Kanban state may have changed.

Minimum checks:

```bash
hermes kanban show <current_worker_or_reviewer_id> --json
hermes kanban list --status running --json
```

If the JSON shape or shell pipeline fails, retry with simpler parsing. Do not let a parsing error become the status update.

## Phase-change reporting

Report the real phase in concise terms:

- Worker `ready/running`: say which card is active and what gate it is working toward.
- Worker `blocked` with `review-required`: summarize worker handoff, explicitly say **not PASS**, then complete/unlock only if this is the established review-required handoff pattern.
- Reviewer `ready/running`: say GPT-5.5 review is the battle line; no commit/push yet.
- Reviewer `done` with PASS: run General final gates before commit/push.
- Reviewer `done`/summary `BLOCKED`: treat it as a real blocker; route the fix loop immediately before reporting if the fix scope is clear.

## BLOCKED review fix loop

When GPT-5.5 review returns `BLOCKED` with an exact finding:

1. Extract the blocking finding, files/lines, and reviewer `fix_prompt` from `hermes kanban show <review_id> --json`.
2. Create a new fix card assigned to the same implementer profile that produced the blocked output.
3. Create a dependent re-review card assigned to `default`/GPT-5.5.
4. If needed, mark the review-required or blocked handoff as complete only to unlock the intended dependent card, and make the completion summary explicit: `review-required handoff accepted; not PASS` or `BLOCKED verdict recorded; not PASS`.
5. Report to Ayman: blocker, fix card id, re-review card id, no commit/push.

Do not claim success or proceed to commit while the fix or re-review is pending.

## Good concise status shape

```markdown
## Update

Card X review came back BLOCKED.

Blocker:
- <plain-language issue>

Good news:
- <what reviewer confirmed is safe>

Next card:
- Fix: `<id>` — <worker>
- Re-review: `<id>` — GPT-5.5

No commit. No push until PASS.
```

## ImmoPilot/Convex example pattern

A financial backend review may pass tenant/security structure but block on data-validity details. Example: Convex `v.number()` can accept `NaN`/`Infinity`, so payment amount/date mutations need explicit finite-number checks, and required strings like void reasons should be rejected after trim. Route this as a same-worker fix, then GPT-5.5 re-review; do not bypass because all build gates passed.
