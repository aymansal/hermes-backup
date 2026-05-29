# ImmoPilot Moroccan promoteur payment workflow lessons

Use this reference when orchestrating ImmoPilot cards that touch sales, incoming payments, balances, TVA, or client payment schedules.

## Core product correction

ImmoPilot is for Moroccan real-estate promoteurs. Do not frame the payment model as USA-style mortgage-first logic. Bank financing can exist, but it is one Moroccan case, not the default worldview.

Core currency doctrine: ImmoPilot's normal Moroccan sale, payment, purchase, and échéancier flows use Moroccan dirham. Display amounts as MAD/DH and do not expose a free `devise`/currency textbox in these flows. If a schema or mutation keeps a `currency` field for compatibility, default/pass `MAD` internally. Multi-currency must be a future controlled/system-level feature with exchange-rate logic, not arbitrary user-entered text.

Prefer Moroccan promoteur language and workflow concepts:

- `avance` / reservation advance
- `tranche` payments
- `solde` / final balance
- `échéancier` / payment schedule
- `remise des clés` / handover milestone
- notarial or contract milestones where relevant
- mixed flows: client advance + scheduled promoteur installments + bank disbursement + final balance

## Payment and TVA doctrine

Incoming payments are receipts against a sale's TTC contract total. They do not create TVA themselves.

Rules:

- Sale/contract stores HT, TVA, and TTC snapshots.
- Incoming payments apply against TTC.
- Multiple incoming payments per sale are allowed.
- Active incoming payments should count toward consumed balance: `pending`, `received`, `reconciled`.
- Non-active incoming payments should not consume balance: `voided`, `archived`.
- Backend must reject any create/update where active payments would exceed sale TTC.
- On payment update, enforce using the effective payment amount for any real edit, not only when amount changes.
- Legacy sales without trustworthy TTC snapshots must not be guessed from old price fields or defaulted to 20%; block balance-sensitive edits and require review.

## Safe implementation sequence

Before wiring a real incoming payment submit or building an échéancier UI:

1. Sale TVA backend persistence: HT/TVA/TTC snapshots, validation, audit.
2. Incoming payment balance enforcement: active sum <= sale TTC, legacy/no-TTC safe failure.
3. Moroccan échéancier backend: planned tranches/due dates/expected amounts/status/link to payments.
4. Échéancier UI on sale/client/payment screens.
5. Sale detail + échéancier read wiring: prove the UI can read real sale TTC, schedule lines, summary, loading/not-found/legacy states before enabling any create/update/cancel/payment submit controls.
6. Échéancier creation/edit UI and incoming payment submit wiring only after the read path is truthful and reviewed.

Rule: for financial UI, read truth before write power. Do not enable write controls until the screen has a verified read path and no fake/no-op states.

## Review pitfalls

- Build `paymentScheduleLines` before visible schedule controls.
- Keep incoming payments as receipts against sale TTC; optional `scheduleLineId` links a receipt to a schedule line but must validate same tenant and same sale.
- Schedule summaries may derive paid amount from linked incoming payments to avoid dual-source-of-truth drift.
- UI can surface the échéancier before mutations are wired, but CTAs must be disabled with clear copy and the screen must show honest disconnected/no-TTC/empty states instead of fake avance/tranche rows.
- For sale-detail UI, route health and rendered French copy matter: block visible HTML entity leakage (`&apos;`, `&amp;apos;`) because it makes ERP screens look unserious.

## Review pitfalls

After the Moroccan échéancier backend is reviewed, committed, and pushed, the next visible UI card should usually be a focused UI card rather than more backend work.

Recommended pattern:

- Worker profile: use the UI/Kimi lane for visible schedule surfaces.
- Primary route: start with `/app/sales/[saleId]` because the schedule belongs to the sale contract and sale TTC total.
- Scope: add the échéancier section/surface and minimal links only; avoid broad redesign if Ayman may hand-polish later.
- Required states: honest not-found/unavailable/no-TTC/no-data states before fake examples.
- Required display concepts: sale TTC, expected schedule total, encaissements paid, remaining balance, next due date, overdue count, balance status, and lines for avance/tranches/solde/custom labels.
- Required control discipline: add-line/record-payment CTAs must be real navigation/actions or disabled with explanatory copy until mutations are safely wired.
- Finish discipline: UI cards need route and CSS health verification after PASS, especially because build/codegen can poison Next `.next` during dev preview.

## Review pitfalls

GPT-5.5 review should explicitly check:

- No USA mortgage-first assumptions in naming or flow.
- No double-taxing: payments do not calculate TVA.
- Multiple payments remain possible while overpayment is blocked.
- Updates cannot bypass balance enforcement through non-amount edits.
- Legacy/no-TTC records are preserved and flagged/rejected, never silently guessed.
- No enabled no-op buttons in financial UI.
- No fake client/sale/payment/schedule records in échéancier UI; unavailable data must be shown as unavailable, not invented.
