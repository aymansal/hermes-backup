# ImmoPilot financial TVA retrofit playbook

Use this when Ayman introduces or changes financial/tax doctrine after some ERP cards already exist, especially Sobhi/ImmoPilot money flows.

## Core rule

New records must follow the current TVA doctrine. Old records must be preserved, flagged, and reviewed — never guessed.

Do not tell Ayman that a doctrine update automatically applies to already-built backend/schema/UI. Be explicit:

- doctrine applies going forward;
- current UI may show the new rule;
- backend persistence/reporting may still need hardening cards;
- older records need migration-safe review state, not silent defaults.

## TVA doctrine baseline

- Default TVA is 20% for new taxable records when the operator omits a rate.
- Operators may set 0% or a custom valid rate per relevant line/document.
- Preserve HT/subtotal, TVA amount, and TTC/total separately where records are tax-bearing.
- Preserve real units on cost lines: `m3`, `m2`, `kg`, `ton`, `piece`, `lot`, etc.
- Land acquisition, notary fees, permits, bank fees, labor, subcontracting, and manual adjustments are source costs, not fake material purchases.
- Cost allocation and reporting views must distinguish HT / TVA / TTC / unknown tax split when source records carry tax.

## Retrofit sequence

1. TVA audit map across all money-touching schema/functions/UI.
2. Sales TVA backend with snapshots, validation, audit, and legacy tax-review marking.
3. Purchases/purchaseItems TVA backend with line-level TVA, preserved units, HT/TVA/TTC totals, and legacy review marking.
4. Manual source costs for land acquisition, permits, notary, labor, bank fees, adjustments with 0/custom/20% TVA.
5. Cost allocation/reporting TVA awareness separating HT/TVA/TTC and unknown tax splits.
6. Review UI to confirm/fix TVA on older records.

## Sequencing lesson from Epic 6

If a sale/reservation UI shows TVA but the sales backend does not persist HT/TVA/TTC snapshots yet, insert a focused backend hardening card before incoming-payment UI. Otherwise payment UI may depend on incomplete contract totals.

Recommended card before incoming payment UI:

- Sale TVA backend persistence:
  - `subtotalAmount` / HT snapshot;
  - `taxRateSnapshot`;
  - `taxAmountSnapshot`;
  - `totalContractAmountSnapshot` / TTC;
  - deterministic math and rounding;
  - default 20% only for new omitted taxable records;
  - allow 0/custom valid rates;
  - audit financial changes;
  - keep tenant/project/apartment/client ownership and project-apartment invariant;
  - migration-safe optional fields for existing records.

## Review blockers to enforce

GPT review should BLOCK if any of these appear:

- Deposit or financial inputs accept `NaN`, `Infinity`, negative values, or impossible values such as deposit greater than total where enforceable.
- Legacy sales/purchases with missing TVA fields are silently backfilled to 20% on read/update.
- Old records are treated as known-tax records without operator confirmation.
- UI enables persistence before backend tax fields are safely wired.
- Reports combine HT/TTC or confirmed/unknown tax records without labeling.

## Status reporting pattern

When Ayman asks whether the new TVA rule applies to old work, answer in three buckets:

- already applied in current UI/code;
- doctrine saved but backend/reporting still pending;
- unaffected modules that do not store TVA directly.

Then recommend the next hardening card only if it protects a downstream dependency.