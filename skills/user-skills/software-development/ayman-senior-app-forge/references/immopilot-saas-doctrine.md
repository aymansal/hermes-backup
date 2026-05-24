# ImmoPilot SaaS Doctrine

Session-derived doctrine for Ayman's current serious app workflow.

## Product naming

- Product/platform name: `ImmoPilot`.
- First tenant/client: `Sobhi Immobilier`.
- Sobhi is organization/client data only, not the app identity.
- Do not hardcode `sobhi` in routes, package names, Convex table names, generic components, shared helpers, or product shell branding.

## Current build priority

ImmoPilot is the first SaaS product. It is a Moroccan real-estate developer ERP / promoteur immobilier platform.

POS products are later modules/products after ImmoPilot's SaaS foundation is stable:

- Snack-spana restaurant POS
- ElectroMA electronics POS
- Samurai-style retail/clothing POS
- general POS platform

## Backend and tenancy

Default backend: Convex-first SaaS.

Tenant model for ImmoPilot:

- tenant key: `organizationId`
- tenant entity: `organizations`
- first tenant display name: `Sobhi Immobilier`

Every organization-owned record includes `organizationId`. Project-scoped records include `projectId` where relevant.

Hierarchy:

```text
Organization
  → Project
    → Tranche
      → Bloc
        → Building
          → Floor
            → Apartment
```

## Core schema blueprint

The implementation blueprint is stored in:

```text
/home/ubuntu/.hermes/knowledge/ayman-app-standard/IMMOPILOT_CONVEX_SCHEMA_BLUEPRINT.md
```

Core tables:

```text
organizations
memberships
projects
tranches
blocs
buildings
floors
apartments
suppliers
subcontractors
materials
purchases
purchaseItems
deliveryNotes
outgoingPayments
clients
sales
incomingPayments
costAllocations
documents
auditLogs
```

Required Convex helper modules:

```text
convex/lib/tenant.ts
convex/lib/permissions.ts
convex/lib/audit.ts
convex/lib/hierarchy.ts
convex/lib/money.ts
convex/lib/errors.ts
```

Required helper pattern for ImmoPilot:

```text
requireUser(ctx)
requireOrganizationAccess(ctx, organizationId)
requirePermission(ctx, access, permission)
assertBelongsToOrganization(record, organizationId)
assertAllBelongToOrganization(records, organizationId)
assertHierarchyChain(ctx, { organizationId, projectId, trancheId, blocId, buildingId, floorId, apartmentId })
writeAuditLog(ctx, organizationId, actor, action, target, metadata)
```

## UI doctrine

The UI doctrine is stored in:

```text
/home/ubuntu/.hermes/knowledge/ayman-app-standard/IMMOPILOT_UI_DOCTRINE.md
```

ImmoPilot should feel like:

```text
A professional real-estate finance and project control center.
```

Not:

```text
toy admin template
POS app
crypto dashboard
random gradient SaaS
generic AI-generated panel
```

UI priorities:

- serious, clean, premium but practical
- Moroccan business-friendly
- finance-aware
- desktop-powerful
- mobile-usable for chantier/site capture
- strong tables, forms, hierarchy navigation, documents, and reports

Hard UI bans:

- random gradients
- fake analytics chart walls
- generic dashboard filler
- tables without filters/pagination
- destructive financial actions without confirmation
- mobile screens that are squeezed desktop tables
- hardcoded Sobhi branding in product shell

## Workflow correction captured

When Ayman says the app is for a client, distinguish:

- product/platform name
- tenant/client name
- seed/demo organization data

Do not preserve obsolete redirect docs as compatibility clutter if Ayman asks to delete unused trash. Clean the doctrine set directly when safe.
