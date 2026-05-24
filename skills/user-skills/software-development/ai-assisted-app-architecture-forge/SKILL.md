---
name: ai-assisted-app-architecture-forge
description: Build serious apps with AI agents using architecture-first, reference-guided, review-gated workflows that prevent giant files, mixed frontend/backend code, weak UI taste, and stack drift.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ai-coding, architecture, frontend, backend, pos, erp, code-quality, review-gates]
    related_skills: [shadow-mission-orchestration, writing-plans, requesting-code-review, test-driven-development]
---

# AI-Assisted App Architecture Forge

## Purpose

Use this Skill Rune when Ayman wants to plan, design, refactor, or build a serious app with AI agents — especially POS, ERP, CRM, inventory, dashboard, or admin-panel systems.

The goal is not to let AI generate a full app in one cursed strike. The goal is to make AI operate like a disciplined senior software team:

- architecture before code
- reference repos before improvisation
- small Kanban cards before large generation
- worker agents implement, reviewer agents judge
- UI taste is specified, not guessed
- frontend, backend, and business logic stay separated
- quality gates pass before work is accepted

## Trigger conditions

Load this skill when the mission involves:

- creating a new app architecture or starter template
- deciding stack for POS/ERP/business apps
- reviewing old AI-generated apps for lessons
- preventing giant `page.tsx`, `App.tsx`, `supabase.ts`, `api.ts`, or `utils.ts` files
- making AI agents code like senior developers
- building Ayman App Standard or a project-specific equivalent
- extracting lessons from reference repos
- designing AI coding/review workflows

## Required inputs

Before implementation, gather:

1. App type: POS, ERP, dashboard, CRM, inventory, admin panel, etc.
2. Product workflows and user roles.
3. Backend/data needs: relational, realtime, offline, audit, reporting.
4. UI direction and reference products.
5. Hardware needs: printer, barcode scanner, cash drawer, mobile/tablet.
6. Reference repos or existing legacy repo paths.
7. Risk level: prototype vs production/Core Crystal.

If repo access is needed, use read-only clone/inspection first. Do not modify legacy repos unless Ayman explicitly asks.

## Standard doctrine

### 1. Architecture before code

No serious coding starts until the architecture draft exists:

- stack choice
- folder structure
- feature boundaries
- backend boundary
- data model
- API/service contract
- UI design direction
- quality gates

### 2. Reference repos before improvisation

Reference repos are training grounds, not copy-paste sources.

Allowed:

- folder structure inspiration
- naming pattern inspiration
- component decomposition pattern
- API/service boundary pattern
- testing/gate pattern
- UI layout pattern

Forbidden:

- copying proprietary code
- importing code without license review
- copying secrets/config
- copying bad patterns because they exist in a repo

### 3. Small reviewed cards

Use Kanban or delegate_task when work is non-trivial. Each card should have:

- objective
- files allowed
- files forbidden
- acceptance criteria
- verification command
- reviewer type
- status

Do not let implementation workers approve their own work.

## Default Ayman Business App Stack v0.1

Use this as a starting recommendation, then adjust per project:

- Monorepo: Turborepo or npm workspaces
- Frontend: Next.js + TypeScript
- UI: Tailwind + shadcn/Radix-style primitives
- Shared packages:
  - `packages/ui`
  - `packages/shared` for schemas/types/constants
  - `packages/config` for eslint/tsconfig
- Backend: choose exactly one active backend direction per project
- Validation: shared schemas or server boundary validation
- Gates: lint, typecheck, build, tests, architecture review, security review

### Backend choice

Prefer **Supabase/Postgres-first** for:

- ERP
- accounting/cost allocation
- inventory with audit trails
- reporting-heavy apps
- real-estate project/unit profitability
- relational hierarchy
- long-term data ownership

Prefer **Convex-first** for:

- realtime operational dashboards
- fast internal tools
- collaborative/live apps
- apps where backend functions and reactive queries simplify delivery

Prefer **custom API/Postgres-first** for:

- high-control enterprise systems
- complex backend domain logic
- long-term portability
- strict audit/compliance needs

Hard rule: do not mix Convex and Supabase as active backends unless an explicit architecture decision record approves it.

## File size and boundary gates

These are review gates, not vibes:

- Route/page files: target under 300 lines, hard review at 500 lines.
- Feature components: target under 250 lines, hard review at 300 lines.
- Controller hooks: target under 250 lines, hard review at 350 lines.
- Backend route/controller files: target under 200 lines, hard review at 300 lines.
- Service/domain files: target under 300 lines, hard review at 400 lines.
- Generic `utils.ts`, `api.ts`, `supabase.ts`: must stay small and single-purpose; split by domain early.

Pages compose features. Pages must not own full product logic.

Allowed in a page:

- layout composition
- route-level metadata
- selecting a feature shell
- light loading/error wrapper

Forbidden in a page:

- large forms
- business calculations
- database access
- printing logic
- offline sync logic
- report calculations
- large modal implementations
- many unrelated `useState` blocks

## Required feature folder pattern

For serious features:

```text
features/<feature-name>/
  components/
  hooks/
  services/
  types.ts
  schemas.ts
  constants.ts
  index.ts
```

For POS/ERP, common features include:

- `pos`
- `products`
- `inventory`
- `orders`
- `customers`
- `reports`
- `settings`
- `auth-lock`
- `printing`
- `offline-sync`

## POS/offline/printing rules

Critical POS operations must be server-side or conflict-safe:

- sale creation
- payment recording
- refund/cancel order
- stock decrement/increment
- receipt number generation
- shift/day close
- cash drawer operations
- role/PIN verification

Offline must be its own subsystem:

```text
features/offline-sync/
  local-db.ts
  mutation-queue.ts
  sync-engine.ts
  conflict-policy.ts
  sync-status.ts
```

Printing and hardware code must be isolated:

```text
features/printing/
  printer-client.ts
  receipt-template.ts
  qz-signing.ts
  hardware-status.ts
```

Security bans:

- No private key in `NEXT_PUBLIC_*` variables.
- No production signing secret in browser code.
- No raw secret logging.
- PINs/passwords should be hashed, not retrievable.
- Admin UI should reset PINs, not display stored PINs.

## Legacy repo review workflow

When Ayman provides old repos to learn from:

1. Discover exact repo names with GitHub CLI or provided paths.
2. Clone into a dedicated read-only analysis workspace.
3. Generate a structural summary:
   - package scripts/dependencies
   - top-level tree
   - key source folders
   - largest files
   - framework/backend/data-access signals
4. Delegate independent reviews per repo using GPT-5.5 or equivalent reviewer.
5. Ask reviewers for:
   - stack detected
   - good decisions
   - mistakes/risks with evidence paths
   - lessons for the standard
   - stack recommendation implications
6. Igris verifies and synthesizes cross-repo conclusions.
7. Update the project standard with extracted hard bans and required patterns.

See `references/ayman-legacy-pos-repo-review.md` for the ElectroMA/Snack-spana/Samurai-Men-s-Wear findings that shaped this skill.

## Common System Alerts

- **Giant page file:** stop feature work and split into feature modules.
- **Direct DB from UI:** move critical operations behind server/API/RPC/backend functions.
- **Split-brain backend:** choose one active backend or write an explicit architecture decision.
- **Mock files used as production types:** rename/split into `types.ts`, `fixtures.ts`, and dev-only mocks.
- **No test gate:** add at least lint/typecheck/build and critical-domain tests before calling the app serious.
- **Pretty UI but bad structure:** run architecture review before more UI polish.
- **Reference repo copied blindly:** reject and extract patterns only.

## Output format for architecture recommendations

```text
System report:
<plain verdict>

Recommended stack:
- Frontend:
- Backend:
- Database:
- UI:
- Shared packages:
- Quality gates:

Architecture rules:
- <rules>

Risks / bans:
- <risks>

Next cards:
- <small Kanban cards>
```
