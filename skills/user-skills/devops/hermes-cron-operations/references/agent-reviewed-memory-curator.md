# Agent-Reviewed Memory Curator Pattern

## Context

A no-agent cron can still write to Holographic memory if its script calls the memory store directly. `no_agent=True` only means the scheduler skips the LLM; it is not a read-only safety boundary.

In the Daily Holographic Memory Curator case, the original script:

- scanned Hermes session history
- extracted candidate facts using regex filters
- rejected obvious secrets/transient noise
- wrote accepted facts using `MemoryStore.add_fact(...)` or a SQLite fallback

That meant model/provider settings on the cron job were decorative while `no_agent` was enabled.

## Desired Architecture

Use two stages:

1. **Deterministic candidate scout**
   - keeps regex/session scanning and secret/transient filtering
   - runs in dry-run mode
   - prints candidate facts and rejection counts
   - performs zero memory writes

2. **Agent reviewer**
   - receives script stdout as cron context
   - uses a pinned model/provider/reasoning profile
   - dedupes against existing Holographic memory
   - stores only durable, compact facts

Example cron job shape:

```json
{
  "script": "daily_memory_curator_candidates.py",
  "no_agent": false,
  "provider": "opencode-go",
  "model": "deepseek-v4-pro",
  "reasoning_effort": "xhigh",
  "enabled_toolsets": ["memory"]
}
```

## Wrapper Script Pattern

Create a wrapper rather than mutating the original curator immediately:

```python
#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path.home() / ".hermes" / "scripts" / "daily_memory_curator.py"


def main() -> int:
    cmd = [sys.executable, str(SCRIPT), "--dry-run", "--verbose"]
    completed = subprocess.run(cmd, text=True, capture_output=True, timeout=150)
    if completed.stdout:
        print(completed.stdout.rstrip())
    if completed.stderr:
        print(completed.stderr.rstrip(), file=sys.stderr)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
```

Verify:

```bash
python ~/.hermes/scripts/daily_memory_curator_candidates.py | sed -n '1,40p'
```

Expected signs:

- `Mode: DRY-RUN`
- `Facts added: 0`
- `Write path: dry-run`

## Reviewer Prompt Skeleton

Use a prompt like:

```text
You are the Daily Holographic Memory Curator reviewer.

The attached script output is a DRY-RUN candidate report only. The script has not written memory. Review candidates with strict durable-memory standards and use Holographic memory/fact_store tools only for facts that truly deserve persistence.

Rules:
- Store only compact durable facts that will still matter in future sessions.
- Prefer user preferences, stable project facts, stable architecture/workflow decisions, and reusable technical environment facts.
- Reject compaction-summary instructions, assistant promises, current task state, PR/issue/commit/job IDs, quota/run status, logs, raw commands, malformed noisy sentences, and anything likely stale within a week.
- Never store secrets, tokens, cookies, private keys, or raw logs.
- Do not store commands as facts. Procedures belong in Skill Runes, not Holographic memory.
- Before adding a fact, search/probe existing Holographic memory to avoid duplicates or contradictions.
- If no candidates pass, add nothing and report that nothing durable passed review.
```

## Code Patch Checklist for Per-Job Reasoning

- `cron/jobs.py`: normalize and persist `reasoning_effort`
- `cron/scheduler.py`: job override beats global `agent.reasoning_effort`
- `tools/cronjob_tools.py`: expose field in schema, create/update path, and formatted output
- tests:
  - create stores `xhigh`
  - update sets `xhigh`
  - empty string clears
  - scheduler passes xhigh to `AIAgent`
  - fallback to global reasoning still works

Run:

```bash
python -m pytest tests/cron/test_jobs.py tests/cron/test_scheduler.py -q -o 'addopts='
```

## Pitfalls

- Do not call a no-agent cron "using DeepSeek" just because the job has `model: deepseek-v4-pro`; no-agent ignores the model.
- Do not let both the script and agent write memory. Pick one writer; for curated memory, make the agent the writer.
- Do not store noisy user frustration literally as durable operating rules unless it is clear, stable, and not contradicted by existing profile/memory.
- Do not restart Hermes silently after patching scheduler code. Ask Ayman first.
