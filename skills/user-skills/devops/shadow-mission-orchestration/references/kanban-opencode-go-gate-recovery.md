# Kanban OpenCode Go Gate recovery

## Trigger
Use this reference when a Kanban worker assigned to an OpenCode Go profile exits cleanly but the board shows a protocol failure such as:

```text
worker exited cleanly (rc=0) without calling kanban_complete or kanban_block — protocol violation
Agent crashed 3x
```

Especially likely when Ayman says an OpenCode Go subscription/API key changed or expired.

## Doctrine
This is often an Access Gate problem, not an app/code failure. Do not immediately rewrite the feature or blame the worker output.

## Safe recovery sequence

1. **Protect secrets**
   - Never repeat the API key back in chat.
   - Store it only in `.env` files / configured secret locations.
   - Do not save raw keys to memory, skills, docs, logs, or commits.

2. **Update all relevant Hermes profile env files**
   Common OpenCode Go profile locations on Ayman's Hermes VPS:

   ```text
   ~/.hermes/.env
   ~/.hermes/profiles/shadowkimiresearch/.env
   ~/.hermes/profiles/shadowdscoder/.env
   ~/.hermes/profiles/memoryreviewds/.env
   ~/.hermes/profiles/memoryscoutds/.env
   ```

   Replace only the `OPENCODE_GO_API_KEY=` value. Do not print the value.

3. **Run a redacted env check**
   Verify each file has a non-empty `OPENCODE_GO_API_KEY`, but print only booleans / redacted status.

4. **Smoke test the affected profile**
   Example:

   ```bash
   hermes -p shadowkimiresearch chat -q 'Respond exactly: OPENCODE_GO_SMOKE_OK' --toolsets safe --quiet
   ```

   Success is the exact smoke marker without provider/auth errors.

5. **Resume the blocked Kanban card**
   If the worker was auto-blocked from the expired key:

   ```bash
   hermes kanban --board <board> unblock <task_id>
   hermes kanban --board <board> dispatch
   hermes kanban --board <board> show <task_id>
   ```

6. **If it fails again, inspect before rerouting**
   Run a short `hermes kanban log <task_id>` and `git status --short`.
   Workers may leave usable uncommitted code even when they fail to call `kanban_complete` / `kanban_block`. If the log contains a final report and files exist, preserve the work, complete the worker as a review-required handoff, and start GPT-5.5 review.

## Success criteria
- Profile smoke test passes.
- The card is running again, or its useful output is salvaged into a review-required handoff.
- No secret value appears in chat, commits, docs, memory, or skill text.

## Pitfall
Do not capture `OpenCode Go is broken` as a durable rule. The durable lesson is the recovery path: refresh the Access Key in the relevant profile `.env` files, smoke test the profile, then unblock/dispatch or salvage the worker output.
