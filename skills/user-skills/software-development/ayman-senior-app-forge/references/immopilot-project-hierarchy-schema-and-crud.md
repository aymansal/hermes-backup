# ImmoPilot project hierarchy schema + project CRUD workflow

Session-derived notes for future ImmoPilot backend hierarchy work.

## Card sequence

After route shells and security foundation:

1. `Card 3.1` — project hierarchy schema only.
2. `Card 3.2` — project CRUD Convex functions only.
3. `Card 3.3` — hierarchy CRUD for tranches/blocs/buildings/floors/apartments.
4. UI project list/detail comes after backend tenant-safe functions pass review.

Keep these cards small. Do not combine schema, CRUD, and UI into one raid.

## Hierarchy schema pattern

Real-estate hierarchy:

```text
Organization → Project → Tranche → Bloc → Building → Floor → Apartment
```

Tables:

```text
projects
tranches
blocs
buildings
floors
apartments
```

Every hierarchy table is tenant-owned and must include:

```text
organizationId
```

Child tables should carry enough parent IDs to support ownership checks and project-scoped queries without relying on frontend-trusted IDs:

```text
projectId
trancheId
blocId
buildingId
floorId
```

Apartment MVP fields:

```text
code
surface
typology
price
status: available | reserved | sold | blocked
```

## Tenant-safe index rule

For ImmoPilot hierarchy tables, parent/status/list indexes must lead with `organizationId`.

Reviewer-blocking examples:

```text
BAD:  ["projectId", "sortOrder"]
GOOD: ["organizationId", "projectId", "sortOrder"]

BAD:  ["trancheId", "sortOrder"]
GOOD: ["organizationId", "trancheId", "sortOrder"]

BAD:  ["blocId", "sortOrder"]
GOOD: ["organizationId", "blocId", "sortOrder"]

BAD:  ["buildingId", "levelNumber"]
GOOD: ["organizationId", "buildingId", "levelNumber"]

BAD:  ["projectId", "status"]
GOOD: ["organizationId", "projectId", "status"]

BAD:  ["floorId"]
GOOD: ["organizationId", "floorId"]
```

Reason: future CRUD should be structurally guided into tenant scope instead of making cross-tenant queries easy by accident.

## Project CRUD card scope

Card 3.2 should create project CRUD functions only, usually in `convex/projects.ts` unless repo conventions say otherwise.

Required functions:

```text
list
get
create
update
archive
```

Required enforcement:

- all functions use Convex argument validators
- derive user identity server-side; never accept `userId` for authz
- require active organization membership
- require permissions:
  - `projects.view` for list/get
  - `projects.create` for create
  - `projects.update` for update
  - `projects.archive` for archive
- use organization-scoped indexes; no unscoped production `ctx.db.query(...).collect()`
- assert project ownership before returning, patching, or archiving
- duplicate project code checks must be organization-scoped via `by_organization_code`
- update/archive must write audit logs; creation should also audit if the existing helper supports it
- archive must set `status: "archived"`, not delete
- errors must be leak-safe for cross-tenant IDs

## Hierarchy CRUD card scope

Card 3.3 should create hierarchy CRUD/list functions only, usually in `convex/hierarchy.ts` unless repo conventions say otherwise.

Expected coverage:

```text
tranches: list/get/create/update/archive
blocs: list/get/create/update/archive
buildings: list/get/create/update/archive
floors: list/get/create/update only unless schema has safe archive/status support
apartments: list/get/create/update/status-or-price/archive-equivalent where schema supports it
```

Required enforcement:

- every exported query/mutation takes `organizationId`
- list/read functions require existing view permissions (`projects.view` for hierarchy nodes, `apartments.view` for apartments)
- mutations require existing exact permissions (`hierarchy.manage`, `apartments.update`, `apartments.updatePrice`, etc.)
- all ID reads assert `organizationId` ownership before returning data
- creates/updates validate the full parent chain instead of trusting frontend-supplied ancestor IDs
- avoid destructive deletes for referenced hierarchy nodes; if floors have no status/archive field, document the limitation instead of deleting
- apartment archive must use only schema-supported status values; do not invent an `archived` status if the schema only allows `available | reserved | sold | blocked`
- code uniqueness checks must normalize/trim consistently before lookup and storage

## Review pitfalls

GPT-5.5 review should explicitly check:

- parent/status indexes lead with `organizationId`
- CRUD functions do not rely on frontend-trusted parent IDs
- no Sobhi hardcoding or fake seed data
- no UI or broader hierarchy CRUD scope creep
- no weakened membership, permission, audit, or safe-error helpers
- audit logs do not store secrets
- project code duplicate checks normalize trimmed code before lookup and also guard code changes on update
- optional Convex args narrowed outside a callback may still be `undefined` inside `.withIndex()` callbacks; capture narrowed values in local constants before passing them to `.eq(...)`
- worker claims about missing Convex deployment tokens are not enough to waive `pnpm exec convex codegen --dry-run --typecheck enable`; the General/reviewer should rerun the gate from the controlling environment before PASS

## Verification gates

Use all available gates before PASS/commit:

```bash
pnpm typecheck
pnpm lint
pnpm build
pnpm exec convex codegen --dry-run --typecheck enable
```

Commit only after reviewer PASS and a final General verification run.
