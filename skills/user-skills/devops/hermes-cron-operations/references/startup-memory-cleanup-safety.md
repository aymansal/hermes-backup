# Startup Memory Cleanup Safety Pattern

Use this reference when a Hermes Raid Timer, one-shot systemd unit, startup script, or manual maintenance script needs to mutate the Holographic memory database while temporarily stopping live Hermes services.

## Class of problem

A script that stops `hermes-gateway.service` and/or `hermes-dashboard.service` must not rely on the happy path to bring them back. Any failure between `stop` and `start` can leave the Telegram Comms Gate and Shadow Realm down until a human notices.

This is especially dangerous for scripts that run unattended at startup, from cron, or as one-shot systemd services.

## Safe pattern

1. Put service restoration in a `trap`, not only at the end of the script.
2. Reset failed state before start, so a previous failed unit does not block resummoning.
3. Use a known interpreter path or `python3`; do not rely on a login-shell alias.
4. Back up the DB before mutation.
5. Verify target rows are gone and FTS row count still matches the facts table.
6. Verify both services are active and the dashboard port is listening before reporting PASS.

## Bash skeleton

```bash
#!/usr/bin/env bash
set -euo pipefail

SERVICES=(hermes-dashboard.service hermes-gateway.service)
LOG="$HOME/.hermes/logs/memory_cleanup_$(date +%Y%m%d_%H%M%S).log"
exec >"$LOG" 2>&1

restore_services() {
  systemctl --user reset-failed "${SERVICES[@]}" || true
  systemctl --user start "${SERVICES[@]}" || true
  systemctl --user --no-pager --full status "${SERVICES[@]}" || true
}
trap restore_services EXIT

systemctl --user stop "${SERVICES[@]}" || true
backup="$HOME/.hermes/memory_store.db.pre-delete.$(date +%Y%m%d_%H%M%S).bak"
cp "$HOME/.hermes/memory_store.db" "$backup"

python3 - <<'PY'
import sqlite3
p='/home/ubuntu/.hermes/memory_store.db'
ids=[145,146]
con=sqlite3.connect(p, timeout=30)
con.execute('PRAGMA busy_timeout=30000')
ph=','.join('?'*len(ids))
print('existing_before_count', con.execute(f'SELECT count(*) FROM facts WHERE fact_id IN ({ph})', ids).fetchone()[0])
con.execute('BEGIN IMMEDIATE')
con.executemany('DELETE FROM fact_entities WHERE fact_id=?', [(i,) for i in ids])
con.executemany('DELETE FROM facts WHERE fact_id=?', [(i,) for i in ids])
con.commit()
print('remaining_after', con.execute(f'SELECT fact_id FROM facts WHERE fact_id IN ({ph})', ids).fetchall())
con.execute("INSERT INTO facts_fts(facts_fts) VALUES ('rebuild')")
con.commit()
print('facts_rows', con.execute('SELECT count(*) FROM facts').fetchone()[0])
print('fts_rows', con.execute('SELECT count(*) FROM facts_fts').fetchone()[0])
con.close()
PY
```

## Verification commands

```bash
systemctl --user status hermes-dashboard.service hermes-gateway.service --no-pager --full
ss -ltnp | grep -E '(:9119|hermes|python)' || true
python3 - <<'PY'
import sqlite3
con=sqlite3.connect('/home/ubuntu/.hermes/memory_store.db')
print('facts_rows', con.execute('SELECT count(*) FROM facts').fetchone()[0])
print('fts_rows', con.execute('SELECT count(*) FROM facts_fts').fetchone()[0])
con.close()
PY
```

## PASS criteria

- Target fact IDs return zero rows.
- `facts_fts` rebuild succeeds.
- `hermes-dashboard.service` is active.
- `hermes-gateway.service` is active.
- Dashboard port is listening on the configured host/port.
- A backup path and log path are reported.

## Failure mode to avoid

Never write scripts where service restart only happens after the DB mutation block. The restoration must happen even if the mutation block fails.