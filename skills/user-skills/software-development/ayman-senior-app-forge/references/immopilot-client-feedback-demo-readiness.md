# ImmoPilot client feedback demo readiness

Use this reference when Ayman asks whether ImmoPilot is ready for Sobhi/client testing, internal preview, or a feedback session.

## Positioning doctrine

Do not position an early ImmoPilot build as a working ERP. Position it as a workflow prototype:

```text
Here is the workflow prototype. We want your feedback before locking the final system.
```

This protects trust while still letting a client react to real flows.

## Readiness levels

### Too rough for client feedback
If many core screens still say backend not connected, have missing routes, or the main flow cannot be clicked end-to-end, say it is only a rough visual demo.

### Internal preview for Ayman
Minimum useful internal preview path:

```text
Fournisseurs → Achats → Paiements
```

This lets Ayman judge the finance source-record loop before showing a client.

### First client feedback demo
Minimum useful client feedback path:

```text
Dashboard
→ Projets
→ Projet detail
→ Unités
→ Fournisseurs
→ Achats
→ Paiements
→ Projet Coûts
```

This gives the client concrete workflow questions:

- Does this match how you track costs?
- Do you split purchases across projects?
- What information do you expect on project cost?
- Do suppliers/subcontractors look right?
- What reports matter?

## Product rule

The first feedback demo should emphasize workflow understanding and reactions, not production readiness or paid onboarding.

## Engineering implication

Before a client feedback session, create a short demo checklist/script after these are in place:

1. Achats UI shell.
2. Paiements UI shell.
3. Project `Coûts` lens.
4. Cleaner demo data.
5. Stable preview route smoke.

Do not spend excessive time on polish before the feedback loop unless Ayman asks; he may hand-polish/redesign later. Focus on clickable flows, clear labels, and honest prototype copy.
