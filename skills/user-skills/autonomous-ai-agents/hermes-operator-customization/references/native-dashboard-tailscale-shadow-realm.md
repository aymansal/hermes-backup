# Native Hermes Shadow Realm Dashboard over Tailscale

Session-specific reference for Ayman's Hermes VPS setup.

## Naming

- Native Hermes web dashboard = Shadow Realm.
- Telegram gateway = Comms Gate.
- Holographic/local memory = Shadow Archive.
- VPS = Dungeon Core.

## Durable setup pattern

Use the protected `hermes-agent` skill for canonical commands, then follow the operator-customization skill for Ayman-specific discipline.

For the native dashboard, do not confuse it with Open WebUI. Native dashboard is launched by:

```bash
hermes dashboard
```

Default local URL:

```text
http://127.0.0.1:9119
```

Tailscale URL used in this setup:

```text
http://100.72.70.121:9119/
```

## Persistent systemd user service shape

A persistent dashboard service can live at:

```text
~/.config/systemd/user/hermes-dashboard.service
```

Example shape:

```ini
[Unit]
Description=Hermes Agent Native Web Dashboard
After=default.target

[Service]
Type=simple
WorkingDirectory=/home/ubuntu
Environment=HOME=/home/ubuntu
Environment=PATH=/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin
Environment=HERMES_DASHBOARD_TUI=1
ExecStart=/home/ubuntu/.local/bin/hermes dashboard --host 100.72.70.121 --port 9119 --no-open --insecure --tui
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

Enable/start:

```bash
systemctl --user daemon-reload
systemctl --user enable --now hermes-dashboard.service
```

Reboot survival needs user linger:

```bash
sudo loginctl enable-linger $USER
loginctl show-user "$USER" -p Linger
```

## Verification commands

```bash
systemctl --user is-enabled hermes-dashboard.service
systemctl --user is-active hermes-dashboard.service
ss -ltnp | grep ':9119\b' || true
curl -I http://100.72.70.121:9119/
```

Also verify Telegram and Tailscale if the user asks whether all gates survive reboot:

```bash
loginctl show-user "$USER" -p Linger --value
systemctl --user is-enabled hermes-gateway.service
systemctl --user is-active hermes-gateway.service
systemctl --user is-enabled hermes-dashboard.service
systemctl --user is-active hermes-dashboard.service
systemctl is-enabled tailscaled.service
systemctl is-active tailscaled.service
```

Expected successful durable state:

```text
Linger=yes
tailscaled.service enabled/active
hermes-gateway.service enabled/active
hermes-dashboard.service enabled/active
100.72.70.121:9119 listening
```

## Security notes

The native dashboard can read/write `config.yaml` and `.env`, including secrets. Binding to a Tailscale IP with `--insecure` is acceptable only when the user explicitly accepts Tailscale-only access. Do not expose it to public internet.

If the user is less certain, prefer localhost + SSH tunnel instead:

```bash
ssh -L 9119:127.0.0.1:9119 ubuntu@VPS_IP
```

## Communication lesson

If the user says the dashboard already works, do not continue troubleshooting. Confirm the Gate is open and explain persistence/reboot behavior clearly.
