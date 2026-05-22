# Session lessons — Persona, operator profile, and Telegram setup

Date: 2026-05-21

## What happened

The user provided a long “Shadow System Operator” persona and expected it to become the actual Hermes soul. The assistant initially saved only a memory summary, then the user discovered `~/.hermes/SOUL.md` still contained the default template. The correct fix was to write the full persona into `~/.hermes/SOUL.md` and verify it.

The user then provided a long operator profile. The correct durable pattern was to preserve the full profile in `~/.hermes/OPERATOR_PROFILE.md` and keep `~/.hermes/memories/USER.md` compact for active loading.

When beginning Telegram setup, `hermes gateway setup` was difficult to drive through the terminal UI. Code inspection showed the gateway auto-enables Telegram when `TELEGRAM_BOT_TOKEN` exists in the environment/config. The practical fallback is to write the token to `~/.hermes/.env` without printing it, then install/start the gateway and verify.

The user later pasted the BotFather token directly and asked the assistant to do the setup. The successful path was to update `.env` programmatically with token redaction, set `GATEWAY_ALLOW_ALL_USERS=false`, chmod `.env` to 0600, feed both `hermes gateway install` prompts using `printf 'Y\nY\n'`, start the gateway, verify systemd service state, and verify the bot via Telegram `getMe` without printing the token.

## Durable user correction

The user explicitly corrected the assistant: “don’t do those sloppy half missions; do exactly what I ask.” For Hermes customization tasks, exact execution means changing the actual artifact and verifying it, not only saving memory or describing the plan.

The user also corrected the persona hierarchy: Ayman is the Shadow Monarch, not the Operator and not Lord. The assistant role can remain “Shadow System Operator” / Ignis, but the user-facing title and SOUL.md hierarchy should refer to Ayman as the Shadow Monarch. When this correction appears, update active memory, fact/Holographic memory if available, and `~/.hermes/SOUL.md`, then verify the remaining title references.

The user also wanted Holographic/local memory to become practically useful. The correct SOUL.md update is a “Feed the Shadow Archive” rule that tells Hermes to proactively save durable facts while avoiding memory pollution. Store preferences, stable business/project facts, environment details, chosen architecture/workflow decisions, reusable lessons, and important people/projects/tools/integrations. Do not store secrets, temporary task progress, raw logs, stale artifacts, or one-off chat noise. Procedures should become Skill Runes; human-readable business knowledge should go into Obsidian notes.

The user showed impatience when terminal instructions were too explanatory or when they accidentally typed `bash`/`sh` before commands. For command-help moments, give the exact command first, then explain only if needed.

## Commands and files

Soul/persona file:

```bash
cat ~/.hermes/SOUL.md
nl -ba ~/.hermes/SOUL.md
wc -l ~/.hermes/SOUL.md
head -5 ~/.hermes/SOUL.md
```

Operator profile files:

```bash
cat ~/.hermes/OPERATOR_PROFILE.md
cat ~/.hermes/memories/USER.md
wc -l ~/.hermes/OPERATOR_PROFILE.md ~/.hermes/memories/USER.md
```

Telegram gateway checks:

```bash
hermes gateway status
hermes config path
hermes config env-path
```

Telegram fallback path when the user will paste the token manually:

```bash
# Store TELEGRAM_BOT_TOKEN in ~/.hermes/.env without echoing it back.
hermes gateway install
hermes gateway start
sudo loginctl enable-linger $USER
hermes gateway status
```

Non-interactive install/start path after `.env` is configured:

```bash
printf 'Y\nY\n' | hermes gateway install
hermes gateway start
hermes gateway status
```

Troubleshooting logs:

```bash
grep -i "telegram\|error\|failed\|unauthorized\|allowed\|pair" ~/.hermes/logs/gateway.log | tail -80
journalctl --user -u hermes-gateway --no-pager -n 80
```

## Redacted token verification pattern

Use a script that reads `.env`, calls Telegram `getMe`, and prints only non-secret bot metadata:

```python
from pathlib import Path
import urllib.request, json
p = Path.home() / '.hermes/.env'
token = None
for line in p.read_text().splitlines():
    if line.startswith('TELEGRAM_BOT_TOKEN='):
        token = line.split('=', 1)[1].strip().strip('"\'')
        break
assert token
with urllib.request.urlopen(f'https://api.telegram.org/bot{token}/getMe', timeout=15) as r:
    data = json.loads(r.read().decode())
print('telegram_getMe_ok=', bool(data.get('ok')), sep='')
if data.get('ok'):
    print('bot_username=', data.get('result', {}).get('username', ''), sep='')
    print('bot_name=', data.get('result', {}).get('first_name', ''), sep='')
```

## Pairing / allowlist behavior

With `GATEWAY_ALLOW_ALL_USERS=false` and no `TELEGRAM_ALLOWED_USERS`, gateway warns that unauthorized users will be denied. For DMs, the intended operator flow is still to message the bot, receive a pairing code, then approve it:

```bash
hermes pairing approve telegram CODE_HERE
```

If no code appears, inspect gateway logs for `unauthorized`, `pair`, and `allowed`.

## Pitfalls

- Do not confuse persistent memory with `SOUL.md`; they are separate artifacts.
- Do not claim a persona/profile was installed unless the file was actually written and verified.
- For this persona stack, Ayman is the Shadow Monarch; do not address him as Operator or Lord after correction.
- When Holographic/local memory is enabled, SOUL.md should include a durable-fact storage rule, but it must also protect against storing secrets and stale/temporary noise.
- If the user asks for a command, provide the exact command first. Avoid over-explaining while they are trying to operate the terminal.
- Do not print Telegram bot tokens or other Access Keys back to the user.
- If the user pasted a real token into chat, recommend regenerating it after setup is confirmed, but still complete the requested setup unless they revoke permission.
- `hermes gateway setup` interactive selection may be unreliable through a PTY automation layer; direct `.env` configuration is the stable fallback, not a claim that the wizard is broken.
- When the user asks about the “native Hermes web UI”, distinguish it from Open WebUI. Native Hermes Web Dashboard is launched with `hermes dashboard` on `127.0.0.1:9119`; Open WebUI is a separate third-party frontend connected through Hermes API Server on `8642`. For the native dashboard, check `hermes dashboard --help/status`, verify port `9119`, and check optional deps `fastapi`, `uvicorn`, and `ptyprocess`. Prefer localhost plus SSH tunnel because the dashboard can read/write `.env` secrets and does not have strong standalone auth.
