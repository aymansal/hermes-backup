---
name: codex-troubleshooting
description: Diagnose and fix Codex provider failures, SDK bugs, and fallback chain issues in Hermes
triggers:
  - Codex GPT-5.5 fails with cryptic errors
  - NoneType object is not iterable from openai-codex provider
  - ChatGPT Codex backend returns empty or malformed responses
  - Fallback chain breaks after Codex failure
  - Need to distinguish provider outage vs SDK code bug
---

# Skill Rune: Codex Troubleshooting

## Purpose
Quickly distinguish real Codex provider outages from OpenAI SDK bugs, apply targeted patches, and understand the fallback chain when Codex fails.

## Required Access Keys
- CODEX_API_KEY or ChatGPT OAuth token (for the Codex provider itself)
- Hermes read access to ~/.hermes/logs/ (agent.log, errors.log, gateway.log)

## Phase 1 — Read-Only Diagnosis

### Check the real error (not the sanitized gateway message)
The gateway's _sanitize_gateway_final_response replaces raw errors with "⚠️ The model provider failed after retries." Read the underlying logs directly:

```bash
grep "NoneType.*iterable\|TypeError" ~/.hermes/logs/agent.log | tail -20
grep -A 5 "API call failed" ~/.hermes/logs/errors.log | tail -40
```

### Distinguish provider outage vs SDK bug

| Symptom | Likely cause | Evidence |
|---------|-------------|----------|
| TypeError: NoneType object is not iterable | **OpenAI SDK bug** (code-level) | Line 61 in _parsing/_responses.py iterating response.output when it is None |
| HTTP 400: model_not_supported | Fallback provider rejection | GitHub Copilot or other fallback does not support the model name |
| HTTP 429 / rate limit | Genuine provider quota exhaustion | Headers show x-ratelimit-* or retry-after |
| HTTP 401 / auth failed | Expired credentials | resolve_codex_runtime_credentials fails or token expired |

## Phase 2 — Known SDK Bugs and Fixes

### Bug: ChatGPT Codex backend sends null output

**Affected:** OpenAI SDK ≤ 2.24.0 with api_mode=codex_responses via chatgpt.com/backend-api/codex

**Error:**
```
TypeError: 'NoneType' object is not iterable
```

**Root cause:** The ChatGPT Codex backend occasionally sends a response.completed SSE event where response.output is null instead of []. The SDK's parse_response() (line 61) does:

```python
for output in response.output:  # None → TypeError
```

**Fix (1-line patch to vendored SDK):**

Edit venv/lib/python3.11/site-packages/openai/lib/_parsing/_responses.py line 61:

```python
# BEFORE (broken)
for output in response.output:

# AFTER (fixed)
for output in (response.output or []):
```

**Alternative fix (Hermes-side guard in agent/codex_runtime.py):**
Wrap the run_codex_stream call to catch TypeError during streaming and fall back to run_codex_create_stream_fallback, mirroring the existing RuntimeError handling for missing response.completed.

## Phase 3 — Fallback Chain Behavior

When Codex fails, Hermes attempts fallback in this order (subject to config):
1. **Credential pool rotation** — next Codex account if pool is configured
2. **GitHub Copilot** — same model name, but Copilot only supports specific models (e.g. gpt-4, gpt-4o, not gpt-5.5 or claude-sonnet-4.6)
3. **OpenCode Go / other auxiliary provider** — e.g. glm-5.1, kimi-k2.5

**Pitfall:** If the fallback provider rejects the model name with model_not_supported, the user sees multiple "provider failed" messages stacked together. Check logs for the actual BadRequestError to see which fallback is rejecting what.

## Phase 4 — Verification After Fix

After patching, verify without restarting the gateway:
```bash
# Confirm the patch is in place
grep -n "response.output or \[\]" venv/lib/python3.11/site-packages/openai/lib/_parsing/_responses.py

# Test a single Codex call from the venv
source venv/bin/activate
python3 -c "
from openai import OpenAI
# ... use resolve_codex_runtime_credentials() or hardcode test key
"
```

## Phase 5 — Revival Stone (Rollback)
- The 1-line SDK patch is idempotent; reverting is the same edit in reverse.
- If the SDK is upgraded (e.g. pip install --upgrade openai), the patch may be overwritten. Re-apply after upgrade.

## Common System Alerts

### "database disk image is malformed" (kanban notifier)
This is **unrelated** to Codex. The kanban SQLite database at ~/.hermes/kanban/ is corrupted. See kanban-orchestrator skill for recovery (sqlite3 .recover, or delete and reinitialize).

### "Transient agent failure" repeated many times
If the gateway logs show Transient agent failure every turn, the provider is consistently failing. Check errors.log for the underlying error_type — TypeError means code bug, BadRequestError means config/model mismatch, APIConnectionError means network/credentials.
