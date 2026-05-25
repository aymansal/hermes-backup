# Codex manual selection vs auto-switching — May 2026

## Trigger

Ayman selected the ChatGPT/Codex account labeled `Tiktok` in the Shadow Realm, but Hermes later switched to `Swayam`. He decided to remove the auto-switcher entirely and manage account choice manually.

## Root cause

Two different switching paths could override manual selection:

1. **Proactive runtime selection** in `hermes_cli/runtime_provider.py` treated `model.credential_id` as the current input to quota ranking. If another usable account had a nearer eligible reset, `pool.select_codex_by_quota(...)` could choose it and, with `persist_runtime_switch: true`, write it back to config.
2. **Reactive failover** in `agent/agent_runtime_helpers.py` / `agent/credential_pool.py` could rotate on Codex `429`, `402`, or auth-refresh failure and persist/swap to the next account.

Ayman's policy changed: manual dashboard selection should be authoritative, not advisory.

## Desired behavior

- `codex_quota_rotation.enabled: false`
- `codex_quota_rotation.persist_runtime_switch: false`
- Runtime provider should resolve selected Codex accounts via `pool.select_by_id(selected_credential_id)`.
- Quota/reset rankings may remain useful as display metadata or for future optional auto mode, but must not change selected account by default.
- If the selected account hits quota/auth/billing failure, surface the failure instead of silently switching accounts.
- If the selected account is deleted, clear `model.credential_id`; do not silently choose an `auto_candidate`.

## Patch map from this session

- `hermes_cli/runtime_provider.py`
  - Remove proactive quota selection for pinned Codex credentials.
  - Use `pool.select_by_id(selected_credential_id)`.
  - Do not call `persist_selected_codex_credential_id(..., reason='proactive_runtime_rotation')` for manual mode.

- `agent/agent_runtime_helpers.py`
  - Add a helper that checks `codex_quota_rotation_config().get('enabled')`.
  - For Codex billing/rate-limit/auth-refresh-failed recovery, if auto-switching is disabled, return failure instead of rotating.

- `agent/credential_pool.py`
  - Defense in depth: `mark_exhausted_and_rotate()` should return `None` for `openai-codex` when rotation is disabled, instead of falling through to generic pool selection.

- `hermes_cli/web_server.py`
  - `/api/model/codex/accounts` should not mark `accounts[0]` or `auto_candidate` selected when no selected id exists.
  - Account removal should clear the selected id when removing the selected account, not auto-select a replacement.

- `~/.hermes/config.yaml`
  - Set:
    ```yaml
    codex_quota_rotation:
      enabled: false
      persist_runtime_switch: false
    ```

## Regression test expectations

- Runtime provider test should assert selected Codex id calls `select_by_id`, even if quota rotation config exists.
- It should assert no persistence call occurs for proactive auto-switch.
- Dashboard tests should assert no selected account is invented when `model.credential_id` is absent.
- Removal tests should assert deleting the selected account clears selection.

## Safe verification

```bash
cd ~/.hermes/hermes-agent
python -m pytest \
  tests/hermes_cli/test_runtime_provider_resolution.py \
  tests/hermes_cli/test_codex_account_selection_dashboard.py \
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

## Restart safety

Do not restart gateway/dashboard while Kanban work is active unless Ayman explicitly approves. Code changes require service restart to fully apply; config writes apply to future config reads but long-lived imports/processes may still need restart.
