---
name: codex-operations
description: Operate, configure, diagnose, and troubleshoot the Hermes OpenAI Codex provider — credential pool, quota rotation, dashboard integration, SDK bug fixes, and fallback chain behavior.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, openai-codex, credential-pool, quota, dashboard, cron, troubleshooting, sdk-bugs, failover]
    created_by: agent
---

# Codex Operations

## Purpose

Use this Skill Rune when modifying, configuring, debugging, or troubleshooting Hermes' OpenAI Codex / ChatGPT provider. This covers:

- Credential pool management and account labeling
- Quota rotation, reset-window selection, and reactive 429/402 failover
- Dashboard Codex account cards and quota display
- Scheduled quota warmup cron jobs
- Diagnosing real provider outages vs SDK code bugs vs gateway sanitizer false positives
- Patching known OpenAI SDK bugs (NoneType iterable crashes)
- Understanding the Codex fallback chain

This skill consolidates the former narrow skills `codex-credential-pool-operations`, `codex-quota-rotation`, `codex-troubleshooting`, and `hermes-provider-diagnostics` into one class-level reference.

## Required Access Keys

- Hermes source checkout path, usually `~/.hermes/hermes-agent`
- Hermes auth state `~/.hermes/auth.json` (for credential pool inspection)
- `.env` for runtime keys (never print or store secrets)
- Do not print OAuth tokens, refresh tokens, cookies, raw auth headers, emails, or full credential IDs — use short id prefixes only

---

## Section 1: Credential Pool Operations

### Dashboard Codex Label Allocation

Bug pattern: using `label=f"Gpt{len(pool.entries()) + 1}"` creates duplicate labels after deleting an earlier slot. Example: existing `Gpt1`, `Gpt2`, `Gpt4` leads to another `Gpt4`.

Preferred fix — allocate lowest free slot:

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

Then use: `label=_next_codex_dashboard_label(pool.entries())`

Regression tests cover: fills gap (`Gpt1,Gpt2,Gpt4` → `Gpt3`), appends when no gap, ignores non-matching labels, case-insensitive, ignores `Gpt0`.

### Manual vs Auto Account Selection

Ayman's current policy: **manual dashboard selection is authoritative**. Do not implement, re-enable, or assume proactive Codex account auto-switching unless explicitly asked.

- Selecting an account in Shadow Realm sets `model.credential_id`; Hermes uses that exact account.
- `codex_quota_rotation.enabled` and `codex_quota_rotation.persist_runtime_switch` should remain `false` for manual mode.
- Reactive 429/402 handling must not silently persist or swap to another account while auto-switching is disabled.
- Dashboard API fallbacks must not auto-pick an `auto_candidate` when no account is selected.

### Safe Account Inspection

```bash
cd ~/.hermes/hermes-agent
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

See `references/codex-label-quota-warmup-2026-05.md` for the dashboard duplicate-label bug and warmup fix details.

### Metadata Repair Safety

Manual repair of `~/.hermes/auth.json` touches the Core Crystal. Ask Ayman before doing it. Recommended: backup with timestamp, change only the duplicate `label` field, verify with safe id prefixes.

---

## Section 2: Quota Rotation & Selection

### Configuration

Relevant `~/.hermes/config.yaml` keys:

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

### Selection Rule

A candidate account is eligible only if:
1. Quota cache is fresh enough
2. Selected quota window is above threshold
3. Weekly/secondary quota is not explicitly depleted
4. Selected reset window is at least **1 hour away** by real current time
5. Among eligible accounts, choose the nearest reset

Reason: an account resetting in 10–15 minutes is too close to use meaningfully.

### Read-Only Quota Ranking

```bash
python - <<'PY'
from hermes_cli.config import load_config
from agent.credential_pool import load_pool
from agent.codex_quota import rank_codex_accounts_by_quota, choose_codex_quota_candidate, codex_quota_rotation_config
from datetime import datetime, timezone

cfg = load_config()
model = cfg.get('model') or {}
selected = str(model.get('credential_id') or '')
rot = codex_quota_rotation_config(cfg)
pool = load_pool('openai-codex')
entries = pool.entries() if pool else []
ranked = rank_codex_accounts_by_quota(entries, current_id=selected, ...)
chosen, meta = choose_codex_quota_candidate(entries, current_id=selected, ...)
print('selected_id_present:', bool(selected))
print('rotation:', {k: rot.get(k) for k in sorted(rot)})
print('chosen_label:', getattr(chosen, 'label', None), 'reason:', meta.get('reason'))
for i, row in enumerate(ranked, 1):
    # ... print safe metadata only
    print(f"#{i} label={...} selected={...} above={...} reset_eligible={...}")
PY
```

### Quota Warmup Cron

Staggered warmup: wake one account per hour in Morocco time (09:00, 10:00, 11:00, 12:00). Use separate state keys per slot (`warmup_09_date`, `warmup_10_date`, etc.). Warmup timeout ~105s, quota refresh ~35s, total max ~140s per slot (within Hermes cron's ~3-minute limit).

If `hermes chat` lacks `--credential-id`, prefer a short-lived Python subprocess that loads an isolated credential pool and selects the target account directly. Avoid the older temporary `model.credential_id` config-mutation pattern — it can race with live gateway/dashboard config reads.

### Debugging Path

1. Inspect `codex_quota_rotation` config first.
2. Inspect ranking with sanitized output.
3. Check proactive vs reactive switch path.
4. Search Battle Traces for `credential pool: marking ... exhausted`, `rotated to ...`, `Credential 429`.
5. For warm-up failures, do NOT trust state-file "done" markers alone. Fetch live `/usage` for each explicit credential and compare reset windows.

See `references/codex-quota-staggered-warmup-2026-05.md`, `references/codex-quota-cron-reliability-hardening-2026-05.md`, `references/codex-quota-cron-slot-verification-2026-05.md` for session-specific details.

---

## Section 3: Provider Diagnostics & Troubleshooting

### Distinguishing Real Outage from Code Bug

| Symptom | Real Outage | Code Bug |
|---------|-------------|----------|
| Error type in logs | `APIError`, `AuthenticationError`, `RateLimitError` | `TypeError`, `AttributeError`, `KeyError` |
| HTTP status visible | 401, 429, 500, 503 | None — crash before HTTP response |
| Provider response time | May be slow/hanging | Fast — crashes immediately |
| Retry attempts | 1/3, 2/3, 3/3 with backoff | 1/3 then "Non-retryable client error" |

**Rule of thumb:** If the error type is `TypeError`, it is a code bug. Do not switch providers. Fix the code.

### Known SDK Bug: ChatGPT Codex null output

**Affected:** OpenAI SDK ≤ 2.24.0 with `api_mode=codex_responses` via `chatgpt.com/backend-api/codex`

**Error:** `TypeError: 'NoneType' object is not iterable`

**Root cause:** ChatGPT Codex backend occasionally sends `response.output = null` instead of `[]`. The SDK's `parse_response()` iterates `response.output` without null-guarding.

**Fix (1-line SDK patch):**
```bash
cd ~/.hermes/hermes-agent
SDK_FILE="venv/lib/python3.11/site-packages/openai/lib/_parsing/_responses.py"
BACKUP="${SDK_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$SDK_FILE" "$BACKUP"
sed -i 's/for output in response.output:/for output in (response.output or []):/' "$SDK_FILE"
python3 -m py_compile "$SDK_FILE"
```

Also patch related files that iterate `response.output`:
- `openai/types/responses/response.py` — `output_text` property
- `openai/types/responses/parsed_response.py` — `output_parsed` property

After patching, restart the gateway. If the SDK is later upgraded (`pip install --upgrade openai`), the patch may be overwritten — re-apply.

See `references/openai-sdk-nones.md` for the specific bug pattern and tracing.

### Gateway Sanitizer False Positive (Bug #28670)

The gateway's `_sanitize_gateway_final_response()` can replace **legitimate assistant answers** with "⚠️ The model provider failed after retries." if the answer text contains patterns like `HTTP 404` or `API call failed`.

Check if already fixed: look for the length guard in `gateway/run.py`:
```python
if len(body) > 400 or body.count("\n") > 4:
    return False  # Long answers are not false-positive replaced
```

If the guard is missing, the bug is present. Fix in `gateway/run.py`, not the SDK.

### Fallback Chain Behavior

When Codex fails, Hermes attempts fallback in order:
1. **Credential pool rotation** — next Codex account if pool is configured
2. **GitHub Copilot** — same model name (only supports specific models)
3. **OpenCode Go / other auxiliary provider** — e.g. `glm-5.1`, `kimi-k2.5`

**Pitfall:** If fallback provider rejects the model name with `model_not_supported`, stacked "provider failed" messages appear. Check logs for the actual `BadRequestError`.

### Reactive 429/402 Failover

When `mark_exhausted_and_rotate()` is called, it must use quota-aware selection (not pool priority/round-robin). Patch both proactive and reactive paths:
- Proactive: `runtime_provider.py` / `select_codex_by_quota()`
- Reactive: `CredentialPool.mark_exhausted_and_rotate()` — avoid deadlock by not calling public methods that re-acquire the same non-reentrant lock

See `references/reactive-429-min-reset-lead.md` for the session-specific root cause and patch map.

### Verification After Any Codex Change

```bash
cd ~/.hermes/hermes-agent
python -m pytest \
  tests/hermes_cli/test_dashboard_codex_labels.py \
  tests/hermes_cli/test_runtime_provider_resolution.py \
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

Dashboard changes also need `npm run build`.

---

## Section 4: Dashboard Integration

### Quota Display

For Codex quota in the dashboard and Telegram footer, use the `/usage` endpoint:
```
GET https://chatgpt.com/backend-api/codex/usage?client_version=1.0.0
```

Return only sanitized fields: `plan_type`, reset times, remaining percentages, `limit_reached`. Never return PII like `user_id`, `account_id`, or `email`.

Implementation pattern:
1. `fetch_live_codex_quota()` helper resolves OAuth credentials, calls `/usage`, parses safe fields.
2. `save_codex_quota_from_headers()` as best-effort fallback after successful model calls.
3. Dashboard endpoint `/api/model/quota` returns cached + live data with `live_fetch_failed` flag.
4. For Telegram footer, reuse the sanitized helper — do not create a parallel provider path.

### Account Cards

Dashboard-managed account cards should write `model.credential_id` on selection. Render accounts as compact click-to-select cards, not dropdowns. Existing live sessions may need `/reset` after account switch.

Never generate labels from `len(pool.entries()) + 1`. Allocate lowest unused `GptN` slot.

See `references/codex-dashboard-account-labeling.md` for the label-allocation bug and helper.

### Service Restarts

- Code changes in `hermes_cli/web_server.py` require `systemctl --user restart hermes-dashboard`.
- Cron script changes apply automatically at next run.
- Gateway restart needed only if gateway/Telegram footer code changed.
- Ask Ayman before restarting any service.

---

## Section 5: Warmup False Positives

Do NOT trust a state-file "done" marker or subprocess `OK` alone for warm-up verification. Fetch live `/usage` for each explicit credential ID and compare reset windows against the intended Morocco-time stagger.

The older pattern `AIAgent(..., credential_pool=isolated_pool)` may still use account #1 for slots #2/#3 because the Codex client path reloads/selects from the normal pool. Prefer direct credential selection or explicit `credential_id` targeting.

See `references/codex-warmup-false-pass.md` for the concrete false-PASS pattern and verification fix.

---

## Common System Alerts

- **Nearest reset picks a bad account:** check stale quota, below threshold, weekly depleted, or reset too close (under min_reset_lead_seconds).
- **Dashboard selected card differs from runtime:** ensure runtime switch persistence is enabled and dashboard polling refreshes account list, not just quota.
- **Reactive 429 ignores quota ranking:** patch `mark_exhausted_and_rotate()`.
- **TypeError NoneType:** SDK code bug, not provider outage — apply the 1-line patch.
- **Gateway sanitizer false positive:** check for length guard in `gateway/run.py`.
- **Warm-up cron says done but only first account reset moved:** treat as false PASS; verify each explicit credential with live `/usage`.
- **Database disk image malformed:** unrelated to Codex — kanban SQLite corruption; see kanban-orchestrator skill for recovery.
- **Transient agent failure repeated:** check `errors.log` for `error_type`; TypeError = code bug, BadRequestError = config mismatch, APIConnectionError = network/credentials.

---

## References

- `references/codex-label-quota-warmup-2026-05.md` — dashboard duplicate-label and all-account quota warmup fix
- `references/codex-quota-cron-slot-verification-2026-05.md` — cron slot verification details
- `references/codex-quota-staggered-warmup-2026-05.md` — staggered warmup schedule and implementation
- `references/codex-quota-cron-reliability-hardening-2026-05.md` — cron hardening against timeouts and races
- `references/codex-manual-selection-vs-auto-switching-2026-05.md` — manual selection doctrine and reactive path
- `references/codex-warmup-false-pass.md` — warm-up false-PASS pattern and verification fix
- `references/reactive-429-min-reset-lead.md` — reactive 429 failover and min reset lead-time
- `references/openai-sdk-nones.md` — ChatGPT null-output SDK bug pattern