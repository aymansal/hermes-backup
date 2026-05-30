# Product Intent Review Pitfall: Remove Means Remove

## Trigger
Use this when a Kanban card changes ERP/product UI based on Ayman's product correction, especially when he says a field, option, or control is obvious, unnecessary, or should not exist.

## Lesson
Do not satisfy the instruction with the narrowest technical equivalent. Ayman expects product intent, not minimum compliance.

Bad interpretation:
- User says: "Devise should not be a textbox; Morocco is obviously MAD."
- Worker changes editable `Devise` input into a read-only `MAD` box.
- Reviewer passes because arbitrary input is gone.

Correct interpretation:
- Remove the visible `Devise`/currency field entirely from the main form.
- Keep `currency: "MAD"` internally only if backend/type compatibility needs it.
- Show currency through amount formatting (`DH`/`MAD`) or system settings, not as user-facing form clutter.

## Worker prompt requirement
When the user says a UI element should not exist, instruct the worker explicitly:
- remove the visible label/control entirely
- do not replace it with disabled/read-only UI
- keep internal constants/defaults only if required for compatibility
- verify the served page text no longer contains the removed label

## Reviewer checklist
Before PASS, verify:
- the visible UI no longer contains the removed label/control
- there is no disabled/read-only substitute standing in for the removed field
- internal defaults are not arbitrary user input
- the implementation matches the product intent, not only data-safety minimums
- the served preview HTML for the exact route does not contain the removed label, placeholder, or standalone substitute value (for example `Devise`, `placeholder="MAD"`, or a standalone `MAD` form row)

If a reviewer returns PASS but the user points out an intent mismatch, treat the PASS as superseded by product correction: open a same-worker fix loop immediately, update the review prompt to encode the corrected intent explicitly, and do not commit the narrow implementation.

## Example
For Moroccan ImmoPilot sale forms:
- `Devise` field: absent from visible form
- internal default: `MAD` allowed
- amount display: formatted as MAD/DH
- no currency selector/textbox/read-only currency form row
