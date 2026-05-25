---
name: codex-credential-pool-operations
description: "Operate Hermes OpenAI Codex credential-pool accounts, dashboard account labels, quota cache, and scheduled quota warmups safely."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [hermes, openai-codex, credential-pool, quota, dashboard, cron]
    related_skills: [hermes-agent, systematic-debugging, test-driven-development]
    created_by: agent
---

# Codex Credential Pool Operations

## Purpose

Use this Skill Rune when modifying or troubleshooting Hermes `openai-codex` credential-pool behavior: dashboard-added accounts, account selection, labels, live `/usage` quota cache, quota rotation, Telegram/dashboard quota displays, or cron warmup scripts.

This skill complements the protected `hermes-agent` skill. Load `hermes-agent` first for general Hermes CLI/repo guidance, then use this skill for Codex-account-specific operations.

## Required Access Keys / Config

- Existing Hermes source checkout path, usually `~/.hermes/hermes-agent`.
- Hermes auth state path, usually `~/.hermes/auth.json`.
- Any live Codex warmup/generation test consumes a small amount of quota and must be approved by Ayman first.
- Do not print OAuth tokens, refresh tokens, cookies, raw auth headers, emails, or account identifiers beyond short credential id prefixes.

## Read-only checks first

From the Hermes repo:

```bash
cd ~/.hermes/hermes-agent
git status --short
git branch --show-current
git diff -- hermes_cli/web_server.py agent/codex_quota.py
```

Inspect account metadata safely:

```bash
python - <<'PY'
import collections, json, pathlib
p = pathlib.Path.home() / '.hermes' / 'auth.json'
j = json.loads(p.read_text())
entries = ((j.get('credential_pool') or {}).get('openai-codex') or [])
labels = [str(e.get('label') or '') for e in entries if isinstance(e, dict)]
counts = collections.Counter(label.lower() for label in labels if label)
print('openai-codex entries:', len(entries))
for i, e in enumerate(entries, 1):
    print(f"#{i} id_prefix={str(e.get('id') or '')[:6]} label={e.get('label')!r}")
print('duplicate_labels=' + ','.join(sorted(k for k, v in counts.items() if v > 1)))
PY
```

## Dashboard Codex label allocation

Bug pattern: using `label=f"Gpt{len(pool.entries()) + 1}"` creates duplicate labels after deleting an earlier slot. Example: existing `Gpt1`, `Gpt2`, `Gpt4` leads to another `Gpt4`.

Preferred fix:

```python
_CODEX_DASHBOARD_LABEL_RE = re.compile(r"^gpt(\d+)$", re.IGNORECASE)


def _next_codex_dashboard_label(entries) -> str:
    """Return the lowest free GptN label for dashboard-added Codex accounts."""
    used: set[int] = set()
    for entry in entries:
        label = str(getattr(entry, "label", "") or "").strip()
        match = _CODEX_DASHBOARD_LABEL_RE.match(label)
        if not match:
            continue
        try:
            number = int(match.group(1))
        except ValueError:
            continue
        if number > 0:
            used.add(number)

    candidate = 1
    while candidate in used:
        candidate += 1
    return f"Gpt{candidate}"
```

Then use:

```python
label=_next_codex_dashboard_label(pool.entries())
```

Do not rename existing accounts automatically in this dashboard-login path. Existing-account refresh by fingerprint should preserve id and label.

## Regression tests for labels

Add focused tests covering:

- fills gap: `Gpt1`, `Gpt2`, `Gpt4` -> `Gpt3`
- appends when no gap
- ignores non-matching labels
- case-insensitive matching
- ignores `Gpt0` and invalid labels

Run:

```bash
python -m pytest tests/hermes_cli/test_dashboard_codex_labels.py -q -o 'addopts='
```

## Manual account selection vs auto-switching

Ayman's current policy: **manual dashboard selection is authoritative**. Do not implement, re-enable, or assume proactive Codex account auto-switching unless Ayman explicitly asks for it again.

Expected behavior:

- Selecting a ChatGPT/Codex account in the Shadow Realm sets `model.credential_id` and Hermes should use that exact account.
- Quota/reset metadata may be displayed for visibility, but must not silently change the selected account.
- `codex_quota_rotation.enabled` and `codex_quota_rotation.persist_runtime_switch` should remain `false` for manual mode.
- Proactive runtime provider resolution should call `pool.select_by_id(selected_credential_id)`, not `pool.select_codex_by_quota(...)`.
- Reactive Codex `429` / `402` / auth-refresh-failed handling should not silently persist or swap to another dashboard account while auto-switching is disabled; surface the selected account failure instead.
- Dashboard API fallbacks should not auto-pick an `auto_candidate` when no account is selected; deleting the selected account should clear selection rather than choosing another account behind Ayman's back.

Safe verification after touching this logic:

```bash
cd ~/.hermes/hermes-agent
python -m pytest \
  tests/hermes_cli/test_runtime_provider_resolution.py \
  tests/hermes_cli/test_codex_account_selection_dashboard.py \
  tests/agent/test_codex_quota_rotation.py \
  -q -o 'addopts='
python -m py_compile \
  agent/codex_quota.py \
  agent/credential_pool.py \
  agent/agent_runtime_helpers.py \
  hermes_cli/runtime_provider.py \
  hermes_cli/web_server.py \
  hermes_cli/config.py \
  run_agent.py
```

See `references/codex-manual-selection-vs-auto-switching-2026-05.md` for the session-specific root cause and patch map.

## Quota warmup / refresh scripts

For scheduled warmups, selected-account-only commands are insufficient:

```bash
hermes chat -q "Warmup ping. Reply exactly: OK" --provider openai-codex --model gpt-5.5
```

That only uses the globally selected `model.credential_id`.

Preferred staggered script behavior for Ayman's current quota formation:

- Enumerate every usable `credential_pool.openai-codex` entry from `auth.json` but return only safe metadata: `id`, `id_prefix`, `label`.
- Do **not** warm all accounts at the same hour; that overlaps all 5h quota windows and wastes quota.
- Wake one account per hour in Morocco time:
  - 09:00 → account #1 → expected reset around 14:00
  - 10:00 → account #2 → expected reset around 15:00
  - 11:00 → account #3 → expected reset around 16:00
  - 12:00 → account #4 → expected reset around 17:00
- For each slot, make one tiny generation call only for the assigned credential, then fetch live `/usage` for that same credential.
- Print safe lines only: slot, `label/id_prefix`, remaining percent, reset time, `live_failed`.
- Treat partial failure as retryable: print failures, return non-zero, and do not mark that slot date complete.
- Use separate state keys like `warmup_09_date`, `warmup_10_date`, etc.; old aggregate keys such as `warmup_date` must not block staggered slots.
- Harden against cron hard-kills: child process timeouts must leave margin under Hermes cron's ~3-minute run limit. Current pattern: warmup timeout about 105s, quota refresh timeout about 35s, max expected child time about 140s.
- If warmup fails, skip quota refresh for that account and print that it was skipped; this preserves time for the next cron tick retry inside the same 20-minute window.

If `hermes chat` lacks `--credential-id`, a practical fallback is a short-lived Python subprocess that temporarily sets `model.credential_id`, creates `AIAgent(provider='openai-codex', model='gpt-5.5', enabled_toolsets=['safe'], quiet_mode=True, skip_context_files=True, skip_memory=True)`, calls one warmup ping, and restores the original config in `finally`.

## Safe quota refresh verification

A read-only-ish live `/usage` check can verify all accounts without generation:

```bash
PYTHONPATH=. python - <<'PY'
from hermes_cli.auth import read_credential_pool
from agent.codex_quota import fetch_live_codex_quota

entries = read_credential_pool('openai-codex') or []
for e in entries:
    cid = e.get('id')
    label = e.get('label')
    if not cid or not e.get('access_token'):
        continue
    q = fetch_live_codex_quota(timeout_seconds=12.0, credential_id=cid)
    buckets = q.get('buckets') or []
    primary = next((b for b in buckets if b.get('label') == '5h' or b.get('key') == 'primary'), buckets[0] if buckets else {})
    print(label, cid[:6], 'remaining', primary.get('remaining_percent'), 'reset_at', primary.get('reset_at'), 'live_failed', q.get('live_fetch_failed', False))
PY
```

Watch for existing backoff logic in `agent.codex_quota.fetch_live_codex_quota`; dashboard polling may skip recently attempted unused accounts. A scheduled refresh script can use a short-lived subprocess and bypass only the local backoff check while still calling the real live `/usage` helper.

## Metadata repair safety

Manual repair of `~/.hermes/auth.json` touches the Core Crystal. Ask Ayman before doing it.

Recommended repair for duplicate labels:

1. Backup `auth.json` with a timestamp.
2. Change only the duplicate `label` field, not token fields.
3. Verify labels with safe id prefixes.

Example policy: keep the first duplicate as `Gpt4`, rename the later duplicate to the lowest free slot such as `Gpt3`.

## Restart / deployment

- Code changes in `hermes_cli/web_server.py` require a dashboard process restart to affect the Shadow Realm UI/API.
- Cron script changes at the same script path affect the next cron run automatically.
- Gateway restart is not needed unless gateway/Telegram footer code changed.
- Ask Ayman before restarting any service.

## References

- `references/codex-label-quota-warmup-2026-05.md` — condensed session detail for the dashboard duplicate-label and all-account quota warmup fix.