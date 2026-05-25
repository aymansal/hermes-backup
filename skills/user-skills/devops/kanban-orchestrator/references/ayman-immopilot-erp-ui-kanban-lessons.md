# Ayman ImmoPilot ERP/UI Kanban Lessons

Use this reference when orchestrating ImmoPilot/Sobhi ERP frontend + Convex cards for Ayman.

## Proceeding after a temporary UI check

If Ayman pauses a raid to inspect a UI link and then says the next step was already agreed, do not re-ask for the same choice. Resume the agreed next card and report the spawned worker/reviewer IDs.

Pattern:
- User asks to check last UI route → provide route/status.
- User confirms/checks it → continue the previously recommended card if it was already accepted.
- Only ask again if the inspection revealed a blocker or the next card choice changed.

## UI card boundaries when Ayman plans hand polish

When Ayman says a UI screen needs hand polish later, worker cards must avoid broad redesign. Phrase the next card explicitly:

- “Do not redesign or heavily polish the existing screen.”
- “Only add the new route/feature and minimal links needed for navigation.”
- “Keep disabled placeholder actions honest; no fake writes.”

This prevents worker models from sanding a screen Ayman intends to refine manually.

## Review gate: no fake/no-op UI controls

GPT review should treat visible no-op buttons/handlers as blockers, even on placeholder screens. If a button says “Retour”, “Exporter”, “Réserver”, etc., it must either:

- perform real navigation/action,
- be disabled with a clear placeholder/tool-tip label, or
- be removed.

A visible enabled no-op is not production-serious/data-honest and should route to a same-worker fix card.

## Next.js dev preview after builds/codegen

For ImmoPilot Next dev previews, `pnpm build` or Convex/codegen work can poison `.next` while `next dev` is running. Symptoms observed:

- previously healthy routes return HTTP 500,
- generated chunks or CSS go missing,
- backend-only changes appear to break frontend routes.

Recovery pattern after approval for restart/cache clear:

1. stop tracked Next dev processes on port 3000,
2. `rm -rf apps/web/.next`,
3. restart with a tracked background process: `pnpm --filter @immopilot/web dev --hostname 0.0.0.0 --port 3000`,
4. verify every relevant route returns HTTP 200 before commit or before sending a Tailscale link.

Do not present a route as test-ready from a mere “Local: Ready” notification; verify with HTTP checks.

## Convex generated API cleanliness

For cards that add Convex modules/functions, generated bindings are part of the acceptance gate.

Checklist:
- `convex/_generated/api.d.ts` exposes the new module/function.
- `pnpm exec convex codegen --dry-run --typecheck enable` is clean.
- “Command would write file” means generated output still differs, even if the module appears present.
- Check ordering as well as content: Convex may expect imports and `fullApi` entries sorted alphabetically (e.g. `apartments` before `health`).

If full write-mode codegen needs an Access Key but dry-run reveals a simple generated-file diff, fix the deterministic diff and verify dry-run clean. Never invent or print tokens.

## Apartment module sequencing

For the ImmoPilot apartment module, keep the route progression clear so Ayman understands what each card adds:

- `4.1` backend query/functions: `apartments.list` / later `apartments.get` and generated Convex API bindings.
- `4.2` apartment inventory UI: `/app/projects/[projectId]/apartments`, searchable/filterable table/cards.
- `4.3` apartment detail UI: `/app/projects/[projectId]/apartments/[apartmentId]`, reached from a row/card link, with full read-only unit record sections.

If Ayman says the inventory UI is already done and asks what Kimi will do next, explain that Kimi is adding the detail screen, not redoing the inventory screen. Include explicit worker instruction: “Do not redesign the inventory UI; only add minimal links to the detail route.”

## Commit discipline

For Ayman’s ImmoPilot cards:
- Worker done is not enough.
- Reviewer PASS is not enough for preview cards.
- Commit only after PASS, clean gates, clean route verification, and known preview cache recovery if needed.
- If review BLOCKED, create a same-worker fix card with the exact blocker and a dependent GPT re-review card.
