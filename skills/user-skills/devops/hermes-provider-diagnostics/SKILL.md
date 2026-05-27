---
name: hermes-provider-diagnostics
description: Diagnose and fix model provider failures in Hermes — distinguish real outages from SDK bugs, trace the code path, and patch safely.
trigger: "Hermes reports a provider failure, 'NoneType' object is not iterable, gateway sanitize false-positives, or any 'model provider failed after retries' message."
---

# Skill Rune: hermes-provider-diagnostics

## Purpose

When Hermes says a model provider failed, the failure can be:
1. A **real provider outage** (quota exhausted, rate limit, auth expired, backend down)
2. A **false-positive from the gateway sanitizer** (bug #28670 — already fixed in recent versions)
3. A **code bug in the OpenAI SDK or Hermes adapter** (e.g. SDK 2.24.0 `parse_response` crashing on `response.output = None`)

This skill provides the systematic diagnostic path to tell these apart and fix them without blind restarts or provider switching.

## Required Access Keys

None for diagnosis. For fixes:
- Hermes config at `~/.hermes/config.yaml` (read)
- `~/.hermes/logs/agent.log` and `~/.hermes/logs/gateway.log` (read)
- Hermes source checkout at `~/.hermes/hermes-agent` (read, sometimes write for patches)

## Assumptions

- Hermes gateway is running (or was running recently enough that logs exist)
- You have read access to `~/.hermes/logs/`
- You have read access to the Hermes source checkout

## Phase 1 — Inspect the Battle Traces

Always read the logs before guessing. The gateway message "⚠️ The model provider failed after retries" is a **summary**, not the root cause.

```bash
# Last 200 lines of the agent log
tail -n 200 ~/.hermes/logs/agent.log

# Search for the specific error
grep -n "NoneType.*iterable\|TypeError" ~/.hermes/logs/agent.log | tail -10

# Full traceback (if any)
grep -B 5 -A 30 "Traceback (most recent call last)" ~/.hermes/logs/agent.log | tail -80
```

**Key signals:**
- `error_type=TypeError` with `'NoneType' object is not iterable` → **SDK code bug**, not a provider outage
- `error_type=APIError` with HTTP 401/429/500 → **real provider error**
- `error_type=RuntimeError` with "Expected to have received `response.created`" → **backend prelude issue**, already handled by Hermes fallback
- `kanban notifier tick failed: database disk image is malformed` → **separate SQLite corruption**, unrelated to provider

## Phase 2 — Distinguish Real Outage from Code Bug

| Symptom | Real Outage | Code Bug |
|---------|-------------|----------|
| Error type in logs | `APIError`, `AuthenticationError`, `RateLimitError` | `TypeError`, `AttributeError`, `KeyError` |
| HTTP status visible | 401, 429, 500, 503 | None — crash before HTTP response |
| Provider response time | May be slow/hanging | Fast — crashes immediately on first event |
| Retry attempts in logs | 1/3, 2/3, 3/3 with backoff | 1/3 then "Non-retryable client error" |
| Model name in error | Same model each retry | May rotate through fallbacks |

**Rule of thumb:** If the error type is `TypeError`, it is a code bug. Do not switch providers. Fix the code.

## Phase 3 — Trace the Code Path

For `TypeError: 'NoneType' object is not iterable` on Codex (openai-codex provider):

1. The crash happens in `agent/codex_runtime.py` → `run_codex_stream()`
2. Which calls `stream.get_final_response()`
3. Which calls `ResponseStreamState.handle_event()` → `parse_response()`
4. In `openai/lib/_parsing/_responses.py`, line ~61:
   ```python
   for output in response.output:  # crashes when output is None
   ```
5. ChatGPT's backend now sends `response.output = null` on some `response.completed` events, but SDK 2.24.0 assumes it's always a list.

**Verify the SDK version:**
```bash
cd /home/ubuntu/.hermes/hermes-agent
source venv/bin/activate
python3 -c "import openai; print(openai.__version__)"
```

**Check upstream for the fix:** Newer SDK versions (2.38.0+) may have fixed this. Check `pip index versions openai`.

## Phase 4 — Apply the Fix (SDK Patch with Backup)

If upgrading the SDK is risky or not desired, patch the installed SDK directly. Always back up first.

```bash
cd /home/ubuntu/.hermes/hermes-agent
SDK_FILE="venv/lib/python3.11/site-packages/openai/lib/_parsing/_responses.py"
BACKUP="${SDK_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$SDK_FILE" "$BACKUP"

# Apply the guard
sed -i 's/for output in response.output:/for output in (response.output or []):/' "$SDK_FILE"

# Verify compile
python3 -m py_compile "$SDK_FILE"
```

**Also patch related files that iterate `response.output`:**
- `openai/types/responses/response.py` — `output_text` property
- `openai/types/responses/parsed_response.py` — `output_parsed` property

**Restart the gateway** after patching — Python caches imported modules in memory:
```bash
# If running under systemd
sudo systemctl restart hermes-gateway

# Or kill the gateway process and let it respawn
pkill -f "hermes.*gateway"
```

## Phase 5 — Verify

After restart, send a test message to the model that was failing. Check logs for clean `api_call succeeded` instead of `error_type=TypeError`.

```bash
tail -n 50 ~/.hermes/logs/agent.log | grep -E "error_type=|conversation turn:|response ready:"
```

## Phase 6 — Revival Stone (Rollback)

If the patch breaks something else, restore from backup:
```bash
cp venv/lib/python3.11/site-packages/openai/lib/_parsing/_responses.py.backup.* \
   venv/lib/python3.11/site-packages/openai/lib/_parsing/_responses.py
```

## Common False Positives

### Bug #28670 — Gateway Sanitizer Eats Valid Answers
The gateway's `_sanitize_gateway_final_response()` on Telegram can replace **legitimate assistant answers** with "⚠️ The model provider failed after retries" if the answer text contains patterns like `HTTP 404` or `API call failed`.

**Check if already fixed:** Look for the length guard in `gateway/run.py`:
```python
if len(body) > 400 or body.count("\n") > 4:
    return False  # Fixed: long answers are not false-positive replaced
```

If the guard is missing, the bug is present. The fix is in `gateway/run.py` — do not patch the SDK for this.

### Credential Pool Rotation
If the logs show fallback attempts through multiple models (gpt-5.4, claude-sonnet-4.6, etc.), the credential pool is rotating. This is normal after a provider failure, but the root cause is still upstream.

## References

- `references/openai-sdk-nones.md` — Specific bug pattern: ChatGPT backend sending `response.output = null` with SDK 2.24.0
