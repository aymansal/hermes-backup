---
name: hermes-cron-operations
description: Configure, debug, and extend Hermes cron jobs and scheduler behavior — no_agent scripts, agent-reviewed jobs, per-job model/provider/reasoning, scripts, toolsets, and safe verification.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, cron, scheduler, raid-timers, no-agent, reasoning, jobs, automation, memory-curation]
    created_by: agent
---

# Hermes Cron Operations

## Purpose

Use this Skill Rune when configuring, debugging, or extending Hermes cron jobs / Raid Timers. This covers:

- `no_agent=True` script-only jobs
- Agent-reviewed cron jobs with scripts feeding prompt context
- Per-job model/provider/base_url/toolset configuration
- Per-job reasoning overrides such as `reasoning_effort: xhigh`
- Cron job persistence in `~/.hermes/cron/jobs.json`
- Scheduler behavior in `cron/scheduler.py`
- Cron tool API behavior in `tools/cronjob_tools.py`
- Safe verification without restarting live gateways until Ayman approves

This is the class-level umbrella for cron internals. Do not create one-session skills for individual cron bugs; add references here.

## Required Access Keys / Config Values

- Hermes checkout path, usually `~/.hermes/hermes-agent`
- Hermes home path, usually `~/.hermes`
- Target cron job ID or job name
- If changing provider/model: provider name and model ID must be known; do not guess Access Keys
- Approval before service/gateway restarts, cron changes, config edits, or writes touching live automation

Never print secrets from `.env`, auth files, cookies, tokens, or credential pools.

---

## Phase 1 — Inspect the Raid Timer Read-Only

Start with read-only discovery:

```bash
cd ~/.hermes/hermes-agent
python - <<'PY'
from cron.jobs import list_jobs
for j in list_jobs():
    print({
        k: j.get(k)
        for k in [
            'id', 'name', 'model', 'provider', 'base_url', 'script',
            'no_agent', 'reasoning_effort', 'enabled_toolsets',
            'schedule_display', 'next_run_at', 'last_status'
        ]
    })
PY
```

If using the Hermes tool surface, `cronjob(action='list')` is enough to inspect high-level state, but raw file inspection may reveal fields not yet formatted by the tool.

Key files:

- `~/.hermes/cron/jobs.json` — persisted jobs
- `~/.hermes/scripts/<script>` — scripts referenced by jobs
- `cron/jobs.py` — create/update/load normalization
- `cron/scheduler.py` — actual execution path
- `tools/cronjob_tools.py` — agent-facing tool schema and formatting

---

## Core Rule: `no_agent` Means No LLM, Not Read-Only

A `no_agent: true` cron skips the LLM entirely. The scheduler runs the script and delivers stdout verbatim.

Important consequences:

- Job `model`, `provider`, `base_url`, and `reasoning_effort` are ignored while `no_agent` is true.
- The script can still mutate files, databases, APIs, and Holographic memory if it is coded to do so.
- Empty stdout means silent success.
- Non-zero exit means scheduler error alert.

Pitfall: do not assume a `no_agent` job is harmless. Inspect the script for writes before changing trust boundaries.

---

## Pattern: Agent-Reviewed Script Job

Use this when deterministic code should gather candidates, but an LLM should decide what to do with them.

1. Make the script produce a **dry-run / candidate-only report**.
2. Set `no_agent: false`.
3. Keep the script attached; its stdout becomes context for the agent prompt.
4. Pin provider/model/reasoning on the job.
5. Restrict `enabled_toolsets` to the minimum required.
6. Write the prompt so the agent is explicitly responsible for final decisions and safety filters.

Example shape:

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

For memory curation, the script should not call `MemoryStore.add_fact()` in this mode. It should only print candidates. The reviewing agent uses memory/fact-store tools after dedupe and durability checks.

See `references/agent-reviewed-memory-curator.md` for the concrete pattern from the Daily Holographic Memory Curator conversion.

---

## Adding Per-Job Reasoning Support

If Hermes does not yet support per-job reasoning, patch the full path:

1. `cron/jobs.py`
   - Add a `reasoning_effort` parameter to `create_job()`.
   - Normalize allowed values: `none`, `minimal`, `low`, `medium`, `high`, `xhigh`.
   - Persist it in job records.
   - Allow `update_job(..., {'reasoning_effort': ''})` to clear the override.

2. `cron/scheduler.py`
   - Load global config as a dict defensively.
   - Resolve reasoning as: job override first, then `agent.reasoning_effort`.
   - Pass `reasoning_config=parse_reasoning_effort(effort)` into `AIAgent`.

3. `tools/cronjob_tools.py`
   - Expose `reasoning_effort` in the tool schema.
   - Accept it on create/update.
   - Include it in formatted job output.

4. Tests
   - create job stores per-job reasoning
   - update job sets reasoning
   - empty string clears reasoning
   - scheduler override beats global config
   - scheduler falls back to global config when unset

Targeted verification:

```bash
cd ~/.hermes/hermes-agent
python -m pytest tests/cron/test_jobs.py tests/cron/test_scheduler.py -q -o 'addopts='
```

---

## Safe Runtime Change Flow

For live systems, do not jump straight to service restarts.

1. Patch code and tests.
2. Update the job record or use `cronjob(action='update', ...)`.
3. Verify `cron.jobs.get_job(job_id)` returns the intended fields.
4. Run the candidate script directly if present.
5. Run targeted tests.
6. Only then ask Ayman to approve gateway/scheduler restart if loaded Python modules need refresh.

Service restarts touch the live Comms Gate. Ask first.

---

## Verification Snippets

Check one job:

```bash
cd ~/.hermes/hermes-agent
python - <<'PY'
from cron.jobs import get_job
job_id = 'REPLACE_ME'
j = get_job(job_id)
print({k: j.get(k) for k in [
    'id', 'name', 'model', 'provider', 'script', 'no_agent',
    'reasoning_effort', 'enabled_toolsets'
]})
PY
```

Check candidate script output without writes:

```bash
python ~/.hermes/scripts/daily_memory_curator_candidates.py | sed -n '1,40p'
```

Expected signs for a dry-run curator:

- `Mode: DRY-RUN`
- `Facts added: 0`
- `Write path: dry-run`

---

## Pattern: Script-Only Status-Change Watchdog

Use this when the user wants a reliable Comms Gate ping only when durable state changes, without burning model calls or requiring the main chat to poll.

Recommended shape:

1. Write a `~/.hermes/scripts/<name>.py` script that is read-only against the source system and persists only a compact snapshot under `~/.hermes/cron/state/`.
2. First run prints a baseline deployment message.
3. Future runs print only meaningful transitions; empty stdout means silent success.
4. Create the Raid Timer with `no_agent: true`, a short cron schedule such as `*/2 * * * *`, and `deliver: telegram` when the user wants the current `/sethome` destination.
5. Verify from the default/operator profile, not a worker profile: inspect `~/.hermes/cron/jobs.json`, run `hermes cron list --all`, and run the script twice — first should notify, second should be silent if nothing changed.

Example use case: a Kanban worker status watchdog that scans board SQLite files read-only, reports new active cards and status changes like `running → blocked` or `running → done`, and stays quiet otherwise.

## Common System Alerts

- **Model/provider set but ignored:** job is probably `no_agent: true`.
- **Reasoning override ignored:** scheduler may only read global `agent.reasoning_effort`; patch per-job support.
- **Cron tool does not show new field:** update `_format_job()` and tool schema in `tools/cronjob_tools.py`.
- **Script still writes memory/database:** convert it to candidate-only or dry-run wrapper before attaching to an agent-reviewed job.
- **Tests pass but live cron still old:** gateway/scheduler process likely has old module loaded; ask before restart.
- **Unrelated dirty repo files:** report clearly and avoid committing broad unrelated changes.

---

## References

- `references/agent-reviewed-memory-curator.md` — Daily Holographic Memory Curator conversion from no_agent direct writes to DeepSeek V4 Pro xhigh review
