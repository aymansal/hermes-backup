# OpenAI SDK `response.output = None` Bug Pattern

## Symptom

Hermes using `openai-codex` provider with model `gpt-5.5` (or any Codex model) fails with:

```
error_type=TypeError summary='NoneType' object is not iterable
```

Gateway shows: "⚠️ The model provider failed after retries."

## Root Cause

The **ChatGPT Codex backend** (`chatgpt.com/backend-api/codex`) changed its SSE stream format. It now sends `response.completed` events where `response.output` is `null` instead of `[]`.

OpenAI Python SDK version **2.24.0** (May 2025) has a bug in `lib/_parsing/_responses.py`:

```python
# Line ~61 — crashes when response.output is None
for output in response.output:
```

This is called from:
1. `agent/codex_runtime.py:run_codex_stream()` → `stream.get_final_response()`
2. → `ResponseStreamState.handle_event()` → `parse_response()`

## Affected SDK Versions

- **Confirmed broken:** 2.24.0 (Hermes default as of May 2026)
- **Likely fixed in:** 2.38.0+ (latest as of May 2026)
- **Hermes has NOT upgraded** — `pyproject.toml` still pins `openai==2.24.0`

## Files to Patch

All three files iterate `response.output` without a None guard:

1. `venv/lib/python3.11/site-packages/openai/lib/_parsing/_responses.py:61`
2. `venv/lib/python3.11/site-packages/openai/types/responses/response.py:315`
3. `venv/lib/python3.11/site-packages/openai/types/responses/parsed_response.py:100`

## Patch

```python
# Before (crashes)
for output in response.output:

# After (safe)
for output in (response.output or []):
```

Same change for `self.output` in the two property methods.

## Why Not Just Upgrade the SDK?

Upgrading `openai` from 2.24.0 → 2.38.0 may fix this, but it can also:
- Introduce new breaking changes in the Responses API streaming format
- Change default timeouts or retry behavior
- Break other Hermes code that depends on SDK internals

The 1-line patch is lower risk for a production gateway.

## Verification After Patch

```bash
# Compile check
python3 -m py_compile venv/lib/python3.11/site-packages/openai/lib/_parsing/_responses.py

# Restart gateway (Python caches imports in memory)
sudo systemctl restart hermes-gateway
```

Send a test message. The logs should show:
- `conversation turn: model=gpt-5.5` 
- `response ready:` without `error_type=TypeError`

## History

- **2026-05-27:** Discovered on Ayman's Hermes VPS. ChatGPT backend started sending `null` output arrays. Patched SDK 2.24.0 in-place with backups.
