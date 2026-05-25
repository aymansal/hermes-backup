# ImmoPilot route surface + review patterns

Session-derived notes for future ImmoPilot route/shell work.

## Route surface order

After the Convex security/tenant foundation passes review, the next frontend foundation slice should be route surfaces, not business modules:

- `/platform` — Ayman/operator SaaS control surface
- `/platform/organizations` — tenant/client organization control shell
- `/platform/audit` — operator audit visibility shell
- `/app` — tenant ERP home shell
- `/app/projects` — project workspace placeholder
- `/app/settings` — tenant settings placeholder

The route shell is a boundary exercise first. Do not build employees/payroll, apartments, payments, documents, or real dashboards in this slice.

## Next.js route-group pitfall

Do not create root route groups like `(platform)/page.tsx` and `(app)/page.tsx` if both resolve to `/`. Next.js rejects multiple root pages. Use real route segments instead:

```text
apps/web/src/app/platform/page.tsx
apps/web/src/app/platform/layout.tsx
apps/web/src/app/app/page.tsx
apps/web/src/app/app/layout.tsx
```

This preserves the two-shell architecture while producing actual `/platform` and `/app` URLs.

## Placeholder auth must fail closed

A frontend shell may use development placeholders before real auth is wired, but they must be explicitly dev-only.

Forbidden:

```ts
usePlatformAccess() -> { isPlatform: true }
useOrganization() -> DEV_ORG
```

when those values are returned in every environment.

Required behavior:

- development may show clearly labeled foundation/dev placeholders
- production must return `null`, `false`, or an explicit unconfigured/unauthenticated state
- platform routes must not pretend a visitor is an operator admin
- tenant routes must not pretend an organization context exists
- shells should render `AccessDeniedState` or a foundation/auth-not-wired placeholder instead of fake data

## Anti-slop shell constraints

- No fake metrics, charts, revenue, tenant counts, or invented operational data.
- No Sobhi hardcoding in generic routes, components, helpers, or branding.
- No business-module implementation in route skeleton cards.
- Use empty states that explain what will connect later.
- Keep `/platform` visually/contextually distinct from `/app` without overdesign.

## Review/commit checkpoint pattern

For ImmoPilot repo raids:

1. Worker implements.
2. GPT-5.5 reviews.
3. If `BLOCKED`, create a same-worker fix card with the exact review failures.
4. Re-review the fix.
5. Commit only after `PASS`.
6. Do not start the next raid with uncommitted reviewed changes.

If a worker blocks itself with a `review-required` handoff and the output is ready for review, the General can complete that implementation card with a summary to unlock the reviewer child. This is not a PASS; it is only routing the handoff to the review gate.

## Local dev preview corruption pattern

During Next.js dev after generated/build artifacts change, a stale `.next` cache can produce blank pages or 500s such as:

```text
Cannot find module './613.js'
Could not find ... segment-explorer-node.js#SegmentViewNode
__webpack_modules__[moduleId] is not a function
```

Safe local-dev recovery, with Ayman approval because it kills a process and deletes cache:

```bash
# stop the tracked Next dev process
rm -rf apps/web/.next
pnpm --filter @immopilot/web dev --hostname 0.0.0.0 --port 3000
curl -sS -o /dev/null -w 'local=%{http_code}\n' http://127.0.0.1:3000/
curl -sS -o /dev/null -w 'tailscale=%{http_code}\n' http://100.72.70.121:3000/
```

This is a local dev cache resummon, not a deploy and not WARP.
