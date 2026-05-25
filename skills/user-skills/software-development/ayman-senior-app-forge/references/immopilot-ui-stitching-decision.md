# ImmoPilot UI stitching decision — V1 coverage + compact navigation

Session lesson: Ayman reviewed two clickable ImmoPilot visual prototypes.

## Decision

For implementation-phase UI stitching, do **not** keep chasing prototype polish. Continue building the real app and use:

- **V1 as the functional/module baseline**: serious ERP coverage, practical density, real-estate developer workflows, finance/project-control orientation.
- **V2 navigation as the shell correction**: compact/top navigation or non-scroll compact nav pattern instead of V1's oversized scrollable sidebar.

Ayman may personally redesign the final visual UI later. Agent-built UI should prioritize wiring real backend flows, buttons, states, and screens safely over speculative taste iterations.

## What failed / what to avoid

- V1 problem: oversized, scrollable enterprise sidebar.
- V2 problem: visually worse overall despite a better compact navigation idea.
- Avoid assuming "modern/creative" means replacing the product feel wholesale.
- Avoid spending more raids on aesthetic prototypes once the product direction is clear enough.

## Implementation guidance

When building ImmoPilot screens now:

1. Use the existing real app architecture and real Convex data functions.
2. Keep screens modular and stitch buttons/forms/tables to real flows.
3. Use V1's module coverage and information architecture for what pages should contain.
4. Use V2's compact navigation idea only to avoid huge scrollable sidebars.
5. Keep design restrained and replaceable, so Ayman can redesign the final UI without fighting tangled business logic.
6. Do not hardcode Sobhi into product branding; Sobhi is sample/tenant data only.

## Acceptance cue

A screen is acceptable for this phase if it is navigable, connected or ready to connect to tenant-safe backend functions, has clear loading/empty/error/access states, and does not block future visual redesign.
