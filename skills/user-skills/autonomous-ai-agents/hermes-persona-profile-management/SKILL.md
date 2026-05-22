---
name: hermes-persona-profile-management
description: "Manage Hermes persona (SOUL.md) and user/operator profile files without confusing memory summaries with actual config artifacts."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, persona, profile, memory, soul, configuration]
    created_by: agent
---

# Hermes Persona & Operator Profile Management

Use this skill when the user asks to update, inspect, install, or troubleshoot Hermes' persona / "soul" / identity, or the user's operator profile. This skill is especially relevant when the user expects an actual file/config change, not just a memory update.

## Core distinction

- `~/.hermes/SOUL.md` = assistant persona and behavior: how Hermes should speak and operate.
- `~/.hermes/memories/USER.md` = compact active user profile loaded into context.
- A separate long-form profile file, e.g. `~/.hermes/OPERATOR_PROFILE.md`, can preserve a detailed dossier without bloating active memory.
- Persistent memory entries are useful but are not a replacement for requested file/config writes.

## Workflow

1. Clarify the artifact only if the user's wording is ambiguous.
   - If they say "make this your soul" or "update your soul", update `~/.hermes/SOUL.md`.
   - If they say "this is me" or provide an operator profile, save it as a user/operator profile, not as the persona.

2. Before writing, identify the target path:
   - Persona: `~/.hermes/SOUL.md`
   - Compact profile: `~/.hermes/memories/USER.md`
   - Long profile: `~/.hermes/OPERATOR_PROFILE.md` or another clearly named file.

3. Write the actual artifact when the user clearly requested it.
   - Do not only call memory.
   - Do not only summarize.
   - If the user asks for an overwrite or full replacement, perform the file write and verify it.

4. Verify after writing:
   - Use a line count / first lines check, e.g. `wc -l <file>` and `head -5 <file>`.
   - Report exactly which files changed.
   - If one artifact was not changed, say so plainly.

5. Keep active memory compact:
   - Save detailed user dossiers to a long-form markdown file.
   - Write a compact summary into `~/.hermes/memories/USER.md` so future sessions load cleanly.

## User-specific pitfall

This user dislikes partial missions. If they ask to update a file/config, they expect the actual artifact to change. A memory-only update after a file/config request is a failed mission.

Say what changed, verify it, and avoid implying a config file was updated if only memory was updated.

## Reading commands to give the user

```bash
cat /home/ubuntu/.hermes/SOUL.md
nl -ba /home/ubuntu/.hermes/SOUL.md
cat /home/ubuntu/.hermes/memories/USER.md
cat /home/ubuntu/.hermes/OPERATOR_PROFILE.md
```

Tell the user not to prefix these with `bash` or `sh`; those commands start a new shell and can confuse command entry.

## Safety

- Do not print or store secrets in persona/profile files.
- If overwriting a large existing profile, confirm if the user did not clearly request replacement.
- When the user clearly supplies replacement content and asks to update the file, execute and verify instead of asking redundant confirmation.

## Reference

See `references/shadow-operator-profile-session.md` for the session-specific lesson that motivated this skill.
