# ImmoPilot dev shadows: sleep and wake protocol

Session-derived reference for stopping and resuming ImmoPilot local development processes safely on Ayman's Hermes VPS.

## Trigger

Use when Ayman asks to:

- stop work for the night
- put the ImmoPilot dungeon to sleep
- resume what was stopped yesterday
- turn back on the local dev app
- verify that WARP stayed off

## Durable preference

Ayman prefers **Cloudflare WARP left off unless explicitly needed**. Do not turn WARP on as part of a normal ImmoPilot wake/resume flow. Keep Tailscale active because it is the normal safe preview route.

## Sleep protocol

Before stopping anything, inspect first:

```bash
printf 'ports=\n'
ss -ltnp | grep -E ':(3000|3001|3210|3211|6791)\b' || true
printf '\nimmopilot_processes=\n'
ps -ef | grep -E 'immopilot|next dev|next-server|convex dev|node.*convex' | grep -v grep || true
printf '\nwarp=\n'
systemctl is-active warp-svc.service 2>/dev/null || true
printf '\ntailscale=\n'
systemctl is-active tailscaled.service 2>/dev/null || true
```

Stop only the known ImmoPilot dev processes and Convex spawned children. Do not kill unrelated Node processes unless verified. Stopping or restarting system services still needs Ayman approval.

Expected sleep state:

```text
ports 3000/3001/3210/3211/6791: quiet
ImmoPilot dev processes: none
WARP: inactive
Tailscale: active
```

## Wake protocol

Read-only scan first:

```bash
cd /home/ubuntu/immopilot
pwd
test -f package.json && node -e "const p=require('./package.json'); console.log(p.scripts)"
ss -ltnp | grep -E ':(3000|3001|3210|3211|6791)\b' || true
ps -ef | grep -E 'immopilot|next dev|next-server|convex dev|node.*convex' | grep -v grep || true
systemctl is-active warp-svc.service 2>/dev/null || true
systemctl is-active tailscaled.service 2>/dev/null || true
```

Start Convex dev in one tracked background process:

```bash
cd /home/ubuntu/immopilot
pnpm convex:dev
```

Start Next.js in a separate tracked background process:

```bash
cd /home/ubuntu/immopilot
pnpm --filter @immopilot/web dev --hostname 0.0.0.0 --port 3000
```

Then verify:

```bash
ss -ltnp | grep -E ':(3000|3001|3210|3211|6791)\b' || true
ps -ef | grep -E 'immopilot|next dev|next-server|convex dev|node.*convex' | grep -v grep || true
curl -I --max-time 10 http://127.0.0.1:3000
curl -I --max-time 10 http://100.72.70.121:3000
systemctl is-active warp-svc.service 2>/dev/null || true
```

Expected wake state:

```text
Next.js: listening on 0.0.0.0:3000
Local route: HTTP 200 OK
Tailscale route: HTTP 200 OK
Convex dev process: running
WARP: inactive
Tailscale: active
```

Report the process IDs if started via Hermes background tools, and give Ayman the preview URL:

```text
http://100.72.70.121:3000
```

## Blank page / Next dev cache corruption recovery

Use this when Ayman reports the Tailscale preview is a blank page, or when Next dev logs show errors like:

```text
Cannot find module './<chunk>.js'
Could not find ... segment-explorer-node.js#SegmentViewNode in the React Client Manifest
__webpack_modules__[moduleId] is not a function
GET / 500
```

Read-only diagnosis first:

```bash
cd /home/ubuntu/immopilot
curl -sS -D - http://127.0.0.1:3000/ -o /tmp/immopilot_home.html | sed -n '1,40p'
curl -sS -D - http://100.72.70.121:3000/ -o /tmp/immopilot_home_ts.html | sed -n '1,40p'
# inspect the tracked web process log if Hermes started it
```

If local and Tailscale both return HTTP 500 with chunk/module errors, the likely root cause is stale/corrupted `apps/web/.next` from hot reload or concurrent build/edit cycles. This is a generated cache, not the Core Crystal.

Because this kills a dev process and deletes a directory, ask Ayman for explicit approval before proceeding. After approval:

```bash
# release only the tracked web dev process, not Convex and not unrelated Node processes
rm -rf apps/web/.next
pnpm --filter @immopilot/web dev --hostname 0.0.0.0 --port 3000
```

Verify before reporting success:

```bash
curl -sS -D - http://127.0.0.1:3000/ -o /tmp/immopilot_after_resummon.html | sed -n '1,30p'
curl -sS -D - http://100.72.70.121:3000/ -o /tmp/immopilot_after_resummon_ts.html | sed -n '1,30p'
python3 - <<'PY'
from pathlib import Path
for path in ['/tmp/immopilot_after_resummon.html', '/tmp/immopilot_after_resummon_ts.html']:
    text = Path(path).read_text(errors='replace')
    print(path, 'has_ImmoPilot=', 'ImmoPilot' in text, 'has_500=', 'statusCode":500' in text or 'Internal Server Error' in text)
PY
```

Expected result:

```text
HTTP 200 OK locally and over Tailscale
has_ImmoPilot=True
has_500=False
```

## Pitfalls

- A delayed background notification like `Ready` may arrive after the server was already stopped. Treat it as stale until you re-check ports and processes.
- Do not wake WARP during normal resume. The correct normal network path is Tailscale.
- Do not claim the app is live until both local and Tailscale HTTP checks return success.
- Keep Convex and Next.js as separate tracked processes so either shadow can be inspected or released independently.
- If `pnpm build` passes but dev preview is blank/500, inspect the dev process log; the production build cache and the dev server cache can disagree.
