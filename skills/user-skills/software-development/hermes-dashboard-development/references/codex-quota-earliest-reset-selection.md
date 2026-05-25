# Codex quota rotation: earliest-reset account selection

## Trigger

Use this reference when debugging or modifying OpenAI Codex / ChatGPT multi-account quota rotation in Hermes, especially when the dashboard selected card does not match runtime account switching or quota is consumed from the wrong account.

## Durable lesson

For Ayman's Codex account pool, the desired proactive selection rule is not "use the account with the most quota remaining." It is:

> Among usable accounts whose selected quota window is still useful for at least one hour, use the account whose active quota window resets soonest.

The one-hour lead-time gate matters because an account resetting in 10–15 minutes may not provide enough time to consume its quota effectively. Exclude those too-soon reset candidates first, then burn quota from the eligible bucket that will refresh first. The lead-time threshold should be configurable as `codex_quota_rotation.min_reset_lead_seconds`, defaulting to `3600`.

## Correct ranking shape

For cached/live sanitized quota rows, rank candidates roughly as:

1. Account is available / not in cooldown.
2. Weekly / secondary quota is healthy when explicitly reported.
3. Primary quota is above the configured threshold.
4. Primary reset lead time is at least `codex_quota_rotation.min_reset_lead_seconds` (default 3600 seconds).
5. Primary reset time is earliest (`reset_at` / `reset_after_seconds`) among lead-time-eligible candidates.
6. Remaining primary percentage is a tie-breaker, not the main criterion.
7. Stable priority / index tie-breakers last.

Do not keep the currently selected account merely because it is still above threshold if another usable account resets sooner. The current account is only a tie-breaker or conservative fallback when no usable reset-aware candidate exists.

## Dashboard/runtime consistency

When runtime quota rotation chooses a different Codex account and `codex_quota_rotation.persist_runtime_switch` is enabled, persist the selected credential id back to config (`model.credential_id`) using the sanitized helper. Otherwise the Shadow Realm reads stale config and highlights the wrong account.

Frontend polling must refresh both:

- `/api/model/quota` for the selected account quota payload.
- `/api/model/codex/accounts` for selected-card state.

If only quota is polled, account cards can remain visually stale after an automatic runtime switch.

## Implementation recipe

Patch the rotation and dashboard in three layers, then verify each layer:

1. `agent/codex_quota.py`
   - In `rank_codex_accounts_by_quota`, make `reset_rank` sort before remaining quota for usable above-threshold accounts.
   - Keep remaining percentage as a tie-breaker only.
   - In `choose_codex_quota_candidate`, let the top usable ranked account win even when the current account is healthy; return a distinct reason such as `rotated_to_earliest_reset` for this case.
2. `hermes_cli/runtime_provider.py`
   - After `pool.select_codex_by_quota(...)`, if the selected entry id differs from `model.credential_id` and `persist_runtime_switch` is enabled, call `persist_selected_codex_credential_id(..., reason="proactive_runtime_rotation")`.
   - Treat persistence failure as non-fatal but log at debug level; runtime credential resolution should still return the chosen entry.
3. `web/src/pages/ModelsPage.tsx`
   - Poll quota and account-list endpoints together so selected-card state tracks persisted automatic switches.
   - Keep both calls failure-isolated with `.catch(() => null)` so Models analytics still render.
4. `agent/credential_pool.py`
   - Patch reactive `mark_exhausted_and_rotate()` for `openai-codex` so live 429/402 failover uses the same quota-aware chooser after marking the failed account exhausted.
   - Avoid deadlock: this method already holds `self._lock`, so do not call public methods that reacquire the same non-reentrant lock. Use an unlocked helper path or call the pure chooser with already-available entries.
   - In strict reactive mode, do not fall back to generic pool order when quota-aware rotation is enabled but every candidate is ineligible due to stale quota, weekly depletion, low remaining quota, or too-short reset lead time.
5. `hermes_cli/web_server.py`
   - `/api/model/codex/accounts` should attach global rotation metadata such as `rotation_eligible`, `auto_candidate`, `reset_lead_seconds`, `reset_lead_eligible`, `quota_rank`, `weekly_healthy`, and `stale_quota`.
   - If no account is selected, dashboard fallback selection should prefer `auto_candidate` before `accounts[0]`.
   - If deleting the selected account, choose the next selected account using the same global auto-candidate rule, not list order.

## Verification targets

- Unit tests for `rank_codex_accounts_by_quota` / `choose_codex_quota_candidate` should include:
  - Two above-threshold accounts where the lower-remaining account resets sooner; earliest reset wins.
  - Current account above threshold but later reset; another usable account with earlier reset wins.
  - An otherwise healthy account resetting too soon (for example 15 minutes) is excluded when `min_reset_lead_seconds=3600`.
  - Strict reactive selection returns no candidate instead of falling back to list order when only too-soon candidates exist.
  - Reactive `CredentialPool.mark_exhausted_and_rotate()` chooses the quota-aware eligible account after a 429/402, not generic pool priority.
  - Weekly-depleted accounts never beat weekly-healthy accounts.
  - Unknown/stale quota remains conservative fallback behavior.
- Runtime provider tests should confirm a quota-selected Codex entry can persist `model.credential_id` when `persist_runtime_switch` is true.
- Dashboard API tests should confirm `/api/model/codex/accounts` exposes non-secret rotation metadata and marks the global `auto_candidate` using the same one-hour lead-time gate.
- Dashboard UI tests or manual browser verification should confirm the selected account card changes after automatic/persisted selection.

## Live dashboard verification pitfall

The dashboard root route may reject `HEAD` with HTTP 405 while serving `GET` correctly. For service health after a dashboard restart, prefer a GET probe such as `curl -fsS -o /dev/null -w '%{http_code}\n' http://<dashboard-host>:<port>/`. Direct calls to protected `/api/...` routes can return 401 without indicating a broken route; use authenticated frontend fetches or check `_PUBLIC_API_PATHS` before treating that as a regression.
