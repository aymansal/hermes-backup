# Telegram /sethome Delivery for Cron Jobs

## Lesson

For Ayman's Hermes cron jobs, use `deliver: telegram` by default when the intended target is the current Telegram home destination. Do **not** hardcode a chat/topic such as `telegram:<chat_id>:<thread_id>` unless Ayman explicitly asks for that exact topic.

`deliver: telegram` follows the active Telegram `/sethome` target. If notifications arrive in the wrong topic, first check whether `/sethome` itself points there before editing every job.

## Safe workflow

1. Inspect jobs read-only with `cronjob(action='list')`.
2. Identify jobs with hardcoded Telegram destinations.
3. Update only the intended jobs:

```python
cronjob(action='update', job_id='<id>', deliver='telegram')
```

4. Re-list jobs and verify all expected jobs show:

```text
deliver: telegram
```

5. Tell Ayman that changing `/sethome` changes where these jobs deliver.

## Pitfalls

- A hardcoded topic keeps delivering there even if Ayman later changes `/sethome`.
- `deliver: telegram` is correct for general cron reports, watchdogs, backup reports, memory-curator reports, and quota-warmup reports unless a specific chat/topic was requested.
- Do not confuse `deliver: telegram` with "this current topic". It means the configured Telegram home channel/topic.
