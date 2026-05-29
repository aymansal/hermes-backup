# Codex / ChatGPT quota global architecture

Use this reference when the operator asks how Hermes displays multiple ChatGPT/Codex account quotas, how Shadow Realm account selection becomes the global chat account, or how the Telegram quota footer stays aligned with the actual runtime credential.

## Core invariant

The dashboard account selector is not just a UI filter. Selecting a ChatGPT/Codex account writes the global runtime model config:

```yaml
model:
  provider: openai-codex
  default: gpt-5.5
  credential_id: <selected_codex_credential_id>
```

New Hermes runtimes that call `resolve_runtime_provider()` should honor this selection across dashboard chat, Telegram, terminal CLI sessions, cron-created agents, and other standard agent entry points. Existing live agents may already hold a resolved credential in memory; user-facing UI/copy should say `/reset`, a new session, or process restart may be needed for those live sessions.

Ayman's preferred behavior: manual dashboard selection is authoritative. Do not proactively switch selected ChatGPT accounts based on quota/reset metadata unless the operator explicitly asks for rotation behavior.

## Backend pieces

Primary files:

- `agent/codex_quota.py`
- `agent/credential_pool.py`
- `hermes_cli/runtime_provider.py`
- `hermes_cli/web_server.py`
- `run_agent.py`
- `gateway/run.py`
- `gateway/runtime_footer.py`

### Credential pool

Multiple ChatGPT/Codex accounts are stored under the `openai-codex` credential pool. Each entry may contain tokens and raw provider metadata, so dashboard routes must construct a fresh allowlisted response shape.

Safe per-account fields include:

- Hermes-local `id`
- `label`
- `source`
- `auth_type`
- `priority`
- `last_status`
- `last_error_code`
- `selected`
- sanitized `quota`

Never return access tokens, refresh tokens, cookies, raw provider account ids, emails, raw JWT claims, raw auth headers, or the raw `/usage` response.

### Live quota source

Prefer the read-only ChatGPT Codex usage endpoint:

```text
GET https://chatgpt.com/backend-api/codex/usage?client_version=1.0.0
```

The helper should resolve/refresh the selected OAuth credential, call `/usage`, parse only safe fields, and store sanitized quota into the matching credential-pool entry as `last_quota`.

Response headers from normal Codex model calls are only a fallback/cache source. When saving header quota, attach it to the credential that actually made the request:

```python
pool = getattr(self, "_credential_pool", None)
credential_id = getattr(pool, "current_id", None) if pool is not None else None
save_codex_quota_from_headers(headers, credential_id=credential_id)
```

## Dashboard API routes

In `hermes_cli/web_server.py`:

- `GET /api/model/quota` returns live sanitized quota for the selected account and includes `active_provider`, `active_model`, `is_active`, and `selected_credential_id`.
- `GET /api/model/codex/accounts` returns all sanitized account rows and the current `selected_id`.
- `POST /api/model/codex/accounts/select` validates the credential id, then writes `model.provider=openai-codex` and `model.credential_id=<id>` via `save_config(cfg)`.

Selection must preserve unrelated model config such as `model.default`.

## Runtime provider behavior

In `hermes_cli/runtime_provider.py`, when provider is `openai-codex`, read `model.credential_id` and call:

```python
entry = pool.select_by_id(selected_credential_id)
```

If selected id is unavailable, fail clearly instead of silently picking another account. Manual selection is the source of truth.

## Dashboard UI behavior

In `web/src/lib/api.ts`, expose typed helpers:

- `getModelQuota()`
- `getCodexAccounts()`
- `selectCodexAccount(credential_id)`

In `web/src/pages/ModelsPage.tsx`, render `ChatGPTQuotaCard` as card-first UI:

- compact clickable account cards
- selected badge/highlight
- quota buckets per account
- selected account uses fresher `/api/model/quota` data
- non-selected accounts use cached `account.quota`
- selected account card can include active main-model metadata
- suppress the duplicate active Codex model card below if that model is already represented inside the selected account card

Polling should refresh both quota and account metadata every 5 seconds:

```ts
Promise.all([
  api.getModelQuota().catch(() => null),
  api.getCodexAccounts().catch(() => null),
])
```

Polling quota alone can leave selected card/status stale.

## Telegram/runtime footer behavior

Footer config for Ayman's quota-only Telegram footer:

```yaml
display:
  platforms:
    telegram:
      runtime_footer:
        enabled: true
        fields:
        - quota
        timezone: Africa/Casablanca
  runtime_footer:
    enabled: false
```

`gateway/run.py` should extract the actual credential used by the completed agent:

```python
_pool = getattr(_agent, "_credential_pool", None)
_current_credential = _pool.current() if _pool is not None else None
_resolved_credential_id = getattr(_current_credential, "id", None)
```

Then pass it to `gateway.runtime_footer.build_footer_line(..., credential_id=agent_result.get("credential_id"))`.

`build_footer_line()` should call:

```python
fetch_live_codex_quota(timeout_seconds=3.0, credential_id=credential_id)
```

This keeps the footer tied to the account that actually answered, not only the global config value, which may be stale for already-created agents.

## User-facing explanation pattern

When summarizing this system for Ayman, lead with the invariant:

> `model.credential_id` is the crown. The Shadow Realm writes it, and all new Hermes runtimes obey it.

Then describe the route:

1. multiple accounts live in the `openai-codex` credential pool
2. live quota comes from ChatGPT Codex `/usage`
3. dashboard exposes sanitized quota/accounts/select endpoints
4. card click writes `model.provider` + `model.credential_id`
5. runtime provider resolves the selected credential for new agents
6. Telegram footer uses the actual runtime credential id and the same sanitized quota helper

Keep the answer practical. Fantasy flavor is acceptable, but technical truth first.