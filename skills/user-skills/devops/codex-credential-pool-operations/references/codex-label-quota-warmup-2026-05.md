# Codex label + quota warmup fix detail — May 2026

## Context

Ayman's Hermes Shadow Realm had two related OpenAI Codex account-management issues:

1. Dashboard-added Codex accounts could receive duplicate labels after deletion. Example state: `Gpt1`, `Gpt2`, `Gpt4`; adding a new account used `len(pool.entries()) + 1` and created another `Gpt4`.
2. The Morocco 09:00 quota warmup cron used `hermes chat --provider openai-codex --model gpt-5.5` without a credential selector, so it warmed only the globally selected `model.credential_id` account. Other credential-pool accounts kept separate 5h reset windows.

## Files involved

- `hermes_cli/web_server.py`
- `agent/codex_quota.py`
- `agent/credential_pool.py`
- `hermes_cli/auth_commands.py`
- `~/.hermes/scripts/codex_quota_warmup.py`

## Label fix pattern

Root cause: dashboard login path created new labels with:

```python
label=f"Gpt{len(pool.entries()) + 1}"
```

Correct class of fix: allocate the lowest free numeric `GptN` slot by scanning existing labels case-insensitively and only considering labels matching `^gpt(\d+)$`. Do not auto-rename existing accounts in the login path. Existing-account refresh by account fingerprint should preserve its id and label.

Regression tests to carry forward:

- `Gpt1`, `Gpt2`, `Gpt4` -> `Gpt3`
- `Gpt1`, `Gpt2`, `Gpt3` -> `Gpt4`
- ignores `Main`, `codex`, other non-matches
- case-insensitive: `gpt1`, `GPT2` -> `Gpt3`
- ignores `Gpt0`, `Gptx`

## Warmup script pattern

The scheduled script should:

- Enumerate usable `credential_pool.openai-codex` entries from `auth.json`.
- Return only safe metadata: `id`, `id_prefix`, `label`; never return tokens.
- At warmup slot, perform one tiny generation call for each credential and then refresh quota for each credential.
- At refresh slot, fetch `/usage` for each credential with no generation.
- Print safe summaries only.
- On partial failures, print the failures, exit non-zero, and do not mark the slot date complete so cron can retry in the same window.

## Credential selection caveat

At time of this session, `hermes chat --help` showed no `--credential-id` flag. A safe fallback used a short-lived Python subprocess:

1. Load config and deep-copy original config.
2. Temporarily set `model.provider = openai-codex` and `model.credential_id = <target>`.
3. Instantiate `AIAgent(provider='openai-codex', model='gpt-5.5', enabled_toolsets=['safe'], quiet_mode=True, skip_context_files=True, skip_memory=True, max_iterations=1)`.
4. Send `Warmup ping. Reply exactly: OK`.
5. Restore original config in `finally`.

This is acceptable only because it is short-lived, restores in `finally`, and does not print secrets.

## Verification commands used

Focused label tests:

```bash
python -m pytest tests/hermes_cli/test_dashboard_codex_labels.py -q -o 'addopts='
```

Warmup helper tests:

```bash
python -m pytest tests/scripts/test_codex_quota_warmup_helpers.py -q -o 'addopts='
```

Codex quota rotation tests:

```bash
python -m pytest tests/agent/test_codex_quota_rotation.py -q -o 'addopts='
```

Dashboard/web regression tests:

```bash
python -m pytest tests/hermes_cli/test_codex_account_selection_dashboard.py tests/hermes_cli/test_web_server.py -q -o 'addopts='
```

Safe all-account live quota check:

```bash
PYTHONPATH=. python - <<'PY'
from hermes_cli.auth import read_credential_pool
from agent.codex_quota import fetch_live_codex_quota

entries = read_credential_pool('openai-codex') or []
for e in entries:
    cid = e.get('id')
    label = e.get('label')
    if not cid or not e.get('access_token'):
        continue
    q = fetch_live_codex_quota(timeout_seconds=12.0, credential_id=cid)
    buckets = q.get('buckets') or []
    primary = next((b for b in buckets if b.get('label') == '5h' or b.get('key') == 'primary'), buckets[0] if buckets else {})
    print(label, cid[:6], 'remaining', primary.get('remaining_percent'), 'reset_at', primary.get('reset_at'), 'live_failed', q.get('live_fetch_failed', False))
PY
```

## Safety boundaries

- Do not print tokens, refresh tokens, cookies, raw headers, emails, or full account ids.
- Do not edit `auth.json` metadata without explicit approval and a timestamped backup.
- Do not restart dashboard/gateway without explicit approval.
- Do not touch unrelated local patches in Ayman's Hermes checkout, especially dashboard quota patches.