# Kanban progress estimation for Ayman

Use this reference when Ayman asks for a percentage like "how much is done?" during an ImmoPilot/Hermes Kanban raid.

## Core lesson

Do not report raw Kanban done/remaining as the product truth. Kanban cards are not equal weight: review cards, fix cards, small route shells, backend foundations, and final smoke tests have very different risk and effort.

Always separate two numbers:

1. **Raw board completion** — mechanical count from `hermes kanban stats`.
2. **Weighted/product completion** — judgment based on doctrine epics, committed feature coverage, open high-risk gaps, and whether routes are wired or only honest shells.

## Fast method

1. Run a lightweight board count:
   - `hermes kanban --board <board> stats`
2. Inspect the current active card summary only if needed:
   - `hermes kanban --board <board> show <active_task_id>`
3. Compare against the project doctrine/epics, not only card counts:
   - `docs/doctrine/IMMOPILOT_KANBAN_EPICS.md`
   - current commits / merged modules if already visible
4. State both estimates plainly.

## Response pattern

```text
Raw Kanban count: <x>% done / <y>% remaining.
Product-weighted MVP estimate: about <a>% done / <b>% remaining.

Why different:
- Cards are not equal size.
- Review/fix cards inflate the done count.
- Remaining final gates/dashboard/security/smoke tests may be heavier than their card count.

My tactical read:
<one short paragraph, no fake precision>
```

## ImmoPilot example from the evidence-spine raid

In the May 2026 ImmoPilot session, `hermes kanban stats` showed:

- done: 154
- todo: 3
- blocked: 6
- raw completion: ~94.5%

But the honest product estimate was closer to **80–82% complete / 18–20% remaining**, because dashboard/reporting, final tenant-isolation review, UI/design/performance review, final smoke test, and unwired route shells still mattered more than their raw card count.

## Pitfalls

- Do not say "94% complete" without caveat when the remaining work includes high-risk final reviews or production-MVP smoke testing.
- Do not invent exact precision. Use ranges like `80–82%` when weighing roadmap completion.
- Do not turn a quick percentage question into a long audit unless Ayman explicitly asks for details.
