# Kanban fast-status heartbeat doctrine

## Trigger
Use this reference when Ayman asks only:

- `Update?`
- `Status?`
- `Updates?`
- short equivalents during a Kanban raid

## Session signal
Ayman explicitly stopped the operator after a status request turned into ~12 minutes of extra work. His correction: he only asked for updates, not investigation.

## Rule
A status request is a heartbeat ping, not permission for a dungeon crawl.

Do only the smallest useful check:

1. `hermes kanban show <active_card>` or known review card.
2. Optional compact active board list for `running`, `blocked`, `todo`.
3. Stop and report.

Avoid unless Ayman says `Go`, asks for details, or the status cannot be answered otherwise:

- full logs/runs
- git diffs
- tests/builds/codegen
- route smoke
- creating fix cards
- dispatching reviewers
- committing
- reading large files

## Response shape
Keep it short and use Ayman's plain-English update format:

```text
## Update
One short sentence with the current state.

## Problem
Only include if blocked or risky; explain the real-world issue simply.

## What I did
1-3 bullets about worker/review/fix/push actions. Avoid raw commands and file paths unless needed.

## Next
One short sentence with the next gate.
```

Do not repeat the same fact in different words. Avoid developer jargon. Explain blockers like a business risk: “money could be visible without date limits,” “a fake tenant could be queried,” or “a button looked usable but did nothing.”

## Go means action
When Ayman replies `Go` after a proposed next move, execute that move directly and report the result. Examples:

- review-required worker blocked → mark worker done and dispatch reviewer.
- PASS review → run final gates and commit only the reviewed files.
- narrow blocker → create or perform the smallest same-scope fix and send to re-review.

## Kanban worker protocol salvage
If a worker is blocked with `worker exited cleanly (rc=0) without calling kanban_complete or kanban_block`, do not assume the task failed. This often means the worker did useful work but missed the Kanban handoff.

Fast salvage sequence:

1. Inspect only the minimal evidence needed:
   - `hermes kanban --board <board> log <task_id> | tail -160`
   - `git status --short`
   - `git diff --stat`
   - `git ls-files --others --exclude-standard`
2. If the log shows a final report and the files exist, complete the worker as `review-required handoff`, not PASS.
3. Start the existing reviewer.
4. If no usable code exists, reroute or ask for inline authorization.

This preserves momentum without bypassing review discipline.

## Blocked-parent re-review workaround
If a narrow fix is applied after a review card is `blocked`, a child re-review may stay `todo` because the blocked parent prevents promotion. In that case, create a dispatchable unparented re-review card whose body explicitly references the blocked review ID and the applied fix. After PASS, clean up the stale todo/blocked helper cards before committing.

## Inline fix exception
If a Kanban fix card cannot dispatch and the requested fix is tiny, low-risk, and already authorized inline, it is acceptable to patch directly. Still preserve review discipline:

1. inspect the exact file/range,
2. apply the minimal patch,
3. run relevant gates,
4. create/dispatch GPT-5.5 re-review,
5. do not commit until PASS.

## Pitfall
Do not answer a quick status with “I’ll check” and then spend minutes running gates. Report the heartbeat first; deeper work requires `Go` or explicit detail request.
