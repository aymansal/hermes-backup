# ImmoPilot Kanban Security Foundation Review Notes

Session lesson from the first ImmoPilot security/tenant foundation raid.

## Trigger

Use this reference when creating or reviewing early ImmoPilot foundation cards that touch Convex auth, tenant isolation, platform/operator permissions, audit logs, rate limits, or safe errors.

## Kanban routing lessons

- Create dependency edges at task creation time with `--parent`, not after the cards are already ready/running. Late linking can briefly allow children to run before parent handoffs exist.
- If a user-specific skill is required by a worker profile, verify that the worker profile can resolve it before passing `--skill`. If profile-scoped skill resolution is uncertain, embed the essential doctrine directly in the task body and point to absolute doctrine file paths.
- For BLOCKED reviews, create a new fix card assigned back to the same implementer, then create a new re-review card depending on the fix card.

## Security review lessons

The first implementation looked healthy and passed typecheck/lint/build/Convex compile, but review still found security weaknesses. Do not treat green gates as security PASS.

### Active membership only

If schema supports membership statuses such as `invited`, `active`, and `disabled`, tenant authorization must fail closed and require active exactly:

```ts
if (!membership || membership.status !== "active") {
  throw new AppError("Access denied or resource not found.", "FORBIDDEN");
}
```

Do not merely reject `disabled`; that accidentally authorizes invited users.

### Production-safe errors must not accept arbitrary messages

A helper named `safeError` should not accept caller-provided production-facing messages. The safe path should map only from an allowed code to a fixed non-leaking message:

```ts
export function safeError(code: AppErrorCode): AppError {
  return new AppError(safeErrorMessage(code), code);
}
```

If custom/internal debug messages are needed later, use a separately named helper with clear non-production semantics.

### Convex watcher duplicate-symbol alerts

A long-running `convex dev` watcher can emit transient duplicate-symbol errors while files are being edited. Verify with a fresh one-shot compile before treating it as stable:

```bash
pnpm exec convex dev --once
pnpm exec tsc --noEmit --project convex/tsconfig.json
```

If one-shot compile passes and search shows only one declaration/import path, treat the live watcher alert as a transient rebuild artifact, while still checking the relevant diff.

## Review acceptance reminders

A GPT-5.5 review should inspect:

- changed files and diff, not just worker summary;
- tenant authorization fail-closed behavior;
- platform/operator permissions separated from tenant roles;
- safe error handling that cannot leak tenant or record details;
- rate-limit/audit helper semantics as real foundations, not security theater;
- absence of Sobhi hardcoding in generic code;
- no WARP, deploys, restarts, installs, secrets, or business modules in foundation cards.
