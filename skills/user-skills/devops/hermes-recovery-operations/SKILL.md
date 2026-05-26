---
name: hermes-recovery-operations
description: Restore, clone, migrate, and validate a Hermes Agent installation from backup artifacts without leaking secrets.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [hermes, backup, restore, recovery, migration, vps, secrets]
---

# Hermes Recovery Operations

Use this Skill Rune when the user wants to restore Hermes Agent onto a new VPS, clone their Hermes setup, publish/copy a backup artifact, or validate a Hermes recovery vault.

## Operator doctrine

- If the user asks for a specific command, give the copy-paste command first. Keep caveats brief and place them after the command.
- Separate the restore into three layers:
  1. **Body:** source code, config template, Skill Runes, systemd units.
  2. **Brain:** memory DB, skills, kanban DB, cron definitions, persona/profile.
  3. **Access Keys:** `.env`, `auth.json`, OAuth tokens, Telegram tokens, provider keys.
- Never claim a clone is fully restored until the user has run the restore script/copy steps, filled `.env`, re-authenticated OAuth providers, and verified `hermes doctor` plus gateway status.
- Public temporary repos are only acceptable for sanitized body/skeleton artifacts. Do not include memory DB, kanban DB, cron state, session DB, `.env`, `auth.json`, logs, or tokens in public copies.
- If the user wants “same knowledge from the get-go,” public skeleton is insufficient; transfer the Brain layer privately, preferably as an encrypted archive.

## Required Access Keys / values

- GitHub repo URL or local backup path.
- New VPS SSH login if transferring archives directly.
- Runtime Access Keys for the new VPS, set manually in `~/.hermes/.env`.
- OAuth re-login for providers that store tokens in `auth.json` or provider-specific auth stores.

## Safe read-only checks

```bash
pwd
ls -la
ls -la ~/.hermes 2>/dev/null || true
ls -la ~/.hermes/backups/hermes-backup 2>/dev/null || true
gh repo view OWNER/REPO --json nameWithOwner,visibility,isPrivate
```

## Restore flow from a Hermes backup repo

```bash
git clone https://github.com/OWNER/REPO.git
cd REPO
```

If `scripts/restore.sh` is real and executable:

```bash
bash scripts/restore.sh
```

If no real restore script exists, use manual restore:

```bash
mkdir -p ~/.hermes ~/.config/systemd/user
rsync -a config/ ~/.hermes/
rm -rf ~/.hermes/hermes-agent
rsync -a source/hermes-agent/ ~/.hermes/hermes-agent/
mkdir -p ~/.hermes/skills
rsync -a skills/user-skills/ ~/.hermes/skills/
rsync -a state/ ~/.hermes/
rsync -a systemd/ ~/.config/systemd/user/
if [ -f ~/.hermes/_install_method ]; then mv ~/.hermes/_install_method ~/.hermes/.install_method; fi
cp secrets/env.template ~/.hermes/.env
chmod 600 ~/.hermes/.env
```

Then fill Access Keys and verify:

```bash
nano ~/.hermes/.env
cd ~/.hermes/hermes-agent
hermes doctor
hermes config check
hermes skills list
hermes memory status
hermes cron list
```

Start gateway only after credentials are ready:

```bash
systemctl --user daemon-reload
loginctl enable-linger "$USER"
systemctl --user enable --now hermes-gateway
systemctl --user status hermes-gateway --no-pager -n 50
```

## Brain pack transfer

Use when the target VPS should inherit the same knowledge without receiving the full secret layer.

```bash
cd ~
tar -czf hermes-brain-pack.tar.gz \
  .hermes/memory_store.db \
  .hermes/kanban.db \
  .hermes/cron \
  .hermes/skills \
  .hermes/config.yaml \
  .hermes/SOUL.md \
  .hermes/OPERATOR_PROFILE.md \
  2>/dev/null
gpg -c hermes-brain-pack.tar.gz
scp ~/hermes-brain-pack.tar.gz.gpg user@FRIEND_VPS_IP:/tmp/
```

On the target VPS:

```bash
cd /tmp
gpg -d hermes-brain-pack.tar.gz.gpg > hermes-brain-pack.tar.gz
cd ~
tar -xzf /tmp/hermes-brain-pack.tar.gz
chmod 600 ~/.hermes/memory_store.db ~/.hermes/kanban.db ~/.hermes/config.yaml 2>/dev/null || true
```

## Public temporary restore kit rules

Before publishing any public temporary kit, strip high-risk state:

```bash
rsync -a \
  --exclude='.git/' \
  --exclude='state/' \
  --exclude='backup-manifest.json' \
  PRIVATE_BACKUP_DIR/ PUBLIC_TEMP_DIR/
```

Run leak checks before push:

```bash
find PUBLIC_TEMP_DIR \( -name '.env' -o -name 'auth.json' -o -name 'state.db' -o -name 'memory_store.db' -o -name 'kanban.db' -o -name '*.pem' -o -name '*.key' \) -print
```

Close public temporary repos immediately after use. Prefer deletion; if deletion scope is missing, make private.

```bash
gh repo edit OWNER/REPO --visibility private --accept-visibility-change-consequences
# deletion requires delete_repo scope:
gh auth refresh -h github.com -s delete_repo
gh repo delete OWNER/REPO --yes
```

## Common System Alerts

- `scripts/restore.sh` only says “See README”: the backup has a placeholder restore script; manual restore or forge a real script and commit it.
- `HTTP 403 delete_repo`: GitHub CLI lacks delete permission; run `gh auth refresh -h github.com -s delete_repo` or make the repo private instead.
- User expects same knowledge after public skeleton restore: explain Body vs Brain vs Access Keys, then provide brain-pack transfer commands.

## References

- See `references/hermes-backup-restore-patterns.md` for the session-derived restore patterns and public/private artifact split.
