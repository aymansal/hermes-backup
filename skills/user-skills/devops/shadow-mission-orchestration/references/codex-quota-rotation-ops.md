# Codex Quota Rotation Ops Doctrine

Use this reference when designing, fixing, reviewing, or activating Hermes Codex/ChatGPT multi-account quota rotation in the Shadow Realm/dashboard/gateway path.

## Core model

- Dashboard-selected account and backend runtime account must share one source of truth. No hidden backend-only switch that leaves the Shadow Realm showing a different selected account.
- Rotation is allowed only after fresh, trusted quota/account health evidence.
- Conservative fallback is preferred: if evidence is stale, missing, auth-broken, or ambiguous, do not rotate blindly.
- Account labels/short IDs are acceptable in summaries; never expose tokens, cookies, OAuth payloads, or refresh/access secrets.

## Health gates vs ranking

Treat account eligibility as two stages:

1. **Hard health gates** — an account is not healthy for proactive switching if:
   - authentication is broken or credential refresh fails;
   - live quota fetch fails and there is no trusted fresh cache;
   - cached quota is older than the configured max age;
   - weekly/secondary quota is explicitly depleted;
   - runtime pool status marks the credential unavailable for real model calls.

2. **Ranking among healthy accounts** — use the primary/5-hour bucket to choose the best candidate:
   - rotate away below threshold (Ayman default: 5%);
   - prefer the account whose 5h reset window ends soonest when it still has usable quota;
   - keep the current/selected account when it remains above threshold and weekly-healthy.

Weekly quota is a gate, not the ranking window. The 5h bucket ranks only accounts that pass weekly/auth/freshness gates.

## Required cases to cover in tests

- 5h low + weekly healthy → rotate to another weekly-healthy account with usable 5h quota.
- 5h healthy + weekly depleted → do not switch into that account; treat it as unavailable for proactive rotation.
- all accounts weekly depleted → do not rotate blindly; keep selected/current if possible and surface conservative reason/metadata.
- weekly healthy + 5h depleted → rotate away if another weekly-healthy account has usable 5h quota; otherwise keep/fallback conservatively.
- depleted/cooldown but authenticated selected account → dashboard quota display may still attempt live `/usage` refresh; runtime model calls must still respect exhaustion/cooldown.
- auth-broken selected account → dashboard should show live fetch/auth failure and cached/stale state if available; no quota fix can make broken auth usable.

## Activation sequence

1. Read-only scan: config, credential pool/account state, existing cron jobs, dashboard/gateway service status, and current Kanban board state.
2. Implement with a coding worker (`deepseek-v4-flash` by Ayman default).
3. GPT-5.5 review checks only worker output/diff/tests, not a full redo.
4. If review BLOCKED, route a fix card back to the same worker/profile with exact failures.
5. Activate config/cron only after Ayman approves.
6. Restart dashboard/gateway only after separate explicit approval; Ayman requires separate confirmation for Telegram gateway restart.
7. Verify end-to-end after restart: selected account sync, quota display, auth-broken/depleted messaging, cron job visibility in default/runtime profile, and runtime logs.

## Unused-account quota refresh cadence

Ayman wants unused/non-selected Codex accounts to stay reasonably fresh without hammering Codex usage endpoints.

- Unused/non-selected accounts should live-refresh quota only when their last live fetch attempt is missing or at least 30 minutes old.
- Failed live fetch attempts count for the 30-minute backoff so broken-auth accounts do not spin constantly.
- Selected account behavior remains responsive: selecting an account should still attempt the appropriate live quota refresh and must not be suppressed merely because it was previously unused.
- Runtime model calls must still respect credential exhaustion/cooldown/auth status; dashboard quota refresh is metadata observation, not proof the credential is usable.
- If implemented as config, default the interval to 1800 seconds and keep it sanitized/no-secret in dashboard/API payloads.

Required tests:

- unused account with no previous fetch is refreshed;
- unused account is not fetched again before 30 minutes;
- unused account is fetched after 30+ minutes;
- selected account still refreshes appropriately;
- failed unused-account fetch backs off for 30 minutes;
- no secrets are exposed in account/quota payloads.

## Warmup timer pattern

- Use `Africa/Casablanca` timezone logic, not a hardcoded GMT offset.
- A cron schedule can run every few minutes in UTC while a script silently checks Morocco local time and acts only once per intended window.
- Around 09:00 local: tiny warmup Codex call to open the 5h quota window, then refresh quota metadata.
- Around 14:00 local: refresh quota metadata.
- Empty stdout means silent no-op; non-empty stdout reports actual action or failure.

## Reporting expectations

For quota rotation raids, report phase changes immediately:

- worker started/completed;
- review started/passed/failed;
- activation/config written;
- cron created/verified;
- restart approval needed;
- any provider auth failure or stale quota state discovered.

Do not wait for Ayman to ask when a review passes or a decision gate opens.