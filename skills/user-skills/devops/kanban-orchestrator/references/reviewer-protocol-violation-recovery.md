# Reviewer protocol violation recovery

Use this when a reviewer appears to be running too long or the board shows a crash/protocol violation, but the logs contain a usable PASS/BLOCKED verdict.

## Trigger

- A reviewer run exits with `worker exited cleanly (rc=0) without calling kanban_complete or kanban_block`.
- The Kanban card may remain running or be automatically retried.
- The user asks why the review is taking so long.

## Recovery pattern

1. Inspect the review card and runs:
   ```bash
   hermes kanban show <review_task_id>
   hermes kanban runs <review_task_id>
   hermes kanban log <review_task_id> --tail 8000
   ```

2. If the log contains a clear reviewer verdict, treat that verdict as substantive even if the worker failed protocol.
   - Do not ignore a BLOCKED verdict just because `kanban_block` was not called.
   - Extract exact failures, evidence paths/lines, required fixes, tests run, and any security notes.

3. If a duplicate retry is still running and the existing verdict is sufficient, reclaim the stuck/retry review:
   ```bash
   hermes kanban reclaim <review_task_id> --reason "Reviewer produced verdict in log but failed Kanban protocol; recording verdict manually."
   ```

4. Record the verdict on the review card using `complete` only when you need the board lifecycle to advance to a fix iteration. In the result/summary, clearly state PASS or BLOCKED and mention the protocol violation.
   ```bash
   hermes kanban complete <review_task_id> \
     --result "BLOCKED. Reviewer verdict recovered from log after protocol violation. Exact failures: ..." \
     --summary "BLOCKED; protocol violation recovered manually; fix iteration spawned."
   ```

5. For BLOCKED reviews, create a new fix card assigned to the same worker profile that produced the failed implementation. Include the reviewer’s exact failures and acceptance criteria. Dispatch it.

6. Immediately inspect the board after dispatch. If completing a blocked review promoted deploy/restart/cron/activation children, reclaim/re-block them until a later PASS review.

## User reporting

Report plainly:

- The reviewer was not simply slow.
- It produced a verdict, but failed the Kanban completion/block protocol.
- The General recovered the verdict, recorded it, and routed fixes back to the worker.
- Give task IDs and current status.

Avoid saying the review passed or failed based only on status flags; use the log verdict as evidence.

## CLI notes

- `hermes kanban log <task_id> --lines N` is invalid.
- Use `hermes kanban log <task_id> --tail N`.
- If needed, pipe to shell tools outside the skill docs, but prefer native `--tail` in reusable instructions.
