# Hermes Backup — Shadow System Recovery Vault

Private backup for Ayman's Hermes Agent setup.

Last generated: `2026-05-22T09:53:46Z`

## What is included

- `source/hermes-agent/` — full Hermes source snapshot with current local patches.
- `source/local-patches.patch` — local tracked-file diff against upstream checkout.
- `config/config.yaml` — sanitized Hermes config. Secret-looking values are replaced with `<SET_ON_RESTORE>`.
- `config/SOUL.md` and `config/OPERATOR_PROFILE.md` — Shadow System persona/profile.
- `skills/user-skills/` — installed Skill Runes.
- `state/memory_store.db` — Holographic/local memory database backup.
- `state/kanban.db` and `state/cron/` — durable automation/board state where present.
- `systemd/` — Hermes user service/timer units, sanitized.
- `secrets/env.template` — Access Key names only, values blank.
- `scripts/restore.sh` — quick restore helper for a fresh VPS.

## What is intentionally excluded

No `.env`, `auth.json`, OAuth tokens, GitHub tokens, Telegram bot tokens, SSH keys, cookies, raw logs, session transcript DB, cache files, media caches, or process locks are committed.

The Core Crystal is protected: secrets must be restored from your password manager or the original secure source.

## Quick restore on a new VPS

```bash
git clone https://github.com/aymansal/hermes-backup.git
cd hermes-backup
bash scripts/restore.sh
# fill ~/.hermes/.env with Access Keys
cd ~/.hermes/hermes-agent
hermes doctor
hermes gateway status
```

If `hermes` is not installed globally yet, use the official installer first or run from the copied source environment.
