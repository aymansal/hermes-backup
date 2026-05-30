# Kanban SQLite DB Corruption Recovery

## Symptom
Gateway logs spam every ~5 seconds:
```
WARNING gateway.run: kanban notifier tick failed: database disk image is malformed
```

Other commands can also expose the corruption, especially notification commands:
```bash
hermes kanban --board <board> notify-list
# sqlite3.DatabaseError: database disk image is malformed
```

The kanban board may still load, workers/reviewers may still run, and `show/list` can appear healthy, but notifications are broken and the log noise obscures real issues. For Ayman, this violates the Kanban contract because the General may be forced into manual polling and become unavailable in chat; finish the active review/fix gate first if one is running, then repair the DB with approval.

## Diagnosis

1. Confirm the DB path (usually `~/.hermes/kanban/kanban.db` or under the active profile):
   ```bash
   find ~/.hermes -name "kanban.db" -type f 2>/dev/null
   ```

2. Verify corruption:
   ```bash
   sqlite3 ~/.hermes/kanban/kanban.db "PRAGMA integrity_check;"
   ```
   Expected: `ok` if healthy. Anything else means corruption.

## Recovery Options

### Option A — SQLite `.recover` (preserves data)
```bash
DB="~/.hermes/kanban/kanban.db"
BACKUP="${DB}.bak.$(date +%Y%m%d_%H%M%S)"
cp "$DB" "$BACKUP"
sqlite3 "$DB" ".recover" | sqlite3 "${DB}.recovered"
mv "${DB}.recovered" "$DB"
```
Then verify: `sqlite3 "$DB" "PRAGMA integrity_check;"`

If `sqlite3: command not found`, do **not** install packages blindly on Ayman's VPS. Use the Python rebuild fallback first.

### Option A2 — Python table rebuild fallback when sqlite3 CLI is missing

Use when the DB opens enough to read `sqlite_master` and most tables, but one table/page is corrupt. This preserves readable board history and reconstructs notifier rows when the corruption is limited to `kanban_notify_subs` payload pages.

High-level pattern:
1. `cp -a "$DB" "$DB.bak.<timestamp>"`.
2. Open old DB readonly with Python `sqlite3.connect(f"file:{DB}?mode=ro", uri=True)`.
3. Create a new DB from readable `sqlite_master` table schemas.
4. Copy all readable tables with `SELECT *`.
5. If `kanban_notify_subs` fails on `SELECT *`, salvage key columns with full-column scans (`task_id`, `platform`, `chat_id`, `thread_id`) and reconstruct rows with `last_event_id` set to the current max `task_events.id` for that task to avoid replay spam.
6. Create indexes after data copy.
7. Verify `PRAGMA integrity_check` returns `ok`.
8. Move the corrupt DB aside and swap the rebuilt DB into place.

Expected verification:
```bash
python3 - <<'PY'
from pathlib import Path
import sqlite3
DB = Path.home() / '.hermes/kanban/boards/immopilot/kanban.db'
conn = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
print(conn.execute('PRAGMA integrity_check').fetchone()[0])
print(conn.execute('SELECT * FROM kanban_notify_subs').fetchall())
conn.close()
PY
hermes kanban --board immopilot notify-list
```

Only after the rebuilt DB verifies cleanly, restart the gateway with approval and confirm there are no fresh `kanban notifier tick failed` messages.

### Option B — Rebuild from dump (if recover fails)
```bash
DB="~/.hermes/kanban/kanban.db"
sqlite3 "$DB" ".dump" > /tmp/kanban_dump.sql
mv "$DB" "${DB}.corrupt.$(date +%Y%m%d_%H%M%S)"
sqlite3 "$DB" < /tmp/kanban_dump.sql
```

### Option C — Delete and reinitialize (nuclear, loses board history)
```bash
DB="~/.hermes/kanban/kanban.db"
mv "$DB" "${DB}.corrupt.$(date +%Y%m%d_%H%M%S)"
# Hermes will recreate the DB on next kanban operation
```

## Restart
After any recovery, restart the Hermes gateway so the notifier reconnects to the repaired DB:
```bash
sudo systemctl restart hermes   # or however Hermes is managed on this host
```

## Prevention
- The kanban DB is SQLite. Avoid concurrent writers (e.g., multiple gateway processes, manual SQLite CLI ops while the gateway is running).
- Ensure the filesystem has free space; ENOSPC during a write can corrupt SQLite.
- If corruption recurs, check for failing storage (smartctl, dmesg) or abrupt process kills (OOM killer).
