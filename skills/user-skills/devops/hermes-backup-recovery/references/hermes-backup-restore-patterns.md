# Hermes backup and restore patterns

Session-derived details for future Hermes recovery work.

## Backup refresher vs restore installer

A Hermes backup refresh script such as:

```text
~/.hermes/scripts/hermes_backup_to_github.py
```

pushes sanitized backup artifacts from the current VPS to GitHub. It is not automatically a restore installer on the new VPS.

The desired new-VPS UX is:

```bash
git clone https://github.com/OWNER/hermes-backup.git
cd hermes-backup
bash scripts/restore.sh
```

If `scripts/restore.sh` is a placeholder, future agents should forge it rather than telling the user cloning is enough.

## Artifact split

### Body

Usually safe for a sanitized temporary public copy:

- Hermes source snapshot
- sanitized config/persona/profile files
- Skill Runes
- sanitized systemd units
- `.env` key-name template

### Brain

Needed for “same knowledge from the get-go,” but should not be public:

- `~/.hermes/memory_store.db`
- `~/.hermes/skills/`
- `~/.hermes/kanban.db`
- `~/.hermes/cron/`
- `~/.hermes/config.yaml`
- `~/.hermes/SOUL.md`
- `~/.hermes/OPERATOR_PROFILE.md`

Transfer as an encrypted brain pack, then restore over the skeleton.

### Access Keys

Do not include in public repos or normal backups:

- `~/.hermes/.env`
- `~/.hermes/auth.json`
- OAuth tokens
- Telegram bot tokens
- provider API keys
- GitHub tokens
- SSH keys/cookies

Use separate runtime keys for semi-trusted VPSes when possible.

## User interaction lessons

- When Ayman asks for “the command,” give only the command first. Add context after.
- If he explicitly chooses a riskier path (for example a temporary public repo), obey after a safety scan and avoid repeating the same warning loop.
- If the desired outcome is “same knowledge,” do not offer a stripped public kit as if equivalent. State that it is only the Body and provide Brain transfer commands.

## Verification checklist

After restore, verify:

```bash
cd ~/.hermes/hermes-agent
hermes doctor
hermes config check
hermes skills list
hermes memory status
hermes cron list
systemctl --user status hermes-gateway --no-pager -n 50
```

Expected unresolved manual work:

- fill `~/.hermes/.env`
- re-run OAuth logins if auth state was not intentionally transferred
- confirm Telegram/gateway routing from the actual Comms Gate
