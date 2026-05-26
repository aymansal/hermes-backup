# Kanban fast-status heartbeat doctrine

## Trigger
Use this reference when Ayman asks only:

- `Update?`
- `Status?`
- `Updates?`
- short equivalents during a Kanban raid

## Session signal
Ayman explicitly stopped the operator after a status request turned into ~12 minutes of extra work. His correction: he only asked for updates, not investigation.

## Rule
A status request is a heartbeat ping, not permission for a dungeon crawl.

Do only the smallest useful check:

1. `hermes kanban show <active_card>` or known review card.
2. Optional compact active board list for `running`, `blocked`, `todo`.
3. Stop and report.

Avoid unless Ayman says `Go`, asks for details, or the status cannot be answered otherwise:

- full logs/runs
- git diffs
- tests/builds/codegen
- route smoke
- creating fix cards
- dispatching reviewers
- committing
- reading large files

## Response shape
Keep it short:

```text
Status: <running|blocked|done>
Active card: <id + title>
Reason/verdict: <one line from summary if visible>
Next move: <one safe action>
```

## Go means action
When Ayman replies `Go` after a proposed next move, execute that move directly and report the result. Examples:

- review-required worker blocked → mark worker done and dispatch reviewer.
- PASS review → run final gates and commit only the reviewed files.
- narrow blocker → create or perform the smallest same-scope fix and send to re-review.

## Inline fix exception
If a Kanban fix card cannot dispatch and the requested fix is tiny, low-risk, and already authorized inline, it is acceptable to patch directly. Still preserve review discipline:

1. inspect the exact file/range,
2. apply the minimal patch,
3. run relevant gates,
4. create/dispatch GPT-5.5 re-review,
5. do not commit until PASS.

## Pitfall
Do not answer a quick status with “I’ll check” and then spend minutes running gates. Report the heartbeat first; deeper work requires `Go` or explicit detail request.
