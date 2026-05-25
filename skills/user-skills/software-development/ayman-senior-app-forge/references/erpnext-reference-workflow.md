# ERPNext Reference Workflow for ImmoPilot

## Purpose

ERPNext is a local reference boss for ERP domain modeling, not ImmoPilot's foundation.

Use it to study mature ERP concepts before designing ImmoPilot modules, then translate the useful concepts into the existing ImmoPilot architecture:

- Next.js frontend
- Convex backend
- shared SaaS database
- `organizationId` tenant isolation
- platform/operator dashboard separate from tenant ERP app
- backend permissions, audit logs, and rate limits

## Local reference path

```text
/home/ubuntu/.hermes/workspaces/reference-repos/erpnext
```

Treat this clone as read-only reference material. Do not edit it as part of ImmoPilot work.

## When to inspect ERPNext

Inspect ERPNext before designing or reviewing serious ImmoPilot modules such as:

- employees / staff registry
- salaries / payroll / monthly salary payment status
- accounting / chart of accounts / journal entries
- purchases / supplier invoices / outgoing payments
- clients / sales / incoming payments
- subscriptions / platform billing concepts
- projects / tasks / profitability
- suppliers / customers / CRM
- assets / documents / reports

## How to use it safely

For each module:

1. Inspect the relevant ERPNext module/doctypes/reports locally.
2. Extract entity names, workflows, statuses, edge cases, and reporting ideas.
3. Reject anything tied to Frappe/Python/MariaDB implementation details unless it reveals a domain concept.
4. Translate into ImmoPilot Convex tables, indexes, validators, and helpers.
5. Add `organizationId` to all tenant-owned data.
6. Add backend permission checks and ID ownership checks.
7. Add audit logs for sensitive finance, payroll, document, and platform actions.
8. Add rate limits for abusive/expensive flows.
9. Update the relevant ImmoPilot doctrine Markdown before coding.

## Direct-use warning

Do not switch ImmoPilot to ERPNext/Frappe unless Ayman explicitly chooses a full architecture pivot.

Using ERPNext directly would change the Dungeon Core from:

```text
Next.js + Convex + custom SaaS operator dashboard
```

to:

```text
Frappe + Python + MariaDB + ERPNext customization
```

That is a major stack decision, not a normal implementation detail.

## Default verdict

```text
ERPNext = reference / benchmark / domain teacher.
ImmoPilot = custom Convex-first SaaS product.
```
