"""Tests for dashboard Codex credential label resolution.

Replaces the old GptN auto-label logic with operator-provided names.
"""

from hermes_cli.web_server import _resolve_codex_label


def test_custom_label_used():
    """When user provides a custom label, it is used."""
    assert _resolve_codex_label("Swarm", "") == "Swarm"


def test_custom_label_trimmed():
    """Label gets whitespace-trimmed."""
    assert _resolve_codex_label("  My Account  ", "") == "My Account"


def test_custom_label_bounded():
    """Label gets truncated to 64 chars."""
    long = "a" * 100
    assert _resolve_codex_label(long, "") == "a" * 64


def test_blank_label_fallback():
    """When no label is provided, a neutral fallback is used (not GptN)."""
    result = _resolve_codex_label("", "")
    assert result == "ChatGPT Account"
    assert "Gpt" not in result
    assert "gpt" not in result


def test_none_label_fallback():
    """When label is None, a neutral fallback is used."""
    result = _resolve_codex_label(None, "")
    assert result == "ChatGPT Account"


def test_existing_label_preserved_on_reauth():
    """When re-authenticating, the existing label is preserved if no new label given."""
    assert _resolve_codex_label("", "Main") == "Main"
    assert _resolve_codex_label("  ", "Main") == "Main"
    assert _resolve_codex_label(None, "My Account") == "My Account"


def test_explicit_label_overrides_existing_on_reauth():
    """When a non-empty label is explicitly provided on re-auth, it updates."""
    assert _resolve_codex_label("Updated", "Old") == "Updated"


def test_existing_label_preserved_with_blank_fallback():
    """Re-auth preserves the existing label even though fallback exists."""
    result = _resolve_codex_label("", "Gpt1")
    assert result == "Gpt1"


# ── Integration tests: credential pool persistence ────────────────────────

import json
from unittest.mock import MagicMock


def _make_mock_response(status_code, json_data):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    return resp


def _setup_auth_json(hermes_home, pool_entries: list):
    """Write auth.json to the test hermes home with the given pool entries."""
    hermes_home.mkdir(parents=True, exist_ok=True)
    (hermes_home / "auth.json").write_text(
        json.dumps({"version": 1, "credential_pool": {"openai-codex": pool_entries}}, indent=2)
    )
    (hermes_home / "config.yaml").write_text("model:\n  provider: openrouter\n  default: test\n")


def _setup_mock_httpx(monkeypatch):
    """Monkeypatch httpx.Client so the worker gets sequenced mock responses."""
    import httpx as _httpx

    mock_client = MagicMock()
    mock_client.post.side_effect = [
        _make_mock_response(200, {
            "user_code": "ABCD-1234", "device_auth_id": "dev-id", "interval": "5",
        }),
        _make_mock_response(200, {
            "authorization_code": "auth-code", "code_verifier": "code-verifier",
        }),
        _make_mock_response(200, {
            "access_token": "stub-access-token", "refresh_token": "stub-refresh-token",
        }),
    ]
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_client
    monkeypatch.setattr(_httpx, "Client", lambda **kw: mock_cm)
    return mock_client


def _run_worker(sid, monkeypatch, hermes_home):
    """Run _codex_full_login_worker with mocked HTTP and sleep."""
    from hermes_cli import web_server as ws

    _setup_mock_httpx(monkeypatch)
    monkeypatch.setattr("time.sleep", lambda s: None)
    ws._codex_full_login_worker(sid)
    sess = ws._oauth_sessions.get(sid, {})
    return sess.get("status"), sess.get("error_message")


def test_codex_worker_new_account_with_label(tmp_path, monkeypatch):
    """New account with explicit label persists that label."""
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes"))
    _setup_auth_json(tmp_path / "hermes", [])

    from hermes_cli import web_server as ws
    sid = "test-new-with-label"
    ws._oauth_sessions[sid] = {
        "session_id": sid, "provider": "openai-codex", "flow": "device_code",
        "created_at": __import__("time").time(), "status": "pending", "error_message": None,
        "label": "Swarm",
    }
    monkeypatch.setattr(ws, "_codex_account_fingerprint", lambda tok: "")
    try:
        status, err = _run_worker(sid, monkeypatch, tmp_path / "hermes")
        assert status == "approved", f"worker failed: {err}"
        pool_data = json.loads(((tmp_path / "hermes") / "auth.json").read_text())
        creds = pool_data["credential_pool"]["openai-codex"]
        assert len(creds) == 1
        assert creds[0]["label"] == "Swarm"
    finally:
        ws._oauth_sessions.pop(sid, None)


def test_codex_worker_new_account_blank_label(tmp_path, monkeypatch):
    """New account with blank label gets neutral fallback."""
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes"))
    _setup_auth_json(tmp_path / "hermes", [])

    from hermes_cli import web_server as ws
    sid = "test-new-blank"
    ws._oauth_sessions[sid] = {
        "session_id": sid, "provider": "openai-codex", "flow": "device_code",
        "created_at": __import__("time").time(), "status": "pending", "error_message": None,
        # No "label" key — simulates POST without label field
    }
    monkeypatch.setattr(ws, "_codex_account_fingerprint", lambda tok: "")
    try:
        status, err = _run_worker(sid, monkeypatch, tmp_path / "hermes")
        assert status == "approved", f"worker failed: {err}"
        pool_data = json.loads(((tmp_path / "hermes") / "auth.json").read_text())
        creds = pool_data["credential_pool"]["openai-codex"]
        assert len(creds) == 1
        assert creds[0]["label"] == "ChatGPT Account"
        assert "Gpt" not in creds[0]["label"]
    finally:
        ws._oauth_sessions.pop(sid, None)


def test_codex_worker_reauth_preserves_label_when_blank(tmp_path, monkeypatch):
    """Re-auth with blank label preserves the existing credential's label."""
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes"))
    _setup_auth_json(tmp_path / "hermes", [
        {
            "id": "cred-1", "label": "Main", "auth_type": "oauth", "priority": 0,
            "source": "dashboard_device_code", "access_token": "old-token",
            "refresh_token": "old-refresh",
            "account_fingerprint": "fp-main",
        },
    ])
    from hermes_cli import web_server as ws
    sid = "test-reauth-blank"
    ws._oauth_sessions[sid] = {
        "session_id": sid, "provider": "openai-codex", "flow": "device_code",
        "created_at": __import__("time").time(), "status": "pending", "error_message": None,
        # No label key — refresh without new label
    }
    monkeypatch.setattr(ws, "_codex_account_fingerprint", lambda tok: "fp-main")
    try:
        status, err = _run_worker(sid, monkeypatch, tmp_path / "hermes")
        assert status == "approved", f"worker failed: {err}"
        pool_data = json.loads(((tmp_path / "hermes") / "auth.json").read_text())
        creds = pool_data["credential_pool"]["openai-codex"]
        assert len(creds) == 1
        # Label must be preserved from the old credential
        assert creds[0]["label"] == "Main", "re-auth with blank label must preserve old label"
    finally:
        ws._oauth_sessions.pop(sid, None)


def test_codex_worker_reauth_updates_label_when_provided(tmp_path, monkeypatch):
    """Re-auth with a non-empty label updates the credential's label."""
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes"))
    _setup_auth_json(tmp_path / "hermes", [
        {
            "id": "cred-1", "label": "Old", "auth_type": "oauth", "priority": 0,
            "source": "dashboard_device_code", "access_token": "old-token",
            "refresh_token": "old-refresh",
            "account_fingerprint": "fp-update",
        },
    ])
    from hermes_cli import web_server as ws
    sid = "test-reauth-update"
    ws._oauth_sessions[sid] = {
        "session_id": sid, "provider": "openai-codex", "flow": "device_code",
        "created_at": __import__("time").time(), "status": "pending", "error_message": None,
        "label": "Updated Name",
    }
    monkeypatch.setattr(ws, "_codex_account_fingerprint", lambda tok: "fp-update")
    try:
        status, err = _run_worker(sid, monkeypatch, tmp_path / "hermes")
        assert status == "approved", f"worker failed: {err}"
        pool_data = json.loads(((tmp_path / "hermes") / "auth.json").read_text())
        creds = pool_data["credential_pool"]["openai-codex"]
        assert len(creds) == 1
        assert creds[0]["label"] == "Updated Name", "re-auth with new label must update"
    finally:
        ws._oauth_sessions.pop(sid, None)
