# Reactive 429 Codex Rotation + Minimum Reset Lead

## Session Learning

A Codex quota-rotation fix can appear correct in proactive runtime selection but still fail during live `429` fallback.

Observed pattern:

```text
credential pool: marking <account> exhausted (status=429), rotating
credential pool: rotated to <farther-reset-account>
Credential 429 (rate limit) — rotated to pool entry [REDACTED]
```

Root cause: the reactive credential-pool path used `_select_unlocked()` after marking the current credential exhausted. That generic selector respects pool order / round-robin / priority, not Codex quota reset windows.

## Durable Fix Shape

Patch both paths:

1. Proactive path:
   - `hermes_cli/runtime_provider.py`
   - `CredentialPool.select_codex_by_quota()`
   - `agent.codex_quota.choose_codex_quota_candidate()`

2. Reactive path:
   - `agent/credential_pool.py::mark_exhausted_and_rotate()`
   - after `_mark_exhausted()` and `self._current_id = None`, if provider is `openai-codex` and quota rotation is enabled, compute available entries and call `choose_codex_quota_candidate(..., current_id='', fallback_to_first=False)`

## One-Hour Reset Lead Rule

Ayman corrected the rule: nearest reset must be useful, not merely nearest.

Eligibility rule:

```text
reset_at - now >= min_reset_lead_seconds
```

Default:

```yaml
codex_quota_rotation:
  min_reset_lead_seconds: 3600
```

This excludes accounts resetting in 10–15 minutes because there is not enough time to burn meaningful quota before reset.

## Lock Pitfall

`CredentialPool` uses `threading.Lock()`, not `RLock`.

Inside `mark_exhausted_and_rotate()` do **not** call public methods like `select_codex_by_quota()` if they acquire `self._lock`. That can deadlock. Instead, while already holding the lock:

- call `_available_entries(clear_expired=True, refresh=True)`
- pass those entries directly to `choose_codex_quota_candidate()`
- set `self._current_id = next_entry.id` if one is selected

## Strict Fallback Pitfall

Reactive quota-aware rotation should not blindly fall back to first account if all candidates fail the quota gates. Use a strict chooser mode such as `fallback_to_first=False` so too-soon or stale candidates are not chosen just because they are first in pool order.

If quota-aware selection itself raises unexpectedly, falling back to generic pool strategy is acceptable as a resilience path and should log debug context.

## Test Cases to Preserve

- account with reset in 15 minutes is excluded when `min_reset_lead_seconds=3600`
- account with reset in 75 minutes is eligible
- if only too-soon candidates exist and strict mode is active, chooser returns `None`
- reactive `mark_exhausted_and_rotate(status_code=429)` chooses quota-eligible nearest reset, not pool priority order
- runtime-provider test expectations include forwarding `min_reset_lead_seconds`

## Sanitized Inspection Fields

Safe fields to print:

- label
- selected boolean
- remaining percent
- reset timestamp
- reset lead minutes
- `reset_lead_eligible`
- `weekly_healthy`
- `stale_quota`
- status string

Do not print credential IDs, access tokens, refresh tokens, cookies, or auth store payloads.
