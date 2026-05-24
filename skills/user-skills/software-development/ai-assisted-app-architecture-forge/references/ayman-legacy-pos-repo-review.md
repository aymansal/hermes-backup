# Ayman Legacy POS Repo Review

This reference captures durable lessons from a read-only review of three Ayman GitHub repos used to shape the AI-Assisted App Architecture Forge.

Reviewed repos:

- `aymansal/ElectroMA`
- `aymansal/Snack-spana`
- `aymansal/Samurai-Men-s-Wear`

Inspection method:

- cloned into a dedicated local analysis workspace
- generated structure/stack/largest-file summaries
- delegated GPT-5.5 read-only reviews per repo
- no dependency installs
- no runtime/build execution
- no repo modifications

## Executive verdict

The stack was not the only problem. The bigger failure was lack of architectural enforcement.

Common failure pattern:

1. AI generated useful product features quickly.
2. Files grew too large.
3. UI, state, business logic, database access, printing, offline sync, and permissions blended together.
4. Some projects added better structure later, but old confused paths remained.
5. Without review gates, the codebase accepted architectural debt as normal progress.

## ElectroMA

Stack detected:

- Next.js App Router
- React 18
- TypeScript strict mode
- Supabase/Postgres
- Tailwind v4
- Radix/shadcn-style UI
- SWR
- jsPDF, SheetJS, barcode tooling

Good decisions:

- checkout/server/API/RPC direction was promising
- SQL stock/payment logic existed
- partial `lib/api`, `lib/hooks`, `lib/auth` separation
- strong POS/inventory domain thinking

Mistakes:

- client components directly access Supabase
- inconsistent API boundary
- oversized components: product management, product modal, orders, dashboard shell
- duplicated mobile/desktop logic
- weak test/lint/typecheck scripts
- inconsistent permission enforcement
- risky PIN display/retrieval patterns

Lesson:

Next.js + Supabase can work, but only if critical mutations go through server/API/RPC boundaries. UI must not become the database layer.

## Snack-spana

Stack detected:

- Next.js 16
- React 19
- TypeScript
- Supabase
- Tailwind
- IndexedDB
- PWA
- QZ Tray printing

Good decisions:

- strong product document
- restaurant POS workflow was understood
- offline and printing concerns were identified
- QZ printing separated somewhat

Main System Alert:

`src/app/page.tsx` became about 5,911 lines and absorbed almost everything:

- screens
- modals
- cart logic
- reports
- receipt HTML
- lock/profile logic
- localStorage settings
- realtime subscriptions
- printing orchestration

Other mistakes:

- `src/lib/supabase.ts` became about 1,155 lines
- frontend/backend boundary mixed
- offline sync hidden inside general Supabase file
- risky PIN/security patterns
- private-key/public-env pattern risk around QZ signing

Lesson:

Snack-spana is the warning boss. Hard-ban giant page files and force feature folders from day one.

## Samurai-Men-s-Wear

Stack detected:

- Turborepo/npm workspaces
- Next.js 16
- React 19
- TypeScript
- Tailwind
- `apps/web`
- `packages/ui`
- shared eslint/tsconfig packages
- Convex active backend
- Supabase backend folder also exists
- Dexie offline cache
- QZ Tray printing

Good decisions:

- monorepo direction
- shared UI package
- shared config packages
- feature folders
- controller hooks
- backend schema/functions
- Turbo scripts for build/lint/format/typecheck

Mistakes:

- split-brain backend: Convex active backend plus Supabase backend folder
- backend folder outside workspace gates
- Supabase backend incomplete/orphaned
- domain model drift between Convex and Supabase
- plaintext PIN storage in Convex path
- large backend/controller files remain
- weak/no test gate

Lesson:

Samurai is closest to the desired direction, but future apps must pick one backend direction and enforce it.

## Extracted hard bans

- No `page.tsx` / route file over 300-500 lines without explicit refactor.
- No feature component over 300 lines without review justification.
- No giant `supabase.ts`, `api.ts`, or `utils.ts` owning multiple domains.
- No direct database writes from UI components.
- No mixed Convex + Supabase active backend without an explicit architecture decision.
- No backend folder outside workspace/build gates if it is real code.
- No plaintext PIN/password storage.
- No `NEXT_PUBLIC_*PRIVATE_KEY` or public private keys.
- No mock files as production type sources.
- No one-shot full app generation.

## Extracted required patterns

- monorepo for serious business apps
- feature folders
- thin pages
- shared UI primitives
- domain/service layer
- typed API/client boundary
- separate offline subsystem when needed
- separate printing/hardware subsystem when needed
- review gates before acceptance
- lint/typecheck/build/test gates from day one

## Default stack implication

For Ayman business systems, start with:

- Turborepo or npm workspaces
- Next.js + TypeScript frontend
- Tailwind + shadcn/Radix-style UI
- `packages/ui`
- `packages/shared`
- `packages/config`
- one active backend direction

For Sobhi Immobilier / ERP-style systems, prefer Supabase/Postgres-first or custom API/Postgres-first because relational hierarchy, auditability, cost allocation, reporting, and profit per unit matter.
