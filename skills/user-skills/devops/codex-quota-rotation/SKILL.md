---
name: codex-quota-rotation
description: Operate and debug Hermes OpenAI Codex credential-pool quota rotation, reset-window selection, reactive 429 failover, and dashboard sync.
version: 1.0.0
author: Hermes Agent
tags: [hermes, codex, quota, credential-pool, failover, dashboard]
created_by: agent
---

# Codex Quota Rotation

## Purpose

Use this Skill Rune when working on Hermes OpenAI Codex / ChatGPT account quota rotation, especially when multiple Codex OAuth accounts exist in the credential pool and Hermes must choose which account to use next.

This covers:

- proactive runtime account selection
- reactive `402` / `429` credential-pool failover
- quota reset-window ranking
- minimum reset lead-time rules
- persisted runtime switches to `config.yaml`
- Shadow Realm / Models page selected-account sync

## Required Access Keys / Config

Do not print or store secrets.

Relevant non-secret config lives in `~/.hermes/config.yaml`:

```yaml
model:
  provider: openai-codex
  credential_id: <selected credential id>

codex_quota_rotation:
  enabled: true
  threshold_percent: 5
  window_key: primary
  max_quota_cache_age_seconds: 900
  persist_runtime_switch: true
  prefer_reset_ending_soonest: true
  min_reset_lead_seconds: 3600
```

Secrets and OAuth tokens live in auth state / `.env`; never echo them.

## Operator Rule

For Ayman's Hermes setup, nearest reset is not enough by itself.

A candidate account is eligible only if:

1. quota cache is fresh enough,
2. selected quota window is above threshold,
3. weekly/secondary quota is not explicitly depleted,
4. selected reset window is at least **1 hour away** by real current time,
5. then, among eligible accounts, choose the nearest reset.

Reason: an account resetting in 10–15 minutes is too close to use meaningfully, even if it is technically the nearest reset.

## Safe Read-Only Checks

Run checks that redact IDs/tokens. Print labels and booleans, not credential values.

```bash
python - <<'PY'
from hermes_cli.config import load_config
from agent.credential_pool import load_pool
from agent.codex_quota import rank_codex_accounts_by_quota, choose_codex_quota_candidate, codex_quota_rotation_config
from datetime import datetime, timezone
import time

cfg = load_config()
model = cfg.get('model') or {}
selected = str(model.get('credential_id') or '')
rot = codex_quota_rotation_config(cfg)
pool = load_pool('openai-codex')
entries = pool.entries() if pool else []
ranked = rank_codex_accounts_by_quota(
    entries,
    current_id=selected,
    threshold_percent=rot.get('threshold_percent', 5),
    window_key=rot.get('window_key', 'primary'),
    prefer_reset_ending_soonest=rot.get('prefer_reset_ending_soonest', True),
    max_quota_cache_age_seconds=rot.get('max_quota_cache_age_seconds', 0),
    min_reset_lead_seconds=rot.get('min_reset_lead_seconds', 0),
)
chosen, meta = choose_codex_quota_candidate(
    entries,
    current_id=selected,
    threshold_percent=rot.get('threshold_percent', 5),
    window_key=rot.get('window_key', 'primary'),
    prefer_reset_ending_soonest=rot.get('prefer_reset_ending_soonest', True),
    max_quota_cache_age_seconds=rot.get('max_quota_cache_age_seconds', 0),
    min_reset_lead_seconds=rot.get('min_reset_lead_seconds', 0),
)
print('provider:', model.get('provider'))
print('selected_id_present:', bool(selected))
print('rotation:', {k: rot.get(k) for k in sorted(rot)})
print('entries:', len(entries))
print('chosen_label:', getattr(chosen, 'label', None), 'reason:', meta.get('reason'))
for i, row in enumerate(ranked, 1):
    entry = row['entry']
    reset = row.get('reset_at')
    lead = row.get('reset_lead_seconds')
    reset_s = datetime.fromtimestamp(reset, timezone.utc).isoformat() if reset else None
    print(f"#{i} label={getattr(entry,'label','')} selected={row.get('selected')} above={row.get('above_threshold')} reset_eligible={row.get('reset_lead_eligible')} weekly_ok={row.get('weekly_healthy')} stale={row.get('stale_quota')} rem={row.get('remaining_percent')} reset={reset_s} lead_min={None if lead is None else round(lead/60,1)} status={row.get('quota_status')}")
PY
```

## Debugging Path

1. Inspect `codex_quota_rotation` config first.
2. Inspect current ranking with sanitized output.
3. Check whether the switch was proactive or reactive:
   - proactive path: `runtime_provider.py` / `select_codex_by_quota()`
   - reactive path: `CredentialPool.mark_exhausted_and_rotate()` after live `402` / `429`
4. Search Battle Traces for:
   - `credential pool: marking ... exhausted`
   - `credential pool: rotated to ...`
   - `Credential 429`
   - `Credential 402`
5. If logs show reactive rotation, verify that reactive path also uses quota-aware selection. A common pitfall is fixing proactive selection only while reactive `429` still uses pool priority / round-robin.
6. For scheduled Codex warm-up failures, do **not** trust a state-file "done" marker or a subprocess `OK` alone. Fetch live `/usage` for each explicit credential id and compare reset windows against the intended Morocco-time stagger before declaring success. See `references/codex-warmup-false-pass.md`.

## Patch Pattern

- `agent/codex_quota.py`
  - ranking and candidate eligibility
  - include `min_reset_lead_seconds`
  - include non-secret row metadata like `reset_lead_seconds` and `reset_lead_eligible`

- `agent/credential_pool.py`
  - reactive `mark_exhausted_and_rotate()`
  - when provider is `openai-codex` and quota rotation is enabled, call the quota chooser after marking the failed account exhausted
  - avoid deadlock: this method already holds `self._lock`; do not call public methods that re-acquire the same non-reentrant lock

- `hermes_cli/runtime_provider.py`
  - proactive runtime selection must pass every quota-rotation option into `select_codex_by_quota()`
  - persist switch if `persist_runtime_switch` is enabled

- `web/src/pages/ModelsPage.tsx`
  - if runtime switches are persisted, dashboard polling should refresh both quota and Codex account list so the selected card follows reality

## Verification

Targeted tests:

```bash
/home/ubuntu/.hermes/hermes-agent/venv/bin/python -m pytest \
  tests/agent/test_codex_quota_rotation.py \
  tests/hermes_cli/test_runtime_provider_resolution.py \
  -q -o 'addopts='
```

Compile check:

```bash
/home/ubuntu/.hermes/hermes-agent/venv/bin/python -m py_compile \
  agent/codex_quota.py \
  agent/credential_pool.py \
  hermes_cli/runtime_provider.py \
  hermes_cli/web_server.py \
  run_agent.py
```

Dashboard changes need:

```bash
npm run build
```

## Restart / Safety

- Code changes do not affect the running Telegram gateway until the gateway is restarted.
- Ask before restarting Comms Gate or dashboard unless the user has already explicitly approved.
- Prefer read-only status checks first:

```bash
systemctl --user is-active hermes-gateway
systemctl --user status hermes-gateway --no-pager -n 50
```

If restarting from the gateway conversation itself, consider delayed restart so the current response can finish:

```bash
systemd-run --user --unit=hermes-gateway-delayed-restart --on-active=2s /bin/systemctl --user restart hermes-gateway
```

## Common System Alerts

- **Nearest reset picks a bad account:** check whether the account is stale, below threshold, weekly depleted, or below the 1-hour reset lead-time.
- **Dashboard selected card differs from runtime:** ensure runtime switch persistence is enabled and dashboard polling refreshes Codex accounts, not quota only.
- **Reactive 429 ignores quota ranking:** patch `mark_exhausted_and_rotate()`; proactive ranking fixes alone are insufficient.
- **Warm-up cron says done but only first account reset moved:** treat it as a false PASS. Verify each explicit credential with live `/usage`; the warm-up call should use the target token directly and only mark the slot done after the expected reset window is observed. Do not assume `AIAgent(..., credential_pool=isolated_pool)` forces the target Codex account — the Codex client path may reload/select from the normal pool and still use account #1 for #2/#3 slots.
- **Deadlock after patch:** likely called `select_codex_by_quota()` while already holding `CredentialPool._lock`. Use quota chooser directly on available entries inside the locked section instead.

## Reference Notes

- Session-specific implementation detail: `references/reactive-429-min-reset-lead.md`
- Codex warm-up false PASS and direct-token verification pattern: `references/codex-warmup-false-pass.md`
