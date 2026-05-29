# Hermes update auto-stash with custom source patches

## Context
When a Hermes install is Git-based, `hermes update` protects local source edits by auto-stashing dirty files before updating. This is helpful for ordinary accidental edits, but it is a poor control plane for deliberate custom dashboard/runtime modifications.

## Verified source behavior
Relevant source paths:
- `hermes_cli/main.py` — `cmd_update`, `_stash_local_changes_if_needed`, `_restore_stashed_changes`
- `scripts/install.sh` — installer update path with stash prompt
- `website/docs/getting-started/updating.md` — official update flow docs

Observed behavior from source:
- Dirty tree detection uses `git status --porcelain`.
- Stash command uses `git stash push --include-untracked -m hermes-update-autostash-...`.
- The stash therefore captures both modified and untracked files.
- In interactive/gateway prompt mode, Hermes can ask `Restore local changes now? [Y/n]`.
- In non-interactive automation/cron, restore may proceed without the operator answering `n`.
- If stash restore conflicts, Hermes preserves the stash but resets the working tree clean with `git reset --hard HEAD` so conflict markers do not brick the CLI.
- Official docs also state that `hermes update` can auto-restart running gateways after update.

## Why this is risky for deliberate custom source patches
For custom Hermes source features such as dashboard quota cards, multi-account Codex selection, runtime footer patches, or approval-token patches, auto-stash is too broad and too implicit:
- It may capture scratch/untracked files unrelated to the intended patch.
- It cannot express ordered patch intent or scope.
- It can reapply old custom changes silently in cron.
- A conflict can remove the custom code from the live tree until manually restored/fixed.
- Gateway auto-restart is undesirable for unattended Comms Gate operations.

## Preferred workflow
For planned local customizations, keep a patch pack outside the repo and never run `hermes update` while the patch is applied.

Safe sequence:
1. Create native backup: `hermes backup` or `hermes update --backup` only after patch is removed.
2. Reverse/unapply the custom patch with `git apply --reverse --check` then `git apply --reverse`.
3. Confirm the repo is clean with `git status --porcelain`.
4. Run `hermes update --backup` or controlled Git update.
5. Reapply custom patch with `git apply --check` then `git apply`.
6. Verify Python compile, targeted tests, and dashboard build.
7. Restart dashboard only after PASS. Gateway restart requires explicit operator approval.

If unapply fails: stop before update. If reapply fails after update: leave clean updated source, report BLOCKED, and fix the patch against upstream.

## Operator communication lesson
If the operator asks “why not use Hermes auto-stash?”, answer directly: auto-stash is a safety net, not a deployment strategy. It is good for preserving accidental local edits, but for recurring custom patches it is less deterministic than an explicit unapply/update/apply/verify workflow.