---
name: shadcn-ui-cli
description: Use when installing, verifying, initializing, or using the shadcn CLI to add shadcn/ui components to a Next.js/React project, especially for the Sobhi Immobilier ERP dashboard, forms, dialogs, tables, tabs, and admin UI.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [shadcn, ui, cli, nextjs, react, tailwind, components]
    related_skills: [terminal-command-guidance, opensrc, real-estate-erp-reference-repos]
---

# Skill Rune: shadcn UI CLI

## Overview

`shadcn` is the CLI for adding shadcn/ui components to React/Next.js apps. It does not behave like a normal component library that stays hidden inside `node_modules`; it writes component source files into the project so the app owns the UI code.

Use this Skill Rune when preparing or modifying the UI layer for the Sobhi Immobilier / Moroccan promoteur immobilier ERP: dashboards, forms, dialogs, tables, project detail tabs, supplier profile cards, cost entry modals, and apartment inventory screens.

Current Hermes VPS status discovered during setup:

- Installed binary: `/home/ubuntu/.local/bin/shadcn`
- Installed version: `4.8.0`
- Install command used: `npm install -g --prefix "$HOME/.local" shadcn@latest`
- Installed size: about `110M`
- `~/.local/bin` is on `PATH`

## When to Use

Use this skill when:

- Installing or verifying the `shadcn` CLI.
- Initializing shadcn/ui in a new Next.js/React project.
- Adding UI components to the ERP app.
- Inspecting shadcn docs/examples from the CLI.
- Planning a UI implementation raid that needs consistent components.

Do not use this skill to:

- Run `shadcn init` outside the actual project directory.
- Add many components blindly before the app stack and folder aliases are clear.
- Overwrite existing components without checking diffs.

## Required Access Keys

Usually none.

Required commands:

```bash
node --version
npm --version
command -v shadcn
```

Network access is required when `shadcn` fetches registry items or installs package dependencies.

## Phase 1 — Inspect the Hunter's Terminal

Read-only scan first:

```bash
command -v shadcn || true
shadcn --version || true
node --version
npm --version
case ":$PATH:" in *":$HOME/.local/bin:"*) echo 'HOME_LOCAL_BIN_IN_PATH=yes';; *) echo 'HOME_LOCAL_BIN_IN_PATH=no';; esac
```

Expected on Ayman's Hermes VPS:

```text
/home/ubuntu/.local/bin/shadcn
4.8.0
HOME_LOCAL_BIN_IN_PATH=yes
```

## Phase 2 — Install / Update the CLI

If missing, install safely in the user-local prefix. Avoid sudo unless explicitly required.

```bash
npm install -g --prefix "$HOME/.local" shadcn@latest
```

Verify:

```bash
command -v shadcn
shadcn --version
shadcn --help
```

If the binary exists but the shell cannot find it:

```bash
export PATH="$HOME/.local/bin:$PATH"
command -v shadcn
```

## Phase 3 — Initialize in a Project

Only run this inside the actual app repo.

```bash
cd /path/to/project
pwd
ls -la
shadcn init
```

Before initializing, verify this is a compatible project:

```bash
test -f package.json && echo 'package.json found'
test -f tailwind.config.ts -o -f tailwind.config.js -o -f tailwind.config.mjs && echo 'tailwind config found' || true
test -f tsconfig.json && echo 'tsconfig found'
```

`shadcn init` may modify or create files such as:

- `components.json`
- `app/globals.css` or equivalent global CSS
- `lib/utils.ts`
- `components/ui/*`
- dependency entries in `package.json`

This is a meaningful write operation. Confirm project path before running it.

## Phase 4 — Add Components

Recommended starter components for the Sobhi Immobilier ERP MVP:

```bash
shadcn add button card input label textarea select checkbox dialog dropdown-menu tabs badge separator table form popover calendar command sheet alert skeleton toast
```

For a smaller first cut:

```bash
shadcn add button card input label textarea select dialog tabs table form badge dropdown-menu
```

For project structure builder screens:

```bash
shadcn add accordion dialog form input label select button card separator
```

For cost/purchase/payment entry:

```bash
shadcn add form input label select textarea calendar popover button card dialog
```

For dashboards and lists:

```bash
shadcn add card table badge dropdown-menu tabs skeleton separator
```

After adding components, inspect changes:

```bash
git status --short
git diff -- components.json package.json app components lib 2>/dev/null || true
```

## Phase 5 — Inspect Docs and Registry Items

The installed CLI supports docs/search/view commands:

```bash
shadcn --help
shadcn search ui
shadcn docs button form table dialog
shadcn view button card table form dialog
```

Use this before guessing component APIs.

## Project-Specific ERP Component Plan

For the Moroccan real-estate developer ERP, map components like this:

- Global shell: `sheet`, `button`, `dropdown-menu`, `separator`, navigation components from app code.
- Project detail: `tabs`, `card`, `badge`, `table`.
- Structure builder: `accordion`, `dialog`, `form`, `input`, `select`.
- Cost entry: `form`, `input`, `select`, `textarea`, `calendar`, `popover`.
- Purchases and bons de livraison: `form`, `table`, `dialog`, `badge`, upload components from app/storage stack.
- Supplier profile: `card`, `table`, `tabs`, `badge`.
- Apartment inventory: `table`, `badge`, `dropdown-menu`, `input` for filters.
- Reports: `table`, `card`, `tabs`, export buttons.

## Reference Repos to Inspect with opensrc

Before building UI screens, inspect local reference dungeons:

```bash
DASH="$(opensrc path Kiranism/next-shadcn-dashboard-starter)"
SHADCN="$(opensrc path shadcn-ui/ui)"
NEXTCRM="$(opensrc path pdovhomilja/nextcrm-app)"
rg "sidebar|dashboard|layout" "$DASH"
rg "components/ui|button|dialog|form|table" "$SHADCN"
rg "invoice|project|document|client" "$NEXTCRM"
```

For tables:

```bash
TABLE="$(opensrc path TanStack/table)"
rg "ColumnDef|useReactTable|getCoreRowModel" "$TABLE"
```

For forms:

```bash
RHF="$(opensrc path react-hook-form/react-hook-form)"
ZOD="$(opensrc path colinhacks/zod)"
rg "useFieldArray|Controller|FormProvider" "$RHF"
rg "object\(|array\(|enum\(" "$ZOD"
```

## Common System Alerts

### `shadcn: command not found`

Most likely cause: CLI missing or `~/.local/bin` not on `PATH`.

Verify:

```bash
ls -la "$HOME/.local/bin/shadcn" 2>/dev/null || true
printf '%s\n' "$PATH"
```

Fix:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

If missing, install:

```bash
npm install -g --prefix "$HOME/.local" shadcn@latest
```

### `EACCES` during global install

Do not jump to sudo. Use user-local prefix:

```bash
npm install -g --prefix "$HOME/.local" shadcn@latest
```

### `shadcn init` runs in wrong directory

Stop. Check `pwd`, `package.json`, and git status. If files were modified in the wrong repo, do not delete blindly; inspect `git status --short` first and revert only after confirmation.

### Component aliases are wrong

Check `components.json` and `tsconfig.json` path aliases:

```bash
cat components.json
cat tsconfig.json
```

The app should have sane aliases such as `@/components`, `@/lib`, and `@/hooks` depending on project structure.

### Tailwind or global CSS issues

Verify Tailwind config and global CSS files exist and match the project router setup:

```bash
ls -la app pages src 2>/dev/null || true
ls -la tailwind.config.* postcss.config.* 2>/dev/null || true
find . -maxdepth 3 -name 'globals.css' -o -name 'global.css'
```

## Rollback / Safety

Uninstall CLI:

```bash
npm uninstall -g --prefix "$HOME/.local" shadcn
```

Rollback project changes after `shadcn init` or `shadcn add` only if the project is under git and the Shadow Monarch confirms:

```bash
git status --short
git diff
# after confirmation only:
git restore <files>
```

Do not remove `components/ui` or `components.json` blindly; they may contain project customizations.

## Verification Checklist

- [ ] `command -v shadcn` returns `/home/ubuntu/.local/bin/shadcn` or another expected path.
- [ ] `shadcn --version` works.
- [ ] `shadcn --help` lists `init`, `add`, `docs`, `view`, and `search`.
- [ ] `shadcn init` is only run inside the intended project directory.
- [ ] `components.json` exists after init.
- [ ] Added components appear under the expected UI component directory.
- [ ] `git status --short` and `git diff` are reviewed after writes.
- [ ] App still builds or at least TypeScript/lint checks are run after component additions.
