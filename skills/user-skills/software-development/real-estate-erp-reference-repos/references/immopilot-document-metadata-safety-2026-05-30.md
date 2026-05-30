# ImmoPilot document metadata backend safety notes — 2026-05-30

## Context
After the doctrine-first audit, the first build card was document metadata foundation backend. Review blocked the first implementation because document attachment safety was incomplete.

## Durable lesson
Document metadata is security-sensitive even before real file upload exists. Treat attachment metadata like financial evidence: every read and state change must prove tenant scope and referenced entity ownership, not only document row ownership.

## Required backend behavior
For `documents` metadata functions:

- `create`: validate referenced entity exists and belongs to `organizationId` before insert.
- `listByEntity`: validate the referenced entity before querying documents.
- `listByProject`: validate the project belongs to `organizationId` before querying project documents.
- `get`: validate document row `organizationId`, then validate the referenced entity still belongs to the org before returning. If the referenced entity is gone, return a safe not-found/null rather than leaking stale metadata.
- `archive` / `markDeleted`: validate document row `organizationId` and referenced entity/project scope before changing status.
- Default lists exclude `status: deleted` unless explicitly requested.
- Archive/delete are soft metadata state transitions and should be audited.

## Unsupported entity types
The doctrine allowed broad `entityType` values including `deliveryNote` and `other`, but implementation safety must be stricter:

- `deliveryNote`: reject until a real `deliveryNotes` table/functions exist. Do not fake a table or silently attach.
- `other`: reject until there is a safe scoped model. Do not allow arbitrary unvalidated attachments.
- Keeping a schema union value for future doctrine compatibility is acceptable only if all public functions reject it safely at runtime.
- Do not let existing `other`/`deliveryNote` rows bypass validation through `get`, `archive`, or `markDeleted`.

## Reviewer pressure points
A GPT-5.5 reviewer should explicitly check:

1. `other` is not an arbitrary attachment backdoor.
2. `deliveryNote` is safely rejected until implemented.
3. Every read/state-change path validates referenced entity/project ownership.
4. Permissions use `documents.view`, `documents.upload`, `documents.delete` or equivalent role doctrine.
5. Deleted docs are hidden by default.
6. No UI/upload/OCR/e-signature is added in the metadata foundation card.
7. Gates pass: `git diff --check`, typecheck, lint, build, Convex codegen dry-run with typecheck, Convex TS noEmit.

## Card sequencing
Do not build upload UI before the metadata spine is reviewed. After metadata backend PASS, safe next cards are:

1. Document center shell — honest UI and empty states, no fake upload.
2. Actual upload/storage flow.
3. DeliveryNotes / bons de livraison backend linked to document metadata.
