# ImmoPilot global nav vs project lens doctrine

## Trigger

Use this reference whenever planning or implementing ImmoPilot navigation, project detail tabs, purchases/payments, inventory, personnel/payroll, or project profitability flows.

## Core product correction

Ayman identified that the app was drifting into duplicated navigation:

```text
Global nav: Projects / Apartments / Purchases / Payments / Documents / Reports
Project tabs: Overview / Hierarchy / Apartments / Purchases / Payments / Documents / Reports
```

This makes users ask whether they are viewing company-wide data or project-scoped data.

The doctrine is:

```text
Global navbar = company-wide source records.
Project tabs = project lens / filtered project context.
```

## Naming decisions

Preferred global navbar labels:

```text
Tableau de bord
Projets
Inventaire
Achats
Paiements
Personnel
Clients
Documents
Rapports
Paramètres
```

Preferred project tabs:

```text
Vue d’ensemble
Structure
Unités
Coûts
Ventes
Documents
Rapport
```

Important label semantics:

- Global `Inventaire` = all units across the organization/company, across all projects.
- Project `Unités` = units belonging to this project only.
- Global `Achats` = source purchase records/invoices company-wide.
- Project `Coûts` = allocated costs for this project, not a duplicate purchase/payment module.
- Global `Paiements` = company-wide payment records.
- Project `Rapport` = project-specific report/lens.

Routes may remain stable even if labels change. Do not rename routes/components just to match labels unless explicitly scoped.

## Allocation doctrine

Costs should be organization-owned first, then optionally allocated to projects.

Examples:

```text
cement purchase → one supplier invoice → allocated across Project A / Project B / Project C
salary payment → one employee payroll record → allocated across Project A / Project B if needed
```

Recommended data-shape concept:

```text
purchase { organizationId, supplierId, totalAmount, status, ... }
purchaseAllocation { organizationId, purchaseId, projectId, amount, percentage?, notes }

salaryPayment { organizationId, employeeId, payrollPeriodId, amount, status, ... }
salaryAllocation { organizationId, salaryPaymentId, projectId, amount, percentage?, notes }
```

Project profitability should read from allocation lines:

```text
project revenue
- allocated purchases
- allocated supplier/subcontractor payments
- allocated payroll/personnel costs
- allocated other expenses
= project profit/margin
```

## Personnel / payroll correction

Do not split `Employees` and `Payroll` into two duplicated heavy sidebar modules.

Use one global module:

```text
Personnel
```

Inside it, model sections such as:

```text
Employés
Paie mensuelle
Paiements salaires
Affectations projets
Documents
```

Employee registry, salary terms, monthly payroll status, salary payments, documents, and project allocations belong together as one personnel module. Inside a project, show only personnel/payroll costs allocated to that project under `Coûts` or reporting views.

## UI implementation rules

- Do not duplicate source-record modules inside project tabs.
- If the same underlying data appears globally and inside a project, use different wording to show scope.
- Global pages create/manage canonical records.
- Project tabs show filtered/allocated/project-scoped views.
- Keep placeholder/prototype labels honest until backend allocation is wired.
- For small label/doctrine corrections, avoid broad doc rewrites; append targeted doctrine sections instead.

## Review checklist

Before PASS on navigation/cost-module work, verify:

- Global nav and project tabs communicate different scopes.
- Project tabs do not duplicate `Achats`/`Paiements` when the intent is allocated costs.
- Global `Inventaire` and project `Unités` wording is consistent in visible copy.
- Personnel/payroll is not split into two duplicated sidebar modules.
- Cost records remain tenant-owned by `organizationId` and project allocation is explicit.
- Existing routes remain stable unless route refactor was explicitly scoped.
