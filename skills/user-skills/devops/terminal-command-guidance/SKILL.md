---
name: terminal-command-guidance
description: "Guide operators through shell commands safely: copy-paste hygiene, prompt confusion, read-only diagnostics, and interpreting terminal output."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [terminal, shell, cli, troubleshooting, operator-guidance, commands]
    related_skills: [systematic-debugging, hermes-agent]
---

# Terminal Command Guidance

## Purpose

Use this Skill Rune when helping a user run shell commands manually in a terminal, especially when they are new to CLI workflows, pasting commands incorrectly, entering nested shells, or reporting that commands produce no output.

The goal is practical control of the System: clear commands, safe read-only checks first, no secret exposure, and no guesswork.

## Triggers

Load this skill when the user:
- Asks how to read, inspect, or edit files from the terminal.
- Says a command "shows nothing" or "doesn't work".
- Pastes a transcript showing prompts like `$`, `ubuntu@host:~$`, `>`, or errors like `command not found`.
- Copies the language label or wrapper word (`bash`, `sh`, etc.) instead of just the command.
- Needs to run Hermes CLI commands, inspect `~/.hermes`, logs, services, ports, or config files.

## Operator Tone

For this user, keep the Shadow System Operator style when giving CLI guidance: direct, tactical, practical first, lightly dramatic second. Use phrases like "read-only scan first" or "Battle Trace" sparingly, but always make the real technical command and interpretation clear.

## Read-Only First

When diagnosing terminal confusion, start with commands that cannot modify state:

```sh
whoami
printf 'HOME=%s\nHERMES_HOME=%s\nPWD=%s\n' "$HOME" "${HERMES_HOME:-}" "$PWD"
ls -la /path/to/file
wc -c /path/to/file
nl -ba /path/to/file
stat /path/to/file
```

Do not suggest edits, deletes, service restarts, or config writes until the user has confirmed the target path/account/session.

## Copy-Paste Hygiene

### Do

Give one command at a time when the user is struggling. If the user says “bro give me command” or shows frustration, put the command first with no heading or lecture:

```sh
nl -ba /home/ubuntu/.hermes/SOUL.md
```

Use absolute paths for diagnostics when path expansion might be confusing:

```sh
stat /home/ubuntu/.hermes/SOUL.md
```

Include an end marker when testing whether output is hidden or empty:

```sh
cat /home/ubuntu/.hermes/SOUL.md; echo '<<< END OF FILE'
```

### Do Not

Do not tell a confused user to paste a block headed by a shell name like this:

```text
bash
cat ~/.hermes/SOUL.md
```

They may type `bash` or `sh` first, which starts a nested shell and changes the prompt. Instead, say explicitly:

```text
Do not type `bash` or `sh`. Paste only this command:
```

Then provide exactly one command.

## Recognizing Nested Shell Confusion

If the transcript shows:

```text
ubuntu@host:~$ sh
$
```

or:

```text
ubuntu@host:~$ bash
```

The user started another shell. First instruct them to leave it:

```sh
exit
```

Then continue from the original prompt.

If the transcript shows:

```text
$ gfn
sh: 1: gfn: not found
```

Do not chase the missing command as the main issue unless it is relevant. Explain that `gfn` was simply typed as a command and the shell correctly reported it missing.

## Minimal Debug Path for "Command Shows Nothing"

1. Verify terminal output works:

```sh
printf 'TEST_OUTPUT_WORKS\n'
```

2. Verify identity and paths:

```sh
whoami
printf 'HOME=%s\nHERMES_HOME=%s\nPWD=%s\n' "$HOME" "${HERMES_HOME:-}" "$PWD"
```

3. Verify file existence and size:

```sh
ls -la /absolute/path/to/file
wc -c /absolute/path/to/file
stat /absolute/path/to/file
```

4. Read with line numbers:

```sh
nl -ba /absolute/path/to/file
```

5. If content may be invisible/control characters, inspect bytes:

```sh
xxd /absolute/path/to/file | head
```

6. If shell builtins or aliases are suspect, use Python as a fallback reader:

```sh
python3 -c 'from pathlib import Path; p=Path("/absolute/path/to/file"); print("exists", p.exists()); print("size", p.stat().st_size if p.exists() else "missing"); print(p.read_text() if p.exists() else "")'
```

## Interpreting Results

- `No such file or directory`: wrong path, wrong user, wrong profile, or different machine/container.
- `wc -c` returns `0`: the file exists but is empty.
- `wc -c` returns nonzero but `cat` appears blank: content may be comments/whitespace, terminal display issue, pager confusion, or invisible characters; use `nl -ba` and `xxd`.
- Prompt changes from `user@host:~$` to `$`: user entered another shell; ask them to `exit` before continuing.
- `command not found`: either a typo, copied placeholder, or missing binary. Do not persist a rule that the tool is broken; diagnose the specific command.

## Safety

- Never ask the user to paste secrets into chat.
- When commands involve credentials, show placeholders or environment variable names only.
- Confirm before destructive commands: deletion, overwrites, service stops, firewall changes, database operations, or production deploy changes.

## References

- `references/shell-prompt-confusion.md` — session-derived pattern for users accidentally typing `bash`/`sh` wrappers and interpreting blank command output.
