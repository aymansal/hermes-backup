# ImmoPilot Operator Security and Payroll Doctrine Notes

## Purpose

This reference captures session-derived doctrine for ImmoPilot as a serious SaaS platform, not just a client dashboard.

## Two-sided SaaS model

ImmoPilot must have two controlled surfaces:

```text
1. Platform/operator dashboard — Ayman-side SaaS control room.
2. Tenant ERP application — client-side application used by organizations like Sobhi Immobilier.
```

Do not confuse tenant admins with platform admins.

A tenant `owner` controls only their organization. A platform/operator actor controls SaaS-level operations and must have separate access checks.

## Platform/operator dashboard responsibilities

The operator dashboard should support:

- tenant/client organization list
- tenant onboarding
- subscription/payment status tracking
- client health/status tracking
- invite/credential setup for first tenant users
- safe credential/integration management when added
- support visibility
- audit visibility
- suspend/reactivate tenant controls

Suggested route family:

```text
/platform
/platform/organizations
/platform/organizations/[organizationId]
/platform/billing
/platform/support
/platform/audit
```

## Tenant ERP app responsibilities

The tenant app is the actual business application used by client organizations.

Suggested route family:

```text
/app
/app/projects
/app/apartments
/app/purchases
/app/payments
/app/clients
/app/documents
/app/settings
```

Every tenant route/query/mutation/report/export must be scoped by `organizationId`.

## Security baseline

Security must be part of architecture, not a final polish pass.

Required baseline:

- backend authorization, not UI-only checks
- strict `organizationId` tenant isolation
- platform permissions separate from tenant permissions
- ID ownership checks on all referenced tenant records
- rate limiting for abusive or expensive flows
- audit logs for sensitive platform, finance, payroll, document, credential, and permission actions
- safe credential handling and masked display
- input validation for all mutations/actions
- safe typed errors that do not reveal other tenants' resources
- file/document access checks and upload restrictions
- no secrets in repo, frontend bundle, logs, or audit records
- production security gates before launch

## Rate-limit targets

Rate limits should exist for:

- login/signup/invite flows
- resend invite / reset password flows
- platform tenant creation
- document uploads
- OCR/import jobs when added
- AI-assisted features when added
- exports and expensive reports
- public/demo/contact endpoints
- repeated suspicious mutation attempts

Scope rate limits by actor, organization, action type, and IP/device where available.

## Payroll / employee module requirement

ImmoPilot must include employee/staff and salary tracking, because real-estate developer operations include payroll and recurring staff costs.

Expected module concepts:

- employees / staff registry
- employment details and status
- salary/compensation terms
- monthly payroll periods
- salary payment records
- paid / unpaid / partial payment status per month
- payroll-related documents/attachments
- payroll audit trail
- restricted permissions for viewing/managing payroll

Payroll touches money and personal employee data. Treat it as Core Crystal data.

Required rules:

- all payroll data is tenant-owned and must include `organizationId`
- payroll views require explicit payroll/finance permissions
- salary creation/update/payment actions require audit logs
- monthly payment status must be backend-derived or backend-validated
- payroll exports require explicit permission and audit logs
- employee data must not leak across organizations

## Suggested helper modules

Plan security helpers before feature implementation:

```text
convex/lib/auth.ts
convex/lib/platform.ts
convex/lib/tenant.ts
convex/lib/permissions.ts
convex/lib/audit.ts
convex/lib/rateLimit.ts
convex/lib/validation.ts
convex/lib/errors.ts
convex/lib/security.ts
```

Core helper concepts:

```text
requireUser(ctx)
requirePlatformAccess(ctx)
requirePlatformPermission(ctx, permission)
requireOrganizationAccess(ctx, organizationId)
requirePermission(ctx, access, permission)
assertBelongsToOrganization(record, organizationId)
assertAllBelongToOrganization(records, organizationId)
checkRateLimit(ctx, scope)
writeAuditLog(ctx, payload)
safeError(code)
```

## Review questions

Every sensitive feature review should ask:

```text
Who is the actor: platform or tenant?
What organizationId is involved?
What permission is required?
Are all referenced IDs owned by the same organization?
Could this leak another tenant's data through result, count, error, search, export, or timing?
Is the action rate-limited if abusive/expensive?
Is the action audited if sensitive?
Are secrets/credentials masked and excluded from logs?
Does the UI hide controls AND does the backend enforce rules?
```
