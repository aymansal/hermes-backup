# Profile-scoped cron and durable side effects

## Lesson

Kanban workers run under their assigned Hermes profile. Durable state created inside a worker may be written under that worker profile's Hermes home instead of the default gateway profile.

This can make a task appear successful while production never sees it.

## Concrete failure mode

A worker assigned to `memoryscoutds` created a cron job for a daily memory curator. The job was valid but landed in:

```text
/home/ubuntu/.hermes/profiles/memoryscoutds/cron/jobs.json
```

The live gateway scheduler was running under the default profile and read:

```text
/home/ubuntu/.hermes/cron/jobs.json
```

Result: the worker's job looked scheduled from the worker profile but would never fire in the actual gateway.

## Safe pattern

For cards that create durable system state:

1. Let workers design, implement, or propose the change.
2. Verify from the operator/default context, not just from the worker profile.
3. For gateway-visible cron jobs, create or update the final job with the native `cronjob` tool from the parent/operator context when possible.
4. Run `hermes cron list` from the default profile and inspect `/home/ubuntu/.hermes/cron/jobs.json` if needed.
5. Remove any stale duplicate job created under a worker profile after the correct default-profile job exists.
6. Have a reviewer certify the real production/default path.

## Applies to

- Cron jobs / raid timers
- Webhook subscriptions
- Systemd services
- Profile configuration
- Tool/provider config
- Files intended for production paths
- Any side effect the gateway, dashboard, or Telegram runtime must see

## Review checklist

- Is the durable state in the profile the runtime actually uses?
- Does the scheduler/service/gateway list the new object?
- Is there a duplicate object under a worker profile that should be removed?
- Did a reviewer inspect real state rather than trusting the worker summary?
