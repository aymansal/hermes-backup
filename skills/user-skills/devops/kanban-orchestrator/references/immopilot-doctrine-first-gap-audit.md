# ImmoPilot doctrine-first gap audit pattern

## Trigger
Use this when Ayman says the app feels incomplete, worries the final product will not be enough, mentions missing ERP pieces already discussed (documents, bons de livraison, uploads, purchases, supplier payments, reports), or worries that continued AI coding will make the app sluggish/fragile.

## Operator stance
Do not respond by immediately creating the next feature card. Treat the concern as a product-map failure risk, not a single missing button.

Say plainly:
- the app may be strong in one workflow but still incomplete as an ERP;
- the next safe move is a read-only audit against doctrine;
- no code changes happen until gaps are ranked and turned into small cards.

## Audit card shape
Create a read-only Kanban card before implementation. Required constraints:
- Work in the project repo.
- Read doctrine first, especially MVP scope, schema blueprint, screen blueprints, epics, UI doctrine, SaaS architecture, review checklist, quality gates, and file-size/boundary rules.
- Inspect current routes, components, Convex schema/functions, and docs.
- Classify each module as `exists`, `partial`, or `missing` with evidence paths and business risk.
- Run `git status --short` at start and end and require a clean/no-change report.
- No code/docs/schema/config/package/generated edits.
- No commit/push.

Minimum module map for ImmoPilot:
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
18. Code health: oversized files, duplicated logic, placeholder/prototype patterns, AI-sludge risk

## Review gate
Create a dependent GPT-5.5 review card that checks whether the audit is evidence-based, covers all required modules, ranks top gaps by business importance, recommends small reviewable cards, and preserves ERP-first doctrine:
- no Stripe-first assumptions;
- no fake data;
- no Sobhi hardcoding;
- Moroccan promoteur workflows;
- MAD/DH implicit where relevant;
- documents/uploads and bons de livraison called out explicitly.

## Typical findings from the first ImmoPilot audit
The first audit found that sales/incoming payments/échéancier/reconciliation were the strongest implemented chain, while the ERP core was still incomplete on the chantier/supplier/document side.

Most important gaps:
- documents/uploads missing as a real module;
- bons de livraison/delivery notes missing despite doctrine;
- frontend auth/operator tenant management still partial/stubbed;
- purchases and outgoing payments backend exist but UI is placeholder/disabled;
- dashboard/reports missing;
- cost allocations too narrow;
- several files already exceed file-size doctrine thresholds.

The recommended first build card after the audit was document metadata foundation (backend/schema only), because documents are the evidence spine for BL, invoices, contracts, CIN, payment proofs, plans, and audit evidence.

## Sequencing rule after audit
Do not jump from audit to a giant feature card. Convert findings into small cards:
1. document metadata foundation backend;
2. document center shell;
3. deliveryNotes / bons de livraison backend;
4. purchases UI real Convex wiring;
5. outgoing payments UI.

Each implementation card still needs worker handoff, GPT-5.5 review, final gates, commit, and push only after PASS.
