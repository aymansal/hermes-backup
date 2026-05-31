# ImmoPilot carry-on / Kanban resume pattern

## Trigger
Use when Ayman says a short continuation command such as:

- "carry on with ImmoPilot"
- "continue ImmoPilot"
- "what next for ImmoPilot"

Especially after context compaction or after unrelated Hermes/system work interrupted the app raid.

## Doctrine
Do not guess the next feature from memory alone. Resume from the current repo + Kanban truth, then pick the next small reviewed slice.

## Safe resume sequence

1. Load the ImmoPilot forge/orchestration skills.
2. Search recent session context only enough to identify likely active raid state; do not over-investigate if Kanban can answer directly.
3. Inspect the real repo state first:
   - `git -C /home/ubuntu/immopilot status --short --branch`
4. Inspect the ImmoPilot board:
   - `hermes kanban --board immopilot list --status running`
   - `hermes kanban --board immopilot list --status blocked`
   - `hermes kanban --board immopilot list --status todo`
   - or `hermes kanban --board immopilot stats`
5. If an older card is blocked by a stale/protocol issue but later audit/cards already moved past it, do not blindly resurrect it. Read the latest product/audit/review cards and continue from the current doctrine-backed sequence.
6. For repo-changing work, create a worker card plus a dependent GPT-5.5 review card before implementation. Use `dir:/home/ubuntu/immopilot`, not scratch.
7. Dispatch only the worker, then report card IDs/status quickly so the chat remains available.

## Choosing the next slice
For ImmoPilot, when a reviewed product gap audit exists, prefer its ranked next cards over stale board ordering. The doctrine-first sequence after the documents/backend gap is:

1. document metadata foundation backend
2. documents route/center shell
3. bons de livraison backend
4. purchase UI/backend wiring
5. outgoing payments UI wiring

Adjust only if the current board shows a more recent PASS/BLOCKED decision.

## Kanban CLI pitfall
The `--board` option belongs immediately after `kanban`, before the subcommand:

```bash
hermes kanban --board immopilot show <task_id>
```

Not:

```bash
hermes kanban show <task_id> --board immopilot
```

The latter fails with `unrecognized arguments: --board immopilot`.

## Reporting shape
Keep the first update compact:

```text
System report: ImmoPilot raid resumed.
Repo: clean/dirty
Current board: <running/blocked/todo summary>
Opened/continued: <worker card id>, review <review card id>
Next move: wait for worker handoff → GPT-5.5 review → final gates → commit/push if PASS
```
