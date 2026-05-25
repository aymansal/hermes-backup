---
name: hermes-dashboard-development
description: "Use when modifying or debugging the Hermes native web dashboard: FastAPI API routes, React pages, web_dist builds, dashboard systemd restarts, and provider/account status cards."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [hermes-agent, dashboard, fastapi, react, typescript, provider-status]
    related_skills: [debugging-hermes-tui-commands, systematic-debugging]
---

# Hermes Dashboard Development

## Overview

Use this Skill Rune when changing the native Hermes web dashboard, the Shadow Realm: React pages under `web/src`, API routes in `hermes_cli/web_server.py`, dashboard static builds in `hermes_cli/web_dist`, and dashboard-only status panels such as model/provider/account cards.

The dashboard is a two-gate system:

1. Backend Gate: FastAPI routes in `hermes_cli/web_server.py`.
2. Frontend Gate: React/TypeScript in `web/src`, compiled into `hermes_cli/web_dist` by `npm run build`.

A backend-only patch is not visible in the browser if the frontend bundle was not rebuilt. A frontend-only patch cannot read data unless the endpoint is available and passes dashboard auth middleware.

## When to Use

- Adding a card, panel, or status readout to a dashboard page such as Models, Config, Sessions, Logs, or Chat.
- Adding a read-only `/api/...` endpoint for dashboard UI consumption.
- Debugging dashboard browser errors, 401/403 API responses, stale bundles, or React build failures.
- Surfacing provider status metadata such as OAuth login state, cached quota, model selection, or active provider/account state.
- Restarting only the dashboard service after a dashboard patch.

For embedded Chat/WebSocket failures (`[session ended]`, `/api/pty`, `/api/events`), use `debugging-hermes-tui-commands` first, then return here for normal dashboard API/UI development.

## Read-Only First

Before changing code, inspect the route and page shape:

```bash
# Backend route discovery
python -m py_compile hermes_cli/web_server.py

# Search exact route/page names with Hermes file tools, not blind shell grep.
# Typical files:
#   hermes_cli/web_server.py
#   web/src/lib/api.ts
#   web/src/pages/<PageName>.tsx
```

Check whether the dashboard is served from a built bundle:

```bash
systemctl --user --no-pager --full status hermes-dashboard
ss -ltnp | grep ':9119'
```

## Backend Pattern: Safe Read-Only API Route

For dashboard display data, prefer a small sanitized endpoint:

```python
@app.get("/api/model/quota")
def get_model_quota():
    """Return sanitized cached provider/account quota for dashboard display."""
    try:
        # Load config/state, return only non-secret fields.
        return {"available": True, "buckets": []}
    except Exception:
        _log.exception("GET /api/model/quota failed")
        return {"available": False, "buckets": []}
```

Rules:

- Never return Access Keys, bearer tokens, refresh tokens, cookies, private URLs, or raw auth headers.
- Return derived/sanitized values only: booleans, percentages, timestamps, labels, model/provider names.
- If the SPA must call the endpoint without an injected session header, add the route to `_PUBLIC_API_PATHS` only if it is truly read-only and non-sensitive.
- If the endpoint exposes sensitive config or secrets, keep it behind the session token and call it with the session header from `web/src/lib/api.ts`.

## Frontend Pattern: API Type + Page Card

1. Add a typed API helper in `web/src/lib/api.ts`:

```ts
getModelQuota: () => fetchJSON<ModelQuotaResponse>("/api/model/quota"),
```

2. Add response interfaces near related model/provider types.
3. In the page component:
   - Add `useState<ModelQuotaResponse | null>(null)`.
   - Load it with other page data via `Promise.all([...]).catch(() => null)` so quota failure does not break the whole page.
   - Render a small card that handles all states: unavailable, cached-but-inactive, active, and stale.

## Provider Quota / Account Status Pattern

For requests that reuse Shadow Realm quota outside the dashboard (for example, Telegram reply footers), see `references/dashboard-quota-gateway-footer.md`. The key rule is: reuse the sanitized quota helper/endpoints already built for the dashboard; do not invent a parallel quota scraper or expose auth state.

Prefer the provider's explicit read-only usage endpoint when one exists. For OpenAI Codex / ChatGPT accounts, the authoritative live source is:

```text
GET https://chatgpt.com/backend-api/codex/usage?client_version=1.0.0
```

That endpoint returns the current account quota without generating a model response. Parse and return only sanitized fields:

- `plan_type`
- `rate_limit.primary_window.used_percent`, `reset_at`, `reset_after_seconds`, `limit_window_seconds`
- `rate_limit.secondary_window.used_percent`, `reset_at`, `reset_after_seconds`, `limit_window_seconds`
- safe booleans such as `allowed`, `limit_reached`, `credits.has_credits`, `credits.unlimited`

Do **not** return PII from the usage payload such as `user_id`, `account_id`, or `email`.

Codex response headers can still be used as a fallback/cache source after normal provider calls:

- `x-codex-primary-window-minutes`
- `x-codex-primary-used-percent`
- `x-codex-primary-reset-at`
- `x-codex-primary-reset-after-seconds`
- `x-codex-secondary-window-minutes`
- `x-codex-secondary-used-percent`
- `x-codex-secondary-reset-at`
- `x-codex-plan-type`
- `x-codex-active-limit`

Implementation pattern:

1. Add a helper such as `fetch_live_codex_quota()` that resolves/refreshes Codex OAuth credentials, calls `/usage`, parses only safe quota fields, and stores the sanitized result in provider state as `last_quota`.
2. Keep `save_codex_quota_from_headers()` as a best-effort fallback after successful Codex model calls.
3. Expose quota via a read-only dashboard endpoint such as `/api/model/quota`; if live fetch fails, return cached sanitized quota with a `live_fetch_failed` flag instead of breaking the page.
4. Render progress bars from the live/cached data on the Models page.
5. If the user asks for live monitoring, poll the dashboard endpoint from the frontend with `window.setInterval(..., 5000)` and failure-isolate it so Models analytics still load.

See `references/codex-chatgpt-quota-dashboard.md` for the concrete endpoint shape and session recipe.

If the same quota must appear in messaging-platform reply footers, reuse the sanitized helper instead of creating a second provider path. See `references/codex-quota-gateway-footer.md` for the gateway runtime-footer pattern, including Telegram quota-only footers with reset times.

When reporting Codex quota to Ayman in chat, convert provider UTC reset timestamps to Morocco local time / UTC+1 first. The `/usage` endpoint and sanitized quota helpers expose reset times as UTC-oriented timestamps; user-facing Telegram summaries should not dump raw UTC unless explicitly requested. Label the timezone clearly, e.g. `2026-05-22 22:44:12 UTC+1`, and keep UTC only as a secondary diagnostic value.

For OpenAI Codex / ChatGPT multi-account dashboards, account selection is not just a quota-view filter. The selected account should write `model.provider=openai-codex` plus `model.credential_id=<credential_id>` so all new Hermes runtime paths that call `resolve_runtime_provider()` use that account. Render accounts as card-like UI, not a dropdown or flat row list, and state clearly that existing live sessions may need `/reset`, a new session, or process restart because API keys can already be resolved in memory. For Ayman's preferred Shadow Realm UX, account cards should be compact and clickable directly; avoid redundant “Use for Hermes chat” buttons, and merge duplicated active Codex model-card metadata into the selected account card when practical. Implementation notes and test targets live in `references/codex-account-cards-global-selection.md`.

For Codex quota rotation across multiple ChatGPT accounts, the account with the closest primary reset time should beat an account with more remaining quota once both accounts are usable, but only if that reset is far enough away to be useful. Ayman's global rule is: exclude candidates whose selected quota window resets in less than `codex_quota_rotation.min_reset_lead_seconds` (default 3600 seconds / 1 hour), then choose the nearest reset among the remaining usable accounts. This rule must apply globally: proactive runtime selection, reactive 429/402 failover, dashboard `/api/model/codex/accounts` metadata, dashboard fallback selection, and account-removal fallback. Do not keep the currently selected account merely because it is above threshold when another healthy above-threshold account resets earlier and passes the lead-time gate. If runtime quota rotation switches accounts and `codex_quota_rotation.persist_runtime_switch` is enabled, persist the new `model.credential_id` so the Shadow Realm selected card matches the actual runtime account. Frontend polling should refresh both `/api/model/quota` and `/api/model/codex/accounts`; polling quota alone can leave account-card selection stale after automatic switches. Detailed ranking, lead-time, and verification notes live in `references/codex-quota-earliest-reset-selection.md`.

When adding dashboard-managed Codex accounts, never generate display labels from `len(pool.entries()) + 1`. Deleting a middle account makes length-based labels collide (`Gpt1`, `Gpt2`, `Gpt4` -> new `Gpt4`). Allocate the lowest unused `GptN` slot, or persist a monotonic counter if product policy requires never reusing labels. See `references/codex-dashboard-account-labeling.md` for the concrete bug, helper pattern, and regression tests.

## Build and Verification

Always run both backend and frontend checks after dashboard changes:

```bash
/home/ubuntu/.hermes/hermes-agent/venv/bin/python -m py_compile \
  /home/ubuntu/.hermes/hermes-agent/hermes_cli/web_server.py \
  /home/ubuntu/.hermes/hermes-agent/run_agent.py

cd /home/ubuntu/.hermes/hermes-agent/web && npm run build
```

If a new helper file was added, include it in `py_compile` too.

Then restart only the dashboard service unless the change affects a different daemon:

```bash
systemctl --user restart hermes-dashboard
sleep 2
systemctl --user --no-pager --full status hermes-dashboard | sed -n '1,18p'
```

Probe the endpoint from the live bind address. If the endpoint returns `401`, check `_PUBLIC_API_PATHS` or frontend session-token header usage before assuming the route is broken.

## Common Pitfalls

0. **Codex quota works in the model path but not in dashboard/footer after account switch.** ChatGPT/Codex account switches may store OAuth credentials in `credential_pool.openai-codex[0]` while older quota helpers look only under `providers.openai-codex.tokens`. If `/api/model/quota` says `logged_in=false` / `No Codex credentials stored` but sanitized auth inspection shows credential-pool tokens present, patch the quota resolver to accept both storage shapes. See `references/codex-quota-credential-pool-mismatch.md` for the safe diagnostic and fix path.

0a. **Duplicate Codex account labels after deletion.** Dashboard-managed Codex labels must not be based on pool length. If the user reports `Gpt4` appearing twice after deleting `Gpt3`, inspect the dashboard device-code login code for `label=f"Gpt{len(pool.entries()) + 1}"` and replace it with a helper that scans existing `GptN` labels and chooses the lowest unused slot. See `references/codex-dashboard-account-labeling.md`.

1. **Forgetting the frontend build.** Editing `web/src/...` does not change what the dashboard serves until `npm run build` updates `hermes_cli/web_dist`.

2. **Route works internally but browser gets 401.** Dashboard API middleware gates `/api/*` by default. Add only safe read-only endpoints to `_PUBLIC_API_PATHS`, or call with `X-Hermes-Session-Token` via `fetchJSON` when appropriate.

3. **Leaking secrets through “helpful” status endpoints.** Provider state often contains tokens. Never return whole provider state. Construct a new sanitized dict.

4. **Breaking the page because optional status failed.** Quota/status cards must fail soft with `.catch(() => null)` and render an unavailable message. Do not block main Models analytics.

5. **Confusing local analytics with provider quotas.** Local token/cost analytics are not provider quota. Provider quota should come from provider-specific headers/API responses and be labeled as cached/provider-reported.

6. **Restarting unrelated Shadows.** For dashboard-only API/UI patches, restart `hermes-dashboard` only. Do not disrupt gateway, Telegram, memory, or model services unless the code path requires it.

## Verification Checklist

- [ ] Backend route returns sanitized JSON only.
- [ ] Frontend `api.ts` has typed helper and response interface.
- [ ] Page loads optional status with failure isolation.
- [ ] `py_compile` passes for changed Python files.
- [ ] `npm run build` passes for dashboard web bundle.
- [ ] `hermes-dashboard` restarts and is active/running.
- [ ] Live endpoint probe returns expected JSON.
- [ ] Browser hard refresh shows the new card/panel.
