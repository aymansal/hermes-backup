# ImmoPilot Kanban GitHub finalization doctrine

## Trigger
Use this reference for ImmoPilot repo-changing Kanban cards after worker implementation and independent review.

## Session lesson
Ayman corrected the workflow after a repo-loss incident and recovery: local-only commits are not enough for ImmoPilot. Once GPT-5.5 review passes and the General verifies gates, the card must be committed and pushed to GitHub so the recovery source exists outside the VPS.

## Required finish path
1. Worker implements scoped card and leaves review-required handoff.
2. If worker blocks with `review-required`, inspect the log/result; if code is present and gates were run, explicitly complete the worker card as review-required and dispatch the review card.
3. GPT-5.5 review must return PASS/BLOCKED.
4. On PASS, the General runs final repo integrity checks from the intended repo root:
   - `pwd`
   - `git rev-parse --show-toplevel`
   - package/workspace manifest exists
   - `git status --short`
5. Run final gates from the verified root:
   - `git diff --check`
   - `pnpm typecheck`
   - `pnpm lint`
   - `pnpm build`
   - route smoke for changed and adjacent routes when the dev server is available
6. Commit with a useful subject and include review/gate evidence in the commit body.
7. Push to the configured GitHub remote.
8. Report commit hash, pushed branch, routes/gates verified, and next card.

## Safety guardrails
- Never use `scratch` workspace for the real ImmoPilot repo path; use `dir:/home/ubuntu/immopilot` or a deliberate worktree.
- If repo integrity fails, stop. Do not commit, do not kill the only live dev server, and report the exact failure.
- If a route smoke initially returns a transient 500 but the HTML/body shows a valid page and retry returns 200, capture the retry pattern, not a false blocker.
- Do not push secrets. Run a lightweight tracked-file secret scan before first remote creation or when env/config files were touched.
- Do not restart Hermes/gateway/system services without Ayman approval.

## GitHub baseline
For ImmoPilot, the current expected remote is the private repo:

```text
https://github.com/aymansal/immopilot
```

Local main should track `origin/main`.
