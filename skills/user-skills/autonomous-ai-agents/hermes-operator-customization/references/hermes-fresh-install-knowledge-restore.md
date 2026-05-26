# Fresh Hermes install + knowledge-only restore

Use this when Ayman wants to clone his Hermes behavior/persona/knowledge onto another VPS without breaking the official Hermes install or global `hermes` command.

## Lesson

Do **not** restore the backed-up Hermes source tree over a fresh install by default. Restoring `~/.hermes/hermes-agent` can create path/venv/symlink confusion where `hermes` only works from a specific directory or does not exist in `PATH`.

Preferred architecture:

1. Install Hermes fresh using the official installer so the command wrapper, venv, and shell PATH are created correctly.
2. Restore the *knowledge layer* only: persona/profile files, config, skills, memory DB, kanban/cron state, and `.env` template if needed.
3. Re-login OAuth providers such as OpenAI Codex / ChatGPT on the new VPS.
4. Run `hermes doctor` and launch Hermes.

## Recommended new-VPS flow

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

source ~/.bashrc 2>/dev/null || true
export PATH="$HOME/.local/bin:$PATH"
which hermes
hermes --version

cd ~/hermes-backup
git pull
bash scripts/restore.sh --knowledge-only --yes

hermes login --provider openai-codex
hermes doctor
hermes
```

## Restore script shape

The backup repo's `scripts/restore.sh` should default to `--knowledge-only`, not full source restore. It may still offer `--full` for exact recovery, but full mode should be clearly marked invasive because it may move/replace `~/.hermes/hermes-agent` and restore systemd units.

`--knowledge-only` should restore:

- `~/.hermes/config.yaml` and persona/profile files from `config/`
- `~/.hermes/skills/` from `skills/user-skills/`
- `~/.hermes/memory_store.db`, `kanban.db`, and cron definitions from `state/`
- `~/.hermes/.env` from `secrets/env.template` only if `.env` does not already exist

`--knowledge-only` should not restore:

- `source/hermes-agent/`
- user systemd units
- `.env` secret values
- `auth.json` / OAuth tokens

## Pitfalls

- If `hermes: command not found`, first fix the install/PATH layer; do not keep copying source snapshots over the install.
- If no `venv/bin/hermes` or `.venv/bin/hermes` exists under `~/.hermes/hermes-agent`, that is not a memory/knowledge failure; install Hermes fresh.
- Do not tell the user to fill every Access Key if they want OAuth-first setup. For Codex/ChatGPT, use `hermes login --provider openai-codex` first, then let Hermes configure remaining providers.
- If the user is frustrated and asks for commands, give the exact command sequence first and keep explanation short.

## Verification

```bash
which hermes
hermes --version
hermes login --provider openai-codex
hermes doctor
ls -lh ~/.hermes/memory_store.db ~/.hermes/config.yaml 2>/dev/null
ls ~/.hermes/skills | head
```
