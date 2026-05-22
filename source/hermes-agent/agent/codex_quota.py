"""OpenAI Codex / ChatGPT account quota helpers.

The Codex ChatGPT backend exposes account-window usage from two places:
response headers on normal Responses calls and the non-generating ``/usage``
endpoint.  This module parses both shapes and stores only sanitized quota data
in Hermes auth state so dashboard pages can display quota without exposing
OAuth tokens, user ids, emails, or raw response payloads.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

import requests

_CODEX_USAGE_URL = "https://chatgpt.com/backend-api/codex/usage?client_version=1.0.0"


def _header(headers: Mapping[str, Any], name: str) -> str:
    lname = name.lower()
    for key, value in headers.items():
        if str(key).lower() == lname:
            return str(value or "").strip()
    return ""


def _int_header(headers: Mapping[str, Any], name: str) -> Optional[int]:
    raw = _header(headers, name)
    if raw == "":
        return None
    try:
        return int(float(raw))
    except (TypeError, ValueError):
        return None


def _clamp_percent(value: Any) -> int:
    try:
        return max(0, min(100, int(round(float(value or 0)))))
    except (TypeError, ValueError):
        return 0


def _bucket_from_values(
    *,
    key: str,
    label: str,
    used_percent: Any = None,
    reset_at: Any = None,
    reset_after_seconds: Any = None,
    window_minutes: Any = None,
    window_seconds: Any = None,
) -> Optional[dict[str, Any]]:
    if (
        used_percent is None
        and reset_at is None
        and reset_after_seconds is None
        and window_minutes is None
        and window_seconds is None
    ):
        return None
    used = _clamp_percent(used_percent)
    if window_minutes is None and window_seconds is not None:
        try:
            window_minutes = int(float(window_seconds) / 60)
        except (TypeError, ValueError):
            window_minutes = None
    return {
        "key": key,
        "label": label,
        "window_minutes": window_minutes,
        "used_percent": used,
        "remaining_percent": max(0, 100 - used),
        "reset_at": reset_at,
        "reset_after_seconds": reset_after_seconds,
    }


def _bucket(headers: Mapping[str, Any], prefix: str, label: str) -> Optional[dict[str, Any]]:
    return _bucket_from_values(
        key=prefix,
        label=label,
        used_percent=_int_header(headers, f"x-codex-{prefix}-used-percent"),
        reset_at=_int_header(headers, f"x-codex-{prefix}-reset-at"),
        reset_after_seconds=_int_header(headers, f"x-codex-{prefix}-reset-after-seconds"),
        window_minutes=_int_header(headers, f"x-codex-{prefix}-window-minutes"),
    )


def parse_codex_usage_payload(payload: Mapping[str, Any]) -> Optional[dict[str, Any]]:
    """Return sanitized quota info from the Codex ``/usage`` JSON payload.

    The endpoint includes PII fields such as user id and email; they are
    intentionally ignored here.  Only account plan, credit flags, and quota
    windows are returned.
    """
    if not isinstance(payload, Mapping):
        return None
    rate_limit = payload.get("rate_limit")
    if not isinstance(rate_limit, Mapping):
        return None

    primary_window = rate_limit.get("primary_window")
    secondary_window = rate_limit.get("secondary_window")
    primary = None
    secondary = None
    if isinstance(primary_window, Mapping):
        primary = _bucket_from_values(
            key="primary",
            label="5h",
            used_percent=primary_window.get("used_percent"),
            reset_at=primary_window.get("reset_at"),
            reset_after_seconds=primary_window.get("reset_after_seconds"),
            window_seconds=primary_window.get("limit_window_seconds"),
        )
    if isinstance(secondary_window, Mapping):
        secondary = _bucket_from_values(
            key="secondary",
            label="Weekly",
            used_percent=secondary_window.get("used_percent"),
            reset_at=secondary_window.get("reset_at"),
            reset_after_seconds=secondary_window.get("reset_after_seconds"),
            window_seconds=secondary_window.get("limit_window_seconds"),
        )
    buckets = [b for b in (primary, secondary) if b]
    if not buckets:
        return None

    credits = payload.get("credits")
    if not isinstance(credits, Mapping):
        credits = {}
    return {
        "provider": "openai-codex",
        "source": "usage_endpoint",
        "captured_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "captured_at_unix": int(time.time()),
        "plan_type": payload.get("plan_type") if isinstance(payload.get("plan_type"), str) else None,
        "active_limit": payload.get("rate_limit_reached_type") if isinstance(payload.get("rate_limit_reached_type"), str) else None,
        "allowed": bool(rate_limit.get("allowed")) if rate_limit.get("allowed") is not None else None,
        "limit_reached": bool(rate_limit.get("limit_reached")) if rate_limit.get("limit_reached") is not None else None,
        "credits_unlimited": bool(credits.get("unlimited")) if credits.get("unlimited") is not None else None,
        "credits_has_credits": bool(credits.get("has_credits")) if credits.get("has_credits") is not None else None,
        "buckets": buckets,
    }


def parse_codex_quota_headers(headers: Mapping[str, Any]) -> Optional[dict[str, Any]]:
    """Return sanitized quota info from Codex response headers, or None."""
    primary = _bucket(headers, "primary", "5h")
    secondary = _bucket(headers, "secondary", "Weekly")
    buckets = [b for b in (primary, secondary) if b]
    if not buckets:
        return None

    plan_type = _header(headers, "x-codex-plan-type") or None
    active_limit = _header(headers, "x-codex-active-limit") or None
    unlimited_raw = _header(headers, "x-codex-credits-unlimited").lower()
    has_credits_raw = _header(headers, "x-codex-credits-has-credits").lower()

    return {
        "provider": "openai-codex",
        "source": "response_headers",
        "captured_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "captured_at_unix": int(time.time()),
        "plan_type": plan_type,
        "active_limit": active_limit,
        "credits_unlimited": unlimited_raw == "true" if unlimited_raw else None,
        "credits_has_credits": has_credits_raw == "true" if has_credits_raw else None,
        "buckets": buckets,
    }


def _selected_codex_credential_id() -> Optional[str]:
    try:
        from hermes_cli.config import load_config

        cfg = load_config()
        model_cfg = cfg.get("model", {}) if isinstance(cfg, dict) else {}
        if isinstance(model_cfg, Mapping):
            selected = str(model_cfg.get("credential_id") or "").strip()
            return selected or None
    except Exception:
        return None
    return None


def _pool_entries() -> list[dict[str, Any]]:
    try:
        from hermes_cli.auth import read_credential_pool

        entries = read_credential_pool("openai-codex")
        return list(entries) if isinstance(entries, list) else []
    except Exception:
        return []


def _pool_entry_payload(credential_id: Optional[str]) -> Optional[dict[str, Any]]:
    target = str(credential_id or "").strip()
    entries = _pool_entries()
    if target:
        for entry in entries:
            if isinstance(entry, dict) and str(entry.get("id") or "") == target:
                return entry
        return None
    for entry in entries:
        if isinstance(entry, dict) and str(entry.get("access_token") or "").strip():
            return entry
    return None


def _account_meta(entry: Optional[Mapping[str, Any]]) -> dict[str, Any]:
    if not isinstance(entry, Mapping):
        return {}
    return {
        "selected_credential_id": entry.get("id"),
        "selected_credential_label": entry.get("label"),
    }


def _save_codex_quota(quota: Mapping[str, Any], credential_id: Optional[str] = None) -> None:
    from hermes_cli.auth import (
        _auth_store_lock,
        _load_auth_store,
        _load_provider_state,
        _save_auth_store,
        _store_provider_state,
    )

    selected_id = str(credential_id or _selected_codex_credential_id() or "").strip()
    with _auth_store_lock():
        auth_store = _load_auth_store()
        if selected_id:
            pool = auth_store.setdefault("credential_pool", {})
            entries = pool.get("openai-codex")
            if isinstance(entries, list):
                for entry in entries:
                    if isinstance(entry, dict) and str(entry.get("id") or "") == selected_id:
                        entry["last_quota"] = dict(quota)
                        _save_auth_store(auth_store)
                        return
        # Legacy/singleton cache fallback for older auth stores.
        state = _load_provider_state(auth_store, "openai-codex") or {}
        state["last_quota"] = dict(quota)
        _store_provider_state(auth_store, "openai-codex", state, set_active=False)
        _save_auth_store(auth_store)


def save_codex_quota_from_headers(headers: Mapping[str, Any], credential_id: Optional[str] = None) -> Optional[dict[str, Any]]:
    """Parse and persist sanitized Codex quota cache into auth.json.

    This never stores bearer tokens or raw response headers.  It only writes the
    public usage-window fields listed in ``parse_codex_quota_headers``.
    """
    quota = parse_codex_quota_headers(headers)
    if not quota:
        return None
    try:
        _save_codex_quota(quota, credential_id=credential_id)
    except Exception:
        # Quota capture is best-effort; never break an agent call over it.
        return quota
    return quota


def _resolve_pool_codex_credentials(credential_id: Optional[str]) -> tuple[str, Optional[dict[str, Any]]]:
    from agent.credential_pool import load_pool
    from hermes_cli.auth import AuthError

    pool = load_pool("openai-codex")
    if pool and pool.has_credentials():
        selected = str(credential_id or "").strip()
        entry = pool.select_by_id(selected) if selected else pool.select()
        if entry is not None:
            token = str(getattr(entry, "runtime_api_key", None) or getattr(entry, "access_token", "") or "").strip()
            if token:
                payload = _pool_entry_payload(entry.id) or {
                    "id": entry.id,
                    "label": entry.label,
                }
                return token, payload
    raise AuthError(
        "No usable OpenAI Codex credential in credential_pool.openai-codex.",
        provider="openai-codex",
        code="codex_pool_credential_missing",
        relogin_required=True,
    )


def fetch_live_codex_quota(timeout_seconds: float = 10.0, credential_id: Optional[str] = None) -> dict[str, Any]:
    """Fetch live sanitized quota from Codex ``/usage`` and cache it.

    This endpoint is a lightweight account-usage read, not a model generation
    call.  If a dashboard-selected pool credential exists, quota is fetched for
    that exact account; otherwise Hermes falls back to the legacy singleton
    Codex auth resolver for compatibility.
    """
    from agent.auxiliary_client import _codex_cloudflare_headers
    from agent.model_metadata import _resolve_requests_verify
    from hermes_cli.auth import AuthError, resolve_codex_runtime_credentials

    selected_id = str(credential_id or _selected_codex_credential_id() or "").strip() or None
    account_entry: Optional[dict[str, Any]] = None
    try:
        try:
            access_token, account_entry = _resolve_pool_codex_credentials(selected_id)
        except Exception:
            if selected_id:
                raise
            creds = resolve_codex_runtime_credentials(refresh_if_expiring=True)
            access_token = str(creds.get("api_key") or "").strip()
        if not access_token:
            raise AuthError(
                "Codex auth is missing access_token. Run `hermes auth` to re-authenticate.",
                provider="openai-codex",
                code="codex_auth_missing_access_token",
                relogin_required=True,
            )
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            **_codex_cloudflare_headers(access_token),
        }
        response = requests.get(
            _CODEX_USAGE_URL,
            headers=headers,
            timeout=max(3.0, float(timeout_seconds)),
            verify=_resolve_requests_verify(),
        )
        if response.status_code == 401 and not selected_id:
            creds = resolve_codex_runtime_credentials(force_refresh=True)
            access_token = str(creds.get("api_key") or "").strip()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
                **_codex_cloudflare_headers(access_token),
            }
            response = requests.get(
                _CODEX_USAGE_URL,
                headers=headers,
                timeout=max(3.0, float(timeout_seconds)),
                verify=_resolve_requests_verify(),
            )
        response.raise_for_status()
        payload = response.json()
        quota = parse_codex_usage_payload(payload)
        if not quota:
            raise RuntimeError("Codex /usage response did not include quota windows")
        _save_codex_quota(quota, credential_id=selected_id)
        return {
            "logged_in": True,
            "available": True,
            **_account_meta(account_entry),
            **quota,
        }
    except Exception as exc:
        cached = load_cached_codex_quota(credential_id=selected_id)
        cached["live_fetch_failed"] = True
        cached["message"] = f"Live Codex quota fetch failed; showing cached quota. {exc}"
        return cached


def load_cached_codex_quota(credential_id: Optional[str] = None) -> dict[str, Any]:
    """Load sanitized cached Codex quota for dashboard display."""
    try:
        selected_id = str(credential_id or _selected_codex_credential_id() or "").strip() or None
        entry = _pool_entry_payload(selected_id)
        if isinstance(entry, Mapping):
            quota = entry.get("last_quota")
            logged_in = bool(str(entry.get("access_token") or "").strip())
            base = {
                "provider": "openai-codex",
                "logged_in": logged_in,
                **_account_meta(entry),
            }
            if isinstance(quota, dict):
                return {**base, "available": True, **quota}
            return {
                **base,
                "available": False,
                "message": "No cached ChatGPT quota yet for this account. Send one OpenAI Codex message or refresh quota.",
                "buckets": [],
            }

        from hermes_cli.auth import _load_auth_store, _load_provider_state

        auth_store = _load_auth_store()
        state = _load_provider_state(auth_store, "openai-codex") or {}
        quota = state.get("last_quota")
        logged_in = bool((state.get("tokens") or {}).get("access_token"))
        if isinstance(quota, dict):
            return {
                "provider": "openai-codex",
                "logged_in": logged_in,
                "available": True,
                **quota,
            }
        return {
            "provider": "openai-codex",
            "logged_in": logged_in,
            "available": False,
            "message": "No cached ChatGPT quota yet. Select or authenticate an OpenAI Codex account.",
            "buckets": [],
        }
    except Exception as exc:
        return {
            "provider": "openai-codex",
            "logged_in": False,
            "available": False,
            "message": f"Quota cache unavailable: {exc}",
            "buckets": [],
        }
