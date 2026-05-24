---
name: ayman-senior-app-forge
description: Forge Ayman's serious business apps with architecture-first, reference-guided, ImmoPilot-first real-estate ERP SaaS, Convex tenant isolation, curated UI taste packs, Kanban, and independent review gates.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ayman, app-architecture, saas, pos, convex, tenant-isolation, ai-coding, kanban]
    created_by: agent
---

# Ayman Senior App Forge

## Purpose

Use this Skill Rune before planning, reviewing, or implementing serious apps for Ayman: POS, SaaS, ERP, CRM, inventory, dashboards, admin panels, or Moroccan business systems.

The goal is to stop AI-generated junior spaghetti by forcing:

- architecture before code
- small Kanban cards before implementation
- reference repos before improvisation
- frontend/backend boundary discipline
- componentized UI
- Convex-first SaaS where relevant
- ImmoPilot real-estate ERP first, with Sobhi Immobilier as first tenant/client
- shared-database tenant isolation by `organizationId` for ImmoPilot and `businessId` for future POS
- independent review before completion

## Required inputs

Before coding, collect or derive:

- app type: POS, ERP, CRM, dashboard, inventory, admin panel, SaaS
- product/platform name vs first client/tenant name
- active backend choice
- tenant model if SaaS
- correct tenant key (`organizationId` for ImmoPilot; `businessId` for later POS unless unified)
- auth provider and roles
- offline/printing needs for POS
- first target vertical/domain: real-estate developer ERP first; restaurant/electronics/clothing/general retail later
- reference repos/docs to inspect
- quality gates available in the repo

Do not guess Access Keys or deploy targets. Do not start implementation before the architecture and acceptance gates exist.

## Current SaaS doctrine — ImmoPilot first

Ayman's current SaaS priority is **ImmoPilot**, a Moroccan real-estate developer ERP platform.

Critical naming correction:

- Product/platform name: `ImmoPilot`.
- First client/tenant: `Sobhi Immobilier`.
- Tenant key for ImmoPilot: `organizationId`.
- Sobhi Immobilier is tenant data only; do not hardcode `sobhi` in routes, package names, Convex table names, generic components, shared helpers, or product shell branding.

Default ImmoPilot stack:

- SaaS-first
- Convex-first backend
- one main codebase
- one main Vercel deployment
- one shared Convex backend/database
- many organizations/companies as tenants
- tenant isolation by `organizationId`
- Convex functions enforcing membership and permissions
- real-estate hierarchy: Organization → Project → Tranche → Bloc → Building → Floor → Apartment
- auditable cost/profit flows

POS products are later modules/products, not the first SaaS schema driver. Snack-spana, ElectroMA, Samurai-style retail, and general POS can be added after ImmoPilot's foundation is stable.

## Future POS agency doctrine

For later POS products, the default remains Convex-first SaaS with tenant isolation. POS tenants may use `businessId` unless the product family is intentionally unified under `organizationId` later.

Dedicated deployments are premium exceptions, not the default.

## Core tenant isolation rules

For shared Convex database SaaS, every tenant-owned table must include the correct tenant key unless explicitly documented as global/system data:

- ImmoPilot real-estate ERP: `organizationId`
- Future POS products: usually `businessId`

Every Convex function touching tenant data must:

1. authenticate user or staff/session actor
2. determine target tenant key (`organizationId` or `businessId`)
3. verify membership/session belongs to that tenant
4. verify permission
5. validate all referenced IDs belong to the same tenant
6. query/mutate only records scoped by tenant key
7. write audit log for sensitive actions

Forbidden:

- unscoped `ctx.db.query(...).collect()` in production tenant paths
- updating records by ID without ownership check
- UI-only permission checks
- global localStorage caches for tenant data
- reports that accidentally aggregate all tenants
- error messages that reveal another tenant's data or existence

## Required Convex helper pattern

Plan these modules early:

```text
convex/lib/tenant.ts
convex/lib/permissions.ts
convex/lib/audit.ts
convex/lib/errors.ts
```

Required helpers for ImmoPilot:

```text
requireUser(ctx)
requireOrganizationAccess(ctx, organizationId)
requirePermission(ctx, access, permission)
assertBelongsToOrganization(record, organizationId)
assertAllBelongToOrganization(records, organizationId)
assertHierarchyChain(ctx, { organizationId, projectId, trancheId, blocId, buildingId, floorId, apartmentId })
writeAuditLog(ctx, organizationId, actor, action, target, metadata)
```

For future POS products, equivalent helpers may use `businessId`. Do not reuse POS helper names inside ImmoPilot unless the platform is intentionally unified later.

## Reference repo lessons

Ayman's legacy repos and this planning session showed these durable lessons:

- ImmoPilot: product/platform name for the real-estate ERP SaaS; Sobhi Immobilier is only the first tenant/client and must not be hardcoded into product identity.
- Tenant naming matters: ImmoPilot uses `organizationId`; later POS products may use `businessId` unless intentionally unified.
- ElectroMA: Next/Supabase POS had promising domain ideas but risked direct database access from UI and large components.
- Snack-spana: giant `page.tsx`-style app files are a hard ban; POS logic, receipt printing, settings, reports, and modals must be split by feature.
- Samurai-Men-s-Wear: closest architecture direction; Convex is the active backend. Supabase code there is backup/reference only and must be clearly labeled if present.

Use reference repos for patterns and anti-patterns, not blind copying.

## App standard document location

Ayman's current living standard is stored at:

```text
/home/ubuntu/.hermes/knowledge/ayman-app-standard
```

Important files include:

- `STACK_DECISION_RULES.md`
- `IMMOPILOT_SAAS_ARCHITECTURE.md`
- `IMMOPILOT_CONVEX_SCHEMA_BLUEPRINT.md`
- `IMMOPILOT_UI_DOCTRINE.md`
- `IMMOPILOT_UI_REFERENCE_PACK.md`
- `IMMOPILOT_DESIGN.md`
- `IMMOPILOT_MVP_SCOPE.md`
- `IMMOPILOT_PERMISSION_MODEL.md`
- `IMMOPILOT_SCREEN_BLUEPRINTS.md`
- `IMMOPILOT_KANBAN_EPICS.md`
- `TENANT_ISOLATION_AND_RELIABILITY.md`
- `SAAS_POS_ARCHITECTURE.md` for later POS products
- `FILE_SIZE_AND_BOUNDARY_RULES.md`
- `POS_OFFLINE_PRINTING_RULES.md` for later POS products
- `QUALITY_GATES.md`
- `REVIEW_CHECKLIST.md`
- `REFERENCE_REPO_LIBRARY.md`
- `LEGACY_REPO_REVIEW_2026-05-23.md`

When working on an actual repo, read the relevant files before creating implementation cards.

## Workflow

1. **Intake** — define product, business model, users, roles, data ownership, offline/printing needs, and first MVP slice.
2. **Reference scan** — inspect old repos or chosen open-source references for structure, not copy-paste.
3. **Architecture decision** — choose stack and write/update ADR-style notes.
4. **Schema blueprint** — define tables, indexes, permissions, audit, and tenant boundaries before UI.
5. **UI reference pack** — for ImmoPilot UI work, read the UI Doctrine and UI Reference Pack, then deliberately choose external design references (Vercel/Linear/Stripe/Notion/IBM/Wise or UI UX Pro Max searches) as ingredients, not commanders.
6. **Design tokens** — create or update ImmoPilot `IMMOPILOT_DESIGN.md` / repo `DESIGN.md` before serious UI implementation when visual consistency matters.
7. **MVP scope** — lock what is in v1 and what is explicitly out of scope before workers start.
8. **Permission model** — define roles, granular permission keys, sensitive actions, and audit requirements.
9. **Screen blueprints** — define each important screen's purpose, layout, required states, and mobile behavior.
10. **Kanban cards** — split into small tasks with acceptance criteria and review gates. For Ayman, it is acceptable to consciously skip full Kanban for low-risk local bootstrap/status work, but state that decision briefly; forgetting Kanban discipline is the problem, not making an explicit low-risk commander call.
11. **Worker implementation** — workers implement only one card/slice at a time.
12. **Independent review** — GPT-5.5/reviewer checks architecture, security, tenant isolation, UI, and tests.
13. **Iteration loop** — failed review returns to worker with exact failures.
14. **Commander verification** — Igris verifies evidence before reporting PASS.

## Quality gates

Every serious app task must pass:

- lint/typecheck/build where available
- file-size and boundary review
- no secrets or unsafe public env vars
- no frontend/backend mixing
- no giant one-shot generation
- independent review

For SaaS POS, also require:

- `businessId` on tenant-owned records
- membership checks
- permission checks
- ID ownership checks
- business-scoped indexes
- pagination for large lists
- bounded reports
- idempotent POS mutations where retries/offline are possible
- audit logs for sensitive actions
- offline cache partitioned by `businessId` when offline exists

For ImmoPilot real-estate ERP, also require:

- `organizationId` on organization-owned records
- `projectId` on project-scoped records where relevant
- hierarchy ownership checks across project → tranche → bloc → building → floor → apartment
- membership and permission checks for every Convex query/mutation
- organization/project-scoped indexes
- pagination for apartments, purchases, payments, documents, and audit logs
- bounded finance reports by organization/project/date range
- audit logs for financial, document, project, price/status, cost-allocation, and role changes
- no `sobhi` hardcoding outside tenant/client seed/display data

For ImmoPilot UI work, also require:

- read `IMMOPILOT_UI_DOCTRINE.md` and `IMMOPILOT_UI_REFERENCE_PACK.md` before major screen work
- use external UI skill packs as ingredients only; never let them override ImmoPilot domain rules
- prefer Vercel/Linear discipline, Stripe business polish, Notion document calm, and IBM/Wise financial clarity
- use UI UX Pro Max as a search/checklist oracle, not final brand authority
- use Taste Skill (`Leonxlnx/taste-skill`) as anti-slop/polish discipline with restrained ERP dials: design variance 4-5, motion 2-3, visual density 6-7 for dashboards/tables
- use Impeccable (`pbakaus/impeccable`) as the UI quality workflow: shape → build → audit → polish → harden
- use Vercel Labs Agent Skills for production frontend engineering gates: React/Next.js performance, composition patterns, web interface guidelines, and deployment optimization later if Vercel is used
- use Anthropic frontend-design as a creative spark/variant generator, but restrain it for core ERP screens where clarity beats spectacle
- reject generic dashboard filler, random gradients, decorative charts, excessive motion, brand cloning, and UI packs that override domain usability

## Output contract for planning

When asked to plan a new app/module, return:

```text
System report
Assumptions
Architecture decision
Data model / tenant model
Feature slices
Kanban cards
Quality gates
Risks / decisions needed
Next move
```

## References

- `references/pos-saas-convex-tenant-isolation.md` — session-specific doctrine extracted from Ayman's legacy POS/SaaS discussion.
- `references/immopilot-saas-doctrine.md` — current ImmoPilot doctrine: product naming, Sobhi-as-first-tenant correction, real-estate ERP hierarchy, `organizationId` tenant isolation, reliability rules, and POS-later boundary.
- `references/immopilot-ui-reference-pack.md` — how to use external UI skill packs (`awesome-design-md`, UI UX Pro Max, awesome-design-skills, Impeccable, future Taste link) as curated ingredients for ImmoPilot UI without overriding domain doctrine.
- `references/immopilot-dev-preview-and-convex-auth.md` — previewing the local ImmoPilot app over Tailscale, verifying the dev server route, and handling Convex device auth safely.
- `references/immopilot-monorepo-bootstrap.md` — known-good bootstrap pattern for the first ImmoPilot Turborepo/Next/Tailwind/Convex skeleton, including verification commands and common setup fixes.
- `references/immopilot-convex-cloud-setup.md` — session-proven Convex cloud project setup flow for ImmoPilot, including auth choices, generated files, AI guidance hierarchy, verification commands, and Tailscale dev-server checks.
