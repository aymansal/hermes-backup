# Kanban forced-skill worker crash recovery

## Trigger
Use this when a Kanban worker crash-loops immediately and the worker log shows:

```text
Error: Unknown skill(s): <skill-name>
```

This can happen when the commander can load a Skill Rune, but the assigned worker profile cannot see that skill name/path during Kanban startup.

## Doctrine
This is an orchestration/setup mismatch, not evidence that the app task failed. Do not keep dispatching the same card blindly.

## Fast recovery sequence

1. Inspect only minimal evidence:
   - `hermes kanban --board <board> log <task_id> --tail 180`
   - `git status --short`
   - `git diff --stat`
   - `git ls-files --others --exclude-standard`
2. If the repo is clean and the log only shows `Unknown skill(s)`, block the crash-looping card with a clear superseded reason.
3. Create a replacement card in the same real project workspace (`--workspace dir:/absolute/project/path`).
4. Do **not** pass the unavailable skills via `--skill`. Instead, embed the relevant doctrine and required docs directly in the card body.
5. Create a matching review card parented to the replacement worker.
6. Dispatch one pass and verify the replacement card is `running` rather than crash-looping.

## Success criteria
- Old crash-loop card is blocked/superseded so it stops respawning.
- Replacement worker runs without forced skill loading.
- Repo diffs, if any, are from the replacement worker only.
- Review discipline is preserved; replacement output still goes through GPT-5.5 review before commit.

## Pitfall
Do not store a durable rule like "the skill is broken" or "Kanban cannot use skills." The durable lesson is narrower: if a worker profile cannot resolve a forced skill, embed the needed doctrine in the card body and continue with review gates.
