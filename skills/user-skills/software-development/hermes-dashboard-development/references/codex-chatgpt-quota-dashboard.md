# Codex / ChatGPT quota card on Hermes Models page

## Trigger

User wanted the Shadow Realm Models page to show active ChatGPT/Codex account quota like:

```text
5h      ██████████████████░░    90%   20:24
Weekly  ████████████████████    98%   25 May
```

The first implementation used response headers from normal Codex model calls. The user later reported the reading was wrong and requested live refresh every 5 seconds.

## Durable finding

The better live source for OpenAI Codex / ChatGPT quota is the read-only Codex usage endpoint:

```text
GET https://chatgpt.com/backend-api/codex/usage?client_version=1.0.0
```

It returns current account quota without generating a model response. It may include PII such as `user_id`, `account_id`, and `email`; never return those fields to the dashboard or logs.

Useful sanitized fields observed:

```json
{
  "plan_type": "plus",
  "rate_limit": {
    "allowed": true,
    "limit_reached": false,
    "primary_window": {
      "used_percent": 85,
      "limit_window_seconds": 18000,
      "reset_after_seconds": 15533,
      "reset_at": 1779402187
    },
    "secondary_window": {
      "used_percent": 41,
      "limit_window_seconds": 604800,
      "reset_after_seconds": 500169,
      "reset_at": 1779886822
    }
  },
  "credits": {
    "has_credits": false,
    "unlimited": false
  }
}
```

Map:

- `rate_limit.primary_window` → `5h`
- `rate_limit.secondary_window` → `Weekly`
- `limit_window_seconds / 60` → `window_minutes`

Codex response headers remain useful as fallback/cache data after normal model calls:

```text
x-codex-active-limit: premium
x-codex-plan-type: plus
x-codex-credits-unlimited: False
x-codex-credits-has-credits: False
x-codex-primary-window-minutes: 300
x-codex-primary-used-percent: <int>
x-codex-primary-reset-at: <unix-seconds>
x-codex-primary-reset-after-seconds: <int>
x-codex-secondary-window-minutes: 10080
x-codex-secondary-used-percent: <int>
x-codex-secondary-reset-at: <unix-seconds>
x-codex-secondary-reset-after-seconds: <int>
```

## Safe implementation pattern

1. Add/extend `agent/codex_quota.py`:
   - `parse_codex_usage_payload(payload)` parses `/usage` JSON and ignores PII.
   - `fetch_live_codex_quota(timeout_seconds=...)` resolves Codex credentials, refreshes if expiring, calls `/usage`, parses safe fields, and stores sanitized data as provider state `last_quota`.
   - `parse_codex_quota_headers(headers)` and `save_codex_quota_from_headers(headers)` remain best-effort fallback.
   - Clamp `used_percent` to `[0, 100]`.
   - Store/return only provider, source, captured timestamp, plan, safe booleans, and buckets.

2. Use normal Codex auth helpers:

```python
from hermes_cli.auth import resolve_codex_runtime_credentials
from agent.auxiliary_client import _codex_cloudflare_headers
from agent.model_metadata import _resolve_requests_verify

creds = resolve_codex_runtime_credentials(refresh_if_expiring=True)
access_token = str(creds.get("api_key") or "").strip()
headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json",
    **_codex_cloudflare_headers(access_token),
}
```

Do not print the token, raw auth state, or raw response body.

3. Expose a dashboard endpoint in `hermes_cli/web_server.py`:

```python
@app.get("/api/model/quota")
def get_model_quota():
    from agent.codex_quota import fetch_live_codex_quota
    quota = fetch_live_codex_quota(timeout_seconds=8.0)
    quota["active_provider"] = active_provider
    quota["active_model"] = active_model
    quota["is_active"] = active_provider in {"openai-codex", "codex", "openai_codex"}
    return quota
```

4. If the endpoint returns only sanitized read-only data, add it to `_PUBLIC_API_PATHS`:

```python
"/api/model/quota",
```

Without this, direct dashboard fetches may get `401 Unauthorized` even though the route works.

5. Add frontend API type/helper in `web/src/lib/api.ts`:

```ts
getModelQuota: () => fetchJSON<ModelQuotaResponse>("/api/model/quota"),
```

6. Render a `ChatGPTQuotaCard` on `web/src/pages/ModelsPage.tsx`:
   - Load quota with `.catch(() => null)` in the existing `Promise.all`.
   - Display rows for buckets with label, bar, percent, and reset time/date.
   - Show an unavailable message when logged in but no quota exists.
   - Label source accurately: `usage_endpoint` vs `response_headers`.

7. For live monitoring every 5 seconds, add a dedicated polling effect:

```ts
useEffect(() => {
  let cancelled = false;
  const refreshQuota = () => {
    api.getModelQuota()
      .then((quotaData) => {
        if (!cancelled) setQuota(quotaData);
      })
      .catch(() => {});
  };
  refreshQuota();
  const timer = window.setInterval(refreshQuota, 5000);
  return () => {
    cancelled = true;
    window.clearInterval(timer);
  };
}, []);
```

Failure-isolate this polling so quota failures do not break the Models analytics page.

## Verification commands

```bash
/home/ubuntu/.hermes/hermes-agent/venv/bin/python -m py_compile \
  /home/ubuntu/.hermes/hermes-agent/agent/codex_quota.py \
  /home/ubuntu/.hermes/hermes-agent/hermes_cli/web_server.py

cd /home/ubuntu/.hermes/hermes-agent/web && npm run build

systemctl --user restart hermes-dashboard
sleep 2
systemctl --user --no-pager --full status hermes-dashboard | sed -n '1,18p'
```

Probe `/api/model/quota` and confirm:

```text
source usage_endpoint
provider openai-codex
available True
logged_in True
bucket_count 2
5h <percent> <remaining>
Weekly <percent> <remaining>
live_fetch_failed null
```

If the endpoint returns `401`, add the safe read-only route to `_PUBLIC_API_PATHS` or use session-token headers from the frontend.
