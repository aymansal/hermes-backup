# Cron Delivery + No-Agent Curator Case

## Context

Ayman reported that Hermes scheduled job reports were not landing in the same Telegram forum topic:

- Backup cron report reached the current General topic.
- Codex quota cron report landed in another Shadow Realm 2 topic.
- Daily Holographic Memory Curator did not deliver because the job itself failed.

Desired target for all Hermes cron/system reports:

```text
telegram:-1003650104887:1
```

Meaning: Shadow Realm 2 group, General topic/thread `1`.

## Diagnosis pattern

1. List all cron jobs and check each job's `deliver`, `last_status`, and `last_delivery_error`.
2. Inspect `~/.hermes/cron/jobs.json` only as evidence; use the native cron tool/CLI for updates when possible.
3. Check `~/.hermes/cron/output/<job_id>/` to distinguish delivery failure from execution failure.
4. Read `~/.hermes/logs/agent.log` for scheduler lines such as delivered target, silent run, missing output, SQLite lock, or timeout.
5. For Telegram forum topics, do not assume the group is enough. Pin the exact thread target: `telegram:<chat_id>:<thread_id>`.

## Fix pattern used

- Updated every existing cron job to explicit delivery target `telegram:-1003650104887:1`.
- Converted the Daily Holographic Memory Curator from agent-driven prompt mode to a `no_agent=true` script.
- Used a dedicated script under `~/.hermes/scripts/daily_memory_curator.py`.
- Manual terminal script run verified exit `0` and added deduped durable facts.
- Manual cron run verified scheduler status OK; empty stdout was accepted as a silent OK because no new facts remained.

## Why no-agent script mode was better

Agent-driven curator jobs can fail for this class because:

- Cron sessions may not expose interactive memory tools.
- Long tool loops increase SQLite lock/timeout risk.
- The model can over-scan, retry, or trigger extra background review behavior.
- Delivery success does not imply memory write success.

A no-agent script is better for recurring curator automation because it is deterministic, bounded, quiet when no facts exist, and easier to verify from output files and scheduler logs.

## Verification checklist

After patching this class of job, verify:

- `cronjob list` shows each relevant job has explicit `Deliver: telegram:<chat_id>:<thread_id>`.
- Curator job shows `script=<script>.py` and `no_agent=true`.
- Last status is OK and `last_delivery_error` is null.
- Manual run creates an output file under `~/.hermes/cron/output/<job_id>/`.
- If no new facts exist, output may say `silent (empty output)` and scheduler logs may say `agent returned [SILENT] — skipping delivery`; this is successful for quiet no-agent jobs.
- The next scheduled run remains unchanged after manual testing.

## Data-quality guardrails

The curator should reject:

- secrets, API keys, tokens, cookies, private keys
- bearer/OAuth/JWT values
- raw logs and raw transcript dumps
- quota percentages, cooldowns, timestamps, run/session IDs
- PR/issue numbers and commit SHAs
- transient process state or anything likely stale within a week

Store only compact declarative durable facts.