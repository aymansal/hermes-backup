# Safe Dev Server Resummon Pattern

Session-derived pattern for restarting a local preview/dev server without breaking the wrong service.

## When to use

Use when the user asks to "resummon", restart, refresh, or bring back a dev/preview server, especially Next.js/Vite/Turbo/pnpm servers bound to a known port.

## Doctrine

Do not kill random `node` processes. Identify the exact listener and process tree first, then terminate only the dev-server PIDs tied to the target port.

## Read-only inspection

```sh
ss -ltnp '( sport = :3000 )' || true
ps -eo pid,ppid,cmd | grep -E 'next|vite|pnpm|turbo|<project-name>' | grep -v grep || true
git status --short
```

For a different port, replace `:3000` with the target port.

## Safe release sequence

1. Find the parent dev command and child server PIDs from `ss` and `ps`.
2. Send `TERM` to the identified parent first.
3. Re-check the port.
4. If child server PIDs remain bound to the same target port, send `TERM` only to those exact PIDs.
5. Do not escalate to `KILL` unless the user authorizes and the target PID/port has been verified again.

Example:

```sh
kill -TERM <parent_pid>
for i in $(seq 1 20); do
  if ss -ltnp '( sport = :3000 )' | grep -q ':3000'; then
    sleep 0.5
  else
    break
  fi
done
ss -ltnp '( sport = :3000 )' || true
```

If exact child PIDs remain:

```sh
kill -TERM <child_pid_1> <child_pid_2>
```

## Resummon under tracking

Prefer starting the replacement server with Hermes background process tracking rather than shell-level `nohup`, `&`, or `disown`, so future logs and lifecycle are visible.

Example command shape:

```sh
pnpm --filter <package> dev --hostname 0.0.0.0 --port 3000
```

## Verification gates

Verify the port listener and the expected HTTP routes before reporting success:

```sh
ss -ltnp '( sport = :3000 )' || true
curl -sS -o /dev/null -w 'local=%{http_code}\n' http://127.0.0.1:3000/
curl -sS -o /dev/null -w 'lan_or_tailscale=%{http_code}\n' http://<host-ip>:3000/
```

If the app has important route groups, verify representative routes too, e.g. `/platform` and `/app`.

## Reporting standard

Report reality first:

- Which PID/listener was stopped.
- Which command was used to restart.
- The current listener.
- Local and remote/Tailscale HTTP status codes.

Then mention the lesson: read-only scan first, exact PIDs only, tracked restart, verified route checks.
