# Custom Hermes dashboard/source persistence across updates

## Trigger
Use this when a Hermes installation has local dashboard/runtime customizations (for example Codex quota cards, multiple Codex account management, selected-account runtime routing, or Telegram quota footers) and the operator asks for automatic updates or daily cron updates.

## Core lesson
Native `hermes backup` protects Hermes home data, but it excludes the `hermes-agent/` source tree. Dashboard/runtime customizations live in source files, so they must be persisted via git/fork/branch or a patch artifact, not only by native backup.

## Safe update architecture
Do not schedule a blind daily `hermes update` on a dirty customized source tree. First make the source state durable:

1. Create a custom branch, e.g. `ayman/custom-dashboard-codex-quota`.
2. Commit custom source changes in logical groups:
   - Codex quota helper / credential-pool metadata
   - dashboard account cards and quota UI
   - runtime selected-account resolution
   - Telegram runtime quota footer
   - tests and small fixes
3. Push to a private/custom fork remote.
4. Use upstream NousResearch as `upstream` and the custom fork as `origin`.
5. Daily automation should `fetch upstream`, rebase/merge the custom branch, build/test, and stop on conflict.

## Daily automation behavior
A safe Raid Timer should:

- take a native `hermes backup` before changing source
- check for a clean git tree before update
- fetch upstream
- rebase the custom branch onto `upstream/main`
- run Python compile checks for changed backend/runtime files
- run the dashboard frontend build if web files changed
- restart only `hermes-dashboard` automatically if verification passes
- avoid automatic `hermes-gateway` restart unless the operator explicitly configured it
- send a PASS / NOOP / BLOCKED report

## Failure behavior
If rebase conflicts, tests fail, or build fails:

- abort/stop the update path
- do not restart services
- do not force push
- do not delete files
- report the exact blocked file/stage and leave current running services untouched

## Why this matters
Custom dashboard/runtime modifications can be overwritten or blocked by normal upstream updates. Treat them as a maintained downstream branch, not as disposable local edits.
