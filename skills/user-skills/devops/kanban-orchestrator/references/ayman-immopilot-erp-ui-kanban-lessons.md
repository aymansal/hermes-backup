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

## Review gate: no visible HTML entity leakage in UI copy

For ImmoPilot UI cards, especially French/Moroccan ERP copy, review should block visible entity leakage such as `&apos;`, `&amp;apos;`, `&eacute;`, `&mdash;`, or `&nbsp;` when it appears as user-facing text. This often happens when a worker puts HTML entities inside JS prop strings or template strings where React does not decode them.

Pre-review scan:

```bash
rg "&apos;|&amp;apos;|&eacute;|&mdash;|&nbsp;" apps/web/src
```

Fix pattern:
- in JS/TSX string props, use real apostrophes/typographic apostrophes (`d'échéancier` or `d’échéancier`) instead of `&apos;`;
- in JSX text nodes, prefer readable French text with real characters;
- do not broaden scope or redesign just to fix copy;
- rerun gates and route probes before committing.

If GPT blocks only for entity leakage, record the blocked review, create a same-worker copy-fix card, then a dependent GPT re-review card focused on rendered copy and route health.

## UI worker crash recovery with partial fake data

If a UI worker crashes/protocol-violates after writing files, inspect its log/diff before simply reclaiming. In ImmoPilot, a Kimi UI worker can leave partial components plus `*-placeholder` data containing invented clients, emails, phone numbers, sales, or payment totals. Treat invented business records as a blocker even if the files compile.

Recovery pattern:

1. Report the worker failure separately from product status: provider overload/protocol violation is not a PASS or a code review verdict.
2. Inspect the partial diff/log for fake records, enabled no-op controls, or misleading totals.
3. Create a recovery card that explicitly says to remove/replace fake placeholder data and build real Convex-backed UI or honest empty/loading/error states.
4. Create a dependent GPT-5.5 review card whose first checklist item is “no fake client/sale/payment records remain.”
5. Do not commit, preview-promote, or ask Ayman to test the UI until recovery review passes and route/CSS health is verified.

## UI copy entity leakage review gate

For ImmoPilot UI cards, especially French/Moroccan copy inside TSX prop strings or template strings, visible HTML entities are blockers. React does not decode `&apos;` inside JavaScript strings, so users may see `n&amp;apos;a` / `d&amp;apos;échéancier` instead of proper French.

Worker/reviewer checklist:
- Search newly touched UI files for `&apos;`, `&amp;apos;`, `&eacute;`, and similar entities.
- In JS/TSX strings, use real apostrophes (`'`) or typographic apostrophes (`’`) rather than HTML entities.
- Probe rendered HTML for entity leakage before PASS when a visible UI card touched French copy.
- Treat entity leakage as a product-quality blocker, not cosmetic noise.

## Next.js dev preview after builds/codegen

For ImmoPilot Next dev previews, `pnpm build` or Convex/codegen work can poison `.next` while `next dev` is running. Symptoms observed:

- previously healthy routes return HTTP 500,
- generated chunks or CSS go missing,
- backend-only changes appear to break frontend routes,
- route probes hang/time out while a stale `next-server` still owns port 3000.

Recovery pattern after approval for restart/cache clear:

1. stop tracked Next dev processes on port 3000,
2. if the port remains busy, inspect/kill the stale parent process tree as well as the `next-server` child (`bash -lic ...`, `npm exec`, `sh -c`, `node .../next`, `next-server`, and any `jest-worker/processChild.js` children),
3. verify port 3000 is clear with `ss -ltnp | grep ':3000' || echo 'port 3000 clear'`,
4. `rm -rf apps/web/.next`,
5. restart with a tracked background process: `pnpm --filter @immopilot/web dev --hostname 0.0.0.0 --port 3000`,
6. verify every relevant route returns HTTP 200 before commit or before sending a Tailscale link.

Do not present a route as test-ready from a mere “Local: Ready” notification; verify with HTTP checks. For UI cards, note that final `pnpm build`/Convex codegen can poison the freshly verified dev server again; if a post-build probe fails but gates pass, resummon once more after commit and report the final preview process ID/routes.

## Convex provider-safe frontend read wiring

When wiring ImmoPilot frontend pages to Convex reads, do not rely on `useQuery(..., "skip")` to make a component safe outside `ConvexProvider`. The hook can skip query execution but still requires provider context. For routes that must render honestly when Convex URL/org/provider is not ready, require a structural split:

1. outer route/shell checks provider/org/client readiness using non-Convex-safe context/env hooks only,
2. if missing, render an honest disconnected/unavailable state and mount no Convex hooks,
3. only mount the inner query component under a real `ConvexProvider`/`ConvexReactClient` and real org readiness,
4. keep hooks stable inside the inner component and use skip semantics only for query args that are validly provider-scoped.

Review should probe the disconnected path (for example `/app/sales/test-sale`) and block if it 500s because `useQuery` mounted without provider. This was the key 6.9 blocker: skip alone was insufficient; the fix was an outer/inner component split.

## Convex generated API cleanliness

For cards that add Convex modules/functions, generated bindings are part of the acceptance gate.

Checklist:
- `convex/_generated/api.d.ts` exposes the new module/function.
- `pnpm exec convex codegen --dry-run --typecheck enable` is clean.
- “Command would write file” means generated output still differs, even if the module appears present.
- Check ordering as well as content: Convex may expect imports and `fullApi` entries sorted alphabetically (e.g. `apartments` before `health`).

If full write-mode codegen needs an Access Key but dry-run reveals a simple generated-file diff, fix the deterministic diff and verify dry-run clean. Never invent or print tokens.

### Local Convex deployment gate for ImmoPilot reviews

If a reviewer blocks an otherwise clean Convex card only because `pnpm exec convex codegen --dry-run --typecheck enable` reports `No CONVEX_DEPLOYMENT set`, treat it as an environment gate, not a code blocker. Safe recovery pattern:

1. Verify no committed env file exists and do not print secrets.
2. Run `pnpm exec convex dev --once` from `/home/ubuntu/immopilot` to configure a local deployment. It writes `.env.local`; confirm `.env.local` is ignored by `.gitignore` and never stage it.
3. Re-run `pnpm exec convex codegen --dry-run --typecheck enable`.
4. If codegen passes and the reviewer already found no code blocker, add a Kanban comment with the new evidence and complete the review card as PASS from the General/operator context.
5. Include any generated binding updates such as `convex/_generated/api.d.ts` in the commit alongside the new Convex module/schema.

After `convex dev --once` or build/codegen runs, the Next dev preview can become cache-poisoned. Verify the preview route; if it returns missing `.next/server` chunks, follow the dev-preview cache recovery gate and ask before resummoning the preview.

## Apartment module sequencing

For the ImmoPilot apartment module, keep the route progression clear so Ayman understands what each card adds:

- `4.1` backend query/functions: `apartments.list` / later `apartments.get` and generated Convex API bindings.
- `4.2` apartment inventory UI: `/app/projects/[projectId]/apartments`, searchable/filterable table/cards.
- `4.3` apartment detail UI: `/app/projects/[projectId]/apartments/[apartmentId]`, reached from a row/card link, with full read-only unit record sections.

If Ayman says the inventory UI is already done and asks what Kimi will do next, explain that Kimi is adding the detail screen, not redoing the inventory screen. Include explicit worker instruction: “Do not redesign the inventory UI; only add minimal links to the detail route.”

## Backend-only card expectations

For ImmoPilot backend/schema cards (for example Epic 6 client/sale/payment foundations), do not imply Ayman has a new UI to visually test. State plainly: "nothing new is visible yet; this was backend only." If a live preview is checked after backend/codegen/build work, frame it as a smoke test that the existing UI survived the build/codegen/cache cycle, not as product review of the new card. This avoids wasting Ayman's attention looking for screens that were intentionally not built yet.

## Sobhi TVA, cost units, and source-cost doctrine

For the full mid-run doctrine-change workflow, see `references/immopilot-live-doctrine-change-playbook.md`. For the concrete financial TVA retrofit sequence and review blockers, see `references/immopilot-financial-tva-retrofit.md`.

Ayman clarified that Sobhi needs TVA as a real input across financial flows, not a hidden assumption. Future ImmoPilot cards touching purchases, costs, sales/contracts, incoming/outgoing payments, allocations, or reports must check the doctrine files before implementation:

- TVA defaults to 20%.
- Operators must be able to set TVA to 0% or a custom reviewed rate per relevant line/document.
- Cost lines must preserve real units such as `m3`, `m2`, `kg`, `ton`, `piece`, and `lot` instead of flattening everything into generic amounts.
- Land acquisition, notary fees, permits, bank fees, labor, subcontracting, and manual adjustments are source costs; do not fake them as material purchases.
- Project `Coûts` views are lenses over source records + `costAllocations`, with subtotal/TVA/total separation where source records carry tax.

If a running UI card includes price/tax fields before backend support exists, require honest disabled/empty/pending states or a clear handoff note; do not invent persistence.

For ImmoPilot sales/payments work, also load `references/immopilot-moroccan-payment-workflow.md`: use Moroccan promoteur concepts (`avance`, `tranche`, `solde`, `échéancier`), treat incoming payments as receipts against sale TTC, and enforce active payment sums without guessing legacy TVA/TTC.

Financial TVA retrofit sequence to recall after current Epic 6 work:

1. TVA audit map across all money-touching schema/functions/UI.
2. Sales TVA backend with snapshots, validation, audit, and legacy tax-review marking.
3. Purchases/purchaseItems TVA backend with line-level TVA, preserved units, HT/TVA/TTC totals, and legacy review marking.
4. Manual source costs for land acquisition, permits, notary, labor, bank fees, adjustments with 0/custom/20% TVA.
5. Cost allocation/reporting TVA awareness separating HT/TVA/TTC and unknown tax splits.
6. Review UI to confirm/fix TVA on older records.

Rule: new records follow TVA doctrine; old records are preserved, flagged, and reviewed — never guessed.

When TVA doctrine is introduced while building sales/payment flows, insert a focused backend hardening card before downstream payment UI depends on sale totals. For ImmoPilot this pattern was `6.5B — Sale TVA backend persistence` between sale form UI and incoming payment UI: persist HT/TVA/TTC snapshots, default new records to 20% only on creation, allow 0/custom rates, validate deposits against effective/recomputed TTC totals, and avoid silent legacy backfills. Payment UI should then treat payments as receipts against sale TTC, not as tax-generating records.

When a newly added UI shows TVA before backend persistence exists, do not continue to dependent payment/reporting UI without first considering a backend hardening card. For Epic 6 this means adding Sale TVA backend persistence before Incoming Payment UI, so payment screens can depend on correct contract totals.

Review must block financial hardening cards if deposit/amount fields accept `NaN`, `Infinity`, negative/impossible values, or if legacy missing TVA fields are silently backfilled to 20%. Old records need an explicit unknown/review-needed state instead of guessed tax snapshots.

## Mid-run doctrine corrections during active Kanban work

When Ayman introduces a product rule while a worker is already running (for example TVA/default-rate doctrine during a sale UI card), do not wait until the next card silently. Act immediately:

1. Add a comment to the active worker card with the new constraint so the worker can adjust if still running.
2. Add a matching comment to the review card so GPT-5.5 explicitly checks it.
3. Patch the relevant doctrine files in the repo if the rule is stable product truth.
4. Open a separate GPT-5.5 review card for the doctrine diff when it is meaningful product architecture.
5. If the current implementation missed the new rule, mark the review BLOCKED and create a same-worker fix + re-review loop.
6. Tell Ayman clearly what is doctrine-only vs implemented code; do not imply older backend/schema/UI automatically gained the new logic.

This pattern prevents drift between “what we learned” and “what workers are building.”

## Next.js dev preview cache poison after build/codegen

In ImmoPilot, repeated `pnpm build` / Convex codegen cycles can leave the Next dev preview on port 3000 serving stale `.next` chunks (`Cannot find module './555.js'`, `./613.js`, React Client Manifest errors). Treat this as a preview-cache issue only after code gates pass.

Safe finish pattern after review PASS:

1. Ask Ayman before touching the running preview process or deleting `.next`.
2. Kill the tracked dev preview process.
3. Run `rm -rf apps/web/.next`.
4. Restart `pnpm --filter @immopilot/web dev --hostname 0.0.0.0 --port 3000` as a tracked background process.
5. Verify the new route, `/app/clients`, `/app/projects`, and one CSS asset return HTTP 200 before commit/push.

Do not commit/push visible UI cards only because production build passed; finish with dev preview health when Ayman expects a Tailscale UI to test.

## Convex local deployment gate for codegen review

When a reviewer blocks only because `pnpm exec convex codegen --dry-run --typecheck enable` cannot run due to missing `CONVEX_DEPLOYMENT`, first inspect whether `.env.local` is ignored, then use the repo-local Convex setup path rather than treating it as a code blocker:

1. Run `pnpm exec convex dev --once` from the repo to configure a local deployment and generate ignored `.env.local` values.
2. Verify `.env.local` is ignored by `.gitignore` and do not print or commit its values.
3. Rerun `pnpm exec convex codegen --dry-run --typecheck enable`.
4. If codegen passes and the reviewer already found no code blocker, add PASS conversion evidence to the review card, complete it, then commit/push after normal clean-gate checks.

Do not store or echo Convex deployment values in card summaries; report only that an ignored local deployment was configured.

## Backend-only card reporting and visual testing

For ImmoPilot backend/schema/function cards, do not imply there is new UI for Ayman to visually inspect. If the preview is checked after backend/codegen work, frame it explicitly as a health check for existing routes, not a feature test. Say plainly: “nothing new is visible yet; this card was backend-only.” The next visible checkpoint starts when the relevant UI card begins.

## Moroccan échéancier UI card pattern

When moving from backend payment schedule support to visible UI, create a focused UI worker + GPT-5.5 review pair rather than expanding backend cards. For Epic 6-style work, the default UI surface is `/app/sales/[saleId]` because the échéancier is anchored to the sale TTC contract total.

Worker prompt requirements:
- Use Moroccan promoteur terms (`échéancier`, `avance`, `tranche`, `solde`, `encaissements`, `TTC`).
- Show honest unavailable/no-data/legacy-no-TTC states if real sale/schedule/org wiring is not available.
- Do not invent schedule rows, clients, sales, payments, or amounts to make the screen look full.
- Add only the new schedule surface and minimal navigation; do not redesign unrelated screens.
- Treat add-line / record-payment controls as disabled with clear copy unless real mutations are wired; no enabled no-op controls.

Review prompt requirements:
- Check no USA mortgage-first wording became the default.
- Check payments are described as receipts against sale TTC and not TVA-generating events.
- Check route/CSS health after PASS before committing visible UI cards, because Next dev preview may be cache-poisoned by build/codegen.

## Convex local deployment for codegen gates

If `pnpm exec convex codegen --dry-run --typecheck enable` is blocked only because `CONVEX_DEPLOYMENT` is missing, and the repo is local/dev, the operator may run `pnpm exec convex dev --once` to create an ignored `.env.local` local deployment, then rerun the dry-run codegen gate. Verify `.env.local` is ignored before committing. Do not print or commit Convex secrets/URLs. If codegen updates generated API bindings, include those generated files in review/commit after gates pass.

## BLOCKED review iteration unlock pattern

When GPT review returns BLOCKED and a same-worker fix card is created as a child of that blocked review, the fix can remain stuck in `todo` until the blocked review is formally completed. Complete the blocked review with an explicit summary like “BLOCKED verdict recorded, not PASS, unlocking fix card,” then verify only the intended fix child promotes. Never treat that completion as acceptance, and do not commit until the dependent re-review returns PASS.

## Worker overload / protocol violation recovery on UI cards

If a UI worker crashes, exits cleanly without `kanban_complete`/`kanban_block`, or hits provider overload after writing partial files, treat the partial diff as contaminated until reviewed. Do not simply unlock the original reviewer.

Recovery pattern:
1. Inspect the worker log and `git status --short` to identify partial files.
2. If partial UI files contain fake placeholder records or misleading prototype data, call that out explicitly as a no-fake-data risk.
3. Create a new recovery worker card, preferably with the same UI profile once provider pressure clears, that starts from the partial files but requires removing/replacing fake data with real Convex wiring or honest empty/loading/not-found states.
4. Create a dependent GPT-5.5 recovery review card focused on the crash residue: fake data, enabled no-op controls, route existence, responsive UI, route/CSS health, and unintended scope.
5. Only after recovery review PASS should the General rerun final gates, resummon poisoned preview if needed, verify route/CSS health, then commit/push.

This came up on Epic 6.4 when a Kimi worker hit HTTP 429/provider overload after creating partial client UI files with fake Moroccan client records. The correct recovery was not to preserve the placeholder dataset; it was to create a recovery card requiring honest empty/not-found client UI and no fake financial records.

## Convex read wiring UI cards

When an ImmoPilot UI card wires frontend reads to Convex, require safe query gating before review/commit:

- Inspect the current provider/auth/org stubs before deciding wiring. Do not assume a real organization context exists.
- Keep React hooks in stable order, but skip Convex queries until all required readiness inputs are valid (provider/client URL, organizationId, parsed IDs, etc.). Use Convex skip semantics or the repo-approved equivalent rather than conditionally calling hooks.
- If provider/org readiness is missing, render an honest disconnected/no-org state and do not issue invalid queries.
- Preserve legacy/no-TTC explicit states; never guess old sale totals or default TVA to make a read screen look populated.
- No financial write mutation UI should be enabled during read-wiring cards.

## Apostrophe/entity leakage review gate for French ERP UI

For ImmoPilot French/Moroccan UI strings, treat visible HTML entity leakage as a blocker, especially in JS prop strings/template strings:

- Do not put `&apos;`, `&amp;apos;`, `&eacute;`, etc. inside strings that React will render as text.
- Use real French characters/apostrophes (`n’a`, `d’échéancier`, `réservation`) or safe JSX text instead.
- After UI fixes, grep the newly touched files for `&apos;`, `&amp;apos;`, and similar entities, and probe rendered HTML when possible.
- This applies even when the feature is otherwise architecturally correct; visible entity leakage makes the ERP look unserious.

## Convex React provider/query gating in UI read-wiring cards

When wiring ImmoPilot UI routes to Convex reads, do not assume `useQuery(..., "skip")` is enough for disconnected/provider-missing states. `skip` avoids executing the query, but the hook still requires a mounted `ConvexProvider` / `ConvexReactClient` context. A route can still 500 if a component calls `useQuery` outside the provider, even with skip args.

Safe pattern for read-wiring cards:

1. Add/verify provider infrastructure at the app shell level.
2. In the route/page shell, check provider URL/client/org readiness using non-Convex hooks/context/env-safe values only.
3. If provider/org is missing, render an honest unavailable/disconnected state before mounting any component that calls Convex hooks.
4. Mount a separate inner query component only when provider + real org readiness are confirmed.
5. Inside that provider-safe inner component, use `skip` for argument readiness (`saleId`, IDs, filters), but never as the only protection against a missing provider.
6. Reviewer must probe the disconnected route (for example `/app/sales/test-sale`) and confirm it returns 200 with honest unavailable copy, not 500.

This emerged on ImmoPilot 6.9: the first fix used `useQuery(..., "skip")`, but GPT review correctly blocked because the sale detail route still crashed without ConvexProvider. The accepted fix structurally split outer readiness shell from inner query component.

## Commit discipline

For Ayman’s ImmoPilot cards:
- Worker done is not enough.
- Reviewer PASS is not enough for preview cards.
- Backend-only PASS does not create a new visual test surface; report it as backend accepted, committed, and pushed.
- Commit only after PASS, clean gates, clean route verification when preview/UI health is relevant, and known preview cache recovery if needed.
- If review BLOCKED, create a same-worker fix card with the exact blocker and a dependent GPT re-review card, then unlock the fix via the blocked-review iteration pattern above.
