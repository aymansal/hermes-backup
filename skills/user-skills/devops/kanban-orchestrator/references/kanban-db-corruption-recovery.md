# Kanban SQLite DB Corruption Recovery

## Symptom
Gateway logs spam every ~5 seconds:
```
WARNING gateway.run: kanban notifier tick failed: database disk image is malformed
```

The kanban board may still load, but notifications are broken and the log noise obscures real issues.

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
