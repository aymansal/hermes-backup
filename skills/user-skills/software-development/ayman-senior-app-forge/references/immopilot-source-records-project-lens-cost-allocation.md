# ImmoPilot doctrine: source records vs project lens + cost allocation

## When to use
Use this reference when planning or implementing ImmoPilot navigation, purchases, payments, suppliers/subcontractors, personnel/payroll, project finance tabs, or Convex schema/functions for costs.

## Core product doctrine
- Global navbar = company-wide source records. Users create and manage durable business records here.
- Project tabs = project lens. Users inspect/filter records that affect one project here.
- Do not duplicate global modules inside projects with the same meaning and label.

## Navigation naming
Global navbar should use company modules/source records such as:
- `Inventaire` = all units across the organization/all projects.
- `Achats` = global purchases/expenses.
- `Paiements` = global outgoing/incoming payment tracking as appropriate.
- `Personnel` = staff registry plus payroll/salaries inside one module.

Project tabs should use project-lens names such as:
- `Unités` = this project's apartments/shops/offices/units.
- `Coûts` = allocated costs affecting this project.
- `Ventes`, `Documents`, `Rapport` as project-scoped views.

Avoid repeating `Achats`/`Paiements`/`Personnel` as full project management modules. In project context, show allocated/linked records only.

## Cost allocation doctrine
Costs originate at organization level, then optionally allocate to projects.

A cost source can be:
- unallocated,
- allocated entirely to one project,
- split across multiple projects.

Use allocation lines for cross-project impact. Allocation line shape should be implementation-ready:
- `organizationId`
- `sourceType` (purchase item, outgoing payment, salary payment, other expense, etc.)
- `sourceId`
- `projectId`
- `amount`
- optional `percentage`
- optional `quantity`
- optional `notes`
- audit readiness fields

## Cement example
If Sobhi buys cement for multiple projects in one purchase, do not create separate purchases per project by default.

Model it as:
- one global purchase/expense source record,
- line items if needed,
- allocation lines splitting the amount/quantity across Project A, Project B, Project C.

Project `Coûts` shows only the allocated share for that project.

## Personnel/payroll doctrine
Do not split Employees and Payroll into two heavy sidebar modules.

Use one global `Personnel` module containing:
- staff/personnel records,
- salary terms,
- payroll periods,
- salary payments,
- optional project allocation readiness.

Salaries behave like company costs that may be allocated to one or more projects. Project pages should show personnel cost allocations under `Coûts`, not duplicate employee/payroll management.

## Backend planning implications
Before implementing finance backend, update/verify schema plans so purchases are not project-owned-only.

Recommended implementation order:
1. Supplier/subcontractor schema/functions.
2. Purchase/expense schema + allocation lines.
3. Outgoing payment schema/functions, allocation-ready.
4. Global `Achats`/`Paiements` UI shells.
5. Project `Coûts` lens.
6. `Personnel` module as a later epic unless MVP priority pulls it forward.

## Kanban/review workflow lesson
If a worker blocks as `review-required` after writing useful uncommitted docs/code, do not treat it as final PASS. Preserve the diff, mark/complete it explicitly as a review-required handoff, then start a GPT-5.5 review card. Only commit after reviewer PASS and General verification.

## Pitfalls
- Do not rename routes just to rename labels. Keep route stability unless a dedicated migration card exists.
- Do not gut doctrine docs; patch surgically.
- Do not implement schema/code in a doctrine/spec card.
- Do not use `projectId` on purchases as the only ownership model; it must not block multi-project allocation.
- Do not hardcode Sobhi except as example text.
