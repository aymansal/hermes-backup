# Codex quota staggered warmup formation — May 2026

## Current formation

Ayman changed the quota warmup strategy from all-account simultaneous warmup to one account per hour in Morocco time:

- 09:00 → account #1 → expected reset around 14:00
- 10:00 → account #2 → expected reset around 15:00
- 11:00 → account #3 → expected reset around 16:00
- 12:00 → account #4 → expected reset around 17:00

Reason: warming all four accounts at the same time overlaps all four 5h quota windows, wasting quota if real work begins later. Staggering creates a rolling reset formation.

## Active script

Path: `~/.hermes/scripts/codex_quota_warmup.py`

Important behavior:

- `STAGGERED_SLOTS = {9: 0, 10: 1, 11: 2, 12: 3}`
- Cron still runs every 10 minutes, but the script stays silent outside the first 20 minutes of each slot.
- Each slot warms exactly one account with one tiny generation call, then fetches live `/usage` for that account.
- State keys are per-slot: `warmup_09_date`, `warmup_10_date`, `warmup_11_date`, `warmup_12_date`.
- Old aggregate keys such as `warmup_date` are harmless and must not block the new staggered slots.

## Verified mapping on 2026-05-24

Safe dry check reported:

```text
usable_accounts: 4
09:00 -> account #1 Tiktok/733df7 -> expected reset ~14:00
10:00 -> account #2 Swayam/2b206b -> expected reset ~15:00
11:00 -> account #3 Iyaaz/7b3aa2 -> expected reset ~16:00
12:00 -> account #4 Isrow/adfb14 -> expected reset ~17:00
```

## Tests

Focused verification command:

```bash
python3 -m py_compile /home/ubuntu/.hermes/scripts/codex_quota_warmup.py
python -m pytest tests/scripts/test_codex_quota_warmup_helpers.py -q -o 'addopts='
```

Result on 2026-05-24:

```text
6 passed
```

## Safety

Do not run live warmup manually without Ayman's approval: it consumes a small amount of Codex quota. Dry checks should import the script and inspect `_slot`, `_codex_entries`, and `_entry_for_slot` only.
