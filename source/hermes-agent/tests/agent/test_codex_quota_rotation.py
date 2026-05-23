from __future__ import annotations

import time

from agent.codex_quota import (
    choose_codex_quota_candidate,
    codex_quota_bucket_score,
    rank_codex_accounts_by_quota,
)
from agent.credential_pool import CredentialPool, PooledCredential


def _quota(remaining: int, reset_at: int = 1000, captured_at_unix: int | None = None):
    quota = {
        "provider": "openai-codex",
        "buckets": [
            {
                "key": "primary",
                "label": "5h",
                "remaining_percent": remaining,
                "used_percent": 100 - remaining,
                "reset_at": reset_at,
            }
        ],
    }
    if captured_at_unix is not None:
        quota["captured_at_unix"] = captured_at_unix
    return quota


def _entry(cid: str, remaining: int | None, reset_at: int = 1000, priority: int = 0, captured_at_unix: int | None = None):
    payload = {
        "id": cid,
        "label": cid,
        "auth_type": "oauth",
        "priority": priority,
        "source": "device_code",
        "access_token": f"token-{cid}",
    }
    if remaining is not None:
        payload["last_quota"] = _quota(remaining, reset_at=reset_at, captured_at_unix=captured_at_unix)
    return PooledCredential.from_dict("openai-codex", payload)


def test_quota_score_uses_primary_remaining_percent():
    assert codex_quota_bucket_score(_quota(7), threshold_percent=5)["quota_status"] == "ok"
    assert codex_quota_bucket_score(_quota(4), threshold_percent=5)["quota_status"] == "low"
    assert codex_quota_bucket_score(_quota(0), threshold_percent=5)["quota_status"] == "exhausted"


def test_rank_prefers_more_remaining_then_earliest_reset():
    entries = [
        _entry("soon", 50, reset_at=1000, priority=2),
        _entry("more", 80, reset_at=9000, priority=1),
        _entry("low", 3, reset_at=10, priority=0),
    ]

    ranked = rank_codex_accounts_by_quota(entries, threshold_percent=5)

    assert [row["id"] for row in ranked] == ["more", "soon", "low"]


def test_rank_tie_breaks_by_earliest_reset_at():
    entries = [
        _entry("later", 50, reset_at=9000, priority=0),
        _entry("sooner", 50, reset_at=1000, priority=1),
    ]

    ranked = rank_codex_accounts_by_quota(entries, threshold_percent=5)

    assert [row["id"] for row in ranked] == ["sooner", "later"]


def test_choose_keeps_selected_when_above_threshold():
    selected = _entry("selected", 10, reset_at=1000)
    better = _entry("better", 80, reset_at=2000)

    chosen, meta = choose_codex_quota_candidate([selected, better], current_id="selected", threshold_percent=5)

    assert chosen.id == "selected"
    assert meta["reason"] == "selected_above_threshold"


def test_choose_rotates_from_low_selected_to_above_threshold_candidate():
    selected = _entry("selected", 1, reset_at=1000)
    candidate = _entry("candidate", 30, reset_at=2000)

    chosen, meta = choose_codex_quota_candidate([selected, candidate], current_id="selected", threshold_percent=5)

    assert chosen.id == "candidate"
    assert meta["reason"] == "rotated_to_above_threshold"


def test_choose_keeps_selected_when_every_account_below_threshold():
    selected = _entry("selected", 1, reset_at=1000)
    other = _entry("other", 2, reset_at=2000)

    chosen, meta = choose_codex_quota_candidate([selected, other], current_id="selected", threshold_percent=5)

    assert chosen.id == "selected"
    assert meta["reason"] == "kept_selected_no_above_threshold"


def test_credential_pool_quota_selection_sets_current_id(monkeypatch, tmp_path):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes"))
    selected = _entry("selected", 1, reset_at=1000)
    candidate = _entry("candidate", 30, reset_at=2000)
    pool = CredentialPool("openai-codex", [selected, candidate])

    chosen = pool.select_codex_by_quota(selected_credential_id="selected", threshold_percent=5)

    assert chosen.id == "candidate"
    assert pool.current_id == "candidate"


# ---------------------------------------------------------------------------
# Blocker 1: stale cache enforcement
# ---------------------------------------------------------------------------

def test_stale_high_quota_not_chosen_over_current_safe():
    """Stale high-quota candidate must not drive preemptive rotation."""
    now = int(time.time())
    selected = _entry("selected", 10, reset_at=1000, captured_at_unix=now)
    stale_high = _entry("stale-high", 80, reset_at=2000, captured_at_unix=now - 1000)

    chosen, meta = choose_codex_quota_candidate(
        [selected, stale_high],
        current_id="selected",
        threshold_percent=5,
        max_quota_cache_age_seconds=900,
    )

    # Stale high-quota should be treated as unknown, not above-threshold.
    # The selected account is above-threshold (10 >= 5) and fresh — keep it.
    assert chosen.id == "selected"
    assert meta["reason"] == "selected_above_threshold"


def test_all_candidates_stale_keeps_selected():
    """When every candidate has stale quota, keep the selected account."""
    now = int(time.time())
    selected = _entry("selected", 1, reset_at=1000, captured_at_unix=now - 2000)
    other_stale = _entry("stale-other", 80, reset_at=2000, captured_at_unix=now - 2000)

    chosen, meta = choose_codex_quota_candidate(
        [selected, other_stale],
        current_id="selected",
        threshold_percent=5,
        max_quota_cache_age_seconds=900,
    )

    # All stale — fall back to keeping selected, do not rotate into stale data.
    assert chosen.id == "selected"
    assert meta["reason"] == "kept_selected_no_above_threshold"


def test_fresh_above_threshold_preferred_over_stale_high():
    """Fresh above-threshold candidate should rank above stale high-quota."""
    now = int(time.time())
    selected = _entry("selected", 1, reset_at=1000, captured_at_unix=now)
    stale_high = _entry("stale-high", 80, reset_at=2000, captured_at_unix=now - 1000)
    fresh_ok = _entry("fresh-ok", 30, reset_at=3000, captured_at_unix=now)

    ranked = rank_codex_accounts_by_quota(
        [selected, stale_high, fresh_ok],
        threshold_percent=5,
        max_quota_cache_age_seconds=900,
    )

    # fresh_ok should rank first (above threshold, fresh)
    # selected ranks behind fresh_ok (below threshold)
    # stale_high should rank last (treated as unknown, stale)
    ids = [row["id"] for row in ranked]
    assert ids[0] == "fresh-ok"
    assert "stale-high" in ids
    stale_row = next(row for row in ranked if row["id"] == "stale-high")
    assert stale_row["stale_quota"] is True
    assert stale_row["above_threshold"] is False


def test_missing_captured_at_unix_treated_as_stale():
    """When captured_at_unix is missing, treat the quota as stale."""
    now = int(time.time())
    selected = _entry("selected", 10, reset_at=1000, captured_at_unix=now)
    no_timestamp = _entry("no-ts", 80, reset_at=2000, captured_at_unix=None)

    chosen, meta = choose_codex_quota_candidate(
        [selected, no_timestamp],
        current_id="selected",
        threshold_percent=5,
        max_quota_cache_age_seconds=900,
    )

    # "no-ts" has no captured_at_unix — treated as stale, not above-threshold.
    # Selected is fresh and above threshold — keep it.
    assert chosen.id == "selected"
    assert meta["reason"] == "selected_above_threshold"


def test_max_quota_cache_age_zero_disables_stale_check():
    """When max_quota_cache_age_seconds=0, stale check is disabled."""
    now = int(time.time())
    selected = _entry("selected", 1, reset_at=1000, captured_at_unix=now)
    stale_high = _entry("stale-high", 80, reset_at=2000, captured_at_unix=now - 10000)

    chosen, meta = choose_codex_quota_candidate(
        [selected, stale_high],
        current_id="selected",
        threshold_percent=5,
        max_quota_cache_age_seconds=0,
    )

    # Stale check disabled — highest above-threshold wins even if stale.
    assert chosen.id == "stale-high"
    assert meta["reason"] == "rotated_to_above_threshold"


# ---------------------------------------------------------------------------
# Weekly (secondary) quota hard gate
# ---------------------------------------------------------------------------

def _quota_with_weekly(
    remaining_5h: int,
    remaining_weekly: int,
    reset_at: int = 1000,
    captured_at_unix: int | None = None,
):
    quota = {
        "provider": "openai-codex",
        "buckets": [
            {
                "key": "primary",
                "label": "5h",
                "remaining_percent": remaining_5h,
                "used_percent": 100 - remaining_5h,
                "reset_at": reset_at,
            },
            {
                "key": "secondary",
                "label": "Weekly",
                "remaining_percent": remaining_weekly,
                "used_percent": 100 - remaining_weekly,
                "reset_at": reset_at + 86_400,
            },
        ],
    }
    if captured_at_unix is not None:
        quota["captured_at_unix"] = captured_at_unix
    return quota


def _entry_with_weekly(
    cid: str,
    remaining_5h: int,
    remaining_weekly: int,
    reset_at: int = 1000,
    priority: int = 0,
    captured_at_unix: int | None = None,
):
    return PooledCredential.from_dict("openai-codex", {
        "id": cid,
        "label": cid,
        "auth_type": "oauth",
        "priority": priority,
        "source": "device_code",
        "access_token": f"token-{cid}",
        "last_quota": _quota_with_weekly(
            remaining_5h, remaining_weekly,
            reset_at=reset_at,
            captured_at_unix=captured_at_unix,
        ),
    })


# --- Case 1 / 4: 5h low, weekly healthy → rotate to better 5h candidate ---

def test_weekly_healthy_rotates_to_better_5h_candidate():
    """Weekly healthy + low 5h → rotate to another account with better 5h."""
    selected = _entry_with_weekly("selected", 1, 80)       # low 5h, weekly healthy
    candidate = _entry_with_weekly("candidate", 30, 50)    # better 5h, weekly healthy

    chosen, meta = choose_codex_quota_candidate(
        [selected, candidate], current_id="selected",
    )

    assert chosen.id == "candidate"
    assert meta["reason"] == "rotated_to_above_threshold"


# --- Case 2: 5h healthy, weekly depleted → don't select that account ---

def test_weekly_depleted_blocks_rotation_into_that_account():
    """An account with high 5h but depleted weekly must not be chosen."""
    selected = _entry_with_weekly("selected", 1, 80)       # low 5h, weekly healthy
    weekly_depleted = _entry_with_weekly("depleted", 80, 0)  # high 5h, weekly EXHAUSTED

    chosen, meta = choose_codex_quota_candidate(
        [selected, weekly_depleted], current_id="selected",
    )

    # Must NOT rotate into the weekly-depleted account even though it has 80% 5h.
    assert chosen.id == "selected"
    assert meta["reason"] == "kept_selected_no_above_threshold"


def test_weekly_depleted_not_eligible_for_rotation():
    """Weekly-depleted account must not be in usable_above pool."""
    selected = _entry_with_weekly("selected", 10, 80)      # healthy both
    weekly_depleted = _entry_with_weekly("depleted", 99, 0)  # high 5h but weekly depleted

    ranked = rank_codex_accounts_by_quota([selected, weekly_depleted])
    dep_row = next(r for r in ranked if r["id"] == "depleted")
    sel_row = next(r for r in ranked if r["id"] == "selected")

    assert dep_row["weekly_healthy"] is False
    assert dep_row["above_threshold"] is True       # 5h is above threshold
    assert dep_row["quota_status"] == "ok"
    # Despite good 5h, weekly-depleted must sort below weekly-healthy entries.
    assert ranked.index(dep_row) > ranked.index(sel_row)


# --- Case 3: all accounts weekly depleted → keep selected ---

def test_all_accounts_weekly_depleted_keeps_selected():
    """When every account is weekly-depleted, keep the selected one."""
    selected = _entry_with_weekly("selected", 50, 0)    # weekly depleted, good 5h
    other = _entry_with_weekly("other", 10, 0)           # weekly depleted, low 5h

    chosen, meta = choose_codex_quota_candidate(
        [selected, other], current_id="selected",
    )

    assert chosen.id == "selected"
    assert meta["reason"] == "kept_selected_weekly_depleted"


def test_all_weekly_depleted_no_selected_falls_back_to_first():
    """All weekly depleted with no current → fallback (no blind rotation)."""
    a = _entry_with_weekly("a", 80, 0)
    b = _entry_with_weekly("b", 30, 0)

    chosen, meta = choose_codex_quota_candidate([a, b], current_id="")

    # Fallback to first in ranked list since no current.
    assert chosen.id in {"a", "b"}
    assert meta["reason"] == "fallback_no_current"


def test_weekly_depleted_ranked_below_weekly_healthy():
    """Weekly-depleted accounts must sort below weekly-healthy ones."""
    healthy = _entry_with_weekly("healthy", 3, 50)       # low 5h, weekly healthy
    depleted = _entry_with_weekly("depleted", 80, 0)     # high 5h, weekly depleted

    ranked = rank_codex_accounts_by_quota([depleted, healthy])

    ids = [r["id"] for r in ranked]
    assert ids[0] == "healthy", f"Expected healthy first, got {ids}"
    assert ids[1] == "depleted"


# --- Case 2 variant: selected is weekly-depleted with good 5h,
#     candidate is weekly-healthy but low 5h → keep selected ---

def test_selected_weekly_depleted_no_better_candidate():
    """Selected weekly-depleted, only candidate has low 5h → keep selected."""
    selected = _entry_with_weekly("selected", 50, 0)     # weekly depleted, good 5h
    candidate = _entry_with_weekly("candidate", 1, 80)   # weekly healthy, low 5h

    chosen, meta = choose_codex_quota_candidate(
        [selected, candidate], current_id="selected",
    )

    # Don't rotate to low-5h candidate; keep selected despite weekly depletion.
    assert chosen.id == "selected"
    assert meta["reason"] == "kept_selected_weekly_depleted"


# --- Case 1 variant: weekly healthy, 5h depleted → rotate to better 5h ---

def test_weekly_healthy_5h_low_rotates_to_weekly_healthy_better_5h():
    """Weekly healthy + low 5h → rotate if weekly-healthy better 5h exists."""
    selected = _entry_with_weekly("selected", 1, 80)     # low 5h, weekly healthy
    better = _entry_with_weekly("better", 40, 60)        # better 5h, weekly healthy

    chosen, meta = choose_codex_quota_candidate(
        [selected, better], current_id="selected",
    )

    assert chosen.id == "better"
    assert meta["reason"] == "rotated_to_above_threshold"


# --- Weekly healthy + 5h healthy remains ---

def test_weekly_healthy_and_5h_healthy_keeps_selected():
    """Both axes healthy → keep selected."""
    selected = _entry_with_weekly("selected", 50, 80)
    other = _entry_with_weekly("other", 90, 60)

    chosen, meta = choose_codex_quota_candidate(
        [selected, other], current_id="selected",
    )

    assert chosen.id == "selected"
    assert meta["reason"] == "selected_above_threshold"
