"""Gateway runtime-metadata footer.

Renders a compact footer showing runtime state (model, context %, cwd) and
appends it to the FINAL message of an agent turn when enabled.  Off by default
to keep replies minimal.

Config (``~/.hermes/config.yaml``)::

    display:
      runtime_footer:
        enabled: true                       # off by default
        fields: [model, context_pct, cwd]   # order shown; drop any to hide

Per-platform overrides live under ``display.platforms.<platform>.runtime_footer``.
Users can toggle the global setting with ``/footer on|off`` from both the CLI
and any gateway platform.

The footer is appended to the final response text in ``gateway/run.py`` right
before returning the response to the adapter send path — so it only lands on
the final message a user sees, not on tool-progress updates or streaming
partials.  When streaming is on and the final text has already been delivered
piecemeal, the footer is sent as a separate trailing message via
``send_trailing_footer()``.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

_DEFAULT_FIELDS: tuple[str, ...] = ("model", "context_pct", "cwd")
_SEP = " · "


def _home_relative_cwd(cwd: str) -> str:
    """Return *cwd* with ``$HOME`` collapsed to ``~``.  Empty string if unset."""
    if not cwd:
        return ""
    try:
        home = os.path.expanduser("~")
        p = os.path.abspath(cwd)
        if home and (p == home or p.startswith(home + os.sep)):
            return "~" + p[len(home):]
        return p
    except Exception:
        return cwd


def _model_short(model: Optional[str]) -> str:
    """Drop ``vendor/`` prefix for readability (``openai/gpt-5.4`` → ``gpt-5.4``)."""
    if not model:
        return ""
    return model.rsplit("/", 1)[-1]


def _parse_quota_reset(value: Any) -> Optional[datetime]:
    """Parse a quota reset timestamp from unix seconds or ISO text."""
    if value is None or value == "":
        return None
    try:
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        text = str(value).strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _format_quota_reset(bucket: dict[str, Any]) -> str:
    """Render reset time/date compactly for a quota bucket."""
    reset_dt = _parse_quota_reset(bucket.get("reset_at"))
    if not reset_dt and bucket.get("reset_after_seconds") is not None:
        try:
            reset_dt = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(
                seconds=float(bucket.get("reset_after_seconds") or 0)
            )
        except Exception:
            reset_dt = None
    if not reset_dt:
        return ""
    local_dt = reset_dt.astimezone()
    local_now = datetime.now(timezone.utc).astimezone(local_dt.tzinfo)
    if local_dt.date() == local_now.date():
        return local_dt.strftime("%H:%M")
    return local_dt.strftime("%a %H:%M")


def format_quota_footer(quota: Optional[dict[str, Any]]) -> str:
    """Render sanitized Codex quota buckets for gateway footers.

    Expected input is the sanitized shape returned by ``agent.codex_quota``:
    ``{"buckets": [{"label": "5h", "remaining_percent": 83, ...}]}``.
    Secrets, account ids, and raw provider payloads are never read or rendered.
    """
    if not isinstance(quota, dict) or not quota.get("available"):
        return ""
    buckets = quota.get("buckets")
    if not isinstance(buckets, list):
        return ""
    parts: list[str] = []
    for bucket in buckets:
        if not isinstance(bucket, dict):
            continue
        label = str(bucket.get("label") or bucket.get("key") or "quota").strip()
        remaining = bucket.get("remaining_percent")
        if remaining is None and bucket.get("used_percent") is not None:
            try:
                remaining = max(0, 100 - round(float(bucket.get("used_percent") or 0)))
            except Exception:
                remaining = None
        if remaining is None:
            continue
        try:
            remaining_i = max(0, min(100, round(float(remaining))))
        except Exception:
            continue
        reset = _format_quota_reset(bucket)
        suffix = f" reset {reset}" if reset else ""
        parts.append(f"{label} {remaining_i}% left{suffix}")
    return _SEP.join(parts)


def resolve_footer_config(
    user_config: dict[str, Any] | None,
    platform_key: str | None = None,
) -> dict[str, Any]:
    """Resolve effective runtime-footer config for *platform_key*.

    Merge order (later wins):
        1. Built-in defaults (enabled=False)
        2. ``display.runtime_footer``
        3. ``display.platforms.<platform_key>.runtime_footer``
    """
    resolved = {"enabled": False, "fields": list(_DEFAULT_FIELDS)}
    cfg = (user_config or {}).get("display") or {}

    global_cfg = cfg.get("runtime_footer")
    if isinstance(global_cfg, dict):
        if "enabled" in global_cfg:
            resolved["enabled"] = bool(global_cfg.get("enabled"))
        if isinstance(global_cfg.get("fields"), list) and global_cfg["fields"]:
            resolved["fields"] = [str(f) for f in global_cfg["fields"]]

    if platform_key:
        platforms = cfg.get("platforms") or {}
        plat_cfg = platforms.get(platform_key)
        if isinstance(plat_cfg, dict):
            plat_footer = plat_cfg.get("runtime_footer")
            if isinstance(plat_footer, dict):
                if "enabled" in plat_footer:
                    resolved["enabled"] = bool(plat_footer.get("enabled"))
                if isinstance(plat_footer.get("fields"), list) and plat_footer["fields"]:
                    resolved["fields"] = [str(f) for f in plat_footer["fields"]]

    return resolved


def format_runtime_footer(
    *,
    model: Optional[str],
    context_tokens: int,
    context_length: Optional[int],
    cwd: Optional[str] = None,
    fields: Iterable[str] = _DEFAULT_FIELDS,
    quota: Optional[dict[str, Any]] = None,
) -> str:
    """Render the footer line, or return "" if no fields have data.

    Fields are skipped silently when their underlying data is missing — a
    partially-populated footer is better than a line with ``?%`` or empty slots.
    """
    parts: list[str] = []
    for field in fields:
        if field == "model":
            m = _model_short(model)
            if m:
                parts.append(m)
        elif field == "context_pct":
            if context_length and context_length > 0 and context_tokens >= 0:
                pct = max(0, min(100, round((context_tokens / context_length) * 100)))
                parts.append(f"{pct}%")
        elif field == "cwd":
            rel = _home_relative_cwd(cwd or os.environ.get("TERMINAL_CWD", ""))
            if rel:
                parts.append(rel)
        elif field == "quota":
            quota_text = format_quota_footer(quota)
            if quota_text:
                parts.append(quota_text)
        # Unknown field names are silently ignored.

    if not parts:
        return ""
    return _SEP.join(parts)


def build_footer_line(
    *,
    user_config: dict[str, Any] | None,
    platform_key: str | None,
    model: Optional[str],
    context_tokens: int,
    context_length: Optional[int],
    cwd: Optional[str] = None,
    credential_id: Optional[str] = None,
) -> str:
    """Top-level entry point used by gateway/run.py.

    Returns the footer text (empty string when disabled or no data).  Callers
    append this to the final response themselves, preserving a single blank
    line of separation.
    """
    cfg = resolve_footer_config(user_config, platform_key)
    if not cfg.get("enabled"):
        return ""
    fields = cfg.get("fields") or _DEFAULT_FIELDS
    quota = None
    if "quota" in fields:
        try:
            from agent.codex_quota import fetch_live_codex_quota

            quota = fetch_live_codex_quota(
                timeout_seconds=3.0,
                credential_id=credential_id,
            )
        except Exception:
            quota = None
    return format_runtime_footer(
        model=model,
        context_tokens=context_tokens,
        context_length=context_length,
        cwd=cwd,
        fields=fields,
        quota=quota,
    )
