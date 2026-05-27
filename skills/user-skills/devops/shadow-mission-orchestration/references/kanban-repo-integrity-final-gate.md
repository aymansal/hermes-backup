# Kanban repo integrity and final-commit safety

## Trigger
Use this reference before final gates/commit in a Kanban coding raid, and whenever a worker/reviewer ran in scratch/worktree directories or the app dev server is running from a long-lived process.

## Why this exists
A Kanban raid can produce PASS-reviewed work while the live filesystem is not what it appears to be. In one ImmoPilot raid, the Next dev server was still serving from a deleted directory inode while `/home/ubuntu/immopilot` no longer contained a Git repo or package manifest. Final gates then failed with:

```text
No package.json found
fatal: not a git repository
/proc/<pid>/cwd -> /home/ubuntu/immopilot/apps/web (deleted)
```

The durable lesson is not that a specific repo is broken. The lesson is to add an integrity checkpoint before committing and to stop immediately if the Core Crystal path is damaged.

## Pre-commit integrity checkpoint
Before running final gates or `git commit`, verify from the intended workdir:

```bash
pwd
git rev-parse --show-toplevel
test -f package.json || test -f pnpm-workspace.yaml
git status --short
```

For a monorepo, the expected top-level path and manifest must match the mission brief. If `git rev-parse` fails, or the manifest is missing, do **not** run install/build/commit commands.

## Dev-server deleted-cwd check
If the app is reachable but source files look missing, inspect whether the dev server is serving from a deleted directory:

```bash
ps -eo pid,ppid,stat,etime,%cpu,%mem,cmd | grep -E 'next|pnpm|vite|turbo' | grep -v grep
readlink /proc/<pid>/cwd
```

A result like:

```text
/home/ubuntu/project/apps/web (deleted)
```

means the preview is temporary. Do not kill/restart it until source recovery is planned.

## If integrity fails
1. Stop the finalization path.
2. Report plainly: PASS-reviewed work may exist, but the repo path is damaged and no commit was created.
3. Do not claim the card is sealed.
4. Do not kill the live dev process if it is the only remaining preview.
5. Ask Ayman before restoration if restoring/replacing project files is required.
6. Recover from a verified source: Git remote, backup, known temp clone, or explicit user-approved snapshot.
7. Re-run gates from the restored repo before committing.

## Kanban cleanup caution
Do not close the only review/task records before final repo integrity is verified unless the cleanup itself is harmless and reversible. If cleanup already happened and commit fails, report that state exactly.

## Stale preview after a green build
Sometimes the code and build are good, but the long-running preview server is stale after `.next` output changes. Signature:

```text
pnpm build: PASS
fresh dev server on alternate port: route smoke PASS
current preview port: 500 / missing chunk / stale .next error
```

Do not confuse this with a failed implementation. Treat it as a preview-process resummon issue:

1. Report the code/reviewer verdict separately from preview health.
2. If final gates and a fresh dev server passed, it is safe to commit/push the code.
3. Tell Ayman the current preview is stale and ask for explicit approval before restarting/killing the preview process.
4. After approval, kill only the process bound to the preview port, restart from the verified repo root, and route-smoke the client path again.
5. Report the new process/session id and exact routes checked.

## Success criteria
- `git rev-parse --show-toplevel` returns the expected repo root.
- The package/workspace manifest exists at the expected root.
- `git status --short` shows the intended changed files only.
- Final gates run from that verified root.
- Commit hash is created only after the above checks pass.
- If preview was restarted, route smoke passes on the canonical preview port before saying the live Gate is open.
