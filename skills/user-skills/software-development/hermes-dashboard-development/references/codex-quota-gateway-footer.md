# Codex quota reuse in gateway runtime footers

When the Shadow Realm already exposes Codex/ChatGPT quota through `agent.codex_quota.fetch_live_codex_quota()` and `/api/model/quota`, reuse that same sanitized helper for gateway reply footers instead of creating a second provider call path.

## Pattern

- Add a `quota` field to `gateway/runtime_footer.py` rather than hardcoding quota into the Telegram adapter.
- Keep `display.runtime_footer.fields` and per-platform `display.platforms.<platform>.runtime_footer.fields` as the control surface.
- When the provider uses a credential pool, pass the active runtime credential through the agent result into the footer builder. Do **not** let the footer read only global `model.credential_id`; that value can be stale or intentionally different from the account the cached gateway agent is actually using.
- For OpenAI Codex, have `gateway/run.py` extract the active credential from the completed agent (`agent._credential_pool.current().id` when `agent.provider == "openai-codex"`), return it as `agent_result["credential_id"]`, and call `build_footer_line(..., credential_id=agent_result.get("credential_id"))`.
- Have `gateway/runtime_footer.build_footer_line()` accept `credential_id: Optional[str]` and forward it to `fetch_live_codex_quota(timeout_seconds=3.0, credential_id=credential_id)`.
- For Telegram quota-only footers, configure:

```yaml
display:
  platforms:
    telegram:
      runtime_footer:
        enabled: true
        fields: [quota]
```

## Rendering guidance

A compact, useful footer should show remaining percentage plus reset time/date, without the model name when the user asks for quota-only output:

```text
5h 83% left reset 03:38 · Weekly 94% left reset Wed 13:00
```

Use local time for reset display. If the reset is today, time alone is enough; otherwise include weekday plus time.

## Safety rules

- Never read or render Access Keys, bearer tokens, refresh tokens, account IDs, emails, or raw auth state.
- Use only the sanitized quota shape from `agent.codex_quota`: bucket labels, remaining/used percentages, reset timestamps, plan labels, and availability flags.
- If live quota fetch fails, rely on the helper's existing cached fallback. Do not make the final user reply fail because optional quota metadata is unavailable.

## Verification

Run targeted checks after adding or changing footer quota rendering:

```bash
/home/ubuntu/.hermes/hermes-agent/venv/bin/python -m py_compile \
  gateway/runtime_footer.py gateway/run.py agent/codex_quota.py

/home/ubuntu/.hermes/hermes-agent/venv/bin/python -m pytest \
  tests/gateway/test_runtime_footer.py -q -o 'addopts='
```

Restart only the affected gateway service when deploying footer changes:

```bash
systemctl --user restart hermes-gateway
systemctl --user --no-pager --full status hermes-gateway | sed -n '1,22p'
```

## Streaming pitfall

Gateway runtime footers are appended to the final response body only when the body has not already been streamed/sent. If streaming has already delivered the answer, Hermes sends the footer as a small trailing message. That is expected footer behavior, not a Telegram adapter bug.