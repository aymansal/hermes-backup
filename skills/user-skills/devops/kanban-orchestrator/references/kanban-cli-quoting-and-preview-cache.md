# Kanban CLI quoting and Next preview-cache recovery

Session-derived detail from ImmoPilot UI/backend raids.

## Kanban CLI body/comment quoting

When creating Kanban cards from shell, do **not** interpolate long Markdown bodies containing backticks through `$(cat file)` or unquoted command strings. Markdown inline code such as `` `convex/_generated/api.d.ts` `` can be interpreted by the shell before Hermes receives it, stripping important review criteria or injecting command output into the card body.

Safer patterns:

1. Prefer programmatic subprocess argument arrays where the body is passed as a single argv value, not through shell expansion.
2. If using shell, avoid backticks in inline code or escape them carefully.
3. After creating important review cards, immediately inspect `hermes kanban show <task_id>` to verify the body survived intact.
4. If a card body was polluted or stripped, add a corrective General comment with exact criteria before the worker/reviewer starts.

Example safer creation pattern in Python:

```python
subprocess.run([
    "hermes", "kanban", "--board", "immopilot", "create", "--json",
    "Review Card X",
    "--assignee", "default",
    "--workspace", "dir:/path/to/repo",
    "--parent", worker_id,
    "--body", review_body,
], check=True)
```

CLI reminder: `hermes kanban create` uses the title as a positional argument. It does not accept `--title`.

## Next dev preview cache after build/codegen

For Next.js dev servers, running `pnpm build` or generated-code commands while a dev server is active can leave `.next` in a stale/collided state. Symptoms can include:

- routes returning HTTP 500 after quality gates passed;
- missing `.next/server/vendor-chunks/...` modules;
- HTML loading but CSS assets returning 404;
- public/Tailscale preview unhealthy even though the committed code and build are valid.

Recovery pattern before asking Ayman to inspect UI or before committing preview-sensitive work:

1. Stop the tracked dev server process.
2. Remove `apps/web/.next`.
3. Restart the dev server using Hermes tracked background process, not shell-level `nohup`/`&` wrappers.
4. Verify the relevant routes with `curl` return HTTP 200.
5. For visual preview, verify critical CSS/assets as needed before sharing the link.

Do not classify this as a code failure until cache has been cleared and routes rechecked. Do not restart/clear without Ayman approval when it touches his running preview gate.

## Review-required handoffs after a stuck/blocked worker

When a worker writes useful files but cannot complete cleanly (for example freezes at `preparing kanban_complete`, or blocks with `review-required` after one environment-dependent gate such as Convex 401), keep the status language precise:

- Marking the worker `done` is only a handoff unlock, not approval.
- The completion summary must say `review-required handoff, not PASS`.
- Preserve uncommitted files unless the user chooses revert/cancel.
- Immediately create or dispatch an independent GPT-5.5 review card with the exact changed files, route probes, and quality gates.
- If the issue was a dev preview cache problem, resummon the preview and re-probe routes before dispatching review so the reviewer sees meaningful output.
- Do not commit until the review card returns PASS and the General verifies routes/assets again.

Useful summary pattern:

```text
Review-required handoff, not PASS: worker wrote <scope>, but <freeze/block reason>. Preserved uncommitted changes for GPT-5.5 review. No commit performed.
```