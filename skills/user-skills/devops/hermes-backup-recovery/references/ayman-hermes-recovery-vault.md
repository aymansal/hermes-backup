# Ayman Hermes Recovery Vault

## Current known vault
Ayman's private Hermes recovery vault is `aymansal/hermes-backup`.

It is intended for Hermes disaster recovery, not general project-source backup. It stores sanitized Hermes source/config/skills/memory/systemd/cron/state and an env-key template, while excluding secret values and OAuth material.

## Important script paths
- Live backup refresher on the Hermes VPS: `~/.hermes/scripts/hermes_backup_to_github.py`
- Recovery vault restore helper: `scripts/restore.sh`
- Recovery vault copy of backup refresher: `scripts/backup_now.py`

## Lesson from May 2026 restore-script forge
The backup refresher initially preserved a placeholder `scripts/restore.sh` that only printed `See README.md for restore instructions.` The recovery repo now needs to preserve the real restore helper from git HEAD during rebuilds, because the backup script clears and recreates the repo working tree.

Preservation pattern:
- In the backup refresher, read `git show HEAD:scripts/restore.sh` before/while rebuilding.
- Write that content back to `scripts/restore.sh`.
- Fall back to a minimal pointer only if no prior restore helper exists.

## Restore command shape
On a new VPS:
```bash
sudo apt update
sudo apt install -y git curl rsync python3 python3-venv python3-pip build-essential

git clone https://github.com/aymansal/hermes-backup.git
cd hermes-backup
bash scripts/restore.sh
```

Non-interactive mode:
```bash
bash scripts/restore.sh --yes
```

After restore:
```bash
nano ~/.hermes/.env
cd ~/.hermes/hermes-agent
hermes doctor
hermes auth add openai-codex  # if Codex/OAuth is needed
```

Then start gateway:
```bash
loginctl enable-linger "$USER"
systemctl --user daemon-reload
systemctl --user enable --now hermes-gateway
systemctl --user status hermes-gateway --no-pager -n 50
```

## Security boundary
Do not tell Ayman a public restore kit is equivalent to the private vault. A public-safe kit should strip memory/state/config context as needed and is usually body-only. The private vault or encrypted brain pack is needed for same knowledge.

## Project boundary
This vault does not automatically include POS/Samurai/Spana/ImmoPilot source-code repos. It may include references or memories about them. Use separate Project Vaults for actual business app code.
