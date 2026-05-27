---
name: hermes-backup-recovery
description: Back up and restore a Hermes Agent installation across VPS hosts using sanitized recovery vaults, restore scripts, and Access Key separation.
tags:
  - hermes
  - backup
  - restore
  - disaster-recovery
  - vps
---

# Hermes Backup Recovery

## Purpose
Use this skill when the user asks how to back up, clone, migrate, or restore a Hermes Agent setup onto a new VPS. The goal is to restore Hermes safely without leaking Access Keys or confusing Hermes operational memory with external project source-code backups.

## Required Access Keys / Values
- GitHub access method for the private recovery vault, or an alternate transfer route.
- New VPS SSH access if copying archives directly.
- Runtime Access Keys to refill `~/.hermes/.env` after restore.
- OAuth re-login ability for providers such as OpenAI Codex, Nous, Qwen, etc.

Never print, store, or commit secret values. `.env`, `auth.json`, OAuth tokens, Telegram bot tokens, SSH keys, and cookies stay out of sanitized backups.

## Recovery Vault Shape
A sanitized Hermes recovery vault should include:
- Hermes source snapshot, usually `~/.hermes/hermes-agent`
- sanitized `config.yaml`, `SOUL.md`, `OPERATOR_PROFILE.md`
- Skill Runes
- Holographic/fact memory DB if the user wants the same knowledge
- Kanban DB and cron definitions when needed
- sanitized systemd user units
- `secrets/env.template` with key names only
- `scripts/restore.sh` that performs the actual restore

It should exclude:
- `.env` secret values
- `auth.json` / OAuth tokens
- Telegram/GitHub/model provider tokens
- SSH private keys
- raw logs, caches, media caches
- session transcript DB unless explicitly requested

For friend clones, ensure terminal Hermes and Comms Gates have operational toolsets. Top-level `toolsets` must include `terminal`, `file`, `code_execution`, `web`, `skills`, etc.; if it is restored as only `hermes-cli`, even the local terminal session can report that no active terminal execution gate/tools are available. For Telegram, `platform_toolsets.telegram` should include those operational toolsets plus `hermes-telegram`.

## Safe Read-only Checks
Before answering what is backed up, inspect:
```bash
cat backup-manifest.json
find . -maxdepth 2 -type d | sort
find . -name '.env' -o -name 'auth.json' -o -name 'state.db' -o -name '*.pem' -o -name '*.key'
```

If asked whether business app repos are included, verify by manifest/search. Do not assume Hermes memory equals project code.

## Restore Workflow
On the new VPS, after cloning the recovery vault:
```bash
sudo apt update
sudo apt install -y git curl rsync python3 python3-venv python3-pip build-essential

git clone https://github.com/OWNER/hermes-backup.git
cd hermes-backup
bash scripts/restore.sh
```

Then refill keys and verify:
```bash
nano ~/.hermes/.env
cd ~/.hermes/hermes-agent
hermes doctor
```

Then start the Comms Gate only after Access Keys and OAuth logins are ready:
```bash
loginctl enable-linger "$USER"
systemctl --user daemon-reload
systemctl --user enable --now hermes-gateway
systemctl --user status hermes-gateway --no-pager -n 50
```

## Restore Script Requirements
A good `scripts/restore.sh` should:
1. Ask before overwriting unless passed `--yes`.
2. Support `--dry-run`.
3. Install basic packages only when not skipped.
4. Restore config, source, skills, state, and systemd units.
5. Create `.env` from template but never overwrite existing `.env`.
6. Preserve or warn about existing `auth.json`; do not restore secrets silently.
7. Run `hermes doctor` after copy when not in dry-run mode.
8. Print next steps for `.env`, OAuth login, and gateway start.

## Transfer Routes Without GitHub Login
If the user does not want to authenticate GitHub on an untrusted VPS:
- Prefer encrypted archive transfer (`tar` + `gpg -c` + `scp`).
- Or use a fine-grained read-only token scoped to one repo and revoke after use.
- Or use a read-only deploy key and delete it after use.
- Avoid making a full recovery vault public if it contains memory/state/config context.
- If direct `scp` is blocked by separate Tailscale accounts/tailnets, invert the flow: publish a sanitized patch/archive at a controlled URL and have the target VPS `curl -L` it. Do not assume the operator can push files into another tailnet.

## Custom Source / Dashboard Patch Transfers
When the recovery vault includes a full Hermes source snapshot but the target already ran a safe knowledge-only restore, do not rerun a broad restore just to copy custom UI/code. Instead:
1. Identify the source-code battle group from the final working Hermes state (dashboard UI, backend APIs, runtime provider, quota/account helpers, gateway footer).
2. Create one `git diff --binary` patch from the source or recovery-vault snapshot.
3. Scan the patch for obvious secret formats before sharing.
4. On the target, create a timestamped tarball backup of `~/.hermes/hermes-agent`.
5. Run `git apply --check` before `git apply`; stop on conflicts and never force apply.
6. Verify with `python -m compileall ...` and web build checks where applicable.
7. Enable related config explicitly (for example Telegram runtime footer fields) and restart services only after verification/approval.

See `references/custom-hermes-dashboard-transfer.md` for the Codex multi-account + quota dashboard transfer pattern.

## GitHub Backup Timestamps
GitHub folder timestamps show the last commit that changed content under that path, not the last time a backup job inspected it. A daily backup can run successfully while stable folders such as `systemd/` or sanitized `secrets/` still show several days old because their bytes did not change. For freshness, check `backup-manifest.json`, the latest commit, and the paths that matter for the requested artifact (for custom dashboard code, usually `source/`).

## Common System Alerts
- **Clone only is not restore:** after `git clone`, run `bash scripts/restore.sh`.
- **Access Key missing:** restore can copy templates, but the Gate will not open until `.env` is filled.
- **OAuth missing:** `auth.json` is excluded, so login again on the new VPS.
- **Project code missing:** Hermes backup may restore knowledge about projects but not actual POS/Samurai/Spana/ImmoPilot repos. Use separate Project Vaults.
- **Delete public temp repo fails:** `gh repo delete` needs `delete_repo` scope; otherwise make it private.

## Ayman-Specific Reference
See `references/ayman-hermes-recovery-vault.md` for the known current recovery-vault shape and lessons from the restore-script forge.
