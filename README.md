# Hermes Backup — Shadow System Recovery Vault

Private backup for Ayman's Hermes Agent setup.

Last generated: `2026-05-28T03:00:27Z`

## Included
- Full Hermes source snapshot with local patches
- Sanitized config, persona/profile, Skill Runes
- Holographic memory DB, kanban DB, cron definitions
- Sanitized systemd user units
- Access Key template only, no secret values

## Excluded
`.env` values, `auth.json`, OAuth tokens, GitHub tokens, Telegram bot tokens, SSH keys, cookies, raw logs, session transcript DB, caches, and media caches.

## Quick restore
```bash
git clone https://github.com/aymansal/hermes-backup.git
cd hermes-backup
bash scripts/restore.sh
# fill ~/.hermes/.env from secrets/env.template
cd ~/.hermes/hermes-agent
hermes doctor
```
