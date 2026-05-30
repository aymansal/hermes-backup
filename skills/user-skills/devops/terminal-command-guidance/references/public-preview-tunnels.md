# Public Preview Tunnels for Non-Tailscale Devices

Use this reference when Ayman needs to view a local/dev/static preview from a machine that is not on Tailscale.

## When to use

- A preview server is already running locally or on a Tailscale-only URL.
- The user needs access from a public PC/device without Tailscale.
- Direct public IP access fails because the cloud firewall/security list blocks the port.
- The content is safe enough to expose temporarily, and the user explicitly approves a public tunnel.

## Safety doctrine

A public tunnel is an exposed Gate. Before opening it:

1. Verify the local service is healthy.
2. Check whether the service contains secrets, admin panels, private data, or production Core Crystal content.
3. Ask for explicit approval before installing tunnel tools or exposing a port publicly.
4. Tell the user that anyone with the tunnel URL can view it while the tunnel is running.
5. Keep it temporary; offer a clear close command/action.

Do not open public tunnels for production data, auth dashboards, private admin consoles, or credential-bearing apps without stronger access control.

## Read-only checks first

```sh
curl -sS -o /dev/null -w '%{http_code} http://127.0.0.1:<PORT>/\n' --max-time 5 http://127.0.0.1:<PORT>/
ss -ltnp '( sport = :<PORT> )' || true
command -v cloudflared || true
```

If testing direct public IP:

```sh
curl -sS https://ifconfig.me
```

Then ask the user to try:

```text
http://<PUBLIC_IP>:<PORT>/
```

If it fails, the cloud firewall/security list is likely blocking the public port even though the local service is alive.

## Local Next/Turborepo preview before tunnel

For pnpm workspace Next apps, start the preview with package filter arguments passed directly to the script. Do **not** insert an extra `--` after `dev`; with Next 15 this can be interpreted as a project directory named `--hostname`:

```sh
# Good
pnpm --filter @immopilot/web dev --hostname 0.0.0.0 --port 3000

# Bad: may fail with "Invalid project directory provided ... /apps/web/--hostname"
pnpm --filter @immopilot/web dev -- --hostname 0.0.0.0 --port 3000
```

Before exposing through Cloudflare, probe local routes and CSS:

```sh
curl -sS -o /tmp/local-page.html -w 'page HTTP %{http_code} bytes=%{size_download}\n' --max-time 20 http://127.0.0.1:<PORT>/app/payments/new
css=$(grep -o '/_next/static/css/[^" ]*\.css[^" ]*' /tmp/local-page.html | head -n1 || true)
[ -n "$css" ] && curl -sS -o /tmp/local.css -w 'css HTTP %{http_code} bytes=%{size_download}\n' --max-time 20 "http://127.0.0.1:<PORT>$css"
```

## Cloudflared quick tunnel pattern

Install only after approval. Choose the package matching architecture:

```sh
uname -m
```

For ARM64/aarch64 Ubuntu:

```sh
mkdir -p /tmp/cloudflared-install
cd /tmp/cloudflared-install
curl -L --fail --show-error -o cloudflared.deb \
  https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i cloudflared.deb
cloudflared --version
```

For x86_64/amd64 Ubuntu, use:

```sh
https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
```

Start the tunnel under managed background tracking. Prefer logging to a file because some cloudflared runs may not print the trycloudflare URL into the process output captured by the agent:

```sh
cloudflared tunnel --url http://127.0.0.1:<PORT> \
  --no-autoupdate \
  --loglevel info \
  --logfile /tmp/<name>-cloudflared.log
```

Then extract the URL:

```sh
grep -Eo 'https://[-a-zA-Z0-9.]+\.trycloudflare\.com' /tmp/<name>-cloudflared.log | tail -n1
```

## Verification

Verify the exact route the user will share, not only `/`. For app previews, also verify the CSS asset because a poisoned Next dev server can return HTML `200` while serving CSS `404` and appearing as plain HTML in the browser.

```sh
url="https://...trycloudflare.com"
curl -L -sS -o /tmp/tunnel-check.html -w '%{http_code}\n' --max-time 20 "$url/app/sales/new"
## Verification

Verify the exact route the user will share, not only `/`, and verify CSS/assets through the tunnel. A page can return HTTP 200 but look like raw HTML if the local Next dev server is serving stale HTML with missing `/_next/static/css/...` assets.

```sh
url="https://...trycloudflare.com"
route="/app/sales/new"
curl -L -sS -o /tmp/tunnel-check.html -w 'page HTTP %{http_code} bytes=%{size_download}\n' --max-time 20 "$url$route"
wc -c /tmp/tunnel-check.html
css=$(grep -o '/_next/static/css/[^" ]*\.css[^" ]*' /tmp/tunnel-check.html | head -n1 || true)
if [ -n "$css" ]; then
  curl -L -sS -o /tmp/tunnel-check.css -w 'css HTTP %{http_code} bytes=%{size_download}\n' --max-time 20 "$url$css"
else
  echo 'css not found'
fi
```

If the public tunnel shows raw/unstyled HTML, diagnose local first before blaming Cloudflare:

```sh
curl -sS -o /tmp/local-check.html -w 'local page HTTP %{http_code}\n' --max-time 10 http://127.0.0.1:<PORT>/<ROUTE>
css=$(grep -o '/_next/static/css/[^" ]*\.css[^" ]*' /tmp/local-check.html | head -n1 || true)
[ -n "$css" ] && curl -sS -o /tmp/local-check.css -w 'local css HTTP %{http_code}\n' --max-time 10 "http://127.0.0.1:<PORT>$css"
```

If local CSS is 404, the tunnel is forwarding correctly and the preview server is poisoned. Ask approval, then use the safe dev-server resummon reference: kill only the verified preview PIDs, clear `.next`, restart the dev server, then re-check local and tunnel CSS.

Optionally inspect the downloaded HTML for an expected product marker, without printing secrets:

```sh
python3 - <<'PY'
from pathlib import Path
s = Path('/tmp/tunnel-check.html').read_text(errors='ignore')[:5000]
print('contains_expected_marker=', 'ImmoPilot' in s)
PY
```

## Reporting to user

Report:

- Public tunnel URL.
- That HTTP verification passed.
- That it is temporary and public to anyone with the link.
- How to close it.

Example:

```text
Temporary public Gate is open:
https://example.trycloudflare.com

Verified: HTTP 200 and expected page marker present.
Anyone with the link can view it while this tunnel is running.
Say "Close prototype tunnel" when done.
```

## Closing the tunnel

Use the process/session manager when available, but always verify the actual `cloudflared` child process is gone afterward. A managed background session may kill only the wrapper shell while leaving the `cloudflared tunnel --url ...` child alive.

```sh
pgrep -a cloudflared
```

Then terminate only the tunnel PID/session that matches the preview URL/port. After termination, verify both process state and public URL failure:

```sh
pgrep -a cloudflared || true
python3 - <<'PY'
import urllib.request
url = 'https://<your-subdomain>.trycloudflare.com/<route>'
try:
    r = urllib.request.urlopen(url, timeout=8)
    print('UNEXPECTED', r.status)
except Exception as e:
    print('closed_or_unreachable', type(e).__name__, str(e)[:180])
PY
```

If the URL returns Cloudflare `530` or connection failure and `pgrep` is empty, the public Gate is sealed. Leave the local preview running unless the user explicitly asked to stop it too.


```sh
pgrep -af 'cloudflared tunnel --url http://127\.0\.0\.1:<PORT>' || true
# Replace <PID> with the exact PID shown above.
kill <PID>
sleep 2
pgrep -a cloudflared || true
```

Expected public check after closure is an unreachable/Cloudflare error such as HTTP 530. Keep the local preview server running unless the user explicitly asks to close it too.
