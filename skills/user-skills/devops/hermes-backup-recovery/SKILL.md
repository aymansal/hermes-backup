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
Use this skill when the user asks how to back up, clone, migrate, or restore a Hermes Agent setup onto a new VPS. The goal is to restore Hermes safely without leaking Access Keys or confusing Hermes operators with stale runtime state.

Reference: `references/friend-clone-tool-access.md` covers platform-specific tool access debugging after friend-VPS restores.

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
On a new VPS, install Hermes itself first so the global `hermes` command exists. The recovery vault restore script is primarily for knowledge/config/source state; its default `--knowledge-only` mode does **not** install the CLI globally.

```bash
sudo apt update
sudo apt install -y git curl rsync python3 python3-venv python3-pip build-essential
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash -s -- --skip-setup
source ~/.bashrc 2>/dev/null || true
export PATH="$HOME/.local/bin:$PATH"
which hermes
hermes --version
```

Then clone and restore the recovery vault:
```bash
git clone https://github.com/OWNER/hermes-backup.git
cd hermes-backup
bash scripts/restore.sh --knowledge-only --yes
```

Then use the Codex-first interactive setup path instead of manually editing `.env`:
```bash
hermes auth add openai-codex
hermes
```

Inside Hermes, ask it to configure Telegram interactively. The operator still must obtain or paste the Telegram BotFather token when prompted; Hermes/Codex cannot silently create or know that token. Hermes can then save it securely, configure the gateway, run `hermes doctor`, and start/verify the Comms Gate after operator approval.

Suggested mission prompt:
```text
Set up Hermes on this VPS using my ChatGPT Codex login as the model provider. Configure Telegram gateway from scratch. Guide me to create a Telegram bot with BotFather, ask me for the token, save it securely in ~/.hermes/.env without printing it back, configure the gateway, set my current Telegram chat as home, start the systemd user service only after I approve, and verify end-to-end.
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

## Friend VPS Full Clone Restores
When cloning Ayman's Hermes setup for a friend's VPS, do not leave the target with only restored config/knowledge and no global `hermes` command. Default friend-clone restore should restore source/dashboard + brain, then install/reinstall the Hermes CLI launcher from the restored source snapshot. Backup source snapshots are sanitized and may not include `.git`, so do **not** call the normal installer with `--dir ~/.hermes/hermes-agent` after restoring source; it will fail with “Directory exists but is not a git repository.” Instead create `~/.hermes/hermes-agent/venv`, run `venv/bin/python -m pip install -e '.[all]'`, and write a `~/.local/bin/hermes` launcher pointing at the venv entrypoint. After pip install, patch the installed OpenAI SDK null-output bug (`response.output`/`self.output` can be `None` from ChatGPT Codex) because the venv is not part of the sanitized source snapshot; otherwise friend clones can still crash with `TypeError: 'NoneType' object is not iterable`. Keep systemd service restoration opt-in via `--with-systemd`, and never restore `.env`, `auth.json`, OAuth tokens, Telegram bot tokens, provider keys, or private keys. See `references/friend-vps-full-clone-restore.md` for the session-derived restore script pattern and verification checks.

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

## Friend clone boundary

For friend VPS clones, do not treat a full owner disaster-recovery restore as the default. See `references/friend-clone-config-boundary.md`: restore knowledge/persona/skills/memory, but generate a fresh host-local config and auth with the friend's own account. Full `config.yaml` restore is for owner disaster recovery, not portable friend clones.

## Common System Alerts
- **Clone only is not restore:** after `git clone`, run `bash scripts/restore.sh`.
- **Access Key missing:** restore can copy templates, but the Gate will not open until `.env` is filled.
- **OAuth missing:** `auth.json` is excluded, so login again on the new VPS.
- **Project code missing:** Hermes backup may restore knowledge about projects but not actual POS/Samurai/Spana/ImmoPilot repos. Use separate Project Vaults.
- **Delete public temp repo fails:** `gh repo delete` needs `delete_repo` scope; otherwise make it private.

## Ayman-Specific Reference
See `references/ayman-hermes-recovery-vault.md` for the known current recovery-vault shape and lessons from the restore-script forge.
