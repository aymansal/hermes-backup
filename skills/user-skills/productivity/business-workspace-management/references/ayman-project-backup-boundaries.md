# Ayman Project Backup Boundaries

## Lesson
Ayman may ask whether the Hermes recovery backup also includes POS/Samurai/Spana/ImmoPilot or other business app source code. Do not assume it does.

## Current known boundary
The Hermes recovery vault is scoped to Hermes itself and its operational brain:
- Hermes source snapshot under `~/.hermes/hermes-agent`
- sanitized Hermes config/persona/profile
- Skill Runes
- Holographic memory DB
- Kanban DB
- cron definitions
- sanitized systemd user units
- `.env` key-name template only

It intentionally excludes or does not cover by default:
- external project/app repo folders
- POS/Samurai/Spana/ImmoPilot source code unless explicitly added to a backup plan
- secret values, OAuth tokens, `auth.json`, SSH keys
- logs/caches/session transcript DB

## Answer pattern
If asked, say plainly:
- “Hermes backup restores Hermes knowledge and operation.”
- “It may contain notes/references about projects.”
- “It does not necessarily contain the actual project code.”
- “We need a separate Project Vault / repo backup layer for the apps.”

## Safe verification pattern
Use read-only checks before claiming coverage:
- inspect the backup manifest
- search the backup for project names
- list top-level included directories
- inspect project workspace roots if known

## Recommended architecture
Use two layers:
1. **Hermes Recovery Vault** — agent brain/body/config/skills/memory/automation.
2. **Project Vaults** — one GitHub/private backup or encrypted archive per actual business app/client system.

Avoid mixing all business source code into the Hermes backup unless Ayman explicitly wants a monorepo-style disaster-recovery vault and accepts the size/security tradeoffs.
