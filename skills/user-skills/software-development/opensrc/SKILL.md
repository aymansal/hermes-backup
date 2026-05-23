---
name: opensrc
description: Use when installing, configuring, or using Vercel Labs opensrc to fetch real package source code for coding agents, debugging dependencies, inspecting npm/PyPI/crates/GitHub repositories, and caching source locally under ~/.opensrc or OPENSRC_HOME.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [opensrc, vercel, dependencies, source-code, cli, coding-agents]
    related_skills: [terminal-command-guidance, codebase-inspection]
---

# Skill Rune: opensrc

## Purpose

`opensrc` is a Vercel Labs CLI for giving coding agents access to the real source code of packages and repositories. It resolves packages through registry APIs, shallow-clones the correct source at the matching version/tag, and caches the result locally.

Use it when package docs are not enough and the System needs the actual implementation: types, internals, examples, edge cases, exports, generated files, or version-specific behavior.

Official identifiers discovered from npm:

- npm package: `opensrc`
- binary: `opensrc`
- description: `Fetch source code for packages to give coding agents deeper context`
- homepage: `https://opensrc.sh`
- repository: `https://github.com/vercel-labs/opensrc`
- cache default: `~/.opensrc/`
- cache override Rune: `OPENSRC_HOME`

## Required Access Keys

Usually none.

Network access is required for cache misses because `opensrc` resolves registry metadata and clones source repositories. Private package/repository support may require normal Git/npm/PyPI credentials already configured in the environment, but do not paste or print secrets.

## Assumptions

- OS: Linux/macOS/Windows with a shell.
- Required commands: `node`, `npm`, `git`.
- Recommended Node.js: 18+.
- Install method: `npm install -g opensrc`.
- Global install is a write operation; ask the Shadow Monarch before running it unless already authorized.

## Phase 1 — Inspect the Hunter's Terminal

Read-only scan first. No blades out yet.

```bash
command -v opensrc && opensrc --version || true
node --version
npm --version
git --version
printf 'OPENSRC_HOME=%s\n' "${OPENSRC_HOME:-}"
```

Interpretation:

- If `opensrc` prints a path/version, the Gate is already open.
- If `opensrc` is missing but `node`, `npm`, and `git` exist, install can proceed after approval.
- If Node.js is older than 18 or npm/git are missing, fix prerequisites first.
- If `OPENSRC_HOME` is empty, cache defaults to `~/.opensrc/`.

## Phase 2 — Install / Configure

Global npm install:

```bash
npm install -g opensrc
```

If system-global npm fails with `EACCES` on `/usr/lib/node_modules`, do **not** jump to `sudo` by default. Prefer a user-local prefix:

```bash
npm install -g --prefix "$HOME/.local" opensrc
export PATH="$HOME/.local/bin:$PATH"
```

Verify the user-local binary directly if the shell has not refreshed PATH:

```bash
"$HOME/.local/bin/opensrc" --version
```

Optional cache location:

```bash
export OPENSRC_HOME="$HOME/.opensrc"
```

For project-local or sandboxed use without global install:

```bash
npx opensrc path zod
```

Do not run cache removal commands unless explicitly requested; they delete local cached source.

## Phase 3 — Open the Gate

Verify the binary and basic help:

```bash
command -v opensrc
opensrc --version
opensrc --help
```

Fetch a small known package as a smoke test:

```bash
opensrc path zod
```

Expected result: an absolute path under `~/.opensrc/` or `$OPENSRC_HOME`.

## Phase 4 — Use opensrc During Coding Raids

### Get package source path

```bash
opensrc path zod
opensrc path react
opensrc path next
```

### Inspect source with normal tools

```bash
rg "parse" "$(opensrc path zod)"
rg "Router" "$(opensrc path vercel/next.js)"
python - <<'PY'
from pathlib import Path
p = Path('PUT_PATH_HERE')
print(p)
print('\n'.join(str(x) for x in list(p.rglob('*'))[:50]))
PY
```

### Multiple packages at once

```bash
rg "parse" $(opensrc path zod react next)
```

### Specific versions

```bash
opensrc path zod@3.22.0
opensrc path pypi:flask@3.0.0
```

### Lockfile-aware npm resolution

Use `--cwd` so opensrc can detect versions from the project lockfile:

```bash
opensrc path --cwd /path/to/project zod
```

or from inside the project:

```bash
opensrc path --cwd "$PWD" zod
```

## Supported Source Targets

- npm: default or `npm:` prefix
  - `opensrc path zod`
  - `opensrc path npm:zod`
- PyPI: `pypi:`, `pip:`, or `python:` prefix
  - `opensrc path pypi:requests`
- crates.io: `crates:`, `cargo:`, or `rust:` prefix
  - `opensrc path crates:serde`
- GitHub: `owner/repo` or full URL
  - `opensrc path vercel/next.js`
- GitLab: `gitlab:` or full URL
- Bitbucket: `bitbucket:` or full URL

## Cache Operations

List cached sources:

```bash
opensrc list
opensrc list --json
```

Remove one cached source:

```bash
opensrc remove zod
opensrc rm pypi:requests
```

Clean cache. These are destructive to local cache only, but still confirm first:

```bash
opensrc clean
opensrc clean --packages
opensrc clean --repos
opensrc clean --npm
opensrc clean --pypi
opensrc clean --crates
```

## Agent Workflow Pattern

When a dependency bug or API uncertainty appears:

1. Identify the package and version from the project lockfile.
2. Run `opensrc path --cwd "$PROJECT_DIR" <package>`.
3. Search the fetched source for the symbol, error, or type.
4. Read the implementation files directly.
5. Use findings to patch the local app or write tests.
6. Cite source paths in the final report, not vague memory.

Example:

```bash
cd /path/to/project
PKG_PATH="$(opensrc path --cwd "$PWD" zod)"
printf 'Source: %s\n' "$PKG_PATH"
rg "class ZodError|ZodError" "$PKG_PATH"
```

## Common System Alerts

### `opensrc: command not found`

Most likely cause: not installed or npm global bin is not on `PATH`.

Verify:

```bash
npm bin -g
npm prefix -g
printf '%s\n' "$PATH"
```

If global install failed with `EACCES`, install to the user-local prefix instead of using sudo first:

```bash
npm install -g --prefix "$HOME/.local" opensrc
export PATH="$HOME/.local/bin:$PATH"
command -v opensrc || "$HOME/.local/bin/opensrc" --version
```

If it was installed but not found, ensure `~/.local/bin` is on PATH.

Fix path or reinstall after approval:

```bash
npm install -g opensrc
```

### `npm: command not found`

Node/npm missing. Install Node.js 18+ using the operator-approved runtime manager or package manager.

### Clone or network failure

The Gate is sealed by network/DNS/GitHub/registry access.

Verify:

```bash
git --version
npm ping
GIT_TERMINAL_PROMPT=0 git ls-remote https://github.com/vercel-labs/opensrc.git HEAD
```

### Wrong package version

Use `--cwd` inside the project so lockfiles guide resolution:

```bash
opensrc path --cwd /path/to/project <package>
```

Or specify the version explicitly:

```bash
opensrc path <package>@<version>
```

### Cache confusion

Inspect cache:

```bash
opensrc list --json
printf 'OPENSRC_HOME=%s\n' "${OPENSRC_HOME:-$HOME/.opensrc}"
```

Only clean/remove cache after confirming with the Shadow Monarch.

## Rollback / Safety

Uninstall global package:

```bash
npm uninstall -g opensrc
```

Remove cache only with confirmation:

```bash
rm -rf "$HOME/.opensrc"
```

If `OPENSRC_HOME` was set in shell config, remove that line from the relevant profile file after confirming the target file.

## Verification Checklist

- [ ] `command -v opensrc` returns a binary path.
- [ ] `opensrc --version` works.
- [ ] `opensrc path zod` returns an absolute cached source path.
- [ ] `opensrc list` shows fetched sources after a smoke test.
- [ ] Cache location is known: `~/.opensrc/` or `$OPENSRC_HOME`.
- [ ] For project work, `--cwd "$PROJECT_DIR"` is used when lockfile version matters.
