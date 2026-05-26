# ImmoPilot Manual B2B SaaS Onboarding

## Session signal

Ayman corrected the SaaS assumption: early ImmoPilot SaaS should **not** mean pricing page, Stripe, credit-card checkout, or self-serve billing.

Moroccan client reality:

- many clients do not pay online by card
- Ayman is not yet operating with full online-payment infrastructure
- clients may pay by bank transfer or manual arrangement
- Ayman then opens access manually

## Doctrine

Early ImmoPilot SaaS = **manual B2B operator onboarding**.

Use this model before planning billing/pricing work:

```text
Client pays Ayman outside the app
→ Ayman opens /platform operator dashboard
→ Ayman creates client organization
→ Ayman creates or invites owner/user accounts
→ Ayman assigns roles/permissions
→ Ayman marks tenant active
→ client authenticates into /app
```

## Required platform/operator dashboard capabilities

Prioritize:

- create organization/client tenant
- create/invite tenant owner and users
- assign tenant roles/permissions
- set organization status:
  - active
  - trial/manual-review
  - suspended
  - cancelled/archived
- record manual commercial status:
  - unpaid
  - paid
  - overdue
  - bank transfer pending/received
- optional access end date (`accessUntil`) for manual renewals
- suspend/reactivate access
- operator notes and audit logs

## Explicitly not first

Do not propose these as early requirements unless Ayman asks:

- Stripe
- credit-card checkout
- pricing page as a required launch gate
- self-serve subscription portal
- automated plan upgrades/downgrades

They can be future enhancements, not the first SaaS layer.

## Architecture implications

Still keep real SaaS tenant foundations:

- `organizationId` tenant isolation
- platform/operator identity separate from tenant roles
- membership and permission checks
- tenant status checks before app access
- audit logs for operator tenant/user actions
- safe invite/reset flows

## Suggested timing

Build manual operator onboarding before giving real clients production access, but not before the ERP core is useful enough to onboard.

Recommended order:

1. Finish key tenant ERP modules needed by first client.
2. Add `/platform` operator dashboard for manual organization/user provisioning.
3. Add tenant status/access checks.
4. Add audit and support visibility.
5. Add optional online billing/pricing only later if business model needs it.

## Repo doctrine patch pattern

When this doctrine is corrected or refined, update the human-readable repo doctrine immediately if the change is small and low-risk. Do not force Kanban for a simple docs-only correction when Ayman says to patch it directly.

For ImmoPilot, patch these doctrine files first:

- `docs/doctrine/IMMOPILOT_SAAS_ARCHITECTURE.md`
- `docs/doctrine/IMMOPILOT_CONVEX_SCHEMA_BLUEPRINT.md`
- `docs/doctrine/IMMOPILOT_MVP_SCOPE.md`
- `docs/doctrine/IMMOPILOT_UI_DOCTRINE.md`
- `docs/doctrine/IMMOPILOT_KANBAN_EPICS.md`

Verification pattern:

```bash
git diff --check
grep -R "manual B2B\|bank transfer\|manualPaymentStatus\|Stripe/card\|self-serve" -n docs/doctrine
```

Commit only the intended doctrine files, especially if worker/backend changes are also uncommitted in the tree.

Useful schema language:

```text
status: trial | active | suspended | archived
accessUntil
manualPaymentStatus: unpaid | paid | overdue | waived
manualPaymentReference
operatorNotes
planLabel
```
