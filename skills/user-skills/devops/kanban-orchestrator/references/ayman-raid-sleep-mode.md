# Ayman Raid Sleep Mode

Use this reference when Ayman says “let’s go sleep”, “let go sleep”, “put it to sleep”, or otherwise asks to let the server rest after a raid.

## Intent

Ayman wants nonessential power-consuming processes stopped while keeping Hermes reachable so he can message again tomorrow.

Do **not** shut down Hermes, the Telegram gateway, SSH, Tailscale, or the dashboard unless he explicitly asks for that destructive/service-affecting action.

## What to stop

After confirming there is no uncommitted work or active required worker/reviewer task that must keep running, stop nonessential raid shadows such as:

- project dev servers (`next dev`, Vite, local app servers),
- preview/static servers (`python3 -m http.server` on app/demo ports),
- temporary public tunnels (`cloudflared tunnel --url ...`) opened for preview,
- idle language-server helper processes spawned during the raid if not needed overnight,
- stale worker processes that are no longer associated with active cards.

## What to leave alive

Keep the communication and control plane alive:

- Hermes Telegram gateway / Comms Gate,
- Hermes dashboard / Shadow Realm if normally running,
- SSH/Tailscale/system networking,
- scheduled backups or other intentional always-on automations unless Ayman explicitly asks to pause them.

## Safe sequence

1. Check the board for active cards and the repo for uncommitted work.
2. If active worker/reviewer cards exist, report them and only stop if Ayman explicitly wants to interrupt.
3. Stop preview/dev/tunnel processes gracefully, then force-kill only the same matched PIDs if they remain.
4. Verify listening ports after cleanup.
5. Verify Hermes gateway/dashboard are still alive.
6. Report what was stopped, what remains alive, and whether the repo is clean.

## Reporting style

Keep the report short and calming:

- “Sleep mode engaged.”
- List stopped process classes, not a noisy PID dump.
- Confirm Hermes is still standing watch.

Avoid promising future work. The point is to end the raid cleanly.
