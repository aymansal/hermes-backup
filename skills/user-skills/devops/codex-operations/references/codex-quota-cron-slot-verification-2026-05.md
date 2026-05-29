# Codex quota cron slot verification — May 2026

## Context

Ayman reported that one Codex account showed a 14:00 Morocco reset while the other accounts did not start/reset as expected. The existing `codex_quota_warmup.py` cron job ran every 10 minutes and was named `warmup/refresh`, but read-only inspection showed the script only implemented a 09:00 Morocco slot:

```python
WINDOW_MINUTES = 20
WARMUP_HOUR = 9

def _slot(now):
    if now.minute >= WINDOW_MINUTES:
        return None
    if now.hour == WARMUP_HOUR:
        return "warmup"
    return None
```

The persisted state only had:

```json
{
  "warmup_at": "...",
  "warmup_date": "..."
}
```

There was no separate `refresh_date` / `refresh_at` or 14:00 slot.

## Lesson

For quota cron issues, do not trust the job name or an earlier report. Verify the script's actual slot logic and state keys. A job named `warmup/refresh` may still only implement a warmup slot.

## Safe diagnostic sequence

1. List cron job config and confirm `script`, `no_agent`, `deliver`, and `last_status`.
2. Read the cron script and inspect `_slot()` / schedule constants.
3. Read the script's state file, usually `~/.hermes/state/codex_quota_warmup_state.json`.
4. Read the first in-window cron output for the day.
5. Run a safe live `/usage` check for each account without printing tokens or full IDs.
6. Compare live reset times against the earlier report.

## Fix pattern

If the goal is to actually start the next 5h quota windows, add a separate Morocco-time refresh/start slot, typically 14:00:

- `09:00` warmup: tiny generation for every usable Codex credential, then live `/usage` for every credential.
- `14:00` restart: tiny generation for every usable Codex credential, then live `/usage` for every credential.
- Use separate state keys such as `warmup_date` and `restart_date` or `refresh_date`.
- Partial account failure should exit non-zero and should not mark that slot complete, so cron retries during the window.
- Reports must say whether each account received a generation call or only a `/usage` refresh.

If the user only wants display freshness, a refresh-only slot can fetch `/usage` without generation, but it does not start a new 5h window.

## Safety

A true restart/warmup slot consumes a tiny amount of Codex quota per account. Ask Ayman before patching the script to add generation at 14:00 or running the restart manually.

Never print tokens, refresh tokens, cookies, raw auth headers, emails, or full account IDs. Use labels and short ID prefixes only.
