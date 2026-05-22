# Codex quota after account switch: provider state vs credential pool

## Trigger

Use this note when the Shadow Realm `/api/model/quota`, Telegram runtime footer quota, or `agent.codex_quota.fetch_live_codex_quota()` reports Codex unavailable after the user switched ChatGPT/Codex accounts, while normal Codex model calls may still work.

## Symptom

Sanitized probes can show:

```text
active_provider: openai-codex
active_model: gpt-5.5
is_active: true
available: false
logged_in: false
live_fetch_failed: true
message: No Codex credentials stored. Run `hermes auth` to authenticate.
```

But `~/.hermes/auth.json` may still have an OAuth entry under:

```text
credential_pool.openai-codex[0]
```

instead of the older provider state location:

```text
providers.openai-codex.tokens
```

Do not print tokens, account IDs, or emails. Only report boolean presence of `access_token` / `refresh_token` and safe config fields.

## Root cause

Some Codex auth flows/account switches populate the credential pool, while older quota helpers may call `resolve_codex_runtime_credentials()` / `_read_codex_tokens()` paths that expect provider state. The model runtime may still resolve credentials through the pool, but the quota display path can look sealed.

## Safe diagnostic pattern

Use sanitized Python probes from the Hermes repo/venv:

```bash
/home/ubuntu/.hermes/hermes-agent/venv/bin/python - <<'PY'
from hermes_cli.config import load_config
from hermes_cli.auth import _load_auth_store

cfg = load_config()
print('model.provider:', (cfg.get('model') or {}).get('provider'))
print('model.default:', (cfg.get('model') or {}).get('default'))

store = _load_auth_store()
print('active_provider:', store.get('active_provider'))
providers = store.get('providers') or {}
print('providers has openai-codex:', isinstance(providers, dict) and 'openai-codex' in providers)

pool = store.get('credential_pool') or {}
entries = pool.get('openai-codex') if isinstance(pool, dict) else None
print('credential_pool.openai-codex entries:', len(entries) if isinstance(entries, list) else 0)
if isinstance(entries, list) and entries:
    entry = entries[0]
    if isinstance(entry, dict):
        print('pool access_token present:', bool(entry.get('access_token')))
        print('pool refresh_token present:', bool(entry.get('refresh_token')))
PY
```

For the live endpoint, prefer Python/urllib or curl with explicit URL and no pipe-to-interpreter pattern. Print only sanitized fields from `/api/model/quota`.

## Fix path

Patch quota/account usage helpers so Codex credential resolution accepts both storage shapes:

1. Prefer the normal runtime resolver if it returns an access token.
2. If provider state is missing, read `read_credential_pool('openai-codex')` or equivalent credential-pool helper.
3. Select a non-disabled entry with `access_token` and, for refresh support, `refresh_token` if present.
4. Keep provider-state fallback for compatibility.
5. When persisting sanitized `last_quota`, avoid overwriting credential-pool secrets or leaking PII.
6. Re-test:
   - `fetch_live_codex_quota()` sanitized summary
   - `/api/model/quota` sanitized summary
   - Telegram runtime footer preview if `fields: [quota]`
7. Restart only affected services: usually `hermes-dashboard` for dashboard API process and `hermes-gateway` for Telegram footer changes.

## Related routing check

This mismatch affects quota display, not necessarily auxiliary-model routing. Still verify quota-saving sessions did not regress the separate routing fix:

- `auxiliary.compression`
- `auxiliary.title_generation`
- `auxiliary.approval`
- `auxiliary.web_extract`
- `auxiliary.curator`

If delegation should avoid Codex too, inspect `delegation.provider` and `delegation.model`; empty values may inherit the main provider depending on runtime behavior.
