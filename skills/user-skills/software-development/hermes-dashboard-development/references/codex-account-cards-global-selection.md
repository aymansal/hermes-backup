# Codex / ChatGPT account cards + global selected account behavior

Use this reference when improving OpenAI Codex / ChatGPT multi-account support in the Hermes native dashboard.

## Desired behavior

- Multiple ChatGPT/Codex accounts are rendered as account cards, not a small row list or dropdown.
- The selected account is visually highlighted and described as the account used for Hermes chat.
- Selecting an account writes the global runtime config path:

```yaml
model:
  provider: openai-codex
  credential_id: <selected_account_id>
```

- New runtime agent creation paths that call `resolve_runtime_provider()` should honor `model.credential_id`, including dashboard chat, Telegram Gateway, terminal Hermes sessions, cron, and other runtime paths.
- Existing already-created agents may keep their resolved API key in memory; UI copy should state that `/reset`, a new session, or process restart may be needed.

## Backend pattern

### Sanitized per-account quota

`hermes_cli/web_server.py::_codex_account_rows()` can include a per-account `quota` field from credential-pool entry `last_quota`, but it must be allowlisted.

Safe quota fields:

- `available`
- `source`
- `captured_at`
- `captured_at_unix`
- `plan_type`
- `active_limit`
- `credits_unlimited`
- `credits_has_credits`
- `message`
- `buckets[]` with only `key`, `label`, `window_minutes`, `used_percent`, `remaining_percent`, `reset_at`, `reset_after_seconds`

Never return:

- access tokens
- refresh tokens
- cookies
- emails
- provider account IDs
- raw JWT claims
- raw usage payloads
- raw auth headers
- unknown quota keys

### Header quota capture should target the actual runtime credential

Codex response headers should be cached against the credential that made the request, not only whatever config currently says. A safe pattern is:

```python
pool = getattr(self, "_credential_pool", None)
credential_id = None
if pool is not None:
    credential_id = getattr(pool, "current_id", None) or getattr(pool, "_current_id", None)
save_codex_quota_from_headers(headers, credential_id=credential_id)
```

Prefer adding a non-secret `CredentialPool.current_id` property so callers do not have to reach into `_current_id` directly.

## Frontend pattern

### API typing

Add a lighter per-account quota type rather than reusing raw provider state:

```ts
export interface CodexAccountQuota {
  available: boolean;
  source?: string;
  captured_at?: string;
  captured_at_unix?: number;
  plan_type?: string | null;
  active_limit?: string | null;
  credits_unlimited?: boolean | null;
  credits_has_credits?: boolean | null;
  message?: string;
  buckets: ModelQuotaBucket[];
}

export interface CodexAccount {
  // existing safe metadata...
  quota?: CodexAccountQuota | null;
}
```

### Models page UI

Render an outer “ChatGPT accounts” card containing one compact card per account. Each account card should show:

- account label
- non-secret Hermes credential id
- selected badge/highlight
- plan badge if available
- status warning if present
- compact quota buckets if available

For the selected account, prefer fresher live data from `/api/model/quota` over cached `account.quota`.

Ayman's preferred interaction for this class of UI is minimal and card-first: when account cards are visible, make the whole card clickable for selection instead of adding a separate “Use for Hermes chat” button. Disable only the already-selected card action, but keep the selected card visually distinct.

When a selected Codex account is also the active main model provider, consolidate the provider/model metadata into the selected account card instead of rendering a second redundant model card below it. Include the useful model details in the selected account card, such as provider, model name, rank/main badge, context/output limits, session/token usage, capabilities, and the “Use as” control. Suppress only that duplicated active Codex model entry from the lower model grid; leave other model cards untouched.

Add explicit copy:

> Selection is written to `model.credential_id` and applies to new Hermes chat runtimes across dashboard, Telegram, and terminal. Existing live sessions may need /reset or restart.

### OAuth provider card UI

Keep this compact: render mini-cards for Codex accounts instead of flat rows. Show selected badge, label, id, compact quota summary, status, and remove button. Avoid duplicating the full Models page quota UI.

## Tests worth adding

- `_codex_account_rows()` includes sanitized `quota` and does not leak secret/raw fields.
- selecting an account writes `model.provider=openai-codex` and `model.credential_id` while preserving unrelated model config.
- runtime provider resolution uses selected Codex credential id.
- `run_agent._capture_rate_limits()` passes the current pool credential id into `save_codex_quota_from_headers()`.

## Verification

Run from repo root:

```bash
venv/bin/python -m py_compile \
  hermes_cli/web_server.py \
  agent/codex_quota.py \
  agent/credential_pool.py \
  hermes_cli/runtime_provider.py \
  run_agent.py

./scripts/run_tests.sh tests/hermes_cli/test_codex_account_selection_dashboard.py tests/gateway/test_runtime_footer.py
cd web && npm run build
```

For dashboard-only changes, restart only `hermes-dashboard`; do not restart the Telegram Gateway unless runtime behavior must be reloaded and the user confirms.
