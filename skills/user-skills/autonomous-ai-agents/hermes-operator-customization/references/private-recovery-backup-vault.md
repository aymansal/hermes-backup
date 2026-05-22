# Hermes private recovery backup vault — 2026-05-22

## Trigger

Use this reference when Ayman asks to "backup yourself", make Hermes portable to another VPS, create a private GitHub recovery vault, or keep Hermes backed up automatically.

## Class-level lesson

A portable Hermes backup should be a recovery vault, not a raw copy of `~/.hermes`. Back up enough to resummon the System quickly while excluding Access Keys and volatile/session data.

## Safe backup contents

Include:

- Hermes source snapshot, including local patches and untracked operational files that affect runtime.
- Sanitized `~/.hermes/config.yaml`.
- `~/.hermes/SOUL.md` and `~/.hermes/OPERATOR_PROFILE.md`.
- Installed Skill Runes from `~/.hermes/skills/`.
- Local memory DB such as `~/.hermes/memory_store.db`, copied via SQLite backup API when possible.
- Durable automation state such as `kanban.db` and cron definitions, if present.
- Sanitized systemd user units from `~/.config/systemd/user/hermes*.service` and `hermes*.timer`.
- `secrets/env.template` containing environment variable names only, with blank values.
- A `scripts/restore.sh` helper and clear README.

Exclude:

- `.env` values.
- `auth.json` and OAuth/credential-pool files.
- GitHub tokens, Telegram bot tokens, provider API keys, SSH keys, cookies, private keys.
- Raw logs.
- Session transcript DB (`state.db`) unless the user explicitly requests transcript migration and accepts the privacy risk.
- Cache/media/process/lock files.

## Workflow

1. Load `hermes-agent` first for canonical Hermes paths and commands.
2. Use or create a private GitHub repo, e.g. `aymansal/hermes-backup`.
3. Clone it under `~/.hermes/backups/<repo>` so backup artifacts stay outside the active source checkout.
4. Build the vault from a clean staging directory while preserving `.git`.
5. Sanitize config-like files by replacing secret-looking key values with `<SET_ON_RESTORE>`.
6. Generate `secrets/env.template` from keys in `~/.hermes/.env`, never values.
7. Use SQLite backup API for live SQLite DBs; avoid copying WAL/shm files directly unless doing a full cold backup.
8. Run a literal leak check against current `.env` values before committing. If any secret value appears in staged text or DB backup, refuse to commit and report the file path only.
9. Commit and push to the private repo.
10. Verify remote visibility is `PRIVATE`, default branch exists, latest commit is pushed, root contents include README/manifest/scripts, and local backup repo is clean.
11. If the user wants "always backed up", create a cron/no-agent Raid Timer that runs a deterministic backup script daily. The script should stay quiet when nothing changed and speak only on push/error.

## Restore shape

A fresh VPS restore should look like:

```bash
git clone https://github.com/aymansal/hermes-backup.git
cd hermes-backup
bash scripts/restore.sh

# Fill Access Keys from secure source
nano ~/.hermes/.env

cd ~/.hermes/hermes-agent
hermes doctor
hermes gateway status
```

Do not claim the new VPS is fully operational until `.env` Access Keys are restored and `hermes doctor` / gateway status pass.

## Verification commands

```bash
gh repo view OWNER/REPO --json nameWithOwner,visibility,isPrivate,defaultBranchRef,url,pushedAt

gh api repos/OWNER/REPO/contents --jq '.[].name' | sort

git -C ~/.hermes/backups/REPO status --short --branch
```

## Pitfalls

- A private repo is not a reason to upload secrets. Private reduces blast radius; it does not remove the need for sanitization.
- Do not upload `state.db` by default. It is valuable for transcript recall but high privacy risk and not required to restore the operational System.
- Do not read/print `.env` values while summarizing. Presence/count/key names are enough.
- A broad regex secret scan will flag example tokens in tests/docs. Treat those as secondary; the decisive scan is whether current literal `.env` values appear in the staged vault.
- Keep the backup job script deterministic and non-chatty so recurring cron delivery does not spam Telegram.
