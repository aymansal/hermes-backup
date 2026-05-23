# Core Reference Pack Fetch — 2026-05-23

## Purpose

Session-specific fetch record for the Sobhi Immobilier / Moroccan promoteur immobilier ERP reference repos. Use this as a quick cache map before re-fetching or assigning coding agents.

## Fetch command pattern

The core pack was fetched with `opensrc path <owner/repo>` into the default cache:

```bash
~/.opensrc/
```

No package installs were run inside the reference repos. Only source caches were created.

## Cached repos

- `Kiranism/next-shadcn-dashboard-starter`
  - Cache path: `/home/ubuntu/.opensrc/repos/github.com/Kiranism/next-shadcn-dashboard-starter/main`
  - Use for: ERP dashboard shell, sidebar, page layout, shadcn conventions.

- `pdovhomilja/nextcrm-app`
  - Cache path: `/home/ubuntu/.opensrc/repos/github.com/pdovhomilja/nextcrm-app/main`
  - Use for: Next.js CRM, projects, invoices, documents, Prisma/shadcn CRUD patterns.

- `midday-ai/midday`
  - Cache path: `/home/ubuntu/.opensrc/repos/github.com/midday-ai/midday/main`
  - Use for: finance overview, invoices, files, financial dashboards.

- `documenso/documenso`
  - Cache path: `/home/ubuntu/.opensrc/repos/github.com/documenso/documenso/main`
  - Use for: PDFs, document lifecycle, upload/download, document audit patterns.

- `shadcn-ui/ui`
  - Cache path: `/home/ubuntu/.opensrc/repos/github.com/shadcn-ui/ui/main`
  - Use for: component composition, dialogs, forms, tables, accessibility.

- `TanStack/table`
  - Cache path: `/home/ubuntu/.opensrc/repos/github.com/TanStack/table/alpha`
  - Use for: column definitions, filtering, pagination, row selection, data grids.

- `react-hook-form/react-hook-form`
  - Cache path: `/home/ubuntu/.opensrc/repos/github.com/react-hook-form/react-hook-form/master`
  - Use for: nested forms, field arrays, form state, validation integration.

- `colinhacks/zod`
  - Cache path: `/home/ubuntu/.opensrc/repos/github.com/colinhacks/zod/main`
  - Use for: validation schemas, type inference, validation errors.

Also present from smoke test:

- `zod@4.4.3`
  - Cache path: `/home/ubuntu/.opensrc/repos/github.com/colinhacks/zod/4.4.3`

## Cache size and disk result

After fetch:

```text
~/.opensrc: 351M
/home filesystem: 145G total, 19G used, 126G available, 13% used
```

## Verification commands

```bash
opensrc list
du -sh "$HOME/.opensrc"
df -h "$HOME"
```

Feature-specific probes:

```bash
rg "invoice|payment|document" /home/ubuntu/.opensrc/repos/github.com/midday-ai/midday/main
rg "sidebar|dashboard|layout" /home/ubuntu/.opensrc/repos/github.com/Kiranism/next-shadcn-dashboard-starter/main
rg "ColumnDef|useReactTable" /home/ubuntu/.opensrc/repos/github.com/TanStack/table/alpha
```

## Lessons

- GitHub repo metadata size can overestimate the actual `opensrc` shallow cache size.
- Start with the core pack; defer heavier extended repos like `supabase/supabase` and `twentyhq/twenty` until a feature needs them.
- Cache paths may use the repo default branch name (`main`, `master`, `alpha`); future agents should call `opensrc path <repo>` rather than hardcoding branch names when possible.
