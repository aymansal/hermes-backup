# ImmoPilot dashboard UI real-metrics safety

Session lesson from Card 8.2 dashboard UI work.

## Trigger

Use this reference when building or reviewing the ImmoPilot `/app` dashboard or any real-data dashboard UI connected to Convex aggregate queries.

## Durable lesson

A dashboard can pass “real data only” review and still fail honesty/safety if the UI sends unsafe query arguments or silently uses placeholder tenant context.

For ImmoPilot dashboards:

- Use real `api.dashboard.getDashboardMetrics` data only.
- Do not create fake chart rows, fake metric values, demo samples, or Sobhi-specific dashboard data.
- Financial numbers must come only from backend `financialDetail`.
- If `financialDetail` is absent, show honest copy: permission required or date range required. Do not show fake zeroes.
- Default state must not request all-time financial totals.

## Date-range safety

Financial detail requires a bounded valid range. The UI must validate before calling Convex with `dateFrom`/`dateTo`:

- both start and end dates present, or neither is sent for count-only metrics
- dates parse to valid timestamps
- start date is before or equal to end date
- date window stays within the backend maximum window

If invalid:

- show clear French UI copy near the inputs
- omit `dateFrom`/`dateTo` from query args
- keep the finance panel in a safe “sélectionnez une période” / unavailable state
- avoid turning backend `BAD_REQUEST` into the normal user experience

## Tenant/auth honesty

The UI must not call dashboard queries with placeholder tenant IDs such as:

- `dev-org`
- `stub-org`

If real organization context is unavailable:

- render an honest unavailable/deferred dashboard state
- do not silently use a fake organization
- do not fake tenant data to make the dashboard look alive

## Review blockers to catch

- Placeholder org ID reaches `getDashboardMetrics`.
- Date inputs can trigger backend errors without a user-facing explanation.
- Money totals are derived in the frontend from operational counts/status summaries.
- Missing financial detail is displayed as zero money.
- Enabled buttons/filters/links look active but do nothing.
- Static dashboard constants become fake business data instead of labels/status metadata.

## Safe handoff wording

For a worker/reviewer handoff, require:

- changed files
- exact data source used
- exact date validation behavior
- exact org/auth unavailable behavior
- proof that financial UI only renders backend `financialDetail`
- source links checked
- gates run: typecheck, lint, build, diff check, fake/Sobhi/secret scan
