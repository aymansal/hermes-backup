# Reusing Shadow Realm quota in gateway footers

When a user asks for Telegram/Discord/etc. replies to show the same provider quota as the Shadow Realm, do not create a second quota implementation. Reuse the dashboard's sanitized quota path.

## Relevant code paths

- `agent/codex_quota.py`
  - `fetch_live_codex_quota(timeout_seconds=...)` fetches live ChatGPT/Codex quota and falls back to cached sanitized quota on failure.
  - `load_cached_codex_quota()` reads the cached sanitized quota from auth state.
  - Returned data must not include tokens, email, account id, user id, cookies, or raw auth headers.
- `hermes_cli/web_server.py`
  - `/api/model/quota` is the Shadow Realm endpoint.
- `gateway/runtime_footer.py`
  - Defines footer fields and rendering. Add new safe fields here, e.g. `quota`.
- `gateway/run.py`
  - Calls `build_footer_line(...)` after the agent turn and appends/sends the footer.

## Safe implementation pattern

1. Inspect first:
   - `gateway/runtime_footer.py`
   - `gateway/run.py` around `build_footer_line(...)`
   - `agent/codex_quota.py`
   - `/api/model/quota` in `hermes_cli/web_server.py`
2. Add a footer field such as `quota` to `runtime_footer.py`.
3. For quota, call `fetch_live_codex_quota(timeout_seconds=small_value)` or `load_cached_codex_quota()` depending on latency needs.
4. Render only compact sanitized values from `buckets`, typically remaining percentages:
   - compact: `5h 83% · W 94%`
   - readable: `5h 83% remaining · Weekly 94% remaining`
5. Keep quota failure isolated. If quota is unavailable, omit the field instead of failing the whole reply.
6. Prefer platform-specific config for Telegram:

```yaml
display:
  platforms:
    telegram:
      runtime_footer:
        enabled: true
        fields: [model, context_pct, quota]
```

## Streaming caveat

The existing gateway footer is appended to the final response only when the body has not already been sent. If streaming already delivered the response body, `gateway/run.py` sends the footer as a separate trailing message. Tell the user this before patching if they ask for the footer literally inside the same Telegram message every time. That requirement may need a streaming behavior change or Telegram streaming disablement.

## Verification

Run targeted checks before restarting services:

```bash
/home/ubuntu/.hermes/hermes-agent/venv/bin/python -m py_compile \
  /home/ubuntu/.hermes/hermes-agent/gateway/runtime_footer.py \
  /home/ubuntu/.hermes/hermes-agent/gateway/run.py \
  /home/ubuntu/.hermes/hermes-agent/agent/codex_quota.py

cd /home/ubuntu/.hermes/hermes-agent && \
  /home/ubuntu/.hermes/hermes-agent/venv/bin/python -m pytest tests/gateway/test_runtime_footer.py -q -o 'addopts='
```

Restart only the gateway for gateway-footer changes:

```bash
systemctl --user restart hermes-gateway
systemctl --user --no-pager --full status hermes-gateway
```
