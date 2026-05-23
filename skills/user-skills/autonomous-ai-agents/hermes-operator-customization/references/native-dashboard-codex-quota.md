# Native dashboard Codex quota display

Session lesson: when customizing the Hermes native dashboard Models page for Ayman's Shadow Realm, show ChatGPT/Codex quota as **remaining quota**, not used quota.

## Trigger

Use this reference when the user asks to add, debug, or adjust Codex/ChatGPT account quota display in the Hermes native dashboard.

## Durable behavior preference

- Display quota bars and percentages as remaining capacity, e.g. `87% left`.
- Do not show a bare percent; it is ambiguous.
- If showing used percent, keep it secondary/tooltip only, e.g. tooltip `13% used`.
- Poll live quota every 5 seconds while the Models page is open.

## Implementation pattern used

Backend:

- File: `agent/codex_quota.py`
- Prefer live Codex usage endpoint over stale response headers:
  - `https://chatgpt.com/backend-api/codex/usage?client_version=1.0.0`
- Use existing Hermes Codex auth resolver to refresh OAuth tokens when needed.
- Never expose or return tokens, user IDs, email, raw auth headers, or raw payloads.
- Return sanitized fields only:
  - `plan_type`
  - `source`
  - `captured_at`
  - `buckets[].used_percent`
  - `buckets[].remaining_percent`
  - `buckets[].reset_at`
  - `buckets[].reset_after_seconds`

Dashboard API:

- File: `hermes_cli/web_server.py`
- Route: `GET /api/model/quota`
- Should fetch live quota, cache sanitized fallback, and include active provider/model metadata.

Frontend:

- File: `web/src/pages/ModelsPage.tsx`
- Poll `api.getModelQuota()` every 5 seconds.
- Render each quota row using `remaining_percent`:
  - bar width = remaining percent
  - label = `${remainingPct}% left`
  - tooltip can show `${usedPct}% used`

## Gateway / Telegram footer timezone pitfall

The dashboard formats `reset_at` in the browser timezone, but Telegram runtime footers are rendered by the VPS gateway process. If the VPS timezone is UTC and Ayman's browser is UTC+1, the same quota reset timestamp can show one hour apart, e.g. dashboard `22:44` vs Telegram `21:44`.

Before patching, verify read-only:

```bash
date -Is
timedatectl | sed -n '1,8p'
/home/ubuntu/.hermes/hermes-agent/venv/bin/python - <<'PY'
from agent.codex_quota import load_cached_codex_quota
from gateway.runtime_footer import format_quota_footer
print(format_quota_footer(load_cached_codex_quota()))
PY
```

Preferred fix path: add/consume a configured footer timezone for Telegram (for example `display.platforms.telegram.runtime_footer.timezone: Europe/Vienna` or the timezone Ayman chooses) instead of relying on the VPS local timezone. Ask Ayman to choose the timezone and approve the code/config patch before editing or restarting the gateway.

## Verification commands

Run from repo root:

```bash
/home/ubuntu/.hermes/hermes-agent/venv/bin/python -m py_compile agent/codex_quota.py hermes_cli/web_server.py
cd web && npm run build
systemctl --user restart hermes-dashboard
systemctl --user is-active hermes-dashboard
/home/ubuntu/.hermes/hermes-agent/venv/bin/python - <<'PY'
import json, urllib.request
obj=json.loads(urllib.request.urlopen('http://100.72.70.121:9119/api/model/quota',timeout=15).read().decode())
print(json.dumps({
 'source': obj.get('source'),
 'buckets': [{k:b.get(k) for k in ['label','used_percent','remaining_percent']} for b in (obj.get('buckets') or [])],
 'live_fetch_failed': obj.get('live_fetch_failed')
}, indent=2))
PY
```

## Safety notes

- Do not print OAuth tokens or `auth.json` contents.
- The Codex `/usage` response can include email/user/account identifiers; never forward those to chat or UI.
- Restart only `hermes-dashboard` unless the change touches gateway behavior.
