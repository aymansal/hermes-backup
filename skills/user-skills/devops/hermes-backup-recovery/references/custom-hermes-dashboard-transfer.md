# Custom Hermes Dashboard / Codex Quota Transfer Pattern

Use this reference when a Hermes recovery vault contains custom source changes, but the target VPS already has a fresh Hermes install plus knowledge/personality restore. The goal is to transfer only the final custom code layer without overwriting the whole app.

## Scenario
- Source Hermes has custom Shadow Realm/dashboard code for multiple Codex/ChatGPT accounts, live quota display, global account selection, and Telegram quota footer.
- Target Hermes already restored `SOUL.md`, skills, memory/config, etc.
- Direct `scp` may not work because the target VPS is behind a different Tailscale tailnet/account.

## Recommended transfer shape
1. Generate a single patch from the final working source state, not from intermediate attempts.
2. Include only the required source files, not the whole Hermes directory, venv, `.env`, `auth.json`, logs, or caches.
3. Share the patch via a pull route: raw GitHub/Gist/private repo URL, temporary controlled download link, or file attachment the target operator can upload/download.
4. Have the target VPS download the patch to `/tmp/<patch-name>.patch`.
5. Let the target Hermes agent apply it under a strict prompt, or use a deterministic shell block.

## Example file battle group for Codex dashboard + quota
Adjust paths to the actual diff, but this class of change commonly includes:

```text
agent/codex_quota.py
agent/agent_runtime_helpers.py
agent/credential_pool.py
gateway/run.py
gateway/runtime_footer.py
hermes_cli/config.py
hermes_cli/runtime_provider.py
hermes_cli/web_server.py
run_agent.py
web/src/components/OAuthLoginModal.tsx
web/src/components/OAuthProvidersCard.tsx
web/src/lib/api.ts
web/src/pages/ModelsPage.tsx
```

## Source-side patch creation
From the final working Hermes checkout:

```bash
cd ~/.hermes/hermes-agent
PATCH="$HOME/hermes-codex-dashboard-global-quota-final.patch"

git diff --binary -- \
  agent/agent_runtime_helpers.py \
  agent/credential_pool.py \
  gateway/run.py \
  gateway/runtime_footer.py \
  hermes_cli/config.py \
  hermes_cli/runtime_provider.py \
  hermes_cli/web_server.py \
  run_agent.py \
  web/src/components/OAuthLoginModal.tsx \
  web/src/components/OAuthProvidersCard.tsx \
  web/src/lib/api.ts \
  web/src/pages/ModelsPage.tsx \
  > "$PATCH"

git diff --binary --no-index /dev/null agent/codex_quota.py >> "$PATCH" || true
```

Secret scan before sharing:

```bash
grep -Ei 'api[_-]?key|token|secret|password|authorization|bearer' "$PATCH" || true
python3 - <<'PY'
import re, pathlib, sys
p=pathlib.Path(sys.argv[1])
s=p.read_text(errors='ignore')
patterns={
 'openai_sk': r'sk-[A-Za-z0-9_-]{20,}',
 'github_pat': r'gh[pousr]_[A-Za-z0-9_]{20,}',
 'telegram_bot': r'\b\d{8,12}:[A-Za-z0-9_-]{30,}\b',
 'jwt': r'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}',
 'bearer_literal': r'Bearer\s+[A-Za-z0-9._-]{20,}',
}
for name, pat in patterns.items():
    print(f'{name}:', len(re.findall(pat, s)))
PY "$PATCH"
sha256sum "$PATCH"
```

Variable names may match the simple `grep`; real token-like patterns should be zero.

## Target-side strict prompt
Give the target Hermes this shape, after the patch is present at `/tmp/hermes-codex-dashboard-global-quota-final.patch`:

```text
Mission: apply only /tmp/hermes-codex-dashboard-global-quota-final.patch to this Hermes Agent installation.
Rules:
- Do not overwrite the whole Hermes installation.
- Do not touch or print secrets, `.env`, `auth.json`, cookies, or private credentials.
- Do not delete files.
- Do not restart services until verification passes and I approve.
- Inspect first: pwd, which hermes, hermes --version, source path exists, git status, patch file exists.
- Create a timestamped backup tarball of ~/.hermes/hermes-agent before applying anything.
- Run git apply --check before git apply.
- If git apply --check fails, stop and report the exact conflict/error. Do not force apply.
- Apply only this patch file.
- Verify Python syntax with compileall; run web build checks if npm/web are available.
- Enable Telegram quota footer config if this patch includes footer support.
- Ask before restarting hermes-gateway or hermes-dashboard.
```

## Target-side deterministic command block
If avoiding agent improvisation:

```bash
cd ~/.hermes/hermes-agent || exit 1
cd ~/.hermes || exit 1
tar -czf "$HOME/hermes-agent-before-codex-quota-patch-$(date +%Y%m%d-%H%M%S).tar.gz" hermes-agent
cd ~/.hermes/hermes-agent || exit 1

git apply --check /tmp/hermes-codex-dashboard-global-quota-final.patch || {
  echo "Patch check failed. Stop and send the error."
  exit 1
}

git apply /tmp/hermes-codex-dashboard-global-quota-final.patch || exit 1
python -m compileall agent hermes_cli gateway run_agent.py || exit 1

hermes config set display.platforms.telegram.runtime_footer.enabled true
hermes config set display.platforms.telegram.runtime_footer.fields '["quota"]'

echo "Verified. Restart gateway/dashboard only after approval."
```

## Pitfalls
- Do not use `--knowledge-only` restore to transfer source/dashboard code; it intentionally avoids overwriting app source.
- Do not copy the full `~/.hermes/hermes-agent` folder over a fresh install unless doing a full self-migration with rollback plan.
- Do not assume GitHub folder timestamps equal backup-run timestamps; they mean last content change.
- Do not share real Access Keys. The patch gives code machinery only; target still needs its own `.env` values and OAuth login.
