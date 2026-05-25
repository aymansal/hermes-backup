# Cron Session Memory Curator Coverage

## Trigger

Use this reference when creating, reviewing, or troubleshooting a Hermes Raid Timer that reads recent sessions and stores durable facts into Holographic/fact_store.

## Lesson captured

A curator cron run can succeed technically while failing the mission if it only calls `session_search()` with no arguments. The default browse mode returns only the 3 most recent sessions. That is not the same as "all sessions since the last run" or "all sessions in the last 24 hours".

## Required verification

Before reporting that a session-memory curator did the job, verify coverage independently:

1. Check the cron job status and output.
2. Inspect the cron session/tool calls if needed.
3. Count actual sessions in the intended window from `~/.hermes/state.db`, using message timestamps when available.
4. Compare that count to the sessions the curator claims it inspected.
5. Report partial success if facts were stored but coverage was incomplete.

## Safe read-only SQLite pattern

Use a read-only diagnostic query shape like this from terminal when allowed:

```bash
python3 - <<'PY'
import sqlite3, time, datetime
conn = sqlite3.connect('/home/ubuntu/.hermes/state.db')
conn.row_factory = sqlite3.Row
cut = time.time() - 86400
rows = conn.execute("""
select s.id, s.title, s.source, s.started_at,
       max(m.timestamp) as last_msg,
       s.message_count,
       count(m.id) as actual_messages
from sessions s
left join messages m on m.session_id = s.id
group by s.id
having coalesce(max(m.timestamp), s.started_at) >= ?
order by coalesce(max(m.timestamp), s.started_at) desc
""", (cut,)).fetchall()
print('count', len(rows))
for r in rows:
    ts = datetime.datetime.fromtimestamp(float(r['last_msg'] or r['started_at']), datetime.UTC).isoformat()
    print(r['id'], '|', r['source'], '| msgs', r['actual_messages'], '| last', ts, '|', r['title'])
PY
```

For a daily curator, prefer the exact previous-run-to-current-run window over a rolling 24h window when you can determine it.

## Curator implementation requirements

For daily session-memory curation, prefer a `no_agent=true` script over an agent-driven cron prompt when reliability matters. Agent-mode curator jobs can fail even after good prompting because cron sessions may not expose the interactive `memory`/`fact_store` tools, and long tool loops increase SQLite lock/timeout risk.

A robust curator script or prompt should require the worker to:

- Enumerate sessions by timestamp, not rely only on `session_search()` default browse.
- Exclude cron sessions and empty sessions unless explicitly relevant.
- Group continuation sessions by title/topic, e.g. `Multi Model Account Selection #1-#7` as one topic cluster.
- Inspect enough context per cluster to identify durable decisions and corrections.
- Reject secrets, credentials, bearer/OAuth/JWT values, cookies, private keys, raw logs, task IDs, PR/commit/session IDs, quota percentages/cooldowns, timestamps, run IDs, and transient run state.
- Avoid raw transcript dumps; store clean declarative facts only.
- Deduplicate against existing Holographic/fact_store content before adding.
- Report actual sessions found, sessions skipped with reasons, topic clusters inspected, facts added, duplicates skipped, and uncertainty.
- Emit empty stdout when no new durable facts are found if `no_agent=true` should remain quiet.

## Delivery route verification

Do not ignore delivery metadata. A curator can succeed and still leave Ayman blind if `deliver=origin` has no resolved origin. When reviewing or patching this class of Raid Timer:

1. Check `cronjob(action='list')` for `last_delivery_error`.
2. If it says `no delivery target resolved for deliver=origin`, update the job to an explicit known target such as `telegram:<chat_id>` or `telegram:<chat_id>:<thread_id>` after approval.
3. Re-run the job once with `cronjob(action='run', job_id=...)` when safe.
4. Verify `last_status=ok`, `last_delivery_error=null`, the next scheduled run remains daily, and a new markdown report appears under `~/.hermes/cron/output/<job_id>/`.
5. Read the new report and confirm it states the actual session count and inspected clusters, not only that facts were added.

## Writing facts from cron: avoid agent tools; keep SQLite work short

Interactive tools such as `memory` and `fact_store` may be unavailable inside Hermes cron runs. Do not build a daily curator that depends on those tools being callable from an agent-mode cron session.

Preferred pattern for unattended daily curation:

1. Configure the cron job as `no_agent=true` with a dedicated script under `~/.hermes/scripts/`.
2. Read `/home/ubuntu/.hermes/state.db` with short read-only SQLite connections, e.g. URI `file:/home/ubuntu/.hermes/state.db?mode=ro`, `timeout=2`, and bounded result windows.
3. Deduplicate and filter candidates in memory before opening the Holographic memory DB.
4. Write only clean durable facts, using either the Holographic `MemoryStore` API when available or a minimal direct SQLite transaction that matches the current schema.
5. Keep write transactions tiny: set a busy timeout, open late, commit fast, close immediately, and never hold a write connection while scanning sessions or calling external tools.
6. Print a compact report only when facts are added or an error occurs; empty stdout is a valid silent OK for no-new-facts runs.

MemoryStore API pattern when using the module is viable:

```python
import sys
from pathlib import Path
sys.path.insert(0, '/home/ubuntu/.hermes/hermes-agent/plugins/memory/holographic')
from store import MemoryStore

ms = MemoryStore(Path('/home/ubuntu/.hermes/memory_store.db'))
fid = ms.add_fact(content='...', category='general', tags='tag1,tag2')
ms.close()
```

Direct SQLite writes are acceptable only when the script is intentionally short-lived, schema-aware, deduplicated, and uses short transactions. The anti-pattern is a long agent/tool loop opening write-capable `memory_store.db` connections while also scanning, prompting, or retrying.

Read-only inspection of `state.db` remains safe via raw SQLite with `mode=ro` and `timeout=2`.

## Data quality patterns

When curating Holographic memory, apply these quality rules:

- **Raw voice transcripts are not facts.** If a fact starts with `[The user sent a voice message~` or `[Ayman]`, it is a raw transcript or quote. Replace it with a clean declarative statement that captures the same decision or preference. Example: `[Ayman] Let go with ImmoPilot i like it` → `Ayman chose ImmoPilot as the product name for the real-estate ERP SaaS.`
- **Merge duplicates.** If three facts say the same thing (e.g., facts 84, 94, 95 all say "cron delivery to Shadow Realm 2 General topic"), consolidate into one canonical fact and remove the extras.
- **Update stale facts.** Facts containing transient data (quota percentages, server PIDs, process states, account counts) that will be wrong within 7 days should be updated to remove the transient part or flagged. Structural information (credential architecture, cron schedule, delivery routing) is durable; numeric state is not.
- **One-week test.** If the fact will be stale within 7 days, it does not belong in Holographic memory. Flag it for cleanup rather than adding it.

## Patch-and-verify checklist

For this exact class of fix, success means all of these are true:

- Curator does not rely on bare `session_search()` browse mode for a full scan; it enumerates `/home/ubuntu/.hermes/state.db` by timestamp for the scan window.
- The implementation clusters related sessions before extraction when needed.
- The job is `no_agent=true` if the purpose is unattended daily curation rather than an interactive one-off review.
- The script has secret/transient rejection, dedupe, bounded reads, short SQLite transactions, and silent OK behavior for no-new-facts runs.
- Job delivery target is explicit and resolvable, e.g. `telegram:<chat_id>:<thread_id>` for Telegram forum topics.
- Manual run after the patch either prints a compact added-facts report or produces a verified silent OK because no new durable facts remain.
- Holographic/fact_store contains only clean durable facts; raw transcripts and transient run states are flagged for cleanup rather than blindly preserved.
- After a run, verify `last_status=ok`, `last_delivery_error=null`, next schedule remains correct, and a new output record exists under `~/.hermes/cron/output/<job_id>/` even if it records silent output.

## Reporting standard

If the job added facts but only scanned a small default sample, say:

```text
Result: PARTIAL.
The Raid Timer stored useful facts, but coverage failed: it inspected only N sessions while the state DB shows M sessions in the target window.
```

Do not certify the Gate as fully open until coverage and writes are both verified.
