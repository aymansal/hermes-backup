# Temporary public preview tunnels

Use this when a local/Tailscale preview is working but Ayman needs to open it from a PC that is not on Tailscale.

## Situation

- Local preview server is already running and verified, for example `127.0.0.1:3001`.
- Tailscale URL works only on Tailscale devices.
- Public VPS IP may fail because cloud firewall/security lists block the port.
- Ayman approves a temporary public Gate for a static preview.

## Safe sequence

1. Verify the local preview first:

```sh
curl -sS -o /dev/null -w '%{http_code}\n' --max-time 5 http://127.0.0.1:<PORT>/
ss -ltnp '( sport = :<PORT> )'
```

2. Try public IP only if the server is already bound to `0.0.0.0`, but do not assume cloud firewall allows it.

3. If public IP fails, ask approval before exposing a temporary tunnel:

```text
This exposes the static preview publicly while the tunnel runs. Confirm before I open it.
```

4. Install/use `cloudflared` only after approval. Prefer the package matching architecture, then start in background under Hermes tracking:

```sh
cloudflared tunnel --url http://127.0.0.1:<PORT> --no-autoupdate --loglevel info --logfile /tmp/<name>-cloudflared.log
```

5. Extract and verify the URL:

```sh
grep -Eo 'https://[-a-zA-Z0-9.]+\.trycloudflare\.com' /tmp/<name>-cloudflared.log | tail -n1
curl -L -sS -o /tmp/<name>-tunnel-check.html -w '%{http_code}\n' --max-time 20 '<URL>/'
```

6. Tell Ayman:

- public URL;
- that anyone with the link can view it;
- how to close it later.

## Pitfalls

- Do not present a Tailscale IP as public internet access.
- Do not open cloud firewall rules blindly for throwaway previews; a temporary tunnel is usually cleaner.
- Do not leave the user thinking the prototype is production-secure. It is a public temporary preview Gate.
- If `cloudflared` produces no stdout in Hermes background tracking, use `--logfile` and parse the logfile for the trycloudflare URL.
