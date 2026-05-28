# Ayman preview gate and temporary public tunnel pattern

Use this when an Ayman Kanban raid produces a local web UI preview, especially ImmoPilot or Hermes dashboard work.

## Trigger

- A worker/reviewer has passed a frontend/UI card and the General is about to give Ayman a preview link.
- Ayman reports a screenshot that looks like raw/unstyled HTML.
- Ayman asks to view the local preview outside Tailscale.

## Preview link response style

When Ayman asks for a specific preview link, give exactly that link first and keep status minimal. Example: if he says "Just give me the Tailscale link", respond with the Tailscale URL(s) only or with one short label per URL. Do not include public tunnel links, long status summaries, or unrelated runtime/footer commentary unless he asked for status too.

## Preview verification before reporting success

A reviewer PASS means the diff met acceptance criteria; it does **not** prove the running dev server is healthy. Before reporting a frontend/UI card as inspectable, committing it for visual review, or answering Ayman's `Status?` after a UI worker/reviewer completed, verify the live route from the operator/default context. If the board says PASS but the route returns `500`, report the contradiction as `review PASS, live preview unhealthy`, read the dev Battle Trace, and fix/ask for a safe resummon before claiming the Gate is usable.

Before giving the link, verify the page and its critical CSS from the operator/default context:

```bash
curl -sS -o /tmp/preview.html -w 'route HTTP %{http_code}\n' http://127.0.0.1:<port>/<route>
css=$(python3 - <<'PY'
from pathlib import Path
import re
s = Path('/tmp/preview.html').read_text(errors='ignore')
print((re.findall(r'href="([^"]+\.css[^"]*)"', s) or [''])[0])
PY
)
printf 'css ref: %s\n' "$css"
[ -n "$css" ] && curl -sS -o /tmp/preview.css -w 'css HTTP %{http_code} bytes %{size_download}\n' "http://127.0.0.1:<port>$css"
```

If the HTML is `200` but the CSS is `404`, the app may display as raw unstyled HTML even though the route is alive. This happened with Next dev after repo changes: HTML referenced `/_next/static/css/app/layout.css`, but the file was absent until the dev shadow was resummoned and `.next` was rebuilt.

If the route returns `500` with a Next dev webpack-runtime error like `Cannot find module './613.js'`, treat it as a likely stale/corrupt `.next` chunk cache after route/component changes **only after** checking the error page/log. Do not commit or call the preview usable until a restart/cache rebuild restores both the list route and a representative dynamic route (for example `/app/projects` and `/app/projects/<placeholder-id>`).

## Safe fix for stale Next dev assets

This is a write/restart action, so ask Ayman first. If approved:

```bash
# stop the tracked Next/pnpm dev process for the app
kill <pnpm/next pids>

# only if approved and this is a local dev preview, not production
rm -rf apps/web/.next

pnpm --filter <web-package> dev --hostname 0.0.0.0 --port <port>
```

Then re-run the route + CSS probes. Report concrete evidence: route HTTP, CSS HTTP, CSS byte count, and whether expected page text appears.

## Starting an ImmoPilot dev preview on request

When Ayman says he cannot access ImmoPilot and asks to start the server, treat that as approval to start a local dev preview, but still stay read-only first and avoid restart/cache deletion unless separately approved.

Safe sequence:

1. Inspect whether a preview is already listening and whether a dev shadow exists:

```bash
ss -ltnp | grep -E ':3000|:3001|:5173' || true
ps aux | grep -E 'next dev|pnpm.*dev|immopilot' | grep -v grep || true
git status --short
node -e "const p=require('./apps/web/package.json'); console.log(p.name); console.log(p.scripts)"
```

2. If no server is listening, start it as a tracked background process from the repo root:

```bash
pnpm --filter @immopilot/web dev --hostname 0.0.0.0 --port 3000
```

Use the terminal/process background tracking rather than shell `&`, so the process can be polled or killed later.

3. Verify the port, a representative route, and critical CSS before claiming the Gate is open:

```bash
ss -ltnp | grep ':3000' || true
curl -sS -o /tmp/immopilot-preview.html -w 'route HTTP %{http_code}\n' http://127.0.0.1:3000/app/projects
css=$(python3 - <<'PY'
from pathlib import Path
import re
s=Path('/tmp/immopilot-preview.html').read_text(errors='ignore')
print((re.findall(r'href="([^"]+\.css[^"]*)"', s) or [''])[0])
PY
)
[ -n "$css" ] && curl -sS -o /tmp/immopilot-preview.css -w 'css HTTP %{http_code} bytes %{size_download}\n' "http://127.0.0.1:3000$css"
```

4. Return the Tailscale preview link with minimal evidence. For Ayman's VPS, use the known Tailscale host when applicable: `http://100.72.70.121:3000/app/projects`.

If `git status` shows worker changes while a Kanban card is active, report them as active raid traces, not as a blocker to starting the dev server. Do not commit, push, delete `.next`, or restart an existing server unless Ayman explicitly approves that extra action.

## Temporary outside-Tailscale preview

Ayman prefers temporary tunnels over public firewall ports for non-Tailscale prototype access. If `cloudflared` is installed, use a disposable tunnel and verify it end to end:

```bash
cloudflared tunnel --url http://127.0.0.1:<port> --no-autoupdate --loglevel info --logfile /tmp/<app>-cloudflared.log
# extract:
grep -Eo 'https://[-a-zA-Z0-9.]+\.trycloudflare\.com' /tmp/<app>-cloudflared.log | tail -n 1
```

Verify the public URL and CSS:

```bash
curl -L -sS -o /tmp/public-preview.html -w 'HTTP %{http_code} final %{url_effective}\n' "$URL/<route>"
# probe CSS the same way as local, using "$URL$css_ref"
```

Report the URL only after route and CSS return `200`. Make clear it is temporary, public, and should be closed when done. When Ayman says to close it, kill the cloudflared process and verify the tunnel no longer responds.

## Safety notes

- Do not open firewall ports for quick prototype viewing unless Ayman explicitly asks.
- Do not expose production/Core Crystal data through temporary tunnels.
- Do not leave unexplained public preview tunnels running; include the process/session identifier or a clear close instruction in the handoff.
- If the tunnel process connects but prints no URL to captured stdout, restart it with an explicit logfile and extract the `trycloudflare.com` URL from that file.
