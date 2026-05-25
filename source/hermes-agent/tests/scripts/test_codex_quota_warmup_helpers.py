import importlib.util
import json
import sys
from pathlib import Path


# Use real absolute path — Path.home() in Hermes profile sessions
# resolves to the profile-scoped home, not the actual installation.
SCRIPT_PATH = Path("/home/ubuntu/.hermes/scripts/codex_quota_warmup.py")


def load_script():
    spec = importlib.util.spec_from_file_location("codex_quota_warmup_test", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_codex_entries_returns_only_safe_usable_metadata(tmp_path):
    mod = load_script()
    mod.HOME = tmp_path
    auth_path = tmp_path / ".hermes" / "auth.json"
    auth_path.parent.mkdir(parents=True)
    auth_path.write_text(json.dumps({
        "credential_pool": {
            "openai-codex": [
                {"id": "abc123456", "label": "Gpt1", "access_token": "secret-token", "email": "nope@example.com"},
                {"id": "def456789", "label": "Gpt2", "access_token": ""},
                {"id": "ghi789000", "access_token": "secret-token-2"},
                {"label": "missing-id", "access_token": "secret-token-3"},
            ]
        }
    }))

    assert mod._codex_entries() == [
        {"id": "abc123456", "id_prefix": "abc123", "label": "Gpt1"},
        {"id": "ghi789000", "id_prefix": "ghi789", "label": "ghi789"},
    ]


def test_summarize_quota_prefers_primary_bucket_and_formats_reset():
    mod = load_script()
    summary = mod._summarize_quota("Gpt1", "abc123456", {
        "buckets": [
            {"key": "secondary", "label": "weekly", "remaining_percent": 50, "reset_at": "2026-05-23T20:00:00Z"},
            {"key": "primary", "label": "5h", "remaining_percent": 99, "reset_at": "2026-05-23T14:00:00Z"},
        ],
        "live_fetch_failed": False,
    })

    assert summary == "Gpt1/abc123: remaining=99% reset=15:00:00 live_failed=False"


def test_warmup_all_marks_partial_failure_as_retryable(monkeypatch):
    mod = load_script()
    monkeypatch.setattr(mod, "_codex_entries", lambda: [
        {"id": "ok123456", "id_prefix": "ok1234", "label": "Gpt1"},
        {"id": "bad123456", "id_prefix": "bad123", "label": "Gpt2"},
    ])

    def fake_warmup(entry):
        if entry["id"].startswith("bad"):
            raise RuntimeError("boom")
        return f"{entry['label']}/{entry['id_prefix']}: warmup call completed"

    monkeypatch.setattr(mod, "_warmup_call_for_entry", fake_warmup)

    results = mod._warmup_all()

    assert results.ok is False
    assert results.any_success is True
    assert "Gpt1/ok1234: warmup call completed" in results.lines
    assert "Gpt2/bad123: warmup failed: boom" in results.lines


def test_slot_returns_staggered_warmup_slots_or_none():
    """Verify staggered 09/10/11/12 slots map to accounts 1/2/3/4."""
    mod = load_script()
    tz = mod.ZoneInfo("Africa/Casablanca")
    dt = mod.datetime

    for hour, index in [(9, 0), (10, 1), (11, 2), (12, 3)]:
        for minute in (0, 5, 19):
            slot = mod._slot(dt(2026, 5, 23, hour, minute, tzinfo=tz))
            assert slot is not None
            assert slot.name == f"warmup_{hour:02d}"
            assert slot.hour == hour
            assert slot.account_index == index

        for minute in (20, 30, 45, 59):
            assert mod._slot(dt(2026, 5, 23, hour, minute, tzinfo=tz)) is None

    for hour in (0, 6, 8, 13, 14, 15, 20, 23):
        assert mod._slot(dt(2026, 5, 23, hour, 0, tzinfo=tz)) is None


def test_entry_for_slot_selects_expected_account_and_errors_if_missing():
    mod = load_script()
    entries = [
        {"id": "one123", "id_prefix": "one123", "label": "One"},
        {"id": "two123", "id_prefix": "two123", "label": "Two"},
    ]

    assert mod._entry_for_slot(mod.WarmupSlot("warmup_09", 9, 0), entries)["label"] == "One"
    assert mod._entry_for_slot(mod.WarmupSlot("warmup_10", 10, 1), entries)["label"] == "Two"

    try:
        mod._entry_for_slot(mod.WarmupSlot("warmup_11", 11, 2), entries)
    except RuntimeError as exc:
        assert "expects account #3" in str(exc)
    else:
        raise AssertionError("expected RuntimeError for missing account")


def test_main_returns_0_outside_any_slot(monkeypatch):
    """Verify main() exits silently (return 0) when _slot returns None."""
    mod = load_script()
    monkeypatch.setattr(mod, "_slot", lambda now: None)
    monkeypatch.setattr(mod, "_load_state", lambda: {})
    monkeypatch.setattr(mod, "_save_state", lambda s: None)

    rc = mod.main()
    assert rc == 0
