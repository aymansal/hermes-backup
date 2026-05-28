---
name: skillui
description: Use when extracting a website, repository, or local project's design system into DESIGN.md, SKILL.md, and .skill packages with the SkillUI CLI.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [skillui, design-system, design-tokens, ui, claude-skills, static-analysis]
    created_by: agent
    source_repo: https://github.com/amaancoderx/npxskillui
---

# SkillUI Design System Extraction

## Purpose

Use this Skill Rune when Ayman wants to reverse-engineer a website, GitHub repo, or local app into a design-system package using `skillui` (`https://github.com/amaancoderx/npxskillui`).

SkillUI is a Node CLI that performs static design analysis and generates:

- `DESIGN.md`
- `SKILL.md`
- `.skill` ZIP package
- `CLAUDE.md`
- optional screenshots / visual references in ultra mode
- auto-install into `~/.claude/skills/<name>/` when generating a skill package

It does **not** require API keys. Ultra mode requires Playwright + Chromium.

## Required Access Keys / Config Values

None for default static analysis.

Required runtime:

- Node.js 18+
- npm
- network access for `--url`, `--repo`, remote fonts, and optional screenshots
- Playwright + Chromium only for `--mode ultra`

Current install on Ayman's Hermes VPS:

```bash
skillui --version
# 1.3.4
```

Installed from local clone:

```text
/home/ubuntu/workspace/npxskillui-inspect
```

User-prefix binary:

```text
/home/ubuntu/.local/bin/skillui
```

## Safe read-only checks

Run these first:

```bash
node -v
npm -v
command -v skillui
skillui --version
skillui --help
```

Inspect the source clone if needed:

```bash
cd /home/ubuntu/workspace/npxskillui-inspect
git status --short
git log -1 --oneline --decorate
npm audit --omit=dev
```

## Install / update from source

Use user-local prefix, not `/usr`, to avoid sudo/root writes:

```bash
cd /home/ubuntu/workspace/npxskillui-inspect
git pull --ff-only
npm ci
npm run build
npm install -g . --prefix "$HOME/.local"
skillui --version
```

If `skillui` is not found, verify `~/.local/bin` is on PATH:

```bash
printf '%s\n' "$PATH" | tr ':' '\n' | grep -Fx "$HOME/.local/bin"
```

## Common commands

### Extract a live website

```bash
skillui --url https://linear.app --out /home/ubuntu/design-systems --name linear
```

### Extract a local project

```bash
skillui --dir /absolute/path/to/project --out /home/ubuntu/design-systems --name project-name
```

### Extract a public GitHub repository

```bash
skillui --repo https://github.com/org/repo --out /home/ubuntu/design-systems --name repo-name
```

### Generate DESIGN.md only

```bash
skillui --url https://stripe.com --format design-md --out /home/ubuntu/design-systems --name stripe
```

### Generate `.skill` only

```bash
skillui --dir /absolute/path/to/project --format skill --out /home/ubuntu/design-systems --name project-name
```

### Ultra mode with screenshots and visual extraction

```bash
npm install -g playwright --prefix "$HOME/.local"
npx playwright install chromium
skillui --url https://linear.app --mode ultra --screens 7 --out /home/ubuntu/design-systems --name linear
```

## Output shape

For `--name linear --out /home/ubuntu/design-systems`, expect:

```text
/home/ubuntu/design-systems/linear-design/
├── linear-design.skill
├── SKILL.md
├── CLAUDE.md
├── DESIGN.md
├── references/
│   └── DESIGN.md
├── tokens/              # if tokens are emitted
├── screens/             # ultra mode
└── screenshots/         # URL screenshot when available
```

SkillUI also installs a generated Claude Code skill to:

```text
~/.claude/skills/<safe-name>-design/SKILL.md
```

Hermes does not automatically load Claude's `~/.claude/skills`; if Ayman wants the generated design skill available to Hermes, copy or adapt the generated `SKILL.md` into `~/.hermes/skills/<category>/<name>/SKILL.md` or create a Hermes Skill Rune with `skill_manage`.

## Verification checklist

After running SkillUI, verify:

```bash
OUT=/home/ubuntu/design-systems/<name>-design
test -f "$OUT/DESIGN.md"
test -f "$OUT/SKILL.md"
test -f "$OUT/<name>-design.skill"
test -f "$OUT/CLAUDE.md"
test -f "$HOME/.claude/skills/<name>-design/SKILL.md"
```

Inspect size and first lines:

```bash
wc -c "$OUT/SKILL.md" "$OUT/DESIGN.md"
sed -n '1,80p' "$OUT/SKILL.md"
```

## Common System Alerts

- `EACCES` during `npm install -g`: npm prefix is `/usr`; install with `--prefix "$HOME/.local"` instead.
- `Playwright not installed`: default mode can continue; ultra mode needs `playwright` and Chromium.
- `0 colors · 0 components`: the target may be CLI/backend code with no CSS/JSX design surface. Use a real UI repo, app directory, or website URL.
- `--repo` on private repos: SkillUI can only clone if local git credentials can access the repo. Do not paste tokens into commands.
- Generated `.skill` is Claude-oriented, not automatically a Hermes skill.

## Rollback / cleanup

Remove generated output:

```bash
rm -rf /home/ubuntu/design-systems/<name>-design
```

Remove generated Claude skill:

```bash
rm -rf "$HOME/.claude/skills/<name>-design"
```

Remove local SkillUI CLI install:

```bash
npm uninstall -g skillui --prefix "$HOME/.local"
```

Do not delete `/home/ubuntu/workspace/npxskillui-inspect` unless Ayman explicitly confirms.
