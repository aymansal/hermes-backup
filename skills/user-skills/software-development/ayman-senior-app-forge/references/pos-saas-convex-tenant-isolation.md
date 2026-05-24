# POS SaaS Convex Tenant Isolation — Ayman Session Notes

## Durable user/project facts

- Ayman plans to open a POS agency.
- The old operating model was clone repo → new GitHub repo → Vercel deploy → create database → ship to client.
- Ayman wants to replace that with SaaS because clone-per-client deployment will not scale to many clients.
- Ayman wants Convex as the default POS backend because of its large free tier.
- Ayman corrected that in Samurai-Men-s-Wear, Convex is the active backend; Supabase backend code is backup/reference only.

## Reviewed legacy repos

- `aymansal/ElectroMA`
- `aymansal/Snack-spana`
- `aymansal/Samurai-Men-s-Wear`

Main lessons:

- ElectroMA: good POS/inventory domain direction, but frontend/backend boundaries and large components need stronger enforcement.
- Snack-spana: giant single-file app/page patterns are a hard anti-pattern for future work.
- Samurai-Men-s-Wear: closest direction for Ayman's future apps; Convex active backend, monorepo/shared package direction. Backup backend folders must be clearly labeled so agents do not misclassify them as active architecture.

## Doctrine files created in knowledge base

Path:

```text
/home/ubuntu/.hermes/knowledge/ayman-app-standard
```

Important files:

- `SAAS_POS_ARCHITECTURE.md` — Convex-first SaaS POS architecture.
- `TENANT_ISOLATION_AND_RELIABILITY.md` — shared database safety doctrine.
- `STACK_DECISION_RULES.md` — POS agency products default to Convex-first SaaS multi-tenant architecture.
- `QUALITY_GATES.md` — SaaS POS shared Convex database tasks require tenant isolation review.
- `REFERENCE_REPO_LIBRARY.md` — legacy repos as references and anti-pattern sources.

## Shared-database safety rule

For SaaS POS:

```text
One Convex project
Many businesses/tenants
Every tenant-owned record has businessId
Every tenant-owned query/mutation verifies business access
Every reviewer checks tenant isolation before PASS
```

No client can read, write, infer, export, or sync another client's data.

## Required Convex access sequence

Every tenant-touching Convex function must:

1. authenticate user or POS staff session
2. determine target `businessId`
3. verify membership/session belongs to `businessId`
4. verify permission
5. validate referenced IDs belong to the same `businessId`
6. query/mutate only rows scoped by `businessId`
7. write audit log for sensitive actions

## Required reliability patterns

- business-scoped indexes
- pagination for large lists
- bounded reports by `businessId` and date range
- idempotency for sale/payment mutations
- defensive UI states
- plan limits to protect free tier
- audit logs for staff, settings, refunds, inventory adjustments, support access, and exports

## Recommended next implementation-planning step

Before coding, create a Convex schema blueprint covering:

- businesses
- memberships
- staffProfiles
- products
- categories
- sales
- saleItems
- payments
- inventoryMovements
- settings
- auditLogs
- indexes
- permission helper modules
