# Kanban notifier subscriptions and phase-event limits

## Why this exists

During an ImmoPilot raid, the General expected Telegram to report that a worker had started. The board was healthy and the gateway was active, but Ayman did not receive a "worker started" notification. Inspection showed two separate realities:

1. The current gateway Kanban notifier only delivers terminal/attention events, not all phase transitions.
2. Tasks created from the CLI may not be subscribed to the current Telegram topic unless the operator explicitly subscribes them.

This matters because Ayman's Kanban doctrine expects the main chat to stay informed without manual long polling.

## Current notifier behavior to assume

The gateway notifier delivers events like:

- `completed`
- `blocked`
- `gave_up`
- `crashed`
- `timed_out`

Do **not** assume Telegram will notify on:

- `created`
- `claimed`
- `spawned`
- `running`
- `heartbeat`

So a missing "worker started" message is not automatically a broken Comms Gate. It may be a notifier scope limit.

## Operator checklist when creating cards from CLI

After creating a worker/reviewer pair, explicitly subscribe each card to the current Telegram topic if the user expects pings:

```bash
hermes kanban --board <board> notify-subscribe <task_id> \
  --platform telegram \
  --chat-id <chat_id> \
  --thread-id <thread_id> \
  --notifier-profile default
```

Then verify:

```bash
hermes kanban --board <board> notify-list <task_id>
hermes kanban --board <board> notify-list
```

The row should show the task id and `telegram:<chat_id>:<thread_id>`.

## Review-required handoff unlock pattern

Some workers intentionally `block` with `review-required` because they are not allowed to declare PASS. When that happens:

1. Inspect the worker handoff with `hermes kanban show <worker_id>`.
2. Record that it is a handoff, not a pass.
3. Mark the worker task `complete` only to unlock the dependent reviewer:

```bash
hermes kanban --board <board> complete <worker_id> \
  --summary "review-required handoff, not PASS. <short summary>. Reviewer required before commit/push."
```

4. Dispatch once:

```bash
hermes kanban --board <board> dispatch
```

5. Verify the reviewer is `running` and report the reviewer id/status.

Never commit, deploy, or report success until the reviewer returns PASS and the General verifies final gates.

## If user asks why no start ping arrived

Answer plainly:

- notifier subscription may be missing for that card;
- current notifier does not emit `claimed`/`spawned` start events;
- terminal event pings should still arrive when a worker blocks/completes/crashes/times out;
- subscribe the active cards now and continue the raid.

## Future improvement card

If Ayman asks for full phase-change pings, queue a Hermes ops card to extend the notifier to include safe start/progress events such as `claimed`/`spawned` and reviewer start, with rate limiting. Do not pretend the current notifier already supports it.
