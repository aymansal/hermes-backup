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

Reference: `references/immopilot-source-records-project-lens-cost-allocation.md` captures Ayman's ImmoPilot doctrine correction: global navbar = company-wide source records, project tabs = project lens, global `Inventaire` vs project `Unités`, project `Coûts` as allocated costs, and one `Personnel` module with payroll/salaries inside.

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

- Reference repos/docs to inspect include the persistent ERPNext clone at `/home/ubuntu/.hermes/workspaces/reference-repos/erpnext` for ERP domain concepts. Use it as a benchmark/reference only, not as ImmoPilot's foundation unless Ayman explicitly chooses a full Frappe/Python/MariaDB stack pivot.

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
- two controlled surfaces: platform/operator dashboard for Ayman-side SaaS operations, and tenant ERP app for client organizations
- platform/operator dashboard manages manual tenant onboarding, client/payment status, invites/credentials, support, audit visibility, and tenant suspend/reactivate controls
- early ImmoPilot SaaS is manual B2B onboarding: no Stripe/pricing/credit-card checkout as a first requirement; Moroccan clients may pay Ayman by bank transfer/manual arrangement, then Ayman creates or activates their organization/users in `/platform`
- tenant ERP app serves client organizations such as Sobhi Immobilier and scopes all tenant data by `organizationId`
- many organizations/companies as tenants
- tenant isolation by `organizationId`
- Convex functions enforcing membership and permissions
- platform/operator permissions separate from tenant roles
- security baseline includes backend authz, rate limiting for abusive/expensive flows, audit logs, safe credential handling, file security, secret hygiene, validation, safe errors, and production security gates
- during ImmoPilot local development, keep WARP off unless Ayman explicitly approves turning it on for a specific need; Tailscale/dev preview checks should not silently re-enable it
- real-estate hierarchy: Organization → Project → Tranche → Bloc → Building → Floor → Apartment
- auditable cost/profit flows
- employee/staff registry and payroll/salary tracking are required ImmoPilot capabilities; for MVP they should live together under one global `Personnel` module rather than duplicate `Employees` and `Payroll` sidebar modules
- monthly salary payment status, payroll permissions, and payroll audit logs must be designed before implementation
- global company navigation owns source records; project tabs are project lenses over linked/allocated records, not duplicate source-record modules
- purchases, payments, and personnel/payroll costs should be organization-owned first and then optionally allocated across one or more projects, supporting Sobhi-style shared cement/staff costs

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
- `IMMOPILOT_SAAS_OPERATOR_AND_SECURITY.md`
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
10. **Kanban cards** — split into small tasks with acceptance criteria and review gates. For Ayman, use Kanban for non-trivial code/backend/UI raids, multi-step implementations, risky changes, or work needing independent review. It is acceptable to consciously skip full Kanban for low-risk local bootstrap/status work or small doctrine/documentation corrections, especially when Ayman says “no need for Kanban” / “just do it”; state that decision briefly, patch directly, verify, and commit only the intended docs. Forgetting Kanban discipline is the problem, not making an explicit low-risk commander call.
11. **Worker implementation** — workers implement only one card/slice at a time.
12. **Hallmark UI audit** — for important UI screens/components, automatically apply Hallmark-style anti-slop review before PASS. It audits/polishes only; it does not override ImmoPilot doctrine, `DESIGN.md`, tenant workflows, or ERP clarity.
13. **Independent review** — GPT-5.5/reviewer checks architecture, security, tenant isolation, UI, and tests.
14. **Iteration loop** — failed review returns to worker with exact failures.
15. **Commander verification** — Igris verifies evidence before reporting PASS.
16. **Active phase reporting** — for Ayman's ImmoPilot raids, report phase changes immediately: worker started, worker completed/blocked, reviewer started, review PASS/BLOCKED, fix iteration spawned, approval gate opened, commit checkpoint created. Do not wait for Ayman to ask after a card finishes; silence after a phase transition is a commander failure.
17. **Revival Stone checkpoint** — for ImmoPilot repo raids, commit only after a reviewed `PASS`, then push the reviewed commit to GitHub before starting the next repo-changing raid. Include review/gate evidence in the commit body, verify the pushed branch, and start the next slice from a clean working tree. Do not carry uncommitted reviewed changes into the next slice. If GitHub remote is missing, stop and create/configure the private remote with Ayman's approval before declaring the checkpoint sealed. See `references/immopilot-kanban-github-finalization.md`.

## Quality gates

Every serious app task must pass:

- lint/typecheck/build where available
- file-size and boundary review
- no secrets or unsafe public env vars
- no frontend/backend mixing
- no giant one-shot generation
- independent review
- commit checkpoint after review PASS before starting the next repo-changing raid
- For ImmoPilot security foundation work, apply the lessons in `references/immopilot-kanban-security-foundation-review.md`: require active memberships exactly, keep `safeError` non-leaking by not accepting arbitrary caller messages, verify Convex watcher duplicate-symbol alerts with a fresh one-shot compile, and route BLOCKED review fixes back through Kanban.

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
- hierarchy parent/status/list indexes lead with `organizationId` (for example `organizationId + projectId + status`, not bare `projectId + status`)
- pagination for apartments, purchases, payments, documents, and audit logs
- bounded finance reports by organization/project/date range
- audit logs for financial, document, project, price/status, cost-allocation, and role changes
- no `sobhi` hardcoding outside tenant/client seed/display data

For ImmoPilot UI work, also require:

- read `IMMOPILOT_UI_DOCTRINE.md` and `IMMOPILOT_UI_REFERENCE_PACK.md` before major screen work
- use external UI skill packs as ingredients only; never let them override ImmoPilot domain rules
- prefer Vercel/Linear discipline, Stripe business polish, Notion document calm, and IBM/Wise financial clarity
- use UI UX Pro Max as a search/checklist oracle, not final brand authority
- use Hallmark (`nutlope/hallmark`) automatically as an anti-AI-slop UI audit/redesign discipline after important screen/component implementation: preserve DESIGN.md tokens, reject invented metrics, fake chrome, gradient text, emoji feature icons, generic card-grid filler, random token values, weak contrast, missing focus states, horizontal mobile scroll, and two-line clickable labels
- for route/shell skeletons before real auth is wired, placeholder auth must fail closed outside development: never return fake platform admins, fake organizations, or tenant context in production builds; render an access-denied/auth-not-wired foundation state instead
- use Taste Skill (`Leonxlnx/taste-skill`) as anti-slop/polish discipline with restrained ERP dials: design variance 4-5, motion 2-3, visual density 6-7 for dashboards/tables
- use Impeccable (`pbakaus/impeccable`) as the UI quality workflow: shape → build → audit → polish → harden
- use Vercel Labs Agent Skills for production frontend engineering gates: React/Next.js performance, composition patterns, web interface guidelines, and deployment optimization later if Vercel is used
- use Anthropic frontend-design as a creative spark/variant generator, but restrain it for core ERP screens where clarity beats spectacle
- for ImmoPilot product-direction prototypes, do not default to a huge scrollable enterprise sidebar; prefer compact top nav/pill navigation, secondary tabs, or a thin non-scroll rail so all primary modules are reachable without sidebar scrolling
- when Ayman asks for a clickable visual MVP, consider producing or iterating toward two directions: a serious ERP baseline for module coverage and a modern compact SaaS direction for taste/product feel
- for current ImmoPilot implementation UI, use V1's serious ERP module coverage/density as the functional baseline, but use V2's compact/top navigation idea instead of V1's oversized scrollable sidebar; Ayman may personally redesign final UI later, so prioritize stitching real flows/buttons/states over speculative aesthetic polish
- ImmoPilot navigation doctrine: global navbar represents company-wide source records, while project tabs represent a project lens. Prefer global `Inventaire` for all organization units and project `Unités` for this project's units. Avoid duplicating global `Achats`/`Paiements` inside project tabs; use project `Coûts` for allocated costs from purchases, payments, personnel/payroll, and other expense records. Use one global `Personnel` module for employees + payroll rather than separate duplicated Employees/Payroll sidebar modules; see `references/immopilot-global-nav-project-lens.md`.
- modern/creative for Ayman means airy rounded SaaS polish, compact navigation, strong typography, thoughtful whitespace, and domain-useful cards — not decorative Dribbble UI or generic dashboard sludge
- use one global `Personnel` module for employees + payroll/salary status/payment/allocation instead of separate duplicated sidebar modules
- modern/creative for Ayman means airy rounded SaaS polish, compact navigation, strong typography, thoughtful whitespace, and domain-useful cards — not decorative Dribbble UI or generic dashboard sludge
- reject generic dashboard filler, random gradients, decorative charts, excessive motion, brand cloning, oversized scrollable sidebars, and UI packs that override domain usability
- see `references/immopilot-ui-stitching-decision.md` for the V1/V2 prototype decision and how to implement UI while preserving redesign flexibility

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
- `references/immopilot-manual-b2b-saas-onboarding.md` — manual B2B SaaS onboarding doctrine: no Stripe/pricing first, use `/platform` operator dashboard to create/activate organizations and users after bank transfer/manual payment.
- `references/immopilot-ui-reference-pack.md` — how to use external UI skill packs (`awesome-design-md`, UI UX Pro Max, awesome-design-skills, Impeccable, future Taste link) as curated ingredients for ImmoPilot UI without overriding domain doctrine.
- `references/immopilot-dev-preview-and-convex-auth.md` — previewing the local ImmoPilot app over Tailscale, verifying the dev server route, and handling Convex device auth safely.
- `references/immopilot-dev-shadows-sleep-wake.md` — stopping/resuming ImmoPilot local dev shadows safely; wake Convex + Next.js, verify local/Tailscale HTTP 200, keep WARP inactive unless explicitly needed.
- `references/immopilot-monorepo-bootstrap.md` — known-good bootstrap pattern for the first ImmoPilot Turborepo/Next/Tailwind/Convex skeleton, including verification commands and common setup fixes.
- `references/immopilot-convex-cloud-setup.md` — session-proven Convex cloud project setup flow for ImmoPilot, including auth choices, generated files, AI guidance hierarchy, verification commands, and Tailscale dev-server checks.
- `references/erpnext-reference-workflow.md` — how to use the local ERPNext clone as an ERP domain reference without pivoting away from Convex/Next.
- `references/immopilot-operator-security-payroll.md` — two-sided SaaS operator dashboard, security baseline, rate limiting, and employee/payroll doctrine notes.
- `references/immopilot-route-surface-and-review-patterns.md` — session-proven route surface workflow: `/platform` + `/app` skeleton sequence, Next.js route segment pitfall, fail-closed placeholder auth, review-required handoff routing, commit checkpoints, and local Next dev cache resummon.
- `references/immopilot-kanban-security-foundation-review.md` — session-proven Kanban/review lessons for ImmoPilot security foundation cards, including active-only memberships, non-leaking `safeError`, and Convex watcher duplicate-symbol verification.
- `references/immopilot-project-hierarchy-schema-and-crud.md` — session-proven hierarchy schema and project CRUD workflow: schema-only vs CRUD card split, `organizationId`-leading parent/status indexes, project CRUD permission/audit requirements, and review pitfalls.
- `references/immopilot-visual-prototype-feedback.md` — visual prototype feedback: V1 oversized scrollable sidebar problem, V2 compact/modern SaaS direction, and how to use airy rounded references without losing ERP seriousness.
- `references/immopilot-global-nav-project-lens.md` — product/navigation doctrine: global navbar as company-wide source records, project tabs as project lens, `Inventaire` vs `Unités`, `Coûts` for allocated project costs, and single `Personnel` module for employees/payroll.
- `references/immopilot-global-records-vs-project-lens.md` — navigation and finance doctrine correction: global navbar owns company-wide source records, project tabs are project lenses, purchases/personnel costs can be allocated across projects, and employees/payroll belong together under one Personnel module.
- `references/immopilot-convex-polymorphic-allocation-typing.md` — Convex typing lessons for `costAllocations.sourceType/sourceId`, `Pick<QueryCtx, "db">` helper ctx typing, avoiding invalid template-string ID casts, and verifying Convex-specific typecheck before PASS.
- `references/immopilot-client-feedback-demo-readiness.md` — readiness levels and positioning for internal preview vs first Sobhi/client feedback demo: workflow prototype, not working ERP; minimum path through Fournisseurs/Achats/Paiements/Projet Coûts.
- `references/immopilot-kanban-github-finalization.md` — repo-changing Kanban finish path for ImmoPilot: review-required handoff, GPT-5.5 PASS, final gates, commit with review summary, push to GitHub, and repo-integrity guardrails.
