# Stuck worker diagnostics

Use this when a Kanban worker has been running much longer than expected or the user reports that the dashboard looks blocked/stale.

## What counts as evidence of a stuck worker

A worker is likely stuck when several of these are true at the same time:

- `hermes kanban show <task_id>` shows `running` for far longer than the card's expected scope.
- Events only show `claim_extended` with `reason: pid_alive`; `last_heartbeat_at` is `None` or stale.
- `hermes kanban log <task_id> --tail ...` has not changed for many minutes.
- The process is alive but mostly idle, for example `ps` shows low total CPU time, `STAT` sleeping, and wait channel like `futex_do_wait`.
- The last log lines are tool-preparation messages such as `preparing kanban_complete` with no completion/block event afterward.
- The repo has uncommitted files from the worker, but the card never transitions to done/blocked.

This is different from a worker that is actively running tests or builds: active workers have fresh logs, child processes with CPU/IO activity, or new card events.

## Read-only diagnostic sequence

Run these before deciding to interrupt:

```bash
hermes kanban --board <board> show <task_id>
hermes kanban --board <board> runs <task_id>
hermes kanban --board <board> log <task_id> --tail 260
ps -p <pid> -o pid,ppid,stat,etime,time,%cpu,%mem,wchan:30,cmd
pgrep -P <pid> -a
stat ~/.hermes/kanban/boards/<board>/logs/<task_id>.log
git -C <repo> status --short
git -C <repo> diff --stat
```

If the card affects a live dev preview, also check the route error separately. For Next.js dev servers, `ENOENT` under `.next/server/...` or missing CSS/vendor chunks can be stale cache rather than source-code failure.

## Safe recovery pattern

1. Report the evidence plainly to the user; do not just say the worker is "still running" if it is only alive by PID.
2. Ask before killing or reclaiming, unless the user has already authorized that exact recovery path.
3. Preserve worker-written files unless the user explicitly chose revert/cancel.
4. Reclaim/interrupt the worker, then run verification yourself or create a focused fix card with the exact failure.
5. Only promote to review after the route/build/test gates are healthy enough for a reviewer to inspect meaningful output.
6. Do not commit from a stuck worker's output until GPT-5.5 review returns PASS and the General verifies served routes/assets.

## Operator language

Good status line:

```text
The worker is alive but not progressing: PID exists, no heartbeat, log mtime stale, last line stuck at kanban_complete preparation.
```

Bad status line:

```text
Still running, probably fine.
```

The distinction matters: a living process is not always a working shadow.
