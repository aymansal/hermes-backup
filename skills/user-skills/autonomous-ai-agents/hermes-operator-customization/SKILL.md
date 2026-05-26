---
name: hermes-operator-customization
description: "Customize Hermes for an operator: SOUL.md persona, user profile memory files, and Telegram gateway setup with exact execution and verification."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, persona, memory, gateway, telegram, operator-setup]
---

# Hermes Operator Customization

Use this skill when the user asks to personalize Hermes itself for a recurring operator workflow: changing the assistant persona, saving an operator profile, configuring the Telegram Comms Gate, or correcting how Hermes should execute setup tasks for this user.

This skill is intentionally a companion to the protected `hermes-agent` skill. Load `hermes-agent` first for canonical commands, then use this skill for user-specific workflow discipline and recurring setup patterns.

## Core rule: exact artifact changes, not implied completion

If the user asks to update a file/config/system artifact, change the actual artifact and verify it. Do not only save a memory summary or say it is remembered.

Examples:

- If the user says “make this your soul”, write the full persona into `~/.hermes/SOUL.md` and verify with `wc -l` or `head`.
- If the user gives an operator profile, preserve the long form in a real file and keep the active memory/profile compact.
- If the user asks to establish Telegram, start the actual setup flow or directly configure the required env/config after receiving credentials.

Pitfall learned: saving a preference in memory is not the same as updating `SOUL.md`. The user considers that a sloppy half mission.

## Read-only first, then explicit approval for side effects

Ayman's operational rule is strict: for Hermes config edits, `.env` writes, package installs, service/gateway/dashboard restarts, cron creation/runs, GitHub pushes, or any other side effect, first report the exact proposed action, what it touches, risk/rollback, and wait for Ayman's approval. A pasted Access Key plus "use it" is not blanket permission to store it, switch providers, or restart services; ask which steps he approves. After approval, execute and verify.

Default diagnostic checks before Hermes config changes:

```bash
hermes --version
hermes gateway status
hermes config path
hermes config env-path
```

For file verification:

```bash
wc -l ~/.hermes/SOUL.md ~/.hermes/memories/USER.md 2>/dev/null || true
head -5 ~/.hermes/SOUL.md
```

If the user clearly asks to write/update a non-destructive config/profile file, execute it and verify. If the action is destructive, risky, or exposes secrets, confirm first.

## Persona / Soul updates

Canonical file:

```text
~/.hermes/SOUL.md
```

Workflow:

1. Preserve the user’s persona text as provided unless they ask for compression.
2. Write it to `~/.hermes/SOUL.md`.
3. Verify line count and first lines.
4. Tell the user exactly what file changed.

Addressing/title pitfall: for Ayman’s Shadow System persona, the assistant is the Shadow System Operator / Igris. Address Ayman as “Shadow Monarch” unless he gives a newer explicit title. If the user corrects the assistant name, title, hierarchy, or persona vocabulary, update `SOUL.md`, user memory, and (when available) fact/Holographic memory so the framing remains consistent across sessions. Do not preserve stale persona names in skill text.

Memory-law pitfall: when local memory/Holographic is enabled, `SOUL.md` should explicitly instruct Hermes to save useful durable facts, while avoiding memory pollution. Add or preserve a section that says to proactively store stable preferences, business/project facts, environment facts, architecture/workflow decisions, and reusable lessons; never store secrets, temporary progress, raw logs, stale PR/issue/commit IDs, or one-off chat noise. Procedures belong in Skill Runes; human-readable company knowledge belongs in Obsidian notes.

Verification:

```bash
wc -l ~/.hermes/SOUL.md
head -5 ~/.hermes/SOUL.md
grep -n -i 'Shadow Monarch\|Shadow Archive\|Feed the Shadow Archive' ~/.hermes/SOUL.md
```

To show the user how to inspect it:

```bash
cat ~/.hermes/SOUL.md
nl -ba ~/.hermes/SOUL.md
```

## Operator profile updates

For a long user/operator dossier, use two layers:

1. Full long-form archive:

```text
~/.hermes/OPERATOR_PROFILE.md
```

2. Compact active profile / memory file:

```text
~/.hermes/memories/USER.md
```

Why: the full profile preserves the user’s exact context, while the compact profile stays small enough to be useful in future sessions.

Verification:

```bash
wc -l ~/.hermes/OPERATOR_PROFILE.md ~/.hermes/memories/USER.md
head -3 ~/.hermes/OPERATOR_PROFILE.md
head -3 ~/.hermes/memories/USER.md
```

## Local memory provider setup

Load `hermes-agent` before answering or acting. Use this section when the user asks to enable a Hermes memory plugin/provider, especially local-first memory such as Holographic.

Safe inspect first:

```bash
hermes memory status
hermes config path
hermes config env-path
```

Local-first default for this operator: prefer built-in Hermes memory plus the local Holographic provider before suggesting paid/cloud memory providers. Do not ask for cloud Access Keys unless the user explicitly chooses a cloud provider.

For Holographic setup, the expected durable config shape is:

```yaml
memory:
  provider: holographic
  holographic:
    db_path: ~/.hermes/memory_store.db
    default_trust: '0.5'
    hrr_dim: '1024'
```

Important pitfall: `default_trust` should be a confidence-like value around `0.5`; if the setup prompt receives `3` or another high number, correct it back to `0.5` before verification. Do not preserve obviously invalid trust values just because the prompt accepted them.

After changing the memory provider, resummon Hermes surfaces that need the new config, then verify:

```bash
hermes gateway restart
hermes memory status
grep -n -i 'provider: holographic\|default_trust\|hrr_dim\|db_path' ~/.hermes/config.yaml
```

Report only the provider/status/config keys. Never expose secrets from `.env` during memory setup.

## Hermes auxiliary model routing / quota control

Load `hermes-agent` before answering or acting. Use this section when Ayman wants to reduce Codex/OpenAI quota burn by moving Hermes auxiliary work — compression, web extraction, title generation, approvals, memory review, curator review — to cheaper providers such as OpenCode Go, or when he reports dashboard/Telegram Codex quota display mismatches.

Workflow discipline:

1. Phase 1: perform a read-only scan only — `hermes config path`, `hermes config env-path`, `hermes --version`, `hermes status --all`, and inspect relevant `config.yaml` sections.
2. Check only presence/absence of Access Keys in `.env`; never print key values.
3. Verify provider/model IDs from local Hermes code/docs before proposing config. Do not assume model slugs.
4. Report current config and the exact proposed YAML patch.
5. Apply only after Ayman approves. Before writing, create a backup of `~/.hermes/config.yaml`; after writing, run `hermes config check`.

For Ayman’s current preference, the intended role split is:

- compression: cheap huge-context model, preferably OpenCode Go `deepseek-v4-flash` if live verification confirms it is served.
- curator/background memory: judgment model, OpenCode Go `glm-5.1` with `glm-5` fallback.
- web/doc extraction: long structured summaries, OpenCode Go `kimi-k2.6` with `kimi-k2.5` fallback.
- approval/safety: judgment model is preferred, but verify the actual Hermes approval path because small hardcoded token budgets can break reasoning-heavy models.
- title generation/tiny metadata: prefer a fast model that returns final `content` without spending the whole budget in `reasoning_content`; in live OpenCode Go tests `minimax-m2.7` and `qwen3.5-plus` behaved better than `deepseek-v4-flash` for real title generation.

See `references/opencode-go-auxiliary-routing.md` for the detailed inspection pattern, known Hermes v0.14.0 OpenCode Go model list, draft config shape, Access Key activation pitfalls, smoke-test commands, reasoning-content pitfalls, and quota-warning caveat. A reusable smoke-test helper lives at `scripts/test_auxiliary_routing.py`.

Access Key handling for Ayman: he considers his Tailscale-protected Hermes chat acceptable for sharing Access Keys and prefers non-alarmist handling. Still do not echo, log, or store secrets in memory/skills. If he provides an Access Key as part of an approved Hermes provider-routing change, write it to the requested `.env`/config target as part of the setup instead of treating it as missing later; verify by active-env presence/length/status only.

Important env pitfall: commented template lines in `.env` such as `# OPENCODE_GO_API_KEY=` are not active credentials. Presence checks must ignore commented lines and verify the live shell/runtime can actually read `OPENCODE_GO_API_KEY`; otherwise auxiliary smoke tests will fail with “Provider 'opencode-go' is set in config.yaml but no API key was found.”

## Native Hermes Web Dashboard setup

Load `hermes-agent` before answering or acting.

Important pitfall: if the user says “native Hermes web UI” or “Hermes web UI”, do not default to Open WebUI. Hermes has its own native Web Dashboard launched with `hermes dashboard`. Open WebUI is a separate third-party frontend connected through the API Server; mention it only when the user explicitly asks for Open WebUI or an OpenAI-compatible external frontend.

Read-only scan:

```bash
hermes dashboard --help
hermes dashboard --status
ss -ltnp | grep ':9119\\b' || true
python3 - <<'PY'
mods = ['fastapi', 'uvicorn', 'ptyprocess']
for m in mods:
    try:
        __import__(m); print(m, 'OK')
    except Exception as e:
        print(m, 'MISSING', e.__class__.__name__)
PY
```

Native dashboard basics:

```bash
hermes dashboard --no-open
# default URL inside the machine:
# http://127.0.0.1:9119
```

Optional chat tab:

```bash
hermes dashboard --tui --no-open
```

If dependencies are missing, install the web/PTY extras in the active Hermes environment:

```bash
pip install 'hermes-agent[web,pty]'
```

Security rule: the native dashboard can read/write `config.yaml` and `.env`, including API keys. It has no standalone strong authentication. Prefer binding to `127.0.0.1` and using an SSH tunnel from the user’s computer:

```bash
ssh -L 9119:127.0.0.1:9119 ubuntu@VPS_IP
# Then open locally:
# http://127.0.0.1:9119
```

Only bind to a Tailscale IP or `0.0.0.0 --insecure` when the user explicitly accepts the risk. Never expose the dashboard to the public internet.

## Local voice/STT setup

Load `hermes-agent` before answering or acting. Use this section when Ayman asks about Telegram voice messages, local speech-to-text, Spokenly, Whisper, NVIDIA Parakeet, or custom ASR.

Key pitfall: if the user mentions an "NVIDIA voice model" or "Parakeet v2", do **not** assume the issue is GPU/CUDA. NVIDIA Parakeet is an ASR model family and may be used CPU/local/remote depending on the runtime. Clarify model/runtime only when it changes the command path.

Hermes has two relevant local STT paths:

- Built-in `stt.provider: local` uses `faster-whisper`.
- `stt.provider: local_command` uses `HERMES_LOCAL_STT_COMMAND` and can bridge Parakeet, Spokenly, or any custom ASR wrapper that writes a `.txt` transcript.

For custom ASR, prefer an isolated venv and wrapper script instead of installing heavy ML deps into the live Hermes environment. On Oracle ARM free-tier VPSes, Parakeet 0.6B-class models are usually feasible for short Telegram voice notes with 4 OCPUs/24 GB RAM, but ARM64 dependency compatibility is the main risk. If swap is 0, propose adding an 8 GB swapfile before heavy ML installs/runs, but ask approval because it changes system config.

See `references/local-stt-parakeet.md` for the read-only suitability checks, Parakeet v2/v3 tradeoff, `HERMES_LOCAL_STT_COMMAND` bridge shape, and PC-over-Tailscale alternative.

## Telegram Comms Gate setup

Load `hermes-agent` before answering or acting.

Read-only scan:

```bash
hermes gateway status
hermes config path
hermes config env-path
```

If `hermes gateway setup` works interactively, use it. If the terminal UI makes selection unreliable, use the env-backed path: Hermes auto-enables Telegram when `TELEGRAM_BOT_TOKEN` is present.

Required Access Key:

```text
TELEGRAM_BOT_TOKEN
```

Never print or repeat the token back. Write it only to `~/.hermes/.env` or let the user paste it into setup.

After token/config is present:

```bash
hermes gateway install
hermes gateway start
sudo loginctl enable-linger $USER
hermes gateway status
```

If the user explicitly pastes the token and asks the agent to do it, do not repeat the token. Write/update `~/.hermes/.env` programmatically, replace any existing/commented `TELEGRAM_BOT_TOKEN` and `GATEWAY_ALLOW_ALL_USERS`, set file mode `0600`, then verify only booleans/redacted facts:

```bash
python3 - <<'PY'
from pathlib import Path
import os, re
p = Path.home() / '.hermes/.env'
p.parent.mkdir(parents=True, exist_ok=True)
text = p.read_text() if p.exists() else ''
token = '<TOKEN_FROM_USER>'
keys = {
    'TELEGRAM_BOT_TOKEN': f'TELEGRAM_BOT_TOKEN={token}',
    'GATEWAY_ALLOW_ALL_USERS': 'GATEWAY_ALLOW_ALL_USERS=false',
}
out, seen = [], set()
for line in text.splitlines():
    m = re.match(r'^\s*#?\s*([A-Za-z_][A-Za-z0-9_]*)\s*=', line)
    if m and m.group(1) in keys:
        k = m.group(1)
        if k not in seen:
            out.append(keys[k]); seen.add(k)
    else:
        out.append(line)
for k, v in keys.items():
    if k not in seen:
        if out and out[-1].strip(): out.append('')
        out.append(v)
p.write_text('\n'.join(out).rstrip() + '\n')
os.chmod(p, 0o600)
print('Telegram env configured; token redacted; permissions set to 600')
PY
```

`hermes gateway install` can prompt twice. In non-interactive tool use, feed both confirmations:

```bash
printf 'Y\nY\n' | hermes gateway install
hermes gateway start
hermes gateway status
```

Verify Telegram API without exposing the token by calling `getMe` from a script that reads `.env` and prints only `ok`, bot username, and bot display name. Also inspect systemd status/logs with token redaction.

If Telegram does not respond:

```bash
grep -i "telegram\|error\|failed\|unauthorized\|allowed\|pair" ~/.hermes/logs/gateway.log | tail -80
journalctl --user -u hermes-gateway --no-pager -n 80
```

Security recommendation for this user: prefer pairing/allowed users over allowing all users. With `GATEWAY_ALLOW_ALL_USERS=false` and no allowlist, the first DM should trigger pairing; tell the user to message the bot, then approve the code with `hermes pairing approve telegram CODE`.

## Hermes private recovery backup vault

Load `hermes-agent` before answering or acting. Use this section when Ayman asks to back up Hermes itself, make the current operator setup portable to another VPS, or keep a private GitHub recovery vault up to date.

Core principle: create a recovery vault, not a raw dump of `~/.hermes`. The vault should resummon Hermes quickly while protecting Access Keys and high-privacy runtime artifacts.

Recommended contents:

- Hermes source snapshot with local patches.
- Sanitized `config.yaml`.
- `SOUL.md` and `OPERATOR_PROFILE.md`.
- Installed Skill Runes.
- Local memory DB (`memory_store.db`) via SQLite backup API when possible.
- Durable automation state such as `kanban.db` and cron definitions.
- Sanitized Hermes systemd user units.
- `secrets/env.template` with variable names only, never values.
- README, manifest, restore helper, and deterministic backup refresher script.

Always exclude `.env` values, `auth.json`, OAuth tokens, GitHub tokens, Telegram bot tokens, SSH keys, cookies, private keys, raw logs, caches, media caches, process locks, and `state.db` session transcripts unless the user explicitly requests transcript migration and accepts the privacy risk.

Before committing/pushing a backup, run a leak check against literal current `.env` values and refuse to commit if any value appears in staged text or DB files. Report file paths only, not secret values.

For “always backed up,” prefer a no-agent cron/Raid Timer that runs a deterministic script daily, stays silent when nothing changed, and reports only pushes or errors.

See `references/private-recovery-backup-vault.md` for the full recovery-vault shape, restore path, verification commands, and pitfalls.

### Fresh install + knowledge-only restore pitfall

When restoring Hermes onto a new/friend VPS, prefer **fresh official install first, knowledge-only restore second**. Do not restore `source/hermes-agent/` over the install by default; it can create broken venv/path/symlink states where the global `hermes` command is missing or only works from a specific directory.

Recommended flow:

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
source ~/.bashrc 2>/dev/null || true
export PATH="$HOME/.local/bin:$PATH"
cd ~/hermes-backup
git pull
bash scripts/restore.sh --knowledge-only --yes
hermes login --provider openai-codex
hermes doctor
hermes
```

The recovery repo restore helper should default to `--knowledge-only` (persona/profile/config/skills/memory/kanban/cron, `.env` template only) and reserve `--full` for explicit exact recovery of source/systemd. See `references/hermes-fresh-install-knowledge-restore.md` for the detailed pattern and verification commands.

## User communication style during these tasks

The user wants direct, tactical execution under his command authority:

- Ayman decides operational steps; the assistant reports and waits for approval before side effects.
- Do the action when safe and explicitly approved/requested.
- Verify results before claiming success.
- Avoid long explanations while they are trying to get a command.
- If they ask for “command to see all of it”, give the exact command first.
- If a setup needs a missing token/API key, stop and ask for the Access Key.
- Do not frame yourself as the decision-maker; the Shadow System Operator/General executes the Shadow Monarch's decisions.

Use Shadow System Operator flavor sparingly: practical report first, flavor second.

## References

- `references/session-2026-05-21-persona-profile-telegram.md` — session-specific lessons: SOUL.md vs memory, operator profile split, Telegram direct env fallback, Holographic trust correction, Shadow Archive memory-law insertion, Shadow Monarch title correction, and native Hermes Web Dashboard vs Open WebUI distinction.
- `references/native-dashboard-tailscale-shadow-realm.md` — persistent native Hermes dashboard (“Shadow Realm”) over Tailscale via systemd user service, verification commands, reboot-survival checks, and security caveats.
- `references/native-dashboard-codex-quota.md` — Codex/ChatGPT quota display in the native dashboard and Telegram runtime footer: live `/usage` endpoint, 5-second dashboard polling, sanitized data only, remaining quota (`% left`) preference, and timezone mismatch pitfall between browser-rendered dashboard and VPS-rendered Telegram footer.
- `references/private-recovery-backup-vault.md` — private GitHub recovery vault pattern for backing up Hermes source/config/skills/memory/systemd without committing Access Keys, logs, caches, or session transcripts.
- `references/hermes-fresh-install-knowledge-restore.md` — safer new-VPS recovery pattern: install Hermes fresh for a healthy command/venv/PATH layer, then restore only Hermes persona/config/skills/memory/kanban/cron knowledge before Codex OAuth login.
- `references/local-stt-parakeet.md` — local/custom STT bridge for Hermes voice messages using NVIDIA Parakeet/Spokenly via `HERMES_LOCAL_STT_COMMAND`, including Oracle ARM VPS suitability checks and Tailscale bridge alternative.
