# ImmoPilot global records vs project lens

## Trigger

Use this when planning or implementing ImmoPilot navigation, purchases/payments, personnel/payroll, project detail tabs, project reporting, or any ERP module that can exist at company level and then affect one or more projects.

## Session-derived correction

Ayman identified that the current global app navigation and project-inside tabs can feel duplicated when they repeat labels like Apartments, Purchases, Payments, Documents, and Reports. The issue is not that both layers exist; the issue is that their responsibilities and labels are too similar.

Core doctrine:

```text
Global navbar = source records / company-wide command.
Project tabs = project lens / allocated or linked records for one project.
```

## Navigation model

Global/company navigation should manage organization-wide records:

```text
Dashboard
Projects
Inventory / Units
Purchases
Payments
Personnel
Clients
Documents
Reports
Settings
```

Project detail navigation should avoid looking like a duplicate of the global navbar. Prefer project-context labels:

```text
Overview
Structure
Units
Costs
Sales
Documents
Report
```

Suggested French labels:

```text
Vue d’ensemble
Structure
Unités
Coûts
Ventes
Documents
Rapport
```

## Why this matters

Sobhi’s real workflow includes purchases that are not naturally project-owned at creation time. Example: buying cement for multiple projects at once.

Correct model:

```text
Global purchase record
→ allocation lines to Project A / Project B / Project C
→ each project sees only its allocated cost through the project Costs tab
```

Wrong model:

```text
Project A purchase + Project B purchase + Project C purchase
```

That duplicates records and breaks financial truth.

## Purchase / payment doctrine

Purchases and payments are organization-owned first, then optionally allocated to projects.

Suggested shape:

```text
purchase {
  organizationId
  supplierId
  invoiceNumber
  totalAmount
  status
}

purchaseAllocation {
  organizationId
  purchaseId
  projectId
  amount
  percentage?
  notes
}
```

This supports:

- one purchase for one project
- one purchase split across many projects
- unallocated purchases waiting for assignment
- allocation corrections with audit logs

## Personnel/payroll doctrine

Do not split Employees and Payroll into two heavy sidebar modules for MVP. Ayman corrected that this creates unnecessary duplication.

Use one global module:

```text
Personnel
```

Inside Personnel:

```text
Employees
Monthly payroll
Salary payments
Project assignments / allocations
Documents
```

Employee/staff records, salary terms, monthly payroll rows, and salary payment status live together in this Personnel module. Payroll still has sensitive finance/privacy rules, but it is not a separate duplicate sidebar item.

Salary payments can be allocated to projects like other cost sources:

```text
salaryPayment {
  organizationId
  employeeId
  payrollPeriodId
  amount
  status
}

salaryAllocation {
  organizationId
  salaryPaymentId
  projectId
  amount
  percentage?
}
```

## Project cost lens

Project Costs should combine allocated cost sources:

```text
allocated purchases
+ supplier/subcontractor payments
+ personnel/payroll allocations
+ other expenses
```

Project profitability should be derived from allocated costs, not from duplicated project-local source records.

## UI implementation rules

- Keep the global navbar clearly company-wide.
- Keep project tabs clearly project-scoped.
- Avoid repeating exact global module labels inside project pages when a project-lens label is clearer.
- Prefer `Costs` / `Coûts` inside a project instead of duplicating `Purchases` + `Payments` tabs.
- Prefer global `Inventaire` for the company-wide units route and project `Unités` for the project-scoped units tab; keep routes stable unless a separate route-migration card explicitly approves churn.
- If the global navbar points to `/app/apartments`, that route must exist and return 200. A small UI-only `Inventaire` shell is acceptable before aggregation/backend work, but its copy must clearly say it is company-wide units across projects.
- Prefer `Units` / `Unités` over `Apartments` where the product may include shops/offices/commercial units.
- Do not duplicate employee/payroll management inside project pages; show allocated personnel cost only.
- If a project tab links to a full global module, make the context explicit with filters/breadcrumbs.

## Planning impact

Before implementing Epic 5, insert or perform a planning correction card such as:

```text
Card 5.0: Company-wide cost allocation and navigation model
```

It should update doctrine and acceptance criteria for:

- global vs project navigation
- `Inventaire` global route shell requirement when `/app/apartments` is exposed in nav
- purchases with multi-project allocations
- personnel/payroll as one module
- salary payment allocations
- project cost/report calculations
- permission and audit requirements for financial/personnel actions
