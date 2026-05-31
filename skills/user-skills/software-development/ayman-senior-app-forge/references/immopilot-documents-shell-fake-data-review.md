# ImmoPilot document-shell fake-data review lesson

## Trigger
Use this when building or reviewing an ImmoPilot Documents route/module before real upload/storage/auth wiring is complete.

## Lesson
A route shell may show the intended structure of the documents module, but it must not render fake document records. In the session that created `/app/documents`, review correctly BLOCKED because the worker used placeholder records and a hardcoded Sobhi filename.

## Safe shell pattern
Allowed before real metadata/storage is connected:
- Static category/filter definitions such as contrats, CIN, factures, bons de livraison, preuves de paiement, plans, autres.
- Serious ERP copy explaining the module is the evidence spine.
- Honest empty/unwired state.
- Disabled upload button or no upload button, with clear copy that storage/auth is not wired.
- Table/mobile-card layout skeleton with zero rows.

Forbidden:
- Fake filenames, fake document rows, fake dates, fake linked entities, fake owners, fake metrics, or fake upload success.
- Hardcoded `Sobhi` in generic product code. Sobhi is tenant data only.
- Enabled archive/delete/upload controls before they actually work.
- Claiming backend wiring when auth/org context is still stubbed.

## Review search checklist
Search touched document files for:

```text
Sobhi
PLACEHOLDER_DOCUMENTS
.pdf
2025
2026
```

Then inspect whether matches are static labels/copy or fake records. Category labels are okay; fake business records are not.
