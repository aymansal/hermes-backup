# ImmoPilot live doctrine-change playbook

Use this when Ayman introduces a stable product/accounting rule while a Kanban raid is already in motion.

## Trigger

Ayman says a new business rule must apply across ImmoPilot, especially around money, TVA, units, costs, reporting, tenant behavior, or Sobhi workflow.

Examples:
- TVA must be an explicit field, default 20%, with 0% or custom rates.
- Cost lines must preserve real units such as `m3`, `m2`, `kg`, `ton`, `piece`, `lot`.
- Land acquisition, notary, permits, labor, bank fees, and manual adjustments are source costs, not fake material purchases.

## Immediate operator actions

1. Add a comment to the active worker card with the new constraint if the worker is still running.
2. Add a comment to the active reviewer card so GPT-5.5 checks the new rule explicitly.
3. Patch repo doctrine files before future cards drift.
4. Open a separate GPT-5.5 review card for meaningful doctrine diffs.
5. Tell Ayman what is doctrine-only vs implemented code. Do not imply old backend/schema/UI now obeys the new rule automatically.

## TVA-specific sequencing lesson

If TVA is added while building sales/payment flows, do not proceed directly to incoming payment UI after adding only a visual TVA form.

Insert a backend hardening card first:

**Sale TVA backend persistence**
- Persist sale HT/subtotal, TVA rate snapshot, TVA amount snapshot, and TTC/contract total snapshot.
- Default omitted tax rate to 20 only for new records.
- Allow valid 0% and custom rates.
- Reject NaN, Infinity, negative rates/amounts, impossible totals.
- Preserve legacy records without guessing missing TVA as 20%.
- Validate deposits both when the deposit is provided and when price/tax changes would make an existing deposit exceed recomputed TTC.
- Audit financial changes.
- Preserve tenant, client, apartment, project, and project-apartment invariants.

Only after that should incoming payment UI depend on sale totals.

## Payment UI lesson

Incoming payments usually do not create TVA. They are receipts against sale/contract TTC.

Payment UI should:
- say payment applies against sale TTC / contract total;
- avoid adding a separate TVA field to the payment itself unless a future accounting rule requires it;
- validate positive finite amount;
- avoid exceeding remaining balance when known;
- keep submit disabled if backend wiring is not safe yet;
- use honest unavailable/empty states instead of fake sale/payment data.

## Legacy-data rule

Never silently rewrite old records to fit a new doctrine. For old financial records:
- preserve existing totals;
- add optional fields or explicit review-needed state;
- mark unknown tax split honestly;
- let a future review UI confirm HT/TVA/TTC, 0%, custom, exempt, or mixed cases.

## Review blockers that are worth catching

GPT-5.5 should BLOCK, even if build/tests pass, when:
- a deposit can be NaN, Infinity, negative, or greater than the contract total;
- lowering price/TVA can leave an existing deposit greater than recomputed TTC;
- legacy records are silently backfilled with default TVA;
- a payment screen implies payments create TVA;
- an enabled button has no real action/href;
- fake clients, sales, payments, prices, or totals are introduced.

## Commit discipline

Do not commit doctrine or implementation until:
- worker handoff is reviewed;
- GPT-5.5 review returns PASS;
- gates pass;
- Convex generated API dry-run is clean, or write-mode codegen is run and generated files included;
- UI route/CSS health is verified after resummoning Next dev preview if `.next` is cache-poisoned.
