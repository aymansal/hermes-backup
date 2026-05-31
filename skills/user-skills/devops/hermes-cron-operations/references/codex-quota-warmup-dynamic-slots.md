# Codex quota warmup: dynamic staggered slots

## Context

Ayman's Codex quota warmup job runs as a Hermes cron no-agent script and should stagger ChatGPT Codex account warmups so each account's 5-hour reset window lands one hour apart.

## Durable lesson

Do not hardcode a fixed `STAGGERED_SLOTS = {9: 0, 10: 1, ...}` map when the number of `openai-codex` credential-pool accounts can change. The script should count usable accounts from `~/.hermes/auth.json` and derive the active slot from the Morocco hour.

Recommended model:

```python
START_HOUR = 9
WINDOW_MINUTES = 20

def _slot(now: datetime, entries: list[dict]) -> WarmupSlot | None:
    if now.minute >= WINDOW_MINUTES:
        return None
    account_index = now.hour - START_HOUR
    if account_index < 0 or account_index >= len(entries):
        return None
    return WarmupSlot(
        name=f"warmup_{now.hour:02d}",
        hour=now.hour,
        account_index=account_index,
    )
```

With `START_HOUR = 9`:

- account #1 warms at 09:00 Morocco → reset around 14:00
- account #2 warms at 10:00 Morocco → reset around 15:00
- account #3 warms at 11:00 Morocco → reset around 16:00
- account #4 warms at 12:00 Morocco → reset around 17:00
- account #5 warms at 13:00 Morocco → reset around 18:00
- account #6 warms at 14:00 Morocco → reset around 19:00

If the desired doctrine changes so account #5 warms at 14:00 and account #6 at 15:00, set `START_HOUR = 10` and document the change clearly.

## Pitfall: gateway-hosted cron has no catch-up

On Ayman's setup the gateway process hosts the cron ticker. If `hermes-gateway.service` is stopped during warmup windows, those slots are missed; when the gateway resumes later, the script exits silently if the current hour has no slot. Do not report "all accounts warmed" just because the cron job has recent silent `ok` runs. Verify actual output files and the state file for today's slot keys.

## Verification checklist

1. Confirm usable account count without printing tokens:
   - read `credential_pool.openai-codex` labels/id prefixes only
   - count only entries with access tokens
2. Inspect today's output under `~/.hermes/cron/output/<job_id>/`.
3. Inspect `~/.hermes/state/codex_quota_warmup_state.json` for `warmup_HH_date == today` per slot.
4. Check gateway logs for `Cron ticker stopped/started` around the warmup windows.
5. Dry-test slot math by injecting Morocco datetimes for each account hour and one outside hour.

## Safety

- Never print access tokens, refresh tokens, cookies, raw headers, or full credential IDs.
- Script stdout should include only label plus short id prefix.
- Changing warmup schedule is a live automation edit; ask Ayman before patching the script or cron job.
