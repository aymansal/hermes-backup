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


def _parse_reset_at(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        text = str(value).strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.timestamp()
    except Exception:
        return None


def _quota_buckets(quota: Any) -> list[Mapping[str, Any]]:
    if not isinstance(quota, Mapping):
        return []
    buckets = quota.get("buckets")
    if not isinstance(buckets, list):
        return []
    return [bucket for bucket in buckets if isinstance(bucket, Mapping)]


def _get_weekly_bucket(quota: Any) -> Optional[Mapping[str, Any]]:
    """Return the weekly/secondary quota bucket if present, else None.

    Only returns a bucket when the payload explicitly has a bucket with
    key ``"secondary"``.  Returns None when there is no weekly window,
    which is the conservative default — absence of weekly data is not
    treated as depletion.
    """
    buckets = _quota_buckets(quota)
    for bucket in buckets:
        key = str(bucket.get("key") or "").strip().lower()
        if key == "secondary":
            return bucket
    return None


def _preferred_bucket(quota: Any, window_key: str = "primary") -> Optional[Mapping[str, Any]]:
    buckets = _quota_buckets(quota)
    if not buckets:
        return None
    preferred = str(window_key or "primary").strip().lower()
    for bucket in buckets:
        if str(bucket.get("key") or "").strip().lower() == preferred:
            return bucket
    if preferred == "primary":
        for bucket in buckets:
            label = str(bucket.get("label") or "").strip().lower()
            window = bucket.get("window_minutes")
            if "5h" in label or window == 300:
                return bucket
    return buckets[0]


def codex_remaining_percent(quota: Any, window_key: str = "primary") -> Optional[float]:
    """Return remaining quota percent for the preferred Codex window."""
    bucket = _preferred_bucket(quota, window_key=window_key)
    if not bucket:
        return None
    remaining = bucket.get("remaining_percent")
    if remaining is None and bucket.get("used_percent") is not None:
        try:
            remaining = 100 - float(bucket.get("used_percent") or 0)
        except Exception:
            remaining = None
    try:
        return max(0.0, min(100.0, float(remaining)))
    except (TypeError, ValueError):
        return None


def codex_reset_at(quota: Any, window_key: str = "primary") -> Optional[float]:
    """Return reset timestamp for the preferred Codex window, if known."""
    bucket = _preferred_bucket(quota, window_key=window_key)
    if not bucket:
        return None
    reset = _parse_reset_at(bucket.get("reset_at"))
    if reset is not None:
        return reset
    try:
        after = bucket.get("reset_after_seconds")
        if after is not None:
            return time.time() + float(after)
    except Exception:
        return None
    return None


def codex_quota_bucket_score(
    quota: Any,
    *,
    threshold_percent: float = 5,
    window_key: str = "primary",
) -> dict[str, Any]:
    """Return non-secret score metadata for one sanitized quota payload."""
    remaining = codex_remaining_percent(quota, window_key=window_key)
    reset_at = codex_reset_at(quota, window_key=window_key)
    try:
        threshold = float(threshold_percent)
    except Exception:
        threshold = 5.0
    return {
        "remaining_percent": remaining,
        "reset_at": reset_at,
        "above_threshold": bool(remaining is not None and remaining >= threshold),
        "quota_status": (
            "unknown" if remaining is None else
            "exhausted" if remaining <= 0 else
            "low" if remaining < threshold else
            "ok"
        ),
    }


def codex_quota_rotation_config(config: Optional[Mapping[str, Any]] = None) -> dict[str, Any]:
    """Load normalized disabled-by-default Codex quota rotation settings."""
    if config is None:
        try:
            from hermes_cli.config import load_config

            loaded = load_config()
            config = loaded if isinstance(loaded, Mapping) else {}
        except Exception:
            config = {}
    raw = config.get("codex_quota_rotation", {}) if isinstance(config, Mapping) else {}
    if not isinstance(raw, Mapping):
        raw = {}
    try:
        threshold = float(raw.get("threshold_percent", 5))
    except Exception:
        threshold = 5.0
    try:
        max_age = int(raw.get("max_quota_cache_age_seconds", 900))
    except Exception:
        max_age = 900
    try:
        unused_backoff = int(raw.get("unused_fetch_backoff_seconds", 1800))
    except Exception:
        unused_backoff = 1800
    try:
        min_reset_lead = int(raw.get("min_reset_lead_seconds", 3600))
    except Exception:
        min_reset_lead = 3600
    return {
        "enabled": bool(raw.get("enabled", False)),
        "threshold_percent": max(0.0, min(100.0, threshold)),
        "window_key": str(raw.get("window_key") or "primary"),
        "max_quota_cache_age_seconds": max(0, max_age),
        "persist_runtime_switch": bool(raw.get("persist_runtime_switch", False)),
        "prefer_reset_ending_soonest": bool(raw.get("prefer_reset_ending_soonest", True)),
        "unused_fetch_backoff_seconds": max(0, unused_backoff),
        "min_reset_lead_seconds": max(0, min_reset_lead),
    }


def _unused_fetch_backoff_seconds() -> int:
    """Return configured backoff in seconds for unused-account quota refreshes."""
    try:
        cfg = codex_quota_rotation_config()
        return max(0, int(cfg.get("unused_fetch_backoff_seconds", 1800)))
    except Exception:
        return 1800


def _last_fetch_attempt_at(credential_id: Optional[str] = None) -> Optional[float]:
    """Return last live quota fetch attempt timestamp, or None if never attempted.

    Reads ``last_fetch_attempt_at_unix`` from the credential pool entry.
    This is set on every attempt regardless of success/failure so the
    unused-account backoff gate has accurate timing.
    """
    entry = _pool_entry_payload(credential_id)
    if not isinstance(entry, Mapping):
        return None
    raw = entry.get("last_fetch_attempt_at_unix")
    try:
        return float(raw) if raw is not None else None
    except (TypeError, ValueError):
        return None


def _record_fetch_attempt(credential_id: Optional[str] = None) -> None:
    """Persist ``last_fetch_attempt_at_unix`` on the credential entry.

    Called before every live fetch attempt (success or failure) so the
    unused-account backoff gate sees the attempt even when the fetch
    raises an exception.
    """
    from hermes_cli.auth import (
        _auth_store_lock,
        _load_auth_store,
        _save_auth_store,
    )

    selected_id = str(credential_id or _selected_codex_credential_id() or "").strip()
    now = int(time.time())
    with _auth_store_lock():
        auth_store = _load_auth_store()
        if selected_id:
            pool = auth_store.setdefault("credential_pool", {})
            entries = pool.get("openai-codex")
            if isinstance(entries, list):
                for entry in entries:
                    if isinstance(entry, dict) and str(entry.get("id") or "") == selected_id:
                        entry["last_fetch_attempt_at_unix"] = now
                        _save_auth_store(auth_store)
                        return


def persist_selected_codex_credential_id(credential_id: str, *, reason: str = "runtime") -> bool:
    """Persist the active Codex credential id to config.yaml, never tokens."""
    selected = str(credential_id or "").strip()
    if not selected:
        return False
    try:
        from hermes_cli.config import load_config, save_config

        cfg = load_config()
        if not isinstance(cfg, dict):
            return False
        model_cfg = cfg.get("model", {})
        if not isinstance(model_cfg, dict):
            model_cfg = {"default": str(model_cfg or "")}
        if str(model_cfg.get("credential_id") or "").strip() == selected:
            return False
        model_cfg["provider"] = "openai-codex"
        model_cfg["credential_id"] = selected
        cfg["model"] = model_cfg
        save_config(cfg)
        return True
    except Exception:
        return False


def rank_codex_accounts_by_quota(
    entries: list[Any],
    *,
    current_id: str = "",
    threshold_percent: float = 5,
    window_key: str = "primary",
    prefer_reset_ending_soonest: bool = True,
    max_quota_cache_age_seconds: int = 0,
    min_reset_lead_seconds: int = 0,
) -> list[dict[str, Any]]:
    """Rank pool entries using sanitized cached Codex quota only.

    Returned rows contain entry object references plus non-secret score fields.
    Unknown quota sorts behind known above-threshold candidates but ahead of
    known below-threshold candidates only when no usable quota is available.

    When *max_quota_cache_age_seconds* > 0, any entry whose cached quota
    ``captured_at_unix`` is older than that threshold (or missing) is treated
    as unknown/unusable for preemptive above-threshold rotation.  This prevents
    stale high-quota snapshots from driving a rotation into an account whose
    quota may have already been consumed.

    Each row also carries a ``weekly_healthy`` flag.  When the quota payload
    has an explicit weekly (secondary) bucket with ``remaining_percent <= 0``,
    the account is gated as depleted regardless of its 5h primary window.
    Absence of a weekly bucket is *not* treated as depletion — the account
    is still eligible for rotation.
    """
    ranked: list[dict[str, Any]] = []
    current = str(current_id or "").strip()
    now = int(time.time())
    max_age = max(0, int(max_quota_cache_age_seconds))
    min_reset_lead = max(0, int(min_reset_lead_seconds))
    for index, entry in enumerate(entries):
        quota = getattr(entry, "last_quota", None)
        quota_is_stale = False
        if max_age > 0 and isinstance(quota, Mapping):
            captured = quota.get("captured_at_unix")
            if not isinstance(captured, (int, float)) or (now - int(captured)) > max_age:
                quota_is_stale = True
        elif max_age > 0 and quota is None:
            quota_is_stale = True
        # Build score from the original quota; stale flag is applied below.
        score = codex_quota_bucket_score(
            quota if not quota_is_stale else None,
            threshold_percent=threshold_percent,
            window_key=window_key,
        )
        remaining = score.get("remaining_percent")
        reset_at = score.get("reset_at")
        reset_lead_seconds = None
        reset_lead_eligible = True
        if min_reset_lead > 0:
            reset_lead_eligible = False
            if reset_at is not None:
                reset_lead_seconds = float(reset_at) - float(now)
                reset_lead_eligible = reset_lead_seconds >= min_reset_lead
        elif reset_at is not None:
            reset_lead_seconds = float(reset_at) - float(now)
        above = bool(score.get("above_threshold") and not quota_is_stale and reset_lead_eligible)
        is_current = bool(current and getattr(entry, "id", "") == current)
        if reset_at is not None and prefer_reset_ending_soonest:
            reset_rank = float(reset_at)
            missing_reset_rank = 0
        else:
            # Known reset windows are preferred over unknown reset windows when
            # the operator wants to burn the account whose window ends soonest.
            reset_rank = float("inf")
            missing_reset_rank = 1
        remaining_rank = float(remaining) if remaining is not None else -1.0

        # --- Weekly (secondary) health gate ---
        # Only flag as depleted when we have *explicit proof* — a fresh quota
        # payload with a secondary bucket whose remaining_percent is <= 0.
        # Absence of a weekly bucket is NOT treated as depletion (conservative
        # default).  Stale / None quota also skips the weekly gate so existing
        # stale-cache fallback logic is undisturbed.
        weekly_healthy = True
        weekly_remaining = None
        if not quota_is_stale and isinstance(quota, Mapping):
            weekly_bucket = _get_weekly_bucket(quota)
            if weekly_bucket is not None:
                weekly_raw = weekly_bucket.get("remaining_percent")
                try:
                    weekly_remaining = float(weekly_raw) if weekly_raw is not None else None
                except (TypeError, ValueError):
                    weekly_remaining = None
                if weekly_remaining is not None:
                    weekly_healthy = weekly_remaining > 0

        ranked.append({
            "entry": entry,
            "id": getattr(entry, "id", ""),
            "remaining_percent": remaining,
            "reset_at": reset_at,
            "quota_status": score.get("quota_status"),
            "above_threshold": above,
            "selected": is_current,
            "stale_quota": quota_is_stale,
            "reset_lead_seconds": reset_lead_seconds,
            "reset_lead_eligible": reset_lead_eligible,
            "weekly_healthy": weekly_healthy,
            "weekly_remaining_percent": weekly_remaining,
            "sort_key": (
                0 if (above and weekly_healthy) else
                1 if weekly_healthy else
                2,
                reset_rank,
                missing_reset_rank,
                0 if is_current else 1,
                -remaining_rank,
                getattr(entry, "priority", index),
                index,
            ),
        })
    return sorted(ranked, key=lambda row: row["sort_key"])


def choose_codex_quota_candidate(
    entries: list[Any],
    *,
    current_id: str = "",
    threshold_percent: float = 5,
    window_key: str = "primary",
    prefer_reset_ending_soonest: bool = True,
    max_quota_cache_age_seconds: int = 0,
    min_reset_lead_seconds: int = 0,
    fallback_to_first: bool = True,
) -> tuple[Optional[Any], dict[str, Any]]:
    """Choose a safe Codex account for preemptive quota rotation.

    Weekly (secondary) quota is a hard health gate: an account with
    explicit weekly depletion is treated as unavailable regardless of
    its 5h primary window.  Only accounts passing the weekly health gate
    are eligible for above-threshold rotation.

    When *max_quota_cache_age_seconds* > 0, stale cached quota is treated as
    unknown/unusable for above-threshold decisions — the function will not
    rotate into an account whose quota snapshot is too old to trust.
    If all candidates are stale/unknown, the selected account is kept and
    reactive 402/429 fallback remains the safety net.

    Cases handled:
      1. 5h low, weekly healthy     → rotate to better 5h candidate if exists
      2. 5h healthy, weekly depleted → account treated as unavailable; don't select it
      3. All weekly depleted          → keep selected if possible (no blind rotation)
      4. Weekly healthy, 5h depleted  → rotate away if better 5h candidate exists
    """
    ranked = rank_codex_accounts_by_quota(
        entries,
        current_id=current_id,
        threshold_percent=threshold_percent,
        window_key=window_key,
        prefer_reset_ending_soonest=prefer_reset_ending_soonest,
        max_quota_cache_age_seconds=max_quota_cache_age_seconds,
        min_reset_lead_seconds=min_reset_lead_seconds,
    )
    current_row = next((row for row in ranked if row.get("selected")), None)

    # Only accounts that pass BOTH gates (5h above threshold AND weekly
    # healthy) are candidates for proactive rotation.
    usable_above = [r for r in ranked if r.get("weekly_healthy") and r.get("above_threshold")]

    # 1. Any account that passes both gates may be used.  Because
    # ``rank_codex_accounts_by_quota`` already applies the configured ordering,
    # the top usable account is the account whose relevant window resets soonest
    # when ``prefer_reset_ending_soonest`` is enabled.  This deliberately allows
    # rotating away from a healthy selected account to burn the window that will
    # refresh first.
    if usable_above:
        top = usable_above[0]
        if current_row and top.get("id") == current_row.get("id"):
            return top["entry"], {"reason": "selected_above_threshold", "candidates": ranked}
        reason = "rotated_to_earliest_reset"
        if not (current_row and current_row.get("weekly_healthy") and current_row.get("above_threshold")):
            reason = "rotated_to_above_threshold"
        return top["entry"], {"reason": reason, "candidates": ranked}

    # 2. No better candidate — keep selected as conservative fallback.
    if current_row:
        if not current_row.get("weekly_healthy"):
            # Weekly depletion is the reason we can't rotate (5h might be fine).
            reason = "kept_selected_weekly_depleted"
        else:
            reason = "kept_selected_no_above_threshold"
        return current_row["entry"], {"reason": reason, "candidates": ranked}

    # 4. No current at all — fallback to first entry unless the caller is a
    # strict reactive path that must not rotate into an ineligible account.
    if fallback_to_first:
        return (ranked[0]["entry"] if ranked else None), {"reason": "fallback_no_current", "candidates": ranked}
    return None, {"reason": "no_eligible_candidate", "candidates": ranked}


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
                        entry["last_fetch_attempt_at_unix"] = int(time.time())
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


def _resolve_pool_codex_credentials(
    credential_id: Optional[str],
    *,
    _for_quota_display: bool = False,
) -> tuple[str, Optional[dict[str, Any]]]:
    from agent.credential_pool import load_pool
    from hermes_cli.auth import AuthError

    pool = load_pool("openai-codex")
    if pool and pool.has_credentials():
        selected = str(credential_id or "").strip()
        if selected:
            entry = pool.select_by_id(selected)
            # For quota display: if the selected credential is exhausted or in
            # cooldown, select_by_id returns None.  Fall back to get_by_id so
            # we can still attempt a live /usage fetch.  Runtime model calls
            # still respect exhaustion — this bypass is only for display.
            if entry is None and _for_quota_display:
                entry = pool.get_by_id(selected)
        else:
            entry = pool.select()
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

    For **unused** accounts (explicit ``credential_id`` that does not match the
    globally-selected credential), an automatic backoff applies: the live fetch
    is skipped if the last attempt was less than ``unused_fetch_backoff_seconds``
    ago (default 30 minutes).  The globally-selected account is always fetched
    on demand.
    """
    from agent.auxiliary_client import _codex_cloudflare_headers
    from agent.model_metadata import _resolve_requests_verify
    from hermes_cli.auth import AuthError, resolve_codex_runtime_credentials

    selected_id = str(credential_id or _selected_codex_credential_id() or "").strip() or None
    account_entry: Optional[dict[str, Any]] = None

    # ── Unused-account backoff gate ──────────────────────────────────
    # When we're asked to refresh a specific credential that is NOT the
    # globally-selected one, respect the cooldown so background/dashboard
    # polling of unused accounts doesn't hammer Codex endpoints.
    explicit_credential = str(credential_id or "").strip() or None
    global_selected = _selected_codex_credential_id()
    if explicit_credential and global_selected and explicit_credential != global_selected:
        backoff = _unused_fetch_backoff_seconds()
        last_attempt = _last_fetch_attempt_at(explicit_credential)
        if last_attempt is not None and (time.time() - last_attempt) < backoff:
            cached = load_cached_codex_quota(credential_id=explicit_credential)
            cached["backoff_remaining_seconds"] = int(backoff - (time.time() - last_attempt))
            return cached

    # Record the attempt timestamp before making the call so even failed
    # attempts count toward the backoff.
    _record_fetch_attempt(selected_id)

    try:
        try:
            access_token, account_entry = _resolve_pool_codex_credentials(
                selected_id, _for_quota_display=bool(selected_id),
            )
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
