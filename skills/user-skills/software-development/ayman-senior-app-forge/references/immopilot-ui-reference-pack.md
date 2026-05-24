# ImmoPilot UI Reference Pack — Session Notes

Use this reference when planning or reviewing ImmoPilot UI work with external design/taste skill packs.

## Context

Ayman asked how to benefit from GitHub UI skill packs such as `awesome-design-md`, UI UX Pro Max, Taste, Impeccable, Vercel agent skills, and Anthropic/Claude frontend-design skills.

The durable lesson: external UI skills are ingredients, not commanders. They should improve ImmoPilot's visual language, tokens, component discipline, accessibility, React/Next.js production quality, and review checklists without overriding product/domain doctrine.

## Prime directive

External UI packs may influence:

- visual language
- spacing and typography
- component treatment
- state design
- review checklists
- accessibility and performance criteria
- prototype workflow

External UI packs must not influence:

- Convex schema
- tenant model
- permissions
- financial rules
- project hierarchy
- Moroccan real-estate workflow
- product-vs-tenant naming

## Inspected sources and roles

### VoltAgent/awesome-design-md

Repo: `https://github.com/voltagent/awesome-design-md`

Use for:
- DESIGN.md examples and token structure.
- Brand-grade references like Vercel, Linear, Stripe, Notion, IBM, Wise/Coinbase/Revolut.
- Creating ImmoPilot's own DESIGN.md.

Recommended ImmoPilot mix:
- 60% Vercel/Linear discipline.
- 20% Stripe business polish.
- 10% Notion document/entity calm.
- 10% IBM/Wise financial clarity.

Do not use for direct brand cloning or replacing ImmoPilot's own design system.

### UI UX Pro Max

Repo: `https://github.com/nextlevelbuilder/ui-ux-pro-max-skill`

Use for:
- Design-system brainstorming.
- UX anti-pattern and checklist searches.
- Table/dashboard/finance/chart guidance.
- Next.js/shadcn implementation reminders.

Useful command pattern:

```bash
python3 src/ui-ux-pro-max/scripts/search.py "<query>" --design-system -p "ImmoPilot"
python3 src/ui-ux-pro-max/scripts/search.py "<query>" --domain style -n 3
python3 src/ui-ux-pro-max/scripts/search.py "<query>" --domain ux -n 3
python3 src/ui-ux-pro-max/scripts/search.py "<query>" --stack nextjs
python3 src/ui-ux-pro-max/scripts/search.py "<query>" --stack shadcn
```

Filtering lesson:
- It suggested real-estate luxury typography like Cinzel/Josefin. That may fit marketing pages, but is probably too decorative for daily ERP screens.
- It suggested real-time monitoring. Useful for operations/control-center thinking, but ImmoPilot is not DevOps software.

Use it as a search oracle and checklist generator, not final brand authority.

### Taste Skill

Repo: `https://github.com/Leonxlnx/taste-skill`

Use for:
- Anti-slop frontend discipline.
- Stronger spacing, typography, component polish, loading/empty/error states.
- Dependency verification before imports.
- Avoiding generic shadcn defaults.
- Avoiding emoji icons in professional UI.
- CSS Grid over fragile flex math.
- `min-h-[100dvh]` instead of `h-screen` for full-height sections.
- Animating transform/opacity instead of layout properties.

Relevant skill packs observed:
- `design-taste-frontend`
- `gpt-taste`
- `minimalist-ui`
- `redesign-existing-projects`
- `stitch-design-taste`
- `image-to-code` for visual references

Avoid for core ERP:
- `industrial-brutalist-ui`
- excessive GSAP/ThreeJS/effects
- infinite micro-animations unless they clearly communicate live status

Recommended ImmoPilot Taste dials:
- `DESIGN_VARIANCE`: 4-5 for ERP core, 6 for marketing/demo pages.
- `MOTION_INTENSITY`: 2-3 for ERP core, 4-5 for polished transitions.
- `VISUAL_DENSITY`: 6-7 for dashboards/tables, 4-5 for onboarding/settings.

### Impeccable

Repo: `https://github.com/pbakaus/impeccable`

Use as a UI quality workflow:

```text
shape → build → audit → polish → harden
```

Valuable reference areas:
- typography
- color and contrast
- spatial design
- motion design
- interaction design
- responsive design
- UX writing

Useful rules:
- Load `PRODUCT.md` and `DESIGN.md` context before UI work.
- Separate product UI from marketing/brand UI.
- Cards are overused; use them only when they are the best affordance.
- Never nest cards inside cards.
- Use 4pt spacing scale: 4, 8, 12, 16, 24, 32, 48, 64, 96.
- Use fixed rem scales for app/dashboard typography.
- Use tabular numbers for money/data tables.
- Ensure 44px touch targets.
- Write concrete loading/empty/error states.

Anti-patterns to adopt:
- no gradient text
- no decorative glassmorphism by default
- no hero-metric SaaS cliché
- no identical card grids everywhere
- no modal as first thought
- no gray text on colored backgrounds
- no bounce/elastic easing

### Vercel Labs Agent Skills

Repo: `https://github.com/vercel-labs/agent-skills`

Use as engineering-grade frontend quality layer, not as taste layer.

Relevant skills:
- `web-design-guidelines`: final UI audit for accessibility, forms, focus, keyboard, reduced motion, images, performance, theming, touch, i18n.
- `react-best-practices`: React/Next.js performance, data fetching, RSC/client boundaries, Suspense, bundle size, waterfalls, serialization, re-renders.
- `composition-patterns`: reusable component architecture and APIs; avoid boolean prop proliferation.
- `react-view-transitions`: subtle route/detail transitions only when they help continuity.
- `vercel-optimize`: later only if ImmoPilot deploys to Vercel and has real traffic/cost signals.

Rules to harvest:
- eliminate async waterfalls
- avoid barrel imports that bloat bundles
- use direct imports and dynamic imports for heavy components
- keep server components as default where possible
- minimize client serialization
- do not define components inside components
- use composition instead of boolean-prop explosion
- reflect navigation/filter state in URLs where useful

### Anthropic Claude Frontend Design Skill

Source: `https://github.com/anthropics/claude-code/blob/main/plugins/frontend-design/skills/frontend-design/SKILL.md`

Use as creative spark and variant-generation layer.

Useful ideas:
- choose a clear conceptual aesthetic before coding
- define purpose, audience, tone, constraints, and differentiation
- execute intentionally, not randomly
- use typography, color, motion, spatial composition, and detail deliberately
- avoid generic AI aesthetics and purple-gradient SaaS sludge

ImmoPilot adaptation:
- Core ERP aesthetic: refined utilitarian, financial control center, calm premium density.
- Marketing/demo aesthetic: premium Moroccan real-estate operating system, more visual but still disciplined.

Do not let this override daily ERP usability. Core screens need speed, clarity, data entry, trust, and financial seriousness more than spectacle.

## Required UI workflow for ImmoPilot

For important screens:

1. Read `IMMOPILOT_UI_DOCTRINE.md`.
2. Read `IMMOPILOT_UI_REFERENCE_PACK.md`.
3. Use UI UX Pro Max for screen-specific search/checklist if useful.
4. Choose an intentional posture, usually Vercel/Linear + Stripe + IBM/Wise.
5. Use Claude frontend-design to force a clear concept when exploring variants.
6. Use Taste with restrained ERP dials to prevent AI slop.
7. Use Impeccable to shape, audit, polish, and harden.
8. Use Vercel React/composition/web-design guidance for production correctness.
9. Convert selected direction to shadcn/Tailwind components.
10. Review screenshots/browser output against doctrine and reference pack.

## Review questions

- Does the screen answer a real ImmoPilot business question?
- Does it feel like serious real-estate ERP, not generic AI dashboard sludge?
- Are tables searchable/filterable/paginated where needed?
- Are forms grouped, validated, and safe?
- Are money/status/document states clear?
- Are loading, empty, error, and access-denied states present?
- Are destructive/financial actions confirmed?
- Is Sobhi only tenant data, not product branding?
- Did external design packs improve clarity rather than decorate randomly?
- Did the implementation respect React/Next.js performance and composition rules?
