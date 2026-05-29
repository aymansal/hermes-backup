# Codex quota cron reliability hardening — May 2026

## Trigger

Ayman was concerned the quota cron would fail like the previous two days. The reliability problem was not the stagger schedule itself; it was that child process timeouts could approach or exceed Hermes cron's hard run interrupt.

## Durable lesson

Scheduled no-agent scripts should keep their own child-process timeout budget comfortably below the scheduler hard limit, so they can print a useful failure report and return non-zero before cron kills them.

## Applied pattern

For `~/.hermes/scripts/codex_quota_warmup.py`:

- Hermes cron runs every 10 minutes.
- Each slot is open for 20 minutes.
- A failed slot must not mark `warmup_HH_date` complete.
- Returning non-zero lets the next tick retry within the same slot.
- Warmup child timeout: about 105 seconds.
- Quota refresh child timeout: about 35 seconds.
- Maximum expected child time: about 140 seconds, leaving margin below the cron hard limit.
- If warmup fails, skip quota refresh and print `quota refresh skipped because warmup failed` to preserve time.

## Verification used

```bash
python3 -m py_compile /home/ubuntu/.hermes/scripts/codex_quota_warmup.py
python -m pytest tests/scripts/test_codex_quota_warmup_helpers.py -q -o 'addopts='
```

Dry import check confirmed the stagger mapping without spending quota:

```text
09:00 -> account #1 -> reset ~14:00
10:00 -> account #2 -> reset ~15:00
11:00 -> account #3 -> reset ~16:00
12:00 -> account #4 -> reset ~17:00
```

## Safety

Do not manually run live warmup/generation without approval because it spends a small amount of Codex quota. Dry checks may inspect slot mapping and account prefixes only.
