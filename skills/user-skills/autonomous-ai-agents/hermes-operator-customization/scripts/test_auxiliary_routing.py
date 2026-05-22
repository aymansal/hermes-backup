#!/usr/bin/env python3
"""Smoke-test Hermes auxiliary model routing.

Run from the Hermes repo root with the Hermes venv after sourcing ~/.hermes/.env, e.g.:

    cd ~/.hermes/hermes-agent
    set -a; . ~/.hermes/.env >/dev/null 2>&1 || true; set +a
    venv/bin/python ~/.hermes/skills/autonomous-ai-agents/hermes-operator-customization/scripts/test_auxiliary_routing.py

The script calls the configured auxiliary slots and prints only model/task status.
It never prints API keys. It intentionally reports finish_reason and whether
reasoning_content was present, because some OpenCode Go models can return HTTP
200 while spending short budgets on reasoning and emitting empty final content.
"""
from __future__ import annotations

import json
import re
import time

from agent.auxiliary_client import call_llm

TESTS = [
    ("compression", "Reply with exactly: COMPRESSION_OK", 300),
    ("title_generation", "Reply with exactly: TITLE_OK", 300),
    ("approval", "Reply with exactly: APPROVAL_OK", 300),
    ("web_extract", "Reply with exactly: WEB_EXTRACT_OK", 300),
    ("curator", "Reply with exactly: CURATOR_OK", 300),
]

SECRET_RE = re.compile(r"sk-[A-Za-z0-9_-]{8,}")


def scrub(text: object) -> str:
    return SECRET_RE.sub("[REDACTED]", str(text))[:700]


def dump_result(task: str, ok: bool, started: float, **extra: object) -> None:
    payload = {"task": task, "ok": ok, "seconds": round(time.time() - started, 2)}
    payload.update(extra)
    print(json.dumps(payload, ensure_ascii=False))


def call_task(task: str, prompt: str, max_tokens: int) -> None:
    started = time.time()
    try:
        resp = call_llm(
            task=task,
            messages=[
                {
                    "role": "system",
                    "content": "You are a routing smoke test. Follow the user instruction exactly.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=max_tokens,
            timeout=120,
        )
        choice = resp.choices[0]
        msg = choice.message
        msg_dict = getattr(msg, "model_dump", lambda: getattr(msg, "__dict__", {}))()
        content = msg_dict.get("content") or ""
        reasoning = msg_dict.get("reasoning_content") or ""
        dump_result(
            task,
            True,
            started,
            model_reported=getattr(resp, "model", "") or "<unknown>",
            finish_reason=getattr(choice, "finish_reason", None),
            content=scrub(content),
            content_empty=not bool(str(content).strip()),
            has_reasoning_content=bool(str(reasoning).strip()),
        )
    except Exception as exc:
        dump_result(
            task,
            False,
            started,
            error_type=type(exc).__name__,
            error=scrub(exc),
        )


def main() -> int:
    for task, prompt, max_tokens in TESTS:
        call_task(task, prompt, max_tokens)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
