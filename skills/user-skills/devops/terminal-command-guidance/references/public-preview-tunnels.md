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

```sh
url="https://...trycloudflare.com"
curl -L -sS -o /tmp/tunnel-check.html -w '%{http_code}\n' --max-time 20 "$url/"
wc -c /tmp/tunnel-check.html
```

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

Use the process/session manager when available, or identify the exact cloudflared PID before killing. Do not kill unrelated processes.

```sh
pgrep -a cloudflared
```

Then terminate only the tunnel PID/session that matches the preview URL/port.
