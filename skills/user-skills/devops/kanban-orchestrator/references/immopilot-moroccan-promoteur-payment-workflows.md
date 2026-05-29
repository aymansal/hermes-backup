# ImmoPilot Moroccan promoteur payment workflows

Use this reference for ImmoPilot cards that touch sales, encaissements, payment schedules, TVA, balances, or reporting.

## Product framing

ImmoPilot is for Moroccan real-estate promoteurs. Do not default to US mortgage-first assumptions.

Preferred domain language:
- `encaissement` / incoming payment
- `avance` / reservation advance
- `tranche` / installment milestone
- `solde` / remaining balance
- `échéancier` / payment schedule
- contract total is TTC when used for payment balance enforcement

Bank financing can exist, but it is one Moroccan case inside the promoteur workflow, not the default worldview.

## Safe backend sequence

Before wiring payment submit or schedule UI:
1. Persist sale HT / TVA / TTC snapshots safely.
2. Enforce active incoming payment totals against sale TTC.
3. Build Moroccan promoteur `échéancier` backend.
4. Build `échéancier` UI.
5. Wire incoming payment submit and optional schedule-line matching.

## Incoming payment balance enforcement

Rules:
- Multiple payments per sale are allowed.
- Payments apply against sale TTC / total contract amount.
- Payments do not create TVA.
- Count active statuses: `pending`, `received`, `reconciled`.
- Ignore `voided` and `archived`.
- Reject `sum(active payments) + effective amount > sale TTC`.
- Legacy/no-TTC sales must be rejected safely for real edits/payments; never guess `20%` or `sale.price`.

Review pitfalls found in-session:
- `update` must enforce using effective amount for any real edit, not only when `amount` changes.
- No-op `update` calls should return unchanged before balance/legacy-TTC enforcement.
- On update, exclude the payment itself from the active sum.

## Échéancier backend expectations

Schedule lines should support Moroccan promoteur milestones:
- `Avance` / reservation advance
- `Tranche 1`, `Tranche 2`, etc.
- `Solde`
- custom labels

Each line should carry tenant-safe sale context and fields such as:
- `organizationId`, `saleId`, `clientId`, `apartmentId`, `projectId`
- `label`, `dueDate`, `expectedAmount`, paid/derived-paid support
- `status`, `sortOrder`, optional `notes`, timestamps

Statuses should fit promoteur flow:
- planned
- partially paid
- paid
- late
- cancelled

Financial rules:
- Sum of non-cancelled expected schedule amounts must not exceed sale TTC.
- Complete schedules must equal sale TTC, or the system must explicitly flag them as incomplete/mismatched.
- Do not silently treat mismatched schedules as balanced.
- Audit create/update/cancel/reorder/replace mutations.

## Kanban review guardrails

For these cards, GPT-5.5 review must be strict about:
- overpayment and over-scheduling
- legacy total guessing
- tenant leaks
- missing audit logs
- generated Convex API drift
- no fake data, no Sobhi hardcoding, no Stripe
