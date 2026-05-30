# ImmoPilot doctrine-first gap audit pattern — 2026-05-30

## Trigger
Use this reference when Ayman says ImmoPilot feels incomplete, missing real ERP pieces, fragile, sluggish, or at risk of “AI-sludge,” especially after several narrow feature cards.

## Lesson
Do not continue blindly into the next feature card. The correct move is a read-only product gap audit against the local doctrine, then small backend-first cards.

## Audit card shape
Create a Kanban audit card that is explicitly read-only:

- No code/docs/schema/config/package/generated file edits.
- Read `docs/doctrine/IMMOPILOT_MVP_SCOPE.md` first.
- Read `docs/doctrine/IMMOPILOT_CONVEX_SCHEMA_BLUEPRINT.md` and screen/epic/UI/quality docs as relevant.
- Inspect routes, components, Convex schema/functions, and placeholder libs.
- Start and end with `git status --short`; report if anything changed.
- No commit/push.

## Required module map
Classify each module as `exists`, `partial`, or `missing`, with evidence paths and business risk:

1. Organization/membership/permissions
2. Project hierarchy: project → tranche → bloc → building → floor → apartment
3. Apartment inventory/status/detail
4. Suppliers and subcontractors
5. Purchases and purchase line items
6. Bons de livraison / delivery notes
7. Outgoing supplier/subcontractor payments
8. Cost allocations / project cost lens
9. Clients
10. Sales/reservations
11. Incoming payments
12. Échéancier/payment schedules/reconciliation
13. Documents/uploads/attachment metadata
14. Dashboard/reports/overdue alerts
15. Settings/operator tenant management
16. Audit logs/financial safety
17. UI quality: loading/empty/error/access-denied states
18. Code health: oversized files, duplicated logic, risky AI-sludge patterns

## Output shape
The audit completion comment should include:

- Top 10 gaps ranked by business importance.
- What already works well.
- What is dangerous/fragile.
- Next 5 recommended cards, each small and reviewable.
- Which card should be first and why.
- Explicit documents/uploads and bon de livraison state.

## 2026-05-30 finding pattern
The audit found ImmoPilot was strongest on:

- sales → incoming payments → échéancier → reconciliation

The critical missing/partial ERP side was:

- documents/uploads
- bons de livraison
- real auth/operator tenant management
- purchases UI/schema completeness
- outgoing supplier payments UI
- dashboard/reports
- cost allocation depth
- placeholder client/sales/inventory lists
- fragile financial numbering
- oversized files / placeholder-prototype patterns

Recommended first build card was `Document metadata foundation backend`, because documents are the evidence spine for BL, invoices, contracts, CIN, payment proofs, plans, and audit.

## Card sequencing after audit
Prefer this sequence unless new doctrine or user priority changes it:

1. Document metadata foundation — backend only.
2. Document center shell — honest UI, no fake upload.
3. DeliveryNotes / Bons de livraison backend.
4. Real purchases UI wiring.
5. Outgoing payments UI and supplier balances.

## Safety phrase
If the user is worried about completeness or code quality, answer plainly:

> We stop swinging blindly. First we read the doctrine and map the gaps. No blades out yet.
