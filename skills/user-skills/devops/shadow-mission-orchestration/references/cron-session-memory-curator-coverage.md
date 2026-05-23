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

## Curator prompt requirements

A robust curator prompt should require the worker to:

- Enumerate sessions by timestamp, not rely only on `session_search()` default browse.
- Exclude cron sessions and empty sessions unless explicitly relevant.
- Group continuation sessions by title/topic, e.g. `Multi Model Account Selection #1-#7` as one topic cluster.
- Inspect enough context per cluster to identify durable decisions and corrections.
- Reject secrets, task IDs, PR/commit/session IDs, quota percentages, and transient run state.
- Deduplicate against fact_store before adding.
- Report actual sessions found, sessions skipped with reasons, topic clusters inspected, facts added, duplicates skipped, and uncertainty.

## Delivery route verification

Do not ignore delivery metadata. A curator can succeed and still leave Ayman blind if `deliver=origin` has no resolved origin. When reviewing or patching this class of Raid Timer:

1. Check `cronjob(action='list')` for `last_delivery_error`.
2. If it says `no delivery target resolved for deliver=origin`, update the job to an explicit known target such as `telegram:<chat_id>` or `telegram:<chat_id>:<thread_id>` after approval.
3. Re-run the job once with `cronjob(action='run', job_id=...)` when safe.
4. Verify `last_status=ok`, `last_delivery_error=null`, the next scheduled run remains daily, and a new markdown report appears under `~/.hermes/cron/output/<job_id>/`.
5. Read the new report and confirm it states the actual session count and inspected clusters, not only that facts were added.

## Patch-and-verify checklist

For this exact class of fix, success means all of these are true:

- Prompt includes an explicit warning that bare `session_search()` only returns 3 sessions.
- Prompt requires a read-only SQLite enumeration of `/home/ubuntu/.hermes/state.db` for the scan window.
- Prompt requires clustering related sessions before extraction.
- Job delivery target is explicit and resolvable.
- Manual run after the patch reports more than the default 3 sessions when the state DB contains more.
- Holographic/fact_store contains only clean durable facts; raw transcripts and transient run states are flagged for later review rather than edited/deleted automatically.

## Reporting standard

If the job added facts but only scanned a small default sample, say:

```text
Result: PARTIAL.
The Raid Timer stored useful facts, but coverage failed: it inspected only N sessions while the state DB shows M sessions in the target window.
```

Do not certify the Gate as fully open until coverage and writes are both verified.
