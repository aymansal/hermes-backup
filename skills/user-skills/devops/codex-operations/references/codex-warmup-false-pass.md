# Codex warm-up false PASS pitfall

## Trigger

Use this reference when the Codex quota warm-up cron claims a staggered slot succeeded, but the user's live ChatGPT/Codex quota page shows only the first account reset as expected while later accounts did not move to their intended reset windows.

## What happened

A cron script can mark account #2/#3 warm-up slots as done because the warm-up subprocess returned `OK`, while the actual Codex reset windows still do not match the intended stagger. This is a false PASS.

Observed diagnostic shape:

- Warm-up state file records `warmup_09`, `warmup_10`, and `warmup_11` as done for the day.
- Live `/usage` can still show resets that do not align with the planned formation:
  - #1 should reset around 14:00 Morocco after 09:00 warm-up.
  - #2 should reset around 15:00 Morocco after 10:00 warm-up.
  - #3 should reset around 16:00 Morocco after 11:00 warm-up.
- The script may have used `AIAgent(..., credential_pool=isolated_pool)` and assumed that the call used the target account. That assumption is false in this Hermes path: `AIAgent` Codex client construction can reload/select from the normal `openai-codex` credential pool instead of honoring the injected isolated pool, causing account #2/#3 slots to make the actual warm-up request with account #1 while still printing `OK`.
- Read-only probe from the May 2026 incident showed the exact false-pass shape: target #1 initialized with #1, but target #2 and target #3 both still initialized with #1's runtime key. In other words, isolated pool selection recorded the intended target while the actual Codex client path reloaded/selected from the normal pool.

## Durable lesson

For Codex quota warm-up, success must mean: **a direct call used the intended account and the same account's live `/usage` confirms the expected reset window.**

Do not treat these as proof by themselves:

- A subprocess printed `OK`.
- Hermes `AIAgent` was passed an isolated credential pool.
- The quota cache refreshed successfully.
- The state file says the slot is done.

## Safer implementation pattern

1. Select account #N from `credential_pool.openai-codex` in `auth.json` without printing secrets.
2. Use that entry's access token directly for a tiny Codex Responses API warm-up call. Do not route the warm-up through `AIAgent` unless you have a fresh probe proving the initialized client key matches the intended credential id.
3. Immediately fetch live `/usage` for the same credential id.
4. Verify the primary 5h reset is within the expected slot window:
   - 09:00 warm-up -> around 14:00 Morocco.
   - 10:00 warm-up -> around 15:00 Morocco.
   - 11:00 warm-up -> around 16:00 Morocco.
   - 12:00 warm-up -> around 17:00 Morocco, only if a fourth account exists.
5. Only write `warmup_<hour>_date` to the state file after verification passes.
6. If verification fails, return non-zero and print a sanitized alert with account label/id prefix, observed reset, and expected reset range.

## Read-only verification checklist

Before changing code, inspect sanitized state and live usage:

- Cron job exists and runs the expected script.
- State file records which slots were marked done.
- Credential pool order and labels match the user's intended account order.
- Live `/usage` is fetched per explicit credential id, not just the globally selected account.
- Reset windows are compared against expected Morocco-time windows.

## User handling note

If the user reports this after a previous "fix," do not reassure them from state-file success. Acknowledge that the earlier proof was insufficient, inspect live quota per account, and call the old result a false PASS if the reset windows do not match.