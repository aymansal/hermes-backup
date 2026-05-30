---
name: real-estate-erp-reference-repos
description: Use when planning or building the Sobhi Immobilier / Moroccan promoteur immobilier ERP and you need public reference repos to inspect with Vercel Labs opensrc for dashboards, CRM, finance, documents, inventory, forms, tables, validation, and app architecture.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [real-estate-erp, references, opensrc, nextjs, shadcn, finance, documents]
    related_skills: [opensrc, github-repo-management, codebase-inspection, writing-plans, subagent-driven-development]
---

# Skill Rune: Real Estate ERP Reference Repos

## Overview

This Skill Rune gives Hermes agents a curated set of public reference repos for building **ImmoPilot**, Ayman's Moroccan promoteur immobilier / real-estate developer ERP SaaS.

Naming rule:

- Product/platform: `ImmoPilot`.
- First tenant/client: `Sobhi Immobilier`.
- Tenant key: `organizationId`.
- Do not hardcode Sobhi into app identity, routes, packages, generic components, Convex table names, or shared helpers.

The goal is not to copy code blindly. The goal is to inspect real production-grade and domain-adjacent code with `opensrc`, learn architecture and patterns, then write original project-specific code for the ERP.

The ERP blueprint needs:

- Project hierarchy: project → tranche → bloc → building → floor → apartment
- Suppliers and subcontractors
- Products/material catalog
- Purchases and bons de livraison
- Outgoing payments and supplier balances
- Client sales and incoming payments
- Cost allocation down to apartments
- Dashboards and reports
- Documents: invoices, contracts, plans, payment proofs, delivery notes
- Mobile-friendly fast data entry for chantier users

No single public repo perfectly matches this Moroccan real-estate developer workflow. Use a reference pack: finance app + CRM app + document app + admin dashboard + tables/forms/validation libraries + inventory/property examples.

## When to Use

Use this skill when:

- Planning the ERP architecture or MVP implementation.
- Assigning Kanban/coding-agent raids for ERP features.
- Looking for examples before building dashboards, forms, tables, documents, finance flows, or CRM screens.
- Debugging package/library behavior with `opensrc`.
- Asking agents to write code in the style of strong real-world TypeScript/Next.js apps.

Do not use this skill for:

- Copying licensed code directly without checking license.
- Replacing product requirements from the ERP blueprint.
- Treating low-star domain repos as authoritative architecture.

## Required Access Keys

Usually none for public repos.

Required tools:

```bash
command -v opensrc
command -v gh || true
command -v rg
command -v git
```

Network access is required for first-time fetches.

## Prime Directive

Study patterns, do not loot blindly.

For ImmoPilot, use a **doctrine-first workflow before reference-repo inspiration or feature coding**:

1. Read the local product doctrine first (`docs/doctrine/IMMOPILOT_MVP_SCOPE.md`, `IMMOPILOT_CONVEX_SCHEMA_BLUEPRINT.md`, screen/epic/UI/quality gate docs as relevant).
2. If the user expresses concern that the product feels incomplete, fragile, or like "AI-sludge", stop feature work and run a read-only product gap audit against doctrine before creating more build cards.
3. Convert audit findings into small reviewable cards. Do not jump from audit directly into a giant module.
4. Use reference repos only after doctrine establishes the product truth and the card scope.
5. Preserve Moroccan promoteur ERP semantics: documents/uploads, bons de livraison, purchases, supplier payments, cost allocation, and dashboard truth are core ERP modules, not polish.

Correct use:

- Inspect local doctrine before coding or referencing external repos.
- Inspect folder structure.
- Learn naming conventions.
- Learn component composition.
- Learn data model patterns.
- Learn validation/form/table patterns.
- Write original ERP code fitted to our requirements.
- Cite reference paths in worker summaries.

Incorrect use:

- Continue feature coding when the user is questioning product completeness.
- Copy large files directly.
- Pull in irrelevant complexity.
- Import another repo's business model without adapting it.
- Trust a repo only because it has stars.

## Recommended Reference Pack

### Core MVP Reference Pack

Fetch these first for ImmoPilot ERP MVP:

```bash
opensrc path Kiranism/next-shadcn-dashboard-starter
opensrc path pdovhomilja/nextcrm-app
opensrc path midday-ai/midday
opensrc path documenso/documenso
opensrc path shadcn-ui/ui
opensrc path TanStack/table
opensrc path react-hook-form/react-hook-form
opensrc path colinhacks/zod
```

This covers:

- Admin dashboard shell
- CRM/projects/invoices/documents
- Finance overview and file workflows
- Document/PDF handling
- shadcn component composition
- Data tables
- Forms
- Runtime validation

### Extended Reference Pack

Use these when the feature requires deeper patterns:

```bash
opensrc path twentyhq/twenty
opensrc path pesanio/pesan-pms
opensrc path arnobt78/Warehouse-Stock-Inventory-Management-System--NextJS-FullStack
opensrc path pjborowiecki/QUANTUM-STASH-inventory-Management-SaaS-NextJs-TypeScript-NextAuth-v5-Postgres-Drizzle-Tailwind
opensrc path formbricks/formbricks
opensrc path vercel/ai
opensrc path supabase/supabase
opensrc path prisma/prisma
opensrc path dubinc/dub
```

## Repo Roles

### `midday-ai/midday`

Use for finance, invoicing, files, financial overview, and dashboard UX.

```bash
MIDDAY="$(opensrc path midday-ai/midday)"
printf 'midday: %s\n' "$MIDDAY"
```

Study for:

- Financial overview screens
- Invoicing flows
- File reconciliation and storage patterns
- Dashboard cards and charts
- Supabase/Tailwind app organization

ERP feature mapping:

- Project financial dashboard
- Supplier balance dashboard
- Payment tracking
- Cost/category dashboards
- Document attachments around finance records

### `twentyhq/twenty`

Use for CRM-style entity modeling, contacts, companies, records, timelines, and large app structure.

```bash
TWENTY="$(opensrc path twentyhq/twenty)"
printf 'twenty: %s\n' "$TWENTY"
```

Study for:

- Contact/company models
- Record detail pages
- Activity/history patterns
- Large TypeScript monorepo organization
- Permissions/roles style thinking

ERP feature mapping:

- Clients
- Suppliers
- Subcontractors
- Activity logs
- User roles later

### `documenso/documenso`

Use for document workflows, PDFs, signing-style status flows, and document audit trails.

```bash
DOCUMENSO="$(opensrc path documenso/documenso)"
printf 'documenso: %s\n' "$DOCUMENSO"
```

Study for:

- Document model
- PDF workflows
- Upload/download handling
- Document status lifecycle
- Contract-like screens

ERP feature mapping:

- Bons de livraison
- Factures
- Devis
- Contracts
- Plans
- Payment proofs
- Document audit logs

### `pdovhomilja/nextcrm-app`

Use as a smaller, closer-stack reference for Next.js CRM + projects + invoicing + documents.

```bash
NEXTCRM="$(opensrc path pdovhomilja/nextcrm-app)"
printf 'nextcrm: %s\n' "$NEXTCRM"
```

Study for:

- Next.js 16 app structure
- React 19 patterns
- PostgreSQL + Prisma 7 usage
- shadcn/ui CRUD screens
- CRM/project/invoice/document module boundaries

ERP feature mapping:

- Supplier/client CRUD
- Project module
- Invoice/payment screens
- Documents module

### `Kiranism/next-shadcn-dashboard-starter`

Use for the ERP shell, navigation, dashboard starter, and shadcn layout.

```bash
DASH="$(opensrc path Kiranism/next-shadcn-dashboard-starter)"
printf 'dashboard starter: %s\n' "$DASH"
```

Study for:

- App shell
- Sidebar/navigation
- Page layouts
- Dashboard UI organization
- shadcn component conventions

ERP feature mapping:

- Global layout
- Project detail tabs
- Dashboard pages
- Admin navigation

### `pesanio/pesan-pms`

Use cautiously for property-management domain ideas.

```bash
PESAN="$(opensrc path pesanio/pesan-pms)"
printf 'pesan-pms: %s\n' "$PESAN"
```

Study for:

- Property/unit terminology
- Domain screens
- Property management data shapes

ERP feature mapping:

- Apartment inventory
- Building/unit concepts

Warning: lower-star domain repo. Treat as domain inspiration, not architecture authority.

### Inventory References

Use for products/materials, suppliers, stock, purchases, invoices, and analytics.

```bash
INV1="$(opensrc path arnobt78/Warehouse-Stock-Inventory-Management-System--NextJS-FullStack)"
INV2="$(opensrc path pjborowiecki/QUANTUM-STASH-inventory-Management-SaaS-NextJs-TypeScript-NextAuth-v5-Postgres-Drizzle-Tailwind)"
printf 'warehouse: %s\nquantum: %s\n' "$INV1" "$INV2"
```

Study for:

- Product/material catalog
- Supplier workflows
- Inventory CRUD
- Invoice and order models
- Analytics dashboard patterns
- Role-based access ideas

ERP feature mapping:

- Products/material catalog
- Purchases
- Delivery notes
- Supplier balances
- Chantier material tracking

### `shadcn-ui/ui`

Use for professional component composition.

```bash
SHADCN="$(opensrc path shadcn-ui/ui)"
printf 'shadcn: %s\n' "$SHADCN"
```

Study for:

- Component organization
- Dialogs
- Forms
- Tables
- Date pickers
- Command menus
- Accessibility patterns

ERP feature mapping:

- Every UI screen
- Fast data entry modals
- Project detail tabs
- Cost entry forms

### `TanStack/table`

Use for all serious data-grid patterns.

```bash
TABLE="$(opensrc path TanStack/table)"
printf 'tanstack table: %s\n' "$TABLE"
```

Study for:

- Column definitions
- Sorting/filtering
- Pagination
- Row selection
- Faceted filters
- Column visibility

ERP feature mapping:

- Apartment inventory
- Supplier list
- Purchases table
- Payments report
- Cost/category report

### `react-hook-form/react-hook-form` + `colinhacks/zod`

Use for forms and validation.

```bash
RHF="$(opensrc path react-hook-form/react-hook-form)"
ZOD="$(opensrc path colinhacks/zod)"
printf 'rhf: %s\nzod: %s\n' "$RHF" "$ZOD"
```

Study for:

- Nested forms
- Field arrays
- Form state
- Validation schemas
- Type inference
- Error handling

ERP feature mapping:

- Project structure builder
- Cost entry
- Purchase entry
- Payment forms
- Apartment sales forms
- Client forms

### `formbricks/formbricks`

Use for form-heavy product architecture and survey/form-builder patterns.

```bash
FORMBRICKS="$(opensrc path formbricks/formbricks)"
printf 'formbricks: %s\n' "$FORMBRICKS"
```

Study for:

- Form flows
- Question/field-like dynamic data structures
- Product app architecture
- Analytics patterns

ERP feature mapping:

- Dynamic cost entry forms
- Future configurable chantier input screens

### `vercel/ai`

Use later for AI features, not MVP core.

```bash
AI="$(opensrc path vercel/ai)"
printf 'vercel ai: %s\n' "$AI"
```

Study for:

- Structured AI output
- AI assistant integration
- Document classification helpers

ERP feature mapping later:

- OCR/classification assistant
- AI anomaly detection
- AI report explanations

### `supabase/supabase` and `prisma/prisma`

Use depending on backend choice.

```bash
SUPABASE="$(opensrc path supabase/supabase)"
PRISMA="$(opensrc path prisma/prisma)"
printf 'supabase: %s\nprisma: %s\n' "$SUPABASE" "$PRISMA"
```

Study for:

- Auth/storage/database platform patterns
- ORM behavior
- Migrations
- Relation modeling

ERP feature mapping:

- Auth
- Document storage
- Postgres schema
- Query and relation behavior

## Recommended Feature-to-Repo Map

### Global app shell

Inspect:

```bash
opensrc path Kiranism/next-shadcn-dashboard-starter
opensrc path shadcn-ui/ui
```

Look for:

```bash
rg "sidebar|navigation|dashboard|layout" "$(opensrc path Kiranism/next-shadcn-dashboard-starter)"
```

### Project hierarchy builder

Inspect:

```bash
opensrc path shadcn-ui/ui
opensrc path react-hook-form/react-hook-form
opensrc path colinhacks/zod
```

Look for:

```bash
rg "fieldArray|useFieldArray|nested" "$(opensrc path react-hook-form/react-hook-form)"
rg "tree|accordion|collapsible|dialog" "$(opensrc path shadcn-ui/ui)"
```

### Costs, purchases, payments

Inspect:

```bash
opensrc path midday-ai/midday
opensrc path pdovhomilja/nextcrm-app
opensrc path arnobt78/Warehouse-Stock-Inventory-Management-System--NextJS-FullStack
```

Look for:

```bash
rg "invoice|payment|transaction|expense|supplier|customer" "$(opensrc path midday-ai/midday)"
rg "invoice|payment|client|project|document" "$(opensrc path pdovhomilja/nextcrm-app)"
```

### Supplier and client CRM

Inspect:

```bash
opensrc path twentyhq/twenty
opensrc path pdovhomilja/nextcrm-app
```

Look for:

```bash
rg "contact|company|customer|client|activity" "$(opensrc path twentyhq/twenty)"
```

### Documents and uploads

Inspect:

```bash
opensrc path documenso/documenso
opensrc path midday-ai/midday
```

Look for:

```bash
rg "upload|document|pdf|file|storage" "$(opensrc path documenso/documenso)"
rg "upload|document|file|storage" "$(opensrc path midday-ai/midday)"
```

### Tables and reports

Inspect:

```bash
opensrc path TanStack/table
opensrc path Kiranism/next-shadcn-dashboard-starter
```

Look for:

```bash
rg "ColumnDef|useReactTable|getCoreRowModel|getPaginationRowModel" "$(opensrc path TanStack/table)"
```

## Kanban Worker Prompt Template

Use this when assigning a coding worker:

```text
You are implementing <FEATURE> for ImmoPilot, Ayman's Moroccan real-estate developer ERP SaaS.

Product/platform: ImmoPilot.
First tenant/client: Sobhi Immobilier.
Tenant key: organizationId.
Do not hardcode Sobhi into product identity, routes, package names, table names, generic components, or shared helpers.

Doctrine-first step, before coding:
- Read the relevant local docs/doctrine files and cite the exact files/sections used.
- If the feature touches documents, BL, finance, purchases, payments, tenancy, audit, or dashboard truth, explicitly state the doctrine-backed scope and non-goals.
- If the product feels incomplete or scope is uncertain, stop and perform/read a product gap audit before implementation.

Before coding, inspect these reference repos with opensrc only after doctrine scope is clear:
- <repo 1>: learn <specific pattern>
- <repo 2>: learn <specific pattern>
- <repo 3>: learn <specific pattern>

Rules:
- Do not copy large code blocks directly.
- Study architecture, naming, validation, component structure, and data flow.
- Write original project-specific code matching our ERP blueprint.
- Cite the exact doctrine files and reference files/folders you inspected.
- Keep MVP scope tight.
- Add tests or verification steps where practical.
```

Example:

```text
Implement the Supplier Profile screen.
Inspect:
- twentyhq/twenty for company/contact detail page structure
- midday-ai/midday for financial summary cards
- TanStack/table for related payments/purchases tables
- shadcn-ui/ui for card/dialog/table component composition

Build original ERP code for supplier info, total purchases, total paid, remaining credit, delivery notes, payments, and documents.
```

## License Safety

Before copying any actual code directly, inspect license:

```bash
gh repo view OWNER/REPO --json licenseInfo --jq '.licenseInfo.spdxId'
```

Rules:

- Pattern study is allowed.
- Small API usage snippets are generally fine, but still cite reference.
- Do not copy full files or proprietary-looking business logic.
- If license is missing/unclear, treat repo as read-only inspiration.

## Common Pitfalls

1. **Looking for a perfect ERP clone.** Public repos rarely match the exact domain. Compose a reference pack instead.

2. **Trusting low-star domain repos too much.** A property-management repo may teach terminology but not architecture quality.

3. **Overfitting to reference architecture.** Our ERP has its own hierarchy and allocation engine. Do not import unrelated SaaS complexity.

4. **Skipping the blueprint.** Reference repos are support material; the local ImmoPilot doctrine under `docs/doctrine/` remains the product truth. If the user says the app feels incomplete, missing core modules, or at risk of AI-sludge, do not keep coding the next feature. Run a read-only doctrine gap audit, rank gaps by business importance, then create small backend-first cards.

5. **Treating documents or bons de livraison as polish.** For Moroccan promoteur ERP, documents/uploads and BL are evidence spine modules for contracts, CIN, invoices, payment proofs, plans, chantier delivery, purchases, and audit. Build metadata and ownership rules before upload UI.

6. **Copying code without license review.** Study first. Copy only with clear license compatibility and a reason.

7. **Ignoring version-specific dependencies.** Use `opensrc path --cwd "$PROJECT_DIR" <package>` once the ERP repo exists so agents inspect the exact installed package version.

## Reference Files

- `references/core-pack-fetch-2026-05-23.md` — session fetch record for the already-cached core MVP reference pack, including cache paths, size, verification commands, and lessons about shallow cache size.
- `references/immopilot-doctrine-first-gap-audit-2026-05-30.md` — doctrine-first read-only gap audit pattern for when ImmoPilot feels incomplete or at risk of AI-sludge; includes module map, output shape, and recommended card sequence.
- `references/immopilot-document-metadata-safety-2026-05-30.md` — backend safety checklist for document metadata cards: entity ownership validation on create/list/get/archive/delete, safe rejection of `other`/`deliveryNote`, permissions, audit, and sequencing before upload UI.

## Verification Checklist

- [ ] Relevant reference repos fetched with `opensrc path`.
- [ ] Worker cited exact files/folders inspected.
- [ ] Implementation follows ERP blueprint, not just reference repo structure.
- [ ] No large direct copied code unless license checked and approved.
- [ ] Forms use validation patterns appropriate for nested ERP data.
- [ ] Tables support filtering/search/pagination where needed.
- [ ] Documents link to correct business objects.
- [ ] Financial logic remains explicit and auditable.
