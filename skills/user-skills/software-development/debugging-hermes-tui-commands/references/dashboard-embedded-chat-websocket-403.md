# Dashboard embedded chat: WebSocket 403 via non-loopback bind

## Symptom

The Shadow Realm / Hermes dashboard loads over HTTP, but the Chat tab immediately prints:

- `[session ended]`
- `events feed disconnected — tool calls may not appear`

The user cannot continue or initiate a chat session from the dashboard.

## Diagnostic pattern

The dashboard page can return `200 OK`, while the embedded chat fails because it uses WebSockets separately:

- `/api/pty` — PTY bridge for terminal chat
- `/api/events` — sidebar/tool-call event feed
- `/api/pub` — PTY child back-channel publisher

If those endpoints reject with HTTP 403, the page appears alive but the chat/session ends immediately.

Useful checks:

```bash
systemctl --user --no-pager --full status hermes-dashboard
ss -ltnp | grep -E ':(9119|<dashboard-port>)'
curl -sS -i --max-time 5 http://<host>:<port>/ | head -40
journalctl --user -u hermes-dashboard --no-pager -n 200
```

Then extract the injected session token from the dashboard HTML and probe the WebSockets with the Hermes venv Python, because the system Python may not have `websockets` installed:

```bash
/home/ubuntu/.hermes/hermes-agent/venv/bin/python - <<'PY'
import asyncio, re, urllib.request, urllib.parse, time
import websockets
host = '100.x.x.x'
port = 9119
html = urllib.request.urlopen(f'http://{host}:{port}/', timeout=5).read().decode('utf-8', 'replace')
token = re.search(r'__HERMES_SESSION_TOKEN__="([^"]+)"', html).group(1)
async def main():
    channel = 'probe' + str(int(time.time()))
    for endpoint in ['api/events', 'api/pty']:
        url = f'ws://{host}:{port}/{endpoint}?token={urllib.parse.quote(token)}&channel={channel}'
        try:
            async with websockets.connect(url, open_timeout=5, close_timeout=1):
                print(endpoint, 'open')
        except Exception as e:
            print(endpoint, type(e).__name__, str(e)[:200])
asyncio.run(main())
PY
```

## Root cause to check

In `hermes_cli/web_server.py`, `_ws_client_is_allowed()` allows loopback clients always, and all clients only when `_is_public_bind()` is true. `_is_public_bind()` historically returned true only for `0.0.0.0` or `::`.

That creates a mismatch when the dashboard is launched like:

```bash
hermes dashboard --host <tailscale-ip> --port 9119 --no-open --insecure --tui
```

The HTTP page loads on the Tailscale IP, but WebSocket endpoints still reject remote peers as non-loopback unless the bind host is `0.0.0.0` or `::`.

## Fix shape

Prefer a code/config fix that treats explicit `--insecure` non-local binds as intentionally public for WebSocket client checks, rather than changing the service to `0.0.0.0` unless the operator accepts broader exposure.

A safer implementation pattern is to store the allow-public decision on `app.state` in `start_server()` and have `_is_public_bind()` read that flag, e.g. `app.state.allow_public = allow_public`. This covers Tailscale-bound hosts without broadening the listen interface.

After patching, restart only the dashboard service and re-probe `/api/events` and `/api/pty` before declaring the Gate open.

## Safety note

Do not recommend `0.0.0.0 --insecure` as the first fix. The dashboard exposes sensitive config/API surfaces and has only ephemeral token auth. Prefer binding to Tailscale/private interface plus a code/config fix that allows that intended peer path.