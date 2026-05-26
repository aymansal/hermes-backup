# ImmoPilot Convex polymorphic allocation typing

## Trigger

Use this note when implementing or reviewing ImmoPilot Convex tables/functions where one field can reference different source tables, especially `costAllocations.sourceType + sourceId`.

## Lesson captured

During the purchase/cost allocation backend raid, review caught real Convex typecheck failures caused by treating polymorphic IDs too loosely or with invalid template-string casts.

Bad pattern:

```ts
args.sourceId as `purchaseItems:${string}`
```

This does not produce a valid Convex `Id<"purchaseItems">` for `ctx.db.get`, and can make TypeScript infer unusable unions that break field access such as `source.totalCost`.

Better pattern:

- Narrow by `sourceType` first.
- In the `purchaseItem` branch, cast/validate as `Id<"purchaseItems">` only after the branch is known.
- Fetch the record with a correctly typed Convex ID.
- Verify `organizationId` immediately after fetching.
- Access source-specific fields only inside the narrowed branch.

## Helper ctx typing pitfall

Do not invent hand-rolled Convex db helper types like:

```ts
{ db: { get: (id: unknown) => Promise<unknown> } }
```

Convex `db.get` is overloaded and this hand-rolled type is incompatible with generated Convex types.

Prefer repo-style generated ctx picks:

```ts
import type { QueryCtx } from "./_generated/server";

type DbOnlyCtx = Pick<QueryCtx, "db">;
```

Then use that helper ctx type for read-only validation helpers such as allocation target validation.

## Allocation target validation rule

For `costAllocations`, target ownership checks must remain even while fixing types:

- source record belongs to `organizationId`.
- target project belongs to `organizationId`.
- hierarchy/apartment target belongs to the same organization/project when implemented.
- do not remove validation just to satisfy TypeScript.

## Review checklist

Before PASS on polymorphic allocation code:

- `pnpm typecheck --force` passes.
- `pnpm lint --force` passes.
- `pnpm build --force` passes.
- Convex-specific typecheck/dev check has no TypeScript errors; auth-only 401 is acceptable only after TS is clean.
- `git diff --check` passes.
- No references to non-existent tables through `v.id("missingTable")`.
- No broad `any` added to bypass Convex typing.
- No UI/payment/personnel scope creep sneaks into allocation backend cards.
