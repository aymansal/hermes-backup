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
- Asks to restart, resummon, refresh, or bring back a local preview/dev server bound to a port.

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

For dev-server resummons, inspect the exact port listener and process tree before terminating anything. Never kill random `node` processes; release only verified PIDs bound to the requested preview Gate, then verify local and remote/Tailscale HTTP status codes before reporting success. If a Next.js preview is alive but shows raw/plain HTML, missing styling, CSS 404s, route 500s, or late `Local:` watch notifications, follow `references/next-dev-preview-poison.md`: verify HTML and CSS separately, then clear `.next` and resummon only the verified preview process tree.

For non-Tailscale access to a local/static preview, use `references/temporary-public-preview-tunnels.md`: verify local health first, try public IP only if appropriate, ask approval before exposing a temporary public tunnel, prefer `cloudflared tunnel --url http://127.0.0.1:<PORT>`, parse `--logfile` if background stdout is empty, verify HTTP 200 on the generated URL and the specific app route/CSS the user will show, and remind Ayman that anyone with the link can view it while the tunnel runs.

## Safe Dev Server Resummon

When resummoning a preview/dev server, follow `references/safe-dev-server-resummon.md`: identify the exact port listener with `ss`, map the process tree with `ps`, terminate only verified dev-server PIDs, restart under Hermes/background tracking, and verify local plus remote/Tailscale routes before claiming the Gate is open.

## Public Preview Tunnels

When Ayman needs to view a local/static/dev preview from a PC without Tailscale, follow `references/public-preview-tunnels.md`: verify local health first, test direct public IP if appropriate, ask explicit approval before installing or opening a public tunnel, prefer a temporary `cloudflared tunnel --url http://127.0.0.1:<PORT>` Gate, parse the `trycloudflare.com` URL from a logfile if stdout is empty, verify HTTP 200 through the tunnel, and warn that anyone with the link can view it until closed.

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

## Hermes tool access debugging

When Hermes says it cannot use terminal, file, web, or other tools after `hermes tools enable ...`, do not repeat the same generic enable commands. First identify the active platform and session process.

Key lessons:
- `hermes tools enable NAME` defaults to `--platform cli`; Telegram/gateway sessions need `--platform telegram` too.
- Tool schemas are snapshotted at session start. After tool/config changes, use `/new` or `/reset`; for gateways, restart the gateway process when needed.
- Verify `hermes config path` and `HERMES_HOME` before assuming the edited config is the one being used.
- For one-shot CLI verification, include both `-q` and `-t`, e.g. `hermes chat -q "Use terminal to run pwd" -t terminal,file,web,skills,memory,session_search,delegation,code_execution`.
- Check both `hermes tools list --platform cli` and `hermes tools list --platform telegram` before declaring the Gate open.
- If the user already tried the obvious enable commands and is frustrated, switch immediately to an audit/proof command that prints config path, per-platform toolsets, and schema availability.

## Safety

- Never ask the user to paste secrets into chat.
- When commands involve credentials, show placeholders or environment variable names only.
- Confirm before destructive commands: deletion, overwrites, service stops, firewall changes, database operations, or production deploy changes.

## Platform-scope correction pitfall

When the user says they are using terminal/CLI Hermes only, stay on the CLI path. Do not pivot to Telegram, gateway, or platform-gateway fixes unless the user explicitly mentions them. For CLI tool-access issues, inspect the terminal path first: `hermes config path`, `hermes tools list --platform cli`, `platform_toolsets.cli`, `toolsets`, `agent.disabled_toolsets`, and whether `cli.py` is resolving `_get_platform_tools(config, "cli")`. If the user is frustrated, acknowledge the scope correction plainly before giving the next command.

## References

- `references/shell-prompt-confusion.md` — session-derived pattern for users accidentally typing `bash`/`sh` wrappers and interpreting blank command output.
- `references/safe-dev-server-resummon.md` — safe pattern for restarting a port-bound preview/dev server without killing unrelated processes.
