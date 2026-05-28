# Friend clone config boundary

## Lesson

A Hermes recovery repo can be valid for disaster recovery but still be unsafe as a friend-clone source if it restores the operator's full `config.yaml`. A full config transplant can carry provider routing, credential placeholders, platform/toolset overrides, dashboard assumptions, and local VPS behavior into a different machine. Fresh Hermes installs avoid this because config is generated for the new host.

## Rule

For friend clones, restore knowledge and identity, not the full operational config by default.

Prefer restoring:
- `SOUL.md` / persona and operator customization
- user skills and references
- non-secret memory/state that the user explicitly wants copied
- dashboard/source snapshot only when the clone is meant to share that body

Do not restore by default:
- `.env`
- `auth.json` or OAuth tokens
- full `config.yaml`
- provider credential IDs or placeholders
- host-specific service/runtime settings

## Safer clone flow

1. Back up any existing friend config before touching it.
2. Restore knowledge/persona/skills/memory only.
3. Let Hermes create or migrate a fresh config on the friend's VPS.
4. Run `hermes auth add openai-codex` or another provider setup interactively with the friend's own account.
5. Enable CLI toolsets on the fresh config: `terminal`, `file`, `web`, `skills`, `memory`, `session_search`, `delegation`, `code_execution`.
6. Test with a one-shot CLI command that forces toolsets:
   `hermes chat -q "Use your terminal tool to run: pwd && whoami" -t terminal,file,web,skills,memory,session_search,delegation,code_execution`

## Diagnostic focus for terminal-only failures

If the user says they are only using terminal Hermes, do not investigate Telegram/gateway first. Inspect CLI resolution:
- `hermes config path`
- `hermes tools list --platform cli`
- `platform_toolsets.cli` in `config.yaml`
- root `toolsets` in `config.yaml`
- `agent.disabled_toolsets`
- whether the installed source path and `which hermes` point to the same venv/source snapshot

## Restore-script implication

A recovery script should distinguish:
- full owner disaster recovery: can restore full config after sanitization
- friend clone / portable clone: should skip full config and write only minimal safe CLI defaults
