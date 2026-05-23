from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace


def _write_auth_store(tmp_path, payload: dict) -> None:
    hermes_home = tmp_path / "hermes"
    hermes_home.mkdir(parents=True, exist_ok=True)
    (hermes_home / "auth.json").write_text(json.dumps(payload, indent=2))


def test_codex_account_rows_include_only_sanitized_quota(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes"))
    _write_auth_store(
        tmp_path,
        {
            "version": 1,
            "credential_pool": {
                "openai-codex": [
                    {
                        "id": "cred-1",
                        "label": "ChatGPT account 1",
                        "auth_type": "oauth",
                        "priority": 0,
                        "source": "device_code",
                        "access_token": "secret-access-token",
                        "refresh_token": "secret-refresh-token",
                        "email": "do-not-return@example.com",
                        "raw_payload": {"token": "nope"},
                        "last_quota": {
                            "provider": "openai-codex",
                            "source": "usage_endpoint",
                            "captured_at": "2026-05-22T00:00:00Z",
                            "captured_at_unix": 1779408000,
                            "plan_type": "plus",
                            "active_limit": "primary",
                            "credits_unlimited": False,
                            "credits_has_credits": True,
                            "account_id": "acct-secret",
                            "email": "quota-secret@example.com",
                            "raw_payload": {"private": True},
                            "buckets": [
                                {
                                    "key": "primary",
                                    "label": "5h",
                                    "used_percent": 25,
                                    "remaining_percent": 75,
                                    "reset_at": 1779410000,
                                    "reset_after_seconds": 900,
                                    "authorization": "Bearer secret",
                                }
                            ],
                        },
                    }
                ]
            },
        },
    )

    from hermes_cli.web_server import _codex_account_rows

    rows = _codex_account_rows("cred-1")

    assert rows[0]["selected"] is True
    assert rows[0]["has_refresh_token"] is True
    assert rows[0]["quota_status"] == "ok"
    quota = rows[0]["quota"]
    assert quota == {
        "available": True,
        "buckets": [
            {
                "key": "primary",
                "label": "5h",
                "used_percent": 25,
                "remaining_percent": 75,
                "reset_at": 1779410000,
                "reset_after_seconds": 900,
            }
        ],
        "source": "usage_endpoint",
        "captured_at": "2026-05-22T00:00:00Z",
        "plan_type": "plus",
        "active_limit": "primary",
        "captured_at_unix": 1779408000,
        "credits_unlimited": False,
        "credits_has_credits": True,
    }
    serialized = json.dumps(rows)
    assert "secret-access-token" not in serialized
    assert "secret-refresh-token" not in serialized
    assert "do-not-return" not in serialized
    assert "acct-secret" not in serialized
    assert "raw_payload" not in serialized
    assert "authorization" not in serialized


def test_codex_account_rows_blank_label_not_gptn(tmp_path, monkeypatch):
    """Blank and missing labels get neutral fallback, never GptN."""
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes"))
    _write_auth_store(
        tmp_path,
        {
            "version": 1,
            "credential_pool": {
                "openai-codex": [
                    {"id": "cred-blank", "label": "", "auth_type": "oauth", "priority": 0, "source": "device_code", "access_token": "t1"},
                    {"id": "cred-none", "auth_type": "oauth", "priority": 0, "source": "device_code", "access_token": "t2"},
                    {"id": "cred-named", "label": "Swarm", "auth_type": "oauth", "priority": 0, "source": "device_code", "access_token": "t3"},
                ]
            },
        },
    )

    from hermes_cli.web_server import _codex_account_rows

    rows = _codex_account_rows("")

    labels = {r["id"]: r["label"] for r in rows}
    assert labels["cred-blank"] == "ChatGPT Account", "blank label should use neutral fallback"
    assert labels["cred-none"] == "ChatGPT Account", "missing label should use neutral fallback"
    assert labels["cred-named"] == "Swarm", "explicit label should be preserved"
    for r in rows:
        assert "Gpt" not in r["label"], f"no GptN fallback for {r['id']}: {r['label']}"


def test_select_codex_account_writes_global_model_credential_id(tmp_path, monkeypatch):
    hermes_home = tmp_path / "hermes"
    monkeypatch.setenv("HERMES_HOME", str(hermes_home))
    _write_auth_store(
        tmp_path,
        {
            "version": 1,
            "credential_pool": {
                "openai-codex": [
                    {
                        "id": "cred-2",
                        "label": "ChatGPT account 2",
                        "auth_type": "oauth",
                        "priority": 0,
                        "source": "device_code",
                        "access_token": "token",
                    }
                ]
            },
        },
    )
    (hermes_home / "config.yaml").write_text("model:\n  provider: openrouter\n  default: test-model\n")

    from hermes_cli.config import load_config
    from hermes_cli.web_server import CodexAccountSelection, select_codex_account

    response = asyncio.run(select_codex_account(CodexAccountSelection(credential_id="cred-2")))

    cfg = load_config()
    assert response["selected_id"] == "cred-2"
    assert cfg["model"]["provider"] == "openai-codex"
    assert cfg["model"]["credential_id"] == "cred-2"
    assert cfg["model"]["default"] == "test-model"


def test_capture_rate_limits_saves_codex_quota_for_current_pool_id(monkeypatch):
    captured: dict = {}

    def fake_save(headers, credential_id=None):
        captured["headers"] = headers
        captured["credential_id"] = credential_id

    monkeypatch.setattr("agent.codex_quota.save_codex_quota_from_headers", fake_save)

    from run_agent import AIAgent

    agent = SimpleNamespace(
        provider="openai-codex",
        _credential_pool=SimpleNamespace(current_id="cred-live"),
        _rate_limit_state=None,
    )
    response = SimpleNamespace(headers={"x-codex-primary-used-percent": "30"})

    AIAgent._capture_rate_limits(agent, response)  # type: ignore[arg-type]

    assert captured["headers"] == response.headers
    assert captured["credential_id"] == "cred-live"
