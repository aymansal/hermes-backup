# ImmoPilot dashboard aggregate finance safety

## When to use

Use this reference when building or reviewing ImmoPilot dashboard/report aggregate queries, especially Convex backend metrics for purchases, payments, sales, apartments, documents, or delivery notes.

## Session lesson

During Card 8.1, repeated GPT-5.5 reviews found that dashboard metrics can look tenant-safe while still leaking financial information through aggregate fields.

The dangerous pattern was not cross-tenant access. It was **all-time money totals** exposed in normal dashboard responses or inside fields that were not truly date-bounded.

## Rules

- Operational dashboard users may receive counts, status counts, and non-money operational summaries.
- Money totals must be behind financial permission, not merely organization access or operational dashboard access.
- Money totals must require a validated bounded date range (`dateFrom` + `dateTo`).
- No all-time unbounded money totals in dashboard responses.
- Do not leak denied financial data as fake zero/default values. Prefer an omitted optional `financialDetail` object or explicit unavailable metadata.
- `financialDetail.*.byStatus` is still financial if it includes amounts. Compute it from date-filtered records, not from the full tenant dataset.
- Apartment/property price totals are money totals. Do not return `apartments.totalPrice` or equivalent in the top-level operational response. Remove it or gate/date-bound it like other financial detail.
- Surface area totals/counts/status summaries are operational unless the product later declares them sensitive.
- Accountant/finance-only roles should be able to access finance-safe dashboard data without needing unrelated operational permission, but financial fields must remain separately gated.

## Review checklist

- Check top-level response fields for any amount-bearing totals: purchase totals, payment totals, sale totals, balances, apartment prices, revenue/cost-like metrics.
- Check nested `byStatus` objects; if they contain `amount`, `totalAmount`, `price`, `paid`, `remaining`, etc., they are financial.
- Verify every amount-bearing field is computed after date filtering.
- Verify the date range is validated before any financial detail is returned.
- Verify non-financial users get count/status summaries only.
- Verify generated Convex API bindings are updated when adding new modules.
- Run Convex-specific type gates in addition to app typecheck/build.

## Safe implementation shape

```ts
const hasOperationalAccess = await hasPermission(..., "reports.viewOperational");
const hasFinancialAccess = await hasPermission(..., "reports.viewFinancial");

if (!hasOperationalAccess && !hasFinancialAccess) {
  throw new ConvexError("Permission denied");
}

const validatedDateRange = validateDateRange(args.dateFrom, args.dateTo);
const includeFinancial = hasFinancialAccess && validatedDateRange !== undefined;

return {
  operationalCounts,
  statusCounts,
  financialDetail: includeFinancial
    ? computeFinancialDetail(dateFilteredRecords)
    : undefined,
};
```

## Common blockers

- A helper computes `financial.byStatus` from all organization records, then the parent query returns it under a gated object.
- A top-level operational object includes a money total such as `totalPrice`.
- A financial user can call the dashboard without `dateFrom/dateTo` and still get totals.
- Codegen dry-run passes, but `convex/_generated/api.d.ts` was not actually updated/tracked.
