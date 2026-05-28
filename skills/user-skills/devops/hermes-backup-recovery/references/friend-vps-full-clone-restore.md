# Friend VPS full-clone restore pattern

## Context
When cloning Ayman's Hermes setup onto a friend's VPS, the restore must produce a working global `hermes` command, not only copy knowledge/config. A previous restore flow defaulted to knowledge-only and left the target VPS with restored files but no CLI launcher on PATH.

## Correct class-level lesson
For friend/full-clone restores, the recovery script should either:

1. restore the Hermes source/dashboard snapshot first, then run the restored `scripts/install.sh` with `--skip-setup --dir "$HERMES_HOME/hermes-agent" --hermes-home "$HERMES_HOME"`; or
2. if running knowledge-only and no `hermes` command exists, install official Hermes first, then restore knowledge.

Do not treat `git clone` + `restore.sh` as equivalent to installing Hermes unless the script explicitly creates/repairs the CLI launcher.

## Expected backup contents for full clone
A friend-clone recovery vault may include:

- `source/hermes-agent/hermes_cli/web_server.py`
- `source/hermes-agent/hermes_cli/web_dist/`
- `source/hermes-agent/web/src/`
- `state/memory_store.db`
- `state/kanban.db`
- `state/cron/`
- `skills/user-skills/`
- sanitized config/persona/profile files
- `secrets/env.template`

It must not include:

- `.env` secret values
- `auth.json`
- OAuth tokens
- Telegram bot tokens
- provider API keys
- SSH/private keys

## Restore script behavior to prefer
Default friend clone should be `--full` mode, but systemd restore should remain opt-in via `--with-systemd` because enabling/replacing services is higher risk.

Recommended UX:

```bash
bash scripts/restore.sh --yes
```

The script should:

- install base packages if needed
- restore sanitized config/persona/profile
- restore skills
- restore memory/kanban/cron state
- create `.env` from template only if missing
- restore source/dashboard snapshot
- install/reinstall the global Hermes CLI launcher from the restored source snapshot
- run `hermes doctor` if not a dry run

## Verification
Before committing changes to the recovery vault, run:

```bash
bash -n scripts/restore.sh
bash scripts/restore.sh --dry-run --yes
git diff --check
```

Then verify the vault shape with existence checks for dashboard, memory, and secret exclusions.
